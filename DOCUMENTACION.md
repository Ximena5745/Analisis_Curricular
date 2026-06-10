# Sistema de Análisis Microcurricular — Documentación Técnica

**Versión:** 2.0  
**Propósito:** Plataforma de analítica académica para evaluar, comparar y visualizar la calidad de diseños microcurriculares de programas de educación superior.  
**Contexto institucional:** Politécnico Grancolombiano — Dirección de Innovación y Calidad Curricular.

---

## Tabla de Contenidos

1. [Marco del Problema](#1-marco-del-problema)
2. [Arquitectura del Sistema](#2-arquitectura-del-sistema)
3. [Formato de Datos de Entrada](#3-formato-de-datos-de-entrada)
4. [Módulo de Extracción (ExcelExtractor)](#4-módulo-de-extracción-excelextractor)
5. [Módulo de Limpieza de Núcleos Temáticos (nucleos_cleaner)](#5-módulo-de-limpieza-de-núcleos-temáticos-nucleos_cleaner)
6. [Módulo de Análisis de Calidad (CurricularAnalyzer)](#6-módulo-de-análisis-de-calidad-curricularanalyzer)
7. [Módulo de Cobertura del Perfil de Egreso (perfil_coverage_analyzer)](#7-módulo-de-cobertura-del-perfil-de-egreso-perfil_coverage_analyzer)
8. [Módulo de Asignaturas Compartidas (shared_subjects_analyzer)](#8-módulo-de-asignaturas-compartidas-shared_subjects_analyzer)
9. [Módulo de Modelado de Tópicos (topic_modeler)](#9-módulo-de-modelado-de-tópicos-topic_modeler)
10. [Módulo de Validación (QualityValidator)](#10-módulo-de-validación-qualityvalidator)
11. [Módulo de Detección de Temáticas (ThematicDetector)](#11-módulo-de-detección-de-temáticas-thematicdetector)
12. [Módulo de Reportes (ReportGenerator)](#12-módulo-de-reportes-reportgenerator)
13. [Dashboard Interactivo](#13-dashboard-interactivo)
14. [Orquestación del Pipeline (run_analysis.py)](#14-orquestación-del-pipeline-run_analysispy)
15. [Resultados y Validación](#15-resultados-y-validación)
16. [Configuración Centralizada (config.py)](#16-configuración-centralizada-configpy)

---

## 1. Marco del Problema

### 1.1 Contexto

Las instituciones de educación superior enfrentan desafíos crecientes en la gestión de la calidad curricular. Los microcurrículos —documentos que detallan cada asignatura: resultados de aprendizaje, contenidos, estrategias pedagógicas y evaluación— constituyen la unidad basal del diseño curricular. Sin embargo, suelen producirse de forma descentralizada, lo que genera problemas como:

- **Duplicidad temática**: asignaturas de diferentes programas abordan los mismos contenidos sin coordinación.
- **Brechas curriculares**: elementos del perfil de egreso que no tienen correspondencia con ninguna asignatura.
- **Desequilibrio de saberes**: predominancia de teoría (Saber) sobre práctica (SaberHacer) o actitudes (SaberSer).
- **Inconsistencias taxonómicas**: resultados de aprendizaje declarados en niveles Bloom altos (Crear, Evaluar) pero redactados con verbos de niveles inferiores.
- **Asimetrías entre sedes**: un mismo programa impartido en múltiples campus con contenidos divergentes.

### 1.2 Objetivos del Sistema

1. **Automatizar** la extracción y consolidación de datos microcurriculares desde archivos Excel institucionales.
2. **Cuantificar** la calidad curricular mediante indicadores ponderados objetivos.
3. **Detectar** brechas entre el perfil de egreso declarado y el contenido curricular impartido.
4. **Identificar** asignaturas compartidas o similares entre programas para optimizar la oferta académica.
5. **Revelar** tendencias temáticas emergentes (IA, sostenibilidad, transformación digital) en el currículo.
6. **Visualizar** todos los resultados en un dashboard interactivo para tomadores de decisiones.

---

## 2. Arquitectura del Sistema

### 2.1 Diagrama General

```
┌─────────────────────────────────────────────────────────────────────┐
│                      ENTRADA: Archivos Excel .xlsx                  │
│         (5 hojas por programa: Perfil, Competencias, RA,            │
│          Estrategias Meso, Estrategias Micro)                       │
└───────────────────────────┬─────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────────┐
│  EXTRACTOR (ExcelExtractor)                                         │
│  • Detección fuzzy de hojas por nombre                              │
│  • Normalización de nombres de columna                              │
│  • Extracción de sede/modalidad desde código en nombre archivo      │
│  • Propagación de metadatos (Programa, Sede, Modalidad)             │
└───────────────────────────┬─────────────────────────────────────────┘
                            │
          ┌─────────────────┼─────────────────┐
          ▼                 ▼                  ▼
┌─────────────────┐ ┌──────────────┐ ┌──────────────────┐
│ LIMPIEZA        │ │ ANÁLISIS     │ │ COBERTURA        │
│ NÚCLEOS         │ │ CALIDAD      │ │ PERFIL EGRESO    │
│ (nucleos_cleaner)│ │ (analyzer)   │ │ (perfil_coverage)│
│ • 7 filtros     │ │ • 6 indica-  │ │ • TF-IDF 1500    │
│ • Score académico│ │ dores ponde- │ │ • BM25 híbrido   │
│ • Isolation     │ │ rados        │ │ • 9 campos       │
│   Forest        │ │ • Score 0-100│ │ • Trazabilidad   │
└─────────────────┘ └──────────────┘ └──────────────────┘
          │                  │                  │
          ▼                  ▼                  ▼
┌─────────────────┐ ┌──────────────┐ ┌──────────────────┐
│ ASIGNATURAS     │ │ TÓPICOS LDA  │ │ TEMÁTICAS        │
│ COMPARTIDAS     │ │ (topic_model)│ │ (thematic_detector)│
│ • Jaccard       │ │ • LDA batch  │ │ • 10 tendencias  │
│ • Coseno TF-IDF │ │ • 10 tópicos │ │ • Keywords match │
│ • Intra/Inter   │ │ • Fingerprint│ │ • Configurable   │
└─────────────────┘ └──────────────┘ └──────────────────┘
          │                  │                  │
          └──────────────────┼──────────────────┘
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│  REPORTES (ReportGenerator)                                         │
│  • Excel maestro (15 hojas)                                        │
│  • Reporte HTML individual por programa                            │
│  • Reporte JSON estructurado                                       │
│  • Matriz programas × temáticas                                    │
│  • Indicadores consolidados                                        │
└─────────────────────────────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│  DASHBOARD (Streamlit) — 10 páginas                                │
│  • Inicio │ Tipo de Saber │ Cobertura Perfil │ Cobertura Temática  │
│  • Tendencias │ Minería Texto │ Bloom │ Familias │ Config │ Datos  │
└─────────────────────────────────────────────────────────────────────┘
```

### 2.2 Stack Tecnológico

| Componente | Tecnología | Versión |
|-----------|-----------|---------|
| Lenguaje | Python | ≥ 3.10 |
| Procesamiento datos | pandas, numpy | 2.0+, 1.24+ |
| Visualización | plotly, streamlit | 5.18+, 1.30+ |
| Machine Learning | scikit-learn | 1.3+ |
| NLP | spaCy, rank-bm25 | 3.7+, 0.2+ |
| Excel | openpyxl | 3.1+ |
| Clustering | scipy | 1.11+ |
| Navegación dashboard | streamlit-option-menu | 0.3.6+ |
| Grafos | networkx | 3.0+ |
| Tests | pytest | 9.0+ |

### 2.3 Estructura del Proyecto

```
Analisis_Curricular/
├── run_analysis.py              # Orquestador del pipeline completo
├── config.py                    # Configuración centralizada (~500 líneas)
├── dashboard_tematico.py        # Dashboard Streamlit (~4500 líneas)
├── DOCUMENTACION.md             # Este documento
├── requirements.txt
├── src/
│   ├── __init__.py
│   ├── extractor.py             # ExcelExtractor (~680 líneas)
│   ├── analyzer.py              # CurricularAnalyzer (~510 líneas)
│   ├── thematic_detector.py     # ThematicDetector (~280 líneas)
│   ├── validator.py             # QualityValidator (~190 líneas)
│   ├── nucleos_cleaner.py       # Limpieza núcleos temáticos (~290 líneas)
│   ├── perfil_coverage_analyzer.py  # Cobertura perfil egreso (~480 líneas)
│   ├── shared_subjects_analyzer.py  # Asignaturas compartidas (~420 líneas)
│   ├── topic_modeler.py         # LDA y fingerprint TF-IDF (~245 líneas)
│   └── report_generator.py      # ReportGenerator (~800 líneas)
├── dashboard/
│   ├── __init__.py
│   └── app.py                   # Dashboard alternativo simplificado
├── tests/
│   ├── test_integracion.py      # Test de integración (3 archivos reales)
│   ├── test_nuevos_modulos.py   # Tests unitarios (5 módulos)
│   └── test_thematic_detector.py # Tests unitarios ThematicDetector
├── data/
│   ├── raw/                     # Archivos Excel de entrada
│   ├── processed/               # Datos procesados
│   └── output/                  # Reportes generados
│       ├── reportes/            # HTML/JSON individuales
│       ├── matrices/            # Programas × Temáticas
│       └── consolidado/         # Excel maestro + indicadores
├── templates/                   # Plantillas para reportes
├── assets/                      # Recursos (logo, etc.)
└── logs/                        # Archivos de log
```

---

## 3. Formato de Datos de Entrada

### 3.1 Estructura del Archivo Excel

Cada programa académico se entrega en un archivo `.xlsx` con 5 hojas de datos más 2 hojas auxiliares de taxonomía:

| Hoja | Nombre exacto | Header row | Columnas esperadas |
|------|--------------|------------|-------------------|
| Perfil Egreso | `Paso1 Analisis perfil egreso` | 1 (fila 2) | 11 columnas |
| Competencias | `Paso 2 Redacción competen` | 1 (fila 2) | 7 columnas |
| RA | `Paso 3 Redacción RA` | 1 (fila 2) | 9 columnas |
| Estrategias Meso | `Paso 4 Estrategias mesocurricu` | 0 (fila 1) | 6 columnas |
| Estrategias Micro | `Paso 5 Estrategias micro` | 1 (fila 2) | 16 columnas |
| Taxonomía Comp. | `Taxonomía para competencias` | — | — |
| Taxonomía RA | `Taxonomias para RA` | — | — |

Las filas de encabezado (`header_row`) están en índice 0-indexado: el valor 1 significa que la fila 2 contiene los nombres de columna y la fila 1 tiene placeholders o instrucciones. La hoja de Estrategias Meso usa `header_row=0` porque su primera fila ya contiene los encabezados reales.

### 3.2 Columnas de la Hoja "Paso 5 Estrategias micro" (la principal)

```
Tipo de Saber, Resultado de aprendizaje, Semestre,
Nombre asignatura o módulo, Indicadores de logro asignatura o módulo,
Tipología, B.Institucional, B.Disciplinar, B.Electivo,
Créditos, Número de horas trabajo directo,
Número de horas trabajo independiente, Total de horas,
Núcleos temáticos, Actividades de aprendizaje,
Actividades de evaluación, Acciones de retroalimentación
```

### 3.3 Codificación de Sede y Modalidad

El nombre del archivo debe terminar con un código de 4 caracteres:

| Código | Sede | Modalidad |
|--------|------|-----------|
| PBOG | Bogotá | Presencial |
| PMED | Medellín | Presencial |
| VNAL | Nacional | Virtual |
| HBOG | Bogotá | Híbrido |
| HMED | Medellín | Híbrido |

El extractor parsea este código con el patrón `filename[-4:]` y lo mapea mediante los diccionarios `sede_map` y `modalidad_map`. Estos metadatos se propagan a todas las filas extraídas.

---

## 4. Módulo de Extracción (ExcelExtractor)

**Archivo:** `src/extractor.py` (~680 líneas)

### 4.1 Clase y Constructor

```python
class ExcelExtractor:
    def __init__(self, file_path: str)
```

Abre el workbook con `openpyxl.load_workbook(data_only=True)`. Extrae el nombre del programa del nombre del archivo mediante regex: `FormatoRA_(.+?)_[A-Z]{4}`. Si el archivo no sigue la convención de nomenclatura, usa el nombre base sin extensión.

### 4.2 Detección Fuzzy de Hojas

```python
def _find_sheet(sheet_names, target_name)
```

Dado que los nombres de hoja pueden tener espacios al final o ligeras variaciones, la función busca la primera hoja cuyo nombre, tras eliminar espacios, comience con el target esperado. Si no encuentra coincidencia fuzzy, prueba coincidencia exacta. Si tampoco así, lanza una excepción.

### 4.3 Detección de Fila de Encabezados

```python
def _find_header_row(sheet, expected_cols)
```

Escanea las primeras 10 filas de la hoja. Para cada fila, calcula un score de coincidencia contra las columnas esperadas: cuenta cuántas celdas no-null coinciden (normalizadas: sin tildes, minúsculas) con la lista de columnas esperadas. Retorna el índice de la fila con mayor coincidencia. Si ninguna fila supera el umbral mínimo de coincidencias, usa el `HEADER_ROWS` de configuración como fallback.

### 4.4 Métodos de Extracción por Hoja

Cada método devuelve un DataFrame con las columnas correspondientes más las columnas `Programa`, `Sede`, `Modalidad`, `Codigo` añadidas automáticamente.

| Método | Hoja destino | Columnas |
|--------|-------------|----------|
| `extract_competencias()` | Paso 2 | 7 cols (No., Verbo, Objeto, Finalidad, Condición, Redacción, Tipo) |
| `extract_resultados_aprendizaje()` | Paso 3 | 9 cols (Competencia, Número, TipoSaber, SaberAsociado, Taxonomía, Dominio, Nivel, Verbo, RA) |
| `extract_estrategias_meso()` | Paso 4 | 6 cols (RA, Estrategia, Descripción, Indicador, Retroalimentación, Instrumentos) |
| `extract_estrategias_micro()` | Paso 5 | 16 cols (ver §3.2) |
| `extract_perfil_egreso()` | Paso 1 | 11 cols (Programa, Modalidad, Perfil prof., Perfil ocup., Saber, SaberHacer, SaberSer, Áreas prof., Tareas prof., Poblaciones, Valor agregado) |

### 4.5 Normalización de Columnas

```python
def _normalize_column_name(name)
```

1. Convierte a string
2. Elimina tildes (NFKD → ASCII)
3. Convierte a minúsculas
4. Elimina caracteres especiales no alfanuméricos (excepto espacios)
5. Sustituye espacios múltiples por uno solo
6. Busca coincidencia fuzzy contra la lista de columnas esperadas (substring match)

### 4.6 Extracción de Sede y Modalidad

```python
def _extract_sede_modalidad(filename)
```

Parsea el código de 4 letras al final del nombre (sin extensión). Usa los mapeos:

```python
sede_map = {
    'PBOG': 'Bogotá', 'PMED': 'Medellín', 'VNAL': 'Nacional',
    'HBOG': 'Bogotá', 'HMED': 'Medellín', 'HVAL': 'Virtual',
}
modalidad_map = {'P': 'Presencial', 'V': 'Virtual', 'H': 'Híbrido'}
```

### 4.7 Extracción del Nombre del Programa Inteligente

Si la hoja de perfil de egreso está disponible, lee la celda A3 (`df_perfil.iloc[2, 0]`) como nombre real del programa, sobreescribiendo el nombre derivado del archivo. Esto corrige casos donde el nombre del archivo está truncado o usa convenciones distintas.

### 4.8 Método `extract_all()`

```python
def extract_all(self) -> Dict
```

Retorna un diccionario con:
- `metadata`: `{programa, archivo, fecha, sede, modalidad, codigo}`
- `competencias`: DataFrame
- `resultados_aprendizaje`: DataFrame
- `estrategias_meso`: DataFrame
- `estrategias_micro`: DataFrame
- `perfil_egreso`: DataFrame

Cada hoja es opcional: si no se encuentra, se retorna un DataFrame vacío y se registra una advertencia.

### 4.9 Validación de Estructura

```python
def validate_structure(self) -> Dict
```

Verifica:
- Hojas obligatorias: Competencias y RA (deben existir y tener datos)
- Hojas opcionales: Meso, Micro, Perfil (se registra advertencia si faltan)
- Retorna `{valid: bool, errors: List[str], warnings: List[str], info: List[str]}`

---

## 5. Módulo de Limpieza de Núcleos Temáticos (nucleos_cleaner)

**Archivo:** `src/nucleos_cleaner.py` (~290 líneas)

### 5.1 Propósito

La columna "Núcleos temáticos" de las estrategias micro contiene, en celdas de texto libre, una lista de temas que la asignatura aborda. Sin embargo, frecuentemente incluye fragmentos no temáticos: instrucciones ("actividades de aprendizaje"), encabezados ("unidad 1"), fragmentos ("de la"), o ruido general. Este módulo implementa un pipeline de limpieza en cascada para separar núcleos válidos de inválidos.

### 5.2 Funciones de Preprocesamiento

#### `_normalizar(texto: str) → str`

```python
unicodedata.normalize('NFKD', texto.lower()).encode('ascii', 'ignore').decode('ascii')
```

Elimina tildes, convierte a minúsculas, elimina caracteres no-ASCII. Es la normalización base usada en todos los filtros.

#### `limpiar_nucleo(texto: str) → str`

Elimina prefijos numéricos y viñetas:

```python
t = re.sub(r'^\d+[\.\)]\s*', '', t)       # "1. Texto" → "Texto"; "2) Texto" → "Texto"
t = re.sub(r'^[•\-–—*]\s*', '', t)        # "• Texto" → "Texto"; "- Texto" → "Texto"
```

#### `tokenizar_nucleo_celda(texto_celda: str) → List[str]`

Divide una celda que puede contener múltiples núcleos separados por:

```python
partes = re.split(r'[;\n\|]+', texto)      # split por ; nueva línea o |
# Luego, para cada parte, subdivide por items numerados:
sub = re.split(r'(?<!\d)(?=\d+[\.\)]\s+\w)', p)  # "1. text" o "2) text"
```

El split por items numerados usa una aserción negativa `(?<!\d)` para evitar partir dentro de números decimales. Cada sub-elemento se limpia con `limpiar_nucleo` y se añade si `len > 0`.

### 5.3 Pipeline de Validación: `es_nucleo_valido(texto) → Tuple[bool, str]`

Aplica 7 filtros en cascada secuencial. Tan pronto como un filtro rechaza el texto, retorna `(False, razón)`. Si todos los filtros pasan, retorna `(True, "")`.

#### Filtro 1: Longitud Mínima

```
if len(t) < MIN_LONGITUD (4) → "Demasiado corto (X chars, min 4)"
```

#### Filtro 2: Longitud Máxima

```
if len(t) > MAX_LONGITUD (150) → "Demasiado largo (X chars, max 150)"
```

#### Filtro 3: Solo Caracteres Especiales

```python
if re.match(r'^[\d\s\.\,\;\:\-]+$', t) → "Solo números o caracteres especiales"
```

Acepta solo dígitos, espacios, puntos, comas, puntos y coma, dos puntos y guiones.

#### Filtro 4: Conteo de Palabras

```
if len(t.split()) < MIN_PALABRAS (2) → "Menos de 2 palabras"
```

#### Filtro 5: Patrón de Encabezado/Instrucción

Evalúa contra `_PATRON_NO_NUCLEO`, una expresión regular compuesta que captura 18 patrones de encabezados docentes comunes:

```
^(construccion\s+y\s+dinamicas?|dinamicas?\s+de|
  estrategias?\s+de\s+(ensenanza|aprendizaje|evaluacion)|
  actividades?\s+(de\s+)?(aprendizaje|evaluacion)|
  metodologia|criterios?\s+de|recursos?\s+(educativos?|didacticos?)|
  indicadores?\s+de|competencias?\s+(generales?|especificas?)|
  resultados?\s+de\s+aprendizaje|nucleo\s+tematico|
  temas?\s+a\s+(desarrollar|tratar)|
  contenido[s]?\s*(del?\s+)?curso|
  unidad\s+(tematica\s+)?\d*|modulo\s+\d*|
  semana\s+\d*|bloque\s+(tematico)?\s*\d*)
```

Cada alternativa está anclada al inicio (`^`) y es case-insensitive.

#### Filtro 6: Inicio con Preposición/Conjunción (Fragmento)

Evalúa contra `_INICIO_INVALIDO` tras aplicar `limpiar_nucleo`:

```python
^(o |y |e |u |ni |pero |sino |aunque |mas |porque |pues |
  de |del |al |a |en |con |sin |por |para |
  lo |la |el |los |las |un |una |
  que |si |su |sus |se |le |les )
```

34 palabras funcionales del español que, cuando inician un núcleo, indican que es un fragmento de una frase mayor.

#### Filtro 7: Terminación con Letra Suelta

```python
if _FINAL_LETRA_SUELTA.search(t_norm) → "Termina con letra suelta (probable truncamiento)"
```

Patrón: `\s+[A-Za-z]$` — captura cadenas como "Expansión A", "Análisis B", que son truncamientos de items enumerados.

### 5.4 Score Académico: `calcular_score_academico(texto) → float`

Asigna un puntaje numérico entre 0 y 1 que refleja qué tan "académico" es el núcleo.

**Fórmula:**

```
score = (P × 0.15) + (T × 0.02) − (N × 0.10)
score = max(0.0, min(1.0, score))
```

Donde:
- `P` = conteo de palabras académicas positivas presentes en el texto
- `T` = número total de palabras en el texto
- `N` = conteo de palabras negativas presentes

**Palabras positivas** (30 términos): análisis, fundamentacion, teorica, practica, aplicacion, evaluacion, diagnostico, planeacion, gestion, desarrollo, investigacion, innovacion, estrategia, metodologia, sistema, proceso, modelo, marco, enfoque, metodo, tecnica, herramienta, instrumento, indicador, variable, factor, componente, elemento, estructura, funcion, mecanismo.

Cada una aporta `+0.15`.

**Palabras negativas** (21 términos): taller, ejercicio, practica, lectura, exposicion, debate, salida, campo, visita, conferencia, seminario, charla, introduccion, bienvenida, presentacion, generalidades, induccion, nivelacion, repaso, "repaso general".

Cada una aporta `-0.10`.

**Justificación de coeficientes:**
- `+0.15` por keyword positiva: permite que con ~3 palabras positivas un texto corto (5 palabras) alcance score > 0.5.
- `+0.02` por palabra total: recompensa núcleos sustantivos.
- `-0.10` por keyword negativa: penaliza términos no académicos.
- Clip a `[0, 1]`: garantiza puntaje como probabilidad.

### 5.5 Pipeline Completo: `filtrar_nucleos_dataframe(df, columna) → DataFrame`

```python
def filtrar_nucleos_dataframe(df, columna='Núcleos temáticos')
```

Para cada fila del DataFrame:
1. Lee el texto de la celda en `columna`
2. Si está vacío o es NaN, salta
3. `tokenizar_nucleo_celda()` → lista de núcleos candidatos
4. Para cada candidato:
   a. `limpiar_nucleo()`
   b. `es_nucleo_valido()` → si inválido, registrar en lista de rechazados con razón
   c. Si válido, `calcular_score_academico()`
   d. Clasificar: si score ≥ `UMBRAL_SCORE_ACADEMICO` (0.5) → "ALTO", sino "BAJO"

Retorna un diccionario con:
- `validos`: lista de `{nucleo, score, clasificacion, programa, asignatura, semestre}`
- `rechazados`: lista de `{nucleo_original, razon, programa, asignatura}`
- `stats`: `{total, validos, rechazados, tasa_rechazo}`

### 5.6 Detección de Anomalías: `detectar_anomalias_nucleos(series, contamination) → pd.Series`

Usa **Isolation Forest** sobre vectores TF-IDF para identificar núcleos temáticos atípicos.

**Parámetros:**
- `contamination=0.15` (porcentaje esperado de anomalías)
- Mínimo 10 muestras (si `n < 10`, todas retornan `False`)
- Vectorizador: `TfidfVectorizer(max_features=100, min_df=1, max_df=0.9)`
- Modelo: `IsolationForest(contamination=0.15, random_state=42)`
- Predicción: `fit_predict()` sobre matriz TF-IDF densa. Anomalía si predicción = `-1`.

Este detector complementa los filtros basados en reglas capturando núcleos sintácticamente válidos pero semánticamente anómalos en el contexto del corpus.

### 5.7 Justificación del Enfoque

La combinación de 7 filtros basados en reglas + score académico + Isolation Forest proporciona:

1. **Alta precisión**: los filtros de reglas eliminan ~90% del ruido conocido (encabezados, fragmentos, formatos inválidos).
2. **Cobertura**: el score académico captura matices de calidad que los filtros binarios no pueden.
3. **Detección de novedades**: Isolation Forest identifica patrones anómalos no previstos por las reglas.
4. **Auditabilidad**: cada rechazo se registra con su razón, permitiendo ajustar los filtros.

---

## 6. Módulo de Análisis de Calidad (CurricularAnalyzer)

**Archivo:** `src/analyzer.py` (~510 líneas)

### 6.1 Score de Calidad Compuesto

Calcula 6 indicadores y los combina en un score 0-100 mediante promedio ponderado:

```
score_total = (score_completitud × 0.25) +
              (score_complejidad × 0.20) +
              (score_balance × 0.15) +
              (score_diversidad × 0.15) +
              (score_cobertura × 0.15) +
              (80.0 × 0.10)
```

El peso de `calidad_redaccion` es fijo en 80.0 como placeholder (pendiente de implementación completa de análisis lingüístico).

### 6.2 Indicador 1: Completitud (peso 0.25)

Se calcula por DataFrame individualmente y luego se pondera:

```
completitud_df = (celdas_llenas / total_celdas) × 100
completitud_total = completitud_comp × 0.3 + completitud_ra × 0.4 +
                    completitud_meso × 0.15 + completitud_micro × 0.15
```

Los pesos reflejan la importancia relativa: RA (0.4) y Competencias (0.3) son los componentes más críticos del diseño curricular.

### 6.3 Indicador 2: Complejidad Cognitiva (peso 0.20)

#### 6.3.1 Asignación de Nivel Bloom

El método `_get_nivel_taxonomico(row)` implementa la decisión **ADR-04**: prioriza la columna "Nivel Dominio" sobre la taxonomía de verbos Bloom.

**Algoritmo:**

```
1. Obtener valor de 'Nivel Dominio' de la fila
2. Si no es NaN:
   - Buscar subcadenas en orden descendente de nivel:
     'crea' o 'disena' → nivel 6 (Crear)
     'evalua' o 'critica' → nivel 5 (Evaluar)
     'analisis' o 'analis' → nivel 4 (Analizar)
     'aplic' → nivel 3 (Aplicar)
     'comprend' o 'entiend' → nivel 2 (Comprender)
     'recuerd' o 'identific' o 'reconoc' → nivel 1 (Recordar)
3. Si no hay match o Nivel Dominio es NaN:
   - Fallback a búsqueda de verbo en TAXONOMIA_BLOOM:
     Para cada (nivel, config) en TAXONOMIA_BLOOM:
       Si el verbo del RA está en config['verbos']:
         retornar config['nivel']
4. Default: nivel 2 (Comprender)
```

**Tabla de verbos Bloom:**

| Nivel | Nombre | Verbos |
|-------|--------|--------|
| 1 | RECORDAR | definir, listar, recordar, identificar, nombrar, reconocer, reproducir, seleccionar, enumerar |
| 2 | COMPRENDER | explicar, describir, interpretar, resumir, clasificar, comparar, ejemplificar, parafrasear, ilustrar |
| 3 | APLICAR | aplicar, ejecutar, implementar, usar, utilizar, demostrar, resolver, calcular, operar |
| 4 | ANALIZAR | analizar, diferenciar, organizar, atribuir, comparar, contrastar, examinar, investigar, categorizar |
| 5 | EVALUAR | evaluar, criticar, juzgar, verificar, validar, argumentar, defender, apoyar, justificar |
| 6 | CREAR | crear, diseñar, construir, planificar, producir, generar, desarrollar, formular, proponer |

#### 6.3.2 Bandas de Complejidad

```
Básico    = niveles [1, 2]  → Recordar, Comprender
Intermedio = niveles [3, 4] → Aplicar, Analizar
Avanzado   = niveles [5, 6] → Evaluar, Crear

nivel_promedio = media de todos los niveles asignados
indice_complejidad = ((nivel_promedio − 1) / 5) × 100  → escala 0–100
```

### 6.4 Indicador 3: Balance de Tipos de Saber (peso 0.15)

```
Para cada tipo en ['Saber', 'SaberHacer', 'SaberSer']:
    porcentaje = (conteo_tipo / total_RA) × 100

desviacion_estandar = np.std([%Saber, %SaberHacer, %SaberSer])
score_balance = max(0, min(100, 100 − desviacion_estandar × 5))
```

El balance ideal (referencia institucional) es 33.3% cada tipo. El score penaliza desviaciones: una desviación estándar de 20 puntos porcentuales reduce el score a 0.

### 6.5 Indicador 4: Cobertura de Competencias (peso 0.15)

```
competencias_con_ra = df_ra['Competencia por desarrollar'].nunique()
total_competencias = df_comp['Redacción competencia'].nunique()

porcentaje_cobertura = (competencias_con_ra / total_competencias) × 100
promedio_ra_por_competencia = mean(conteo_RA_por_competencia)
```

### 6.6 Indicador 5: Diversidad Metodológica (peso 0.15)

Busca en columnas de actividades de aprendizaje y evaluación la presencia de 21 keywords metodológicas:

```
clase magistral, taller, laboratorio, caso, estudio de caso,
problema, proyecto, simulación, debate, ejercicio,
lectura, seminario, tutoría, investigación, exposición,
charla, demonstración, mapeo, analogía
```

Define un subconjunto de **metodologías activas** (7 items):

```python
metodologias_activas = {'Taller', 'Laboratorio', 'Caso', 'Problema',
                        'Proyecto', 'Simulación', 'Debate'}
```

```
score_diversidad = min(100, num_estrategias_unicas × 8)
porcentaje_activas = (conteo_activas / total_keywords_encontradas) × 100
```

El factor 8 significa que con 13 estrategias únicas se alcanza el score máximo de 100.

---

## 7. Módulo de Cobertura del Perfil de Egreso (perfil_coverage_analyzer)

**Archivo:** `src/perfil_coverage_analyzer.py` (~480 líneas)

### 7.1 Propósito

Evalúa cuantitativamente en qué medida los contenidos curriculares (asignaturas, RA, indicadores, actividades) cubren los elementos declarados en el perfil de egreso del programa. Cada elemento del perfil se clasifica como CUBIERTO o BRECHA.

### 7.2 Extracción de Elementos del Perfil

```python
def extraer_elementos_perfil(df_perfil: pd.DataFrame) -> List[Dict]
```

Recorre las 9 columnas del perfil definidas en `COLUMNAS_PERFIL`:

```python
['Perfil profesional', 'Perfil ocupacional', 'Saber', 'SaberHacer',
 'SaberSer', 'Áreas profesionales', 'Tareas profesionales',
 'Poblaciones actuación', 'Valor agregado']
```

Para cada celda:
1. Si `len(valor) ≤ 3` → se omite
2. Si la celda tiene ≤ 15 palabras → se mantiene entera
3. Si tiene más de 15 palabras → se divide por los delimitadores `[/\n•–—]`
4. Cada sub-elemento se recorta y se añade si `len > 3`

Cada elemento se almacena como:
```python
{'campo': 'Saber', 'elemento': 'texto original', 'elemento_norm': 'texto normalizado'}
```

### 7.3 Construcción del Corpus Curricular

```python
def construir_corpus_curriculo(df_micro, df_ra) → (corpus, corpus_fuente)
```

Extrae texto de:

- **Paso 5** (estrategias micro): columnas `Resultado de aprendizaje`, `Nombre asignatura o módulo`, `Indicadores de logro asignatura o módulo`, `Núcleos temáticos`, `Actividades de evaluación`
- **Paso 3** (RA): columna `SaberAsociado` (incluida con peso doble: se duplica en el corpus)

Cada entrada se normaliza (`_normalizar_texto`) y se etiqueta en `corpus_fuente` con:
```python
{'columna': col, 'asignatura': nombre_asignatura, 'texto_display': str(val)[:120]}
```

### 7.4 Vectorización TF-IDF

```python
TFIDF_KWARGS = dict(
    max_features=1500,
    min_df=1,           # un término que aparece en 1 documento mínimo
    max_df=0.85,        # ignora términos en >85% de documentos
    ngram_range=(1, 3),  # unigramas, bigramas, trigramas
    sublinear_tf=True,   # log(1 + tf) en vez de tf crudo
    stop_words=STOP_WORDS_FINAL,
)
```

**Stop words:** unión de stop words de spaCy (si está disponible) más un conjunto extra de 18 términos académicos genéricos (mediante, traves, partir, nivel, proceso, manera, ambito, contexto, actividad, desarrollo, aplicacion, estudiante, programa, curricular, asignatura, modulo). Fallback a 33 términos si spaCy no está instalado.

### 7.5 Cálculo de Cobertura Híbrida

```python
def calcular_cobertura_elemento(elemento_norm, corpus, corpus_fuente,
                                 vectorizer, tfidf_matrix) → (score, idx, asig, doc)
```

Combina dos métricas:

#### Componente 1: Similitud Coseno (60%)

```python
def _score_top_k_ponderado(sim_row):
    orden = np.argsort(sim_row)[::-1]
    k = min(3, len(orden))
    top_idx = orden[:k]
    top_scores = sim_row[top_idx]
    pesos = PESOS_TOP_K[:k]  # [0.5, 0.3, 0.2] truncado si k<3
    pesos = pesos / pesos.sum()  # renormalizado a suma=1
    score = np.dot(top_scores, pesos)
    return score, top_idx[0]
```

**Fórmula:** `score_coseno = w₁·s₁ + w₂·s₂ + w₃·s₃`
donde `w = [0.5, 0.3, 0.2]` y `s₁ ≥ s₂ ≥ s₃` son las tres mayores similitudes coseno entre el vector TF-IDF del elemento y los vectores del corpus.

**Justificación del ponderación top-3:** Un elemento del perfil puede estar cubierto por múltiples documentos curriculares. Los top-3 capturan las contribuciones más relevantes sin diluir el score con ruido de documentos no relacionados.

#### Componente 2: BM25 (40%)

```python
from rank_bm25 import BM25Okapi
tokenized = [doc.split() for doc in corpus if doc.strip()]
bm25 = BM25Okapi(tokenized)
query = elemento_norm.split()
scores = bm25.get_scores(query)
score_bm25 = min(1.0, max(scores) / (max(scores) + 2.0))
```

**Fórmula:** `score_BM25_norm = min(1.0, max(BM25_scores) / (max(BM25_scores) + 2.0))`

BM25 es un modelo de ranking probabilístico que pondera términos por su frecuencia en el documento y rareza en el corpus. La normalización `x/(x+2)` mapea el score máximo al rango `[0,1)` con asíntota en 1. El valor 2 en el denominador es un parámetro empírico que produce una curva de saturación razonable.

#### Score Híbrido Final

```
score_hibrido = 0.6 × score_coseno + 0.4 × score_BM25_norm
score_hibrido = max(0.0, min(1.0, score_hibrido))
```

**Fundamento de la combinación:** La similitud coseno captura alineación semántica global (coocurrencia de términos importantes), mientras BM25 captura relevancia específica (términos raros pero muy pertinentes). La ponderación 60/40 da más peso a la alineación semántica general.

### 7.6 Umbrales de Clasificación

Cada campo del perfil tiene su propio umbral, calibrado según la naturaleza del contenido:

| Campo | Umbral | Justificación |
|-------|--------|---------------|
| Perfil profesional | 0.28 | Contenido más general, mayor diversidad de redacción |
| Perfil ocupacional | 0.28 | Similar al profesional |
| Saber | 0.35 | Contenido teórico, mediano nivel de especificidad |
| SaberHacer | 0.35 | Contenido procedimental |
| SaberSer | 0.32 | Contenido actitudinal, más difícil de mapear |
| Áreas profesionales | 0.38 | Alta especificidad, requiere mayor coincidencia |
| Tareas profesionales | 0.38 | Alta especificidad |
| Poblaciones actuación | 0.32 | Moderadamente específico |
| Valor agregado | 0.30 | Contenido diferenciador, umbral intermedio |

El umbral global de fallback es `UMBRAL_COBERTURA = 0.35`.

### 7.7 Clasificación y Trazabilidad

```
score ≥ umbral_del_campo → 'CUBIERTO'
score < umbral_del_campo → 'BRECHA'
```

Para cada elemento clasificado como CUBIERTO, se registra la **trazabilidad**:
- `idx_mejor`: índice del documento en el corpus con mayor similitud
- `asignatura_trazable`: nombre de la asignatura que mejor cubre el elemento
- `doc_trazable`: texto del documento que generó la máxima similitud (truncado a 120 caracteres)

### 7.8 Métricas Agregadas

```
cobertura_global = ((total_elementos − num_brechas) / total_elementos) × 100
cobertura_por_campo = % de elementos CUBIERTO dentro de cada campo
```

### 7.9 Generación de Recomendaciones

Reglas para generar alertas textuales:

1. Si `num_brechas > 5`: Recomendación genérica de revisión.
2. Si `cobertura_global < 40%`: Alerta crítica, recomienda revisión completa del perfil vs. currículo.
3. Por campo: Si un campo concentra múltiples brechas, se genera una recomendación específica: `"Campo '{campo}': {count} elemento(s) sin cobertura. Evaluar si es necesario reforzar en el plan de estudios."`

### 7.10 Algoritmo Completo

```
INPUT: df_perfil, df_micro, df_ra
OUTPUT: {
  programa: str,
  total_elementos: int,
  cobertura_global: float,
  cobertura_por_campo: Dict[str, float],
  elementos: [{campo, elemento, score, umbral, clasificacion, asignatura_trazable, doc_trazable}],
  brechas: [{...elementos con clasificacion='BRECHA'}],
  num_brechas: int,
  recomendaciones: [str],
  corpus_size: int
}

1. Extraer nombre del programa desde df_perfil
2. Extraer elementos del perfil → lista de {campo, elemento, elemento_norm}
3. Construir corpus curricular desde df_micro + df_ra
4. Si len(corpus) < 3 → todos los scores = 0, todos BRECHA
5. Entrenar TfidfVectorizer con TFIDF_KWARGS sobre corpus
6. Para cada elemento:
   a. Obtener umbral específico del campo (o fallback 0.35)
   b. Vectorizar elemento_norm con el mismo vectorizer
   c. Calcular similitud coseno contra tfidf_matrix
   d. Calcular score top-3 ponderado
   e. Calcular BM25 score normalizado
   f. Combinar: score = 0.6 × coseno + 0.4 × BM25
   g. Clasificar: score >= umbral → CUBIERTO, sino BRECHA
   h. Si CUBIERTO: registrar trazabilidad (mejor_match)
7. Calcular cobertura_global y cobertura_por_campo
8. Generar recomendaciones basadas en brechas
9. Retornar diccionario completo
```

---

## 8. Módulo de Asignaturas Compartidas (shared_subjects_analyzer)

**Archivo:** `src/shared_subjects_analyzer.py` (~420 líneas)

### 8.1 Propósito

Identifica asignaturas que se repiten entre programas académicos, tanto con nombre exacto como con contenido similar. Esto permite detectar oportunidades de unificación, homologación o coordinación curricular.

### 8.2 Constantes

```python
UMBRAL_IDENTICO = 0.95    # Similitud coseno para considerar "idéntica"
UMBRAL_SIMILAR = 0.60     # Similitud mínima para reportar como "similar"
max_asignaturas = 500      # Límite de pares para muestreo estratificado
```

Columnas consideradas para el contenido (similitud semántica):

```python
COLUMNAS_CONTENIDO = [
    'Nombre asignatura o módulo',       # Solo para identificación
    'Indicadores de logro asignatura o módulo',
    'Núcleos temáticos',
    'Resultado de aprendizaje'
]
```

### 8.3 Asignaturas Idénticas

```python
def detectar_asignaturas_identicas(df) → DataFrame
```

1. Normaliza el nombre de asignatura (minúsculas, sin tildes)
2. Agrupa por nombre normalizado
3. Filtra grupos con `nunique(Programa) > 1`
4. Retorna DataFrame con: `{nombre_asignatura, programas: [lista], sedes: [lista], num_programas}`

### 8.4 Comparación Intra-Sede

```python
def comparar_intra_sede(df) → DataFrame
```

Para cada programa que existe en **múltiples sedes** (ej: "Administración de Empresas" en Bogotá y Medellín), calcula dos métricas de similitud entre los conjuntos de asignaturas de cada par de sedes:

#### Similitud de Jaccard (sobre nombres)

```
Jaccard(A, B) = |A ∩ B| / |A ∪ B|
```

Donde `A` y `B` son los conjuntos de nombres de asignaturas (normalizados) de sede A y sede B.

#### Similitud Semántica (TF-IDF + coseno)

```python
textos_a = [texto_asignatura(row) for row in sede_a]
textos_b = [texto_asignatura(row) for row in sede_b]

vectorizer = TfidfVectorizer(max_features=200, min_df=1, max_df=0.9, ngram_range=(1,2))
tfidf = vectorizer.fit_transform(textos_a + textos_b)
sim_matrix = cosine_similarity(tfidf[:n_a], tfidf[n_a:])
sim_max = sim_matrix.max()  # máxima similitud entre cualquier par (a, b)
```

El texto de cada asignatura se construye concatenando las columnas de contenido excluyendo el nombre (`COLUMNAS_CONTENIDO[1:]`), normalizado.

### 8.5 Comparación Inter-Programa

```python
def comparar_inter_programa(df, umbral_identico=0.95, umbral_similar=0.60,
                            max_asignaturas=500) → DataFrame
```

Compara asignaturas entre **diferentes programas**, no entre sedes del mismo programa.

#### Muestreo Estratificado (control de complejidad O(n²))

Dado que `n` asignaturas producirían `O(n²)` pares, se implementa un muestreo estratificado por programa:

```
Si n_asignaturas > max_asignaturas (500):
    n_por_programa = max(1, 500 // n_programas)
    Para cada programa:
        Si sus asignaturas > n_por_programa:
            muestra_aleatoria(n=n_por_programa, random_state=42)
    Concatenar todas las muestras
```

**Justificación:** 500 asignaturas producen ~125,000 pares, procesables en segundos. Sin muestreo, 3,000 asignaturas producirían ~4.5 millones de pares, inviables en un dashboard interactivo.

#### Vectorización y Similitud

```python
vectorizer = TfidfVectorizer(
    max_features=300, min_df=1, max_df=0.85,
    ngram_range=(1, 2),
    stop_words=['el', 'la', 'de', 'que', ...]
)
tfidf = vectorizer.fit_transform(textos)
sim_matrix = cosine_similarity(tfidf)  # matriz completa n×n
```

Para cada par `(i, j)` con `programa_i ≠ programa_j` y `sim ≥ umbral_similar (0.60)`:

```python
categoria = 'IDENTICO' if sim >= 0.95 else 'SIMILAR'
```

### 8.6 Generación de Recomendaciones

```python
def _recomendar(row):
    if sim >= 0.95:    return 'UNIFICAR'    # Misma asignatura, fusionar
    elif sim >= 0.80:  return 'HOMOLOGAR'   # Muy similar, validar equivalencia
    else:              return 'COORDINAR'   # Similar, coordinar contenidos
```

| Rango | Recomendación | Acción sugerida |
|-------|--------------|-----------------|
| ≥ 0.95 | UNIFICAR | Unificar en una sola asignatura para todos los programas |
| ≥ 0.80 | HOMOLOGAR | Homologar entre programas (reconocimiento mutuo) |
| ≥ 0.60 | COORDINAR | Coordinar contenidos para evitar duplicidad parcial |

### 8.7 Pipeline Completo

```python
def detectar_asignaturas_compartidas(df) → Dict
```

1. **Paso 1:** Ejecutar `comparar_intra_sede(df)` → pares intra-sede
2. **Paso 2:** Ejecutar `comparar_inter_programa(df)` → pares inter-programa + recomendaciones
3. **Ejecutar** `detectar_asignaturas_identicas(df)` → nombres exactos repetidos
4. **Agregar resumen**: total programas, pares intra-sede, pares inter-programa, asignaturas idénticas

Retorna:
```python
{
    'intra_sede': DataFrame,
    'inter_programa': DataFrame,
    'asignaturas_identicas': DataFrame,
    'resumen': {
        'total_programas': int,
        'pares_intra_sede': int,
        'pares_inter_programa': int,
        'asignaturas_identicas': int
    }
}
```

---

## 9. Módulo de Modelado de Tópicos (topic_modeler)

**Archivo:** `src/topic_modeler.py` (~245 líneas)

### 9.1 Propósito

Aplica **Latent Dirichlet Allocation (LDA)** no supervisado sobre el corpus textual de los SaberAsociado (Resultados de Aprendizaje) para descubrir automáticamente los temas subyacentes del currículo, complementando la detección basada en keywords fijas.

### 9.2 Constantes

```python
N_TOPICS_DEFAULT = 10     # Número de tópicos por defecto
N_TOP_WORDS = 15          # Palabras por tópico
```

### 9.3 Entrenamiento LDA

```python
def entrenar_lda(corpus, n_topics=10, n_top_words=15) → Dict
```

#### Preprocesamiento

```python
corpus_limpio = [_normalizar(t) for t in corpus
                 if pd.notna(t) and len(str(t)) > 5]
```

Normalización:
1. Unicode NFKD → ASCII (elimina tildes)
2. Minúsculas
3. Elimina caracteres no alfabéticos excepto espacios
4. Espacios simples

#### Validación de Corpus

```
Si len(corpus_limpio) < n_topics → n_topics = max(2, len(corpus_limpio) // 2)
Si len(corpus_limpio) < 5 → retorna vacío (corpus insuficiente)
```

#### Vectorización

```python
vectorizer = CountVectorizer(
    max_features=500,     # Vocabulario máximo
    min_df=2,             # Término debe aparecer en ≥2 documentos
    max_df=0.85,          # Ignorar términos en >85% de documentos
    stop_words=STOPWORDS, # 36 stop words en español
    ngram_range=(1, 2)    # Unigramas y bigramas
)
counts = vectorizer.fit_transform(corpus_limpio)
```

#### Modelo LDA

```python
model = LatentDirichletAllocation(
    n_components=n_topics,
    random_state=42,
    max_iter=100,
    learning_method='batch'
)
topic_distribution = model.fit_transform(counts)
```

Parámetros no explícitos (valores por defecto de sklearn):
- `doc_topic_prior (alpha)`: 0.1
- `topic_word_prior (beta)`: 1.0 / n_components
- `learning_decay`: 0.7 (solo relevante en 'online')
- `mean_change_tol`: 0.001
- `evaluate_every`: -1 (sin evaluación periódica)

#### Extracción de Tópicos

```python
for topic_idx, topic in enumerate(model.components_):
    top_indices = topic.argsort()[:-n_top_words - 1:-1]  # top 15
    top_words = [feature_names[i] for i in top_indices]
    top_weights = [float(topic[i]) for i in top_indices]
```

#### Asignación de Tópico Dominante por Documento

```python
doc_topic = topic_distribution[i]  # distribución [P(t1), P(t2), ..., P(tk)]
topico_dom = int(doc_topic.argmax())
confianza = float(doc_topic.max())
```

### 9.4 Asignación de Tópicos por Programa

```python
def asignar_topicos_a_programas(df_ra, n_topics=10) → Dict
```

1. Agrupa `SaberAsociado` por programa (columna `Programa`)
2. Concatena todos los textos de cada programa
3. Entrena LDA sobre el corpus completo
4. Para cada programa:
   - Vectoriza su texto concatenado
   - Obtiene distribución de tópicos con `model.transform()`
   - Asigna tópico dominante (mayor probabilidad)
   - Registra confianza

Retorna:
```python
{
    'topics': [{topic_id, words: [str], weights: [float]}],
    'programa_topico': [{programa, topico_dominante, confianza}],
    'programa_dist': [{programa, distribucion: [float]}]  # n_topics probabilidades
    'model': LDA_model,           # Para reutilización
    'vectorizer': CountVectorizer,# Para reutilización
    'corpus_size': int,
    'n_topics': int
}
```

### 9.5 Fingerprint TF-IDF por Programa

```python
def obtener_fingerprint_tfidf(df_ra, n_terms=10) → DataFrame
```

Para cada programa, extrae los `n_terms` términos con mayor peso TF-IDF que lo distinguen del resto.

**Algoritmo:**
1. Concatena todos los `SaberAsociado` de cada programa
2. Vectoriza con `TfidfVectorizer(max_features=200, min_df=1, max_df=0.85, ngram_range=(1,2))`
3. Para cada programa `i`:
   - Obtiene la fila TF-IDF correspondiente
   - Ordena los pesos descendente
   - Toma los primeros `n_terms` donde `peso > 0`
4. Retorna DataFrame: `{programa, terminos_distinctivos: "término1, término2, ..."}`

### 9.6 36 Stop Words para Tópicos

```
el, la, de, que, y, a, en, un, ser, se, no, por, con, su, para, como,
estar, tener, le, lo, del, las, los, al, una, es, e, o, pero, mas,
este, entre, porque, cuando, muy, sin, vez, mucho, saber, sobre,
tambien, hasta, hay, donde, quien, desde, todos, durante, uno, les,
ni, contra, otros, fueron, ese, eso, ante, ellos, esto, mi, antes,
algunos, unos, yo, te, ti, nos, cada, asi
```

---

## 10. Módulo de Validación (QualityValidator)

**Archivo:** `src/validator.py` (~190 líneas)

### 10.1 Propósito

Valida la estructura y redacción de los Resultados de Aprendizaje (RA) según estándares institucionales de calidad.

### 10.2 Validación de Estructura del RA

```python
def validar_estructura_competencias(df_competencias) → Dict
```

Cada competencia debe tener los 4 componentes estructurales:
- **Verbo**: acción observable (debe coincidir con nivel Bloom declarado)
- **Objeto conceptual**: contenido sobre el que se actúa
- **Finalidad**: propósito del aprendizaje
- **Condición de contexto**: circunstancias de aplicación

Para cada fila de competencias, verifica que las columnas correspondientes no estén vacías:

```
validez_por_fila = todas_las_columnas_requeridas_tienen_datos
porcentaje_validez = (filas_válidas / total_filas) × 100
```

### 10.3 Validación de Coherencia Verbo-Taxonomía

```python
def validar_coherencia_taxonomica(df_ra) → Dict
```

Para cada RA:
1. Extrae el verbo principal del RA (primera palabra después de normalizar)
2. Busca el verbo en la tabla `TAXONOMIA_BLOOM` para determinar su nivel
3. Compara contra el nivel Bloom declarado en la columna `Taxonomía`
4. Si coinciden → coherente; si no → incoherencia

```
porcentaje_coherencia = (RA_coherentes / total_RA) × 100
```

### 10.4 Validación de Medibilidad

```python
def validar_medibilidad_ra(df_ra) → Dict
```

Un RA es medible si:
- Contiene un verbo de acción observable (presente en `TAXONOMIA_BLOOM`)
- Tiene al menos un objeto o contenido asociado (columna `SaberAsociado` no vacía)
- Tiene al menos 5 palabras en total

```
porcentaje_medible = (RA_medibles / total_RA) × 100
```

### 10.5 Score de Validación por Programa

```python
def validate_programa_completo(data) → Dict
```

Ejecuta las tres validaciones y combina en un score general:

```python
score_validacion = (
    validez_estructura × 0.4 +
    coherencia_taxonomica × 0.35 +
    medibilidad × 0.25
)
```

Retorna:
```python
{
    'score_validacion': float,          # 0–100
    'estructura': {...},
    'coherencia_taxonomica': {...},
    'medibilidad': {...},
    'alertas': [str]                    # Lista de problemas encontrados
}
```

---

## 11. Módulo de Detección de Temáticas (ThematicDetector)

**Archivo:** `src/thematic_detector.py` (~280 líneas)

### 11.1 Propósito

Detecta la presencia de 10 temáticas globales en los contenidos curriculares mediante búsqueda de palabras clave en campos específicos.

### 11.2 Las 10 Temáticas

| # | Temática | Keywords | Contexto Keywords |
|---|----------|----------|-------------------|
| 1 | SOSTENIBILIDAD | 17 (sostenibilidad, ambiental, ODS, economía circular, ...) | 4 |
| 2 | INTELIGENCIA ARTIFICIAL | 19 (machine learning, deep learning, NLP, GPT, ...) | 2 |
| 3 | RSE | 13 (RSE, ética empresarial, gobierno corporativo, ...) | 0 |
| 4 | TRANSFORMACIÓN DIGITAL | 17 (industria 4.0, IoT, blockchain, cloud, ...) | 2 |
| 5 | INNOVACIÓN Y EMPRENDIMIENTO | 16 (startup, design thinking, lean startup, MVP, ...) | 2 |
| 6 | GLOBALIZACIÓN | 14 (globalización, internacionalización, multicultural, ...) | 2 |
| 7 | ÉTICA Y VALORES | 15 (ética, valores, integridad, deontología, bioética, ...) | 2 |
| 8 | LIDERAZGO | 16 (liderazgo, soft skills, inteligencia emocional, ...) | 2 |
| 9 | ANÁLISIS DE DATOS | 17 (data analytics, estadística, Power BI, Python, SQL, ...) | 2 |
| 10 | GESTIÓN DEL CAMBIO | 10 (cambio organizacional, agile, scrum, ...) | 2 |

### 11.3 Algoritmo de Detección

```python
def analyze_programa(data) → Dict
```

Para cada temática, busca sus keywords en 3 campos del microcurrículo:
- `Núcleos temáticos`
- `Indicadores de logro asignatura o módulo`
- `Actividades de aprendizaje` / `Actividades de evaluación`

**Lógica de matching:**
- Búsqueda case-insensitive con substring
- Si la keyword contiene espacios, se busca como frase exacta
- Si no contiene espacios, se busca como palabra completa (rodeada de límites de palabra `\b`)

**Métricas por temática:**
```
asignaturas_con_tematica = n° asignaturas únicas donde se encontró al menos 1 keyword
cobertura = asignaturas_con_tematica / total_asignaturas × 100
```

**Detección por contexto:** Si se encuentra un keyword de contexto (más específico), la temática se marca como "FUERTE". Si solo se encuentran keywords base, se marca como "DÉBIL".

### 11.4 Matriz de Temáticas

```python
def generate_thematic_matrix(all_tematicas) → DataFrame
```

Genera una matriz `Programas × Temáticas` donde cada celda contiene el porcentaje de cobertura (0–100). Si un programa no tiene datos para una temática, la celda queda vacía.

### 11.5 Reporte de Resumen

```python
def generate_summary_report(matriz) → str
```

Genera un reporte textual con:
- Temáticas más y menos presentes
- Promedio de cobertura por temática
- Programas líderes en cada temática
- Distribución general

---

## 12. Módulo de Reportes (ReportGenerator)

**Archivo:** `src/report_generator.py` (~800 líneas)

### 12.1 Reporte HTML por Programa

```python
generate_html_report(data, indicadores, output_path, cobertura_perfil=None)
```

Genera una página HTML autónoma (sin dependencias externas) con:
- Score de calidad y desglose por indicador
- Métricas clave (competencias, RA, estrategias)
- Barras de progreso de tipos de saber
- Distribución de niveles Bloom
- Tabla de competencias
- Sección de cobertura de perfil (si se proporciona): cobertura global, brechas, recomendaciones

### 12.2 Reporte JSON por Programa

```python
generate_json_report(data, indicadores, tematicas, output_path, cobertura_perfil=None)
```

Genera un JSON estructurado con tipos nativos (conversión automática de numpy types).

Estructura:
```json
{
  "programa": "...",
  "fecha": "YYYY-MM-DD",
  "archivo": "...",
  "indicadores": { "score_calidad": 85.3, "completitud": {...}, ... },
  "tematicas": { "tematicas_presentes": [...], "num_tematicas": 5, "resumen": {...} },
  "resumen": { "total_competencias": 12, "total_ra": 48, ... },
  "cobertura_perfil": { "cobertura_global": 72.5, "num_brechas": 3, ... }
}
```

### 12.3 Matriz Programas × Temáticas

```python
generate_excel_matrix(matriz, output_path)
```

Exporta la matriz con anchos de columna ajustados automáticamente.

### 12.4 Excel Consolidado de Indicadores

```python
generate_consolidated_excel(all_indicadores, output_path)
```

Una hoja con un renglón por programa: score, competencias, RA, %saber, distribución Bloom, completitud.

### 12.5 Excel Maestro (15 hojas)

```python
generate_excel_maestro(all_results, output_path)
```

El archivo más completo del sistema. Sus 15 hojas son:

| Hoja | Contenido | Columnas clave |
|------|-----------|----------------|
| 01_Resumen_Ejecutivo | Un renglón por programa | Programa, Sede, Modalidad, Score_Calidad, Cobertura_Perfil, Brechas, Competencias, RA, Estrategias |
| 02_Competencias | Todas las competencias concatenadas | Programa, No., Verbo, Objeto, Finalidad, Condición, Redacción, Tipo |
| 03_RA_Completo | Todos los RA | Programa, Competencia, TipoSaber, SaberAsociado, Taxonomía, Nivel Dominio, Verbo RA |
| 04_Nucleos_Validos | Núcleos aceptados | Programa, Asignatura, Núcleo, Score_Académico, Clasificación |
| 05_Nucleos_Rechazados | Núcleos rechazados | Programa, Asignatura, Núcleo_Original, Razón_Rechazo |
| 06_Cobertura_Perfil_Egreso | Elementos del perfil | Programa, Campo, Elemento, Score, Umbral, Clasificación, Asignatura_Trazable |
| 06b_Cobertura_Por_Campo | Cobertura agregada | Programa, Campo, Elementos_Cubiertos, Total_Elementos, Porcentaje |
| 07_Brechas_Perfil | Brechas (score < umbral) | Programa, Campo, Elemento, Score, Umbral |
| 08_Divergencia_Inter_Sede | Pares intra-sede | Programa, Sede_A, Sede_B, Jaccard, Similitud_Semántica |
| 09_Asignaturas_Identicas | Nombres exactos repetidos | Asignatura, Programas, Sedes, Num_Programas |
| 10_Asignaturas_Similares | Pares similares | Programa_A, Asignatura_A, Programa_B, Asignatura_B, Similitud, Categoría, Recomendación |
| 11_Bloques_Curriculares | Conteo por bloque | Programa, B.Institucional, B.Disciplinar, B.Electivo, Total |
| 12_Carga_Horaria | Horas por semestre | Programa, Semestre, HTD, HTI, Total_Horas |
| 13_Bloom_Distribucion | Niveles Bloom | Programa, Básico%, Intermedio%, Avanzado%, Nivel_Promedio |
| 14_Tematicas_Emergentes | Cobertura de temáticas | Programa, Sostenibilidad%, IA%, RSE%, ..., Gestión_Cambio% |
| 15_Alertas_y_Recomendaciones | Alertas automáticas | Programa, Tipo_Alerta, Descripción, Recomendación |

---

## 13. Dashboard Interactivo

**Archivo:** `dashboard_tematico.py` (~4500 líneas)  
**Framework:** Streamlit 1.30+ con `streamlit-option-menu`

### 13.1 Arquitectura del Dashboard

El dashboard es una aplicación web de una sola página (SPA) con navegación lateral. Todos los datos se cargan en memoria y se cachean en `st.session_state` para evitar reprocesamiento en cada interacción.

### 13.2 Sistema de Carga y Caché

1. El usuario arrastra archivos Excel en la página de Inicio
2. `procesar_archivos()` extrae y consolida datos de todos los archivos
3. Los resultados se guardan en `st.session_state` con clave de caché basada en nombres de archivo
4. Los filtros (programa, modalidad, sede, nivel) producen un `df_filtered` que se pasa a todas las páginas

### 13.3 Las 10 Páginas

#### 13.3.1 Inicio (`pagina_inicio`)

**Contenido:**
- Tarjetas de acceso rápido a cada funcionalidad
- Métricas globales: programas cargados, score promedio, asignaturas, registros
- Gráfico de radar con los 6 indicadores de calidad
- Box plot de distribución de scores
- Top/Bottom 5 programas por score
- KPIs por programa (competencias, RA, créditos, núcleos, tendencias)
- Barras por modalidad y sede

**Carga:** Solo requiere la carga inicial de archivos.

#### 13.3.2 Tipo de Saber (`pagina_tipo_saber`)

**Contenido:**
- Distribución Saber/SaberHacer/SaberSer por programa (barras apiladas)
- Línea de referencia 40% SaberHacer y 10% SaberSer
- Desglose por semestre (mapa de calor)
- Tabla detallada con porcentajes

**Lógica:** Agrupa por programa y por semestre, cuenta ocurrencias de cada tipo en `Tipo de Saber`, calcula porcentajes.

#### 13.3.3 Cobertura de Perfil (`pagina_cobertura_perfil`)

**Contenido:**
- Resumen global: programas con/sin perfil, cobertura promedio, brechas totales
- Por programa: tabla de elementos con score TF-IDF, umbral, clasificación (CUBIERTO/BRECHA), trazabilidad
- Recomendaciones automáticas
- Gráfico comparativo de cobertura entre programas (barras con semáforo Rojo-Amarillo-Verde)
- Barras agrupadas cubiertos vs. brechas

**Carga:** Lee hoja Paso1 y Paso3 de cada archivo, ejecuta `analizar_cobertura_perfil_completa` por programa, cachea resultados por firma MD5 de nombres de archivo.

#### 13.3.4 Cobertura Temática (`pagina_cobertura`)

**Contenido:**
- Panel de revisión y exclusión de núcleos (multiselect, cambios en tiempo real)
- Métricas: núcleos únicos, total menciones, promedio por asignatura, diversidad (entropía de Shannon normalizada)
- Matriz de presencia de núcleos por programa (top 20, heatmap)
- Top 20 núcleos más frecuentes (barras)
- Top 20 asignaturas con más núcleos (densidad)
- Explorador por programa

**Fórmula de diversidad:**
```
H = -Σ p_i × log₂(p_i)           # Entropía de Shannon
diversidad = H / log₂(n) × 100   # Normalizada a 0–100
```
donde `p_i` = frecuencia relativa del núcleo `i` y `n` = núcleos únicos.

#### 13.3.5 Tendencias Globales (`pagina_tendencias`)

**Contenido:**
- Barras de cobertura por temática para el conjunto filtrado
- Selector de programa para vista detallada
- Radar de temáticas por programa
- Tabla detallada: cada fila = keyword encontrado, columna = campo donde se encontró (núcleos / indicadores / actividades)
- Configuración cargada desde `config_tendencias.json`

**Lógica:** Búsqueda case-insensitive de keywords en 3 campos, conteo de asignaturas únicas que mencionan cada temática.

#### 13.3.6 Minería de Texto (`pagina_nlp`)

**Contenido:**
- Top 30 términos TF-IDF globales
- Bigramas y trigramas más frecuentes
- Per-programa: top 20 términos, nube de keywords
- Matriz de similitud entre asignaturas (heatmap)
- Par de asignaturas más similares

**Lógica TF-IDF:** `TfidfVectorizer(max_features=50, stop_words=STOPWORDS_ES)` sobre `Texto_Completo` (columna que concatena RA + indicadores + núcleos + actividades).

#### 13.3.7 Bloom & Integración (`pagina_bloom_integracion`)

**Contenido:**
- Distribución de niveles Bloom por programa (barras)
- Nivel Bloom promedio
- Clasificación en bandas: Básico/Intermedio/Avanzado
- Gráfico Sankey: integración entre temáticas (tendencias) y niveles Bloom

**Lógica del Sankey:** Para cada combinación (temática, nivel Bloom), cuenta asignaturas donde ambos coinciden. El ancho de los vínculos es proporcional al conteo.

#### 13.3.8 Familias Curriculares (`pagina_familias_curriculares`)

**Contenido:**
- Tabla de asignaturas compartidas entre programas (columna por programa, marca "X")
- Mapa de calor asignatura × programa
- Histograma de asignaturas por cantidad de programas que las comparten
- Métrica de asignaturas compartidas totales

**Lógica:** Agrupa por nombre de asignatura, filtra `nunique(Programa) > 1`, construye matriz pivote.

#### 13.3.9 Configurar Tendencias (`pagina_config_tendencias`)

**Contenido:**
- Editor visual para las 10 tendencias: nombre, descripción, color, keywords
- Importar configuración desde JSON
- Exportar configuración a JSON
- Guardar en `config_tendencias.json`

#### 13.3.10 Explorar Datos (`pagina_datos`)

**Contenido:**
- Visor de datos crudos con columnas seleccionables
- Filtros: programa, tipo de saber, campo de texto
- Tabla paginada (10, 25, 50, 100 filas)
- Estadísticas de columnas seleccionadas

### 13.4 Filtros Globales

Todas las páginas reciben `df_filtered`, que es el DataFrame filtrado por:
- **Programa** (sidebar): Todos o uno específico
- **Modalidad**: Presencial, Virtual, Híbrido
- **Sede**: Bogotá, Medellín, Nacional
- **Nivel**: Pregrado, Posgrado

Los filtros se aplican en el `main()` antes de despachar a cada página.

### 13.5 Navegación

```python
pagina = option_menu(
    menu_title=None,
    options=list(PAGINAS.keys()),
    icons=[v[0] for v in PAGINAS.values()],
    default_index=0,
)
```

Las páginas se renderizan mediante una cadena `if-elif`. Cada página recibe `df_filtered` y, cuando requiere cómputo intensivo, usa `st.spinner()` para feedback de carga.

---

## 14. Orquestación del Pipeline (run_analysis.py)

**Archivo:** `run_analysis.py` (~280 líneas)

### 14.1 Flujo de Ejecución

```
main()
│
├─ print_header()
├─ Crear directorios de salida
├─ Buscar archivos Excel en INPUT_FOLDER
│
├─ Inicializar ThematicDetector y ReportGenerator
│
├─ Por cada archivo (process_single_program):
│   ├─ 1. ExcelExtractor.extract_all()
│   ├─ 2. validate_structure()
│   ├─ 3. CurricularAnalyzer.generar_reporte_indicadores()
│   ├─ 4. ThematicDetector.analyze_programa()
│   ├─ 5. QualityValidator.validate_programa_completo()
│   ├─ 6. analizar_cobertura_perfil_completa(df_perfil, df_micro, df_ra)
│   ├─ 7. generate_html_report()
│   └─ 8. generate_json_report()
│
├─ Consolidar resultados:
│   ├─ Matriz de temáticas (Programas × Temáticas)
│   ├─ Excel consolidado de indicadores
│   ├─ Resumen de temáticas
│   ├─ Excel maestro (15 hojas)
│   ├─ Asignaturas compartidas (todas las estrategias micro)
│   └─ Topic modeling LDA (todos los SaberAsociado)
│
└─ Resumen final: scores, top 5, errores
```

### 14.2 Manejo de Errores

- Cada archivo se procesa en un bloque `try/except`
- Si falla, se registra el error y se continúa con el siguiente
- Al final, se reporta el número de programas exitosos vs. fallidos
- Un archivo con solo errores estructurales (no fatales) se procesa parcialmente

### 14.3 Output Files

| Archivo | Ruta | Generado cuando |
|---------|------|-----------------|
| Reporte HTML | `output/reportes/reporte_[programa].html` | Por programa |
| Reporte JSON | `output/reportes/reporte_[programa].json` | Por programa |
| Matriz temáticas | `output/matrices/matriz_tematicas.xlsx` | Todos procesados |
| Indicadores consolidados | `output/consolidado/indicadores_consolidados.xlsx` | Todos procesados |
| Excel maestro | `output/consolidado/excel_maestro.xlsx` | Todos procesados |
| Log | `logs/analisis_[fecha].log` | Por ejecución |

---

## 15. Resultados y Validación

### 15.1 Pruebas Unitarias (13 tests)

| Archivo | Tests | Cobertura |
|---------|-------|-----------|
| `test_nuevos_modulos.py` | 5 | nucleos_cleaner (5 funciones), perfil_coverage (pipeline completo), shared_subjects (con DataFrame 3 filas), topic_modeler (LDA con 6 docs), report_generator (instanciación) |
| `test_thematic_detector.py` | 8 | inicialización, detección de 2 temáticas (Sostenibilidad, IA), detección en texto vacío, normalización, extracción de contexto, múltiples keywords, DataFrame completo |

### 15.2 Test de Integración (12 checks)

`test_integracion.py` procesa 3 archivos Excel reales en 5 fases:

1. **Extracción** (3 checks): cada archivo debe cargarse sin errores, tener metadatos válidos
2. **Núcleos** (4 checks): `es_nucleo_valido` con casos válidos e inválidos
3. **Cobertura de perfil** (3 checks): cobertura_global, brechas, recomendaciones
4. **Asignaturas compartidas** (1 check): detecta pares entre combinaciones de 2+ programas
5. **Tópicos LDA** (1 check): entrena con 3 tópicos y verifica estructura de salida

### 15.3 Resultados de Prueba con 99 Programas

En una ejecución real con 99 programas académicos:

| Métrica | Valor |
|---------|-------|
| Programas procesados | 99/99 |
| Tamaño Excel maestro | 905 KB |
| Asignaturas compartidas intra-sede | 16 pares |
| Asignaturas compartidas inter-programa | 661 pares |
| Pipeline completo | ~3 minutos |
| Tests | 13/13 pasan |

### 15.4 Thresholds y Aceptación

| Criterio | Estándar | Verificado |
|----------|----------|------------|
| Pipeline < 5 min | ✓ | ~3 min con 99 programas |
| Tasa de rechazo núcleos 5-25% | ✓ | Dentro del rango |
| Excel maestro < 10 MB | ✓ | 905 KB |
| "Expansión A/B" → rechazado | ✓ | Filtro 7 |
| "Análisis financiero" → aceptado | ✓ | Pasa los 7 filtros |
| "Fundamentación teórica" → aceptado | ✓ | Pasa los 7 filtros |

---

## 16. Configuración Centralizada (config.py)

**Archivo:** `config.py` (~500 líneas)

### 16.1 Propósito

Centraliza todos los parámetros ajustables del sistema en un solo punto, evitando valores hardcodeados en los módulos.

### 16.2 Constantes de Rutas

| Constante | Valor por defecto |
|-----------|-------------------|
| `BASE_DIR` | Directorio raíz del proyecto (autodetectado) |
| `INPUT_FOLDER` | `BASE_DIR / "data" / "raw"` |
| `OUTPUT_FOLDER` | `BASE_DIR / "data" / "output"` |
| `PROCESSED_FOLDER` | `BASE_DIR / "data" / "processed"` |
| `TEMPLATES_DIR` | `BASE_DIR / "templates"` |
| `DB_PATH` | `BASE_DIR / "data" / "microcurricular.db"` |

### 16.3 Constantes de Estructura Excel

| Constante | Propósito |
|-----------|-----------|
| `EXCEL_SHEETS` | Mapeo de nombres lógicos a nombres reales de hojas |
| `HEADER_ROWS` | Fila de encabezado (0-indexed) para cada hoja |
| `EXPECTED_COLUMNS` | Lista de columnas esperadas por hoja |

### 16.4 Constantes de Temáticas

`TEMATICAS`: diccionario con 10 entradas, cada una con `keywords` y `contexto_keywords`.

### 16.5 Constantes de Taxonomía

| Constante | Propósito |
|-----------|-----------|
| `TAXONOMIA_BLOOM` | 6 niveles con listas de verbos |
| `TIPOS_SABER` | `['Saber', 'SaberHacer', 'SaberSer']` |
| `COMPLEJIDAD_THRESHOLDS` | Rangos para Básico/Intermedio/Avanzado |
| `BALANCE_IDEAL_SABER` | Porcentajes ideales (33.3% cada uno) |

### 16.6 Constantes de Núcleos

```python
NUCLEOS_CONFIG = {
    'MIN_LONGITUD': 4,
    'MAX_LONGITUD': 150,
    'MIN_PALABRAS': 2,
    'CONTAMINATION_IF': 0.15,
    'UMBRAL_SCORE_ACADEMICO': 0.5,
    'USE_SPACY': False,
    'SPACY_MODEL': 'es_core_news_sm',
}
```

### 16.7 Constantes de Cobertura de Perfil

| Constante | Propósito |
|-----------|-----------|
| `UMBRAL_COBERTURA` | Umbral global de similitud (0.35) |
| `UMBRALES_POR_CAMPO` | Umbrales específicos por campo (9 campos) |
| `COLUMNAS_PERFIL` | Columnas del perfil a analizar (9 campos) |

### 16.8 Constantes de Calidad

```python
QUALITY_WEIGHTS = {
    'completitud': 0.25,
    'complejidad_cognitiva': 0.20,
    'balance_tipo_saber': 0.15,
    'diversidad_metodologica': 0.15,
    'cobertura_competencias': 0.15,
    'calidad_redaccion': 0.10
}
```

### 16.9 Constantes Generales

`CONFIG` agrupa: logging, procesamiento paralelo, exportación, LLM, caché, validación, dashboard, reportes.

### 16.10 Validación Automática

Al importar `config.py`, se ejecuta `validate_config()` que verifica:
- Pesos de calidad suman 1.0 (±0.01)
- Directorios requeridos existen

Si hay errores, se imprime advertencia pero no se interrumpe la ejecución.

---

## Referencias

1. Blei, D. M., Ng, A. Y., & Jordan, M. I. (2003). Latent Dirichlet Allocation. *Journal of Machine Learning Research*, 3, 993–1022.
2. Robertson, S. E., & Walker, S. (1994). Some simple effective approximations to the 2-Poisson model for probabilistic weighted retrieval. *SIGIR '94*, 232–241.
3. Shannon, C. E. (1948). A mathematical theory of communication. *Bell System Technical Journal*, 27(3), 379–423.
4. Liu, F. T., Ting, K. M., & Zhou, Z. H. (2008). Isolation Forest. *ICDM '08*, 413–422.
5. Anderson, L. W., & Krathwohl, D. R. (2001). *A taxonomy for learning, teaching, and assessing: A revision of Bloom's taxonomy of educational objectives*. Longman.
6. Pedregosa, F., et al. (2011). Scikit-learn: Machine Learning in Python. *Journal of Machine Learning Research*, 12, 2825–2830.
7. Jaccard, P. (1901). Étude comparative de la distribution florale dans une portion des Alpes et du Jura. *Bulletin de la Société Vaudoise des Sciences Naturelles*, 37, 547–579.
8. Salton, G., & Buckley, C. (1988). Term-weighting approaches in automatic text retrieval. *Information Processing & Management*, 24(5), 513–523.

---

*Documento generado a partir del código fuente v2.0. Todos los parámetros, umbrales y pesos son los valores actuales en producción.*
