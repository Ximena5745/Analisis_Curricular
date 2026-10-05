"""
Figura 1 (Resultados): ruta de alineación curricular, de la competencia a la evidencia directa.

Cada tramo se expresa sobre su propia base (competencias, RA únicos o estrategias), con los
valores auditados (D13–D17). Reemplaza el radar de variables V1–V5.

Uso: python auditoria/scripts/figura_cadena.py
Salida: auditoria/figuras/R0_figura1_cadena_evidencia.png
"""
import os

import plotly.graph_objects as go

NAVY, AZUL, DORADO, MAGENTA, GRIS = '#0F385A', '#1FB2DE', '#FBAF17', '#EC0677', '#8A94A0'
ESLABONES = [  # (etiqueta, numerador, base, nombre de la base, variable, color)
    ('Atributo del perfil con alineación en alguna capa', 2476, 2574, 'atributos', 'V1', AZUL),
    ('RA vinculado a una competencia', 338, 338, 'RA únicos', '—', GRIS),
    ('RA evaluable', 338, 338, 'RA únicos', 'V3', GRIS),
    ('Matriz sin verbo repetido en competencias específicas', 45, 50, 'matrices', 'V2', AZUL),
    ('RA con estrategia mesocurricular', 294, 338, 'RA únicos', 'V4', AZUL),
    ('Estrategia con indicador e instrumento', 391, 391, 'estrategias', '—', GRIS),
]
# V5 (nivel de evidencia de los indicadores) no es un tramo de la ruta: la plantilla no lo exige (D26); se informa en R5.
y = [f'<b>{v}</b>  {e}' if v != '—' else e for e, _, _, _, v, _ in ESLABONES][::-1]
x = [100 * n / b for _, n, b, _, _, _ in ESLABONES][::-1]
txt = [f'{100 * n / b:.1f} %'.replace('.', ',') + f'  ({n:,}/{b:,} {nb})'.replace(',', '.')
       for _, n, b, nb, _, _ in ESLABONES][::-1]
fig = go.Figure(go.Bar(x=x, y=y, orientation='h', marker_color=[c for *_, c in ESLABONES][::-1],
                       text=txt, textposition='outside', textfont=dict(size=13, color=NAVY), cliponaxis=False))
fig.add_annotation(x=100, y=-0.95, xref='x', yref='y', showarrow=False, xanchor='right',
                   text='Gris: condición del instrumento · Azul: articulación',
                   font=dict(size=11, color=GRIS))
fig.update_layout(font=dict(family='Arial', size=14, color=NAVY), paper_bgcolor='white', plot_bgcolor='white',
                  width=1100, height=520, margin=dict(t=20, b=60, l=420, r=230), bargap=0.35, separators=',.',
                  xaxis=dict(range=[0, 100], ticksuffix=' %', gridcolor='#E6EBF0', zeroline=False),
                  yaxis=dict(tickfont=dict(size=13)))
os.makedirs('auditoria/figuras', exist_ok=True)
fig.write_image('auditoria/figuras/R0_figura1_cadena_evidencia.png', scale=2)
print('OK')
