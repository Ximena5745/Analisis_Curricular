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

# Cargar archivo raw
file_path = 'data/raw/FORMATOS RA CICLO UNO RC/FormatoRA_AdmonPub_VNAL.xlsx'
with open(file_path, 'rb') as f:
    file_bytes = f.read()

# Leer sin header
df_raw = pd.read_excel(BytesIO(file_bytes), sheet_name='Paso 5 Estrategias micro', header=None, engine='openpyxl')
print("=== Datos crudos del Excel (sin processing) ===")
print(f"Total filas: {len(df_raw)}")

# Buscar la columna de asignatura (Índice 3 típicamente)
col_idx = 3  # "Nombre asignatura o módulo" está en la posición 3 (0-indexed)
print(f"\nColumna índice {col_idx}:")
print(f"Encabezado: {df_raw.iloc[1, col_idx]}")
print()

# Mostrar primeros 10 valores de esa columna
print("Primeros 20 valores de la columna:")
for i in range(2, min(22, len(df_raw))):
    val = df_raw.iloc[i, col_idx]
    es_nulo = pd.isna(val)
    es_vacio = str(val).strip() == '' if not es_nulo else True
    print(f"  Fila {i}: '{val}' - nulo={es_nulo}, vacio={es_vacio}")