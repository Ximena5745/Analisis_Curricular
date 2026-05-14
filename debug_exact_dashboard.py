import pandas as pd
import unicodedata
import re
from io import BytesIO

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

def normalizar_columnas(df):
    nuevos_nombres = {}
    for col in df.columns:
        nfkd = unicodedata.normalize('NFKD', str(col))
        sin_acentos = ''.join(c for c in nfkd if not unicodedata.combining(c))
        nuevos_nombres[col] = sin_acentos
    return df.rename(columns=nuevos_nombres)

# Simular EXACTAMENTE como lo hace el dashboard
file_path = 'data/raw/FORMATOS RA CICLO UNO RC/FormatoRA_AdmonPub_VNAL.xlsx'
with open(file_path, 'rb') as f:
    file_bytes = f.read()

uploaded_file = BytesIO(file_bytes)
uploaded_file.name = 'FormatoRA_AdmonPub_VNAL.xlsx'

# Como está en el dashboard:
print("=== Como el dashboard ===")
df = pd.read_excel(uploaded_file, sheet_name='Paso 5 Estrategias micro', header=1, engine='openpyxl')
print(f"Despues de read_excel: {len(df)} filas")

# normalizar_columnas
df = normalizar_columnas(df)
print(f"Despues de normalizar_columnas: {len(df)} filas")

# Aplicar _normalize_column_name a columnas
df.columns = [_normalize_column_name(c) for c in df.columns]
print(f"Despues de _normalize_column_name a columnas: {len(df)} filas")

# Buscar columna
asig_col = _find_column(df, 'Nombre asignatura o modulo')
print(f"Columna encontrada: {asig_col}")

if asig_col:
    all_vals = df[asig_col].dropna()
    print(f"Valores en columna: {len(all_vals)}")
    print(f"Primer valor: '{all_vals.iloc[0]}'")
    print(f"Ultimo valor: '{all_vals.iloc[-1]}'")

# Ahora ver si hay filtrado por Programa/Modalidad/Sede
df['Programa'] = 'Administración Pública'
df['Modalidad'] = 'Presencial'
df['Sede'] = 'Virtual - Nacional'

grupos_resumen = ['Programa', 'Modalidad', 'Sede']
for key, g in df.groupby(grupos_resumen):
    prog, modalidad, sede = key
    asig_col_g = _find_column(g, 'Nombre asignatura o modulo')
    if asig_col_g:
        all_vals_g = g[asig_col_g].dropna()
        print(f"\nGrupo {prog}: {len(g)} filas, {len(all_vals_g)} valores en columna")
        print(f"  Primer valor: '{all_vals_g.iloc[0]}'")
        print(f"  Ultimo valor: '{all_vals_g.iloc[-1]}'")