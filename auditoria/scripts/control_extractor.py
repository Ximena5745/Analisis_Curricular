"""
Control antes/después de la corrección P2 (src/extractor.py).

Ejecuta el extractor del proyecto sobre los 50 archivos y guarda, por matriz:
columnas del perfil reconocidas, elementos/celdas de perfil, filas por hoja y
si el encabezado real quedó como fila de datos.

Uso:
    python auditoria/scripts/control_extractor.py antes
    python auditoria/scripts/control_extractor.py despues
"""
import glob
import json
import logging
import os
import sys
import warnings

warnings.filterwarnings('ignore')
logging.disable(logging.CRITICAL)
sys.path.insert(0, '.')
from config import COLUMNAS_PERFIL  # noqa: E402
from src.extractor import ExcelExtractor  # noqa: E402
from src.perfil_coverage_analyzer import extraer_elementos_perfil  # noqa: E402

etiqueta = sys.argv[1] if len(sys.argv) > 1 else 'antes'
filas = []
for f in sorted(glob.glob('data/raw/FORMATOS RA CICLO UNO RC/*.xlsx')):
    e = ExcelExtractor(f)
    d = e.extract_all()
    p1, p2, p3, p4, p5 = (d['perfil_egreso'], d['competencias'], d['resultados_aprendizaje'],
                          d['estrategias_meso'], d['estrategias_micro'])

    def tiene_encabezado_como_dato(df, texto):
        return bool(len(df)) and df.astype(str).apply(lambda c: c.str.strip().eq(texto)).any().any()

    filas.append({
        'archivo': os.path.basename(f),
        'p1_campos_perfil_reconocidos': sum(c in p1.columns for c in COLUMNAS_PERFIL),
        'p1_perfil_profesional_celdas': int(p1['Perfil profesional'].notna().sum()) if 'Perfil profesional' in p1 else 0,
        'p1_perfil_ocupacional_celdas': int(p1['Perfil ocupacional'].notna().sum()) if 'Perfil ocupacional' in p1 else 0,
        'p1_elementos_divididos': len(extraer_elementos_perfil(p1)),
        'p2_filas': len(p2), 'p2_tiene_col_redaccion': int('Redacción competencia' in p2.columns),
        'p2_competencias': int(p2['Redacción competencia'].notna().sum()) if 'Redacción competencia' in p2 else None,
        'p3_filas': len(p3), 'p4_filas': len(p4), 'p4_tiene_col_estrategia': int('Estrategia del programa' in p4.columns),
        'p4_encabezado_como_dato': int(tiene_encabezado_como_dato(p4, 'Resultado de aprendizaje')),
        'p5_filas': len(p5),
    })
tot = {k: sum(x[k] for x in filas if isinstance(x[k], (int, bool)) and x[k] is not None)
       for k in filas[0] if k != 'archivo'}
json.dump({'etiqueta': etiqueta, 'totales': tot, 'por_matriz': filas},
          open(f'auditoria/control_extractor_{etiqueta}.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
sys.stdout.reconfigure(encoding='utf-8')
print(etiqueta, json.dumps(tot, ensure_ascii=False, indent=1))
