"""
Verificación dato a dato de Resultados R8 (asignaturas compartidas, minería de texto).

  1. Cobertura de las 159 homónimas sobre los registros de asignatura (con y sin electivas).
  2. Asignaturas presentes en más programas.
  3. Consistencia de las homónimas (D10): idénticas ≥ 0,95; alta 0,60–0,95; divergentes < 0,60.
  4. Pares con distinto nombre y similitud ≥ 0,60 entre programas distintos (D10), clasificados con regla:
       modalidad   — los nombres coinciden al quitar «virtual»/«presencial»
       variante    — similitud de nombre ≥ 0,85 (errores tipográficos, mayúsculas, singular/plural)
       homologación — el resto
  5. Términos TF-IDF más relevantes del contenido de las asignaturas.

Uso: python auditoria/scripts/verificar_r8.py
Salida: auditoria/evidencia_r8.json
"""
import glob
import json
import logging
import re
import sys
import unicodedata
import warnings
from collections import Counter
from difflib import SequenceMatcher

import pandas as pd

warnings.filterwarnings('ignore')
logging.disable(logging.CRITICAL)
sys.path.insert(0, '.')
from sklearn.feature_extraction.text import TfidfVectorizer  # noqa: E402

from src.extractor import ExcelExtractor  # noqa: E402
from src.shared_subjects_analyzer import consolidar_asignaturas, detectar_asignaturas_compartidas  # noqa: E402
from src.topic_modeler import STOPWORDS  # noqa: E402

sys.stdout.reconfigure(encoding='utf-8')


def norm(t):
    t = unicodedata.normalize('NFKD', str(t)).encode('ascii', 'ignore').decode('ascii').lower()
    return re.sub(r'\s+', ' ', re.sub(r'[^a-z0-9 ]', ' ', t)).strip()


micro = pd.concat([ExcelExtractor(f).extract_estrategias_micro()
                   for f in sorted(glob.glob('data/raw/FORMATOS RA CICLO UNO RC/*.xlsx'))], ignore_index=True)
col = 'Nombre asignatura o módulo'
reg = micro[micro[col].notna() & ~micro[col].astype(str).str.strip().str.fullmatch(r'[\d.,\s]+')].copy()
reg['clave'] = reg[col].map(norm)
# un registro de asignatura = fila con nombre (D6); las filas siguientes del bloque no repiten nombre
prog_por_clave = reg.groupby('clave')['Programa'].nunique()
compartidas = set(prog_por_clave[prog_por_clave > 1].index)
electiva = reg['clave'].str.match(r'^electiva')
EV = {'registros': len(reg), 'denominaciones': reg['clave'].nunique(),
      'denominaciones_en_mas_de_un_programa_con_electivas': len(compartidas),
      'registros_en_compartidas_con_electivas': int(reg['clave'].isin(compartidas).sum()),
      'registros_sin_electivas': int((~electiva).sum())}
comp_sin = {c for c in compartidas if not c.startswith('electiva')}
EV['denominaciones_compartidas_sin_electivas'] = len(comp_sin)
EV['registros_en_compartidas_sin_electivas'] = int(reg['clave'].isin(comp_sin).sum())
EV['top_programas'] = prog_por_clave.sort_values(ascending=False).head(8).to_dict()

r = detectar_asignaturas_compartidas(micro)
hom = r['homonimas']
EV['homonimas'] = {'n': len(hom), 'identicas_ge_095': int((hom['similitud_media'] >= 0.95).sum()) if 'similitud_media' in hom else None}
sim_col = next(c for c in hom.columns if 'simil' in c.lower())
s = hom[sim_col]
EV['homonimas'] = {'n': len(hom), 'identicas': int((s >= 0.95).sum()), 'alta': int(((s >= 0.6) & (s < 0.95)).sum()),
                   'divergentes': int((s < 0.6).sum()), 'media': round(float(s.mean()), 3),
                   'divergentes_lista': hom.loc[s < 0.6].sort_values(sim_col).head(15).to_dict('records')}

inter = r['inter_programa']
pares = inter[(inter['programa_a'] != inter['programa_b']) & (~inter['mismo_nombre'])].copy()
na = next(c for c in pares.columns if c.endswith('_a') and 'asig' in c)
nb = next(c for c in pares.columns if c.endswith('_b') and 'asig' in c)
quitar = lambda t: re.sub(r'\b(virtual|presencial)\b', '', norm(t)).strip()


def clase_par(a, b):
    if quitar(a) == quitar(b):
        return 'Duplicación por modalidad'
    if SequenceMatcher(None, norm(a), norm(b), autojunk=False).ratio() >= 0.85:
        return 'Variante de nombre o error tipográfico'
    return 'Homologación potencial'


pares['clase'] = [clase_par(a, b) for a, b in zip(pares[na], pares[nb])]
EV['pares_distinto_nombre'] = {'n': len(pares), 'asignaturas': len(set(pares[na]) | set(pares[nb])),
                               'por_clase': dict(Counter(pares['clase'])),
                               'ejemplos': {c: pares.loc[pares['clase'] == c, [na, nb]].drop_duplicates().head(8).values.tolist()
                                            for c in pares['clase'].unique()}}

asig = consolidar_asignaturas(micro)
vec = TfidfVectorizer(stop_words=STOPWORDS, max_features=2000, ngram_range=(1, 2), min_df=2)
X = vec.fit_transform(asig['texto'].map(norm))
peso = X.sum(axis=0).A1
EV['tfidf_top'] = [vec.get_feature_names_out()[i] for i in peso.argsort()[::-1][:20]]
json.dump(EV, open('auditoria/evidencia_r8.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=str)
print(json.dumps({k: v for k, v in EV.items() if k not in ('homonimas',)}, ensure_ascii=False, indent=1, default=str)[:4000])
print({k: v for k, v in EV['homonimas'].items() if k != 'divergentes_lista'})
for d in EV['homonimas']['divergentes_lista']:
    print('  DIV', {k: d[k] for k in list(d)[:5]})
