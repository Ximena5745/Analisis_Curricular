import pandas as pd
import unicodedata
import re

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

archivos = [
    'data/raw/FORMATOS RA CICLO UNO RC/FormatoRA_AdmonPub_VNAL.xlsx',
    'data/raw/FORMATOS RA CICLO UNO RC/Formato RA_AdmonHotelGastro_PBOG.xlsx'
]

for fpath in archivos:
    print('=== ' + fpath.split('/')[-1] + ' ===')
    df = pd.read_excel(fpath, sheet_name='Paso 5 Estrategias micro', header=1, engine='openpyxl')
    df = normalizar_columnas(df)
    df.columns = [_normalize_column_name(c) for c in df.columns]
    
    asig_col = _find_column(df, 'Nombre asignatura o modulo')
    if asig_col:
        all_vals = df[asig_col].dropna()
        print('Total no nulos: ' + str(len(all_vals)))
        
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
        print('Unicos: ' + str(asigs_normalizadas.nunique()))
        print('Primer valor: ' + str(all_vals.iloc[0]))
        print()