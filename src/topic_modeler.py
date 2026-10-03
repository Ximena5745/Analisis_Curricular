"""
Modelado de tópicos (LDA) sobre los núcleos temáticos depurados (Etapa 2).

Un documento = un núcleo temático (ítem numerado de la celda de núcleos).

Descubre temáticas latentes en el corpus curricular para identificar
familias de conocimiento y agrupaciones temáticas entre programas.
"""

import logging
import re
import unicodedata
from typing import Dict, List
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

logger = logging.getLogger(__name__)

N_TOPICS_DEFAULT = 13
N_TOP_WORDS = 15
STOPWORDS = [
    # Artículos, preposiciones, conjunciones
    'el', 'la', 'de', 'que', 'y', 'a', 'en', 'un', 'ser', 'se',
    'no', 'por', 'con', 'su', 'para', 'como', 'estar', 'tener',
    'le', 'lo', 'del', 'las', 'los', 'al', 'una', 'es', 'e', 'o',
    'pero', 'mas', 'este', 'entre', 'porque', 'cuando', 'muy',
    'sin', 'vez', 'mucho', 'saber', 'sobre', 'tambien', 'hasta',
    'hay', 'donde', 'quien', 'desde', 'todos', 'durante', 'uno',
    'les', 'ni', 'contra', 'otros', 'fueron', 'ese', 'eso', 'ante',
    'ellos', 'esto', 'mi', 'antes', 'algunos', 'unos', 'yo',
    'te', 'ti', 'nos', 'cada', 'asi',
    # Términos académicos estructurales genéricos que producen tópicos
    # poco interpretables (p.ej. T3 con «generalidades», T10 con «antropoceno»
    # era un artefacto de términos muy raros y muy frecuentes a la vez).
    # Se añaden aquí para que el LDA no los use como palabras representativas
    # de un tópico — no se eliminan del corpus, solo de las features.
    'generalidades', 'introduccion', 'conceptos', 'basicos', 'fundamentos',
    'aspectos', 'elementos', 'principios', 'nociones', 'nociones basicas',
    'teoria', 'marco', 'general', 'aplicacion', 'aplicaciones',
    'proceso', 'procesos', 'sistema', 'sistemas', 'gestion',
    'analisis', 'desarrollo', 'implementacion', 'evaluacion',
    'metodologia', 'metodo', 'tecnica', 'herramienta', 'modelo',
    # Términos de bajo poder discriminativo en currículo universitario
    'estudiante', 'estudiantes', 'docente', 'aprendizaje', 'ensenanza',
    'competencia', 'competencias', 'resultado', 'objetivo', 'actividad',
    'estrategia', 'area', 'campo', 'nivel', 'tipo', 'forma', 'uso', 'manera',
]


def _normalizar(texto: str) -> str:
    if pd.isna(texto):
        return ''
    t = unicodedata.normalize('NFKD', str(texto))
    t = t.encode('ascii', 'ignore').decode('ascii')
    t = t.lower().strip()
    t = re.sub(r'[^a-záéíóúñü\s]', ' ', t)
    t = re.sub(r'\s+', ' ', t)
    return t.strip()


def entrenar_lda(
    corpus: List[str],
    n_topics: int = N_TOPICS_DEFAULT,
    n_top_words: int = N_TOP_WORDS
) -> Dict:
    """
    Entrena un modelo LDA sobre el corpus de SaberAsociado.

    Args:
        corpus: Lista de textos (SaberAsociado de todos los programas)
        n_topics: Número de tópicos a extraer
        n_top_words: Palabras por tópico

    Returns:
        Dict con:
        - topics: lista de dicts {topic_id, top_words, weight}
        - topic_distribution: matriz documento → tópico
        - model: modelo LDA entrenado
        - vectorizer: CountVectorizer entrenado
        - feature_names: nombres de las features
    """
    corpus_limpio = [_normalizar(t) for t in corpus if pd.notna(t) and len(str(t)) > 5]

    if len(corpus_limpio) < n_topics:
        logger.warning(
            f"Corpus demasiado pequeño ({len(corpus_limpio)} docs) "
            f"para {n_topics} tópicos, ajustando a {max(2, len(corpus_limpio) // 2)}"
        )
        n_topics = max(2, len(corpus_limpio) // 2)

    if len(corpus_limpio) < 5:
        logger.warning("Corpus insuficiente (<5 docs), no se puede entrenar LDA")
        return {
            'topics': [],
            'topic_distribution': np.array([]),
            'model': None,
            'vectorizer': None,
            'feature_names': []
        }

    vectorizer = CountVectorizer(
        max_features=500,
        min_df=2,
        max_df=0.85,
        stop_words=STOPWORDS,
        ngram_range=(1, 2)
    )

    doc_word = vectorizer.fit_transform(corpus_limpio)
    feature_names = vectorizer.get_feature_names_out()

    lda = LatentDirichletAllocation(
        n_components=n_topics,
        random_state=42,
        max_iter=100,
        learning_method='batch'
    )
    lda.fit(doc_word)

    topics = []
    for topic_idx, topic in enumerate(lda.components_):
        top_indices = topic.argsort()[:-n_top_words - 1:-1]
        top_words = [feature_names[i] for i in top_indices]
        top_weights = [float(topic[i]) for i in top_indices]
        topics.append({
            'topic_id': topic_idx,
            'top_words': top_words,
            'top_weights': top_weights,
            'weight_sum': float(topic.sum())
        })

    topic_distribution = lda.transform(doc_word)

    logger.info(
        f"LDA entrenado: {n_topics} tópicos, "
        f"{len(corpus_limpio)} documentos, "
        f"{len(feature_names)} features"
    )
    return {
        'topics': topics,
        'topic_distribution': topic_distribution,
        'model': lda,
        'vectorizer': vectorizer,
        'feature_names': list(feature_names)
    }


def corpus_nucleos(df_micro: pd.DataFrame) -> pd.DataFrame:
    """
    Construye el corpus del LDA: un registro por núcleo temático depurado.

    Cada celda de núcleos (fila de inicio de la asignatura) se separa por su
    numeración con tokenizar_nucleo_celda y se aplica el control mínimo de
    es_nucleo_valido.

    Returns:
        DataFrame con columnas Programa y Nucleo.
    """
    from src.nucleos_cleaner import tokenizar_nucleo_celda, es_nucleo_valido
    col = next((c for c in df_micro.columns
                if _normalizar(c).replace(' ', '') == 'nucleostematicos'), None)
    if col is None:
        return pd.DataFrame(columns=['Programa', 'Nucleo'])
    filas = []
    for prog, celda in zip(df_micro.get('Programa', pd.Series('', index=df_micro.index)), df_micro[col]):
        if pd.isna(celda):
            continue
        filas += [{'Programa': prog, 'Nucleo': n} for n in tokenizar_nucleo_celda(celda) if es_nucleo_valido(n)]
    return pd.DataFrame(filas, columns=['Programa', 'Nucleo'])


# Parámetros del LDA de consenso (auditoría P14: k elegido por coherencia NPMI y
# estabilidad entre semillas para k = 5…30; ver auditoria/scripts/estabilidad_lda.py)
CONSENSO_LDA = dict(k=13, semillas=tuple(range(10)), max_iter=500, alfa=0.1, beta=0.01,
                    min_df=5, max_df=0.3, max_features=600)


def corpus_asignaturas(df_micro: pd.DataFrame) -> pd.DataFrame:
    """
    Corpus del análisis temático: un documento por asignatura con sus núcleos depurados.

    Se conserva una sola matriz por programa (la primera por nombre de archivo),
    porque las sedes de un programa multisede repiten sus contenidos.

    Returns:
        DataFrame con columnas Programa, Archivo, asignatura y texto.
    """
    from src.nucleos_cleaner import tokenizar_nucleo_celda, es_nucleo_valido
    col_nuc = next((c for c in df_micro.columns
                    if _normalizar(c).replace(' ', '') == 'nucleostematicos'), None)
    col_asig = next((c for c in df_micro.columns
                     if _normalizar(c).replace(' ', '') == 'nombreasignaturaomodulo'), None)
    if col_nuc is None or 'Programa' not in df_micro.columns:
        return pd.DataFrame(columns=['Programa', 'Archivo', 'asignatura', 'texto'])
    df = df_micro
    if 'Archivo' in df.columns:
        primera = df.groupby('Programa')['Archivo'].min()
        df = df[df['Archivo'] == df['Programa'].map(primera)]
    filas = []
    for _, r in df.iterrows():
        if pd.isna(r[col_nuc]):
            continue
        nuc = [n for n in tokenizar_nucleo_celda(r[col_nuc]) if es_nucleo_valido(n)]
        if nuc:
            filas.append({'Programa': r['Programa'], 'Archivo': r.get('Archivo', ''),
                          'asignatura': r[col_asig] if col_asig else '', 'texto': ' . '.join(nuc)})
    return pd.DataFrame(filas, columns=['Programa', 'Archivo', 'asignatura', 'texto'])


def _lematizar(textos: List[str]) -> List[str]:
    """Lemas de sustantivos, adjetivos y nombres propios (spaCy), sin tildes ni palabras vacías."""
    from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS
    vacias = set(_normalizar(' '.join(STOPWORDS)).split()) | set(ENGLISH_STOP_WORDS)
    try:
        import spacy
        nlp = spacy.load('es_core_news_sm', disable=['parser', 'ner'])
        vacias |= {_normalizar(w) for w in nlp.Defaults.stop_words}
        docs = [[_normalizar(t.lemma_) for t in d if t.pos_ in ('NOUN', 'ADJ', 'PROPN') and t.is_alpha]
                for d in nlp.pipe(textos, batch_size=64)]
    except (ImportError, OSError):
        logger.warning("spaCy/es_core_news_sm no disponible: se usa texto normalizado sin lematizar")
        docs = [_normalizar(t).split() for t in textos]
    return [' '.join(w for w in d if len(w) > 2 and w not in vacias) for d in docs]


def modelar_topicos_consenso(df_micro: pd.DataFrame, k: int = None, semillas=None) -> Dict:
    """
    LDA de consenso sobre las asignaturas (núcleos temáticos depurados).

    Entrena un LDA por semilla, agrupa los k × n_semillas tópicos por similitud
    coseno (clúster jerárquico promedio) en k grupos y promedia cada grupo. La
    distribución de cada asignatura es el promedio, entre semillas, de la
    probabilidad de los tópicos que caen en cada grupo.

    Returns:
        Dict con topics, asignatura_topico (Programa, asignatura, topico_dominante,
        confianza), programa_dist, corpus_size, k y semillas.
    """
    from sklearn.cluster import AgglomerativeClustering
    p = CONSENSO_LDA
    k = k or p['k']
    semillas = tuple(semillas) if semillas is not None else p['semillas']
    corpus = corpus_asignaturas(df_micro)
    vacio = {'topics': [], 'asignatura_topico': pd.DataFrame(), 'programa_dist': pd.DataFrame(),
             'corpus_size': len(corpus), 'k': k, 'semillas': list(semillas)}
    if len(corpus) < max(5, k):
        logger.warning("Corpus insuficiente para el LDA de consenso")
        return vacio

    docs = _lematizar(corpus['texto'].tolist())
    try:
        vec = CountVectorizer(max_features=p['max_features'], min_df=min(p['min_df'], len(docs)),
                              max_df=p['max_df'], ngram_range=(1, 2))
        X = vec.fit_transform(docs)
    except ValueError:
        # Corpus pequeño u homogéneo: max_df elimina todo el vocabulario
        vec = CountVectorizer(max_features=p['max_features'], min_df=1, ngram_range=(1, 2))
        X = vec.fit_transform(docs)
    fn = vec.get_feature_names_out()

    comps, dists = [], []
    for s in semillas:
        lda = LatentDirichletAllocation(n_components=k, random_state=s, max_iter=p['max_iter'],
                                        learning_method='batch', doc_topic_prior=p['alfa'],
                                        topic_word_prior=p['beta']).fit(X)
        comps.append(lda.components_ / lda.components_.sum(axis=1, keepdims=True))
        dists.append(lda.transform(X))
    C = np.vstack(comps)
    grupos = AgglomerativeClustering(n_clusters=k, metric='cosine', linkage='average').fit_predict(C)

    topicos_palabras = np.vstack([C[grupos == g].mean(axis=0) for g in range(k)])
    D = np.zeros((X.shape[0], k))
    for i, dist in enumerate(dists):
        for t in range(k):
            D[:, grupos[i * k + t]] += dist[:, t]
    D /= D.sum(axis=1, keepdims=True)

    topics = []
    for g, fila in enumerate(topicos_palabras):
        top = fila.argsort()[:-N_TOP_WORDS - 1:-1]
        topics.append({'topic_id': g, 'top_words': [fn[i] for i in top],
                       'top_weights': [float(fila[i]) for i in top],
                       'n_topicos_agrupados': int((grupos == g).sum())})

    asig = corpus[['Programa', 'asignatura']].copy()
    asig['topico_dominante'] = D.argmax(axis=1)
    asig['confianza'] = D.max(axis=1).round(4)
    prog = pd.DataFrame(D, columns=[f'topico_{t}' for t in range(k)])
    prog['programa'] = corpus['Programa'].values
    prog = prog.groupby('programa').mean().round(4).reset_index()

    logger.info(f"LDA de consenso: k={k}, {len(semillas)} semillas, {len(docs)} asignaturas, {len(fn)} términos")
    return {'topics': topics, 'asignatura_topico': asig, 'programa_dist': prog,
            'corpus_size': len(docs), 'k': k, 'semillas': list(semillas), 'model': 'consenso'}


def asignar_topicos_a_programas(
    df_ra: pd.DataFrame,
    n_topics: int = N_TOPICS_DEFAULT,
    columna: str = 'SaberAsociado'
) -> Dict:
    """
    Entrena LDA sobre la columna de texto indicada y asigna tópicos a cada documento.

    Args:
        df_ra: DataFrame con la columna de texto y Programa (p. ej. corpus_nucleos)
        n_topics: Número de tópicos
        columna: Columna de texto ('Nucleo' para el análisis del artículo)

    Returns:
        Dict con:
        - topics: lista de tópicos con palabras clave
        - programa_topico: DataFrame programa → tópico dominante
        - programa_dist: DataFrame programa → distribución completa de tópicos
    """
    if columna not in df_ra.columns:
        logger.error(f"Columna '{columna}' no encontrada")
        return {'topics': [], 'programa_topico': pd.DataFrame(), 'programa_dist': pd.DataFrame()}

    # Mismo filtro que entrenar_lda, para que cada fila de la distribución
    # corresponda a su programa
    df_ra = df_ra[df_ra[columna].notna() & (df_ra[columna].astype(str).str.len() > 5)]
    corpus = df_ra[columna].tolist()
    if len(corpus) < 5:
        logger.warning("Pocos documentos, no se puede entrenar LDA")
        return {'topics': [], 'programa_topico': pd.DataFrame(), 'programa_dist': pd.DataFrame()}

    resultado = entrenar_lda(corpus, n_topics=n_topics)
    if resultado['model'] is None:
        return {'topics': [], 'programa_topico': pd.DataFrame(), 'programa_dist': pd.DataFrame()}

    dist = resultado['topic_distribution']
    programas = df_ra['Programa'].values if 'Programa' in df_ra.columns else [f'Doc_{i}' for i in range(len(corpus))]

    rows_dist = []
    rows_topico = []
    for i, prog in enumerate(programas):
        if i >= dist.shape[0]:
            break
        dist_row = {'programa': prog}
        for t in range(dist.shape[1]):
            dist_row[f'topico_{t}'] = round(float(dist[i, t]), 4)
        rows_dist.append(dist_row)

        topico_dom = int(dist[i].argmax())
        confianza = float(dist[i].max())
        rows_topico.append({
            'programa': prog,
            'topico_dominante': topico_dom,
            'confianza': round(confianza, 4)
        })

    df_dist = pd.DataFrame(rows_dist) if rows_dist else pd.DataFrame()
    df_topico = pd.DataFrame(rows_topico) if rows_topico else pd.DataFrame()

    return {
        'topics': resultado['topics'],
        'programa_topico': df_topico,
        'programa_dist': df_dist,
        'model': resultado['model'],
        'corpus_size': len(corpus)
    }


def obtener_fingerprint_tfidf(df_ra: pd.DataFrame, n_terms: int = 10) -> pd.DataFrame:
    """
    Calcula el fingerprint TF-IDF de cada programa (términos únicos).

    Args:
        df_ra: DataFrame con SaberAsociado y Programa
        n_terms: Términos por programa

    Returns:
        DataFrame con programa y sus términos más distintivos
    """
    if 'SaberAsociado' not in df_ra.columns or 'Programa' not in df_ra.columns:
        return pd.DataFrame()

    from sklearn.feature_extraction.text import TfidfVectorizer

    programas = df_ra['Programa'].unique()
    corpus_por_programa = {}
    for prog in programas:
        textos = df_ra[df_ra['Programa'] == prog]['SaberAsociado'].dropna()
        texto = ' '.join([_normalizar(t) for t in textos if pd.notna(t)])
        if len(texto) > 10:
            corpus_por_programa[prog] = texto

    if len(corpus_por_programa) < 2:
        return pd.DataFrame()

    prog_names = list(corpus_por_programa.keys())
    textos = [corpus_por_programa[p] for p in prog_names]

    vectorizer = TfidfVectorizer(
        max_features=200, min_df=1, max_df=0.85,
        stop_words=STOPWORDS, ngram_range=(1, 2)
    )
    tfidf = vectorizer.fit_transform(textos)
    features = vectorizer.get_feature_names_out()

    rows = []
    for i, prog in enumerate(prog_names):
        row = tfidf[i].toarray()[0]
        top_idx = row.argsort()[-n_terms:][::-1]
        terms = [features[j] for j in top_idx if row[j] > 0]
        rows.append({'programa': prog, 'terminos_distintivos': ', '.join(terms[:n_terms])})

    return pd.DataFrame(rows)


if __name__ == '__main__':
    print("Módulo de Topic Modeling (LDA + Fingerprint TF-IDF)")
