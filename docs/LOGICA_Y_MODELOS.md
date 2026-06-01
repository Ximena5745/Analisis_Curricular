# Lógica del Sistema, Modelos y Fuentes de Información

**Proyecto:** Sistema de Análisis Microcurricular  
**Versión:** 1.0.0  
**Fecha:** Mayo 2026

---

## Tabla de Contenidos

1. [Arquitectura Lógica del Sistema](#1-arquitectura-lógica-del-sistema)
2. [Pipeline de Procesamiento Detallado](#2-pipeline-de-procesamiento-detallado)
3. [Modelos de Machine Learning y Técnicas Analíticas](#3-modelos-de-machine-learning-y-técnicas-analíticas)
4. [Modelos de Datos](#4-modelos-de-datos)
5. [Fuentes de Información](#5-fuentes-de-información)
6. [Respuestas y Salidas del Sistema](#6-respuestas-y-salidas-del-sistema)
7. [Indicadores y Fórmulas Matemáticas](#7-indicadores-y-fórmulas-matemáticas)
8. [Flujo de Datos Completo](#8-flujo-de-datos-completo)
9. [Configuración y Parametrización](#9-configuración-y-parametrización)

---

## 1. Arquitectura Lógica del Sistema

### 1.1 Diagrama de Capas

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                           CAPA DE PRESENTACIÓN                               │
│  ┌─────────────────────────────────────────┐  ┌───────────────────────────┐  │
│  │       Dashboard Modular (app.py)        │  │  Dashboard Temático       │  │
│  │  ┌─────┐ ┌───────┐ ┌──────┐ ┌───────┐  │  │  Avanzado                │  │
│  │  │Home │ │Progs  │ │Temas │ │Compar │  │  │  (dashboard_tematico.py)  │  │
│  │  └─────┘ └───────┘ └──────┘ └───────┘  │  └───────────────────────────┘  │
│  └─────────────────────────────────────────┘                                │
├──────────────────────────────────────────────────────────────────────────────┤
│                           CAPA DE NEGOCIO                                    │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐       │
│  │  Extractor   │ │  Analyzer    │ │  Thematic    │ │  Validator   │       │
│  │  (carga y    │ │  (indicado-  │ │  Detector    │ │  (estructura │       │
│  │  normaliza)  │ │  res)        │ │  (keywords)  │ │  y redacción)│       │
│  └──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘       │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │              Report Generator (HTML, JSON, Excel, PDF)                │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
├──────────────────────────────────────────────────────────────────────────────┤
│                      CAPA DE ML Y ANALÍTICA                                  │
│  ┌──────────┐ ┌────────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────┐   │
│  │ TF-IDF   │ │ Coseno     │ │Clustering│ │Entropía  │ │CountVect.   │   │
│  │ Vectorizer│ │Similitud   │ │Aglo.     │ │Shannon   │ │N-gramas     │   │
│  └──────────┘ └────────────┘ └──────────┘ └──────────┘ └──────────────┘   │
├──────────────────────────────────────────────────────────────────────────────┤
│                           CAPA DE DATOS                                      │
│  ┌────────────────────┐ ┌──────────────────┐ ┌────────────────────────┐    │
│  │  Excel Files (raw) │ │  DataFrames      │ │  Output Files         │    │
│  │  7 hojas c/u       │ │  (pandas)        │ │  HTML, JSON, Excel    │    │
│  └────────────────────┘ └──────────────────┘ └────────────────────────┘    │
└──────────────────────────────────────────────────────────────────────────────┘
```

### 1.2 Flujo de Control

```
[Usuario] 
    │
    ├─ python validate_files.py ────────────────────┐
    │   └─ ExcelExtractor.validate_structure()       │
    │       └─ Verifica: hojas, headers, columnas    │
    │                                                │
    ├─ python run_analysis.py ───────────────────────┤
    │   ├─ ExcelExtractor.extract_all()              │
    │   │   ├─ extract_competencias()                │
    │   │   ├─ extract_resultados_aprendizaje()      │
    │   │   ├─ extract_estrategias_meso()            │
    │   │   └─ extract_estrategias_micro()           │
    │   ├─ CurricularAnalyzer.generar_reporte()      │
    │   │   ├─ calcular_balance_tipo_saber()         │
    │   │   ├─ calcular_complejidad_cognitiva()      │
    │   │   ├─ calcular_cobertura_competencias()     │
    │   │   ├─ calcular_diversidad_metodologica()    │
    │   │   └─ calcular_completitud()                │
    │   ├─ ThematicDetector.analyze_programa()       │
    │   │   └─ detect_in_dataframe() en cada sección │
    │   ├─ QualityValidator.validate_programa()      │
    │   └─ ReportGenerator (HTML, JSON, Excel)       │
    │                                                │
    ├─ streamlit run dashboard/app.py ───────────────┤
    │   ├─ load_all_programs() → caché               │
    │   ├─ Páginas: Inicio, Programas, Temáticas,    │
    │   │           Comparativa, Estrategias Micro   │
    │   └─ Filtros: Modalidad, Sede, Nivel           │
    │                                                │
    └─ streamlit run dashboard_tematico.py ──────────┤
        ├─ procesar_archivos() → DataFrame unificado │
        ├─ analizar_cobertura() (núcleos, entropía)   │
        ├─ analizar_tendencias() (10 tendencias)      │
        ├─ analizar_nlp() (TF-IDF, n-gramas)         │
        └─ Páginas: Inicio, Cobertura, Tendencias,   │
                    NLP, Bloom, Similitud             │
```

---

## 2. Pipeline de Procesamiento Detallado

### 2.1 Fase 1: Validación de Archivos

**Input:** Archivos Excel en `data/raw/`  
**Output:** `{'valid': bool, 'errors': List[str], 'warnings': List[str], 'info': Dict}`

**Lógica (`extractor.py:397-465`):**
1. Verificar existencia de hojas requeridas (`Paso 2 Redacción competen`, `Paso 3 Redacción RA`)
2. Verificar existencia de hojas opcionales (`Paso 4 Estrategias mesocurricu`, `Paso 5 Estrategias micro`)
3. Intentar extraer competencias → si falla, agregar error
4. Intentar extraer RA → si falla, agregar error
5. Si hay errores → `valid = False`

### 2.2 Fase 2: Extracción de Datos

**Input:** Ruta a archivo Excel  
**Output:** Dict con metadata + 4 DataFrames

**Lógica de extracción de competencias (`extractor.py:229-263`):**
1. Obtener nombre de hoja desde `EXCEL_SHEETS['COMPETENCIAS']`
2. Leer hoja con pandas, usando `header_row` preconfigurado (fila 2, índice 1)
3. Si no se encuentra header, usar detección automática (`_find_header_row`):
   - Buscar en primeras 10 filas la que tenga más coincidencias con columnas esperadas
   - Score mínimo requerido: 50% de columnas esperadas
4. Limpiar columnas `Unnamed` y filas vacías
5. Agregar columnas `Programa`, `Archivo`

**Detección de header (`extractor.py:132-175`):**
```python
for row_idx in range(max_rows):  # max_rows = 10
    row_values = [cell.value for cell in sheet[row_idx + 1]]
    row_normalized = [normalize(v) for v in row_values]
    score = sum(1 for exp in expected_normalized if exp in row_normalized)
    if score > best_score:
        best_score = score
        best_match = row_idx
# Requiere score >= 50% de columnas esperadas
```

**Normalización de nombres de columna (`extractor.py:95-130`):**
- Convertir a minúsculas
- Remover tildes (á→a, é→e, etc.)
- Remover caracteres especiales (solo a-z, 0-9, espacios)
- Comprimir espacios múltiples

### 2.3 Fase 3: Análisis de Indicadores

**Input:** Dict de `extract_all()`  
**Output:** Dict con 7 grupos de indicadores

**Balance de tipos de saber (`analyzer.py:76-123`):**
```
Para cada tipo en [Saber, SaberHacer, SaberSer]:
    porcentaje = (count / total_RA) * 100
desviacion = np.std([p_Saber, p_SaberHacer, p_SaberSer])
balanceado = desviacion < 10.0
```

**Complejidad cognitiva (`analyzer.py:246-302`):**
```
Para cada RA:
    nivel = buscar verbo en TAXONOMIA_BLOOM (6 niveles)
    si no encontrado: inferir desde nivel_dominio
    si no: default = 2
    
Clasificar:
    Básico    = niveles 1-2 (Recordar, Comprender)
    Intermedio = niveles 3-4 (Aplicar, Analizar)
    Avanzado   = niveles 5-6 (Evaluar, Crear)

índice_complejidad = ((nivel_promedio - 1) / 5) * 100
```

**Diversidad metodológica (`analyzer.py:347-420`):**
```
keywords_buscar = [clase magistral, taller, laboratorio, caso, ...]
para cada texto en columna Estrategias:
    para cada keyword:
        si keyword in texto_lower: contar

% metodologías_activas = activas / total * 100
metodologías_activas = [Taller, Laboratorio, Caso, Problema, Proyecto, Simulación, Debate]
```

**Completitud (`analyzer.py:422-468`):**
```
completitud_df = filled_cells / total_cells * 100
completitud_total = comp(30%) + RA(40%) + meso(15%) + micro(15%)
```

**Score de calidad (`analyzer.py:470-507`):**
```
score_completitud  = completitud_total              (peso 25%)
score_complejidad  = indice_complejidad             (peso 20%)
score_balance      = 100 - desviacion * 5           (peso 15%)
score_cobertura    = % cobertura                    (peso 15%)
score_diversidad   = min(100, num_estrategias * 8)  (peso 15%)
score_redaccion    = 80.0 (placeholder)             (peso 10%)

score_total = Σ(score_i * peso_i)
```

### 2.4 Fase 4: Detección de Temáticas

**Input:** Dict de `extract_all()`  
**Output:** Dict con presencia de 10 temáticas

**Lógica (`thematic_detector.py:261-422`):**
1. Para competencias: `detect_in_dataframe(columna='Redacción competencia')`
2. Para RA: `detect_in_dataframe(columna='Resultados Aprendizaje')`
3. Para estrategias micro: `detect_in_dataframe(columnas=['Actividades de aprendizaje', ...])`
4. Para cada temática, contar frecuencia en cada sección
5. Normalizar por créditos: `por_creditos = total_coincidencias / creditos_totales * 10`
6. Generar matriz Programas × Temáticas

**Detección individual (`thematic_detector.py:131-205`):**
```python
text_normalized = normalize(texto)  # minúsculas, sin tildes
for tematica, config in TEMATICAS.items():
    for keyword in config['keywords']:
        pattern = r'\b' + re.escape(keyword_normalized) + r'\w*'
        matches = re.findall(pattern, text_normalized)
        # match como palabra completa o con sufijos
```

### 2.5 Fase 5: Validación de Calidad

**Input:** Dict de `extract_all()` o string individual  
**Output:** Dict con issues, suggestions, score

**Estructura de competencia (`validator.py:48-131`):**
```
1. ¿Tiene verbo taxonómico? (Bloom list)
2. ¿Longitud ≥ 5 palabras? (objeto conceptual)
3. ¿Tiene finalidad? ("para", "con el fin de")
4. ¿Tiene condición de contexto? ("en contexto", "considerando")
5. ¿Demasiado larga? (>50 palabras → warning)
   Válida si issues ≤ 1
```

**Coherencia verbo-nivel (`validator.py:133-197`):**
```
nivel_verbo = buscar verbo en TAXONOMIA_BLOOM
nivel_declarado = inferir desde nivel_dominio string
coherente = nivel_verbo == nivel_declarado
```

**RA medible (`validator.py:199-248`):**
```
tiene_verbo_observable = verbo in verbos_taxonomicos
tiene_verbo_no_observable = [saber, conocer, entender, aprender] in primeras 3 palabras
observable = tiene_verbo_observable AND NOT tiene_verbo_no_observable
```

### 2.6 Fase 6: Generación de Reportes

**HTML (`report_generator.py:78-279`):**
- Template con CSS embebido (Segoe UI, paleta #3498db)
- Métricas: score, competencias, RA, estrategias
- Barras de progreso para tipos de saber
- Tabla de competencias
- Footer automático

**JSON (`report_generator.py:320-367`):**
```json
{
  "programa": "...",
  "fecha_generacion": "ISO datetime",
  "archivo_origen": "...",
  "indicadores": { ... },
  "tematicas": {
    "presentes": ["SOSTENIBILIDAD", ...],
    "num_tematicas": 3,
    "resumen": { ... }
  },
  "resumen": {
    "total_competencias": 5,
    "total_ra": 13,
    "total_estrategias_micro": 45
  }
}
```

**Excel consolidado (`report_generator.py:369-412`):**
- Columnas: Programa, Score_Calidad, Total_Competencias, Total_RA, Saber_%, SaberHacer_%, SaberSer_%, Complejidad_%, Indice_Complejidad, Completitud_%

---

## 3. Modelos de Machine Learning y Técnicas Analíticas

### 3.1 TF-IDF Vectorizer

**Ubicación:** `dashboard_tematico.py:1148-1151`  
**Librería:** `sklearn.feature_extraction.text.TfidfVectorizer`

**Parametrización:**

| Parámetro | Valor | Justificación |
|-----------|-------|---------------|
| `max_features` | 100 | Limita a los 100 términos más relevantes del corpus |
| `min_df` | 2 | Ignora términos que aparecen en menos de 2 documentos (elimina ruido) |
| `max_df` | 0.8 | Ignora términos que aparecen en >80% de documentos (elimina stopwords) |
| `stop_words` | Lista personalizada ~60 palabras | Stopwords en español específicas del dominio curricular |
| `ngram_range` | (1, 3) | Captura términos individuales, bigramas y trigramas (frases curriculares) |

**Uso en el sistema:**
```python
vectorizer = TfidfVectorizer(
    max_features=100, min_df=2, max_df=0.8,
    stop_words=list(STOPWORDS_ES), ngram_range=(1, 3)
)
tfidf_matrix = vectorizer.fit_transform(df['Texto_Completo'])
features = vectorizer.get_feature_names_out()
tfidf_sum = tfidf_matrix.sum(axis=0).A1
top_idx = tfidf_sum.argsort()[::-1][:30]
top_terminos = {features[i]: float(tfidf_sum[i]) for i in top_idx}
```

**Aplicaciones:**
1. Extracción de top-30 términos más relevantes del corpus curricular
2. Generación de top-20 términos por programa individual
3. Entrada para similitud coseno entre programas/asignaturas

### 3.2 TF-IDF por Programa (Instancia Independiente)

**Ubicación:** `dashboard_tematico.py:1158-1175`

Se crea un vectorizador independiente por cada programa:

```python
vec_p = TfidfVectorizer(
    max_features=50, min_df=2, max_df=0.85,
    stop_words=list(STOPWORDS_ES), ngram_range=(1, 2)
)
```

**Diferencias con el global:**
- `max_features=50` (menos términos por programa)
- `max_df=0.85` (más permisivo con términos frecuentes)
- `ngram_range=(1, 2)` (solo unigramas y bigramas)

### 3.3 Similitud Coseno

**Ubicación:** `dashboard_tematico.py:1200-1230`, `dashboard/app.py:848-888`  
**Librería:** `sklearn.metrics.pairwise.cosine_similarity`

**Fórmula:**
```
sim(A, B) = (A · B) / (||A|| × ||B||)
```

**Parametrización entre programas (`app.py:873-876`):**
```python
vectorizer = TfidfVectorizer(max_features=100, stop_words='spanish')
tfidf = vectorizer.fit_transform(similitud_data)
sim_matrix = cosine_similarity(tfidf)
similitud = float(sim_matrix[0][1])
```

**Parametrización entre asignaturas (`dashboard_tematico.py:1210-1212`):**
```python
vec_asig = TfidfVectorizer(max_features=50, stop_words=list(STOPWORDS_ES))
tfidf_asig = vec_asig.fit_transform(df_asig['Texto_Completo'])
sim = cosine_similarity(tfidf_asig)
similitud_df = pd.DataFrame(sim, index=..., columns=...)
```

**Salida:** Matriz N×N de similitud + par más similar (excluyendo diagonal)

### 3.4 Clustering Aglomerativo

**Ubicación:** `dashboard_tematico.py` (importado en línea 23)  
**Librería:** `sklearn.cluster.AgglomerativeClustering`

**Disponible pero no invocado directamente en flujo principal.** El clustering jerárquico está importado para uso futuro o análisis exploratorio. Agruparía programas según su perfil multidimensional de indicadores.

### 3.5 Entropía de Shannon

**Ubicación:** `dashboard_tematico.py:1043-1052`  
**Librería:** `scipy.stats.entropy`

**Fórmula:**
```
H = -Σ p(x) · log₂(p(x))
diversidad = (H / log₂(N)) × 100
```

Donde:
- `p(x)` = frecuencia relativa de cada núcleo temático
- `N` = número de núcleos únicos
- `diversidad` = normalizado a escala 0-100

**Uso:**
```python
frecuencias = np.array(list(nucleos_counter.values()))
probabilidades = frecuencias / frecuencias.sum()
shannon = entropy(probabilidades, base=2)
max_ent = np.log2(len(nucleos_counter))
diversidad = (shannon / max_ent) * 100
```

**Interpretación:**
- 100 = máxima diversidad (todos los núcleos con igual frecuencia)
- 0 = mínima diversidad (un solo núcleo domina)

### 3.6 Count Vectorizer (N-gramas)

**Ubicación:** `dashboard_tematico.py:1178-1191`  
**Librería:** `sklearn.feature_extraction.text.CountVectorizer`

**Parametrización:**

| Parámetro | Valor |
|-----------|-------|
| `ngram_range` | (2, 3) |
| `max_features` | 30 |
| `stop_words` | Lista personalizada ~60 palabras |
| `min_df` | 2 |

**Uso:**
```python
vec_ng = CountVectorizer(
    ngram_range=(2, 3), max_features=30,
    stop_words=list(STOPWORDS_ES), min_df=2
)
ng_matrix = vec_ng.fit_transform(df['Texto_Completo'])
ng_count = ng_matrix.sum(axis=0).A1
ng_names = vec_ng.get_feature_names_out()
top_ngrams = sorted(
    [(ng_names[i], int(ng_count[i])) for i in range(len(ng_names))],
    key=lambda x: x[1], reverse=True
)[:20]
```

**Propósito:** Identificar frases curriculares recurrentes de 2-3 palabras (ej: "aprendizaje basado en problemas", "pensamiento crítico")

### 3.7 Detección por Keywords (Sistema Basado en Reglas)

**Ubicación:** `src/thematic_detector.py`  
**No es ML supervisado** — es un sistema de reglas con diccionarios de keywords.

**Estructura de cada temática:**
```python
'SOSTENIBILIDAD': {
    'keywords': [
        'sostenibilidad', 'sostenible', 'desarrollo sostenible',
        'ODS', 'medio ambiente', 'ambiental', 'cambio climático', ...
    ],
    'contexto_keywords': [
        'dimensiones económicas, ambientales y sociales',
        'triple línea de base', ...
    ]
}
```

**Lógica de matching:**
```python
pattern = r'\b' + re.escape(keyword_normalized) + r'\w*'
matches = re.findall(pattern, text_normalized)
```

**10 temáticas configuradas:**
1. SOSTENIBILIDAD (~15 keywords)
2. INTELIGENCIA ARTIFICIAL (~15 keywords)
3. RESPONSABILIDAD SOCIAL EMPRESARIAL (~13 keywords)
4. TRANSFORMACIÓN DIGITAL (~15 keywords)
5. INNOVACIÓN Y EMPRENDIMIENTO (~14 keywords)
6. GLOBALIZACIÓN Y PERSPECTIVA GLOCAL (~14 keywords)
7. ÉTICA Y VALORES (~14 keywords)
8. LIDERAZGO Y HABILIDADES BLANDAS (~15 keywords)
9. ANÁLISIS DE DATOS (~14 keywords)
10. GESTIÓN DEL CAMBIO (~10 keywords)

**Total aproximado: ~139 keywords**

### 3.8 Taxonomía de Bloom (Clasificación Determinística)

**Ubicación:** `config.py:246-277`, `analyzer.py:125-163`

**Estructura:**
```python
TAXONOMIA_BLOOM = {
    'RECORDAR':  {'nivel': 1, 'verbos': ['definir', 'listar', ...]},
    'COMPRENDER': {'nivel': 2, 'verbos': ['explicar', 'describir', ...]},
    'APLICAR':   {'nivel': 3, 'verbos': ['aplicar', 'ejecutar', ...]},
    'ANALIZAR':  {'nivel': 4, 'verbos': ['analizar', 'diferenciar', ...]},
    'EVALUAR':   {'nivel': 5, 'verbos': ['evaluar', 'criticar', ...]},
    'CREAR':     {'nivel': 6, 'verbos': ['crear', 'diseñar', ...]}
}
```

**54 verbos en total** (9 por nivel).

**Lógica de clasificación (`analyzer.py:125-163`):**
1. Buscar verbo exacto en diccionario de Bloom
2. Si no encontrado, inferir desde `nivel_dominio` (coincidencia de substring):
   - "analisis" o "analis" → nivel 4
   - "evalua" o "critica" → nivel 5
   - "crea" o "diseña" → nivel 6
   - "aplic" → nivel 3
   - "comprend" o "entiend" → nivel 2
3. Default: nivel 2

### 3.9 Clasificación por Dominio (Taxonomías Extendidas)

**Ubicación:** `dashboard_tematico.py:700-768`

Desde `Taxonomias_MatrizBD.xlsx` (hoja "Verbos"):

**15 subcategorías → 3 dominios:**

| Dominio | Subcategorías |
|---------|--------------|
| **Cognitivo** | Conocimiento, Comprensión, Aplicación, Análisis, Síntesis, Evaluación, Creación |
| **Procedimental** | Imitación, Manipulación, Precisión, Control |
| **Actitudinal** | Percepción, Responder, Valorar, Organizar, Caracterizar |

**Cada subcategoría tiene orden jerárquico (1-15) para priorización.**

**Mapeo a Bloom:**
```python
_SUBCAT_TO_BLOOM = {
    'conocimiento':  'Recordar',
    'comprension':   'Comprender',
    'aplicacion':    'Aplicar',
    'analisis':      'Analizar',
    'sintesis':      'Crear',
    'evaluacion':    'Evaluar',
    'creacion':      'Crear',
    'imitacion':     'Aplicar',
    'manipulacion':  'Aplicar',
    'precision':     'Aplicar',
    'control':       'Evaluar',
    'percepcion':    'Recordar',
    'responder':     'Comprender',
    'valorar':       'Evaluar',
    'organizar':     'Analizar',
    'caracterizar':  'Crear',
}
```

### 3.10 Stemming Simple

**Ubicación:** `dashboard_tematico.py:771-783`

Función de stemming en español basada en reglas (no usa librería externa):

```python
def _stem_es(word: str) -> str:
    w = word.strip().lower()
    for suf in ('ando', 'iendo', 'ados', 'idos', 'ado', 'ido',
                'amos', 'emos', 'imos', 'aron', 'ieron', ...):
        if w.endswith(suf) and len(w) - len(suf) >= 4:
            return w[:-len(suf)]
    return w
```

**Propósito:** Normalizar verbos conjugados para matching con taxonomía.

---

## 4. Modelos de Datos

### 4.1 Modelo de Entrada (ExcelExtractor)

```
ExcelExtractor.extract_all() → Dict
│
├── metadata: Dict
│   ├── programa: str          # Nombre del programa
│   ├── archivo: str           # Nombre del archivo
│   └── ruta: str              # Ruta completa
│
├── competencias: pd.DataFrame
│   ├── No.                    # Número secuencial
│   ├── Verbo competencia      # Verbo principal
│   ├── Objeto conceptual      # Objeto del verbo
│   ├── Finalidad              # Propósito
│   ├── Condición de contexto  # Contexto (opcional)
│   ├── Redacción competencia  # Texto completo
│   ├── Tipo de competencia    # Específica/Genérica
│   ├── Programa               # Metadato agregado
│   └── Archivo                # Metadato agregado
│
├── resultados_aprendizaje: pd.DataFrame
│   ├── Competencia por desarrollar
│   ├── Número de resultado
│   ├── TipoSaber              # Saber/SaberHacer/SaberSer
│   ├── SaberAsociado
│   ├── Taxonomía
│   ├── Dominio Asociado
│   ├── Nivel Dominio
│   ├── Verbo RA
│   ├── Resultados Aprendizaje
│   ├── Programa
│   └── Archivo
│
├── estrategias_meso: pd.DataFrame
│   ├── Resultado de aprendizaje
│   ├── Estrategia del programa
│   ├── Descripción
│   ├── Indicador de Impacto
│   ├── Acciones de retroalimentación
│   ├── Instrumentos de medición
│   ├── Programa
│   └── Archivo
│
└── estrategias_micro: pd.DataFrame
    ├── Tipo de Saber
    ├── Estrategias de enseñanza aprendizaje
    ├── Recursos
    ├── Horas de trabajo autónomo
    ├── Horas de trabajo presencial
    ├── Criterios de evaluación
    ├── Acciones de retroalimentación
    ├── Nivel                        # Pregrado/Posgrado
    ├── Componente académico         # B. Institucional, etc.
    ├── Nombre asignatura o módulo
    ├── Créditos
    ├── Semestre
    ├── Núcleos temáticos
    ├── Indicadores de logro
    ├── Programa
    └── Archivo
```

### 4.2 Modelo de Indicadores (CurricularAnalyzer)

```
generar_reporte_indicadores() → Dict
│
├── programa: str
├── score_calidad: float            # 0-100
│
├── balance_tipo_saber: Dict
│   ├── Saber: float                # %
│   ├── SaberHacer: float           # %
│   ├── SaberSer: float             # %
│   ├── desviacion_estandar: float
│   └── balanceado: bool
│
├── complejidad_cognitiva: Dict
│   ├── Básico: float               # %
│   ├── Intermedio: float           # %
│   ├── Avanzado: float             # %
│   ├── nivel_promedio: float       # 1-6
│   └── indice_complejidad: float   # 0-100
│
├── cobertura_competencias: Dict
│   ├── total_competencias: int
│   ├── competencias_con_ra: int
│   ├── porcentaje_cobertura: float # %
│   └── promedio_ra_por_competencia: float
│
├── diversidad_metodologica: Dict
│   ├── num_estrategias_unicas: int
│   ├── estrategias_mas_frecuentes: List[Tuple[str, int]]
│   └── porcentaje_metodologias_activas: float
│
├── completitud: Dict
│   ├── completitud_competencias: float    # %
│   ├── completitud_ra: float              # %
│   ├── completitud_estrategias_meso: float
│   ├── completitud_estrategias_micro: float
│   └── completitud_total: float           # %
│
└── resumen: Dict
    ├── total_competencias: int
    ├── total_ra: int
    ├── total_estrategias_meso: int
    └── total_estrategias_micro: int
```

### 4.3 Modelo de Temáticas (ThematicDetector)

```
analyze_programa(programa_data) → Dict
│
├── programa: str
├── tematicas_presentes: List[str]      # ["SOSTENIBILIDAD", ...]
├── num_tematicas: int
├── creditos_totales: float
│
├── resumen: Dict[TEMATICA → Dict]
│   ├── presente: bool
│   ├── frecuencia_competencias: int
│   ├── frecuencia_ra: int
│   ├── frecuencia_estrategias: int
│   ├── asignaturas_con_tematica: int
│   ├── total_coincidencias: int
│   └── por_creditos: float             # Normalizado x10 créditos
│
└── detalle: Dict
    ├── competencias: pd.DataFrame      # Con columnas {TEMATICA}_presente
    ├── resultados_aprendizaje: pd.DataFrame
    └── estrategias_micro: pd.DataFrame
```

### 4.4 Modelo del Dashboard Temático (DataFrame Unificado)

```
procesar_archivos() → pd.DataFrame
│
Columnas:
├── Programa                     # Nombre del programa
├── Modalidad                    # Presencial/Virtual/Híbrido
├── Sede                         # Bogotá/Medellín/Nacional
├── Código                       # PBOG, PMED, etc.
├── Nivel                        # Pregrado/Posgrado (detectado)
├── Tipo de Saber                # Saber/SaberHacer/SaberSer (normalizado)
├── Resultado de aprendizaje     # Texto del RA
├── Nombre asignatura o módulo   # Asignatura
├── Indicadores de logro         # Texto
├── Núcleos temáticos            # Separados por ; o \n
├── Créditos                     # Numérico
├── Semestre                     # Numérico
├── Componente académico         # B. Institucional, etc. (detectado)
├── Texto_Completo               # Concatenación de RA + Asignatura + Indicadores + Núcleos
```

### 4.5 Modelo del Dashboard Modular (Programas)

```
load_all_programs() → List[Dict]
│
Cada programa:
├── nombre: str
├── archivo: str
├── modalidad: str
├── sede: str
├── codigo: str
├── nivel: str                    # Pregrado/Posgrado/Mixto
├── componentes_academicos: List[str]
├── data: Dict                    # raw data de extract_all()
├── indicadores: Dict             # de generar_reporte_indicadores()
├── tematicas: Dict               # de analyze_programa()
└── creditos_total: float
```

---

## 5. Fuentes de Información

### 5.1 Fuentes Primarias

| Fuente | Formato | Ubicación | Contenido |
|--------|---------|-----------|-----------|
| Archivos microcurriculares | Excel (.xlsx) | `data/raw/` | 7 hojas por archivo (Perfil Egreso, Competencias, RA, Estrategias Meso, Estrategias Micro, Taxonomías) |
| Matriz de Taxonomías | Excel (.xlsx) | `data/raw/Taxonomias_MatrizBD.xlsx` | Hoja "Verbos" con verbos clasificados por subcategoría y dominio |

### 5.2 Fuentes Configurables

| Archivo | Formato | Propósito |
|---------|---------|-----------|
| `config.py` | Python | Configuración global: rutas, pesos, temáticas, umbrales, logging, LLM |
| `config_tendencias.json` | JSON | Personalización de 10 tendencias globales (keywords, colores, descripciones) |

### 5.3 Fuentes de Conocimiento Interno (Hardcoded)

| Componente | Contenido | Líneas |
|-----------|-----------|--------|
| `TAXONOMIA_BLOOM` | 6 niveles, 54 verbos | `config.py:246-277` |
| `TEMATICAS` | 10 temáticas, ~139 keywords | `config.py:111-239` |
| `TIPOS_SABER` | `['Saber', 'SaberHacer', 'SaberSer']` | `config.py:280` |
| `QUALITY_WEIGHTS` | 6 pesos que suman 1.0 | `config.py:287-294` |
| `COMPLEJIDAD_THRESHOLDS` | Rangos Básico(1-2), Intermedio(3-4), Avanzado(5-6) | `config.py:297-301` |
| `BALANCE_IDEAL_SABER` | ~33% cada tipo | `config.py:304-308` |
| `EXCEL_SHEETS` | Mapeo de nombres de hojas | `config.py:48-56` |
| `EXPECTED_COLUMNS` | Columnas esperadas por hoja | `config.py:67-105` |
| `STOPWORDS_ES` | ~60 stopwords en español | `dashboard_tematico.py:643-653` |
| Paleta de colores | 5 paletas institucionales | `dashboard_tematico.py:28-39` |
| Códigos de sede/modalidad | Mapeo PBOG→Bogotá, etc. | `dashboard_tematico.py:826-837` |

### 5.4 Fuentes Derivadas (Generadas por el Sistema)

| Fuente | Formato | Ubicación | Generado por |
|--------|---------|-----------|-------------|
| Reporte HTML individual | HTML | `data/output/reportes/` | `ReportGenerator.generate_html_report()` |
| Reporte JSON individual | JSON | `data/output/reportes/` | `ReportGenerator.generate_json_report()` |
| Matriz Programas × Temáticas | Excel | `data/output/matrices/` | `ReportGenerator.generate_excel_matrix()` |
| Indicadores consolidados | Excel | `data/output/consolidado/` | `ReportGenerator.generate_consolidated_excel()` |
| Dashboard interactivo | Web (Streamlit) | `http://localhost:8501` | `dashboard/app.py` |

---

## 6. Respuestas y Salidas del Sistema

### 6.1 Salidas por Programa

#### A. Score de Calidad (0-100)
```
Score = 88.5/100
```
Acompañado de semáforo: 🟢 ≥75, 🟡 50-74, 🔴 <50

#### B. Balance de Tipos de Saber
```
Saber:       38.5%
SaberHacer:  30.8%
SaberSer:    30.8%
Desviación:   4.5%
Estado:      ✅ Balanceado
```

#### C. Complejidad Cognitiva (Bloom)
```
Básico:       7.7%
Intermedio:  30.8%
Avanzado:    61.5%
Nivel promedio: 4.5/6
Índice complejidad: 75.0/100
```

#### D. Cobertura de Competencias
```
Total competencias:      5
Competencias con RA:    5
Cobertura:             100.0%
Promedio RA/comp:        2.6
```

#### E. Diversidad Metodológica
```
Estrategias únicas:       12
Metodologías activas:   65.0%
Top: Taller (15), Caso (10), Proyecto (8)
```

#### F. Completitud
```
Competencias:          95.0%
Resultados Aprendizaje: 98.0%
Estrategias Meso:       80.0%
Estrategias Micro:      85.0%
Completitud Total:      89.5%
```

#### G. Temáticas Detectadas
```
Temáticas: SOSTENIBILIDAD, INTELIGENCIA ARTIFICIAL, INNOVACIÓN Y EMPRENDIMIENTO
```

### 6.2 Salidas Consolidadas

#### A. Matriz Programas × Temáticas (Excel)
| Programa | SOSTENIBILIDAD | IA | TRANSF_DIGITAL | ... |
|----------|---------------|-----|----------------|-----|
| Adm. Empresas | 5 | 2 | 0 | ... |
| Ing. Sistemas | 1 | 12 | 8 | ... |
| Derecho | 3 | 0 | 1 | ... |

#### B. Tabla Resumen con Semáforo
| Programa | Score | Créditos | Comp. | RA | Completitud | Complejidad Avanzado | Temáticas |
|----------|-------|----------|-------|-----|-------------|---------------------|-----------|
| Prog A | 🟢 88.5 | 140 | 5 | 13 | 89.5% | 61.5% | 3 |
| Prog B | 🟡 62.3 | 120 | 4 | 10 | 75.2% | 35.0% | 1 |
| Prog C | 🔴 45.0 | 130 | 3 | 8 | 55.0% | 20.0% | 0 |

#### C. Alertas de Calidad
| Programa | Alerta | Prioridad |
|----------|--------|-----------|
| Prog C | ⚠️ Score bajo (45/100) | Alta |
| Prog B | 📋 Completitud baja (55%) | Media |
| Prog A | 🟣 SaberSer bajo (5.2%) | Media |

#### D. Cobertura de Tendencias (Dashboard Temático)
| Tendencia | Cobertura | Asignaturas |
|-----------|-----------|-------------|
| Sostenibilidad | 45.2% | 28 |
| Inteligencia Artificial | 22.6% | 14 |
| Transformación Digital | 12.9% | 8 |
| ... | ... | ... |

#### E. Diversidad Temática (Entropía)
```
Núcleos Únicos:       145
Total Menciones:     1,234
Promedio por Asig:     4.2
Diversidad:          72.5/100
```

#### F. Top Términos TF-IDF
| Término | Peso TF-IDF |
|---------|-------------|
| análisis financiero | 0.452 |
| desarrollo sostenible | 0.389 |
| pensamiento crítico | 0.341 |
| ... | ... |

### 6.3 Salidas del Dashboard

| Página | Visualización | Tipo de Respuesta |
|--------|--------------|-------------------|
| Inicio | KPIs principales | Métricas numéricas |
| Inicio | Programas por modalidad/sede | Gráfico de barras apiladas |
| Inicio | Distribución Tipo de Saber | Gráfico de pastel |
| Inicio | Resumen por programa | Tabla paginada con diferencias |
| Programas | Score + métricas | Métricas + gráficos pie |
| Programas | Balance Saber | Gráfico de pastel |
| Programas | Complejidad Bloom | Gráfico de pastel |
| Programas | Temáticas detectadas | Cards de éxito |
| Programas | Competencias | Tabla |
| Temáticas | Programas por temática | Métrica + tabla |
| Comparativa | Perfil de indicadores | Gráfico radar |
| Comparativa | Tabla comparativa | Tabla |
| Comparativa | Similitud TF-IDF | Métrica |
| Comparativa | Estrategias pedagógicas | Barras agrupadas |
| Comparativa | Ranking scores | Barras horizontales |
| Comparativa | Tipo Saber por programa | Barras apiladas |
| Comparativa | Alertas de calidad | Tabla con prioridad |
| Estrategias Micro | Tipo Saber por programa | Barras + pastel |
| Estrategias Micro | Tipología | Barras + pastel |
| Estrategias Micro | Horas promedio | Barras |
| Estrategias Micro | Estrategias aprendizaje | Barras + sunburst |
| Cobertura (DT) | Núcleos únicos, diversidad | Métricas |
| Cobertura (DT) | Matriz Programas × Núcleos | Mapa de calor |
| Cobertura (DT) | Top núcleos | Barras horizontales |
| Cobertura (DT) | Densidad por asignatura | Barras |
| Tendencias (DT) | Cobertura por tendencia | Barras horizontales |
| Tendencias (DT) | Asignaturas por tendencia | Barras |
| Tendencias (DT) | Brechas curriculares | Advertencias |
| Tendencias (DT) | Detalle por programa | Expansores |
| NLP (DT) | Top términos TF-IDF | Tabla/barras |
| NLP (DT) | N-gramas frecuentes | Tabla |
| NLP (DT) | Términos por programa | Expansores |
| Bloom (DT) | Distribución por dominio | Barras/pastel |
| Bloom (DT) | Clasificación verbos | Tabla |
| Similitud (DT) | Matriz de similitud | Mapa de calor |

### 6.4 Formatos de Exportación

| Formato | Contenido | Tamaño Aprox. |
|---------|-----------|---------------|
| HTML | Reporte visual con CSS embebido | ~15-25 KB por programa |
| JSON | Datos estructurados completos | ~5-10 KB por programa |
| Excel (Matriz) | Programas × Temáticas | Variable (~50 filas × 15 columnas) |
| Excel (Consolidado) | Todos los indicadores | Variable (~50 filas × 12 columnas) |

---

## 7. Indicadores y Fórmulas Matemáticas

### 7.1 Score de Calidad

```
Score = C × 0.25 + CC × 0.20 + B × 0.15 + D × 0.15 + CB × 0.15 + R × 0.10

Donde:
  C  = Completitud total (%)
  CC = Índice de complejidad cognitiva (0-100)
  B  = 100 - desviación_estándar × 5  (0-100, clamp)
  D  = min(100, num_estrategias_únicas × 8)
  CB = Porcentaje de cobertura de competencias
  R  = 80.0 (placeholder de calidad de redacción)
```

### 7.2 Índice de Complejidad Cognitiva

```
IC = ((nivel_promedio - 1) / 5) × 100

Donde:
  nivel_promedio = media aritmética de niveles Bloom (1-6) de todos los RA
  Rango: 0 (todo básico) a 100 (todo avanzado)
```

### 7.3 Desviación del Balance

```
σ = √(Σ(xi - x̄)² / n)

Donde:
  xi = porcentaje de cada tipo de saber
  n = 3 (Saber, SaberHacer, SaberSer)
  
Balanceado si σ < 10%
```

### 7.4 Cobertura de Competencias

```
Cobertura = (competencias_con_RA / total_competencias) × 100
Promedio_RA = total_RA / competencias_con_RA
```

### 7.5 Completitud

```
Por DataFrame:
  completitud = (celdas_no_NaN / total_celdas) × 100

Total ponderada:
  C_total = C_comp × 0.30 + C_RA × 0.40 + C_meso × 0.15 + C_micro × 0.15
```

### 7.6 Frecuencia Temática Normalizada

```
por_creditos = total_coincidencias / creditos_totales × 10
```

Interpretación: número de coincidencias por cada 10 créditos académicos.

### 7.7 Cobertura de Tendencias (Dashboard Temático)

```
cobertura = (asignaturas_únicas_con_temática / total_asignaturas_únicas) × 100
```

### 7.8 Diversidad Temática (Entropía de Shannon)

```
H = -Σ p_i × log₂(p_i)
diversidad = H / log₂(N) × 100

Donde:
  p_i = frecuencia relativa del núcleo i
  N = número de núcleos únicos
```

### 7.9 Similitud Coseno

```
sim(A, B) = Σ(A_i × B_i) / √(ΣA_i²) × √(ΣB_i²)

Donde A y B son vectores TF-IDF de dos programas o asignaturas
```

---

## 8. Flujo de Datos Completo

### 8.1 Pipeline run_analysis.py

```
[Excel Files] 
    │
    ▼
[ExcelExtractor] ───► validate_structure() ───► {valid, errors, warnings}
    │
    ▼
[ExcelExtractor] ───► extract_all() ───► {metadata, competencias, RA, estrategias}
    │
    ├──► [CurricularAnalyzer] ───► generar_reporte_indicadores()
    │       └──► {score, balance, complejidad, cobertura, diversidad, completitud}
    │
    ├──► [ThematicDetector] ───► analyze_programa()
    │       └──► {tematicas_presentes, resumen, detalle}
    │
    ├──► [QualityValidator] ───► validate_programa_completo()
    │       └──► {score, competencias, RA, resumen}
    │
    └──► [ReportGenerator] ───► generate_html_report()
                            ───► generate_json_report()
    
[Consolidado]
    └──► [ThematicDetector] ───► generate_thematic_matrix() ───► Excel
    └──► [ReportGenerator] ───► generate_consolidated_excel() ───► Excel
```

### 8.2 Pipeline dashboard_tematico.py

```
[Excel Files] 
    │
    ▼
[procesar_archivos()] ───► DataFrame unificado
    │ Columnas: Programa, Modalidad, Sede, Nivel, Tipo Saber, 
    │           RA, Asignatura, Indicadores, Núcleos, Créditos
    │
    ├──► [analizar_cobertura()] ───► Dict
    │       ├── nucleos_counter: Counter
    │       ├── nucleos_unicos: int
    │       ├── densidad_asignatura: Series
    │       ├── shannon: float
    │       ├── diversidad: float (0-100)
    │       └── matriz_cobertura: DataFrame (Programas × Top-20 Núcleos)
    │
    ├──► [analizar_tendencias()] ───► Dict
    │       ├── matriz: DataFrame (Programas × Tendencias)
    │       ├── cobertura: Dict (Tendencia → % asignaturas)
    │       ├── detalle: Dict (Tendencia → Programa → List[Hallazgos])
    │       ├── ausentes: List[str]
    │       └── asig_counts: Dict (Tendencia → n_asignaturas)
    │
    ├──► [analizar_nlp()] ───► Dict
    │       ├── top_terminos: Dict (TF-IDF global)
    │       ├── top_por_programa: Dict (TF-IDF por programa)
    │       └── top_ngrams: Dict (frecuencia n-gramas)
    │
    └──► [calcular_similitud_asignaturas()] ───► Dict
            ├── similitud_df: DataFrame (N×N matrix)
            ├── par_similar: {asig1, asig2, similitud}
            └── n_asignaturas: int
```

### 8.3 Pipeline dashboard/app.py

```
[Excel Files]
    │
    ▼
[load_all_programs()] (cached) ───► List[Program]
    │
    ├──► Filtros: Modalidad, Sede, Nivel
    │
    ├──► Página Inicio: KPIs, resumen, estructura
    ├──► Página Programas: score, balance, complejidad, temáticas
    ├──► Página Temáticas: filtro, tabla, métrica
    ├──► Página Comparativa: radar, tabla, similitud, estrategias, ranking
    └──► Página Estrategias Micro: tipo saber, tipología, horas, estrategias
```

---

## 9. Configuración y Parametrización

### 9.1 Parámetros Globales (config.py)

| Parámetro | Valor Default | Descripción |
|-----------|---------------|-------------|
| `LOG_LEVEL` | `INFO` | Nivel de logging (DEBUG, INFO, WARNING, ERROR) |
| `PARALLEL_PROCESSING` | `True` | Procesamiento paralelo de archivos |
| `MAX_WORKERS` | `4` | Número máximo de procesos paralelos |
| `EXPORT_FORMATS` | `['html', 'pdf', 'excel', 'json']` | Formatos de exportación |
| `LLM_ENABLED` | `False` | Integración con LLM (opcional) |
| `LLM_PROVIDER` | `'anthropic'` | Proveedor LLM |
| `LLM_MODEL` | `'claude-3-5-sonnet-20241022'` | Modelo LLM |
| `ENABLE_CACHE` | `True` | Cache de datos procesados |
| `MIN_COMPETENCIAS` | `3` | Mínimo de competencias esperadas |
| `MIN_RA_POR_COMPETENCIA` | `2` | Mínimo de RA por competencia |
| `MIN_COMPLETITUD` | `70.0` | % mínimo de completitud |
| `DASHBOARD_PORT` | `8501` | Puerto del dashboard |

### 9.2 Pesos del Score de Calidad

```python
QUALITY_WEIGHTS = {
    'completitud': 0.25,           # 25%
    'complejidad_cognitiva': 0.20, # 20%
    'balance_tipo_saber': 0.15,    # 15%
    'diversidad_metodologica': 0.15, # 15%
    'cobertura_competencias': 0.15, # 15%
    'calidad_redaccion': 0.10      # 10%
}
# Deben sumar exactamente 1.0 (validado en validate_config())
```

### 9.3 Umbrales de Complejidad

```python
COMPLEJIDAD_THRESHOLDS = {
    'BASICO': (1, 2),      # Recordar, Comprender
    'INTERMEDIO': (3, 4),  # Aplicar, Analizar
    'AVANZADO': (5, 6)     # Evaluar, Crear
}
```

### 9.4 Balance Ideal de Saber

```python
BALANCE_IDEAL_SABER = {
    'Saber': 33.3,
    'SaberHacer': 33.3,
    'SaberSer': 33.4
}
```

### 9.5 Umbrales de Alertas (Dashboard)

| Alerta | Umbral | Prioridad |
|--------|--------|-----------|
| Score bajo | `score_calidad < 50` | Alta |
| Completitud baja | `completitud < 70%` | Media |
| SaberSer bajo | `saber_ser < 8%` | Media |
| Complejidad baja | `%_avanzado < 15%` | Baja |
| Sin créditos | `creditos_total == 0` | Alta |

### 9.6 Configuración de Tendencias (JSON)

```json
{
  "TENDENCIAS_GLOBALES": {
    "SOSTENIBILIDAD": {
      "keywords": ["sostenibilidad", "ODS", "medio ambiente", ...],
      "color": "#2ECC71",
      "descripcion": "Sostenibilidad y Desarrollo Sostenible (ODS)"
    }
  },
  "INSTRUCCIONES": {
    "como_usar": [...],
    "notas": [...]
  },
  "VERSION": "1.0"
}
```

### 9.7 Paletas de Colores (Dashboard Temático)

```python
PALETA_DOUBLE_SPLIT = ['#0FFF8B', '#0FBFFF', '#0F83FF', '#FF0F83', '#FF8B0F']
PALETA_AZUL = ['#092196', '#1A2663', '#748BFC', '#A8B7FF', '#DBE1FF']
COLORES_MODALIDAD = {'Presencial': '#0F83FF', 'Virtual': '#748BFC', 'Híbrido': '#0FFF8B'}
COLORES_SEDE = {'Bogotá': '#0F83FF', 'Medellín': '#1565C0', 'Nacional': '#0FFF8B'}
```

---

**Documento generado el:** Mayo 2026  
**Versión:** 1.0.0  
**Ubicación:** `docs/LOGICA_Y_MODELOS.md`
