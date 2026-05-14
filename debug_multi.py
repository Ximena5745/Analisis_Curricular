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

# Simular lo que hace el dashboard con TODOS los archivos
# Cargar múltiples archivos como lo hace el dashboard
import os

carpeta = 'data/raw/FORMATOS RA CICLO UNO RC/'
archivos = [f for f in os.listdir(carpeta) if f.endswith('.xlsx')]

all_data = []
for nombre in archivos[:5]:  # Solo los primeros 5 para probar
    try:
        filepath = os.path.join(carpeta, nombre)
        df = pd.read_excel(filepath, sheet_name='Paso 5 Estrategias micro', header=1, engine='openpyxl')
        df = normalizar_columnas(df)
        df.columns = [_normalize_column_name(c) for c in df.columns]
        
        # Agregar metadata
        df['Programa'] = nombre.replace('FormatoRA_', '').replace('Formato RA_', '').replace('.xlsx', '').split('_')[0]
        df['Modalidad'] = 'Presencial'
        df['Sede'] = 'Virtual'
        
        all_data.append(df)
    except:
        pass

df_consolidado = pd.concat(all_data, ignore_index=True)
print('Total filas consolidado: ' + str(len(df_consolidado)))

# Agrupar
grupos_resumen = ['Programa', 'Modalidad', 'Sede']
for key, g in df_consolidado.groupby(grupos_resumen):
    prog, mod, sed = key
    if 'Admon' in prog or 'Pub' in prog:
        asig_col = _find_column(g, 'Nombre asignatura o modulo')
        if asig_col:
            all_vals = g[asig_col].dropna()
            print('\nGrupo: ' + prog + ' - ' + mod + ' - ' + sed)
            print('  Filas en grupo: ' + str(len(g)))
            print('  Valores en columna: ' + str(len(all_vals)))
            
            asigs_limpios = []
            for v in all_vals:
                v_str = str(v).strip()
                try:
                    float(v_str)
                    continue
                except:
                    asigs_limpios.append(v)
            
            print('  Despues filtro numerico: ' + str(len(asigs_limpios)))
            
            asigs_normalizadas = pd.Series(asigs_limpios).apply(_normalize_value)
            print('  Unicos (nunique): ' + str(asigs_normalizadas.nunique()))
            
            # Verificar duplicados
            print('  Primer valor: ' + str(all_vals.iloc[0]) if len(all_vals) > 0 else 'N/A')