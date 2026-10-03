"""
Aplica la propuesta de tendencias integradas (auditoria/propuesta_tendencias_integradas.json) a las
1.616 asignaturas sin electivas y mide cobertura, multietiqueta y asignaturas sin tendencia.

Regla: tendencia asignada si algún término aparece en el NOMBRE de la asignatura, o si el CONTENIDO
(núcleos + indicadores) suma ≥ 2 puntos (término de varias palabras = 2; de una palabra = 1).

Uso: python auditoria/scripts/tendencias_integradas.py [archivo_lista.json]
Salida: auditoria/evidencia_tendencias_integradas.json y auditoria/Tendencias_integradas.xlsx
"""
import glob
import json
import logging
import re
import sys
import unicodedata
import warnings
from collections import Counter

import pandas as pd

warnings.filterwarnings('ignore')
logging.disable(logging.CRITICAL)
sys.path.insert(0, '.')
from src.extractor import ExcelExtractor  # noqa: E402
from src.shared_subjects_analyzer import consolidar_asignaturas  # noqa: E402

sys.stdout.reconfigure(encoding='utf-8')


def norm(t):
    t = unicodedata.normalize('NFKD', str(t)).encode('ascii', 'ignore').decode('ascii').lower()
    return re.sub(r'\s+', ' ', re.sub(r'[^a-z0-9. ]', ' ', t)).strip()


ARCH = sys.argv[1] if len(sys.argv) > 1 else 'auditoria/propuesta_tendencias_integradas.json'
SUF = '' if ARCH.endswith('integradas.json') else '_15'
P = json.load(open(ARCH, encoding='utf-8'))['tendencias']
PAT = {k: [(t, re.compile(r'(?<![a-z0-9])' + re.escape(norm(t)) + r'(?![a-z0-9])'), 2 if ' ' in t else 1) for t in v['terminos']]
       for k, v in P.items()}


def asignar(nombre, contenido):
    n, c = norm(nombre), norm(contenido)
    out = {}
    for k, pats in PAT.items():
        en_nombre = [t for t, p, _ in pats if p.search(n)]
        en_cont = [(t, w) for t, p, w in pats if p.search(c)]
        if en_nombre or sum(w for _, w in en_cont) >= 2:
            out[k] = sorted(set(en_nombre) | {t for t, _ in en_cont})
    return out


micro = pd.concat([ExcelExtractor(f).extract_estrategias_micro()
                   for f in sorted(glob.glob('data/raw/FORMATOS RA CICLO UNO RC/*.xlsx'))], ignore_index=True)
asig = consolidar_asignaturas(micro)
filas = []
for _, r in asig.iterrows():
    a = asignar(r['asignatura'], r['texto'])
    filas.append({'Programa': r['Programa'], 'Sede': r['Codigo'], 'Asignatura': r['asignatura'],
                  'Tendencias': ', '.join(f"{k} {P[k]['nombre']}" for k in sorted(a)),
                  'N.º tendencias': len(a),
                  'Términos': ' | '.join(f"{k}: {', '.join(v)}" for k, v in sorted(a.items())), '_k': sorted(a)})
d = pd.DataFrame(filas)
n = len(d)
por = {k: int(d['_k'].map(lambda x: k in x).sum()) for k in P}
prog = {k: int(d.loc[d['_k'].map(lambda x: k in x), 'Programa'].nunique()) for k in P}
sin = d[d['N.º tendencias'] == 0]
EV = {'asignaturas': n, 'cubiertas': int((d['N.º tendencias'] > 0).sum()),
      'cobertura_pct': round(100 * (d['N.º tendencias'] > 0).mean(), 1),
      'media_tendencias': round(float(d['N.º tendencias'].mean()), 2),
      'distribucion_n': d['N.º tendencias'].value_counts().sort_index().to_dict(),
      'por_tendencia': {f"{k} {P[k]['nombre']}": {'asignaturas': v, 'pct': round(100 * v / n, 1), 'programas': prog[k]}
                        for k, v in por.items()},
      'sin_tendencia_ejemplos': Counter(sin['Asignatura']).most_common(40)}
json.dump(EV, open(f'auditoria/evidencia_tendencias_integradas{SUF}.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

with pd.ExcelWriter(f'auditoria/Tendencias_integradas{SUF}.xlsx') as w:
    pd.DataFrame([{'Código': k, 'Sector': v['sector'], 'Tendencia': v['nombre'], 'Origen': v['origen'],
                   'Términos': ', '.join(v['terminos']), 'Asignaturas': por[k], '% de 1.616': round(100 * por[k] / n, 1),
                   'Programas (de 39)': prog[k]} for k, v in P.items()]).to_excel(w, sheet_name='Tendencias', index=False)
    d.drop(columns='_k').assign(**{'Validación': '', 'Observación': ''}).to_excel(w, sheet_name='Asignaturas', index=False)
    sin[['Programa', 'Asignatura']].to_excel(w, sheet_name='Sin_tendencia', index=False)
print(json.dumps({k: v for k, v in EV.items() if k != 'sin_tendencia_ejemplos'}, ensure_ascii=False, indent=1))
print('SIN:', EV['sin_tendencia_ejemplos'])
