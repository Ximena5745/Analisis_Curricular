# Documentación de APIs

## Estado Actual

**Sin API REST formal.** Sistema opera en modo CLI y dashboard local.

## CLI (Interfaz de Línea de Comandos)

### Uso Principal

```bash
python main.py
```

Este comando:
1. procesa todos los archivos Excel en `data/raw/`
2. genera reportes en `data/output/`
3. muestra métricas en consola

### hooks Programáticos

Los módulos Python pueden importarse directamente:

```python
from src.extractor import extract_data
from src.analyzer import analyze_competencies
from src.validator import validate_competencies
from src.report_generator import generate_html_report

# Extracción
data = extract_data("data/raw/FormatoRA_Ejemplo.xlsx")

# Análisis
metrics = analyze_competencies(data)

# Validación
validation = validate_competencies(data)

# Reporte
generate_html_report(data, "output/reporte.html")
```

## Dashboard (Streamlit)

```bash
streamlit run dashboard/app.py
```

- Puerto predeterminado: 8501
- Sin autenticación (desarrollo)

## Entrada/Salida CLI

| Comando | Input | Output |
|---------|------|--------|
| `python main.py` | `data/raw/*.xlsx` | `data/output/*.{html,pdf,excel,json}` |

## Formato de Datos (JSON)

### Entrada esperada (Excel)

```
{
  "perfil_egreso": "...",
  "competencias": [
    {
      "numero": 1,
      "verbo": "analizar",
      "objeto": "sistemas de información",
      "finalidad": "para la toma de decisiones",
      "redaccion": "El estudiante analiza sistemas...",
      "tipo": "técnica"
    }
  ],
  "resultados": [
    {
      "competencia": 1,
      "numero": 1,
      "tipo_saber": "saber",
      "verbo": "identificar",
      "resultado": "Identifica los componentes..."
    }
  ]
}
```

### Salida JSON

```json
{
  "programa": "Nombre del programa",
  "fecha_analisis": "2024-01-15",
  "metricas": {
    "total_competencias": 5,
    "total_ra": 12,
    "completitud": 85.5,
    "distribucion": {
      "saber": 33.3,
      "saber_hacer": 33.3,
      "saber_ser": 33.4
    }
  },
  "validacion": {
    "aprobado": true,
    "errores": []
  }
}
```

## Pendientes

- [ ] API REST (FastAPI)
- [ ] Autenticación
- [ ] Rate limiting
- [ ] Documentación OpenAPI/Swagger
- [ ] Endpoints de métricas