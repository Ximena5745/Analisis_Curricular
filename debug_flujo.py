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

# Simular exactamente el flujo del dashboard
file_path = 'data/raw/FORMATOS RA CICLO UNO RC/FormatoRA_AdmonPub_VNAL.xlsx'
with open(file_path, 'rb') as f:
    file_bytes = f.read()

# Como se carga en el dashboard:
uploaded_file = BytesIO(file_bytes)
uploaded_file.name = 'FormatoRA_AdmonPub_VNAL.xlsx'

df = pd.read_excel(uploaded_file, sheet_name='Paso 5 Estrategias micro', header=1, engine='openpyxl')
print(f"1. Despues read_excel: {len(df)} filas")

# normalizar_columnas (primera función)
df = normalizar_columnas(df)
print(f"2. Despues normalizar_columnas: {len(df)} filas")

# Columns con _normalize_column_name
df.columns = [_normalize_column_name(c) for c in df.columns]
print(f"3. Despues _normalize_column_name a columnas: {len(df)} filas")

# Agregar metadata como en dashboard
df['Programa'] = 'Administración Pública'
df['Modalidad'] = 'Presencial'
df['Sede'] = 'Virtual - Nacional'

print(f"4. Despues agregar metadata: {len(df)} filas")

# Ahora el grupo
asig_col = _find_column(df, 'Nombre asignatura o modulo')
print(f"\nColumna: {asig_col}")

# Como se cuenta en el resumen (Pregrado)
all_vals = df[asig_col].dropna()
print(f"Total valores (dropna): {len(all_vals)}")

asigs_limpios = []
for v in all_vals:
    v_str = str(v).strip()
    try:
        float(v_str)
        continue
    except:
        asigs_limpios.append(v)

print(f"Despues filtrar numeros: {len(asigs_limpios)}")

asigs_normalizadas = pd.Series(asigs_limpios).apply(_normalize_value)
asigs_calc = asigs_normalizadas.nunique()
print(f"Unique normalizados: {asigs_calc}")

# Mostrar si hay duplicados en la normalizacion
print("\nVerificar duplicados en normalizacion:")
from collections import Counter
counter = Counter(asigs_normalizadas)
duplicados = {k: v for k, v in counter.items() if v > 1}
if duplicados:
    print(f"HAY DUPLICADOS: {duplicados}")
else:
    print("Sin duplicados")