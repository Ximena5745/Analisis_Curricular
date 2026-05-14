import pandas as pd
import unicodedata
import re
from collections import Counter

def _normalize_value(value):
    normalized = unicodedata.normalize('NFKD', str(value))
    normalized = ''.join(c for c in normalized if not unicodedata.combining(c))
    normalized = normalized.lower()
    normalized = ''.join(c for c in normalized if c.isalnum())
    return normalized

# Load file
df = pd.read_excel('data/raw/FORMATOS RA CICLO UNO RC/FormatoRA_AdmonPub_VNAL.xlsx', 
                   sheet_name='Paso 5 Estrategias micro', header=1, engine='openpyxl')

# Get all non-null values
col_idx = 3  # Nombre asignatura o modulo
all_vals = df.iloc[1:, col_idx].dropna()  # Skip header row

# Filter numeric
asigs = []
for v in all_vals:
    try:
        float(str(v).strip())
    except:
        asigs.append(v)

print('Total asignaturas (sin numericos): ' + str(len(asigs)))

# Normalize and check duplicates
norm_vals = [_normalize_value(v) for v in asigs]
counter = Counter(norm_vals)
duplicates = {k: v for k, v in counter.items() if v > 1}

if duplicates:
    print('\nDuplicated normalized values (' + str(len(duplicates)) + '):')
    for k, v in duplicates.items():
        # Find original values
        orig_vals = [a for a, n in zip(asigs, norm_vals) if n == k]
        print('  "' + k + '" appears ' + str(v) + ' times: ' + str(orig_vals))
else:
    print('\nNo duplicates in normalized values')