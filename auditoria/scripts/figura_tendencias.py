"""
Figura 6 (R8.2): integración de las tendencias del sector empresarial y educativo en los programas (D30).

Panel izquierdo: los 39 programas repartidos en tres grupos por tendencia —la integran en asignaturas propias, la tienen
solo por el núcleo común institucional o no la tienen—, para ver dónde no se integra. Panel derecho: profundidad
(% de las 1.616 asignaturas sin electivas), con escala propia. T15 (formación transversal) se informa aparte, en el texto.

Lista oficial depurada: config_tendencias.json (D21, D30). Datos: auditoria/evidencia_tendencias_r82.json.
Uso: python auditoria/scripts/figura_tendencias.py
Salida: auditoria/figuras/R8_figura6_tendencias.png
"""
import json
import os

import plotly.graph_objects as go
from plotly.subplots import make_subplots

NAVY, AZUL, GRIS, DORADO = '#0F385A', '#1FB2DE', '#E3E8ED', '#FBAF17'
ev = json.load(open('auditoria/evidencia_tendencias_r82.json', encoding='utf-8'))
N_ASIG, N_PROG = ev['asignaturas'], ev['programas']
items = sorted(((k, v) for k, v in ev['por_tendencia'].items() if k != 'T15'),
               key=lambda x: (x[1]['programas_propia'], x[1]['programas']), reverse=True)  # menor integración arriba
nom = [v['nombre'] for _, v in items]
propia = [v['programas_propia'] for _, v in items]
comun = [v['programas'] - v['programas_propia'] for _, v in items]
sin = [N_PROG - v['programas'] for _, v in items]
pro = [v['pct'] for _, v in items]
pc = lambda n: 100 * n / N_PROG  # noqa: E731
f = lambda v: f'{v:.1f} %'.replace('.', ',')  # noqa: E731

fig = make_subplots(rows=1, cols=2, shared_yaxes=True, column_widths=[0.7, 0.3], horizontal_spacing=0.06,
                    subplot_titles=[f'Programas según cómo integran la tendencia (n = {N_PROG})',
                                    f'Profundidad: % de asignaturas (n = {N_ASIG:,})'.replace(',', '.')])
for vals, nombre, color, txt in ((propia, 'La integra en asignaturas propias', NAVY, 'white'),
                                 (comun, 'Solo por el núcleo común institucional', AZUL, 'white'),
                                 (sin, 'No la tiene', GRIS, NAVY)):
    fig.add_trace(go.Bar(y=nom, x=[pc(v) for v in vals], orientation='h', name=nombre, marker_color=color,
                         text=[str(v) if v else '' for v in vals], textposition='inside', insidetextanchor='middle',
                         textfont=dict(color=txt, size=11), customdata=vals,
                         hovertemplate='%{y}: %{customdata} programas<extra></extra>'), 1, 1)
fig.add_trace(go.Bar(y=nom, x=pro, orientation='h', marker_color=DORADO, showlegend=False,
                     text=[f(v) for v in pro], textposition='outside'), 1, 2)
fig.update_layout(font=dict(family='Arial', size=12, color=NAVY), paper_bgcolor='white', plot_bgcolor='white',
                  barmode='stack', bargap=0.28, width=1200, height=700, margin=dict(t=50, b=80, l=330, r=40),
                  separators=',.', legend=dict(orientation='h', x=0.35, xanchor='center', y=-0.08, traceorder='normal'))
fig.update_xaxes(range=[0, 100], ticksuffix=' %', gridcolor='#FFFFFF', row=1, col=1)
fig.update_xaxes(range=[0, 20], ticksuffix=' %', gridcolor='#E6EBF0', row=1, col=2)
for a in fig.layout.annotations:
    a.update(font=dict(size=13, color=NAVY))
os.makedirs('auditoria/figuras', exist_ok=True)
fig.write_image('auditoria/figuras/R8_figura6_tendencias.png', scale=2)
print('OK', [(n, p, c, s, d) for n, p, c, s, d in zip(nom, propia, comun, sin, pro)])
