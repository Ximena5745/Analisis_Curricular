"""
Temáticas (lista oficial, palabra completa; D12) frente a tópicos (LDA de consenso k = 13; D11).

Misma base: las 1.192 asignaturas del corpus del LDA (una matriz por programa, sin electivas).
Para cada temática: asignaturas que la mencionan, distribución de su tópico dominante y
concentración (lift = % de la temática en el tópico / % del tópico en el corpus).
Para cada tópico: temáticas que contiene.

Uso: python auditoria/scripts/tematicas_vs_topicos.py
Salida: auditoria/evidencia_tematicas_topicos.json
"""
import glob
import json
import logging
import re
import sys
import unicodedata
import warnings

import pandas as pd

warnings.filterwarnings('ignore')
logging.disable(logging.CRITICAL)
sys.path.insert(0, '.')
from src.extractor import ExcelExtractor  # noqa: E402
from src.topic_modeler import corpus_asignaturas, modelar_topicos_consenso  # noqa: E402

sys.stdout.reconfigure(encoding='utf-8')


def st(t):
    return unicodedata.normalize('NFKD', str(t)).encode('ascii', 'ignore').decode('ascii').lower()


micro = pd.concat([ExcelExtractor(f).extract_estrategias_micro()
                   for f in sorted(glob.glob('data/raw/FORMATOS RA CICLO UNO RC/*.xlsx'))], ignore_index=True)
corpus = corpus_asignaturas(micro).reset_index(drop=True)
res = modelar_topicos_consenso(micro)
asig = res['asignatura_topico'].reset_index(drop=True)
assert len(asig) == len(corpus)
asig['texto'] = corpus['texto'].map(st)
asig['topico'] = asig['topico_dominante'] + 1
etiquetas = {t['topic_id'] + 1: ', '.join(t['top_words'][:6]) for t in res['topics']}

T = json.load(open('config_tendencias.json', encoding='utf-8'))['TENDENCIAS_GLOBALES']
base = asig['topico'].value_counts(normalize=True)
EV = {'asignaturas': len(asig), 'topicos': etiquetas, 'tematicas': {}, 'topico_tematicas': {}}
for tid, info in T.items():
    pat = r'\b(' + '|'.join(re.escape(st(k)) for k in info['keywords']) + r')\b'
    m = asig['texto'].str.contains(pat, regex=True)
    asig[tid] = m
    if m.sum() == 0:
        EV['tematicas'][tid] = {'asignaturas': 0}
        continue
    dist = asig.loc[m, 'topico'].value_counts(normalize=True)
    lift = (dist / base).dropna().sort_values(ascending=False)
    top = dist.sort_values(ascending=False)
    EV['tematicas'][tid] = {
        'asignaturas': int(m.sum()),
        'topicos_principales': [{'topico': int(k), 'pct_de_la_tematica': round(100 * v, 1), 'lift': round(float(lift[k]), 2)}
                                for k, v in top.head(3).items()],
        'concentracion_top1': round(100 * float(top.iloc[0]), 1),
        'n_topicos_con_presencia': int((dist > 0).sum())}
for k in sorted(etiquetas):
    g = asig[asig['topico'] == k]
    EV['topico_tematicas'][k] = {'asignaturas': len(g),
                                 'tematicas': {tid: round(100 * float(g[tid].mean()), 1) for tid in T if len(g) and g[tid].mean() > 0.1}}
json.dump(EV, open('auditoria/evidencia_tematicas_topicos.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(json.dumps(EV, ensure_ascii=False, indent=1))
