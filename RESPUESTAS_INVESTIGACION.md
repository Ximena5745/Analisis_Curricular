# Respuestas para Artículo Científico — Versión Consolidada

> Respuestas confirmadas para las 11 preguntas de investigación.  
> Basado en el análisis del código fuente y respuestas del autor.

---

## 1. DISEÑO DE INVESTIGACIÓN

**Tipo:** **Design Science Research (DSR)** combinado con **evaluación aplicada institucional**.

Se construyó un artefacto tecnológico (sistema de análisis microcurricular basado en NLP y ML) que fue evaluado empíricamente con datos reales de una institución de educación superior. Sigue el proceso DSR (Hevner et al., 2004): conciencia del problema → sugerencia → desarrollo → evaluación → conclusión.

**Objetivo principal:** **Ambos** — proponer un modelo metodológico para la evaluación curricular automatizada **y** validarlo empíricamente mediante su aplicación a 50 programas académicos reales de 3 facultades.

**Preguntas de investigación (RQ):**

- **RQ1:** ¿Es posible cuantificar objetivamente la calidad de un diseño microcurricular mediante indicadores compuestos derivados de NLP y ML (TF-IDF, BM25, LDA)?
- **RQ2:** ¿Qué tan cubierto está el perfil de egreso declarado por el contenido curricular real, y cómo puede medirse y visualizarse esta brecha de forma sistemática?
- **RQ3:** ¿Qué patrones de similitud y divergencia curricular existen entre programas de una misma institución, y cómo pueden clasificarse para recomendar acciones (unificar, homologar, coordinar)?
- **RQ4:** ¿Los tópicos latentes extraídos mediante LDA revelan una estructura temática del currículo más rica que la detección basada exclusivamente en palabras clave fijas?

---

## 2. UNIDAD DE ANÁLISIS Y ALCANCE EMPÍRICO

### Programas analizados

- **Total:** **50 programas académicos** (archivos en `data/raw/FORMATOS RA CICLO UNO RC`)
- **Niveles:** Pregrado y Posgrado (especializaciones y maestrías)

### Las 3 facultades participantes

| Sigla | Facultad | Programas detectados |
|-------|----------|---------------------|
| **FIDI** | Facultad de Ingeniería, Diseño e Innovación | IngIndustrial, IngSistemas, IngSoftware, Ing.Telecomunicaciones, DiseñoIndustrial, DiseñoGrafico, DiseñoInteractivo, DiseñoModas, DiseñoDigital, Matemáticas, TecnolDesarrolloSoftware, TecnolGestAmbiental, TecnolGuianzaTuris, TecnolLogística, TecnolMercadeoyPublicidad |
| **FNGS** | Facultad de Negocios, Gestión y Sostenibilidad | AdmonEmpresas, ContPub, NegIntl, MercadeoyPublicidad, AdmonPub, AdmonHotelGastro, LCS, Esp.LogisGestCadAbast, EspGerMercadeo, EspGerTributaria, EspGerenProyInteligenciaNegocios, MGEM, MCE, M.GerTalentoHumano |
| **FSCC** | Facultad de Sociedad, Cultura y Creatividad | Derecho, ComunicacionSocial, ComunicacionDigital, ComunicacionSocialPeriodismo, LicEducacionBasicaPrimaria, LicEduInfantil, MEDSTEM, MInnovacionEducativa, TecProfJudicial, EspGestionEducativa, Esp.NeuropsicologiaEscolar, ECENJA, ProfGSSL |

### Sedes y modalidades cubiertas

| Código | Sede | Modalidad | Programas detectados |
|--------|------|-----------|---------------------|
| PBOG | Bogotá | Presencial | ~22 programas |
| PMED | Medellín | Presencial | ~7 programas |
| VNAL | Nacional | Virtual | ~18 programas |
| HBOG | Bogotá | Híbrido | 1 programa |
| HMED | Medellín | Híbrido | ~3 programas |

Se incluyeron **todas las sedes y modalidades disponibles** sin selección.

---

## 3. DATOS REALES UTILIZADOS

### Origen de los archivos

**Mixto:** Los archivos provienen de una combinación de:
- Microcurrículos **vigentes** (diseños curriculares oficiales del período actual)
- **Proyectos de rediseño** curricular (versiones en proceso de actualización)

### Preprocesamiento

Se realizó **limpieza manual previa** de los archivos Excel antes de ejecutar el pipeline automatizado. Esta limpieza incluyó:
- Corrección de nombres de hojas con variaciones ortográficas
- Ajuste de filas de encabezados inconsistentes
- Eliminación de filas de cálculo o totales que interfieren con la lectura

### Uniformidad estructural

El sistema incluye mecanismos de tolerancia:
- Detección fuzzy de hojas (`_find_sheet()` con strip + startswith)
- Normalización de nombres de columna (sin tildes, minúsculas, sin caracteres especiales)
- Detección automática de fila de encabezados

Aun así, ningún archivo de los 50 fue descartado automáticamente; todos pudieron procesarse con éxito.

### Exclusión por calidad

No se excluyeron programas por mala calidad. Todos los archivos disponibles en la carpeta fueron procesados. Los casos con problemas de calidad se reflejan como alertas en la hoja 15 del Excel maestro, pero no se descartaron del análisis.

---

## 4. INTERVENCIÓN DE IA GENERATIVA

### Modelos utilizados

| Herramienta | Tipo | Uso en el proyecto |
|------------|------|-------------------|
| **Claude (Anthropic)** | Asistente conversacional | Generación de código, diseño de arquitectura, depuración, refactorización, documentación, análisis de resultados |
| **GitHub Copilot** | Autocompletado de código | Aceleración de codificación en tiempo real, generación de funciones repetitivas |

### Ciclo de uso

La IA Generativa se empleó en **todo el ciclo de desarrollo**:

1. **Diseño de arquitectura**: definición de la estructura de módulos, patrones de diseño, configuración centralizada
2. **Generación de código**: escritura de las 9 clases/funciones principales del pipeline
3. **Depuración y corrección de errores**: identificación y resolución de bugs (KeyError en sampling, NameError en dashboard, timeout en Excel maestro)
4. **Refactorización**: migración de funciones duplicadas a módulos compartidos, optimización de rendimiento
5. **Documentación**: generación de esta documentación técnica
6. **Análisis de resultados**: interpretación de métricas, identificación de patrones, generación de conclusiones

### Ciclos iterativos

**6+ ciclos de refinamiento** documentados en el historial de cambios del proyecto:

| Ciclo | Alcance |
|-------|---------|
| Sprint 0 | Correcciones de base: columnas esperadas, headers, extracción de sede/modalidad |
| Sprint 1 | Módulo de limpieza de núcleos con 7 filtros en cascada |
| Sprint 2 | Análisis de cobertura de perfil con TF-IDF híbrido |
| Sprint 3 | Detección de asignaturas compartidas (Jaccard + coseno) |
| Sprint 4 | Excel maestro 15 hojas + LDA + dashboard |
| P0 | Remedios transversales: propagación de metadatos, integración de módulos |
| P1 | Refactorización: mover constantes a config.py, invertir ADR-04, eliminar duplicados |
| Rendimiento | Muestreo estratificado, caché de núcleos, fix bug sampling |

### Control humano de las salidas de IA

Todas las sugerencias y código generados por IA fueron **revisados y validados por un desarrollador humano** antes de integrarse. El humano:
- Verificaba la lógica implementada
- Ejecutaba tests para confirmar funcionamiento
- Ajustaba parámetros y umbrales según criterio experto
- Rechazaba soluciones subóptimas y pedía alternativas

### Documentación de cambios

Los cambios entre versiones del sistema **no se documentaron formalmente en un registro curricular** (no hay un antes/después de la matriz curricular). Sin embargo, el historial de git y los sprints reportados constituyen una trazabilidad del desarrollo del *sistema*.

---

## 5. OPERACIONALIZACIÓN DE VARIABLES

### Nivel de reporte

| Variable | Escala | Nivel Programa | Nivel Asignatura | Nivel Matriz |
|----------|--------|:-:|:-:|:-:|
| Score de Calidad | 0–100 | ✓ | ✗ | ✓ |
| Cobertura de Perfil de Egreso | 0–100% | ✓ | ✗ | ✓ |
| Complejidad Cognitiva (Bloom) | Nivel 1–6 | ✓ | ✓ | ✓ |
| Balance Saber / SaberHacer / SaberSer | 0–100% | ✓ | ✓ | ✓ |
| Diversidad Temática (Shannon) | 0–100 | ✓ | ✗ | ✓ |
| Cobertura de Tendencias | 0–100% | ✓ | ✓ | ✓ |
| Asignaturas Compartidas | Conteo | ✓ | ✓ | ✓ |
| Núcleos Válidos / Rechazados | Conteo + Score | ✓ | ✓ | ✓ |
| Tópicos LDA | Categórico | ✓ | ✗ | ✓ |
| Score Académico de Núcleos | 0.0–1.0 | ✓ | ✓ | ✓ |

### Normalización

Todos los indicadores se normalizan a escala **0–100** (o 0.0–1.0 para scores individuales de núcleos y cobertura) para permitir comparación directa entre programas.

### Umbrales de calidad

| Indicador | Bueno | Regular | Crítico |
|-----------|-------|---------|---------|
| Score calidad global | >70 | 50–70 | <50 |
| Cobertura de perfil | >60% | 35–60% | <35% |
| Balance SaberHacer | >30% | 20–30% | <20% |
| Balance SaberSer | >8% | 5–8% | <5% |
| Complejidad Avanzada (Bloom 5-6) | >30% | 15–30% | <15% |
| Score académico de núcleos | >0.5 | 0.3–0.5 | <0.3 |

Estos umbrales están definidos en `config.py` y en la lógica de alertas del Excel maestro (hoja 15). Son **propuestos por el sistema** basados en criterios de calidad curricular general; no son umbrales institucionales formales del Politécnico Grancolombiano.

---

## 6. MÉTODOS ANALÍTICOS

### Tipo de análisis

| Tipo | Presente | Evidencia |
|------|:--------:|-----------|
| **Descriptivo** | ✓ | Métricas, distribuciones, estadísticas por programa en dashboard y Excel maestro |
| **Comparativo** | ✓ | Intra-sede (mismo programa en distintas sedes), inter-programa (asignaturas similares), por modalidad, por nivel |
| **Evaluativo** | ✓ | Contra umbrales de calidad, alertas automáticas (hoja 15), clasificación CUBIERTO/BRECHA |

### Comparaciones ejecutadas

- **Intra-sede:** Un mismo programa (ej: Contaduría Pública) en sedes Bogotá y Medellín → similitud Jaccard + coseno
- **Inter-programa:** Asignaturas de programas distintos (ej: Ing. Sistemas vs. Ing. Software) → pares similares con recomendaciones
- **Por modalidad:** Presencial vs. Virtual vs. Híbrido
- **Por nivel:** Pregrado vs. Posgrado

### Métricas agregadas

Sí — promedios, desviaciones estándar, valores máximos/mínimos, top/bottom performers. El Excel maestro incluye una hoja de resumen ejecutivo con todos los programas en una tabla.

### Visualización

Dashboard Streamlit con gráficos interactivos Plotly: barras, heatmaps, radares, diagramas Sankey, dendrogramas, mapas de calor.

---

## 7. VALIDACIÓN DEL SISTEMA

### Estado actual: **Validación planeada como trabajo futuro**

### Validación existente (técnica)

| Tipo | Ítems | Resultado |
|------|-------|-----------|
| Tests unitarios | 5 tests (nucleos_cleaner, perfil_coverage, shared_subjects, topic_modeler, report_generator) | 5/5 pasan |
| Tests detección temática | 8 tests (inicialización, detección Sostenibilidad, IA, texto vacío, normalización, contexto, múltiples keywords, DataFrame) | 8/8 pasan |
| Test de integración | 12 checks con 3 archivos reales (extracción, núcleos, cobertura perfil, shared subjects, LDA) | 12/12 pasan |
| Ejecución completa | 50 programas reales | 50/50 procesados |
| Verificación manual de filtros | Casos "Expansión A/B" → rechazado, "Análisis financiero" → aceptado, "Fundamentación teórica" → aceptado | Correcto |

### Validación NO realizada (trabajo futuro)

- ❌ Validación por **expertos curriculares** de los reportes generados
- ❌ Contraste de resultados contra el **currículo oficial** en papel
- ❌ Medición de **precisión/recall** de componentes (filtros de núcleos, cobertura de perfil, detección de tendencias)
- ❌ **Validación inter-evaluador** (humano vs. sistema)
- ❌ **Uso en decisiones reales** de ajuste curricular

### Plan de validación propuesto

1. **Fase 1 — Validación técnica** (completada): tests automatizados + ejecución con datos reales
2. **Fase 2 — Validación por expertos** (pendiente): 3-5 expertos curriculares revisan reportes de 10 programas seleccionados y califican: precisión, utilidad, relevancia
3. **Fase 3 — Validación de impacto** (pendiente): medir si las recomendaciones del sistema llevaron a cambios curriculares concretos

---

## 8. RIESGO, GOBERNANZA Y CONTROL HUMANO

### Controles humanos implementados

| Control | Descripción | Ubicación |
|---------|-------------|-----------|
| Revisión de núcleos | Panel en dashboard para excluir núcleos inválidos manualmente; cambios en tiempo real | `pagina_cobertura()` |
| Trazabilidad de cobertura | Cada elemento CUBIERTO muestra qué asignatura y qué texto generaron la máxima similitud | `perfil_coverage_analyzer.py` |
| Filtros transparentes | Cada núcleo rechazado registra la razón exacta del rechazo | `nucleos_cleaner.py` |
| Score interpretable | El score académico muestra qué palabras contribuyeron (positivas/negativas) | `calcular_score_academico()` |
| Validación humana de IA | Todo el código generado por Claude/Copilot fue revisado por un desarrollador antes de integrarse | Proceso de desarrollo |

### Rechazo de sugerencias de IA

Durante el desarrollo, se rechazaron o modificaron sugerencias de IA en casos como:
- Implementaciones ineficientes (reemplazadas por enfoques más performantes)
- Soluciones que no respetaban la estructura de datos real
- Enfoques que no consideraban edge cases (archivos sin ciertas hojas, datos vacíos)

### Sesgos y errores detectados y corregidos

| Error | Síntoma | Corrección |
|-------|---------|------------|
| KeyError en sampling | `groupby().apply().reset_index(drop=True)` perdía columna `programa` | Reemplazado por loop explícito con `pd.concat()` |
| NameError en dashboard | Funciones `_es_nucleo_valido`/`_limpiar_nucleo` eliminadas del módulo pero 4 call sites no migrados | Migrados a `nucleos_cleaner.limpiar_nucleo` y `es_nucleo_valido(...)[0]` |
| Timeout Excel maestro | `comparar_inter_programa` en O(n²) con 3,135 subjects | Muestreo estratificado con `max_asignaturas=500` |
| Archivo 0 bytes | Pipeline incompleto — Excel maestro se escribía antes de poblar datos | Reordenación: extraer primero, luego generar |
| Falseamiento en ADR-04 | Bloom se evaluaba antes que Nivel Dominio | Inversión: Nivel Dominio primero, Bloom como fallback |

---

## 9. ARTEFACTO TECNOLÓGICO

### Estado actual: **Prototipo funcional**

El sistema está completamente desarrollado, con código funcional, tests, configuración centralizada y documentación. Sin embargo:
- **No está en producción institucional**
- **Solo el equipo de desarrollo lo ha utilizado**
- Requiere que el usuario coloque archivos Excel en la carpeta `data/raw/` y ejecute `run_analysis.py` o `streamlit run dashboard_tematico.py`

### Componentes del artefacto

| Componente | Propósito | Estado |
|-----------|-----------|--------|
| Pipeline de análisis | Procesamiento batch de archivos → indicadores → reportes | Funcional, probado con 50 programas |
| Dashboard Streamlit | Visualización interactiva con 10 páginas | Funcional, listo para uso |
| Excel maestro | 15 hojas consolidadas | Generado correctamente (peso ~905 KB) |
| Reportes HTML/JSON | Por programa | Generados correctamente |
| Tests automatizados | 13 tests de validación | 13/13 pasan |

### Uso en sesiones reales

El dashboard **no ha sido usado en sesiones reales** con tomadores de decisiones o analistas curriculares. Está diseñado para ello pero no se ha desplegado en un entorno de uso continuo.

### Exportación de reportes

Los reportes se generan localmente en `data/output/`. No se ha verificado su uso en procesos de toma de decisiones institucionales.

---

## 10. ALCANCE Y LIMITACIONES

### Lo que el sistema SÍ hace

- Procesa archivos Excel con estructura específica de 5 hojas del Politécnico Grancolombiano
- Limpia y filtra núcleos temáticos con 7 filtros en cascada
- Calcula 6 indicadores de calidad (score compuesto 0–100)
- Mide cobertura del perfil de egreso con TF-IDF + BM25 híbrido
- Detecta asignaturas compartidas (intra-sede, inter-programa, idénticas)
- Descubre tópicos latentes con LDA
- Detecta 10 tendencias globales por keywords
- Genera Excel maestro con 15 hojas
- Visualiza todo en dashboard Streamlit

### Lo que el sistema NO puede hacer actualmente

1. **Procesar otros formatos** — solo Excel con la estructura específica de 5 hojas. Cualquier variación requiere ajustar `config.py`
2. **Corpus pequeños** — LDA requiere mínimo 5 documentos; cobertura de perfil mínimo 3
3. **Análisis multilingüe** — stop words, keywords, verbos Bloom y expresiones regulares están en español
4. **Análisis longitudinal** — solo procesa un corte transversal (un período)
5. **Clasificación automática por facultad** — no existe mapping de programas a facultades
6. **Calibración automática** — umbrales y pesos son fijos en configuración
7. **Dashboard multiusuario** — Streamlit es monousuario
8. **API REST** — no hay interfaz de servicios

### Limitaciones por tipo de programa

- **Programas con pocas asignaturas (< 10)**: corpus pequeño → métricas inestables, LDA no entrenable
- **Programas con núcleos vacíos**: detección temática y cobertura degradadas
- **Áreas muy especializadas**: vocabulario no cubierto por keywords de tendencias
- **Programas con RA mal redactados**: detección Bloom cae a default (Comprender, nivel 2)

### Limitaciones por calidad del dato

- Archivos sin hoja de perfil de egreso → cobertura de perfil no disponible
- Columnas de bloques curriculares ausentes → no es posible clasificar por bloque (Institucional/Disciplinar/Electivo)
- Filas de totales no filtradas correctamente → ruido en conteos
- Tildes inconsistentes en nombres de asignatura → afectan matching exacto

### Dependencia del idioma

ALTA — el sistema está diseñado para español. Componentes con dependencia lingüística:
- Stop words (36–33 términos)
- Keywords de tendencias (10 grupos, ~150 términos)
- Verbos Bloom (54 verbos en 6 niveles)
- Patrones de exclusión de núcleos (34 iniciadores inválidos, 18 patrones de instrucción)
- Palabras académicas (30 positivas, 21 negativas)

Portar a otro idioma requiere traducir/reemplazar todas estas listas en `config.py` y los módulos correspondientes.

---

## 11. ÉTICA Y DATOS

### Estatus de los datos

- **Los datos curriculares son propiedad institucional** del Politécnico Grancolombiano
- **No se anonimizaron** los nombres de programas ni asignaturas
- **No se requiere anonimización para publicación** — los nombres reales de programas pueden aparecer en el artículo

### Consentimiento institucional

No se ha gestionado consentimiento formal para publicación. Se recomienda:
1. Obtener autorización por escrito de la Vicerrectoría Académica o Dirección de Innovación y Calidad Curricular
2. Verificar que los datos no incluyan información sensible de estudiantes o docentes
3. Confirmar que los diseños microcurriculares no tengan restricciones de propiedad intelectual

### En el código actual

- No hay capa de anonimización
- Los reportes generados incluyen nombres reales
- Los logs registran nombres de archivos y programas

---

## Resumen de parámetros del sistema

| Componente | Parámetros ajustables | Dónde se definen |
|-----------|----------------------|------------------|
| Extracción | 5 nombres de hoja, 7 header rows, columnas esperadas (7+9+6+16+11) | `config.py:EXCEL_SHEETS`, `HEADER_ROWS`, `EXPECTED_COLUMNS` |
| Filtros de núcleos | min_len=4, max_len=150, min_words=2, 18 patrones, 34 iniciadores, 30 palabras +, 21 palabras −, contamination_if=0.15, umbral_académico=0.5 | `config.py:NUCLEOS_CONFIG` + `nucleos_cleaner.py` |
| Cobertura de perfil | max_features=1500, ngram=(1,3), sublinear_tf=True, pesos_top3=[0.5,0.3,0.2], peso_coseno=0.6, peso_bm25=0.4, umbral_fallback=0.35, 9 umbrales_por_campo | `config.py:UMBRAL_COBERTURA`, `UMBRALES_POR_CAMPO`, `perfil_coverage_analyzer.py:TFIDF_KWARGS` |
| Asignaturas compartidas | umbral_identico=0.95, umbral_similar=0.60, max_asignaturas=500, max_features_intra=200, max_features_inter=300 | `shared_subjects_analyzer.py` |
| LDA | n_topics=10, n_top_words=15, max_features_cv=500, min_df=2, max_df=0.85, ngram=(1,2), max_iter=100, learning_method='batch' | `topic_modeler.py` |
| Calidad | 6 pesos (0.25+0.20+0.15+0.15+0.15+0.10), score_redacción_placeholder=80 | `config.py:QUALITY_WEIGHTS` |
| Temáticas | 10 grupos, ~150 keywords, ~20 context_keywords | `config.py:TEMATICAS` |

---

## Glosario de siglas

| Sigla | Significado |
|-------|-------------|
| RA | Resultado de Aprendizaje |
| LDA | Latent Dirichlet Allocation |
| TF-IDF | Term Frequency — Inverse Document Frequency |
| BM25 | Best Matching 25 (modelo de ranking probabilístico) |
| NLP | Natural Language Processing |
| ML | Machine Learning |
| DSR | Design Science Research |
| ADR | Architecture Decision Record |
| FIDI | Facultad de Ingeniería, Diseño e Innovación |
| FNGS | Facultad de Negocios, Gestión y Sostenibilidad |
| FSCC | Facultad de Sociedad, Cultura y Creatividad |
| HTD | Horas de Trabajo Directo |
| HTI | Horas de Trabajo Independiente |
| KPI | Key Performance Indicator |

---

## Referencias

1. Hevner, A. R., March, S. T., Park, J., & Ram, S. (2004). Design science in information systems research. *MIS Quarterly*, 28(1), 75–105.
2. Blei, D. M., Ng, A. Y., & Jordan, M. I. (2003). Latent Dirichlet Allocation. *Journal of Machine Learning Research*, 3, 993–1022.
3. Robertson, S. E., & Walker, S. (1994). Some simple effective approximations to the 2-Poisson model for probabilistic weighted retrieval. *SIGIR '94*, 232–241.
4. Shannon, C. E. (1948). A mathematical theory of communication. *Bell System Technical Journal*, 27(3), 379–423.
5. Liu, F. T., Ting, K. M., & Zhou, Z. H. (2008). Isolation Forest. *ICDM '08*, 413–422.
6. Anderson, L. W., & Krathwohl, D. R. (2001). *A taxonomy for learning, teaching, and assessing: A revision of Bloom's taxonomy of educational objectives*. Longman.
7. Pedregosa, F., et al. (2011). Scikit-learn: Machine Learning in Python. *Journal of Machine Learning Research*, 12, 2825–2830.
8. Jaccard, P. (1901). Étude comparative de la distribution florale dans une portion des Alpes et du Jura. *Bulletin de la Société Vaudoise des Sciences Naturelles*, 37, 547–579.
9. Salton, G., & Buckley, C. (1988). Term-weighting approaches in automatic text retrieval. *Information Processing & Management*, 24(5), 513–523.
10. Van der Aalst, W. (2016). *Process Mining: Data Science in Action*. Springer.
