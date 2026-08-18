# PROMPT MEJORADO: Análisis Microcurricular con IA

## 🎯 OBJETIVO GENERAL
Crear un artículo educativo que documente el proceso completo de **análisis microcurricular automatizado** usando IA, desde la extracción de datos hasta la generación de insights, dirigido a académicos y diseñadores curriculares.

---

## 📋 ESTRUCTURA DEL ARTÍCULO

### **1. INTRODUCCIÓN**
- **Contexto**: Retos actuales en análisis curricular manual
- **Propuesta de valor**: Cómo la IA acelera y mejora el análisis microcurricular
- **Alcance**: Programas académicos analizados, periodos, ubicaciones (PBOG, HMED, VNAL, PMED)
- **Pregunta de investigación**: ¿Cómo puede la IA identificar patrones de coherencia curricular a escala?

---

### **2. METODOLOGÍA PASO A PASO** (incluir capturas y código)

#### **Fase 1: Extracción y Estructuración de Datos**
- **Fuente**: Carpeta `/data/raw/FORMATOS RA CICLO UNO RC`
- **Archivos base**: FormatoRA_*.xlsx (múltiples programas académicos)
- **Estructura de datos**: 
  - Nombre programa
  - Ubicación (sedes)
  - Resultados de aprendizaje (RA)
  - Competencias asociadas
  - Unidades temáticas
  - Horas de dedicación
- **Herramientas**: Python + Pandas (lectura y limpieza)
- **Output**: Dataset estructurado en formato .csv o base de datos

#### **Fase 2: Integración IA (Claude API)**
- **Tareas de IA**:
  - Análisis de semántica en resultados de aprendizaje
  - Identificación automática de competencias transversales
  - Detección de redundancias y vacíos curriculares
  - Clasificación de contenidos por nivel de complejidad (Bloom's taxonomy)
- **Prompts específicos**: 
  - Extracción de competencias
  - Análisis de coherencia vertical (ciclo progresivo)
  - Identificación de alineación con resultados de aprendizaje
- **Validación**: Comparación IA vs. análisis manual

#### **Fase 3: Análisis Exploratorio**
- **Estadísticas descriptivas**:
  - Distribución de RA por programa
  - Cobertura de competencias genéricas vs. específicas
  - Variabilidad entre sedes
  - Densidad de contenidos
- **Visualizaciones**:
  - Tablas comparativas por sede
  - Gráficos de distribución de competencias
  - Mapas de coherencia curricular (diagrama de flujo)
  - Heatmaps de alineación RA-Competencias

#### **Fase 4: Generación de Reportes**
- **Outputs**:
  - Resumen ejecutivo por programa
  - Reporte de coherencia curricular
  - Matriz de fortalezas y brechas
  - Recomendaciones de mejora
- **Formato**: Documentos Word, PDF, dashboards interactivos

---

### **3. RESULTADOS** (datos concretos — sección vigente del artículo, no una plantilla genérica)

La sección de Resultados del artículo real (`articulo_curricular_IA.md`, `## 4. RESULTADOS`) ya no sigue el esquema genérico 3.1/3.2/3.3 de las versiones anteriores de este prompt. Su estructura actual, que debe mantenerse y no sustituirse, es:

- **R1–R5**: una variable cuantitativa por resultado — V1 coherencia vertical, V2 coherencia horizontal, V3 evaluabilidad, V4 trazabilidad, V5 orientación a indicadores — cada una con media, desviación típica, tabla por sede e "Implicación" (qué decisión habilita el hallazgo).
- **R6–R7**: estadística inferencial — correlaciones de Spearman entre variables (R6) y comparaciones Kruskal-Wallis/Mann-Whitney entre sedes y niveles de formación (R7).
- **R8**: los módulos del panel analítico de seguimiento curricular, organizados por área de decisión — **estos son los 7 ítems del dashboard (`dashboard_tematico.py`) que todo texto nuevo de Resultados debe cubrir, con contexto (qué mide y con qué método) y resultado (cifra real, no placeholder)**:

  | Ítem del dashboard | Dónde vive en el artículo |
  |---|---|
  | Tipo de saber (detalle por programa) | R2, ampliación |
  | Familias curriculares | R8.1 |
  | Minería de Texto y Análisis Semántico | R8.1 / R8.2 |
  | Cobertura temática (diversidad/densidad) | R8.2 |
  | Tendencias y Brechas | R8.2 |
  | Cobertura de perfil | R8.3 |
  | Taxonomías Curriculares e Integración | R8.4 |
  | — Síntesis (matriz de valor por área) | R8.5 |

**Regla de fundamentación (obligatoria):** cada cifra de R8 debe salir de ejecutar el código del proyecto sobre el corpus real (`analisis_tematico_avanzado.py` para tendencias/cobertura temática/minería de texto; las funciones de cálculo de `dashboard_tematico.py` para tipo de saber, familias curriculares y taxonomías/Bloom; `src/perfil_coverage_analyzer.py` para cobertura de perfil), nunca inventarse ni generalizarse a partir de un ejemplo. Si al ejecutar un módulo el resultado es inconsistente con lo que el resto del corpus sugiere (como ocurrió con la clasificación por dominio taxonómico, ver R8.4), eso se reporta como hallazgo de validación del propio proyecto, no se descarta ni se maquilla.

**Regla de tono (obligatoria):** el artículo debe ser comprensible para profesionales de áreas distintas a la analítica de datos o el diseño curricular. Cada término técnico (TF-IDF, entropía/diversidad, similitud de coseno, dominio taxonómico, p-valor) se explica en una frase simple la primera vez que aparece en una sección. Las cifras y tablas se mantienen con todo su rigor; lo que cambia es que cada cifra va acompañada de una frase que explica qué significa para alguien que no maneja el método.

---

### **4. IMPLEMENTACIÓN TÉCNICA** (sección opcional para desarrolladores)

#### **Stack Tecnológico**
- **Lenguaje**: Python 3.9+
- **Librerías**: Pandas, Openpyxl, Anthropic SDK
- **Procesamiento**: Lectura masiva Excel → normalización → API IA
- **Modelo IA**: el configurado en `config.py` (`CONFIG['LLM_MODEL']`) — no fijar un nombre de modelo en este prompt ni en el artículo, porque queda desactualizado en cuanto el proyecto actualiza de versión; referenciar siempre la fuente de verdad (`config.py`)
- **Visualización**: Matplotlib, Seaborn, Plotly (HTML interactivo)

#### **Código Clave** (fragmentos explicados)
```python
# Ejemplo: Lectura de formatos RA
import pandas as pd

archivos = glob.glob('data/raw/FORMATOS RA CICLO UNO RC/*.xlsx')
datos_completos = []

for archivo in archivos:
    df = pd.read_excel(archivo)
    # Extracción de información relevante
    datos_completos.append(df)

df_master = pd.concat(datos_completos)
```

```python
# Ejemplo: Integración con Claude IA (Sonnet)
from anthropic import Anthropic

client = Anthropic()

prompt = f"""
Analiza estos resultados de aprendizaje y:
1. Identifica las competencias clave
2. Evalúa alineación con objetivos del programaShow 
3. Propone mejoras de coherencia
4. Clasifica por nivel de complejidad (Bloom's taxonomy)

Datos:
{df_master.to_string()}
"""

response = client.messages.create(
    model=CONFIG['LLM_MODEL'],  # definido en config.py, no hardcodear el nombre aqui
    max_tokens=3000,
    messages=[{"role": "user", "content": prompt}]
)
```

---

### **5. DISCUSIÓN Y CONCLUSIONES**

- **Ventajas encontradas**: 
  - Automatización reduce tiempo de análisis 70-80%
  - Identifica patrones humanos podrían pasar por alto
  - Escalable a todas las facultades/programas
  
- **Limitaciones**: 
  - Requiere validación manual de hallazgos críticos
  - Sensible a calidad de entrada de datos
  
- **Recomendaciones futuras**:
  - Integración con sistema de gestión curricular
  - Análisis predictivo de resultados estudiantiles
  - Evaluación de impacto tras implementar mejoras

---

## 📊 ESPECIFICACIONES DE CONTENIDO

| Aspecto | Especificación |
|---------|---|
| **Público objetivo** | Académicos, diseñadores curriculares, administradores educativos |
| **Tono** | Técnico pero accesible, educativo |
| **Extensión** | 3,000-4,000 palabras + figuras |
| **Figuras esperadas** | 8-12 (tablas, gráficos, diagramas) |
| **Secciones** | Introducción, Metodología, Resultados, Implementación, Conclusiones |
| **Datos base** | Mínimo 10-15 programas de las carpetas raw |
| **Coherencia** | Narrativa progresiva: problema → solución → resultados → impacto |

---

## 🛠️ TAREAS CONCRETAS A REALIZAR

1. **Explorar archivos Excel**: Identificar estructura común de datos
2. **Extraer y normalizar**: Crear dataset único con todos los programas
3. **Aplicar análisis IA**: Generar insights sobre coherencia curricular
4. **Crear visualizaciones**: Gráficos y tablas que ilustren hallazgos
5. **Redactar artículo**: Integrar metodología, código y resultados
6. **Validar coherencia**: Revisar que cada sección conecte con la anterior

---

## 📁 ARCHIVOS A GENERAR

- `articulo_final.docx` → Documento Word con formato editorial
- `datos_procesados.csv` → Dataset limpio consolidado
- `análisis_IA_resultados.json` → Insights generados por IA
- `visualizaciones.pptx` → Figuras profesionales (opcional)
- `codigo_reproducible.py` → Script completo del análisis

---

## ✅ CRITERIOS DE CALIDAD

- ✓ Directo: Sin divagaciones, cada párrafo aporta
- ✓ Coherente: Flujo lógico introducción → metodología → resultados
- ✓ Con imágenes: Mínimo 1 visual por sección
- ✓ Con análisis: Datos concretos, no especulaciones
- ✓ Educativo: Explica "cómo" y "por qué", no solo "qué"
- ✓ Reproducible: Código compartible, metodología clara
