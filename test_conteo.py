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

def analizar_archivo(filepath):
    filename = os.path.basename(filepath)
    print(f"\n{'='*70}")
    print(f"Archivo: {filename}")
    print("="*70)
    
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
            print("  ERROR: No se encontró columna de asignatura")
            return None
        
        # Contar asignaturas (nuevo método)
        asigs_sin_nulos = df[asig_col].dropna()
        asigs_no_total = asigs_sin_nulos[~asigs_sin_nulos.apply(lambda x: str(x).replace('.','').replace('-','').isdigit())]
        asigs_normalizadas = asigs_no_total.apply(_normalize_value)
        asigs_calc = asigs_normalizadas.nunique()
        
        # Leer total oficial
        raw = pd.read_excel(filepath, sheet_name='Paso 5 Estrategias micro', header=None, engine='openpyxl')
        
        # MOSTRAR TODAS LAS FILAS CON "TOTAL" para debug
        print("  Todas las filas con 'total':")
        for r in range(raw.shape[0]):
            for c in range(raw.shape[1]):
                cell = raw.iloc[r, c]
                if pd.notna(cell):
                    cn = _norm(str(cell))
                    if 'total' in cn:
                        next_col = c + 1 if c + 1 < raw.shape[1] else c
                        val = raw.iloc[r, next_col] if next_col < raw.shape[1] else None
                        print(f"    Fila {r}, Col {c}: '{cell}' -> valor: {val}")
        
        asigs_oficial = 0
        for r in range(raw.shape[0]):
            for c in range(raw.shape[1]):
                cell = raw.iloc[r, c]
                if pd.notna(cell):
                    cn = _norm(str(cell))
                    # Buscar solo la fila correcta: "Total materias (asignaturas y módulos) del programa" o "Total asignaturas del programa"
                    if ('total materias' in cn and 'asignatura' in cn) or 'total asignaturas del programa' in cn:
                        next_col = c + 1 if c + 1 < raw.shape[1] else c
                        val = raw.iloc[r, next_col]
                        try:
                            asigs_oficial = int(float(val)) if pd.notna(val) and str(val).strip() else 0
                        except:
                            asigs_oficial = 0
                        print(f"  -> Fila seleccionada: '{cell}' -> valor oficial: {asigs_oficial}")
        
        diff = asigs_calc - asigs_oficial
        print(f"  Asignaturas calculadas: {asigs_calc}")
        print(f"  Asignaturas oficiales: {asigs_oficial}")
        print(f"  Diferencia: {diff}")
        
        if diff != 0:
            print(f"  *** DIFERENCIA DETECTADA ***")
        
        return {'archivo': filename, 'calculado': asigs_calc, 'oficial': asigs_oficial, 'diff': diff}
        
    except Exception as e:
        print(f"  ERROR: {e}")
        return None

# Buscar archivos
archivos = glob('data/raw/FORMATOS RA CICLO UNO RC/*.xlsx')
print(f"Se encontraron {len(archivos)} archivos")

# Analizar solo los archivos con problemas (VNAL)
archivos_problema = [a for a in archivos if 'VNAL' in a]
resultados = []
for archivo in archivos_problema[:3]:
    resultado = analizar_archivo(archivo)
    if resultado:
        resultados.append(resultado)

# Resumen
print("\n" + "="*70)
print("RESUMEN")
print("="*70)
for r in resultados:
    diff_str = f"DIFF: {r['diff']}" if r['diff'] != 0 else "OK"
    print(f"{r['archivo'][:40]:40} calc={r['calculado']:3} of={r['oficial']:3} {diff_str}")