"""
Script para validar estructura de archivos Excel microcurriculares.

Verifica que los archivos tengan la estructura esperada antes de procesarlos.

Uso:
    python validate_files.py
"""

import sys
from pathlib import Path
from datetime import datetime

sys.path.append(str(Path(__file__).parent))

from src.extractor import ExcelExtractor
from config import INPUT_FOLDER


def print_header():
    """Imprime encabezado."""
    print("=" * 60)
    print("  VALIDACION DE ARCHIVOS EXCEL")
    print("=" * 60 + "\n")
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")


def validate_file(file_path: Path) -> dict:
    """
    Valida un archivo Excel.

    Args:
        file_path (Path): Ruta al archivo

    Returns:
        dict: Resultado de validación
    """
    try:
        extractor = ExcelExtractor(str(file_path))
        validation = extractor.validate_structure()
        return validation
    except Exception as e:
        return {
            'valid': False,
            'errors': [f"Error al abrir archivo: {str(e)}"],
            'warnings': [],
            'info': {}
        }


def main():
    """Función principal."""
    print_header()

    input_folder = Path(INPUT_FOLDER)
    print(f"Analizando archivos en: {input_folder}\n")

    # Buscar archivos Excel
    excel_files = list(input_folder.glob('*.xlsx'))

    if not excel_files:
        print(f"[X] No se encontraron archivos Excel en: {input_folder}")
        return

    print(f"Encontrados {len(excel_files)} archivos\n")
    print("="*60)

    # Validar cada archivo
    results = {
        'validos': [],
        'con_advertencias': [],
        'con_errores': []
    }

    for file_path in excel_files:
        print(f"\n[FILE] {file_path.name}")

        validation = validate_file(file_path)

        # Clasificar resultado
        if validation['valid'] and not validation['warnings']:
            results['validos'].append(file_path.name)
            print("   [OK] OK")

        elif validation['valid'] and validation['warnings']:
            results['con_advertencias'].append(file_path.name)
            print("   [!]  Advertencias:")
            for warning in validation['warnings']:
                print(f"      - {warning}")

        else:
            results['con_errores'].append(file_path.name)
            print("   [X] Errores:")
            for error in validation['errors']:
                print(f"      - {error}")

        # Mostrar info adicional
        if validation['info']:
            info = validation['info']
            if 'num_competencias' in info:
                print(f"      Competencias: {info['num_competencias']}")
            if 'num_resultados_aprendizaje' in info:
                print(f"      RA: {info['num_resultados_aprendizaje']}")

    # Resumen
    print("\n" + "="*60)
    print("RESUMEN")
    print("="*60)
    print(f"\n  Total archivos: {len(excel_files)}")
    print(f"  [OK] Válidos: {len(results['validos'])}")
    print(f"  [!]  Con advertencias: {len(results['con_advertencias'])}")
    print(f"  [X] Con errores: {len(results['con_errores'])}")

    # Mostrar archivos con errores
    if results['con_errores']:
        print(f"\n[!]  ARCHIVOS CON ERRORES:")
        for filename in results['con_errores']:
            print(f"     - {filename}")

        # Guardar lista de errores
        error_file = Path('data/output/validacion_errores.txt')
        error_file.parent.mkdir(parents=True, exist_ok=True)
        with open(error_file, 'w', encoding='utf-8') as f:
            f.write(f"Archivos con errores - {datetime.now()}\n")
            f.write("="*60 + "\n\n")
            for filename in results['con_errores']:
                f.write(f"- {filename}\n")

        print(f"\n   Lista guardada en: {error_file}")

    # Recomendaciones
    if results['con_errores']:
        print(f"\n[TIP] RECOMENDACIÓN:")
        print(f"   Revisa los archivos con errores antes de ejecutar el análisis completo.")
        print(f"   Puedes ejecutar: python run_analysis.py")
        print(f"   El sistema procesará solo los archivos válidos.")
    else:
        print(f"\n[*] ¡Todos los archivos están listos para procesar!")
        print(f"   Ejecuta: python run_analysis.py")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[!]  Validación interrumpida")
        sys.exit(1)
    except Exception as e:
        print(f"\n[X] Error: {str(e)}")
        sys.exit(1)
