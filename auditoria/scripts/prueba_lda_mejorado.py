"""
P14 (prueba): LDA con las recomendaciones 1–4, sin modificar el código del proyecto.

1. Documento = asignatura (sus núcleos temáticos depurados unidos), no el núcleo suelto.
2. Una matriz por programa (39): se descartan las sedes repetidas de los multisede.
3. Vocabulario: lemas de spaCy (es_core_news_sm), solo sustantivos, adjetivos y nombres
   propios; palabras vacías del proyecto + español de spaCy + inglés.
4. Calidad: coherencia NPMI y UMass + estabilidad entre 5 semillas, para k = 5…30.

Uso: python auditoria/scripts/prueba_lda_mejorado.py
Salida: auditoria/evidencia_lda_mejorado.json
"""
import glob
import json
import logging
import sys
import unicodedata
import warnings

warnings.filterwarnings('ignore')
logging.disable(logging.CRITICAL)
sys.path.insert(0, '.')
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import spacy  # noqa: E402
from sklearn.decomposition import LatentDirichletAllocation  # noqa: E402
from sklearn.feature_extraction.text import CountVectorizer, ENGLISH_STOP_WORDS  # noqa: E402

from src.extractor import ExcelExtractor  # noqa: E402
from src.nucleos_cleaner import tokenizar_nucleo_celda, es_nucleo_valido  # noqa: E402
from src.topic_modeler import STOPWORDS  # noqa: E402

sys.stdout.reconfigure(encoding='utf-8')
SEMILLAS = (42, 0, 1, 7, 123)
KS = range(5, 31)


def sin_tildes(t):
    return unicodedata.normalize('NFKD', str(t)).encode('ascii', 'ignore').decode('ascii').lower()


# --- 1 y 2: asignaturas de una matriz por programa ---
asig, vistos = [], set()
for f in sorted(glob.glob('data/raw/FORMATOS RA CICLO UNO RC/*.xlsx')):
    m = ExcelExtractor(f).extract_estrategias_micro()
    prog = m['Programa'].iloc[0]
    if prog in vistos:
        continue
    vistos.add(prog)
    for nombre, celda in zip(m['Nombre asignatura o módulo'], m['Núcleos temáticos']):
        if pd.isna(celda):
            continue
        nuc = [n for n in tokenizar_nucleo_celda(celda) if es_nucleo_valido(n)]
        if nuc:
            asig.append({'Programa': prog, 'asignatura': nombre, 'texto': ' . '.join(nuc), 'n_nucleos': len(nuc)})
asig = pd.DataFrame(asig)

# --- 3: lematización y vocabulario ---
nlp = spacy.load('es_core_news_sm', disable=['parser', 'ner'])
vacias = {sin_tildes(w) for w in STOPWORDS} | {sin_tildes(w) for w in nlp.Defaults.stop_words} | set(ENGLISH_STOP_WORDS)
docs = []
for d in nlp.pipe(asig['texto'].tolist(), batch_size=64):
    lem = [sin_tildes(t.lemma_) for t in d if t.pos_ in ('NOUN', 'ADJ', 'PROPN') and t.is_alpha]
    docs.append(' '.join(w for w in lem if len(w) > 2 and w not in vacias))
vec = CountVectorizer(max_features=1000, min_df=3, max_df=0.5, ngram_range=(1, 2))
X = vec.fit_transform(docs)
fn = vec.get_feature_names_out()
B = (X > 0).astype(int).tocsc()
N = X.shape[0]
df_w = np.asarray(B.sum(axis=0)).ravel()


def coherencias(top):
    npmi, umass = [], []
    for i in range(len(top)):
        for j in range(i + 1, len(top)):
            a, b = top[i], top[j]
            co = B[:, a].multiply(B[:, b]).sum()
            umass.append(np.log((co + 1) / df_w[b]))
            if co == 0:
                npmi.append(-1.0)
            else:
                p_ab, p_a, p_b = co / N, df_w[a] / N, df_w[b] / N
                npmi.append(np.log(p_ab / (p_a * p_b)) / -np.log(p_ab))
    return float(np.mean(npmi)), float(np.mean(umass))


def ajustar(k, seed):
    return LatentDirichletAllocation(n_components=k, random_state=seed, max_iter=100,
                                     learning_method='batch').fit(X).components_


EV = {'documentos': N, 'programas': len(vistos), 'vocabulario': len(fn),
      'palabras_por_doc': round(float(np.mean([len(d.split()) for d in docs])), 1), 'k': {}}
print(f"documentos {N} | programas {len(vistos)} | vocabulario {len(fn)} | palabras/doc {EV['palabras_por_doc']}", flush=True)
for k in KS:
    comp = {s: ajustar(k, s) for s in SEMILLAS}
    tops = {s: [list(t.argsort()[:-11:-1]) for t in c] for s, c in comp.items()}
    coh = [coherencias(t) for t in tops[42]]
    jac = []
    for s in SEMILLAS[1:]:
        otros = [set(t) for t in tops[s]]
        jac += [max(len(set(a) & b) / len(set(a) | b) for b in otros) for a in tops[42]]
    r = {'npmi': round(float(np.mean([c[0] for c in coh])), 4), 'umass': round(float(np.mean([c[1] for c in coh])), 3),
         'jaccard_medio': round(float(np.mean(jac)), 3),
         'estables_ge_0_5': round(float(np.mean([j >= 0.5 for j in jac])), 3),
         'topicos': [', '.join(fn[i] for i in t[:8]) for t in tops[42]]}
    EV['k'][k] = r
    print(f"k={k:2d} npmi={r['npmi']:.4f} umass={r['umass']:.3f} jaccard={r['jaccard_medio']:.3f} estables={r['estables_ge_0_5']:.0%}", flush=True)
json.dump(EV, open('auditoria/evidencia_lda_mejorado.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
