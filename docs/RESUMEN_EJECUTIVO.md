# Resumen Ejecutivo del Sistema de Análisis Microcurricular

## 1. ¿Qué es este sistema?

Es una herramienta de **análisis automatizado de diseños curriculares** para programas educativos institucionales.

Permite procesar archivos Excel con la estructura curricular oficial y generar reportes automáticos con métricas de calidad.

## 2. ¿Qué problema resuelve?

Las instituciones educativas necesitan evaluar la calidad de sus programas curriculares, pero el análisis manual de competencias y resultados de aprendizaje es:

- **Tedioso**: cientos de celdas por programa
- **Propenso a errores**: revisión manual extensa
- **Inconsistente**: diferente interpretación entre evaluadores
- **Sin métricas objetivas**: sulit evaluar calidad globalmente

Este sistema automatiza el proceso completo.

## 3. ¿Quiénes lo usan?

- Dirección académica / Vicerrectorado académico
- Coordinadores de programa
- Docentes que diseñan currículos
- Evaluadores externos (pares académicos, acreditadores)

## 4. ¿Qué hace exactamente?

### Funcionalidades principales

| Funcionalidad | Descripción |
|--------------|-------------|
| **Lectura de archivos Excel** | Procesa formatos institucionales (.xlsx) con hojas estandarizadas |
| **Extracción de competencias** | Identifica y extrae competencias del formato |
| **Extracción de RA** | Extrae Resultados de Aprendizaje por competencia |
| **Análisis de verbos** | Verifica que los verbos sean válidos según taxonomía de Bloom |
| **Distribución de tipos de saber** | Calcula % Saberes: Saber / Saber Hacer / Saber Ser |
| **Detección de temáticas** | Identifica temáticas especiales (IA, Sostenibilidad, Innovación, etc.) |
| **Validación de calidad** | Verifica completitud mínima (70%), estructura, coherencia |
| **Generación de reportes** | Exporta a HTML, PDF, Excel, JSON |
| **Dashboard interactivo** | Visualización gráfica en navegador web |

### ¿Qué NO hace?

- No modifica el currículo original
- No genera nouveau contenido curricular
- No valida aspectos pedagógicos-subjectivos
- No es un sistema de gestión de notas/calificaciones

## 5. ¿Cómo funciona? (Flujo simple)

```
1. Usuario coloca archivos Excel en carpeta designada
2. Ejecuta el sistema (una línea de comando)
3. Sistema procesa automáticamente:
   - Lee cada archivo Excel
   - Extrae competencias y RA
   - Calcula métricas
   - Valida calidad
4. Genera reportes en segundos
5. Usuario revisa dashboard o reportes
```

**Tiempo promedio:** menos de 30 segundos por programa.

## 6. ¿Qué obtiene el usuario?

###Reportes generados

| Formato | Contenido |
|--------|-----------|
| **HTML** | Reporte visual navegable |
| **PDF** | Documento para compartir |
| **Excel** | Datos estructurados para manipulación |
| **JSON** | Integración con otros sistemas |

###Métricas incluidas

- Número total de competencias
- Número total de Resultados de Aprendizaje
- Porcentaje de completitud
- Distribución por tipo de saber
- Score de calidad general
- Listado de errores/advertencias
- Temáticas detectadas

## 7. Alcance del proyecto

### Dentro del alcance

- [x] Procesamiento de archivos Excel formato institucional
- [x] Extracción de competencias y RA
- [x] Análisis de taxonomía (verbos)
- [x] Cálculo de distribución de saberes
- [x] Detección de temáticas especiales
- [x] Validación de completitud
- [x] Generación de reportes multi-formato
- [x] Dashboard interactivo

### Outside del alcance (VERSION 1.0)

- [ ] API REST (versiones futuras)
- [ ] Autenticación de usuarios
- [ ] Base de datos centralizada
- [ ] Integración con LMS (Moodle, etc.)
- [ ] Análisis comparativo entre programas
- [ ] Recomendaciones automáticas de mejora

## 8. Beneficios concretos

| Beneficio | Antes | Después |
|----------|-------|--------|
| Tiempo de análisis | 4-8 horas por programa | 30 segundos |
| Consistencia | Depende del evaluador | Algoritmo uniforme |
| Métricas | Subjetivas/partiales | Objectives y completas |
| Reportes |_manual | Automáticos |
| Revisión | Una persona | Toda la institución |

## 9. ¿Qué necesitan para usarlo?

### Requisitos mínimos

- Computadora con Windows/Linux/Mac
- Python 3.8 o superior
- 4 GB de RAM

### Dependencias (incluidas en instalación)

- pandas (manejo de datos)
- plotly (gráficos)
- streamlit (dashboard)
- openpyxl (lectura Excel)

## 10. Roadmap / Próximos pasos

### Corto plazo (0-3 meses)

- Más tests automatizados
- Mejorar detección de errores

### Mediano plazo (3-6 meses)

- API para integraciones
- Dashboard avanzado
-Docker

### Largo plazo (6-12 meses)

- Módulo de comparación entre programas
- Integración con sistemas académicos
- Predicción de tendencias

## 11. Contacto y soporte

[Placeholder: agregar contacto]

---

**Versión del documento:** 1.0
**Fecha de creación:** Mayo 2026
**Próxima revisión:** [Fecha]