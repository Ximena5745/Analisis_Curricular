# Definiciones finales de la auditoría

Fuente única de las definiciones usadas para verificar el artículo curricular. Fecha de verificación: 2026-10-01 17:37.
Las mismas definiciones están en el Word (sección "Definiciones finales") y en el Excel (hoja "Definiciones").

| Término | Definición | Dónde está el dato | Regla de conteo | Valor final | Decisión |
|---|---|---|---|---|---|
| Matriz (unidad programa-sede) | Un archivo FormatoRA_<Programa>_<Sede>.xlsx. Es la unidad de análisis de los descriptivos. | Carpeta data/raw/FORMATOS RA CICLO UNO RC (*.xlsx) | Contar archivos .xlsx con las hojas Paso 1 a Paso 5. | 50 | D1 |
| Programa académico | Denominación del programa, con independencia de la sede. Un programa ofrecido en varias sedes tiene una matriz por sede. | Nombre del archivo: texto entre "FormatoRA_" y "_<Sede>" | Agrupar matrices por denominación. Denominador de las cifras "por programa". | 39 | D1 |
| Programa multisede | Programa con matriz en más de una sede. | Nombre del archivo | Denominaciones con 2 o más archivos. | 8 programas / 19 matrices | D1 |
| Sede y modalidad | Ubicación y modalidad de la oferta, codificadas en el sufijo del archivo: PBOG/PMED presencial, HBOG/HMED híbrida, VNAL virtual nacional. | Sufijo del nombre del archivo | Bogotá (PBOG, HBOG), Medellín (PMED, HMED), oferta virtual nacional (VNAL). | 2 sedes físicas + oferta virtual; 3 modalidades | — |
| Nivel de formación | Profesional universitario (incluye licenciaturas), Tecnología, Técnica profesional (pregrado); Especialización, Maestría (posgrado). | Denominación del programa | Esp* → Especialización; MCE, MEDSTEM, MGEM, MGerTalentoHumano, MInnovacionEducativa → Maestría; Tecnol* → Tecnología; TecProf* → Técnica; resto → Profesional. | 34 / 5 / 1 / 5 / 5 matrices | — |
| Perfil profesional y ocupacional | Textos del Paso 1 que describen el perfil profesional y el perfil ocupacional. No se denomina "perfil de egreso". | Hoja "Paso1 Analisis perfil egreso", columnas C y D, fila 3 | Una celda con contenido = un registro. No se divide el texto en frases ni por separadores. | 100 (50 profesionales + 50 ocupacionales) | D2, D3 |
| Competencia | Competencia redactada en el Paso 2. | Hoja "Paso 2 Redacción competen", columna F, desde la fila 3 | Filas con texto en la columna F, excluyendo instrucciones "[…]" y el encabezado repetido. | 222 | — |
| Resultado de aprendizaje (RA) único | Redacción distinta de un RA dentro de una matriz. La identidad es el texto, no el número. | Hoja "Paso 3 Redacción RA", columna I, desde la fila 3 (se excluye la hoja "- Backup") | Texto normalizado (minúsculas, sin tildes ni puntuación final), deduplicado dentro de cada matriz. | 341 | D4 |
| Registro de RA | Fila del Paso 3. Un RA se repite una vez por cada competencia a la que aporta. Solo para preguntas sobre vínculos competencia–RA. | Hoja "Paso 3 Redacción RA", columna I | Filas con texto en la columna I. | 586 | D4 |
| Estrategia mesocurricular declarada | Estrategia del programa nombrada en el Paso 4. Se escribe solo en la primera fila de su bloque. | Hoja "Paso 4 Estrategias mesocurricu", columna B, desde la fila 3 | Filas con RA en la columna A y nombre de estrategia en la columna B. | 391 | D5 |
| Vínculo RA–estrategia | Fila del Paso 4 que asocia un RA con la estrategia de su bloque. | Hoja "Paso 4 Estrategias mesocurricu", columna A | Filas con RA en la columna A. | 1.612 | D5 |
| Registro de asignatura | Una asignatura o módulo del plan de estudios de una matriz. Incluye los espacios electivos (nota N1). | Hoja "Paso 5 Estrategias micro", columna D, desde la fila 3 | Filas con nombre en la columna D, excluyendo la fila de totales (columna D numérica, una por matriz). | 1.757 | D6 |
| Denominación de asignatura | Nombre distinto de asignatura en todo el corpus. | Paso 5, columna D | Nombre en minúsculas, sin tildes ni puntuación, deduplicado en el corpus. | 709 | D6 |
| Espacio electivo | Registro de asignatura cuyo contenido depende de la electiva elegida ("Electiva 1…4", "Electiva I…IV", "Electiva"). No declara núcleos; es rasgo del diseño, no omisión. | Paso 5, columna D | Registros de asignatura sin núcleos temáticos. | 141 (4 por matriz de pregrado profesional; 1 en 5 de posgrado) | N1 |
| Núcleo temático | Ítem numerado ("1. …", "2. …") de la celda de núcleos de una asignatura, aunque ocupe varias líneas. Si la celda no está numerada, cada línea es un núcleo. | Paso 5, columna "Núcleos temáticos", fila de inicio de cada asignatura (celda combinada, se cuenta una vez) | Separar solo por la numeración al inicio de línea. No se corta por comas ni por saltos de línea internos; no se aplica el filtro es_nucleo_valido. | 6.671 (2.815 únicos) | D7 |
| Densidad de núcleos | Número de núcleos por asignatura con núcleos, dentro de cada matriz. | Paso 5 | Núcleos / asignaturas con núcleos, por matriz (no agrupar por nombre en todo el corpus). | media 4,1; mediana 4 | D7 |

## Decisiones de método

- **D1** — 39 programas académicos (por denominación); 50 matrices = unidades programa-sede.
- **D2** — El Paso 1 se denomina "perfil profesional y ocupacional".
- **D3** — Perfil: una celda con contenido = un registro; sin dividir el texto.
- **D4** — RA único = texto normalizado deduplicado dentro de cada matriz; las filas solo para vínculos.
- **D5** — Estrategia = nombre en la columna B del Paso 4; las filas con RA son vínculos.
- **D6** — Registro de asignatura = una asignatura por matriz, sin la fila de totales.
- **D7** — Núcleo temático = ítem numerado de la celda de núcleos.
- **N1** — Los espacios electivos sin núcleos se documentan como nota de datos, no como hallazgo.

## Reproducción

Desde la raíz del proyecto, ejecutar en orden los scripts de `auditoria/scripts/`: `verificar_extraccion.py`, `eda_resultados_aprendizaje.py`, `verificar_corpus.py`, `verificar_resultados.py`, `verificar_micro.py` y `generar_entregables.py`.
