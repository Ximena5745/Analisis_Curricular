import pandas as pd
import unicodedata
import re

# Simular exactamente lo que hace el dashboard incluyendo carga de archivos

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

# Prima: leer el archivo original
from io import BytesIO

with open(filepath, 'rb') as f:
    file_bytes = f.read()

uploaded_file = BytesIO(file_bytes)
uploaded_file.name = "FormatoRA_AdmonPub_VNAL.xlsx"

# Leer como lo hace el dashboard
df = pd.read_excel(uploaded_file, sheet_name='Paso 5 Estrategias micro', header=1, engine='openpyxl')
df.columns = [_normalize_column_name(c) for c in df.columns]

print("Columnas:", df.columns.tolist())
print()

# Verificar que la columna tiene valores
asig_col = _find_column(df, 'Nombre asignatura o modulo')
print(f"Columna encontrada: {asig_col}")

# Hacer lo mismo que el dashboard
all_vals = df[asig_col].dropna()
print(f"Total valores no nulos: {len(all_vals)}")

# Ver los valores de cerca
print("\nValores exactos (repr):")
for i, v in enumerate(all_vals):
    print(f"{i}: {repr(v)}")