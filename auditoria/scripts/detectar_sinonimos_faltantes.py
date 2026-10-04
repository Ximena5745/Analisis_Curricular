"""
Candidatos a sinónimos: lemas de los ítems del perfil que NO aparecen (por raíz) en ninguna unidad de su propia
matriz, pero que tienen en ella una variante morfológica cercana (prefijo común ≥ 4 letras o similitud de cadena
≥ 0,75). Cada candidato se cuenta en cuántas matrices y en cuántos ítems aparece.

Uso: python auditoria/scripts/detectar_sinonimos_faltantes.py
Salida: auditoria/Sinonimos_candidatos.xlsx
"""
import glob
import logging
import os
import sys
import warnings
from collections import defaultdict
from difflib import SequenceMatcher

import pandas as pd

warnings.filterwarnings('ignore')
logging.disable(logging.CRITICAL)
sys.path.insert(0, '.')
sys.stdout.reconfigure(encoding='utf-8')
import src.asociacion_perfil as ap  # noqa: E402

cand = defaultdict(lambda: {'matrices': set(), 'items': set()})
faltantes = defaultdict(lambda: {'matrices': set(), 'items': set()})
for f in sorted(glob.glob('data/raw/FORMATOS RA CICLO UNO RC/FormatoRA_*.xlsx')):
    try:
        m = ap.leer_matriz(f)
    except Exception as e:  # noqa: BLE001
        print('omitida', os.path.basename(f), e)
        continue
    mz = os.path.basename(f)[10:-5]
    lem_m = set()
    for ents in m['entidades'].values():
        for e in ents:
            for u in e['unidades']:
                lem_m |= ap.lemas(u)
    raices_m = {ap._raiz(l) for l in lem_m}
    for it in ap.items_perfil(m):
        for l, grupo in ap._expandir(ap.lemas(it['item'])):
            if len(l) < 5 or grupo & raices_m:
                continue
            vecinos = sorted(x for x in lem_m if len(x) >= 5 and x != l and
                             (os.path.commonprefix([l, x]).__len__() >= max(4, min(len(l), len(x)) - 4)
                              or SequenceMatcher(None, l, x).ratio() >= 0.75))
            if vecinos:
                for v in vecinos[:4]:
                    cand[(l, v)]['matrices'].add(mz)
                    cand[(l, v)]['items'].add(it['item'][:80])
            else:
                faltantes[l]['matrices'].add(mz)
                faltantes[l]['items'].add(it['item'][:80])
    print('ok', mz, flush=True)

c = pd.DataFrame([{'Lema perfil': l, 'Variante en matriz': v, 'Matrices': len(d['matrices']), 'Ítems': len(d['items']),
                   'Ejemplo': next(iter(d['items']))} for (l, v), d in cand.items()]).sort_values(['Matrices', 'Ítems'], ascending=False)
s = pd.DataFrame([{'Lema perfil': l, 'Matrices': len(d['matrices']), 'Ítems': len(d['items']), 'Ejemplo': next(iter(d['items']))}
                  for l, d in faltantes.items()]).sort_values(['Matrices', 'Ítems'], ascending=False)
with pd.ExcelWriter('auditoria/Sinonimos_candidatos.xlsx') as w:
    c.to_excel(w, sheet_name='Variantes', index=False)
    s.to_excel(w, sheet_name='Sin_variante', index=False)
print('\n== Variantes morfológicas (top 60) ==')
print(c.head(60).to_string(index=False, max_colwidth=50))
print('\n== Lemas del perfil sin ninguna variante en su matriz (top 50) ==')
print(s.head(50).to_string(index=False, max_colwidth=50))
