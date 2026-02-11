"""
Script de análisis consolidado de Estrategias Microcurriculares (Paso 5).

Consolida todos los programas en un solo archivo y genera análisis específicos.

Uso:
    python analisis_estrategias_micro.py
"""

import pandas as pd
import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Configuración
INPUT_FOLDER = Path('data/raw')
OUTPUT_FOLDER = Path('data/output/analisis_micro')
OUTPUT_FOLDER.mkdir(parents=True, exist_ok=True)

# Estilo para gráficos
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")


def consolidar_estrategias_micro(input_folder: Path) -> pd.DataFrame:
    """
    Consolida la hoja 'Paso 5 Estrategias micro' de todos los archivos Excel.

    Args:
        input_folder: Carpeta con archivos Excel

    Returns:
        DataFrame consolidado con todos los programas
    """
    print("="*60)
    print("  CONSOLIDANDO ESTRATEGIAS MICROCURRICULARES")
    print("="*60 + "\n")

    archivos_excel = list(input_folder.glob('*.xlsx'))
    print(f"Archivos encontrados: {len(archivos_excel)}\n")

    all_data = []

    for archivo in archivos_excel:
        try:
            # Extraer nombre del programa
            programa_nombre = archivo.stem.replace('FormatoRA_', '').replace('_PBOG', '').replace('_VNAL', '').replace('_PMED', '')

            print(f"Procesando: {programa_nombre}...")

            # Leer hoja con header en fila 2 (índice 1)
            df = pd.read_excel(archivo, sheet_name='Paso 5 Estrategias micro', header=1)

            # Agregar columna de programa
            df['Programa'] = programa_nombre

            # Agregar a lista
            all_data.append(df)

            print(f"  OK - {len(df)} registros\n")

        except Exception as e:
            print(f"  [X] Error: {str(e)}\n")

    # Consolidar todo
    df_consolidado = pd.concat(all_data, ignore_index=True)

    print("="*60)
    print(f"TOTAL ANTES DE FILTRAR: {len(df_consolidado)} registros de {len(all_data)} programas")

    # FILTRAR: Excluir filas donde "Tipo de Saber" esté vacío
    registros_antes = len(df_consolidado)
    df_consolidado = df_consolidado[df_consolidado['Tipo de Saber'].notna()]
    df_consolidado = df_consolidado[df_consolidado['Tipo de Saber'].astype(str).str.strip() != '']
    registros_despues = len(df_consolidado)
    registros_eliminados = registros_antes - registros_despues

    print(f"Registros con 'Tipo de Saber' vacio eliminados: {registros_eliminados}")

    # NORMALIZAR: Corregir inconsistencias de mayúsculas/minúsculas
    normalizacion_map = {
        'saber': 'Saber',
        'saberhacer': 'SaberHacer',
        'saberser': 'SaberSer',
        'Saber': 'Saber',
        'SaberHacer': 'SaberHacer',
        'SaberSer': 'SaberSer',
        'Saberhacer': 'SaberHacer',
        'Saberser': 'SaberSer'
    }

    df_consolidado['Tipo de Saber'] = df_consolidado['Tipo de Saber'].astype(str).str.strip().map(
        lambda x: normalizacion_map.get(x, x)
    )

    print(f"Valores normalizados en 'Tipo de Saber'")
    print(f"TOTAL DESPUES DE FILTRAR: {registros_despues} registros")
    print("="*60 + "\n")

    return df_consolidado


def analizar_tipo_saber(df: pd.DataFrame) -> dict:
    """Análisis de distribución de tipos de saber."""
    print("\n[1] ANALISIS: Distribución de Tipos de Saber")
    print("-"*60)

    tipo_saber_counts = df['Tipo de Saber'].value_counts()
    tipo_saber_pct = df['Tipo de Saber'].value_counts(normalize=True) * 100

    resultado = {
        'counts': tipo_saber_counts.to_dict(),
        'porcentajes': tipo_saber_pct.to_dict()
    }

    print("\nDistribución Global:")
    for tipo, count in tipo_saber_counts.items():
        pct = tipo_saber_pct[tipo]
        print(f"  {tipo:15} {count:4} ({pct:5.1f}%)")

    # Por programa
    print("\nDistribución por Programa:")
    tipo_por_programa = pd.crosstab(df['Programa'], df['Tipo de Saber'], normalize='index') * 100
    print(tipo_por_programa.round(1).to_string())

    return resultado


def analizar_semestres(df: pd.DataFrame) -> dict:
    """Análisis de distribución por semestres."""
    print("\n\n[2] ANALISIS: Distribución por Semestres")
    print("-"*60)

    # Limpiar datos de semestre
    df['Semestre_Clean'] = pd.to_numeric(df['Semestre'], errors='coerce')

    semestre_counts = df['Semestre_Clean'].value_counts().sort_index()

    print("\nActividades por Semestre:")
    for sem, count in semestre_counts.items():
        if not pd.isna(sem):
            print(f"  Semestre {int(sem):2}: {count:4} actividades")

    # Promedio de actividades por semestre por programa
    print("\nPromedio de actividades por semestre:")
    avg_por_programa = df.groupby('Programa')['Semestre_Clean'].value_counts().groupby('Programa').mean()
    for prog, avg in avg_por_programa.items():
        print(f"  {prog:20} {avg:5.1f} actividades/semestre")

    return {'semestre_counts': semestre_counts.to_dict()}


def analizar_creditos_horas(df: pd.DataFrame) -> dict:
    """Análisis de créditos y horas."""
    print("\n\n[3] ANALISIS: Créditos y Horas de Trabajo")
    print("-"*60)

    # Limpiar datos numéricos
    df['Creditos_Clean'] = pd.to_numeric(df['Créditos'], errors='coerce')
    df['Horas_Directas_Clean'] = pd.to_numeric(df['Número de horas trabajo directo'], errors='coerce')
    df['Horas_Independientes_Clean'] = pd.to_numeric(df['Número de horas trabajo independiente'], errors='coerce')
    df['Total_Horas_Clean'] = pd.to_numeric(df['Total de horas'], errors='coerce')

    # Estadísticas por programa
    print("\nEstadísticas de Créditos por Programa:")
    creditos_stats = df.groupby('Programa')['Creditos_Clean'].agg(['sum', 'mean', 'count'])
    creditos_stats.columns = ['Total_Creditos', 'Promedio_Creditos', 'Num_Asignaturas']
    print(creditos_stats.round(2).to_string())

    print("\n\nDistribución de Horas:")
    print(f"  Total Horas Directas:      {df['Horas_Directas_Clean'].sum():,.0f}")
    print(f"  Total Horas Independientes: {df['Horas_Independientes_Clean'].sum():,.0f}")
    print(f"  Total General:             {df['Total_Horas_Clean'].sum():,.0f}")

    # Ratio horas independientes vs directas
    print("\n\nRatio Horas Independientes / Directas por Programa:")
    for programa in df['Programa'].unique():
        df_prog = df[df['Programa'] == programa]
        directas = df_prog['Horas_Directas_Clean'].sum()
        independientes = df_prog['Horas_Independientes_Clean'].sum()
        if directas > 0:
            ratio = independientes / directas
            print(f"  {programa:20} {ratio:5.2f}:1")

    return {
        'creditos_stats': creditos_stats.to_dict(),
        'total_horas_directas': float(df['Horas_Directas_Clean'].sum()),
        'total_horas_independientes': float(df['Horas_Independientes_Clean'].sum())
    }


def analizar_tipologia(df: pd.DataFrame) -> dict:
    """Análisis de tipología de asignaturas."""
    print("\n\n[4] ANALISIS: Tipología de Asignaturas")
    print("-"*60)

    if 'Tipología' in df.columns:
        tipo_counts = df['Tipología'].value_counts()

        print("\nDistribución de Tipologías:")
        for tipo, count in tipo_counts.items():
            pct = (count / len(df)) * 100
            print(f"  {str(tipo)[:30]:30} {count:4} ({pct:5.1f}%)")

        return {'tipologia_counts': tipo_counts.to_dict()}
    else:
        print("  [!] Columna 'Tipología' no encontrada")
        return {}


def analizar_componentes_formacion(df: pd.DataFrame) -> dict:
    """Análisis de componentes de formación (Institucional, Disciplinar, Electivo)."""
    print("\n\n[5] ANALISIS: Componentes de Formación")
    print("-"*60)

    componentes = ['B.Institucional', 'B.Disciplinar', 'B.Electivo']

    # Contar por programa
    print("\nDistribución de Componentes por Programa:")

    for programa in df['Programa'].unique():
        df_prog = df[df['Programa'] == programa]
        print(f"\n  {programa}:")

        for comp in componentes:
            if comp in df.columns:
                # Contar valores no nulos y no vacíos
                count = df_prog[comp].notna().sum()
                pct = (count / len(df_prog)) * 100
                print(f"    {comp:20} {count:4} ({pct:5.1f}%)")

    return {}


def analizar_actividades_aprendizaje(df: pd.DataFrame) -> dict:
    """Análisis de actividades de aprendizaje más frecuentes."""
    print("\n\n[6] ANALISIS: Actividades de Aprendizaje")
    print("-"*60)

    if 'Actividades de aprendizaje' in df.columns:
        # Extraer actividades únicas
        actividades = df['Actividades de aprendizaje'].dropna().astype(str)

        # Palabras clave para identificar metodologías
        metodologias = {
            'Clase magistral': ['magistral', 'exposicion', 'clase teorica'],
            'Taller': ['taller', 'practica'],
            'Proyecto': ['proyecto', 'pbl', 'aprendizaje basado en proyectos'],
            'Caso de estudio': ['caso', 'estudio de caso'],
            'Debate': ['debate', 'discusion'],
            'Investigación': ['investigacion', 'indagacion'],
            'Trabajo colaborativo': ['colaborativo', 'grupal', 'equipo'],
            'Simulación': ['simulacion', 'juego de rol']
        }

        # Contar menciones
        print("\nMetodologías Detectadas (por menciones en textos):")
        for metodo, keywords in metodologias.items():
            count = sum(actividades.str.lower().str.contains('|'.join(keywords), na=False))
            if count > 0:
                pct = (count / len(actividades)) * 100
                print(f"  {metodo:25} {count:4} menciones ({pct:5.1f}%)")

        return {}
    else:
        print("  [!] Columna 'Actividades de aprendizaje' no encontrada")
        return {}


def generar_visualizaciones(df: pd.DataFrame, output_folder: Path):
    """Genera gráficos de análisis."""
    print("\n\n[7] GENERANDO VISUALIZACIONES")
    print("-"*60)

    # 1. Distribución de Tipos de Saber
    fig, ax = plt.subplots(figsize=(10, 6))
    tipo_saber_counts = df['Tipo de Saber'].value_counts()
    tipo_saber_counts.plot(kind='bar', ax=ax, color=['#3498db', '#e74c3c', '#2ecc71'])
    ax.set_title('Distribución de Tipos de Saber', fontsize=14, fontweight='bold')
    ax.set_xlabel('Tipo de Saber', fontsize=12)
    ax.set_ylabel('Número de Actividades', fontsize=12)
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig(output_folder / 'grafico_1_tipos_saber.png', dpi=300, bbox_inches='tight')
    print(f"  [OK] grafico_1_tipos_saber.png")
    plt.close()

    # 2. Créditos por Programa
    fig, ax = plt.subplots(figsize=(12, 6))
    df_creditos = df.groupby('Programa')['Créditos'].apply(lambda x: pd.to_numeric(x, errors='coerce').sum())
    df_creditos.sort_values(ascending=False).plot(kind='barh', ax=ax, color='#9b59b6')
    ax.set_title('Total de Créditos por Programa', fontsize=14, fontweight='bold')
    ax.set_xlabel('Créditos Totales', fontsize=12)
    ax.set_ylabel('Programa', fontsize=12)
    plt.tight_layout()
    plt.savefig(output_folder / 'grafico_2_creditos_programa.png', dpi=300, bbox_inches='tight')
    print(f"  [OK] grafico_2_creditos_programa.png")
    plt.close()

    # 3. Distribución por Semestre
    fig, ax = plt.subplots(figsize=(10, 6))
    semestre_clean = pd.to_numeric(df['Semestre'], errors='coerce')
    semestre_counts = semestre_clean.value_counts().sort_index()
    semestre_counts.plot(kind='line', marker='o', ax=ax, color='#e67e22', linewidth=2, markersize=8)
    ax.set_title('Distribución de Actividades por Semestre', fontsize=14, fontweight='bold')
    ax.set_xlabel('Semestre', fontsize=12)
    ax.set_ylabel('Número de Actividades', fontsize=12)
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(output_folder / 'grafico_3_semestres.png', dpi=300, bbox_inches='tight')
    print(f"  [OK] grafico_3_semestres.png")
    plt.close()

    # 4. Horas Directas vs Independientes
    fig, ax = plt.subplots(figsize=(10, 6))
    horas_data = df.groupby('Programa').agg({
        'Número de horas trabajo directo': lambda x: pd.to_numeric(x, errors='coerce').sum(),
        'Número de horas trabajo independiente': lambda x: pd.to_numeric(x, errors='coerce').sum()
    })
    horas_data.plot(kind='bar', ax=ax, color=['#3498db', '#e74c3c'])
    ax.set_title('Horas de Trabajo por Programa', fontsize=14, fontweight='bold')
    ax.set_xlabel('Programa', fontsize=12)
    ax.set_ylabel('Total de Horas', fontsize=12)
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha='right')
    ax.legend(['Trabajo Directo', 'Trabajo Independiente'])
    plt.tight_layout()
    plt.savefig(output_folder / 'grafico_4_horas_trabajo.png', dpi=300, bbox_inches='tight')
    print(f"  [OK] grafico_4_horas_trabajo.png")
    plt.close()

    print("\n  [*] Todas las visualizaciones generadas exitosamente\n")


def generar_reporte_excel(df: pd.DataFrame, analisis_results: dict, output_folder: Path):
    """Genera archivo Excel consolidado con múltiples hojas."""
    print("\n[8] GENERANDO ARCHIVO EXCEL CONSOLIDADO")
    print("-"*60)

    output_file = output_folder / f'consolidado_estrategias_micro_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'

    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        # Hoja 1: Datos consolidados completos
        df.to_excel(writer, sheet_name='Datos Consolidados', index=False)
        print(f"  [OK] Hoja 'Datos Consolidados' - {len(df)} registros")

        # Hoja 2: Resumen por Programa
        resumen_programa = df.groupby('Programa').agg({
            'Tipo de Saber': 'count',
            'Semestre': lambda x: pd.to_numeric(x, errors='coerce').nunique(),
            'Créditos': lambda x: pd.to_numeric(x, errors='coerce').sum(),
            'Número de horas trabajo directo': lambda x: pd.to_numeric(x, errors='coerce').sum(),
            'Número de horas trabajo independiente': lambda x: pd.to_numeric(x, errors='coerce').sum(),
            'Total de horas': lambda x: pd.to_numeric(x, errors='coerce').sum()
        })
        resumen_programa.columns = ['Total_Actividades', 'Num_Semestres', 'Total_Creditos',
                                    'Horas_Directas', 'Horas_Independientes', 'Total_Horas']
        resumen_programa.to_excel(writer, sheet_name='Resumen por Programa')
        print(f"  [OK] Hoja 'Resumen por Programa' - {len(resumen_programa)} programas")

        # Hoja 3: Distribución Tipo de Saber
        tipo_saber_matrix = pd.crosstab(df['Programa'], df['Tipo de Saber'], margins=True)
        tipo_saber_matrix.to_excel(writer, sheet_name='Distribucion Tipo Saber')
        print(f"  [OK] Hoja 'Distribucion Tipo Saber'")

        # Hoja 4: Listado de Asignaturas Únicas
        asignaturas = df[['Programa', 'Nombre asignatura o módulo', 'Semestre', 'Créditos']].drop_duplicates()
        asignaturas = asignaturas.sort_values(['Programa', 'Semestre'])
        asignaturas.to_excel(writer, sheet_name='Asignaturas', index=False)
        print(f"  [OK] Hoja 'Asignaturas' - {len(asignaturas)} asignaturas únicas")

    print(f"\n  [*] Archivo guardado: {output_file.name}\n")
    return output_file


def main():
    """Función principal."""
    print("\n" + "="*60)
    print("  ANALISIS DE ESTRATEGIAS MICROCURRICULARES")
    print("  Consolidación y Análisis de Paso 5")
    print("="*60)
    print(f"  Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60 + "\n")

    # 1. Consolidar datos
    df_consolidado = consolidar_estrategias_micro(INPUT_FOLDER)

    # 2. Ejecutar análisis
    analisis_results = {}

    analisis_results['tipo_saber'] = analizar_tipo_saber(df_consolidado)
    analisis_results['semestres'] = analizar_semestres(df_consolidado)
    analisis_results['creditos_horas'] = analizar_creditos_horas(df_consolidado)
    analizar_tipologia(df_consolidado)
    analizar_componentes_formacion(df_consolidado)
    analizar_actividades_aprendizaje(df_consolidado)

    # 3. Generar visualizaciones
    generar_visualizaciones(df_consolidado, OUTPUT_FOLDER)

    # 4. Generar Excel consolidado
    output_file = generar_reporte_excel(df_consolidado, analisis_results, OUTPUT_FOLDER)

    # Resumen final
    print("="*60)
    print("  RESUMEN FINAL")
    print("="*60)
    print(f"\n  Total registros consolidados: {len(df_consolidado):,}")
    print(f"  Total programas analizados:   {df_consolidado['Programa'].nunique()}")
    print(f"  Total asignaturas únicas:     {df_consolidado['Nombre asignatura o módulo'].nunique()}")
    print(f"\n  Archivos generados:")
    print(f"    - {output_file.name}")
    print(f"    - 4 gráficos PNG")
    print(f"\n  Ubicación: {OUTPUT_FOLDER}")
    print("\n" + "="*60)
    print("  [*] ANALISIS COMPLETADO EXITOSAMENTE")
    print("="*60 + "\n")


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"\n[X] Error fatal: {str(e)}")
        import traceback
        traceback.print_exc()
