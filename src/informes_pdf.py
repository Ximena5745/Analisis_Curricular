"""
Informes en PDF del Resumen Ejecutivo: uno general del conjunto cargado y uno por programa.

El módulo no calcula indicadores: recibe los resultados ya calculados por el dashboard (V1–V5, valoración por
criterios de src/indicadores_articulo.py, asociación del perfil, tipo de saber y tendencias) y los compone en un
documento. Usa la fuente Helvetica de fpdf2 (latin-1): los caracteres fuera de ese juego se sustituyen.
"""

from datetime import datetime
from pathlib import Path
from typing import Dict, Iterable, List, Sequence

from fpdf import FPDF
from fpdf.fonts import FontFace

LOGO = Path(__file__).resolve().parent.parent / 'assets' / 'logo_poli.png'

AZUL = (15, 56, 90)        # #0F385A
CIAN = (31, 178, 222)      # #1FB2DE
MAGENTA = (236, 6, 119)    # #EC0677
AMARILLO = (251, 175, 23)  # #FBAF17
GRIS = (138, 148, 160)     # #8A94A0
FONDO = (234, 249, 253)    # #EAF9FD

COLOR_ESTADO = {'Cumple': (209, 240, 250), 'Parcial': (254, 239, 205), 'No cumple': (252, 214, 232),
                'Sin dato': (230, 232, 235), 'Descriptiva': (245, 246, 248)}
COLOR_BARRA_ESTADO = {'Cumple': CIAN, 'Parcial': AMARILLO, 'No cumple': MAGENTA, 'Sin dato': GRIS}

_SUSTITUTOS = {'–': '-', '—': '-', '≥': '>=', '≤': '<=', '→': '->', '…': '...', '“': '"', '”': '"', '‘': "'",
               '’': "'", 'κ': 'kappa', '²': '2', '·': '-', '•': '-', ' ': ' ', ' ': ' '}

PIE = 'Propuesta para validar por el comité curricular. Calculado con los archivos cargados en el dashboard.'


def texto(t) -> str:
    """Texto apto para la fuente Helvetica (latin-1), sin marcas de negrita de Markdown."""
    s = '' if t is None else str(t)
    s = s.replace('**', '')
    for a, b in _SUSTITUTOS.items():
        s = s.replace(a, b)
    return s.encode('latin-1', 'replace').decode('latin-1')


def pct(v) -> str:
    return '-' if v is None else f'{v:.1f} %'.replace('.', ',')


class _Informe(FPDF):
    def __init__(self, titulo: str):
        super().__init__(orientation='P', unit='mm', format='A4')
        self.titulo = texto(titulo)
        self.set_auto_page_break(auto=True, margin=16)
        self.set_margins(15, 18, 15)
        self.alias_nb_pages()

    def header(self):
        if self.page_no() == 1:
            return
        self.set_font('Helvetica', 'B', 8)
        self.set_text_color(*GRIS)
        self.set_xy(15, 8)
        self.cell(0, 5, self.titulo, align='L')
        self.set_draw_color(*CIAN)
        self.line(15, 13.5, self.w - 15, 13.5)
        self.set_y(18)

    def footer(self):
        self.set_y(-12)
        self.set_font('Helvetica', '', 7)
        self.set_text_color(*GRIS)
        self.cell(0, 5, texto(PIE), align='L')
        self.cell(0, 5, f'Página {self.page_no()}/{{nb}}', align='R')


# --- Bloques de composición -----------------------------------------------------------------------------------

def _portada(pdf: _Informe, titulo: str, subtitulo: str, alcance: str, fecha: str):
    pdf.add_page()
    pdf.set_fill_color(*AZUL)
    pdf.rect(0, 0, pdf.w, 46, style='F')
    if LOGO.exists():  # el logo es azul oscuro: va sobre un recuadro blanco para que se vea en la franja
        pdf.set_fill_color(255, 255, 255)
        pdf.rect(pdf.w - 15 - 42, 6, 42, 28, style='F', round_corners=True, corner_radius=2)
        pdf.image(str(LOGO), x=pdf.w - 15 - 40, y=8, w=38)
    pdf.set_xy(15, 12)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font('Helvetica', '', 9)
    pdf.cell(0, 5, texto(subtitulo), new_x='LMARGIN', new_y='NEXT')
    pdf.set_font('Helvetica', 'B', 17)
    pdf.multi_cell(pdf.w - 30 - 40, 8, texto(titulo), new_x='LMARGIN', new_y='NEXT')
    pdf.set_y(50)
    pdf.set_text_color(*AZUL)
    pdf.set_font('Helvetica', '', 8.5)
    pdf.multi_cell(0, 4.5, texto(f'{alcance}  |  Generado el {fecha}'), new_x='LMARGIN', new_y='NEXT')
    pdf.ln(2)


def _seccion(pdf: _Informe, titulo: str):
    if pdf.get_y() > pdf.h - 45:
        pdf.add_page()
    pdf.ln(3)
    pdf.set_fill_color(*CIAN)
    pdf.rect(15, pdf.get_y() + 1, 1.6, 6, style='F')
    pdf.set_x(19)
    pdf.set_font('Helvetica', 'B', 12)
    pdf.set_text_color(*AZUL)
    pdf.cell(0, 8, texto(titulo), new_x='LMARGIN', new_y='NEXT')
    pdf.ln(1)


def _subtitulo(pdf: _Informe, titulo: str):
    if pdf.get_y() > pdf.h - 35:
        pdf.add_page()
    pdf.ln(1)
    pdf.set_font('Helvetica', 'B', 10)
    pdf.set_text_color(*AZUL)
    pdf.cell(0, 6, texto(titulo), new_x='LMARGIN', new_y='NEXT')


def _parrafo(pdf: _Informe, t: str, tam: float = 9, color=AZUL):
    pdf.set_font('Helvetica', '', tam)
    pdf.set_text_color(*color)
    pdf.multi_cell(0, 4.6, texto(t), align='L', new_x='LMARGIN', new_y='NEXT')
    pdf.ln(1)


def _lista(pdf: _Informe, items: Iterable[str], tam: float = 9):
    pdf.set_font('Helvetica', '', tam)
    pdf.set_text_color(*AZUL)
    for it in items:
        pdf.set_x(17)
        pdf.cell(4, 4.6, '-')
        pdf.multi_cell(0, 4.6, texto(it), align='L', new_x='LMARGIN', new_y='NEXT')
    pdf.ln(1)


def _kpis(pdf: _Informe, items: Sequence[tuple]):
    """Fila de tarjetas (etiqueta, valor)."""
    n = len(items)
    if not n:
        return
    gap = 3
    ancho = (pdf.w - 30 - gap * (n - 1)) / n
    y = pdf.get_y()
    for i, (etq, val) in enumerate(items):
        x = 15 + i * (ancho + gap)
        pdf.set_fill_color(*FONDO)
        pdf.set_draw_color(*CIAN)
        pdf.rect(x, y, ancho, 17, style='DF')
        pdf.set_xy(x + 2.5, y + 2)
        pdf.set_font('Helvetica', '', 7.5)
        pdf.set_text_color(*GRIS)
        pdf.cell(ancho - 5, 4, texto(etq))
        pdf.set_xy(x + 2.5, y + 7)
        pdf.set_font('Helvetica', 'B', 14)
        pdf.set_text_color(*AZUL)
        pdf.cell(ancho - 5, 8, texto(val))
    pdf.set_y(y + 20)


def _barras(pdf: _Informe, filas: Sequence[tuple], ancho_etq: float = 70):
    """Barras horizontales 0–100 %: (etiqueta, valor, color, nota)."""
    ancho_max = pdf.w - 30 - ancho_etq - 42
    for etq, val, color, nota in filas:
        if pdf.get_y() > pdf.h - 25:
            pdf.add_page()
        y = pdf.get_y()
        pdf.set_font('Helvetica', '', 8.5)
        pdf.set_text_color(*AZUL)
        pdf.set_xy(15, y)
        pdf.cell(ancho_etq, 6, texto(etq))
        pdf.set_fill_color(236, 239, 242)
        pdf.rect(15 + ancho_etq, y + 1.2, ancho_max, 3.6, style='F')
        if val is not None:
            pdf.set_fill_color(*color)
            pdf.rect(15 + ancho_etq, y + 1.2, max(0.4, ancho_max * min(val, 100) / 100), 3.6, style='F')
        pdf.set_xy(15 + ancho_etq + ancho_max + 2, y)
        pdf.set_font('Helvetica', 'B', 8.5)
        pdf.cell(16, 6, pct(val))
        pdf.set_font('Helvetica', '', 7)
        pdf.set_text_color(*GRIS)
        pdf.cell(0, 6, texto(nota))
        pdf.set_y(y + 6.5)
    pdf.ln(1)


def _barras_apiladas(pdf: _Informe, filas: Sequence[tuple], ancho_etq: float = 62):
    """Una barra por criterio con los conteos de matrices por estado: (etiqueta, {estado: n})."""
    ancho_max = pdf.w - 30 - ancho_etq - 4
    for etq, conteo in filas:
        total = sum(conteo.values())
        if not total:
            continue
        y = pdf.get_y()
        pdf.set_font('Helvetica', '', 8.5)
        pdf.set_text_color(*AZUL)
        pdf.set_xy(15, y)
        pdf.cell(ancho_etq, 7, texto(etq))
        x = 15 + ancho_etq
        for estado in ('Cumple', 'Parcial', 'No cumple', 'Sin dato'):
            n = conteo.get(estado, 0)
            if not n:
                continue
            w = ancho_max * n / total
            pdf.set_fill_color(*COLOR_BARRA_ESTADO[estado])
            pdf.rect(x, y + 1, w, 5, style='F')
            if w > 5:
                pdf.set_xy(x, y + 1)
                pdf.set_font('Helvetica', 'B', 7.5)
                pdf.set_text_color(255, 255, 255)
                pdf.cell(w, 5, str(n), align='C')
            x += w
        pdf.set_y(y + 7.5)
    # leyenda
    pdf.set_font('Helvetica', '', 7.5)
    x = 15 + ancho_etq
    y = pdf.get_y() + 1
    for estado in ('Cumple', 'Parcial', 'No cumple', 'Sin dato'):
        pdf.set_fill_color(*COLOR_BARRA_ESTADO[estado])
        pdf.rect(x, y + 1, 3, 3, style='F')
        pdf.set_xy(x + 4, y)
        pdf.set_text_color(*AZUL)
        pdf.cell(22, 5, texto(estado))
        x += 26
    pdf.set_y(y + 7)


def _tabla(pdf: _Informe, columnas: Sequence[str], filas: Sequence[Sequence], anchos: Sequence[float],
           col_estado: Iterable[int] = (), tam: float = 7.5, alinear=None):
    """Tabla con encabezado azul; las columnas en `col_estado` se colorean según el estado."""
    if not filas:
        return
    col_estado = set(col_estado)
    pdf.set_font('Helvetica', '', tam)
    pdf.set_text_color(*AZUL)
    pdf.set_draw_color(205, 214, 222)
    pdf.set_fill_color(255, 255, 255)
    encabezado = FontFace(emphasis='BOLD', color=(255, 255, 255), fill_color=AZUL)
    with pdf.table(col_widths=tuple(anchos), headings_style=encabezado, line_height=1.25 * tam * 0.3528 + 1.2,
                   text_align=alinear or 'LEFT', padding=1, borders_layout='HORIZONTAL_LINES',
                   cell_fill_color=(246, 250, 252), cell_fill_mode='ROWS') as tabla:
        fila = tabla.row()
        for c in columnas:
            fila.cell(texto(c))
        for datos in filas:
            fila = tabla.row()
            for i, v in enumerate(datos):
                estilo = FontFace(fill_color=COLOR_ESTADO.get(str(v))) if i in col_estado and str(v) in COLOR_ESTADO else None
                fila.cell(texto(v), style=estilo)
    pdf.ln(2)


def _nota_metodo(pdf: _Informe, criterios: Sequence[tuple]):
    _seccion(pdf, 'Nota metodológica')
    _lista(pdf, [f'{v} {e}: {c}.' for v, e, c in criterios], tam=8)
    _parrafo(pdf, 'Estados: Cumple = la regla de la plantilla institucional se cumple en todos los casos; Parcial = en '
                  'algunos; No cumple = en ninguno; Sin dato = la matriz no tiene la información para evaluarla. No hay '
                  'puntaje compuesto ni pesos; la mediana del conjunto cargado solo sitúa a cada matriz. El nivel de '
                  'evidencia de los indicadores (N1 implementación a N5 efecto externo) y la exigencia de los RA se '
                  'describen sin calificarse, porque la plantilla no fija un criterio para ellos.', tam=8, color=GRIS)


# --- Recomendaciones -------------------------------------------------------------------------------------------

def recomendaciones_matriz(estados: Dict[str, str], fila: Dict, n_sin_perfil: int, n_ra_no_eval: int,
                           n_est_incompletas: int) -> List[str]:
    """Acciones concretas por cada criterio en Parcial o No cumple (y por la evidencia, si no hay N3–N4)."""
    recs = []
    if estados.get('V1') in ('Parcial', 'No cumple'):
        recs.append(f'V1 Perfil: revisar {n_sin_perfil} atributo(s) del perfil de egreso sin alineación; incorporarlos '
                    'en competencias, RA o asignaturas, o ajustar la redacción del perfil.')
    if estados.get('V2') in ('Parcial', 'No cumple'):
        recs.append(f"V2 Coherencia: diferenciar el verbo repetido entre competencias específicas "
                    f"({fila.get('Verbos repetidos') or 'ver Paso 2'}).")
    if estados.get('V3') in ('Parcial', 'No cumple'):
        recs.append(f'V3 Evaluabilidad: reformular {n_ra_no_eval} RA con verbo observable y finalidad de desempeño '
                    'o producto (detalle en el anexo).')
    if estados.get('V4') in ('Parcial', 'No cumple'):
        recs.append(f"V4 Trazabilidad: vincular {fila.get('RA sin estrategia', 0)} RA a una estrategia "
                    'mesocurricular con instrumento en el Paso 4.')
    if estados.get('V5') in ('Parcial', 'No cumple'):
        recs.append(f'V5 Indicadores: completar indicador e instrumento en {n_est_incompletas} estrategia(s) del Paso 4.')
    niv = fila.get('Indicadores por nivel') or {}
    if fila.get('Estrategias') and not (niv.get('N3', 0) + niv.get('N4', 0)):
        recs.append('Evidencia (recomendación, sin criterio en la plantilla): ninguna estrategia declara indicadores de '
                    'aprendizaje demostrado (N3) o transferencia (N4); conviene incluir al menos uno por estrategia.')
    return recs


# --- Informes --------------------------------------------------------------------------------------------------

def informe_general(d: Dict) -> bytes:
    """
    Informe del conjunto cargado.

    d: 'alcance', 'kpis' [(etiqueta, valor)], 'globales' (calcular_indicadores()['globales']), 'criterios'
       (indicadores_articulo.CRITERIOS), 'conteo_criterios' [(etiqueta, {estado: n})], 'lectura' [str],
       'prioridades' [dict con Matriz, Programa, V1..V5, No cumple, Parcial], 'alertas' [dict], 'tendencias'
       [dict], 'programas' [dict], 'errores' [dict].
    """
    fecha = d.get('fecha') or datetime.now().strftime('%Y-%m-%d %H:%M')
    pdf = _Informe('Informe general de análisis microcurricular')
    _portada(pdf, 'Informe general de análisis microcurricular', 'Resumen ejecutivo del conjunto cargado',
             d.get('alcance', ''), fecha)
    _kpis(pdf, d['kpis'])

    if d.get('lectura'):
        _seccion(pdf, 'Lectura rápida')
        _lista(pdf, d['lectura'])

    g = d.get('globales') or {}
    if g.get('matrices'):
        _seccion(pdf, 'Coherencia y trazabilidad curricular (V1-V5)')
        _parrafo(pdf, 'Valor del conjunto, cada variable sobre su propia base.', tam=8, color=GRIS)
        _barras(pdf, [
            ('V1 Perfil alineado (alguna capa)', g.get('V1'), CIAN, f"{g.get('atributos_perfil', 0)} atributos"),
            ('V2 Matrices sin verbo repetido', g.get('V2'), CIAN, f"{g.get('matrices', 0)} matrices"),
            ('V3 RA evaluables', g.get('V3'), CIAN, f"{g.get('ra_unicos', 0)} RA únicos"),
            ('V4 RA con estrategia meso', g.get('V4'), CIAN, f"{g.get('ra_unicos', 0)} RA únicos"),
            ('V5 Estrategias con evidencia N2+', g.get('V5'), CIAN, f"{g.get('estrategias', 0)} estrategias"),
        ])
        _subtitulo(pdf, 'Valoración por criterios: matrices por estado')
        _barras_apiladas(pdf, d.get('conteo_criterios', []))

    pri = d.get('prioridades') or []
    if pri:
        _seccion(pdf, 'Matrices que requieren atención')
        _parrafo(pdf, 'Ordenadas por número de criterios en «No cumple» y luego en «Parcial». Cada programa tiene su '
                      'informe individual con el detalle y las acciones sugeridas.', tam=8, color=GRIS)
        cols = ['Programa', 'Modalidad', 'Ciudad', 'V1', 'V2', 'V3', 'V4', 'V5', 'No cumple', 'Parcial']
        _tabla(pdf, cols, [[p.get(c, '') for c in cols] for p in pri], (50, 20, 20, 12, 12, 12, 12, 12, 11, 11),
               col_estado=range(3, 8), tam=6.8, alinear=('LEFT',) * 3 + ('CENTER',) * 7)

    if d.get('alertas') or d.get('tendencias'):
        _seccion(pdf, 'Hallazgos transversales')
        for a in d.get('alertas', []):
            _parrafo(pdf, f"[{a['Categoría']}] {a['Hallazgo']}. Recomendación: {a['Recomendación']}", tam=8.5)
        if d.get('tendencias'):
            _subtitulo(pdf, 'Presencia de las tendencias globales')
            _parrafo(pdf, 'No existe un mínimo institucional de cobertura: la tabla ordena las tendencias de menor a '
                          'mayor presencia para que el comité decida cuáles reforzar según el perfil de cada programa.',
                     tam=8, color=GRIS)
            cols = ['Tendencia', 'Asignaturas', '% de asignaturas', 'Programas', '% de programas']
            _tabla(pdf, cols, [[t['Tendencia'], t['Asignaturas'], pct(t['% de asignaturas']), t['Programas'],
                                pct(t['% de programas'])] for t in d['tendencias']], (80, 22, 26, 22, 26),
                   alinear=('LEFT',) + ('CENTER',) * 4)

    if d.get('programas'):
        _seccion(pdf, 'Perfil por programa')
        cols = ['Programa', 'Matrices', 'Asignaturas', 'Saber', 'SaberHacer', 'SaberSer', 'Tendencias']
        _tabla(pdf, cols, [[p['Programa'], p['Matrices'], p['Asignaturas'], pct(p['Saber']), pct(p['SaberHacer']),
                            pct(p['SaberSer']), p['Tendencias']] for p in d['programas']],
               (62, 16, 18, 18, 20, 18, 18), tam=7, alinear=('LEFT',) + ('CENTER',) * 6)

    if d.get('errores'):
        _seccion(pdf, 'Archivos no evaluados')
        _lista(pdf, [f"{e['archivo']}: {e['causa']}" for e in d['errores']], tam=8)

    _nota_metodo(pdf, d.get('criterios', []))
    return bytes(pdf.output())


def informe_programa(d: Dict) -> bytes:
    """
    Informe de un programa (todas sus matrices programa-sede).

    d: 'programa', 'alcance', 'kpis', 'matrices' [dict con matriz, sede, valoracion, recomendaciones,
       sin_alineacion, ra_no_evaluables, ra_sin_estrategia, estrategias_incompletas], 'tipo_saber' [dict],
       'tendencias_presentes' [str], 'tendencias_ausentes' [str], 'alertas' [str], 'criterios'.
    """
    fecha = d.get('fecha') or datetime.now().strftime('%Y-%m-%d %H:%M')
    pdf = _Informe(f"Informe del programa: {d['programa']}")
    _portada(pdf, d['programa'], 'Informe individual de análisis microcurricular', d.get('alcance', ''), fecha)
    _kpis(pdf, d['kpis'])

    resumen = []
    for m in d['matrices']:
        estados = [v for v in m['valoracion'] if v['Variable'] != '—']
        nc = [f"{v['Variable']} {v['Tramo']}" for v in estados if v['Estado'] == 'No cumple']
        pa = [f"{v['Variable']} {v['Tramo']}" for v in estados if v['Estado'] == 'Parcial']
        ok = [v['Variable'] for v in estados if v['Estado'] == 'Cumple']
        resumen.append(f"{m.get('etiqueta', m['matriz'])}: cumple {len(ok)} de {len(estados)} criterios"
                       + (f"; no cumple: {', '.join(nc)}" if nc else '')
                       + (f"; parcial: {', '.join(pa)}" if pa else '') + '.')
    if resumen:
        _seccion(pdf, 'Lectura rápida')
        _lista(pdf, resumen + [f'Alerta: {a}' for a in d.get('alertas', [])])

    for m in d['matrices']:
        _seccion(pdf, f"Valoración por criterios - {m.get('etiqueta', m['matriz'])}")
        filas = [[f"{v['Variable']} {v['Tramo']}" if v['Variable'] != '—' else v['Tramo'], v['Resultado'],
                  v['Estado'], v['Referencia (mediana)']] for v in m['valoracion']]
        _tabla(pdf, ['Criterio', 'Resultado', 'Estado', 'Mediana del conjunto'], filas, (50, 72, 20, 38),
               col_estado=[2], tam=7.3)
        if m.get('recomendaciones'):
            _subtitulo(pdf, 'Acciones sugeridas')
            _lista(pdf, m['recomendaciones'], tam=8.5)

    if d.get('tipo_saber'):
        _seccion(pdf, 'Distribución del tipo de saber')
        _tabla(pdf, ['Tipo de saber', 'Programa', 'Mediana del conjunto', 'Diferencia'],
               [[t['Tipo'], pct(t['Programa']), pct(t['Mediana']),
                 '-' if t['Programa'] is None or t['Mediana'] is None
                 else f"{t['Programa'] - t['Mediana']:+.1f} pp".replace('.', ',')] for t in d['tipo_saber']],
               (60, 40, 40, 40), alinear=('LEFT', 'CENTER', 'CENTER', 'CENTER'))

    if d.get('tendencias_presentes') is not None:
        _seccion(pdf, 'Tendencias globales')
        _parrafo(pdf, f"Presentes ({len(d['tendencias_presentes'])}): "
                      + (', '.join(d['tendencias_presentes']) or 'ninguna') + '.', tam=8.5)
        _parrafo(pdf, f"Sin presencia ({len(d['tendencias_ausentes'])}): "
                      + (', '.join(d['tendencias_ausentes']) or 'ninguna') + '.', tam=8.5)

    anexos = [m for m in d['matrices'] if m.get('sin_alineacion') or m.get('ra_no_evaluables')
              or m.get('ra_sin_estrategia') or m.get('estrategias_incompletas')]
    if anexos:
        _seccion(pdf, 'Anexo: elementos a revisar')
        for m in anexos:
            _subtitulo(pdf, m.get('etiqueta', m['matriz']))
            if m.get('sin_alineacion'):
                _parrafo(pdf, f"Atributos del perfil sin alineación en ninguna capa ({len(m['sin_alineacion'])})", tam=8.5)
                _tabla(pdf, ['Perfil', 'Componente', 'Atributo'], m['sin_alineacion'], (28, 32, 120), tam=7)
            if m.get('ra_no_evaluables'):
                _parrafo(pdf, f"RA no evaluables ({len(m['ra_no_evaluables'])})", tam=8.5)
                _tabla(pdf, ['Resultado de aprendizaje', 'Motivo'], m['ra_no_evaluables'], (130, 50), tam=7)
            if m.get('ra_sin_estrategia'):
                _parrafo(pdf, f"RA sin estrategia mesocurricular con instrumento ({len(m['ra_sin_estrategia'])})",
                         tam=8.5)
                _tabla(pdf, ['Resultado de aprendizaje'], [[r] for r in m['ra_sin_estrategia']], (180,), tam=7)
            if m.get('estrategias_incompletas'):
                _parrafo(pdf, f"Estrategias del Paso 4 sin indicador o sin instrumento ({len(m['estrategias_incompletas'])})",
                         tam=8.5)
                _tabla(pdf, ['Estrategia', 'Falta'], m['estrategias_incompletas'], (140, 40), tam=7)

    _nota_metodo(pdf, d.get('criterios', []))
    return bytes(pdf.output())
