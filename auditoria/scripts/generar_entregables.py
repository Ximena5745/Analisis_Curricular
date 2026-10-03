"""
Genera los entregables de la auditoría de la Etapa 1 (Extracción):
    auditoria/Auditoria_Etapa1_Extraccion.xlsx
    auditoria/Auditoria_Etapa1_Extraccion.docx

Requiere haber ejecutado antes auditoria/scripts/verificar_extraccion.py
"""
import json
import sys as _s0
_s0.path.insert(0, 'auditoria/scripts')
import textos_articulo as TXT
from collections import Counter

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Pt, RGBColor, Cm
from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side

EV = json.load(open('auditoria/evidencia_extraccion.json', encoding='utf-8'))
T = EV['totales']
XLSX = 'auditoria/Auditoria_Etapa1_Extraccion.xlsx'
DOCX = 'auditoria/Auditoria_Etapa1_Extraccion.docx'
ARTICULO = 'articulo_curricular_IA.md (resumen / abstract)'
TEXTO_FUENTE = ('Estudio aplicado de métodos mixtos sobre 50 matrices de 39 programas: 586 registros de '
                'resultados de aprendizaje, 1.612 estrategias mesocurriculares, 1.757 registros de '
                'asignatura y 1.466 elementos de perfiles de egreso […]')

n = lambda x: f'{x:,}'.replace(',', '.')
estrategias_distintas = sum(a['p4_estrategias_distintas'] for a in EV['archivos'])
multi = T['programas_multisede']
multi_txt = ', '.join(f'{k} ({v} sedes)' for k, v in multi.items())
extra_sede = sum(v - 1 for v in multi.values())
perdidos_p1 = T['p1_reales'] - T['p1_codigo']

VERDICT = {
    'OK': ('✅ Confirmada', 'C6EFCE'),
    'PAR': ('⚠️ Parcial', 'FFEB9C'),
    'NO': ('❌ No sustentada', 'FFC7CE'),
    'NV': ('❓ No verificable', 'D9D9D9'),
}

# ---------------------------------------------------------------------------
# Afirmaciones auditadas: cada campo responde a una pregunta concreta
# ---------------------------------------------------------------------------
A = [
    dict(
        id='A1', afirmacion='"50 matrices"',
        que='Cuántos archivos Excel (una matriz curricular por archivo) componen el corpus.',
        donde='Carpeta data/raw/FORMATOS RA CICLO UNO RC — archivos *.xlsx',
        regla='Contar archivos .xlsx que abren correctamente y contienen las hojas Paso1 a Paso5.',
        art='50', rec=n(T['archivos']), coincide='Sí', v='OK', tipo='Ninguno',
        explicacion=(f'Hay {T["archivos"]} archivos .xlsx; todos abren y todos tienen las cinco hojas '
                     'Paso1–Paso5. 24 archivos traen además una hoja "Paso 3 Redacción RA - Backup", que '
                     'se excluye correctamente del análisis.'),
        ejemplo='Ver hoja "Inventario_archivos" (nombre, sede, hojas, huella SHA-256 de cada archivo).',
        riesgo='Ninguno.',
        accion='Ninguna. Conservar la huella SHA-256 para demostrar en el futuro que se usaron los mismos archivos.',
        redaccion='Sin cambios.',
        evidencia='Inventario_archivos'),
    dict(
        id='A2', afirmacion='"39 programas"',
        que='Cuántos programas académicos componen el corpus.',
        donde='Nombre del archivo: FormatoRA_<Programa>_<Sede>.xlsx. Cada archivo es una matriz (unidad programa-sede).',
        regla='DECISIÓN DE MÉTODO D1 (autora, 2026-10-01): programa = denominación; las 50 matrices son 50 unidades programa-sede.',
        art='39', rec=f'{n(T["programas"])} programas / {T["archivos"]} unidades programa-sede', coincide='Sí', v='OK', tipo='Ninguno',
        explicacion=(f'Agrupando los archivos por denominación hay 39 programas. 8 de ellos tienen matriz en varias sedes '
                     f'({multi_txt}), es decir {extra_sede} matrices adicionales: 39 + {extra_sede} = 50. '
                     'La autora decidió mantener 39 programas académicos y tratar cada matriz como unidad programa-sede. '
                     'Cuidado de redacción: no escribir "50 programas"; usar "50 matrices" o "50 unidades programa-sede". '
                     'Caso a confirmar: ComunicacionSocial (VNAL) y ComunicacionSocialPeriodismo (PBOG) cuentan como 2 programas.'),
        ejemplo='ContPub_HMED, ContPub_PBOG y ContPub_VNAL: 1 programa, 3 unidades programa-sede.',
        riesgo='Bajo, si se distingue en todo el texto "programa" (39) de "matriz / unidad programa-sede" (50).',
        accion='Revisar que los denominadores "por programa" usen 39 y los "por matriz" usen 50.',
        redaccion='"50 matrices curriculares (unidades programa-sede) de 39 programas académicos".',
        evidencia='A2_Programas'),
    dict(
        id='A3', afirmacion='"586 registros de resultados de aprendizaje"',
        que='Cuántas filas con un resultado de aprendizaje (RA) redactado hay en las 50 matrices.',
        donde='Hoja "Paso 3 Redacción RA", columna I "Resultados Aprendizaje", desde la fila 3 (fila 2 = encabezado). Se excluye la hoja "- Backup".',
        regla='Contar filas con la columna I no vacía.',
        art='586', rec=f'{n(T["ra_registros"])} filas = {n(T["ra_unicos_por_archivo"])} RA únicos', coincide='Sí', v='OK', tipo='Ninguno',
        explicacion=(f'Se cuentan {n(T["ra_registros"])} filas. Importante para no malinterpretar: son REGISTROS, no RA distintos. '
                     f'Un mismo RA se escribe una vez por cada tipo de saber que desarrolla, por eso hay '
                     f'{n(T["ra_unicos_por_archivo"])} redacciones distintas dentro de cada matriz '
                     f'(y {n(T["ra_unicos_global"])} textos distintos en todo el corpus, porque las sedes de un mismo programa repiten RA). '
                     'El artículo usa correctamente la palabra "registros".'),
        ejemplo='Un RA que desarrolla Saber y SaberHacer aparece en 2 filas: cuenta 2 registros, 1 RA.',
        riesgo='Bajo, siempre que en el cuerpo del artículo no se hable de "586 RA" como si fueran distintos.',
        accion='Revisar que todo el texto use "registros" o aclare 341 formulaciones únicas.',
        redaccion='Sin cambios en el resumen.',
        evidencia='A3_RA_unicos_por_formato y A3_Detalle_RA_unicos'),
    dict(
        id='A4', afirmacion='"1.612 estrategias mesocurriculares"',
        que=('Cuántas estrategias del programa (actividades como "Consultoría a empresas" o "Simulacro Saber Pro") '
             'se declararon para desarrollar los RA.'),
        donde='Hoja "Paso 4 Estrategias mesocurricu". Columna A = RA, columna B = nombre de la estrategia. Datos desde la fila 3 (fila 1 = instrucciones, fila 2 = encabezado).',
        regla='Valor del artículo: filas con columna A (RA) no vacía. Valor alternativo: filas con columna B (estrategia) no vacía.',
        art='1.612', rec=f'{n(T["p4_filas_con_ra"])} filas RA–estrategia / {n(T["p4_con_estrategia"])} estrategias declaradas',
        coincide='El número sí; lo que cuenta, no', v='PAR', tipo='Redacción (unidad mal nombrada)',
        explicacion=(f'La hoja no tiene una fila por estrategia, sino una fila por cada RA vinculado a una estrategia. '
                     f'El nombre de la estrategia se escribe solo en la primera fila de su bloque (columna B) y las filas '
                     f'siguientes la dejan vacía, aunque pertenecen a la misma estrategia. Resultado: hay '
                     f'{n(T["p4_filas_con_ra"])} filas con RA, pero solo {n(T["p4_con_estrategia"])} filas donde se declara '
                     f'una estrategia ({n(estrategias_distintas)} nombres distintos sumando cada matriz). '
                     f'Es decir, 1.612 son VÍNCULOS RA–estrategia, no 1.612 estrategias. '
                     f'Las otras {n(T["p4_sin_estrategia"])} filas son RA asociados a una estrategia declarada más arriba.'),
        ejemplo=('FormatoRA_AdmonEmpresas_HMED, fila 3: RA "Analiza los principios económicos…" + estrategia '
                 '"Prueba estandarizada (simulacro Saber Pro)". Filas 4, 5 y 6: otros RA, columna B vacía (misma estrategia). '
                 'Fila 7: nueva estrategia "Consultoría a empresas". → 5 filas, 2 estrategias.'),
        riesgo='Un lector entiende que el programa tiene ~4 veces más estrategias de las que realmente declaró.',
        accion='Corregir la unidad en el resumen, tablas y cuerpo del artículo.',
        redaccion=(f'"1.612 vínculos entre resultados de aprendizaje y estrategias mesocurriculares '
                   f'({n(T["p4_con_estrategia"])} estrategias declaradas)".'),
        evidencia='A4_Ejemplos_Paso4'),
    dict(
        id='A5', afirmacion='"1.757 registros de asignatura"',
        que='Cuántas filas de asignatura o módulo (nivel microcurricular) hay en las 50 matrices.',
        donde='Hoja "Paso 5 Estrategias micro", columna D "Nombre asignatura o módulo", desde la fila 3.',
        regla='Contar filas con columna D no vacía y EXCLUIR la fila final de totales de cada matriz.',
        art='1.757', rec=f'{n(T["p5_registros"])} (pero el código produce {n(T["p5_filas_col_D"])})',
        coincide='Sí, solo con un filtro que el código no tiene', v='PAR', tipo='Método (no reproducible desde el código)',
        explicacion=(f'En la columna D hay {n(T["p5_filas_col_D"])} filas con contenido. Al final de cada matriz hay una fila de '
                     f'cierre — p. ej. "Total asignaturas del programa" — donde la columna D tiene un NÚMERO (42, 47…), '
                     f'no un nombre de asignatura. Son {T["p5_totales"]} filas, una por archivo. '
                     f'{n(T["p5_filas_col_D"])} − {T["p5_totales"]} = {n(T["p5_registros"])}: el valor del artículo es correcto. '
                     f'El problema es que el código del repositorio (src/extractor.py) NO excluye esas filas: si alguien '
                     f'vuelve a ejecutar el análisis obtiene {n(T["p5_filas_col_D"])}, y en el análisis de asignaturas '
                     f'aparecen 50 "asignaturas" llamadas "42", "47", etc. Además, {T["p5_sin_ra"]} asignaturas no tienen RA '
                     'asociado (columna B vacía).'),
        ejemplo='FormatoRA_AdmonEmpresas_HMED: columna C = "Total materias (asignaturas y módulos) del programa", columna D = 42.',
        riesgo='Un auditor que re-ejecute el código no reproduce el 1.757; los resultados de asignaturas compartidas (A10) y de IA micro (A11) pueden cambiar.',
        accion='Agregar en el extractor el filtro de filas de totales y documentarlo en Método.',
        redaccion='Sin cambio de cifra. Añadir en Método: "se excluyó la fila de totales de cada matriz (50 filas)".',
        evidencia='A5_Filas_totales'),
    dict(
        id='A6', afirmacion='"1.466 elementos de perfiles de egreso"',
        que='Cuántos textos de perfil se analizaron.',
        donde='Hoja "Paso1 Analisis perfil egreso", columnas C "Perfil profesional" y D "Perfil ocupacional", fila 3.',
        regla=('DECISIÓN DE MÉTODO (autora): se denomina "perfil profesional y ocupacional" (no "perfil de egreso") y '
               'una celda con contenido = un registro, sin dividir el texto en frases.'),
        art='1.466', rec='100 (50 perfiles profesionales + 50 ocupacionales)', coincide='No',
        v='NO', tipo='Método (unidad no realista + filtro silencioso en el código) y redacción (denominación)',
        explicacion=(f'El 1.466 sale de partir el texto de 9 columnas en frases cada vez que hay "/", saltos de línea o viñetas: '
                     'una celda de "Tareas profesionales" puede convertirse en 35 "elementos". La autora descartó esa unidad '
                     'por no ser realista. Además, el código omite sin aviso 6 columnas en '
                     f'{T["p1_archivos_variante"]} matrices cuyo encabezado está escrito distinto ("Saberhacer", "ÁreasProfesionales"…), '
                     f'perdiendo {n(perdidos_p1)} fragmentos: por eso da 1.466 y no {n(T["p1_reales"])}. '
                     'Contando celdas: cada matriz tiene exactamente 1 perfil profesional y 1 ocupacional = 100 registros. '
                     '(Las 9 columnas de la hoja suman 988 celdas; Saber/SaberHacer/SaberSer, 666, son insumos de la redacción de competencias, no perfil.)'),
        ejemplo='ComunicacionSocial_VNAL: el código produce 7 fragmentos (pierde 75); con la regla nueva aporta 2 registros: 1 perfil profesional y 1 ocupacional.',
        riesgo='Alto: el 10,6 % de "alertas de falta de respaldo" (A9) se calculó sobre fragmentos y no es trasladable a 100 perfiles; debe recalcularse.',
        accion='Cambiar la unidad y la denominación en todo el artículo; recalcular A9 sobre los 100 textos de perfil.',
        redaccion='"50 perfiles profesionales y 50 perfiles ocupacionales".',
        evidencia='A6_Perfil_columnas'),
]

PENDIENTES_AFIRM = [
    # (ID, tema, etapa, qué falta definir / opciones / recomendación)
    ('Tabla 16', 'Tópicos del análisis temático', 'Resultados',
     'Re-estimar con el LDA de consenso (k = 13; consolidado/topicos_lda.xlsx al correr run_analysis.py). Nota: el tópico 1 (mercadeo, comunicación, planeación) es dominante en 330 de 1.192 asignaturas y el tópico 11 en ninguna; confianza media 0,42.'),
    ('A11', 'IA en 79,5 % de los programas y 3,3 % de los registros', 'Resultados',
     'Búsqueda por palabra completa ya corregida. Definir la base: con texto de RA 31/39; con núcleos + indicadores 32/39 y 86 de 1.616 asignaturas.'),
    ('V1–V5', 'Tabla 2 (variables)', 'Variables',
     'V1 cerrada (D13); V2 cerrada (D14 = 90 %); V3 cerrada (D15 = 100 %, estructural); V4 cerrada (D16 = 87,1 %; 98,0 % sin RA genérico); V5 definida (D17 = 0,8 % de estrategias con evidencia directa; falta kappa). Pendientes: V5 constante por estrategia. Luego regenerar la Figura 1 sin V1.'),
    ('P16', 'Reportes por programa (Etapa 7)', 'Procedimiento',
     'DECISIÓN: nombrar reporte_<Programa>_<Sede> (hoy 50 matrices → 39 informes por sobrescritura). Recomendado; no cambia cifras.'),
    ('P17', 'Versión de Python y bibliotecas (Tabla 6)', 'Procedimiento',
     'DECISIÓN: indicar el entorno de la corrida final (Docker 3.10, entorno local 3.12.7; la auditoría usó 3.14) y generar requirements con versiones exactas (pip freeze).'),
    ('P21', 'Isolation Forest en la Tabla 6', 'Procedimiento',
     'DECISIÓN: no se usa (detectar_anomalias_nucleos no se invoca). Quitar de la Tabla 6 (recomendado) o integrarlo y describirlo en una etapa.'),
    ('P20', 'Registro de la estructuración generativa', 'Procedimiento',
     'DECISIÓN: aportar el registro de entradas, salidas y decisiones humanas (fuera del repositorio) o eliminar la frase.'),
    ('P22', 'Nombre del aplicativo "CurriculoPoli"', 'Procedimiento',
     'CONFIRMAR: el código titula la app "Analisis Tematico Microcurricular". Añadir "modalidad" a los filtros del texto.'),
    ('P19', 'Código documentado', 'Procedimiento',
     'Falta versionar el cálculo de V3 y la fuente de las Tablas 16–17 originales; acotar la afirmación si no aparecen.'),
    ('Corpus', 'Fuente del 63 % de la oferta', 'Corpus', 'Citar documento institucional, fecha de corte y total de programas.'),
    ('Código', 'analisis_tematico_avanzado.py (núcleos)', 'Código',
     'DECISIÓN: reconocer "Tipo de saber", no rellenar núcleos hacia abajo y quitar el filtro de tipo de saber (6.631 → 6.671).'),
    ('Inferencia', 'Pruebas por sede/nivel', 'Resultados',
     'Repetir con una matriz por programa: los 8 multisede comparten RA y 89–100 % de núcleos.'),
    ('Dashboard', 'Cobertura del perfil por grupo', 'Código', 'Opcional: mostrar cobertura_por_grupo (D9) en dashboard_tematico.py.'),
    ('Discusión', 'Validación de la Discusión auditada', 'Discusión',
     'Revisar 4.1–4.5 (Textos_corregidos, Resultados_consolidado.docx). Confirmar citas (Liu et al., 2024; Pusporini & Nurdiyanto, 2024; NIST, 2023; Devia-Acevedo, 2024) y la definición de P3, P4 y P9 en el Marco.'),
    ('CINE-F', 'Asignación CINE-F de los programas', 'Discusión / R8',
     'Validar la hoja CINE-F_programas (3 programas con alternativa). El contraste del puntaje académico (D22, Figura 7) y la propuesta GreenMetric dependen de ella; recalcular con verificar_score_academico.py si cambia.'),
    ('Git', 'Publicación', 'Proyecto',
     'Commits locales en auditoria/p2-extractor-encabezados; push a origin rechazado (403, cuenta PlaneacionPoli). Definir cuenta o remoto.'),
]

ANOMALIAS = [
    ('Alta', 'Código', 'Filtro silencioso de columnas del perfil (24 matrices pierden 6 de 9 campos).', 'src/perfil_coverage_analyzer.py:197; config.py:397', 'A6, A9', 'Normalizar encabezados antes de extraer.'),
    ('Alta', 'Reproducibilidad', 'Las 50 filas de totales del Paso 5 no se excluyen en el código; el 1.757 no sale del pipeline.', 'src/extractor.py:380', 'A5, A10, A11', 'Filtrar filas cuya columna D sea numérica.'),
    ('Alta', 'Reproducibilidad', 'Los reportes por programa se nombran sin sede: los programas multisede se sobrescriben (50 matrices → 39 nombres; hay 47 JSON mezclando corridas).', 'run_analysis.py:112-114', 'Salidas por programa', 'Nombrar reporte_<Programa>_<Sede> y limpiar la carpeta antes de correr.'),
    ('Media', 'Extracción', 'Paso 4 se lee con la fila de instrucciones como encabezado; el encabezado real entra como dato (+50 filas).', 'config.py:62 (HEADER_ROWS)', 'A4', 'Usar fila de encabezado 2 (índice 1).'),
    ('Media', 'Extracción', 'Paso 2 (competencias): en 44 matrices la fila tomada como encabezado es de instrucciones. El artículo además dice 217 en tablas y 220 en el texto.', 'config.py:60', 'Competencias (no auditada)', 'Auditar el conteo de competencias.'),
    ('Media', 'Código', 'Cada extract_* captura cualquier error y devuelve una tabla vacía: un archivo puede desaparecer sin aviso.', 'src/extractor.py:302 y ss.', 'Todas', 'Registrar el error y detener la ejecución, o reportar conteo por archivo.'),
    ('Media', 'Extracción', '7 combinaciones distintas de hojas; en 25 matrices la hoja Paso 3 tiene un espacio final y se resuelve por coincidencia de prefijo.', 'src/extractor.py:197-216', 'A3', 'Funciona hoy; validar explícitamente que no se lea la hoja Backup.'),
    ('Baja', 'Formato', 'Encabezados con variantes en todas las hojas (Paso 5 tiene 7 versiones; errata "C.Fudamentación").', 'Archivos crudos', '—', 'Mapa de sinónimos de columnas.'),
    ('Baja', 'Calidad de datos', f'{T["p5_sin_ra"]} asignaturas sin RA asociado; 201 filas micro sin "Tipo de Saber".', 'Paso 5', 'A8', 'Reportar como limitación.'),
]

EMBUDO = [
    ('Archivos', 'Archivos .xlsx en la carpeta', T['archivos'], ''),
    ('Archivos', 'Programas (decisión: 1 matriz = 1 programa)', T['archivos'], f'Antes 39 denominaciones; {extra_sede} eran sedes adicionales'),
    ('Paso 3 – RA', 'Filas con RA (columna I)', T['ra_registros'], 'Sin pérdidas'),
    ('Paso 3 – RA', 'RA distintos dentro de cada matriz', T['ra_unicos_por_archivo'], 'Un RA se repite por cada competencia a la que aporta'),
    ('Paso 4 – Meso', 'Filas con RA (columna A) = vínculos RA–estrategia', T['p4_filas_con_ra'], 'Valor del artículo'),
    ('Paso 4 – Meso', 'Filas donde se declara una estrategia (columna B)', T['p4_con_estrategia'], 'Estrategias reales'),
    ('Paso 5 – Micro', 'Filas con contenido en columna D', T['p5_filas_col_D'], 'Lo que produce el código'),
    ('Paso 5 – Micro', '(−) Filas de totales', -T['p5_totales'], 'Una por matriz'),
    ('Paso 5 – Micro', '= Registros de asignatura', T['p5_registros'], 'Valor del artículo'),
    ('Paso 1 – Perfil', 'Elementos leyendo los 9 campos', T['p1_reales'], 'Valor correcto'),
    ('Paso 1 – Perfil', '(−) Elementos perdidos por nombre de columna', -perdidos_p1, f'{T["p1_archivos_variante"]} matrices afectadas'),
    ('Paso 1 – Perfil', '= Elementos que usa el código', T['p1_codigo'], 'Valor del artículo (unidad descartada)'),
    ('Paso 1 – Perfil', 'Celdas con contenido en las 9 columnas (sin dividir)', 988, 'Referencia'),
    ('Paso 1 – Perfil', 'Perfiles profesionales + ocupacionales (1 celda = 1 registro)', 100, 'Unidad adoptada: 50 + 50'),
]

DECISIONES = [
    ('D1', '2026-10-01', 'Unidad "programa"', 'Se mantienen 39 programas académicos (por denominación); las 50 matrices son unidades programa-sede. (Revierte la decisión previa "cada matriz es un programa".)', 'A2, A11, C2 y toda cifra "por programa"'),
    ('D2', '2026-10-01', 'Denominación del Paso 1', 'Se denomina "perfil profesional y ocupacional", no "perfil de egreso".', 'A6, A9'),
    ('D3', '2026-10-01', 'Unidad de conteo del perfil', 'Una celda con contenido = un registro; no se divide el texto en frases ni por separadores.', 'A6, A9'),
    ('D4', '2026-10-01', 'Unidad de RA', 'RA único = texto normalizado deduplicado dentro de cada matriz (341). Las filas (586) solo para vínculos.', 'A3, A7, A8'),
    ('D5', '2026-10-01', 'Unidad de estrategia meso', 'Estrategia = fila con nombre en la columna B del Paso 4 (391). Las 1.612 filas son vínculos RA–estrategia.', 'A4, A8'),
    ('D6', '2026-10-01', 'Registros de asignatura', 'Una asignatura por matriz, excluyendo la fila de totales (1.757).', 'A5, A10, A11'),
    ('D10', '2026-10-02', 'Asignaturas compartidas (Etapa 5)', 'Contenido de una asignatura = núcleos temáticos + indicadores de logro de todo su bloque (sin texto de RA); se comparan las 1.616 asignaturas sin muestreo y solo entre programas distintos; umbral 0,60 sin calibración documentada.', 'P12, P12b, A10'),
    ('D9', '2026-10-02', 'Cobertura del perfil (Etapa 4)', 'Elemento = una celda de los 9 campos del Paso 1 (988), sin dividir; corpus = contenidos de las asignaturas (sin SaberAsociado ni textos de RA, derivados del perfil). Resultados agregados en 4 grupos (Perfil, Saberes, Campo de actuación, Valor agregado; config.GRUPOS_PERFIL), cada celda con el umbral de su campo.', 'P9, P9b, P9c, A9, dashboard_tematico.py'),
    ('D8', '2026-10-02', 'Puntaje de calidad (Etapa 3)', 'Exigencia por nivel declarado en escala común 1–6 según la progresión de su dominio; completitud y cobertura de competencias como condiciones verificadas; puntaje = exigencia 40 % + equilibrio 30 % + variedad 30 %.', 'P7, P8, dashboard/app.py, reportes'),
    ('D22', '2026-10-03', 'Puntaje académico en la Discusión', 'Recalculado sobre el corpus D7 (6.671 núcleos; fórmula vigente sin «práctica»; −0,10 por formato): media 0,197; 95,2 % bajo 0,5. El contraste aplicado/teórico (U = 4.151.991; p = 0,565; 5.780 núcleos) no es reproducible: la clasificación no está en el repositorio. Se sustituye por Kruskal-Wallis por campo amplio CINE-F (decisión de la autora): mediana por programa H = 19,71, gl = 7, p = 0,006, ε² = 0,41. Conclusión invertida: el puntaje no es neutral a la disciplina. Script: auditoria/scripts/verificar_score_academico.py.', 'Discusión 4.5, Figura 7'),
    ('D21', '2026-10-03', 'Lista oficial de tendencias', 'config_tendencias.json = 15 tendencias del sector empresarial (12) y educativo (3), consolidadas de la propuesta integrada de 32 (auditoria/propuesta_tendencias_integradas.json) que une config.TEMATICAS y la lista anterior (respaldo en auditoria/config_tendencias_anterior.json); IA como tendencia propia. Regla única en src/tendencias.py: término en el nombre o ≥ 2 puntos en el contenido (compuesto = 2; simple = 1). Aplicada en dashboard_tematico.py y analisis_tematico_avanzado.py. Cobertura 100 % de 1.616 asignaturas.', 'R8.2, Figura 6, dashboard, CA.3, CA.6'),
    ('D20', '2026-10-03', 'R8 (modelos analíticos)', 'R8 en tres bloques (asignaturas compartidas, tópicos y temas, cobertura del perfil) con valores D7, D9–D12 y P14; Tablas 12–15 y Figura 6 recalculadas (auditoria/scripts/verificar_r8.py, figura_tendencias.py, verificar_cobertura_perfil.py). La matriz de valor (Tabla 15 original), el resumen V1–V5 (Tabla 16 original) y la síntesis pasan a la Discusión. Lista oficial de temas pendiente de confirmar.', 'R8, Tablas 12–15, Figura 6'),
    ('D19', '2026-10-03', 'Diferencias entre sedes (Resultados R7)', 'Kruskal-Wallis sobre V2, V4 y V5 (V1 y V3 constantes; HBOG descriptiva), con 49 matrices y con una matriz por programa (n = 38); ninguna significativa. Tabla 11 con ambas versiones; se elimina la Figura 8 (cajas por sede con valores anteriores) y la Implicación pasa a la Discusión.', 'R7, Tabla 11'),
    ('D18', '2026-10-03', 'Asociación entre variables (Resultados R6)', 'No se interpretan correlaciones: V1 y V3 constantes, V2 binaria, V5 distinta de cero en 2 matrices. Spearman sobre los 3 pares estimables (n = 50 y n = 39), todos no significativos. Se retiran la Tabla 13 y la Figura 7 (matriz de correlación); se sustituyen por la distribución por matriz (Figura 5, auditoria/scripts/figura_r6.py).', 'R6, Figura 5'),
    ('D17', '2026-10-03', 'V5 (Resultados R5)', 'Todos los indicadores del Paso 4 son indicadores de logro del RA (modelo institucional). Se clasifican por nivel de evidencia: N1 Implementación, N2 Percepción y reacción, N3 Aprendizaje demostrado, N4 Transferencia, N5 Efecto externo (Kirkpatrick con nivel de implementación), con 4 reglas de decisión (simulación = N3; contar participantes = N1; compuesto = nivel más alto; productos sin criterio = N1). Evidencia directa = N3–N4; N5 se reporta aparte. Unidad de validación: 170 redacciones (kappa pendiente). V5 = % de estrategias con evidencia directa = 3/391 (0,8 %). Regla: auditoria/scripts/verificar_v5.py; Excel: auditoria/Clasificacion_indicadores_V5.xlsx.', 'R5, Tabla 10, Figura 1'),
    ('D16', '2026-10-02', 'V4 (Resultados R4)', 'V4 = % de los 341 RA únicos (D4, incluido el RA genérico institucional) vinculados a una estrategia meso con indicador e instrumento. Bloque de estrategia: B/C/E combinadas; indicadores e instrumentos de cualquier fila del bloque valen para todos sus RA. Emparejamiento: similitud ≥ 0,80 (sin autojunk) o mejor coincidencia mutua ≥ 0,50 (RA reformulados). Resultado con clasificación diferenciada (Tabla 9; antes Tabla 10, se renumera al eliminar la Tabla 9 de V3): todos 297/341 = 87,1 % (media por matriz 87,9 %); RA de programa 295/301 = 98,0 %; RA genérico 2/40 = 5,0 %; micro 100 %. Script: auditoria/scripts/v4_alternativas.py.', 'R4, Figura 4, Figura 1'),
    ('D15', '2026-10-02', 'V3 (Resultados R3)', 'V3 = % de RA únicos por matriz con verbo observable (en SaberSer se admite el verbo de la taxonomía afectiva) y finalidad de desempeño o producto declarado. Resultado 100 % (341/341): condición estructural, fuera del radar y de las correlaciones.', 'R3, Tabla 9, Figura 1'),
    ('D14', '2026-10-02', 'V2 (Resultados R2)', 'V2 = % de matrices sin verbo repetido entre competencias específicas (la genérica institucional "Analizar fenómenos contemporáneos" no cuenta como repetición) = 45/50 = 90 %. Vacíos de tipo de saber: 0 (constante, se informa en el texto).', 'R2, Tabla 8, Figura 1'),
    ('D13', '2026-10-02', 'V1 (Resultados R1)', 'V1 = correspondencia competencia–RA: cada RA cita una competencia del Paso 2. Es una condición estructural de la matriz (100 % en las 50 matrices), no un indicador de calidad; se excluye del radar (Figura 1) y de las correlaciones. El tramo competencia → perfil no es verificable (la matriz no lo registra).', 'R1, Tabla 2, Figura 1, R6'),
    ('D11', '2026-10-02', 'Corpus del LDA (Etapa 6)', 'LDA de consenso sobre los núcleos temáticos depurados agrupados por asignatura (una matriz por programa, lemas; 1.192 documentos), k = 13, 10 semillas (src/topic_modeler.modelar_topicos_consenso). Reemplaza el LDA sobre SaberAsociado.', 'P13, P14, Tabla 16'),
    ('D12', '2026-10-02', 'Temas de agenda global (Etapa 6)', 'Cada término se busca como palabra completa y sin tildes (analisis_tematico_avanzado.py y dashboard_tematico.py), no como subcadena.', 'P15, A11, Tabla 17, dashboard'),
    ('D7', '2026-10-01', 'Unidad "núcleo temático"', 'Un núcleo = un ítem numerado de la celda de núcleos ("1. …", "2. …"), aunque ocupe varias líneas; si la celda no está numerada, cada línea es un núcleo. No se corta por comas ni por saltos de línea internos.', 'C13, Etapa 2 (LDA, densidad, asignaturas compartidas)'),
]

REDACCION = [
    ('Original', 'Estudio aplicado de métodos mixtos sobre 50 matrices de 39 programas: 586 registros de resultados de aprendizaje, '
                 '1.612 estrategias mesocurriculares, 1.757 registros de asignatura y 1.466 elementos de perfiles de egreso, analizados '
                 'mediante cinco variables de coherencia y trazabilidad, minería de texto, modelado temático y contraste estadístico exploratorio.'),
    ('Propuesta de la autora', 'Estudio aplicado de métodos mixtos sobre 50 matrices curriculares correspondientes a 50 programas académicos: '
                 '341 resultados de aprendizaje únicos por programa, 391 estrategias mesocurriculares declaradas, 1.757 registros de '
                 'asignatura y 100 perfiles de egresados (profesional y ocupacional), analizados mediante […]'),
    ('Versión corregida vigente (auditoría)', TXT.RESUMEN[0][1]),
    ('Notas', TXT.RESUMEN[1][1] + ' Ajustes: 39 programas (D1); RA únicos (D4); estrategias declaradas (D5); '
              '"50 perfiles profesionales y 50 ocupacionales" (D2, D3); perfil 5,0 % (D9); homónimas 9,4 % (D10).'),
]

MENCIONES_39 = [
    (531, 'Tabla 17 tendencias', '"39 programas · 1.807 registros"', 'Mantener 39; cambiar 1.807 por 1.757 (1.807 incluye las 50 filas de totales).'),
    (539, 'Tabla 17 – IA', '60 registros = 3,3 % (60/1.807)', 'Recalcular sobre 1.757 registros.'),
    (548, 'Resultados IA', '"…3,3% de los registros"', 'Actualizar con el valor recalculado.'),
    (601, 'Recomendaciones', '"79,5% vs 3,3%"', 'Actualizar el 3,3 %.'),
    (743, 'Conclusiones', '"…3,3% de los registros"', 'Actualizar el 3,3 %.'),
]

# ---------------------------------------------------------------------------
# EXCEL
# ---------------------------------------------------------------------------
HDR = PatternFill('solid', fgColor='1F3864')
thin = Side(style='thin', color='BFBFBF')
BOX = Border(left=thin, right=thin, top=thin, bottom=thin)
WRAP = Alignment(wrap_text=True, vertical='top')


def tabla(ws, cabeceras, filas, anchos, fila0=1):
    for j, c in enumerate(cabeceras, 1):
        cell = ws.cell(fila0, j, c)
        cell.font = Font(bold=True, color='FFFFFF')
        cell.fill = HDR
        cell.alignment = Alignment(wrap_text=True, vertical='center')
        cell.border = BOX
    for i, fila in enumerate(filas, fila0 + 1):
        for j, v in enumerate(fila, 1):
            cell = ws.cell(i, j, v)
            cell.alignment = WRAP
            cell.border = BOX
    for j, w in enumerate(anchos, 1):
        ws.column_dimensions[ws.cell(1, j).column_letter].width = w
    ws.freeze_panes = ws.cell(fila0 + 1, 2)
    ws.auto_filter.ref = f'A{fila0}:{ws.cell(fila0, len(cabeceras)).column_letter}{fila0 + len(filas)}'


wb = Workbook()
ws = wb.active
ws.title = 'LEEME'
leeme = [
    ('Auditoría analítica independiente — Etapa 1: Extracción de datos', ''),
    ('Artículo', ARTICULO),
    ('Texto auditado', TEXTO_FUENTE),
    ('Fecha de verificación', EV['fecha']),
    ('Datos crudos (solo lectura)', EV['carpeta'] + ' — 50 archivos; huellas SHA-256 en "Inventario_archivos"'),
    ('Cómo reproducir', '1) python auditoria/scripts/verificar_extraccion.py   2) python auditoria/scripts/generar_entregables.py'),
    ('', ''),
    ('VEREDICTOS', ''),
    ('✅ Confirmada', 'El valor coincide con los datos y el método es adecuado.'),
    ('⚠️ Parcial', 'El valor coincide, pero hay reservas de método o de redacción.'),
    ('❌ No sustentada', 'El valor no coincide o el método no lo respalda.'),
    ('❓ No verificable', 'Falta un dato, archivo o información.'),
    ('', ''),
    ('TIPOS DE ERROR', ''),
    ('Cálculo', 'La operación aritmética o el conteo están mal hechos.'),
    ('Método', 'El procedimiento (filtros, lectura de columnas, reglas) no mide lo que se dice o no es reproducible.'),
    ('Redacción', 'El número es correcto, pero el texto nombra mal lo que se contó o lo interpreta mal.'),
    ('', ''),
    ('HOJAS', ''),
    ('Resumen_afirmaciones', 'Una fila por afirmación: qué se cuenta, dónde, con qué regla, valor, veredicto y acción.'),
    ('Embudo_conteos', 'Cómo se llega desde los archivos crudos a cada cifra (cuántas filas entran y salen en cada paso).'),
    ('Evidencia_por_archivo', 'Conteos de cada matriz; permite comprobar cualquier total sumando la columna.'),
    ('A2_Programas / A4_Ejemplos_Paso4 / A5_Filas_totales / A6_Perfil_columnas', 'Evidencia fila por fila de cada reserva.'),
    ('Anomalias', 'Problemas de extracción y código, por severidad.'),
    ('Pendientes', 'Afirmaciones y verificaciones para las siguientes etapas.'),
    ('Inventario_archivos', 'Archivos crudos con huella SHA-256 para garantizar que una futura auditoría use los mismos datos.'),
]
for i, (a, b) in enumerate(leeme, 1):
    ws.cell(i, 1, a).font = Font(bold=True, size=14 if i == 1 else 11)
    ws.cell(i, 2, b).alignment = WRAP
ws.column_dimensions['A'].width = 38
ws.column_dimensions['B'].width = 120

ws = wb.create_sheet('Resumen_afirmaciones')
cab = ['ID', 'Afirmación del artículo', '¿Qué se está contando?', '¿Dónde se cuenta? (archivo / hoja / columna / filas)',
       'Regla de conteo', 'Valor en artículo', 'Valor recalculado', '¿Coincide?', 'Veredicto', 'Tipo de error',
       'Explicación del veredicto', 'Ejemplo con datos reales', 'Riesgo si no se corrige', 'Acción recomendada',
       'Redacción sugerida', 'Hoja de evidencia']
filas = [[a['id'], a['afirmacion'], a['que'], a['donde'], a['regla'], a['art'], a['rec'], a['coincide'],
          VERDICT[a['v']][0], a['tipo'], a['explicacion'], a['ejemplo'], a['riesgo'], a['accion'],
          a['redaccion'], a['evidencia']] for a in A]
tabla(ws, cab, filas, [6, 22, 32, 34, 30, 11, 18, 14, 16, 20, 70, 45, 35, 35, 40, 18])
for i, a in enumerate(A, 2):
    ws.cell(i, 9).fill = PatternFill('solid', fgColor=VERDICT[a['v']][1])
    ws.cell(i, 9).font = Font(bold=True)

ws = wb.create_sheet('Embudo_conteos')
tabla(ws, ['Hoja / nivel', 'Paso', 'Registros', 'Nota'], [list(e) for e in EMBUDO], [18, 55, 12, 40])

ws = wb.create_sheet('Evidencia_por_archivo')
keys = ['archivo', 'programa_codigo', 'sede', 'p3_ra_registros', 'p3_ra_unicos', 'p4_filas_con_ra',
        'p4_filas_con_estrategia', 'p4_filas_sin_estrategia', 'p5_filas_col_D', 'p5_filas_totales',
        'p5_registros_asignatura', 'p5_asignaturas_sin_ra', 'p1_encabezado', 'p1_elementos_codigo',
        'p1_elementos_reales', 'p1_elementos_perdidos']
nombres = ['Archivo', 'Programa', 'Sede', 'P3: registros RA', 'P3: RA distintos', 'P4: vínculos RA–estrategia',
           'P4: estrategias declaradas', 'P4: filas sin estrategia', 'P5: filas col. D', 'P5: filas de totales',
           'P5: registros asignatura', 'P5: asignaturas sin RA', 'P1: tipo encabezado', 'P1: elementos (código)',
           'P1: elementos (reales)', 'P1: elementos perdidos']
filas = [[a[k] for k in keys] for a in EV['archivos']]
tot = ['TOTAL', '', ''] + [sum(f[j] for f in filas) if isinstance(filas[0][j], int) else '' for j in range(3, len(keys))]
tabla(ws, nombres, filas + [tot], [42, 26, 7] + [13] * 13)
for c in ws[len(filas) + 2]:
    c.font = Font(bold=True)

ws = wb.create_sheet('A2_Programas')
prog = {}
for a in EV['archivos']:
    prog.setdefault(a['programa_codigo'], []).append(a)
dudas = {'ComunicacionSocial': 'Confirmar si es el mismo programa que ComunicacionSocialPeriodismo (PBOG)',
         'ComunicacionSocialPeriodismo': 'Confirmar si es el mismo programa que ComunicacionSocial (VNAL)'}
filas = [[i, p, len(v), ', '.join(x['sede'] for x in v), '\n'.join(x['archivo'] for x in v),
          'Sí' if len(v) > 1 else 'No', dudas.get(p, '')] for i, (p, v) in enumerate(sorted(prog.items()), 1)]
tabla(ws, ['#', 'Programa (según nombre de archivo)', 'Nº matrices', 'Sedes', 'Archivos', '¿Multisede?', 'A validar'],
      filas, [5, 34, 11, 18, 48, 11, 50])

ws = wb.create_sheet('A4_Ejemplos_Paso4')
ws.cell(1, 1, 'Cómo leer: cada fila es un RA. La columna B solo se llena cuando empieza una estrategia nueva; '
              'las filas siguientes con B vacía pertenecen a esa misma estrategia. Por eso filas ≠ estrategias.').font = Font(italic=True)
ej = EV['ejemplos_p4'][:6]
tabla(ws, ['Archivo', 'Fila Excel', 'A: Resultado de aprendizaje', 'B: Estrategia del programa', 'C: Descripción',
           'D: Indicador', '¿Cuenta como estrategia nueva?'],
      [[e['archivo'], e['fila_excel'], e['A_resultado_aprendizaje'], e['B_estrategia_programa'], e['C_descripcion'],
        e['D_indicador'], 'Sí' if e['B_estrategia_programa'] != '(vacío)' else 'No (hereda la de arriba)'] for e in ej],
      [34, 9, 50, 34, 40, 40, 22], fila0=3)

ws = wb.create_sheet('A5_Filas_totales')
tabla(ws, ['#', 'Archivo', 'Fila Excel', 'Columna C (texto)', 'Columna D (valor leído como "asignatura")', 'Créditos'],
      [[i, t['archivo'], t['fila_excel'], t['C_texto'], t['D_valor'], t['creditos']] for i, t in enumerate(EV['filas_totales_p5'], 1)],
      [5, 42, 10, 48, 22, 10])

ws = wb.create_sheet('A6_Perfil_columnas')
tabla(ws, ['Archivo', 'Tipo de encabezado', 'Columnas que el código omite (nombre real ≠ nombre esperado): elementos',
           'Elementos contados por el código', 'Elementos reales', 'Elementos perdidos'],
      [[p['archivo'], p['encabezado'], p['columnas_omitidas_por_el_codigo'], p['elementos_contados'],
        p['elementos_reales'], p['perdidos']] for p in EV['perfil_columnas']],
      [42, 14, 90, 14, 14, 14])

ws = wb.create_sheet('Anomalias')
tabla(ws, ['Severidad', 'Categoría', 'Descripción', 'Ubicación', 'Afecta a', 'Corrección sugerida'],
      [list(a) for a in ANOMALIAS], [10, 16, 70, 30, 22, 45])
color = {'Alta': 'FFC7CE', 'Media': 'FFEB9C', 'Baja': 'E2EFDA'}
for i, a in enumerate(ANOMALIAS, 2):
    ws.cell(i, 1).fill = PatternFill('solid', fgColor=color[a[0]])

ws = wb.create_sheet('Pendientes')
tabla(ws, ['ID', 'Afirmación', 'Etapa', 'Qué verificar'], [list(p) for p in PENDIENTES_AFIRM] + [
    ('—', 'Competencias: 217 (tablas) vs 220 (texto)', 'Extracción', 'Auditar Paso 2 con encabezado correcto.'),
    ('—', '709 asignaturas únicas y 168 compartidas', 'Limpieza', f'Se obtuvieron 716 y 170 con normalización simple; documentar la regla usada.'),
], [6, 60, 14, 70])

ws = wb.create_sheet('Inventario_archivos')
tabla(ws, ['#', 'Archivo', 'Programa', 'Sede', 'Hojas', '¿Hoja Backup Paso 3?', 'Tamaño (bytes)', 'SHA-256'],
      [[i, a['archivo'], a['programa_codigo'], a['sede'], a['hojas'], 'Sí' if a['tiene_backup_paso3'] else 'No',
        a['tamano_bytes'], a['sha256']] for i, a in enumerate(EV['archivos'], 1)],
      [5, 42, 26, 7, 80, 12, 12, 68])
ws = wb.create_sheet('Decisiones_metodo', index=1)
tabla(ws, ['ID', 'Fecha', 'Tema', 'Decisión', 'Afecta a'], [list(d) for d in DECISIONES], [6, 12, 26, 90, 30])
ws = wb.create_sheet('Redaccion_corregida', index=2)
tabla(ws, ['Versión', 'Texto'], [list(r) for r in REDACCION], [28, 150])
ws = wb.create_sheet('Menciones_39', index=wb.sheetnames.index('A4_Ejemplos_Paso4'))
ws.cell(1, 1, 'Con D1 vigente (39 programas) solo deben corregirse las menciones que usan 1.807 registros (D6).').font = Font(italic=True)
tabla(ws, ['Línea', 'Sección', 'Texto actual', 'Acción'], [list(m) for m in MENCIONES_39], [8, 26, 70, 60], fila0=3)

# ---------------------------------------------------------------------------
# ETAPA 2 — EDA de resultados de aprendizaje (si existe la evidencia)
# ---------------------------------------------------------------------------
try:
    EDA = json.load(open('auditoria/evidencia_eda_ra.json', encoding='utf-8'))
except FileNotFoundError:
    EDA = None

if EDA:
    R = EDA['resumen']
    pct = lambda a, b: f'{a / b:.1%}'.replace('.', ',')
    ft, ut = R['filas_por_tipo'], R['unicos_por_tipo']
    u_tot = R['ra_unicos_texto']
    EDA_HALLAZGOS = [
        ('E1', 'Unidad de análisis',
         f'586 filas del Paso 3 corresponden a {u_tot} RA únicos (texto normalizado, dentro de cada matriz). '
         f'Cada RA se repite en promedio {586 / u_tot:.2f} veces (rango por matriz {R["factor_min"]}–{R["factor_max"]}) '
         'porque se copia en cada competencia a la que aporta.',
         f'Mediana de RA únicos por matriz: {R["unicos_mediana"]:.0f} (mín. {R["unicos_min"]}, máx. {R["unicos_max"]}).',
         'Calcular porcentajes y pruebas estadísticas sobre RA únicos por matriz; usar filas solo para preguntas sobre vínculos competencia–RA.'),
        ('E2', 'Distribución por tipo de saber depende de la unidad',
         f'Por filas: Saber {pct(ft["Saber"], 586)}, SaberHacer {pct(ft["SaberHacer"], 586)}, SaberSer {pct(ft["SaberSer"], 586)} '
         f'(coincide con el artículo: 37,9 / 31,1 / 31,1). Por RA únicos: Saber {pct(ut["Saber"], u_tot)}, '
         f'SaberHacer {pct(ut["SaberHacer"], u_tot)}, SaberSer {pct(ut["SaberSer"], u_tot)}.',
         'Los RA de SaberSer son pocos y genéricos y se reutilizan en varias competencias; contar filas los infla.',
         'El "equilibrio cercano a un tercio" del artículo es un efecto de contar filas. Reportar ambas distribuciones y matizar la conclusión.'),
        ('E3', 'Numeración inconsistente',
         f'{R["inconsistencias"]} casos en {R["matrices_con_inconsistencia_numeracion"]} matrices: el mismo texto con dos números o el mismo número con dos textos. '
         f'Por eso contar por "Número de resultado" da {R["ra_unicos_numero"]} y por texto {u_tot}.',
         'Ej.: AdmonEmpresas_HMED, "Ejecuta acciones de gestión…" figura como RA 5 y RA 7.',
         'Declarar en Método que la identidad del RA es su texto, no su número.'),
        ('E4', 'RA sin estrategia mesocurricular',
         f'{u_tot - R["ra_con_meso"]} RA únicos ({pct(u_tot - R["ra_con_meso"], u_tot)}) no aparecen en el Paso 4; '
         f'todos ({R["ra_con_micro"]}) aparecen en el Paso 5.',
         f'Reserva: hay {R["p4_huerfanos"]} textos en el Paso 4 que no coinciden exactamente con ningún RA del Paso 3 '
         '(posibles variaciones de redacción), por lo que parte de esos casos puede ser un problema de digitación y no de diseño.',
         'Revisar a mano los textos huérfanos antes de calcular A8 (ruta completa).'),
        ('E5', 'Hojas Backup con contenido ajeno',
         f'Las {R["backups"]} hojas "Paso 3 Redacción RA - Backup" contienen RA de otro programa '
         '(p. ej. teoría de circuitos en Administración de Empresas): son plantillas copiadas.',
         'El extractor las excluye correctamente.',
         'Documentar la exclusión en Método; no usar las hojas Backup en ningún análisis.'),
        ('E6', 'Completitud',
         f'{R["nulos"]} celdas vacías en las 8 columnas clave del Paso 3 (competencia, número, tipo de saber, saber asociado, '
         'taxonomía, dominio, nivel, verbo).', 'El Paso 3 está completo.', 'Ninguna.'),
    ]

    ws = wb.create_sheet('EDA_Resumen')
    ws.cell(1, 1, 'Etapa 2 — Análisis exploratorio (EDA) de resultados de aprendizaje').font = Font(bold=True, size=13)
    ws.cell(2, 1, 'Regla de RA único: texto de la columna I del Paso 3, normalizado (minúsculas, sin tildes ni puntuación final), '
                  'deduplicado dentro de cada matriz. Las mismas redacciones en sedes distintas cuentan por separado.').alignment = WRAP
    tabla(ws, ['ID', 'Tema', 'Hallazgo', 'Evidencia / matiz', 'Implicación para el artículo'],
          [list(h) for h in EDA_HALLAZGOS], [6, 26, 70, 55, 55], fila0=4)
    tabla_tipo = [
        ('Saber', ft['Saber'], pct(ft['Saber'], 586), ut['Saber'], pct(ut['Saber'], u_tot)),
        ('SaberHacer', ft['SaberHacer'], pct(ft['SaberHacer'], 586), ut['SaberHacer'], pct(ut['SaberHacer'], u_tot)),
        ('SaberSer', ft['SaberSer'], pct(ft['SaberSer'], 586), ut['SaberSer'], pct(ut['SaberSer'], u_tot)),
        ('Varios tipos', 0, '0,0%', ut['varios_tipos'], pct(ut['varios_tipos'], u_tot)),
        ('Total', 586, '100%', u_tot, '100%'),
    ]
    ws2 = wb.create_sheet('EDA_Tipo_saber')
    tabla(ws2, ['Tipo de saber', 'Filas Paso 3', '% filas', 'RA únicos', '% únicos'], [list(x) for x in tabla_tipo], [16, 14, 10, 12, 10])

    ws = wb.create_sheet('EDA_RA_por_programa')
    k = ['archivo', 'programa', 'sede', 'p3_filas', 'ra_unicos_texto', 'ra_unicos_numero', 'factor_repeticion',
         'filas_Saber', 'filas_SaberHacer', 'filas_SaberSer', 'unicos_Saber', 'unicos_SaberHacer', 'unicos_SaberSer',
         'unicos_varios_tipos', 'nulos_columnas_clave', 'p4_filas_que_citan_ra', 'p5_filas_que_citan_ra',
         'ra_con_meso', 'ra_con_micro', 'ra_con_ambos', 'ra_sin_meso', 'p4_textos_huerfanos']
    h = ['Archivo', 'Programa', 'Sede', 'Filas Paso 3', 'RA únicos (texto)', 'RA únicos (número)', 'Filas por RA',
         'Filas Saber', 'Filas SaberHacer', 'Filas SaberSer', 'Únicos Saber', 'Únicos SaberHacer', 'Únicos SaberSer',
         'Únicos con varios tipos', 'Nulos col. clave', 'Filas Paso 4 que citan RA', 'Filas Paso 5 que citan RA',
         'RA con meso', 'RA con micro', 'RA con ambos', 'RA sin meso', 'Textos Paso 4 sin RA equivalente']
    fl = [[p[x] for x in k] for p in EDA['por_programa']]
    fl.append(['TOTAL', '', ''] + [sum(f[j] for f in fl) if j != 6 else round(586 / u_tot, 2) for j in range(3, len(k))])
    tabla(ws, h, fl, [40, 24, 7] + [11] * (len(k) - 3))
    for c in ws[len(fl) + 1]:
        c.font = Font(bold=True)

    ws = wb.create_sheet('EDA_Inconsistencias')
    tabla(ws, ['Archivo', 'Tipo', 'Detalle', 'Texto(s) del RA'],
          [[i['archivo'], i['tipo'], i['detalle'], i['ra']] for i in EDA['inconsistencias']], [40, 26, 22, 100])

    ws = wb.create_sheet('EDA_RA_sin_ruta')
    tabla(ws, ['Archivo', 'RA', 'Filas Paso 4', 'Filas Paso 5', 'Falta en'],
          [[s['archivo'], s['ra'], s['en_paso4'], s['en_paso5'], s['falta']] for s in EDA['ra_sin_ruta']], [40, 90, 11, 11, 22])

    # --- RA únicos por formato (resumen y detalle), ubicadas junto a A3
    POR_FORMATO = [[i, p['archivo'], p['programa'], p['sede'], p['p3_filas'], p['ra_unicos_texto'],
                    p['p3_filas'] - p['ra_unicos_texto'], p['factor_repeticion'], p['ra_unicos_numero'],
                    'Sí' if p['ra_unicos_numero'] != p['ra_unicos_texto'] else 'No']
                   for i, p in enumerate(EDA['por_programa'], 1)]
    ws = wb.create_sheet('A3_RA_unicos_por_formato', index=wb.sheetnames.index('A4_Ejemplos_Paso4'))
    ws.cell(1, 1, 'RA únicos = textos distintos de la columna I del Paso 3 dentro de cada formato (normalizados: '
                  'minúsculas, sin tildes ni puntuación final). Filas repetidas = copias del mismo RA en otras competencias.').alignment = WRAP
    tabla(ws, ['#', 'Formato (archivo)', 'Programa', 'Sede', 'Filas Paso 3', 'RA únicos', 'Filas repetidas',
               'Filas por RA', 'RA según columna "Número"', '¿Número ≠ texto?'],
          POR_FORMATO + [['', 'TOTAL', '', '', sum(x[4] for x in POR_FORMATO), sum(x[5] for x in POR_FORMATO),
                          sum(x[6] for x in POR_FORMATO), round(586 / u_tot, 2), sum(x[8] for x in POR_FORMATO), '']],
          [5, 42, 26, 7, 12, 11, 12, 11, 14, 12], fila0=3)
    for c in ws[ws.max_row]:
        c.font = Font(bold=True)

    ws = wb.create_sheet('A3_Detalle_RA_unicos', index=wb.sheetnames.index('A4_Ejemplos_Paso4'))
    tabla(ws, ['Formato (archivo)', 'Nº RA en el formato', 'Texto del RA', 'Número(s) asignado(s)', 'Tipo(s) de saber',
               'Filas en Paso 3', 'Filas Excel donde aparece', 'Competencias a las que aporta'],
          [[d['archivo'], d['n'], d['ra'], d['numeros'], d['tipos'], d['filas_p3'], d['filas_excel'], d['competencias']]
           for d in EDA['detalle_ra']], [40, 10, 90, 14, 16, 10, 18, 14])

    ws = wb.create_sheet('EDA_Backups')
    tabla(ws, ['Archivo', 'RA en hoja Backup', 'RA compartidos con hoja principal', 'Diagnóstico'],
          [[b['archivo'], b['ra_en_backup'], b['compartidos_con_hoja_principal'], b['diagnostico']] for b in EDA['backups']],
          [40, 14, 18, 50])

# ---------------------------------------------------------------------------
# CORPUS (Tabla 1) y RESULTADOS (A7-A11)
# ---------------------------------------------------------------------------
try:
    COR = json.load(open('auditoria/evidencia_corpus.json', encoding='utf-8'))
    RES = json.load(open('auditoria/evidencia_resultados.json', encoding='utf-8'))
except FileNotFoundError:
    COR = RES = None

MIC_FULL = json.load(open('auditoria/evidencia_micro.json', encoding='utf-8'))
MIC = MIC_FULL['resumen']
if COR and RES:
    TN = COR['resumen']['tabla_por_nivel']
    ART_T1 = {'Profesional universitario': (34, 169, 439, 1213), 'Tecnología': (5, 20, 50, 171),
              'Técnica profesional': (1, 5, 13, 30), 'Pregrado': (40, 194, 502, 1414),
              'Especialización': (5, 12, 39, 93), 'Maestría': (5, 11, 45, 105),
              'Posgrado': (10, 23, 84, 198), 'Total': (50, 217, 586, 1612)}
    T1 = []
    for nv, (m, c, r, e) in ART_T1.items():
        x = TN[nv]
        T1.append([nv, m, x['matrices'], c, x['competencias'], r, x['ra_filas'], x['ra_unicos'], e,
                   x['meso_filas'], x['meso_estrategias'], x['asignaturas'],
                   'Sí' if (m, c, r, e) == (x['matrices'], x['competencias'], x['ra_filas'], x['meso_filas']) else 'No (competencias)'])
    CR = COR['resumen']
    idem = sum(1 for m in CR['multisede'] if m['ra_identicos'])
    mat_idem = sum(len(m['sedes'].split(', ')) for m in CR['multisede'] if m['ra_identicos'])
    CORPUS = [
        ('C1', '50 matrices curriculares', '50', '50 archivos', '✅ Confirmada', '—', 'Sin cambios.'),
        ('C2', '"de 50 programas"', '50', '39 programas académicos / 50 unidades programa-sede', '❌ No sustentada', 'Redacción (D1)',
         'Con D1 son 39 programas. Escribir "50 matrices curriculares de 39 programas académicos"; además así deja de contradecir la frase "ocho programas se ofrecen en más de una sede".'),
        ('C3', '"tres sedes y tres modalidades"', '3 / 3', f'Modalidades: {CR["modalidades"]}. Ubicaciones: {CR["ciudades"]}. Códigos de sede: 5.', '⚠️ Parcial', 'Redacción',
         'Solo son 3 sedes si la oferta virtual nacional cuenta como sede. Precisar: "dos sedes físicas (Bogotá, Medellín) y oferta virtual nacional, en tres modalidades".'),
        ('C4', '"63% de la oferta institucional"', '63 %', 'Dato institucional confirmado por la autora (2026-10-01); no está en los archivos del corpus', '✅ Confirmada (fuente externa)', '—',
         'Para que sea auditable: citar en nota la fuente (documento o sistema institucional, fecha de corte y nº total de programas en renovación: 50 / N = 63 %) y archivar copia de la fuente en el expediente.'),
        ('C5', '"Ocho programas se ofrecen en más de una sede"', '8', '8 denominaciones con 19 matrices', '✅ Confirmada', '—', 'Sin cambios.'),
        ('C6', '"Paso 1: perfil de egreso"', '—', 'La hoja se llama "Paso1 Analisis perfil egreso"', '⚠️ Parcial', 'Redacción (D2)',
         'Usar "perfil profesional y ocupacional" (decisión D2), indicando que así se denomina el Paso 1.'),
        ('C7', 'Tabla 1 – matrices por nivel', '34/5/1/5/5', '34/5/1/5/5 (licenciaturas incluidas en Profesional universitario)', '✅ Confirmada', '—',
         'Agregar nota: "Profesional universitario incluye 3 licenciaturas".'),
        ('C8', 'Tabla 1 – competencias', '217', f'{TN["Total"]["competencias"]} (col. F del Paso 2 con texto; se excluye el encabezado repetido en la fila 3 de 5 matrices)', '❌ No sustentada', 'Cálculo',
         'No se reproduce 217. La salida recalculo_2026 da 220 porque asigna 0 competencias a EspGerTributaria (tiene 2). Valor correcto: 222. Corregir la Tabla 1 por nivel (ver Corpus_Tabla1).'),
        ('C9', 'Tabla 1 – RA', '586', f'586 filas = {TN["Total"]["ra_unicos"]} RA únicos', '⚠️ Parcial', 'Unidad (D4)',
         'Con D4 la columna debe ser RA únicos (341) o rotularse "registros de RA".'),
        ('C10', 'Tabla 1 – estrategias meso', '1.612', f'1.612 vínculos = {TN["Total"]["meso_estrategias"]} estrategias', '❌ No sustentada', 'Redacción (D5)',
         'La columna cuenta vínculos RA–estrategia; rotular "vínculos RA–estrategia" o reportar 391 estrategias.'),
        ('C11', '1.757 registros de asignatura', '1.757', '1.757', '✅ Confirmada', '—', 'Sin cambios.'),
        ('C12', '709 denominaciones únicas', '709', '709 (minúsculas, sin tildes ni puntuación); 716 texto exacto, 713 minúsculas, 710 sin tildes', '✅ Confirmada', '—',
         'Se reproduce exactamente con normalización (minúsculas, sin tildes ni puntuación). Declarar la regla en nota.'),
        ('C13a', '7.906 menciones de núcleos temáticos', '7.906',
         f'{n(MIC["R3_nucleos"])} núcleos numerados (D7); regla del artículo (corte por coma, ";" y salto de línea): {n(MIC["R1_menciones"])}',
         '❌ No sustentada', 'Método',
         f'Las celdas numeran cada núcleo ({n(MIC["celdas_nucleos"] - MIC["R3_celdas_sin_numeracion"])} de {n(MIC["celdas_nucleos"])} celdas). ' +
         'El 7.906 sale de analisis_tematico_avanzado.py, que corta además por comas: parte núcleos como "Análisis, descripción y diseño de cargos…" '
         'en varios trozos. El propio proyecto (dashboard_tematico.py) documenta que NO debe cortarse por coma. Diferencia residual con 7.951 recalculado: 45 (filas sin tipo de saber).'),
        ('C13b', '3.432 núcleos únicos', '3.432',
         f'{n(MIC["R3_unicos"])} únicos (D7, sin distinguir mayúsculas ni tildes); regla del artículo: {n(MIC["R1_unicos"])} ({n(MIC["R1_unicos_sin_mayusculas"])} sin distinguir mayúsculas)',
         '❌ No sustentada', 'Método',
         'Además del corte por coma, la regla distingue mayúsculas: "Planeación" y "planeación" cuentan como núcleos distintos.'),
        ('C13c', '"de las cuales 5.780 resultaron válidas"', '5.780',
         f'Filtro del proyecto sobre la regla R2: {n(MIC["R2_validos"])} de {n(MIC["R2_tokens"])}. Aplicado a los {n(MIC["R3_nucleos"])} núcleos numerados rechaza {MIC["R3_rechazados_por_filtro_R2"]}',
         '❌ No sustentada', 'Método + redacción',
         '(1) No es un subconjunto de 7.906: viene de otra tokenización. (2) El filtro descarta núcleos legítimos: 563 por empezar con artículo '
         '("La balanza de pagos y el equilibrio general", "El machine learning"), 236 de una palabra ("Planeación", "Organización", "Control"), '
         '55 por terminar en letra ("Política económica parte I"), 42 por parecer encabezado ("Dinámica del mercado", "Metodologías y análisis de datos") '
         'y 30 por longitud. El LDA (n = 5.780) se estimó sin ~14 % del contenido declarado.'),
        ('C13d', '"9,8 núcleos por asignatura" (cuerpo del .md, línea 523)', '9,8',
         f'{str(MIC["R3_densidad_media"]).replace(".", ",")} por asignatura con núcleos (mediana {MIC["R3_densidad_mediana"]:.0f}; máx. {MIC["R3_densidad_max"]})',
         '❌ No sustentada', 'Método',
         'El código agrupa por NOMBRE de asignatura en todo el corpus: "Razonamiento Cuantitativo" suma los núcleos de sus 40 matrices. Debe calcularse por asignatura dentro de cada matriz.'),
        ('C13e', 'Núcleos de programas multisede', '—',
         f'Únicos sumando matrices: {n(MIC["nucleos_unicos_sumando_matrices"])}; sumando programas: {n(MIC["nucleos_unicos_sumando_programas"])}',
         'Hallazgo', 'Independencia',
         'Las sedes de un mismo programa comparten entre 89 % y 100 % de sus núcleos (hoja Multisede): los conteos sobre 50 matrices repiten contenido.'),
        ('C14', '"Se incluyeron todas las matrices que habían completado los cinco pasos"', '—', 'Las 50 matrices tienen datos en Pasos 1–5', '✅ Confirmada', '—', 'Sin cambios.'),
        ('C15', '"las unidades no son plenamente independientes"', '—',
         f'Las {idem} denominaciones multisede tienen RA IDÉNTICOS entre sedes ({mat_idem} matrices); AdmonEmpresas también asignaturas idénticas.',
         '⚠️ Parcial', 'Método (seudorreplicación)',
         'La advertencia es correcta pero insuficiente: en RA y V1–V4 hay 11 matrices que son copias. Las pruebas por sede o nivel (p. ej. p = 0,0001) deben repetirse con una matriz por denominación como análisis de sensibilidad.'),
    ]
    rr = RES['resumen']
    rc = rr['recalculo_2026']
    RESULTADOS = [
        ('R1', 'Resultados: 586 registros de RA y 341 formulaciones únicas', '586 / 341', '586 / 341 (D4)', '✅ Confirmada', '—', '—'),
        ('R2', 'Denominadores declarados: 341 (textual), 586 (tipo de saber), 50 (programa-sede)', '341 / 586 / 50',
         'Coherentes con D1 y D4. Tipo de saber por registros 37,9 / 31,1 / 31,1 % vs por RA únicos 47,8 / 36,1 / 15,8 %. Faltan los denominadores micro (1.757) y meso (391).',
         '⚠️ Parcial', 'Redacción', 'Declarar que la unidad del tipo de saber es el registro (RA × competencia) y añadir 1.757 asignaturas.'),
        ('R3', 'Registro de decisiones de la IAg (aceptada / ajustada / descartada)', '—',
         'No existe en el repositorio ni en los datos (igual que P20); no se analiza en Resultados.',
         '❌ No sustentada', 'Evidencia', 'Mover a Limitaciones o Trabajo futuro sin afirmar que existe, o aportar el registro.'),
        ('R4', 'Tabla 7: corpus por sede', '50 / 217 / 586 / 1.612',
         'Matrices, RA y vínculos meso por sede = auditoría. Competencias: VNAL 93 (no 89), PBOG 75 (no 74); total 222. "Estrategias meso" son vínculos (D5): estrategias declaradas 391 (VNAL 170, PBOG 132, PMED 59, HMED 24, HBOG 6). Por decisión de la autora, la Tabla 7 muestra RA únicos (139/119/52/25/6 = 341) y solo estrategias declaradas (391).',
         '⚠️ Parcial', 'Dato / etiqueta', 'Usar la Tabla 7 corregida (Textos_corregidos, Resultados).'),
        ('R5', 'VNAL y PBOG concentran el 78 % de las matrices; HBOG un único programa', '78 %',
         '39/50 = 78 %; HBOG = Matemáticas. Además, 19 matrices de 8 programas multisede tienen RA idénticos: comparaciones por sede no independientes.',
         '✅ Confirmada', 'Inferencia', 'Añadir la advertencia de no independencia entre sedes.'),
        ('R1.1', 'V1: cada RA se rastrea hasta una competencia', '100 %', '100 % en las 50 matrices (mínimo 100 %); citas del Paso 3 coinciden con competencias del Paso 2.', '✅ Confirmada', '—', '—'),
        ('R1.2', 'V1: … y la competencia hasta el perfil de egreso (Pasos 1–3)', '—', 'La matriz no registra vínculo competencia → perfil; V1 solo mide RA → competencia.', '❌ No sustentada', 'Método', 'Redefinir V1 como correspondencia competencia–RA (D13) y declarar que el tramo al perfil no es verificable.'),
        ('R1.3', 'V1: "perfil de egreso" / "50 programas"', '—', 'D2: perfil profesional y ocupacional. D1: 50 matrices (39 programas).', '❌ No sustentada (redacción)', 'Redacción', 'Corregir denominación y unidad.'),
        ('R1.4', 'V1 propiedad del instrumento, constante, sin tratamiento correlacional (R6)', '—', 'Correcto: constante sin varianza. Verificar en R6 que V1 no entra en correlaciones.', '✅ Confirmada', '—', 'Comprobar al auditar R6.'),
        ('F1', 'Figura 1: radar V1–V5', 'V1 100; V2 ≈ 76; V3 ≈ 98; V4 ≈ 52; V5 ≈ 78 (lectura visual)',
         'V1 correcto. V2 (proyecto 93,1 %; definición 13,8 %), V3 (99,2 %), V4 (≈ 86 %) y V5 (77,8 % por vínculos / 100 % por estrategia) en revisión; sin código que genere la figura.',
         '⚠️ Parcial', 'Cálculo / presentación', 'Quitar V1 del radar (D13) y regenerar la figura con código versionado al cerrar V2–V5.'),
        ('R2.1', 'Analizar: 50 ocurrencias en el 100 % de los programas', '50; 100 %',
         '50 ocurrencias ✅, pero en 42 de 50 matrices (31 de 39 programas = 79,5 %), no en el 100 %.', '❌ No sustentada', 'Cálculo', 'Corregir a "en 31 de los 39 programas".'),
        ('R2.2', 'Dominar 25, Aplicar 21, Implementar 20, Desarrollar 19 (217 competencias)', '25 / 21 / 20 / 19',
         'Sobre 222 competencias: Dominar 26, Aplicar 22, Implementar 20, Desarrollar 19, Diseñar 19. Figura 3: Formular 8 (no 7).', '⚠️ Parcial', 'Dato', 'Actualizar con 222 competencias y regenerar la Figura 3.'),
        ('R2.3', 'Concentración en niveles taxonómicos intermedios; redundancias entre programas afines', '—',
         'Interpretación sin cálculo: "Dominar" e "Implementar" no son verbos de Bloom; repetir "Analizar" entre programas distintos no es redundancia curricular.', '⚠️ Parcial', 'Interpretación', 'Acotar o sustentar con el nivel taxonómico declarado.'),
        ('R2.4', 'Tabla 8: verbos repetidos en 13 programas (26 %); vacíos de tipo de saber 0', '13 (26 %); 0',
         '13 de 50 matrices (26 %) ✅; por programa 9 de 39 (23 %). Vacíos: 0 ✅.', '⚠️ Parcial', 'Unidad', 'Rotular "matrices" (D1) o reportar 9/39 programas.'),
        ('R2.5', 'Distribución de los 586 RA: 37,9 / 31,1 / 31,1 % (Figura 2), próxima a un tercio', '37,9 / 31,1 / 31,1',
         'Cifras correctas sobre 586 registros (RA × competencia), no sobre RA. Por RA únicos (341): Saber 48,1 %, SaberHacer 36,1 %, SaberSer 15,8 %. Cada RA tiene un solo tipo de saber (D4: 341); la aparente paridad se debe a que los RA de SaberSer se reutilizan en 3,4 competencias en promedio (Saber 1,4; SaberHacer 1,5).',
         '⚠️ Parcial', 'Unidad / interpretación', 'Declarar la unidad (registros) y reportar también la distribución por RA únicos.'),
        ('R2.6', 'Rangos por matriz: SaberHacer 28,6–33,3 %; Saber 33,3–42,9 %; ninguna ≥ 35 %', '—', 'Reproducido exactamente (por registros).', '✅ Confirmada', '—', 'Citar la fuente de los rangos de referencia (25–45 / 35–60 / 10–30 %).'),
        ('R2.7', 'Cada competencia se descompone típicamente en un RA de cada tipo de saber', '—',
         '182 de 222 competencias (82 %) tienen exactamente un registro de cada tipo; 40 solo de Saber. El mecanismo es correcto para los registros.', '✅ Confirmada', '—', 'Precisar "182 de 222 competencias".'),
        ('R2.8', 'Tipo de competencia (Paso 2, col. G): específica / genérica', '—',
         '182 específicas y 40 genéricas. Las 40 genéricas son la misma competencia institucional "Analizar fenómenos contemporáneos", una en cada una de 40 matrices; son también las 40 competencias que solo tienen un RA de Saber. Analizar = 40 genéricas + 10 específicas; entre las específicas el verbo más frecuente es Dominar (26).',
         'Hallazgo', 'Interpretación', 'Separar específicas y genéricas al contar verbos y repeticiones.'),
        ('R2.9', 'Repetición de verbos dentro de la matriz considerando el tipo de competencia', '13 (26 %)',
         'Solo 5 matrices (3 programas: Derecho, Ing. Telecomunicaciones, Ing. Sistemas) repiten un verbo entre competencias del mismo tipo (todas específicas). Las otras 8 repiten "Analizar" entre una específica y la genérica institucional, que no es un desajuste del programa.',
         '❌ No sustentada (como desajuste)', 'Método', 'Tabla 8: 5 de 50 matrices (10 %); 3 de 39 programas (7,7 %).'),
        ('R3.1', 'Evaluabilidad media 98,3 %, rango 88,9–100 %, HMED 95,7 %, HBOG 100 % (Tabla 9)', '98,3 %',
         'No hay código de V3. La única salida (recalculo_2026.xlsx) da media 99,2 %, mínimo 70 % (TecnolLogistica_VNAL) y HMED 100 %; ninguna cifra del texto se reproduce. Sus valores (70 %, 90 % con 7 RA únicos) implican denominador en registros, no en RA.',
         '❓ No verificable', 'Trazabilidad del cálculo', 'Definir una regla operativa de V3, versionar el código y recalcular (pendiente de decisión).'),
        ('R3.2', 'Los RA menos evaluables usan verbos como conocer, reflexionar o valorar', '—',
         'En la columna "Verbo RA" de los 341 RA únicos: conocer 0, reflexionar 0, valorar 1. Los verbos más frecuentes son identificar (59), aplicar (48), analizar (47), diseñar (26) y reconocer (26).',
         '❌ No sustentada', 'Dato', 'Retirar los ejemplos o reemplazarlos por los verbos que efectivamente resulten no observables con la regla adoptada.'),
        ('R3.3', 'Un RA es evaluable si usa verbo observable y declara producto o evidencia', '—',
         'Sin regla documentada para "producto o evidencia". Sensibilidad del criterio de verbo: con lista de verbos de estado mental que incluye "reconocer", 92,0 % de RA únicos (media por matriz 92,1 %, mínimo 60 %); sin "reconocer", 99,7 %.',
         '⚠️ Parcial', 'Método', 'Fijar la lista de verbos no observables y la regla de producto; reportar la sensibilidad.'),
        ('R3.4', 'Tabla 9: evaluabilidad por sede (n, media, mediana, desv. típica)', 'HMED 95,7 / 94,7',
         'Los valores son coherentes con un cálculo sobre REGISTROS (RA × competencia), no sobre RA únicos: HMED = Derecho 18/19 (94,7 %), AdmonEmpresas o ContPub 12/13 (92,3 %) y 100 % → media 95,7 %, mediana 94,7 %; el mínimo 88,9 % = 8/9. La regla que marca un RA como no evaluable no se puede reconstruir. Los programas multisede tienen RA idénticos, por lo que sus sedes no son observaciones independientes.',
         '⚠️ Parcial', 'Unidad / trazabilidad', 'Recalcular sobre RA únicos (D4) con regla versionada; mantener la nota de HBOG.'),
        ('R3.5', 'Unidad de V3: registros (cada RA se evalúa distinto en cada matriz)', '586 registros',
         'Entre matrices es cierto y ya lo cubre D4 (únicos por matriz). Dentro de una matriz no: de 146 RA repetidos, 142 tienen idénticos tipo, taxonomía, dominio, nivel y verbo en todos sus registros, y el Paso 4 vincula la evaluación al texto del RA sin indicar competencia (solo 12 de 146 tienen tantos vínculos como registros).',
         '⚠️ Parcial', 'Unidad', 'V3 sobre RA únicos por matriz; registros solo como medida complementaria de carga evaluativa.'),
        ('R3.6', 'V3 recalculado con regla versionada (auditoria/scripts/verificar_v3.py)', '98,3 %',
         'Regla (D15): verbo del RA (col. H) no es de estado mental —en SaberSer se admite el verbo de la taxonomía afectiva— Y declara finalidad de desempeño ("para + infinitivo" observable) o producto concreto. Resultado: 341 de 341 RA únicos (100 %) en las 50 matrices. Sin la excepción actitudinal, 340/341 (99,7 %): solo DisenoModas_PBOG "Valora los requerimientos del usuario…" (SaberSer, BAK actitudinal, nivel Percepción).',
         '✅ Resuelta (valor corregido)', 'Cálculo', 'V3 = 100 %, constante: condición estructural (como V1). Eliminar la Tabla 9 por sede y la "focalización en el 1,7 %".'),
        ('R4.1', 'V4: media 52,3 % (rango 31,6–100 %); sedes 49,1–54,2 %; desv. intra-sede hasta 17,9', '52,3 %',
         'ERROR DE CÁLCULO RECONSTRUIDO: el artículo divide RA ÚNICOS vinculados entre REGISTROS (RA × competencia): reproduce media 51,4 %, HMED 49,1 %, PBOG 54,0 %, HBOG 71,4 %, mínimo 31,6 %. Corregido (D16): 297 de 341 RA = 87,1 % (media por matriz 87,9 %, rango 62,5–100 %); sin el RA genérico, 295/301 = 98,0 %. El RA genérico institucional explica 38 de los 44 RA sin estrategia.',
         '❌ No sustentada', 'Cálculo', 'Reemplazar 52,3 % por 87,1 %; "casi la mitad" por "44 RA, 38 de ellos el RA genérico institucional".'),
        ('R4.5', 'Caso TecProfJudicial_VNAL (33,3 % en el primer recálculo)', '—',
         'Artefacto: (1) la comparación difflib con autojunk subestimaba la similitud de textos largos (0,43 vs 0,84), (2) el Paso 4 conserva la redacción anterior de un RA reformulado en el Paso 3 ("asociados al derecho penal, laboral…" vs "a las diferentes áreas del derecho"), (3) el RA genérico no tiene estrategia. Valor final: 5 de 6 RA (83,3 %); solo falta el RA genérico.',
         'Hallazgo', 'Calidad de datos / cálculo', 'Sincronizar el Paso 4 con el Paso 3 (lista desplegable). Desincronización detectada en 2 matrices (TecProfJudicial y MEDSTEM, VNAL).'),
        ('R4.2', 'V4: ruta Perfil→Competencia→RA→Instrumento', '—',
         'La matriz no registra competencia→perfil (igual que V1) y todas las estrategias declaradas tienen instrumento: V4 con y sin instrumento es igual (87,1 %). En la práctica V4 = RA vinculado a una estrategia meso.', '⚠️ Parcial', 'Método', 'Definir V4 como RA únicos vinculados a una estrategia meso con instrumento.'),
        ('R4.3', '"La variable más alejada del óptimo"; "casi la mitad de los RA carece de estrategia"', '—',
         'Con 87,1 % la brecha (44 RA) se explica casi toda por el RA genérico (38); entre RA de programa son 6 RA en 5 matrices (MercadeoyPublicidad PMED 71,4 %; DisenoGrafico PBOG/PMED y MercadeoyPublicidad PBOG 85,7 %; DisenoIndustrial PBOG 87,5 %).', '❌ No sustentada', 'Interpretación', 'Reescribir la implicación con la brecha real y nombrar las matrices críticas.'),
        ('R4.4', 'Figura 4: diagrama de caja por sede', '—',
         'Inadecuado: HMED (n = 3) y HBOG (n = 1) no admiten caja; oculta el origen de la brecha; usa el 52,3 %. Sustituida (2026-10-03) por la composición de los 44 RA sin estrategia por sede y clase y por matriz (auditoria/scripts/figura_v4.py); las tasas quedan en la Tabla 9, sin duplicar datos.', '⚠️ Parcial', 'Presentación', 'Sustituir por la figura de puntos.'),
        ('R5.1', 'V5: el 77,8 % de las estrategias diligencia al menos un indicador; Tabla 10 por sede', '77,8 %',
         'ERROR DE UNIDAD RECONSTRUIDO: el 77,8 % (y PBOG 81,9; PMED 79,3; VNAL 76,3; HMED 54,6; HBOG 100) es el % de FILAS de RA del Paso 4 con indicador en la misma fila. En el Paso 4 los indicadores ocupan filas propias dentro del bloque combinado de la estrategia, por lo que el valor depende del número de filas, no de la estrategia. Por estrategia: 391 de 391 tienen indicador (100 %).',
         '❌ No sustentada', 'Unidad', 'Reemplazar por la medida por estrategia; ver R5.2.'),
        ('R5.2', 'Predominan indicadores de gestión sobre los de logro (revisión cualitativa)', '—',
         'Con D17 (5 niveles de evidencia): de 1.185 indicadores (170 redacciones), N1 Implementación 808 (68,2 %), N2 Percepción y reacción 371 (31,3 %), N3 Aprendizaje demostrado 5 (0,4 %), N4 Transferencia 0 y N5 Efecto externo 1 (0,1 %). Estrategias con evidencia directa (N3–N4): 3 de 391 (0,8 %), en TecProfJudicial_VNAL (2 de 7) y AdmonPub_VNAL (1 de 6); una estrategia con N5 (TecProfJudicial). La redacción R162 (sustentación ante jurados) quedaba en N1 con la regla anterior: caso para la validación experta.',
         '✅ Confirmada (cuantificada)', '—', 'Reformular como nivel de evidencia del logro; validar las 170 redacciones con doble codificación (kappa).'),
        ('R5.3', 'Figura 5 (mapa de calor por sede) y Figura 6 / Figura 1 (radar V1–V5)', '—',
         'Usan valores no sustentados (V3 98,3; V4 52,3; V5 77,8) e incluyen V1 y V3 constantes; el radar presentaba V5 como fortaleza y V4 como brecha principal, lo contrario de los valores auditados (V4 87,1 %; V5 0,8 %). DECISIÓN DE LA AUTORA: se reemplazan por la Figura 1 "Cadena de evidencia del logro" (auditoria/scripts/figura_cadena.py).',
         '✅ Resuelta (figura sustituida)', 'Presentación', 'Eliminar el radar y el mapa de calor del artículo.'),
        ('R6.1', 'Spearman V3–V4 ρ = 0,329 (p = 0,020) y V3–V5 ρ = 0,317 (p = 0,025)', '0,329 / 0,317',
         'Con valores auditados V3 = 100 % en las 50 matrices (D15): varianza nula, coeficiente no definido. Las dos asociaciones significativas del artículo provienen del cálculo por registros de V3.', '❌ No sustentada', 'Cálculo', 'Eliminar ambas asociaciones y su interpretación.'),
        ('R6.2', 'V4–V5 ρ = −0,017: "desacople" entre trazabilidad (52,3 %) e indicadores (77,8 %)', '−0,017',
         'Recalculado con D16–D17 (n = 50): V4–V5 ρ = −0,134 (p = 0,354); V2–V4 ρ = −0,028 (p = 0,846); V2–V5 ρ = 0,068 (p = 0,639). Con una matriz por programa (n = 39), igual: ninguna significativa. Además V2 es casi binaria (5 matrices en 0 %) y V5 es distinta de 0 solo en 2 matrices: distribuciones degeneradas que no admiten un análisis de asociación informativo. La lectura del "desacople" se apoya en 52,3 % y 77,8 %, ambos no sustentados.',
         '❌ No sustentada', 'Método', 'Sustituir R6 por una declaración breve: V1 y V3 constantes, V2 y V5 degeneradas; no se estiman asociaciones. Retirar Tabla 13 y Figura 7.'),
        ('R7.1', 'Kruskal-Wallis entre sedes: V3, V4 (H = 0,075; p = 0,995) y V5 (ε² = 0,029); Figura 8', 'p > 0,05',
         'Conclusión confirmada con valores auditados, pero cifras y variables obsoletas: V3 es constante (D15). Recalculado (sin HBOG): 49 matrices V2 H = 2,64 p = 0,451; V4 H = 3,53 p = 0,317; V5 H = 2,51 p = 0,474; 38 programas (una matriz por programa) p ≥ 0,182. "49 programas" son 49 matrices no independientes. Figura 8 con valores anteriores y cajas con n = 3.',
         '⚠️ Parcial', 'Cálculo / presentación', 'Usar Tabla 11 recalculada (49 y 38); eliminar Figura 8; Implicación a Discusión.'),
        ('R8.1', '709 denominaciones; 159 (22,4 %) en más de un programa; 6 asignaturas en 28–29 de 39 programas', '709 / 159 / 6',
         '709 y 159 ✅ (D6, D10). Seis asignaturas en 28–29 programas ✅ (Razonamiento Cuantitativo, Cultura Política y Sociedad, Pensamiento Crítico, Análisis y Visualización de Datos, Oportunidades para Emprender: 29; Desarrollo Sostenible: 28).', '✅ Confirmada', '—', '—'),
        ('R8.2', 'Las 159 homónimas concentran 1.078 de 1.757 registros (61,4 %)', '61,4 %',
         'Reconstruido: 1.078 de 1.757 = registros cuya denominación está en más de un programa INCLUYENDO las electivas (168 denominaciones). El artículo mezcla 159 denominaciones (sin electivas) con 1.078 registros (con electivas). Coherente: 159 homónimas = 937 de 1.616 asignaturas (58,0 %).', '⚠️ Parcial', 'Dato', 'Usar 937 de 1.616 (58,0 %) o declarar la base exacta.'),
        ('R8.3', 'Tabla 11: idénticas 27 (17,0 %), alta similitud 86 (54,1 %), divergentes 46 (28,9 %); media 0,697; Proceso Administrativo 0,341', '28,9 %',
         'Con D10 (núcleos + indicadores, solo entre programas distintos): idénticas 133 (83,6 %), alta similitud 11 (6,9 %), divergentes 15 (9,4 %); media 0,928. Proceso Administrativo = 1,000 (7 programas, contenido idéntico); Fundamentos de Redacción 0,370 (divergente ✅). El artículo incluye actividades de evaluación y compara versiones del mismo programa.',
         '❌ No sustentada', 'Método', 'Reemplazar Tabla 11 y ejemplos con D10.'),
        ('R8.4', '344 pares con distinto nombre y similitud ≥ 0,60 (302 homologación, 32 errores de nombre, 10 duplicación por modalidad)', '344',
         'Con D10: 203 pares entre programas distintos (44 asignaturas). Regla versionada (verificar_r8.py): 14 variantes de nombre o error tipográfico (Imvestigación/Investigación Creación; Teoría de/del Diseño; Teorías/Teoría de la Computación) y 189 candidatos a homologación (con falsos positivos léxicos). La duplicación por modalidad (Consultorio Jurídico Virtual) ocurre dentro del mismo programa y queda fuera del contraste entre programas.',
         '⚠️ Parcial', 'Cálculo', 'Recalcular sobre los 203 pares y versionar la regla de clasificación.'),
        ('R8.5', 'LDA sobre 5.780 núcleos, 10 tópicos equilibrados (8,7–10,9 %) (Tabla 13)', '10 tópicos',
         'Sustituido por D11/P14: LDA de consenso, k = 13, 1.192 asignaturas. Distribución de tópicos dominantes no equilibrada: el tópico 1 (mercadeo, comunicación, planeación) es dominante en 27,7 % de las asignaturas; otros entre 2,9 % y 14,8 %; el tópico 11 en ninguna.',
         '❌ No sustentada', 'Método', 'Re-estimar Tabla 13 con el modelo vigente; retirar "distribución equilibrada".'),
        ('R8.6', 'Densidad temática: 4,5 menciones por registro (n = 1.757)', '4,5',
         'Con D7: 6.671 núcleos / 1.616 asignaturas con núcleos = media 4,1 (mediana 4).', '❌ No sustentada', 'Dato', 'Reemplazar por 4,1 (mediana 4).'),
        ('R8.7', 'Tendencias globales: 10 temas, amplitud y profundidad (Figura 9); IA 79,5 % / 3,3 %; ciberseguridad 2 de 39; salud mental 5', 'Figura 9',
         'Los 10 temas de la Figura 9 (Ética profesional, Competencias digitales, Diversidad e inclusión, Salud mental, Ciberseguridad…) provienen de data/output/recalculo_2026.xlsx y NO coinciden con config_tendencias.json, la lista que describe la Etapa 6 (Gestión del cambio, Calidad, Liderazgo, Globalización…; ciberseguridad es término de Transformación digital). Sin código que genere esa lista. Con la lista de config y palabra completa: IA 32/39 programas y 86 de 1.616 asignaturas (5,3 %). Pendiente A11 (base).',
         '❓ No verificable', 'Trazabilidad', 'Definir la lista oficial de temas (una sola) y recalcular la Figura 9 con código versionado.'),
        ('R8.8', 'Cobertura del perfil: 1.466 elementos, 89,4 % cubiertos, 155 (10,6 %) en brecha; Tabla 14 por campo', '10,6 %',
         'Con D3/D9: 988 elementos, 49 alertas (5,0 %). Por campo: Perfil profesional 0/50, Perfil ocupacional 0/50, Saber 5/222 (2,3 %), SaberHacer 14/222 (6,3 %), SaberSer 13/222 (5,9 %), Áreas profesionales 4/57 (7,0 %), Tareas 8/60 (13,3 %), Poblaciones 5/53 (9,4 %), Valor agregado 0/52. El patrón "campos de dónde trabajará concentran las brechas" se mantiene atenuado; los ejemplos (Casinos, Junta Directiva) provienen de la división por frases, descartada (D3).',
         '❌ No sustentada', 'Método', 'Reemplazar Tabla 14 con D9 y revisar los ejemplos con la unidad celda.'),
        ('R8.9', 'Clasificador automático de tipo de saber desactivado por baja concordancia', '—',
         'No hay registro de la evaluación de concordancia en el repositorio.', '❓ No verificable', 'Evidencia', 'Aportar la evidencia o acotar la frase.'),
        ('R8.10', 'Tabla 15 (matriz de valor) y Tabla 16 (resumen V1–V5); síntesis "bien formulado y mal articulado"', '—',
         'Usan 28,9 %, 155 (10,6 %), 52,3 %, 79,5/3,3 %, V2 74 %, V3 98,3 %, V5 77,8 %, todos no sustentados. Con valores auditados (D13–D17) la síntesis se invierte: bien formulado y articulado (V4 87,1 %; 98,0 % RA de programa), pero sin evidencia directa del logro (V5 0,8 %). La Figura 6 (radar) se retiró (R5.3).',
         '❌ No sustentada', 'Interpretación', 'Reescribir Tablas 15–16 y la síntesis con valores auditados.'),
        ('R8.11', 'Lista oficial de temas (config_tendencias.json, confirmada por la autora): términos genéricos', '—',
         'Contribución por término (palabra completa, 1.616 asignaturas): Calidad depende de "procesos" (347 asignaturas, 39 programas; p. ej., "procesos aleatorios", "procesos participativos") y "normas" (33; NIIF); Liderazgo de "comunicacion" (168); Globalización de "global" (98; "escala local y global", "planeación global de la producción"); Ética de "valores" (30; "valores presentes", "valores de probabilidad"); Análisis de datos de "indicadores" (20). Sin esos términos: Calidad 100 → 66,7 % de programas (26,5 → 5,8 % de asignaturas); Liderazgo 89,7 → 51,3 %; Globalización 82,1 → 43,6 %; Ética 79,5 → 53,8 %. Sostenibilidad, IA, Transformación digital e Innovación no cambian.',
         'Hallazgo', 'Método (diccionario)', 'Depurar los términos genéricos de la lista oficial (decisión de la autora) y recalcular la Figura 6.'),
        ('CA.1', 'Aplicativo: clasificación taxonómica de RA (página Bloom & Integración, detectar_taxonomia)', '—',
         'Evaluada contra lo declarado en el Paso 3 (341 RA únicos; auditoria/scripts/evaluar_clasificaciones_app.py): acuerdo de dominio 17,6 % y de subcategoría 4,1 %. Asigna Actitudinal a 330 de 341 RA (declarado: 54). Causa: busca cualquier verbo de la BD (352 verbos) en todo el texto, con coincidencia por raíz, y prioriza la subcategoría de mayor orden, que corresponde al dominio actitudinal (órdenes 11–15). La página sigue ACTIVA en el aplicativo, aunque el artículo (R8.4) afirma que el clasificador se desactivó.',
         '❌ No sustentada', 'Código / redacción', 'Desactivar la inferencia y usar el dominio y nivel declarados en el Paso 3, o corregir el algoritmo (verbo principal del RA = primera palabra; sin prioridad por orden). Ajustar R8.4.'),
        ('CA.2', 'Aplicativo: nivel de formación inferido (_detectar_nivel)', '—',
         'Pregrado/Posgrado inferido de las columnas B./C. del Paso 5: acuerdo 100 % (50/50) con el nivel real.', '✅ Confirmada', '—', '—'),
        ('CA.3', 'Aplicativo: listas de palabras clave', '—',
         'Dos listas paralelas e incoherentes: config.TEMATICAS (src/thematic_detector, reportes por programa) y config_tendencias.json (dashboard). Solo coinciden en Sostenibilidad; TEMATICAS incluye Responsabilidad Social Empresarial y no Calidad. Un mismo tema puede tener cifras distintas según el módulo.',
         '⚠️ Parcial', 'Código', 'Dashboard y análisis temático usan la lista oficial (D21). Decisión de la autora (2026-10-03): mantener config.TEMATICAS en src/thematic_detector y la página Bloom & Integración (CA.1) sin cambios.'),
        ('CA.4', 'Aplicativo: densidad de núcleos en el dashboard (analizar_cobertura)', '—',
         'El filtrado usa tokenizar_nucleo_celda (D7), pero la densidad usa _split_nucleos del dashboard, que corta por salto de línea y agrupa por nombre de asignatura entre programas: no coincide con D7 (4,1 núcleos por asignatura).',
         '⚠️ Parcial', 'Código', 'Calcular la densidad con tokenizar_nucleo_celda y por (programa, asignatura).'),
        ('CA.5', 'Temáticas (lista oficial, palabra completa) frente a tópicos (LDA de consenso k = 13)', '—',
         'Misma base: 1.192 asignaturas (auditoria/scripts/tematicas_vs_topicos.py). Correspondencia fuerte solo en 3 temáticas: IA ↔ tópico 13 (56 % de las asignaturas con IA; lift 15,9; el 76 % del tópico menciona IA), Sostenibilidad ↔ tópicos 7, 10 y 12 (86 %, 79 % y 67 % de cada tópico; tema transversal repartido en tres), Análisis de datos ↔ tópico 9 (probabilidad y estadística; lift 7,3). Liderazgo (68 %), Transformación digital (71 %) y Calidad se concentran en el tópico 1 por términos genéricos (comunicación, digital, procesos), lo que confirma R8.11. Ética, Globalización e Innovación no tienen tópico propio. Cuatro tópicos disciplinares (2 física/lenguaje, 3 derecho público, 5 educación, 8 pensamiento numérico) no contienen ninguna temática.',
         'Hallazgo', 'Método', 'Temáticas y tópicos miden cosas distintas (agenda transversal frente a contenido disciplinar): usar temáticas depuradas para reportes y tópicos solo como exploración; para GreenMetric, la clasificación ODS.'),
        ('CA.6', 'Propuesta: lista integrada de tendencias del sector empresarial y educativo', '—',
         'Integra config.TEMATICAS y config_tendencias.json, depura términos genéricos y agrega tendencias: 32 tendencias (22 empresariales, 10 educativas) en auditoria/propuesta_tendencias_integradas.json. Regla: término en el nombre, o ≥ 2 puntos en el contenido (término compuesto = 2; simple = 1). Cobertura: 1.616 de 1.616 asignaturas (100 %), 1,64 tendencias por asignatura. Riesgo: varios términos se agregaron a partir de asignaturas no cubiertas (sobreajuste) y E04 y D05 tienen menos de 6 asignaturas. Script: auditoria/scripts/tendencias_integradas.py; Excel: auditoria/Tendencias_integradas.xlsx.',
         '✅ Resuelta (D21)', 'Método (diccionario)', 'Adoptada como lista oficial consolidada en 15 tendencias; la autora aprobó la asignación propuesta (2026-10-03).'),
        ('A7', 'Evaluabilidad 98,3 %', '98,3 %', f'Salida existente: {rc["V3_media"]} % (mín. {rc["V3_min"]} %). No hay código.',
         '❓ No verificable', 'Trazabilidad del cálculo',
         'Ningún archivo produce 98,3 %; la única salida da 99,2 %. Además el marco teórico (p68) define evaluabilidad como "instrumento asociado" y los resultados (p166) como "verbo observable + producto". Unificar definición y conservar el script.'),
        ('A8', 'Ruta completa 52,3 %', '52,3 %',
         f'Recalculado: {rr["v4_media_prog_similitud"]} % (media por programa, similitud ≥ 0,80; global {rr["v4_global_similitud"]} %; exacto {rr["v4_global_exacto"]} %). Salida existente: {rc["V4_media"]} %.',
         '❌ No sustentada', 'Cálculo',
         'Dos cálculos independientes dan ~86 %, no 52,3 %. La conclusión "casi la mitad de los RA no tiene ruta" no se sostiene: es ~1 de cada 7. Revisar todos los párrafos que interpretan el 52,3 %.'),
        ('A9', '10,6 % del perfil sin respaldo', '10,6 % (155/1.466)',
         'Con D3 y D9 (celdas de los 9 campos, corpus sin circularidad), código corregido = auditoría: 49/988 = 5,0 %. Por grupo: Perfil 0/100; Saberes 32/666 (4,8 %); Campo de actuación 17/170 (10,0 %); Valor agregado 0/52.',
         '✅ Resuelta (valor corregido)', 'Método', 'Reemplazar por 5,0 % (49/988) y reportar por grupo.'),
        ('A10', '28,9 % de homónimas divergentes', '28,9 % (46/159)',
         'Con D10 (núcleos + indicadores, solo entre programas distintos), código corregido = auditoría: 15/159 = 9,4 %.',
         '✅ Resuelta (valor corregido)', 'Método', 'Reemplazar por 9,4 % (15/159); declarar que el umbral 0,60 no está calibrado.'),
        ('A11a', 'IA en 79,5 % de los programas', '79,5 % (31/39)',
         f'Recalculado (palabra completa, lista estricta, agrupando por denominación): 31/39 = 79,5 %. Por matriz: {rr["ia_prog_estricta"]}/50. Código actual (subcadena): {rr["ia_prog_subcadena"]}/50.',
         '⚠️ Parcial', 'Método (código)',
         'El valor se reproduce con un método correcto, pero el código del repositorio busca subcadenas ("ia" en "sociales", "influencia"…) y marcaría el 100 %. Corregir el código y documentar la lista de términos.'),
        ('A11b', 'IA en 3,3 % de los registros', '3,3 % (60/1.807)',
         f'Recalculado: {rr["ia_reg_estricta"]}/1.757 = {100 * rr["ia_reg_estricta"] / 1757:.1f} % (lista estricta); lista del proyecto {rr["ia_reg_config"]} = {100 * rr["ia_reg_config"] / 1757:.1f} %; subcadena {rr["ia_reg_subcadena"]}.',
         '⚠️ Parcial', 'Denominador', 'El denominador 1.807 incluye las 50 filas de totales; la salida existente dice 3,4 %. Con 1.757 y lista estricta: 3,5 %. La conclusión "amplia pero superficial" se mantiene.'),
    ]

    ws = wb.create_sheet('Corpus_auditoria')
    tabla(ws, ['ID', 'Afirmación', 'Valor artículo', 'Valor recalculado', 'Veredicto', 'Tipo', 'Explicación / corrección'],
          [list(x) for x in CORPUS], [6, 34, 14, 50, 16, 20, 80])
    ws = wb.create_sheet('Corpus_Tabla1')
    tabla(ws, ['Nivel', 'Matrices (art.)', 'Matrices (rec.)', 'Competencias (art.)', 'Competencias (rec.)', 'RA filas (art.)',
               'RA filas (rec.)', 'RA únicos (rec.)', 'Meso (art.)', 'Meso vínculos (rec.)', 'Estrategias declaradas (rec.)',
               'Asignaturas (rec.)', '¿Coincide?'], T1, [24, 10, 10, 12, 12, 10, 10, 10, 10, 12, 14, 12, 16])
    ws = wb.create_sheet('Corpus_por_matriz')
    km = ['archivo', 'nivel', 'sede', 'competencias', 'ra_filas', 'ra_unicos', 'meso_filas', 'meso_estrategias', 'asignaturas',
          'celdas_nucleos', 'nucleos_menciones']
    tabla(ws, km, [[x[k] for k in km] for x in COR['por_matriz']], [42, 24, 7] + [12] * 8)
    ws = wb.create_sheet('Corpus_multisede')
    tabla(ws, ['Programa', 'Sedes', '¿RA idénticos?', '¿Asignaturas idénticas?'],
          [[m['programa'], m['sedes'], 'Sí' if m['ra_identicos'] else 'No', 'Sí' if m['asignaturas_identicas'] else 'No']
           for m in CR['multisede']], [24, 22, 14, 18])
    # --- Revisión de competencias
    import pandas as _pd
    _rc = _pd.read_excel('data/output/recalculo_2026.xlsx', 'Variables_V1_V5')
    _rc_map = {(r.prog, r.sede): int(r.n_comp) for r in _rc.itertuples()}
    filas_c = []
    for x in COR['por_matriz']:
        rcv = _rc_map.get((x['programa'], x['sede']))
        filas_c.append([x['archivo'], x['programa'], x['sede'], x['nivel'], x['competencias'], rcv,
                        x['competencias'] - (rcv or 0),
                        'Coincide' if rcv == x['competencias'] else 'Revisar en Competencias_detalle'])
    filas_c.append(['TOTAL', '', '', '', sum(f[4] for f in filas_c), sum(f[5] or 0 for f in filas_c),
                    sum(f[6] for f in filas_c), 'Artículo: 217'])
    ws = wb.create_sheet('Competencias_por_matriz')
    ws.cell(1, 1, 'Regla: filas del Paso 2 desde la fila 3 con texto en la columna F, excluyendo instrucciones "[…]" y el encabezado repetido. '
                  'El artículo solo reporta totales por nivel (ver Competencias_por_nivel).').alignment = WRAP
    tabla(ws, ['Archivo', 'Programa', 'Sede', 'Nivel', 'Competencias (auditoría)', 'Competencias (recalculo_2026)',
               'Diferencia', 'Estado'], filas_c, [42, 26, 7, 24, 14, 16, 11, 30], fila0=3)
    for c in ws[ws.max_row]:
        c.font = Font(bold=True)

    ART_C = {'Profesional universitario': 169, 'Tecnología': 20, 'Técnica profesional': 5, 'Pregrado': 194,
             'Especialización': 12, 'Maestría': 11, 'Posgrado': 23, 'Total': 217}
    _rcn = {}
    for x in COR['por_matriz']:
        _rcn[x['nivel']] = _rcn.get(x['nivel'], 0) + (_rc_map.get((x['programa'], x['sede'])) or 0)
    _rcn['Pregrado'] = sum(_rcn.get(k, 0) for k in ['Profesional universitario', 'Tecnología', 'Técnica profesional'])
    _rcn['Posgrado'] = _rcn.get('Especialización', 0) + _rcn.get('Maestría', 0)
    _rcn['Total'] = _rcn['Pregrado'] + _rcn['Posgrado']
    ws = wb.create_sheet('Competencias_por_nivel')
    tabla(ws, ['Nivel', 'Matrices', 'Artículo', 'recalculo_2026', 'Auditoría', 'Diferencia (auditoría − artículo)', '¿Coincide?'],
          [[nv, TN[nv]['matrices'], a, _rcn.get(nv), TN[nv]['competencias'], TN[nv]['competencias'] - a,
            'Sí' if TN[nv]['competencias'] == a else 'No'] for nv, a in ART_C.items()], [24, 10, 10, 14, 11, 16, 11])
    for i in range(2, ws.max_row + 1):
        if ws.cell(i, 7).value == 'No':
            ws.cell(i, 7).fill = PatternFill('solid', fgColor='FFC7CE')

    ws = wb.create_sheet('Competencias_detalle')
    det = COR.get('competencias_detalle', [])
    tabla(ws, ['Archivo', 'Nivel', 'Fila Excel', 'Col. A (No.)', 'Col. F (redacción de la competencia)', 'Tipo', '¿Se cuenta?'],
          [[d['archivo'], d['nivel'], d['fila_excel'], d['col_A_numero'], d['col_F_competencia'], d['tipo'], d['cuenta']] for d in det],
          [40, 22, 9, 10, 90, 18, 34])
    for i in range(2, ws.max_row + 1):
        if str(ws.cell(i, 7).value).startswith('No'):
            ws.cell(i, 7).fill = PatternFill('solid', fgColor='FFEB9C')

    ws = wb.create_sheet('Resultados_A7_A11')
    tabla(ws, ['ID', 'Afirmación', 'Valor artículo', 'Valor recalculado / evidencia', 'Veredicto', 'Tipo de error', 'Explicación / corrección'],
          [list(x) for x in RESULTADOS], [7, 28, 16, 70, 16, 20, 80])
    ws = wb.create_sheet('Resultados_por_programa')
    kr = ['archivo', 'ra_unicos', 'ra_en_p4_exacto', 'ra_en_p4_similitud', 'v4_exacto', 'v4_similitud', 'asignaturas',
          'ia_estricta', 'ia_config', 'ia_subcadena']
    tabla(ws, kr, [[x[k] for k in kr] for x in RES['por_programa']], [42] + [12] * 9)
    ws = wb.create_sheet('IA_asignaturas')
    tabla(ws, ['Archivo', 'Asignatura', 'Término IA detectado'],
          [[a['archivo'], a['asignatura'], a['termino']] for a in RES['ia_asignaturas']], [42, 50, 24])
    ws = wb.create_sheet('IA_falsos_positivos')
    tabla(ws, ['Archivo', 'Asignatura', 'Palabra clave', 'Contexto (el código la cuenta como IA)'],
          [[e['archivo'], e['asignatura'], e['keyword'], e['contexto']] for e in RES['falsos_positivos_subcadena']], [40, 34, 12, 70])

VAR_FULL = json.load(open('auditoria/evidencia_variables.json', encoding='utf-8'))
VR = VAR_FULL['resumen']
VARIABLES = [
    ('V0', 'Sección Variables', '"cinco variables calculables uniformemente en las 50 matrices"', '—',
     'No existe código de V1–V5 en el repositorio; solo las salidas recalculo_2026.xlsx y data/processed/variables_recalculadas.csv (10-ago).',
     '❓ No verificable', 'Reproducibilidad', 'Versionar el script que calcula V1–V5; sin él, la Tabla 2 no puede auditarse más allá de reconstruir sus fórmulas.'),
    ('V1', 'Tabla 2', 'V1: proporción de RA con competencia de referencia trazable hasta el perfil', f'{VR["V1_proyecto"]} % (todas las matrices)',
     f'{VR["V1_aud"]} % en las 50 matrices (mínimo {VR["V1_min_aud"]} %)', '⚠️ Parcial', 'Método',
     'La matriz no registra el vínculo competencia→perfil: V1 solo verifica RA→competencia. Además es constante (100 % en todas las matrices): '
     'no discrimina y no puede entrar en correlaciones ni pruebas de diferencias. Redactar "proporción de RA asociados a una competencia declarada" y presentarla como condición verificada, no como variable.'),
    ('V2', 'Tabla 2', 'V2: proporción de competencias cuyo verbo rector se repite', f'{VR["V2_proyecto"]} % (media del proyecto)',
     f'Según la definición: {str(VR["V2_def_articulo"]).replace(".", ",")} % de competencias con verbo repetido. Complemento: {str(VR["V2_complemento"]).replace(".", ",")} %',
     '❌ No sustentada', 'Método',
     'El proyecto calcula 1 − (verbos distintos repetidos / competencias): (1) mide lo contrario de la definición (ausencia de repetición) y '
     '(2) cuenta verbos, no competencias. Ej.: AdmonEmpresas, 5 competencias, 2 comparten verbo → definición 40 %; proyecto 80 %. '
     f'El indicador binario de vacíos en tipos de saber vale 0 en las 50 matrices ({VR["matrices_con_vacio_tipo_saber"]} con vacíos): es constante.'),
    ('V3', 'Tabla 2', 'V3: proporción de RA con verbo observable y producto o evidencia declarada', f'{VR["V3_proyecto"]} %',
     f'Valor del proyecto {VR["V3_proyecto"]} %; {VR["V3_matrices_bajo_100"]} matrices bajo 100 %. No hay regla documentada para detectar "producto o evidencia"',
     '❓ No verificable', 'Reproducibilidad',
     'Documentar el catálogo de verbos observables y el criterio de "producto o evidencia". Prácticamente constante (48 de 50 matrices = 100 %). '
     'La definición del marco teórico (p68: "instrumento asociado") difiere de esta.'),
    ('V4', 'Tabla 2', 'V4: proporción de RA con ruta completa perfil → competencia → RA → instrumento', f'{VR["V4_proyecto"]} % (artículo vigente: 52,3 %)',
     f'{str(VR["V4_con_instrumento"]).replace(".", ",")} % exigiendo instrumento (= {str(VR["V4_sin_instrumento"]).replace(".", ",")} % sin exigirlo)',
     '⚠️ Parcial', 'Método / redacción',
     'Todas las estrategias declaran instrumento, por lo que la condición "instrumento" no discrimina; el tramo perfil→competencia no está en la matriz. '
     'V4 mide en la práctica "RA vinculado a una estrategia meso". La categoría de origen "B1. Cobertura de perfil" no corresponde: es trazabilidad RA→evaluación.'),
    ('V5', 'Tabla 2', 'V5: proporción de estrategias mesocurriculares con al menos un indicador', f'{VR["V5_proyecto"]} %',
     f'Por estrategia (definición): {str(VR["V5_por_estrategia"]).replace(".", ",")} %. Por fila RA–estrategia (lo que calcula el proyecto): {str(VR["V5_por_fila"]).replace(".", ",")} %',
     '❌ No sustentada', 'Método',
     'El denominador del proyecto son las 1.612 filas RA–estrategia (n_meso), no las 391 estrategias (D5). Con la definición del artículo V5 = 100 % en las 50 matrices: '
     'toda estrategia declara indicador. El 77,8 % mide filas sin indicador dentro de bloques que sí lo tienen.'),
    ('V6', 'Categoría B2', '"El desempeño del aplicativo se contrastó con la revisión experta… contraste que orientó la fijación de umbrales"', '—',
     'NOTAS_REVISION_v2.md (pendientes 9 y 10): el umbral 0,60 "conviene calibrarlo con una muestra validada por pares" y las brechas de perfil deben "revisarse manualmente antes de reportarlas"',
     '❓ No verificable', 'Redacción / evidencia',
     'No hay en el repositorio registros de la revisión experta (muestra, revisores, acuerdo). Las notas del proyecto la describen como pendiente. '
     'Aportar la evidencia o reformular como "se recomienda".'),
    ('V7', 'Categoría B2', '"tasa de rechazo del filtrado de núcleos" como criterio de calibración', '—',
     f'El filtro rechaza {MIC["R3_rechazados_por_filtro_R2"]} de {n(MIC["R3_nucleos"])} núcleos numerados (14 %), en su mayoría legítimos (C13c)',
     '⚠️ Parcial', 'Método', 'Reportar la tasa es correcto como auditoría del pipeline, pero muestra que el filtro está mal calibrado; con D7 no se aplica.'),
    ('V8', 'Categoría A', '"componentes generados con apoyo de la IAg"', '—', 'Las matrices no registran qué componentes se generaron con IAg',
     '❓ No verificable', 'Evidencia', 'Indicar cómo se documentó el uso de IAg (registro de prompts, versiones) o acotar la afirmación.'),
]

TAX = json.load(open('auditoria/evidencia_taxonomias.json', encoding='utf-8'))
_tf, _tu, _tm = TAX['filas'], TAX['unicos'], TAX['matrices']
_pf = lambda a, b: f'{100 * a / b:.1f}'.replace('.', ',')
PROCEDIMIENTO = [
    ('P1', 'Etapa 1', 'Códigos de sede/modalidad (PBOG, VNAL, HMED, PMED, HBOG)', '—', 'Coinciden con los 50 nombres de archivo', '✅ Confirmada', '—', 'Sin cambios.'),
    ('P2', 'Etapa 1', '"el sistema localiza los encabezados por aproximación, sin corrección manual"', '—',
     'ANTES: filas de encabezado fijas y nombres exactos (perdía 6 campos del perfil en 24 matrices; leía instrucciones como encabezado en Paso 2 y Paso 4). '
     'CORREGIDO 2026-10-02 en src/extractor.py y config.py: detección de la fila de encabezado, normalización de nombres y sinónimos (COLUMN_ALIASES), descarte de filas de instrucciones y encabezados repetidos. '
     'Control antes → después: campos de perfil 306 → 450; competencias reconocidas 15 → 222; columna "Estrategia del programa" 0 → 50 matrices; encabezado leído como dato en Paso 4 50 → 0; Paso 3 (586) y Paso 5 sin cambios. pytest: 83 aprobadas, 0 fallidas.',
     '✅ Resuelta (código corregido)', 'Método',
     'El texto queda verdadero. Evidencia: auditoria/control_extractor_antes.json y _despues.json. Las cifras auditadas no cambian.'),
    ('P3', 'Tabla 3', 'Columnas clave por hoja', '—',
     'Paso 1 omite Áreas, Tareas y Poblaciones (usadas en cobertura); Paso 4 omite "Instrumentos de medición" (requerido por V4); Paso 1 se rotula "Perfil de egreso"',
     '⚠️ Parcial', 'Redacción', 'Completar las columnas usadas por el análisis y aplicar D2.'),
    ('P4', 'Etapa 2', '"Siete filtros sucesivos"', '7', '7 condiciones en src/nucleos_cleaner.py:es_nucleo_valido', '✅ Confirmada', '—', 'Sin cambios.'),
    ('P5', 'Etapa 2', '"de 7.906 menciones, 5.780 superaron los filtros y 2.126 (26,9 %) se descartaron"', '26,9 %',
     'ANTES: 7.906 (corte por coma, analisis_tematico_avanzado.py) y 5.780 (otra tokenización + 7 filtros que rechazaban núcleos legítimos) mezclados. '
     'CORREGIDO 2026-10-02 (opción A, D7): src/nucleos_cleaner.py separa por numeración y aplica solo un control mínimo (vacío, solo números, instrucciones "[…]"); '
     'filtros heurísticos desactivados (config NUCLEOS_CONFIG["FILTROS_ESTRICTOS"] = False). analisis_tematico_avanzado.py usa la misma separación; '
     'la densidad se calcula por asignatura dentro de cada matriz y los únicos sin distinguir mayúsculas. '
     'Control antes → después: ítems 6.714 → 6.671; válidos 5.777 → 6.671; rechazados 937 → 0; únicos 2.429 → 2.815. pytest: 83 aprobadas.',
     '✅ Resuelta (código corregido)', 'Cálculo / método',
     'Reescribir la Etapa 2: 6.671 núcleos (2.815 únicos) en 1.616 asignaturas; el control de calidad no identificó entradas inválidas. '
     'Residual: analisis_tematico_avanzado.py descarta 378 filas sin "Tipo de Saber" y obtiene 6.631. Evidencia: auditoria/control_nucleos_antes.json y _despues.json.'),
    ('P6', 'Etapa 2', 'Puntaje orientativo y detector de atípicos (Isolation Forest; Liu et al., 2008)', '—',
     'Ambos implementados; el umbral del puntaje está inactivo (no decide)', '✅ Confirmada', '—', 'Sin cambios.'),
    ('P7', 'Etapa 3', 'Puntaje de calidad: completitud 25 %, exigencia 20 %, equilibrio, cobertura y variedad 15 % c/u', '90 % declarado',
     'ANTES: sexto componente "calidad_redaccion" = constante 80 (10 %); exigencia por verbo, no por nivel declarado; completitud sobre todas las columnas y filas; '
     'equilibrio por filas; cobertura sin emparejar (hasta 140 %); el resumen del reporte rotulaba asignaturas como "RA". '
     'CORREGIDO 2026-10-02 (E3-1 a E3-7) en src/analyzer.py, config.py, src/report_generator.py y dashboard/app.py: exigencia por nivel declarado en escala común 1–6 '
     '(PROGRESIONES_TAXONOMICAS); completitud y cobertura recalculadas con unidades D4–D6 resultan 100 % en los 50 programas y pasan a condiciones verificadas (no puntúan); '
     'puntaje = exigencia 40 % + equilibrio 30 % + variedad 30 % (pesos declarados 20/15/15 reescalados). '
     'Control antes → después: puntaje 46,8–87,0 (media 67,7) → 17,4–71,6 (media 44,7); exigencia media 41,3 → 51,4. pytest 83 aprobadas.',
     '✅ Resuelta (código corregido)', 'Método',
     'Reescribir la Etapa 3 con tres componentes ponderados y dos condiciones verificadas. Evidencia: auditoria/control_score_antes.json y _despues.json; comparar_exigencia.py.'),
    ('P8', 'Etapa 3 / Tabla 4', '"Bloom 44,1 % / BAK 55,9 %" y niveles de la Tabla 4', '44,1 / 55,9',
     f'Por filas: Bloom {_pf(_tf["Bloom"], 586)} % / BAK {_pf(_tf["BAK"], 586)} %. Por RA únicos (D4): Bloom {_pf(_tu["Bloom"], 341)} % / BAK {_pf(_tu["BAK"], 341)} %. '
     f'Por matriz: {_tm.get("BAK + Bloom", 0)} usan ambas, {_tm.get("Bloom", 0)} solo Bloom, {_tm.get("BAK", 0)} solo BAK.',
     '✅ Resuelta (texto corregido)', 'Redacción',
     'Texto y Tabla 4 corregidos (E3-6): porcentajes por RA únicos, mezcla de taxonomías dentro de las matrices, niveles BAK "Evaluación" y "Caracterizar", y escala común 1–6 declarada.'),
    ('P9', 'Etapa 4', '"Cada elemento del perfil se compara… métrica híbrida TF-IDF y BM25… alerta si su máxima similitud no alcanza el umbral"', '—',
     'El código no usa la máxima similitud: score = 0,6 × coseno TF-IDF ponderado de los 3 mejores documentos (0,5/0,3/0,2) + 0,4 × BM25 máximo suavizado (s/(s+2)). '
     'Lematización spaCy y BM25 se omiten en silencio si no están instalados (en este entorno sí lo están).',
     '⚠️ Parcial', 'Redacción / reproducibilidad', 'Describir la métrica real y registrar en el log las dependencias activas.'),
    ('P9b', 'Etapa 4', 'Corpus de comparación ("contenidos del programa")', '—',
     'ANTES: el corpus incluía "SaberAsociado" (Paso 3) y el texto de los RA, redactados a partir del perfil (98,6 % de las celdas de Saber idénticas a un SaberAsociado). '
     'CORREGIDO 2026-10-02 en src/perfil_coverage_analyzer.py: corpus = nombre, indicadores de logro, núcleos temáticos y actividades de evaluación de las asignaturas; '
     'columnas reconocidas por nombre normalizado (también corrige la lectura del dashboard desplegado, que perdía campos con encabezado variante).',
     '✅ Resuelta (código corregido)', 'Método (circularidad)', 'Sin fuentes derivadas del perfil, las alertas en Saber / SaberHacer / SaberSer pasan de 0 % a 2,3 / 6,3 / 5,9 %.'),
    ('P9c', 'Etapa 4', 'Unidad "elemento del perfil" y resultado (10,6 %, 155/1.466)', '10,6 %',
     'CORREGIDO (D9): una celda de los 9 campos del Paso 1 = un elemento (988), sin dividir el texto. Control antes → después: elementos 2.562 → 988; alertas 323 (12,6 %) → 49 (5,0 %); '
     'documentos del corpus 13.177 → 6.610. Por campo: Perfil profesional 0/50, Perfil ocupacional 0/50, Saber 5/222 (2,3 %), SaberHacer 14/222 (6,3 %), SaberSer 13/222 (5,9 %), '
     'Áreas 4/57 (7,0 %), Tareas 8/60 (13,3 %), Poblaciones 5/53 (9,4 %), Valor agregado 0/52. Por grupo (opción 1, solo agregación): Perfil 0/100 (0 %), Saberes 32/666 (4,8 %), Campo de actuación 17/170 (10,0 %), Valor agregado 0/52 (0 %). Lectura del dashboard: 988 / 48 (incluye filas de totales del Paso 5). pytest 83 aprobadas.',
     '✅ Resuelta (código corregido)', 'Método',
     'Reemplazar 10,6 % (155/1.466) por 5,0 % (49/988) en el resumen (A9) y en la sección de cobertura. Evidencia: auditoria/control_cobertura_antes.json y _despues.json.'),
    ('P10', 'Tabla 5', 'Umbrales por campo (0,28–0,38)', '—', 'Coinciden con config.UMBRALES_POR_CAMPO', '✅ Confirmada', '—', 'Sin cambios.'),
    ('P11', 'Etapa 4', '"umbrales… se fijaron empíricamente contra la revisión experta (P6)"', '—',
     'NOTAS_REVISION_v2.md (pend. 9–10): calibración con pares pendiente; no hay registros de la revisión', '❓ No verificable', 'Evidencia',
     'Aportar la muestra, los revisores y el acuerdo, o reformular.'),
    ('P12', 'Etapa 5', '"compara las asignaturas de todos los programas por coincidencia de nombre y por similitud de contenidos"', '—',
     'ANTES: comparación por contenido sobre una muestra aleatoria (máx. 500 de 1.616 asignaturas); fila por fila (sin consolidar el bloque de cada asignatura); '
     'la tabla de homónimas venía de un script ausente. CORREGIDO 2026-10-02 en src/shared_subjects_analyzer.py: consolidar_asignaturas (una fila por asignatura de cada matriz, '
     'sin electivas ni totales); comparación de las 1.616 asignaturas sin muestreo, solo entre programas distintos, con marca de mismo nombre; nueva función divergencia_homonimas. '
     'Control antes → después: pares inter-programa 454 (muestra) → 6.268 (todas); pares con nombre distinto y contenido similar: 203; homónimas 179 (texto exacto, con electivas) → 159.',
     '✅ Resuelta (código corregido)', 'Método / reproducibilidad', 'Evidencia: auditoria/control_asignaturas_antes.json y _despues.json. pytest 83 aprobadas.'),
    ('P12b', 'Etapa 5 / A10', 'Divergencia de homónimas: 28,9 % (46/159, sim < 0,60)', '28,9 %',
     'CORREGIDO (D10): contenido = núcleos temáticos + indicadores de logro (sin texto de RA); similitud media solo entre versiones de programas distintos. '
     'Resultado del pipeline = auditoría independiente: 15 de 159 homónimas divergentes (9,4 %). Umbral 0,60 mantenido, sin calibración documentada.',
     '✅ Resuelta (código corregido)', 'Método',
     'Reemplazar 28,9 % (46/159) por 9,4 % (15/159) en el resumen y en la sección de asignaturas compartidas; declarar que el umbral no está calibrado.'),
    ('P13', 'Etapa 6', '"LDA… se aplica sobre los temas depurados en la Etapa 2"', '—',
     'CORREGIDO: src/topic_modeler.corpus_nucleos construye el corpus con los 6.671 núcleos (D7) y run_analysis.py entrena el LDA sobre ellos '
     '(6.659 documentos tras descartar textos de ≤ 5 caracteres). Antes: SaberAsociado del Paso 3 (586 filas, 399 textos distintos). '
     'Estabilidad: entre 4 semillas, coincidencia media de las palabras principales 22 % (0 de 30 tópicos ≥ 50 %).',
     '✅ Resuelta (código corregido)', 'Método', 'Evidencia: auditoria/evidencia_etapa6.json y evidencia_lda_nucleos.json. Re-estimar la Tabla 16 con estos tópicos.'),
    ('P14', 'Etapa 6', 'k = 10 como compromiso entre interpretabilidad y granularidad', '10',
     'Calibración: con núcleos sueltos UMass no tiene óptimo (sube hasta k = 30) y la coincidencia entre semillas es 21–32 %. Con el corpus por asignatura (1.192, una matriz por programa, lemas) '
     'el óptimo es k = 13 en NPMI, UMass y estabilidad. CORREGIDO: src/topic_modeler.modelar_topicos_consenso = LDA de consenso (10 semillas, 500 iteraciones, alfa 0,1, beta 0,01, 600 términos, '
     'tópicos agrupados por coseno y promediados), k = 13. Control con el código: coincidencia entre dos consensos con semillas distintas 59,2 % (8/13 tópicos ≥ 50 %); antes 21,5 % (0/10).',
     '✅ Resuelta (código corregido)', 'Método', 'Evidencia: control_topicos_despues.json, evidencia_estabilidad_lda.json, evidencia_lda_mejorado.json. Re-estimar la Tabla 16.'),
    ('P15', 'Etapa 6', 'Presencia de diez temas de agenda global con lista ajustable', '—',
     'CORREGIDO: analisis_tematico_avanzado.py y dashboard_tematico.py buscan cada término como palabra completa y sin tildes (antes por subcadena: IA 1.473 → 86 asignaturas). '
     '"Ciberseguridad" no es un tema: es un término de Transformación digital.',
     '✅ Resuelta (código corregido)', 'Método / redacción', 'Sustituir "ciberseguridad" por "transformación digital" en el texto; recalcular la Tabla 17.'),
    ('P14b', 'Etapa 6', 'Estabilidad de los tópicos (prueba de mejoras)', '—',
     'Corpus actual (6.659 núcleos): coincidencia entre semillas 21–32 % según k; UMass sin óptimo hasta k = 30. Corpus mejorado (asignatura como documento, 39 matrices, lemas, '
     'palabras vacías en inglés; 1.192 documentos): óptimo k = 13 en NPMI (0,181), UMass y estabilidad (42 %). Variantes de LDA ≤ 43 %; LDA de consenso 59 % (62 % de tópicos estables, NPMI 0,32); NMF 74–100 % y NPMI ≈ 0,40.',
     '✅ Resuelta (ver P14)', 'Método', 'Evidencia: evidencia_k_lda*.json, evidencia_lda_mejorado.json, evidencia_estabilidad_lda.json, estabilidad_lda.py; docs/lda_calibracion*.csv.'),
    ('P16', 'Etapa 7', '"Por cada programa se generan un archivo consolidado y un informe navegable"', '—',
     'Por matriz se generan HTML + JSON (run_analysis.py:111-114) con nombre sin sede: los multisede se sobrescriben (50 → 39). El consolidado (indicadores_consolidados.xlsx, excel_maestro.xlsx) es único para el corpus, no por programa.',
     '⚠️ Parcial', 'Código / redacción', 'Nombrar reporte_<Programa>_<Sede>; redactar "por matriz… y un consolidado del corpus".'),
    ('P22', 'Etapa 7', 'CurriculoPoli filtra por sede, nivel y programa', '—',
     'dashboard_tematico.py:5093-5113 filtra por programa, modalidad, sede y nivel. El nombre "CurriculoPoli" no aparece en el código.',
     '✅ Confirmada (con matiz)', 'Redacción', 'Añadir modalidad; confirmar el nombre del aplicativo.'),
    ('P17', 'Tabla 6', 'Python 3.10 y bibliotecas', '3.10', 'Dockerfile: python:3.10-slim; entorno local 3.12.7; auditoría 3.14. requirements.txt solo con mínimos (">=").',
     '⚠️ Parcial', 'Reproducibilidad', 'Declarar el entorno de la corrida final y fijar versiones exactas (pip freeze).'),
    ('P21', 'Tabla 6', 'scikit-learn: TF-IDF, LDA, Isolation Forest', '—',
     'TF-IDF y LDA en uso; Isolation Forest solo en src/nucleos_cleaner.detectar_anomalias_nucleos, que ningún script ni el dashboard invoca. rank-bm25, spaCy, scipy.stats, plotly y streamlit sí se usan.',
     '❌ No sustentada (Isolation Forest)', 'Redacción', 'Quitar Isolation Forest de la Tabla 6 o integrarlo al proceso.'),
    ('P18', 'Tabla 6', 'IA generativa "solo diseño y construcción"', '—',
     'Integración con Claude presente pero desactivada (LLM_ENABLED = False); modelo inconsistente: config.py claude-3-5-sonnet-20241022 vs llm_integration.py claude-sonnet-4-6.',
     '✅ Confirmada (con matiz)', 'Redacción', 'Mencionar que el módulo existe y estuvo desactivado.'),
    ('P19', 'Cierre', '"El código, versiones, semillas, parámetros… están documentados"', '—',
     'Semilla 42 y parámetros en config.py y config_tendencias.json. Ya versionados: divergencia de asignaturas y LDA sobre núcleos. Faltan: código de V3, fuente de las Tablas 16–17 originales, versiones exactas; umbrales sin justificar (0,60; umbrales del perfil).',
     '⚠️ Parcial', 'Reproducibilidad', 'Completar el repositorio o acotar la afirmación.'),
    ('P20', 'Cierre', '"la estructuración generativa de las matrices es trazable mediante el registro de entradas, salidas y decisiones humanas"', '—',
     'No hay registro de la estructuración de las matrices en el repositorio ni en docs/; solo instrucciones de redacción del artículo (PROMPT_MEJORADO_ARTICULO.md).', '❌ No sustentada', 'Evidencia',
     'Adjuntar el registro o eliminar la frase.'),
]

import sys as _sys
_sys.path.insert(0, 'auditoria/scripts')
from generar_excel import build as _build_excel
from definiciones import definiciones as _defs, md as _defs_md
DEFINICIONES = _defs(T, MIC, TN)
open('auditoria/DEFINICIONES.md', 'w', encoding='utf-8').write(_defs_md(DEFINICIONES, EV['fecha']))
HOJAS = _build_excel(globals())  # Excel depurado; las hojas de trabajo anteriores no se guardan

# ---------------------------------------------------------------------------
# WORD
# ---------------------------------------------------------------------------
def sombrear(cell, hexcolor):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:fill'), hexcolor)
    tcPr.append(shd)


def tabla_doc(doc, cab, filas, anchos=None):
    t = doc.add_table(rows=1, cols=len(cab))
    t.style = 'Table Grid'
    for j, c in enumerate(cab):
        cell = t.rows[0].cells[j]
        cell.text = ''
        r = cell.paragraphs[0].add_run(c)
        r.bold = True
        r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        r.font.size = Pt(9)
        sombrear(cell, '1F3864')
    for fila in filas:
        cells = t.add_row().cells
        for j, v in enumerate(fila):
            cells[j].text = ''
            cells[j].paragraphs[0].add_run(str(v)).font.size = Pt(9)
    if anchos:
        for row in t.rows:
            for j, w in enumerate(anchos):
                row.cells[j].width = Cm(w)
    return t


doc = Document()
st = doc.styles['Normal']
st.font.name = 'Calibri'
st.font.size = Pt(10.5)
for s in doc.sections:
    s.left_margin = s.right_margin = Cm(2)

doc.add_heading('Auditoría analítica independiente', 0)
doc.add_paragraph('Etapa 1 — Extracción de datos').runs[0].bold = True
tabla_doc(doc, ['Campo', 'Detalle'], [
    ('Artículo', ARTICULO),
    ('Pasaje auditado', TEXTO_FUENTE),
    ('Fecha de verificación', EV['fecha']),
    ('Datos crudos', EV['carpeta'] + ' (50 archivos, solo lectura; huellas SHA-256 en el Excel anexo)'),
    ('Anexo de evidencia', 'Auditoria_Etapa1_Extraccion.xlsx'),
    ('Reproducción', 'python auditoria/scripts/verificar_extraccion.py y python auditoria/scripts/generar_entregables.py'),
    ('Alcance', 'Afirmaciones A1–A6 (conteos del corpus). A7–A11 se auditan en la etapa de Resultados.'),
], [4, 13])

doc.add_heading('1. Resumen ejecutivo', 1)
cnt = Counter(a['v'] for a in A)
doc.add_paragraph(f'Se auditaron 6 afirmaciones de conteo: {cnt["OK"]} confirmadas, {cnt["PAR"]} parciales, '
                  f'{cnt["NO"]} no sustentada. Ningún número es un error de cálculo; los problemas son de método '
                  '(qué filas y columnas se leen) y de redacción (qué se dice que se contó).')
for txt in [
    f'A6 (❌): "1.466 elementos de perfil" es producto de un error del código, que omite columnas cuando el '
    f'encabezado está escrito de otra forma. El universo real es {n(T["p1_reales"])}; se pierde el '
    f'{perdidos_p1 / T["p1_reales"]:.0%}. Arrastra al 10,6 % (A9).',
    f'A4 (⚠️): las "1.612 estrategias" son 1.612 vínculos RA–estrategia; las estrategias declaradas son {n(T["p4_con_estrategia"])}.',
    f'A5 (⚠️): el 1.757 es correcto, pero el código del repositorio produce {n(T["p5_filas_col_D"])} porque no '
    'excluye las 50 filas de totales; no es reproducible.',
]:
    doc.add_paragraph(txt, style='List Bullet')

doc.add_heading('Decisiones de método adoptadas por la autora', 2)
tabla_doc(doc, ['ID', 'Tema', 'Decisión', 'Afecta a'], [(d[0], d[2], d[3], d[4]) for d in DECISIONES], [1, 3.5, 9, 3.5])
doc.add_heading('Redacción del corpus en el resumen', 2)
tabla_doc(doc, ['Versión', 'Texto'], REDACCION, [3.5, 13.5])
doc.add_heading('Menciones a 1.807 registros que deben corregirse', 2)
tabla_doc(doc, ['Línea', 'Sección', 'Texto actual', 'Acción'], [tuple(str(x) for x in m) for m in MENCIONES_39], [1.3, 3, 6.5, 6.2])

doc.add_heading('Definiciones finales', 2)
doc.add_paragraph('Definiciones usadas para todos los conteos de la auditoría. Son las mismas del Excel (hoja Definiciones) '
                  'y de auditoria/DEFINICIONES.md.')
tabla_doc(doc, ['Término', 'Definición', 'Regla de conteo', 'Valor final', 'Dec.'],
          [(d['termino'], d['definicion'] + ' Fuente: ' + d['fuente'] + '.', d['regla'], d['valor'], d['decision'])
           for d in DEFINICIONES], [3, 6, 4.6, 2.4, 1])

doc.add_heading('Textos corregidos del artículo', 2)
doc.add_paragraph('Versiones aprobadas por la autora durante la auditoría. También en el Excel (hoja Textos_corregidos) '
                  'y en auditoria/TEXTOS_CORREGIDOS.md.')
for _tit, _bloques in TXT.SECCIONES:
    doc.add_heading(_tit, 3)
    for _b in _bloques:
        if _b[0] == 'p':
            doc.add_paragraph(_b[1])
        elif _b[0] == 'n':
            doc.add_paragraph(_b[1]).runs[0].italic = True
        elif _b[0] in ('h', 'h2'):
            doc.add_heading(_b[1], 4)
        elif _b[0] == 'fig':
            doc.add_paragraph(f'[{_b[1]}]').runs[0].italic = True
        else:
            doc.add_paragraph(_b[1]).runs[0].bold = True
            tabla_doc(doc, _b[2], [tuple(f) for f in _b[3]])
open('auditoria/TEXTOS_CORREGIDOS.md', 'w', encoding='utf-8').write(TXT.markdown(EV['fecha']))
_pm = ['# Pendientes por definir (inicio de la etapa de Resultados)', '',
       f'Generado por auditoria/scripts/generar_entregables.py ({EV["fecha"]}). También en el Excel (hoja Pendientes) y en el Word.', '',
       '| ID | Tema | Etapa | Qué falta definir |', '|---|---|---|---|']
_pm += ['| ' + ' | '.join(str(c).replace('|', '/') for c in _p) + ' |' for _p in PENDIENTES_AFIRM]
open('auditoria/PENDIENTES.md', 'w', encoding='utf-8').write('\n'.join(_pm) + '\n')

doc.add_heading('2. Tabla de auditoría', 1)
t = tabla_doc(doc, ['ID', 'Afirmación', 'Qué se cuenta', 'Artículo', 'Recalculado', 'Veredicto'],
              [(a['id'], a['afirmacion'], a['que'].split('.')[0] + '.', a['art'], a['rec'], VERDICT[a['v']][0]) for a in A],
              [1.2, 3.2, 5.5, 1.8, 3.3, 2.5])
for i, a in enumerate(A, 1):
    sombrear(t.rows[i].cells[5], VERDICT[a['v']][1])

doc.add_heading('3. Detalle por afirmación', 1)
doc.add_paragraph('Cada afirmación se presenta con la misma estructura, para que un lector externo pueda '
                  'repetir la verificación sin conocer el proyecto.')
for a in A:
    doc.add_heading(f'{a["id"]} — {a["afirmacion"]}  ·  {VERDICT[a["v"]][0]}', 2)
    t = tabla_doc(doc, ['Pregunta', 'Respuesta'], [
        ('¿Qué se está contando?', a['que']),
        ('¿Dónde está el dato?', a['donde']),
        ('¿Con qué regla se contó?', a['regla']),
        ('Valor en el artículo', a['art']),
        ('Valor recalculado', a['rec']),
        ('¿Coincide?', a['coincide']),
        ('Tipo de error', a['tipo']),
        ('Explicación', a['explicacion']),
        ('Ejemplo con datos reales', a['ejemplo']),
        ('Riesgo si no se corrige', a['riesgo']),
        ('Acción recomendada', a['accion']),
        ('Redacción sugerida', a['redaccion']),
        ('Evidencia (hoja del Excel)', a['evidencia']),
    ], [4, 13])
    for row in t.rows[1:]:
        row.cells[0].paragraphs[0].runs[0].bold = True
    sombrear(t.rows[6].cells[1], VERDICT[a['v']][1])

doc.add_heading('4. Del archivo crudo a la cifra publicada (embudo de conteos)', 1)
tabla_doc(doc, ['Nivel', 'Paso', 'Registros', 'Nota'], [(e[0], e[1], n(e[2]), e[3]) for e in EMBUDO], [3, 7, 2.2, 5])

doc.add_heading('5. Anomalías detectadas en extracción y código', 1)
tabla_doc(doc, ['Severidad', 'Descripción', 'Ubicación', 'Afecta a', 'Corrección'],
          [(a[0], a[2], a[3], a[4], a[5]) for a in ANOMALIAS], [1.8, 6.5, 3.2, 2.2, 3.6])

doc.add_heading('6. Correcciones de código propuestas (no aplicadas)', 1)
for titulo, codigo in [
    ('A6 — normalizar encabezados del perfil antes de extraer elementos',
     "def _nk(s): return re.sub(r'[^a-z]', '', unicodedata.normalize('NFKD', str(s))\n"
     "                     .encode('ascii', 'ignore').decode().lower())\n"
     "_MAPA = {_nk(c): c for c in COLUMNAS_PERFIL}\n"
     "df_perfil = df_perfil.rename(columns=lambda c: _MAPA.get(_nk(c), c))"),
    ('A5 — excluir la fila de totales del Paso 5',
     "col = 'Nombre asignatura o módulo'\n"
     "df = df[~df[col].astype(str).str.strip().str.fullmatch(r'[\\d\\.\\s]+')]"),
    ('A4 — leer el encabezado real del Paso 4 (config.py)',
     "HEADER_ROWS['ESTRATEGIAS_MESO'] = 1  # fila 1 = instrucciones, fila 2 = encabezado"),
]:
    doc.add_paragraph(titulo).runs[0].bold = True
    p = doc.add_paragraph()
    r = p.add_run(codigo)
    r.font.name = 'Consolas'
    r.font.size = Pt(9)

doc.add_heading('7. Verificaciones pendientes para la siguiente etapa', 1)
tabla_doc(doc, ['ID', 'Afirmación', 'Qué verificar'], [(p[0], p[1], p[3]) for p in PENDIENTES_AFIRM], [1.2, 7.5, 8])

doc.add_heading('8. Declaración de método de la auditoría', 1)
doc.add_paragraph('Los conteos se recalcularon de forma independiente leyendo directamente los archivos Excel con '
                  'openpyxl, sin usar los archivos procesados del proyecto. Para A6 se reutilizó únicamente la función '
                  'de división de elementos del proyecto, con el fin de aislar el efecto de la lectura de columnas. '
                  'No se modificaron datos crudos ni código original. Las huellas SHA-256 de los 50 archivos permiten '
                  'comprobar en el futuro que la auditoría se repite sobre los mismos datos.')
if EDA:
    doc.add_page_break()
    doc.add_heading('Etapa 2 — Análisis exploratorio (EDA) de resultados de aprendizaje', 1)
    doc.add_paragraph('Objetivo: antes de calcular indicadores, establecer cuál es la unidad de análisis correcta '
                      'y la calidad de los datos de RA. Evidencia completa en las hojas EDA_* del Excel.')
    doc.add_heading('Decisión de método: ¿filas o RA únicos?', 2)
    doc.add_paragraph('En el Paso 3 cada fila es una combinación competencia–tipo de saber–RA. Un mismo RA se copia en '
                      'cada competencia a la que aporta. Por eso:')
    for txt in [
        'Para contar RA, calcular porcentajes (evaluabilidad, ruta completa) y aplicar pruebas estadísticas, la unidad '
        'es el RA único por matriz. Usar filas cuenta varias veces la misma promesa formativa y trata copias como '
        'observaciones independientes.',
        'Las filas solo son la unidad correcta cuando la pregunta es sobre vínculos (p. ej. a cuántas competencias aporta un RA).',
        'La deduplicación se hace dentro de cada matriz: la misma redacción en dos sedes son dos compromisos distintos.',
        'La identidad del RA es su texto normalizado, no su número (la numeración tiene inconsistencias, ver E3).',
    ]:
        doc.add_paragraph(txt, style='List Bullet')
    doc.add_paragraph('Ejemplo de control — FormatoRA_AdmonEmpresas_HMED: 13 filas en el Paso 3 = 7 RA únicos; '
                      'esos 7 RA son citados por 25 filas del Paso 4 y 126 filas del Paso 5. Un RA ("Identifica '
                      'fenómenos contemporáneos…") no tiene estrategia mesocurricular.')
    doc.add_heading('Resultados de aprendizaje únicos por formato', 2)
    doc.add_paragraph('Filas = registros del Paso 3. RA únicos = redacciones distintas dentro del formato. '
                      'El detalle de cada RA (texto, números, filas de Excel) está en la hoja A3_Detalle_RA_unicos.')
    tabla_doc(doc, ['#', 'Formato', 'Filas', 'RA únicos', 'Filas por RA', 'Nº ≠ texto'],
              [(x[0], x[1].replace('FormatoRA_', '').replace('.xlsx', ''), x[4], x[5], x[7], x[9]) for x in POR_FORMATO]
              + [('', 'TOTAL', 586, u_tot, round(586 / u_tot, 2), '')], [1, 7, 1.8, 2, 2.2, 2])
    doc.add_heading('Hallazgos', 2)
    tabla_doc(doc, ['ID', 'Tema', 'Hallazgo', 'Implicación'],
              [(e[0], e[1], e[2] + ' ' + e[3], e[4]) for e in EDA_HALLAZGOS], [1, 3, 8, 5])
    doc.add_heading('Distribución por tipo de saber según la unidad', 2)
    tabla_doc(doc, ['Tipo de saber', 'Filas', '% filas', 'RA únicos', '% únicos'],
              [tuple(str(v) for v in x) for x in tabla_tipo], [3.5, 2.5, 2.5, 2.5, 2.5])
    doc.add_paragraph('Lectura: el artículo afirma que la distribución (37,9 / 31,1 / 31,1) está próxima al referente '
                      'de un tercio. Eso solo es cierto contando filas. Contando RA únicos, el SaberSer cae a '
                      f'{pct(ut["SaberSer"], u_tot)}: los programas declaran pocos RA actitudinales y los reutilizan en '
                      'varias competencias. Es una conclusión distinta y debe reportarse.')

doc.add_page_break()
doc.add_heading('Sección "Variables" y Tabla 2', 1)
tabla_doc(doc, ['ID', 'Afirmación', 'Proyecto / artículo', 'Auditoría', 'Veredicto', 'Explicación'],
          [(v[0], v[2], v[3], v[4], v[5], v[7]) for v in VARIABLES], [1, 3, 2.4, 3.6, 2, 5])

doc.add_page_break()
doc.add_heading('Sección "Procedimiento"', 1)
tabla_doc(doc, ['ID', 'Etapa', 'Afirmación', 'Evidencia', 'Veredicto', 'Corrección'],
          [(x[0], x[1], x[2], x[4], x[5], x[7]) for x in PROCEDIMIENTO], [1, 1.6, 3.6, 4.4, 2, 4.4])

if COR and RES:
    doc.add_page_break()
    doc.add_heading('Sección "Corpus" y Tabla 1', 1)
    tabla_doc(doc, ['ID', 'Afirmación', 'Artículo', 'Recalculado', 'Veredicto', 'Corrección'],
              [(x[0], x[1], x[2], x[3], x[4], x[6]) for x in CORPUS], [1, 3.2, 1.8, 4, 2, 5])
    doc.add_heading('Tabla 1 recalculada', 2)
    tabla_doc(doc, ['Nivel', 'Matrices', 'Compet. art./rec.', 'RA filas', 'RA únicos', 'Meso vínculos', 'Estrategias'],
              [(t[0], t[2], f'{t[3]} / {t[4]}', t[6], t[7], t[9], t[10]) for t in T1], [3.6, 1.6, 2.4, 1.8, 1.8, 2.2, 2])
    doc.add_paragraph('Nota: "Profesional universitario" incluye 3 licenciaturas. Con las decisiones D4 y D5, las columnas '
                      'pertinentes son "RA únicos" y "Estrategias declaradas".')
    doc.add_heading('Resultados del resumen (A7–A11)', 1)
    tabla_doc(doc, ['ID', 'Afirmación', 'Artículo', 'Recalculado', 'Veredicto', 'Explicación'],
              [(x[0], x[1], x[2], x[3], x[4], x[6]) for x in RESULTADOS], [1, 2.6, 2, 4.6, 2, 5])
    doc.add_paragraph('Hallazgo principal: el 52,3 % de trazabilidad del resumen no se reproduce; dos cálculos '
                      'independientes dan alrededor de 86 %. Las interpretaciones construidas sobre "casi la mitad de los RA '
                      'sin ruta" (resultados, discusión y conclusiones) deben revisarse.')

doc.save(DOCX)
print('OK', XLSX, DOCX)
