# Inventario de Componentes

## Código Fuente

| Componente | Archivo | Descripción | Criticidad |
|------------|---------|-------------|------------|------------|
| extractor | `src/extractor.py` | Extracción de Excel | Alta |
| analyzer | `src/analyzer.py` | Análisis de competencias | Alta |
| validator | `src/validator.py` | Validación de calidad | Alta |
| report_generator | `src/report_generator.py` | Generación de reportes | Alta |
| thematic_detector | `src/thematic_detector.py` | Detección de temáticas | Media |
| dashboard | `dashboard/app.py` | Interfaz Streamlit | Alta |
| config | `config.py` | Configuración centralizada | Alta |

## Datos

| Componente | Ubicación | Descripción |
|------------|------------|--------------|
| Excel input | `data/raw/*.xlsx` | Archivos de entrada |
| SQLite | `data/microcurricular.db` | Base de datos local |
| Output | `data/output/*` | Reportes generados |
| Logs | `logs/*.log` | Archivos de log |

## Configuración

| Archivo | Descripción |
|---------|------------|
| `config.py` | Configuración global |
| `config_tendencias.json` | Configuración de tendencias |

## Tests

| Archivo | Cobertura |
|----------|----------|
| `tests/test_thematic_detector.py` | ThematicDetector |

## Documentación

| Archivo | Descripción |
|---------|------------|
| `docs/architecture/` | Arquitectura |
| `docs/backend/` | Backend |
| `docs/frontend/` | Frontend |
| `docs/database/` | Base de datos |
| `docs/apis/` | APIs |
| `docs/devops/` | DevOps |
| `docs/security/` | Seguridad |
| `docs/testing/` | Testing |
| `docs/analytics/` | Analítica |
| `docs/ux/` | UX/UI |

## Dependencias Externas

| Paquete | Versión | Uso |
|---------|--------|-----|
| streamlit | >=1.30.0 | Dashboard |
| pandas | >=2.0.0 | Datos |
| plotly | >=5.18.0 | Visualización |
| openpyxl | >=3.1.0 | Excel |
| scikit-learn | >=1.3.0 | ML (tendencias) |