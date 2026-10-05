"""
Textos corregidos del artículo, aprobados por la autora durante la auditoría.

Fuente única para el Word (sección "Textos corregidos del artículo"), el Excel
(hoja Textos_corregidos) y auditoria/TEXTOS_CORREGIDOS.md. Cada sección es una
lista de bloques: ('p', texto) párrafo, ('t', titulo, cabecera, filas) tabla,
('n', texto) nota.
"""

RESUMEN = [
    ('p', 'Estudio aplicado de métodos mixtos sobre 50 matrices curriculares de 39 programas académicos: 338 resultados de '
          'aprendizaje únicos (deduplicados en cada matriz), 391 estrategias mesocurriculares declaradas, 1.757 registros de '
          'asignatura y 50 perfiles profesionales y 50 perfiles ocupacionales, analizados mediante cinco variables de coherencia '
          'y trazabilidad, minería de texto, modelado temático y contraste estadístico exploratorio. Resultados. La evaluabilidad '
          'alcanzó el 100 %, condición impuesta por la plantilla, y el 87,0 % de los resultados de aprendizaje '
          'presentó una ruta documentada hasta una estrategia con instrumento de evaluación (98,0 % sin el RA genérico institucional). El 65,7 % de los 2.574 atributos del '
          'perfil se respaldó a la vez en competencias, RA y asignaturas, y el 3,8 % en ninguna de ellas (10,9 % en las poblaciones '
          'de actuación); el 9,4 % de las asignaturas '
          'homónimas mostró contenidos divergentes y la inteligencia artificial apareció en el 79,5 % de los programas, pero solo '
          'en el 3,8 % de las asignaturas.'),
    ('n', 'Cifras de IA según la lista oficial de 15 tendencias (D21) sobre las 1.616 asignaturas sin electivas (R8.2): 31 de 39 '
          'programas y 62 asignaturas.'),
]

CORPUS = [
    ('p', 'Las fuentes son 50 matrices curriculares en Excel de 39 programas académicos, ofrecidos en Bogotá, Medellín y en la '
          'oferta virtual nacional, bajo tres modalidades (presencial, virtual e híbrida), que representan el 63 % de la oferta '
          'institucional en renovación curricular [fuente, fecha de corte]. Ocho programas se ofrecen en más de una sede con matriz '
          'propia: Contaduría Pública, Negocios Internacionales e Ingeniería Industrial en tres sedes, y Administración de Empresas, '
          'Derecho, Diseño Gráfico, Ingeniería de Sistemas y Mercadeo y Publicidad en dos. Por ello, la unidad de análisis es el '
          'programa-sede (Tabla 1). Cada matriz curricular se organiza según la secuencia metodológica definida institucionalmente: '
          'Paso 1, perfil profesional y ocupacional; Paso 2, competencias; Paso 3, resultados de aprendizaje; Paso 4, estrategias '
          'mesocurriculares; Paso 5, microcurrículo.'),
    ('t', 'Tabla 1. Composición del corpus por nivel de formación',
     ['Nivel de formación', 'Programas', 'Matrices (programa-sede)', 'Competencias', 'RA únicos', 'Estrategias meso declaradas'],
     [['Profesional universitario¹', '23', '34', '169', '254', '276'],
      ['Tecnología', '5', '5', '20', '34', '41'],
      ['Técnica profesional', '1', '1', '5', '6', '7'],
      ['Pregrado', '29', '40', '194', '294', '324'],
      ['Especialización', '5', '5', '13', '19', '34'],
      ['Maestría', '5', '5', '15', '25', '33'],
      ['Posgrado', '10', '10', '28', '44', '67'],
      ['Total', '39', '50', '222', '338', '391']]),
    ('n', '¹ Incluye tres licenciaturas. Los resultados de aprendizaje únicos se deduplican dentro de cada matriz, sin distinguir '
          'mayúsculas, tildes ni puntuación, porque un mismo RA se registra una vez por cada competencia a la que aporta (586 registros '
          'en total). Las 391 estrategias declaradas se '
          'vinculan a los RA mediante 1.612 registros RA–estrategia.'),
    ('p', 'En el componente microcurricular se procesaron 1.757 registros de asignatura², correspondientes a 709 denominaciones '
          'únicas (normalizadas sin distinguir mayúsculas, tildes ni puntuación). Las asignaturas declaran 6.684 núcleos temáticos, '
          'identificados por la numeración con que cada matriz los enumera (2.828 únicos; mediana de 4 por asignatura). El modelo se '
          'aplica igual a ambos niveles de formación, aunque los resultados se diferencian porque propósitos, alcance y profundidad varían.'),
    ('n', '² Incluye 141 espacios electivos, cuyo contenido depende de la electiva elegida y que, por tanto, no declaran núcleos temáticos.'),
    ('p', 'Se incluyeron todas las matrices que habían completado los cinco pasos y contaban con autorización, y se excluyeron las '
          'versiones incompletas, duplicadas o anteriores al ciclo examinado, así como las hojas de respaldo de los archivos. Los ocho '
          'programas ofrecidos en más de una sede comparten los mismos resultados de aprendizaje y la mayor parte de sus núcleos '
          'temáticos entre sus 19 matrices, por lo que las unidades no son plenamente independientes. En consecuencia, los descriptivos '
          'se calculan sobre las 50 unidades programa-sede, las cifras por programa sobre los 39 programas, y la inferencia se limita a '
          'asociaciones exploratorias.'),
]

ETAPA_2 = [
    ('p', 'Etapa 2. Identificación de los núcleos temáticos. Cada asignatura declara sus núcleos temáticos como una lista numerada '
          'en texto libre. Los núcleos se separaron por su numeración, de modo que un núcleo que ocupa varias líneas o contiene comas '
          'se conserva como unidad; en las cuatro celdas sin numeración se tomó cada línea como un núcleo. Se obtuvieron 6.684 núcleos '
          '(2.828 únicos) en 1.616 asignaturas; un control de calidad (celdas vacías, solo números o texto de instrucciones de la '
          'plantilla) no identificó entradas inválidas. A los núcleos se les asigna un puntaje orientativo, no decisorio, que contrasta '
          'vocabulario académico con vocabulario de formato. '
          'Un control con reglas explícitas y deterministas, basado en la clasificación de problemas de calidad de datos de una '
          'sola fuente (Rahm & Do, 2000), señala para revisión, sin excluirlos ni alterar los conteos, los núcleos que agrupan '
          'varios temas en un solo ítem (3), repiten el nombre de la asignatura (6), se duplican dentro de una misma asignatura '
          '(0) o tienen una extensión atípica, superior a Q3 + 1,5 × RIC del corpus (más de 14 palabras; 255; Tukey, 1977): en '
          'total, 264 núcleos (3,9 %).'),
]

ETAPA_3 = [
    ('p', 'Etapa 3. Calidad del diseño. Cada programa recibe un puntaje de 0 a 100 que pondera la exigencia de sus resultados de '
          'aprendizaje (40 %), el equilibrio entre tipos de saber (30 %) y la variedad de estrategias didácticas (30 %). La completitud '
          'de la matriz y la proporción de competencias con resultados de aprendizaje asociados se verificaron en todos los programas '
          '(100 % en las 50 matrices); como el formato de la matriz garantiza su cumplimiento, se reportan como condiciones verificadas '
          'y no intervienen en el puntaje.'),
    ('p', 'Para ubicar cada resultado de aprendizaje en una escala de exigencia, las matrices emplean dos taxonomías: Bloom en su '
          'versión clásica (48,5 % de los resultados de aprendizaje únicos) y una adaptación con aportes de Krathwohl (BAK, 51,5 %); '
          '26 de las 50 matrices combinan ambas. Las dos distinguen los dominios cognitivo, procedimental y actitudinal, pero solo BAK '
          'asigna escalas propias a los dos últimos, al reconocer que dominar un procedimiento o consolidar una actitud siguen '
          'progresiones distintas de las del conocimiento conceptual (Tabla 4).'),
    ('p', 'Cada nivel declarado se traduce a una escala común de 1 a 6 según su posición en la progresión de su propio dominio, con la '
          'expresión nivel = 1 + (posición − 1) × 5 / (número de niveles − 1). Así, en Bloom y en el dominio cognitivo de BAK cada nivel '
          'conserva su posición (de 1 a 6); en el dominio procedimental de BAK los cuatro niveles equivalen a 1; 2,67; 4,33 y 6, y en el '
          'actitudinal los cinco niveles equivalen a 1; 2,25; 3,5; 4,75 y 6. Esta equivalencia entre escalas de distinta longitud permite '
          'comparar programas que emplean sistemas diferentes y constituye un supuesto del método. El índice de exigencia de cada programa '
          'corresponde al nivel medio de sus resultados de aprendizaje únicos, expresado de 0 a 100.'),
    ('t', 'Tabla 4. Sistemas de clasificación empleados en las matrices',
     ['Taxonomía', 'Resultados de aprendizaje únicos', 'Dominio cognitivo', 'Dominio procedimental', 'Dominio actitudinal'],
     [['Bloom', '164 (48,5 %)', 'Conocimiento, Comprensión, Aplicación, Análisis, Síntesis, Evaluación', '(mismos seis niveles)', '(mismos seis niveles)'],
      ['BAK', '174 (51,5 %)', 'Conocimiento, Comprensión, Aplicación, Análisis, Síntesis, Evaluación',
       'Imitación, Manipulación, Precisión, Control', 'Percepción, Responder, Valorar, Organizar, Caracterizar'],
      ['Total', '338 (100 %)', '', '', '']]),
    ('n', 'Nota: 26 de las 50 matrices combinan ambas taxonomías; 21 emplean solo Bloom y 3 solo BAK. Cada nivel se traduce a una '
          'escala común de 1 a 6 según su posición en la progresión de su dominio.'),
]

ETAPA_4 = [
    ('p', 'Etapa 4. Asociación del perfil profesional y ocupacional (V1). El perfil se descompone en atributos: las funciones que el '
          'texto narrativo de cada perfil atribuye al egresado, identificadas con el léxico de verbos de las hojas de taxonomía de la '
          'propia matriz, y cada ítem de las áreas profesionales, las tareas profesionales y las poblaciones de actuación del perfil '
          'ocupacional. Se obtuvieron 2.580 atributos; seis no son atributos del perfil (cifras de encuestas de empleo y etiquetas de '
          'nivel) y se excluyen, lo que deja 2.574 (Tabla 5). El perfil profesional se evalúa solo a partir de su texto narrativo, '
          'porque el Paso 1 no lo descompone en áreas, tareas ni poblaciones. Quedan fuera del alcance los campos Saber, SaberHacer '
          'y SaberSer, que alimentan por lista desplegable la redacción de los RA (Paso 3) y harían circular la comparación, y el '
          'valor agregado. Cada atributo se contrasta solo con la matriz de su programa, en tres '
          'capas: competencias (Paso 2), resultados de aprendizaje (Paso 3) y asignaturas (nombre, indicadores de logro y núcleos '
          'temáticos del Paso 5, sin electivas). Se excluyen la competencia genérica institucional y su RA, comunes a 40 matrices. '
          'El procedimiento se inscribe en el mapeo curricular asistido por procesamiento de lenguaje natural, que relaciona '
          'resultados de aprendizaje de curso y de programa (Zaki et al., 2023), contenidos y estándares educativos mediante '
          'representaciones vectoriales del texto (Butterfuss & Doran, 2025) o planes de estudio completos (Duarte et al., 2023); a '
          'diferencia de esos trabajos, el contraste parte del perfil de egreso y se limita a la matriz de cada programa.'),
    ('p', 'Un atributo se considera respaldado en una capa si alguna unidad de texto cubre sus conceptos. La cobertura pondera cada '
          'lema por su rareza en la matriz (IDF), reduce el peso del vocabulario presente en más del 15 % de sus unidades, reconoce '
          'familias de palabras y un diccionario de equivalencias de dominio ampliable por la institución, y exige que un rol '
          '(p. ej., «consultor») encuentre su actividad o conserve solo la mitad de su cobertura. La similitud semántica '
          '(paraphrase-multilingual-MiniLM-L12-v2) actúa solo como apoyo de coberturas parciales: el respaldo es explícito si la '
          'cobertura alcanza 0,25 y parcial si alcanza 0,05 con similitud de al menos 0,58. La rareza se pondera con IDF (Spärck '
          'Jones, 1972) y la similitud semántica usa un modelo de oraciones multilingüe (Reimers & Gurevych, 2020). V1 es la proporción de atributos '
          'respaldados en las tres capas; se informa además la proporción sin respaldo en ninguna.'),
    ('p', 'Los parámetros se calibraron contra una lectura de referencia de 11 matrices de ocho enfoques disciplinares (429 '
          'atributos; 1.287 decisiones atributo × capa), elaborada con asistencia de IAg sobre la matriz original, con revisión puntual de 40 de los '
          '429 atributos. El acuerdo fue del 80,1 % (κ de Cohen = 0,44; Cohen, 1960), medido dentro de la muestra usada para '
          'calibrar; al calibrar excluyendo cada enfoque, osciló entre 68,9 % y 84,2 % en el enfoque excluido, lo que aproxima el '
          'desempeño fuera de ella. El método es determinista: la misma matriz '
          'produce el mismo resultado, y sus asociaciones se entregan como propuesta para validar por el comité curricular.'),
    ('t', 'Tabla 5. Atributos del perfil evaluados por componente',
     ['Perfil', 'Componente', 'Atributos'],
     [['Profesional', 'Funciones del texto narrativo', '424'],
      ['Ocupacional', 'Funciones del texto narrativo', '438'], ['', 'Áreas profesionales', '656'],
      ['', 'Tareas profesionales', '633'], ['', 'Poblaciones de actuación', '423'], ['', 'Subtotal', '2.150'],
      ['Total', '', '2.574']]),
    ('n', 'Nota: un ítem del texto narrativo idéntico a un componente del perfil ocupacional se cuenta una sola vez. Se excluyen '
          'seis ítems que no son atributos del perfil. El contraste usa solo el contenido de la matriz del propio programa.'),
    ('n', 'Observación. La lectura de referencia con que se calibró el método se elaboró con asistencia de IAg y no ha sido '
          'validada por el comité curricular. El acuerdo de 80,1 % mide, por tanto, la concordancia del método con esa lectura y '
          'no con un juicio experto independiente; la validación por el comité de una muestra de las decisiones queda como '
          'condición previa al uso de V1 en decisiones institucionales.'),
]

# Procedimiento (versión de la autora, 2026-10-04), con tres ajustes de coherencia con Resultados:
# Etapa 4 = método de asociación vigente (V1) + la cobertura TF-IDF/BM25 como medida complementaria;
# Tabla 4 con D23 (338 RA); Tabla 6 con sentence-transformers y ❓ en lo que no se puede verificar.
PROCEDIMIENTO = [
    ('h2', 'Procedimiento'),
    ('p', 'El análisis se implementó en siete etapas.'),
    ('p', 'Etapa 1. Extracción. El nombre de cada archivo identifica el programa y su sede o modalidad (PBOG, Bogotá presencial; '
          'VNAL, virtual nacional; HMED, Medellín híbrido; PMED, Medellín presencial; HBOG, Bogotá híbrido). Como los encabezados '
          'varían tipográficamente entre archivos, el sistema los localiza por aproximación, sin corrección manual (Tabla 3).'),
    ('t', 'Tabla 3. Estructura de hojas extraídas por programa', ['Hoja', 'Contenido', 'Columnas clave'],
     [['Paso 1', 'Perfil de egreso', 'Perfil profesional, Perfil ocupacional, Saber, SaberHacer, SaberSer, Valor agregado'],
      ['Paso 2', 'Competencias', 'Verbo, Objeto conceptual, Finalidad, Condición'],
      ['Paso 3', 'Resultados de aprendizaje', 'Competencia ref., TipoSaber, SaberAsociado, Taxonomía'],
      ['Paso 4', 'Estrategias mesocurriculares', 'RA ref., Estrategia, Indicador de impacto'],
      ['Paso 5', 'Estrategias microcurriculares', 'Asignatura, Núcleos temáticos, Créditos, Actividades']]),
    ('p', 'Etapa 2. Depuración de los temas declarados. Cada asignatura declara sus núcleos temáticos como una lista numerada en '
          'texto libre. Los núcleos se separaron por su numeración, de modo que un núcleo que ocupa varias líneas o contiene comas se '
          'conserva como unidad; en las cuatro celdas sin numeración se tomó cada línea como un núcleo. Se obtuvieron 6.684 núcleos '
          '(2.828 únicos) en 1.616 asignaturas; un control de calidad (celdas vacías, solo números o texto de instrucciones de la '
          'plantilla) no identificó entradas inválidas.'),
    ('p', 'A los temas retenidos se les asigna un puntaje orientativo, no decisorio, que contrasta vocabulario académico con '
          'vocabulario de formato. '
          'Un control con reglas explícitas y deterministas, basado en la clasificación de problemas de calidad de datos de una '
          'sola fuente (Rahm & Do, 2000), señala para revisión, sin excluirlos ni alterar los conteos, los núcleos que agrupan '
          'varios temas en un solo ítem (3), repiten el nombre de la asignatura (6), se duplican dentro de una misma asignatura '
          '(0) o tienen una extensión atípica, superior a Q3 + 1,5 × RIC del corpus (más de 14 palabras; 255; Tukey, 1977): en '
          'total, 264 núcleos (3,9 %).'),
    ('p', 'Etapa 3. Calidad del diseño. Cada programa recibe un puntaje de 0 a 100 que pondera la exigencia de sus resultados de '
          'aprendizaje (40 %), el equilibrio entre tipos de saber (30 %) y la variedad de estrategias didácticas (30 %).'),
    ('p', 'La exigencia de los resultados de aprendizaje se estableció mediante dos taxonomías: Bloom clásica (48,5 % de los '
          'resultados únicos) y una adaptación con aportes de Krathwohl (BAK, 51,5 %); 26 de las 50 matrices emplean ambas. Las dos '
          'contemplan los dominios cognitivo, procedimental y actitudinal, aunque BAK incorpora escalas diferenciadas para los dos '
          'últimos (Tabla 4). Para comparar los resultados entre taxonomías, los niveles se llevaron a una escala común de 1 a 6, '
          'conservando su posición dentro de cada progresión: el nivel inicial corresponde a 1 y el más avanzado a 6, con los niveles '
          'intermedios distribuidos proporcionalmente. De este modo, la comparación se basa en el grado relativo de exigencia y no en '
          'una equivalencia directa entre los niveles de ambas taxonomías.'),
    ('t', 'Tabla 4. Sistemas de clasificación empleados en las matrices',
     ['Taxonomía', 'Uso en el corpus', 'Dominio cognitivo', 'Dominio procedimental', 'Dominio actitudinal'],
     [['Bloom', '48,5 %', 'Conocimiento, Comprensión, Aplicación, Análisis, Síntesis, Evaluación', '(mismos seis niveles)',
       '(mismos seis niveles)'],
      ['BAK', '51,5 %', 'Conocimiento, Comprensión, Aplicación, Análisis, Síntesis, Evaluación',
       'Imitación, Manipulación, Precisión, Control', 'Percepción, Responder, Valorar, Organizar, Caracterizar']]),
    ('n', 'Nota. Porcentaje sobre los 338 resultados de aprendizaje únicos (Bloom 164; BAK 174).'),
] + ETAPA_4 + [
    ('p', 'Como medida complementaria y exploratoria, que no interviene en V1, los campos excluidos (Saber, SaberHacer, SaberSer y '
          'valor agregado) se comparan con los contenidos de las asignaturas de su programa: nombre, indicadores de logro, núcleos '
          'temáticos y actividades de evaluación, sin los saberes asociados ni la redacción de los RA. La similitud combina el coseno '
          'TF-IDF ponderado de los tres documentos más afines (pesos 0,5, 0,3 y 0,2), con un peso de 0,6, y la puntuación BM25 '
          'máxima normalizada (Robertson & Zaragoza, 2009), con un peso de 0,4. Un elemento se marca como alerta si su puntaje no '
          'alcanza el umbral de su campo (Saber y SaberHacer 0,35; SaberSer 0,32; valor agregado 0,30), fijado según la extensión y '
          'el vocabulario de cada campo. Las alertas priorizan casos para revisión; no prueban la ausencia de respaldo curricular.'),
    ('p', 'Etapa 5. Asignaturas compartidas. El sistema compara las asignaturas de todos los programas por coincidencia de nombre y '
          'por similitud de contenidos (núcleos temáticos e indicadores de logro), solo entre programas distintos, lo que detecta dos '
          'situaciones opuestas: asignaturas homónimas que enseñan cosas distintas y asignaturas con nombres diferentes que cubren lo '
          'mismo. Se excluyen los espacios electivos, que no declaran contenido propio. Una asignatura homónima se considera '
          'divergente cuando la similitud media entre sus versiones es inferior a 0,60.'),
    ('p', 'Etapa 6. Análisis temático. Un modelo LDA identifica, sin una lista predefinida, los temas presentes en los contenidos '
          'declarados (Blei et al., 2003). Cada documento corresponde a una asignatura con sus núcleos temáticos depurados y '
          'lematizados (1.192 asignaturas, con una matriz por programa para evitar duplicar la oferta multisede). El modelo se '
          'configuró con 13 tópicos (k = 13), valor que presentó el mejor equilibrio entre coherencia (NPMI) y estabilidad en el '
          'rango evaluado (k = 5–30). Dado que LDA puede ser inestable con textos breves, los resultados se obtuvieron mediante el '
          'consenso de diez réplicas con semillas distintas. La estabilidad mejoró frente a un LDA simple: dos consensos '
          'independientes compartieron el 59 % de sus palabras principales, frente al 22 %.'),
    ('p', 'Etapa 7. Reportes y consulta. Por cada programa se generan un archivo consolidado y un informe navegable; el aplicativo '
          'CurriculoPoli permite filtrar los resultados por sede, nivel y programa (Tabla 6).'),
    ('t', 'Tabla 6. Stack tecnológico', ['Componente', 'Tecnología', 'Momento de uso'],
     [['Lenguaje y datos', 'Python 3.10 (despliegue), pandas, numpy', 'Ejecución'],
      ['Procesamiento de texto', 'scikit-learn (TF-IDF, LDA), rank-bm25, spaCy, sentence-transformers',
       'Ejecución'],
      ['Estadística', 'scipy.stats', 'Ejecución'],
      ['Visualización', 'plotly, streamlit', 'Ejecución'],
      ['IA generativa', 'Claude (Anthropic)', 'Solo diseño y construcción']]),
    ('n', 'Nota. Versión de Python según la imagen de despliegue y la integración continua del proyecto. La integración de IA '
          'generativa en ejecución (claude-3-5-sonnet-20241022) existe en el código y está desactivada.'),
    ('p', 'El código, las versiones de bibliotecas, semillas, parámetros, diccionarios, umbrales y reglas de preprocesamiento están '
          'documentados en el repositorio del proyecto.'),
]

# Observaciones al final del documento: textos retirados del Procedimiento por no estar respaldados en el proyecto.
OBSERVACIONES = [
    ('h2', 'Observaciones'),
    ('p', 'Se retiraron del Procedimiento los siguientes textos, porque el proyecto no los respalda. Pueden reincorporarse si se '
          'aporta el soporte indicado.'),
    ('p', '1. Etapa 2: «y un detector de valores atípicos señala temas anómalos frente al corpus (Liu et al., 2008)», y '
          '«Isolation Forest» en la Tabla 6. La función existe (src/nucleos_cleaner.detectar_anomalias_nucleos), pero ningún '
          'script ni el aplicativo la ejecutan, por lo que ningún resultado procede de ella (P21). Se retira también la referencia: '
          'Liu, F. T., Ting, K. M., & Zhou, Z.-H. (2008). Isolation forest. En Proceedings of the 2008 Eighth IEEE International '
          'Conference on Data Mining (pp. 413–422). IEEE. https://doi.org/10.1109/ICDM.2008.17. En una prueba sobre los 6.671 '
          'núcleos de la lectura anterior (D7), el detector marcó siempre la cuota fijada por su parámetro de contaminación (997 con 0,15), con temas '
          'académicos legítimos y extensos. Se sustituyó por el control con reglas explícitas descrito en la Etapa 2 '
          '(src/nucleos_cleaner.control_nucleos_reglas).'),
    ('p', '2. Cierre del Procedimiento: «y la estructuración generativa de las matrices es trazable mediante el registro de '
          'entradas, salidas y decisiones humanas». El registro no está en el repositorio (P20). Para reincorporarlo: aportar el '
          'registro como material suplementario.'),
    ('p', '3. Tabla 6: la versión de Python se acota a «3.10 (despliegue)», que es la que fijan el Dockerfile y la integración '
          'continua. La corrida de los resultados pudo hacerse en el entorno local (3.12.7), y las versiones exactas de las '
          'bibliotecas no están fijadas (P17). Para cerrarlo: regenerar los resultados en el entorno de despliegue y fijar las '
          'versiones (pip freeze).'),
    ('p', '4. Etapa 7: el nombre «CurriculoPoli» no coincide con el título del aplicativo en el código («Analisis Tematico '
          'Microcurricular») (P22). Se mantiene en el texto hasta que se unifique.'),
]

ETAPA_5 = [
    ('p', 'Etapa 5. Asignaturas compartidas. El sistema compara las asignaturas de todos los programas por coincidencia de nombre y '
          'por similitud de contenidos (núcleos temáticos e indicadores de logro), solo entre programas distintos, lo que detecta dos '
          'situaciones opuestas: asignaturas homónimas que enseñan cosas distintas y asignaturas con nombres diferentes que cubren lo '
          'mismo. Se excluyen los espacios electivos, que no declaran contenido propio. Una asignatura homónima se considera divergente '
          'cuando la similitud media entre sus versiones es inferior a 0,60, umbral operativo no calibrado con revisión experta.'),
]

ETAPA_6 = [
    ('p', 'Etapa 6. Análisis temático. Un modelo LDA identifica, sin una lista predefinida, los temas que atraviesan los contenidos '
          'declarados (Blei et al., 2003). Cada documento es una asignatura con sus núcleos temáticos depurados y lematizados '
          '(1.192 asignaturas, una matriz por programa para no duplicar la oferta multisede). El número de tópicos (k = 13) '
          'maximizó la coherencia (NPMI) y la estabilidad entre k = 5 y k = 30. Como LDA es inestable con textos breves, el modelo se '
          'estima por consenso de diez réplicas con semillas distintas, cuyos tópicos equivalentes se promedian: dos consensos '
          'independientes comparten el 59 % de sus palabras principales, frente al 22 % de un LDA simple. Los tópicos se interpretan '
          'con fines descriptivos. Un segundo análisis mide la presencia de diez temas de agenda global —inteligencia artificial, '
          'sostenibilidad y transformación digital, entre otros— y, desde 2026, quince tendencias del sector empresarial y educativo, '
          'por coincidencia de palabras completas con una lista de términos ajustable por la institución.'),
    ('t', 'Temas de agenda global (núcleos + indicadores; 1.616 asignaturas sin electivas; 39 programas)',
     ['Tema', 'Asignaturas', 'Programas'],
     [['Calidad y mejora continua', '429', '39'], ['Sostenibilidad', '219', '34'], ['Liderazgo y habilidades blandas', '206', '35'],
      ['Globalización', '171', '32'], ['Innovación y emprendimiento', '130', '35'], ['Transformación digital', '105', '24'],
      ['Inteligencia artificial', '86', '32'], ['Ética y responsabilidad social', '74', '31'],
      ['Análisis de datos y BI', '71', '26'], ['Gestión del cambio', '1', '1']]),
    ('n', 'Nota: conteo por palabra completa y sin tildes. La base de la cifra de IA del Resumen (con o sin texto de RA) está pendiente (A11).'),
]

ETAPA_7 = [
    ('p', 'Etapa 7. Reportes y consulta. Por cada matriz programa-sede se generan un informe navegable (HTML) y sus resultados en '
          'JSON, y un archivo consolidado reúne los indicadores de todo el corpus. El aplicativo [CurriculoPoli — P22] permite filtrar '
          'los resultados por programa, sede, modalidad y nivel (Tabla 6).'),
    ('t', 'Tabla 6. Stack tecnológico (corregida)', ['Componente', 'Tecnología', 'Momento de uso'],
     [['Lenguaje y datos', 'Python [versión de la corrida final — P17], pandas, numpy', 'Ejecución'],
      ['Procesamiento de texto', 'scikit-learn (TF-IDF, LDA), spaCy, sentence-transformers', 'Ejecución'],
      ['Estadística', 'scipy.stats', 'Ejecución'],
      ['Visualización', 'plotly, streamlit', 'Ejecución'],
      ['IA generativa', 'Claude Sonnet', 'Solo diseño y construcción (la integración en ejecución existe y estuvo desactivada)']]),
    ('p', 'El código, las versiones exactas de las bibliotecas, las semillas, los parámetros, los diccionarios, los umbrales y las '
          'reglas de preprocesamiento están documentados en el repositorio del proyecto. [Frase sobre el registro de la '
          'estructuración generativa: mantener solo si se aporta el registro — P20.]'),
    ('n', 'Nota: los corchetes marcan decisiones pendientes (auditoria/PENDIENTES.md).'),
]





RESULTADOS_VERIFICADOS = [
    ('t', 'Respaldo del perfil por capa (para la sección de Resultados)',
     ['Perfil', 'Atributos', 'Tres capas (V1)', 'Ninguna capa'],
     [['Profesional', '424', '73,8 %', '2,6 %'], ['Ocupacional', '2.150', '64,0 %', '4,0 %'],
      ['Total', '2.574', '65,7 %', '3,8 %']]),
    ('p', 'Asignaturas compartidas: 159 asignaturas homónimas, de las cuales 15 (9,4 %) son divergentes; 203 pares de asignaturas '
          'con nombre distinto y contenido similar entre programas.'),
]


RESULTADOS_INTRO = [
    ('p', '3. Resultados. El corpus comprende 50 matrices con 222 competencias, 338 RA únicos, 391 estrategias mesocurriculares y '
          '1.757 asignaturas (Tabla 7). Los 338 RA generan 586 registros, porque un mismo RA puede aportar a varias competencias. '
          'Las propiedades textuales se calculan sobre RA únicos; la distribución por tipo de saber, sobre registros, y las '
          'proporciones por programa-sede, sobre las 50 matrices.'),
    ('t', 'Tabla 7. Corpus analizado por sede y modalidad',
     ['Sede', 'Modalidad', 'Matrices', 'Competencias', 'RA únicos', 'Estrategias meso'],
     [['VNAL', 'Virtual nacional', '22', '93', '138', '170'],
      ['PBOG', 'Bogotá presencial', '17', '75', '118', '132'],
      ['PMED', 'Medellín presencial', '7', '34', '51', '59'],
      ['HMED', 'Medellín híbrido', '3', '17', '25', '24'],
      ['HBOG', 'Bogotá híbrido', '1', '3', '6', '6'],
      ['Total', '', '50', '222', '338', '391']]),
    ('n', 'Nota. Los RA únicos se cuentan dentro de cada matriz, sin distinguir mayúsculas, tildes ni puntuación (D4); las estrategias '
          'son las declaradas en el Paso 4.'),
    ('p', 'VNAL y PBOG reúnen el 78 % de las matrices, y HBOG cuenta con una sola. Diecinueve matrices pertenecen a ocho programas '
          'ofrecidos en varias sedes con RA idénticos, de modo que las sedes no constituyen observaciones independientes. La '
          'Figura 1 resume la cadena de evidencia del logro que se detalla en R1–R5, cada eslabón sobre su propia base.'),
]

RESULTADOS_R1 = [
    ('p', 'R1. Correspondencia del perfil con competencias, resultados de aprendizaje y asignaturas (V1). De los 2.574 atributos del '
          'perfil, el 75,6 % se respalda en alguna competencia, el 72,4 % en algún RA y el 95,2 % en alguna asignatura; el 65,7 % se '
          'respalda en las tres capas (V1) y el 3,8 % (98 atributos) en ninguna (Tabla 8). El perfil profesional se respalda más que '
          'el ocupacional: 73,8 % y 64,0 % en las tres capas, y 2,6 % y 4,0 % sin respaldo. Por matriz, V1 promedia 65,2 % (rango '
          '25,0 %–86,5 %). Los valores más bajos corresponden a la Especialización en Gerencia Tributaria (25,0 %), la Maestría en '
          'Gerencia Estratégica de Mercadeo (27,3 %) '
          'y Matemáticas (34,5 %), donde los RA respaldan menos de la mitad de los atributos (29,2 %, 31,8 % y 41,4 %). La competencia '
          'de referencia de cada RA, en cambio, está declarada en los 338 RA únicos de las 50 matrices, porque la plantilla la exige.'),
    ('t', 'Tabla 8. Respaldo de los atributos del perfil por capa curricular',
     ['Perfil', 'Atributos', 'Competencias', 'RA', 'Asignaturas', 'Tres capas (V1)', 'Ninguna capa'],
     [['Profesional', '424', '82,8 %', '78,3 %', '96,5 %', '73,8 %', '2,6 %'],
      ['Ocupacional', '2.150', '74,2 %', '71,2 %', '95,0 %', '64,0 %', '4,0 %'],
      ['Total', '2.574', '75,6 %', '72,4 %', '95,2 %', '65,7 %', '3,8 %']]),
    ('n', 'Nota. Respaldo explícito o parcial en la matriz del propio programa (Etapa 4). Acuerdo del método con una lectura de '
          'referencia elaborada con asistencia de IAg y revisada puntualmente (40 de 429 atributos): 80,1 % (κ = 0,44; 11 matrices, '
          '1.287 decisiones), medido sobre las mismas matrices usadas para calibrar; pendiente de validación por el comité curricular.'),
]

RESULTADOS_R2 = [
    ('p', 'R2. Tipología y frecuencia de inconsistencias curriculares (V2). De las 222 competencias, 182 son específicas y 40 '
          'genéricas; las genéricas corresponden a una única competencia institucional («Analizar fenómenos contemporáneos») '
          'presente en 40 matrices. Por ello Analizar es el verbo más frecuente (50 ocurrencias, 40 en la competencia genérica); '
          'entre las específicas predominan Dominar (26), Aplicar (22), Implementar (20), Desarrollar (19) y Diseñar (19) '
          '(Figura 2). Cinco matrices de tres programas repiten un verbo entre competencias específicas (V2 = 90 %), y ninguna omite '
          'un tipo de saber (Tabla 9).'),
    ('t', 'Tabla 9. Desajustes horizontales por matriz', ['Tipo de desajuste', 'Matrices', '% de 50', 'Programas (de 39)'],
     [['Verbo repetido entre competencias específicas', '5', '10 %', '3'],
      ['Ausencia de un tipo de saber', '0', '0 %', '0']]),
    ('p', 'Los 586 registros se distribuyen en Saber 37,9 %, SaberHacer 31,1 % y SaberSer 31,1 % (Figura 3); por matriz, SaberHacer '
          'oscila entre 28,6 % y 33,3 % y Saber entre 33,3 % y 42,9 %. La paridad responde a la plantilla: cada competencia específica '
          'se descompone en un RA de cada tipo de saber y cada competencia genérica, en un RA de Saber. Sobre los 338 RA únicos, la '
          'distribución es 47,6 %, 36,4 % y 16,0 %, porque cada RA de SaberSer se reutiliza en 3,4 competencias en promedio, frente a '
          '1,4 en Saber y 1,5 en SaberHacer.'),
]

RESULTADOS_R3 = [
    ('p', 'R3. Evaluabilidad (V3). Se consideró evaluable el RA con verbo observable —en SaberSer se admite el verbo afectivo de la '
          'taxonomía declarada— y con finalidad de desempeño o producto explícito. Los 338 RA únicos cumplen ambos criterios en las '
          '50 matrices (V3 = 100 %). La plantilla impone la estructura verbo + objeto + finalidad + condición; por ello V3 es constante '
          'y figura en la Figura 1 como condición del instrumento y se excluye de R6.'),
]

RESULTADOS_R4 = [
    ('p', 'R4. Trazabilidad (V4). V4 mide la proporción de RA únicos vinculados a una estrategia mesocurricular con indicador e '
          'instrumento (Paso 4); los indicadores e instrumentos de cada estrategia se asignan a todos los RA de su bloque. Se '
          'distinguen los RA de programa y el RA de la competencia genérica institucional, presente en 40 matrices. V4 alcanza el '
          '87,0 % (294 de 338; media por matriz 87,8 %, rango 62,5 %–100 %), con un comportamiento opuesto entre clases: 98,0 % en '
          'los RA de programa y 5,0 % en el RA genérico (Tabla 10).'),
    ('t', 'Tabla 10. Trazabilidad (V4) por sede y clase de RA', ['Sede', 'RA de programa', 'RA genérico', 'Todos los RA'],
     [['VNAL', '100,0 % (123/123)', '0,0 % (0/15)', '89,1 % (123/138)'],
      ['PBOG', '97,1 % (101/104)', '7,1 % (1/14)', '86,4 % (102/118)'],
      ['PMED', '93,2 % (41/44)', '14,3 % (1/7)', '82,4 % (42/51)'],
      ['HMED', '100,0 % (22/22)', '0,0 % (0/3)', '88,0 % (22/25)'],
      ['HBOG¹', '100,0 % (5/5)', '0,0 % (0/1)', '83,3 % (5/6)'],
      ['Total', '98,0 % (292/298)', '5,0 % (2/40)', '87,0 % (294/338)']]),
    ('n', 'Nota. Entre paréntesis, RA con estrategia meso / RA únicos. ¹ Matriz única; valor descriptivo, excluido de las '
          'comparaciones inferenciales.'),
    ('p', 'De los 44 RA sin estrategia, 38 corresponden a la competencia genérica (Figura 4). Los seis restantes se ubican en Mercadeo y '
          'Publicidad (PMED, 2; PBOG, 1), Diseño Gráfico (PBOG y PMED) y Diseño Industrial (PBOG). Entre sedes, V4 varía de 82,4 % '
          '(PMED) a 89,1 % (VNAL). En el nivel micro, todos los RA están asignados a asignaturas con actividades de evaluación '
          '(mediana: 17 asignaturas por RA). El RA del Paso 4 se emparejó con el del Paso 3 por similitud textual ≥ 0,80 o por '
          'mejor coincidencia mutua (≥ 0,50), para recuperar RA reformulados: en dos matrices VNAL, el Paso 4 conserva la redacción '
          'previa de un RA reformulado en el Paso 3. Con coincidencia exacta, V4 sería 81,7 %.'),
]

RESULTADOS_R5 = [
    ('p', 'R5. Indicadores de resultado e impacto (V5). Las 391 estrategias declaran al menos un indicador (1.185 en total, con 170 '
          'redacciones distintas). Como todos son indicadores de logro del RA, se clasificaron por nivel de evidencia: implementación '
          '(N1), percepción y reacción (N2), aprendizaje demostrado con criterios (N3), transferencia a contextos auténticos (N4) y '
          'efecto externo (N5). Las simulaciones se asignaron a N3, el conteo de participantes a N1 y los indicadores compuestos a su '
          'nivel más alto. V5 corresponde a la proporción de estrategias con evidencia directa del logro (N3 o N4).'),
    ('t', 'Tabla 11. Indicadores de logro por nivel de evidencia', ['Nivel', 'Tipo de evidencia', 'Indicadores', '%', 'Estrategias¹'],
     [['N1 Implementación', 'Indirecta', '808', '68,2 %', '18'],
      ['N2 Percepción y reacción', 'Indirecta', '371', '31,3 %', '369'],
      ['N3 Aprendizaje demostrado', 'Directa', '5', '0,4 %', '3'],
      ['N4 Transferencia', 'Directa', '0', '0,0 %', '0'],
      ['N5 Efecto externo', 'Efecto externo', '1', '0,1 %', '1'],
      ['Total', '', '1.185', '100,0 %', '391']]),
    ('n', 'Nota. ¹ Estrategias según el nivel más alto de sus indicadores.'),
    ('p', 'Dos indicadores concentran casi toda la declaración: el número de estudiantes o de ejecuciones (N1) y la valoración del '
          'aporte de la estrategia a los RA (N2). Solo 3 de las 391 estrategias aportan evidencia directa (V5 = 0,8 %), todas en dos '
          'matrices de VNAL: Técnica Profesional Judicial (promedio superior a 450/500 en práctica simulada; sustentación ante jurados) y '
          'Administración Pública (variación de puntajes antes y después de talleres de refuerzo). Ninguna estrategia evalúa la '
          'transferencia, y solo una registra un efecto externo (vinculación laboral de estudiantes). La clasificación aplicó un libro '
          'de códigos de cinco niveles con cuatro reglas de decisión a las 170 redacciones distintas de indicador (anexo); la '
          'aplicó un solo codificador, por lo que la concordancia entre jueces queda pendiente.'),
]

RESULTADOS_R6 = [
    ('p', 'R6. Asociación entre variables curriculares (V1–V5). Seis pares admiten estimación, porque V3 es constante. La '
          'correlación de Spearman sobre las 50 matrices fue V1–V2 ρ = 0,09 (p = 0,513), V1–V4 ρ = 0,12 (p = 0,417), V1–V5 '
          'ρ = −0,13 (p = 0,381), V2–V4 ρ = −0,04 (p = 0,771), V2–V5 ρ = 0,07 (p = 0,639) y V4–V5 ρ = −0,13 (p = 0,353); ninguna es '
          'significativa, tampoco con una matriz por programa (n = 39). V2 adopta dos valores y V5 es distinta de cero en dos '
          'matrices (Figura 5), por lo que los pares que las incluyen carecen de potencia y no se interpretan.'),
]

RESULTADOS_R7 = [
    ('p', 'R7. Diferencias entre sedes (V1, V2, V4, V5). Las diferencias entre sedes se contrastaron con la prueba de Kruskal-Wallis, dada la '
          'desigualdad de tamaños de grupo y el incumplimiento de los supuestos de normalidad y homocedasticidad. HBOG (n = 1) se trató '
          'como caso descriptivo, porque un grupo unitario carece de varianza estimable, y V3 se excluyó por ser constante. '
          'Con 49 matrices —VNAL (n = 22), PBOG (n = 17), PMED (n = 7) y HMED (n = 3)—, ninguna variable difiere entre sedes, '
          'tampoco con una matriz por programa para controlar la dependencia de la oferta multisede (n = 38) (Tabla 12). Sin '
          'contrastes globales significativos, no se realizaron comparaciones post hoc de Dunn. Con n = 3 en HMED y n = 7 en PMED la '
          'potencia es baja: la no significación indica ausencia de evidencia de diferencia, no equivalencia; las posiciones por sede '
          'de la Tabla 10 son descriptivas.'),
    ('t', 'Tabla 12. Prueba de Kruskal-Wallis entre sedes', ['Variable', 'H(3)', 'p', 'ε²', 'H(3)', 'p', 'ε²'],
     [['', '49 matrices', '', '', '38 programas¹', '', ''],
      ['V1 Correspondencia del perfil', '2,20', '0,531', '0,000', '3,74', '0,290', '0,022'],
      ['V2 Coherencia horizontal', '2,64', '0,451', '0,000', '4,86', '0,182', '0,055'],
      ['V4 Trazabilidad', '3,86', '0,277', '0,019', '2,21', '0,529', '0,000'],
      ['V5 Evidencia directa del logro', '2,51', '0,474', '0,000', '2,28', '0,516', '0,000']]),
    ('n', 'Nota. Se excluye HBOG (n = 1); V3 es constante. ε² = (H − k + 1)/(n − k); los valores negativos se reportan como 0. '
          '¹ Una matriz por programa (la primera por nombre de archivo): VNAL 18, PBOG 15, HMED 3, PMED 2.'),
]

RESULTADOS_R8 = [
    ('p', 'R8. Contenido efectivo de la oferta (modelos analíticos). Los módulos de asignaturas compartidas, tópicos, temas de agenda '
          'global y atributos del perfil sin respaldo describen el contenido declarado en los microcurrículos. Se presentan en tres '
          'bloques.'),
    ('h', 'R8.1 Asignaturas compartidas'),
    ('p', 'De las 709 denominaciones de asignatura, 159 (22,4 %) aparecen en más de un programa y reúnen 937 de las 1.616 asignaturas '
          'sin electivas (58,0 %). Seis están presentes en 28 o 29 de los 39 programas: Análisis y Visualización de Datos, Razonamiento '
          'Cuantitativo, Oportunidades para Emprender, Pensamiento Crítico y Ciudadanías Activas, Cultura, Política y Sociedad, y '
          'Desarrollo Sostenible. La similitud de contenido entre versiones de programas distintos (núcleos temáticos e indicadores de '
          'logro; coseno TF-IDF) es alta: 133 homónimas son idénticas y 15 (9,4 %) divergen, con una media de 0,928 (Tabla 13). Las '
          'divergencias se concentran en asignaturas de denominación genérica —Prácticas (0,035), Investigación (0,068), Formulación y '
          'Evaluación de Proyectos (0,068)— y en las cuatro asignaturas de Inglés General (0,469–0,569).'),
    ('t', 'Tabla 13. Consistencia de contenido en asignaturas homónimas', ['Nivel', 'Criterio', 'Asignaturas', '%'],
     [['Idénticas', 'sim ≥ 0,95', '133', '83,6 %'], ['Alta similitud', '0,60 ≤ sim < 0,95', '11', '6,9 %'],
      ['Divergentes', 'sim < 0,60', '15', '9,4 %'], ['Total', '', '159', '100,0 %']]),
    ('n', 'Nota. Similitud coseno media entre versiones de programas distintos; contenido = núcleos temáticos + indicadores de logro; '
          'sin electivas. El umbral de 0,60 es operativo y no se calibró con revisión experta.'),
    ('p', 'En sentido inverso, 203 pares de asignaturas de programas distintos tienen denominación diferente y similitud ≥ 0,60; '
          'involucran 44 asignaturas (Tabla 14). Catorce pares son variantes de una misma denominación, incluidos errores tipográficos '
          '(«Imvestigación Creación» frente a «Investigación Creación»; «Elementos de Teorías de la Computación» frente a «Elementos de '
          'Teoría de la Computación»). Los 189 restantes son candidatos a homologación, que incluyen falsos positivos léxicos —«Machine '
          'Learning para las TIC» frente a «Infraestructura en la Nube»— y requieren validación disciplinar.'),
    ('t', 'Tabla 14. Pares con distinta denominación y contenido similar (n = 203)', ['Categoría', 'Regla', 'Pares', '%'],
     [['Variante de nombre o error tipográfico', 'Similitud de nombre ≥ 0,85', '14', '6,9 %'],
      ['Candidato a homologación', 'Resto de pares', '189', '93,1 %'],
      ['Total', '', '203', '100,0 %']]),
    ('n', 'Nota. Solo pares entre programas distintos, con similitud de contenido ≥ 0,60. La duplicación por modalidad '
          '(p. ej., Consultorio Jurídico frente a Consultorio Jurídico Virtual) ocurre dentro de un mismo programa y no entra en este '
          'contraste.'),
    ('h', 'R8.2 Tópicos y temas de agenda global'),
    ('p', 'El LDA de consenso (k = 13; 1.192 asignaturas) identifica tópicos de peso desigual (Tabla 15). Comunicación, mercadeo y '
          'planeación estratégica es el tópico dominante en el 27,7 % de las asignaturas; le siguen educación e investigación pedagógica '
          '(14,8 %), diseño centrado en el usuario (12,2 %) y gestión de proyectos, finanzas e ingeniería de producción (10,9 %). Los '
          'tópicos disciplinares de ciencias básicas —probabilidad y estadística (4,9 %), física (4,1 %) y pensamiento numérico y '
          'algebraico (3,8 %)— y los de sostenibilidad y políticas públicas (2,9 %) e IA aplicada a estudios de caso (3,5 %) tienen '
          'peso menor; turismo y gestión organizacional no es dominante en ninguna asignatura. La densidad declarativa es de 4,1 '
          'núcleos por asignatura (mediana 4). Los términos con mayor peso TF-IDF —diseño, datos, aplica, comunicación, información, '
          'digitales— muestran un vocabulario orientado a la aplicación.'),
    ('t', 'Tabla 15. Tópicos del LDA de consenso (k = 13)', ['Tópico', 'Contenido', 'Términos característicos', 'Asignaturas¹', '%'],
     [['1', 'Comunicación, mercadeo y planeación estratégica', 'digital, comunicación, estratégico, control, mercadeo, planeación', '330', '27,7 %'],
      ['5', 'Educación e investigación pedagógica', 'educativo, educación, investigación, proyecto, pedagógico, innovación', '177', '14,8 %'],
      ['4', 'Diseño centrado en el usuario y negocio', 'diseño, usuario, experiencia de usuario, negocio, empatía', '146', '12,2 %'],
      ['6', 'Gestión de proyectos, finanzas e ingeniería de producción', 'proyecto, financiero, ingeniería, producción, herramientas', '130', '10,9 %'],
      ['3', 'Derecho público y administración del Estado', 'público, derecho, administrativo, Colombia, social', '93', '7,8 %'],
      ['9', 'Probabilidad y estadística', 'probabilidad, distribución, variable, estadística', '59', '4,9 %'],
      ['2', 'Física y lenguaje visual publicitario (tópico mixto)', 'movimiento, dinámica, ley, energía, lenguaje publicitario, imagen', '49', '4,1 %'],
      ['8', 'Pensamiento numérico y algebraico', 'pensamiento numérico y algebraico, representación', '45', '3,8 %'],
      ['10', 'Sociedad, cultura y ambiente en Colombia', 'social, ambiental, sociedad, cultural, colombiano', '43', '3,6 %'],
      ['12', 'Expresión y construcción en medios digitales', 'expresión, contexto, construcción, digital', '43', '3,6 %'],
      ['13', 'Estudios de caso con datos e inteligencia artificial', 'estudio de caso, datos, inteligencia artificial, visualización', '42', '3,5 %'],
      ['7', 'Sostenibilidad, políticas públicas y ciudadanía', 'sostenible, políticas públicas, negocios, ciudadanía', '35', '2,9 %'],
      ['11', 'Turismo y gestión organizacional', 'información, integral, innovación, turismo, organizacional', '0', '0,0 %'],
      ['Total', '', '', '1.192', '100,0 %']]),
    ('n', 'Nota. ¹ Asignaturas cuyo tópico de mayor probabilidad es el indicado (confianza media 0,42); una matriz por programa.'),
    ('p', 'La presencia de las 15 tendencias del sector empresarial y educativo se midió en dos dimensiones: amplitud (proporción de '
          'programas con al menos una asignatura asociada) y profundidad (proporción de asignaturas) (Figura 6). Todas las asignaturas '
          'quedan asociadas al menos a una tendencia (1,58 en promedio). La inteligencia artificial aparece en 31 de los 39 programas '
          '(79,5 %) pero solo en 62 de las 1.616 asignaturas (3,8 %); sostenibilidad tiene la misma amplitud y el doble de profundidad '
          '(7,7 %). Las tendencias con mayor profundidad son formación ciudadana, humanística, investigativa y práctica (18,4 %), '
          'marketing y comunicación (16,1 %), transformación digital y datos (15,8 %) y estrategia y gestión de proyectos (15,5 %); '
          'innovación educativa e inclusión (33,3 % de los programas) y talento humano y bienestar (41,0 %) tienen la menor amplitud.'),
    ('fig', 'Figura 6. Temas de agenda global: amplitud y profundidad'),
    ('n', 'Nota. Lista oficial de 15 tendencias (config_tendencias.json), que integra las dos listas anteriores del aplicativo y '
          'depura sus términos genéricos. Una tendencia se asigna si algún término aparece en el nombre de la asignatura o si su '
          'contenido suma al menos dos puntos (término compuesto = 2; simple = 1). La tendencia de IA incluye el término «algoritmos»; '
          'sin él, la tendencia comprendería 58 asignaturas (3,6 %).'),
    ('h', 'R8.3 Atributos del perfil sin respaldo curricular'),
    ('p', 'Los 98 atributos sin respaldo en ninguna capa (R1) se concentran en las poblaciones de actuación: 46 de 423 (10,9 %), '
          'componente que además tiene la menor proporción respaldada en las tres capas (45,2 %) (Tabla 16). Doce matrices no tienen '
          'atributos sin respaldo y ninguna supera el 15 %; superan el 10 % la Especialización en Logística y Gestión de la Cadena de '
          'Abastecimiento (12,8 %), la Especialización en Gerencia Tributaria (12,5 %) y Administración Hotelera y Gastronómica '
          '(10,6 %). Además de los 98 atributos sin respaldo, la revisión cualitativa de las matrices con mayor proporción '
          'identificó tres tipos de vacío, que incluyen atributos con respaldo solo parcial: docencia '
          'declarada sin formación didáctica (Matemáticas, Maestría en Contratación Estatal, Especialización en Gerencia Tributaria), '
          'funciones de dirección o coordinación sin contenido directivo (Maestría en Contratación Estatal, Licenciatura en Educación '
          'Básica Primaria) y poblaciones vulnerables —víctimas del conflicto armado, migrantes, comunidades étnicas— sin tratamiento '
          'curricular (Derecho, Licenciatura en Educación Básica Primaria). Los demás corresponden a escenarios específicos, como '
          'casinos y cruceros en Administración Hotelera y Gastronómica o el comercio exterior en Logística.'),
    ('t', 'Tabla 16. Respaldo de los atributos del perfil por componente (n = 2.574; 50 matrices)',
     ['Componente', 'Atributos', 'Tres capas', 'Sin respaldo', '% sin respaldo'],
     [['Poblaciones de actuación', '423', '191 (45,2 %)', '46', '10,9 %'],
      ['Áreas profesionales', '656', '431 (65,7 %)', '18', '2,7 %'],
      ['Funciones del texto narrativo', '862', '600 (69,6 %)', '23', '2,7 %'],
      ['Tareas profesionales', '633', '468 (73,9 %)', '11', '1,7 %'],
      ['Total', '2.574', '1.690 (65,7 %)', '98', '3,8 %']]),
    ('n', 'Nota. Sin respaldo = ningún respaldo explícito ni parcial en competencias, RA ni asignaturas de la matriz del propio '
          'programa (Etapa 4). Los tipos de vacío proceden de la revisión de las matrices con más del 10 % de atributos sin respaldo '
          'y de las de la lectura de referencia.'),
]

# Interpretaciones retiradas de Resultados (Scopus Q1: Resultados solo datos) para la Discusión
DISCUSION_APORTES = [
    ('p', 'V3, la paridad de tipos de saber y la referencia de cada RA a una competencia son propiedades del instrumento: la '
          'plantilla fija la estructura del RA, su descomposición en tres tipos de saber y la competencia de origen. Su valor no '
          'describe la calidad del diseño y no debe leerse como fortaleza. V1, medida como respaldo del perfil en las tres capas, sí '
          'varía entre matrices (25,0 %–86,5 %).'),
    ('p', 'Los rangos de referencia de un currículo por competencias (Saber 25–45 %, SaberHacer 35–60 %, SaberSer 10–30 %) [fuente '
          'pendiente] no son aplicables a registros con esta estructura; aplicarlos llevaría a concluir un déficit práctico en todas '
          'las matrices. La distribución por RA únicos (SaberSer 16,0 %) indica que el componente actitudinal se formula con pocos RA '
          'reutilizados.'),
    ('p', 'La brecha de trazabilidad no es estructural: ningún RA carece de evaluación en las asignaturas y la falta de estrategia '
          'meso se concentra en la competencia genérica institucional, que los programas no planean en el Paso 4. Acciones: definir '
          'institucionalmente su planeación meso, completar la estrategia de los seis RA de programa y vincular el Paso 4 al Paso 3 '
          'por lista desplegable para que una reformulación no rompa el vínculo. La ausencia documental impide verificar la '
          'articulación, pero no prueba que no ocurra.'),
    ('p', 'Los indicadores declarados informan si la estrategia ocurrió y cómo fue valorada, pero casi nunca si el RA se alcanzó: el '
          '99,5 % es evidencia indirecta. Para sostener decisiones de mejora, el Paso 4 debería exigir por estrategia al menos un '
          'indicador de aprendizaje demostrado (N3) con criterio de desempeño y umbral de suficiencia, y, cuando la estrategia ocurra '
          'en contexto real, uno de transferencia (N4).'),
    ('p', 'Con la plantilla actual, la mayoría de las variables mide el cumplimiento del formato y no decisiones de diseño: V3 es '
          'constante, V2 casi binaria y V5 casi nula; solo V1 y V4 reflejan variación entre programas. Ello explica la ausencia de '
          'asociaciones (R6) y orienta la revisión del instrumento hacia variables que discriminen.'),
    ('p', 'La brecha de trazabilidad tiene dos fuentes distintas: una regla común —el RA de la competencia genérica institucional, sin '
          'estrategia meso en 38 de 40 matrices— y decisiones de programa, que explican seis RA en cinco matrices. La revisión debe '
          'atender ambas, no diferenciarse por sede (R7).'),
    ('p', 'Síntesis. El currículo está bien formulado y articulado, pero no genera evidencia directa del logro: las variables que '
          'dependen de enunciados (V3) y de su articulación (V2, V4) se acercan al techo, el perfil se respalda en las tres capas '
          'en dos de cada tres atributos (V1 = 65,7 %), mientras que solo el 0,8 % de las '
          'estrategias declara un indicador de aprendizaje demostrado (V5). Las brechas son puntuales y localizables —15 asignaturas '
          'homónimas divergentes, 14 variantes de denominación, 98 atributos del perfil sin respaldo, seis RA de programa sin '
          'estrategia— y se entregan como listados nominales. La IA tiene amplitud (79,5 % de los programas) sin profundidad (3,8 % de las '
          'asignaturas); la sostenibilidad combina ambas. El procedimiento es transferible a otra institución multisede con matrices '
          'estandarizadas: identificar campos obligatorios y opcionales, medir la cobertura de los segundos y comparar la variabilidad '
          'dentro y entre unidades académicas.'),
]


# Discusión (versión auditada; cifras verificadas contra auditoria/evidencia_*.json)
DISCUSION = [
    ('p', '4. Discusión. Los resultados permiten examinar cuatro proposiciones sobre el uso de inteligencia artificial generativa (IAg) '
          'y análisis determinista en la gestión curricular: la coherencia como producto de la asistencia analítica, los indicadores '
          'como base de decisión, la trazabilidad como condición de legitimidad y la escala como aporte institucional.'),
    ('h2', '4.1 Coherencia y alineación curricular'),
    ('p', 'La IAg puede asistir la estructuración de las matrices y la programación del aplicativo, mientras la detección de desajustes '
          'corresponde al análisis determinista y la decisión a los equipos académicos (Liu et al., 2024; Pusporini & Nurdiyanto, 2024). '
          'Los resultados matizan esta proposición. V3 alcanza el 100 % y la paridad de tipos de saber (Saber 37,9 %, SaberHacer '
          '31,1 % y SaberSer 31,1 % de los registros) es constante porque la plantilla fija la estructura del RA y su descomposición '
          'por saber (R2–R3); lo mismo ocurre con la referencia de cada RA a su competencia. Estos valores describen el instrumento, '
          'no la calidad del diseño, y no deben leerse como fortaleza.'),
    ('p', 'La correspondencia del perfil (V1) sí discrimina entre programas: el respaldo en las tres capas va de 25,0 % a 86,5 % '
          '(R1). El perfil se sostiene sobre todo en las asignaturas (95,2 % de los atributos) y se debilita en las competencias y los '
          'RA (75,6 % y 72,4 %), de modo que parte de lo que el perfil promete se enseña sin formularse como resultado esperado ni '
          'evaluarse como tal. Los vacíos tampoco son aleatorios: se concentran en las poblaciones de actuación (10,9 % sin respaldo) '
          'y responden a tres patrones —docencia sin formación didáctica, dirección sin contenido directivo y poblaciones vulnerables '
          'sin tratamiento curricular— (R8.3). El perfil ocupacional enumera escenarios del mercado laboral que el plan no desarrolla; '
          'la brecha es más de promesa que de contenido, y su corrección puede pasar tanto por ajustar el plan como por acotar el '
          'perfil que se difunde.'),
    ('p', 'Las inconsistencias reales son escasas y localizables: cinco matrices de tres programas (3 de 39; 7,7 %) repiten un verbo '
          'entre competencias específicas (V2 = 90 %). La alta frecuencia de Analizar no es una inconsistencia, pues 40 de sus 50 '
          'ocurrencias corresponden a la competencia genérica institucional. Por la misma razón, los rangos de referencia por tipo de '
          'saber (SaberHacer 35–60 %) no son aplicables a registros con esta estructura: aplicarlos atribuiría un déficit práctico a '
          'todas las matrices. Sobre los 338 RA únicos, SaberSer representa el 16,0 %, lo que indica que el componente actitudinal se '
          'formula con pocos RA reutilizados en varias competencias.'),
    ('h2', '4.2 Indicadores y toma de decisiones curriculares'),
    ('p', 'La educación orientada a resultados supone que los indicadores permiten decidir sobre el logro. Los datos no respaldan esta '
          'proposición en su forma actual. De 1.185 indicadores declarados en el Paso 4, el 99,5 % es evidencia indirecta: informa si la '
          'estrategia se implementó (N1, 808) o cómo fue valorada (N2, 371), pero no si el RA se alcanzó. Solo cinco demuestran '
          'aprendizaje (N3), ninguno transferencia (N4) y uno un efecto externo (N5); en consecuencia, solo 3 de las 391 estrategias (0,8 %) '
          'declaran evidencia directa del logro (V5, R5).'),
    ('p', 'Tampoco puede sostenerse una relación entre variables. Ninguna correlación fue significativa (V2–V4 ρ = −0,04; V2–V5 '
          'ρ = 0,07; V4–V5 ρ = −0,13; V1–V4 ρ = 0,12; n = 50) y ninguna variable difiere entre sedes (R6, R7). Esta ausencia no '
          'prueba independencia: V3 es constante, V2 casi binaria y V5 distinta de cero en dos matrices, de modo que solo V1 y V4 '
          'varían entre programas, y no covarían. Con '
          'la plantilla actual, la mayoría de las variables mide el cumplimiento del formato y no decisiones de diseño.'),
    ('p', 'El aporte atribuible al sistema se sitúa, por tanto, menos en generar indicadores que en hacer visible su nivel. Para '
          'sostener decisiones de mejora, el Paso 4 debería exigir por estrategia al menos un indicador de aprendizaje demostrado (N3), '
          'con criterio de desempeño y umbral de suficiencia, y uno de transferencia (N4) cuando la estrategia ocurra en contexto real.'),
    ('h2', '4.3 Trazabilidad, gobernanza y control humano'),
    ('p', 'La trazabilidad legitima las decisiones curriculares porque permite reconstruir, ante estudiantes, docentes y pares, la '
          'cadena entre perfil y evidencia de evaluación; el marco de riesgos de IA la sitúa en las funciones Map y Measure (NIST, '
          '2023). El 87,0 % de los 338 RA únicos tiene al menos una estrategia mesocurricular, y todos se evalúan en alguna asignatura '
          '(R4). La brecha no es estructural y tiene dos fuentes: una regla común —el RA de la competencia genérica institucional carece '
          'de estrategia meso en 38 de 40 matrices, porque los programas no la planean en el Paso 4— y decisiones de programa, que '
          'explican seis RA en cinco matrices (98,0 % de trazabilidad sin el RA genérico).'),
    ('p', 'La primera fuente pertenece al diseño del instrumento: si el formulario permite cerrar una matriz sin estrategia para un '
          'RA, la omisión se reproduce en todas las sedes. Corresponde definir institucionalmente la planeación meso de la competencia '
          'genérica y vincular el Paso 4 al Paso 3 mediante lista desplegable, para que una reformulación del RA no rompa el vínculo. '
          'La ausencia documental impide verificar la articulación, pero no prueba que no ocurra.'),
    ('p', 'El análisis automatizado concentra, además, influencia institucional: examina 50 matrices y propone '
          'asociaciones para 2.574 atributos del perfil. Si umbrales, listas y pesos son opacos, la decisión se desplaza de los equipos a parámetros técnicos; '
          'por ello cada parámetro y cada intervención deben registrarse (P4, P9). El control humano debe ser, además, efectivo: '
          'revisar 189 pares candidatos a homologación exige tiempo experto real, y aprobarlos en bloque reproduciría el problema que P3 '
          'busca evitar. La capacidad de revisión debe guardar proporción con el volumen de propuestas que el sistema genera.'),
    ('h2', '4.4 Escala institucional y límites del análisis automatizado'),
    ('p', 'El principal aporte de estas herramientas es el alcance, no la velocidad. Un equipo puede comparar dos versiones de una '
          'asignatura, pero difícilmente 159 asignaturas homónimas, 203 pares de nombre distinto o 2.574 atributos del perfil frente a '
          'tres capas curriculares. Ese alcance solo tiene valor si se traduce en acciones; por ello el producto útil no es el indicador '
          'agregado, sino el listado nominal. La consistencia de las homónimas (media 0,928) y el respaldo del perfil en al menos una '
          'capa (96,2 %) describen un currículo articulado; la acción depende de identificar las 15 asignaturas homónimas divergentes, las 14 '
          'variantes de denominación y los 98 atributos del perfil sin respaldo (R8), que permiten asignar responsables y verificar '
          'las correcciones.'),
    ('p', 'Estos hallazgos son transversales: la correspondencia del perfil concierne al aseguramiento de la calidad y al registro '
          'calificado, pero también a la comunicación institucional, que difunde el perfil, y a los comités curriculares, que resuelven '
          'las brechas. Sin mecanismos de coordinación entre estas áreas, la información no se convierte en capacidad de actuación.'),
    ('p', 'La escala tampoco autoriza a delegar en el sistema decisiones de juicio académico. La similitud coseno mide proximidad '
          'léxica, no equivalencia en profundidad, secuencia u orientación disciplinar: entre los 189 candidatos a homologación hay '
          'falsos positivos léxicos. Conforme a P3, el sistema propone y los pares académicos deciden. La escalabilidad es, así, una '
          'propiedad del procedimiento y no del software: otra institución puede reproducirlo con otras herramientas si dispone de un '
          'instrumento curricular estandarizado, separa lo que el sistema calcula de lo que el experto decide y registra los parámetros '
          'que hacen auditable el análisis.'),
    ('p', 'Esta separación importa porque el currículo no es un documento neutro: define qué conocimientos se reconocen como válidos '
          'y qué sujeto se busca formar, y la mediación algorítmica no vuelve objetivas esas definiciones, sino que desplaza el lugar '
          'donde se ejercen (Devia-Acevedo, 2024). El análisis de tendencias lo ilustra: detecta solo lo previsto en su configuración. '
          'La lista oficial de 15 tendencias cubre todas las asignaturas, pero la inteligencia artificial aparece en el 79,5 % de los '
          'programas y solo en el 3,8 % de las asignaturas (R8). El sistema no mide la actualidad del currículo, sino su coincidencia '
          'con una agenda definida por la institución; si ese resultado orienta la oferta, la selección de la lista participa en la '
          'configuración del currículo y debe someterse a deliberación académica.'),
    ('h2', '4.5 Riesgos latentes identificados en la auditoría'),
    ('p', 'La auditoría del procedimiento identificó tres riesgos que no alteran los resultados reportados, pero requieren control. '
          'El primero es el puntaje académico de los núcleos temáticos, que suma por términos de contenido (análisis, metodología, '
          'sistema) y por extensión del texto, y resta por términos de formato o secuencia (taller, exposición, salida de campo, '
          'introducción). No tiene canal hacia ninguna decisión: se calcula después de los filtros de validez, no alimenta V1–V5 y se '
          'exporta solo como columna informativa; su umbral de 0,5 nunca se implementó y, aplicado, excluiría el 95,2 % de los 6.684 '
          'núcleos (media 0,196). La auditoría retiró, además, el término práctica, que figuraba a la vez en ambas listas.'),
    ('p', 'Sin embargo, el puntaje no es neutral respecto de la disciplina. Agrupados los 39 programas por campo amplio CINE-F 2013, '
          'la mediana del puntaje por programa difiere entre campos (Kruskal-Wallis H = 19,56; gl = 7; p = 0,007; ε² = 0,41); la '
          'mediana por campo va de 0,12 en Ciencias sociales, periodismo e información a 0,22 en Educación (Figura 7). El contraste es exploratorio —ocho '
          'campos, varios con dos o tres programas, y una asignación CINE-F pendiente de validación—, pero basta para descartar su uso '
          'como criterio de comparación entre programas. Debe eliminarse o, si se conserva, rediseñarse separando contenido y formato '
          'pedagógico y validarse por campo antes de cualquier uso decisorio.'),
    ('fig', 'Figura 7. Puntaje académico de los núcleos temáticos'),
    ('p', 'El segundo riesgo es estructural en los archivos fuente: en el Paso 5, el nombre de la asignatura, los créditos, el semestre '
          'y los núcleos se registran en celdas combinadas sobre las filas de Saber, SaberHacer y SaberSer, y la lectura con pandas '
          'conserva el valor solo en la primera fila. Las rutinas originales no propagaban ese valor, por lo que los análisis por '
          'asignatura descartaban dos de cada tres registros; la auditoría incorporó la propagación y los resultados reportados ya la '
          'aplican. El tercero es prospectivo: si la redacción de RA converge hacia los patrones que sugieren los modelos generativos, '
          'los currículos podrían conservar coherencia formal y perder capacidad de diferenciación. Este estudio no lo evalúa; queda '
          'como hipótesis para seguimiento longitudinal.'),
]

# Cambios en la lista de referencias por el método de V1 (Etapa 4), para aplicar en el artículo
REFERENCIAS_CAMBIOS = [
    ('p', 'Se conserva: Robertson, S., & Zaragoza, H. (2009). The probabilistic relevance framework: BM25 and beyond. Foundations '
          'and Trends in Information Retrieval, 3(4), 333–389. https://doi.org/10.1561/1500000019 — la cita la medida '
          'complementaria de saberes y valor agregado (Etapa 4 del Procedimiento); no interviene en V1.'),
    ('p', 'Se retira: Liu, F. T., Ting, K. M., & Zhou, Z.-H. (2008). Isolation forest. En Proceedings of the 2008 Eighth IEEE '
          'International Conference on Data Mining (pp. 413–422). IEEE. https://doi.org/10.1109/ICDM.2008.17 — el detector no se '
          'ejecuta en el flujo (P21; ver Observaciones).'),
    ('p', 'Se agrega: Rahm, E., & Do, H. H. (2000). Data cleaning: Problems and current approaches. IEEE Data Engineering '
          'Bulletin, 23(4), 3–13.'),
    ('p', 'Se agrega: Tukey, J. W. (1977). Exploratory data analysis. Addison-Wesley.'),
    ('p', 'Se agrega: Cohen, J. (1960). A coefficient of agreement for nominal scales. Educational and Psychological Measurement, '
          '20(1), 37–46. https://doi.org/10.1177/001316446002000104'),
    ('p', 'Se agrega: Reimers, N., & Gurevych, I. (2020). Making monolingual sentence embeddings multilingual using knowledge '
          'distillation. En Proceedings of the 2020 Conference on Empirical Methods in Natural Language Processing (EMNLP) '
          '(pp. 4512–4525). Association for Computational Linguistics. https://doi.org/10.18653/v1/2020.emnlp-main.365'),
    ('p', 'Se agrega: Butterfuss, R., & Doran, H. (2025). An application of text embeddings to support alignment of educational '
          'content standards. Educational Measurement: Issues and Practice, 44(1), 73–83. https://doi.org/10.1111/emip.12641'),
    ('p', 'Se agrega: Duarte, R., Lacerda Nobre, Â., Pimentel, F., & Jacquinet, M. (2023). Broader terms curriculum mapping: Using '
          'natural language processing and visual-supported communication to create representative program planning experiences. '
          'Applied System Innovation, 7(1), 7. https://doi.org/10.3390/asi7010007'),
    ('p', 'Se agrega: Zaki, N., Turaev, S., Shuaib, K., Krishnan, A., & Mohamed, E. (2023). Automating the mapping of course '
          'learning outcomes to program learning outcomes using natural language processing for accurate educational program '
          'evaluation. Education and Information Technologies, 28(12), 16723–16742. https://doi.org/10.1007/s10639-023-11877-4'),
    ('n', 'Metadatos de las tres referencias de 2023–2025 verificados en Crossref (api.crossref.org) el 2026-10-04. Cohen (1960) y '
          'Spärck Jones (1972) se conservan por ser las fuentes originales del kappa y del IDF.'),
    ('p', 'Se agrega: Spärck Jones, K. (1972). A statistical interpretation of term specificity and its application in retrieval. '
          'Journal of Documentation, 28(1), 11–21. https://doi.org/10.1108/eb026526'),
]

# Resultados consolidados (Word): solo secciones cerradas por la autora
SECCIONES_RESULTADOS = [
    ('Intro', RESULTADOS_INTRO, 'Cerrada: introducción y Tabla 7'),
    ('R1', RESULTADOS_R1, 'Actualizada: V1 = respaldo del perfil en competencias, RA y asignaturas (revierte D13)'),
    ('R2', RESULTADOS_R2, 'Cerrada: V2 = 90 % (D14); fuente de rangos de referencia pendiente'),
    ('R3', RESULTADOS_R3, 'Cerrada: V3 = 100 %, condición estructural (D15)'),
    ('R4', RESULTADOS_R4, 'Cerrada: V4 = 87,0 % de los 338 RA; 98,0 % sin el RA genérico (D16, D4 ajustada por C03)'),
    ('R5', RESULTADOS_R5, 'Cerrada: V5 = 0,8 % de estrategias con evidencia directa (D17)'),
    ('R6', RESULTADOS_R6, 'Cerrada: sin asociaciones estimables (D18)'),
    ('R7', RESULTADOS_R7, 'Cerrada: sin diferencias entre sedes (D19)'),
    ('R8', RESULTADOS_R8, 'Cerrada: tres bloques; lista oficial de 15 tendencias (D20, D21)'),
    ('Discusion', DISCUSION, 'En revisión: cifras auditadas; puntaje académico recalculado (D22)'),
]
RESULTADOS_PENDIENTES = [
]

SECCIONES = [
    ('Resumen (versión corregida)', RESUMEN),
    ('Corpus', CORPUS),
    ('Procedimiento – Etapa 2', ETAPA_2),
    ('Procedimiento – Etapa 3', ETAPA_3),
    ('Procedimiento – Etapa 4', ETAPA_4),
    ('Procedimiento – Etapa 5', ETAPA_5),
    ('Procedimiento – Etapa 6', ETAPA_6),
    ('Procedimiento – Etapa 7', ETAPA_7),
    ('Resultados – introducción y Tabla 7', RESULTADOS_INTRO),
    ('Resultados – R1 (V1)', RESULTADOS_R1),
    ('Resultados – R2 (V2)', RESULTADOS_R2),
    ('Resultados – R3 (V3)', RESULTADOS_R3),
    ('Resultados – R4 (V4)', RESULTADOS_R4),
    ('Resultados – R5 (V5)', RESULTADOS_R5),
    ('Resultados – R6', RESULTADOS_R6),
    ('Resultados – R7', RESULTADOS_R7),
    ('Resultados – R8', RESULTADOS_R8),
    ('Resultados – aportes para la Discusión', DISCUSION_APORTES),
    ('Discusión', DISCUSION),
    ('Resultados ya verificados', RESULTADOS_VERIFICADOS),
    ('Referencias – cambios por el método de V1', REFERENCIAS_CAMBIOS),
]


def markdown(fecha):
    out = ['# Textos corregidos del artículo', '',
           f'Versiones aprobadas por la autora durante la auditoría (verificación {fecha}). '
           'Las mismas están en el Word y en el Excel (hoja Textos_corregidos).', '']
    for titulo, bloques in SECCIONES:
        out += [f'## {titulo}', '']
        for b in bloques:
            if b[0] == 'p':
                out += [b[1], '']
            elif b[0] == 'n':
                out += [f'*{b[1]}*', '']
            elif b[0] in ('h', 'h2'):
                out += [f'### {b[1]}', '']
            elif b[0] == 'fig':
                out += [f'*[{b[1]}]*', '']
            else:
                _, t, cab, filas = b
                out += [f'**{t}**', '', '| ' + ' | '.join(cab) + ' |', '|' + '---|' * len(cab)]
                out += ['| ' + ' | '.join(f) + ' |' for f in filas]
                out.append('')
    return '\n'.join(out)
