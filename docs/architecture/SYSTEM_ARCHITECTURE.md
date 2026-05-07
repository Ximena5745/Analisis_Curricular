# Arquitectura del Sistema de Análisis Microcurricular

## Resumen Ejecutivo

Sistema de análisis automatizado de diseños curriculares para programas educativos. Genera reportes HTML, PDF, Excel y JSON con métricas de calidad curricular.

## Arquitectura General

```
┌─────────────────────────────────────────────────────────────────┐
│                    SISTEMA DE ANÁLISIS                           │
├─────────────────────────────────────────────────────────────────┤
│  INPUT (Excel)  →  PROCESAMIENTO  →  OUTPUT (Reportes)              │
│  ─────────────   ──────────────   ──────────────────                  │
│  data/raw/         src/            data/output/                      │
│  *.xlsx           - extractor     - *.html                      │
│                   - analyzer      - *.pdf                      │
│                   - validator    - *.excel                    │
│                   - report_gen   - *.json                    │
│                                                                 │
│  DASHBOARD (Streamlit)                                           │
│  dashboard/app.py                                                │
└─────────────────────────────────────────────────────────────────┘
```

## Capas de Aplicación

| Capa | Módulo | Descripción |
|------|-------|-----------|
| Presentación | `dashboard/app.py` | Interfaz Streamlit interactiva |
| Lógica de Negocio | `src/analyzer.py`, `src/extractor.py` | Procesamiento y análisis |
| Validación | `src/validator.py` | Reglas de calidad curricular |
| Generación de Reportes | `src/report_generator.py` | Exportación multi-formato |
| Configuración | `config.py` | Parámetros centralizados |

## Tecnologías

| Componente | Tecnología | Versión |
|-----------|-----------|--------|
| Lenguaje | Python | 3.x |
| Datos | pandas, openpyxl | - |
| Dashboard | streamlit | - |
| Visualización | plotly | - |
| Base de datos | SQLite | - |
| LLM (opcional) | Anthropic API / OpenAI API | - |

## Flujo de Datos

```
1. Usuario copia archivos Excel en data/raw/
2. Sistema extrae datos de hojas Excel
3. Analizador procesa competencias y RA
4. Validador verifica calidad
5. Generador crea reportes
6. Dashboard permite exploración visual
```

## Dependencias Internas

- `config.py` → todos los módulos
- `src/extractor.py` → `src/analyzer.py` → `src/validator.py` → `src/report_generator.py`
- `src/thematic_detector.py` → `src/analyzer.py`

## Interfaces

| Interfaz | Descripción |
|----------|-------------|
| CLI | python main.py |
| Web | streamlit run dashboard/app.py |
| API | en desarrollo |

## Métricas de Calidad

| Métrica | Descripción |
|---------|-----------|
| completitud | % de campos llena |
| distribución | balance saber/saber hacer/saber ser |
|动词 |动词使用correcto en RA |
| trazabilidad | perfil → competencia → RA |

## Escalabilidad

- Procesamiento paralelo (configurable `MAX_WORKERS`)
- Cache de resultados
- Base de datos SQLite ligera
- Dashboard Streamlit escalable

## Seguridad

- Sin autenticación en modo desarrollo
- API keys opcionales para LLM
- Archivos locales (no exposición cloud)

## Mantenibilidad

- Configuración centralizada
- Modularidad por función
- Logs configurables
- Tests unitarios disponibles