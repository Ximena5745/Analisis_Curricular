"""
Genera el Word consolidado de Resultados (versiones finales auditadas) con sus
figuras en plotly, usando la paleta institucional del Politécnico Grancolombiano
(#0F385A navy, #1FB2DE azul, #42F2F2 cyan, #FBAF17 dorado, #EC0677 magenta).

Texto: auditoria/scripts/textos_articulo.py (SECCIONES_RESULTADOS: solo secciones cerradas).
Se regenera cada vez que se cierra una sección.
Datos: archivos crudos (solo lectura).

Uso: python auditoria/scripts/generar_word_resultados.py
Salida: auditoria/Resultados_consolidado.docx y auditoria/figuras/*.png
"""
import glob
import os
import re
import sys
import unicodedata
import warnings
from collections import Counter, defaultdict

import openpyxl
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Cm, Pt, RGBColor

warnings.filterwarnings('ignore')
sys.path.insert(0, 'auditoria/scripts')
import textos_articulo as TXT  # noqa: E402

NAVY, AZUL, CYAN, DORADO, MAGENTA = '#0F385A', '#1FB2DE', '#42F2F2', '#FBAF17', '#EC0677'
FUENTE = 'Arial'
OUT = 'auditoria/figuras'
os.makedirs(OUT, exist_ok=True)


def norm(t):
    t = unicodedata.normalize('NFKD', str(t)).encode('ascii', 'ignore').decode('ascii').lower()
    return re.sub(r'\s+', ' ', re.sub(r'[^a-z0-9 ]', ' ', t)).strip()


def hoja(wb, pref):
    return next(wb[n] for n in wb.sheetnames if n.strip().startswith(pref) and 'backup' not in n.lower())


def tipo_saber(t):
    t = norm(t).replace(' ', '')
    return 'SaberSer' if 'ser' in t else 'SaberHacer' if 'hacer' in t else 'Saber' if 'saber' in t else None


# ---------------------------------------------------------------- datos
verbos = defaultdict(Counter)            # verbo -> {Específica, Genérica}
reg_tipo, unico_tipo = Counter(), Counter()
for f in sorted(glob.glob('data/raw/FORMATOS RA CICLO UNO RC/*.xlsx')):
    wb = openpyxl.load_workbook(f, read_only=True, data_only=True)
    for r in hoja(wb, 'Paso 2').iter_rows(min_row=3, values_only=True):
        if len(r) > 6 and r[5] not in (None, '') and not str(r[5]).strip().startswith('['):
            if norm(r[5]).startswith('redaccion') or norm(r[1] or '') == 'verbo':
                continue
            tc = 'Genérica' if norm(r[6] or '').startswith('gen') else 'Específica'
            verbos[str(r[1] or '').strip().capitalize()][tc] += 1
    vistos = {}
    for r in hoja(wb, 'Paso 3').iter_rows(min_row=3, values_only=True):
        if len(r) > 8 and r[8] not in (None, '') and r[2]:
            tp = tipo_saber(r[2])
            if tp:
                reg_tipo[tp] += 1
                vistos.setdefault(str(r[8]).strip().lower(), tp)  # clave D4
    unico_tipo.update(vistos.values())
    wb.close()

ORDEN = ['Saber', 'SaberHacer', 'SaberSer']
ETIQ = {'Saber': 'Saber<br>(conceptual)', 'SaberHacer': 'SaberHacer<br>(procedimental)', 'SaberSer': 'SaberSer<br>(actitudinal)'}
COL = {'Saber': NAVY, 'SaberHacer': AZUL, 'SaberSer': DORADO}
layout_base = dict(font=dict(family=FUENTE, size=14, color=NAVY), paper_bgcolor='white', plot_bgcolor='white', separators=',.')

# ---------------------------------------------------------------- Figura 2
fig = make_subplots(rows=1, cols=2, specs=[[{'type': 'domain'}, {'type': 'domain'}]],
                    subplot_titles=['Registros de RA (RA × competencia)', 'RA únicos'])
for i, (datos, centro) in enumerate([(reg_tipo, 'registros'), (unico_tipo, 'RA únicos')], 1):
    n = sum(datos.values())
    fig.add_trace(go.Pie(labels=[ETIQ[t] for t in ORDEN], values=[datos[t] for t in ORDEN], hole=0.55, sort=False,
                         marker=dict(colors=[COL[t] for t in ORDEN], line=dict(color='white', width=2)),
                         text=[f'{100 * datos[t] / n:.1f} %'.replace('.', ',') + f'<br>({datos[t]})' for t in ORDEN],
                         textinfo='text', textfont=dict(size=14, color='white'),
                         hovertemplate='%{label}: %{value}<extra></extra>', showlegend=(i == 1),
                         title=dict(text=f'<b>{n}</b><br><span style="font-size:13px">{centro}</span>',
                                    position='middle center', font=dict(size=24, color=NAVY))), 1, i)
fig.update_layout(**layout_base, width=1100, height=520, margin=dict(t=50, b=60, l=20, r=20),
                  legend=dict(orientation='h', x=0.5, xanchor='center', y=-0.05))
fig.layout.annotations[0].update(font=dict(size=15, color=NAVY))
fig.layout.annotations[1].update(font=dict(size=15, color=NAVY))
F2 = f'{OUT}/R2_figura2_tipo_saber.png'
fig.write_image(F2, scale=2)

# ---------------------------------------------------------------- Figura 3
top = sorted(verbos, key=lambda v: -sum(verbos[v].values()))[:15][::-1]
fig = go.Figure()
fig.add_trace(go.Bar(y=top, x=[verbos[v]['Específica'] for v in top], orientation='h', name='Competencia específica',
                     marker_color=NAVY, text=[verbos[v]['Específica'] or '' for v in top], textposition='inside',
                     insidetextanchor='middle', textfont=dict(color='white')))
fig.add_trace(go.Bar(y=top, x=[verbos[v]['Genérica'] for v in top], orientation='h', name='Competencia genérica institucional',
                     marker_color=AZUL, text=[verbos[v]['Genérica'] or '' for v in top], textposition='inside',
                     insidetextanchor='middle', textfont=dict(color='white')))
fig.update_layout(**layout_base, barmode='stack', width=1100, height=600, margin=dict(t=30, b=60, l=130, r=30),
                  xaxis=dict(title='Número de competencias', gridcolor='#E6EBF0', zeroline=False),
                  legend=dict(orientation='h', x=0.5, xanchor='center', y=-0.12))
F3 = f'{OUT}/R2_figura3_verbos.png'
fig.write_image(F3, scale=2)

# ---------------------------------------------------------------- Word (manuscrito APA 7, Scopus Q1)
from docx.enum.text import WD_LINE_SPACING  # noqa: E402

LETRA = 'Times New Roman'
doc = Document()
st = doc.styles['Normal']
st.font.name, st.font.size = LETRA, Pt(12)
st.paragraph_format.line_spacing = 2.0
st.paragraph_format.space_after = Pt(0)
for s in doc.sections:
    s.left_margin = s.right_margin = s.top_margin = s.bottom_margin = Cm(2.54)


def parrafo(texto, sangria=True, tam=None, cursiva=False, alinear=None, interlineado=None):
    p = doc.add_paragraph()
    if sangria:
        p.paragraph_format.first_line_indent = Cm(1.27)
    if alinear is not None:
        p.alignment = alinear
    if interlineado:
        p.paragraph_format.line_spacing = interlineado
    r = p.add_run(texto)
    r.font.name, r.italic = LETRA, cursiva
    if tam:
        r.font.size = Pt(tam)
    return p


def titulo(texto, nivel=2):
    # APA 7: nivel 1 centrado en negrita; nivel 2 a la izquierda en negrita
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER if nivel == 1 else WD_ALIGN_PARAGRAPH.LEFT
    r = p.add_run(texto)
    r.bold, r.font.name = True, LETRA


def rotulo(texto):
    # APA 7: "Tabla N" en negrita y, debajo, el título en cursiva
    numero, nombre = texto.split('. ', 1)
    p = doc.add_paragraph()
    r = p.add_run(numero)
    r.bold, r.font.name = True, LETRA
    p = doc.add_paragraph()
    r = p.add_run(nombre)
    r.italic, r.font.name = True, LETRA


def nota(texto):
    p = doc.add_paragraph()
    p.paragraph_format.line_spacing = 1.0
    cuerpo = texto[len('Nota.'):].strip() if texto.startswith('Nota.') else texto
    r = p.add_run('Nota. ')
    r.italic, r.font.name, r.font.size = True, LETRA, Pt(10)
    r = p.add_run(cuerpo)
    r.font.name, r.font.size = LETRA, Pt(10)


def figura(ruta, texto, texto_nota):
    rotulo(texto)
    doc.add_picture(ruta, width=Cm(16))
    doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
    nota(texto_nota)


def tabla(titulo_t, cab, filas, control=False):
    if not control:
        rotulo(titulo_t)
    t = doc.add_table(rows=1, cols=len(cab))
    t.style = 'Table Grid'
    for i, c in enumerate(cab):
        run = t.rows[0].cells[i].paragraphs[0].add_run(c)
        run.bold, run.font.name, run.font.size = True, LETRA, Pt(10)
    for fila in filas:
        celdas = t.add_row().cells
        for i, v in enumerate(fila):
            run = celdas[i].paragraphs[0].add_run(str(v))
            run.font.name, run.font.size = LETRA, Pt(10)
            if fila[0] == 'Total':
                run.bold = True
    for fila in t.rows:
        for c in fila.cells:
            c.paragraphs[0].paragraph_format.line_spacing = 1.0


FIGURAS_EN_LINEA = {
    'Figura 6. Temas de agenda global: amplitud y profundidad': [('auditoria/figuras/R8_figura6_tendencias.png', 'Figura 6. Tendencias del sector empresarial y educativo: amplitud y profundidad',
            'Amplitud: programas con al menos una asignatura que menciona el tema (n = 39). Profundidad: asignaturas que lo mencionan '
            '(n = 1.616, sin electivas). Regla de asignación en la nota del texto.')],
}
FIGURAS = {
    'R6': [('auditoria/figuras/R6_figura_distribucion_variables.png', 'Figura 5. Distribución de las variables V1–V5 por matriz',
            'Cada punto es una matriz (n = 50); los puntos superpuestos se dispersan verticalmente. Valores auditados (D13–D17).')],
    'Intro': [('auditoria/figuras/R0_figura1_cadena_evidencia.png', 'Figura 1. Cadena de evidencia del logro en las matrices',
               'Cada eslabón se calcula sobre su propia base (RA únicos, matrices o estrategias). Gris: condición impuesta por el '
               'instrumento; azul: articulación; magenta: evidencia directa del logro. Fuente: Pasos 2 a 4 de las 50 matrices.')],
    'R2': [(F3, 'Figura 2. Verbos más frecuentes en las competencias, por tipo de competencia',
            'N = 222 competencias. La competencia genérica institucional es «Analizar fenómenos contemporáneos». '
            'Fuente: Paso 2 de las 50 matrices.'),
           (F2, 'Figura 3. Distribución de los resultados de aprendizaje por tipo de saber',
            f'Registros (N = {sum(reg_tipo.values())}): RA asociado a una competencia. RA únicos (N = {sum(unico_tipo.values())}): '
            'contados una vez por matriz. Fuente: Paso 3 de las 50 matrices.')],
    'R4': [('auditoria/figuras/R4_figura4_trazabilidad.png', 'Figura 4. RA sin estrategia mesocurricular por sede, clase y matriz',
            'Izquierda: los 44 RA únicos sin estrategia, según sean el RA de la competencia genérica institucional o RA de programa. '
            'Derecha: matrices con RA de programa sin estrategia. Fuente: Pasos 3 y 4 de las 50 matrices.')],
}
ENCABEZADO = re.compile(r'^((?:3\. Resultados)|(?:R\d+\. [^.]*?\((?:V[^)]*|modelos analíticos)\)))\.\s+(.*)$', re.S)

for clave, bloques, estado in TXT.SECCIONES_RESULTADOS:
    for b in bloques:
        if b[0] == 'p':
            m = ENCABEZADO.match(b[1])
            if m:
                titulo(m.group(1), 1 if m.group(1).startswith('3.') else 2)
                parrafo(m.group(2))
            else:
                parrafo(b[1])
        elif b[0] == 'h':
            titulo(b[1], 3)
        elif b[0] == 'fig':
            for fig in FIGURAS_EN_LINEA[b[1]]:
                figura(*fig)
        elif b[0] == 't':
            tabla(b[1], b[2], b[3])
        elif b[0] == 'n' and (b[1].startswith('Nota.') or b[1].startswith('¹')):
            nota(b[1])
    for fig in FIGURAS.get(clave, []):
        figura(*fig)

# Control de avance (no forma parte del manuscrito)
doc.add_page_break()
p = doc.add_paragraph()
r = p.add_run('Control de avance (no forma parte del manuscrito)')
r.bold, r.font.name, r.font.size = True, LETRA, Pt(10)
tabla('', ['Sección', 'Estado'], [(s[0], s[2]) for s in TXT.SECCIONES_RESULTADOS + TXT.RESULTADOS_PENDIENTES], control=True)
doc.save('auditoria/Resultados_consolidado.docx')
print('OK auditoria/Resultados_consolidado.docx', [s[0] for s in TXT.SECCIONES_RESULTADOS])
