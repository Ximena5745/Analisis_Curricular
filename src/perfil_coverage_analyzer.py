"""
Análisis de Cobertura del Perfil de Egreso.

Mide qué tan cubiertos están los elementos del perfil de egreso
(Saber, SaberHacer, SaberSer, Áreas profesionales, Tareas profesionales,
Valor agregado) por el corpus curricular (SaberAsociado, Indicadores de logro,
Núcleos temáticos) usando TF-IDF + BM25 + similitud coseno.
"""

import logging
import re
import unicodedata
from typing import Dict, List, Tuple, Optional, Any
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from config import (
    UMBRAL_COBERTURA,
    UMBRALES_POR_CAMPO,
    COLUMNAS_PERFIL,
)

logger = logging.getLogger(__name__)

COLUMNAS_CURRICULO = {
    'Paso3': ['SaberAsociado'],
    'Paso5': [
        'Resultado de aprendizaje',
        'Nombre asignatura o módulo',
        'Indicadores de logro asignatura o módulo',
        'Núcleos temáticos',
        'Actividades de evaluación'
    ]
}

ASIGNATURA_COLS = [
    'Nombre asignatura o módulo',
    'Nombre asignatura o modulo',
]

# Stop words: spaCy español + términos académicos vacíos
try:
    from spacy.lang.es.stop_words import STOP_WORDS as _SPACY_STOP
    STOP_WORDS_FINAL = list(
        _SPACY_STOP | {
            'mediante', 'traves', 'partir', 'nivel', 'proceso', 'manera',
            'ambito', 'contexto', 'actividad', 'desarrollo', 'aplicacion',
            'estudiante', 'programa', 'curricular', 'asignatura', 'modulo',
        }
    )
except ImportError:
    STOP_WORDS_FINAL = [
        'el', 'la', 'de', 'que', 'y', 'a', 'en', 'un', 'ser', 'se',
        'no', 'por', 'con', 'su', 'para', 'como', 'estar', 'tener',
        'le', 'lo', 'del', 'las', 'los', 'al', 'una', 'es', 'e',
        'mediante', 'partir', 'nivel', 'proceso', 'manera', 'ambito',
    ]

TFIDF_KWARGS = dict(
    max_features=1500,
    min_df=1,
    max_df=0.85,
    ngram_range=(1, 3),
    sublinear_tf=True,
    stop_words=STOP_WORDS_FINAL,
)

PESOS_TOP_K = np.array([0.5, 0.3, 0.2])
PESO_COSENO = 0.6
PESO_BM25 = 0.4

_nlp = None
_bm25_available = None


def _get_nlp():
    """Carga lazy de spaCy para lematización."""
    global _nlp
    if _nlp is None:
        try:
            import spacy
            _nlp = spacy.load('es_core_news_sm', disable=['ner', 'parser'])
        except Exception as exc:
            logger.warning('spaCy no disponible (%s); lematización desactivada', exc)
            _nlp = False
    return _nlp if _nlp is not False else None


def _preprocesar_ascii(texto: str) -> str:
    texto = str(texto).lower().strip()
    texto = unicodedata.normalize('NFKD', texto)
    texto = texto.encode('ascii', 'ignore').decode('ascii')
    return re.sub(r'\s+', ' ', texto)


def _normalizar_texto(texto: str) -> str:
    """Normaliza texto: ASCII, lematización spaCy si está disponible."""
    if pd.isna(texto):
        return ''
    texto = _preprocesar_ascii(texto)
    if not texto:
        return ''
    nlp = _get_nlp()
    if nlp is None:
        return texto
    doc = nlp(texto)
    lemmas = [
        t.lemma_ for t in doc
        if not t.is_stop and not t.is_punct and len(t.text) > 2
    ]
    return ' '.join(lemmas) if lemmas else texto


def _split_elementos_perfil(valor: str) -> List[str]:
    """
    Divide el valor del perfil en sub-elementos.
    Textos cortos (<=15 palabras) se mantienen enteros; textos largos
    solo se dividen si contienen delimitadores explícitos.
    """
    valor = str(valor).strip()
    if len(valor) <= 3:
        return []
    palabras = len(valor.split())
    if palabras <= 15:
        return [valor]
    if re.search(r'[/\n•–—]', valor):
        partes = re.split(r'[/\n•–—]+', valor)
        resultado = []
        for sub in partes:
            sub = sub.strip().strip('-').strip()
            if len(sub) > 3:
                resultado.append(sub)
        return resultado if resultado else [valor]
    return [valor]


def _umbral_para_campo(campo: str) -> float:
    return UMBRALES_POR_CAMPO.get(campo, UMBRAL_COBERTURA)


def _score_top_k_ponderado(sim_row: np.ndarray) -> Tuple[float, int]:
    """Promedio ponderado de los 3 mejores scores coseno; retorna (score, idx_mejor)."""
    if sim_row.size == 0:
        return 0.0, 0
    orden = np.argsort(sim_row)[::-1]
    k = min(3, len(orden))
    top_idx = orden[:k]
    top_scores = sim_row[top_idx]
    pesos = PESOS_TOP_K[:k]
    pesos = pesos / pesos.sum()
    score = float(np.dot(top_scores, pesos))
    return score, int(top_idx[0])


def _score_bm25_normalizado(elemento_norm: str, corpus: List[str]) -> float:
    """Score BM25 máximo normalizado a [0, 1]."""
    global _bm25_available
    if _bm25_available is False:
        return 0.0
    try:
        from rank_bm25 import BM25Okapi
        _bm25_available = True
    except ImportError:
        _bm25_available = False
        logger.debug('rank_bm25 no instalado; score BM25 omitido')
        return 0.0

    tokenized = [doc.split() for doc in corpus if doc.strip()]
    if not tokenized:
        return 0.0
    bm25 = BM25Okapi(tokenized)
    query = elemento_norm.split()
    if not query:
        return 0.0
    scores = bm25.get_scores(query)
    max_s = float(np.max(scores)) if len(scores) else 0.0
    if max_s <= 0:
        return 0.0
    # Normalización suave respecto al máximo observado en el corpus para esta query
    return min(1.0, max_s / (max_s + 2.0))


def extraer_elementos_perfil(df_perfil: pd.DataFrame) -> List[Dict[str, str]]:
    """
    Extrae elementos del perfil de egreso desde un DataFrame de Paso1.
    """
    elementos = []
    if df_perfil.empty:
        logger.warning("DataFrame de perfil vacío, no hay elementos que extraer")
        return elementos

    for _, row in df_perfil.iterrows():
        for campo in COLUMNAS_PERFIL:
            if campo not in df_perfil.columns:
                continue
            valor = row.get(campo, '')
            if pd.isna(valor) or not str(valor).strip():
                continue
            for sub in _split_elementos_perfil(valor):
                elementos.append({
                    'campo': campo,
                    'elemento': sub,
                    'elemento_norm': _normalizar_texto(sub),
                })
    logger.info(f"Extraídos {len(elementos)} elementos del perfil de egreso")
    return elementos


def _asignatura_de_fila(row: pd.Series) -> str:
    for col in ASIGNATURA_COLS:
        if col in row.index and pd.notna(row.get(col)):
            val = str(row[col]).strip()
            if val:
                return val[:80]
    return ''


def construir_corpus_curriculo(
    df_micro: pd.DataFrame,
    df_ra: pd.DataFrame
) -> Tuple[List[str], List[Dict[str, str]]]:
    """
    Construye el corpus curricular y metadatos de trazabilidad por documento.

    Returns:
        (corpus, corpus_fuente) donde cada fuente tiene:
        columna, asignatura, texto_display
    """
    corpus: List[str] = []
    corpus_fuente: List[Dict[str, str]] = []

    if not df_micro.empty:
        for col in COLUMNAS_CURRICULO['Paso5']:
            if col not in df_micro.columns:
                continue
            for _, row in df_micro.iterrows():
                val = row.get(col)
                if pd.isna(val) or len(str(val).strip()) <= 3:
                    continue
                norm = _normalizar_texto(val)
                if len(norm) <= 3:
                    continue
                asig = _asignatura_de_fila(row) or col
                corpus.append(norm)
                corpus_fuente.append({
                    'columna': col,
                    'asignatura': asig,
                    'texto_display': str(val).strip()[:120],
                })

    if not df_ra.empty:
        for col in COLUMNAS_CURRICULO['Paso3']:
            if col not in df_ra.columns:
                continue
            for _, row in df_ra.iterrows():
                val = row.get(col)
                if pd.isna(val) or len(str(val).strip()) <= 3:
                    continue
                norm = _normalizar_texto(val)
                if len(norm) <= 3:
                    continue
                asig = _asignatura_de_fila(row) or 'Saber asociado (Paso 3)'
                corpus.append(norm)
                corpus_fuente.append({
                    'columna': col,
                    'asignatura': asig,
                    'texto_display': str(val).strip()[:120],
                })

    logger.info(f"Corpus curricular construido con {len(corpus)} documentos")
    return corpus, corpus_fuente


def calcular_cobertura_elemento(
    elemento_norm: str,
    corpus: List[str],
    corpus_fuente: Optional[List[Dict[str, str]]] = None,
    vectorizer: Optional[TfidfVectorizer] = None,
    tfidf_matrix=None,
) -> Tuple[float, int, str, str]:
    """
    Calcula score híbrido (coseno top-3 + BM25) y trazabilidad del mejor match.

    Returns:
        (score, idx_mejor, asignatura_trazable, doc_trazable)
    """
    vacio = (0.0, -1, '', '')
    if not corpus or len(corpus) < 3 or not elemento_norm.strip():
        return vacio

    if vectorizer is None or tfidf_matrix is None:
        vectorizer = TfidfVectorizer(**TFIDF_KWARGS)
        tfidf_matrix = vectorizer.fit_transform(corpus)

    elemento_vec = vectorizer.transform([elemento_norm])
    sim = cosine_similarity(elemento_vec, tfidf_matrix)
    score_coseno, idx_mejor = _score_top_k_ponderado(sim[0])

    score_bm25 = _score_bm25_normalizado(elemento_norm, corpus)
    score = PESO_COSENO * score_coseno + PESO_BM25 * score_bm25
    score = min(1.0, max(0.0, score))

    if score < 0.01:
        return 0.0, -1, '', ''

    asignatura_trazable = ''
    doc_trazable = ''
    if corpus_fuente and 0 <= idx_mejor < len(corpus_fuente):
        fuente = corpus_fuente[idx_mejor]
        asignatura_trazable = fuente.get('asignatura', '')
        col = fuente.get('columna', '')
        texto = fuente.get('texto_display', '')
        doc_trazable = f"{col}: {texto}" if col else texto

    return score, idx_mejor, asignatura_trazable, doc_trazable


def _calcular_cobertura_por_campo(elementos_con_score: List[Dict]) -> Dict[str, float]:
    """Porcentaje de elementos CUBIERTO por campo del perfil."""
    por_campo: Dict[str, Dict[str, int]] = {}
    for e in elementos_con_score:
        campo = e['campo']
        por_campo.setdefault(campo, {'total': 0, 'cubiertos': 0})
        por_campo[campo]['total'] += 1
        if e['clasificacion'] == 'CUBIERTO':
            por_campo[campo]['cubiertos'] += 1
    return {
        campo: round(stats['cubiertos'] / stats['total'] * 100, 1)
        if stats['total'] > 0 else 0.0
        for campo, stats in por_campo.items()
    }


def _elemento_resultado_vacio(elem: Dict, umbral: float) -> Dict[str, Any]:
    return {
        'campo': elem['campo'],
        'elemento': elem['elemento'],
        'score': 0.0,
        'umbral': umbral,
        'clasificacion': 'BRECHA',
        'asignatura_trazable': '',
        'doc_trazable': '',
    }


def analizar_cobertura_perfil_completa(
    df_perfil: pd.DataFrame,
    df_micro: pd.DataFrame,
    df_ra: pd.DataFrame
) -> Dict:
    """
    Ejecuta el análisis completo de cobertura del perfil de egreso.
    """
    resultado: Dict[str, Any] = {
        'programa': '',
        'total_elementos': 0,
        'cobertura_global': 0.0,
        'cobertura_por_campo': {},
        'elementos': [],
        'brechas': [],
        'num_brechas': 0,
        'recomendaciones': [],
        'corpus_size': 0,
    }

    if df_perfil.empty:
        logger.warning("Perfil de egreso vacío, no se puede analizar cobertura")
        return resultado

    programa = df_perfil.get('Programa_Archivo', df_perfil.get('Programa', ['']))
    resultado['programa'] = str(programa.iloc[0]) if hasattr(programa, 'iloc') else str(programa)

    elementos = extraer_elementos_perfil(df_perfil)
    if not elementos:
        logger.warning("No se extrajeron elementos del perfil")
        return resultado

    corpus, corpus_fuente = construir_corpus_curriculo(df_micro, df_ra)
    resultado['corpus_size'] = len(corpus)

    if len(corpus) < 3:
        logger.warning(f"Corpus insuficiente ({len(corpus)} docs), todos los scores serán 0")
        for elem in elementos:
            resultado['elementos'].append(
                _elemento_resultado_vacio(elem, _umbral_para_campo(elem['campo']))
            )
        resultado['total_elementos'] = len(elementos)
        resultado['brechas'] = resultado['elementos']
        resultado['num_brechas'] = len(resultado['brechas'])
        resultado['cobertura_global'] = 0.0
        resultado['cobertura_por_campo'] = _calcular_cobertura_por_campo(resultado['elementos'])
        return resultado

    vectorizer = TfidfVectorizer(**TFIDF_KWARGS)
    tfidf_matrix = vectorizer.fit_transform(corpus)

    elementos_con_score = []
    for elem in elementos:
        umbral = _umbral_para_campo(elem['campo'])
        score, _, asig_traz, doc_traz = calcular_cobertura_elemento(
            elem['elemento_norm'],
            corpus,
            corpus_fuente,
            vectorizer,
            tfidf_matrix,
        )
        clasificacion = 'CUBIERTO' if score >= umbral else 'BRECHA'
        elementos_con_score.append({
            'campo': elem['campo'],
            'elemento': elem['elemento'],
            'score': round(score, 4),
            'umbral': umbral,
            'clasificacion': clasificacion,
            'asignatura_trazable': asig_traz,
            'doc_trazable': doc_traz,
        })

    brechas = [e for e in elementos_con_score if e['clasificacion'] == 'BRECHA']
    num_brechas = len(brechas)
    total = len(elementos_con_score)
    cobertura_global = round(
        (total - num_brechas) / total * 100, 1
    ) if total > 0 else 0.0

    recomendaciones = []
    if num_brechas > 5:
        recomendaciones.append(
            f"Hay {num_brechas} brechas ({cobertura_global}% cobertura). "
            "Revisar los elementos del perfil con baja representación curricular."
        )
    if cobertura_global < 40:
        recomendaciones.append(
            "La cobertura global es crítica (< 40%). "
            "Se recomienda una revisión completa del perfil de egreso vs. el currículo."
        )
    brecha_campos: Dict[str, int] = {}
    for b in brechas:
        brecha_campos.setdefault(b['campo'], 0)
        brecha_campos[b['campo']] += 1
    for campo, count in sorted(brecha_campos.items(), key=lambda x: -x[1]):
        recomendaciones.append(
            f"Campo '{campo}': {count} elemento(s) sin cobertura. "
            "Evaluar si es necesario reforzar en el plan de estudios."
        )
        # Recomendación con trazabilidad inversa: elementos cubiertos en el mismo campo
        cubiertos_campo = [
            e for e in elementos_con_score
            if e['campo'] == campo and e['clasificacion'] == 'CUBIERTO' and e.get('asignatura_trazable')
        ]
        if cubiertos_campo:
            ref = cubiertos_campo[0]
            recomendaciones.append(
                f"  Referencia en '{campo}': revisar contenido de "
                f"{ref['asignatura_trazable']} (score {ref['score']:.0%})."
            )

    resultado['total_elementos'] = total
    resultado['cobertura_global'] = cobertura_global
    resultado['cobertura_por_campo'] = _calcular_cobertura_por_campo(elementos_con_score)
    resultado['elementos'] = elementos_con_score
    resultado['brechas'] = brechas
    resultado['num_brechas'] = num_brechas
    resultado['recomendaciones'] = recomendaciones

    logger.info(
        f"Cobertura perfil {resultado['programa']}: "
        f"{cobertura_global}% ({total - num_brechas}/{total} cubiertos)"
    )
    return resultado


if __name__ == '__main__':
    print("Módulo de Análisis de Cobertura del Perfil de Egreso")
    print("Ejecutar desde run_analysis.py para uso completo.")
