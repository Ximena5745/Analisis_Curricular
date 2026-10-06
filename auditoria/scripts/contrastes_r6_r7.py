"""
R6 (Spearman entre V1, V2, V4 y V5) y R7 (Kruskal-Wallis entre sedes) por matriz, con V5 según D29.

D29: V5 = % de estrategias cuyo indicador de mayor nivel supera la mera implementación (N2 o más). Vale 0 solo si la
matriz no declara indicadores o si todos son de implementación (N1). La evidencia directa (N3–N4) queda como dato
descriptivo de R5. Se calcula también la V5 anterior (D17, evidencia directa) para comprobar que el script reproduce
los valores publicados antes de D29.

Uso: python auditoria/scripts/contrastes_r6_r7.py
Salida: auditoria/evidencia_r6_r7.json
"""
import glob
import json
import os
import sys
from itertools import combinations

import pandas as pd
from scipy.stats import kruskal, spearmanr

sys.path.insert(0, '.')
from src import indicadores_articulo as ia  # noqa: E402

v1 = pd.read_excel('auditoria/Asociacion_perfil_50_matrices.xlsx', sheet_name='Resumen')
d = pd.DataFrame({'matriz': v1['Matriz'], 'V1': 100 - v1['% sin asociación']})
v4 = pd.DataFrame(json.load(open('auditoria/evidencia_v4_alternativas.json', encoding='utf-8'))['por_matriz'])[['matriz', 'V4']]
v5 = pd.DataFrame(json.load(open('auditoria/evidencia_v5.json', encoding='utf-8'))['por_matriz'])[['matriz', 'V5_directa']]
d = d.merge(v4, on='matriz').merge(v5, on='matriz')
REP = {'Derecho_HMED', 'Derecho_VNAL', 'Ing.Telecomunicaciones_PBOG', 'IngSistemas_PBOG', 'IngSistemas_PMED'}
d['V2'] = d['matriz'].map(lambda m: 0.0 if m in REP else 100.0)

filas = {}
for f in sorted(glob.glob('data/raw/FORMATOS RA CICLO UNO RC/*.xlsx')):
    m = ia._evaluar_matriz(ia._leer_matriz(os.path.basename(f), f))
    niv = [e['nivel_max'][:2] if e['nivel_max'] else 'N0' for e in m['estrategias']]
    filas[m['matriz']] = {'programa': m['programa'], 'archivo': os.path.basename(f),
                          'V5': 100 * sum(x >= 'N2' for x in niv) / len(niv) if niv else 0.0}
d['V5'] = d['matriz'].map(lambda x: filas[x]['V5'])
d['programa'] = d['matriz'].map(lambda x: filas[x]['programa'])
d['archivo'] = d['matriz'].map(lambda x: filas[x]['archivo'])
d['sede'] = d['matriz'].str.rsplit('_', n=1).str[1]
assert len(d) == 50 and d.notna().all().all()
uno = d.sort_values('archivo').drop_duplicates('programa')


def rho(df, v5):
    out = {}
    for a, b in combinations(['V1', 'V2', 'V4', v5], 2):
        r, p = spearmanr(df[a], df[b])
        out[f"{a}–{b.replace('V5_directa', 'V5')}"] = (round(r, 2), round(p, 3))
    return out


def kw(df, v):
    g = [x[v].values for _, x in df[df.sede != 'HBOG'].groupby('sede')]
    n, k = sum(map(len, g)), len(g)
    h, p = kruskal(*g)
    return round(h, 2), round(p, 3), round(max(0.0, (h - k + 1) / (n - k)), 3), n


EV = {'n_matrices': len(d), 'n_programas': len(uno),
      'V5_global': f"{sum(d.V5 * 0 + 1)}",
      'V5_por_matriz': {'min': round(d.V5.min(), 1), 'max': round(d.V5.max(), 1), 'mediana': round(d.V5.median(), 1),
                        'en_100': int((d.V5 == 100).sum()), 'minimo': d.loc[d.V5.idxmin(), 'matriz']},
      'spearman_50': rho(d, 'V5'), 'spearman_programas': rho(uno, 'V5'),
      'spearman_50_anterior_D17': rho(d, 'V5_directa'),
      'kruskal_49': {v: kw(d, v) for v in ['V1', 'V2', 'V4', 'V5']},
      'kruskal_programas': {v: kw(uno, v) for v in ['V1', 'V2', 'V4', 'V5']},
      'kruskal_49_anterior_D17': kw(d, 'V5_directa'), 'kruskal_programas_anterior_D17': kw(uno, 'V5_directa')}
del EV['V5_global']


def desc(x):
    f = lambda v: f'{v:.1f}'.replace('.', ',')  # noqa: E731
    return f"{f(x.median())} % ({f(x.min())}–{f(x.max())})" if len(x) > 1 else f"{f(x.iloc[0])} %"


# R7 descriptivo por sede (mediana y rango; V2 como matrices sin repetición)
EV['total'] = {'n': len(d), 'V1': desc(d.V1), 'V2_con_repeticion': int((d.V2 == 0).sum()), 'V4': desc(d.V4), 'V5': desc(d.V5)}
EV['por_sede'] ={s: {'n': len(x), 'V1': desc(x.V1), 'V2': f"{int((x.V2 == 100).sum())} de {len(x)}",
                      'V4': desc(x.V4), 'V5': desc(x.V5)}
                  for s, x in d.groupby('sede')}
json.dump(EV, open('auditoria/evidencia_r6_r7.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
for k, v in EV.items():
    print(k, v)
