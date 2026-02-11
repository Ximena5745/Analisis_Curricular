"""
Ejemplos de uso del sistema de análisis microcurricular.

Este archivo contiene ejemplos prácticos de cómo usar el sistema
para diferentes casos de uso comunes.
"""

from pathlib import Path
import pandas as pd

# Importar módulos
from src.extractor import ExcelExtractor
from src.analyzer import CurricularAnalyzer
from src.thematic_detector import ThematicDetector
from src.validator import QualityValidator
from src.report_generator import ReportGenerator


def ejemplo_1_analisis_simple():
    """
    EJEMPLO 1: Análisis simple de un programa.
    """
    print("\n" + "="*60)
    print("EJEMPLO 1: Análisis Simple de un Programa")
    print("="*60 + "\n")

    # Ruta al archivo (reemplazar con archivo real)
    archivo = "data/raw/FormatoRA_AdmonEmpresas_PBOG.xlsx"

    if not Path(archivo).exists():
        print(f"⚠️  Archivo no encontrado: {archivo}")
        print("   Reemplaza con la ruta a un archivo real")
        return

    # 1. Extraer datos
    print("1️⃣ Extrayendo datos...")
    extractor = ExcelExtractor(archivo)
    data = extractor.extract_all()
    print(f"   ✅ Extraídas {len(data['competencias'])} competencias")
    print(f"   ✅ Extraídos {len(data['resultados_aprendizaje'])} RA")

    # 2. Analizar indicadores
    print("\n2️⃣ Calculando indicadores...")
    analyzer = CurricularAnalyzer(data)
    indicadores = analyzer.generar_reporte_indicadores()
    print(f"   📊 Score de calidad: {indicadores['score_calidad']}/100")

    # 3. Mostrar reporte textual
    print("\n3️⃣ Reporte completo:")
    print(analyzer.generar_reporte_textual())


def ejemplo_2_deteccion_tematicas():
    """
    EJEMPLO 2: Detectar temáticas en un programa.
    """
    print("\n" + "="*60)
    print("EJEMPLO 2: Detección de Temáticas")
    print("="*60 + "\n")

    archivo = "data/raw/FormatoRA_AdmonEmpresas_PBOG.xlsx"

    if not Path(archivo).exists():
        print(f"⚠️  Archivo no encontrado: {archivo}")
        return

    # Extraer datos
    extractor = ExcelExtractor(archivo)
    data = extractor.extract_all()

    # Detectar temáticas
    print("Detectando temáticas...")
    detector = ThematicDetector()
    tematicas = detector.analyze_programa(data)

    print(f"\n📋 Programa: {tematicas['programa']}")
    print(f"🏷️  Temáticas detectadas: {tematicas['num_tematicas']}\n")

    for tematica in tematicas['tematicas_presentes']:
        resumen = tematicas['resumen'][tematica]
        print(f"  ✅ {tematica}")
        print(f"     - En competencias: {resumen['frecuencia_competencias']}")
        print(f"     - En RA: {resumen['frecuencia_ra']}")
        print(f"     - Total: {resumen['total_coincidencias']}\n")


def ejemplo_3_comparar_programas():
    """
    EJEMPLO 3: Comparar múltiples programas.
    """
    print("\n" + "="*60)
    print("EJEMPLO 3: Comparación de Programas")
    print("="*60 + "\n")

    # Archivos a comparar (reemplazar con archivos reales)
    archivos = [
        "data/raw/FormatoRA_AdmonEmpresas_PBOG.xlsx",
        "data/raw/FormatoRA_IngSistemas_PBOG.xlsx"
    ]

    resultados = []

    for archivo in archivos:
        if not Path(archivo).exists():
            print(f"⚠️  Archivo no encontrado: {archivo}")
            continue

        # Extraer y analizar
        extractor = ExcelExtractor(archivo)
        data = extractor.extract_all()
        analyzer = CurricularAnalyzer(data)
        indicadores = analyzer.generar_reporte_indicadores()

        resultados.append({
            'Programa': data['metadata']['programa'],
            'Score': indicadores['score_calidad'],
            'Competencias': indicadores['resumen']['total_competencias'],
            'RA': indicadores['resumen']['total_ra'],
            'Complejidad_Avanzado_%': indicadores['complejidad_cognitiva']['Avanzado']
        })

    if resultados:
        # Crear DataFrame para comparación
        df = pd.DataFrame(resultados)
        print("📊 COMPARATIVA:\n")
        print(df.to_string(index=False))
    else:
        print("No se pudieron cargar archivos para comparar")


def ejemplo_4_identificar_programas_sin_tematica():
    """
    EJEMPLO 4: Identificar programas que NO abordan una temática específica.
    """
    print("\n" + "="*60)
    print("EJEMPLO 4: Programas sin Sostenibilidad")
    print("="*60 + "\n")

    # Buscar todos los archivos
    input_folder = Path("data/raw")
    archivos = list(input_folder.glob("*.xlsx"))

    if not archivos:
        print(f"⚠️  No se encontraron archivos en {input_folder}")
        return

    print(f"Analizando {len(archivos)} programas...\n")

    detector = ThematicDetector()
    programas_sin_sostenibilidad = []

    for archivo in archivos:
        try:
            extractor = ExcelExtractor(str(archivo))
            data = extractor.extract_all()
            tematicas = detector.analyze_programa(data)

            # Verificar si NO tiene sostenibilidad
            if 'SOSTENIBILIDAD' not in tematicas['tematicas_presentes']:
                programas_sin_sostenibilidad.append(data['metadata']['programa'])

        except Exception as e:
            print(f"⚠️  Error en {archivo.name}: {str(e)}")

    print("📋 PROGRAMAS SIN SOSTENIBILIDAD:\n")
    if programas_sin_sostenibilidad:
        for i, programa in enumerate(programas_sin_sostenibilidad, 1):
            print(f"  {i}. {programa}")
        print(f"\n  Total: {len(programas_sin_sostenibilidad)} programas")
    else:
        print("  ✅ ¡Todos los programas abordan sostenibilidad!")


def ejemplo_5_generar_reportes():
    """
    EJEMPLO 5: Generar reportes en múltiples formatos.
    """
    print("\n" + "="*60)
    print("EJEMPLO 5: Generación de Reportes")
    print("="*60 + "\n")

    archivo = "data/raw/FormatoRA_AdmonEmpresas_PBOG.xlsx"

    if not Path(archivo).exists():
        print(f"⚠️  Archivo no encontrado: {archivo}")
        return

    # Extraer y analizar
    extractor = ExcelExtractor(archivo)
    data = extractor.extract_all()
    analyzer = CurricularAnalyzer(data)
    indicadores = analyzer.generar_reporte_indicadores()
    detector = ThematicDetector()
    tematicas = detector.analyze_programa(data)

    # Generar reportes
    generator = ReportGenerator()
    programa_nombre = data['metadata']['programa']

    # HTML
    print("📄 Generando reporte HTML...")
    html_path = f"data/output/reportes/ejemplo_{programa_nombre}.html"
    generator.generate_html_report(data, indicadores, html_path)
    print(f"   ✅ {html_path}")

    # JSON
    print("\n📄 Generando reporte JSON...")
    json_path = f"data/output/reportes/ejemplo_{programa_nombre}.json"
    generator.generate_json_report(data, indicadores, tematicas, json_path)
    print(f"   ✅ {json_path}")

    print("\n✨ Reportes generados exitosamente!")


def ejemplo_6_validacion_calidad():
    """
    EJEMPLO 6: Validar calidad de redacción de competencias.
    """
    print("\n" + "="*60)
    print("EJEMPLO 6: Validación de Calidad")
    print("="*60 + "\n")

    validator = QualityValidator()

    # Ejemplos de competencias
    competencias_ejemplo = [
        "Analizar estados financieros para tomar decisiones empresariales considerando el contexto económico",
        "Gestionar proyectos",  # Muy corta, sin finalidad
        "Conocer sobre sostenibilidad"  # Verbo no observable
    ]

    for i, competencia in enumerate(competencias_ejemplo, 1):
        print(f"\n{i}. Competencia:")
        print(f"   \"{competencia}\"")

        resultado = validator.validate_competencia_structure(competencia)

        if resultado['valid']:
            print("   ✅ VÁLIDA")
        else:
            print("   ❌ INVÁLIDA")
            print("   Issues:")
            for issue in resultado['issues']:
                print(f"     - {issue}")
            if resultado['suggestions']:
                print("   Sugerencias:")
                for sug in resultado['suggestions']:
                    print(f"     - {sug}")


def menu():
    """
    Menú interactivo de ejemplos.
    """
    print("\n" + "="*60)
    print("  EJEMPLOS DE USO - SISTEMA DE ANÁLISIS MICROCURRICULAR")
    print("="*60)

    ejemplos = {
        '1': ("Análisis simple de un programa", ejemplo_1_analisis_simple),
        '2': ("Detección de temáticas", ejemplo_2_deteccion_tematicas),
        '3': ("Comparar múltiples programas", ejemplo_3_comparar_programas),
        '4': ("Programas sin sostenibilidad", ejemplo_4_identificar_programas_sin_tematica),
        '5': ("Generar reportes en múltiples formatos", ejemplo_5_generar_reportes),
        '6': ("Validación de calidad de competencias", ejemplo_6_validacion_calidad),
        '0': ("Ejecutar todos los ejemplos", None)
    }

    print("\nSelecciona un ejemplo:\n")
    for key, (desc, _) in ejemplos.items():
        print(f"  {key}. {desc}")

    print("\n" + "="*60)

    try:
        opcion = input("\nOpción (0-6): ").strip()

        if opcion == '0':
            # Ejecutar todos
            for key, (desc, func) in ejemplos.items():
                if key != '0' and func:
                    func()
        elif opcion in ejemplos:
            desc, func = ejemplos[opcion]
            if func:
                func()
        else:
            print("Opción inválida")

    except KeyboardInterrupt:
        print("\n\n⚠️  Interrumpido por el usuario")


if __name__ == '__main__':
    # Ejecutar menú interactivo
    menu()

    # O ejecutar ejemplo específico descomentando:
    # ejemplo_1_analisis_simple()
    # ejemplo_2_deteccion_tematicas()
    # ejemplo_3_comparar_programas()
    # ejemplo_4_identificar_programas_sin_tematica()
    # ejemplo_5_generar_reportes()
    # ejemplo_6_validacion_calidad()
