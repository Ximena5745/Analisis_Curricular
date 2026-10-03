"""
Configuración global del proyecto de análisis microcurricular.

Este archivo contiene todas las configuraciones centralizadas para:
- Rutas de archivos y carpetas
- Parámetros de procesamiento
- Configuración de logging
- Integración con LLM
- Exportación de resultados
"""

import os
from pathlib import Path
from typing import Dict, List

# ============================================================================
# RUTAS DEL PROYECTO
# ============================================================================

# Directorio base del proyecto
BASE_DIR = Path(__file__).parent.absolute()

# Directorios de datos
DATA_DIR = BASE_DIR / "data"
INPUT_FOLDER = DATA_DIR / "raw"  # Archivos Excel de entrada
PROCESSED_FOLDER = DATA_DIR / "processed"
OUTPUT_FOLDER = DATA_DIR / "output"

# Directorios de código
SRC_DIR = BASE_DIR / "src"
DASHBOARD_DIR = BASE_DIR / "dashboard"
TEMPLATES_DIR = BASE_DIR / "templates"
TESTS_DIR = BASE_DIR / "tests"
DOCS_DIR = BASE_DIR / "docs"

# Archivo de base de datos (opcional)
DB_PATH = DATA_DIR / "microcurricular.db"

# Crear directorios si no existen
for directory in [INPUT_FOLDER, PROCESSED_FOLDER, OUTPUT_FOLDER]:
    directory.mkdir(parents=True, exist_ok=True)

# ============================================================================
# ESTRUCTURA DE ARCHIVOS EXCEL
# ============================================================================

# Nombres de las hojas en los archivos Excel
EXCEL_SHEETS = {
    'PERFIL_EGRESO': 'Paso1 Analisis perfil egreso',
    'COMPETENCIAS': 'Paso 2 Redacción competen',
    'RESULTADOS_APRENDIZAJE': 'Paso 3 Redacción RA',
    'ESTRATEGIAS_MESO': 'Paso 4 Estrategias mesocurricu',
    'ESTRATEGIAS_MICRO': 'Paso 5 Estrategias micro',
    'TAXONOMIA_COMPETENCIAS': 'Taxonomía para competencias',
    'TAXONOMIA_RA': 'Taxonomias para RA'
}

# Fila de headers de respaldo (0-indexed). El extractor detecta la fila real
# comparando cada fila con EXPECTED_COLUMNS; estos valores solo se usan si la
# detección falla (corrección P2 de la auditoría, 2026-10-02).
HEADER_ROWS = {
    'COMPETENCIAS': 1,  # Header en fila 2 (índice 1)
    'RESULTADOS_APRENDIZAJE': 1,  # Header en fila 2 (índice 1) - la fila 1 tiene instrucciones
    'ESTRATEGIAS_MESO': 0,
    'ESTRATEGIAS_MICRO': 1,  # Header en fila 2 (índice 1)
    'PERFIL_EGRESO': 1  # Header en fila 2 (índice 1); fila 1 tiene placeholders
}

# Columnas esperadas por hoja
EXPECTED_COLUMNS = {
    'COMPETENCIAS': [
        'No.',
        'Verbo competencia',
        'Objeto conceptual',
        'Finalidad',
        'Condición de contexto o referencia',
        'Redacción competencia',
        'Tipo de competencia'
    ],
    'RESULTADOS_APRENDIZAJE': [
        'Competencia por desarrollar',
        'Número de resultado',
        'TipoSaber',
        'SaberAsociado',
        'Taxonomía',
        'Dominio Asociado',
        'Nivel Dominio',
        'Verbo RA',
        'Resultados Aprendizaje'
    ],
    'ESTRATEGIAS_MESO': [
        'Resultado de aprendizaje',
        'Estrategia del programa',
        'Descripción',
        'Indicador de Impacto de la Estrategia',
        'Acciones de retroalimentación para los estudiantes',
        'Instrumentos de medición'
    ],
    'ESTRATEGIAS_MICRO': [
        'Tipo de Saber',
        'Resultado de aprendizaje',
        'Semestre',
        'Nombre asignatura o módulo',
        'Indicadores de logro asignatura o módulo',
        'Tipología',
        'B.Institucional', 'B.Disciplinar', 'B.Electivo',
        'Créditos',
        'Número de horas trabajo directo',
        'Número de horas trabajo independiente',
        'Total de horas',
        'Núcleos temáticos',
        'Actividades de aprendizaje',
        'Actividades de evaluación',
        'Acciones de retroalimentación'
    ],
    'PERFIL_EGRESO': [
        'Programa', 'Modalidad', 'Perfil profesional', 'Perfil ocupacional',
        'Saber', 'SaberHacer', 'SaberSer',
        'Áreas profesionales', 'Tareas profesionales',
        'Poblaciones actuación', 'Valor agregado'
    ]
}

# Sinónimos de encabezado observados en las matrices, por hoja. La clave es el
# nombre normalizado (minúsculas, sin tildes, espacios ni puntuación); el valor,
# el nombre canónico de EXPECTED_COLUMNS. Las variantes que solo difieren en
# mayúsculas, tildes o espacios (p. ej. 'Saberhacer', 'ÁreasProfesionales') no
# necesitan entrada: se resuelven por normalización.
COLUMN_ALIASES = {
    'COMPETENCIAS': {
        'tipocompetencia': 'Tipo de competencia',
        'verbo': 'Verbo competencia',
        'redacciondelacompetenciaadesarrollar': 'Redacción competencia',
    },
    'RESULTADOS_APRENDIZAJE': {
        'tipodesaber': 'TipoSaber',
        'niveldeldominio': 'Nivel Dominio',
        'verbo': 'Verbo RA',
        'redacciondelresultadodeaprendizajedelprograma': 'Resultados Aprendizaje',
    },
    'ESTRATEGIAS_MESO': {
        'instrumentos': 'Instrumentos de medición',
    },
    'ESTRATEGIAS_MICRO': {
        'numerodehorasdetrabajodirecto': 'Número de horas trabajo directo',
        'numerodehorasdetrabajoindependiente': 'Número de horas trabajo independiente',
        'tipologiaasignaturaomodulo': 'Tipología',
        'actividadesevaluativas': 'Actividades de evaluación',
    },
}

# ============================================================================
# DETECCIÓN DE TEMÁTICAS
# ============================================================================

TEMATICAS = {
    'SOSTENIBILIDAD': {
        'keywords': [
            'sostenibilidad', 'sostenible', 'sustentabilidad', 'sustentable',
            'ambiental', 'medio ambiente', 'ecológico', 'ecología',
            'cambio climático', 'responsabilidad ambiental',
            'desarrollo sostenible', 'ods', 'objetivos de desarrollo sostenible',
            'huella de carbono', 'economía circular', 'verde', 'green',
            'consumo responsable', 'energías renovables', 'eficiencia energética',
            'movilidad sostenible', 'agua', 'biodiversidad',
            'innovación social', 'desarrollo comunitario', 'responsabilidad social'
        ],
        'contexto_keywords': [
            'dimensiones económicas, ambientales y sociales',
            'triple línea de base',
            'stakeholders',
            'responsabilidad social'
        ]
    },
    'INTELIGENCIA ARTIFICIAL': {
        'keywords': [
            'inteligencia artificial', 'ia', 'ai', 'machine learning',
            'aprendizaje automático', 'deep learning', 'aprendizaje profundo',
            'redes neuronales', 'algoritmos', 'big data', 'ciencia de datos',
            'data science', 'minería de datos', 'nlp', 'procesamiento de lenguaje natural',
            'visión por computador', 'chatbot', 'gpt', 'llm'
        ],
        'contexto_keywords': [
            'modelos predictivos',
            'automatización',
            'análisis de datos'
        ]
    },
    'RESPONSABILIDAD SOCIAL EMPRESARIAL': {
        'keywords': [
            'responsabilidad social empresarial', 'rse', 'rsc',
            'responsabilidad corporativa', 'ética empresarial',
            'gobierno corporativo', 'stakeholders', 'grupos de interés',
            'valor compartido', 'impacto social', 'filantropía',
            'pacto global', 'triple resultado'
        ],
        'contexto_keywords': []
    },
    'TRANSFORMACIÓN DIGITAL': {
        'keywords': [
            'transformación digital', 'digitalización', 'industria 4.0',
            'internet of things', 'iot', 'blockchain', 'cloud computing',
            'nube', 'big data', 'analítica', 'ciberseguridad',
            'automatización', 'robotización', 'erp', 'crm',
            'e-commerce', 'comercio electrónico', 'fintech'
        ],
        'contexto_keywords': [
            'disrupción digital',
            'tecnologías emergentes'
        ]
    },
    'INNOVACIÓN Y EMPRENDIMIENTO': {
        'keywords': [
            'innovación', 'emprendimiento', 'emprendedor', 'startup',
            'modelo de negocio', 'canvas', 'design thinking', 'lean startup',
            'prototipado', 'mvp', 'producto mínimo viable', 'pitch',
            'escalabilidad', 'disrupción', 'creatividad', 'ideación'
        ],
        'contexto_keywords': [
            'mentalidad emprendedora',
            'oportunidades de negocio'
        ]
    },
    'GLOBALIZACIÓN Y PERSPECTIVA GLOCAL': {
        'keywords': [
            'globalización', 'glocal', 'global', 'internacional',
            'internacionalización', 'comercio internacional',
            'mercados globales', 'multiculturalidad', 'interculturalidad',
            'exportación', 'importación', 'tratados comerciales',
            'competitividad global', 'cadena de valor global'
        ],
        'contexto_keywords': [
            'pensamiento global',
            'acción local'
        ]
    },
    'ÉTICA Y VALORES': {
        'keywords': [
            'ética', 'ético', 'valores', 'moral', 'integridad',
            'transparencia', 'honestidad', 'responsabilidad',
            'código de ética', 'dilema ético', 'deontología',
            'bioética', 'justicia', 'equidad', 'respeto'
        ],
        'contexto_keywords': [
            'toma de decisiones éticas',
            'comportamiento profesional'
        ]
    },
    'LIDERAZGO Y HABILIDADES BLANDAS': {
        'keywords': [
            'liderazgo', 'líder', 'trabajo en equipo', 'comunicación',
            'soft skills', 'habilidades blandas', 'inteligencia emocional',
            'empatía', 'negociación', 'resolución de conflictos',
            'pensamiento crítico', 'creatividad', 'adaptabilidad',
            'resiliencia', 'colaboración', 'asertividad'
        ],
        'contexto_keywords': [
            'gestión de equipos',
            'competencias socioemocionales'
        ]
    },
    'ANÁLISIS DE DATOS': {
        'keywords': [
            'análisis de datos', 'analítica', 'data analytics',
            'estadística', 'visualización de datos', 'dashboard',
            'kpi', 'indicadores', 'métricas', 'business intelligence',
            'bi', 'tablero de control', 'python', 'r', 'sql',
            'excel avanzado', 'power bi', 'tableau'
        ],
        'contexto_keywords': [
            'toma de decisiones basada en datos',
            'data-driven'
        ]
    },
    'GESTIÓN DEL CAMBIO': {
        'keywords': [
            'gestión del cambio', 'cambio organizacional',
            'transformación organizacional', 'resistencia al cambio',
            'cultura organizacional', 'desarrollo organizacional',
            'agilidad', 'adaptación', 'flexibilidad', 'scrum', 'agile'
        ],
        'contexto_keywords': [
            'procesos de cambio',
            'adaptación al entorno'
        ]
    }
}

# ============================================================================
# TAXONOMÍAS Y NIVELES COGNITIVOS
# ============================================================================

# Taxonomía de Bloom - Verbos por nivel
TAXONOMIA_BLOOM = {
    'RECORDAR': {
        'nivel': 1,
        'verbos': ['definir', 'listar', 'recordar', 'identificar', 'nombrar',
                   'reconocer', 'reproducir', 'seleccionar', 'enumerar']
    },
    'COMPRENDER': {
        'nivel': 2,
        'verbos': ['explicar', 'describir', 'interpretar', 'resumir', 'clasificar',
                   'comparar', 'ejemplificar', 'parafrasear', 'ilustrar']
    },
    'APLICAR': {
        'nivel': 3,
        'verbos': ['aplicar', 'ejecutar', 'implementar', 'usar', 'utilizar',
                   'demostrar', 'resolver', 'calcular', 'operar']
    },
    'ANALIZAR': {
        'nivel': 4,
        'verbos': ['analizar', 'diferenciar', 'organizar', 'atribuir', 'comparar',
                   'contrastar', 'examinar', 'investigar', 'categorizar']
    },
    'EVALUAR': {
        'nivel': 5,
        'verbos': ['evaluar', 'criticar', 'juzgar', 'verificar', 'validar',
                   'argumentar', 'defender', 'apoyar', 'justificar']
    },
    'CREAR': {
        'nivel': 6,
        'verbos': ['crear', 'diseñar', 'construir', 'planificar', 'producir',
                   'generar', 'desarrollar', 'formular', 'proponer']
    }
}

# Tipos de saber
TIPOS_SABER = ['Saber', 'SaberHacer', 'SaberSer']

# ============================================================================
# INDICADORES Y MÉTRICAS
# ============================================================================

# Pesos para el cálculo del score de calidad (deben sumar 1.0).
# Auditoría Etapa 3 (2026-10-02):
#  - E3-1: se eliminó 'calidad_redaccion' (10 %), constante de 80 sin evaluación.
#  - E3-7: completitud y cobertura de competencias valen 100 % en los 50
#    programas (el formato de la matriz las garantiza); se reportan como
#    condiciones verificadas (CONDICIONES_VERIFICADAS) y no entran al puntaje.
# Los tres componentes que discriminan conservan sus pesos declarados
# (20/15/15) reescalados a 100 %.
QUALITY_WEIGHTS = {
    'complejidad_cognitiva': 20 / 50,
    'balance_tipo_saber': 15 / 50,
    'diversidad_metodologica': 15 / 50,
}
CONDICIONES_VERIFICADAS = ['completitud', 'cobertura_competencias']

# Progresión de niveles por taxonomía y dominio, de menor a mayor exigencia.
# Cada nivel se traduce a una escala común 1-6 según su posición dentro de su
# propio dominio: nivel = 1 + (posición - 1) × 5 / (n.º de niveles - 1).
# Bloom clásico usa los mismos seis niveles en los tres dominios
# (auditoría E3-2, aprobada 2026-10-02).
PROGRESIONES_TAXONOMICAS = {
    ('bloom', None): ['conocimiento', 'comprension', 'aplicacion', 'analisis', 'sintesis', 'evaluacion'],
    ('bak', 'cognitivo'): ['conocimiento', 'comprension', 'aplicacion', 'analisis', 'sintesis', 'evaluacion'],
    ('bak', 'procedimental'): ['imitacion', 'manipulacion', 'precision', 'control'],
    ('bak', 'actitudinal'): ['percepcion', 'responder', 'valorar', 'organizar', 'caracterizar'],
}

# Columnas clave por paso para la completitud (auditoría E3-3)
COLUMNAS_COMPLETITUD = {
    'competencias': ['Verbo competencia', 'Objeto conceptual', 'Finalidad',
                     'Condición de contexto o referencia', 'Redacción competencia', 'Tipo de competencia'],
    'ra': ['Competencia por desarrollar', 'TipoSaber', 'SaberAsociado', 'Taxonomía',
           'Dominio Asociado', 'Nivel Dominio', 'Verbo RA', 'Resultados Aprendizaje'],
    'estrategias_meso': ['Estrategia del programa', 'Descripción', 'Indicador de Impacto de la Estrategia',
                         'Acciones de retroalimentación para los estudiantes', 'Instrumentos de medición'],
    'estrategias_micro': ['Semestre', 'Nombre asignatura o módulo', 'Indicadores de logro asignatura o módulo',
                          'Créditos', 'Núcleos temáticos', 'Actividades de aprendizaje', 'Actividades de evaluación'],
}

# Umbrales para clasificación de complejidad cognitiva
COMPLEJIDAD_THRESHOLDS = {
    'BASICO': (1, 2),  # Recordar, Comprender
    'INTERMEDIO': (3, 4),  # Aplicar, Analizar
    'AVANZADO': (5, 6)  # Evaluar, Crear
}

# Balance ideal de tipos de saber (%)
BALANCE_IDEAL_SABER = {
    'Saber': 33.3,
    'SaberHacer': 33.3,
    'SaberSer': 33.4
}

# ============================================================================
# NÚCLEOS TEMÁTICOS — CONFIGURACIÓN DE FILTRADO
# ============================================================================

NUCLEOS_CONFIG = {
    'MIN_LONGITUD': 4,
    'MAX_LONGITUD': 150,
    'MIN_PALABRAS': 2,
    # Filtros heurísticos de es_nucleo_valido (longitud, nº de palabras,
    # inicio con artículo/preposición, letra final suelta, patrones de
    # encabezado). Desactivados: con la separación por numeración (D7)
    # rechazaban 926 de 6.671 núcleos legítimos (auditoría P5, 2026-10-02).
    'FILTROS_ESTRICTOS': False,
    'CONTAMINATION_IF': 0.15,
    'USE_SPACY': False,
    'SPACY_MODEL': 'es_core_news_sm',

    # ------------------------------------------------------------------
    # INACTIVO — NO ACTIVAR SIN RECALIBRAR PREVIAMENTE
    # ------------------------------------------------------------------
    # 'UMBRAL_SCORE_ACADEMICO' fue definido como umbral para clasificar
    # núcleos en ALTO/BAJO segun calcular_score_academico(). Nunca se
    # implementó: ninguna función del pipeline lo consulta.
    #
    # Se mantiene comentado, y no eliminado, para dejar constancia de la
    # intención de diseño y evitar que se reintroduzca por descuido.
    #
    # Auditoría D22 (2026-10-03) sobre los 6.671 núcleos del corpus actual
    # (segmentación D7; auditoria/scripts/verificar_score_academico.py):
    #   - score medio = 0.197; mediana = 0.16
    #   - el 95,2 % de los núcleos obtiene score < 0.5
    #   => aplicar el umbral 0.5 descartaría casi todo el corpus.
    #      El valor nunca fue calibrado contra datos reales.
    #
    # El término 'practica', que figuraba a la vez en la lista positiva y en
    # la negativa, ya se retiró de ambas (nucleos_cleaner.py).
    #
    # El score NO es neutral a la disciplina: la mediana por programa difiere
    # entre campos amplios CINE-F 2013 (Kruskal-Wallis H = 19.71, gl = 7,
    # p = 0.006, eps2 = 0.41; de 0.12 en Ciencias sociales a 0.22 en
    # Educación). El contraste anterior aplicados/teóricos (p = 0.565) no es
    # reproducible y queda sustituido.
    #
    # Antes de reactivar cualquier uso decisorio del score es necesario:
    #   1. Separar el criterio "vocabulario académico" del criterio
    #      "formato pedagógico", hoy mezclados.
    #   2. Recalibrar el umbral sobre la distribución real del corpus.
    #   3. Validarlo por campo disciplinar hasta eliminar la diferencia
    #      entre campos, o descartarlo.
    #
    # Mientras tanto, el score se calcula y se exporta ÚNICAMENTE como
    # columna informativa para revisión humana (report_generator.py).
    #
    # 'UMBRAL_SCORE_ACADEMICO': 0.5,
}

# ============================================================================
# COBERTURA DEL PERFIL DE EGRESO
# ============================================================================

# Umbral de similitud TF-IDF para clasificar cobertura (fallback)
UMBRAL_COBERTURA = 0.35

# Umbrales diferenciados por campo del perfil de egreso
UMBRALES_POR_CAMPO = {
    'Perfil profesional': 0.28,
    'Perfil ocupacional': 0.28,
    'Saber': 0.35,
    'SaberHacer': 0.35,
    'SaberSer': 0.32,
    'Áreas profesionales': 0.38,
    'Tareas profesionales': 0.38,
    'Poblaciones actuación': 0.32,
    'Valor agregado': 0.30,
}

# Columnas del perfil de egreso que se analizan (todos los campos del perfil)
COLUMNAS_PERFIL = [
    'Perfil profesional', 'Perfil ocupacional',
    'Saber', 'SaberHacer', 'SaberSer',
    'Áreas profesionales', 'Tareas profesionales',
    'Poblaciones actuación', 'Valor agregado'
]

# Grupos para reportar la cobertura del perfil (auditoría Etapa 4, opción 1,
# 2026-10-02). Cada celda se evalúa con el umbral de su campo; los grupos solo
# agregan los resultados.
GRUPOS_PERFIL = {
    'Perfil profesional': 'Perfil',
    'Perfil ocupacional': 'Perfil',
    'Saber': 'Saberes',
    'SaberHacer': 'Saberes',
    'SaberSer': 'Saberes',
    'Áreas profesionales': 'Campo de actuación',
    'Tareas profesionales': 'Campo de actuación',
    'Poblaciones actuación': 'Campo de actuación',
    'Valor agregado': 'Valor agregado',
}

# ============================================================================
# CONFIGURACIÓN DE PROCESAMIENTO
# ============================================================================

CONFIG = {
    # Rutas
    'INPUT_FOLDER': str(INPUT_FOLDER),
    'OUTPUT_FOLDER': str(OUTPUT_FOLDER),
    'PROCESSED_FOLDER': str(PROCESSED_FOLDER),
    'DB_PATH': str(DB_PATH),

    # Logging
    'LOG_LEVEL': 'INFO',  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    'LOG_FILE': str(BASE_DIR / 'logs' / 'analisis_microcurricular.log'),

    # Procesamiento paralelo
    'PARALLEL_PROCESSING': True,
    'MAX_WORKERS': 4,  # Número de procesos paralelos

    # Exportación
    'EXPORT_FORMATS': ['html', 'pdf', 'excel', 'json'],

    # LLM Integration (opcional)
    'LLM_ENABLED': False,
    'LLM_PROVIDER': 'anthropic',  # 'anthropic' o 'openai'
    'LLM_API_KEY': os.getenv('ANTHROPIC_API_KEY') or os.getenv('OPENAI_API_KEY'),
    'LLM_MODEL': 'claude-3-5-sonnet-20241022',  # o 'gpt-4-turbo'
    'LLM_MAX_TOKENS': 4096,

    # Cache
    'ENABLE_CACHE': True,
    'CACHE_DIR': str(DATA_DIR / 'cache'),

    # Validación
    'MIN_COMPETENCIAS': 3,  # Mínimo de competencias esperadas por programa
    'MIN_RA_POR_COMPETENCIA': 2,  # Mínimo de RA por competencia
    'MIN_COMPLETITUD': 70.0,  # % mínimo de completitud para aprobar validación

    # Dashboard
    'DASHBOARD_PORT': 8501,
    'DASHBOARD_THEME': 'light',  # 'light' o 'dark'

    # Reportes
    'REPORTE_LOGO_PATH': str(BASE_DIR / 'assets' / 'logo_institucion.png'),
    'REPORTE_FOOTER': 'Generado automáticamente por Sistema de Análisis Microcurricular',
}

# ============================================================================
# MENSAJES Y TEXTOS
# ============================================================================

MESSAGES = {
    'BIENVENIDA': """
    ===============================================================
       SISTEMA DE ANALISIS MICROCURRICULAR
       Analisis automatizado de disenos curriculares
    ===============================================================
    """,
    'ERROR_ARCHIVO_NO_ENCONTRADO': 'El archivo {filename} no fue encontrado.',
    'ERROR_ESTRUCTURA_INVALIDA': 'El archivo {filename} no tiene la estructura esperada.',
    'EXITO_EXTRACCION': 'Datos extraídos exitosamente de {filename}.',
    'PROCESANDO_PROGRAMA': 'Procesando programa: {programa}...',
    'ANALISIS_COMPLETO': 'Análisis completado. Resultados guardados en {output_path}.'
}

# ============================================================================
# CONFIGURACIÓN DE GRÁFICOS
# ============================================================================

PLOT_CONFIG = {
    'color_palette': ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
                      '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf'],
    'figure_size': (12, 6),
    'font_size': 12,
    'title_font_size': 16,
    'dpi': 300
}

# ============================================================================
# FUNCIONES AUXILIARES
# ============================================================================

def get_config(key: str, default=None):
    """Obtiene un valor de configuración."""
    return CONFIG.get(key, default)

def update_config(updates: Dict):
    """Actualiza la configuración con nuevos valores."""
    CONFIG.update(updates)

def get_tematicas_list() -> List[str]:
    """Retorna lista de nombres de temáticas."""
    return list(TEMATICAS.keys())

def get_keywords_for_tematica(tematica: str) -> List[str]:
    """Retorna keywords de una temática específica."""
    return TEMATICAS.get(tematica, {}).get('keywords', [])

# ============================================================================
# VALIDACIÓN DE CONFIGURACIÓN
# ============================================================================

def validate_config():
    """Valida que la configuración sea correcta."""
    errors = []

    # Validar que los pesos sumen 1.0
    total_weight = sum(QUALITY_WEIGHTS.values())
    if abs(total_weight - 1.0) > 0.01:
        errors.append(f"Los pesos de QUALITY_WEIGHTS deben sumar 1.0 (actual: {total_weight})")

    # Validar que existan los directorios
    required_dirs = [INPUT_FOLDER, OUTPUT_FOLDER, PROCESSED_FOLDER]
    for dir_path in required_dirs:
        if not dir_path.exists():
            errors.append(f"Directorio no encontrado: {dir_path}")

    if errors:
        raise ValueError("Errores en configuración:\n" + "\n".join(errors))

    return True

# Ejecutar validación al importar
try:
    validate_config()
except ValueError as e:
    print(f"ADVERTENCIA: {e}")

if __name__ == '__main__':
    print("Configuración del proyecto:")
    print(f"BASE_DIR: {BASE_DIR}")
    print(f"INPUT_FOLDER: {INPUT_FOLDER}")
    print(f"OUTPUT_FOLDER: {OUTPUT_FOLDER}")
    print(f"\nTemáticas configuradas: {len(TEMATICAS)}")
    for tematica in TEMATICAS.keys():
        print(f"  - {tematica}")
