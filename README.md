# 🎓 Sistema de Análisis Microcurricular

Sistema completo de análisis automatizado para diseños microcurriculares de programas académicos. Permite consolidar, analizar y visualizar información de 50+ programas académicos, detectar temáticas emergentes, calcular indicadores de calidad curricular y generar reportes profesionales.

## 📋 Tabla de Contenidos

- [Características](#-características)
- [Requisitos](#-requisitos)
- [Instalación](#-instalación)
- [Configuración](#-configuración)
- [Uso Rápido](#-uso-rápido)
- [Estructura del Proyecto](#-estructura-del-proyecto)
- [Módulos Principales](#-módulos-principales)
- [Dashboard Interactivo](#-dashboard-interactivo)
- [Ejemplos de Uso](#-ejemplos-de-uso)
- [Troubleshooting](#-troubleshooting)
- [Contribuir](#-contribuir)

---

## ✨ Características

### 🔍 Análisis Automatizado
- ✅ Consolidación de 50+ archivos Excel en base de datos única
- ✅ Extracción normalizada de competencias, RA, estrategias pedagógicas
- ✅ Cálculo de 15+ indicadores de calidad curricular
- ✅ Validación de completitud y consistencia de datos

### 🏷️ Detección de Temáticas
Identifica automáticamente 10 temáticas emergentes:
- Sostenibilidad y Desarrollo Sostenible
- Inteligencia Artificial y Tecnologías Emergentes
- Responsabilidad Social Empresarial
- Transformación Digital
- Innovación y Emprendimiento
- Globalización y Perspectiva Glocal
- Ética y Valores
- Liderazgo y Habilidades Blandas
- Análisis de Datos
- Gestión del Cambio

### 📊 Visualización y Reportería
- Dashboard web interactivo con Streamlit
- Reportes individuales por programa (PDF/HTML/Word)
- Matriz consolidada Programas × Temáticas (Excel)
- Gráficos comparativos (Plotly, Matplotlib, Seaborn)
- Exportación en múltiples formatos

### 🤖 Integración con LLM (Opcional)
- Análisis semántico avanzado con Claude o GPT
- Validación de calidad de redacción
- Sugerencias de mejora curricular

---

## 💻 Requisitos

### Requisitos del Sistema
- **Python**: 3.10 o superior
- **Sistema Operativo**: Windows 10+, macOS 10.15+, Linux (Ubuntu 20.04+)
- **RAM**: Mínimo 4GB (recomendado 8GB para procesamiento de 50 archivos)
- **Espacio en Disco**: 500MB mínimo

### Conocimientos Previos
- Python básico
- Manejo de Excel
- Uso de terminal/línea de comandos (básico)

---

## 📥 Instalación

### Paso 1: Clonar o Descargar el Proyecto

```bash
# Si tienes Git instalado
git clone https://github.com/institucion/analisis-microcurricular.git
cd analisis-microcurricular

# O descarga el ZIP y descomprime
```

### Paso 2: Crear Entorno Virtual (Recomendado)

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Paso 3: Instalar Dependencias

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**Instalación completa:**
```bash
pip install -e .
```

### Paso 4: Verificar Instalación

```bash
python -c "import pandas; import streamlit; import plotly; print('✅ Instalación exitosa!')"
```

---

## ⚙️ Configuración

### 1. Configuración Básica

Edita [config.py](config.py) para ajustar rutas y parámetros:

```python
CONFIG = {
    'INPUT_FOLDER': 'data/raw/',           # Carpeta con archivos Excel
    'OUTPUT_FOLDER': 'data/output/',        # Carpeta para resultados
    'LOG_LEVEL': 'INFO',                    # DEBUG, INFO, WARNING, ERROR
    'PARALLEL_PROCESSING': True,            # Procesamiento paralelo
    'MAX_WORKERS': 4,                       # Procesos simultáneos
}
```

### 2. Colocar Archivos Excel

Copia tus archivos Excel a la carpeta `data/raw/`:

```
proyecto_analisis_microcurricular/
└── data/
    └── raw/
        ├── FormatoRA_AdmonEmpresas_PBOG.xlsx
        ├── FormatoRA_IngSistemas_PBOG.xlsx
        ├── FormatoRA_Derecho_PBOG.xlsx
        └── ... (resto de archivos)
```

### 3. Configuración Opcional: LLM Integration

Si deseas usar Claude o GPT para análisis avanzado:

**Crear archivo `.env` en la raíz del proyecto:**
```bash
# Para Claude
ANTHROPIC_API_KEY=tu_api_key_aqui

# O para OpenAI
OPENAI_API_KEY=tu_api_key_aqui
```

**Activar en config.py:**
```python
CONFIG['LLM_ENABLED'] = True
CONFIG['LLM_PROVIDER'] = 'anthropic'  # o 'openai'
```

---

## 🚀 Uso Rápido

### Opción 1: Script de Análisis Completo (Recomendado)

```bash
python run_analysis.py
```

Este script:
1. ✅ Valida estructura de archivos Excel
2. ✅ Extrae datos de todos los programas
3. ✅ Calcula indicadores y detecta temáticas
4. ✅ Genera reportes consolidados
5. ✅ Guarda resultados en `data/output/`

### Opción 2: Dashboard Interactivo

```bash
streamlit run dashboard/app.py
```

Abre automáticamente en el navegador: `http://localhost:8501`

### Opción 3: Uso Programático

```python
from src.extractor import ExcelExtractor
from src.analyzer import CurricularAnalyzer
from src.thematic_detector import ThematicDetector

# Extraer datos de un programa
extractor = ExcelExtractor('data/raw/FormatoRA_AdmonEmpresas_PBOG.xlsx')
data = extractor.extract_all()

# Analizar indicadores
analyzer = CurricularAnalyzer(data)
indicadores = analyzer.generar_reporte_indicadores()

# Detectar temáticas
detector = ThematicDetector()
tematicas = detector.analyze_programa(data)

print(f"Score de calidad: {indicadores['score_calidad']}/100")
print(f"Temáticas detectadas: {tematicas['tematicas_presentes']}")
```

---

## 📁 Estructura del Proyecto

```
proyecto_analisis_microcurricular/
│
├── README.md                          # Este archivo
├── requirements.txt                   # Dependencias Python
├── config.py                         # Configuración global
├── setup.py                          # Instalación del paquete
│
├── data/                             # Datos
│   ├── raw/                          # 📂 Archivos Excel originales (COLOCA AQUÍ)
│   ├── processed/                    # Datos procesados (CSV, pickle)
│   └── output/                       # 📊 Resultados generados
│       ├── reportes/                 # Reportes por programa
│       ├── consolidado/              # Reportes consolidados
│       └── matrices/                 # Matrices Excel
│
├── src/                              # Código fuente
│   ├── __init__.py
│   ├── extractor.py                 # ⚙️ Extracción de datos Excel
│   ├── analyzer.py                  # 📈 Cálculo de indicadores
│   ├── thematic_detector.py         # 🏷️ Detección de temáticas
│   ├── validator.py                 # ✅ Validación de calidad
│   ├── report_generator.py          # 📄 Generación de reportes
│   ├── llm_integration.py           # 🤖 Integración con LLM
│   └── utils.py                     # Utilidades generales
│
├── dashboard/                        # Dashboard web
│   ├── app.py                       # 🎨 App principal Streamlit
│   ├── pages/                       # Páginas del dashboard
│   │   ├── 1_📊_Programas.py
│   │   ├── 2_🏷️_Temáticas.py
│   │   ├── 3_📈_Comparativa.py
│   │   └── 4_📄_Reportes.py
│   └── components/                  # Componentes reutilizables
│       ├── charts.py
│       ├── tables.py
│       └── filters.py
│
├── templates/                        # Templates HTML/CSS
│   ├── reporte_programa.html
│   ├── dashboard_consolidado.html
│   └── styles.css
│
├── tests/                            # Tests unitarios
│   ├── test_extractor.py
│   ├── test_analyzer.py
│   ├── test_thematic_detector.py
│   └── test_validator.py
│
├── notebooks/                        # Jupyter notebooks
│   └── analisis_exploratorio.ipynb
│
├── docs/                             # Documentación
│   ├── guia_usuario.md
│   ├── diccionario_datos.md
│   └── metodologia.md
│
├── run_analysis.py                   # 🚀 Script principal
├── export_results.py                 # 💾 Exportar resultados
└── validate_files.py                 # ✔️ Validar archivos Excel
```

---

## 🧩 Módulos Principales

### 1. ExcelExtractor (`src/extractor.py`)

Extrae datos de archivos Excel microcurriculares.

```python
from src.extractor import ExcelExtractor

extractor = ExcelExtractor('ruta/archivo.xlsx')

# Extraer competencias
competencias_df = extractor.extract_competencias()

# Extraer resultados de aprendizaje
ra_df = extractor.extract_resultados_aprendizaje()

# Extraer todo
all_data = extractor.extract_all()
```

**Salida:**
```python
{
    'metadata': {'programa': 'Adm. Empresas', 'archivo': '...'},
    'competencias': DataFrame,
    'resultados_aprendizaje': DataFrame,
    'estrategias_meso': DataFrame,
    'estrategias_micro': DataFrame
}
```

### 2. CurricularAnalyzer (`src/analyzer.py`)

Calcula indicadores de calidad curricular.

```python
from src.analyzer import CurricularAnalyzer

analyzer = CurricularAnalyzer(programa_data)

# Balance de tipos de saber
balance = analyzer.calcular_balance_tipo_saber()
# {'Saber': 38.5, 'SaberHacer': 30.8, 'SaberSer': 30.8}

# Complejidad cognitiva
complejidad = analyzer.calcular_complejidad_cognitiva()
# {'Básico': 7.7, 'Intermedio': 30.8, 'Avanzado': 61.5}

# Reporte completo
reporte = analyzer.generar_reporte_indicadores()
```

### 3. ThematicDetector (`src/thematic_detector.py`)

Detecta temáticas en textos curriculares.

```python
from src.thematic_detector import ThematicDetector

detector = ThematicDetector()

# Detectar en un texto
resultado = detector.detect_in_text("Desarrollo sostenible y responsabilidad ambiental...")
# {'SOSTENIBILIDAD': {'presente': True, 'num_coincidencias': 2, ...}}

# Analizar programa completo
tematicas_programa = detector.analyze_programa(programa_data)

# Generar matriz de todos los programas
matriz = detector.generate_thematic_matrix(lista_programas)
```

### 4. QualityValidator (`src/validator.py`)

Valida calidad de redacción y estructura.

```python
from src.validator import QualityValidator

validator = QualityValidator()

# Validar competencia
validacion = validator.validate_competencia_structure(
    "Analizar estados financieros para tomar decisiones empresariales..."
)
# {'valid': True, 'issues': [], 'suggestions': []}

# Validar programa completo
reporte = validator.validate_programa_completo(programa_data)
# {'score': 85, 'errores': [], 'advertencias': [], 'sugerencias': []}
```

---

## 🎨 Dashboard Interactivo

### Iniciar Dashboard

```bash
streamlit run dashboard/app.py
```

### Páginas Disponibles

#### 🏠 Inicio
- KPIs principales (total programas, competencias, RA, score promedio)
- Gráfico de cobertura de temáticas
- Mapa de calor Programas × Temáticas
- Resumen ejecutivo

#### 📊 Programas
- Selector de programa
- Indicadores detallados por programa
- Balance de tipos de saber (donut chart)
- Complejidad cognitiva (radar chart)
- Tabla de competencias y RA

#### 🏷️ Temáticas
- Filtro por temática
- Programas que abordan cada temática
- Frecuencia de keywords
- Word cloud de términos
- Exportar lista de programas

#### 📈 Comparativa
- Seleccionar 2-5 programas
- Gráficos lado a lado
- Scatter plot: complejidad vs diversidad
- Box plot por facultad
- Tabla comparativa

#### 📄 Reportes
- Generar reporte individual (PDF/HTML/Word)
- Descargar matriz consolidada (Excel)
- Dashboard HTML consolidado
- Exportar datos raw (JSON/CSV)

---

## 💡 Ejemplos de Uso

### Ejemplo 1: Análisis de un Solo Programa

```python
from src.extractor import ExcelExtractor
from src.analyzer import CurricularAnalyzer
from src.thematic_detector import ThematicDetector
from src.report_generator import ReportGenerator

# 1. Extraer datos
extractor = ExcelExtractor('data/raw/FormatoRA_AdmonEmpresas_PBOG.xlsx')
data = extractor.extract_all()
print(f"✅ Extraídas {len(data['competencias'])} competencias")

# 2. Analizar
analyzer = CurricularAnalyzer(data)
indicadores = analyzer.generar_reporte_indicadores()
print(f"📊 Score de calidad: {indicadores['score_calidad']}/100")

# 3. Detectar temáticas
detector = ThematicDetector()
tematicas = detector.analyze_programa(data)
print(f"🏷️ Temáticas: {', '.join(tematicas['tematicas_presentes'])}")

# 4. Generar reporte
generator = ReportGenerator()
generator.generate_pdf_report(
    data,
    indicadores,
    'data/output/reportes/admon_empresas.pdf'
)
print("📄 Reporte generado exitosamente")
```

### Ejemplo 2: Identificar Programas con Sostenibilidad

```python
from src.batch_processor import BatchProcessor
from src.thematic_detector import ThematicDetector
import pandas as pd

# Procesar todos los programas
processor = BatchProcessor(input_folder='data/raw/')
all_data = processor.process_all_programs()

# Generar matriz de temáticas
detector = ThematicDetector()
matriz = detector.generate_thematic_matrix(all_data)

# Filtrar programas con sostenibilidad
programas_sostenibles = matriz[matriz['SOSTENIBILIDAD'] > 0]
programas_sostenibles = programas_sostenibles.sort_values('SOSTENIBILIDAD', ascending=False)

# Exportar
programas_sostenibles.to_excel(
    'data/output/programas_con_sostenibilidad.xlsx',
    index=False
)

print(f"✅ {len(programas_sostenibles)} programas abordan sostenibilidad")
print(programas_sostenibles[['Programa', 'SOSTENIBILIDAD']].head(10))
```

### Ejemplo 3: Comparar Programas de una Facultad

```python
from src.batch_processor import BatchProcessor
import pandas as pd

# Cargar datos procesados
df_programas = pd.read_csv('data/processed/programas_consolidado.csv')

# Filtrar por facultad
facultad_ingenieria = df_programas[df_programas['Facultad'] == 'Ingeniería']

# Comparar indicadores
comparacion = facultad_ingenieria[[
    'Programa',
    'Score_Calidad',
    'Complejidad_Cognitiva_Avanzado',
    'Diversidad_Metodologica',
    'Num_Tematicas'
]].sort_values('Score_Calidad', ascending=False)

print(comparacion)
```

### Ejemplo 4: Validar Todos los Archivos

```bash
python validate_files.py
```

**Salida:**
```
╔═══════════════════════════════════════════════════════════╗
║          VALIDACIÓN DE ARCHIVOS EXCEL                    ║
╚═══════════════════════════════════════════════════════════╝

Analizando archivos en: data/raw/

✅ FormatoRA_AdmonEmpresas_PBOG.xlsx - OK
✅ FormatoRA_IngSistemas_PBOG.xlsx - OK
⚠️  FormatoRA_Derecho_PBOG.xlsx - Advertencias:
    - Falta hoja "Paso 5 Estrategias micro"
❌ FormatoRA_Psicologia_PBOG.xlsx - Errores:
    - Header no encontrado en "Paso 2 Redacción competen"

Resumen:
  Total archivos: 50
  ✅ Válidos: 45
  ⚠️  Con advertencias: 3
  ❌ Con errores: 2

Archivos con errores guardados en: data/output/validacion_errores.txt
```

---

## 🔧 Troubleshooting

### Problema: Error al importar openpyxl

```bash
ModuleNotFoundError: No module named 'openpyxl'
```

**Solución:**
```bash
pip install openpyxl
```

### Problema: Streamlit no inicia

```bash
streamlit: command not found
```

**Solución:**
```bash
# Windows
python -m streamlit run dashboard/app.py

# macOS/Linux
python3 -m streamlit run dashboard/app.py
```

### Problema: Archivo Excel no se lee correctamente

```
ValueError: Expected columns not found in sheet 'Paso 2 Redacción competen'
```

**Solución:**
1. Verifica que el archivo tiene la estructura esperada
2. Revisa que los nombres de las hojas coincidan exactamente
3. Ejecuta `python validate_files.py` para diagnóstico detallado

### Problema: Error de memoria al procesar 50 archivos

```
MemoryError
```

**Solución:**
```python
# En config.py, ajusta:
CONFIG['PARALLEL_PROCESSING'] = False
# O reduce workers:
CONFIG['MAX_WORKERS'] = 2
```

### Problema: Reportes PDF no se generan

```bash
pip install weasyprint
```

**En Windows puede requerir GTK3 Runtime:**
https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer/releases

---

## 📚 Documentación Adicional

### Guías Detalladas

- [Guía de Usuario Completa](docs/guia_usuario.md)
- [Diccionario de Datos](docs/diccionario_datos.md)
- [Metodología de Análisis](docs/metodologia.md)

### API Reference

Genera documentación de API con Sphinx:

```bash
cd docs
sphinx-build -b html . _build
```

### Jupyter Notebooks

Explora análisis interactivos:

```bash
jupyter notebook notebooks/analisis_exploratorio.ipynb
```

---

## 🧪 Tests

Ejecutar tests unitarios:

```bash
# Todos los tests
pytest

# Con cobertura
pytest --cov=src --cov-report=html

# Solo un módulo
pytest tests/test_extractor.py -v
```

---

## 🤝 Contribuir

### Reportar Bugs

Abre un issue en GitHub con:
- Descripción del problema
- Pasos para reproducir
- Salida de error completa
- Versión de Python y dependencias

### Proponer Nuevas Funcionalidades

1. Fork el repositorio
2. Crea una rama: `git checkout -b feature/nueva-funcionalidad`
3. Commit cambios: `git commit -m 'Agregar nueva funcionalidad'`
4. Push: `git push origin feature/nueva-funcionalidad`
5. Abre un Pull Request

---

## 📄 Licencia

MIT License - Ver [LICENSE](LICENSE) para detalles.

---

## 👥 Autores

**Coordinación Académica**
- Email: coordinacion@institucion.edu
- GitHub: [@institucion](https://github.com/institucion)

---

## 🙏 Agradecimientos

- Equipo de coordinación académica
- Docentes participantes
- Comunidad de Python y Streamlit

---

## 📞 Soporte

¿Necesitas ayuda?

- 📧 Email: soporte@institucion.edu
- 💬 Slack: #analisis-curricular
- 📖 Wiki: https://github.com/institucion/analisis-microcurricular/wiki

---

## 🔄 Changelog

### v1.0.0 (2024-01-15)
- ✨ Primera versión estable
- ✅ Extracción de datos Excel
- ✅ Cálculo de indicadores
- ✅ Detección de 10 temáticas
- ✅ Dashboard Streamlit
- ✅ Generación de reportes PDF/HTML/Excel

---

**¡Gracias por usar el Sistema de Análisis Microcurricular!** 🎓
