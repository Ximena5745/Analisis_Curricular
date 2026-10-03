"""
Verificación de la Etapa 6 (análisis temático): corpus del LDA, estabilidad
entre semillas y detección de los 10 temas de agenda global.

Uso: python auditoria/scripts/verificar_etapa6.py
Salida: auditoria/evidencia_etapa6.json
"""
import glob
import json
import logging
import re
import sys
import unicodedata
import warnings

warnings.filterwarnings('ignore')
logging.disable(logging.CRITICAL)
sys.path.insert(0, '.')
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from sklearn.decomposition import LatentDirichletAllocation  # noqa: E402
from sklearn.feature_extraction.text import CountVectorizer  # noqa: E402

from src.extractor import ExcelExtractor  # noqa: E402
from src.nucleos_cleaner import tokenizar_nucleo_celda, es_nucleo_valido  # noqa: E402
from src.shared_subjects_analyzer import consolidar_asignaturas  # noqa: E402
from src.topic_modeler import STOPWORDS, _normalizar  # noqa: E402

sys.stdout.reconfigure(encoding='utf-8')
ARCH = sorted(glob.glob('data/raw/FORMATOS RA CICLO UNO RC/*.xlsx'))


def sin_tildes(t):
    t = unicodedata.normalize('NFKD', str(t)).encode('ascii', 'ignore').decode('ascii')
    return t.lower()


ra, micro = [], []
for f in ARCH:
    e = ExcelExtractor(f)
    ra.append(e.extract_resultados_aprendizaje())
    micro.append(e.extract_estrategias_micro())
ra = pd.concat(ra, ignore_index=True)
micro = pd.concat(micro, ignore_index=True)
asig = consolidar_asignaturas(micro)

# --- Corpus del LDA ---
saber = [t for t in ra['SaberAsociado'].dropna().astype(str) if len(t) > 5]
nucleos = []
for c in micro['Núcleos temáticos'].dropna():
    nucleos += [x for x in tokenizar_nucleo_celda(c) if es_nucleo_valido(x)]


def lda_temas(corpus, seed, k=10, n=10):
    docs = [_normalizar(t) for t in corpus]
    vec = CountVectorizer(max_features=500, min_df=2, max_df=0.85, stop_words=STOPWORDS, ngram_range=(1, 2))
    X = vec.fit_transform(docs)
    fn = vec.get_feature_names_out()
    m = LatentDirichletAllocation(n_components=k, random_state=seed, max_iter=100, learning_method='batch').fit(X)
    largo = float(np.mean([len(d.split()) for d in docs]))
    return [set(fn[i] for i in t.argsort()[:-n - 1:-1]) for t in m.components_], largo


def estabilidad(corpus):
    base, largo = lda_temas(corpus, 42)
    jac = []
    for s in (0, 1, 7):
        otro, _ = lda_temas(corpus, s)
        jac += [max(len(a & b) / len(a | b) for b in otro) for a in base]
    return {'documentos': len(corpus), 'palabras_por_doc': round(largo, 1),
            'jaccard_medio_mejor_par': round(float(np.mean(jac)), 2),
            'temas_estables_jaccard_ge_0_5': f'{sum(j >= 0.5 for j in jac)}/{len(jac)}'}


EV = {'lda_codigo': estabilidad(saber), 'lda_nucleos': estabilidad(nucleos),
      'saberasociado_unicos': int(ra['SaberAsociado'].dropna().astype(str).str.strip().str.lower().nunique())}

# --- Temas de agenda global ---
T = json.load(open('config_tendencias.json', encoding='utf-8'))['TENDENCIAS_GLOBALES']
asig['texto'] = asig['texto'].map(sin_tildes)  # núcleos + indicadores de la asignatura
asig['prog39'] = asig['Programa']
temas = []
for tid, info in T.items():
    kws = [sin_tildes(k) for k in info['keywords']]
    sub = asig['texto'].map(lambda t: any(k in t for k in kws))
    pal = asig['texto'].map(lambda t: any(re.search(r'\b' + re.escape(k) + r'\b', t) for k in kws))
    temas.append({'tema': info['descripcion'], 'terminos': len(kws),
                  'asig_subcadena': int(sub.sum()), 'asig_palabra': int(pal.sum()),
                  'prog_subcadena': int(asig.loc[sub, 'prog39'].nunique()),
                  'prog_palabra': int(asig.loc[pal, 'prog39'].nunique())})
EV['temas'] = temas
EV['asignaturas'] = len(asig)
EV['programas'] = int(asig['prog39'].nunique())
EV['ciberseguridad_es_tema'] = any('ciberseg' in v['descripcion'].lower() for v in T.values())
json.dump(EV, open('auditoria/evidencia_etapa6.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(json.dumps(EV, ensure_ascii=False, indent=1))
