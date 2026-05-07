# Análisis de Datos y Analítica

## KPIs y Métricas

| KPI | Descripción | Fuente |
|-----|--------------|--------|
| Total competencias | Número total de competencias | Excel |
| Total RA | Número total de resultados de aprendizaje | Excel |
| Completitud | % de campos llenos | Calculado |
| Distribución saber | % Saber/SaberHacer/SaberSer | Calculado |
| Score calidad | Ponderación de métricas | Calculado |

## Dashboards

| Dashboard | Descripción |
|-----------|-------------|
| métricas globales | Vista general de programas |
| competencias | Detalle por competencia |
| resultados | Detalle por RA |
| calidad | Score de validación |

## Procesos ETL

```
INPUT (Excel) → EXTRACT → TRANSFORM → OUTPUT (HTML/PDF/Excel/JSON)
```

- **Extract:** Lee archivos Excel con pandas/openpyxl
- **Transform:** Procesa competencias, calcula métricas
- **Load:** Exporta a múltiples formatos

## Origen de Datos

- Archivos Excel (`data/raw/*.xlsx`)
- Formato institucional con hojas estandarizadas

## Transformaciones

1. Extracción de competencias y RA
2. Análisis de verbos (taxonomía Bloom)
3. Cálculo de distribución (Saber/SaberHacer/SaberSer)
4. Detección de temáticas
5. Validación de calidad
6. Generación de métricas

## Calidad de Datos

| Validación | Descripción |
|-----------|--------------|
| Completitud | ≥70% campos no vacíos |
| Verbos válidos | Verbos en lista taxonomía |
| Estructura | Columnas esperadas |

## Pendientes

- [ ] Dashboard analítico avanzado
- [ ] Series históricas
- [ ] Comparación entre programas
- [ ] Exporte a BI (Power BI, Tableau)