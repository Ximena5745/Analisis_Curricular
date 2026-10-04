"""
Revisión profunda del indicador «sin asociación en ninguna capa»: método (parámetros calibrados) frente a la
referencia experta, ítem a ítem, con la mejor evidencia que encuentra el método en cada capa.

Uso: python auditoria/scripts/revision_profunda_sin_asociacion.py
Salida: auditoria/Revision_profunda_sin_asociacion.xlsx (hoja Items) y resumen en consola.
"""
import json
import logging
import os
import sys
import warnings

import numpy as np
import pandas as pd

warnings.filterwarnings('ignore')
logging.disable(logging.CRITICAL)
os.environ.setdefault('HF_HUB_OFFLINE', '1')
sys.path.insert(0, '.')
sys.stdout.reconfigure(encoding='utf-8')
import src.asociacion_perfil as ap  # noqa: E402

RAIZ = 'data/raw/FORMATOS RA CICLO UNO RC/FormatoRA_'
PRM = json.load(open('auditoria/evidencia_calibracion_asociacion.json', encoding='utf-8'))['parametros']
ref = pd.read_csv('auditoria/referencia_asociacion_perfil.csv', sep=';', dtype=str)

filas = []
for matriz, g in ref.groupby('Matriz'):
    m = ap.leer_matriz(RAIZ + matriz + '.xlsx')
    items = ap.items_perfil(m)
    P = ap.puntajes(m, items)
    norm = [ap._norm(it['item']) for it in items]
    for _, r in g.iterrows():
        i = next((i for i, n in enumerate(norm) if n.startswith(r['Inicio_item'])), None)
        if i is None:
            continue
        f = {'Matriz': matriz, 'Ítem': items[i]['item'], 'Origen': items[i].get('origen', ''),
             'Revisado': r['Fuente'].startswith('Revisión'), 'Ref_ninguna': int(r['Competencia'] + r['RA'] + r['Asignatura'] == '000')}
        met = []
        for capa in ap.CAPAS:
            c = P[capa]['cob_n' if PRM['nucleo'] else 'cob'][i]
            s = P[capa]['sem'][i]
            ok = (c >= PRM['explicita']) | ((c >= PRM['parcial']) & (s >= PRM['semantica']))
            k = int(np.argmax(c)) if len(c) else None
            met.append(int(ok.any()))
            f[f'Ref_{capa}'] = int(r[capa])
            f[f'Met_{capa}'] = met[-1]
            f[f'Cob_{capa}'] = round(float(c.max()), 3) if len(c) else 0.0
            f[f'Sem_{capa}'] = round(float(s.max()), 3) if len(s) else 0.0
            f[f'Evidencia_{capa}'] = P[capa]['evidencia'][i][k] if k is not None else ''
        f['Met_ninguna'] = int(not any(met))
        filas.append(f)
    print('ok', matriz, flush=True)

d = pd.DataFrame(filas)
d['Caso'] = np.select([(d.Ref_ninguna == 1) & (d.Met_ninguna == 1), (d.Ref_ninguna == 0) & (d.Met_ninguna == 1),
                       (d.Ref_ninguna == 1) & (d.Met_ninguna == 0)],
                      ['Ambos sin asociación', 'Solo el método: sin asociación', 'Solo la referencia: sin asociación'],
                      'Ambos asociado')
d.to_excel('auditoria/Revision_profunda_sin_asociacion.xlsx', sheet_name='Items', index=False)

print('\nParámetros:', PRM)
print('Ítems:', len(d), '| ref %.1f%% | método %.1f%%' % (100 * d.Ref_ninguna.mean(), 100 * d.Met_ninguna.mean()))
print(d.Caso.value_counts().to_string())
print('\nPor origen (método sin asociación %):')
print(d.groupby('Origen')[['Ref_ninguna', 'Met_ninguna']].mean().mul(100).round(1).to_string())
print('\nRevisados (38 cambios): método sin asociación en', int(d[d.Revisado].Met_ninguna.sum()), 'de', int(d.Revisado.sum()))
cols = ['Matriz', 'Ítem', 'Cob_Competencia', 'Sem_Competencia', 'Cob_RA', 'Sem_RA', 'Cob_Asignatura', 'Sem_Asignatura', 'Evidencia_Asignatura']
print('\n== Solo el método marca sin asociación ==')
for _, r in d[d.Caso == 'Solo el método: sin asociación'].iterrows():
    print(f"{r.Matriz[:14]:14s} | {r['Ítem'][:60]:60s} | cobA {r.Cob_Asignatura:.2f} semA {r.Sem_Asignatura:.2f} | {str(r.Evidencia_Asignatura)[:70]}")
print('\n== Solo la referencia marca sin asociación ==')
for _, r in d[d.Caso == 'Solo la referencia: sin asociación'].iterrows():
    print(f"{r.Matriz[:14]:14s} | {r['Ítem'][:60]:60s} | cobA {r.Cob_Asignatura:.2f} semA {r.Sem_Asignatura:.2f} | {str(r.Evidencia_Asignatura)[:70]}")
