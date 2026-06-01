"""
Análisis de Cobertura del Perfil de Egreso.

Mide qué tan cubiertos están los elementos del perfil de egreso
(Saber, SaberHacer, SaberSer, Áreas profesionales, Tareas profesionales,
Valor agregado) por el corpus curricular (SaberAsociado, Indicadores de logro,
Núcleos temáticos) usando TF-IDF + similitud coseno.
"""

import logging
import re
import unicodedata
from typing import Dict, List, Tuple, Optional
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from config import NUCLEOS_CONFIG, UMBRAL_COBERTURA, COLUMNAS_PERFIL

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


def _normalizar_texto(texto: str) -> str:
    """Normaliza texto: minúsculas, sin tildes, espacios simples."""
    if pd.isna(texto):
        return ''
    texto = str(texto).lower().strip()
    texto = unicodedata.normalize('NFKD', texto)
    texto = texto.encode('ascii', 'ignore').decode('ascii')
    texto = re.sub(r'\s+', ' ', texto)
    return texto


def extraer_elementos_perfil(df_perfil: pd.DataFrame) -> List[Dict[str, str]]:
    """
    Extrae elementos del perfil de egreso desde un DataFrame de Paso1.

    Cada elemento del perfil se divide por '/' o '\\n' para obtener
    sub-elementos individuales (ej: 'Saber conocer / Saber comprender').

    Args:
        df_perfil: DataFrame con columnas de PERFIL_EGRESO

    Returns:
        Lista de dicts: [{'campo': 'Saber', 'elemento': 'saber conocer', ...}]
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
            sub_elementos = re.split(r'[/\n•–—]+', str(valor))
            for sub in sub_elementos:
                sub = sub.strip().strip('-').strip()
                if len(sub) > 3:
                    elementos.append({
                        'campo': campo,
                        'elemento': sub,
                        'elemento_norm': _normalizar_texto(sub)
                    })
    logger.info(f"Extraídos {len(elementos)} elementos del perfil de egreso")
    return elementos


def construir_corpus_curriculo(
    df_micro: pd.DataFrame,
    df_ra: pd.DataFrame
) -> List[str]:
    """
    Construye el corpus curricular combinando SaberAsociado (Paso3) con
    Indicadores de logro, Núcleos temáticos y Actividades (Paso5).

    SaberAsociado se incluye con peso doble (se duplica).

    Args:
        df_micro: DataFrame de Paso5 (estrategias_micro)
        df_ra: DataFrame de Paso3 (resultados_aprendizaje)

    Returns:
        Lista de strings del corpus curricular
    """
    corpus = []

    if not df_micro.empty:
        for col in COLUMNAS_CURRICULO['Paso5']:
            if col in df_micro.columns:
                textos = df_micro[col].dropna().astype(str)
                corpus.extend([_normalizar_texto(t) for t in textos if len(str(t)) > 3])

    if not df_ra.empty:
        for col in COLUMNAS_CURRICULO['Paso3']:
            if col in df_ra.columns:
                textos = df_ra[col].dropna().astype(str)
                textos_norm = [_normalizar_texto(t) for t in textos if len(str(t)) > 3]
                corpus.extend(textos_norm)
                corpus.extend(textos_norm)

    logger.info(f"Corpus curricular construido con {len(corpus)} documentos")
    return corpus


def calcular_cobertura_elemento(
    elemento_norm: str,
    corpus: List[str],
    vectorizer: Optional[TfidfVectorizer] = None,
    tfidf_matrix=None
) -> float:
    """
    Calcula el score de cobertura (0-1) de un elemento del perfil
    contra el corpus curricular usando similitud coseno.

    Args:
        elemento_norm: Elemento del perfil normalizado
        corpus: Lista de textos del corpus curricular
        vectorizer: TfidfVectorizer ya entrenado (opcional, para batch)
        tfidf_matrix: Matriz TF-IDF ya transformada (opcional, para batch)

    Returns:
        Score de cobertura entre 0 y 1
    """
    if not corpus or len(corpus) < 3:
        logger.debug("Corpus muy pequeño (< 3 docs), score=0")
        return 0.0

    if vectorizer is None or tfidf_matrix is None:
        vectorizer = TfidfVectorizer(
            max_features=500,
            min_df=1,
            max_df=0.85,
            ngram_range=(1, 3),
            stop_words=['el', 'la', 'de', 'que', 'y', 'a', 'en', 'un', 'ser', 'se',
                        'no', 'por', 'con', 'su', 'para', 'como', 'estar', 'tener',
                        'le', 'lo', 'del', 'las', 'los', 'al', 'una', 'es', 'e']
        )
        tfidf_matrix = vectorizer.fit_transform(corpus)

    elemento_vec = vectorizer.transform([elemento_norm])
    sim = cosine_similarity(elemento_vec, tfidf_matrix)
    score = float(sim.max())
    return score


def analizar_cobertura_perfil_completa(
    df_perfil: pd.DataFrame,
    df_micro: pd.DataFrame,
    df_ra: pd.DataFrame
) -> Dict:
    """
    Ejecuta el análisis completo de cobertura del perfil de egreso.

    Args:
        df_perfil: DataFrame de Paso1 (perfil_egreso)
        df_micro: DataFrame de Paso5 (estrategias_micro)
        df_ra: DataFrame de Paso3 (resultados_aprendizaje)

    Returns:
        Dict con estructura:
        {
            'programa': str,
            'total_elementos': int,
            'cobertura_global': float,
            'elementos': [{'campo': str, 'elemento': str, 'score': float, 'clasificacion': str}],
            'brechas': [elementos con score < 0.35],
            'num_brechas': int,
            'recomendaciones': [str],
            'corpus_size': int
        }
    """
    resultado = {
        'programa': '',
        'total_elementos': 0,
        'cobertura_global': 0.0,
        'elementos': [],
        'brechas': [],
        'num_brechas': 0,
        'recomendaciones': [],
        'corpus_size': 0
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

    corpus = construir_corpus_curriculo(df_micro, df_ra)
    resultado['corpus_size'] = len(corpus)

    if len(corpus) < 3:
        logger.warning(f"Corpus insuficiente ({len(corpus)} docs), todos los scores serán 0")
        for elem in elementos:
            resultado['elementos'].append({
                'campo': elem['campo'],
                'elemento': elem['elemento'],
                'score': 0.0,
                'clasificacion': 'BRECHA'
            })
        resultado['total_elementos'] = len(elementos)
        resultado['brechas'] = resultado['elementos']
        resultado['num_brechas'] = len(resultado['brechas'])
        resultado['cobertura_global'] = 0.0
        return resultado

    vectorizer = TfidfVectorizer(
        max_features=500,
        min_df=1,
        max_df=0.85,
        ngram_range=(1, 3),
        stop_words=['el', 'la', 'de', 'que', 'y', 'a', 'en', 'un', 'ser', 'se',
                    'no', 'por', 'con', 'su', 'para', 'como', 'estar', 'tener',
                    'le', 'lo', 'del', 'las', 'los', 'al', 'una', 'es', 'e']
    )
    tfidf_matrix = vectorizer.fit_transform(corpus)

    elementos_con_score = []
    for elem in elementos:
        score = calcular_cobertura_elemento(
            elem['elemento_norm'], corpus, vectorizer, tfidf_matrix
        )
        clasificacion = 'CUBIERTO' if score >= UMBRAL_COBERTURA else 'BRECHA'
        elementos_con_score.append({
            'campo': elem['campo'],
            'elemento': elem['elemento'],
            'score': round(score, 4),
            'clasificacion': clasificacion
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
    brecha_campos = {}
    for b in brechas:
        brecha_campos.setdefault(b['campo'], 0)
        brecha_campos[b['campo']] += 1
    for campo, count in sorted(brecha_campos.items(), key=lambda x: -x[1]):
        recomendaciones.append(
            f"Campo '{campo}': {count} elemento(s) sin cobertura. "
            "Evaluar si es necesario reforzar en el plan de estudios."
        )

    resultado['total_elementos'] = total
    resultado['cobertura_global'] = cobertura_global
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
