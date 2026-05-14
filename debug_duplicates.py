import pandas as pd
import unicodedata
import re
from io import BytesIO
from collections import Counter

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

# Load file
file_path = 'data/raw/FORMATOS RA CICLO UNO RC/FormatoRA_AdmonPub_VNAL.xlsx'
with open(file_path, 'rb') as f:
    file_bytes = f.read()

uploaded_file = BytesIO(file_bytes)
uploaded_file.name = "FormatoRA_AdmonPub_VNAL.xlsx"

df = pd.read_excel(uploaded_file, sheet_name='Paso 5 Estrategias micro', header=1, engine='openpyxl')
df.columns = [_normalize_column_name(c) for c in df.columns]

# Get all values from the column
asig_col = _find_column(df, 'Nombre asignatura o modulo')
all_vals = df[asig_col].dropna()

asigs_limpios = []
for v in all_vals:
    v_str = str(v).strip()
    try:
        float(v_str)
        continue
    except:
        asigs_limpios.append(v)

# Check for duplicates that normalize to same value
asigs_normalizadas = pd.Series(asigs_limpios).apply(_normalize_value)

print("Checking for normalized duplicates:")
print(f"Total unique (nunique): {asigs_normalizadas.nunique()}")
print(f"Total unique (len set): {len(set(asigs_normalizadas))}")
print()

# Find duplicates
counter = Counter(asigs_normalizadas)
duplicates = {k: v for k, v in counter.items() if v > 1}
if duplicates:
    print("DUPLICATES FOUND:")
    for norm, count in duplicates.items():
        print(f"  '{norm}' appears {count} times")
        # Find original values
        for orig, n in zip(asigs_limpios, asigs_normalizadas):
            if n == norm:
                print(f"      -> '{orig}'")
else:
    print("No duplicates found")

print()
print("All normalized values:")
for orig, norm in zip(asigs_limpios, asigs_normalizadas):
    print(f"  '{orig}' -> '{norm}'")