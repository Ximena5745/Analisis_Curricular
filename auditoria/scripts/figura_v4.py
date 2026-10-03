"""
Figura 4 (R4, V4): dónde están los RA sin estrategia mesocurricular.

Complementa la Tabla 9 (tasas por sede y clase) con la composición absoluta de la brecha:
los 44 RA únicos sin estrategia, por sede y clase (RA genérico institucional / RA de programa),
y la lista de matrices con RA de programa sin estrategia.

Datos: auditoria/evidencia_v4_alternativas.json (v4_alternativas.py; D16).
Uso: python auditoria/scripts/figura_v4.py
Salida: auditoria/figuras/R4_figura4_trazabilidad.png
"""
import json
import os
from collections import Counter

import plotly.graph_objects as go
from plotly.subplots import make_subplots

NAVY, AZUL, DORADO, GRIS = '#0F385A', '#1FB2DE', '#FBAF17', '#8A94A0'
SEDES = ['VNAL', 'PBOG', 'PMED', 'HMED', 'HBOG']

ev = json.load(open('auditoria/evidencia_v4_alternativas.json', encoding='utf-8'))
dif = ev['diferenciada']
sin = {s: {k: dif[s][k]['ra'] - dif[s][k]['con_estrategia'] for k in ('generico', 'programa')} for s in SEDES}
prog = Counter(x['matriz'] for x in ev['mutuo']['sin_estrategia_programa_lista'])

fig = make_subplots(rows=1, cols=2, column_widths=[0.55, 0.45], horizontal_spacing=0.22,
                    subplot_titles=['RA sin estrategia por sede y clase (n = 44)', 'RA de programa sin estrategia, por matriz (n = 6)'])
for clave, nombre, color in (('generico', 'RA genérico institucional', DORADO), ('programa', 'RA de programa', NAVY)):
    v = [sin[s][clave] for s in SEDES]
    fig.add_trace(go.Bar(x=SEDES, y=v, name=nombre, marker_color=color, text=[x or '' for x in v],
                         textposition='inside', textfont=dict(color='white' if color == NAVY else NAVY)), 1, 1)
mats = sorted(prog.items(), key=lambda x: (x[1], x[0]))
NOMBRE = {'MercadeoyPublicidad': 'Mercadeo y Publicidad', 'DisenoGrafico': 'Diseño Gráfico', 'DisenoIndustrial': 'Diseño Industrial'}
fig.add_trace(go.Bar(y=[f"{NOMBRE.get(m.rsplit('_', 1)[0], m.rsplit('_', 1)[0])} ({m.rsplit('_', 1)[1]})" for m, _ in mats], x=[n for _, n in mats], orientation='h',
                     marker_color=NAVY, showlegend=False, text=[n for _, n in mats], textposition='outside'), 1, 2)
fig.update_layout(font=dict(family='Arial', size=13, color=NAVY), paper_bgcolor='white', plot_bgcolor='white',
                  barmode='stack', width=1100, height=520, margin=dict(t=50, b=80, l=60, r=40), separators=',.',
                  legend=dict(orientation='h', x=0.27, xanchor='center', y=-0.14))
fig.update_yaxes(title_text='RA únicos', gridcolor='#E6EBF0', row=1, col=1)
fig.update_xaxes(range=[0, 2.6], dtick=1, gridcolor='#E6EBF0', title_text='RA únicos', row=1, col=2)
for a in fig.layout.annotations:
    a.font = dict(size=14, color=NAVY)
os.makedirs('auditoria/figuras', exist_ok=True)
fig.write_image('auditoria/figuras/R4_figura4_trazabilidad.png', scale=2)
print('OK', sin, dict(prog))
