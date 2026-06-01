"""
Limpieza y filtrado de núcleos temáticos.

Reutiliza y extiende la lógica de _limpiar_nucleo() y _es_nucleo_valido()
de dashboard_tematico.py, agregando razones de rechazo, score académico,
detección de anomalías y pipeline sobre DataFrames.
"""

import logging
import re
import unicodedata
from typing import List, Tuple, Optional
import pandas as pd
import numpy as np
from collections import Counter
from sklearn.feature_extraction.text import TfidfVectorizer

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from config import NUCLEOS_CONFIG

logger = logging.getLogger(__name__)

# Patrones reutilizados de dashboard_tematico.py
_PATRON_NO_NUCLEO = re.compile(
    r'^(construccion\s+y\s+dinamicas?|dinamicas?\s+de|estrategias?\s+de\s+(ensenanza|aprendizaje|evaluacion)|'
    r'actividades?\s+(de\s+)?(aprendizaje|evaluacion)|metodologia|criterios?\s+de|recursos?\s+(educativos?|didacticos?)|'
    r'indicadores?\s+de|competencias?\s+(generales?|especificas?)|resultados?\s+de\s+aprendizaje|'
    r'nucleo\s+tematico|temas?\s+a\s+(desarrollar|tratar)|contenido[s]?\s*(del?\s+)?curso|'
    r'unidad\s+(tematica\s+)?\d*|modulo\s+\d*|semana\s+\d*|bloque\s+(tematico)?\s*\d*)',
    re.IGNORECASE
)

_INICIO_INVALIDO = re.compile(
    r'^(o |y |e |u |ni |pero |sino |aunque |mas |porque |pues |'
    r'de |del |al |a |en |con |sin |por |para |'
    r'lo |la |el |los |las |un |una |'
    r'que |si |su |sus |se |le |les )',
    re.IGNORECASE
)

# Terminan con letra suelta tipo "Expansión A", "Tema B" (truncamiento)
_FINAL_LETRA_SUELTA = re.compile(r'\s+[A-Za-z]$')

_KEYWORDS_ACADEMICAS_POS = [
    'analisis', 'fundamentacion', 'teorica', 'practica', 'aplicacion',
    'evaluacion', 'diagnostico', 'planeacion', 'gestion', 'desarrollo',
    'investigacion', 'innovacion', 'estrategia', 'metodologia', 'sistema',
    'proceso', 'modelo', 'marco', 'enfoque', 'metodo', 'tecnica',
    'herramienta', 'instrumento', 'indicador', 'variable', 'factor',
    'componente', 'elemento', 'estructura', 'funcion', 'mecanismo',
]

_KEYWORDS_ACADEMICAS_NEG = [
    'taller', 'ejercicio', 'practica', 'lectura', 'exposicion', 'debate',
    'salida', 'campo', 'visita', 'conferencia', 'seminario', 'charla',
    'introduccion', 'bienvenida', 'presentacion', 'generalidades',
    'induccion', 'nivelacion', 'repaso', 'repaso general',
]


def _normalizar(texto: str) -> str:
    """Normaliza texto: minúsculas, sin tildes."""
    return unicodedata.normalize(
        'NFKD', texto.lower()
    ).encode('ascii', 'ignore').decode('ascii')


def limpiar_nucleo(texto: str) -> str:
    """Elimina numeración inicial y viñetas de un núcleo temático."""
    t = texto.strip()
    t = re.sub(r'^\d+[\.\)]\s*', '', t)
    t = re.sub(r'^[•\-–—*]\s*', '', t)
    return t.strip()


def tokenizar_nucleo_celda(texto_celda: str) -> List[str]:
    """
    Separa el contenido de una celda en sub-ítems (núcleos individuales).

    Divide por punto y coma, salto de línea, pipe, y también por items
    numerados tipo '1. Núcleo' o '2) Núcleo'.

    Args:
        texto_celda: Texto crudo de la celda de núcleos temáticos

    Returns:
        Lista de strings con cada núcleo individual
    """
    if pd.isna(texto_celda) or not str(texto_celda).strip():
        return []
    texto = str(texto_celda)
    partes = re.split(r'[;\n\|]+', texto)
    resultado = []
    for p in partes:
        sub = re.split(r'(?<!\d)(?=\d+[\.\)]\s+\w)', p)
        for s in sub:
            s = s.strip()
            if s and s != 'nan':
                resultado.append(s)
    return resultado


def es_nucleo_valido(texto: str) -> Tuple[bool, str]:
    """
    Verifica si un texto es un núcleo temático válido, retornando
    (valido, razon_rechazo).

    Filtros en cascada:
    1. Longitud (MIN_LONGITUD - MAX_LONGITUD)
    2. Solo números/caracteres especiales
    3. Mínimo de palabras (MIN_PALABRAS)
    4. Patrones no temáticos (encabezados, instrucciones)
    5. Fragmentos de expresión compuesta (empiezan con conjunción/preposición)

    Args:
        texto: String del núcleo a validar

    Returns:
        Tuple[bool, str]: (True, '') si es válido, (False, 'razón') si no
    """
    t = texto.strip()
    if len(t) < NUCLEOS_CONFIG['MIN_LONGITUD']:
        return False, f"Demasiado corto ({len(t)} chars, min {NUCLEOS_CONFIG['MIN_LONGITUD']})"
    if len(t) > NUCLEOS_CONFIG['MAX_LONGITUD']:
        return False, f"Demasiado largo ({len(t)} chars, max {NUCLEOS_CONFIG['MAX_LONGITUD']})"
    if re.match(r'^[\d\s\.\,\;\:\-]+$', t):
        return False, "Solo números o caracteres especiales"
    if len(t.split()) < NUCLEOS_CONFIG['MIN_PALABRAS']:
        return False, f"Menos de {NUCLEOS_CONFIG['MIN_PALABRAS']} palabras"
    t_norm = _normalizar(t)
    if _PATRON_NO_NUCLEO.match(t_norm):
        return False, "Patrón de encabezado/instrucción"
    t_clean_norm = _normalizar(limpiar_nucleo(t))
    if _INICIO_INVALIDO.match(t_clean_norm):
        return False, "Fragmento de expresión compuesta"
    if _FINAL_LETRA_SUELTA.search(t_norm):
        return False, "Termina con letra suelta (probable trunca miento)"
    return True, ''


def calcular_score_academico(texto: str) -> float:
    """
    Calcula un score académico (0-1) para un núcleo temático basado en
    keywords positivas y negativas.

    Args:
        texto: Núcleo temático

    Returns:
        Score entre 0 y 1
    """
    t = _normalizar(texto)
    palabras = t.split()
    if not palabras:
        return 0.0
    pos = sum(1 for kw in _KEYWORDS_ACADEMICAS_POS if kw in t)
    neg = sum(1 for kw in _KEYWORDS_ACADEMICAS_NEG if kw in t)
    total = len(palabras)
    if total == 0:
        return 0.0
    score = (pos * 0.15 + total * 0.02) - (neg * 0.1)
    score = max(0.0, min(1.0, score))
    return round(score, 4)


def filtrar_nucleos_dataframe(
    df: pd.DataFrame,
    columna: str = 'Núcleos temáticos'
) -> pd.DataFrame:
    """
    Aplica el pipeline completo de filtrado de núcleos sobre un DataFrame.

    Por cada celda de la columna especificada:
    1. Tokeniza en sub-ítems
    2. Limpia cada sub-ítem
    3. Valida cada sub-ítem
    4. Calcula score académico
    5. Clasifica como válido/rechazado

    Args:
        df: DataFrame con columna de núcleos
        columna: Nombre de la columna que contiene los núcleos

    Returns:
        DataFrame con columnas adicionales:
        - nucleo_tokenizado: lista de ítems individuales
        - nucleos_validos: lista de núcleos válidos
        - nucleos_rechazados: lista de dicts {texto, razon}
        - nucleos_scores: dict {nucleo: score}
    """
    resultados = []
    for _, row in df.iterrows():
        raw = str(row.get(columna, ''))
        if raw == 'nan' or not raw.strip():
            resultados.append({
                'nucleo_tokenizado': [],
                'nucleos_validos': [],
                'nucleos_rechazados': [],
                'nucleos_scores': {}
            })
            continue

        items = tokenizar_nucleo_celda(raw)
        validos = []
        rechazados = []
        scores = {}
        for item in items:
            limpio = limpiar_nucleo(item)
            valido, razon = es_nucleo_valido(limpio)
            if valido:
                validos.append(limpio)
                scores[limpio] = calcular_score_academico(limpio)
            else:
                rechazados.append({'texto': limpio, 'razon': razon})

        resultados.append({
            'nucleo_tokenizado': items,
            'nucleos_validos': validos,
            'nucleos_rechazados': rechazados,
            'nucleos_scores': scores
        })

    df_resultado = df.copy()
    df_resultado['nucleo_tokenizado'] = [r['nucleo_tokenizado'] for r in resultados]
    df_resultado['nucleos_validos'] = [r['nucleos_validos'] for r in resultados]
    df_resultado['nucleos_rechazados'] = [r['nucleos_rechazados'] for r in resultados]
    df_resultado['nucleos_scores'] = [r['nucleos_scores'] for r in resultados]

    total_antes = sum(len(r['nucleo_tokenizado']) for r in resultados)
    total_aceptados = sum(len(r['nucleos_validos']) for r in resultados)
    total_rechazados = sum(len(r['nucleos_rechazados']) for r in resultados)
    tasa_rechazo = (total_rechazados / total_antes * 100) if total_antes > 0 else 0
    logger.info(
        f"Filtrado completado: {total_aceptados} válidos, "
        f"{total_rechazados} rechazados ({tasa_rechazo:.1f}%)"
    )
    return df_resultado


def detectar_anomalias_nucleos(
    series: pd.Series,
    contamination: Optional[float] = None
) -> pd.Series:
    """
    Detecta núcleos anómalos usando Isolation Forest sobre TF-IDF.

    Args:
        series: Serie de strings (núcleos temáticos)
        contamination: Fracción esperada de anomalías (default de NUCLEOS_CONFIG)

    Returns:
        Serie booleana: True si el núcleo es anómalo
    """
    if contamination is None:
        contamination = NUCLEOS_CONFIG['CONTAMINATION_IF']

    limpios = series.dropna().astype(str)
    limpios = limpios[limpios.str.strip() != '']

    if len(limpios) < 10:
        logger.warning(
            f"Menos de 10 muestras ({len(limpios)}), "
            "no se puede ejecutar Isolation Forest. Retornando False."
        )
        return pd.Series([False] * len(series), index=series.index)

    vectorizer = TfidfVectorizer(max_features=100, min_df=1, max_df=0.9)
    tfidf = vectorizer.fit_transform(limpios)
    from sklearn.ensemble import IsolationForest
    modelo = IsolationForest(
        contamination=contamination,
        random_state=42
    )
    predicciones = modelo.fit_predict(tfidf.toarray())
    anomalo = pd.Series(predicciones == -1, index=limpios.index)
    n_anomalos = anomalo.sum()
    logger.info(f"Anomalías detectadas: {n_anomalos}/{len(limpios)} ({n_anomalos/len(limpios)*100:.1f}%)")
    resultado = pd.Series([False] * len(series), index=series.index)
    resultado.loc[limpios.index] = anomalo
    return resultado


if __name__ == '__main__':
    sample = "1. Análisis financiero de estados contables\n2. Fundamentación teórica y técnica contable\n3. Expansión A\n4. Salgamos"
    items = tokenizar_nucleo_celda(sample)
    print(f"Items: {items}")
    for item in items:
        limpio = limpiar_nucleo(item)
        valido, razon = es_nucleo_valido(limpio)
        score = calcular_score_academico(limpio) if valido else 0
        print(f"  '{limpio}' -> válido={valido}, razón='{razon}', score={score}")
