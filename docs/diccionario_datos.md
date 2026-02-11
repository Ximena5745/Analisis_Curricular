# 📚 Diccionario de Datos

## Descripción General

Este documento describe la estructura de datos utilizada en el Sistema de Análisis Microcurricular.

---

## Datos de Entrada

### Archivos Excel Microcurriculares

#### Hoja: "Paso 2 Redacción competen"

| Campo | Tipo | Descripción | Ejemplo | Requerido |
|-------|------|-------------|---------|-----------|
| No. | Entero | Número secuencial de la competencia | 1, 2, 3 | ✅ |
| Verbo competencia | Texto | Verbo principal de la competencia | Analizar, Evaluar, Crear | ✅ |
| Objeto conceptual | Texto | Qué se analiza/evalúa/crea | Estados financieros | ✅ |
| Finalidad | Texto | Para qué (propósito) | Para tomar decisiones empresariales | ✅ |
| Condición de contexto o referencia | Texto | En qué contexto | Considerando entorno económico | ⚠️ |
| Redacción competencia | Texto | Texto completo de la competencia | "Analizar estados financieros..." | ✅ |
| Tipo de competencia | Texto | Específica o Genérica | Específica, Genérica | ✅ |

#### Hoja: "Paso 3 Redacción RA"

| Campo | Tipo | Descripción | Ejemplo | Requerido |
|-------|------|-------------|---------|-----------|
| Competencia por desarrollar | Texto | Competencia asociada | Competencia 1 | ✅ |
| Número de resultado | Texto | ID del RA | RA1, RA2 | ✅ |
| TipoSaber | Texto | Tipo de conocimiento | Saber, SaberHacer, SaberSer | ✅ |
| SaberAsociado | Texto | Descripción del saber | Fundamentos de... | ⚠️ |
| Taxonomía | Texto | Dominio taxonómico | Cognitivo, Afectivo, Psicomotor | ⚠️ |
| Dominio Asociado | Texto | Área del conocimiento | Análisis, Síntesis | ⚠️ |
| Nivel Dominio | Texto | Nivel según Bloom | AnálisisBAK, EvaluarBAK | ✅ |
| Verbo RA | Texto | Verbo principal del RA | Identificar, Calcular | ✅ |
| Resultados Aprendizaje | Texto | Texto completo del RA | "Identificar componentes de..." | ✅ |

#### Hoja: "Paso 4 Estrategias mesocurricu"

| Campo | Tipo | Descripción | Ejemplo | Requerido |
|-------|------|-------------|---------|-----------|
| Resultado de aprendizaje | Texto | RA asociado | RA1 | ✅ |
| Estrategia del programa | Texto | Nombre de la estrategia | Proyecto integrador | ✅ |
| Descripción | Texto | Detalle de la estrategia | Los estudiantes desarrollan... | ⚠️ |
| Indicador de Impacto | Texto | Cómo se mide el impacto | % de proyectos completados | ⚠️ |
| Acciones de retroalimentación | Texto | Cómo se retroalimenta | Sesiones de asesoría | ⚠️ |
| Instrumentos de medición | Texto | Herramientas de evaluación | Rúbrica de proyecto | ⚠️ |

#### Hoja: "Paso 5 Estrategias micro"

| Campo | Tipo | Descripción | Ejemplo | Requerido |
|-------|------|-------------|---------|-----------|
| Tipo de Saber | Texto | Saber/SaberHacer/SaberSer | SaberHacer | ✅ |
| Estrategias de enseñanza aprendizaje | Texto | Método pedagógico | Aprendizaje Basado en Problemas | ✅ |
| Recursos | Texto | Materiales y recursos | Laboratorio, Software | ⚠️ |
| Horas de trabajo autónomo | Número | Horas fuera de clase | 4 | ⚠️ |
| Horas de trabajo presencial | Número | Horas en clase | 2 | ⚠️ |
| Criterios de evaluación | Texto | Qué se evalúa | Solución correcta del problema | ⚠️ |
| Acciones de retroalimentación | Texto | Cómo se retroalimenta | Revisión grupal de soluciones | ⚠️ |

**Leyenda:**
- ✅ Requerido: Campo obligatorio para análisis
- ⚠️ Opcional: Campo deseable pero no crítico

---

## Datos de Salida

### 1. Reporte de Indicadores (JSON/Dict)

```json
{
  "programa": "Administración de Empresas",
  "score_calidad": 88.5,
  "balance_tipo_saber": {
    "Saber": 38.5,
    "SaberHacer": 30.8,
    "SaberSer": 30.8,
    "desviacion_estandar": 4.5,
    "balanceado": true
  },
  "complejidad_cognitiva": {
    "Básico": 7.7,
    "Intermedio": 30.8,
    "Avanzado": 61.5,
    "nivel_promedio": 4.5,
    "indice_complejidad": 75.0
  },
  "cobertura_competencias": {
    "total_competencias": 5,
    "competencias_con_ra": 5,
    "porcentaje_cobertura": 100.0,
    "promedio_ra_por_competencia": 2.6
  },
  "diversidad_metodologica": {
    "num_estrategias_unicas": 12,
    "estrategias_mas_frecuentes": [
      ["ABP", 15],
      ["Estudio de caso", 10]
    ],
    "porcentaje_metodologias_activas": 65.0
  },
  "completitud": {
    "completitud_competencias": 95.0,
    "completitud_ra": 98.0,
    "completitud_estrategias_meso": 80.0,
    "completitud_estrategias_micro": 85.0,
    "completitud_total": 89.5
  },
  "resumen": {
    "total_competencias": 5,
    "total_ra": 13,
    "total_estrategias_meso": 8,
    "total_estrategias_micro": 134
  }
}
```

### 2. Análisis de Temáticas (Dict)

```json
{
  "programa": "Administración de Empresas",
  "tematicas_presentes": [
    "SOSTENIBILIDAD",
    "INNOVACIÓN Y EMPRENDIMIENTO",
    "LIDERAZGO Y HABILIDADES BLANDAS",
    "INTELIGENCIA ARTIFICIAL"
  ],
  "num_tematicas": 4,
  "resumen": {
    "SOSTENIBILIDAD": {
      "presente": true,
      "frecuencia_competencias": 3,
      "frecuencia_ra": 5,
      "total_coincidencias": 8
    },
    "INTELIGENCIA ARTIFICIAL": {
      "presente": true,
      "frecuencia_competencias": 2,
      "frecuencia_ra": 6,
      "total_coincidencias": 8
    }
  }
}
```

### 3. Matriz de Temáticas (Excel/DataFrame)

| Programa | Competencias | RA | SOSTENIBILIDAD | IA | INNOVACIÓN | ... |
|----------|--------------|----|-----------------|----|------------|-----|
| Adm. Empresas | 5 | 13 | 8 | 14 | 4 | ... |
| Ing. Sistemas | 6 | 15 | 2 | 25 | 10 | ... |
| Derecho | 4 | 12 | 3 | 0 | 1 | ... |

**Descripción de columnas:**
- **Programa:** Nombre del programa académico
- **Competencias:** Total de competencias del programa
- **RA:** Total de Resultados de Aprendizaje
- **[TEMÁTICA]:** Número de coincidencias de esa temática (suma en competencias + RA)

### 4. Excel Consolidado de Indicadores

| Programa | Score_Calidad | Total_Competencias | Total_RA | Saber_% | SaberHacer_% | ... |
|----------|---------------|-------------------|----------|---------|--------------|-----|
| Prog A | 88.5 | 5 | 13 | 38.5 | 30.8 | ... |
| Prog B | 92.1 | 6 | 15 | 40.0 | 33.3 | ... |

---

## Estructuras de Datos Internas

### Programa Data (Dict)

Estructura retornada por `ExcelExtractor.extract_all()`:

```python
{
    'metadata': {
        'programa': str,      # "Administración de Empresas"
        'archivo': str,       # "FormatoRA_AdmonEmpresas_PBOG.xlsx"
        'ruta': str          # Ruta completa al archivo
    },
    'competencias': pd.DataFrame,              # DataFrame de competencias
    'resultados_aprendizaje': pd.DataFrame,   # DataFrame de RA
    'estrategias_meso': pd.DataFrame,         # DataFrame estrategias meso
    'estrategias_micro': pd.DataFrame         # DataFrame estrategias micro
}
```

### Validation Result (Dict)

Estructura retornada por `ExcelExtractor.validate_structure()`:

```python
{
    'valid': bool,                    # True si pasa validación
    'errors': List[str],             # Lista de errores críticos
    'warnings': List[str],           # Lista de advertencias
    'info': {
        'num_competencias': int,
        'num_resultados_aprendizaje': int
    }
}
```

---

## Constantes Configurables

### Tipos de Saber

```python
TIPOS_SABER = ['Saber', 'SaberHacer', 'SaberSer']
```

### Niveles de Complejidad Cognitiva

```python
COMPLEJIDAD_THRESHOLDS = {
    'BASICO': (1, 2),      # Recordar, Comprender
    'INTERMEDIO': (3, 4),  # Aplicar, Analizar
    'AVANZADO': (5, 6)     # Evaluar, Crear
}
```

### Taxonomía de Bloom

```python
TAXONOMIA_BLOOM = {
    'RECORDAR': {
        'nivel': 1,
        'verbos': ['definir', 'listar', 'recordar', ...]
    },
    'COMPRENDER': {
        'nivel': 2,
        'verbos': ['explicar', 'describir', ...]
    },
    ...
}
```

### Pesos del Score de Calidad

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

---

## Formatos de Exportación

### HTML

Reportes individuales con visualizaciones CSS/HTML

**Ubicación:** `data/output/reportes/reporte_[PROGRAMA].html`

### JSON

Datos estructurados para integración con otras herramientas

**Ubicación:** `data/output/reportes/reporte_[PROGRAMA].json`

### Excel

Matrices y tablas consolidadas

**Ubicaciones:**
- `data/output/matrices/matriz_tematicas.xlsx`
- `data/output/consolidado/indicadores_consolidados.xlsx`

### PDF

(Requiere WeasyPrint) Reportes profesionales para impresión

**Ubicación:** `data/output/reportes/reporte_[PROGRAMA].pdf`

---

## Notas Técnicas

### Normalización de Texto

El sistema normaliza texto para búsqueda:
- Convierte a minúsculas
- Remueve tildes (á→a, é→e)
- Remueve caracteres especiales

**Ejemplo:**
```
"Análisis de Gestión" → "analisis de gestion"
```

### Detección de Keywords

- Búsqueda case-insensitive
- Detecta variantes (sostenibilidad, sostenible, sustentabilidad)
- Extrae contexto (±100 caracteres alrededor de keyword)

### Caché

El sistema cachea resultados procesados para evitar reprocesamiento.

**Ubicación:** `data/cache/`

---

## Versionado

**Versión actual:** 1.0.0

**Cambios entre versiones:** Ver [CHANGELOG.md](../CHANGELOG.md)
