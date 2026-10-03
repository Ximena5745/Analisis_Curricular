"""
Control antes/después de los ajustes de la Etapa 4 (src/perfil_coverage_analyzer.py).

Ejecuta analizar_cobertura_perfil_completa sobre las 50 matrices y guarda
elementos evaluados, alertas de brecha y documentos del corpus, en total y por campo.

Uso:
    python auditoria/scripts/control_cobertura.py antes
    python auditoria/scripts/control_cobertura.py despues
"""
import glob
import json
import logging
import sys
import warnings
from collections import Counter, defaultdict

warnings.filterwarnings('ignore')
logging.disable(logging.CRITICAL)
sys.path.insert(0, '.')
from src.extractor import ExcelExtractor  # noqa: E402
from src.perfil_coverage_analyzer import analizar_cobertura_perfil_completa  # noqa: E402

etiqueta = sys.argv[1] if len(sys.argv) > 1 else 'antes'
tot = Counter()
campo = defaultdict(Counter)
for f in sorted(glob.glob('data/raw/FORMATOS RA CICLO UNO RC/*.xlsx')):
    d = ExcelExtractor(f).extract_all()
    r = analizar_cobertura_perfil_completa(d['perfil_egreso'], d['estrategias_micro'], d['resultados_aprendizaje'])
    tot['elementos'] += r['total_elementos']
    tot['alertas'] += r['num_brechas']
    tot['corpus_docs'] += r.get('corpus_size', 0)
    for e in r['elementos']:
        campo[e['campo']]['elementos'] += 1
        campo[e['campo']]['alertas'] += e['clasificacion'] == 'BRECHA'
res = {'etiqueta': etiqueta, 'elementos': tot['elementos'], 'alertas': tot['alertas'],
       'pct_alertas': round(100 * tot['alertas'] / tot['elementos'], 1) if tot['elementos'] else None,
       'corpus_docs': tot['corpus_docs'],
       'por_campo': {c: {**v, 'pct': round(100 * v['alertas'] / v['elementos'], 1)} for c, v in campo.items()}}
json.dump(res, open(f'auditoria/control_cobertura_{etiqueta}.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
sys.stdout.reconfigure(encoding='utf-8')
print(json.dumps(res, ensure_ascii=False, indent=1))
