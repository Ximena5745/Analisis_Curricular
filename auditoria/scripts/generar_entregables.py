"""
Genera los entregables de la auditoría de la Etapa 1 (Extracción):
    auditoria/Auditoria_Etapa1_Extraccion.xlsx
    auditoria/Auditoria_Etapa1_Extraccion.docx

Requiere haber ejecutado antes auditoria/scripts/verificar_extraccion.py
"""
import json
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
    ('A7', 'La evaluabilidad alcanzó 98,3 %', 'Resultados', 'Definir qué hace "evaluable" a un RA y recalcular.'),
    ('A8', 'Solo el 52,3 % de los RA presentó ruta documentada completa hasta una evidencia de evaluación', 'Resultados', 'Definir "ruta completa"; considerar 141 asignaturas sin RA y vínculos meso sin estrategia.'),
    ('A9', 'El 10,6 % de los elementos del perfil generó alertas de falta de respaldo', 'Resultados', 'Depende de A6: recalcular con 2.562 elementos.'),
    ('A10', 'El 28,9 % de las asignaturas homónimas mostró contenidos divergentes', 'Resultados', 'Depende de A5: verificar exclusión de filas de totales y normalización de nombres (709 vs 716 recalculadas).'),
    ('A11', 'La IA apareció en el 79,5 % de los programas, pero solo en el 3,3 % de los registros micro', 'Resultados', 'Depende de A2 (denominador 39/50) y de A5 (1.757/1.807).'),
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
    ('Paso 3 – RA', 'RA distintos dentro de cada matriz', T['ra_unicos_por_archivo'], 'Un RA se repite por tipo de saber'),
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
    ('D7', '2026-10-01', 'Unidad "núcleo temático"', 'Un núcleo = un ítem numerado de la celda de núcleos ("1. …", "2. …"), aunque ocupe varias líneas; si la celda no está numerada, cada línea es un núcleo. No se corta por comas ni por saltos de línea internos.', 'C13, Etapa 2 (LDA, densidad, asignaturas compartidas)'),
]

REDACCION = [
    ('Original', 'Estudio aplicado de métodos mixtos sobre 50 matrices de 39 programas: 586 registros de resultados de aprendizaje, '
                 '1.612 estrategias mesocurriculares, 1.757 registros de asignatura y 1.466 elementos de perfiles de egreso, analizados '
                 'mediante cinco variables de coherencia y trazabilidad, minería de texto, modelado temático y contraste estadístico exploratorio.'),
    ('Propuesta de la autora', 'Estudio aplicado de métodos mixtos sobre 50 matrices curriculares correspondientes a 50 programas académicos: '
                 '341 resultados de aprendizaje únicos por programa, 391 estrategias mesocurriculares declaradas, 1.757 registros de '
                 'asignatura y 100 perfiles de egresados (profesional y ocupacional), analizados mediante […]'),
    ('Versión corregida (auditoría)', 'Estudio aplicado de métodos mixtos sobre 50 matrices curriculares de 39 programas académicos: '
                 '341 resultados de aprendizaje únicos (deduplicados en cada matriz), 391 estrategias mesocurriculares declaradas, '
                 '1.757 registros de asignatura y 50 perfiles profesionales y 50 perfiles ocupacionales, analizados mediante cinco '
                 'variables de coherencia y trazabilidad, minería de texto, modelado temático y contraste estadístico exploratorio.'),
    ('Ajustes respecto a la propuesta', '(1) "únicos por programa" se lee como 341 en cada programa → "deduplicados en cada matriz". '
                 '(2) "100 perfiles de egresados" → "50 perfiles profesionales y 50 perfiles ocupacionales": son dos textos por programa '
                 'y se decidió no usar "egreso". (3) Condición: los porcentajes del resumen (98,3 %, 52,3 %, 10,6 %, 79,5 %, 3,3 %) '
                 'deben recalcularse sobre estas mismas unidades antes de publicar.'),
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
filas += [[p[0], p[1], '—', '—', '—', '—', '—', '—', 'Pendiente (etapa ' + p[2] + ')', '—', p[3], '—', '—', '—', '—', 'Pendientes'] for p in PENDIENTES_AFIRM]
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
        ('A7', 'Evaluabilidad 98,3 %', '98,3 %', f'Salida existente: {rc["V3_media"]} % (mín. {rc["V3_min"]} %). No hay código.',
         '❓ No verificable', 'Trazabilidad del cálculo',
         'Ningún archivo produce 98,3 %; la única salida da 99,2 %. Además el marco teórico (p68) define evaluabilidad como "instrumento asociado" y los resultados (p166) como "verbo observable + producto". Unificar definición y conservar el script.'),
        ('A8', 'Ruta completa 52,3 %', '52,3 %',
         f'Recalculado: {rr["v4_media_prog_similitud"]} % (media por programa, similitud ≥ 0,80; global {rr["v4_global_similitud"]} %; exacto {rr["v4_global_exacto"]} %). Salida existente: {rc["V4_media"]} %.',
         '❌ No sustentada', 'Cálculo',
         'Dos cálculos independientes dan ~86 %, no 52,3 %. La conclusión "casi la mitad de los RA no tiene ruta" no se sostiene: es ~1 de cada 7. Revisar todos los párrafos que interpretan el 52,3 %.'),
        ('A9', '10,6 % del perfil sin respaldo', '10,6 % (155/1.466)', f'Salida existente: {rc["brechas_perfil"]} brechas; unidad descartada (D3)',
         '❌ No sustentada', 'Método', 'Recalcular sobre los 100 textos de perfil profesional y ocupacional.'),
        ('A10', '28,9 % de homónimas divergentes', '28,9 % (46/159)', f'Salida existente: {rc["divergentes"]}/{rc["asig_compartidas"]} = {rc["pct_divergentes"]} %. No hay código.',
         '⚠️ Parcial', 'Reproducibilidad', 'El valor coincide con la salida, pero no hay script, y "compartida" se definió por denominación (39); con D1 el universo cambia.'),
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
     f'El filtro procesa {n(MIC["R2_tokens"])} ítems y descarta {MIC["R2_rechazados"]} (14,0 %). 7.906 proviene de otra tokenización (corte por coma).',
     '❌ No sustentada', 'Cálculo / método',
     'La resta es aritméticamente correcta pero mezcla dos procesos. Con D7 (núcleos numerados) el filtro descarta 926 de 6.671 (13,9 %), mayoritariamente núcleos legítimos (C13c).'),
    ('P6', 'Etapa 2', 'Puntaje orientativo y detector de atípicos (Isolation Forest; Liu et al., 2008)', '—',
     'Ambos implementados; el umbral del puntaje está inactivo (no decide)', '✅ Confirmada', '—', 'Sin cambios.'),
    ('P7', 'Etapa 3', 'Puntaje de calidad: completitud 25 %, exigencia 20 %, equilibrio, cobertura y variedad 15 % c/u', '90 % declarado',
     'src/analyzer.py:calcular_score_calidad suma un sexto componente "calidad_redaccion" (10 %) = constante 80 ("# Placeholder")',
     '❌ No sustentada', 'Método',
     'Todos los programas reciben 8 puntos fijos no evaluados. Declarar el componente o eliminarlo y recalcular el puntaje.'),
    ('P8', 'Etapa 3 / Tabla 4', '"Bloom 44,1 % / BAK 55,9 %"', '44,1 / 55,9',
     f'Por filas: Bloom {_pf(_tf["Bloom"], 586)} % / BAK {_pf(_tf["BAK"], 586)} %. Por RA únicos (D4): Bloom {_pf(_tu["Bloom"], 341)} % / BAK {_pf(_tu["BAK"], 341)} %. '
     f'Por matriz: {_tm.get("BAK + Bloom", 0)} usan ambas, {_tm.get("Bloom", 0)} solo Bloom, {_tm.get("BAK", 0)} solo BAK.',
     '⚠️ Parcial', 'Cálculo (redondeo) / unidad',
     'Diferencia de 0,1 punto con filas; con RA únicos el reparto es casi parejo (48/52). La Tabla 4 omite niveles usados: BAK cognitivo "Evaluación" (4 RA) y BAK actitudinal "Caracterizar" (3 RA). Aclarar que la taxonomía varía dentro de una misma matriz.'),
    ('P9', 'Etapa 4', '"Cada elemento del perfil se compara… métrica híbrida TF-IDF y BM25"', '—',
     'Unidad "elemento" descartada (D3). BM25 y spaCy se omiten en silencio si no están instalados (src/perfil_coverage_analyzer.py:87, 167)',
     '⚠️ Parcial', 'Método / reproducibilidad', 'Aplicar D3 y hacer obligatorias (o registrar en el log) las dependencias de la métrica.'),
    ('P10', 'Tabla 5', 'Umbrales por campo (0,28–0,38)', '—', 'Coinciden con config.UMBRALES_POR_CAMPO', '✅ Confirmada', '—', 'Sin cambios.'),
    ('P11', 'Etapa 4', '"umbrales… se fijaron empíricamente contra la revisión experta (P6)"', '—',
     'NOTAS_REVISION_v2.md (pend. 9–10): calibración con pares pendiente; no hay registros de la revisión', '❓ No verificable', 'Evidencia',
     'Aportar la muestra, los revisores y el acuerdo, o reformular.'),
    ('P12', 'Etapa 5', 'Comparación por nombre y por contenido', '—',
     'Funciones en src/shared_subjects_analyzer.py; no existe el script que produce las cifras de divergencia (A10)', '⚠️ Parcial', 'Reproducibilidad', 'Versionar el script.'),
    ('P13', 'Etapa 6', '"LDA… se aplica sobre los temas depurados en la Etapa 2"', '—',
     'src/topic_modeler.py entrena LDA sobre "SaberAsociado" del Paso 3 (≤ 586 textos); tools/calibrar_lda.py lo rotula "≈5.780 núcleos". Ningún código aplica LDA a los núcleos.',
     '❌ No sustentada', 'Método', 'Ubicar el cálculo que produjo la Tabla 16 o re-estimar el LDA sobre los núcleos (D7).'),
    ('P14', 'Etapa 6', 'k = 10 con semilla fija', '—', 'random_state = 42; N_TOPICS_DEFAULT = 10. Existe tools/calibrar_lda.py (coherencia c_v para k 5–20) sin resultado reportado',
     '⚠️ Parcial', 'Redacción', 'Reportar la curva de coherencia o declarar que k no se optimizó.'),
    ('P15', 'Etapa 6', 'Presencia de temas de agenda global con lista ajustable', '—', 'Lista en config_tendencias.json; la búsqueda es por subcadena ("ia" en "sociales")',
     '⚠️ Parcial', 'Método', 'Usar coincidencia de palabra completa (A11).'),
    ('P16', 'Etapa 7', '"Por cada programa se generan un archivo consolidado y un informe"', '—',
     'run_analysis.py:112-114 nombra los reportes sin sede: los programas multisede se sobrescriben (50 matrices → 39 nombres)',
     '❌ No sustentada', 'Código', 'Nombrar reporte_<Programa>_<Sede>.'),
    ('P17', 'Tabla 6', 'Python 3.10 y bibliotecas', '3.10', 'Bytecode de 3.10 y 3.14 en el proyecto; requirements.txt sin versiones fijadas (">=")',
     '⚠️ Parcial', 'Reproducibilidad', 'Fijar versiones exactas (pip freeze) y la versión de Python usada en la corrida final.'),
    ('P18', 'Tabla 6', 'IA generativa "solo diseño y construcción"', '—', 'Integración con Claude presente pero desactivada (config LLM_ENABLED = False)', '✅ Confirmada', '—',
     'Mencionar que el módulo existe y no se usó.'),
    ('P19', 'Cierre', '"El código, versiones, semillas, parámetros… están documentados"', '—',
     'Falta el código de V1–V5, de la divergencia de asignaturas y del LDA sobre núcleos; versiones sin fijar', '❌ No sustentada', 'Reproducibilidad',
     'Completar el repositorio o acotar la afirmación.'),
    ('P20', 'Cierre', '"la estructuración generativa de las matrices es trazable mediante el registro de entradas, salidas y decisiones humanas"', '—',
     'No hay registro de prompts ni de decisiones en el repositorio; src/run_tracker.py solo registra corridas del análisis', '❓ No verificable', 'Evidencia',
     'Adjuntar el registro o reformular.'),
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
tabla_doc(doc, ['ID', 'Afirmación', 'Qué verificar'], [(p[0], p[1], p[3]) for p in PENDIENTES_AFIRM] + [
    ('—', 'Competencias: 217 (tablas) vs 220 (texto)', 'Auditar Paso 2 con el encabezado correcto.'),
    ('—', '709 asignaturas únicas / 168 compartidas', 'Se obtienen 716 / 170 con normalización simple; documentar la regla.'),
], [1.2, 7.5, 8])

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
