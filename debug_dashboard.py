import pandas as pd
import unicodedata
import re

# Simular exactamente lo que hace el dashboard

def _normalize_column_name(name: str) -> str:
    normalized = unicodedata.normalize('NFKD', str(name))
    normalized = ''.join(c for c in normalized if not unicodedata.combining(c))
    normalized = normalized.lower()
    normalized = re.sub(r'[\s\-_.]+', '', normalized)
    return normalized

def _normalize_value(value: str) -> str:
    normalized = unicodedata.normalize('NFKD', str(value))
    normalized = ''.join(c for c in normalized if not unicodedata.combining(c))
    normalized = normalized.lower()
    normalized = ''.join(c for c in normalized if c.isalnum())
    return normalized

def _find_column(df, target):
    target_norm = _normalize_column_name(target)
    for col in df.columns:
        col_norm = _normalize_column_name(col)
        if col_norm == target_norm:
            return col
    return None

# Cargar igual que el dashboard
filepath = 'data/raw/FORMATOS RA CICLO UNO RC/FormatoRA_AdmonPub_VNAL.xlsx'

# Cargo con header=1 como el dashboard
df = pd.read_excel(filepath, sheet_name='Paso 5 Estrategias micro', header=1, engine='openpyxl')
df.columns = [_normalize_column_name(c) for c in df.columns]

print("Columnas del df:", df.columns.tolist())

# Asignar como hace el dashboard
programa_nombre = "Administración Pública"
modalidad = "Presencial"
sede = "Virtual - Nacional"
df['Programa'] = programa_nombre
df['Modalidad'] = modalidad
df['Sede'] = sede

# Agrupar como hace el dashboard
grupos_resumen = ['Programa', 'Modalidad', 'Sede']
for key, g in df.groupby(grupos_resumen):
    prog, modalidad, sede = key
    print(f"\nGrupo: {prog} - {modalidad} - {sede}")
    print(f"Tamano grupo: {len(g)}")
    
    asig_col = _find_column(g, 'Nombre asignatura o modulo')
    print(f"Columna encontrada: {asig_col}")
    
    if asig_col:
        all_vals = g[asig_col].dropna()
        print(f"Valores no nulos: {len(all_vals)}")
        
        asigs_limpios = []
        for v in all_vals:
            v_str = str(v).strip()
            try:
                float(v_str)
                continue
            except:
                asigs_limpios.append(v)
        
        print(f"Asignaturas limpiadas: {len(asigs_limpios)}")
        
        asigs_normalizadas = pd.Series(asigs_limpios).apply(_normalize_value)
        asigs_calc = asigs_normalizadas.nunique()
        print(f"Asignaturas calculadas (unique): {asigs_calc}")
        
        # Ahora probar con set en lugar de nunique
        asigs_set = set(asigs_normalizadas)
        print(f"Asignaturas con set: {len(asigs_set)}")
        
        # Verificar si hay duplicados normalizados
        print(f"Duplicados: {len(asigs_limpios) - len(asigs_set)}")