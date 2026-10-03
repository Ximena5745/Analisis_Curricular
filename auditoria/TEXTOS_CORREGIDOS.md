# Textos corregidos del artículo

Versiones aprobadas por la autora durante la auditoría (verificación 2026-10-02 13:21). Las mismas están en el Word y en el Excel (hoja Textos_corregidos).

## Resumen (versión corregida)

Estudio aplicado de métodos mixtos sobre 50 matrices curriculares de 39 programas académicos: 341 resultados de aprendizaje únicos (deduplicados en cada matriz), 391 estrategias mesocurriculares declaradas, 1.757 registros de asignatura y 50 perfiles profesionales y 50 perfiles ocupacionales, analizados mediante cinco variables de coherencia y trazabilidad, minería de texto, modelado temático y contraste estadístico exploratorio. Resultados. La evaluabilidad alcanzó [A7, pendiente] %, y el [A8, pendiente; recálculo de auditoría ≈ 86 %] % de los resultados de aprendizaje presentó una ruta documentada hasta una estrategia con instrumento de evaluación. El 5,0 % de los elementos del perfil generó alertas de posible falta de respaldo curricular (10,0 % en el campo de actuación), el 9,4 % de las asignaturas homónimas mostró contenidos divergentes y la inteligencia artificial apareció en el 79,5 % de los programas, pero solo en el 3,5 % de los registros de asignatura.

*Las cifras entre corchetes siguen pendientes de la etapa de Resultados (A7, A8). El 3,5 % de IA usa la lista estricta de términos con coincidencia de palabra completa sobre 1.757 registros; requiere confirmar la lista con la autora.*

## Corpus

Las fuentes son 50 matrices curriculares en Excel de 39 programas académicos, ofrecidos en Bogotá, Medellín y en la oferta virtual nacional, bajo tres modalidades (presencial, virtual e híbrida), que representan el 63 % de la oferta institucional en renovación curricular [fuente, fecha de corte]. Ocho programas se ofrecen en más de una sede con matriz propia: Contaduría Pública, Negocios Internacionales e Ingeniería Industrial en tres sedes, y Administración de Empresas, Derecho, Diseño Gráfico, Ingeniería de Sistemas y Mercadeo y Publicidad en dos. Por ello, la unidad de análisis es el programa-sede (Tabla 1). Cada matriz curricular se organiza según la secuencia metodológica definida institucionalmente: Paso 1, perfil profesional y ocupacional; Paso 2, competencias; Paso 3, resultados de aprendizaje; Paso 4, estrategias mesocurriculares; Paso 5, microcurrículo.

**Tabla 1. Composición del corpus por nivel de formación**

| Nivel de formación | Programas | Matrices (programa-sede) | Competencias | RA únicos | Estrategias meso declaradas |
|---|---|---|---|---|---|
| Profesional universitario¹ | 23 | 34 | 169 | 257 | 276 |
| Tecnología | 5 | 5 | 20 | 34 | 41 |
| Técnica profesional | 1 | 1 | 5 | 6 | 7 |
| Pregrado | 29 | 40 | 194 | 297 | 324 |
| Especialización | 5 | 5 | 13 | 19 | 34 |
| Maestría | 5 | 5 | 15 | 25 | 33 |
| Posgrado | 10 | 10 | 28 | 44 | 67 |
| Total | 39 | 50 | 222 | 341 | 391 |

*¹ Incluye tres licenciaturas. Los resultados de aprendizaje únicos se deduplican dentro de cada matriz, porque un mismo RA se registra una vez por cada competencia a la que aporta (586 registros en total). Las 391 estrategias declaradas se vinculan a los RA mediante 1.612 registros RA–estrategia.*

En el componente microcurricular se procesaron 1.757 registros de asignatura², correspondientes a 709 denominaciones únicas (normalizadas sin distinguir mayúsculas, tildes ni puntuación). Las asignaturas declaran 6.671 núcleos temáticos, identificados por la numeración con que cada matriz los enumera (2.815 únicos; mediana de 4 por asignatura). El modelo se aplica igual a ambos niveles de formación, aunque los resultados se diferencian porque propósitos, alcance y profundidad varían.

*² Incluye 141 espacios electivos, cuyo contenido depende de la electiva elegida y que, por tanto, no declaran núcleos temáticos.*

Se incluyeron todas las matrices que habían completado los cinco pasos y contaban con autorización, y se excluyeron las versiones incompletas, duplicadas o anteriores al ciclo examinado, así como las hojas de respaldo de los archivos. Los ocho programas ofrecidos en más de una sede comparten los mismos resultados de aprendizaje y la mayor parte de sus núcleos temáticos entre sus 19 matrices, por lo que las unidades no son plenamente independientes. En consecuencia, los descriptivos se calculan sobre las 50 unidades programa-sede, las cifras por programa sobre los 39 programas, y la inferencia se limita a asociaciones exploratorias.

## Procedimiento – Etapa 2

Etapa 2. Identificación de los núcleos temáticos. Cada asignatura declara sus núcleos temáticos como una lista numerada en texto libre. Los núcleos se separaron por su numeración, de modo que un núcleo que ocupa varias líneas o contiene comas se conserva como unidad; en las cuatro celdas sin numeración se tomó cada línea como un núcleo. Se obtuvieron 6.671 núcleos (2.815 únicos) en 1.616 asignaturas; un control de calidad (celdas vacías, solo números o texto de instrucciones de la plantilla) no identificó entradas inválidas. A los núcleos se les asigna un puntaje orientativo, no decisorio, que contrasta vocabulario académico con vocabulario de formato, y un detector de valores atípicos señala núcleos anómalos frente al corpus (Liu et al., 2008).

## Procedimiento – Etapa 3

Etapa 3. Calidad del diseño. Cada programa recibe un puntaje de 0 a 100 que pondera la exigencia de sus resultados de aprendizaje (40 %), el equilibrio entre tipos de saber (30 %) y la variedad de estrategias didácticas (30 %). La completitud de la matriz y la proporción de competencias con resultados de aprendizaje asociados se verificaron en todos los programas (100 % en las 50 matrices); como el formato de la matriz garantiza su cumplimiento, se reportan como condiciones verificadas y no intervienen en el puntaje.

Para ubicar cada resultado de aprendizaje en una escala de exigencia, las matrices emplean dos taxonomías: Bloom en su versión clásica (48,1 % de los resultados de aprendizaje únicos) y una adaptación con aportes de Krathwohl (BAK, 51,9 %); 26 de las 50 matrices combinan ambas. Las dos distinguen los dominios cognitivo, procedimental y actitudinal, pero solo BAK asigna escalas propias a los dos últimos, al reconocer que dominar un procedimiento o consolidar una actitud siguen progresiones distintas de las del conocimiento conceptual (Tabla 4).

Cada nivel declarado se traduce a una escala común de 1 a 6 según su posición en la progresión de su propio dominio, con la expresión nivel = 1 + (posición − 1) × 5 / (número de niveles − 1). Así, en Bloom y en el dominio cognitivo de BAK cada nivel conserva su posición (de 1 a 6); en el dominio procedimental de BAK los cuatro niveles equivalen a 1; 2,67; 4,33 y 6, y en el actitudinal los cinco niveles equivalen a 1; 2,25; 3,5; 4,75 y 6. Esta equivalencia entre escalas de distinta longitud permite comparar programas que emplean sistemas diferentes y constituye un supuesto del método. El índice de exigencia de cada programa corresponde al nivel medio de sus resultados de aprendizaje únicos, expresado de 0 a 100.

**Tabla 4. Sistemas de clasificación empleados en las matrices**

| Taxonomía | Resultados de aprendizaje únicos | Dominio cognitivo | Dominio procedimental | Dominio actitudinal |
|---|---|---|---|---|
| Bloom | 164 (48,1 %) | Conocimiento, Comprensión, Aplicación, Análisis, Síntesis, Evaluación | (mismos seis niveles) | (mismos seis niveles) |
| BAK | 177 (51,9 %) | Conocimiento, Comprensión, Aplicación, Análisis, Síntesis, Evaluación | Imitación, Manipulación, Precisión, Control | Percepción, Responder, Valorar, Organizar, Caracterizar |
| Total | 341 (100 %) |  |  |  |

*Nota: 26 de las 50 matrices combinan ambas taxonomías; 21 emplean solo Bloom y 3 solo BAK. Cada nivel se traduce a una escala común de 1 a 6 según su posición en la progresión de su dominio.*

## Procedimiento – Etapa 4

Etapa 4. Cobertura del perfil profesional y ocupacional. Cada celda de los nueve campos del Paso 1 se trata como un elemento, sin dividir su texto, lo que da 988 elementos. Los campos se agrupan en cuatro categorías: perfil (profesional y ocupacional), saberes (Saber, SaberHacer y SaberSer), campo de actuación (áreas profesionales, tareas profesionales y poblaciones de actuación) y valor agregado (Tabla 5). Cada elemento se compara con los contenidos de las asignaturas de su programa: nombre, indicadores de logro, núcleos temáticos y actividades de evaluación. Se excluyen los saberes asociados y la redacción de los resultados de aprendizaje, porque se formulan a partir del propio perfil y harían circular la comparación.

La similitud combina dos medidas léxicas: el coseno TF-IDF ponderado de los tres documentos más afines (pesos 0,5, 0,3 y 0,2), con un peso de 0,6, y la puntuación BM25 máxima normalizada (Robertson y Zaragoza, 2009), con un peso de 0,4. El elemento se marca como alerta de brecha si su puntaje no alcanza el umbral de su campo. Los umbrales difieren según la extensión y el vocabulario de cada campo, y los resultados se agregan por grupo sin modificar el umbral con que se evaluó cada elemento. Las alertas priorizan casos para revisión; no prueban la ausencia de respaldo curricular.

**Tabla 5. Umbrales de cobertura por campo y grupo del perfil**

| Grupo | Campo del perfil | Elementos | Umbral |
|---|---|---|---|
| Perfil | Perfil profesional | 50 | 0,28 |
|  | Perfil ocupacional | 50 | 0,28 |
|  | Subtotal | 100 |  |
| Saberes | Saber | 222 | 0,35 |
|  | SaberHacer | 222 | 0,35 |
|  | SaberSer | 222 | 0,32 |
|  | Subtotal | 666 |  |
| Campo de actuación | Áreas profesionales | 57 | 0,38 |
|  | Tareas profesionales | 60 | 0,38 |
|  | Poblaciones de actuación | 53 | 0,32 |
|  | Subtotal | 170 |  |
| Valor agregado | Valor agregado | 52 | 0,30 |
| Total |  | 988 |  |

*Nota: cada elemento corresponde a una celda del Paso 1. El corpus de comparación de cada programa incluye solo los contenidos de sus asignaturas.*

## Procedimiento – Etapa 5

Etapa 5. Asignaturas compartidas. El sistema compara las asignaturas de todos los programas por coincidencia de nombre y por similitud de contenidos (núcleos temáticos e indicadores de logro), solo entre programas distintos, lo que detecta dos situaciones opuestas: asignaturas homónimas que enseñan cosas distintas y asignaturas con nombres diferentes que cubren lo mismo. Se excluyen los espacios electivos, que no declaran contenido propio. Una asignatura homónima se considera divergente cuando la similitud media entre sus versiones es inferior a 0,60, umbral operativo no calibrado con revisión experta.

## Procedimiento – Etapa 6

Etapa 6. Análisis temático. Un modelo LDA identifica, sin una lista predefinida, los temas que atraviesan los contenidos declarados (Blei et al., 2003). Cada documento es una asignatura con sus núcleos temáticos depurados y lematizados (1.192 asignaturas, una matriz por programa para no duplicar la oferta multisede). El número de tópicos (k = 13) maximizó la coherencia (NPMI) y la estabilidad entre k = 5 y k = 30. Como LDA es inestable con textos breves, el modelo se estima por consenso de diez réplicas con semillas distintas, cuyos tópicos equivalentes se promedian: dos consensos independientes comparten el 59 % de sus palabras principales, frente al 22 % de un LDA simple. Los tópicos se interpretan con fines descriptivos. Un segundo análisis mide la presencia de diez temas de agenda global —inteligencia artificial, sostenibilidad y transformación digital, entre otros— y, desde 2026, quince tendencias del sector empresarial y educativo, por coincidencia de palabras completas con una lista de términos ajustable por la institución.

**Temas de agenda global (núcleos + indicadores; 1.616 asignaturas sin electivas; 39 programas)**

| Tema | Asignaturas | Programas |
|---|---|---|
| Calidad y mejora continua | 429 | 39 |
| Sostenibilidad | 219 | 34 |
| Liderazgo y habilidades blandas | 206 | 35 |
| Globalización | 171 | 32 |
| Innovación y emprendimiento | 130 | 35 |
| Transformación digital | 105 | 24 |
| Inteligencia artificial | 86 | 32 |
| Ética y responsabilidad social | 74 | 31 |
| Análisis de datos y BI | 71 | 26 |
| Gestión del cambio | 1 | 1 |

*Nota: conteo por palabra completa y sin tildes. La base de la cifra de IA del Resumen (con o sin texto de RA) está pendiente (A11).*

## Procedimiento – Etapa 7

Etapa 7. Reportes y consulta. Por cada matriz programa-sede se generan un informe navegable (HTML) y sus resultados en JSON, y un archivo consolidado reúne los indicadores de todo el corpus. El aplicativo [CurriculoPoli — P22] permite filtrar los resultados por programa, sede, modalidad y nivel (Tabla 6).

**Tabla 6. Stack tecnológico (corregida)**

| Componente | Tecnología | Momento de uso |
|---|---|---|
| Lenguaje y datos | Python [versión de la corrida final — P17], pandas, numpy | Ejecución |
| Procesamiento de texto | scikit-learn (TF-IDF, LDA), rank-bm25, spaCy | Ejecución |
| Estadística | scipy.stats | Ejecución |
| Visualización | plotly, streamlit | Ejecución |
| IA generativa | Claude Sonnet | Solo diseño y construcción (la integración en ejecución existe y estuvo desactivada) |

El código, las versiones exactas de las bibliotecas, las semillas, los parámetros, los diccionarios, los umbrales y las reglas de preprocesamiento están documentados en el repositorio del proyecto. [Frase sobre el registro de la estructuración generativa: mantener solo si se aporta el registro — P20.]

*Nota: los corchetes marcan decisiones pendientes (auditoria/PENDIENTES.md).*

## Resultados – introducción y Tabla 7

3. Resultados. El corpus comprende 50 matrices con 222 competencias, 341 RA únicos, 391 estrategias mesocurriculares y 1.757 asignaturas (Tabla 7). Los 341 RA generan 586 registros, porque un mismo RA puede aportar a varias competencias. Las propiedades textuales se calculan sobre RA únicos; la distribución por tipo de saber, sobre registros, y las proporciones por programa-sede, sobre las 50 matrices.

**Tabla 7. Corpus analizado por sede y modalidad**

| Sede | Modalidad | Matrices | Competencias | RA únicos | Estrategias meso |
|---|---|---|---|---|---|
| VNAL | Virtual nacional | 22 | 93 | 139 | 170 |
| PBOG | Bogotá presencial | 17 | 75 | 119 | 132 |
| PMED | Medellín presencial | 7 | 34 | 52 | 59 |
| HMED | Medellín híbrido | 3 | 17 | 25 | 24 |
| HBOG | Bogotá híbrido | 1 | 3 | 6 | 6 |
| Total |  | 50 | 222 | 341 | 391 |

*Nota. Los RA únicos se cuentan dentro de cada matriz; las estrategias son las declaradas en el Paso 4.*

VNAL y PBOG reúnen el 78 % de las matrices, y HBOG cuenta con una sola. Diecinueve matrices pertenecen a ocho programas ofrecidos en varias sedes con RA idénticos, de modo que las sedes no constituyen observaciones independientes. La Figura 1 resume la cadena de evidencia del logro que se detalla en R1–R5, cada eslabón sobre su propia base.

## Resultados – R1 (V1)

R1. Correspondencia competencia–resultados de aprendizaje (V1). Los 341 RA únicos citan una competencia declarada en el Paso 2 en las 50 matrices (V1 = 100 %). Como la plantilla exige esa referencia, V1 es una propiedad del instrumento; al ser constante, figura en la Figura 1 como condición del instrumento y se excluye de los análisis de asociación (R6). La matriz no registra el vínculo entre competencia y perfil profesional y ocupacional, por lo que ese tramo no es verificable.

## Resultados – R2 (V2)

R2. Tipología y frecuencia de inconsistencias curriculares (V2). De las 222 competencias, 182 son específicas y 40 genéricas; las genéricas corresponden a una única competencia institucional («Analizar fenómenos contemporáneos») presente en 40 matrices. Por ello Analizar es el verbo más frecuente (50 ocurrencias, 40 en la competencia genérica); entre las específicas predominan Dominar (26), Aplicar (22), Implementar (20), Desarrollar (19) y Diseñar (19) (Figura 2). Cinco matrices de tres programas repiten un verbo entre competencias específicas (V2 = 90 %), y ninguna omite un tipo de saber (Tabla 8).

**Tabla 8. Desajustes horizontales por matriz**

| Tipo de desajuste | Matrices | % de 50 | Programas (de 39) |
|---|---|---|---|
| Verbo repetido entre competencias específicas | 5 | 10 % | 3 |
| Ausencia de un tipo de saber | 0 | 0 % | 0 |

Los 586 registros se distribuyen en Saber 37,9 %, SaberHacer 31,1 % y SaberSer 31,1 % (Figura 3); por matriz, SaberHacer oscila entre 28,6 % y 33,3 % y Saber entre 33,3 % y 42,9 %. La paridad responde a la plantilla: cada competencia específica se descompone en un RA de cada tipo de saber y cada competencia genérica, en un RA de Saber. Sobre los 341 RA únicos, la distribución es 48,1 %, 36,1 % y 15,8 %, porque cada RA de SaberSer se reutiliza en 3,4 competencias en promedio, frente a 1,4 en Saber y 1,5 en SaberHacer.

## Resultados – R3 (V3)

R3. Evaluabilidad (V3). Se consideró evaluable el RA con verbo observable —en SaberSer se admite el verbo afectivo de la taxonomía declarada— y con finalidad de desempeño o producto explícito. Los 341 RA únicos cumplen ambos criterios en las 50 matrices (V3 = 100 %). La plantilla impone la estructura verbo + objeto + finalidad + condición; por ello V3 es constante y, como V1, figura en la Figura 1 como condición del instrumento y se excluye de R6.

## Resultados – R4 (V4)

R4. Trazabilidad (V4). V4 mide la proporción de RA únicos vinculados a una estrategia mesocurricular con indicador e instrumento (Paso 4); los indicadores e instrumentos de cada estrategia se asignan a todos los RA de su bloque. Se distinguen los RA de programa y el RA de la competencia genérica institucional, presente en 40 matrices. V4 alcanza el 87,1 % (297 de 341; media por matriz 87,9 %, rango 62,5 %–100 %), con un comportamiento opuesto entre clases: 98,0 % en los RA de programa y 5,0 % en el RA genérico (Tabla 9).

**Tabla 9. Trazabilidad (V4) por sede y clase de RA**

| Sede | RA de programa | RA genérico | Todos los RA |
|---|---|---|---|
| VNAL | 100,0 % (124/124) | 0,0 % (0/15) | 89,2 % (124/139) |
| PBOG | 97,1 % (102/105) | 7,1 % (1/14) | 86,6 % (103/119) |
| PMED | 93,3 % (42/45) | 14,3 % (1/7) | 82,7 % (43/52) |
| HMED | 100,0 % (22/22) | 0,0 % (0/3) | 88,0 % (22/25) |
| HBOG¹ | 100,0 % (5/5) | 0,0 % (0/1) | 83,3 % (5/6) |
| Total | 98,0 % (295/301) | 5,0 % (2/40) | 87,1 % (297/341) |

*Nota. Entre paréntesis, RA con estrategia meso / RA únicos. ¹ Matriz única; valor descriptivo, excluido de las comparaciones inferenciales.*

De los 44 RA sin estrategia, 38 corresponden a la competencia genérica (Figura 4). Los seis restantes se ubican en Mercadeo y Publicidad (PMED, 2; PBOG, 1), Diseño Gráfico (PBOG y PMED) y Diseño Industrial (PBOG). Entre sedes, V4 varía de 82,7 % (PMED) a 89,2 % (VNAL). En el nivel micro, todos los RA están asignados a asignaturas con actividades de evaluación (mediana: 17 asignaturas por RA). En dos matrices VNAL, el Paso 4 conserva la redacción previa de un RA reformulado en el Paso 3.

## Resultados – R5 (V5)

R5. Indicadores de resultado e impacto (V5). Las 391 estrategias declaran al menos un indicador (1.185 en total, con 170 redacciones distintas). Como todos son indicadores de logro del RA, se clasificaron por nivel de evidencia: implementación (N1), percepción y reacción (N2), aprendizaje demostrado con criterios (N3), transferencia a contextos auténticos (N4) y efecto externo (N5). Las simulaciones se asignaron a N3, el conteo de participantes a N1 y los indicadores compuestos a su nivel más alto. V5 corresponde a la proporción de estrategias con evidencia directa del logro (N3 o N4).

**Tabla 10. Indicadores de logro por nivel de evidencia**

| Nivel | Tipo de evidencia | Indicadores | % | Estrategias¹ |
|---|---|---|---|---|
| N1 Implementación | Indirecta | 808 | 68,2 % | 18 |
| N2 Percepción y reacción | Indirecta | 371 | 31,3 % | 369 |
| N3 Aprendizaje demostrado | Directa | 5 | 0,4 % | 3 |
| N4 Transferencia | Directa | 0 | 0,0 % | 0 |
| N5 Efecto externo | Efecto externo | 1 | 0,1 % | 1 |
| Total |  | 1.185 | 100,0 % | 391 |

*Nota. ¹ Estrategias según el nivel más alto de sus indicadores.*

Dos indicadores concentran casi toda la declaración: el número de estudiantes o de ejecuciones (N1) y la valoración del aporte de la estrategia a los RA (N2). Solo 3 de las 391 estrategias aportan evidencia directa (V5 = 0,8 %), todas en dos matrices de VNAL: Técnica Profesional Judicial (promedio superior a 450/500 en práctica simulada; sustentación ante jurados) y Administración Pública (variación de puntajes antes y después de talleres de refuerzo). Ninguna estrategia evalúa la transferencia, y solo una registra un efecto externo (vinculación laboral de estudiantes). La clasificación aplicó un libro de códigos de cinco niveles con cuatro reglas de decisión a las 170 redacciones distintas de indicador (anexo).

## Resultados – R6

R6. Asociación entre variables curriculares (V1–V5). Solo tres pares admiten estimación, porque V1 y V3 son constantes. La correlación de Spearman sobre las 50 matrices fue V2–V4 ρ = −0,03 (p = 0,846), V2–V5 ρ = 0,07 (p = 0,639) y V4–V5 ρ = −0,13 (p = 0,354); ninguna es significativa, tampoco con una matriz por programa (n = 39). V2 adopta dos valores y V5 es distinta de cero en dos matrices (Figura 5), por lo que estos coeficientes carecen de potencia y no se interpretan.

## Resultados – R7

R7. Diferencias entre sedes (V2, V4, V5). Las diferencias entre sedes se contrastaron con la prueba de Kruskal-Wallis, dada la desigualdad de tamaños de grupo y el incumplimiento de los supuestos de normalidad y homocedasticidad. HBOG (n = 1) se trató como caso descriptivo, porque un grupo unitario carece de varianza estimable, y V1 y V3 se excluyeron por ser constantes. Con 49 matrices —VNAL (n = 22), PBOG (n = 17), PMED (n = 7) y HMED (n = 3)—, ninguna variable difiere entre sedes, tampoco con una matriz por programa para controlar la dependencia de la oferta multisede (n = 38) (Tabla 11). Sin contrastes globales significativos, no se realizaron comparaciones post hoc de Dunn. Con n = 3 en HMED y n = 7 en PMED la potencia es baja: la no significación indica ausencia de evidencia de diferencia, no equivalencia; las posiciones por sede de la Tabla 9 son descriptivas.

**Tabla 11. Prueba de Kruskal-Wallis entre sedes**

| Variable | H(3) | p | ε² | H(3) | p | ε² |
|---|---|---|---|---|---|---|
|  | 49 matrices |  |  | 38 programas¹ |  |  |
| V2 Coherencia horizontal | 2,64 | 0,451 | 0,000 | 4,86 | 0,182 | 0,055 |
| V4 Trazabilidad | 3,53 | 0,317 | 0,012 | 2,04 | 0,565 | 0,000 |
| V5 Evidencia directa del logro | 2,51 | 0,474 | 0,000 | 2,28 | 0,516 | 0,000 |

*Nota. Se excluye HBOG (n = 1); V1 y V3 son constantes. ε² = (H − k + 1)/(n − k); los valores negativos se reportan como 0. ¹ Una matriz por programa (la primera por nombre de archivo): VNAL 18, PBOG 15, HMED 3, PMED 2.*

## Resultados – R8

R8. Contenido efectivo de la oferta (modelos analíticos). Los módulos de asignaturas compartidas, tópicos, temas de agenda global y cobertura del perfil describen el contenido declarado en los microcurrículos. Se presentan en tres bloques.

### R8.1 Asignaturas compartidas

De las 709 denominaciones de asignatura, 159 (22,4 %) aparecen en más de un programa y reúnen 937 de las 1.616 asignaturas sin electivas (58,0 %). Seis están presentes en 28 o 29 de los 39 programas: Análisis y Visualización de Datos, Razonamiento Cuantitativo, Oportunidades para Emprender, Pensamiento Crítico y Ciudadanías Activas, Cultura, Política y Sociedad, y Desarrollo Sostenible. La similitud de contenido entre versiones de programas distintos (núcleos temáticos e indicadores de logro; coseno TF-IDF) es alta: 133 homónimas son idénticas y 15 (9,4 %) divergen, con una media de 0,928 (Tabla 12). Las divergencias se concentran en asignaturas de denominación genérica —Prácticas (0,035), Investigación (0,068), Formulación y Evaluación de Proyectos (0,068)— y en las cuatro asignaturas de Inglés General (0,469–0,569).

**Tabla 12. Consistencia de contenido en asignaturas homónimas**

| Nivel | Criterio | Asignaturas | % |
|---|---|---|---|
| Idénticas | sim ≥ 0,95 | 133 | 83,6 % |
| Alta similitud | 0,60 ≤ sim < 0,95 | 11 | 6,9 % |
| Divergentes | sim < 0,60 | 15 | 9,4 % |
| Total |  | 159 | 100,0 % |

*Nota. Similitud coseno media entre versiones de programas distintos; contenido = núcleos temáticos + indicadores de logro; sin electivas. El umbral de 0,60 es operativo y no se calibró con revisión experta.*

En sentido inverso, 203 pares de asignaturas de programas distintos tienen denominación diferente y similitud ≥ 0,60; involucran 44 asignaturas (Tabla 13). Catorce pares son variantes de una misma denominación, incluidos errores tipográficos («Imvestigación Creación» frente a «Investigación Creación»; «Elementos de Teorías de la Computación» frente a «Elementos de Teoría de la Computación»). Los 189 restantes son candidatos a homologación, que incluyen falsos positivos léxicos —«Machine Learning para las TIC» frente a «Infraestructura en la Nube»— y requieren validación disciplinar.

**Tabla 13. Pares con distinta denominación y contenido similar (n = 203)**

| Categoría | Regla | Pares | % |
|---|---|---|---|
| Variante de nombre o error tipográfico | Similitud de nombre ≥ 0,85 | 14 | 6,9 % |
| Candidato a homologación | Resto de pares | 189 | 93,1 % |
| Total |  | 203 | 100,0 % |

*Nota. Solo pares entre programas distintos, con similitud de contenido ≥ 0,60. La duplicación por modalidad (p. ej., Consultorio Jurídico frente a Consultorio Jurídico Virtual) ocurre dentro de un mismo programa y no entra en este contraste.*

### R8.2 Tópicos y temas de agenda global

El LDA de consenso (k = 13; 1.192 asignaturas) identifica tópicos de peso desigual (Tabla 14). Comunicación, mercadeo y planeación estratégica es el tópico dominante en el 27,7 % de las asignaturas; le siguen educación e investigación pedagógica (14,8 %), diseño centrado en el usuario (12,2 %) y gestión de proyectos, finanzas e ingeniería de producción (10,9 %). Los tópicos disciplinares de ciencias básicas —probabilidad y estadística (4,9 %), física (4,1 %) y pensamiento numérico y algebraico (3,8 %)— y los de sostenibilidad y políticas públicas (2,9 %) e IA aplicada a estudios de caso (3,5 %) tienen peso menor; turismo y gestión organizacional no es dominante en ninguna asignatura. La densidad declarativa es de 4,1 núcleos por asignatura (mediana 4). Los términos con mayor peso TF-IDF —diseño, datos, aplica, comunicación, información, digitales— muestran un vocabulario orientado a la aplicación.

**Tabla 14. Tópicos del LDA de consenso (k = 13)**

| Tópico | Contenido | Términos característicos | Asignaturas¹ | % |
|---|---|---|---|---|
| 1 | Comunicación, mercadeo y planeación estratégica | digital, comunicación, estratégico, control, mercadeo, planeación | 330 | 27,7 % |
| 5 | Educación e investigación pedagógica | educativo, educación, investigación, proyecto, pedagógico, innovación | 177 | 14,8 % |
| 4 | Diseño centrado en el usuario y negocio | diseño, usuario, experiencia de usuario, negocio, empatía | 146 | 12,2 % |
| 6 | Gestión de proyectos, finanzas e ingeniería de producción | proyecto, financiero, ingeniería, producción, herramientas | 130 | 10,9 % |
| 3 | Derecho público y administración del Estado | público, derecho, administrativo, Colombia, social | 93 | 7,8 % |
| 9 | Probabilidad y estadística | probabilidad, distribución, variable, estadística | 59 | 4,9 % |
| 2 | Física y lenguaje visual publicitario (tópico mixto) | movimiento, dinámica, ley, energía, lenguaje publicitario, imagen | 49 | 4,1 % |
| 8 | Pensamiento numérico y algebraico | pensamiento numérico y algebraico, representación | 45 | 3,8 % |
| 10 | Sociedad, cultura y ambiente en Colombia | social, ambiental, sociedad, cultural, colombiano | 43 | 3,6 % |
| 12 | Expresión y construcción en medios digitales | expresión, contexto, construcción, digital | 43 | 3,6 % |
| 13 | Estudios de caso con datos e inteligencia artificial | estudio de caso, datos, inteligencia artificial, visualización | 42 | 3,5 % |
| 7 | Sostenibilidad, políticas públicas y ciudadanía | sostenible, políticas públicas, negocios, ciudadanía | 35 | 2,9 % |
| 11 | Turismo y gestión organizacional | información, integral, innovación, turismo, organizacional | 0 | 0,0 % |
| Total |  |  | 1.192 | 100,0 % |

*Nota. ¹ Asignaturas cuyo tópico de mayor probabilidad es el indicado (confianza media 0,42); una matriz por programa.*

La presencia de las 15 tendencias del sector empresarial y educativo se midió en dos dimensiones: amplitud (proporción de programas con al menos una asignatura asociada) y profundidad (proporción de asignaturas) (Figura 6). Todas las asignaturas quedan asociadas al menos a una tendencia (1,58 en promedio). La inteligencia artificial aparece en 31 de los 39 programas (79,5 %) pero solo en 62 de las 1.616 asignaturas (3,8 %); sostenibilidad tiene la misma amplitud y el doble de profundidad (7,7 %). Las tendencias con mayor profundidad son formación ciudadana, humanística, investigativa y práctica (18,4 %), marketing y comunicación (16,1 %), transformación digital y datos (15,8 %) y estrategia y gestión de proyectos (15,5 %); innovación educativa e inclusión (33,3 % de los programas) y talento humano y bienestar (41,0 %) tienen la menor amplitud.

*[Figura 6. Temas de agenda global: amplitud y profundidad]*

*Nota. Lista oficial de 15 tendencias (config_tendencias.json), que integra las dos listas anteriores del aplicativo y depura sus términos genéricos. Una tendencia se asigna si algún término aparece en el nombre de la asignatura o si su contenido suma al menos dos puntos (término compuesto = 2; simple = 1).*

### R8.3 Cobertura del perfil profesional y ocupacional

De los 988 elementos del perfil (celdas de los nueve campos del Paso 1), 49 (5,0 %) no encuentran respaldo suficiente en los contenidos de las asignaturas de su programa (Tabla 15). Las alertas se concentran en Tareas profesionales (13,3 %), Poblaciones de actuación (9,4 %) y Áreas profesionales (7,0 %); los perfiles profesional y ocupacional y el valor agregado no presentan alertas. Dos matrices tienen cobertura inferior al 80 %: Especialización en Gerencia Tributaria (52,0 %; p. ej., «Secretarías de Hacienda», «Tributarista independiente») y Especialización en Gerencia de Proyectos de Inteligencia de Negocios (62,5 %).

**Tabla 15. Cobertura del perfil por campo (n = 988 elementos; 50 matrices)**

| Campo | Elementos | Alertas | % |
|---|---|---|---|
| Tareas profesionales | 60 | 8 | 13,3 % |
| Poblaciones de actuación | 53 | 5 | 9,4 % |
| Áreas profesionales | 57 | 4 | 7,0 % |
| SaberHacer | 222 | 14 | 6,3 % |
| SaberSer | 222 | 13 | 5,9 % |
| Saber | 222 | 5 | 2,3 % |
| Perfil profesional | 50 | 0 | 0,0 % |
| Perfil ocupacional | 50 | 0 | 0,0 % |
| Valor agregado | 52 | 0 | 0,0 % |
| Total | 988 | 49 | 5,0 % |

*Nota. Elemento = celda con contenido, sin dividir. Alerta: puntaje híbrido (0,6 × coseno TF-IDF top-3 + 0,4 × BM25) inferior al umbral de su campo; corpus = núcleos, indicadores y actividades de las asignaturas, sin textos derivados del perfil.*

## Resultados – aportes para la Discusión

V1, V3 y la paridad de tipos de saber son propiedades del instrumento: la plantilla fija la referencia a la competencia, la estructura del RA y su descomposición en tres tipos de saber. Su valor no describe la calidad del diseño y no debe leerse como fortaleza.

Los rangos de referencia de un currículo por competencias (Saber 25–45 %, SaberHacer 35–60 %, SaberSer 10–30 %) [fuente pendiente] no son aplicables a registros con esta estructura; aplicarlos llevaría a concluir un déficit práctico en todas las matrices. La distribución por RA únicos (SaberSer 15,8 %) indica que el componente actitudinal se formula con pocos RA reutilizados.

La brecha de trazabilidad no es estructural: ningún RA carece de evaluación en las asignaturas y la falta de estrategia meso se concentra en la competencia genérica institucional, que los programas no planean en el Paso 4. Acciones: definir institucionalmente su planeación meso, completar la estrategia de los seis RA de programa y vincular el Paso 4 al Paso 3 por lista desplegable para que una reformulación no rompa el vínculo. La ausencia documental impide verificar la articulación, pero no prueba que no ocurra.

Los indicadores declarados informan si la estrategia ocurrió y cómo fue valorada, pero casi nunca si el RA se alcanzó: el 99,5 % es evidencia indirecta. Para sostener decisiones de mejora, el Paso 4 debería exigir por estrategia al menos un indicador de aprendizaje demostrado (N3) con criterio de desempeño y umbral de suficiencia, y, cuando la estrategia ocurra en contexto real, uno de transferencia (N4).

Con la plantilla actual, la mayoría de las variables mide el cumplimiento del formato y no decisiones de diseño: V1 y V3 son constantes, V2 casi binaria y V5 casi nula; solo V4 refleja variación entre programas. Ello explica la ausencia de asociaciones (R6) y orienta la revisión del instrumento hacia variables que discriminen.

La brecha de trazabilidad tiene dos fuentes distintas: una regla común —el RA de la competencia genérica institucional, sin estrategia meso en 38 de 40 matrices— y decisiones de programa, que explican seis RA en cinco matrices. La revisión debe atender ambas, no diferenciarse por sede (R7).

Síntesis. El currículo está bien formulado y articulado, pero no genera evidencia directa del logro: las variables que dependen de enunciados (V1, V3) y de su articulación (V2, V4) se acercan al techo, mientras que solo el 0,8 % de las estrategias declara un indicador de aprendizaje demostrado (V5). Las brechas son puntuales y localizables —15 asignaturas homónimas divergentes, 14 variantes de denominación, 49 elementos del perfil sin respaldo, seis RA de programa sin estrategia— y se entregan como listados nominales. La IA tiene amplitud (82 % de los programas) sin profundidad (5 % de las asignaturas); la sostenibilidad combina ambas. El procedimiento es transferible a otra institución multisede con matrices estandarizadas: identificar campos obligatorios y opcionales, medir la cobertura de los segundos y comparar la variabilidad dentro y entre unidades académicas.

## Resultados ya verificados

**Cobertura del perfil por grupo (para la sección de Resultados)**

| Grupo | Elementos | Alertas | % |
|---|---|---|---|
| Perfil | 100 | 0 | 0,0 % |
| Saberes | 666 | 32 | 4,8 % |
| Campo de actuación | 170 | 17 | 10,0 % |
| Valor agregado | 52 | 0 | 0,0 % |
| Total | 988 | 49 | 5,0 % |

Asignaturas compartidas: 159 asignaturas homónimas, de las cuales 15 (9,4 %) son divergentes; 203 pares de asignaturas con nombre distinto y contenido similar entre programas.
