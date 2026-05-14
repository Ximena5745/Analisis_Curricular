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

# Test with header=0 (no header)
file_path = 'data/raw/FORMATOS RA CICLO UNO RC/FormatoRA_AdmonPub_VNAL.xlsx'
with open(file_path, 'rb') as f:
    file_bytes = f.read()

print("=== Test 1: header=0 (sin especificar fila de header) ===")
df0 = pd.read_excel(BytesIO(file_bytes), sheet_name='Paso 5 Estrategias micro', engine='openpyxl')
print(f"Filas: {len(df0)}")
print(f"Primera fila (raw): {df0.iloc[0].tolist()[:5]}")
print()

print("=== Test 2: header=1 (como el dashboard) ===")
df1 = pd.read_excel(BytesIO(file_bytes), sheet_name='Paso 5 Estrategias micro', header=1, engine='openpyxl')
df1 = normalizar_columnas(df1)
df1.columns = [_normalize_column_name(c) for c in df1.columns]
asig_col = _find_column(df1, 'Nombre asignatura o modulo')
if asig_col:
    all_vals = df1[asig_col].dropna()
    print(f"Filas: {len(df1)}, Valores en columna: {len(all_vals)}")
    print(f"Primer valor: {all_vals.iloc[0]}")
    print(f"Ultimo valor: {all_vals.iloc[-1]}")
print()

print("=== Test 3: header=0 luego drop first row ===")
df0 = pd.read_excel(BytesIO(file_bytes), sheet_name='Paso 5 Estrategias micro', engine='openpyxl')
df0 = df0.iloc[1:]  # Skip first row (header)
df0 = normalizar_columnas(df0)
df0.columns = [_normalize_column_name(c) for c in df0.columns]
asig_col = _find_column(df0, 'Nombre asignatura o modulo')
if asig_col:
    all_vals = df0[asig_col].dropna()
    print(f"Filas: {len(df0)}, Valores en columna: {len(all_vals)}")
    print(f"Primer valor: {all_vals.iloc[0]}")
    print(f"Ultimo valor: {all_vals.iloc[-1]}")