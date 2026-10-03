"""
Control antes/después de los ajustes de la Etapa 5 (src/shared_subjects_analyzer.py).

Consolida el Paso 5 de las 50 matrices con el extractor del proyecto, ejecuta
detectar_asignaturas_compartidas y guarda el resumen y los totales.

Uso:
    python auditoria/scripts/control_asignaturas.py antes
    python auditoria/scripts/control_asignaturas.py despues
"""
import glob
import json
import logging
import sys
import time
import warnings

warnings.filterwarnings('ignore')
logging.disable(logging.CRITICAL)
sys.path.insert(0, '.')
import pandas as pd  # noqa: E402

from src.extractor import ExcelExtractor  # noqa: E402
from src.shared_subjects_analyzer import detectar_asignaturas_compartidas  # noqa: E402

etiqueta = sys.argv[1] if len(sys.argv) > 1 else 'antes'
micro = pd.concat([ExcelExtractor(f).extract_estrategias_micro()
                   for f in sorted(glob.glob('data/raw/FORMATOS RA CICLO UNO RC/*.xlsx'))], ignore_index=True)
t0 = time.time()
r = detectar_asignaturas_compartidas(micro)
res = {'etiqueta': etiqueta, 'segundos': round(time.time() - t0, 1),
       'resumen': {k: (float(v) if isinstance(v, (int, float)) else str(v)) for k, v in r.get('resumen', {}).items()},
       'filas': {k: len(v) for k, v in r.items() if isinstance(v, pd.DataFrame)}}
inter = r.get('inter_programa', pd.DataFrame())
if not inter.empty:
    res['inter_programas_distintos'] = int((inter['programa_a'] != inter['programa_b']).sum()) if 'programa_a' in inter else None
    if 'mismo_nombre' in inter:
        res['inter_nombres_distintos'] = int((~inter['mismo_nombre']).sum())
hom = r.get('homonimas', pd.DataFrame())
if not hom.empty:
    res['homonimas'] = {'asignaturas': len(hom), 'divergentes': int(hom['divergente'].sum()),
                        'pct': round(100 * hom['divergente'].mean(), 1)}
json.dump(res, open(f'auditoria/control_asignaturas_{etiqueta}.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
sys.stdout.reconfigure(encoding='utf-8')
print(json.dumps(res, ensure_ascii=False, indent=1))
