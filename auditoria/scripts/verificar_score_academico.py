"""
Recálculo del score académico (Discusión, riesgo latente) sobre el corpus actual de núcleos (D7).

  1. Distribución del score con la fórmula vigente (src/nucleos_cleaner.calcular_score_academico):
     media, mediana y % de núcleos bajo el umbral inactivo 0,5.
  2. Contraste disciplinar por campo amplio CINE-F 2013 (hoja CINE-F_programas de
     auditoria/Clasificacion_estandar_oferta.xlsx; propuesta pendiente de validación):
     Kruskal-Wallis con ε² = (H − k + 1)/(n − k), a nivel de núcleo y de programa (mediana por programa).

Uso: python auditoria/scripts/verificar_score_academico.py
Salida: auditoria/evidencia_score_academico.json y auditoria/figuras/D_score_academico.png
"""
import glob
import json
import logging
import sys
import warnings

import openpyxl
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from scipy.stats import kruskal

warnings.filterwarnings('ignore')
logging.disable(logging.CRITICAL)
sys.path.insert(0, '.')
sys.stdout.reconfigure(encoding='utf-8')
from src.extractor import ExcelExtractor  # noqa: E402
from src.nucleos_cleaner import calcular_score_academico  # noqa: E402
from src.topic_modeler import corpus_nucleos  # noqa: E402

NAVY, CIAN, DORADO, MAGENTA = '#0F385A', '#1FB2DE', '#FBAF17', '#EC0677'

micro = pd.concat([ExcelExtractor(f).extract_estrategias_micro()
                   for f in sorted(glob.glob('data/raw/FORMATOS RA CICLO UNO RC/*.xlsx'))], ignore_index=True)
nuc = corpus_nucleos(micro)
nuc['score'] = nuc['Nucleo'].map(calcular_score_academico)

ws = openpyxl.load_workbook('auditoria/Clasificacion_estandar_oferta.xlsx', read_only=True)['CINE-F_programas']
cine = {str(r[0]).strip(): r[2] for r in list(ws.iter_rows(values_only=True))[1:] if r[0]}
nuc['campo'] = nuc['Programa'].astype(str).str.strip().map(cine)
sin_campo = sorted(nuc.loc[nuc['campo'].isna(), 'Programa'].astype(str).unique())

def kw(df, col):
    g = [x[col].values for _, x in df.groupby('campo') if len(x) >= 2]
    h, p = kruskal(*g)
    n, k = sum(map(len, g)), len(g)
    return {'H': round(h, 3), 'p': round(p, 4), 'k': k, 'n': n, 'eps2': round((h - k + 1) / (n - k), 4)}

con = nuc.dropna(subset=['campo'])
prog = con.groupby(['Programa', 'campo'], as_index=False)['score'].median()
por_campo = con.groupby('campo')['score'].agg(['count', 'mean', 'median']).round(3)
EV = {'nucleos': len(nuc), 'programas': int(nuc['Programa'].nunique()),
      'media': round(nuc['score'].mean(), 3), 'mediana': round(nuc['score'].median(), 3),
      'pct_bajo_0_5': round(100 * (nuc['score'] < 0.5).mean(), 1),
      'pct_cero': round(100 * (nuc['score'] == 0).mean(), 1),
      'programas_sin_campo': sin_campo,
      'kw_nucleo': kw(con, 'score'), 'kw_programa': kw(prog, 'score'),
      'por_campo': {c: {'nucleos': int(r['count']), 'programas': int((prog['campo'] == c).sum()),
                        'media': r['mean'], 'mediana': r['median']} for c, r in por_campo.iterrows()}}
json.dump(EV, open('auditoria/evidencia_score_academico.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(json.dumps(EV, ensure_ascii=False, indent=1))

orden = por_campo.sort_values('median').index.tolist()
fig = make_subplots(rows=1, cols=2, column_widths=[0.58, 0.42], horizontal_spacing=0.2,
                    subplot_titles=('a. Score por campo amplio CINE-F', f'b. Distribución (n = {len(nuc):,} núcleos)'.replace(',', '.')))
for c in orden:
    fig.add_trace(go.Box(x=con.loc[con['campo'] == c, 'score'], name=f"{c[3:]} (n = {int(por_campo.loc[c, 'count'])})",
                         marker_color=NAVY, line_color=NAVY, fillcolor=CIAN, boxpoints=False, orientation='h',
                         showlegend=False), 1, 1)
fig.add_trace(go.Histogram(x=nuc['score'], xbins=dict(start=0, end=1, size=0.025), marker_color=CIAN,
                           showlegend=False), 1, 2)
fig.add_vline(x=0.5, line=dict(color=MAGENTA, dash='dash', width=2), row=1, col=2)
fig.add_annotation(x=0.52, y=0.95, xref='x2', yref='y2 domain', xanchor='left', showarrow=False,
                   font=dict(color=MAGENTA), text=f"Umbral inactivo 0,5<br>{str(EV['pct_bajo_0_5']).replace('.', ',')} % por debajo")
fig.update_layout(font=dict(family='Arial', size=12, color=NAVY), paper_bgcolor='white', plot_bgcolor='white',
                  width=1300, height=560, margin=dict(t=50, b=50, l=20, r=20), separators=',.')
fig.update_xaxes(range=[0, 1], gridcolor='#E6EBF0', title_text='Score académico (0–1)')
fig.update_yaxes(title_text='Núcleos', row=1, col=2)
fig.write_image('auditoria/figuras/D_score_academico.png', scale=2)
