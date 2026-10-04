"""
Calibración y validación de src/asociacion_perfil.py contra la referencia experta de varios programas.

Referencia: auditoria/referencia_asociacion_perfil.csv (una fila por ítem del perfil y matriz):
    Matriz;Enfoque;Inicio_item;Competencia;RA;Asignatura;Fuente
  Inicio_item: comienzo del ítem normalizado (sin tildes ni mayúsculas), suficiente para identificarlo.
  1 = el concepto está respaldado (explícito o parcial) en esa capa; 0 = no (las relaciones solo temáticas y las
  entidades genéricas no cuentan).
Calibración: rejilla sobre los parámetros que maximiza el kappa promedio por enfoque (cada enfoque pesa lo mismo).
Validación: si hay programas de más de un enfoque, se calibra dejando fuera cada enfoque y se mide el acuerdo
en el enfoque excluido (generalización a un tipo de programa no visto).

Uso: python auditoria/scripts/calibrar_asociacion_perfil.py
Salida: auditoria/evidencia_calibracion_asociacion.json y auditoria/Calibracion_asociacion_perfil.xlsx
"""
import json
import logging
import os
import sys
import warnings
from itertools import product

import numpy as np
import pandas as pd

warnings.filterwarnings('ignore')
logging.disable(logging.CRITICAL)
os.environ.setdefault('HF_HUB_OFFLINE', '1')
sys.path.insert(0, '.')
sys.stdout.reconfigure(encoding='utf-8')
import src.asociacion_perfil as ap  # noqa: E402

RAIZ = 'data/raw/FORMATOS RA CICLO UNO RC/FormatoRA_'
ref = pd.read_csv('auditoria/referencia_asociacion_perfil.csv', sep=';', dtype=str)
for c in ap.CAPAS:
    ref[c] = ref[c].astype(int)

# Puntajes por matriz y emparejamiento con la referencia
CASOS = []   # (enfoque, matriz, capa, cob, cob_n, sem, y, item, cob_d, cob_nd)
faltan = []
for (matriz, enfoque), g in ref.groupby(['Matriz', 'Enfoque']):
    m = ap.leer_matriz(RAIZ + matriz + '.xlsx')
    items = ap.items_perfil(m)
    P = ap.puntajes(m, items)
    norm = [ap._norm(it['item']) for it in items]
    for _, r in g.iterrows():
        i = next((i for i, n in enumerate(norm) if n.startswith(r['Inicio_item'])), None)
        if i is None:
            faltan.append((matriz, r['Inicio_item']))
            continue
        for capa in ap.CAPAS:
            CASOS.append((enfoque, matriz, capa, P[capa]['cob'][i], P[capa]['cob_n'][i], P[capa]['sem'][i], r[capa], items[i]['item'],
                          P[capa]['cob_d'][i], P[capa]['cob_nd'][i]))
    print('ok', matriz, len(g))
print('Ítems de referencia sin emparejar:', faltan)

# Rejilla, predicción, kappa, calibración y métricas: src/calibracion_asociacion.py (misma lógica que usa el aplicativo)
from src.calibracion_asociacion import EXPLICITA, PARCIAL, SEMANTICA, calibrar, kappa, metricas, pred  # noqa: E402


PRM = calibrar(CASOS)
GLOBAL = metricas(CASOS, PRM)
print('Parámetros (todos los programas):', PRM)
print(json.dumps(GLOBAL, ensure_ascii=False, indent=1))
enfoques = sorted({c[0] for c in CASOS})
LOFO = {}
if len(enfoques) > 1:
    for e in enfoques:
        prm_e = calibrar([c for c in CASOS if c[0] != e])
        LOFO[e] = {'parametros': prm_e, 'metricas': metricas([c for c in CASOS if c[0] == e], prm_e)}
        print('Enfoque excluido:', e, LOFO[e]['metricas']['Global'])
disc = [{'Enfoque': c[0], 'Matriz': c[1], 'Capa': c[2], 'Ítem': c[7], 'Referencia': c[6], 'Método': pred(c, PRM),
         'Cobertura (núcleo)': round(float((c[4] if PRM['nucleo'] else c[3]).max()), 3), 'Similitud': round(float(c[5].max()), 3)}
        for c in CASOS if pred(c, PRM) != c[6]]
print('Discrepancias:', len(disc))
for d in disc:
    print('  ', d)
with pd.ExcelWriter('auditoria/Calibracion_asociacion_perfil.xlsx') as xw:
    pd.DataFrame([{'Capa': k, **v} for k, v in GLOBAL.items()]).to_excel(xw, sheet_name='Global', index=False)
    pd.DataFrame([{'Enfoque excluido': e, 'Capa': k, **v} for e, d in LOFO.items() for k, v in d['metricas'].items()]
                 ).to_excel(xw, sheet_name='Validacion_por_enfoque', index=False)
    pd.DataFrame(disc).to_excel(xw, sheet_name='Discrepancias', index=False)
    pd.DataFrame([PRM]).to_excel(xw, sheet_name='Parametros', index=False)
json.dump({'parametros': PRM, 'global': GLOBAL, 'validacion_por_enfoque': LOFO, 'discrepancias': disc, 'sin_emparejar': faltan},
          open('auditoria/evidencia_calibracion_asociacion.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=str)
