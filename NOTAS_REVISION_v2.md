# Notas de revisión — versión 2 del artículo

**Fecha:** 3 de agosto de 2026
**Alcance:** Secciones 3 a Referencias. Secciones 1 y 2 no fueron modificadas.

---

## 1. Cálculos ejecutados sobre datos reales

Todos los estadísticos reportados en la Sección 4 se calcularon sobre el corpus real (50 archivos en `data/raw/FORMATOS RA CICLO UNO RC`), no se simularon.

**Entorno:** Python 3.10, `scipy 1.15.3`, `pandas`, `numpy`.
**Fuente:** `data/processed/datos_procesados.csv` (50 filas × 14 columnas).

| Cálculo | Función | Resultado |
|---|---|---|
| Correlación entre V1–V5 | `scipy.stats.spearmanr` | V3–V4: ρ=0,329 (p=0,0195); V3–V5: ρ=0,317 (p=0,0251); V4–V5: ρ=−0,017 (p=0,9044) |
| Diferencias entre sedes | `scipy.stats.kruskal` | V2: H=3,492 (p=0,322); V3: H=2,761 (p=0,430); V4: H=0,075 (p=0,995); V5: H=4,310 (p=0,230) |
| Tamaño del efecto | ε² = (H − k + 1)/(n − k) | Todos < 0,03 |
| Descriptivos por sede | `pandas.groupby` | Ver Tablas 9, 10, 11 |

**Figuras nuevas generadas:** `fig7_correlacion_spearman.png`, `fig8_kruskal_sedes.png` (en `data/output/`).

---

## 2. Correcciones de datos aplicadas

Dos tablas contenían cifras que no correspondían al corpus. Se verificaron contra los archivos crudos y se corrigieron.

### 2.1 Tabla 7 (antes Tabla 1) — Distribución por sede

La distribución previa no coincidía con el conteo real de archivos. Los **totales sí eran correctos** (50 archivos, 39 programas únicos, 217 competencias, 586 RA, 1.612 estrategias); el error estaba únicamente en el reparto entre sedes.

| Sede | Reportado antes | Real (verificado) |
|------|:---------------:|:-----------------:|
| VNAL | 20 | **22** |
| PBOG | 19 | **17** |
| PMED | 4 | **7** |
| HMED | 6 | **3** |
| HBOG | 1 | 1 |

Verificación reproducible:

```bash
ls *.xlsx | sed 's/\.xlsx$//' | rev | cut -c1-4 | rev | sort | uniq -c
```

### 2.2 Tabla 11 (antes Tabla 5) — Orientación a indicadores por sede

El orden estaba invertido respecto a los datos reales.

| Sede | Reportado antes | Real (media) |
|------|:---------------:|:------------:|
| PBOG | 79,2% | **81,9%** |
| PMED | 70,3% | **79,3%** |
| VNAL | 76,4% | **76,3%** |
| HMED | 84,1% | **54,6%** |
| HBOG | 61,5% | **100,0%** (n=1) |

El promedio global (77,8%) no cambia. Las Tablas 9 y 10 (V3 y V4) sí eran correctas.

---

## 3. Hallazgo que contradice la expectativa del estudio

**V4–V5 no correlacionan** (ρ = −0,017; p = 0,904).

El prompt de mejora anticipaba que los programas con menor trazabilidad tendrían también menor orientación a indicadores, lo que habría reforzado el argumento central. **Los datos no lo respaldan.** Se reportó el resultado tal como salió y se desarrolló su interpretación: trazabilidad e indicadores operan como sistemas desacoplados, porque los indicadores se declaran sobre las estrategias existentes y no sobre el conjunto de RA que debería cubrirse.

Este hallazgo negativo resultó más informativo que una confirmación: identifica el punto exacto del instrumento donde debe introducirse una restricción cruzada (ver R6 y Conclusiones).

---

## 4. Decisiones metodológicas tomadas

| Decisión | Justificación |
|---|---|
| Spearman en lugar de Pearson | Variables son proporciones acotadas [0,100], no normales; V3 con fuerte asimetría; robustez ante extremos en V4/V5 |
| Kruskal-Wallis en lugar de ANOVA | Grupos desiguales (22/17/7/3), incumplimiento de normalidad y homocedasticidad |
| HBOG excluida del contraste inferencial | n=1 no tiene varianza estimable; se trata como caso descriptivo |
| V1 excluida de correlaciones | Constante (100% en los 50 programas); varianza nula, coeficiente indefinido |
| Sin post-hoc de Dunn | Ninguna prueba global resultó significativa; aplicarlo inflaría el error tipo I |

---

## 5. Pendientes de verificación por la autora

1. **Concordancia interjueces (P1).** No se calculó. Se declaró como limitación en 3.1 con el protocolo recomendado para futuras aplicaciones (submuestra ≥20%, doble revisión ciega, Kappa, umbral ≥70%). Requiere decisión sobre si se ejecuta retrospectivamente.

2. **Criterios de exclusión del corpus.** La redacción de 3.1 describe la exclusión de posgrados y borradores. **Confirmar que corresponde a lo efectivamente ocurrido** y precisar el número de matrices excluidas por cada criterio, si está registrado.

3. **Listas de control de la Tabla 4.** Las listas 3, 4, 7, 10 y 11 se reconstruyeron desde `DOCUMENTACION.md`. Verificar que coinciden con la versión en producción de `src/`, particularmente la lista 11 (10 tendencias), que es configurable.

4. **Referencia Martínez (2006).** Los datos de volumen y páginas (Paradigma, 27(2), 7–33) no se verificaron con DOI en esta sesión. Confirmar antes del envío.

5. **CONPES 4144.** Verificar que la URL siga activa y que el número de documento sea el correcto.

6. **Literatura 2024–2026 sobre gobernanza de IA en currículo.** Sugerida en el prompt para reforzar D3–D4; no se incorporó por no disponer de fuentes verificadas. Queda pendiente si se desea actualizar esa parte de la Discusión.

7. **Corrección de lenguaje en Tablas 9–11.** Se eliminaron las etiquetas "mayor/menor cobertura" y se sustituyeron por descriptivos con n y desviación típica, dado que Kruskal-Wallis no detectó diferencias significativas. Revisar que no queden expresiones comparativas en otras partes del texto.

---

## 6. Numeración de tablas

Se renumeraron secuencialmente porque existían dos series solapadas (Metodología y Resultados usaban ambas 1–6).

| Nueva | Contenido | Sección |
|:---:|---|---|
| 1 | Estructura de hojas extraídas | Metodología |
| 2 | Filtros de validación de núcleos | Metodología |
| 3 | Niveles y verbos de Bloom | Metodología |
| 4 | **Taxonomías y listas de control** (nueva) | Metodología |
| 5 | Umbrales de cobertura por campo | Metodología |
| 6 | Stack tecnológico | Metodología |
| 7 | Corpus por sede (corregida) | Resultados |
| 8 | Desajustes horizontales | Resultados |
| 9 | Evaluabilidad por sede | Resultados |
| 10 | Trazabilidad por sede | Resultados |
| 11 | Orientación a indicadores (corregida) | Resultados |
| 12 | **Correlación de Spearman** (nueva) | Resultados |
| 13 | **Kruskal-Wallis** (nueva) | Resultados |
| 14 | Consistencia de asignaturas homónimas (nueva) | Resultados |
| 15 | Clasificación de pares similares (nueva) | Resultados |
| 16 | Tópicos latentes LDA (nueva) | Resultados |
| 17 | Tendencias globales (nueva) | Resultados |
| 18 | Cobertura del perfil por campo (nueva) | Resultados |
| 19 | Matriz de valor por área (nueva) | Resultados |
| 20 | Síntesis de indicadores | Resultados |

Figuras 1–6 sin cambios; **Figuras 7 a 11 nuevas**.

---

## 7. Reproducibilidad

El `.docx` se genera desde el `.md` mediante `md2docx.js`. El Markdown es la fuente única de verdad; el Word se reconstruye a partir de él.

Primera vez (instalar dependencia):

```bash
npm install docx
```

Cada vez que edites el Markdown:

```bash
node md2docx.js
```

El script requiere Node.js y el paquete `docx`. Si aparece `Cannot find module 'docx'`, falta ejecutar el `npm install` en la misma carpeta donde está el script.

---

# Adenda — Sección 4.8 (análisis de modelos)

Se agregó **R8** con los resultados de los módulos que estaban descritos en Metodología pero cuyos hallazgos no aparecían en Resultados: asignaturas compartidas, LDA, tendencias temáticas y cobertura de perfil.

## Datos nuevos extraídos

Se extrajo el **Paso 5** (microcurrículo) de los 50 Excel, que no estaba en los CSV procesados: **1.807 registros**, 759 denominaciones de asignatura, 5.780 núcleos temáticos válidos (13,9% de rechazo en limpieza).

## Hallazgos principales

| Análisis | Resultado | Área |
|---|---|---|
| Asignaturas compartidas | 168 (23,7%) concentran 61,4% de los registros | Planeación |
| Consistencia de contenido | 28,9% divergentes (sim < 0,60) pese a mismo nombre | Currículo |
| Homologación | 344 pares similares; 302 candidatos reales, 32 errores tipográficos, 10 duplicados por modalidad | Currículo |
| LDA | 10 tópicos con pesos entre 8,7% y 10,9% (oferta diversificada) | Mercadeo |
| Tendencias | IA: 79,5% de programas pero 3,3% de registros. Ciberseguridad: 5,1% | Mercadeo / Oferta |
| Cobertura de perfil | 89,4% global; 155 elementos sin respaldo; Áreas profesionales 75,7% | Aseguramiento |

## Anexo accionable generado

`data/output/anexos_accionables.xlsx` — 7 hojas con los listados nominales:

1. `1_Asignaturas_divergentes` (46) — requieren núcleo temático común
2. `2_Candidatas_homologacion` (302) — requieren validación disciplinar
3. `3_Errores_denominacion` (32) — corrección inmediata
4. `4_Brechas_perfil_egreso` (155) — decisión: incorporar contenido o retirar declaración
5. `5_Tendencias` (10)
6. `6_Topicos_LDA` (10)
7. `7_Asignaturas_compartidas` (168)

## Pendientes adicionales de verificación

8. **Diccionario de tendencias.** Las 10 tendencias y sus palabras clave las definí a partir de la lista documentada en `DOCUMENTACION.md`. Verificar que coincida con la configuración en producción y ajustar keywords si el equipo usa otras.

9. **Umbral de similitud 0,60.** Es el valor documentado para "similar". Los 302 candidatos a homologación dependen de él; bajarlo amplía la lista, subirlo la restringe. Conviene calibrarlo con una muestra validada por pares académicos.

10. **Brechas de perfil con score 0,00.** Casos como «Casinos», «Resorts», «Junta Directiva» pueden ser brechas reales o limitación del método: son términos muy cortos y específicos, difíciles de detectar por TF-IDF si el currículo los aborda con otro vocabulario. **Revisar manualmente una muestra antes de reportarlos como incumplimiento.**

11. **LDA con 10 tópicos.** El número está fijado por configuración, no optimizado por coherencia. Si se requiere rigor adicional, calcular coherencia (c_v) para k entre 5 y 20.

12. **Tópicos T3 y T10** contienen términos poco interpretables («antropoceno», «generalidades»). Revisar si conviene ampliar la lista de stop words académicas.

---

# Adenda 2 — Coherencia, redacción y accesibilidad

## Incoherencias corregidas (residuos del esqueleto Word)

| Ubicación | Decía | Ahora |
|---|---|---|
| Corpus de investigación | «tres matrices de Administración, Ingeniería Industrial y Derecho» | 50 matrices, 39 programas, 5 sedes + tabla de volumen por nivel |
| R1–R5, encabezados | «Se presentan mapas…», «Se reporta…» (modo plan) | Descripción de lo efectivamente medido |
| D3 | Una línea: «Se discute que la trazabilidad…» | Argumento desarrollado sobre legitimidad y control humano |
| D5 | Una línea: «Se discute el riesgo…» | Tres mecanismos de subjetivación observables en el propio método |
| Conclusión 1 | «Aporta una conceptualización operativa: IAg…» | Desarrollo del sentido de «infraestructura» y de «centrada en lo humano» |
| Metodología / D2 | 3 referencias sueltas en el cuerpo (formato Word) | Eliminadas; ya figuran en la lista final |

**Nota:** queda una referencia suelta en la línea 92 (sección 1, Introducción). No se tocó porque las secciones 1 y 2 están fuera del alcance autorizado. Conviene eliminarla al integrar.

## Reorganización de la sección 3

El orden anterior mezclaba niveles. Nuevo orden:

1. Diseño (tipo de estudio y alcance)
2. Intervención de la IAg + advertencia de circularidad *(nueva)*
3. Corpus → **Criterios de inclusión/exclusión** (antes estaban dentro de Diseño, separados del corpus)
4. Variables
5. Principios P1–P9 → **Confiabilidad de la revisión humana** (antes en Diseño; pertenece a P1)
6. Pipeline Pasos 1–7 → **Taxonomías** (antes interrumpía entre Paso 3 y Paso 4)
7. Limitaciones

También se renumeraron las tablas de Metodología por el cambio de posición: Umbrales 5→4, Stack 6→5, Taxonomías 4→6.

## Redundancias eliminadas

- **Desacople V4–V5**: se explicaba tres veces casi idéntico (R6, D2, Conclusiones). Ahora se desarrolla completo en R6; D2 y Conclusiones remiten a él y aportan solo la consecuencia teórica.
- **Argumento de escala**: duplicado entre el cierre de R8.4 y D4. R8.4 quedó factual (los listados se entregan como anexo); la elaboración conceptual quedó solo en D4.
- **Párrafo inicial de Metodología**: repetía el apartado «Intervención de la IAg». Se condensó y se le agregó una hoja de ruta de la sección.

## Numeración unificada

Las subsecciones de R8 estaban rotuladas 4.8.1–4.8.4 dentro de una sección llamada R8. Ahora son **R8.1–R8.4**, y las referencias cruzadas se actualizaron.

## Accesibilidad para lectores no académicos

Se conservó el rigor académico y se añadieron tres capas:

1. **Resumen ejecutivo** al inicio del documento (antes de Planteamiento): qué se hizo, por qué importa, cinco hallazgos en lenguaje llano, qué se puede y qué no se puede hacer con los resultados.
2. **Glosario** con tres tablas: términos curriculares, términos técnicos del análisis (qué hace cada método y para qué sirve aquí), códigos de sede y variables.
3. **Cinco cajas «En términos sencillos»** en los puntos de mayor densidad técnica: R6 (correlaciones), R7 (Kruskal-Wallis), R8.1 (asignaturas), R8.2 (tendencias), R8.3 (cobertura de perfil). Se renderizan como recuadros azules destacados.

## Pendiente adicional

13. **Sección 1 (Introducción).** Quedó fuera del alcance, pero ahora contrasta con el resto: mantiene el formato de referencias del Word y frases en modo esquema. Al integrar el artículo conviene homogeneizarla.

---

# Adenda 3 — Corrección de D5 tras auditoría del código

Una revisión del código fuente (`nucleos_cleaner.py`, `report_generator.py`, `config.py`, `analyzer.py`) demostró que la afirmación de D5 sobre el score académico **estaba sobredimensionada**. Se verificaron los cuatro puntos y se corrigió el artículo.

## Verificación realizada

| Afirmación previa del artículo | Verificación en código/datos | Veredicto |
|---|---|---|
| El score «desfavorece sistemáticamente a disciplinas prácticas» | `calcular_score_academico()` se ejecuta **después** de `es_nucleo_valido()`; no filtra, no reordena, no alimenta V1–V5. Único uso: columna informativa en `report_generator.py:544` | **Falso**: no hay canal causal |
| Es una «propiedad observable del procedimiento» | Cruce empírico sobre 5.780 núcleos: aplicadas (n=21 programas) vs teóricas (n=18). Mann-Whitney U=4.151.991, **p=0,565**; Δ medias = −0,003 | **No respaldado por los datos** |
| El score «penaliza práctica» | `practica` está en **ambas** listas (`nucleos_cleaner.py` líneas 48 y 57). «Taller de práctica clínica» → +0,15 −0,20 = 0,03 neto | **Error factual** |
| Clasificación ALTO/BAJO por umbral 0,5 | `UMBRAL_SCORE_ACADEMICO` existe en `config.py:337` pero **ninguna función lo consulta** | **Parámetro muerto** |
| `balance_saberes` afectado por el score | Se calcula sobre el campo declarado `TipoSaber` (`analyzer.py:94-102`) | **Sin relación** |

## Hallazgo nuevo derivado de la auditoría

Al calcular la distribución del score sobre el corpus real: **el 96% de los 5.780 núcleos obtiene score < 0,5** (media = 0,198). Si el umbral se activara, no produciría un sesgo sutil sino el colapso del corpus. Es evidencia de que el parámetro nunca fue calibrado contra datos reales — un caso concreto del riesgo de parámetros heredados de la intención de diseño.

## Cambios aplicados

**Metodología (Paso 2).** Se agregó el apartado «Estatuto de este score: informativo, no decisorio», que precisa el orden de ejecución, la ausencia de efecto sobre indicadores y el carácter no implementado del umbral. Se eliminó la afirmación falsa de que los núcleos «se clasifican como ALTO/BAJO».

**Tabla 6 (taxonomías).** Se marcó el solapamiento de *práctica* entre las listas 3 y 4, y se reformuló la columna de uso como «informativo, no decisorio». Se añadió un párrafo sobre la inconsistencia detectada.

**Limitaciones.** Se separó «sesgo heredado de los modelos» (sin evidencia, declarado como tal) de «sesgo inscrito en las listas de control» (con el resultado empírico p=0,565 y el solapamiento documentado).

**D5 reescrita.** Ahora distingue tres categorías con distinto estatuto probatorio:

1. **Mecanismo operativo** — la lista de 10 tendencias sí alimenta hallazgos reportados (Tabla 17, R8.2) y sí orienta decisiones. Es el único que actúa hoy.
2. **Riesgo latente** — el score académico, con las tres verificaciones (sin canal causal, sin sesgo empírico, con contradicción interna) y el análisis de qué ocurriría si el umbral se activara.
3. **Riesgo prospectivo** — la convergencia hacia el modelo, explícitamente declarada como hipótesis no contrastada por este diseño transversal.

Se añadió un cierre metodológico: el propio episodio de corrección ilustra que *es más fácil postular sesgos algorítmicos plausibles que verificar si operan*, y que la vigilancia epistémica (P7) exige el mismo estándar probatorio que los hallazgos positivos.

**Figura 12 nueva** — `fig12_auditoria_score.png`: boxplot del score por tipo de disciplina (sin diferencia significativa) y distribución con el umbral 0,5 marcado sobre el 96% que excluiría.

## Pendientes adicionales

14. **Depurar las listas del score.** Retirar *práctica* de una de las dos listas y separar el criterio «vocabulario académico» del criterio «formato pedagógico». Mientras el score sea informativo la urgencia es baja, pero es requisito previo a cualquier uso decisorio.

15. ~~**Decidir sobre `UMBRAL_SCORE_ACADEMICO`.**~~ **RESUELTO (3-ago-2026): desactivado.** Se retiró de `NUCLEOS_CONFIG` en `config.py` y se conservó comentado con el registro de la auditoría y las cuatro condiciones previas a cualquier reactivación. Verificado: ninguna función lo consultaba, `config.py` importa sin error y el pipeline de núcleos funciona igual. El artículo (Metodología, Paso 2 y D5) se actualizó para reportar la desactivación como medida adoptada.

16. **Clasificación disciplinar del cruce empírico.** La partición aplicadas/teóricas se hizo por palabras clave en el nombre del programa (21 vs 18). Es razonable pero no oficial: si existe una clasificación institucional por área de conocimiento, conviene rehacer el contraste con ella.


---

# Adenda 4 — Poda de redacción

## Secciones eliminadas

Se retiraron **Resumen ejecutivo** y **Glosario**, que se habían agregado al inicio sin haber sido solicitados y rompían el formato de artículo. También las cinco cajas «En términos sencillos» intercaladas en Resultados. La accesibilidad queda a cargo de la redacción, no de andamiaje añadido.

## Metatexto eliminado

Se suprimieron las frases que anunciaban el contenido en lugar de exponerlo: «Esta sección describe cómo se realizó el estudio. Se organiza en seis apartados…», «Este apartado presenta…», «Conviene precisar…», «Debe subrayarse…», «Cabe señalar…».

## Términos corregidos

| Antes | Ahora | Motivo |
|---|---|---|
| «El diseño metodológico **dialoga** con antecedentes» | «A diferencia de los antecedentes que…» | Metáfora imprecisa |
| «diseño mixto secuencial… (**QUAL → quan**)» | «Estudio mixto de predominio cualitativo» | Notación de especialista, innecesaria |
| «**Decisión curricular que habilita este hallazgo**» (×10) | «**Implicación**» | Fórmula repetida en cada resultado |
| «Corpus primario / Corpus complementario» | Un solo apartado «Corpus» | Subdivisión sin función |

## Condensación

| Apartado | Antes | Ahora |
|---|---|---|
| Apertura de Metodología | 2 párrafos de anuncio + 3 de diseño | 3 párrafos |
| Criterios de inclusión/exclusión | 5 párrafos | 4 párrafos breves |
| Principios P1–P9 | ~600 palabras | ~340 palabras |
| Confiabilidad de la revisión | 4 párrafos | 2 párrafos |
| D1, D2, D4, D5 (aperturas) | Preámbulos de encuadre | Entrada directa al argumento |
| Conclusiones | Glosas sobre los términos empleados | Solo el contenido |

**Extensión del cuerpo:** de ~16.400 a ~14.670 palabras (−11%), sin pérdida de hallazgos, tablas ni figuras.

## Verificado tras la poda

- 20 tablas en secuencia continua, sin referencias cruzadas rotas
- 14 figuras embebidas
- Estructura de encabezados completa (3. Metodología → 6. Conclusiones → Referencias)
- Sin residuos de metatexto ni de los términos corregidos
