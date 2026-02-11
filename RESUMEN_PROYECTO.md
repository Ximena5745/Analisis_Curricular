# 📊 Resumen del Proyecto

## 🎯 Objetivo

Sistema completo de análisis automatizado para diseños microcurriculares de 50+ programas académicos. Permite consolidar, analizar y visualizar información curricular, detectar temáticas emergentes y generar reportes profesionales.

---

## ✨ Características Principales

### 1. 🔍 Análisis Automatizado
- ✅ Extracción de datos desde 50+ archivos Excel
- ✅ Consolidación en base de datos única
- ✅ Cálculo de 15+ indicadores de calidad curricular
- ✅ Validación de completitud y consistencia

### 2. 🏷️ Detección de Temáticas
Identifica 10 temáticas emergentes:
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

### 3. 📊 Visualización y Reportería
- Dashboard web interactivo (Streamlit)
- Reportes individuales por programa (PDF/HTML/JSON)
- Matriz consolidada Programas × Temáticas (Excel)
- Gráficos comparativos interactivos (Plotly)

### 4. 🎨 Dashboard Interactivo

**Páginas:**
- 🏠 **Inicio:** KPIs, cobertura temáticas, ranking programas
- 📊 **Programas:** Análisis individual detallado
- 🏷️ **Temáticas:** Filtrado por temática específica
- 📈 **Comparativa:** Comparación lado a lado (2-5 programas)

---

## 📦 Componentes del Sistema

### Módulos Core (src/)
| Módulo | Líneas | Funcionalidad |
|--------|--------|---------------|
| `extractor.py` | ~450 | Extracción de datos Excel |
| `thematic_detector.py` | ~400 | Detección de temáticas |
| `analyzer.py` | ~400 | Cálculo de indicadores |
| `validator.py` | ~250 | Validación de calidad |
| `report_generator.py` | ~250 | Generación de reportes |

### Scripts Principales
| Script | Propósito |
|--------|-----------|
| `run_analysis.py` | Análisis completo de todos los programas |
| `validate_files.py` | Validación de estructura de archivos |
| `ejemplo_uso.py` | Ejemplos de uso programático |

### Dashboard (dashboard/)
| Archivo | Descripción |
|---------|-------------|
| `app.py` | Aplicación Streamlit principal |

### Documentación (docs/)
| Documento | Contenido |
|-----------|-----------|
| `guia_usuario.md` | Guía completa paso a paso |
| `diccionario_datos.md` | Estructura de datos detallada |

---

## 📊 Indicadores Calculados

### Balance de Tipos de Saber
- Distribución Saber / SaberHacer / SaberSer
- Desviación estándar
- Estado de balance (ideal: ~33% cada uno)

### Complejidad Cognitiva (Taxonomía de Bloom)
- Distribución: Básico / Intermedio / Avanzado
- Nivel promedio (1-6)
- Índice de complejidad (0-100)

### Cobertura de Competencias
- % competencias con ≥1 RA
- Promedio RA por competencia

### Diversidad Metodológica
- Número de estrategias pedagógicas únicas
- % metodologías activas (ABP, casos, proyectos)

### Completitud de Datos
- % campos completos vs. total

### Score General de Calidad (0-100)
Ponderado por:
- Completitud (25%)
- Complejidad cognitiva (20%)
- Balance tipos saber (15%)
- Diversidad metodológica (15%)
- Cobertura competencias (15%)
- Calidad redacción (10%)

---

## 🔄 Flujo de Trabajo

```
1. PREPARACIÓN
   ├─ Colocar archivos Excel en data/raw/
   └─ python validate_files.py

2. ANÁLISIS
   └─ python run_analysis.py
       ├─ Extracción de datos
       ├─ Cálculo de indicadores
       ├─ Detección de temáticas
       └─ Generación de reportes

3. VISUALIZACIÓN
   ├─ streamlit run dashboard/app.py
   └─ Explorar resultados en navegador

4. RESULTADOS
   └─ data/output/
       ├─ reportes/      (HTML, JSON por programa)
       ├─ matrices/      (Excel consolidado)
       └─ consolidado/   (Indicadores generales)
```

---

## 📈 Salidas del Sistema

### Por Programa
- ✅ Reporte HTML visual
- ✅ Reporte JSON estructurado
- ✅ Score de calidad (0-100)
- ✅ Indicadores detallados
- ✅ Temáticas detectadas

### Consolidado
- ✅ Matriz Programas × Temáticas (Excel)
- ✅ Indicadores consolidados (Excel)
- ✅ Ranking de programas
- ✅ Estadísticas institucionales
- ✅ Dashboard interactivo

---

## 🛠️ Tecnologías Utilizadas

| Categoría | Tecnología |
|-----------|-----------|
| **Lenguaje** | Python 3.10+ |
| **Datos** | pandas, openpyxl, numpy |
| **Visualización** | Streamlit, Plotly, Matplotlib |
| **Reportes** | Jinja2, ReportLab, WeasyPrint |
| **Tests** | pytest, pytest-cov |
| **Opcional** | anthropic (Claude API) |

---

## 📊 Estadísticas del Proyecto

```
📁 Archivos creados: 20+
💻 Líneas de código: ~3,000+
📚 Módulos Python: 5
🧪 Tests unitarios: 10+
📖 Páginas documentación: 50+
⚙️ Scripts auxiliares: 3
🎨 Dashboard páginas: 4
```

---

## 🎯 Casos de Uso Clave

### 1. Coordinador Académico
**Objetivo:** Obtener panorama completo de 50 programas

**Flujo:**
1. Ejecutar `python run_analysis.py`
2. Abrir dashboard
3. Revisar KPIs generales
4. Exportar matriz de temáticas
5. Presentar a dirección académica

### 2. Director de Programa
**Objetivo:** Mejorar un programa específico

**Flujo:**
1. Abrir dashboard
2. Seleccionar programa en página "Programas"
3. Revisar score y balance
4. Identificar áreas de mejora
5. Comparar con programas similares

### 3. Comité de Acreditación
**Objetivo:** Evidencia para proceso de acreditación

**Flujo:**
1. Generar reporte HTML del programa
2. Revisar indicadores vs. estándares
3. Adjuntar a carpeta de evidencias
4. Mostrar dashboard en visita

### 4. Vicerrectoría Académica
**Objetivo:** Identificar brechas institucionales

**Flujo:**
1. Revisar matriz de temáticas
2. Identificar programas sin sostenibilidad/IA
3. Planear capacitación docente
4. Hacer seguimiento trimestral

---

## 🚀 Próximos Pasos Sugeridos

### Fase 1 - Corto Plazo (1-2 semanas)
- [ ] Procesar los 50 programas actuales
- [ ] Generar reportes iniciales
- [ ] Presentar resultados a stakeholders
- [ ] Recopilar feedback

### Fase 2 - Mediano Plazo (1-2 meses)
- [ ] Personalizar temáticas según necesidades
- [ ] Integrar con LLM (Claude/GPT) para análisis semántico
- [ ] Crear reportes PDF profesionales
- [ ] Exportar a Power BI

### Fase 3 - Largo Plazo (3-6 meses)
- [ ] Automatizar análisis trimestral
- [ ] Crear API REST para integración
- [ ] Implementar seguimiento histórico
- [ ] Dashboard de tendencias temporales

---

## 🏆 Beneficios Esperados

### Eficiencia
- ⏱️ De **días a minutos** en análisis curricular
- 🤖 Automatización 95% del proceso manual
- 📊 Reportes generados automáticamente

### Calidad
- ✅ Análisis estandarizado y consistente
- 📈 Identificación objetiva de brechas
- 🎯 Datos para toma de decisiones

### Impacto
- 🌍 Alineación con tendencias globales
- 🎓 Mejora continua curricular
- 📋 Evidencia para acreditación

---

## 📞 Soporte y Contacto

**Desarrollador:** Coordinación Académica
**Email:** coordinacion@institucion.edu
**Versión:** 1.0.0
**Fecha:** 2024

---

## 📄 Licencia

MIT License - Ver [LICENSE](LICENSE) para más detalles

---

**🎉 ¡El sistema está listo para usar!**

Lee [INICIO_RAPIDO.md](INICIO_RAPIDO.md) para comenzar en 5 minutos.
