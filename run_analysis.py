"""
Script principal para ejecutar análisis completo de todos los programas.

Uso:
    python run_analysis.py
"""

import logging
from pathlib import Path
from datetime import datetime
import sys

# Agregar src al path
sys.path.append(str(Path(__file__).parent))

from src.extractor import ExcelExtractor
from src.analyzer import CurricularAnalyzer
from src.thematic_detector import ThematicDetector
from src.validator import QualityValidator
from src.report_generator import ReportGenerator
from config import INPUT_FOLDER, OUTPUT_FOLDER, MESSAGES

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(Path(__file__).parent / 'logs' / f'analisis_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def print_header():
    """Imprime encabezado del script."""
    print(MESSAGES['BIENVENIDA'])
    print(f"Fecha y hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")


def process_single_program(file_path: Path, detector: ThematicDetector,
                          generator: ReportGenerator) -> dict:
    """
    Procesa un programa individual.

    Args:
        file_path (Path): Ruta al archivo Excel
        detector (ThematicDetector): Detector de temáticas
        generator (ReportGenerator): Generador de reportes

    Returns:
        dict: Reporte del programa o None si hubo error
    """
    try:
        logger.info(f"Procesando: {file_path.name}")
        print(f"  [DIR] {file_path.name}...")

        # 1. Extraer datos
        extractor = ExcelExtractor(str(file_path))
        data = extractor.extract_all()

        # Validar estructura
        validation = extractor.validate_structure()
        if not validation['valid']:
            logger.warning(f"Archivo con errores: {file_path.name}")
            logger.warning(f"Errores: {validation['errors']}")
            print(f"    [!]  Advertencia: Archivo con errores estructurales")

        # 2. Analizar indicadores
        analyzer = CurricularAnalyzer(data)
        indicadores = analyzer.generar_reporte_indicadores()

        # 3. Detectar temáticas
        tematicas = detector.analyze_programa(data)

        # 4. Validar calidad
        validator = QualityValidator()
        validacion = validator.validate_programa_completo(data)

        # 5. Generar reportes individuales
        programa_nombre = data['metadata']['programa']

        # HTML
        html_path = OUTPUT_FOLDER / 'reportes' / f'reporte_{programa_nombre}.html'
        generator.generate_html_report(data, indicadores, str(html_path))

        # JSON
        json_path = OUTPUT_FOLDER / 'reportes' / f'reporte_{programa_nombre}.json'
        generator.generate_json_report(data, indicadores, tematicas, str(json_path))

        print(f"    [OK] Completado - Score: {indicadores['score_calidad']}/100")
        print(f"       Temáticas: {len(tematicas['tematicas_presentes'])}")

        # Combinar todos los datos para reporte consolidado
        return {
            'data': data,
            'indicadores': indicadores,
            'tematicas': tematicas,
            'validacion': validacion
        }

    except Exception as e:
        logger.error(f"Error procesando {file_path.name}: {str(e)}", exc_info=True)
        print(f"    [X] Error: {str(e)}")
        return None


def main():
    """Función principal."""
    print_header()

    # Crear carpetas necesarias
    (Path(__file__).parent / 'logs').mkdir(exist_ok=True)
    (OUTPUT_FOLDER / 'reportes').mkdir(parents=True, exist_ok=True)
    (OUTPUT_FOLDER / 'matrices').mkdir(parents=True, exist_ok=True)
    (OUTPUT_FOLDER / 'consolidado').mkdir(parents=True, exist_ok=True)

    # Buscar archivos Excel
    input_folder = Path(INPUT_FOLDER)
    excel_files = list(input_folder.glob('*.xlsx'))

    if not excel_files:
        print(f"[X] No se encontraron archivos Excel en: {input_folder}")
        print(f"   Coloca los archivos en la carpeta '{INPUT_FOLDER}'")
        return

    print(f"[FOLDER] Encontrados {len(excel_files)} archivos para procesar\n")

    # Inicializar procesadores
    detector = ThematicDetector()
    generator = ReportGenerator()

    # Procesar cada archivo
    print("="*60)
    print("PROCESANDO PROGRAMAS")
    print("="*60 + "\n")

    all_results = []
    errors = 0

    for idx, file_path in enumerate(excel_files, 1):
        print(f"[{idx}/{len(excel_files)}]", end=" ")

        result = process_single_program(file_path, detector, generator)

        if result:
            all_results.append(result)
        else:
            errors += 1

        print()

    # Generar reportes consolidados
    print("="*60)
    print("GENERANDO REPORTES CONSOLIDADOS")
    print("="*60 + "\n")

    if all_results:
        # 1. Matriz de temáticas
        print("[DATA] Generando matriz de temáticas...")
        all_data = [r['data'] for r in all_results]
        matriz = detector.generate_thematic_matrix(all_data)
        matriz_path = OUTPUT_FOLDER / 'matrices' / 'matriz_tematicas.xlsx'
        generator.generate_excel_matrix(matriz, str(matriz_path))
        print(f"   [OK] Guardado en: {matriz_path}\n")

        # 2. Excel consolidado de indicadores
        print("[DATA] Generando Excel consolidado de indicadores...")
        all_indicadores = [r['indicadores'] for r in all_results]
        consolidado_path = OUTPUT_FOLDER / 'consolidado' / 'indicadores_consolidados.xlsx'
        generator.generate_consolidated_excel(all_indicadores, str(consolidado_path))
        print(f"   [OK] Guardado en: {consolidado_path}\n")

        # 3. Reporte resumen de temáticas
        print("[LIST] Generando reporte de temáticas...")
        resumen_tematicas = detector.generate_summary_report(matriz)
        print(resumen_tematicas)

    # Resumen final
    print("="*60)
    print("RESUMEN FINAL")
    print("="*60)
    print(f"\n[OK] Programas procesados exitosamente: {len(all_results)}")
    print(f"[X] Programas con errores: {errors}")
    print(f"[DATA] Total de archivos: {len(excel_files)}")
    print(f"\n[FOLDER] Resultados guardados en: {OUTPUT_FOLDER}")
    print(f"   - Reportes individuales: {OUTPUT_FOLDER / 'reportes'}")
    print(f"   - Matrices consolidadas: {OUTPUT_FOLDER / 'matrices'}")
    print(f"   - Datos consolidados: {OUTPUT_FOLDER / 'consolidado'}")

    if all_results:
        # Calcular estadísticas generales
        scores = [r['indicadores']['score_calidad'] for r in all_results]
        print(f"\n[CHART] ESTADÍSTICAS GENERALES:")
        print(f"   - Score promedio: {sum(scores)/len(scores):.1f}/100")
        print(f"   - Score máximo: {max(scores):.1f}/100")
        print(f"   - Score mínimo: {min(scores):.1f}/100")

        # Top 5 programas por score
        sorted_results = sorted(all_results,
                               key=lambda x: x['indicadores']['score_calidad'],
                               reverse=True)
        print(f"\n[TOP] TOP 5 PROGRAMAS (por Score de Calidad):")
        for i, r in enumerate(sorted_results[:5], 1):
            programa = r['data']['metadata']['programa']
            score = r['indicadores']['score_calidad']
            print(f"   {i}. {programa}: {score}/100")

    print(f"\n[*] Análisis completado exitosamente!")
    print(f"[LOG] Log guardado en: logs/")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[!]  Proceso interrumpido por el usuario")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error fatal: {str(e)}", exc_info=True)
        print(f"\n[X] Error fatal: {str(e)}")
        sys.exit(1)
