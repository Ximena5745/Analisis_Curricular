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
    """Detecta tendencias globales en los datos."""
    programas = df['Programa'].unique()
    matriz = pd.DataFrame(0, index=programas, columns=list(tendencias.keys()))
    detalle = {t: {p: [] for p in programas} for t in tendencias}

    for _, row in df.iterrows():
        programa = row['Programa']
        texto = str(row.get('Texto_Completo', '')).lower()

        for tid, tinfo in tendencias.items():
            for kw in tinfo['keywords']:
                if kw.lower() in texto:
                    matriz.loc[programa, tid] += 1
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
                        'asignatura': row.get('Nombre asignatura o modulo', '')
                    })
                    break

    cobertura = {}
    for tid in tendencias:
        programas_con = (matriz[tid] > 0).sum()
        cobertura[tid] = (programas_con / len(programas)) * 100

    ausentes = [tid for tid, pct in cobertura.items() if pct == 0]

    return {
        'matriz': matriz,
        'cobertura': cobertura,
        'detalle': detalle,
        'ausentes': ausentes
    }


def analizar_nlp(df: pd.DataFrame) -> Dict:
    """Analisis de mineria de texto con TF-IDF."""
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

    # Similitud entre asignaturas
    df_asig = df.groupby('Nombre asignatura o modulo')['Texto_Completo'].apply(
        lambda x: ' '.join(x)
    ).reset_index()

    similitud_df = pd.DataFrame()
    par_similar = None
    if len(df_asig) > 2:
        vec_asig = TfidfVectorizer(max_features=50, stop_words=list(STOPWORDS_ES))
        tfidf_asig = vec_asig.fit_transform(df_asig['Texto_Completo'])
        sim = cosine_similarity(tfidf_asig)
        similitud_df = pd.DataFrame(
            sim,
            index=df_asig['Nombre asignatura o modulo'],
            columns=df_asig['Nombre asignatura o modulo']
        )
        np.fill_diagonal(sim, 0)
        max_idx = np.unravel_index(sim.argmax(), sim.shape)
        par_similar = {
            'asig1': df_asig.iloc[max_idx[0]]['Nombre asignatura o modulo'],
            'asig2': df_asig.iloc[max_idx[1]]['Nombre asignatura o modulo'],
            'similitud': float(sim[max_idx])
        }

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
        'similitud_df': similitud_df,
        'par_similar': par_similar,
        'top_ngrams': dict(top_ngrams)
    }


# ============================================================================
# PAGINAS DEL DASHBOARD
# ============================================================================

def pagina_inicio(df: pd.DataFrame):
    """Pagina de inicio con metricas generales."""
    st.title("Analisis Tematico Microcurricular")
    st.markdown("---")

    programas = df['Programa'].unique()
    asignaturas = df['Nombre asignatura o modulo'].nunique()
    total_registros = len(df)
    total_palabras = df['Texto_Completo'].str.split().str.len().sum()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Programas", len(programas))
    col2.metric("Registros", f"{total_registros:,}")
    col3.metric("Asignaturas", asignaturas)
    col4.metric("Palabras analizadas", f"{int(total_palabras):,}")

    st.markdown("---")

    col_a, col_b = st.columns(2)

    with col_a:
        st.subheader("Registros por Programa")
        conteo = df['Programa'].value_counts().reset_index()
        conteo.columns = ['Programa', 'Registros']
        fig = px.bar(conteo, x='Programa', y='Registros',
                     color='Programa', text='Registros')
        fig.update_layout(showlegend=False, height=400)
        st.plotly_chart(fig, use_container_width=True)

    with col_b:
        st.subheader("Distribucion Tipo de Saber")
        tipo_saber = df['Tipo de Saber'].value_counts().reset_index()
        tipo_saber.columns = ['Tipo', 'Cantidad']
        fig = px.pie(tipo_saber, values='Cantidad', names='Tipo',
                     color_discrete_sequence=px.colors.qualitative.Set2)
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Resumen por Programa")
    resumen = df.groupby('Programa').agg(
        Registros=('Tipo de Saber', 'count'),
        Asignaturas=('Nombre asignatura o modulo', 'nunique'),
        Semestres=('Semestre', 'nunique'),
        Creditos=('Creditos', 'sum')
    ).reset_index()
    st.dataframe(resumen, use_container_width=True, hide_index=True)


def pagina_cobertura(df: pd.DataFrame, resultados: Dict):
    """Pagina de cobertura y densidad tematica."""
    st.title("Cobertura y Densidad Tematica")
    st.markdown("---")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Nucleos Unicos", resultados['nucleos_unicos'])
    col2.metric("Total Menciones", f"{resultados['total_menciones']:,}")
    col3.metric("Promedio/Asignatura", f"{resultados['promedio_densidad']:.1f}")
    col4.metric("Diversidad", f"{resultados['diversidad']:.1f}/100")

    st.markdown("---")

    st.subheader("Matriz: Programa x Nucleos Tematicos (Top 20)")
    matriz = resultados['matriz_cobertura']
    if not matriz.empty:
        fig = px.imshow(
            matriz.values,
            x=matriz.columns.tolist(),
            y=matriz.index.tolist(),
            color_continuous_scale='YlOrRd',
            text_auto=True,
            aspect='auto'
        )
        fig.update_layout(height=400, xaxis_tickangle=45)
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    col_a, col_b = st.columns(2)

    with col_a:
        st.subheader("Top 20 Nucleos Tematicos")
        top_nucleos = resultados['nucleos_counter'].most_common(20)
        df_nucleos = pd.DataFrame(top_nucleos, columns=['Nucleo', 'Frecuencia'])
        fig = px.bar(df_nucleos, y='Nucleo', x='Frecuencia',
                     orientation='h', color='Frecuencia',
                     color_continuous_scale='Blues')
        fig.update_layout(height=600, yaxis={'categoryorder': 'total ascending'})
        st.plotly_chart(fig, use_container_width=True)

    with col_b:
        st.subheader("Densidad Tematica (Top 20 Asignaturas)")
        densidad_top = resultados['densidad_asignatura'].head(20)
        df_densidad = pd.DataFrame({
            'Asignatura': densidad_top.index,
            'Nucleos': densidad_top.values
        })
        fig = px.bar(df_densidad, y='Asignatura', x='Nucleos',
                     orientation='h', color='Nucleos',
                     color_continuous_scale='Oranges')
        fig.update_layout(height=600, yaxis={'categoryorder': 'total ascending'})
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.subheader("Explorar Nucleos por Programa")
    programa_sel = st.selectbox("Seleccionar programa:", df['Programa'].unique())
    df_prog = df[df['Programa'] == programa_sel]

    nucleos_prog = []
    for _, row in df_prog.iterrows():
        nucleos_raw = str(row.get('Nucleos tematicos', ''))
        if nucleos_raw and nucleos_raw != 'nan':
            nucleos = re.split(r'[,;\n]+', nucleos_raw)
            nucleos_prog.extend([_limpiar_nucleo(n.strip()) for n in nucleos if n.strip() and len(n.strip()) > 3])

    if nucleos_prog:
        counter_prog = Counter(nucleos_prog)
        df_prog_nucleos = pd.DataFrame(
            counter_prog.most_common(15),
            columns=['Nucleo', 'Frecuencia']
        )
        fig = px.bar(df_prog_nucleos, x='Nucleo', y='Frecuencia',
                     color='Frecuencia', color_continuous_scale='Viridis',
                     title=f"Top 15 Nucleos - {programa_sel}")
        fig.update_layout(xaxis_tickangle=45, height=400)
        st.plotly_chart(fig, use_container_width=True)


def pagina_tendencias(df: pd.DataFrame, tendencias: Dict, resultados: Dict):
    """Pagina de alineacion con tendencias globales."""
    st.title("Alineacion con Tendencias Globales")
    st.markdown("---")

    total_tend = len(tendencias)
    detectadas = total_tend - len(resultados['ausentes'])
    col1, col2, col3 = st.columns(3)
    col1.metric("Tendencias Evaluadas", total_tend)
    col2.metric("Tendencias Detectadas", detectadas)
    col3.metric("Tendencias Ausentes", len(resultados['ausentes']))

    st.markdown("---")

    st.subheader("Matriz: Programa x Tendencias")
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
        st.subheader("Cobertura por Tendencia (%)")
        cobertura_data = []
        for tid, pct in resultados['cobertura'].items():
            nombre = tendencias[tid]['descripcion'] if tid in tendencias else tid
            cobertura_data.append({'Tendencia': nombre, 'Cobertura': pct})
        df_cob = pd.DataFrame(cobertura_data).sort_values('Cobertura', ascending=True)

        fig = px.bar(df_cob, y='Tendencia', x='Cobertura',
                     orientation='h', color='Cobertura',
                     color_continuous_scale='RdYlGn',
                     range_color=[0, 100])
        fig.add_vline(x=100, line_dash="dash", line_color="red", opacity=0.5)
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)

    with col_b:
        st.subheader("Menciones Totales por Tendencia")
        menciones_data = []
        for tid in tendencias:
            if tid in resultados['matriz'].columns:
                nombre = tendencias[tid]['descripcion']
                total = int(resultados['matriz'][tid].sum())
                menciones_data.append({'Tendencia': nombre, 'Menciones': total})
        df_menciones = pd.DataFrame(menciones_data).sort_values('Menciones', ascending=True)

        fig = px.bar(df_menciones, y='Tendencia', x='Menciones',
                     orientation='h', color='Menciones',
                     color_continuous_scale='Blues')
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)

    if resultados['ausentes']:
        st.markdown("---")
        st.subheader("Brechas Detectadas")
        st.warning("Las siguientes tendencias NO fueron detectadas en ningun programa:")
        for tid in resultados['ausentes']:
            if tid in tendencias:
                st.markdown(f"- **{tendencias[tid]['descripcion']}**")

    st.markdown("---")
    st.subheader("Detalle por Tendencia")
    tend_sel = st.selectbox(
        "Seleccionar tendencia:",
        list(tendencias.keys()),
        format_func=lambda x: tendencias[x]['descripcion']
    )

    if tend_sel in resultados['detalle']:
        for programa, hallazgos in resultados['detalle'][tend_sel].items():
            if hallazgos:
                with st.expander(f"{programa} ({len(hallazgos)} hallazgos)"):
                    asig_set = set()
                    for h in hallazgos:
                        asig_set.add(h.get('asignatura', 'N/A'))
                    st.markdown(f"**Asignaturas:** {len(asig_set)}")
                    for asig in sorted(asig_set, key=lambda x: str(x)):
                        st.markdown(f"- {asig}")


def pagina_nlp(df: pd.DataFrame, resultados: Dict):
    """Pagina de mineria de texto."""
    st.title("Mineria de Texto y Analisis Semantico")
    st.markdown("---")

    col_a, col_b = st.columns(2)

    with col_a:
        st.subheader("Top Terminos Clave (TF-IDF)")
        n_terms = st.slider("Numero de terminos:", 10, 30, 20, key='slider_tfidf')
        top_items = list(resultados['top_terminos'].items())[:n_terms]
        df_terms = pd.DataFrame(top_items, columns=['Termino', 'Score'])
        df_terms = df_terms.sort_values('Score', ascending=True)

        fig = px.bar(df_terms, y='Termino', x='Score',
                     orientation='h', color='Score',
                     color_continuous_scale='Plasma')
        fig.update_layout(height=max(400, n_terms * 25))
        st.plotly_chart(fig, use_container_width=True)

    with col_b:
        st.subheader("Top N-gramas Frecuentes")
        n_ng = st.slider("Numero de n-gramas:", 5, 20, 15, key='slider_ngrams')
        ng_items = list(resultados['top_ngrams'].items())[:n_ng]
        df_ng = pd.DataFrame(ng_items, columns=['N-grama', 'Frecuencia'])
        df_ng = df_ng.sort_values('Frecuencia', ascending=True)

        fig = px.bar(df_ng, y='N-grama', x='Frecuencia',
                     orientation='h', color='Frecuencia',
                     color_continuous_scale='Magma')
        fig.update_layout(height=max(400, n_ng * 25))
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    st.subheader("Terminos Clave por Programa")
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
                             title=f"Terminos clave - {programa}")
                fig.update_layout(height=450)
                st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    st.subheader("Similitud entre Asignaturas")

    if resultados['par_similar']:
        par = resultados['par_similar']
        st.info(
            f"**Par mas similar:** {par['asig1']} <-> {par['asig2']} "
            f"(Similitud: {par['similitud']:.1%})"
        )

    if not resultados['similitud_df'].empty:
        sim_df = resultados['similitud_df']

        if len(sim_df) <= 30:
            fig = px.imshow(
                sim_df.values,
                x=sim_df.columns.tolist(),
                y=sim_df.index.tolist(),
                color_continuous_scale='RdBu_r',
                text_auto='.2f',
                aspect='auto'
            )
            fig.update_layout(height=700, xaxis_tickangle=45)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.markdown("Demasiadas asignaturas para heatmap. Mostrando top pares:")
            sim_vals = sim_df.values.copy()
            np.fill_diagonal(sim_vals, 0)
            pares = []
            for i in range(len(sim_vals)):
                for j in range(i+1, len(sim_vals)):
                    pares.append({
                        'Asignatura 1': sim_df.index[i],
                        'Asignatura 2': sim_df.columns[j],
                        'Similitud': sim_vals[i, j]
                    })
            df_pares = pd.DataFrame(pares).sort_values('Similitud', ascending=False).head(20)
            st.dataframe(df_pares, use_container_width=True, hide_index=True)

    st.markdown("---")
    st.subheader("Buscar Terminos en los Datos")
    termino_buscar = st.text_input("Escribe un termino o frase para buscar:")
    if termino_buscar:
        mask = df['Texto_Completo'].str.contains(termino_buscar.lower(), na=False)
        resultados_busqueda = df[mask][['Programa', 'Nombre asignatura o modulo',
                                        'Tipo de Saber', 'Semestre']].drop_duplicates()
        st.markdown(f"**{len(resultados_busqueda)} registros encontrados**")
        st.dataframe(resultados_busqueda, use_container_width=True, hide_index=True)


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
    st.sidebar.subheader("Navegacion")
    pagina = st.sidebar.radio(
        "Seleccionar pagina:",
        [
            "Inicio",
            "Cobertura Tematica",
            "Tendencias Globales",
            "Mineria de Texto",
            "Configurar Tendencias",
            "Explorar Datos"
        ]
    )

    # Obtener tendencias
    tendencias = obtener_tendencias()

    # Renderizar pagina
    if pagina == "Inicio":
        pagina_inicio(df)

    elif pagina == "Cobertura Tematica":
        with st.spinner("Analizando cobertura tematica..."):
            resultados_cob = analizar_cobertura(df)
        pagina_cobertura(df, resultados_cob)

    elif pagina == "Tendencias Globales":
        with st.spinner("Detectando tendencias globales..."):
            resultados_tend = analizar_tendencias(df, tendencias)
        pagina_tendencias(df, tendencias, resultados_tend)

    elif pagina == "Mineria de Texto":
        with st.spinner("Ejecutando analisis NLP..."):
            resultados_nlp = analizar_nlp(df)
        pagina_nlp(df, resultados_nlp)

    elif pagina == "Configurar Tendencias":
        pagina_config_tendencias()

    elif pagina == "Explorar Datos":
        pagina_datos(df)


if __name__ == '__main__':
    main()
