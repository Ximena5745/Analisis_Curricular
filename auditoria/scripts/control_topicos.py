"""
Control de la Etapa 6 (P14): ejecuta src.topic_modeler.modelar_topicos_consenso sobre
las 50 matrices, dos veces con conjuntos de semillas distintos, y mide la coincidencia
de las 10 palabras principales entre ambos consensos.

Uso: python auditoria/scripts/control_topicos.py
Salida: auditoria/control_topicos_despues.json
"""
import glob, json, logging, sys, warnings
warnings.filterwarnings('ignore'); logging.disable(logging.CRITICAL); sys.path.insert(0, '.')
import numpy as np
import pandas as pd
from src.extractor import ExcelExtractor
from src.topic_modeler import modelar_topicos_consenso

sys.stdout.reconfigure(encoding='utf-8')
micro = pd.concat([ExcelExtractor(f).extract_estrategias_micro()
                   for f in sorted(glob.glob('data/raw/FORMATOS RA CICLO UNO RC/*.xlsx'))], ignore_index=True)
a = modelar_topicos_consenso(micro)
b = modelar_topicos_consenso(micro, semillas=range(10, 20))
ta = [set(t['top_words'][:10]) for t in a['topics']]
tb = [set(t['top_words'][:10]) for t in b['topics']]
jac = [max(len(x & y) / len(x | y) for y in tb) for x in ta]
res = {'asignaturas': a['corpus_size'], 'programas': int(a['asignatura_topico']['Programa'].nunique()), 'k': a['k'],
       'jaccard_entre_consensos': round(float(np.mean(jac)), 3),
       'topicos_estables_ge_0_5': f'{sum(j >= 0.5 for j in jac)}/{len(jac)}',
       'asignaturas_por_topico': a['asignatura_topico']['topico_dominante'].add(1).value_counts().sort_index().to_dict(),
       'confianza_media': round(float(a['asignatura_topico']['confianza'].mean()), 3),
       'topicos': [f"{t['topic_id'] + 1}: {', '.join(t['top_words'][:8])}" for t in a['topics']]}
res['asignaturas_por_topico'] = {str(k): int(v) for k, v in res['asignaturas_por_topico'].items()}
json.dump(res, open('auditoria/control_topicos_despues.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(json.dumps(res, ensure_ascii=False, indent=1))
