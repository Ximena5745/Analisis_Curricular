"""
P14: compara la estabilidad entre semillas del LDA sobre los núcleos para varios k,
y lista las palabras principales de cada tópico (semilla 42).

Uso: python auditoria/scripts/comparar_k_lda.py [k1 k2 ...]   (por defecto 10 19)
Salida: auditoria/evidencia_k_lda.json
"""
import glob, json, logging, sys, warnings
warnings.filterwarnings('ignore'); logging.disable(logging.CRITICAL); sys.path.insert(0, '.')
import numpy as np
import pandas as pd
from sklearn.decomposition import LatentDirichletAllocation
from sklearn.feature_extraction.text import CountVectorizer
from src.extractor import ExcelExtractor
from src.topic_modeler import STOPWORDS, _normalizar, corpus_nucleos

sys.stdout.reconfigure(encoding='utf-8')
micro = pd.concat([ExcelExtractor(f).extract_estrategias_micro()
                   for f in sorted(glob.glob('data/raw/FORMATOS RA CICLO UNO RC/*.xlsx'))], ignore_index=True)
docs = [_normalizar(t) for t in corpus_nucleos(micro)['Nucleo'] if len(str(t)) > 5]
vec = CountVectorizer(max_features=500, min_df=2, max_df=0.85, stop_words=STOPWORDS, ngram_range=(1, 2))
X = vec.fit_transform(docs); fn = vec.get_feature_names_out()


def temas(k, seed, n=10):
    m = LatentDirichletAllocation(n_components=k, random_state=seed, max_iter=100, learning_method='batch').fit(X)
    return [[fn[i] for i in t.argsort()[:-n - 1:-1]] for t in m.components_]


EV = {'documentos': len(docs)}
KS = [int(a) for a in sys.argv[1:]] or [10, 19]
for k in KS:
    base = temas(k, 42); jac = []
    for s in (0, 1, 7, 123):
        otro = [set(t) for t in temas(k, s)]
        jac += [max(len(set(a) & b) / len(set(a) | b) for b in otro) for a in base]
    EV[f'k{k}'] = {'jaccard_medio': round(float(np.mean(jac)), 3),
                   'topicos_estables_ge_0_5': f'{sum(j >= 0.5 for j in jac)}/{len(jac)}',
                   'topicos_reproducidos_ge_0_3': f'{sum(j >= 0.3 for j in jac)}/{len(jac)}',
                   'topicos': [', '.join(t[:8]) for t in base]}
    print(k, EV[f'k{k}']['jaccard_medio'], EV[f'k{k}']['topicos_estables_ge_0_5'], flush=True)
json.dump(EV, open('auditoria/evidencia_k_lda' + ('' if KS == [10, 19] else '_' + '_'.join(map(str, KS))) + '.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(json.dumps(EV, ensure_ascii=False, indent=1))
