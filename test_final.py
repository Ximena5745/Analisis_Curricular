import pandas as pd
import unicodedata
import os
from glob import glob

def _norm(s):
    return unicodedata.normalize('NFKD', str(s).strip().lower()).encode('ascii', 'ignore').decode('ascii')

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

def procesar_archivo(filepath):
    filename = os.path.basename(filepath)
    print(f"\n{'='*60}")
    print(f"Archivo: {filename}")
    
    try:
        # Leer datos
        df = pd.read_excel(filepath, sheet_name='Paso 5 Estrategias micro', header=1, engine='openpyxl')
        df.columns = [_normalize_column_name(c) for c in df.columns]
        
        asig_col = None
        for c in df.columns:
            if 'nombreasignaturaomodulo' in c:
                asig_col = c
                break
        
        if not asig_col:
            print("  ERROR: No encontró columna de asignatura")
            return None
        
        # Contar asignaturas (nuevo método - excluir filas de totales)
        all_vals = df[asig_col].dropna()
        asigs_limpios = []
        for v in all_vals:
            v_str = str(v).strip()
            try:
                float(v_str)
                continue  # Es número - excluir
            except:
                asigs_limpios.append(v)
        
        asigs_normalizadas = pd.Series(asigs_limpios).apply(_normalize_value)
        asigs_calc = asigs_normalizadas.nunique()
        
        # Leer total oficial del Excel - prioridad: modulos, luego materias, luego asignaturas
        raw = pd.read_excel(filepath, sheet_name='Paso 5 Estrategias micro', header=None, engine='openpyxl')
        asigs_oficial = 0
        
        for r in range(raw.shape[0]):
            for c in range(raw.shape[1]):
                cell = raw.iloc[r, c]
                if pd.notna(cell):
                    cn = _norm(str(cell))
                    
                    # Prioridad 1: Total modulos
                    if asigs_oficial == 0 and ('total modulos del programa' in cn or 'total modulos' in cn):
                        next_col = c + 1
                        if next_col < raw.shape[1]:
                            raw_val = raw.iloc[r, next_col]
                            try:
                                if isinstance(raw_val, (int, float)):
                                    asigs_oficial = int(raw_val)
                                else:
                                    asigs_oficial = int(float(str(raw_val).strip()))
                            except:
                                asigs_oficial = 0
                    
                    # Prioridad 2: Total materias
                    if asigs_oficial == 0 and 'total materias' in cn and 'asignatura' in cn:
                        next_col = c + 1
                        if next_col < raw.shape[1]:
                            raw_val = raw.iloc[r, next_col]
                            try:
                                if isinstance(raw_val, (int, float)):
                                    asigs_oficial = int(raw_val)
                                else:
                                    asigs_oficial = int(float(str(raw_val).strip()))
                            except:
                                asigs_oficial = 0
                    
                    # Prioridad 3: Total asignaturas del programa
                    if asigs_oficial == 0 and 'total asignaturas del programa' in cn:
                        next_col = c + 1
                        if next_col < raw.shape[1]:
                            raw_val = raw.iloc[r, next_col]
                            try:
                                if isinstance(raw_val, (int, float)):
                                    asigs_oficial = int(raw_val)
                                else:
                                    asigs_oficial = int(float(str(raw_val).strip()))
                            except:
                                asigs_oficial = 0
        
        diff = asigs_calc - asigs_oficial
        print(f"  Asignaturas calculadas: {asigs_calc}")
        print(f"  Asignaturas oficiales:  {asigs_oficial}")
        print(f"  Diferencia: {diff}")
        
        if diff == 0:
            print("  ✓ OK")
        else:
            print(f"  ✗ DIFERENCIA: {diff}")
        
        return {'archivo': filename, 'calc': asigs_calc, 'oficial': asigs_oficial, 'diff': diff}
        
    except Exception as e:
        print(f"  ERROR: {e}")
        return None

# Procesar todos los archivos
archivos = glob('data/raw/FORMATOS RA CICLO UNO RC/*.xlsx')
print(f"Total archivos: {len(archivos)}")

resultados = []
for archivo in archivos[:15]:  # Primeros 15
    resultado = procesar_archivo(archivo)
    if resultado:
        resultados.append(resultado)

# Resumen
print("\n" + "="*60)
print("RESUMEN")
print("="*60)
ok = sum(1 for r in resultados if r['diff'] == 0)
error = sum(1 for r in resultados if r['diff'] != 0)
print(f"OK: {ok}, Con diferencia: {error}")
print("\nArchivos con diferencia:")
for r in resultados:
    if r['diff'] != 0:
        print(f"  {r['archivo'][:45]:45} calc={r['calc']:3} of={r['oficial']:3} diff={r['diff']}")