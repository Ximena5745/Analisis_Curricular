# Análisis del Backend

## Stack Tecnológico

| Componente | Tecnología |
|-----------|-----------|
| Lenguaje | Python 3.x |
| Datos | pandas, openpyxl |
| Base de datos | SQLite |
| Opcional | Anthropic/OpenAI API |

## Estructura de Código

```
src/
├── __init__.py
├── extractor.py       # Extracción de datos Excel
├── analyzer.py      # Análisis de competencias y RA
├── validator.py    # Validación de calidad
├── report_generator.py  # Generación de reportes
└── thematic_detector.py  # Detección de temáticas
```

## Módulos Principales

### 1. extractor.py

Extrae datos de archivos Excel de formato institucional.

```python
def extract_data(input_file: Path) -> Dict:
    """Extrae competencias y RA de Excel."""
    
def extract_profile(file: Path) -> Dict:
    """Extrae perfil de egreso."""
```

**Entradas:** archivos `.xlsx` en `data/raw/`  
**Salidas:** diccionarios con competencias, RA, perfiles

### 2. analyzer.py

Analiza competencias, resultados de aprendizaje y métricas.

```python
def analyze_competencies(competencies: List[Dict]) -> Dict:
    """Analiza estructura de competencias."""
    
def calculate_metrics(data: Dict) -> Dict:
    """Calcula métricas de calidad."""
    
def analyze_distribution(data: Dict) -> Dict:
    """Analiza distribución saber/saber hacer/saber ser."""
```

**Dependencias:** `extractor.py`  
**Salidas:** métricas, distribución, verbos

### 3. validator.py

Valida calidad curricular según reglas establecidas.

```python
def validate_competencies(competencies: List[Dict]) -> List[Dict]:
    """Valida competencias y RA."""
    
def check_completeness(data: Dict) -> float:
    """Verifica completitud (% lleno)."""
    
def check_verbs(ra_list: List[str]) -> List[str]:
    """Verifica uso correcto de verbos."""
```

**Reglas de validación:**
- Mínimo 3 competencias por programa
- Mínimo 2 RA por competencia
- Completitud mínima 70%
- Verbos válidos según taxonomía

### 4. report_generator.py

Genera reportes en múltiples formatos.

```python
def generate_html_report(data: Dict, output_path: Path):
    """Genera reporte HTML."""
    
def generate_pdf_report(data: Dict, output_path: Path):
    """Genera reporte PDF."""
    
def generate_excel_report(data: Dict, output_path: Path):
    """Genera reporte Excel."""
    
def generate_json_report(data: Dict, output_path: Path):
    """Genera reporte JSON."""
```

**Formatos de salida:** HTML, PDF, Excel, JSON

### 5. thematic_detector.py

Detecta y categoriza temáticas en competencias.

```python
def detect_thematics(competencies: List[Dict]) -> Dict:
    """Detecta temáticas por palabras clave."""
    
def get_tematica_keywords(tematica: str) -> List[str]:
    """Retorna keywords de una temática."""
```

**Themáticas detectadas:** Tecnológica, Gestión, Legal, Ambiental, etc.

## Configuración (config.py)

```python
CONFIG = {
    'INPUT_FOLDER': 'data/raw/',
    'OUTPUT_FOLDER': 'data/output/',
    'LOG_LEVEL': 'INFO',
    'PARALLEL_PROCESSING': True,
    'MAX_WORKERS': 4,
    'LLM_ENABLED': False,
    'LLM_PROVIDER': 'anthropic',
    'MIN_COMPETENCIAS': 3,
    'MIN_RA_POR_COMPETENCIA': 2,
    'MIN_COMPLETITUD': 70.0,
}
```

## APIs de Entrada (CLI)

| Comando | Descripción |
|---------|-------------|
| `python main.py` | Ejecuta análisis completo |
| `python -c "import ...; ..."` | Uso programático |

## Manejo de Errores

- Archivos no encontrados: mensaje con ruta
- Estructura inválida: aviso de formato
- Errores de procesamiento: logging con nivel

## Logging

Configurable en `config.py`:
- DEBUG, INFO, WARNING, ERROR, CRITICAL
- Archivo en `logs/analisis_microcurricular.log`

## Integración con LLM (Opcional)

```python
CONFIG['LLM_ENABLED'] = True
CONFIG['LLM_PROVIDER'] = 'anthropic'  # o 'openai'
```

API keys via variables de entorno:
- `ANTHROPIC_API_KEY`
- `OPENAI_API_KEY`

## Pendientes / Deuda Técnica

- [ ] API REST formal
- [ ] Autenticación
- [ ] Tests de integración
- [ ] Dockerización
- [ ] CI/CD