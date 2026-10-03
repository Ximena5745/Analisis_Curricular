"""
Figura 6 (R8.2): tendencias del sector empresarial y educativo — amplitud frente a profundidad.

Lista oficial: config_tendencias.json (15 tendencias; D21). Regla: término en el nombre de la asignatura
o ≥ 2 puntos en el contenido (núcleos + indicadores). Base: 1.616 asignaturas sin electivas, 39 programas.

Datos: auditoria/evidencia_tendencias_integradas_15.json (tendencias_integradas.py).
Uso: python auditoria/scripts/figura_tendencias.py
Salida: auditoria/figuras/R8_figura6_tendencias.png
"""
import json
import os

import plotly.graph_objects as go

NAVY, DORADO = '#0F385A', '#FBAF17'
ev = json.load(open('auditoria/evidencia_tendencias_integradas_15.json', encoding='utf-8'))
N_ASIG, N_PROG = ev['asignaturas'], 39
items = sorted(ev['por_tendencia'].items(), key=lambda x: x[1]['programas'])
nom = [k.split(' ', 1)[1] for k, _ in items]
amp = [100 * v['programas'] / N_PROG for _, v in items]
pro = [v['pct'] for _, v in items]
f = lambda v: f'{v:.1f} %'.replace('.', ',')
fig = go.Figure()
fig.add_trace(go.Bar(y=nom, x=amp, orientation='h', name=f'Amplitud: % de programas (n = {N_PROG})', marker_color=NAVY,
                     text=[f(v) for v in amp], textposition='outside'))
fig.add_trace(go.Bar(y=nom, x=pro, orientation='h', name=f'Profundidad: % de asignaturas (n = {N_ASIG:,})'.replace(',', '.'),
                     marker_color=DORADO, text=[f(v) for v in pro], textposition='outside'))
fig.update_layout(font=dict(family='Arial', size=12, color=NAVY), paper_bgcolor='white', plot_bgcolor='white',
                  barmode='group', bargap=0.22, width=1100, height=820, margin=dict(t=20, b=70, l=360, r=60),
                  separators=',.', xaxis=dict(range=[0, 110], ticksuffix=' %', gridcolor='#E6EBF0'),
                  legend=dict(orientation='h', x=0.4, xanchor='center', y=-0.07))
os.makedirs('auditoria/figuras', exist_ok=True)
fig.write_image('auditoria/figuras/R8_figura6_tendencias.png', scale=2)
print('OK', [(n, round(a, 1), p) for n, a, p in zip(nom, amp, pro)])
