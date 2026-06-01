# Documentación Oficial del Proyecto  
## Sistema de Análisis Microcurricular

**Versión:** 1.0.0  
**Fecha:** Mayo 2026  
**Institución:** Coordinación Académica  

---

## Tabla de Contenidos

1. [Objetivos del Proyecto](#1-objetivos-del-proyecto)
2. [Fuentes de Datos](#2-fuentes-de-datos)
3. [Arquitectura del Sistema](#3-arquitectura-del-sistema)
4. [Módulos Principales](#4-módulos-principales)
5. [Dashboard Interactivo](#5-dashboard-interactivo)
6. [Modelos de ML y Técnicas Analíticas](#6-modelos-de-ml-y-técnicas-analíticas)
7. [Visualizaciones](#7-visualizaciones)
8. [Tests](#8-tests)
9. [Métricas e Indicadores](#9-métricas-e-indicadores)
10. [Tecnologías Utilizadas](#10-tecnologías-utilizadas)
11. [Casos de Uso](#11-casos-de-uso)
12. [Instalación y Uso](#12-instalación-y-uso)
13. [Estructura del Proyecto](#13-estructura-del-proyecto)
14. [API de los Módulos](#14-api-de-los-módulos)
15. [Licencia](#15-licencia)

---

## 1. Objetivos del Proyecto

### Objetivo General

Desarrollar un sistema automatizado de análisis curricular que permita consolidar, analizar y visualizar información de 50+ programas académicos a partir de archivos Excel microcurriculares, detectar temáticas emergentes, calcular indicadores de calidad curricular y generar reportes profesionales.

### Objetivos Específicos

| # | Objetivo | Módulo Asociado |
|---|----------|-----------------|
| 1 | Extraer y normalizar datos desde archivos Excel con estructura heterogénea | `extractor.py` |
| 2 | Calcular indicadores cuantitativos de calidad curricular (score 0-100) | `analyzer.py` |
| 3 | Detectar presencia de 10 temáticas emergentes en textos curriculares | `thematic_detector.py` |
| 4 | Validar estructura y redacción de competencias y RA | `validator.py` |
| 5 | Generar reportes en HTML, JSON y Excel | `report_generator.py` |
| 6 | Proveer dashboard interactivo para exploración visual | `dashboard/app.py` |
| 7 | Realizar minería de texto (TF-IDF, coseno, clustering, entropía) | `dashboard_tematico.py` |

### Beneficios Esperados

- Reducción del tiempo de análisis curricular de **días a minutos** (~95% de automatización)
- Análisis estandarizado y consistente entre todos los programas
- Identificación objetiva de brechas curriculares
- Datos para toma de decisiones académicas informadas
- Evidencia para procesos de acreditación institucional

---

## 2. Fuentes de Datos

### 2.1 Archivos de Entrada

Los datos provienen de archivos Excel (`.xlsx`) con formato institucional. Cada archivo representa un programa académico y contiene múltiples hojas con la siguiente estructura:

| Hoja | Nombre en Excel | Propósito |
|------|----------------|-----------|
| Perfil de Egreso | `Paso1 Analisis perfil egreso` | Información general del programa |
| Competencias | `Paso 2 Redacción competen` | Competencias del programa |
| Resultados de Aprendizaje | `Paso 3 Redacción RA` | RA por competencia |
| Estrategias Meso | `Paso 4 Estrategias mesocurricu` | Estrategias a nivel de programa |
| Estrategias Micro | `Paso 5 Estrategias micro` | Estrategias por asignatura |
| Taxonomía Competencias | `Taxonomía para competencias` | Tabla auxiliar de taxonomías |
| Taxonomía RA | `Taxonomias para RA` | Tabla auxiliar de taxonomías |

### 2.2 Estructura de Columnas Esperadas

#### Paso 2 — Competencias
| Columna | Tipo | Requerido |
|---------|------|-----------|
| No. | Entero | Sí |
| Verbo competencia | Texto | Sí |
| Objeto conceptual | Texto | Sí |
| Finalidad | Texto | Sí |
| Condición de contexto o referencia | Texto | No |
| Redacción competencia | Texto | Sí |
| Tipo de competencia | Texto | Sí |

#### Paso 3 — Resultados de Aprendizaje
| Columna | Tipo | Requerido |
|---------|------|-----------|
| Competencia por desarrollar | Texto | Sí |
| Número de resultado | Texto | Sí |
| TipoSaber | Texto (Saber/SaberHacer/SaberSer) | Sí |
| SaberAsociado | Texto | No |
| Taxonomía | Texto | No |
| Dominio Asociado | Texto | No |
| Nivel Dominio | Texto | Sí |
| Verbo RA | Texto | Sí |
| Resultados Aprendizaje | Texto | Sí |

#### Paso 5 — Estrategias Micro
| Columna | Tipo | Requerido |
|---------|------|-----------|
| Tipo de Saber | Texto | Sí |
| Estrategias de enseñanza aprendizaje | Texto | Sí |
| Recursos | Texto | No |
| Horas de trabajo autónomo | Número | No |
| Horas de trabajo presencial | Número | No |
| Criterios de evaluación | Texto | No |
| Acciones de retroalimentación | Texto | No |
| Nivel | Texto (Pregrado/Posgrado) | Sí |
| Componente académico | Texto (B. Institucional, etc.) | No |
| Nombre asignatura o módulo | Texto | Sí |
| Créditos | Número | Sí |
| Semestre | Texto/Número | Sí |
| Núcleos temáticos | Texto | No |
| Indicadores de logro | Texto | No |

### 2.3 Nomenclatura de Archivos

Los archivos siguen el patrón: `FormatoRA_NombrePrograma_CODIGO.xlsx`

Donde **CÓDIGO** (4 caracteres) codifica:

| Posición | Significado | Valores |
|----------|-------------|---------|
| 1 | Modalidad | P=Presencial, V=Virtual, H=Híbrido |
| 2-4 | Sede | BOG=Bogotá, MED=Medellín, NAL=Nacional, VAL=Virtual |

Ejemplo: `FormatoRA_AdmonEmpresas_PBOG.xlsx` → Presencial, Bogotá

### 2.4 Archivo de Taxonomías (Opcional)

`data/raw/Taxonomias_MatrizBD.xlsx` — Hoja "Verbos" con estructura:
- `id_verbo`, `verbo`, `id_subcategoria`, `nombre_subcategoria`, `id_dominio`, `nombre_dominio`

Se utiliza para clasificación taxonómica avanzada de verbos (Bloom, dominio cognitivo/procedimental/actitudinal).

---

## 3. Arquitectura del Sistema

### 3.1 Diagrama de Flujo

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  1. Entrada  │ ──▶ │  2. Carga    │ ──▶ │  3. Análisis │ ──▶ │  4. Reportes │ ──▶ │  5. Dashboard│
│  Excel Files │     │  extractor   │     │  analyzer +  │     │  generator   │     │  Streamlit   │
│  data/raw/   │     │  .py         │     │  thematic_   │     │  .py         │     │  app.py      │
│              │     │              │     │  detector    │     │              │     │              │
└──────────────┘     └──────────────┘     └──────────────┘     └──────────────┘     └──────────────┘
                                                    │
                                                    ▼
                                           ┌──────────────┐
                                           │  Validator   │
                                           │  .py         │
                                           └──────────────┘
```

### 3.2 Pipeline de Procesamiento

1. **Validación** (`validate_files.py` / `extractor.validate_structure()`)
   - Verifica existencia de hojas requeridas
   - Detecta headers automáticamente
   - Reporta errores y advertencias

2. **Extracción** (`ExcelExtractor`)
   - Carga archivo Excel con openpyxl
   - Detecta fila de headers por coincidencia
   - Extrae competencias, RA, estrategias meso y micro
   - Normaliza nombres de columnas (tildes, espacios, mayúsculas)

3. **Análisis** (`CurricularAnalyzer`)
   - Calcula balance de tipos de saber
   - Calcula complejidad cognitiva (Taxonomía de Bloom)
   - Calcula cobertura de competencias
   - Calcula diversidad metodológica
   - Calcula completitud de datos
   - Genera score general de calidad

4. **Detección Temática** (`ThematicDetector`)
   - Busca keywords en todos los textos curriculares
   - Calcula frecuencias por temática
   - Genera matriz Programas × Temáticas
   - Normaliza por créditos académicos

5. **Validación de Calidad** (`QualityValidator`)
   - Valida estructura de competencias (verbo + objeto + finalidad + condición)
   - Verifica coherencia verbo-nivel taxonómico
   - Evalúa mensurabilidad de RA

6. **Generación de Reportes** (`ReportGenerator`)
   - Reporte HTML individual por programa
   - Reporte JSON estructurado
   - Matriz Excel Programas × Temáticas
   - Excel consolidado de indicadores

7. **Visualización** (Dashboard)
   - Carga datos procesados
   - Renderiza KPIs, gráficos y tablas
   - Permite filtros interactivos (modalidad, sede, nivel)
   - Comparación lado a lado de programas

### 3.3 Script Principal

`run_analysis.py` orquesta todo el pipeline:
- Busca archivos Excel en `data/raw/`
- Procesa cada archivo secuencialmente
- Genera reportes individuales y consolidados
- Muestra estadísticas finales

---

## 4. Módulos Principales

### 4.1 `src/extractor.py` — ExcelExtractor

**Clase:** `ExcelExtractor`  
**~587 líneas**

Extrae y normaliza datos de archivos Excel microcurriculares.

| Método | Descripción |
|--------|-------------|
| `__init__(file_path)` | Carga el archivo Excel y extrae nombre del programa |
| `extract_competencias()` | Extrae DataFrame de competencias (Paso 2) |
| `extract_resultados_aprendizaje()` | Extrae DataFrame de RA (Paso 3) |
| `extract_estrategias_meso()` | Extrae estrategias mesocurriculares (Paso 4) |
| `extract_estrategias_micro()` | Extrae estrategias microcurriculares (Paso 5) |
| `extract_all()` | Extrae todos los datos en un dict estructurado |
| `validate_structure()` | Valida estructura del archivo (hojas, columnas) |
| `get_summary()` | Resumen legible del contenido extraído |

**Características clave:**
- Detección automática de fila de headers (por coincidencia con columnas esperadas)
- Normalización tolerante de nombres de columnas (tildes, mayúsculas, espacios)
- Extracción del nombre del programa desde el nombre del archivo (regex)
- Manejo robusto de errores (hojas faltantes, columnas ausentes)

### 4.2 `src/analyzer.py` — CurricularAnalyzer

**Clase:** `CurricularAnalyzer`  
**~660 líneas**

Calcula indicadores cuantitativos de calidad curricular.

| Método | Descripción |
|--------|-------------|
| `calcular_balance_tipo_saber()` | Distribución % Saber / SaberHacer / SaberSer |
| `calcular_complejidad_cognitiva()` | Distribución % Básico / Intermedio / Avanzado (Bloom) |
| `_contar_asignaturas_unicas()` | Conteo preciso de asignaturas desde Paso 5 |
| `calcular_cobertura_competencias()` | % competencias con RA asociado |
| `calcular_diversidad_metodologica()` | N° estrategias únicas, % metodologías activas |
| `calcular_completitud()` | % celdas llenas vs totales por sección |
| `calcular_score_calidad()` | Score ponderado 0-100 combinando 6 indicadores |
| `generar_reporte_indicadores()` | Reporte completo con todos los indicadores |
| `generar_reporte_textual()` | Reporte formateado en texto con barras visuales |

**Ponderación del Score de Calidad:**

| Indicador | Peso |
|-----------|------|
| Completitud | 25% |
| Complejidad Cognitiva | 20% |
| Balance Tipos de Saber | 15% |
| Diversidad Metodológica | 15% |
| Cobertura de Competencias | 15% |
| Calidad de Redacción | 10% |

### 4.3 `src/thematic_detector.py` — ThematicDetector

**Clase:** `ThematicDetector`  
**~641 líneas**

Detecta 10 temáticas emergentes en textos curriculares mediante análisis de keywords.

| Método | Descripción |
|--------|-------------|
| `__init__(tematicas_config, context_window)` | Configura temáticas y ventana de contexto |
| `detect_in_text(text, extract_context)` | Detecta temáticas en un texto individual |
| `detect_in_dataframe(df, text_columns)` | Detecta en DataFrame agregando columnas binarias |
| `analyze_programa(programa_data)` | Analiza programa completo (competencias + RA + estrategias) |
| `generate_thematic_matrix(all_programas)` | Matriz Programas × Temáticas (Excel) |
| `get_programs_by_thematic(matriz, tematica)` | Filtra programas por temática |
| `generate_summary_report(matriz)` | Reporte textual resumen de cobertura |

**Temáticas Detectadas:**

| Temática | Keywords Ejemplo | Color |
|----------|-----------------|-------|
| SOSTENIBILIDAD | sostenibilidad, ODS, cambio climático | Verde |
| INTELIGENCIA ARTIFICIAL | machine learning, deep learning, NLP | Azul |
| RESPONSABILIDAD SOCIAL EMPRESARIAL | RSE, ética empresarial, gobierno corporativo | -- |
| TRANSFORMACIÓN DIGITAL | industria 4.0, IoT, ciberseguridad | Púrpura |
| INNOVACIÓN Y EMPRENDIMIENTO | startup, design thinking, lean startup | Rojo |
| GLOBALIZACIÓN Y PERSPECTIVA GLOCAL | globalización, interculturalidad | Turquesa |
| ÉTICA Y VALORES | ética, integridad, deontología | Cyan |
| LIDERAZGO Y HABILIDADES BLANDAS | liderazgo, trabajo en equipo, soft skills | Azul oscuro |
| ANÁLISIS DE DATOS | estadística, BI, KPIs, dashboard | Verde oscuro |
| GESTIÓN DEL CAMBIO | cambio organizacional, agilidad, scrum | Púrpura |

### 4.4 `src/validator.py` — QualityValidator

**Clase:** `QualityValidator`  
**~344 líneas**

Valida estructura, redacción y coherencia curricular.

| Método | Descripción |
|--------|-------------|
| `validate_competencia_structure(competencia)` | Verbo + Objeto + Finalidad + Condición |
| `validate_verbo_taxonomico(verbo, nivel)` | Coherencia entre verbo y nivel Bloom declarado |
| `validate_ra_measurable(ra)` | RA medible y observable (verbos adecuados) |
| `validate_programa_completo(programa_data)` | Validación completa del programa |

### 4.5 `src/report_generator.py` — ReportGenerator

**Clase:** `ReportGenerator`  
**~436 líneas**

Genera reportes en múltiples formatos.

| Método | Descripción |
|--------|-------------|
| `generate_html_report(data, indicadores, path)` | Reporte HTML con CSS embebido |
| `generate_json_report(data, indicadores, tematicas, path)` | Reporte JSON estructurado |
| `generate_excel_matrix(matriz, path)` | Matriz Programas × Temáticas en Excel |
| `generate_consolidated_excel(all_reportes, path)` | Excel consolidado de todos los programas |

---

## 5. Dashboard Interactivo

### 5.1 Dashboard Modular (`dashboard/app.py`)

Dashboard principal con 5 secciones navegables desde la barra lateral:

| Página | Descripción |
|--------|-------------|
| 🏠 Inicio | KPIs principales, resumen ejecutivo, estructura esperada |
| 📊 Programas | Análisis individual por programa con score, balance, temáticas |
| 🏷️ Temáticas | Filtrado por temática, programas que la abordan |
| 📈 Comparativa | Comparación lado a lado (2 programas) + vista general de todos |
| 📋 Estrategias Micro | Análisis detallado de estrategias pedagógicas |

**Características:**
- Filtros por modalidad (Presencial/Virtual/Híbrido), sede y nivel
- Gráficos Plotly interactivos (radar, barras, pie)
- Tabla resumen con semáforo de scores (🟢 > 75, 🟡 50-74, 🔴 < 50)
- Cálculo de similitud coseno entre programas (TF-IDF)
- Comparación de estrategias pedagógicas entre programas

### 5.2 Dashboard Temático Avanzado (`dashboard_tematico.py`)

Dashboard independiente (~2500+ líneas) con análisis más profundo:

| Sección | Descripción |
|---------|-------------|
| Carga de Archivos | Subida y procesamiento de archivos Excel |
| Análisis de Cobertura | Núcleos temáticos, densidad, entropía de Shannon |
| Tendencias Globales | 10 tendencias con keywords configurables |
| Minería de Texto (NLP) | TF-IDF, n-gramas, términos top por programa |
| Similitud entre Asignaturas | Matriz de similitud coseno, par más similar |
| Taxonomía de Bloom | Clasificación de verbos por nivel y dominio |
| Mapas de Calor | Programas × Temáticas, Tendencias × Asignaturas |

**Paleta institucional (Politécnico Grancolombiano):**
- Navy: `#0F385A`
- Azul: `#1FB2DE`
- Cyan: `#42F2F2`
- Dorado: `#FBAF17`
- Magenta: `#EC0677`

---

## 6. Modelos de ML y Técnicas Analíticas

### 6.1 TF-IDF Vectorization (`sklearn.feature_extraction.text.TfidfVectorizer`)

Utilizado en `dashboard_tematico.py` para:

- **Extracción de términos relevantes:** Identifica los 30 términos con mayor peso TF-IDF en todo el corpus curricular
- **Términos top por programa:** Vectorización individual por programa para caracterización
- **N-gramas (2-3):** Frases relevantes de 2-3 palabras
- **Stopwords personalizadas:** Lista de ~60 stopwords en español

```python
vectorizer = TfidfVectorizer(
    max_features=100, min_df=2, max_df=0.8,
    stop_words=list(STOPWORDS_ES), ngram_range=(1, 3)
)
```

### 6.2 Similitud Coseno (`sklearn.metrics.pairwise.cosine_similarity`)

- **Entre programas:** Mide similitud de contenidos curriculares entre pares de programas
- **Entre asignaturas:** Matriz de similitud entre asignaturas dentro de un programa filtrado
- Útil para identificar redundancias curriculares o programas con enfoques compartidos

### 6.3 Clustering (`sklearn.cluster.AgglomerativeClustering`)

- Clustering jerárquico aglomerativo para agrupar programas según su perfil de indicadores
- Permite identificar familias naturales de programas

### 6.4 Entropía de Shannon (`scipy.stats.entropy`)

- **Diversidad temática:** Mide qué tan distribuidos están los núcleos temáticos en un programa
- **Fórmula:** `H = -Σ p(x) · log₂(p(x))`
- **Normalizada:** `diversidad = (H / H_max) × 100`

### 6.5 Count Vectorization (`sklearn.feature_extraction.text.CountVectorizer`)

- Conteo de frecuencias de n-gramas (2-3 palabras) en todo el corpus
- Identifica frases curriculares recurrentes

### 6.6 Detección por Keywords (Reglas)

El `ThematicDetector` utiliza un enfoque basado en reglas (no ML supervisado):
- Diccionario de ~120 keywords organizadas en 10 categorías temáticas
- Búsqueda con expresión regular (`\bkeyword\w*`) para capturar variantes
- Extracción de contexto (±100 caracteres) alrededor de cada keyword
- Normalización de texto (tildes, mayúsculas) antes del matching

### 6.7 Taxonomía de Bloom

Clasificación de verbos en 6 niveles cognitivos:

| Nivel | Verbos Ejemplo |
|-------|---------------|
| 1 — Recordar | definir, listar, identificar, nombrar |
| 2 — Comprender | explicar, describir, interpretar, resumir |
| 3 — Aplicar | aplicar, ejecutar, implementar, demostrar |
| 4 — Analizar | analizar, diferenciar, organizar, comparar |
| 5 — Evaluar | evaluar, criticar, juzgar, verificar |
| 6 — Crear | crear, diseñar, construir, planificar |

Agrupación en 3 niveles de complejidad:
- **Básico:** Niveles 1-2 (Recordar, Comprender)
- **Intermedio:** Niveles 3-4 (Aplicar, Analizar)
- **Avanzado:** Niveles 5-6 (Evaluar, Crear)

### 6.8 Clasificación por Dominio (Cognitivo/Procedimental/Actitudinal)

Desde el archivo `Taxonomias_MatrizBD.xlsx`:
- 15 subcategorías taxonómicas mapeadas a 3 dominios
- Orden jerárquico (1-15) para priorización en detección
- Colores específicos por subcategoría para visualización

| Dominio | Subcategorías |
|---------|--------------|
| Cognitivo | Conocimiento, Comprensión, Aplicación, Análisis, Síntesis, Evaluación, Creación |
| Procedimental | Imitación, Manipulación, Precisión, Control |
| Actitudinal | Percepción, Responder, Valorar, Organizar, Caracterizar |

---

## 7. Visualizaciones

### 7.1 Tipos de Gráficos (Plotly)

| Gráfico | Ubicación | Propósito |
|---------|-----------|-----------|
| Pie / Donut | Página Programas | Balance Tipos de Saber, Complejidad Cognitiva |
| Radar | Página Comparativa | Perfil multidimensional de programas (5 dimensiones) |
| Barras | Página Comparativa | Ranking de scores, créditos, Tipo de Saber por programa, estrategias |
| Tabla con semáforo | Página Comparativa | Score de calidad con colores (verde/amarillo/rojo) |
| Mapa de Calor | Dashboard Temático | Programas × Temáticas |
| Scatter | Dashboard Temático | Correlaciones entre indicadores |
| Box Plot | Dashboard Temático | Distribución de indicadores por facultad/modalidad |
| Word Cloud | Dashboard Temático | Términos TF-IDF más relevantes |
| Matriz de Similitud | Dashboard Temático | Similitud coseno entre asignaturas |

### 7.2 KPIs

| KPI | Fórmula / Fuente |
|-----|-----------------|
| Total Programas | Conteo de archivos procesados exitosamente |
| Score Promedio | Media de `score_calidad` de todos los programas |
| Programas con Sostenibilidad | Conteo con `SOSTENIBILIDAD_presente = True` |
| Complejidad Promedio | Media de `indice_complejidad` |
| % Metodologías Activas | `activas / total_estrategias × 100` |
| Cobertura Temática | `programas_con_tematica / total_programas × 100` |
| Densidad Temática | `núcleos_únicos / total_asignaturas` |
| Diversidad (Entropía) | `Shannon / H_max × 100` |

### 7.3 Reportes Exportables

| Formato | Contenido | Método |
|---------|-----------|--------|
| HTML | Reporte visual individual por programa | `generate_html_report()` |
| JSON | Datos estructurados exportables | `generate_json_report()` |
| Excel | Matriz Programas × Temáticas | `generate_excel_matrix()` |
| Excel | Indicadores consolidados de todos los programas | `generate_consolidated_excel()` |

---

## 8. Tests

### 8.1 Tests Unitarios

Archivo: `tests/test_thematic_detector.py`

| Test | Descripción |
|------|-------------|
| `test_detector_initialization` | Verifica inicialización correcta del detector |
| `test_detect_sostenibilidad` | Detecta "sostenible" y "ambiental" en texto |
| `test_detect_inteligencia_artificial` | Detecta "machine learning" e "inteligencia artificial" |
| `test_no_detection_in_empty_text` | Texto vacío no produce detecciones |
| `test_normalize_text` | Normalización elimina tildes correctamente |
| `test_extract_context` | Extracción de contexto alrededor de keyword |
| `test_multiple_keywords_in_same_text` | Múltiples keywords de una misma temática |
| `test_detect_in_dataframe_basic` | Detección en DataFrame con columna de texto |

**Ejecución:**
```bash
pytest tests/test_thematic_detector.py -v
```

### 8.2 Scripts de Depuración

El proyecto incluye múltiples scripts auxiliares para depuración y verificación:

| Script | Propósito |
|--------|-----------|
| `validate_files.py` | Validación de estructura de todos los archivos Excel |
| `check_syntax.py` | Verificación de sintaxis de código Python |
| `test_generar_excel.py` | Prueba de generación de archivos Excel |
| `test_conteo_asignaturas.py` | Verificación de conteo de asignaturas |
| `test_simple.py`, `test_final.py` | Pruebas integrales del pipeline |
| `test_validacion_corrección.py` | Prueba de validación con correcciones |
| `debug_*.py` | Múltiples scripts de depuración específica |

### 8.3 Pruebas de Integración

El script `run_analysis.py` funciona como prueba de integración ejecutando el pipeline completo:
1. Validación de estructura
2. Extracción de datos
3. Cálculo de indicadores
4. Detección de temáticas
5. Validación de calidad
6. Generación de reportes

---

## 9. Métricas e Indicadores

### 9.1 Score de Calidad (0-100)

Compuesto por 6 indicadores ponderados:

```
Score = Completitud(25%) + Complejidad Cognitiva(20%) + 
        Balance Saber(15%) + Diversidad Metodológica(15%) + 
        Cobertura Competencias(15%) + Calidad Redacción(10%)
```

### 9.2 Balance de Tipos de Saber

Distribución ideal: ~33% cada tipo (Saber, SaberHacer, SaberSer)
- **Desviación estándar:** Mide qué tan lejos está del ideal
- **Balanceado:** `desviación < 10%`

### 9.3 Índice de Complejidad Cognitiva

```
índice = ((nivel_promedio - 1) / 5) × 100
```
- `nivel_promedio` = media de niveles Bloom (1-6) de todos los RA
- Rango: 0 (todo básico) a 100 (todo avanzado)

### 9.4 Cobertura de Competencias

- `% cobertura = competencias_con_RA / total_competencias × 100`
- `promedio_RA_por_competencia = total_RA / competencias_con_RA`

### 9.5 Diversidad Metodológica

- `num_estrategias_unicas`: Conteo de keywords de metodologías distintas
- `% metodologías activas`: Taller, Laboratorio, Caso, Problema, Proyecto, Simulación, Debate

### 9.6 Completitud

```
completitud_total = completitud_competencias(30%) +
                    completitud_RA(40%) +
                    completitud_meso(15%) +
                    completitud_micro(15%)
```

### 9.7 Métricas Temáticas

- **Cobertura:** `% asignaturas que abordan la temática`
- **Densidad:** `núcleos_temáticos_únicos / total_asignaturas`
- **Frecuencia normalizada:** `coincidencias / créditos × 10`
- **Entropía de Shannon:** Diversidad de núcleos temáticos

---

## 10. Tecnologías Utilizadas

### 10.1 Stack Tecnológico

| Categoría | Tecnología | Versión Mínima |
|-----------|-----------|----------------|
| **Lenguaje** | Python | 3.10+ |
| **Framework Web** | Streamlit | 1.30+ |
| **Manipulación de Datos** | pandas | 2.0+ |
| **Cómputo Numérico** | numpy | 1.24+ |
| **Visualización** | Plotly | 5.18+ |
| **ML / NLP** | scikit-learn | 1.3+ |
| **Estadística** | scipy | 1.11+ |
| **Excel** | openpyxl | 3.1+ |
| **Componentes UI** | streamlit-option-menu | 0.3.6 |

### 10.2 Dependencias (requirements.txt)

```
streamlit>=1.30.0
pandas>=2.0.0
numpy>=1.24.0
plotly>=5.18.0
scikit-learn>=1.3.0
scipy>=1.11.0
openpyxl>=3.1.0
streamlit-option-menu>=0.3.6
```

### 10.3 Estructura del Paquete (setup.py)

- **Nombre:** `analisis-microcurricular`
- **Entry point:** `analisis-curricular=src.main:main`
- **Clasificadores:** Development Status :: 4 - Beta, Education
- **Python requerido:** >=3.10

### 10.4 Integración Opcional con LLM

Configurable en `config.py`:

```python
CONFIG['LLM_ENABLED'] = True
CONFIG['LLM_PROVIDER'] = 'anthropic'  # o 'openai'
CONFIG['LLM_MODEL'] = 'claude-3-5-sonnet-20241022'
```

- Análisis semántico avanzado
- Validación de calidad de redacción
- Sugerencias de mejora curricular

---

## 11. Casos de Uso

### 11.1 Coordinador Académico

**Objetivo:** Obtener panorama completo de 50+ programas

**Flujo:**
1. Ejecutar `python run_analysis.py`
2. Abrir dashboard con `streamlit run dashboard/app.py`
3. Revisar KPIs generales en página Inicio
4. Exportar matriz de temáticas (Excel)
5. Presentar a dirección académica

### 11.2 Director de Programa

**Objetivo:** Mejorar un programa específico

**Flujo:**
1. Abrir dashboard
2. Seleccionar programa en página Programas
3. Revisar score de calidad y balance de tipos de saber
4. Identificar áreas de mejora (baja complejidad, desbalance)
5. Comparar con programas similares en página Comparativa

### 11.3 Comité de Acreditación

**Objetivo:** Evidencia para acreditación

**Flujo:**
1. Generar reporte HTML del programa
2. Revisar indicadores vs estándares
3. Adjuntar reportes a carpeta de evidencias
4. Mostrar dashboard interactivo en visita de pares

### 11.4 Vicerrectoría Académica

**Objetivo:** Identificar brechas institucionales

**Flujo:**
1. Revisar matriz de temáticas consolidada
2. Identificar programas sin cobertura de temáticas clave (Sostenibilidad, IA)
3. Planear capacitación docente focalizada
4. Hacer seguimiento trimestral con nuevos procesamientos

### 11.5 Analista Curricular

**Objetivo:** Análisis profundo de un programa

```python
from src.extractor import ExcelExtractor
from src.analyzer import CurricularAnalyzer
from src.thematic_detector import ThematicDetector

extractor = ExcelExtractor('data/raw/FormatoRA_AdmonEmpresas_PBOG.xlsx')
data = extractor.extract_all()

analyzer = CurricularAnalyzer(data)
indicadores = analyzer.generar_reporte_indicadores()

detector = ThematicDetector()
tematicas = detector.analyze_programa(data)

print(f"Score: {indicadores['score_calidad']}/100")
print(f"Temáticas: {tematicas['tematicas_presentes']}")
```

---

## 12. Instalación y Uso

### 12.1 Instalación

```bash
# 1. Crear entorno virtual
python -m venv venv

# 2. Activar (Windows)
venv\Scripts\activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. (Opcional) Instalación completa
pip install -e .
```

### 12.2 Preparación de Datos

```bash
# Colocar archivos Excel en data/raw/
# Validar estructura
python validate_files.py
```

### 12.3 Ejecución de Análisis

```bash
# Análisis completo de todos los programas
python run_analysis.py
```

### 12.4 Dashboard

```bash
# Dashboard modular
streamlit run dashboard/app.py

# Dashboard temático avanzado (alternativo)
streamlit run dashboard_tematico.py
```

### 12.5 Tests

```bash
# Tests unitarios
pytest tests/test_thematic_detector.py -v

# Todos los tests (si se configuran más)
pytest
```

### 12.6 Configuración

Editar `config.py` para personalizar:
- Rutas de archivos (`INPUT_FOLDER`, `OUTPUT_FOLDER`)
- Pesos de indicadores (`QUALITY_WEIGHTS`)
- Temáticas y keywords (`TEMATICAS`)
- Procesamiento paralelo (`PARALLEL_PROCESSING`, `MAX_WORKERS`)
- Integración LLM (`LLM_ENABLED`, `LLM_PROVIDER`)
- Umbrales de validación (`MIN_COMPETENCIAS`, `MIN_COMPLETITUD`)

Editar `config_tendencias.json` para personalizar tendencias del dashboard temático.

---

## 13. Estructura del Proyecto

```
analisis_curricular/
│
├── config.py                        # Configuración global del sistema
├── config_tendencias.json           # Configuración de tendencias (JSON)
├── requirements.txt                 # Dependencias Python
├── setup.py                         # Instalación del paquete
├── LICENSE                          # Licencia MIT
├── README.md                        # Documentación principal
├── RESUMEN_PROYECTO.md              # Resumen ejecutivo
├── INICIO_RAPIDO.md                 # Guía rápida (5 minutos)
│
├── run_analysis.py                  # Script principal de análisis
├── validate_files.py                # Validación de archivos Excel
├── ejemplo_uso.py                   # Ejemplos de uso programático
├── check_syntax.py                  # Verificación de sintaxis
├── analisis_estrategias_micro.py    # Análisis específico de estrategias micro
├── analisis_tematico_avanzado.py    # Análisis temático avanzado
│
├── dashboard_tematico.py            # Dashboard temático avanzado (independiente)
├── dashboard/
│   ├── app.py                       # Dashboard principal Streamlit
│   └── __init__.py
│
├── src/                             # Código fuente
│   ├── __init__.py
│   ├── extractor.py                 # Extracción de datos Excel
│   ├── analyzer.py                  # Cálculo de indicadores
│   ├── thematic_detector.py         # Detección de temáticas
│   ├── validator.py                 # Validación de calidad
│   └── report_generator.py          # Generación de reportes
│
├── data/
│   ├── raw/                         # Archivos Excel de entrada
│   ├── processed/                   # Datos procesados
│   ├── output/                      # Reportes generados
│   │   ├── reportes/                # HTML y JSON por programa
│   │   ├── matrices/                # Matrices Excel
│   │   └── consolidado/             # Indicadores consolidados
│   └── backup/                      # Copias de seguridad
│
├── tests/
│   ├── __init__.py
│   └── test_thematic_detector.py    # Tests del detector de temáticas
│
├── docs/                            # Documentación
│   ├── DOCUMENTACION_OFICIAL.md     # Este documento
│   ├── diccionario_datos.md         # Diccionario de datos
│   ├── README_GENERAL.md            # README general de docs
│   ├── RESUMEN_EJECUTIVO.md         # Resumen ejecutivo
│   ├── architecture/                # Documentación de arquitectura
│   ├── backend/                     # Documentación de backend
│   ├── frontend/                    # Documentación de frontend
│   ├── database/                    # Documentación de base de datos
│   ├── apis/                        # Documentación de APIs
│   ├── devops/                      # Documentación de DevOps
│   ├── security/                    # Documentación de seguridad
│   ├── testing/                     # Documentación de testing
│   ├── analytics/                   # Documentación de analítica
│   ├── ux/                          # Documentación de UX/UI
│   ├── diagrams/                    # Diagramas del sistema
│   ├── dashboards/                  # Documentación de dashboards
│   ├── deployment/                  # Documentación de despliegue
│   └── recommendations/             # Recomendaciones y roadmap
│
├── debug_*.py                       # Scripts de depuración
├── test_*.py                        # Scripts de prueba
└── .streamlit/
    └── config.toml                  # Configuración de Streamlit
```

---

## 14. API de los Módulos

### 14.1 ExcelExtractor

```python
from src.extractor import ExcelExtractor

# Inicialización
extractor = ExcelExtractor('ruta/archivo.xlsx')

# Extracción completa
data = extractor.extract_all()
# Retorna:
# {
#   'metadata': {'programa': str, 'archivo': str, 'ruta': str},
#   'competencias': pd.DataFrame,
#   'resultados_aprendizaje': pd.DataFrame,
#   'estrategias_meso': pd.DataFrame,
#   'estrategias_micro': pd.DataFrame
# }

# Validación
result = extractor.validate_structure()
# Retorna: {'valid': bool, 'errors': List[str], 'warnings': List[str], 'info': Dict}
```

### 14.2 CurricularAnalyzer

```python
from src.analyzer import CurricularAnalyzer

analyzer = CurricularAnalyzer(programa_data)
reporte = analyzer.generar_reporte_indicadores()
# Retorna: {'programa': str, 'score_calidad': float, 'balance_tipo_saber': Dict,
#           'complejidad_cognitiva': Dict, 'cobertura_competencias': Dict,
#           'diversidad_metodologica': Dict, 'completitud': Dict, 'resumen': Dict}
```

### 14.3 ThematicDetector

```python
from src.thematic_detector import ThematicDetector

detector = ThematicDetector()

# Detección en texto
resultado = detector.detect_in_text("Texto curricular...")
# Retorna: {TEMATICA: {'presente': bool, 'num_coincidencias': int, ...}}

# Análisis de programa
analisis = detector.analyze_programa(programa_data)
# Retorna: {'programa': str, 'tematicas_presentes': List[str], 'resumen': Dict, ...}

# Matriz consolidada
matriz = detector.generate_thematic_matrix(lista_analisis)
# Retorna: pd.DataFrame
```

### 14.4 QualityValidator

```python
from src.validator import QualityValidator

validator = QualityValidator()

# Validar competencia
result = validator.validate_competencia_structure("Analizar...")
# Retorna: {'valid': bool, 'issues': List[str], 'suggestions': List[str], ...}

# Validar programa completo
reporte = validator.validate_programa_completo(programa_data)
# Retorna: {'programa': str, 'score': float, 'competencias': Dict, ...}
```

### 14.5 ReportGenerator

```python
from src.report_generator import ReportGenerator

generator = ReportGenerator()

# Reporte HTML
generator.generate_html_report(data, indicadores, 'output/reporte.html')

# Reporte JSON
generator.generate_json_report(data, indicadores, tematicas, 'output/reporte.json')

# Matriz Excel
generator.generate_excel_matrix(matriz, 'output/matriz.xlsx')

# Excel consolidado
generator.generate_consolidated_excel(all_reportes, 'output/consolidado.xlsx')
```

---

## 15. Licencia

MIT License — Ver archivo [LICENSE](../LICENSE) para más detalles.

---

**Documentación generada el:** Mayo 2026  
**Versión del Proyecto:** 1.0.0  
**Última actualización:** 2026-05-31
