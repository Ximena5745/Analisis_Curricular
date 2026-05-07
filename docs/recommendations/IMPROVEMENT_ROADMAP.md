# Hoja de Ruta de Mejoras

## Prioridades Corto Plazo (0-3 meses)

| Mejora | Prioridad | Estado | Notas |
|-------|----------|--------|-------|
| Tests unitarios extractor | Alta | Pendiente | Coverage crítico |
| Tests unitarios analyzer | Alta | Pendiente | Cobertura de métricas |
| Línea de comandos CLI mejorada | Media | Pendiente | Mejor UX |
| Soporte para Excel moderno | Media | Pendiente | Formato .xlsx |

## Prioridades Mediano Plazo (3-6 meses)

| Mejora | Prioridad | Estado | Notas |
|-------|----------|--------|-------|
| API REST (FastAPI) | Alta | Pendiente | Exponer funcionalidades |
| Autenticación | Media | Pendiente | Si se despliega públicamente |
| Dockerización | Media | Pendiente | Contenedor oficial |
| CI/CD con GitHub Actions | Media | Pendiente | Tests + lint |

## Prioridades Largo Plazo (6-12 meses)

| Mejora | Prioridad | Estado | Notas |
|-------|----------|--------|-------|
| Dashboard avanzado | Media | Pendiente | Más visualizaciones |
| Comparación entre programas | Baja | Pendiente | Análisis multi-programa |
| Integración con LMS | Baja | Pendiente | Moodle, Canvas, etc. |
| Módulo de tendencias IA | Baja | Pendiente | Predicción de tendencias |

## Roadmap Detallado

### Fase 1: Estabilidad (mes 1-3)

- [ ] Agregar 20+ tests unitarios
- [ ] Configurar pytest-cov (target 80%)
- [ ] Agregar ruff para linting
- [ ] Configurar GitHub Actions con tests

### Fase 2: Escalabilidad (mes 3-6)

- [ ] Crear API REST con FastAPI
- [ ] Dockerizar aplicación
- [ ] Agregar autenticación básica
- [ ] Pipeline CI/CD completo

### Fase 3: Modernización (mes 6-12)

- [ ] Dashboard con más features
- [ ] Comparador de programas
- [ ] Módulo de tendencias (IA)
- [ ] Despliegue a producción

## Recursos Requeridos

| Recurso | Estimación |
|---------|-----------|
| Desarrollo tests | 20 horas |
| API REST | 30 horas |
| Docker + CI/CD | 15 horas |
| Dashboard avanzado | 25 horas |

## Métricas de Éxito

- Coverage ≥ 80%
- API latencia < 200ms
- Docker image < 500MB
- CI/CD tiempo < 5 min