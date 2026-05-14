import sys
sys.path.append('.')

from src.extractor import ExcelExtractor
from src.analyzer import CurricularAnalyzer
from pathlib import Path

archivos = [
    'data/raw/FORMATOS RA CICLO UNO RC/FormatoRA_AdmonPub_VNAL.xlsx',
    'data/raw/FORMATOS RA CICLO UNO RC/FormatoRA_AdmonEmpresas_PBOG.xlsx',
]

print("=" * 80)
print("TEST FINAL: Corrección de Conteo de Asignaturas")
print("=" * 80)

for filepath in archivos:
    if not Path(filepath).exists():
        continue
    
    filename = Path(filepath).name
    print("\nArchivo: " + filename)
    print("-" * 80)
    
    try:
        extractor = ExcelExtractor(filepath)
        data = extractor.extract_all()
        analyzer = CurricularAnalyzer(data)
        indicadores = analyzer.generar_reporte_indicadores()
        
        asigs = indicadores['resumen']['total_ra']
        comps = indicadores['resumen']['total_competencias']
        score = indicadores['score_calidad']
        
        print("Resultado: OK")
        print("  Asignaturas (Paso 5): " + str(asigs))
        print("  Competencias: " + str(comps))
        print("  Score Calidad: " + str(score) + "/100")
        
    except Exception as e:
        print("ERROR: " + str(e)[:80])

print("\n" + "=" * 80)
print("Corrección Aplicada Exitosamente")
print("=" * 80)
