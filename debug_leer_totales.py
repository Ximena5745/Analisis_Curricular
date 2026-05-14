import pandas as pd
import unicodedata
import re

def _norm(s):
    return unicodedata.normalize('NFKD', str(s).strip().lower()).encode('ascii', 'ignore').decode('ascii')

def _normalize_column_name(name):
    if pd.isna(name):
        return ''
    normalized = unicodedata.normalize('NFKD', str(name))
    normalized = ''.join(c for c in normalized if not unicodedata.combining(c))
    return normalized.lower().replace(' ', '').replace('_', '').replace('-', '')

# Test with same logic as dashboard's leer_totales_programa
filepath = 'data/raw/FORMATOS RA CICLO UNO RC/FormatoRA_AdmonPub_VNAL.xlsx'

# Load like dashboard does
raw = pd.read_excel(filepath, sheet_name='Paso 5 Estrategias micro', header=None, engine='openpyxl')
print(f'Total rows in raw: {len(raw)}')

# Find column C (index 2)
# Check header
print(f'Column C header (row 1): {raw.iloc[1, 2]}')

# Now search for total values
asigs_oficial = 0

for r in range(raw.shape[0]):
    for c in range(raw.shape[1]):
        cell = raw.iloc[r, c]
        if pd.notna(cell):
            cn = _norm(str(cell))
            if asigs_oficial == 0 and ('total modulos' in cn or 'total asignaturas del programa' in cn or ('total materias' in cn and 'asignatura' in cn)):
                print(f'Found: row={r}, col={c}, cell="{cell}", cn="{cn}"')
                next_col = c + 1
                if next_col < raw.shape[1]:
                    raw_val = raw.iloc[r, next_col]
                    print(f'  Next column value: {raw_val}')
                    try:
                        asigs_oficial = int(float(raw_val)) if isinstance(raw_val, (int, float)) else int(float(str(raw_val).strip()))
                    except:
                        asigs_oficial = 0

print(f'\nAsignaturas oficial: {asigs_oficial}')