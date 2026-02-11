# 📖 Guía de Usuario - Sistema de Análisis Microcurricular

## Tabla de Contenidos
1. [Inicio Rápido](#inicio-rápido)
2. [Preparación de Datos](#preparación-de-datos)
3. [Ejecución del Análisis](#ejecución-del-análisis)
4. [Uso del Dashboard](#uso-del-dashboard)
5. [Interpretación de Resultados](#interpretación-de-resultados)
6. [Casos de Uso Comunes](#casos-de-uso-comunes)
7. [Preguntas Frecuentes](#preguntas-frecuentes)

---

## Inicio Rápido

### 1. Instalación

```bash
# Clonar o descargar el proyecto
cd proyecto_analisis_microcurricular

# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

### 2. Configuración Inicial

1. Crea las carpetas si no existen:
   ```bash
   mkdir data\raw
   mkdir data\output
   ```

2. Coloca tus archivos Excel en `data/raw/`

3. (Opcional) Edita `config.py` para ajustar parámetros

---

## Preparación de Datos

### Formato de Archivos Excel

Tus archivos deben seguir esta estructura:

**Nombre de archivo:** `FormatoRA_NombrePrograma_CODIGO.xlsx`

**Hojas requeridas:**
- `Paso 2 Redacción competen` (header en fila 2)
- `Paso 3 Redacción RA` (header en fila 1)

**Hojas opcionales:**
- `Paso 4 Estrategias mesocurricu`
- `Paso 5 Estrategias micro`

### Validar Archivos Antes de Procesar

```bash
python validate_files.py
```

Este script te mostrará:
- ✅ Archivos válidos
- ⚠️ Archivos con advertencias
- ❌ Archivos con errores estructurales

**Ejemplo de salida:**
```
📄 FormatoRA_AdmonEmpresas_PBOG.xlsx
   ✅ OK
      Competencias: 5
      RA: 13

📄 FormatoRA_Derecho_PBOG.xlsx
   ⚠️  Advertencias:
      - Falta hoja "Paso 5 Estrategias micro"
      Competencias: 4
      RA: 12
```

---

## Ejecución del Análisis

### Análisis Completo (Recomendado)

```bash
python run_analysis.py
```

**Este script ejecuta:**
1. Validación de estructura de archivos
2. Extracción de datos de todos los programas
3. Cálculo de indicadores de calidad
4. Detección de temáticas emergentes
5. Generación de reportes individuales (HTML, JSON)
6. Generación de matrices consolidadas (Excel)

**Salida esperada:**
```
╔═══════════════════════════════════════════════════════════╗
║   SISTEMA DE ANÁLISIS MICROCURRICULAR                    ║
╚═══════════════════════════════════════════════════════════╝

📁 Encontrados 50 archivos para procesar

PROCESANDO PROGRAMAS
============================================================

[1/50]   📂 FormatoRA_AdmonEmpresas_PBOG.xlsx...
    ✅ Completado - Score: 88.5/100
       Temáticas: 4

[2/50]   📂 FormatoRA_IngSistemas_PBOG.xlsx...
    ✅ Completado - Score: 92.1/100
       Temáticas: 6

...

RESUMEN FINAL
============================================================

✅ Programas procesados exitosamente: 48
❌ Programas con errores: 2
📊 Total de archivos: 50

📁 Resultados guardados en: data\output
```

### Análisis de un Solo Programa

```python
from src.extractor import ExcelExtractor
from src.analyzer import CurricularAnalyzer

# Extraer datos
extractor = ExcelExtractor('data/raw/FormatoRA_AdmonEmpresas_PBOG.xlsx')
data = extractor.extract_all()

# Analizar
analyzer = CurricularAnalyzer(data)
indicadores = analyzer.generar_reporte_indicadores()

# Ver reporte
print(analyzer.generar_reporte_textual())
```

---

## Uso del Dashboard

### Iniciar Dashboard

```bash
streamlit run dashboard/app.py
```

El dashboard se abrirá automáticamente en tu navegador en `http://localhost:8501`

### Páginas del Dashboard

#### 🏠 Inicio
- **KPIs principales:** Total programas, competencias, RA, score promedio
- **Gráfico de cobertura de temáticas:** Barras horizontales mostrando cuántos programas abordan cada temática
- **Distribución de scores:** Ranking de programas por calidad

**Uso:**
- Obtén una vista general del estado de todos los programas
- Identifica rápidamente áreas de mejora institucional

#### 📊 Programas
- Selector de programa individual
- Score de calidad
- Balance de tipos de saber (gráfico de dona)
- Complejidad cognitiva (gráfico de dona)
- Temáticas detectadas
- Tabla completa de competencias

**Uso:**
1. Selecciona un programa del dropdown
2. Revisa el score de calidad (0-100)
3. Analiza el balance de Saber/SaberHacer/SaberSer
4. Verifica las temáticas abordadas
5. Exporta tabla de competencias si es necesario

#### 🏷️ Temáticas
- Selector de temática específica
- Lista de programas que la abordan
- Frecuencia en competencias vs. RA

**Uso:**
1. Selecciona una temática (ej: "SOSTENIBILIDAD")
2. Ve cuántos programas la abordan
3. Identifica programas que podrían incorporarla

#### 📈 Comparativa
- Selector múltiple de programas (2-5)
- Radar chart de indicadores
- Tabla comparativa

**Uso:**
1. Selecciona 2-5 programas
2. Compara visualmente en radar chart
3. Analiza tabla con datos exactos
4. Identifica fortalezas y debilidades relativas

---

## Interpretación de Resultados

### Score de Calidad (0-100)

**Rangos:**
- **90-100:** Excelente - Diseño curricular muy completo y robusto
- **75-89:** Bueno - Diseño sólido con áreas de mejora menores
- **60-74:** Aceptable - Requiere atención en algunos aspectos
- **< 60:** Necesita mejora - Revisar estructura y completitud

**Componentes del Score:**
- Completitud de datos (25%)
- Complejidad cognitiva (20%)
- Balance de tipos de saber (15%)
- Diversidad metodológica (15%)
- Cobertura de competencias (15%)
- Calidad de redacción (10%)

### Balance de Tipos de Saber

**Ideal:** Distribución balanceada ~33% cada uno

**Interpretación:**
- **Saber > 50%:** Demasiado teórico, falta práctica
- **SaberHacer > 50%:** Falta fundamentación teórica
- **SaberSer < 20%:** Falta énfasis en actitudes y valores

### Complejidad Cognitiva

**Ideal:** Mayoría en niveles Intermedio y Avanzado

**Niveles según Bloom:**
- **Básico (Recordar, Comprender):** Fundamentos
- **Intermedio (Aplicar, Analizar):** Aplicación práctica
- **Avanzado (Evaluar, Crear):** Pensamiento crítico y creación

**Meta:** > 40% en nivel Avanzado

### Temáticas Emergentes

**Interpretación:**
- Programa con 0-2 temáticas: Falta actualización curricular
- Programa con 3-5 temáticas: Buena pertinencia
- Programa con 6+ temáticas: Excelente alineación con tendencias

---

## Casos de Uso Comunes

### Caso 1: Identificar Programas sin Sostenibilidad

**Objetivo:** Listar programas que NO abordan sostenibilidad para planear actualización curricular

**Pasos:**
1. Ejecutar análisis completo
2. Abrir `data/output/matrices/matriz_tematicas.xlsx`
3. Filtrar columna "SOSTENIBILIDAD" = 0
4. Contactar a responsables de esos programas

### Caso 2: Comparar Programas de una Facultad

**Objetivo:** Benchmarking interno dentro de Facultad de Ingeniería

**Método Dashboard:**
1. Ir a página "Comparativa"
2. Seleccionar todos los programas de Ingeniería
3. Analizar radar chart
4. Identificar mejor programa como referencia

**Método Programático:**
```python
import pandas as pd

df = pd.read_excel('data/output/consolidado/indicadores_consolidados.xlsx')
ing = df[df['Programa'].str.contains('Ing')]
print(ing.sort_values('Score_Calidad', ascending=False))
```

### Caso 3: Generar Reporte para Acreditación

**Objetivo:** Crear evidencia documentada para proceso de acreditación

**Pasos:**
1. Ejecutar análisis del programa
2. Obtener reporte HTML de `data/output/reportes/`
3. Revisar indicadores específicos de acreditación
4. Adjuntar a carpeta de evidencias

---

## Preguntas Frecuentes

### ¿Qué hago si un archivo da error?

1. Ejecuta `python validate_files.py`
2. Revisa los errores específicos
3. Corrige la estructura del Excel:
   - Verifica nombres de hojas
   - Asegura que headers estén en filas correctas
   - Completa datos faltantes

### ¿Cómo agrego una nueva temática?

Edita `config.py`:

```python
TEMATICAS['NUEVA_TEMATICA'] = {
    'keywords': ['keyword1', 'keyword2', ...],
    'contexto_keywords': ['contexto1', ...]
}
```

### ¿Puedo cambiar los pesos del Score de Calidad?

Sí, edita en `config.py`:

```python
QUALITY_WEIGHTS = {
    'completitud': 0.30,  # Aumentar peso a completitud
    'complejidad_cognitiva': 0.20,
    ...
}
```

Asegura que los pesos sumen 1.0

### ¿Cómo exporto datos para Power BI?

Los archivos Excel consolidados son compatibles con Power BI:
- `data/output/consolidado/indicadores_consolidados.xlsx`
- `data/output/matrices/matriz_tematicas.xlsx`

Importa directamente a Power BI Desktop.

### ¿El sistema funciona con otro idioma?

Actualmente está optimizado para español. Para inglés:
1. Traduce keywords en `config.py`
2. Traduce verbos en `TAXONOMIA_BLOOM`

---

## Soporte

**Documentación adicional:**
- [README.md](../README.md) - Información general
- [diccionario_datos.md](diccionario_datos.md) - Estructura de datos
- [metodologia.md](metodologia.md) - Metodología de análisis

**Contacto:**
- Email: coordinacion@institucion.edu
- GitHub Issues: [Reportar problema](https://github.com/institucion/proyecto/issues)
