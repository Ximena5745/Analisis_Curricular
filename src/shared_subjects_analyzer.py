"""
Análisis de asignaturas compartidas y divergencia inter-sede.

Orden de análisis:
1. Intra-sede: mismo programa en distintas sedes (PBOG vs HMED vs VNAL)
2. Inter-programa: programas distintos vs otros programas
3. Asignaturas con nombre exacto idéntico
"""

import logging
import re
import unicodedata
from typing import Dict
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))


logger = logging.getLogger(__name__)

UMBRAL_IDENTICO = 0.95
UMBRAL_SIMILAR = 0.60
# Contenido de una asignatura: indicadores de logro y núcleos temáticos. No se
# incluye el texto de los RA: es propio de cada programa y medía la diferencia
# entre programas, no entre asignaturas (auditoría P12b, 2026-10-02).
COLUMNAS_CONTENIDO = [
    'Nombre asignatura o módulo',
    'Indicadores de logro asignatura o módulo',
    'Núcleos temáticos',
]

# Vectorizador común para comparar contenidos de asignaturas
_TFIDF_ASIGNATURAS = dict(max_df=0.85, ngram_range=(1, 2), sublinear_tf=True)


def _clave_nombre(nombre) -> str:
    """Denominación normalizada: minúsculas, sin tildes ni puntuación."""
    t = _normalizar(nombre)
    return re.sub(r'\s+', ' ', re.sub(r'[^a-z0-9 ]', ' ', t)).strip()


def consolidar_asignaturas(df: pd.DataFrame) -> pd.DataFrame:
    """
    Una fila por asignatura de cada matriz (programa-sede) con su contenido.

    En el Paso 5 el nombre de la asignatura aparece solo en la primera fila de
    su bloque; las filas siguientes (otros RA) pertenecen a la misma
    asignatura. El contenido reúne los núcleos temáticos (separados por su
    numeración, decisión D7) y los indicadores de logro de todo el bloque. Se
    excluyen las filas de totales y los espacios electivos (nota N1).

    Returns:
        DataFrame con Programa, Sede, Codigo, asignatura, clave, texto
    """
    from src.nucleos_cleaner import tokenizar_nucleo_celda

    asig_col = _buscar_columna(df, 'Nombre asignatura o módulo')
    if asig_col is None or df.empty:
        return pd.DataFrame(columns=['Programa', 'Sede', 'Codigo', 'asignatura', 'clave', 'texto'])
    ind_col = _buscar_columna(df, 'Indicadores de logro asignatura o módulo')
    nuc_col = _buscar_columna(df, 'Núcleos temáticos')
    matriz_col = 'Archivo' if 'Archivo' in df.columns else 'Programa'

    filas, actual, matriz_actual = [], None, None
    for _, row in df.iterrows():
        if row.get(matriz_col) != matriz_actual:
            matriz_actual, actual = row.get(matriz_col), None
        nombre = row.get(asig_col)
        if pd.notna(nombre) and str(nombre).strip():
            nombre = str(nombre).strip()
            if re.fullmatch(r'[\d\.\s]+', nombre) or _clave_nombre(nombre).startswith('electiva'):
                actual = None
                continue
            actual = {'Programa': row.get('Programa'), 'Sede': row.get('Sede', ''),
                      'Codigo': row.get('Codigo_Sede', row.get('Codigo', '')),
                      'asignatura': nombre, 'clave': _clave_nombre(nombre), 'partes': []}
            filas.append(actual)
        if actual is None:
            continue
        if nuc_col is not None and pd.notna(row.get(nuc_col)):
            actual['partes'] += tokenizar_nucleo_celda(row.get(nuc_col))
        if ind_col is not None and pd.notna(row.get(ind_col)):
            actual['partes'].append(str(row.get(ind_col)))
    for f in filas:
        f['texto'] = _normalizar(' '.join(f.pop('partes')))
    return pd.DataFrame(filas)


def _normalizar(texto: str) -> str:
    if pd.isna(texto):
        return ''
    t = unicodedata.normalize('NFKD', str(texto))
    t = t.encode('ascii', 'ignore').decode('ascii')
    t = t.lower().strip()
    t = re.sub(r'\s+', ' ', t)
    return t


def _extraer_texto_asignatura(row: pd.Series) -> str:
    """
    Concatena columnas de contenido de una fila en un solo texto
    para calcular similitud.
    """
    partes = []
    for col in COLUMNAS_CONTENIDO[1:]:
        val = row.get(col, '')
        if pd.notna(val) and str(val).strip() and str(val) != 'nan':
            partes.append(_normalizar(str(val)))
    return ' '.join(partes)


def _buscar_columna(df: pd.DataFrame, target: str):
    """Busca columna por nombre normalizado."""
    target_norm = _normalizar(target).replace(' ', '')
    for col in df.columns:
        col_norm = _normalizar(col).replace(' ', '')
        if col_norm == target_norm:
            return col
    return None


def detectar_asignaturas_identicas(df: pd.DataFrame) -> pd.DataFrame:
    """
    Encuentra asignaturas con el mismo nombre exacto en múltiples
    programas o sedes.

    Args:
        df: DataFrame consolidado con columnas Programa, Sede,
            Nombre asignatura o módulo

    Returns:
        DataFrame con columnas: nombre_asignatura, programas (lista),
            sedes (lista), num_programas
    """
    asig_col = _buscar_columna(df, 'Nombre asignatura o módulo')
    if asig_col is None:
        logger.warning("Columna 'Nombre asignatura o módulo' no encontrada")
        return pd.DataFrame()

    # Denominación normalizada, sin electivas ni filas de totales
    df = consolidar_asignaturas(df)
    if df.empty:
        return pd.DataFrame()
    asig_col = 'clave'

    agrupado = (
        df.groupby(asig_col)
        .agg(
            nombre=('asignatura', 'first'),
            programas=('Programa', lambda x: list(dict.fromkeys(x))),
            sedes=('Sede', lambda x: list(dict.fromkeys(x))),
            conteo_programas=('Programa', 'nunique'),
            conteo_sedes=('Sede', 'nunique')
        )
        .reset_index()
    )

    multiples_programas = agrupado[agrupado['conteo_programas'] > 1].copy()
    multiples_programas = multiples_programas.sort_values('conteo_programas', ascending=False)
    multiples_programas = multiples_programas.drop(columns=asig_col).rename(columns={'nombre': 'nombre_asignatura'})

    logger.info(
        f"Asignaturas idénticas: {len(multiples_programas)} "
        f"compartidas entre múltiples programas"
    )
    return multiples_programas


def comparar_intra_sede(df: pd.DataFrame) -> pd.DataFrame:
    """
    PASO 1: Compara el mismo programa en distintas sedes.
    Calcula similitud coseno entre asignaturas del mismo programa
    base pero en distintas sedes.

    Args:
        df: DataFrame consolidado con todos los programas

    Returns:
        DataFrame con pares (programa, sede_a, sede_b, similitud, n_asignaturas_compartidas)
    """
    asig_col = _buscar_columna(df, 'Nombre asignatura o módulo')
    if asig_col is None:
        return pd.DataFrame()

    programas = df.groupby('Programa')
    resultados = []

    for prog_name, grupo in programas:
        sedes = grupo['Sede'].dropna().unique()
        if len(sedes) < 2:
            continue

        for i in range(len(sedes)):
            for j in range(i + 1, len(sedes)):
                    sede_a, sede_b = sedes[i], sedes[j]
                    grupo_a = grupo[grupo['Sede'] == sede_a]
                    grupo_b = grupo[grupo['Sede'] == sede_b]

                    asignaturas_a = set(
                        grupo_a[asig_col].dropna().astype(str).str.strip()
                    )
                    asignaturas_b = set(
                        grupo_b[asig_col].dropna().astype(str).str.strip()
                    )

                    compartidos = asignaturas_a & asignaturas_b
                    union = asignaturas_a | asignaturas_b
                    jaccard = len(compartidos) / len(union) if union else 0

                    textos_a = [_extraer_texto_asignatura(row)
                                for _, row in grupo_a.iterrows()]
                    textos_b = [_extraer_texto_asignatura(row)
                                for _, row in grupo_b.iterrows()]

                    similitud_semantica = 0.0
                    if textos_a and textos_b:
                        corpus = textos_a + textos_b
                        try:
                            vectorizer = TfidfVectorizer(
                                max_features=200, min_df=1, max_df=0.9,
                                ngram_range=(1, 2)
                            )
                            tfidf = vectorizer.fit_transform(corpus)
                            n_a = len(textos_a)
                            sim = cosine_similarity(
                                tfidf[:n_a], tfidf[n_a:]
                            )
                            similitud_semantica = float(sim.max())
                        except Exception:
                            pass

                    resultados.append({
                        'programa': prog_name,
                        'sede_a': sede_a,
                        'sede_b': sede_b,
                        'codigo_a': grupo_a['Codigo'].iloc[0] if 'Codigo' in grupo_a.columns else '',
                        'codigo_b': grupo_b['Codigo'].iloc[0] if 'Codigo' in grupo_b.columns else '',
                        'asignaturas_a': len(asignaturas_a),
                        'asignaturas_b': len(asignaturas_b),
                        'asignaturas_compartidas': len(compartidos),
                        'jaccard_similitud': round(jaccard, 4),
                        'similitud_semantica_max': round(similitud_semantica, 4),
                        'n_asignaturas_a': len(grupo_a),
                        'n_asignaturas_b': len(grupo_b)
                    })

    df_resultado = pd.DataFrame(resultados)
    if not df_resultado.empty:
        df_resultado = df_resultado.sort_values(
            'similitud_semantica_max', ascending=False
        )
    logger.info(
        f"Intra-sede: {len(df_resultado)} pares de sedes comparados "
        f"para {df_resultado['programa'].nunique() if not df_resultado.empty else 0} programas"
    )
    return df_resultado


def comparar_inter_programa(
    df: pd.DataFrame,
    umbral_identico: float = UMBRAL_IDENTICO,
    umbral_similar: float = UMBRAL_SIMILAR,
    max_asignaturas: int = None
) -> pd.DataFrame:
    """
    PASO 2: Compara las asignaturas de programas distintos por contenido.

    Usa todas las asignaturas consolidadas (sin muestreo; auditoría P12) y
    reporta los pares de programas distintos con similitud >= umbral_similar.
    La columna 'mismo_nombre' separa las asignaturas homónimas de las que
    tienen nombre distinto y cubren lo mismo.

    Args:
        df: DataFrame consolidado del Paso 5
        umbral_identico: Similitud para considerar idéntico (0.95)
        umbral_similar: Similitud mínima para reportar (0.60; sin calibración documentada)
        max_asignaturas: Solo para pruebas: limita el número de asignaturas

    Returns:
        DataFrame con pares inter-programa, similitud y categoría
    """
    df_asigs = consolidar_asignaturas(df)
    df_asigs = df_asigs[df_asigs['texto'].str.len() > 5].reset_index(drop=True)
    if df_asigs['Programa'].nunique() < 2:
        logger.warning("Se requieren al menos 2 programas para comparación inter-programa")
        return pd.DataFrame()
    if max_asignaturas is not None and len(df_asigs) > max_asignaturas:
        df_asigs = df_asigs.head(max_asignaturas)

    try:
        tfidf = TfidfVectorizer(**_TFIDF_ASIGNATURAS).fit_transform(df_asigs['texto'])
        sim_matrix = cosine_similarity(tfidf)
    except Exception as e:
        logger.error(f"Error vectorizando: {e}")
        return pd.DataFrame()

    programas = df_asigs['Programa'].to_numpy()
    distinto = programas[:, None] != programas[None, :]
    filas_i, filas_j = np.where(np.triu(sim_matrix >= umbral_similar, k=1) & distinto)
    pares = [{
        'programa_a': df_asigs.at[i, 'Programa'], 'sede_a': df_asigs.at[i, 'Sede'],
        'asignatura_a': df_asigs.at[i, 'asignatura'],
        'programa_b': df_asigs.at[j, 'Programa'], 'sede_b': df_asigs.at[j, 'Sede'],
        'asignatura_b': df_asigs.at[j, 'asignatura'],
        'mismo_nombre': df_asigs.at[i, 'clave'] == df_asigs.at[j, 'clave'],
        'similitud': round(float(sim_matrix[i, j]), 4),
    } for i, j in zip(filas_i, filas_j)]

    df_pares = pd.DataFrame(pares)
    if df_pares.empty:
        logger.info("No se encontraron pares similares entre programas")
        return df_pares

    df_pares['categoria'] = df_pares['similitud'].apply(
        lambda s: 'IDENTICO' if s >= umbral_identico else 'SIMILAR'
    )
    df_pares = df_pares.sort_values('similitud', ascending=False)

    logger.info(
        f"Inter-programa: {len(df_pares)} pares de {len(df_asigs)} asignaturas "
        f"({(~df_pares['mismo_nombre']).sum()} con nombre distinto)"
    )
    return df_pares


def divergencia_homonimas(df: pd.DataFrame, umbral: float = UMBRAL_SIMILAR) -> pd.DataFrame:
    """
    Similitud de contenido de las asignaturas homónimas (misma denominación
    normalizada en dos o más programas). Para cada una se promedia la
    similitud coseno entre sus versiones de programas distintos; las versiones
    de sedes de un mismo programa no se comparan entre sí (auditoría P12b).

    Returns:
        DataFrame con asignatura, programas, versiones, similitud_media y
        divergente (similitud_media < umbral)
    """
    df_asigs = consolidar_asignaturas(df).reset_index(drop=True)
    if df_asigs.empty:
        return pd.DataFrame()
    try:
        tfidf = TfidfVectorizer(**_TFIDF_ASIGNATURAS).fit_transform(df_asigs['texto'])
    except ValueError as e:  # textos sin vocabulario utilizable
        logger.warning(f"Divergencia de homónimas no calculada: {e}")
        return pd.DataFrame()
    filas = []
    for clave, idx in df_asigs.groupby('clave').groups.items():
        idx = list(idx)
        if df_asigs.loc[idx, 'Programa'].nunique() < 2:
            continue
        sim = cosine_similarity(tfidf[idx])
        progs = df_asigs.loc[idx, 'Programa'].to_numpy()
        mascara = np.triu(progs[:, None] != progs[None, :], k=1)
        filas.append({
            'asignatura': df_asigs.at[idx[0], 'asignatura'],
            'programas': int(df_asigs.loc[idx, 'Programa'].nunique()),
            'versiones': len(idx),
            'similitud_media': round(float(sim[mascara].mean()), 3),
        })
    res = pd.DataFrame(filas)
    if res.empty:
        return res
    res['divergente'] = res['similitud_media'] < umbral
    return res.sort_values('similitud_media').reset_index(drop=True)


def generar_recomendaciones(df_pares: pd.DataFrame) -> pd.DataFrame:
    """
    Genera recomendaciones para cada par de asignaturas similares.

    Args:
        df_pares: DataFrame de salida de comparar_inter_programa()

    Returns:
        DataFrame con columna adicional 'recomendacion'
    """
    if df_pares.empty:
        return df_pares

    df = df_pares.copy()

    def _recomendar(row):
        sim = row['similitud']
        if sim >= 0.95:
            return 'UNIFICAR'
        elif sim >= 0.80:
            return 'HOMOLOGAR'
        else:
            return 'COORDINAR'

    df['recomendacion'] = df.apply(_recomendar, axis=1)
    return df


def detectar_asignaturas_compartidas(df: pd.DataFrame) -> Dict:
    """
    Ejecuta el pipeline completo de detección de asignaturas compartidas.

    Args:
        df: DataFrame consolidado de estrategias_micro de todos los programas
            Debe contener columnas: Programa, Sede, Codigo,
            Nombre asignatura o módulo, y las columnas de contenido

    Returns:
        Dict con estructura:
        {
            'intra_sede': DataFrame con pares intra-sede,
            'inter_programa': DataFrame con pares inter-programa + recomendaciones,
            'asignaturas_identicas': DataFrame con nombres idénticos,
            'resumen': dict con métricas globales
        }
    """
    if df.empty:
        logger.warning("DataFrame vacío, no se puede ejecutar análisis")
        return {
            'intra_sede': pd.DataFrame(),
            'inter_programa': pd.DataFrame(),
            'asignaturas_identicas': pd.DataFrame(),
            'resumen': {
                'total_programas': 0,
                'programas_multi_sede': 0,
                'pares_intra_sede': 0,
                'pares_inter_programa': 0,
                'asignaturas_identicas': 0
            }
        }

    asig_col = _buscar_columna(df, 'Nombre asignatura o módulo')
    if asig_col is None:
        logger.error("Columna 'Nombre asignatura o módulo' no encontrada")
        return {'intra_sede': pd.DataFrame(), 'inter_programa': pd.DataFrame(),
                'asignaturas_identicas': pd.DataFrame(), 'resumen': {}}

    logger.info("Iniciando detección de asignaturas compartidas")

    # PASO 1: Intra-sede
    logger.info("PASO 1: Comparación intra-sede (mismo programa, distintas sedes)")
    df_intra = comparar_intra_sede(df)

    # PASO 2: Inter-programa
    logger.info("PASO 2: Comparación inter-programa")
    df_inter = comparar_inter_programa(df)
    df_inter = generar_recomendaciones(df_inter)

    # Asignaturas idénticas (homónimas) y su divergencia de contenido
    df_identicas = detectar_asignaturas_identicas(df)
    df_homonimas = divergencia_homonimas(df)

    n_programas = df['Programa'].nunique()
    programas_multi = df_intra['programa'].nunique() if not df_intra.empty else 0

    resumen = {
        'total_programas': n_programas,
        'programas_multi_sede': programas_multi,
        'pares_intra_sede': len(df_intra),
        'pares_inter_programa': len(df_inter),
        'pares_inter_identicos': len(df_inter[df_inter['categoria'] == 'IDENTICO']) if not df_inter.empty else 0,
        'asignaturas_identicas': len(df_identicas),
        'pares_inter_nombre_distinto': int((~df_inter['mismo_nombre']).sum()) if not df_inter.empty else 0,
        'homonimas_divergentes': int(df_homonimas['divergente'].sum()) if not df_homonimas.empty else 0,
        'pct_homonimas_divergentes': round(100 * df_homonimas['divergente'].mean(), 1) if not df_homonimas.empty else 0.0,
    }

    logger.info(f"Análisis completado: {resumen}")
    return {
        'intra_sede': df_intra,
        'inter_programa': df_inter,
        'asignaturas_identicas': df_identicas,
        'homonimas': df_homonimas,
        'resumen': resumen
    }


if __name__ == '__main__':
    print("Módulo de Análisis de Asignaturas Compartidas e Inter-Sede")
    print("Ejecutar desde run_analysis.py para uso completo.")
