import pandas as pd
import unicodedata
import re

filepath = 'data/raw/FORMATOS RA CICLO UNO RC/FormatoRA_AdmonPub_VNAL.xlsx'

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

df = pd.read_excel(filepath, sheet_name='Paso 5 Estrategias micro', header=1, engine='openpyxl')
df.columns = [_normalize_column_name(c) for c in df.columns]

asig_col = None
for c in df.columns:
    if 'nombreasignaturaomodulo' in c:
        asig_col = c
        break

all_vals = df[asig_col].dropna()

print(f'Total valores en columna: {len(all_vals)}')
print()

print('Todos los valores no nulos:')
for i, v in enumerate(all_vals):
    v_str = str(v).strip()
    es_numero = False
    try:
        float(v_str)
        es_numero = True
    except:
        pass
    es_vacio = v_str == '' or v_str.lower() in ['nan', 'none', 'null']
    print(f'{i}: "{v}" -> numero={es_numero}, vacio={es_vacio}')
print()

asignaturas_limpias = []
for v in all_vals:
    v_str = str(v).strip()
    try:
        float(v_str)
        continue
    except:
        if v_str:
            asignaturas_limpias.append(v)

print(f'Asignaturas limpiadas: {len(asignaturas_limpias)}')

asigs_normalizadas = pd.Series(asignaturas_limpias).apply(_normalize_value)
print(f'Asignaturas unicas (nunique): {asigs_normalizadas.nunique()}')
print(f'Asignaturas unicas (len set): {len(set(asigs_normalizadas))}')

print()
print('Normalizadas:')
for orig, norm in zip(asignaturas_limpias[:10], asigs_normalizadas[:10]):
    print(f'  "{orig}" -> "{norm}"')