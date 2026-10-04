"""
Figura propuesta para R6: distribución por matriz de V1–V5 (valores auditados D13–D17).

Muestra por qué casi no se estiman asociaciones: V3 constante, V2 binaria, V5 casi nula;
solo V1 y V4 varían. Cada punto es una matriz (n = 50); los puntos superpuestos se dispersan.

Uso: python auditoria/scripts/figura_r6.py
Salida: auditoria/figuras/R6_figura_distribucion_variables.png
"""
import json
import os

import numpy as np
import pandas as pd
import plotly.graph_objects as go

NAVY, AZUL, DORADO, MAGENTA, GRIS = '#0F385A', '#1FB2DE', '#FBAF17', '#EC0677', '#8A94A0'
v4 = pd.DataFrame(json.load(open('auditoria/evidencia_v4_alternativas.json', encoding='utf-8'))['por_matriz'])[['matriz', 'V4']]
v5 = pd.DataFrame(json.load(open('auditoria/evidencia_v5.json', encoding='utf-8'))['por_matriz'])[['matriz', 'V5_directa']]
d = v4.merge(v5, on='matriz')
REP = {'Derecho_HMED', 'Derecho_VNAL', 'Ing.Telecomunicaciones_PBOG', 'IngSistemas_PBOG', 'IngSistemas_PMED'}
d['V2'] = d['matriz'].map(lambda m: 0.0 if m in REP else 100.0)
v1 = pd.read_excel('auditoria/Asociacion_perfil_50_matrices.xlsx', sheet_name='Resumen')
d = d.merge(v1.rename(columns={'Matriz': 'matriz', '% tres capas': 'V1'})[['matriz', 'V1']], on='matriz')
d['V3'] = 100.0
d = d.rename(columns={'V5_directa': 'V5'})

FILAS = [('V1', 'V1 Correspondencia del perfil', AZUL), ('V2', 'V2 Coherencia horizontal', AZUL),
         ('V3', 'V3 Evaluabilidad', GRIS), ('V4', 'V4 Trazabilidad', AZUL), ('V5', 'V5 Evidencia directa del logro', MAGENTA)]
rng = np.random.default_rng(42)
fig = go.Figure()
for i, (v, nombre, color) in enumerate(FILAS):
    y = len(FILAS) - 1 - i
    fig.add_trace(go.Scatter(x=d[v], y=y + rng.uniform(-0.22, 0.22, len(d)), mode='markers', showlegend=False,
                             marker=dict(size=9, color=color, opacity=0.75, line=dict(color=NAVY, width=0.6)),
                             text=d['matriz'], hovertemplate='%{text}: %{x:.1f} %<extra></extra>'))
    nota = {'V1': f"{d.V1.min():.1f} %–{d.V1.max():.1f} %".replace('.', ','), 'V3': 'constante', 'V2': '45 en 100 %, 5 en 0 %',
            'V5': f"{(d.V5 > 0).sum()} matrices > 0 %", 'V4': f"{d.V4.min():.1f} %–{d.V4.max():.1f} %".replace('.', ',')}[v]
    fig.add_annotation(x=1.02, xref='paper', y=y, text=nota, showarrow=False, xanchor='left', font=dict(size=12, color=GRIS))
fig.update_layout(font=dict(family='Arial', size=13, color=NAVY), paper_bgcolor='white', plot_bgcolor='white',
                  width=1100, height=480, margin=dict(t=20, b=60, l=260, r=190), separators=',.',
                  xaxis=dict(range=[-4, 103], ticksuffix=' %', gridcolor='#E6EBF0', zeroline=False, title='Valor por matriz'),
                  yaxis=dict(tickvals=list(range(len(FILAS))), ticktext=[n for _, n, _ in FILAS][::-1], range=[-0.6, len(FILAS) - 0.4],
                             showgrid=False))
os.makedirs('auditoria/figuras', exist_ok=True)
fig.write_image('auditoria/figuras/R6_figura_distribucion_variables.png', scale=2)
print('OK')
