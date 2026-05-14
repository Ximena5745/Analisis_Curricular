import pandas as pd
import unicodedata
import re
from io import BytesIO

def _normalize_column_name(name):
    normalized = unicodedata.normalize('NFKD', str(name))
    normalized = ''.join(c for c in normalized if not unicodedata.combining(c))
    normalized = normalized.lower()
    normalized = re.sub(r'[\s\-_.]+', '', normalized)
    return normalized

def _normalize_value(value):
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

# Load like dashboard does
file_path = 'data/raw/FORMATOS RA CICLO UNO RC/FormatoRA_AdmonPub_VNAL.xlsx'
with open(file_path, 'rb') as f:
    file_bytes = f.read()

uploaded_file = BytesIO(file_bytes)
uploaded_file.name = 'FormatoRA_AdmonPub_VNAL.xlsx'

df = pd.read_excel(uploaded_file, sheet_name='Paso 5 Estrategias micro', header=1, engine='openpyxl')
print('Despues read_excel: ' + str(len(df)) + ' filas')

df = normalizar_columnas(df)
print('Despues normalizar_columnas: ' + str(len(df)) + ' filas')

df.columns = [_normalize_column_name(c) for c in df.columns]
print('Despues _normalize_column_name: ' + str(len(df)) + ' filas')

print('\nColumnas: ' + str(df.columns.tolist()))

asig_col = _find_column(df, 'Nombre asignatura o modulo')
print('Columna encontrada: ' + str(asig_col))

if asig_col:
    print('\n=== Usando la columna encontrada ===')
    all_vals = df[asig_col].dropna()
    print('dropna(): ' + str(len(all_vals)))
    
    asigs_limpios = []
    for v in all_vals:
        v_str = str(v).strip()
        try:
            float(v_str)
            continue
        except:
            asigs_limpios.append(v)
    
    print('Despues filtro numerico: ' + str(len(asigs_limpios)))
    
    asigs_normalizadas = pd.Series(asigs_limpios).apply(_normalize_value)
    print('nunique(): ' + str(asigs_normalizadas.nunique()))
    
    print('\nPrimeras 5 valores:')
    for i in range(5):
        print(f'  {i}: {repr(all_vals.iloc[i])}')
    print('\nUltimas 5 valores:')
    for i in range(-5, 0):
        print(f'  {i}: {repr(all_vals.iloc[i])}')