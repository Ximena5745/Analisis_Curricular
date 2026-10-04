"""
Aplica src/asociacion_perfil.py (parámetros calibrados) a todas las matrices de data/raw/FORMATOS RA CICLO UNO RC.
Cada matriz se asocia solo con su propio contenido.

Indicadores por matriz y perfil: % de ítems con respaldo en competencias, RA y asignaturas, % en las tres capas y
% SIN ASOCIACIÓN EN NINGUNA CAPA.

Uso: python auditoria/scripts/asociacion_perfil_50_matrices.py
Salida: auditoria/Asociacion_perfil_50_matrices.xlsx (Resumen, Resumen_perfil, Items, Detalle) y
        auditoria/evidencia_asociacion_50_matrices.json
"""
import glob
import json
import logging
import os
import sys
import warnings

import pandas as pd

warnings.filterwarnings('ignore')
logging.disable(logging.CRITICAL)
os.environ.setdefault('HF_HUB_OFFLINE', '1')
sys.path.insert(0, '.')
sys.stdout.reconfigure(encoding='utf-8')
import src.asociacion_perfil as ap  # noqa: E402


def indicadores(df):
    n = len(df)
    return {'Ítems': n, **{f'% {c}': round(100 * df[c].mean(), 1) for c in ap.CAPAS},
            '% tres capas': round(100 * (df.capas_con_respaldo == 3).mean(), 1),
            '% sin asociación': round(100 * (df.capas_con_respaldo == 0).mean(), 1)}


items, detalle, errores = [], [], []
for f in sorted(glob.glob('data/raw/FORMATOS RA CICLO UNO RC/FormatoRA_*.xlsx')):
    mz = os.path.basename(f)[len('FormatoRA_'):-5]
    try:
        filas = ap.asociar(f)
    except Exception as e:  # noqa: BLE001
        errores.append({'Matriz': mz, 'Error': str(e)[:200]})
        print('ERROR', mz, e, flush=True)
        continue
    detalle += [{'Matriz': mz, **r} for r in filas]
    items += [{'Matriz': mz, **r} for r in ap.resumen_items(filas)]
    print('ok', mz, flush=True)

I_todos = pd.DataFrame(items)
I = I_todos[I_todos.evaluable]   # los indicadores solo cuentan atributos evaluables
res = pd.DataFrame([{'Matriz': m, **indicadores(g)} for m, g in I.groupby('Matriz')]).sort_values('% sin asociación', ascending=False)
res_p = pd.DataFrame([{'Matriz': m, 'Perfil': p, **indicadores(g)} for (m, p), g in I.groupby(['Matriz', 'perfil'])])
tot = {'Global': indicadores(I), **{p: indicadores(g) for p, g in I.groupby('perfil')},
       **{f'Origen: {o}': indicadores(g) for o, g in I.groupby('origen')}}
with pd.ExcelWriter('auditoria/Asociacion_perfil_50_matrices.xlsx') as w:
    res.to_excel(w, sheet_name='Resumen', index=False)
    res_p.to_excel(w, sheet_name='Resumen_perfil', index=False)
    I_todos.to_excel(w, sheet_name='Items', index=False)
    pd.DataFrame(detalle).to_excel(w, sheet_name='Detalle', index=False)
    if errores:
        pd.DataFrame(errores).to_excel(w, sheet_name='Errores', index=False)
json.dump({'parametros': ap.PARAMS, 'factor_rol': ap.FACTOR_ROL, 'matrices': len(res), 'errores': errores, 'totales': tot,
           'por_matriz': res.to_dict('records')}, open('auditoria/evidencia_asociacion_50_matrices.json', 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
print('\nMatrices:', len(res), '| errores:', len(errores), '| ítems no evaluables:', int((~I_todos.evaluable).sum()))
for k, v in tot.items():
    print(f'{k:40s}', v)
print('\nMatrices con más de 15 % sin asociación:', int((res['% sin asociación'] > 15).sum()))
print(res.to_string(index=False))
