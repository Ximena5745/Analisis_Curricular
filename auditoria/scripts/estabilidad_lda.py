"""
P14 (prueba): variantes para mejorar la estabilidad entre semillas del LDA (k = 13),
sobre el corpus mejorado de prueba_lda_mejorado.py (recomendaciones 1–4).

Variantes: más iteraciones; priors dispersos (alfa, beta); vocabulario más estricto;
combinación; NMF (inicialización aleatoria y NNDSVD); LDA de consenso entre 10 semillas.

1. Documento = asignatura (sus núcleos temáticos depurados unidos), no el núcleo suelto.
2. Una matriz por programa (39): se descartan las sedes repetidas de los multisede.
3. Vocabulario: lemas de spaCy (es_core_news_sm), solo sustantivos, adjetivos y nombres
   propios; palabras vacías del proyecto + español de spaCy + inglés.
4. Calidad: coherencia NPMI y UMass + estabilidad entre 5 semillas, para k = 5…30.

Uso: python auditoria/scripts/estabilidad_lda.py
Salida: auditoria/evidencia_estabilidad_lda.json
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
from sklearn.decomposition import LatentDirichletAllocation, NMF
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.cluster import AgglomerativeClustering  # noqa: E402
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

K = 13
SEM = (42, 0, 1, 7, 123)


def vocab(min_df=3, max_df=0.5, max_features=1000):
    v = CountVectorizer(max_features=max_features, min_df=min_df, max_df=max_df, ngram_range=(1, 2))
    return v.fit_transform(docs), v.get_feature_names_out()


def tops(comp, n=10):
    return [set(t.argsort()[:-n - 1:-1]) for t in comp]


def jaccard(lista):
    base, jac = lista[0], []
    for otro in lista[1:]:
        jac += [max(len(a & b) / len(a | b) for b in otro) for a in base]
    return round(float(np.mean(jac)), 3), round(float(np.mean([j >= 0.5 for j in jac])), 3)


def lda(Xm, s, it=100, a=None, b=None):
    return LatentDirichletAllocation(n_components=K, random_state=s, max_iter=it, learning_method='batch',
                                     doc_topic_prior=a, topic_word_prior=b).fit(Xm).components_


def npmi(Xm, comp):
    Bm = (Xm > 0).astype(int).tocsc(); n = Xm.shape[0]; dfw = np.asarray(Bm.sum(axis=0)).ravel(); out = []
    for t in tops(comp):
        t = list(t)
        for i in range(len(t)):
            for j in range(i + 1, len(t)):
                co = Bm[:, t[i]].multiply(Bm[:, t[j]]).sum()
                out.append(-1.0 if co == 0 else np.log(co * n / (dfw[t[i]] * dfw[t[j]])) / -np.log(co / n))
    return round(float(np.mean(out)), 4)


EV = {}
def registrar(nombre, Xm, comps):
    j, e = jaccard([tops(c) for c in comps])
    EV[nombre] = {'jaccard_medio': j, 'estables_ge_0_5': e, 'npmi': npmi(Xm, comps[0])}
    print(f'{nombre:45s} jaccard={j:.3f} estables={e:.0%} npmi={EV[nombre]["npmi"]:.4f}', flush=True)


X0, fn0 = vocab()
registrar('Base (prueba 1-4)', X0, [lda(X0, s) for s in SEM])
registrar('Más iteraciones (500)', X0, [lda(X0, s, it=500) for s in SEM])
registrar('Priors dispersos (alfa 0,1; beta 0,01)', X0, [lda(X0, s, a=0.1, b=0.01) for s in SEM])
X1, fn1 = vocab(min_df=5, max_df=0.3, max_features=600)
registrar('Vocabulario estricto (min_df 5, 600 términos)', X1, [lda(X1, s) for s in SEM])
registrar('Combinado (500 it + priors + vocab. estricto)', X1, [lda(X1, s, it=500, a=0.1, b=0.01) for s in SEM])
T1 = TfidfTransformer().fit_transform(X1)
registrar('NMF TF-IDF (inicialización aleatoria)', X1, [NMF(K, init='random', random_state=s, max_iter=1000).fit(T1).components_ for s in SEM])
registrar('NMF TF-IDF (NNDSVD, determinista)', X1, [NMF(K, init='nndsvd', max_iter=1000).fit(T1).components_ for s in SEM])

# LDA de consenso: 10 corridas, se agrupan los 130 tópicos en K grupos y se promedian
def consenso(semillas):
    C = np.vstack([lda(X1, s, it=500, a=0.1, b=0.01) for s in semillas])
    C = C / C.sum(axis=1, keepdims=True)
    lab = AgglomerativeClustering(n_clusters=K, metric='cosine', linkage='average').fit_predict(C)
    return np.vstack([C[lab == g].mean(axis=0) for g in range(K)])
registrar('Consenso de 10 semillas (dos conjuntos distintos)', X1, [consenso(range(0, 10)), consenso(range(10, 20))])
best = consenso(range(0, 10))
EV['topicos_consenso'] = [', '.join(fn1[i] for i in t.argsort()[:-9:-1]) for t in best]
json.dump(EV, open('auditoria/evidencia_estabilidad_lda.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
