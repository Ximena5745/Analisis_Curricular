"""
DASHBOARD INTERACTIVO - Analisis Tematico Avanzado
Compatible con Streamlit Cloud y ejecucion local.

Ejecutar local: streamlit run dashboard_tematico.py
Deploy cloud:   Subir repo a GitHub y conectar en share.streamlit.io
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from collections import Counter
import re
import json
import unicodedata
import io
from typing import Dict
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from scipy.stats import entropy
import warnings
warnings.filterwarnings('ignore')


def _limpiar_nucleo(texto: str) -> str:
    """Elimina numeracion inicial tipo '1. ', '2. ', etc. de un nucleo tematico."""
    return re.sub(r'^\d+\.\s*', '', texto)


# ============================================================================
# CONFIGURACION DE PAGINA
# ============================================================================

st.set_page_config(
    page_title="Analisis Tematico Microcurricular",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# TENDENCIAS GLOBALES POR DEFECTO
# ============================================================================

TENDENCIAS_DEFAULT = {
    "SOSTENIBILIDAD": {
        "keywords": [
            "sostenibilidad", "sostenible", "desarrollo sostenible",
            "ODS", "objetivos desarrollo", "medio ambiente", "ambiental",
            "ecologia", "verde", "cambio climatico", "huella carbono",
            "economia circular", "recursos naturales"
        ],
        "color": "#2ECC71",
        "descripcion": "Sostenibilidad y Desarrollo Sostenible (ODS)"
    },
    "INTELIGENCIA_ARTIFICIAL": {
        "keywords": [
            "inteligencia artificial", "IA", "machine learning", "aprendizaje automatico",
            "deep learning", "redes neuronales", "algoritmos", "big data",
            "data science", "ciencia datos", "analytics", "mineria datos",
            "chatbot", "NLP", "vision artificial"
        ],
        "color": "#3498DB",
        "descripcion": "Inteligencia Artificial y Tecnologias Emergentes"
    },
    "TRANSFORMACION_DIGITAL": {
        "keywords": [
            "transformacion digital", "digitalizacion", "digital",
            "industria 4.0", "automatizacion", "robotica",
            "internet cosas", "IoT", "cloud computing", "nube",
            "ciberseguridad", "blockchain", "tecnologia"
        ],
        "color": "#9B59B6",
        "descripcion": "Transformacion Digital e Industria 4.0"
    },
    "INNOVACION": {
        "keywords": [
            "innovacion", "innovar", "emprendimiento", "emprender",
            "startup", "creatividad", "disrupcion", "disruptivo",
            "Design thinking", "lean", "agil", "prototipo"
        ],
        "color": "#E74C3C",
        "descripcion": "Innovacion y Emprendimiento"
    },
    "ETICA": {
        "keywords": [
            "etica", "valores", "responsabilidad social", "RSE", "RSC",
            "deontologia", "codigo etico", "integridad",
            "transparencia", "buen gobierno", "compliance"
        ],
        "color": "#F39C12",
        "descripcion": "Etica, Valores y Responsabilidad Social"
    },
    "GLOBALIZACION": {
        "keywords": [
            "globalizacion", "global", "internacional", "glocal",
            "interculturalidad", "multicultural", "diversidad cultural",
            "comercio internacional", "exportacion", "importacion"
        ],
        "color": "#1ABC9C",
        "descripcion": "Globalizacion y Perspectiva Glocal"
    },
    "LIDERAZGO": {
        "keywords": [
            "liderazgo", "trabajo equipo", "colaborativo", "comunicacion",
            "habilidades blandas", "soft skills", "gestion personas",
            "talento humano", "coaching", "mentoring", "negociacion"
        ],
        "color": "#E67E22",
        "descripcion": "Liderazgo y Habilidades Blandas"
    },
    "ANALISIS_DATOS": {
        "keywords": [
            "analisis datos", "estadistica", "data analytics",
            "visualizacion datos", "business intelligence", "BI",
            "dashboard", "metricas", "KPI", "indicadores",
            "toma decisiones basada datos"
        ],
        "color": "#16A085",
        "descripcion": "Analisis de Datos y Business Intelligence"
    },
    "GESTION_CAMBIO": {
        "keywords": [
            "gestion cambio", "adaptabilidad", "resiliencia",
            "agilidad organizacional", "transformacion organizacional",
            "cultura organizacional", "cambio organizacional"
        ],
        "color": "#8E44AD",
        "descripcion": "Gestion del Cambio y Adaptabilidad"
    },
    "CALIDAD": {
        "keywords": [
            "calidad", "mejora continua", "excelencia",
            "ISO", "normas", "estandares", "certificacion",
            "auditoria", "procesos", "eficiencia", "productividad"
        ],
        "color": "#27AE60",
        "descripcion": "Calidad y Mejora Continua"
    }
}

STOPWORDS_ES = set([
    'el', 'la', 'de', 'que', 'y', 'a', 'en', 'un', 'ser', 'se', 'no', 'haber',
    'por', 'con', 'su', 'para', 'como', 'estar', 'tener', 'le', 'lo', 'todo',
    'pero', 'mas', 'hacer', 'o', 'poder', 'decir', 'este', 'ir', 'otro', 'ese',
    'la', 'si', 'me', 'ya', 'ver', 'porque', 'dar', 'cuando', 'muy', 'sin',
    'vez', 'mucho', 'saber', 'que', 'sobre', 'tambien', 'me', 'hasta', 'hay',
    'donde', 'quien', 'desde', 'todos', 'durante', 'uno', 'les', 'ni',
    'contra', 'otros', 'fueron', 'ese', 'eso', 'ante', 'ellos', 'e', 'esto',
    'mi', 'antes', 'algunos', 'unos', 'yo', 'del', 'las', 'los', 'al',
    'una', 'nos', 'te', 'ti'
])


# ============================================================================
# FUNCIONES DE CARGA DE DATOS
# ============================================================================

def normalizar_columnas(df: pd.DataFrame) -> pd.DataFrame:
    """Normaliza nombres de columnas eliminando tildes."""
    nuevos_nombres = {}
    for col in df.columns:
        nfkd = unicodedata.normalize('NFKD', str(col))
        sin_acentos = ''.join(c for c in nfkd if not unicodedata.combining(c))
        nuevos_nombres[col] = sin_acentos
    return df.rename(columns=nuevos_nombres)


def procesar_archivos(uploaded_files) -> pd.DataFrame:
    """Procesa archivos Excel subidos y consolida datos."""
    all_data = []

    for uploaded_file in uploaded_files:
        nombre = uploaded_file.name
        programa_nombre = (
            nombre
            .replace("FormatoRA_", "")
            .replace("_PBOG", "")
            .replace("_VNAL", "")
            .replace("_PMED", "")
            .replace(".xlsx", "")
            .replace(".xls", "")
        )
        try:
            df = pd.read_excel(
                uploaded_file,
                sheet_name='Paso 5 Estrategias micro',
                header=1,
                engine='openpyxl'
            )
            df = normalizar_columnas(df)
            df['Programa'] = programa_nombre
            all_data.append(df)
        except Exception as e:
            st.sidebar.warning(f"Error en {nombre}: {str(e)[:60]}")
            continue

    if not all_data:
        return pd.DataFrame()

    df_consolidado = pd.concat(all_data, ignore_index=True)

    # Filtrar Tipo de Saber vacio
    df_consolidado = df_consolidado[df_consolidado['Tipo de Saber'].notna()]
    df_consolidado = df_consolidado[
        df_consolidado['Tipo de Saber'].astype(str).str.strip() != ''
    ]

    # Normalizar Tipo de Saber
    norm_map = {
        'saber': 'Saber', 'saberhacer': 'SaberHacer', 'saberser': 'SaberSer',
        'Saber': 'Saber', 'SaberHacer': 'SaberHacer', 'SaberSer': 'SaberSer',
        'Saberhacer': 'SaberHacer', 'Saberser': 'SaberSer'
    }
    df_consolidado['Tipo de Saber'] = (
        df_consolidado['Tipo de Saber'].astype(str).str.strip()
        .map(lambda x: norm_map.get(x, x))
    )

    # Preparar texto combinado
    df_consolidado['Texto_Completo'] = (
        df_consolidado['Resultado de aprendizaje'].fillna('') + ' ' +
        df_consolidado['Nombre asignatura o modulo'].fillna('') + ' ' +
        df_consolidado['Indicadores de logro asignatura o modulo'].fillna('') + ' ' +
        df_consolidado['Nucleos tematicos'].fillna('')
    ).str.lower().str.strip()

    return df_consolidado


def obtener_tendencias() -> Dict:
    """Obtiene tendencias desde session_state o usa las por defecto."""
    if 'tendencias' not in st.session_state:
        st.session_state['tendencias'] = json.loads(json.dumps(TENDENCIAS_DEFAULT))
    return st.session_state['tendencias']


# ============================================================================
# FUNCIONES DE ANALISIS
# ============================================================================

def analizar_cobertura(df: pd.DataFrame) -> Dict:
    """Analisis de cobertura y densidad tematica."""
    nucleos_list = []
    for _, row in df.iterrows():
        nucleos_raw = str(row.get('Nucleos tematicos', ''))
        if nucleos_raw and nucleos_raw != 'nan':
            nucleos = re.split(r'[,;\n]+', nucleos_raw)
            nucleos = [_limpiar_nucleo(n.strip()) for n in nucleos if n.strip() and len(n.strip()) > 3]
            nucleos_list.extend(nucleos)

    nucleos_counter = Counter(nucleos_list)

    # Densidad por asignatura
    densidad = df.groupby('Nombre asignatura o modulo')['Nucleos tematicos'].apply(
        lambda x: len(re.split(r'[,;\n]+', ' '.join(x.fillna('').astype(str))))
    ).sort_values(ascending=False)

    # Shannon entropy
    if len(nucleos_counter) > 1:
        frecuencias = np.array(list(nucleos_counter.values()))
        probabilidades = frecuencias / frecuencias.sum()
        shannon = entropy(probabilidades, base=2)
        max_ent = np.log2(len(nucleos_counter))
        diversidad = (shannon / max_ent) * 100
    else:
        shannon = 0
        diversidad = 0

    # Matriz programa x nucleo (top 20)
    top_20 = [n for n, _ in nucleos_counter.most_common(20)]
    matriz = pd.DataFrame(0, index=df['Programa'].unique(), columns=top_20)
    for _, row in df.iterrows():
        programa = row['Programa']
        nucleos_raw = str(row.get('Nucleos tematicos', ''))
        if nucleos_raw and nucleos_raw != 'nan':
            nucleos = re.split(r'[,;\n]+', nucleos_raw)
            for nucleo in [_limpiar_nucleo(n.strip()) for n in nucleos if n.strip()]:
                if nucleo in top_20:
                    matriz.loc[programa, nucleo] += 1

    return {
        'nucleos_counter': nucleos_counter,
        'nucleos_unicos': len(nucleos_counter),
        'total_menciones': sum(nucleos_counter.values()),
        'densidad_asignatura': densidad,
        'promedio_densidad': densidad.mean(),
        'shannon': shannon,
        'diversidad': diversidad,
        'matriz_cobertura': matriz
    }


def analizar_tendencias(df: pd.DataFrame, tendencias: Dict) -> Dict:
    """Detecta tendencias globales en los datos.

    Cobertura = % de asignaturas unicas que abordan la tendencia
    (no % de programas). Esto refleja cuantas materias del total
    trabajan cada tendencia.
    """
    programas = df['Programa'].unique()
    asig_col = 'Nombre asignatura o modulo'
    total_asigs = df[asig_col].nunique()

    matriz = pd.DataFrame(0, index=programas, columns=list(tendencias.keys()))
    detalle = {t: {p: [] for p in programas} for t in tendencias}
    # Sets de asignaturas unicas que tocan cada tendencia
    asig_sets = {tid: set() for tid in tendencias}

    for _, row in df.iterrows():
        programa = row['Programa']
        texto = str(row.get('Texto_Completo', '')).lower()
        asig_raw = row.get(asig_col, '')
        asig_str = (
            str(asig_raw).strip()
            if pd.notna(asig_raw) and str(asig_raw).strip() not in ('nan', '')
            else ''
        )

        for tid, tinfo in tendencias.items():
            for kw in tinfo['keywords']:
                if kw.lower() in texto:
                    matriz.loc[programa, tid] += 1
                    if asig_str:
                        asig_sets[tid].add(asig_str)
                    campos = []
                    if kw.lower() in str(row.get('Resultado de aprendizaje', '')).lower():
                        campos.append('RA')
                    if kw.lower() in str(row.get('Nucleos tematicos', '')).lower():
                        campos.append('Nucleos')
                    if kw.lower() in str(row.get('Indicadores de logro asignatura o modulo', '')).lower():
                        campos.append('Indicadores')
                    detalle[tid][programa].append({
                        'keyword': kw,
                        'campos': campos,
                        'asignatura': asig_str if asig_str else 'Sin nombre'
                    })
                    break

    # Cobertura = % de asignaturas unicas que abordan la tendencia
    cobertura = {}
    asig_counts = {}
    for tid in tendencias:
        n_asigs = len(asig_sets[tid])
        asig_counts[tid] = n_asigs
        cobertura[tid] = (n_asigs / total_asigs * 100) if total_asigs > 0 else 0

    ausentes = [tid for tid, pct in cobertura.items() if pct == 0]

    return {
        'matriz': matriz,
        'cobertura': cobertura,
        'detalle': detalle,
        'ausentes': ausentes,
        'asig_sets': asig_sets,
        'asig_counts': asig_counts,
        'total_asigs': total_asigs
    }


def analizar_nlp(df: pd.DataFrame) -> Dict:
    """Analisis de mineria de texto con TF-IDF (terminos y n-gramas).
    La similitud entre asignaturas se calcula de forma interactiva en la pagina.
    """
    vectorizer = TfidfVectorizer(
        max_features=100, min_df=2, max_df=0.8,
        stop_words=list(STOPWORDS_ES), ngram_range=(1, 3)
    )
    tfidf_matrix = vectorizer.fit_transform(df['Texto_Completo'])
    features = vectorizer.get_feature_names_out()
    tfidf_sum = tfidf_matrix.sum(axis=0).A1
    top_idx = tfidf_sum.argsort()[::-1][:30]
    top_terminos = {features[i]: float(tfidf_sum[i]) for i in top_idx}

    # TF-IDF por programa
    top_por_programa = {}
    for programa in df['Programa'].unique():
        df_p = df[df['Programa'] == programa]
        if len(df_p) < 5:
            continue
        vec_p = TfidfVectorizer(
            max_features=50, min_df=2, max_df=0.85,
            stop_words=list(STOPWORDS_ES), ngram_range=(1, 2)
        )
        try:
            tfidf_p = vec_p.fit_transform(df_p['Texto_Completo'])
            feat_p = vec_p.get_feature_names_out()
            sum_p = tfidf_p.sum(axis=0).A1
            idx_p = sum_p.argsort()[::-1][:20]
            top_por_programa[programa] = {feat_p[i]: float(sum_p[i]) for i in idx_p}
        except Exception:
            continue

    # N-gramas
    vec_ng = CountVectorizer(
        ngram_range=(2, 3), max_features=30,
        stop_words=list(STOPWORDS_ES), min_df=2
    )
    try:
        ng_matrix = vec_ng.fit_transform(df['Texto_Completo'])
        ng_count = ng_matrix.sum(axis=0).A1
        ng_names = vec_ng.get_feature_names_out()
        top_ngrams = sorted(
            [(ng_names[i], int(ng_count[i])) for i in range(len(ng_names))],
            key=lambda x: x[1], reverse=True
        )[:20]
    except Exception:
        top_ngrams = []

    return {
        'top_terminos': top_terminos,
        'top_por_programa': top_por_programa,
        'top_ngrams': dict(top_ngrams)
    }


def calcular_similitud_asignaturas(df_filtrado: pd.DataFrame) -> Dict:
    """Calcula similitud coseno entre asignaturas del dataframe filtrado."""
    asig_col = 'Nombre asignatura o modulo'
    df_asig = df_filtrado.groupby(asig_col)['Texto_Completo'].apply(
        lambda x: ' '.join(x)
    ).reset_index()

    if len(df_asig) < 3:
        return {'similitud_df': pd.DataFrame(), 'par_similar': None, 'n_asignaturas': len(df_asig)}

    vec_asig = TfidfVectorizer(max_features=50, stop_words=list(STOPWORDS_ES))
    tfidf_asig = vec_asig.fit_transform(df_asig['Texto_Completo'])
    sim = cosine_similarity(tfidf_asig)
    similitud_df = pd.DataFrame(
        sim,
        index=df_asig[asig_col],
        columns=df_asig[asig_col]
    )
    sim_copy = sim.copy()
    np.fill_diagonal(sim_copy, 0)
    max_idx = np.unravel_index(sim_copy.argmax(), sim_copy.shape)
    par_similar = {
        'asig1': df_asig.iloc[max_idx[0]][asig_col],
        'asig2': df_asig.iloc[max_idx[1]][asig_col],
        'similitud': float(sim_copy[max_idx])
    }
    return {
        'similitud_df': similitud_df,
        'par_similar': par_similar,
        'n_asignaturas': len(df_asig)
    }


# ============================================================================
# PAGINAS DEL DASHBOARD
# ============================================================================

def _creditos_unicos_programa(grupo: pd.DataFrame) -> int:
    """Suma créditos únicos por asignatura (sin duplicar por número de RAs)."""
    asig_col = 'Nombre asignatura o modulo'
    cred_col = 'Creditos'
    if asig_col not in grupo.columns or cred_col not in grupo.columns:
        return 0
    # Un crédito por asignatura única (primer valor no nulo)
    cred = (
        grupo.dropna(subset=[asig_col])
        .groupby(asig_col)[cred_col]
        .first()
    )
    cred_num = pd.to_numeric(cred, errors='coerce').fillna(0)
    return int(cred_num[cred_num > 0].sum())


def pagina_inicio(df: pd.DataFrame):
    """Pagina de inicio con metricas generales."""
    st.title("Análisis Temático Microcurricular")
    st.markdown("---")
    st.info(
        "**Bienvenido/a.** Este dashboard analiza los microcurrículos de los programas "
        "académicos en tres dimensiones principales: **cobertura temática** (qué temas se trabajan "
        "y con qué profundidad), **tendencias globales** (alineación con retos del mundo actual) y "
        "**análisis de texto** (conceptos clave, similitudes y redundancias). "
        "Navega por las secciones del menú lateral para explorar cada dimensión."
    )

    programas = df['Programa'].unique()
    asignaturas = df['Nombre asignatura o modulo'].nunique()
    total_registros = len(df)
    total_palabras = df['Texto_Completo'].str.split().str.len().sum()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric(
        "Programas Cargados", len(programas),
        help="Número de programas académicos incluidos en el análisis"
    )
    col2.metric(
        "Registros Analizados", f"{total_registros:,}",
        help=(
            "Cada registro corresponde a una fila de estrategia microcurricular "
            "(un Resultado de Aprendizaje de una asignatura). "
            "Una asignatura puede tener varios registros."
        )
    )
    col3.metric(
        "Asignaturas Únicas", asignaturas,
        help="Número de asignaturas o módulos distintos en todos los programas"
    )
    col4.metric(
        "Palabras Analizadas", f"{int(total_palabras):,}",
        help="Total de palabras en los textos de RA, núcleos temáticos e indicadores de logro"
    )

    st.markdown("---")

    col_a, col_b = st.columns(2)

    with col_a:
        st.subheader("Registros por Programa")
        st.caption(
            "Número de filas de estrategia microcurricular por programa. "
            "Programas con más registros tienen mayor detalle de planeación por asignatura."
        )
        conteo = df['Programa'].value_counts().reset_index()
        conteo.columns = ['Programa', 'Registros']
        fig = px.bar(conteo, x='Programa', y='Registros',
                     color='Programa', text='Registros',
                     labels={'Registros': 'N° de registros'})
        fig.update_layout(showlegend=False, height=400)
        st.plotly_chart(fig, use_container_width=True)

    with col_b:
        st.subheader("Distribución Tipo de Saber (todos los programas)")
        st.caption(
            "**Saber** = conocimiento teórico/conceptual. "
            "**SaberHacer** = habilidades prácticas y procedimentales. "
            "**SaberSer** = actitudes, valores y dimensión ética. "
            "Un currículo equilibrado debería contemplar los tres tipos."
        )
        tipo_saber = df['Tipo de Saber'].value_counts().reset_index()
        tipo_saber.columns = ['Tipo', 'Cantidad']
        fig = px.pie(tipo_saber, values='Cantidad', names='Tipo',
                     color_discrete_sequence=px.colors.qualitative.Set2)
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.subheader("Resumen por Programa")
    st.caption(
        "**Créditos**: suma de créditos únicos por asignatura (sin duplicar por número de RAs). "
        "**Registros**: total de filas de estrategia. "
        "**Asignaturas**: materias únicas. "
        "**Semestres**: semestres distintos presentes."
    )

    resumen_rows = []
    for prog in df['Programa'].unique():
        g = df[df['Programa'] == prog]
        resumen_rows.append({
            'Programa': prog,
            'Registros': len(g),
            'Asignaturas': g['Nombre asignatura o modulo'].nunique(),
            'Semestres': g['Semestre'].nunique(),
            'Créditos (únicos)': _creditos_unicos_programa(g)
        })
    resumen = pd.DataFrame(resumen_rows)
    st.dataframe(resumen, use_container_width=True, hide_index=True)


def pagina_cobertura(df: pd.DataFrame, resultados: Dict):
    """Pagina de cobertura y densidad tematica."""
    st.title("Cobertura y Densidad Temática")
    st.markdown("---")
    st.info(
        "**¿Qué mide esta sección?** Analiza los **núcleos temáticos** declarados en los "
        "microcurrículos: qué temas se trabajan, con qué frecuencia, y qué tan distribuidos "
        "están entre asignaturas. Un currículo con alta **diversidad** temática cubre más "
        "áreas del conocimiento."
    )

    col1, col2, col3, col4 = st.columns(4)
    col1.metric(
        "Núcleos Únicos", resultados['nucleos_unicos'],
        help="Número de temas o núcleos temáticos diferentes identificados en todos los programas"
    )
    col2.metric(
        "Total Menciones", f"{resultados['total_menciones']:,}",
        help="Cuántas veces en total aparecen núcleos temáticos (pueden repetirse entre asignaturas)"
    )
    col3.metric(
        "Promedio por Asignatura", f"{resultados['promedio_densidad']:.1f}",
        help="Promedio de núcleos temáticos declarados por asignatura"
    )
    col4.metric(
        "Diversidad Temática", f"{resultados['diversidad']:.1f}/100",
        help=(
            "Índice de diversidad (Entropía de Shannon normalizada). "
            "100 = máxima diversidad (todos los temas con igual peso). "
            "0 = mínima diversidad (un solo tema domina todo)."
        )
    )

    st.markdown("---")

    # ── Matriz mejorada ──────────────────────────────────────────────────────
    st.subheader("Presencia de Núcleos Temáticos por Programa (Top 20)")
    st.caption(
        "Cada celda muestra cuántas veces aparece ese núcleo temático en las filas "
        "del programa. Los núcleos se extraen de la columna «Núcleos temáticos» separados "
        "por coma o punto y coma. Los más frecuentes (como términos cortos) pueden provenir "
        "de asignaturas del bloque institucional compartido entre programas."
    )
    matriz = resultados['matriz_cobertura']
    if not matriz.empty:
        # Truncar nombres de nucleos para mejor legibilidad
        max_len = 35
        col_cortos = {
            c: (c[:max_len] + '…' if len(c) > max_len else c)
            for c in matriz.columns
        }
        matriz_display = matriz.rename(columns=col_cortos)

        fig = px.imshow(
            matriz_display.values,
            x=matriz_display.columns.tolist(),
            y=matriz_display.index.tolist(),
            color_continuous_scale='YlOrRd',
            text_auto=True,
            aspect='auto',
            labels={'color': 'Menciones'}
        )
        fig.update_layout(
            height=max(300, len(matriz_display) * 60 + 150),
            xaxis_tickangle=45,
            xaxis_title="Núcleo Temático (top 20 más frecuentes)",
            yaxis_title="Programa"
        )
        st.plotly_chart(fig, use_container_width=True)

        # Mostrar tabla de nombres completos para referencia
        with st.expander("Ver nombres completos de los núcleos (referencia)"):
            nombres_df = pd.DataFrame([
                {'Abreviado': v, 'Nombre completo': k}
                for k, v in col_cortos.items()
                if k != v
            ])
            if not nombres_df.empty:
                st.dataframe(nombres_df, use_container_width=True, hide_index=True)
            else:
                st.caption("Todos los nombres son cortos y se muestran completos.")

    st.markdown("---")

    col_a, col_b = st.columns(2)

    with col_a:
        st.subheader("Top 20 Núcleos Temáticos")
        st.caption(
            "Frecuencia = cuántas veces aparece ese núcleo en todos los registros. "
            "Los núcleos muy cortos (1-2 palabras) suelen ser temas generales del bloque institucional."
        )
        top_nucleos = resultados['nucleos_counter'].most_common(20)
        df_nucleos = pd.DataFrame(top_nucleos, columns=['Nucleo', 'Frecuencia'])
        # Truncar para visualización
        df_nucleos['Nucleo_display'] = df_nucleos['Nucleo'].apply(
            lambda x: x[:45] + '…' if len(x) > 45 else x
        )
        fig = px.bar(df_nucleos, y='Nucleo_display', x='Frecuencia',
                     orientation='h', color='Frecuencia',
                     color_continuous_scale='Blues',
                     labels={'Nucleo_display': 'Núcleo Temático', 'Frecuencia': 'Menciones'},
                     hover_data={'Nucleo': True, 'Frecuencia': True, 'Nucleo_display': False})
        fig.update_layout(height=600, yaxis={'categoryorder': 'total ascending'})
        st.plotly_chart(fig, use_container_width=True)

    with col_b:
        st.subheader("Densidad Temática (Top 20 Asignaturas)")
        st.caption(
            "Asignaturas con más núcleos temáticos declarados. Alta densidad = mayor "
            "explicitación de contenidos. Asignaturas muy densas pueden tener temas duplicados."
        )
        densidad_top = resultados['densidad_asignatura'].head(20)
        df_densidad = pd.DataFrame({
            'Asignatura': densidad_top.index,
            'Nucleos': densidad_top.values
        })
        df_densidad['Asig_display'] = df_densidad['Asignatura'].apply(
            lambda x: x[:40] + '…' if len(str(x)) > 40 else x
        )
        fig = px.bar(df_densidad, y='Asig_display', x='Nucleos',
                     orientation='h', color='Nucleos',
                     color_continuous_scale='Oranges',
                     labels={'Asig_display': 'Asignatura', 'Nucleos': 'N° Núcleos'},
                     hover_data={'Asignatura': True, 'Nucleos': True, 'Asig_display': False})
        fig.update_layout(height=600, yaxis={'categoryorder': 'total ascending'})
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.subheader("Explorar Núcleos por Programa")
    st.caption("Selecciona un programa para ver sus núcleos temáticos más frecuentes.")
    programa_sel = st.selectbox("Seleccionar programa:", df['Programa'].unique(),
                                key='sel_prog_cobertura')
    df_prog = df[df['Programa'] == programa_sel]

    nucleos_prog = []
    for _, row in df_prog.iterrows():
        nucleos_raw = str(row.get('Nucleos tematicos', ''))
        if nucleos_raw and nucleos_raw != 'nan':
            nucleos = re.split(r'[,;\n]+', nucleos_raw)
            nucleos_prog.extend([
                _limpiar_nucleo(n.strip())
                for n in nucleos
                if n.strip() and len(n.strip()) > 3
            ])

    if nucleos_prog:
        counter_prog = Counter(nucleos_prog)
        df_prog_nucleos = pd.DataFrame(
            counter_prog.most_common(15),
            columns=['Nucleo', 'Frecuencia']
        )
        df_prog_nucleos['Nucleo_display'] = df_prog_nucleos['Nucleo'].apply(
            lambda x: x[:50] + '…' if len(x) > 50 else x
        )
        fig = px.bar(
            df_prog_nucleos, x='Nucleo_display', y='Frecuencia',
            color='Frecuencia', color_continuous_scale='Viridis',
            title=f"Top 15 Núcleos Temáticos — {programa_sel}",
            labels={'Nucleo_display': 'Núcleo Temático', 'Frecuencia': 'Menciones'},
            hover_data={'Nucleo': True, 'Frecuencia': True, 'Nucleo_display': False}
        )
        fig.update_layout(xaxis_tickangle=45, height=450)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info(f"No se encontraron núcleos temáticos para {programa_sel}.")


def pagina_tendencias(df: pd.DataFrame, tendencias: Dict, resultados: Dict):
    """Pagina de alineacion con tendencias globales."""
    st.title("Alineacion con Tendencias Globales")
    st.markdown("---")

    st.info(
        "**¿Qué mide esta sección?** Identifica qué tendencias del mundo actual "
        "están presentes en los planes de estudio. La **cobertura** indica el "
        f"porcentaje de asignaturas (sobre {resultados.get('total_asigs', '?')} en total) "
        "que abordan cada tendencia, detectada mediante palabras clave en los Resultados "
        "de Aprendizaje, Núcleos Temáticos e Indicadores de Logro."
    )

    total_tend = len(tendencias)
    detectadas = total_tend - len(resultados['ausentes'])
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Tendencias Evaluadas", total_tend,
                help="Número total de tendencias globales configuradas para buscar")
    col2.metric("Tendencias Detectadas", detectadas,
                help="Tendencias presentes en al menos una asignatura")
    col3.metric("Tendencias Ausentes", len(resultados['ausentes']),
                help="Tendencias sin ninguna asignatura que las aborde — son brechas curriculares")
    col4.metric("Total Asignaturas", resultados.get('total_asigs', '?'),
                help="Número de asignaturas únicas analizadas en todos los programas")

    st.markdown("---")

    st.subheader("Intensidad por Programa y Tendencia")
    st.caption(
        "Cada celda muestra cuántos registros (filas de estrategia) de ese programa "
        "mencionan al menos una palabra clave de la tendencia. Mayor valor = mayor énfasis."
    )
    matriz = resultados['matriz']
    col_names = {tid: tendencias[tid]['descripcion'] for tid in matriz.columns if tid in tendencias}
    matriz_display = matriz.rename(columns=col_names)

    fig = px.imshow(
        matriz_display.values,
        x=matriz_display.columns.tolist(),
        y=matriz_display.index.tolist(),
        color_continuous_scale='Viridis',
        text_auto=True,
        aspect='auto'
    )
    fig.update_layout(height=450, xaxis_tickangle=45)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    col_a, col_b = st.columns(2)

    with col_a:
        st.subheader("Cobertura por Tendencia (% de asignaturas)")
        st.caption(
            "Porcentaje de asignaturas únicas que abordan cada tendencia. "
            "100% significa que TODAS las asignaturas la tocan. "
            "La línea roja punteada marca el 100%."
        )
        cobertura_data = []
        for tid, pct in resultados['cobertura'].items():
            nombre = tendencias[tid]['descripcion'] if tid in tendencias else tid
            n_asigs = resultados.get('asig_counts', {}).get(tid, 0)
            cobertura_data.append({
                'Tendencia': nombre,
                'Cobertura': round(pct, 1),
                'Asignaturas': n_asigs
            })
        df_cob = pd.DataFrame(cobertura_data).sort_values('Cobertura', ascending=True)

        fig = px.bar(df_cob, y='Tendencia', x='Cobertura',
                     orientation='h', color='Cobertura',
                     color_continuous_scale='RdYlGn',
                     range_color=[0, 100],
                     hover_data=['Asignaturas'],
                     labels={'Cobertura': '% Asignaturas', 'Asignaturas': 'N° Asignaturas'})
        fig.add_vline(x=100, line_dash="dash", line_color="red", opacity=0.5)
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)

    with col_b:
        st.subheader("N° de Asignaturas por Tendencia")
        st.caption(
            "Número absoluto de asignaturas únicas que mencionan cada tendencia. "
            "Útil para comparar el peso real de cada tendencia."
        )
        menciones_data = []
        for tid in tendencias:
            nombre = tendencias[tid]['descripcion']
            n_asigs = resultados.get('asig_counts', {}).get(tid, 0)
            menciones_data.append({'Tendencia': nombre, 'Asignaturas': n_asigs})
        df_menciones = pd.DataFrame(menciones_data).sort_values('Asignaturas', ascending=True)

        fig = px.bar(df_menciones, y='Tendencia', x='Asignaturas',
                     orientation='h', color='Asignaturas',
                     color_continuous_scale='Blues',
                     labels={'Asignaturas': 'N° Asignaturas únicas'})
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)

    if resultados['ausentes']:
        st.markdown("---")
        st.subheader("⚠️ Brechas Curriculares Detectadas")
        st.warning(
            "Las siguientes tendencias **NO fueron detectadas en ninguna asignatura**. "
            "Se recomienda revisar si los programas deberían incorporarlas:"
        )
        for tid in resultados['ausentes']:
            if tid in tendencias:
                st.markdown(f"- **{tendencias[tid]['descripcion']}**")

    st.markdown("---")
    st.subheader("Detalle por Tendencia")
    st.caption(
        "Expande cada programa para ver qué asignaturas abordan la tendencia seleccionada "
        "y en qué campos fue detectada (RA = Resultado de Aprendizaje, Nucleos = Núcleos Temáticos)."
    )
    tend_sel = st.selectbox(
        "Seleccionar tendencia a explorar:",
        list(tendencias.keys()),
        format_func=lambda x: tendencias[x]['descripcion']
    )

    if tend_sel in resultados['detalle']:
        n_asigs_tend = resultados.get('asig_counts', {}).get(tend_sel, 0)
        total_asigs = resultados.get('total_asigs', 1)
        st.markdown(
            f"**{tendencias[tend_sel]['descripcion']}** — presente en "
            f"**{n_asigs_tend} de {total_asigs}** asignaturas "
            f"({n_asigs_tend/total_asigs*100:.1f}% de cobertura)"
        )
        tiene_hallazgos = False
        for programa, hallazgos in resultados['detalle'][tend_sel].items():
            if hallazgos:
                tiene_hallazgos = True
                asig_set = set()
                for h in hallazgos:
                    asig = h.get('asignatura', '')
                    if asig and asig not in ('Sin nombre', 'nan', ''):
                        asig_set.add(asig)
                with st.expander(f"📚 {programa} — {len(asig_set)} asignatura(s)"):
                    for asig in sorted(asig_set):
                        # Mostrar campos donde fue detectada
                        campos_asig = []
                        for h in hallazgos:
                            if h.get('asignatura') == asig:
                                campos_asig.extend(h.get('campos', []))
                        campos_unicos = list(dict.fromkeys(campos_asig))
                        campos_txt = ', '.join(campos_unicos) if campos_unicos else 'Texto general'
                        st.markdown(f"- **{asig}** _(detectada en: {campos_txt})_")
        if not tiene_hallazgos:
            st.info("Esta tendencia no fue detectada en ningún programa con los archivos cargados.")


def pagina_nlp(df: pd.DataFrame, resultados: Dict):
    """Pagina de mineria de texto."""
    st.title("Mineria de Texto y Analisis Semantico")
    st.markdown("---")
    st.info(
        "**¿Qué es esto?** Aplica técnicas de Procesamiento de Lenguaje Natural (NLP) "
        "sobre los textos de los programas para identificar los conceptos más relevantes, "
        "frases repetidas y qué tan similares son las asignaturas entre sí en cuanto a contenido."
    )

    col_a, col_b = st.columns(2)

    with col_a:
        st.subheader("Términos Clave Globales (TF-IDF)")
        st.caption(
            "TF-IDF mide la importancia de un término: alta frecuencia en el documento "
            "pero baja en todos los demás. Revela los conceptos más distintivos del currículo."
        )
        n_terms = st.slider("Número de términos:", 10, 30, 20, key='slider_tfidf')
        top_items = list(resultados['top_terminos'].items())[:n_terms]
        df_terms = pd.DataFrame(top_items, columns=['Termino', 'Score'])
        df_terms = df_terms.sort_values('Score', ascending=True)

        fig = px.bar(df_terms, y='Termino', x='Score',
                     orientation='h', color='Score',
                     color_continuous_scale='Plasma',
                     labels={'Score': 'Relevancia TF-IDF', 'Termino': 'Término'})
        fig.update_layout(height=max(400, n_terms * 25))
        st.plotly_chart(fig, use_container_width=True)

    with col_b:
        st.subheader("Frases Frecuentes (N-gramas)")
        st.caption(
            "N-gramas son combinaciones de 2 o 3 palabras que aparecen juntas frecuentemente. "
            "Revelan conceptos compuestos y enfoques pedagógicos recurrentes."
        )
        n_ng = st.slider("Número de frases:", 5, 20, 15, key='slider_ngrams')
        ng_items = list(resultados['top_ngrams'].items())[:n_ng]
        df_ng = pd.DataFrame(ng_items, columns=['N-grama', 'Frecuencia'])
        df_ng = df_ng.sort_values('Frecuencia', ascending=True)

        fig = px.bar(df_ng, y='N-grama', x='Frecuencia',
                     orientation='h', color='Frecuencia',
                     color_continuous_scale='Magma',
                     labels={'Frecuencia': 'Veces que aparece', 'N-grama': 'Frase'})
        fig.update_layout(height=max(400, n_ng * 25))
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    st.subheader("Términos Clave por Programa")
    st.caption("Compara qué conceptos son más relevantes y distintivos en cada programa académico.")
    if resultados['top_por_programa']:
        tabs = st.tabs(list(resultados['top_por_programa'].keys()))
        for tab, (programa, terminos) in zip(tabs, resultados['top_por_programa'].items()):
            with tab:
                items = list(terminos.items())[:15]
                df_p = pd.DataFrame(items, columns=['Termino', 'Score'])
                df_p = df_p.sort_values('Score', ascending=True)
                fig = px.bar(df_p, y='Termino', x='Score',
                             orientation='h', color='Score',
                             color_continuous_scale='Teal',
                             title=f"Términos más relevantes — {programa}")
                fig.update_layout(height=450)
                st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # ── Similitud entre Asignaturas (interactivo) ──────────────────────────
    st.subheader("Similitud entre Asignaturas")
    st.info(
        "**¿Para qué sirve esto?** Detecta asignaturas con contenidos muy similares entre sí, "
        "lo que puede indicar redundancia o falta de diferenciación curricular. "
        "Una similitud superior al 80% merece revisión. "
        "Puede comparar 2 o más programas a la vez."
    )

    programas_disponibles = sorted(df['Programa'].unique().tolist())
    programas_sel = st.multiselect(
        "Seleccionar programas a comparar (2 o más):",
        programas_disponibles,
        default=programas_disponibles,
        help="Elige qué programas incluir en el análisis de similitud"
    )

    if len(programas_sel) < 2:
        st.warning("Selecciona al menos 2 programas para el análisis de similitud.")
    else:
        df_sim_filtrado = df[df['Programa'].isin(programas_sel)]
        with st.spinner("Calculando similitud..."):
            res_sim = calcular_similitud_asignaturas(df_sim_filtrado)

        if res_sim['n_asignaturas'] < 3:
            st.warning("Se necesitan al menos 3 asignaturas en los programas seleccionados.")
        else:
            if res_sim['par_similar']:
                par = res_sim['par_similar']
                st.info(
                    f"**Par más similar:** {par['asig1']} ↔ {par['asig2']} "
                    f"(Similitud: {par['similitud']:.1%})"
                )

            sim_df = res_sim['similitud_df']
            if not sim_df.empty:
                if len(sim_df) <= 30:
                    fig = px.imshow(
                        sim_df.values,
                        x=sim_df.columns.tolist(),
                        y=sim_df.index.tolist(),
                        color_continuous_scale='RdBu_r',
                        text_auto='.2f',
                        aspect='auto',
                        title="Mapa de calor de similitud (1.0 = idénticas, 0.0 = completamente distintas)"
                    )
                    fig.update_layout(height=700, xaxis_tickangle=45)
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.caption("Demasiadas asignaturas para mapa de calor. Se muestran los pares más similares:")
                    sim_vals = sim_df.values.copy()
                    np.fill_diagonal(sim_vals, 0)
                    pares = []
                    for i in range(len(sim_vals)):
                        for j in range(i + 1, len(sim_vals)):
                            pares.append({
                                'Asignatura 1': sim_df.index[i],
                                'Asignatura 2': sim_df.columns[j],
                                'Similitud': round(sim_vals[i, j], 4)
                            })
                    df_pares = (
                        pd.DataFrame(pares)
                        .sort_values('Similitud', ascending=False)
                        .head(30)
                    )
                    # Marcar pares con alta similitud
                    def highlight_similar(val):
                        if isinstance(val, float) and val >= 0.8:
                            return 'background-color: #ffcccc'
                        return ''
                    st.dataframe(
                        df_pares.style.applymap(highlight_similar, subset=['Similitud']),
                        use_container_width=True,
                        hide_index=True
                    )
                    st.caption("🔴 Similitud ≥ 0.80 puede indicar redundancia curricular.")

    st.markdown("---")
    st.subheader("Buscar Términos en los Datos")
    st.caption("Escribe un concepto o frase para encontrar en qué asignaturas y programas aparece.")
    termino_buscar = st.text_input("Término o frase a buscar:")
    if termino_buscar:
        mask = df['Texto_Completo'].str.contains(termino_buscar.lower(), na=False)
        res_busq = df[mask][['Programa', 'Nombre asignatura o modulo',
                             'Tipo de Saber', 'Semestre']].drop_duplicates()
        st.markdown(f"**{len(res_busq)} registros encontrados** para «{termino_buscar}»")
        st.dataframe(res_busq, use_container_width=True, hide_index=True)


def pagina_tipo_saber(df: pd.DataFrame):
    """Pagina de analisis profundo del Tipo de Saber."""
    st.title("Análisis de Tipo de Saber")
    st.markdown("---")
    st.info(
        "El **Tipo de Saber** clasifica cada estrategia microcurricular según la dimensión "
        "del aprendizaje que desarrolla:\n\n"
        "- 🔵 **Saber** (conocimiento): comprensión conceptual, teórica y declarativa. "
        "Ej: «conoce los fundamentos de…», «identifica los principios de…»\n"
        "- 🟠 **SaberHacer** (habilidad): competencias procedimentales y prácticas. "
        "Ej: «aplica técnicas de…», «elabora un plan de…», «resuelve problemas de…»\n"
        "- 🟣 **SaberSer** (actitud): valores, ética, ciudadanía y dimensión humana. "
        "Ej: «valora la importancia de…», «actúa con responsabilidad en…»\n\n"
        "**Referencia:** Un currículo por competencias equilibrado debería tener énfasis en "
        "SaberHacer (≥40%), complementado con Saber (30-40%) y SaberSer (≥15%)."
    )

    COLORES_SABER = {
        'Saber': '#3498DB',
        'SaberHacer': '#E67E22',
        'SaberSer': '#8E44AD'
    }

    # ── Distribución global ─────────────────────────────────────────────────
    st.markdown("---")
    st.subheader("Distribución Global de Tipo de Saber")

    col_a, col_b = st.columns(2)
    with col_a:
        total_tipo = df['Tipo de Saber'].value_counts().reset_index()
        total_tipo.columns = ['Tipo', 'Registros']
        total_tipo['Porcentaje'] = (total_tipo['Registros'] / total_tipo['Registros'].sum() * 100).round(1)
        fig = px.pie(
            total_tipo, values='Registros', names='Tipo',
            color='Tipo',
            color_discrete_map=COLORES_SABER,
            title='Todos los programas consolidados'
        )
        fig.update_traces(texttemplate='%{label}<br>%{percent:.1%}')
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)

    with col_b:
        # Semáforo de equilibrio
        st.subheader("Diagnóstico de Equilibrio")
        totales = df['Tipo de Saber'].value_counts()
        total = totales.sum()
        for tipo in COLORES_SABER:
            n = int(totales.get(tipo, 0))
            pct = n / total * 100 if total > 0 else 0
            # Referencia
            if tipo == 'Saber':
                ref_min, ref_max = 25, 45
            elif tipo == 'SaberHacer':
                ref_min, ref_max = 35, 60
            else:
                ref_min, ref_max = 10, 30

            estado = "✅ En rango" if ref_min <= pct <= ref_max else (
                "⬆️ Por encima" if pct > ref_max else "⬇️ Por debajo"
            )
            st.metric(
                f"{tipo}",
                f"{pct:.1f}% ({n} registros)",
                delta=f"{estado} (ref: {ref_min}–{ref_max}%)",
                delta_color="off"
            )

    # ── Por programa ────────────────────────────────────────────────────────
    st.markdown("---")
    st.subheader("Comparación de Tipo de Saber por Programa")
    st.caption(
        "Barras apiladas al 100%. Permite comparar el perfil de cada programa: "
        "¿predomina lo teórico (Saber), lo práctico (SaberHacer) o lo actitudinal (SaberSer)?"
    )

    pivot = (
        df.groupby(['Programa', 'Tipo de Saber'])
        .size()
        .reset_index(name='Registros')
    )
    total_prog = pivot.groupby('Programa')['Registros'].transform('sum')
    pivot['Porcentaje'] = (pivot['Registros'] / total_prog * 100).round(1)

    fig = px.bar(
        pivot, x='Programa', y='Porcentaje', color='Tipo de Saber',
        barmode='stack',
        color_discrete_map=COLORES_SABER,
        text='Porcentaje',
        title='Distribución porcentual por programa',
        labels={'Porcentaje': '%', 'Tipo de Saber': 'Tipo'}
    )
    fig.update_traces(texttemplate='%{text:.0f}%', textposition='inside')
    fig.update_layout(height=450, yaxis_title='Porcentaje (%)')
    # Líneas de referencia
    fig.add_hline(y=40, line_dash='dot', line_color='gray', opacity=0.4,
                  annotation_text='Ref. 40%', annotation_position='right')
    st.plotly_chart(fig, use_container_width=True)

    # ── Por semestre ────────────────────────────────────────────────────────
    st.markdown("---")
    st.subheader("Evolución de Tipo de Saber por Semestre")
    st.caption(
        "¿Cómo cambia el enfoque del aprendizaje a lo largo de la carrera? "
        "Se espera que los semestres avanzados tengan mayor proporción de SaberHacer y SaberSer."
    )

    programas_disponibles = sorted(df['Programa'].unique().tolist())
    prog_sel_saber = st.multiselect(
        "Seleccionar programas:",
        programas_disponibles,
        default=programas_disponibles,
        key='saber_prog_sel'
    )
    df_sem = df[df['Programa'].isin(prog_sel_saber)] if prog_sel_saber else df

    # Filtrar semestres numéricos
    df_sem = df_sem.copy()
    df_sem['Semestre_num'] = pd.to_numeric(df_sem['Semestre'], errors='coerce')
    df_sem_valid = df_sem.dropna(subset=['Semestre_num'])

    if not df_sem_valid.empty:
        pivot_sem = (
            df_sem_valid.groupby(['Semestre_num', 'Tipo de Saber'])
            .size()
            .reset_index(name='Registros')
        )
        total_sem = pivot_sem.groupby('Semestre_num')['Registros'].transform('sum')
        pivot_sem['Porcentaje'] = (pivot_sem['Registros'] / total_sem * 100).round(1)
        pivot_sem['Semestre'] = pivot_sem['Semestre_num'].astype(int).astype(str)

        fig = px.line(
            pivot_sem.sort_values('Semestre_num'),
            x='Semestre', y='Porcentaje', color='Tipo de Saber',
            color_discrete_map=COLORES_SABER,
            markers=True,
            title='Evolución del Tipo de Saber por semestre',
            labels={'Porcentaje': '%', 'Semestre': 'Semestre'}
        )
        fig.update_layout(height=400, yaxis_range=[0, 100])
        st.plotly_chart(fig, use_container_width=True)
        st.caption(
            "💡 Si SaberSer es muy bajo en todos los semestres, el programa puede estar "
            "descuidando la formación en valores y ciudadanía."
        )
    else:
        st.info("No hay datos de semestres numéricos para los programas seleccionados.")

    # ── Por asignatura ──────────────────────────────────────────────────────
    st.markdown("---")
    st.subheader("Tipo de Saber Predominante por Asignatura")
    st.caption(
        "Cada asignatura se clasifica según el tipo de saber más frecuente en sus registros. "
        "Útil para identificar si una asignatura es principalmente teórica, práctica o formativa."
    )

    prog_asig_sel = st.selectbox(
        "Seleccionar programa:",
        sorted(df['Programa'].unique()),
        key='saber_asig_prog'
    )
    df_asig_saber = df[df['Programa'] == prog_asig_sel]

    pivot_asig = (
        df_asig_saber.groupby(['Nombre asignatura o modulo', 'Tipo de Saber'])
        .size()
        .reset_index(name='Registros')
    )
    total_asig = pivot_asig.groupby('Nombre asignatura o modulo')['Registros'].transform('sum')
    pivot_asig['Porcentaje'] = (pivot_asig['Registros'] / total_asig * 100).round(1)

    # Ordenar por SaberHacer descendente para identificar asignaturas más prácticas
    orden = (
        pivot_asig[pivot_asig['Tipo de Saber'] == 'SaberHacer']
        .sort_values('Porcentaje', ascending=False)['Nombre asignatura o modulo']
        .tolist()
    )
    todas = pivot_asig['Nombre asignatura o modulo'].unique().tolist()
    orden_completo = orden + [a for a in todas if a not in orden]

    fig = px.bar(
        pivot_asig, y='Nombre asignatura o modulo', x='Porcentaje',
        color='Tipo de Saber',
        color_discrete_map=COLORES_SABER,
        barmode='stack',
        orientation='h',
        category_orders={'Nombre asignatura o modulo': orden_completo},
        title=f'Perfil de Tipo de Saber por asignatura — {prog_asig_sel}',
        labels={'Porcentaje': '%', 'Nombre asignatura o modulo': 'Asignatura'}
    )
    fig.update_layout(
        height=max(400, len(orden_completo) * 25 + 100),
        xaxis_range=[0, 100]
    )
    st.plotly_chart(fig, use_container_width=True)

    # Tabla resumen
    with st.expander("Ver tabla de datos"):
        tabla = pivot_asig.pivot_table(
            index='Nombre asignatura o modulo',
            columns='Tipo de Saber',
            values='Porcentaje',
            fill_value=0
        ).round(1).reset_index()
        tabla.columns.name = None
        st.dataframe(tabla, use_container_width=True, hide_index=True)


def pagina_resumen_ejecutivo(df: pd.DataFrame, tendencias: Dict) -> None:
    """Pagina de resumen ejecutivo con hallazgos y recomendaciones para toma de decisiones."""
    st.title("📋 Resumen Ejecutivo")
    st.markdown("---")
    st.info(
        "Esta sección sintetiza los hallazgos más relevantes del análisis microcurricular "
        "para facilitar la **toma de decisiones** en comités académicos, procesos de "
        "autoevaluación y rediseños curriculares. Incluye alertas automáticas, fortalezas "
        "detectadas y recomendaciones priorizadas."
    )

    programas = df['Programa'].unique().tolist()
    asig_col = 'Nombre asignatura o modulo'
    total_asigs = df[asig_col].nunique()
    total_registros = len(df)

    # ── Métricas generales ──────────────────────────────────────────────────
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Programas analizados", len(programas))
    col2.metric("Asignaturas únicas", total_asigs)
    col3.metric("Registros procesados", f"{total_registros:,}")
    col4.metric("Semestres detectados",
                df['Semestre'].dropna().nunique())

    st.markdown("---")

    # ── Sección 1: Alertas priorizadas ─────────────────────────────────────
    st.subheader("🚦 Alertas y Brechas Detectadas")
    st.caption(
        "Situaciones que requieren atención según criterios de calidad académica. "
        "Ordenadas por prioridad."
    )

    alertas = []

    # 1a. Tipo de Saber — desequilibrios
    totales_saber = df['Tipo de Saber'].value_counts()
    total_ts = totales_saber.sum()
    for tipo, (ref_min, ref_max) in {
        'SaberHacer': (35, 65),
        'SaberSer': (10, 30),
        'Saber': (20, 50)
    }.items():
        pct = totales_saber.get(tipo, 0) / total_ts * 100 if total_ts > 0 else 0
        if pct < ref_min:
            alertas.append({
                'Prioridad': 'Alta' if tipo in ('SaberHacer', 'SaberSer') else 'Media',
                'Categoría': 'Tipo de Saber',
                'Hallazgo': f'**{tipo}** es bajo ({pct:.1f}%) — referencia: {ref_min}–{ref_max}%',
                'Recomendación': (
                    'Revisar asignaturas con 0% de SaberHacer e incorporar actividades prácticas.'
                    if tipo == 'SaberHacer' else
                    'Incorporar resultados de aprendizaje orientados a valores, ética y ciudadanía.'
                    if tipo == 'SaberSer' else
                    'Verificar si el currículo tiene suficiente fundamentación teórica.'
                )
            })
        elif pct > ref_max:
            alertas.append({
                'Prioridad': 'Media',
                'Categoría': 'Tipo de Saber',
                'Hallazgo': f'**{tipo}** es alto ({pct:.1f}%) — referencia: {ref_min}–{ref_max}%',
                'Recomendación': f'Considerar rebalancear hacia los otros tipos de saber.'
            })

    # 1b. Semestres sin datos
    df_sem_num = df.copy()
    df_sem_num['Semestre_num'] = pd.to_numeric(df_sem_num['Semestre'], errors='coerce')
    pct_sin_semestre = df_sem_num['Semestre_num'].isna().mean() * 100
    if pct_sin_semestre > 20:
        alertas.append({
            'Prioridad': 'Media',
            'Categoría': 'Completitud de datos',
            'Hallazgo': f'{pct_sin_semestre:.0f}% de registros sin semestre numérico válido',
            'Recomendación': 'Estandarizar el campo Semestre en los archivos Excel (usar números: 1, 2, 3…)'
        })

    # 1c. Tendencias globales ausentes
    resultados_tend = analizar_tendencias(df, tendencias)
    if resultados_tend['ausentes']:
        desc_ausentes = [tendencias[t]['descripcion'] for t in resultados_tend['ausentes'] if t in tendencias]
        alertas.append({
            'Prioridad': 'Alta',
            'Categoría': 'Tendencias Globales',
            'Hallazgo': f'{len(desc_ausentes)} tendencia(s) sin cobertura: {", ".join(desc_ausentes[:3])}{"…" if len(desc_ausentes) > 3 else ""}',
            'Recomendación': 'Revisar si estas tendencias son relevantes para el perfil del egresado y actualizar los contenidos.'
        })

    # 1d. Tendencias con muy baja cobertura (<20%)
    for tid, pct in resultados_tend['cobertura'].items():
        if 0 < pct < 20 and tid in tendencias:
            alertas.append({
                'Prioridad': 'Baja',
                'Categoría': 'Tendencias Globales',
                'Hallazgo': f'Baja cobertura de **{tendencias[tid]["descripcion"]}** ({pct:.1f}%)',
                'Recomendación': 'Solo unas pocas asignaturas abordan esta tendencia. Considerar ampliar su presencia.'
            })

    # 1e. Asignaturas sin núcleos temáticos
    sin_nucleos = df[df['Nucleos tematicos'].isna() | (df['Nucleos tematicos'].astype(str).str.strip() == '') |
                     (df['Nucleos tematicos'].astype(str).str.strip() == 'nan')]
    asigs_sin_nucleos = sin_nucleos[asig_col].nunique() if not sin_nucleos.empty else 0
    if asigs_sin_nucleos > 0:
        pct_sin = asigs_sin_nucleos / total_asigs * 100
        alertas.append({
            'Prioridad': 'Media',
            'Categoría': 'Completitud de datos',
            'Hallazgo': f'{asigs_sin_nucleos} asignaturas ({pct_sin:.0f}%) sin núcleos temáticos declarados',
            'Recomendación': 'Completar la columna «Núcleos temáticos» en el formato Excel para un análisis más preciso.'
        })

    if alertas:
        orden_prioridad = {'Alta': 0, 'Media': 1, 'Baja': 2}
        df_alertas = pd.DataFrame(alertas).sort_values(
            'Prioridad', key=lambda x: x.map(orden_prioridad)
        )
        for _, a in df_alertas.iterrows():
            icono = '🔴' if a['Prioridad'] == 'Alta' else ('🟡' if a['Prioridad'] == 'Media' else '🟢')
            with st.expander(f"{icono} [{a['Prioridad']}] {a['Categoría']}: {a['Hallazgo']}", expanded=(a['Prioridad'] == 'Alta')):
                st.markdown(f"**💡 Recomendación:** {a['Recomendación']}")
    else:
        st.success("✅ No se detectaron alertas críticas en los programas analizados.")

    # ── Sección 2: Fortalezas detectadas ───────────────────────────────────
    st.markdown("---")
    st.subheader("✅ Fortalezas Detectadas")
    st.caption("Aspectos positivos identificados en el análisis.")

    fortalezas = []
    tend_detectadas = len(tendencias) - len(resultados_tend['ausentes'])
    if tend_detectadas >= len(tendencias) * 0.8:
        fortalezas.append(f"Alta alineación con tendencias globales: **{tend_detectadas}/{len(tendencias)}** tendencias presentes")
    saberhacer_pct = totales_saber.get('SaberHacer', 0) / total_ts * 100 if total_ts > 0 else 0
    if saberhacer_pct >= 35:
        fortalezas.append(f"Buen énfasis en **SaberHacer** ({saberhacer_pct:.1f}%) — favorece la formación por competencias")

    # Diversidad temática
    nucleos_list = []
    for _, row in df.iterrows():
        raw = str(row.get('Nucleos tematicos', ''))
        if raw and raw not in ('nan', ''):
            nucleos_list.extend([n.strip() for n in re.split(r'[,;\n]+', raw) if n.strip() and len(n.strip()) > 3])
    n_unicos = len(set(nucleos_list))
    if n_unicos > total_asigs * 2:
        fortalezas.append(f"Alta diversidad temática: **{n_unicos}** núcleos únicos para {total_asigs} asignaturas")

    if asigs_sin_nucleos == 0:
        fortalezas.append("**100%** de asignaturas con núcleos temáticos declarados")

    if fortalezas:
        for f_item in fortalezas:
            st.markdown(f"- {f_item}")
    else:
        st.info("No se identificaron fortalezas destacadas con los umbrales actuales.")

    # ── Sección 3: Resumen por programa ────────────────────────────────────
    st.markdown("---")
    st.subheader("📊 Perfil por Programa")
    st.caption("Resumen de los indicadores clave por programa para soporte a decisiones curriculares.")

    for prog in sorted(programas):
        df_prog = df[df['Programa'] == prog]
        n_asigs = df_prog[asig_col].nunique()
        n_reg = len(df_prog)
        ts = df_prog['Tipo de Saber'].value_counts()
        ts_total = ts.sum()
        sh_pct = ts.get('SaberHacer', 0) / ts_total * 100 if ts_total > 0 else 0
        ss_pct = ts.get('SaberSer', 0) / ts_total * 100 if ts_total > 0 else 0
        tend_prog = sum(1 for tid in tendencias if resultados_tend['asig_counts'].get(tid, 0) > 0)

        with st.expander(f"📚 {prog} — {n_asigs} asignaturas, {n_reg} registros"):
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Asignaturas", n_asigs)
            c2.metric("SaberHacer", f"{sh_pct:.1f}%",
                      delta="✅ OK" if sh_pct >= 35 else "⚠️ Bajo",
                      delta_color="off")
            c3.metric("SaberSer", f"{ss_pct:.1f}%",
                      delta="✅ OK" if ss_pct >= 10 else "⚠️ Bajo",
                      delta_color="off")
            c4.metric("Tendencias cubiertas", f"{tend_prog}/{len(tendencias)}")

    # ── Sección 4: Descarga ─────────────────────────────────────────────────
    st.markdown("---")
    st.subheader("⬇️ Descargar Datos del Análisis")
    st.caption("Exporta los datos filtrados o el resumen de alertas para presentaciones y reportes.")

    col_dl1, col_dl2 = st.columns(2)
    with col_dl1:
        csv_datos = df[[
            'Programa', 'Nombre asignatura o modulo', 'Semestre',
            'Tipo de Saber', 'Resultado de aprendizaje', 'Nucleos tematicos'
        ]].to_csv(index=False, encoding='utf-8-sig')
        st.download_button(
            label="📄 Descargar datos consolidados (CSV)",
            data=csv_datos,
            file_name="datos_microcurriculares.csv",
            mime="text/csv",
            help="Descarga todos los registros procesados en formato Excel-compatible"
        )
    with col_dl2:
        if alertas:
            csv_alertas = pd.DataFrame(alertas).to_csv(index=False, encoding='utf-8-sig')
            st.download_button(
                label="🚨 Descargar alertas (CSV)",
                data=csv_alertas,
                file_name="alertas_curriculares.csv",
                mime="text/csv",
                help="Descarga el listado de alertas y recomendaciones detectadas"
            )


def pagina_bloom_integracion(df: pd.DataFrame):
    """Pagina de Taxonomia de Bloom por semestre y Mapa de Integracion entre asignaturas."""
    import math as _math

    st.title("🎓 Taxonomía de Bloom e Integración Curricular")
    st.markdown("---")
    st.info(
        "Esta sección analiza dos dimensiones estratégicas del diseño curricular: "
        "**¿Qué nivel cognitivo desarrolla el currículo por semestre?** (Taxonomía de Bloom) y "
        "**¿Qué asignaturas comparten núcleos temáticos?** (Mapa de Integración). "
        "Son herramientas clave para evaluar progresión cognitiva y articulación horizontal del plan de estudios."
    )

    tab_bloom, tab_mapa = st.tabs([
        "🧠 Taxonomía de Bloom por Semestre",
        "🕸️ Mapa de Integración entre Asignaturas"
    ])

    # ─────────────────────────────────────────────────────────────────────────
    # TAB 1 — TAXONOMÍA DE BLOOM
    # ─────────────────────────────────────────────────────────────────────────
    with tab_bloom:
        st.subheader("Taxonomía de Bloom — Niveles de Pensamiento Cognitivo")
        st.caption(
            "La Taxonomía de Bloom clasifica los objetivos de aprendizaje en 6 niveles cognitivos, "
            "desde el más básico (**Recordar**) hasta el más complejo (**Crear**). "
            "Un currículo bien estructurado muestra progresión: semestres iniciales con niveles básicos "
            "y semestres avanzados con niveles de orden superior (Analizar, Evaluar, Crear)."
        )

        # ── Diccionario de verbos por nivel (orden importa: mayor orden = mayor prioridad) ──
        BLOOM = {
            "Recordar":   {
                "verbos": ["identificar", "reconocer", "listar", "nombrar", "recordar",
                           "definir", "enunciar", "señalar", "mencionar", "indicar",
                           "citar", "repetir", "seleccionar", "reproducir", "describir"],
                "color": "#95A5A6", "orden": 1,
                "desc": "Recuperar información previamente aprendida"
            },
            "Comprender": {
                "verbos": ["explicar", "interpretar", "resumir", "inferir", "parafrasear",
                           "categorizar", "ejemplificar", "ilustrar", "generalizar",
                           "relacionar", "contrastar", "clasificar", "comparar", "deducir"],
                "color": "#3498DB", "orden": 2,
                "desc": "Construir significado a partir de la información"
            },
            "Aplicar":    {
                "verbos": ["aplicar", "resolver", "usar", "ejecutar", "implementar",
                           "calcular", "operar", "practicar", "utilizar", "realizar",
                           "desarrollar", "construir", "producir", "elaborar", "demostrar"],
                "color": "#2ECC71", "orden": 3,
                "desc": "Usar procedimientos en situaciones concretas"
            },
            "Analizar":   {
                "verbos": ["analizar", "diferenciar", "examinar", "organizar", "descomponer",
                           "discriminar", "estructurar", "integrar", "atribuir",
                           "diagnosticar", "distinguir", "separar"],
                "color": "#F39C12", "orden": 4,
                "desc": "Descomponer en partes e identificar relaciones"
            },
            "Evaluar":    {
                "verbos": ["evaluar", "justificar", "valorar", "criticar", "defender",
                           "juzgar", "argumentar", "sustentar", "verificar", "comprobar",
                           "fundamentar", "decidir", "priorizar", "validar"],
                "color": "#E74C3C", "orden": 5,
                "desc": "Emitir juicios de valor basados en criterios"
            },
            "Crear":      {
                "verbos": ["diseñar", "crear", "proponer", "formular", "planear",
                           "inventar", "combinar", "generar", "planificar", "innovar",
                           "componer", "hipotetizar", "proyectar"],
                "color": "#9B59B6", "orden": 6,
                "desc": "Reunir elementos para producir algo nuevo"
            },
        }

        # Build normalized verb lookup — higher order wins for ambiguous verbs
        verb_lookup: Dict[str, tuple] = {}
        for nivel, info in BLOOM.items():
            for v in info["verbos"]:
                v_n = unicodedata.normalize('NFKD', v).encode('ascii', 'ignore').decode('ascii')
                if v_n not in verb_lookup or info["orden"] > verb_lookup[v_n][1]:
                    verb_lookup[v_n] = (nivel, info["orden"])

        def detectar_bloom(texto: str) -> str:
            if not texto or str(texto).strip() in ('nan', ''):
                return "No identificado"
            t = unicodedata.normalize('NFKD', str(texto).lower()).encode('ascii', 'ignore').decode('ascii')
            best_orden = 0
            best_nivel = "No identificado"
            for v_n, (nivel, orden) in verb_lookup.items():
                if re.search(r'\b' + re.escape(v_n) + r'\b', t):
                    if orden > best_orden:
                        best_orden = orden
                        best_nivel = nivel
            return best_nivel

        # Apply Bloom classification
        df_bloom = df.copy()
        df_bloom['Nivel_Bloom'] = df_bloom['Resultado de aprendizaje'].apply(detectar_bloom)

        orden_niveles = ["Recordar", "Comprender", "Aplicar", "Analizar", "Evaluar", "Crear", "No identificado"]
        colores_bloom = {n: BLOOM[n]["color"] for n in BLOOM}
        colores_bloom["No identificado"] = "#ECF0F1"

        # ── 1. Distribución global ────────────────────────────────────────────
        conteo_global = df_bloom['Nivel_Bloom'].value_counts().reindex(orden_niveles, fill_value=0)
        total_bloom = int(conteo_global.sum())

        col_pie, col_ref = st.columns([1, 1])
        with col_pie:
            fig_pie = go.Figure(go.Pie(
                labels=conteo_global.index.tolist(),
                values=conteo_global.values.tolist(),
                marker_colors=[colores_bloom[n] for n in conteo_global.index],
                hole=0.35,
                textinfo='label+percent'
            ))
            fig_pie.update_layout(
                title="Distribución global de niveles Bloom",
                height=380, showlegend=False,
                margin=dict(t=50, b=0, l=0, r=0)
            )
            st.plotly_chart(fig_pie, use_container_width=True)

        with col_ref:
            st.markdown("**Referencia de niveles:**")
            for nivel in orden_niveles[:-1]:
                pct = conteo_global.get(nivel, 0) / total_bloom * 100 if total_bloom > 0 else 0
                st.markdown(
                    f"<div style='margin:5px 0'>"
                    f"<span style='background:{colores_bloom[nivel]};padding:2px 10px;"
                    f"border-radius:4px;color:white;font-size:0.82em;font-weight:bold'>"
                    f"N{BLOOM[nivel]['orden']} {nivel}</span> "
                    f"<span style='font-size:0.78em;color:#555'>{BLOOM[nivel]['desc']}</span><br>"
                    f"<b>{pct:.1f}%</b> ({conteo_global.get(nivel, 0)} RAs)"
                    f"</div>",
                    unsafe_allow_html=True
                )

        # Diagnóstico automático
        if total_bloom > 0:
            pct_no_id = conteo_global.get("No identificado", 0) / total_bloom * 100
            pct_altos = sum(conteo_global.get(n, 0) for n in ["Analizar", "Evaluar", "Crear"]) / total_bloom * 100
            pct_bajos = sum(conteo_global.get(n, 0) for n in ["Recordar", "Comprender"]) / total_bloom * 100
            if pct_no_id > 40:
                st.warning(
                    f"⚠️ **{pct_no_id:.0f}%** de los RAs no pudieron clasificarse por Bloom. "
                    "Los textos pueden no iniciar con verbos de acción estandarizados."
                )
            if pct_altos >= 30:
                st.success(
                    f"✅ **{pct_altos:.0f}%** de los RAs están en niveles de orden superior "
                    "(Analizar / Evaluar / Crear). Indica formación orientada al pensamiento crítico."
                )
            if pct_bajos > 55 and pct_no_id < 40:
                st.info(
                    f"📌 **{pct_bajos:.0f}%** de los RAs están en niveles básicos "
                    "(Recordar / Comprender). Verifique si los semestres avanzados incluyen "
                    "objetivos de mayor complejidad cognitiva."
                )

        st.markdown("---")

        # ── 2. Progresión cognitiva por semestre ──────────────────────────────
        st.subheader("Progresión Cognitiva por Semestre")
        st.caption(
            "Muestra cómo cambia la proporción de niveles Bloom a lo largo de los semestres. "
            "Un currículo progresivo debería mostrar crecimiento de las bandas superiores "
            "(Analizar/Evaluar/Crear) hacia los últimos semestres."
        )

        prog_bloom_filter = st.multiselect(
            "Filtrar por programa (dejar vacío = todos los programas):",
            sorted(df_bloom['Programa'].unique().tolist()),
            default=[],
            key="bloom_prog_filter"
        )
        df_bloom_filt = df_bloom[df_bloom['Programa'].isin(prog_bloom_filter)] if prog_bloom_filter else df_bloom

        df_sem = df_bloom_filt.copy()
        df_sem['Semestre_num'] = pd.to_numeric(df_sem['Semestre'], errors='coerce')
        df_sem = df_sem.dropna(subset=['Semestre_num'])
        df_sem['Semestre_num'] = df_sem['Semestre_num'].astype(int)

        if df_sem.empty:
            st.warning("No hay registros con semestre numérico válido para mostrar la progresión.")
        else:
            pivot_sem = (
                df_sem.groupby(['Semestre_num', 'Nivel_Bloom'])
                .size()
                .reset_index(name='count')
            )
            total_sem_grp = pivot_sem.groupby('Semestre_num')['count'].transform('sum')
            pivot_sem['pct'] = pivot_sem['count'] / total_sem_grp * 100

            sems_ordenados = sorted(df_sem['Semestre_num'].unique())
            lvls_en_datos = [n for n in orden_niveles[:-1] if n in pivot_sem['Nivel_Bloom'].values]

            fig_prog = go.Figure()
            for nivel in lvls_en_datos:
                datos_nivel = pivot_sem[pivot_sem['Nivel_Bloom'] == nivel]
                sem_val_map = {int(r['Semestre_num']): r['pct'] for _, r in datos_nivel.iterrows()}
                y_vals = [sem_val_map.get(s, 0) for s in sems_ordenados]
                fig_prog.add_trace(go.Scatter(
                    x=sems_ordenados,
                    y=y_vals,
                    name=nivel,
                    mode='lines+markers',
                    line=dict(color=colores_bloom[nivel], width=2.5),
                    marker=dict(size=7),
                    stackgroup='one',
                    groupnorm='percent'
                ))
            fig_prog.update_layout(
                title="Composición por nivel Bloom (%) a lo largo del plan de estudios",
                xaxis_title="Semestre",
                yaxis_title="% de resultados de aprendizaje",
                height=430,
                legend=dict(orientation='h', y=-0.25),
                xaxis=dict(tickmode='array', tickvals=sems_ordenados)
            )
            st.plotly_chart(fig_prog, use_container_width=True)
            st.caption(
                "**Lectura:** Cada banda de color es un nivel Bloom. "
                "Si las bandas superiores (Evaluar/Crear — rojo/morado) crecen hacia la derecha, "
                "el currículo muestra progresión cognitiva ascendente. "
                "Si son constantes o disminuyen, hay oportunidad de rediseño."
            )

        st.markdown("---")

        # ── 3. Por programa (barras apiladas 100%) ────────────────────────────
        st.subheader("Distribución Bloom por Programa")
        prog_bloom_data = (
            df_bloom.groupby(['Programa', 'Nivel_Bloom'])
            .size()
            .reset_index(name='count')
        )
        total_prog_grp = prog_bloom_data.groupby('Programa')['count'].transform('sum')
        prog_bloom_data['pct'] = prog_bloom_data['count'] / total_prog_grp * 100

        lvls_prog = [n for n in orden_niveles if n in prog_bloom_data['Nivel_Bloom'].values]
        fig_bar_prog = px.bar(
            prog_bloom_data[prog_bloom_data['Nivel_Bloom'].isin(lvls_prog)],
            x='Programa', y='pct', color='Nivel_Bloom',
            color_discrete_map=colores_bloom,
            category_orders={'Nivel_Bloom': lvls_prog},
            title="Distribución de niveles Bloom por programa (100% apilado)",
            labels={'pct': '% de RAs', 'Programa': '', 'Nivel_Bloom': 'Nivel'},
            barmode='stack', text_auto='.0f'
        )
        fig_bar_prog.update_layout(height=420, xaxis_tickangle=15, yaxis_title="% de RAs")
        st.plotly_chart(fig_bar_prog, use_container_width=True)

        st.markdown("---")

        # ── 4. Explorar RAs por nivel ─────────────────────────────────────────
        st.subheader("Explorar Resultados de Aprendizaje por Nivel")
        nivel_sel = st.selectbox(
            "Selecciona un nivel Bloom para ver los RAs correspondientes:",
            orden_niveles,
            key="nivel_bloom_sel"
        )
        df_nivel = (
            df_bloom[df_bloom['Nivel_Bloom'] == nivel_sel]
            [['Programa', 'Semestre', 'Nombre asignatura o modulo', 'Resultado de aprendizaje']]
            .drop_duplicates()
            .sort_values(['Programa', 'Semestre'])
        )
        st.markdown(f"**{len(df_nivel)} resultados de aprendizaje** en nivel **{nivel_sel}**")
        st.dataframe(df_nivel, use_container_width=True, hide_index=True)

    # ─────────────────────────────────────────────────────────────────────────
    # TAB 2 — MAPA DE INTEGRACIÓN
    # ─────────────────────────────────────────────────────────────────────────
    with tab_mapa:
        st.subheader("Mapa de Integración entre Asignaturas")
        st.caption(
            "Visualiza qué asignaturas **comparten núcleos temáticos**. "
            "Un nodo = una asignatura; una línea = al menos un núcleo en común. "
            "El grosor de la línea indica la cantidad de núcleos compartidos. "
            "Útil para detectar redundancias, solapamientos u oportunidades de articulación curricular."
        )

        asig_col = 'Nombre asignatura o modulo'

        # Filtro por programa
        prog_mapa = st.multiselect(
            "Filtrar por programa:",
            sorted(df['Programa'].unique().tolist()),
            default=sorted(df['Programa'].unique().tolist()),
            key="mapa_prog_filter"
        )
        df_mapa = df[df['Programa'].isin(prog_mapa)] if prog_mapa else df

        # Construir diccionario: asignatura -> set de núcleos
        nucleos_dict: Dict[str, set] = {}
        prog_asig: Dict[str, str] = {}
        for _, row in df_mapa.iterrows():
            asig = str(row.get(asig_col, '')).strip()
            if not asig or asig in ('nan', ''):
                continue
            raw_nuc = str(row.get('Nucleos tematicos', '')).strip()
            if raw_nuc and raw_nuc not in ('nan', ''):
                nset = {
                    _limpiar_nucleo(n.strip()).lower()
                    for n in re.split(r'[,;\n]+', raw_nuc)
                    if n.strip() and len(n.strip()) > 3
                }
            else:
                nset = set()
            if asig not in nucleos_dict:
                nucleos_dict[asig] = set()
                prog_asig[asig] = str(row.get('Programa', ''))
            nucleos_dict[asig] |= nset

        subjects = sorted(nucleos_dict.keys())
        n_subjects = len(subjects)

        if n_subjects < 2:
            st.warning("Se necesitan al menos 2 asignaturas con núcleos temáticos para construir el mapa.")
        else:
            # Construir pares con núcleos compartidos
            pares_compartidos = []
            for i in range(n_subjects):
                for j in range(i + 1, n_subjects):
                    s1, s2 = subjects[i], subjects[j]
                    shared = nucleos_dict[s1] & nucleos_dict[s2]
                    if shared:
                        pares_compartidos.append({
                            'Asignatura 1': s1,
                            'Asignatura 2': s2,
                            'Programa 1': prog_asig[s1],
                            'Programa 2': prog_asig[s2],
                            'Núcleos compartidos': len(shared),
                            'Temas compartidos': ', '.join(sorted(shared)[:5]) + ('…' if len(shared) > 5 else '')
                        })

            df_pares = pd.DataFrame(pares_compartidos)

            if df_pares.empty:
                st.info("No se encontraron núcleos temáticos compartidos entre las asignaturas seleccionadas.")
            else:
                # Grado de conectividad
                degree: Counter = Counter()
                for _, row in df_pares.iterrows():
                    degree[row['Asignatura 1']] += int(row['Núcleos compartidos'])
                    degree[row['Asignatura 2']] += int(row['Núcleos compartidos'])

                connected_set = set(df_pares['Asignatura 1'].tolist() + df_pares['Asignatura 2'].tolist())
                isolated_subjects = [s for s in subjects if s not in connected_set]

                col_m1, col_m2, col_m3 = st.columns(3)
                col_m1.metric("Asignaturas en el mapa", n_subjects)
                col_m2.metric("Pares con núcleos compartidos", len(df_pares))
                col_m3.metric("Asignaturas sin conexiones", len(isolated_subjects),
                              delta="aisladas" if isolated_subjects else "Todas conectadas",
                              delta_color="off")
                st.markdown("---")

                # ── Red de integración (grafo circular) ──────────────────────
                st.subheader("Red de Integración Temática")
                max_nodes = 40
                if n_subjects > max_nodes:
                    st.info(
                        f"Hay **{n_subjects}** asignaturas. Mostrando las **{max_nodes}** "
                        f"con mayor conectividad temática."
                    )
                    top_subjects = [s for s, _ in degree.most_common(max_nodes)]
                else:
                    top_subjects = subjects

                n_top = len(top_subjects)
                idx_map = {s: i for i, s in enumerate(top_subjects)}
                angles_list = [2 * _math.pi * i / n_top for i in range(n_top)]
                x_pos = {s: _math.cos(a) for s, a in zip(top_subjects, angles_list)}
                y_pos = {s: _math.sin(a) for s, a in zip(top_subjects, angles_list)}

                # Color por programa
                progs_unicos = sorted({prog_asig[s] for s in top_subjects})
                palette = px.colors.qualitative.Set2 + px.colors.qualitative.Pastel
                prog_color_map = {p: palette[i % len(palette)] for i, p in enumerate(progs_unicos)}

                # Aristas
                max_shared = int(df_pares['Núcleos compartidos'].max()) if not df_pares.empty else 1
                edge_traces = []
                for _, row in df_pares.iterrows():
                    s1, s2 = row['Asignatura 1'], row['Asignatura 2']
                    if s1 not in idx_map or s2 not in idx_map:
                        continue
                    w = max(1, min(8, int(row['Núcleos compartidos']) / max_shared * 8))
                    alpha = round(0.15 + (int(row['Núcleos compartidos']) / max_shared) * 0.65, 2)
                    edge_traces.append(go.Scatter(
                        x=[x_pos[s1], x_pos[s2], None],
                        y=[y_pos[s1], y_pos[s2], None],
                        mode='lines',
                        line=dict(width=w, color=f'rgba(100,100,100,{alpha})'),
                        hoverinfo='none',
                        showlegend=False
                    ))

                # Nodos por programa (una traza por programa para la leyenda)
                node_traces = []
                for prog in progs_unicos:
                    subs_prog = [s for s in top_subjects if prog_asig[s] == prog]
                    node_traces.append(go.Scatter(
                        x=[x_pos[s] for s in subs_prog],
                        y=[y_pos[s] for s in subs_prog],
                        mode='markers+text',
                        name=prog[:35],
                        text=[s[:22] + ('…' if len(s) > 22 else '') for s in subs_prog],
                        textposition='top center',
                        textfont=dict(size=8),
                        marker=dict(
                            size=[10 + min(degree.get(s, 0), 25) for s in subs_prog],
                            color=prog_color_map[prog],
                            line=dict(width=1, color='white')
                        ),
                        hovertext=[
                            f"<b>{s}</b><br>Programa: {prog_asig[s]}<br>"
                            f"Peso de conexiones: {degree.get(s, 0)}<br>"
                            f"Núcleos únicos: {len(nucleos_dict.get(s, set()))}"
                            for s in subs_prog
                        ],
                        hoverinfo='text'
                    ))

                fig_net = go.Figure(data=edge_traces + node_traces)
                fig_net.update_layout(
                    title="Red de integración temática (nodos = asignaturas, líneas = núcleos compartidos)",
                    height=660,
                    showlegend=True,
                    legend=dict(title="Programa", orientation='v', x=1.01, font=dict(size=10)),
                    xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                    yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                    plot_bgcolor='white',
                    margin=dict(t=50, b=20, l=20, r=20)
                )
                st.plotly_chart(fig_net, use_container_width=True)
                st.caption(
                    "**Lectura:** El tamaño del nodo refleja el peso total de conexiones temáticas. "
                    "Nodos muy grandes son asignaturas articuladoras del currículo. "
                    "Nodos aislados (sin líneas) pueden indicar asignaturas sin integración con otras."
                )

                st.markdown("---")

                # ── Heatmap de núcleos compartidos (si hay pocas asignaturas) ─
                if n_subjects <= 35:
                    st.subheader("Matriz de Integración (Núcleos Compartidos)")
                    st.caption(
                        "Cada celda muestra cuántos núcleos temáticos comparten dos asignaturas. "
                        "Valores altos indican alta integración (o posible redundancia a revisar)."
                    )
                    mat = pd.DataFrame(0, index=subjects, columns=subjects)
                    for _, row in df_pares.iterrows():
                        mat.loc[row['Asignatura 1'], row['Asignatura 2']] = int(row['Núcleos compartidos'])
                        mat.loc[row['Asignatura 2'], row['Asignatura 1']] = int(row['Núcleos compartidos'])
                    short = {s: (s[:30] + '…' if len(s) > 30 else s) for s in subjects}
                    mat_disp = mat.rename(index=short, columns=short)
                    fig_heat = px.imshow(
                        mat_disp.values,
                        x=mat_disp.columns.tolist(),
                        y=mat_disp.index.tolist(),
                        color_continuous_scale='YlOrRd',
                        aspect='auto',
                        title="Núcleos temáticos compartidos entre asignaturas",
                        labels=dict(color="Núcleos comunes")
                    )
                    fig_heat.update_layout(
                        height=max(400, n_subjects * 18),
                        xaxis_tickangle=45,
                        xaxis=dict(tickfont=dict(size=9)),
                        yaxis=dict(tickfont=dict(size=9))
                    )
                    st.plotly_chart(fig_heat, use_container_width=True)
                    st.markdown("---")

                # ── Top pares con más núcleos compartidos ─────────────────────
                st.subheader("Pares con Mayor Integración Temática")
                st.caption(
                    "Asignaturas que comparten más núcleos temáticos — "
                    "candidatas a articulación explícita o revisión de solapamiento."
                )
                df_top = df_pares.sort_values('Núcleos compartidos', ascending=False).head(20)
                st.dataframe(df_top, use_container_width=True, hide_index=True)

                # ── Asignaturas aisladas ───────────────────────────────────────
                if isolated_subjects:
                    with st.expander(f"⚠️ Asignaturas sin integración temática ({len(isolated_subjects)})"):
                        st.caption(
                            "Estas asignaturas no comparten ningún núcleo temático con otras. "
                            "Pueden ser especializadas (normal) o indicar falta de articulación curricular."
                        )
                        for s in sorted(isolated_subjects):
                            st.markdown(f"- **{s}** — Programa: {prog_asig.get(s, 'N/A')}")


def pagina_config_tendencias():
    """Pagina para configurar tendencias personalizables."""
    st.title("Configurar Tendencias Globales")
    st.markdown("---")

    tendencias = obtener_tendencias()

    # --- Importar tendencias desde JSON ---
    st.subheader("Importar / Exportar Configuracion")
    col_imp, col_exp = st.columns(2)

    with col_imp:
        uploaded_json = st.file_uploader(
            "Importar tendencias desde JSON:",
            type=['json'],
            key='json_upload'
        )
        if uploaded_json is not None:
            try:
                config = json.load(uploaded_json)
                nuevas = config.get('TENDENCIAS_GLOBALES', config)
                if isinstance(nuevas, dict) and len(nuevas) > 0:
                    st.session_state['tendencias'] = nuevas
                    st.success(f"{len(nuevas)} tendencias importadas.")
                    st.rerun()
            except Exception as e:
                st.error(f"Error al importar: {e}")

    with col_exp:
        config_export = {
            "TENDENCIAS_GLOBALES": tendencias,
            "VERSION": "1.0"
        }
        json_str = json.dumps(config_export, ensure_ascii=False, indent=2)
        st.download_button(
            label="Descargar configuracion actual (JSON)",
            data=json_str,
            file_name="config_tendencias.json",
            mime="application/json"
        )

    st.markdown("---")

    # --- Tendencias actuales ---
    st.subheader(f"Tendencias Actuales ({len(tendencias)})")
    for tid, tinfo in tendencias.items():
        with st.expander(f"{tinfo['descripcion']} ({len(tinfo['keywords'])} keywords)"):
            st.markdown(f"**ID:** `{tid}`")
            st.markdown(f"**Color:** {tinfo['color']}")
            st.markdown(f"**Keywords:** {', '.join(tinfo['keywords'])}")

    st.markdown("---")

    # --- Agregar nueva tendencia ---
    st.subheader("Agregar Nueva Tendencia")
    with st.form("nueva_tendencia"):
        col1, col2 = st.columns(2)
        with col1:
            nuevo_id = st.text_input("ID (sin espacios):", placeholder="MI_TENDENCIA")
            nueva_desc = st.text_input("Descripcion:", placeholder="Mi nueva tendencia")
        with col2:
            nuevo_color = st.color_picker("Color:", "#FF5733")
            nuevas_keywords = st.text_area(
                "Keywords (una por linea):",
                placeholder="keyword1\nkeyword2\nfrase clave"
            )

        submitted = st.form_submit_button("Agregar Tendencia")

        if submitted and nuevo_id and nueva_desc and nuevas_keywords:
            keywords_list = [k.strip() for k in nuevas_keywords.split('\n') if k.strip()]
            if keywords_list:
                st.session_state['tendencias'][nuevo_id] = {
                    "keywords": keywords_list,
                    "color": nuevo_color,
                    "descripcion": nueva_desc
                }
                st.success(f"Tendencia '{nueva_desc}' agregada con {len(keywords_list)} keywords.")
                st.rerun()
            else:
                st.error("Debes ingresar al menos una keyword.")

    st.markdown("---")

    # --- Eliminar tendencia ---
    st.subheader("Eliminar Tendencia")
    if tendencias:
        tid_eliminar = st.selectbox(
            "Seleccionar tendencia a eliminar:",
            list(tendencias.keys()),
            format_func=lambda x: tendencias[x]['descripcion']
        )
        if st.button("Eliminar Tendencia Seleccionada"):
            del st.session_state['tendencias'][tid_eliminar]
            st.success("Tendencia eliminada.")
            st.rerun()

    st.markdown("---")

    # --- Restaurar por defecto ---
    if st.button("Restaurar Tendencias por Defecto"):
        st.session_state['tendencias'] = json.loads(json.dumps(TENDENCIAS_DEFAULT))
        st.success("Tendencias restauradas a valores por defecto.")
        st.rerun()


def pagina_datos(df: pd.DataFrame):
    """Pagina de exploracion de datos crudos."""
    st.title("Explorar Datos")
    st.markdown("---")

    col1, col2, col3 = st.columns(3)
    with col1:
        prog_filter = st.multiselect(
            "Programa:", df['Programa'].unique(),
            default=list(df['Programa'].unique())
        )
    with col2:
        tipo_filter = st.multiselect(
            "Tipo de Saber:", df['Tipo de Saber'].unique(),
            default=list(df['Tipo de Saber'].unique())
        )
    with col3:
        semestres_disponibles = sorted(df['Semestre'].dropna().unique(), key=lambda x: str(x))
        sem_filter = st.multiselect(
            "Semestre:", semestres_disponibles,
            default=list(semestres_disponibles)
        )

    df_filtered = df[
        (df['Programa'].isin(prog_filter)) &
        (df['Tipo de Saber'].isin(tipo_filter)) &
        (df['Semestre'].isin(sem_filter))
    ]

    st.markdown(f"**Registros filtrados:** {len(df_filtered)}")

    columnas_mostrar = [
        'Programa', 'Tipo de Saber', 'Semestre',
        'Nombre asignatura o modulo', 'Resultado de aprendizaje',
        'Indicadores de logro asignatura o modulo', 'Nucleos tematicos'
    ]
    cols_disponibles = [c for c in columnas_mostrar if c in df_filtered.columns]
    st.dataframe(df_filtered[cols_disponibles], use_container_width=True, hide_index=True)

    csv = df_filtered.to_csv(index=False, encoding='utf-8-sig')
    st.download_button(
        label="Descargar datos filtrados (CSV)",
        data=csv,
        file_name="datos_filtrados.csv",
        mime="text/csv"
    )


# ============================================================================
# MAIN
# ============================================================================

def main():
    # --- SIDEBAR ---
    st.sidebar.title("Configuracion")
    st.sidebar.markdown("---")

    # Carga de archivos
    st.sidebar.subheader("Cargar Archivos Excel")
    uploaded_files = st.sidebar.file_uploader(
        "Selecciona los archivos .xlsx de los programas:",
        type=['xlsx'],
        accept_multiple_files=True,
        help="Sube uno o mas archivos Excel con la hoja 'Paso 5 Estrategias micro'"
    )

    if not uploaded_files:
        # Pantalla de bienvenida
        st.title("Analisis Tematico Microcurricular")
        st.markdown("---")
        st.markdown("""
        ### Bienvenido al sistema de analisis tematico avanzado

        Este dashboard analiza los programas academicos en 3 dimensiones:

        1. **Cobertura y Densidad Tematica** - Nucleos tematicos, diversidad, solapamiento
        2. **Alineacion con Tendencias Globales** - Sostenibilidad, IA, Innovacion, etc.
        3. **Mineria de Texto (NLP)** - TF-IDF, n-gramas, similitud entre asignaturas

        ---

        ### Como empezar

        1. Sube tus archivos Excel (.xlsx) en el panel lateral izquierdo
        2. Los archivos deben tener la hoja **'Paso 5 Estrategias micro'** con encabezados en la fila 2
        3. El analisis se ejecutara automaticamente al cargar los archivos

        ---

        ### Estructura esperada del Excel

        | Columna | Descripcion |
        |---------|-------------|
        | Tipo de Saber | Saber, SaberHacer, SaberSer |
        | Resultado de aprendizaje | Texto del RA |
        | Nombre asignatura o modulo | Nombre de la asignatura |
        | Indicadores de logro | Texto de indicadores |
        | Nucleos tematicos | Temas separados por coma o punto y coma |

        ---

        > Puedes configurar las **tendencias globales** a detectar en la pagina "Configurar Tendencias"
        """)
        st.stop()

    # Procesar archivos
    df = procesar_archivos(uploaded_files)

    if df.empty:
        st.error(
            "No se pudieron cargar datos. Verifica que los archivos tengan "
            "la hoja 'Paso 5 Estrategias micro' con encabezados en la fila 2."
        )
        st.stop()

    # Info sidebar
    st.sidebar.success(f"{len(uploaded_files)} archivos cargados")
    st.sidebar.markdown(
        f"**Datos procesados:**\n"
        f"- {len(df)} registros\n"
        f"- {df['Programa'].nunique()} programas\n"
        f"- {df['Nombre asignatura o modulo'].nunique()} asignaturas"
    )

    st.sidebar.markdown("---")

    # Navegacion
    st.sidebar.subheader("Navegación")
    st.sidebar.caption("Selecciona una sección para analizar:")

    PAGINAS = {
        "📋 Resumen Ejecutivo": "Alertas, fortalezas y recomendaciones para toma de decisiones",
        "🏠 Inicio": "Resumen general y métricas clave del currículo",
        "📊 Tipo de Saber": "Saber, SaberHacer y SaberSer por semestre y asignatura",
        "🗂️ Cobertura Temática": "Núcleos temáticos: diversidad y densidad por programa",
        "🌍 Tendencias Globales": "Alineación con IA, Sostenibilidad, Innovación, etc.",
        "🔍 Minería de Texto": "Términos clave, similitud y frases frecuentes",
        "🎓 Bloom & Integración": "Taxonomía de Bloom por semestre y mapa de integración temática",
        "⚙️ Configurar Tendencias": "Personalizar las tendencias globales a detectar",
        "📄 Explorar Datos": "Explorar y filtrar los registros cargados",
    }

    pagina = st.sidebar.radio(
        "Ir a:",
        list(PAGINAS.keys()),
        format_func=lambda x: x
    )

    # Mostrar descripcion de la pagina seleccionada
    st.sidebar.caption(f"_{PAGINAS[pagina]}_")
    st.sidebar.markdown("---")

    # Obtener tendencias
    tendencias = obtener_tendencias()

    # Renderizar pagina
    if pagina == "📋 Resumen Ejecutivo":
        with st.spinner("Generando resumen ejecutivo..."):
            pagina_resumen_ejecutivo(df, tendencias)

    elif pagina == "🏠 Inicio":
        pagina_inicio(df)

    elif pagina == "📊 Tipo de Saber":
        pagina_tipo_saber(df)

    elif pagina == "🗂️ Cobertura Temática":
        with st.spinner("Analizando cobertura temática..."):
            resultados_cob = analizar_cobertura(df)
        pagina_cobertura(df, resultados_cob)

    elif pagina == "🌍 Tendencias Globales":
        with st.spinner("Detectando tendencias globales..."):
            resultados_tend = analizar_tendencias(df, tendencias)
        pagina_tendencias(df, tendencias, resultados_tend)

    elif pagina == "🔍 Minería de Texto":
        with st.spinner("Ejecutando análisis de texto..."):
            resultados_nlp = analizar_nlp(df)
        pagina_nlp(df, resultados_nlp)

    elif pagina == "🎓 Bloom & Integración":
        pagina_bloom_integracion(df)

    elif pagina == "⚙️ Configurar Tendencias":
        pagina_config_tendencias()

    elif pagina == "📄 Explorar Datos":
        pagina_datos(df)


if __name__ == '__main__':
    main()
