"""
Script de comparativo: Paso 3 (INCORRECTO) vs Paso 5 (CORRECTO)
Verifica la discrepancia en conteo de asignaturas
"""
import pandas as pd
import unicodedata
import sys
from pathlib import Path
from collections import Counter

sys.path.append(str(Path(__file__).parent))

from src.extractor import ExcelExtractor
from src.analyzer import CurricularAnalyzer

def _normalize_column_name(name):
    if pd.isna(name):
        return ''
    normalized = unicodedata.normalize('NFKD', str(name))
    normalized = ''.join(c for c in normalized if not unicodedata.combining(c))
    return normalized.lower().replace(' ', '').replace('_', '').replace('-', '')

def _normalize_value(value):
    normalized = unicodedata.normalize('NFKD', str(value))
    normalized = ''.join(c for c in normalized if not unicodedata.combining(c))
    normalized = normalized.lower()
    normalized = ''.join(c for c in normalized if c.isalnum())
    return normalized

# Archivos de prueba
archivos_test = [
    'data/raw/FORMATOS RA CICLO UNO RC/FormatoRA_AdmonPub_VNAL.xlsx',
    'data/raw/FORMATOS RA CICLO UNO RC/FormatoRA_AdmonEmpresas_PBOG.xlsx',
    'data/raw/FORMATOS RA CICLO UNO RC/FormatoRA_ContPub_VNAL.xlsx',
]

print("=" * 120)
print("COMPARATIVO: Paso 3 (INCORRECTO) vs Paso 5 (CORRECTO)")
print("=" * 120)

resultados = []

for filepath in archivos_test:
    if not Path(filepath).exists():
        continue
    
    filename = Path(filepath).name
    print(f"\n{'=' * 120}")
    print(f"Archivo: {filename}")
    print('=' * 120)
    
    # === LÓGICA ACTUAL (INCORRECTA - Paso 3) ===
    print("\n1️⃣  LÓGICA ACTUAL (INCORRECTA): Paso 3 - Resultados de Aprendizaje")
    print("-" * 120)
    
    try:
        extractor = ExcelExtractor(filepath)
        data = extractor.extract_all()
        analyzer = CurricularAnalyzer(data)
        
        ra_df = data['resultados_aprendizaje']
        print(f"   Paso 3 contiene: {len(ra_df)} filas, {len(ra_df.columns)} columnas")
        
        # Búsqueda de columna como lo hace actualmente
        nombre_col_actual = None
        for col in ra_df.columns:
            if 'Competencia' in col and 'desarrollar' in col.lower():
                nombre_col_actual = col
                break
        
        if nombre_col_actual:
            unicos_paso3 = ra_df[nombre_col_actual].nunique()
            print(f"   ❌ Conteo INCORRECTO (Paso 3): {unicos_paso3} competencias únicas")
        else:
            print("   ✗ Columna 'Competencia por desarrollar' no encontrada")
            unicos_paso3 = 0
        
        # Usando analyzer
        indicadores = analyzer.generar_reporte_indicadores()
        dashboard_count = indicadores['resumen']['total_ra']
        print(f"   Dashboard reporta: {dashboard_count}")
        
    except Exception as e:
        print(f"   ❌ Error: {str(e)[:100]}")
        unicos_paso3 = 0
        dashboard_count = 0
    
    # === LÓGICA CORRECTA (Paso 5) ===
    print("\n2️⃣  LÓGICA CORRECTA: Paso 5 - Estrategias Micro")
    print("-" * 120)
    
    try:
        df_paso5 = pd.read_excel(filepath, sheet_name='Paso 5 Estrategias micro', header=1, engine='openpyxl')
        df_paso5.columns = [_normalize_column_name(c) for c in df_paso5.columns]
        
        print(f"   Paso 5 contiene: {len(df_paso5)} filas, {len(df_paso5.columns)} columnas")
        
        # Buscar columna correcta
        asig_col = None
        for c in df_paso5.columns:
            if 'nombreasignaturaomodulo' in c:
                asig_col = c
                break
        
        if asig_col:
            all_vals = df_paso5[asig_col].dropna()
            print(f"   Valores no-nulos en columna: {len(all_vals)}")
            
            # Clasificar: asignaturas vs filas de totales
            asignaturas = []
            filas_totales = []
            
            for v in all_vals:
                v_str = str(v).strip()
                try:
                    float(v_str)
                    filas_totales.append(v)
                except:
                    asignaturas.append(v)
            
            print(f"   Asignaturas encontradas: {len(asignaturas)}")
            print(f"   Filas de totales excluidas: {len(filas_totales)}")
            
            # Normalizar
            asigs_normalizadas = pd.Series(asignaturas).apply(_normalize_value)
            unicos_paso5 = asigs_normalizadas.nunique()
            
            print(f"   ✅ Conteo CORRECTO (Paso 5): {unicos_paso5} asignaturas únicas")
            
            # Detectar duplicados después de normalizar
            counts = Counter(asigs_normalizadas)
            duplicados = {k: v for k, v in counts.items() if v > 1}
            if duplicados:
                print(f"   ⚠️  Duplicados normalizados: {len(duplicados)}")
        else:
            print("   ✗ Columna 'nombre asignatura o modulo' no encontrada")
            unicos_paso5 = 0
            
    except Exception as e:
        print(f"   ❌ Error: {str(e)[:100]}")
        unicos_paso5 = 0
    
    # === RESULTADO ===
    print("\n3️⃣  RESULTADO DE COMPARACIÓN")
    print("-" * 120)
    diferencia = unicos_paso5 - dashboard_count
    signo = "❌" if diferencia != 0 else "✅"
    print(f"   Paso 3 (Incorrecto):  {dashboard_count:3d} competencias")
    print(f"   Paso 5 (Correcto):    {unicos_paso5:3d} asignaturas")
    print(f"   Diferencia:           {diferencia:3d} asignaturas {signo}")
    
    resultados.append({
        'archivo': filename,
        'paso3_incorrecto': dashboard_count,
        'paso5_correcto': unicos_paso5,
        'diferencia': diferencia
    })

# === RESUMEN FINAL ===
print(f"\n{'=' * 120}")
print("RESUMEN FINAL - TODAS LAS PRUEBAS")
print('=' * 120)

df_resultados = pd.DataFrame(resultados)
print("\n" + df_resultados.to_string(index=False))

total_diferencia = df_resultados['diferencia'].sum()
archivos_con_error = len(df_resultados[df_resultados['diferencia'] != 0])

print(f"\n📊 Estadísticas:")
print(f"   • Archivos analizados: {len(df_resultados)}")
print(f"   • Archivos con discrepancia: {archivos_con_error}")
print(f"   • Diferencia total: {total_diferencia} asignaturas")
print(f"\n⚠️  CONCLUSIÓN: El dashboard está usando Paso 3 (competencias) en lugar de Paso 5 (asignaturas)")
