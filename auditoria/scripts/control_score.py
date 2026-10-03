"""
Control antes/después de los ajustes E3 (puntaje de calidad, src/analyzer.py).

Ejecuta extractor + CurricularAnalyzer sobre los 50 archivos y guarda, por
matriz, el puntaje total y cada componente.

Uso:
    python auditoria/scripts/control_score.py antes
    python auditoria/scripts/control_score.py despues
"""
import glob
import json
import logging
import os
import statistics
import sys
import warnings

warnings.filterwarnings('ignore')
logging.disable(logging.CRITICAL)
sys.path.insert(0, '.')
from src.analyzer import CurricularAnalyzer  # noqa: E402
from src.extractor import ExcelExtractor  # noqa: E402

etiqueta = sys.argv[1] if len(sys.argv) > 1 else 'antes'
filas = []
for f in sorted(glob.glob('data/raw/FORMATOS RA CICLO UNO RC/*.xlsx')):
    a = CurricularAnalyzer(ExcelExtractor(f).extract_all())
    filas.append({
        'archivo': os.path.basename(f)[10:-5],
        'score_calidad': a.calcular_score_calidad(),
        'completitud': a.calcular_completitud()['completitud_total'],
        'exigencia': a.calcular_complejidad_cognitiva()['indice_complejidad'],
        'balance_desv': a.calcular_balance_tipo_saber().get('desviacion_estandar'),
        'cobertura_comp': a.calcular_cobertura_competencias()['porcentaje_cobertura'],
        'diversidad': a.calcular_diversidad_metodologica()['num_estrategias_unicas'],
    })
ordenados = sorted(filas, key=lambda x: -x['score_calidad'])
for i, x in enumerate(ordenados, 1):
    x['posicion'] = i
res = {'etiqueta': etiqueta,
       'media': {k: round(statistics.mean(x[k] for x in filas), 1) for k in filas[0] if k not in ('archivo', 'posicion')},
       'por_matriz': filas}
json.dump(res, open(f'auditoria/control_score_{etiqueta}.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
sys.stdout.reconfigure(encoding='utf-8')
print(etiqueta, json.dumps(res['media'], ensure_ascii=False))
