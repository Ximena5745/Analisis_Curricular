"""
Excel de auditoría depurado: solo la información necesaria para auditar.

Se invoca desde generar_entregables.py (build(globals())), que ya tiene en
memoria las afirmaciones, decisiones y evidencias cargadas.

Hojas:
  LEEME, Hallazgos, Decisiones_metodo, Redaccion_corregida, Tabla1_corpus,
  Evidencia_por_matriz, Competencias_detalle, RA_unicos_detalle,
  Meso_ejemplos, Micro_filas_totales, Perfil_columnas, Multisede,
  IA_detecciones, Anomalias, Pendientes, Inventario_archivos
"""
from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side

HDR = PatternFill('solid', fgColor='1F3864')
_thin = Side(style='thin', color='BFBFBF')
BOX = Border(left=_thin, right=_thin, top=_thin, bottom=_thin)
WRAP = Alignment(wrap_text=True, vertical='top')
COLOR_VEREDICTO = {'✅': 'C6EFCE', '⚠️': 'FFEB9C', '❌': 'FFC7CE', '❓': 'D9D9D9', 'Hallazgo': 'DDEBF7'}

EVIDENCIA = {
    'A1': 'Inventario_archivos', 'A2': 'Evidencia_por_matriz', 'A3': 'RA_unicos_detalle',
    'A4': 'Meso_ejemplos', 'A5': 'Micro_filas_totales', 'A6': 'Perfil_columnas',
    'C1': 'Inventario_archivos', 'C2': 'Evidencia_por_matriz', 'C3': 'Evidencia_por_matriz', 'C4': '—',
    'C5': 'Multisede', 'C6': '—', 'C7': 'Tabla1_corpus', 'C8': 'Tabla1_corpus, Competencias_detalle',
    'C9': 'Tabla1_corpus, RA_unicos_detalle', 'C10': 'Tabla1_corpus, Meso_ejemplos', 'C11': 'Micro_filas_totales',
    'C12': '—', 'C13a': 'Evidencia_por_matriz', 'C13b': 'Evidencia_por_matriz', 'C13c': 'Anomalias', 'C13d': 'Evidencia_por_matriz', 'C13e': 'Multisede', 'C14': 'Evidencia_por_matriz', 'C15': 'Multisede',
    'E1': 'RA_unicos_detalle', 'E2': 'RA_unicos_detalle', 'E3': 'RA_unicos_detalle', 'E4': 'Evidencia_por_matriz',
    'E5': 'Anomalias', 'E6': '—',
    'A7': '—', 'A8': 'Evidencia_por_matriz', 'A9': 'Perfil_columnas', 'A10': '—',
    'A11a': 'IA_detecciones', 'A11b': 'IA_detecciones',
}


def _tabla(ws, cab, filas, anchos, fila0=1):
    for j, c in enumerate(cab, 1):
        x = ws.cell(fila0, j, c)
        x.font = Font(bold=True, color='FFFFFF')
        x.fill = HDR
        x.alignment = Alignment(wrap_text=True, vertical='center')
        x.border = BOX
    for i, f in enumerate(filas, fila0 + 1):
        for j, v in enumerate(f, 1):
            x = ws.cell(i, j, v)
            x.alignment = WRAP
            x.border = BOX
    for j, w in enumerate(anchos, 1):
        ws.column_dimensions[ws.cell(1, j).column_letter].width = w
    ws.freeze_panes = ws.cell(fila0 + 1, 2)
    if filas:
        ws.auto_filter.ref = f'A{fila0}:{ws.cell(fila0, len(cab)).column_letter}{fila0 + len(filas)}'


def _nota(ws, texto):
    ws.cell(1, 1, texto).font = Font(italic=True)


def _negrita_ultima(ws):
    for c in ws[ws.max_row]:
        c.font = Font(bold=True)


def build(g):
    A, CORPUS, RESULTADOS = g['A'], g['CORPUS'], g['RESULTADOS']
    EDA_H, DEC, RED = g['EDA_HALLAZGOS'], g['DECISIONES'], g['REDACCION']
    EV, EDA, COR, RES, T1 = g['EV'], g['EDA'], g['COR'], g['RES'], g['T1']
    VER = g['VERDICT']
    wb = Workbook()

    # 1. LEEME
    ws = wb.active
    ws.title = 'LEEME'
    filas = [
        ('Auditoría analítica independiente del artículo curricular', ''),
        ('Artículo auditado', 'Articulo_curricular_IA.docx (versión vigente, 14-ago-2026) — resumen y sección Corpus.'),
        ('Datos crudos', EV['carpeta'] + ' (50 archivos, solo lectura; huellas SHA-256 en Inventario_archivos).'),
        ('Fecha de verificación', EV['fecha']),
        ('Reproducir', 'Ejecutar en orden: verificar_extraccion.py, eda_resultados_aprendizaje.py, verificar_corpus.py, '
                       'verificar_resultados.py, generar_entregables.py (carpeta auditoria/scripts).'),
        ('', ''),
        ('Cómo leer', '1) Hallazgos: un renglón por afirmación con su veredicto. 2) La columna "Evidencia" indica la hoja '
                      'donde se comprueba. 3) Decisiones_metodo fija las unidades de conteo adoptadas por la autora.'),
        ('', ''),
        ('✅ Confirmada', 'Coincide con los datos y el método es adecuado.'),
        ('⚠️ Parcial', 'El valor coincide, con reservas de método o redacción.'),
        ('❌ No sustentada', 'No coincide o el método no la respalda.'),
        ('❓ No verificable', 'Falta dato, archivo o código.'),
        ('Hallazgo', 'Observación del análisis exploratorio, sin afirmación del artículo asociada.'),
        ('', ''),
        ('NOTAS SOBRE LOS DATOS', 'Características del corpus documentadas por la auditoría que no constituyen hallazgos sobre el artículo.'),
        ('N1 Espacios electivos', f'{g["MIC"]["asig_sin_nucleos"]} registros de asignatura no declaran núcleos temáticos; todos son espacios electivos '
                                  '("Electiva 1…4", "Electiva I…IV", "Electiva"): 4 en cada una de las 34 matrices de pregrado profesional y 1 en '
                                  '5 matrices de posgrado (EspGerTributaria, EspGestionEducativa, MEDSTEM, MGerTalentoHumano, MInnovacionEducativa). '
                                  'Es un rasgo del diseño (el contenido lo define la electiva elegida), no una omisión. La misma electiva se escribe '
                                  'de 9 formas distintas, lo que debe considerarse al contar denominaciones y asignaturas compartidas. '
                                  'Detalle por matriz: Evidencia_por_matriz.'),
        ('N2 Corrección de datos crudos', '2026-10-02: la autora corrigió en FormatoRA_EspGerTributaria_PBOG.xlsx (Paso 5, núcleos temáticos) la numeración "1, …" '
                                          'por "1. …". SHA-256 anterior 56c3b9bb…59cf35; nuevo eb6e12f9…95ee9a (Inventario_archivos). Se re-ejecutó toda la verificación: '
                                          'ninguna cifra auditada cambió (6.671 núcleos, 2.815 únicos, 709 denominaciones, 222 competencias, 341 RA, 391 estrategias, 1.757 asignaturas).'),
        ('', ''),
        ('Tipos de error', 'Cálculo (conteo u operación mal hechos) · Método (filtros, reglas o unidad inadecuados o no '
                           'reproducibles) · Redacción (el número es correcto pero se nombra o interpreta mal).'),
    ]
    for i, (a, b) in enumerate(filas, 1):
        ws.cell(i, 1, a).font = Font(bold=True, size=14 if i == 1 else 11)
        ws.cell(i, 2, b).alignment = WRAP
    ws.column_dimensions['A'].width = 24
    ws.column_dimensions['B'].width = 120

    # 2. Hallazgos (registro único)
    H = []
    for a in A:
        H.append([a['id'], 'Resumen – corpus', a['afirmacion'], a['art'], a['rec'], VER[a['v']][0], a['tipo'],
                  a['explicacion'], f"{a['accion']} Redacción: {a['redaccion']}", EVIDENCIA.get(a['id'], '—')])
    for c in CORPUS:
        H.append([c[0], 'Sección Corpus', c[1], c[2], c[3], c[4], c[5], c[6], '', EVIDENCIA.get(c[0], '—')])
    for e in EDA_H:
        H.append([e[0], 'EDA (calidad de datos)', e[1], '—', e[2], 'Hallazgo', '—', e[3], e[4], EVIDENCIA.get(e[0], '—')])
    for x in g['PROCEDIMIENTO']:
        H.append([x[0], 'Procedimiento – ' + x[1], x[2], x[3], x[4], x[5], x[6], x[7], '', '—'])
    for v in g['VARIABLES']:
        H.append([v[0], v[1], v[2], v[3], v[4], v[5], v[6], v[4] if False else v[7], '', 'Evidencia_por_matriz'])
    for r in RESULTADOS:
        H.append([r[0], 'Resumen – resultados (preliminar)', r[1], r[2], r[3], r[4], r[5], r[6], '', EVIDENCIA.get(r[0], '—')])
    ws = wb.create_sheet('Hallazgos')
    _tabla(ws, ['ID', 'Sección', 'Afirmación', 'Valor artículo', 'Valor auditado', 'Veredicto', 'Tipo de error',
                'Explicación', 'Corrección sugerida', 'Evidencia (hoja)'], H,
           [7, 18, 30, 14, 36, 16, 20, 70, 50, 22])
    for i in range(2, ws.max_row + 1):
        v = str(ws.cell(i, 6).value)
        for k, col in COLOR_VEREDICTO.items():
            if v.startswith(k):
                ws.cell(i, 6).fill = PatternFill('solid', fgColor=col)

    # Definiciones finales
    ws = wb.create_sheet('Definiciones')
    _tabla(ws, ['Término', 'Definición', 'Dónde está el dato', 'Regla de conteo', 'Valor final', 'Decisión'],
           [[d['termino'], d['definicion'], d['fuente'], d['regla'], d['valor'], d['decision']] for d in g['DEFINICIONES']],
           [28, 60, 42, 55, 26, 9])

    # 3. Decisiones y 4. Redacción
    ws = wb.create_sheet('Decisiones_metodo')
    _tabla(ws, ['ID', 'Fecha', 'Tema', 'Decisión', 'Afecta a'], [list(d) for d in DEC], [6, 12, 26, 90, 30])
    ws = wb.create_sheet('Redaccion_corregida')
    _tabla(ws, ['Versión', 'Texto'], [list(r) for r in RED], [28, 150])

    # Textos corregidos del artículo
    import textos_articulo as TXT
    ws = wb.create_sheet('Textos_corregidos')
    filas_t = []
    for tit, bloques in TXT.SECCIONES:
        for b in bloques:
            if b[0] in ('p', 'n', 'h', 'fig'):
                filas_t.append([tit, {'p': 'Párrafo', 'n': 'Nota', 'h': 'Subtítulo', 'fig': 'Figura'}[b[0]], b[1]])
            else:
                filas_t.append([tit, 'Tabla', b[1] + '\n' + ' | '.join(b[2]) + '\n' + '\n'.join(' | '.join(f) for f in b[3])])
    _tabla(ws, ['Sección', 'Tipo', 'Texto'], filas_t, [26, 10, 150])

    # 5. Tabla 1
    ws = wb.create_sheet('Tabla1_corpus')
    _tabla(ws, ['Nivel', 'Matrices (art.)', 'Matrices (aud.)', 'Competencias (art.)', 'Competencias (aud.)',
                'RA filas (art.)', 'RA filas (aud.)', 'RA únicos (aud.)', 'Meso (art.)', 'Meso vínculos (aud.)',
                'Estrategias declaradas (aud.)', 'Asignaturas (aud.)', '¿Coincide?'], T1,
           [24, 10, 10, 12, 12, 10, 10, 10, 10, 12, 14, 12, 16])
    for i in range(2, ws.max_row + 1):
        if str(ws.cell(i, 13).value).startswith('No'):
            ws.cell(i, 13).fill = PatternFill('solid', fgColor='FFC7CE')

    # 6. Evidencia por matriz (una fila por archivo, todas las cifras)
    import pandas as pd
    rc = pd.read_excel('data/output/recalculo_2026.xlsx', 'Variables_V1_V5')
    rc_comp = {(r.prog, r.sede): int(r.n_comp) for r in rc.itertuples()}
    ext = {a['archivo']: a for a in EV['archivos']}
    eda = {p['archivo']: p for p in EDA['por_programa']}
    res = {p['archivo']: p for p in RES['por_programa']}
    mic = {p['archivo']: p for p in g['MIC_FULL']['por_matriz']}
    var = {p['archivo']: p for p in g['VAR_FULL']['por_matriz']}
    filas = []
    for m in COR['por_matriz']:
        f = m['archivo']
        e, d, r = ext[f], eda[f], res[f]
        filas.append([f, m['programa'], m['sede'], m['nivel'], m['competencias'], rc_comp.get((m['programa'], m['sede'])),
                      m['ra_filas'], m['ra_unicos'], 'Sí' if d['ra_unicos_numero'] != d['ra_unicos_texto'] else 'No',
                      m['meso_filas'], m['meso_estrategias'], d['ra_sin_meso'], e['p5_filas_col_D'], e['p5_filas_totales'],
                      m['asignaturas'], mic[f]['asig_sin_nucleos'], mic[f]['nucleos_R3'], mic[f]['menciones_R1'],
                      mic[f]['validos_R2'], e['p1_encabezado'], r['v4_similitud'], r['ia_estricta'],
                      var[f]['V2'], var[f]['V2_def_articulo_pct_repetidos'], var[f]['V5'], var[f]['V5_por_estrategia']])
    tot = ['TOTAL', '', '', ''] + [sum(x[j] or 0 for x in filas) if isinstance(filas[0][j], (int, float)) and j not in (20, 22, 23, 24, 25) else ''
                                   for j in range(4, 26)]
    ws = wb.create_sheet('Evidencia_por_matriz')
    _tabla(ws, ['Archivo', 'Programa', 'Sede', 'Nivel', 'Competencias', 'Competencias (recalculo_2026)', 'RA filas',
                'RA únicos', 'Nº de RA ≠ texto', 'Meso vínculos', 'Estrategias declaradas', 'RA sin estrategia meso',
                'Filas col. D Paso 5', 'Filas de totales', 'Asignaturas', 'Espacios electivos sin núcleos (nota N1)',
                'Núcleos numerados (D7)', 'Núcleos regla artículo (corte por coma)', 'Núcleos "válidos" (filtro proyecto)',
                'Encabezado perfil', 'Trazabilidad V4 % (aud.)', 'Asignaturas con IA',
                'V2 proyecto %', 'V2 según definición (% verbos repetidos)', 'V5 proyecto % (por fila)', 'V5 según definición (% estrategias)'],
           filas + [tot], [40, 24, 7, 22, 12, 14, 9, 9, 10, 10, 12, 12, 11, 10, 11, 11, 12, 14, 14, 12, 13, 11, 11, 14, 12, 14])
    _negrita_ultima(ws)

    # 7-8. Detalle fila a fila (competencias y RA)
    ws = wb.create_sheet('Competencias_detalle')
    _tabla(ws, ['Archivo', 'Nivel', 'Fila Excel', 'Col. A', 'Col. F (competencia)', 'Tipo', '¿Se cuenta?'],
           [[x['archivo'], x['nivel'], x['fila_excel'], x['col_A_numero'], x['col_F_competencia'], x['tipo'], x['cuenta']]
            for x in COR.get('competencias_detalle', [])], [40, 22, 9, 8, 90, 18, 30])
    ws = wb.create_sheet('RA_unicos_detalle')
    _tabla(ws, ['Archivo', 'Nº RA', 'Texto del RA', 'Número(s) asignado(s)', 'Tipo(s) de saber', 'Filas en Paso 3',
                'Filas Excel', 'Competencias a las que aporta'],
           [[x['archivo'], x['n'], x['ra'], x['numeros'], x['tipos'], x['filas_p3'], x['filas_excel'], x['competencias']]
            for x in EDA['detalle_ra']], [40, 7, 90, 12, 16, 9, 16, 12])

    # 9-11. Evidencia puntual
    ws = wb.create_sheet('Meso_ejemplos')
    _nota(ws, 'Cada fila es un RA; la estrategia (col. B) se escribe solo en la primera fila de su bloque. Filas ≠ estrategias.')
    _tabla(ws, ['Archivo', 'Fila', 'A: RA', 'B: Estrategia', 'D: Indicador', '¿Estrategia nueva?'],
           [[e['archivo'], e['fila_excel'], e['A_resultado_aprendizaje'], e['B_estrategia_programa'], e['D_indicador'],
             'Sí' if e['B_estrategia_programa'] != '(vacío)' else 'No'] for e in EV['ejemplos_p4'][:6]],
           [34, 7, 55, 34, 45, 14], fila0=3)
    ws = wb.create_sheet('Micro_filas_totales')
    _nota(ws, 'Filas de totales del Paso 5 (una por matriz): la col. D tiene un número, no una asignatura. Se excluyen: 1.807 − 50 = 1.757.')
    _tabla(ws, ['Archivo', 'Fila Excel', 'Col. C', 'Col. D'],
           [[t['archivo'], t['fila_excel'], t['C_texto'], t['D_valor']] for t in EV['filas_totales_p5']], [42, 10, 50, 10], fila0=3)
    ws = wb.create_sheet('Perfil_columnas')
    _nota(ws, 'Paso 1. Con D3 se cuentan celdas: 1 perfil profesional + 1 ocupacional por matriz (100). '
              'Columnas a la derecha: evidencia del error del código que produjo 1.466.')
    _tabla(ws, ['Archivo', 'Encabezado', 'Perfil profesional (celdas)', 'Perfil ocupacional (celdas)',
                'Columnas que el código omite', 'Fragmentos contados por el código', 'Fragmentos reales'],
           [[p['archivo'], p['encabezado'], 1, 1, p['columnas_omitidas_por_el_codigo'], p['elementos_contados'],
             p['elementos_reales']] for p in EV['perfil_columnas']], [42, 12, 12, 12, 70, 14, 12], fila0=3)

    # 12. Multisede
    ws = wb.create_sheet('Multisede')
    _pct = {m['programa']: m['pct_compartido'] for m in g['MIC']['multisede']}
    _tabla(ws, ['Programa', 'Sedes', '¿RA idénticos entre sedes?', '¿Asignaturas idénticas?', '% núcleos compartidos por todas sus sedes'],
           [[m['programa'], m['sedes'], 'Sí' if m['ra_identicos'] else 'No', 'Sí' if m['asignaturas_identicas'] else 'No',
             _pct.get(m['programa'])] for m in COR['resumen']['multisede']], [24, 22, 16, 18, 20])

    # 13. IA
    ws = wb.create_sheet('IA_detecciones')
    filas = [['Detección válida', a['archivo'], a['asignatura'], a['termino'], ''] for a in RES['ia_asignaturas']]
    filas += [['Falso positivo del código', e['archivo'], e['asignatura'], e['keyword'], e['contexto']]
              for e in RES['falsos_positivos_subcadena']]
    _tabla(ws, ['Tipo', 'Archivo', 'Asignatura', 'Término', 'Contexto (falsos positivos)'], filas, [22, 40, 40, 22, 60])

    # 14. Anomalías
    R = EDA['resumen']
    anom = [list(a) for a in g['ANOMALIAS']] + [
        ('Alta', 'Reproducibilidad', 'No existe código para V1–V5 ni para la divergencia de asignaturas; solo la salida recalculo_2026.xlsx.', 'Repositorio', 'A7, A8, A10', 'Versionar los scripts que producen cada cifra.'),
        ('Alta', 'Consistencia', 'El .docx vigente y el .md reportan valores distintos (evaluabilidad 98,3 vs 99,2 %; trazabilidad 52,3 vs 86,2 %).', 'Articulo_curricular_IA.docx / .md', 'A7, A8', 'Fijar una sola versión fuente del artículo.'),
        ('Alta', 'Código', 'Detección de IA por subcadena: "ia" coincide con "sociales", "influencia"… (marca 50/50 matrices).', 'analisis_tematico_avanzado.py:464', 'A11', 'Usar coincidencia de palabra completa.'),
        ('Alta', 'Método', 'Núcleos: el 7.906/3.432 corta por comas (parte núcleos numerados); el 5.780 usa otra tokenización. Ninguna respeta la numeración de la celda.', 'analisis_tematico_avanzado.py:358; src/nucleos_cleaner.py:135', 'C13a–c, LDA', 'Separar por numeración (D7).'),
        ('Alta', 'Método', f'El filtro es_nucleo_valido rechaza {g["MIC"]["R3_rechazados_por_filtro_R2"]} núcleos numerados legítimos. Ejemplos: '
                  + '; '.join(f'"{e["nucleo"][:60]}" ({k})' for k, v in g['MIC_FULL']['ejemplos_rechazo_R3'].items() for e in v[:2]),
         'src/nucleos_cleaner.py:146-181 (_INICIO_INVALIDO, MIN_PALABRAS, _FINAL_LETRA_SUELTA, _PATRON_NO_NUCLEO)', 'C13c, LDA (n = 5.780)',
         'Quitar del filtro el inicio con artículo, las palabras únicas, "parte I/II" y los encabezados temáticos; revisar a mano los rechazos.'),
        ('Media', 'Método', 'Densidad de núcleos agrupada por nombre de asignatura en todo el corpus (suma las 40 matrices de "Razonamiento Cuantitativo").', 'analisis_tematico_avanzado.py:378', 'C13d', 'Calcular por asignatura dentro de cada matriz.'),
        ('Media', 'Datos crudos', f'Las {R["backups"]} hojas "Paso 3 … - Backup" contienen RA de otros programas (plantillas copiadas).', 'Archivos crudos', 'E5', 'Excluir y documentar.'),
        ('Media', 'Datos crudos', f'Numeración de RA inconsistente en {R["matrices_con_inconsistencia_numeracion"]} matrices: '
                  + '; '.join(f"{i['archivo'].replace('FormatoRA_', '').replace('.xlsx', '')} ({i['detalle']})" for i in EDA['inconsistencias']),
         'Paso 3', 'E3', 'Identificar el RA por su texto.'),
    ]
    ws = wb.create_sheet('Anomalias')
    _tabla(ws, ['Severidad', 'Categoría', 'Descripción', 'Ubicación', 'Afecta a', 'Corrección sugerida'], anom,
           [10, 16, 75, 30, 18, 40])
    color = {'Alta': 'FFC7CE', 'Media': 'FFEB9C', 'Baja': 'E2EFDA'}
    for i in range(2, ws.max_row + 1):
        ws.cell(i, 1).fill = PatternFill('solid', fgColor=color.get(ws.cell(i, 1).value, 'FFFFFF'))

    # 15. Pendientes
    pend = [(x[2], f'{x[0]} · {x[1]}', x[3]) for x in g['PENDIENTES_AFIRM']]
    ws = wb.create_sheet('Pendientes')
    _tabla(ws, ['Etapa', 'Ítem', 'Qué verificar'], [list(p) for p in pend], [14, 50, 80])

    # 16. Inventario
    ws = wb.create_sheet('Inventario_archivos')
    _tabla(ws, ['#', 'Archivo', 'Sede', 'Tamaño (bytes)', 'SHA-256'],
           [[i, a['archivo'], a['sede'], a['tamano_bytes'], a['sha256']] for i, a in enumerate(EV['archivos'], 1)],
           [5, 44, 7, 13, 70])

    wb.save(g['XLSX'])
    return wb.sheetnames
