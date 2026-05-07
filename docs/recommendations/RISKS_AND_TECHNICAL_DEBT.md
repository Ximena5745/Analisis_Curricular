# Riesgos y Deuda Técnica

## Riesgos Técnicos

| Riesgo | Severidad | Probabilidad | Impacto | Mitigación |
|--------|----------|---------------|---------|------------|
| Datos corruptos en Excel | Alta | Media | Crítico | Validación en extractor |
| Formato Excel incompatible | Alta | Media | Alto | Detección de formato |
| MemoryError con archivos grandes | Media | Baja | Alto | Procesamiento parcial |
| Dependencias obsoletas | Media | Media | Medio | Actualización regular |
| Sin tests = regression | Alta | Alta | Crítico | Agregar tests |

## Deuda Técnica

| Item | Descripción | Prioridad | Esfuerzo |
|------|-----------|----------|----------|
| Tests unitarios | Coverage bajo | Alta | 20h |
| Documentación API | No existe | Alta | 10h |
| Linter/format | No configurado | Media | 5h |
| Type hints | Incompleto | Media | 15h |
| CI/CD | No existe | Alta | 15h |
| Docker | No existe | Media | 8h |

## Hallazgos

- Sistema funcional pero en desarrollo
- Sin tests para módulos críticos
- Sin pipeline CI/CD
- Sin Docker oficial

## Recomendaciones

1. Priorizar tests antes de nuevas features
2. Configurar ruff + mypy
3. Crear API REST para extensibilidad
4. Dockerizar para reproducibilidad