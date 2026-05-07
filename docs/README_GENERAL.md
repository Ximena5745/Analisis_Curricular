# README del Proyecto

## Sistema de Análisis Microcurricular

Análisis automatizado de diseños curriculares para programas educativos.

## Descripción

Sistema que procesa archivos Excel de formato institucional y genera:
- Reportes HTML, PDF, Excel, JSON
- Métricas de calidad curricular
- Dashboard interactivo Streamlit

## Estructura

```
analisis_curricular/
├── config.py              # Configuración global
├── main.py               # Punto de entrada CLI
├── requirements.txt      # Dependencias
├── src/                  # Módulos de procesamiento
│   ├── extractor.py
│   ├── analyzer.py
│   ├── validator.py
│   ├── report_generator.py
│   └── thematic_detector.py
├── dashboard/            # Dashboard Streamlit
│   └── app.py
├── data/
│   ├── raw/             # Archivos Excel de entrada
│   ├── processed/       # Datos procesados
│   └── output/         # Reportes generados
├── docs/                # Documentación
│   └── architecture/
└── tests/              # Tests unitarios
```

## Uso Rápido

```bash
# 1. Instalar dependencias
pip install -r requirements.txt

# 2. Colocar archivos Excel en data/raw/

# 3. Ejecutar análisis
python main.py

# 4. Dashboard (opcional)
streamlit run dashboard/app.py
```

## Requisitos

- Python 3.8+
- Windows/Linux/Mac

## Dependencias

- streamlit >= 1.30.0
- pandas >= 2.0.0
- numpy >= 1.24.0
- plotly >= 5.18.0
- openpyxl >= 3.1.0
- scikit-learn >= 1.3.0
- scipy >= 1.11.0

## Documentación Generada

| Documento | Descripción |
|----------|-------------|
| `architecture/SYSTEM_ARCHITECTURE.md` | Arquitectura general |
| `backend/BACKEND_ANALYSIS.md` | Análisis del backend |
| `frontend/FRONTEND_ANALYSIS.md` | Análisis del dashboard |
| `database/DATABASE_ANALYSIS.md` | Base de datos |
| `apis/API_DOCUMENTATION.md` | APIs y CLI |
| `devops/DEVOPS_ANALYSIS.md` | DevOps y despliegue |
| `security/SECURITY_AUDIT.md` | Seguridad |
| `testing/TESTING_ANALYSIS.md` | Testing y calidad |
| `analytics/DATA_ANALYTICS.md` | Analítica |
| `ux/UX_UI_ANALYSIS.md` | UX/UI |

## Estado del Proyecto

- **Madurez:** Desarrollo
- **Producción:** No desplegado
- **next Steps:** Ver `recommendations/IMPROVEMENT_ROADMAP.md`

## Contribuir

1. Fork del repositorio
2. Crear rama (`git checkout -b feature/nueva`)
3. Commit (`git commit -m 'Agrega feature'`)
4. Push (`git push origin feature/nueva`)
5. Pull Request

## Licencia

MIT