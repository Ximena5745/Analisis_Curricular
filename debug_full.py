import streamlit as st
import pandas as pd
import unicodedata
import re
from io import BytesIO

# Copiar las funciones EXACTAS del dashboard
def _norm(s: str) -> str:
    return unicodedata.normalize('NFKD', str(s).strip().lower()).encode('ascii', 'ignore').decode('ascii')

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

# Simular carga de archivos como hace el dashboard
file_path = 'data/raw/FORMATOS RA CICLO UNO RC/FormatoRA_AdmonPub_VNAL.xlsx'
with open(file_path, 'rb') as f:
    file_bytes = f.read()

uploaded_file = BytesIO(file_bytes)
uploaded_file.name = "FormatoRA_AdmonPub_VNAL.xlsx"

# Leer igual que dashboard_tematico.py
df = pd.read_excel(
    uploaded_file,
    sheet_name='Paso 5 Estrategias micro',
    header=1,
    engine='openpyxl'
)
df.columns = [_normalize_column_name(c) for c in df.columns]

# Obtener metadata del nombre del archivo (como hace el dashboard)
nombre = uploaded_file.name
modalidad = "Presencial"
sede = "Virtual - Nacional"

# Intentar leer nombre del programa de la hoja Paso1
try:
    uploaded_file.seek(0)
    df_perfil = pd.read_excel(
        uploaded_file,
        sheet_name='Paso1 Analisis perfil egreso',
        header=None,
        nrows=10,
        engine='openpyxl'
    )
    if df_perfil is not None and len(df_perfil) > 2 and len(df_perfil.columns) > 0:
        val = df_perfil.iloc[2, 0]
        if val is not None and str(val).strip():
            programa_nombre = str(val).strip()
        else:
            programa_nombre = "No identificado"
    else:
        programa_nombre = "No identificado"
except:
    programa_nombre = nombre.replace("FormatoRA_", "").replace(".xlsx", "")

df['Programa'] = programa_nombre
df['Modalidad'] = modalidad
df['Sede'] = sede
df['Nivel'] = "Pregrado"

print(f"Programa: {programa_nombre}")
print(f"Modalidad: {modalidad}")
print(f"Sede: {sede}")
print(f"Nivel: Pregrado")

# Agrupar como hace el resumen
grupos_resumen = ['Programa', 'Modalidad', 'Sede']
for key, g in df.groupby(grupos_resumen):
    prog, mod, sed = key
    
    # Usar la lógica EXACTA del dashboard para Pregrado
    asig_col = _find_column(g, 'Nombre asignatura o modulo')
    if asig_col:
        all_vals = g[asig_col].dropna()
        print(f"\nTotal valores en columna '{asig_col}': {len(all_vals)}")
        
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
        print(f"Asignaturas calculadas: {asigs_calc}")
        
        # Mostrar las primeras normalizadas
        print("\nPrimeras 5 normalizaciones:")
        for o, n in zip(asigs_limpios[:5], asigs_normalizadas[:5]):
            print(f"  '{o}' -> '{n}'")