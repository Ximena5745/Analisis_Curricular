"""
Figura 1 (Resultados): perfil de las variables curriculares V1–V5 con valores auditados.

Valores (decisiones D13–D17):
  V1 100 % (estructural), V2 90 %, V3 100 % (estructural), V4 87,1 %, V5 0,8 %.
V1 y V3 se marcan como condiciones estructurales del instrumento (punto hueco, etiqueta gris).

Uso: python auditoria/scripts/figura_v1_v5.py
Salida: auditoria/figuras/R0_figura1_perfil_variables.png
"""
import os

import plotly.graph_objects as go

NAVY, AZUL, DORADO, GRIS = '#0F385A', '#1FB2DE', '#FBAF17', '#8A94A0'
VARS = [('V1', 'Correspondencia<br>competencia–RA', 100.0, True),
        ('V2', 'Coherencia<br>horizontal', 90.0, False),
        ('V3', 'Evaluabilidad', 100.0, True),
        ('V4', 'Trazabilidad', 87.0, False),
        ('V5', 'Evidencia directa<br>del logro', 0.8, False)]
eje = [f"<b>{v}</b><br>{n}" + ('<br><i>(estructural)</i>' if e else '') for v, n, _, e in VARS]
val = [x for _, _, x, _ in VARS]

fig = go.Figure()
fig.add_trace(go.Scatterpolar(r=val + [val[0]], theta=eje + [eje[0]], mode='lines', fill='toself',
                              fillcolor='rgba(31,178,222,0.18)', line=dict(color=NAVY, width=2.5), showlegend=False,
                              hoverinfo='skip'))
for (v, n, x, e), t in zip(VARS, eje):
    fig.add_trace(go.Scatterpolar(
        r=[x], theta=[t], mode='markers+text', showlegend=False,
        marker=dict(size=13, color='white' if e else NAVY, line=dict(color=GRIS if e else NAVY, width=2.5)),
        text=[f'{x:.1f} %'.replace('.', ',')], textposition='top center' if x > 50 else 'middle right',
        textfont=dict(size=13, color=GRIS if e else NAVY)))
fig.update_layout(
    font=dict(family='Arial', size=13, color=NAVY), paper_bgcolor='white', width=950, height=860,
    margin=dict(t=120, b=90, l=130, r=130), separators=',.',
    polar=dict(bgcolor='white',
               radialaxis=dict(range=[0, 105], tickvals=[20, 40, 60, 80, 100], ticksuffix=' %', gridcolor='#E6EBF0',
                               tickfont=dict(size=10, color=GRIS), angle=54, tickangle=54),
               angularaxis=dict(gridcolor='#E6EBF0', linecolor='#C8CED6', direction='clockwise', rotation=90)))
os.makedirs('auditoria/figuras', exist_ok=True)
fig.write_image('auditoria/figuras/R0_figura1_perfil_variables.png', scale=2)
print('OK')
