"""
DASHBOARD INTERACTIVO - Analisis Tematico Avanzado
Compatible con Streamlit Cloud y ejecucion local.

Ejecutar local: streamlit run dashboard_tematico.py
Deploy cloud:   Subir repo a GitHub y conectar en share.streamlit.io
"""

import streamlit as st
import streamlit.components.v1 as st_components
from streamlit_option_menu import option_menu
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from collections import Counter
import re
import json
import unicodedata
from typing import Dict, Optional
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import AgglomerativeClustering
from scipy.stats import entropy
import warnings
warnings.filterwarnings('ignore')


# Patrones que NO son núcleos temáticos (encabezados de sección, instrucciones, etc.)
_PATRON_NO_NUCLEO = re.compile(
    r'^(construccion\s+y\s+dinamicas?|dinamicas?\s+de|estrategias?\s+de\s+(ensenanza|aprendizaje|evaluacion)|'
    r'actividades?\s+(de\s+)?(aprendizaje|evaluacion)|metodologia|criterios?\s+de|recursos?\s+(educativos?|didacticos?)|'
    r'indicadores?\s+de|competencias?\s+(generales?|especificas?)|resultados?\s+de\s+aprendizaje|'
    r'nucleo\s+tematico|temas?\s+a\s+(desarrollar|tratar)|contenido[s]?\s*(del?\s+)?curso|'
    r'unidad\s+(tematica\s+)?\d*|modulo\s+\d*|semana\s+\d*|bloque\s+(tematico)?\s*\d*)',
    re.IGNORECASE
)

# Fragmentos que empiezan con conjunción o preposición: indican que el texto
# es la segunda parte de una expresión compuesta (ej. "o su versión actualizada")
_INICIO_INVALIDO = re.compile(
    r'^(o |y |e |u |ni |pero |sino |aunque |mas |porque |pues |'
    r'de |del |al |a |en |con |sin |por |para |'
    r'lo |la |el |los |las |un |una |'
    r'que |si |su |sus |se |le |les )',
    re.IGNORECASE
)


def _limpiar_nucleo(texto: str) -> str:
    """Elimina numeracion inicial tipo '1. ', '2. ', etc. de un nucleo tematico."""
    texto = re.sub(r'^\d+[\.\)]\s*', '', texto.strip())
    texto = re.sub(r'^[•\-–—*]\s*', '', texto)
    return texto.strip()


def _es_nucleo_valido(texto: str) -> bool:
    """Verifica que el texto sea un nucleo tematico real y no un encabezado o instruccion."""
    t = texto.strip()
    if len(t) < 4 or len(t) > 150:
        return False
    # Descartar si es sólo números o caracteres especiales
    if re.match(r'^[\d\s\.\,\;\:\-]+$', t):
        return False
    # Requerir mínimo 2 palabras (filtra términos sueltos como "construcción", "dinámicas")
    if len(t.split()) < 2:
        return False
    t_norm = unicodedata.normalize('NFKD', t.lower()).encode('ascii', 'ignore').decode('ascii')
    # Descartar patrones no temáticos
    if _PATRON_NO_NUCLEO.match(t_norm):
        return False
    # Descartar fragmentos que son la segunda parte de una expresión compuesta.
    # Se aplica sobre el texto YA LIMPIO (sin numeración "1. " ni viñetas)
    # para que "3. o su versión actualizada" → "o su versión actualizada" sea rechazado.
    t_clean_norm = unicodedata.normalize(
        'NFKD', _limpiar_nucleo(t).lower()
    ).encode('ascii', 'ignore').decode('ascii')
    if _INICIO_INVALIDO.match(t_clean_norm):
        return False
    return True


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
# ESTILOS VISUALES — POLITECNICO GRANCOLOMBIANO
# Paleta: #0F385A (navy) | #1FB2DE (azul) | #42F2F2 (cyan)
#         #FBAF17 (dorado) | #EC0677 (magenta) — tema claro
# ============================================================================

st.markdown("""
<style>
/* ══════════════════════════════════════════════════════════════════════════
   FORZAR MODO CLARO SIEMPRE — pisa variables CSS de Streamlit en dark mode
   ══════════════════════════════════════════════════════════════════════════ */
:root,
:root[data-theme="dark"],
:root[data-theme="light"] {
    color-scheme: light !important;
    --background-color:           #FFFFFF !important;
    --secondary-background-color: #EAF9FD !important;
    --text-color:                 #0F385A !important;
    --font:                       'Segoe UI', 'Inter', sans-serif !important;
    --primary-color:              #1FB2DE !important;
}
/* Cubre la preferencia del sistema operativo en dark mode */
@media (prefers-color-scheme: dark) {
    :root {
        color-scheme: light !important;
        --background-color:           #FFFFFF !important;
        --secondary-background-color: #EAF9FD !important;
        --text-color:                 #0F385A !important;
    }
}

/* ── Fondo y texto de la app principal ──────────────────────────────────── */
html, body,
.stApp, .stApp > div,
.main, .block-container,
[data-testid="stAppViewContainer"],
[data-testid="stHeader"] {
    font-family: 'Segoe UI', 'Inter', sans-serif !important;
    background-color: #FFFFFF !important;
    color: #0F385A !important;
}

/* ── Contenido dentro de tabs, expanders, columnas ─────────────────────── */
.stTabs [data-baseweb="tab-panel"],
[data-testid="stExpander"],
[data-testid="column"] {
    background-color: #FFFFFF !important;
    color: #0F385A !important;
}

/* ── Inputs, selectbox, multiselect ─────────────────────────────────────── */
/* Caja de control (fondo blanco, texto navy) */
[data-baseweb="select"] > div:first-child,
[data-baseweb="base-input"],
.stTextInput input, .stTextArea textarea, .stNumberInput input {
    background-color: #FFFFFF !important;
    color: #0F385A !important;
    border-color: #1FB2DE !important;
}
/* Texto del placeholder e input interno */
[data-baseweb="select"] input,
[data-baseweb="select"] [data-id="datepicker-input"] {
    color: #0F385A !important;
    background-color: transparent !important;
}
/* Chips / tags de items seleccionados en multiselect */
[data-baseweb="tag"] {
    background-color: #EAF9FD !important;
    border: 1px solid #1FB2DE !important;
}
[data-baseweb="tag"] span {
    color: #0F385A !important;
    background-color: transparent !important;
}
[data-baseweb="tag"] button,
[data-baseweb="tag"] [role="button"] {
    color: #0F385A !important;
    background-color: transparent !important;
}
/* Lista desplegable de opciones */
[data-baseweb="menu"],
[data-baseweb="popover"] > div {
    background-color: #FFFFFF !important;
}
[data-baseweb="menu"] li,
[data-baseweb="menu"] [role="option"] {
    color: #0F385A !important;
    background-color: #FFFFFF !important;
}
[data-baseweb="menu"] li:hover,
[data-baseweb="menu"] [role="option"]:hover {
    background-color: #EAF9FD !important;
}
/* Opción seleccionada en el dropdown */
[data-baseweb="menu"] [aria-selected="true"] {
    background-color: #D0F4FA !important;
    color: #0F385A !important;
}

/* ── Métricas y texto general ───────────────────────────────────────────── */
[data-testid="stMetricValue"],
[data-testid="stMetricLabel"],
[data-testid="stMetricDelta"],
.stMarkdown, .stText, p, h1, h2, h3, h4, h5, label {
    color: #0F385A !important;
}

/* ── Barra lateral ──────────────────────────────────────────────────────── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0F385A 0%, #071E32 100%);
    border-right: 3px solid #1FB2DE;
}
[data-testid="stSidebar"] * {
    color: #FFFFFF !important;
}
/* ── option_menu: fondo y texto ─────────────────────────────────────────── */
/* Contenedor principal del menú */
[data-testid="stSidebar"] .nav,
[data-testid="stSidebar"] .nav-pills,
[data-testid="stSidebar"] ul.nav {
    background-color: transparent !important;
}
/* Cada ítem */
[data-testid="stSidebar"] .nav-link,
[data-testid="stSidebar"] a.nav-link {
    color: rgba(255,255,255,0.85) !important;
    background-color: transparent !important;
    border-left: 3px solid transparent !important;
    border-radius: 6px !important;
    padding: 7px 12px !important;
    margin: 2px 0 !important;
    font-size: 13px !important;
    transition: background 0.2s, border-left 0.2s;
}
/* Hover */
[data-testid="stSidebar"] .nav-link:hover,
[data-testid="stSidebar"] a.nav-link:hover {
    background-color: rgba(31,178,222,0.20) !important;
    color: #FFFFFF !important;
}
/* Activo */
[data-testid="stSidebar"] .nav-link.active,
[data-testid="stSidebar"] a.nav-link.active {
    background-color: rgba(31,178,222,0.30) !important;
    border-left: 3px solid #FBAF17 !important;
    color: #FFFFFF !important;
    font-weight: 600 !important;
}
/* Iconos */
[data-testid="stSidebar"] .nav-link i,
[data-testid="stSidebar"] a.nav-link i {
    color: #42F2F2 !important;
}
[data-testid="stSidebar"] hr {
    border-color: rgba(66,242,242,0.25) !important;
}
[data-testid="stSidebar"] .stFileUploader {
    background: rgba(255,255,255,0.07);
    border-radius: 8px;
    padding: 8px;
    border: 1px solid rgba(31,178,222,0.3);
}
/* Zona de drop: fondo oscuro para que el texto blanco sea visible */
[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"],
[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] > div {
    background-color: rgba(7, 30, 50, 0.85) !important;
    border: 1px dashed rgba(66,242,242,0.5) !important;
    border-radius: 6px !important;
}
/* Todos los textos dentro del file uploader */
[data-testid="stSidebar"] [data-testid="stFileUploader"] label,
[data-testid="stSidebar"] [data-testid="stFileUploader"] span,
[data-testid="stSidebar"] [data-testid="stFileUploader"] small,
[data-testid="stSidebar"] [data-testid="stFileUploader"] p,
[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] *,
[data-testid="stSidebar"] [data-testid="stFileUploaderDropzoneInstructions"] * {
    color: #FFFFFF !important;
    background-color: transparent !important;
}
/* Botón "Browse files" */
[data-testid="stSidebar"] [data-testid="stFileUploader"] button,
[data-testid="stSidebar"] [data-testid="stBaseButton-secondary"] {
    background: rgba(31,178,222,0.25) !important;
    border: 1px solid rgba(66,242,242,0.5) !important;
    color: #FFFFFF !important;
    border-radius: 6px !important;
}

/* ── Encabezados principales ─────────────────────────────────────────────── */
h1 {
    color: #0F385A !important;
    border-bottom: 3px solid #1FB2DE;
    padding-bottom: 8px;
}
h2 {
    color: #0F385A !important;
    border-left: 4px solid #1FB2DE;
    padding-left: 10px;
}
h3 {
    color: #0F385A !important;
}

/* ── Tarjetas de métricas ─────────────────────────────────────────────────── */
[data-testid="stMetric"] {
    background: linear-gradient(135deg, #EAF9FD 0%, #F5FEFF 100%);
    border: 1px solid #A8E6F5;
    border-left: 4px solid #1FB2DE;
    border-radius: 10px;
    padding: 14px 16px !important;
    box-shadow: 0 2px 8px rgba(31,178,222,0.12);
}
[data-testid="stMetricValue"] {
    color: #0F385A !important;
    font-weight: 700 !important;
}
[data-testid="stMetricLabel"] {
    color: #1FB2DE !important;
    font-size: 0.85em !important;
    font-weight: 600 !important;
}

/* ── Cuadros info / warning / success / error ────────────────────────────── */
[data-testid="stAlert"][data-baseweb="notification"] {
    border-radius: 10px !important;
    border-left-width: 5px !important;
}
div[data-testid="stAlert"] > div[role="alert"] {
    border-radius: 10px;
}

/* Info → azul Politécnico */
div[data-baseweb="notification"][kind="info"],
div[class*="stInfo"] {
    background-color: #E8F8FD !important;
    border-left: 5px solid #1FB2DE !important;
    color: #0F385A !important;
}

/* Success → verde */
div[data-baseweb="notification"][kind="positive"] {
    background-color: #EAFAF1 !important;
    border-left: 5px solid #27AE60 !important;
}

/* Warning → dorado Politécnico */
div[data-baseweb="notification"][kind="warning"] {
    background-color: #FFFBEA !important;
    border-left: 5px solid #FBAF17 !important;
    color: #5C3D00 !important;
}

/* Error → magenta Politécnico */
div[data-baseweb="notification"][kind="negative"] {
    background-color: #FEE5F2 !important;
    border-left: 5px solid #EC0677 !important;
    color: #5A0030 !important;
}

/* ── Tabs ────────────────────────────────────────────────────────────────── */
[data-testid="stTabs"] [role="tablist"] {
    border-bottom: 2px solid #1FB2DE;
    gap: 4px;
}
[data-testid="stTabs"] [role="tab"] {
    background: #EAF9FD;
    border-radius: 8px 8px 0 0;
    color: #0F385A;
    font-weight: 500;
    padding: 8px 18px;
    border: 1px solid #A8E6F5;
    border-bottom: none;
    transition: background 0.2s;
}
[data-testid="stTabs"] [role="tab"]:hover {
    background: #C5EEF8;
}
[data-testid="stTabs"] [role="tab"][aria-selected="true"] {
    background: #1FB2DE !important;
    color: #FFFFFF !important;
    border-color: #1FB2DE;
    font-weight: 700 !important;
}

/* ── Botones ─────────────────────────────────────────────────────────────── */
.stButton > button, .stDownloadButton > button {
    background: linear-gradient(135deg, #1FB2DE, #0F385A) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 8px 22px !important;
    font-weight: 600 !important;
    box-shadow: 0 3px 8px rgba(15,56,90,0.22) !important;
    transition: transform 0.15s, box-shadow 0.15s !important;
}
.stButton > button:hover, .stDownloadButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 5px 14px rgba(15,56,90,0.32) !important;
    background: linear-gradient(135deg, #FBAF17, #D48F00) !important;
}

/* ── Expanders ───────────────────────────────────────────────────────────── */
details {
    border: 1px solid #A8E6F5 !important;
    border-radius: 8px !important;
    margin-bottom: 6px !important;
}
details summary {
    background: linear-gradient(90deg, #EAF9FD, #F5FEFF) !important;
    color: #0F385A !important;
    font-weight: 500;
    border-radius: 8px;
    padding: 8px 14px;
}
details[open] summary {
    border-bottom: 2px solid #1FB2DE;
    border-radius: 8px 8px 0 0;
}

/* ── Selectbox / Multiselect ─────────────────────────────────────────────── */
[data-testid="stMultiSelect"] [data-baseweb="tag"] {
    background: #1FB2DE !important;
    color: white !important;
    border-radius: 5px;
}

/* ── Tabla dataframe ─────────────────────────────────────────────────────── */
[data-testid="stDataFrame"] {
    border: 1px solid #A8E6F5 !important;
    border-radius: 8px !important;
    overflow: hidden;
}

/* ── Divisor horizontal ─────────────────────────────────────────────────── */
hr {
    border: none;
    border-top: 2px solid #D0F0FA;
    margin: 20px 0;
}

/* ── Caption / pequeño texto ─────────────────────────────────────────────── */
[data-testid="stCaptionContainer"] p,
small, .caption {
    color: #4A7A90 !important;
}

/* ── Spinner ─────────────────────────────────────────────────────────────── */
[data-testid="stSpinner"] > div {
    border-top-color: #1FB2DE !important;
}

/* ── Header institucional (banner) ──────────────────────────────────────── */
.poligran-header {
    background: linear-gradient(135deg, #0F385A 0%, #1FB2DE 70%, #42F2F2 100%);
    padding: 20px 28px;
    border-radius: 12px;
    margin-bottom: 18px;
    box-shadow: 0 4px 20px rgba(15,56,90,0.25);
}
.poligran-header h2 {
    color: white !important;
    border: none !important;
    padding: 0 !important;
    margin: 0;
    font-size: 1.5em;
    text-shadow: 0 1px 3px rgba(0,0,0,0.2);
}
.poligran-header p {
    color: rgba(255,255,255,0.9) !important;
    margin: 5px 0 0 0;
    font-size: 0.95em;
}
.poligran-badge {
    background: #FBAF17;
    color: #0F385A;
    font-size: 0.72em;
    font-weight: 700;
    padding: 3px 12px;
    border-radius: 20px;
    letter-spacing: 0.5px;
    display: inline-block;
    margin-top: 8px;
}

/* ── Sección con fondo suave ─────────────────────────────────────────────── */
.section-card {
    background: #F5FDFF;
    border: 1px solid #C5EEF8;
    border-radius: 10px;
    padding: 16px 20px;
    margin: 10px 0;
}
.section-card-accent {
    background: #F5FDFF;
    border: 1px solid #C5EEF8;
    border-left: 4px solid #FBAF17;
    border-radius: 10px;
    padding: 16px 20px;
    margin: 10px 0;
}

/* ── Badge de alerta ────────────────────────────────────────────────────── */
.badge-alta   { background:#EC0677; color:white; padding:2px 8px; border-radius:12px; font-size:0.78em; font-weight:700; }
.badge-media  { background:#FBAF17; color:#0F385A; padding:2px 8px; border-radius:12px; font-size:0.78em; font-weight:700; }
.badge-baja   { background:#42F2F2; color:#0F385A; padding:2px 8px; border-radius:12px; font-size:0.78em; font-weight:700; }
</style>
""", unsafe_allow_html=True)

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
        "color": "#42F2F2",
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
        "color": "#1A5276",
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


_TAXONOMIAS_MATRIZ_PATH = "data/raw/Taxonomias_MatrizBD.xlsx"

# ── Dominio de cada subcategoría (clave normalizada sin acentos) ──────────────
_SUBCAT_TO_DOMAIN: Dict[str, str] = {
    'conocimiento':  'Cognitivo',
    'comprension':   'Cognitivo',
    'aplicacion':    'Cognitivo',
    'analisis':      'Cognitivo',
    'sintesis':      'Cognitivo',
    'evaluacion':    'Cognitivo',
    'creacion':      'Cognitivo',
    'imitacion':     'Procedimental',
    'manipulacion':  'Procedimental',
    'precision':     'Procedimental',
    'control':       'Procedimental',
    'percepcion':    'Actitudinal',
    'responder':     'Actitudinal',
    'valorar':       'Actitudinal',
    'organizar':     'Actitudinal',
    'caracterizar':  'Actitudinal',
}

# Orden jerárquico (1=más básico … 15=más complejo) para priorizar al detectar
_SUBCAT_ORDER: Dict[str, int] = {
    'conocimiento': 1,  'comprension': 2,  'aplicacion': 3,
    'analisis':     4,  'sintesis':    5,  'evaluacion': 6,
    'imitacion':    7,  'manipulacion': 8, 'precision':  9, 'control': 10,
    'percepcion':  11,  'responder':   12, 'valorar':   13,
    'organizar':   14,  'caracterizar': 15,
}

# Colores por subcategoría (tonos del dominio)
_SUBCAT_COLORS: Dict[str, str] = {
    'Conocimiento': '#AED6F1', 'Comprension': '#5DADE2',
    'Aplicacion':   '#2E86C1', 'Analisis':    '#1A5276',
    'Sintesis':     '#7D3C98', 'Evaluacion':  '#922B21',
    'Imitacion':    '#ABEBC6', 'Manipulacion': '#58D68D',
    'Precision':    '#1E8449', 'Control':     '#0B5345',
    'Percepcion':   '#B3DCF0', 'Responder':   '#5DADE2',
    'Valorar':      '#2E86C1', 'Organizar':   '#1A5276',
    'Caracterizar': '#0F385A',
}

_DOMAIN_COLORS: Dict[str, str] = {
    'Cognitivo':      '#2E86C1',
    'Procedimental':  '#1E8449',
    'Actitudinal':    '#42F2F2',
    'No identificado': '#BDC3C7',
}

# Mapeo explícito: nombre_subcategoria (normalizado sin acentos) → nivel Bloom
_SUBCAT_TO_BLOOM: Dict[str, str] = {
    'conocimiento':  'Recordar',
    'comprension':   'Comprender',
    'aplicacion':    'Aplicar',
    'analisis':      'Analizar',
    'sintesis':      'Crear',
    'evaluacion':    'Evaluar',
    'creacion':      'Crear',
    # Procedimental → Aplicar (uso práctico de habilidades)
    'imitacion':     'Aplicar',
    'manipulacion':  'Aplicar',
    'precision':     'Aplicar',
    'control':       'Evaluar',
    # Actitudinal → distribuir entre niveles inferiores
    'percepcion':    'Recordar',
    'responder':     'Comprender',
    'valorar':       'Evaluar',
    'organizar':     'Analizar',
    'caracterizar':  'Crear',
}


def _stem_es(word: str) -> str:
    """Extrae el stem aproximado de un verbo español quitando terminaciones comunes."""
    w = word.strip().lower()
    # Longer suffixes first to avoid premature truncation
    for suf in ('ando', 'iendo', 'ados', 'idos', 'ado', 'ido',
                'amos', 'emos', 'imos', 'aron', 'ieron',
                'ará', 'erá', 'irá', 'ara', 'era', 'ira',
                'ar', 'er', 'ir',
                'as', 'es', 'an', 'en',
                'a', 'e', 'o'):
        if w.endswith(suf) and len(w) - len(suf) >= 4:
            return w[:-len(suf)]
    return w


def leer_taxonomias_bloom(uploaded_files=None) -> Dict[str, list]:
    """
    Carga verbos desde data/raw/Taxonomias_MatrizBD.xlsx, hoja 'Verbos'.
    Estructura: id_verbo | verbo | id_subcategoria | nombre_subcategoria |
                id_dominio | nombre_dominio
    Retorna: {nombre_subcategoria_normalizado: [verbos...]}
    """
    import os

    def _norm(s: str) -> str:
        return unicodedata.normalize('NFKD', str(s).strip().lower()).encode('ascii', 'ignore').decode('ascii')

    taxonomias: Dict[str, list] = {}

    if os.path.exists(_TAXONOMIAS_MATRIZ_PATH):
        try:
            df_v = pd.read_excel(_TAXONOMIAS_MATRIZ_PATH, sheet_name='Verbos', engine='openpyxl')
            # Normalize column names for safe access
            df_v.columns = [_norm(c) for c in df_v.columns]

            col_verbo  = next((c for c in df_v.columns if c == 'verbo'), None)
            col_subcat = next((c for c in df_v.columns if 'nombre_subcategoria' in c), None)

            if col_verbo and col_subcat:
                for _, row in df_v.iterrows():
                    subcat = _norm(str(row[col_subcat]))
                    verbo  = _norm(str(row[col_verbo]))
                    if subcat in ('', 'nan') or verbo in ('', 'nan') or len(verbo) < 3:
                        continue
                    taxonomias.setdefault(subcat, []).append(verbo)
        except Exception:
            taxonomias = {}

    return {nivel: list(dict.fromkeys(verbos)) for nivel, verbos in taxonomias.items()}


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
            uploaded_file.seek(0)
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

    # Normalizar Tipo de Saber (tolerante a espacios, guiones, acentos, mayúsculas)
    def _norm_tipo_saber(valor: str) -> str:
        v = unicodedata.normalize('NFKD', str(valor).strip().lower()).encode('ascii', 'ignore').decode('ascii')
        v = re.sub(r'[\s\-_/]+', '', v)   # quitar espacios, guiones, barras
        if v in ('saber', 'conocimiento', 'conceptual', 'teorico', 'conocer'):
            return 'Saber'
        if 'saberhacer' in v or v in ('hacer', 'practica', 'procedimental', 'habilidad', 'proceder'):
            return 'SaberHacer'
        if 'saberser' in v or v in ('ser', 'actitud', 'valor', 'etica', 'actitudinal', 'humano'):
            return 'SaberSer'
        return valor  # mantener original si no se reconoce

    df_consolidado['Tipo de Saber'] = (
        df_consolidado['Tipo de Saber'].astype(str).str.strip()
        .map(_norm_tipo_saber)
    )
    # Descartar filas cuyo Tipo de Saber no sea uno de los tres válidos
    df_consolidado = df_consolidado[
        df_consolidado['Tipo de Saber'].isin({'Saber', 'SaberHacer', 'SaberSer'})
    ]

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

def _split_nucleos(texto: str) -> list:
    """Separa núcleos temáticos. NO divide por coma porque las comas son
    parte de la descripción del núcleo (ej: 'Ciudadanía: relaciones, dinámicas...')."""
    partes = re.split(r'[;\n\|]+', texto)
    # También dividir en ítems numerados tipo "1. Núcleo" o "2) Núcleo"
    resultado = []
    for p in partes:
        sub = re.split(r'(?<!\d)(?=\d+[\.\)]\s+\w)', p)
        resultado.extend(sub)
    return resultado


def analizar_cobertura(df: pd.DataFrame) -> Dict:
    """Analisis de cobertura y densidad tematica."""
    nucleos_list = []
    for _, row in df.iterrows():
        nucleos_raw = str(row.get('Nucleos tematicos', ''))
        if nucleos_raw and nucleos_raw != 'nan':
            nucleos = [
                _limpiar_nucleo(n.strip()) for n in _split_nucleos(nucleos_raw)
                if _es_nucleo_valido(n.strip())
            ]
            nucleos_list.extend(nucleos)

    nucleos_counter = Counter(nucleos_list)

    # Densidad por asignatura
    densidad = df.groupby('Nombre asignatura o modulo')['Nucleos tematicos'].apply(
        lambda x: len(_split_nucleos(' '.join(x.fillna('').astype(str))))
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
            for nucleo in [_limpiar_nucleo(n.strip()) for n in _split_nucleos(nucleos_raw) if _es_nucleo_valido(n.strip())]:
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
    cred_col = next(
        (c for c in grupo.columns if c.lower().replace('é', 'e') in ('creditos', 'credito')),
        None
    )
    if asig_col not in grupo.columns or cred_col is None:
        return 0
    # Un crédito por asignatura única (primer valor no nulo)
    cred = (
        grupo.dropna(subset=[asig_col])
        .groupby(asig_col)[cred_col]
        .first()
    )
    cred_num = pd.to_numeric(cred, errors='coerce').fillna(0)
    return int(cred_num[cred_num > 0].sum())


def _creditos_por_bloque(grupo: pd.DataFrame) -> Dict[str, int]:
    """
    Desglosa créditos únicos por bloque (Institucional, Disciplinar, Electivo).
    Cada subject se cuenta una sola vez (primer valor no nulo de créditos).
    """
    asig_col = 'Nombre asignatura o modulo'
    cred_col = next(
        (c for c in grupo.columns if c.lower().replace('é', 'e') in ('creditos', 'credito')),
        None
    )
    if asig_col not in grupo.columns or cred_col is None:
        return {'Institucional': 0, 'Disciplinar': 0, 'Electivo': 0, 'Total': 0}

    # Una fila por asignatura única (toma la primera fila con nombre)
    asig_df = (
        grupo.dropna(subset=[asig_col])
        .groupby(asig_col, as_index=False)
        .first()
    )
    asig_df = asig_df.copy()
    asig_df[cred_col] = pd.to_numeric(asig_df[cred_col], errors='coerce').fillna(0)

    def _sum_bloque(col_name: str) -> int:
        if col_name not in asig_df.columns:
            return 0
        mask = asig_df[col_name].astype(str).str.strip().str.upper().isin(['X', 'SI', 'SÍ', '1', 'TRUE'])
        return int(asig_df.loc[mask, cred_col].sum())

    inst  = _sum_bloque('B.Institucional')
    disc  = _sum_bloque('B.Disciplinar')
    elec  = _sum_bloque('B.Electivo')
    total = int(asig_df[asig_df[cred_col] > 0][cred_col].sum())
    return {'Institucional': inst, 'Disciplinar': disc, 'Electivo': elec, 'Total': total}


def leer_totales_programa(uploaded_files) -> Dict[str, Dict[str, int]]:
    """
    Lee los totales OFICIALES de créditos desde las filas de resumen declaradas
    al final de cada Excel (ej: 'Total créditos programa', 'Total créditos bloque
    institucional', etc.).

    Estrategia: escanea TODAS las celdas buscando las etiquetas de totales;
    el valor oficial se lee de la columna de Créditos en la misma fila.
    El número de filas varía por programa, por lo que NO se usa posición fija.
    """
    def _norm(s: str) -> str:
        return unicodedata.normalize('NFKD', str(s).strip().lower()).encode('ascii', 'ignore').decode('ascii')

    totales: Dict[str, Dict[str, int]] = {}

    for f in uploaded_files:
        nombre = f.name
        prog = (nombre
                .replace("FormatoRA_", "").replace("_PBOG", "")
                .replace("_VNAL", "").replace("_PMED", "")
                .replace(".xlsx", "").replace(".xls", ""))
        try:
            f.seek(0)
            raw = pd.read_excel(
                f, sheet_name='Paso 5 Estrategias micro',
                header=None, engine='openpyxl'
            )

            # Encontrar columna de Créditos por encabezado (fila 1 = Excel fila 2)
            cred_col_idx = next(
                (i for i, v in enumerate(raw.iloc[1])
                 if pd.notna(v) and 'dito' in _norm(str(v))),
                9  # fallback: columna J (índice 9)
            )

            pt: Dict[str, int] = {}
            nrows, ncols = raw.shape

            for r in range(nrows):
                for c in range(ncols):
                    cell = raw.iloc[r, c]
                    if not pd.notna(cell):
                        continue
                    cn = _norm(str(cell))
                    # Leer el crédito de la misma fila en la columna de Créditos
                    raw_val = (raw.iloc[r, cred_col_idx]
                               if cred_col_idx < ncols else None)
                    try:
                        val = int(float(raw_val)) if pd.notna(raw_val) else 0
                    except (ValueError, TypeError):
                        val = 0

                    if 'total creditos programa' in cn or 'total creditos del programa' in cn:
                        pt['total'] = val
                    elif 'bloque inst' in cn:
                        pt['institucional'] = val
                    elif 'bloque disc' in cn:
                        pt['disciplinar'] = val
                    elif 'bloque elec' in cn:
                        pt['electivo'] = val

            totales[prog] = pt
        except Exception:
            totales[prog] = {}

    return totales


def pagina_inicio(df: pd.DataFrame, totales_oficiales: Optional[Dict] = None):
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
        "Los créditos oficiales se leen directamente desde las filas de totales declaradas "
        "al final de cada Excel ('Total créditos programa', 'Total créditos bloque...'). "
        "La columna **⚠ Dif.** compara el total oficial con la suma de los tres bloques."
    )

    resumen_rows = []
    for prog in df['Programa'].unique():
        g = df[df['Programa'] == prog]

        # Totales oficiales del Excel (footer rows)
        of = (totales_oficiales or {}).get(prog, {})
        cr_total   = of.get('total',         0)
        cr_inst    = of.get('institucional',  0)
        cr_disc    = of.get('disciplinar',    0)
        cr_elec    = of.get('electivo',       0)

        # Si no hay totales oficiales, caer al cálculo propio
        if cr_total == 0:
            bl = _creditos_por_bloque(g)
            cr_total = bl['Total']
            cr_inst  = bl['Institucional']
            cr_disc  = bl['Disciplinar']
            cr_elec  = bl['Electivo']

        suma_bloques = cr_inst + cr_disc + cr_elec
        diferencia   = cr_total - suma_bloques

        resumen_rows.append({
            'Programa':          prog,
            'Registros':         len(g),
            'Asignaturas':       g['Nombre asignatura o modulo'].nunique(),
            'Semestres':         g['Semestre'].nunique(),
            'Cr. Total':         cr_total,
            'Cr. Institucional': cr_inst,
            'Cr. Disciplinar':   cr_disc,
            'Cr. Electivo':      cr_elec,
            'Suma bloques':      suma_bloques,
            '⚠ Dif.':           diferencia,
        })

    resumen = pd.DataFrame(resumen_rows)

    def _color_dif(val):
        if val == 0:
            return 'background-color:#d4edda;color:#155724'
        return 'background-color:#f8d7da;color:#721c24'

    st.dataframe(
        resumen.style.map(_color_dif, subset=['⚠ Dif.']),
        use_container_width=True, hide_index=True
    )
    st.caption(
        "**Cr. Total** = declarado en el Excel (fila 'Total créditos programa'). "
        "**Suma bloques** = Institucional + Disciplinar + Electivo. "
        "**⚠ Dif. = 0** ✅ coinciden | **≠ 0** 🔴 revisar el Excel."
    )


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

    # ── Revisión y depuración de núcleos ─────────────────────────────────────
    todos_nucleos_ord = resultados['nucleos_counter'].most_common()
    if 'nucleos_excluidos' not in st.session_state:
        st.session_state['nucleos_excluidos'] = []

    with st.expander("🔍 Revisar y depurar núcleos detectados", expanded=False):
        st.caption(
            "Revisa los núcleos identificados automáticamente. Si alguno no es un núcleo "
            "temático válido (fragmentos, errores de formato, etc.), exclúyelo del análisis. "
            "Los cambios se aplican inmediatamente a todos los gráficos de esta página."
        )
        df_revision = pd.DataFrame(
            [{'Núcleo': n, 'Menciones': c} for n, c in todos_nucleos_ord]
        )
        st.dataframe(df_revision, use_container_width=True, hide_index=True, height=250)

        opciones = [n for n, _ in todos_nucleos_ord]
        excluidos_sel = st.multiselect(
            "Seleccionar núcleos a excluir:",
            options=opciones,
            default=[x for x in st.session_state['nucleos_excluidos'] if x in opciones],
            placeholder="Escribe para buscar un núcleo…",
            key='ms_nucleos_excluidos'
        )
        st.session_state['nucleos_excluidos'] = excluidos_sel
        if excluidos_sel:
            st.warning(f"**{len(excluidos_sel)}** núcleo(s) excluido(s) del análisis.")
        else:
            st.success("Todos los núcleos detectados están incluidos en el análisis.")

    # Aplicar exclusiones al counter y recalcular métricas derivadas
    excluidos = set(st.session_state.get('nucleos_excluidos', []))
    nucleos_counter = Counter({k: v for k, v in resultados['nucleos_counter'].items()
                               if k not in excluidos})
    nucleos_unicos   = len(nucleos_counter)
    total_menciones  = sum(nucleos_counter.values())
    if nucleos_unicos > 1:
        _frec = np.array(list(nucleos_counter.values()), dtype=float)
        _prob = _frec / _frec.sum()
        _h    = entropy(_prob, base=2)
        diversidad = (_h / np.log2(nucleos_unicos)) * 100
    else:
        diversidad = 0.0
    # Reconstruir matriz filtrada (top 20)
    top_20_fil = [n for n, _ in nucleos_counter.most_common(20)]
    matriz = pd.DataFrame(0, index=df['Programa'].unique(), columns=top_20_fil)
    for _, row in df.iterrows():
        programa = row['Programa']
        nucleos_raw = str(row.get('Nucleos tematicos', ''))
        if nucleos_raw and nucleos_raw != 'nan':
            for nuc in [_limpiar_nucleo(n.strip()) for n in _split_nucleos(nucleos_raw)
                        if _es_nucleo_valido(n.strip())]:
                if nuc in top_20_fil and nuc not in excluidos:
                    matriz.loc[programa, nuc] += 1

    st.markdown("---")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric(
        "Núcleos Únicos", nucleos_unicos,
        help="Número de temas o núcleos temáticos diferentes identificados en todos los programas"
    )
    col2.metric(
        "Total Menciones", f"{total_menciones:,}",
        help="Cuántas veces en total aparecen núcleos temáticos (pueden repetirse entre asignaturas)"
    )
    col3.metric(
        "Promedio por Asignatura", f"{resultados['promedio_densidad']:.1f}",
        help="Promedio de núcleos temáticos declarados por asignatura"
    )
    col4.metric(
        "Diversidad Temática", f"{diversidad:.1f}/100",
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
            color_continuous_scale='Blues',
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
        top_nucleos = nucleos_counter.most_common(20)
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
                     color_continuous_scale='Blues',
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
            nucleos_prog.extend([
                _limpiar_nucleo(n.strip())
                for n in _split_nucleos(nucleos_raw)
                if _es_nucleo_valido(n.strip()) and _limpiar_nucleo(n.strip()) not in excluidos
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

    tab_global, tab_programa = st.tabs([
        "🌍 Vista Global — Todos los Programas",
        "🏫 Análisis por Programa"
    ])

    # ── TAB 1: VISTA GLOBAL ───────────────────────────────────────────────────
    with tab_global:
        st.subheader("Asignaturas que abordan cada tendencia por programa")
        st.caption(
            "Número de asignaturas **únicas** (cada una contada una sola vez) "
            "que tratan cada tendencia, desglosado por programa."
        )
        # Construir tabla: programa × tendencia → # asignaturas únicas
        detalle = resultados['detalle']
        rows_bar = []
        for tid, por_prog in detalle.items():
            nombre_tend = tendencias[tid]['descripcion'] if tid in tendencias else tid
            nombre_tend_corto = nombre_tend[:35] + '…' if len(nombre_tend) > 35 else nombre_tend
            for prog, registros in por_prog.items():
                n_uniq = len({r['asignatura'] for r in registros if r['asignatura'] != 'Sin nombre'})
                if n_uniq > 0:
                    rows_bar.append({'Tendencia': nombre_tend_corto, 'Programa': str(prog), 'Asignaturas': n_uniq})
        if rows_bar:
            df_bar_global = pd.DataFrame(rows_bar)
            # Ordenar tendencias por total descendente
            orden = (
                df_bar_global.groupby('Tendencia')['Asignaturas'].sum()
                .sort_values(ascending=False).index.tolist()
            )
            fig_bar_global = px.bar(
                df_bar_global,
                x='Tendencia', y='Asignaturas', color='Programa',
                barmode='group',
                color_discrete_sequence=['#0F385A', '#1FB2DE', '#42F2F2', '#FBAF17', '#EC0677'],
                labels={'Asignaturas': 'N° Asignaturas únicas'},
                category_orders={'Tendencia': orden}
            )
            fig_bar_global.update_layout(
                height=480,
                xaxis_tickangle=35,
                xaxis=dict(tickfont=dict(size=10)),
                legend=dict(orientation='h', y=1.08),
                yaxis_title='N° Asignaturas únicas'
            )
            st.plotly_chart(fig_bar_global, use_container_width=True)
        else:
            st.info("No se detectaron tendencias en los datos cargados.")

        st.markdown("---")

        col_a, col_b = st.columns(2)
        with col_a:
            st.subheader("Cobertura por Tendencia (% de asignaturas)")
            st.caption("Porcentaje de asignaturas únicas que abordan cada tendencia.")
            cobertura_data = []
            for tid, pct in resultados['cobertura'].items():
                nombre = tendencias[tid]['descripcion'] if tid in tendencias else tid
                n_asigs = resultados.get('asig_counts', {}).get(tid, 0)
                cobertura_data.append({'Tendencia': nombre[:35], 'Cobertura': round(pct, 1), 'Asignaturas': n_asigs})
            df_cob = pd.DataFrame(cobertura_data).sort_values('Cobertura', ascending=True)
            fig = px.bar(df_cob, y='Tendencia', x='Cobertura', orientation='h',
                         color='Cobertura', color_continuous_scale='RdYlGn', range_color=[0, 100],
                         hover_data=['Asignaturas'],
                         labels={'Cobertura': '% Asignaturas'})
            fig.add_vline(x=50, line_dash="dash", line_color="#FBAF17", opacity=0.7)
            fig.update_layout(height=480)
            st.plotly_chart(fig, use_container_width=True)

        with col_b:
            st.subheader("N° de Asignaturas por Tendencia")
            st.caption("Número absoluto de asignaturas que mencionan cada tendencia.")
            menciones_data = []
            for tid in tendencias:
                nombre = tendencias[tid]['descripcion']
                n_asigs = resultados.get('asig_counts', {}).get(tid, 0)
                menciones_data.append({'Tendencia': nombre[:35], 'Asignaturas': n_asigs})
            df_menciones = pd.DataFrame(menciones_data).sort_values('Asignaturas', ascending=True)
            fig = px.bar(df_menciones, y='Tendencia', x='Asignaturas', orientation='h',
                         color='Asignaturas',
                         color_continuous_scale=[[0, '#EAF9FD'], [0.5, '#1FB2DE'], [1, '#0F385A']],
                         labels={'Asignaturas': 'N° Asignaturas únicas'})
            fig.update_layout(height=480)
            st.plotly_chart(fig, use_container_width=True)

        if resultados['ausentes']:
            st.markdown("---")
            st.subheader("⚠️ Brechas Curriculares Detectadas")
            st.warning(
                "Las siguientes tendencias **no fueron detectadas en ninguna asignatura**. "
                "Considere si los programas deberían incorporarlas:"
            )
            for tid in resultados['ausentes']:
                if tid in tendencias:
                    st.markdown(f"- **{tendencias[tid]['descripcion']}**")

        st.markdown("---")
        st.subheader("Detalle por Tendencia (todos los programas)")
        st.caption("Expande cada programa para ver qué asignaturas abordan la tendencia seleccionada.")
        tend_sel = st.selectbox(
            "Seleccionar tendencia:",
            list(tendencias.keys()),
            format_func=lambda x: tendencias[x]['descripcion'],
            key="tend_sel_global"
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
                            campos_asig = []
                            for h in hallazgos:
                                if h.get('asignatura') == asig:
                                    campos_asig.extend(h.get('campos', []))
                            campos_txt = ', '.join(dict.fromkeys(campos_asig)) or 'Texto general'
                            st.markdown(f"- **{asig}** _(detectada en: {campos_txt})_")
            if not tiene_hallazgos:
                st.info("Esta tendencia no fue detectada en ningún programa.")

    # ── TAB 2: POR PROGRAMA ───────────────────────────────────────────────────
    with tab_programa:
        st.subheader("Análisis de Tendencias por Programa")
        st.caption(
            "Selecciona un programa para ver en detalle cuántas asignaturas cubren cada tendencia "
            "y cuáles son las asignaturas que las abordan."
        )

        programas_disp = sorted(df['Programa'].unique().tolist())
        prog_sel = st.selectbox("Seleccionar programa:", programas_disp, key="tend_prog_sel")

        df_prog = df[df['Programa'] == prog_sel]
        asig_col_t = 'Nombre asignatura o modulo'
        total_asigs_prog = df_prog[asig_col_t].nunique()

        # Calcular cobertura específica para este programa
        cob_prog = []
        for tid, tinfo in tendencias.items():
            kws = [unicodedata.normalize('NFKD', k.lower()).encode('ascii', 'ignore').decode('ascii')
                   for k in tinfo['keywords']]
            asigs_con_tend = set()
            for _, row in df_prog.iterrows():
                texto = str(row.get('Texto_Completo', '')).lower()
                texto_n = unicodedata.normalize('NFKD', texto).encode('ascii', 'ignore').decode('ascii')
                asig = str(row.get(asig_col_t, '')).strip()
                if asig and asig not in ('nan', '') and any(k in texto_n for k in kws):
                    asigs_con_tend.add(asig)
            pct = len(asigs_con_tend) / total_asigs_prog * 100 if total_asigs_prog > 0 else 0
            cob_prog.append({
                'Tendencia': tinfo['descripcion'][:40],
                'ID': tid,
                'Asignaturas': len(asigs_con_tend),
                'Cobertura': round(pct, 1),
                'Lista': sorted(asigs_con_tend)
            })

        df_cob_prog = pd.DataFrame(cob_prog).sort_values('Cobertura', ascending=False)

        # Métricas del programa
        n_con_tend = (df_cob_prog['Asignaturas'] > 0).sum()
        col_p1, col_p2, col_p3 = st.columns(3)
        col_p1.metric("Asignaturas del programa", total_asigs_prog)
        col_p2.metric("Tendencias detectadas", f"{n_con_tend}/{len(tendencias)}")
        col_p3.metric("Cobertura promedio", f"{df_cob_prog['Cobertura'].mean():.1f}%")

        st.markdown("---")

        # Gráfico horizontal de cobertura para el programa
        fig_prog = px.bar(
            df_cob_prog.sort_values('Cobertura', ascending=True),
            y='Tendencia', x='Cobertura', orientation='h',
            color='Cobertura',
            color_continuous_scale=[[0, '#EC0677'], [0.3, '#42F2F2'], [0.6, '#1FB2DE'], [1, '#0F385A']],
            range_color=[0, 100],
            hover_data=['Asignaturas'],
            title=f"Cobertura de tendencias en {prog_sel}",
            labels={'Cobertura': '% Asignaturas', 'Tendencia': ''}
        )
        fig_prog.add_vline(x=50, line_dash="dot", line_color="#FBAF17", opacity=0.8,
                           annotation_text="50%", annotation_position="top right")
        fig_prog.update_layout(height=480, showlegend=False)
        st.plotly_chart(fig_prog, use_container_width=True)

        # Detalle: asignaturas por tendencia del programa
        st.markdown("---")
        st.subheader(f"Asignaturas de **{prog_sel}** por Tendencia")
        tend_sel_prog = st.selectbox(
            "Seleccionar tendencia:",
            df_cob_prog['ID'].tolist(),
            format_func=lambda x: tendencias[x]['descripcion'] if x in tendencias else x,
            key="tend_sel_prog"
        )
        row_sel = df_cob_prog[df_cob_prog['ID'] == tend_sel_prog].iloc[0] if not df_cob_prog.empty else None
        if row_sel is not None:
            asigs_lista = row_sel['Lista']
            if asigs_lista:
                st.markdown(
                    f"**{len(asigs_lista)} asignatura(s)** de {prog_sel} abordan "
                    f"**{tendencias[tend_sel_prog]['descripcion']}** ({row_sel['Cobertura']:.1f}%):"
                )
                for a in asigs_lista:
                    st.markdown(f"- {a}")
            else:
                st.info(f"Ninguna asignatura de **{prog_sel}** aborda esta tendencia.")


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
    col_prog_sim, col_top_sim = st.columns([3, 1])
    with col_prog_sim:
        programas_sel = st.multiselect(
            "Seleccionar programas a comparar (2 o más):",
            programas_disponibles,
            default=programas_disponibles,
            help="Elige qué programas incluir en el análisis de similitud"
        )
    with col_top_sim:
        max_asigs_heat = st.number_input(
            "Máx. asignaturas en heatmap:",
            min_value=5, max_value=80, value=40, step=5,
            help="Limita el heatmap a las N asignaturas con mayor similitud promedio"
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
                # Reducir a top-N asignaturas por similitud promedio (excl. diagonal)
                if len(sim_df) > max_asigs_heat:
                    sim_vals_full = sim_df.values.copy()
                    np.fill_diagonal(sim_vals_full, 0)
                    avg_sim = sim_vals_full.mean(axis=1)
                    top_idx = np.argsort(avg_sim)[::-1][:int(max_asigs_heat)]
                    top_names = [sim_df.index[i] for i in sorted(top_idx)]
                    sim_df_heat = sim_df.loc[top_names, top_names]
                    st.caption(
                        f"📊 Mostrando las **{int(max_asigs_heat)} asignaturas** con mayor similitud promedio "
                        f"(de {res_sim['n_asignaturas']} totales). Ajusta el límite en el campo superior."
                    )
                else:
                    sim_df_heat = sim_df

                tab_grupos, tab_pares = st.tabs(["🔍 Grupos Temáticos", "📋 Pares Más Similares"])

                with tab_grupos:
                    st.caption(
                        "Las asignaturas se agrupan automáticamente según similitud de contenido. "
                        "Grupos con alta cohesión comparten vocabulario y temáticas similares."
                    )
                    n_max = min(10, max(2, len(sim_df) // 2))
                    n_clusters = st.slider(
                        "Número de grupos:", min_value=2, max_value=n_max,
                        value=min(5, n_max), key="n_clusters_nlp"
                    )

                    # Clustering aglomerativo sobre matriz de distancias
                    dist_matrix = 1.0 - sim_df.values.clip(0, 1)
                    np.fill_diagonal(dist_matrix, 0.0)
                    clustering = AgglomerativeClustering(
                        n_clusters=n_clusters, metric='precomputed', linkage='average'
                    )
                    labels = clustering.fit_predict(dist_matrix)

                    PALETA = ['#0F385A', '#1FB2DE', '#42F2F2', '#FBAF17', '#EC0677',
                              '#2E7D32', '#6A1B9A', '#E65100', '#00695C', '#AD1457']

                    for cid in range(n_clusters):
                        idx = [i for i, lb in enumerate(labels) if lb == cid]
                        subjects = sorted([sim_df.index[i] for i in idx])
                        if not subjects:
                            continue

                        # Cohesión intra-grupo (similitud promedio)
                        if len(idx) > 1:
                            sub_sim = sim_df.values[np.ix_(idx, idx)].copy()
                            np.fill_diagonal(sub_sim, 0)
                            cohesion = sub_sim.sum() / (len(idx) * (len(idx) - 1))
                        else:
                            cohesion = 1.0

                        color = PALETA[cid % len(PALETA)]
                        label = f"Grupo {cid + 1} &nbsp;·&nbsp; {len(subjects)} asignaturas &nbsp;·&nbsp; Cohesión: {cohesion:.0%}"

                        with st.expander(f"Grupo {cid + 1} — {len(subjects)} asignaturas (cohesión {cohesion:.0%})"):
                            cols = st.columns(2)
                            for k, subj in enumerate(subjects):
                                cols[k % 2].markdown(
                                    f"<div style='padding:4px 8px;margin:2px 0;border-radius:4px;"
                                    f"border-left:3px solid {color};background:#F5FDFF;font-size:0.88em'>"
                                    f"{subj}</div>",
                                    unsafe_allow_html=True
                                )

                    st.caption(
                        "💡 Cohesión alta = asignaturas muy similares entre sí (posible redundancia). "
                        "Ajusta el número de grupos para obtener agrupaciones más o menos detalladas."
                    )

                with tab_pares:
                    sim_vals = sim_df.values.copy()
                    np.fill_diagonal(sim_vals, 0)
                    pares = []
                    for i in range(len(sim_vals)):
                        for j in range(i + 1, len(sim_vals)):
                            pares.append({
                                'Asignatura 1': str(sim_df.index[i]),
                                'Asignatura 2': str(sim_df.columns[j]),
                                'Similitud': round(float(sim_vals[i, j]), 4)
                            })
                    df_pares = (
                        pd.DataFrame(pares)
                        .sort_values('Similitud', ascending=False)
                        .head(40)
                    )
                    def highlight_similar(val):
                        if isinstance(val, float):
                            if val >= 0.8:
                                return 'background-color:#FEE5F2;color:#EC0677;font-weight:bold'
                            if val >= 0.6:
                                return 'background-color:#FFFBEA;color:#8C6000'
                        return ''
                    st.dataframe(
                        df_pares.style.map(highlight_similar, subset=['Similitud']),
                        use_container_width=True,
                        hide_index=True
                    )
                    st.caption("🔴 ≥ 0.80 = posible redundancia · 🟡 0.60–0.79 = revisar diferenciación")

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
    # Garantizar que solo entran los tres tipos válidos
    df = df[df['Tipo de Saber'].isin({'Saber', 'SaberHacer', 'SaberSer'})].copy()

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
        'Saber': '#1FB2DE',
        'SaberHacer': '#0F385A',
        'SaberSer': '#42F2F2'
    }
    REFS_SABER = {
        'Saber':     (25, 45),
        'SaberHacer': (35, 60),
        'SaberSer':  (10, 30)
    }

    # ── Distribución global + Diagnóstico ───────────────────────────────────
    st.markdown("---")
    st.subheader("Distribución Global de Tipo de Saber")

    totales = df['Tipo de Saber'].value_counts()
    total = totales.sum()

    col_donut, col_diag = st.columns([1, 1])
    with col_donut:
        total_tipo = df['Tipo de Saber'].value_counts().reset_index()
        total_tipo.columns = ['Tipo', 'Registros']
        fig_donut = px.pie(
            total_tipo, values='Registros', names='Tipo',
            color='Tipo', color_discrete_map=COLORES_SABER,
            hole=0.45,
            title='Composición global (todos los programas)'
        )
        fig_donut.update_traces(
            texttemplate='%{label}<br><b>%{percent:.1%}</b>',
            textfont_size=12
        )
        fig_donut.update_layout(height=380, showlegend=False,
                                margin=dict(t=50, b=10, l=10, r=10))
        st.plotly_chart(fig_donut, use_container_width=True)

    with col_diag:
        st.markdown("**Diagnóstico de Equilibrio**")
        st.caption("Referencia recomendada para currículos por competencias")
        for tipo, (ref_min, ref_max) in REFS_SABER.items():
            n = int(totales.get(tipo, 0))
            pct = n / total * 100 if total > 0 else 0
            if ref_min <= pct <= ref_max:
                icono, color = "✅", "#27AE60"
            elif pct > ref_max:
                icono, color = "⬆️", "#FBAF17"
            else:
                icono, color = "⬇️", "#EC0677"
            bar_pct = int(pct * 2)
            st.markdown(
                f"<div style='margin:10px 0;padding:10px 14px;border-radius:8px;"
                f"border-left:4px solid {COLORES_SABER[tipo]};background:#F5FDFF'>"
                f"<b style='color:{COLORES_SABER[tipo]}'>{tipo}</b> "
                f"<span style='float:right;color:{color};font-weight:700'>{icono} {pct:.1f}%</span><br>"
                f"<div style='background:#E0F0F8;border-radius:4px;height:8px;margin:6px 0'>"
                f"<div style='background:{COLORES_SABER[tipo]};width:{min(bar_pct,100)}%;height:8px;border-radius:4px'></div></div>"
                f"<small style='color:#666'>Referencia: {ref_min}–{ref_max}% &nbsp;|&nbsp; {n} registros</small>"
                f"</div>",
                unsafe_allow_html=True
            )

    # ── Radar + Scatter de balance por programa ─────────────────────────────
    st.markdown("---")
    st.subheader("Perfil de Competencias por Programa")
    st.caption(
        "**Radar:** compara simultáneamente los 3 tipos de saber entre programas — "
        "el área ideal es amplia y equilibrada. "
        "**Mapa de balance:** posición óptima = SaberHacer alto (eje X) y SaberSer alto (eje Y)."
    )

    pivot = (
        df.groupby(['Programa', 'Tipo de Saber'])
        .size()
        .reset_index(name='Registros')
    )
    total_prog = pivot.groupby('Programa')['Registros'].transform('sum')
    pivot['Porcentaje'] = (pivot['Registros'] / total_prog * 100).round(1)
    pivot_wide = pivot.pivot_table(index='Programa', columns='Tipo de Saber',
                                   values='Porcentaje', fill_value=0).reset_index()

    tab_radar, tab_barra = st.tabs([
        "🕸️ Radar de Competencias",
        "📊 Comparativo Detallado"
    ])

    with tab_radar:
        tipos_disp = [t for t in ['Saber', 'SaberHacer', 'SaberSer'] if t in pivot_wide.columns]
        fig_radar = go.Figure()
        palette_radar = ['#0F385A', '#1FB2DE', '#42F2F2', '#FBAF17', '#EC0677']
        for i, row in pivot_wide.iterrows():
            vals = [row.get(t, 0) for t in tipos_disp]
            vals_closed = vals + [vals[0]]
            cats_closed = tipos_disp + [tipos_disp[0]]
            fig_radar.add_trace(go.Scatterpolar(
                r=vals_closed,
                theta=cats_closed,
                fill='toself',
                fillcolor=f"rgba({int(palette_radar[i % len(palette_radar)].lstrip('#')[0:2], 16)},"
                          f"{int(palette_radar[i % len(palette_radar)].lstrip('#')[2:4], 16)},"
                          f"{int(palette_radar[i % len(palette_radar)].lstrip('#')[4:6], 16)},0.15)",
                line=dict(color=palette_radar[i % len(palette_radar)], width=2),
                name=str(row['Programa'])
            ))
        # Zona de referencia
        ref_vals = [35, 47.5, 20]
        fig_radar.add_trace(go.Scatterpolar(
            r=ref_vals + [ref_vals[0]],
            theta=tipos_disp + [tipos_disp[0]],
            fill='toself',
            fillcolor='rgba(251,175,23,0.07)',
            line=dict(color='#FBAF17', width=1, dash='dot'),
            name='Zona referencia'
        ))
        fig_radar.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 100],
                                       tickfont=dict(size=10), ticksuffix='%')),
            height=450,
            showlegend=True,
            legend=dict(orientation='h', y=-0.15),
            title="Radar de tipos de saber por programa (zona dorada = rango ideal)"
        )
        st.plotly_chart(fig_radar, use_container_width=True)
        st.caption("La zona dorada punteada representa el rango de referencia ideal.")

    with tab_barra:
        fig_bar = px.bar(
            pivot.sort_values('Tipo de Saber'),
            x='Porcentaje', y='Programa', color='Tipo de Saber',
            barmode='group', orientation='h',
            color_discrete_map=COLORES_SABER,
            text='Porcentaje',
            title='Comparativo detallado por programa y tipo de saber',
            labels={'Porcentaje': '%', 'Tipo de Saber': 'Tipo'}
        )
        fig_bar.update_traces(texttemplate='%{text:.0f}%', textposition='outside')
        for tipo, (ref_min, ref_max) in REFS_SABER.items():
            fig_bar.add_vline(x=ref_min, line_dash='dot',
                              line_color=COLORES_SABER.get(tipo, 'gray'), opacity=0.4)
        fig_bar.update_layout(height=max(300, len(pivot_wide) * 80),
                              xaxis=dict(range=[0, 100], title='% de registros'),
                              yaxis_title='')
        st.plotly_chart(fig_bar, use_container_width=True)
        st.caption("Las líneas punteadas verticales marcan el límite mínimo de referencia para cada tipo.")

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

    # ── Tabla semáforo por asignatura ───────────────────────────────────────
    tabla_wide = pivot_asig.pivot_table(
        index='Nombre asignatura o modulo',
        columns='Tipo de Saber',
        values='Porcentaje',
        fill_value=0
    ).round(1).reset_index()
    tabla_wide.columns.name = None

    # Asegurar que existen las columnas aunque no haya datos
    for col in ['Saber', 'SaberHacer', 'SaberSer']:
        if col not in tabla_wide.columns:
            tabla_wide[col] = 0.0

    # Ordenar igual que antes (por SaberHacer desc)
    tabla_wide = tabla_wide.set_index('Nombre asignatura o modulo').loc[
        [a for a in orden_completo if a in tabla_wide['Nombre asignatura o modulo'].values]
    ].reset_index()

    st.caption("Distribución porcentual de cada tipo de saber por asignatura, ordenadas de mayor a menor SaberHacer.")

    cols_mostrar = ['Nombre asignatura o modulo', 'Saber', 'SaberHacer', 'SaberSer']
    tabla_display = tabla_wide[[c for c in cols_mostrar if c in tabla_wide.columns]].rename(
        columns={'Nombre asignatura o modulo': 'Asignatura'}
    )
    st.dataframe(
        tabla_display.style.format(
            {c: '{:.1f}%' for c in ['Saber', 'SaberHacer', 'SaberSer'] if c in tabla_display.columns}
        ),
        use_container_width=True,
        hide_index=True,
        height=min(600, len(tabla_display) * 35 + 60)
    )


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
            nucleos_list.extend([_limpiar_nucleo(n.strip()) for n in _split_nucleos(raw) if _es_nucleo_valido(n.strip())])
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


def pagina_bloom_integracion(df: pd.DataFrame, taxonomias_externas: Dict | None = None):
    """Taxonomía por dominios/subcategorías de la BD y Mapa de Integración."""
    import math as _math

    st.title("🎓 Taxonomías Curriculares e Integración")
    st.markdown("---")
    st.info(
        "Clasifica los Resultados de Aprendizaje según los **dominios** (Cognitivo, Procedimental, Actitudinal) "
        "y **subcategorías** definidas en la base de datos taxonómica (646 verbos). "
        "Explore la distribución, la progresión por semestre y la articulación temática entre asignaturas."
    )

    tab_dom, tab_sub, tab_prog, tab_ra, tab_mapa = st.tabs([
        "🎯 Por Dominio",
        "📊 Por Subcategoría",
        "📈 Progresión",
        "🔍 Explorar RAs",
        "🕸️ Mapa de Integración",
    ])

    # ── Construcción del lookup de verbos desde la BD taxonómica ─────────────
    # verb_to_tax: {verbo_norm: (dominio, subcategoria_display, orden)}
    verb_to_tax: Dict[str, tuple] = {}
    subcat_display_map: Dict[str, str] = {}   # norm → display name

    if taxonomias_externas:
        for subcat_norm, verbos_bd in taxonomias_externas.items():
            dominio  = _SUBCAT_TO_DOMAIN.get(subcat_norm, 'Cognitivo')
            orden    = _SUBCAT_ORDER.get(subcat_norm, 0)
            # Display name: title-case sin acentos ASCII → conservar original
            subcat_display = subcat_norm.replace('comprension', 'Comprensión')\
                                        .replace('aplicacion',  'Aplicación')\
                                        .replace('analisis',    'Análisis')\
                                        .replace('sintesis',    'Síntesis')\
                                        .replace('evaluacion',  'Evaluación')\
                                        .replace('creacion',    'Creación')\
                                        .replace('imitacion',   'Imitación')\
                                        .replace('manipulacion','Manipulación')\
                                        .replace('precision',   'Precisión')\
                                        .replace('percepcion',  'Percepción')\
                                        .title()
            subcat_display_map[subcat_norm] = subcat_display
            for v in verbos_bd:
                v_n = unicodedata.normalize('NFKD', v).encode('ascii', 'ignore').decode('ascii')
                if v_n not in verb_to_tax or orden > verb_to_tax[v_n][2]:
                    verb_to_tax[v_n] = (dominio, subcat_display, orden)
        st.success(
            f"✅ BD cargada: **{len(verb_to_tax)}** verbos únicos · "
            f"**{len(subcat_display_map)}** subcategorías · "
            f"**3** dominios (Cognitivo / Procedimental / Actitudinal)"
        )
    else:
        st.warning(
            "⚠️ No se encontró **Taxonomias_MatrizBD.xlsx** en `data/raw/`. "
            "La clasificación usará solo los verbos base del diccionario interno."
        )

    def detectar_taxonomia(texto: str):
        """Retorna (dominio, subcategoria) usando la BD taxonómica con stem matching."""
        if not texto or str(texto).strip() in ('nan', ''):
            return ('No identificado', 'No identificado')
        t = unicodedata.normalize('NFKD', str(texto).lower()).encode('ascii', 'ignore').decode('ascii')
        words_t = re.findall(r'\b[a-z]{3,}\b', t)
        text_stems = [(w, _stem_es(w)) for w in words_t]
        best_orden = -1
        best_dom   = 'No identificado'
        best_sub   = 'No identificado'
        for v_n, (dom, sub, orden) in verb_to_tax.items():
            if orden <= best_orden:
                continue
            if re.search(r'\b' + re.escape(v_n) + r'\b', t):
                best_orden, best_dom, best_sub = orden, dom, sub
                continue
            v_stem = _stem_es(v_n)
            if len(v_stem) < 4:
                continue
            for word, word_stem in text_stems:
                if word_stem == v_stem or word.startswith(v_stem) or v_n.startswith(word_stem):
                    best_orden, best_dom, best_sub = orden, dom, sub
                    break
        return (best_dom, best_sub)

    df_tax = df.copy()
    df_tax[['Dominio', 'Subcategoria']] = df_tax['Resultado de aprendizaje'].apply(
        lambda x: pd.Series(detectar_taxonomia(x))
    )

    dominios_todos   = ['Cognitivo', 'Procedimental', 'Actitudinal', 'No identificado']
    programas_todos  = sorted(df_tax['Programa'].unique().tolist())

    # ── Filtros globales (fuera de los tabs) ──────────────────────────────────
    with st.expander("🔧 Filtros", expanded=False):
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            dom_filter = st.multiselect(
                "Dominio:", dominios_todos, default=[], key="tax_dom_filter"
            )
        with col_f2:
            prog_filter = st.multiselect(
                "Programa:", programas_todos, default=[], key="tax_prog_filter"
            )

    df_filt = df_tax.copy()
    if dom_filter:
        df_filt = df_filt[df_filt['Dominio'].isin(dom_filter)]
    if prog_filter:
        df_filt = df_filt[df_filt['Programa'].isin(prog_filter)]

    total_ras = len(df_filt)

    # ─────────────────────────────────────────────────────────────────────────
    # TAB 1 — POR DOMINIO
    # ─────────────────────────────────────────────────────────────────────────
    with tab_dom:
        st.subheader("Distribución por Dominio Taxonómico")
        st.caption(
            "**Cognitivo**: qué sabe el estudiante (conocimiento, comprensión, análisis…). "
            "**Procedimental**: qué sabe hacer (imitación → control). "
            "**Actitudinal**: cómo actúa y valora (percepción → caracterizar)."
        )

        conteo_dom = df_filt['Dominio'].value_counts().reindex(dominios_todos, fill_value=0)

        col_d1, col_d2 = st.columns([1, 1])
        with col_d1:
            fig_dom_pie = go.Figure(go.Pie(
                labels=conteo_dom.index.tolist(),
                values=conteo_dom.values.tolist(),
                marker_colors=[_DOMAIN_COLORS.get(d, '#BDC3C7') for d in conteo_dom.index],
                hole=0.38,
                textinfo='label+percent',
                pull=[0.04 if d == 'No identificado' else 0 for d in conteo_dom.index]
            ))
            fig_dom_pie.update_layout(
                title="% de RAs por dominio",
                height=370, showlegend=False,
                margin=dict(t=50, b=0, l=0, r=0)
            )
            st.plotly_chart(fig_dom_pie, use_container_width=True)

        with col_d2:
            st.markdown("**Resumen de dominios:**")
            for dom in dominios_todos:
                n   = int(conteo_dom.get(dom, 0))
                pct = n / total_ras * 100 if total_ras > 0 else 0
                color = _DOMAIN_COLORS.get(dom, '#BDC3C7')
                st.markdown(
                    f"<div style='margin:8px 0;padding:8px 12px;border-left:4px solid {color};"
                    f"border-radius:4px;background:#f8f9fa'>"
                    f"<b style='color:{color}'>{dom}</b><br>"
                    f"<span style='font-size:1.3em;font-weight:bold'>{n}</span> RAs "
                    f"<span style='color:#666'>({pct:.1f}%)</span>"
                    f"</div>",
                    unsafe_allow_html=True
                )

        # Distribución por programa
        st.markdown("---")
        st.subheader("Distribución por Dominio y Programa")
        prog_dom = (
            df_filt.groupby(['Programa', 'Dominio'])
            .size().reset_index(name='RAs')
        )
        total_prog = prog_dom.groupby('Programa')['RAs'].transform('sum')
        prog_dom['pct'] = prog_dom['RAs'] / total_prog * 100
        fig_bar_dom = px.bar(
            prog_dom, x='Programa', y='pct', color='Dominio',
            color_discrete_map=_DOMAIN_COLORS,
            category_orders={'Dominio': dominios_todos},
            barmode='stack', text_auto='.0f',
            labels={'pct': '% RAs', 'Programa': ''},
            title="Composición por dominio (%) por programa"
        )
        fig_bar_dom.update_layout(height=400, xaxis_tickangle=15, yaxis_title="% de RAs",
                                   legend=dict(orientation='h', y=-0.25))
        st.plotly_chart(fig_bar_dom, use_container_width=True)

    # ─────────────────────────────────────────────────────────────────────────
    # TAB 2 — POR SUBCATEGORÍA
    # ─────────────────────────────────────────────────────────────────────────
    with tab_sub:
        st.subheader("Distribución por Subcategoría")
        st.caption("Seleccione uno o más dominios para filtrar las subcategorías mostradas.")

        dom_sub_filter = st.multiselect(
            "Dominio a mostrar:",
            ['Cognitivo', 'Procedimental', 'Actitudinal'],
            default=['Cognitivo', 'Procedimental', 'Actitudinal'],
            key="tax_dom_sub_filter"
        )
        df_sub = df_filt[df_filt['Dominio'].isin(dom_sub_filter)] if dom_sub_filter else df_filt
        df_sub = df_sub[df_sub['Subcategoria'] != 'No identificado']

        conteo_sub = (
            df_sub.groupby(['Dominio', 'Subcategoria'])
            .size().reset_index(name='RAs')
            .sort_values(['Dominio', 'RAs'], ascending=[True, False])
        )

        if conteo_sub.empty:
            st.info("No hay datos para las subcategorías seleccionadas.")
        else:
            fig_sub_bar = px.bar(
                conteo_sub, x='RAs', y='Subcategoria', color='Dominio',
                color_discrete_map=_DOMAIN_COLORS,
                orientation='h', text='RAs',
                labels={'RAs': 'Resultados de Aprendizaje', 'Subcategoria': ''},
                title="RAs clasificados por subcategoría taxonómica"
            )
            fig_sub_bar.update_layout(height=max(350, len(conteo_sub) * 30),
                                       yaxis={'categoryorder': 'total ascending'},
                                       legend=dict(orientation='h', y=-0.15))
            st.plotly_chart(fig_sub_bar, use_container_width=True)

            # Tabla resumen con % por subcategoría
            total_sub = int(conteo_sub['RAs'].sum())
            conteo_sub['%'] = (conteo_sub['RAs'] / total_sub * 100).round(1)
            st.dataframe(
                conteo_sub[['Dominio', 'Subcategoria', 'RAs', '%']]
                .reset_index(drop=True),
                use_container_width=True, hide_index=True
            )

    # ─────────────────────────────────────────────────────────────────────────
    # TAB 3 — PROGRESIÓN POR SEMESTRE
    # ─────────────────────────────────────────────────────────────────────────
    with tab_prog:
        st.subheader("Progresión por Semestre")
        st.caption(
            "Un currículo progresivo muestra dominios procedimentales y actitudinales crecientes "
            "hacia semestres superiores, junto con subcategorías cognitivas más complejas."
        )

        prog_prog_filter = st.multiselect(
            "Programa (vacío = todos):",
            programas_todos, default=[], key="tax_prog_prog_filter"
        )
        vista_prog = st.radio(
            "Agrupar por:", ["Dominio", "Subcategoría"], horizontal=True, key="tax_vista_prog"
        )

        df_p = df_filt[df_filt['Programa'].isin(prog_prog_filter)] if prog_prog_filter else df_filt
        df_p = df_p.copy()
        df_p['Semestre_num'] = pd.to_numeric(df_p['Semestre'], errors='coerce')
        df_p = df_p.dropna(subset=['Semestre_num'])
        df_p['Semestre_num'] = df_p['Semestre_num'].astype(int)

        if df_p.empty:
            st.warning("No hay datos con semestre numérico para mostrar la progresión.")
        else:
            group_col = 'Dominio' if vista_prog == "Dominio" else 'Subcategoria'
            pivot_p = (
                df_p.groupby(['Semestre_num', group_col])
                .size().reset_index(name='count')
            )
            total_g = pivot_p.groupby('Semestre_num')['count'].transform('sum')
            pivot_p['pct'] = pivot_p['count'] / total_g * 100
            sems_ord = sorted(df_p['Semestre_num'].unique())

            color_map_prog = _DOMAIN_COLORS if vista_prog == "Dominio" else {
                row[group_col]: _SUBCAT_COLORS.get(row[group_col], '#BDC3C7')
                for _, row in pivot_p.iterrows()
            }
            cats_presentes = pivot_p[group_col].unique().tolist()

            fig_p = go.Figure()
            for cat in cats_presentes:
                datos_cat = pivot_p[pivot_p[group_col] == cat]
                val_map   = {int(r['Semestre_num']): r['pct'] for _, r in datos_cat.iterrows()}
                y_vals    = [val_map.get(s, 0) for s in sems_ord]
                fig_p.add_trace(go.Scatter(
                    x=sems_ord, y=y_vals, name=cat,
                    mode='lines+markers',
                    line=dict(color=color_map_prog.get(cat, '#BDC3C7'), width=2.5),
                    marker=dict(size=7),
                    stackgroup='one', groupnorm='percent'
                ))
            fig_p.update_layout(
                title=f"Composición por {group_col} (%) por semestre",
                xaxis_title="Semestre", yaxis_title="% de RAs",
                height=450,
                legend=dict(orientation='h', y=-0.3),
                xaxis=dict(tickmode='array', tickvals=sems_ord)
            )
            st.plotly_chart(fig_p, use_container_width=True)

    # ─────────────────────────────────────────────────────────────────────────
    # TAB 4 — EXPLORAR RAs
    # ─────────────────────────────────────────────────────────────────────────
    with tab_ra:
        st.subheader("Explorar Resultados de Aprendizaje")

        col_e1, col_e2, col_e3 = st.columns(3)
        with col_e1:
            dom_e = st.selectbox(
                "Dominio:", ['Todos'] + dominios_todos, key="tax_dom_e"
            )
        with col_e2:
            subcats_disp = sorted(df_tax['Subcategoria'].unique().tolist())
            sub_e = st.selectbox(
                "Subcategoría:", ['Todas'] + subcats_disp, key="tax_sub_e"
            )
        with col_e3:
            prog_e = st.selectbox(
                "Programa:", ['Todos'] + programas_todos, key="tax_prog_e"
            )

        df_e = df_tax.copy()
        if dom_e != 'Todos':
            df_e = df_e[df_e['Dominio'] == dom_e]
        if sub_e != 'Todas':
            df_e = df_e[df_e['Subcategoria'] == sub_e]
        if prog_e != 'Todos':
            df_e = df_e[df_e['Programa'] == prog_e]

        cols_show = ['Programa', 'Semestre', 'Nombre asignatura o modulo',
                     'Resultado de aprendizaje', 'Dominio', 'Subcategoria']
        cols_show = [c for c in cols_show if c in df_e.columns]
        df_e_show = df_e[cols_show].drop_duplicates().sort_values(['Programa', 'Semestre'])
        st.markdown(f"**{len(df_e_show)} RAs** coinciden con los filtros seleccionados.")
        st.dataframe(df_e_show, use_container_width=True, hide_index=True)

    # ─────────────────────────────────────────────────────────────────────────
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
                    unicodedata.normalize('NFKD', _limpiar_nucleo(n.strip()).lower()).encode('ascii', 'ignore').decode('ascii')
                    for n in _split_nucleos(raw_nuc)
                    if _es_nucleo_valido(n.strip())
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
                        color_continuous_scale='Blues',
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
        # ── Banner institucional ───────────────────────────────────────────
        st.markdown("""
        <div class="poligran-header">
            <div>
                <h2>📊 Sistema de Análisis Microcurricular</h2>
                <p>Herramienta para el análisis temático, cognitivo e integrador del plan de estudios</p>
                <span class="poligran-badge">POLITÉCNICO GRANCOLOMBIANO</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # ── Descripción de módulos ─────────────────────────────────────────
        st.markdown("### ¿Qué puedes analizar con esta herramienta?")

        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("""
            <div class="section-card">
                <h3 style="color:#003F8A;margin-top:0">📋 Resumen Ejecutivo</h3>
                <p style="font-size:0.88em;color:#444">Alertas automáticas, fortalezas detectadas y
                recomendaciones priorizadas para comités académicos y procesos de autoevaluación.</p>
            </div>
            <div class="section-card" style="margin-top:10px">
                <h3 style="color:#003F8A;margin-top:0">📊 Tipo de Saber</h3>
                <p style="font-size:0.88em;color:#444">Distribución de <b>Saber</b>, <b>SaberHacer</b>
                y <b>SaberSer</b> por semestre, programa y asignatura. Diagnóstico de balance.</p>
            </div>
            <div class="section-card" style="margin-top:10px">
                <h3 style="color:#003F8A;margin-top:0">🗂️ Cobertura Temática</h3>
                <p style="font-size:0.88em;color:#444">Núcleos temáticos: diversidad,
                densidad y solapamiento entre programas. Matriz de núcleos.</p>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown("""
            <div class="section-card">
                <h3 style="color:#0077C8;margin-top:0">🌍 Tendencias Globales</h3>
                <p style="font-size:0.88em;color:#444">Alineación del currículo con tendencias como
                Sostenibilidad, IA, Transformación Digital, Innovación y Ética.</p>
            </div>
            <div class="section-card" style="margin-top:10px">
                <h3 style="color:#0077C8;margin-top:0">🔍 Minería de Texto</h3>
                <p style="font-size:0.88em;color:#444">Análisis TF-IDF de términos relevantes,
                n-gramas frecuentes y similitud entre asignaturas para detectar redundancias.</p>
            </div>
            <div class="section-card" style="margin-top:10px">
                <h3 style="color:#0077C8;margin-top:0">📄 Explorar Datos</h3>
                <p style="font-size:0.88em;color:#444">Filtrar y explorar todos los registros
                cargados por programa, tipo de saber y semestre. Exportar a CSV.</p>
            </div>
            """, unsafe_allow_html=True)

        with col3:
            st.markdown("""
            <div class="section-card" style="border-left:4px solid #1FB2DE">
                <h3 style="color:#003F8A;margin-top:0">🎓 Bloom & Integración</h3>
                <p style="font-size:0.88em;color:#444"><b>Taxonomía de Bloom:</b> clasificación cognitiva
                de RAs (Recordar→Crear) y progresión por semestre.<br>
                <b>Mapa de integración:</b> red que muestra qué asignaturas comparten núcleos temáticos.</p>
            </div>
            <div class="section-card" style="margin-top:10px;border-left:4px solid #1FB2DE">
                <h3 style="color:#003F8A;margin-top:0">⚙️ Configurar Tendencias</h3>
                <p style="font-size:0.88em;color:#444">Personaliza las tendencias globales a detectar:
                agrega, edita o elimina tendencias con sus palabras clave. Exporta/importa en JSON.</p>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")

        # ── Cómo empezar ──────────────────────────────────────────────────
        col_how, col_struct = st.columns([1, 1])
        with col_how:
            st.markdown("""
            <div class="section-card">
            <h3 style="color:#003F8A;margin-top:0">🚀 Cómo empezar</h3>

            1. Sube uno o más archivos **Excel (.xlsx)** en el panel lateral izquierdo
            2. Los archivos deben contener la hoja **'Paso 5 Estrategias micro'** con encabezados en la **fila 2**
            3. El análisis se ejecuta automáticamente al cargar los archivos
            4. Navega por las secciones usando el menú lateral

            > **Puedes cargar varios programas a la vez** para análisis comparativos.
            </div>
            """, unsafe_allow_html=True)

        with col_struct:
            st.markdown("""
            <div class="section-card">
            <h3 style="color:#003F8A;margin-top:0">📋 Estructura esperada del Excel</h3>
            </div>
            """, unsafe_allow_html=True)
            st.table(pd.DataFrame({
                "Columna": [
                    "Tipo de Saber",
                    "Resultado de aprendizaje",
                    "Nombre asignatura o modulo",
                    "Indicadores de logro",
                    "Nucleos tematicos",
                    "Semestre",
                    "Creditos"
                ],
                "Descripción": [
                    "Saber / SaberHacer / SaberSer",
                    "Texto del resultado de aprendizaje (verbo de acción)",
                    "Nombre de la asignatura o módulo",
                    "Indicadores de evaluación del RA",
                    "Temas separados por coma o punto y coma",
                    "Número de semestre (1, 2, 3…)",
                    "Créditos académicos de la asignatura"
                ]
            }))

        st.stop()

    # Procesar archivos y leer totales oficiales del footer de cada Excel
    df = procesar_archivos(uploaded_files)
    for f in uploaded_files:
        f.seek(0)
    totales_oficiales = leer_totales_programa(uploaded_files)

    if df.empty:
        st.error(
            "No se pudieron cargar datos. Verifica que los archivos tengan "
            "la hoja 'Paso 5 Estrategias micro' con encabezados en la fila 2."
        )
        st.stop()

    # Info sidebar
    st.sidebar.markdown(
        f"""
        <div style='background:rgba(247,148,29,0.15);border:1px solid rgba(247,148,29,0.4);
        border-radius:8px;padding:10px 14px;margin-bottom:8px'>
        <div style='font-size:0.78em;color:rgba(255,255,255,0.7);margin-bottom:4px'>
        ✅ {len(uploaded_files)} archivo(s) cargado(s)</div>
        <div style='font-size:0.82em;color:#fff'>
        <b>{df['Programa'].nunique()}</b> programas &nbsp;|&nbsp;
        <b>{df['Nombre asignatura o modulo'].nunique()}</b> asignaturas<br>
        <b>{len(df):,}</b> registros procesados
        </div></div>
        """,
        unsafe_allow_html=True
    )

    st.sidebar.markdown("---")

    # Navegacion con option_menu
    PAGINAS = {
        "Inicio":               ("house",          "Resumen general y métricas clave del currículo"),
        "Tipo de Saber":        ("bar-chart",       "Saber, SaberHacer y SaberSer por semestre y asignatura"),
        "Cobertura Temática":   ("map",             "Núcleos temáticos: diversidad y densidad por programa"),
        "Tendencias Globales":  ("graph-up-arrow",  "Alineación con IA, Sostenibilidad, Innovación, etc."),
        "Minería de Texto":     ("search",          "Términos clave, similitud y frases frecuentes"),
        "Bloom & Integración":  ("diagram-3",       "Taxonomía de Bloom y mapa de integración temática"),
        "Configurar Tendencias":("sliders",         "Personalizar las tendencias globales a detectar"),
        "Explorar Datos":       ("table",           "Explorar y filtrar los registros cargados"),
    }

    with st.sidebar:
        pagina = option_menu(
            menu_title=None,
            options=list(PAGINAS.keys()),
            icons=[v[0] for v in PAGINAS.values()],
            default_index=0,
            styles={
                "container": {
                    "padding": "4px 0",
                    "background-color": "#0F385A",
                    "border-radius": "0px",
                },
                "icon": {
                    "color": "#42F2F2",
                    "font-size": "15px",
                },
                "nav-link": {
                    "font-size": "13px",
                    "color": "#FFFFFF",
                    "background-color": "transparent",
                    "padding": "8px 14px",
                    "border-radius": "6px",
                    "margin": "2px 4px",
                    "--hover-color": "rgba(31,178,222,0.25)",
                },
                "nav-link-selected": {
                    "background-color": "rgba(31,178,222,0.35)",
                    "border-left": "3px solid #FBAF17",
                    "font-weight": "600",
                    "color": "#FFFFFF",
                },
            }
        )

    st.sidebar.caption(f"_{PAGINAS[pagina][1]}_")
    st.sidebar.markdown("---")
    st.sidebar.markdown(
        """
        <div style='text-align:center;padding:10px 0;opacity:0.7'>
        <div style='font-size:0.7em;color:rgba(255,255,255,0.6)'>
        Politécnico Grancolombiano<br>
        Análisis Microcurricular v2.0
        </div></div>
        """,
        unsafe_allow_html=True
    )

    # Obtener tendencias
    tendencias = obtener_tendencias()

    # Scroll al top al cambiar de página
    st_components.html(
        "<script>window.parent.document.querySelector('.main').scrollTo(0, 0);</script>",
        height=0
    )

    # Renderizar pagina
    if pagina == "Inicio":
        pagina_inicio(df, totales_oficiales)

    elif pagina == "Tipo de Saber":
        pagina_tipo_saber(df)

    elif pagina == "Cobertura Temática":
        with st.spinner("Analizando cobertura temática..."):
            resultados_cob = analizar_cobertura(df)
        pagina_cobertura(df, resultados_cob)

    elif pagina == "Tendencias Globales":
        with st.spinner("Detectando tendencias globales..."):
            resultados_tend = analizar_tendencias(df, tendencias)
        pagina_tendencias(df, tendencias, resultados_tend)

    elif pagina == "Minería de Texto":
        with st.spinner("Ejecutando análisis de texto..."):
            resultados_nlp = analizar_nlp(df)
        pagina_nlp(df, resultados_nlp)

    elif pagina == "Bloom & Integración":
        taxonomias_bloom = leer_taxonomias_bloom(uploaded_files)
        pagina_bloom_integracion(df, taxonomias_bloom)

    elif pagina == "Configurar Tendencias":
        pagina_config_tendencias()

    elif pagina == "Explorar Datos":
        pagina_datos(df)


if __name__ == '__main__':
    main()
