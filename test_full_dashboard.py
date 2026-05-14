import pandas as pd
import unicodedata
import re
import os
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

def normalizar_columnas(df):
    nuevos_nombres = {}
    for col in df.columns:
        nfkd = unicodedata.normalize('NFKD', str(col))
        sin_acentos = ''.join(c for c in nfkd if not unicodedata.combining(c))
        nuevos_nombres[col] = sin_acentos
    return df.rename(columns=nuevos_nombres)

def _find_column(df, target):
    target_norm = _normalize_column_name(target)
    for col in df.columns:
        col_norm = _normalize_column_name(col)
        if col_norm == target_norm:
            return col
    return None

# Load all files the way dashboard does
carpeta = 'data/raw/FORMATOS RA CICLO UNO RC/'
archivos = [f for f in os.listdir(carpeta) if f.endswith('.xlsx')]

all_data = []
for nombre in archivos:
    try:
        filepath = os.path.join(carpeta, nombre)
        with open(filepath, 'rb') as f:
            file_bytes = f.read()
        
        uploaded_file = BytesIO(file_bytes)
        uploaded_file.name = nombre
        
        # Load like dashboard
        df = pd.read_excel(uploaded_file, sheet_name='Paso 5 Estrategias micro', header=1, engine='openpyxl')
        
        # normalizar_columnas
        df = normalizar_columnas(df)
        df.columns = [_normalize_column_name(c) for c in df.columns]
        
        # Get metadata
        prog_key = nombre.replace('FormatoRA_', '').replace('Formato RA_', '').replace('.xlsx', '').split('_')[0]
        
        # Try to get real program name
        try:
            uploaded_file.seek(0)
            df_perfil = pd.read_excel(uploaded_file, sheet_name='Paso1 Analisis perfil egreso', header=None, nrows=10, engine='openpyxl')
            if df_perfil is not None and len(df_perfil) > 2 and len(df_perfil.columns) > 0:
                val = df_perfil.iloc[2, 0]
                if val is not None and str(val).strip():
                    prog_key = str(val).strip()
        except:
            pass
        
        # Determine modalidad from filename
        modalidad = 'Presencial'
        sede = 'Bogota'
        nivel = 'Pregrado'
        
        if 'VNAL' in nombre or 'Virtual' in nombre:
            sede = 'Virtual - Nacional'
        if 'HMED' in nombre or 'HBOG' in nombre or 'Hibrido' in nombre:
            modalidad = 'Hibrido'
        if 'PMED' in nombre or 'PBOG' in nombre:
            modalidad = 'Presencial'
        if 'VNAL' in nombre or 'HVAL' in nombre:
            sede = 'Virtual - Nacional'
        
        if 'Maestria' in prog_key or 'Especializacion' in prog_key:
            nivel = 'Posgrado'
        
        df['Programa'] = prog_key
        df['Modalidad'] = modalidad
        df['Sede'] = sede
        df['Nivel'] = nivel
        
        all_data.append(df)
    except Exception as e:
        print(f'Error loading {nombre}: {e}')

df_consolidado = pd.concat(all_data, ignore_index=True)
print('Total rows: ' + str(len(df_consolidado)))

# Group like dashboard
grupos_resumen = ['Programa', 'Modalidad', 'Sede', 'Nivel']
unique_groups = df_consolidado[grupos_resumen].drop_duplicates()

for _, row in unique_groups.iterrows():
    prog = row['Programa']
    modalidad = row['Modalidad']
    sede = row['Sede']
    nivel_detectado = row['Nivel']
    
    g = df_consolidado[(df_consolidado['Programa'] == prog) & 
                        (df_consolidado['Modalidad'] == modalidad) & 
                        (df_consolidado['Sede'] == sede) & 
                        (df_consolidado['Nivel'] == nivel_detectado)]
    
    if 'AdmonPub' in prog and 'Virtual' in sede:
        print('\n=== Administracion Publica group ===')
        print('Rows in group: ' + str(len(g)))
        
        asig_col = _find_column(g, 'Nombre asignatura o modulo')
        print('Column found: ' + str(asig_col))
        
        if asig_col:
            all_vals = g[asig_col].dropna()
            print('Non-null values: ' + str(len(all_vals)))
            
            asigs_limpios = []
            for v in all_vals:
                v_str = str(v).strip()
                try:
                    float(v_str)
                    continue
                except:
                    asigs_limpios.append(v)
            
            print('After numeric filter: ' + str(len(asigs_limpios)))
            
            asigs_normalizadas = pd.Series(asigs_limpios).apply(_normalize_value)
            asigs_calc = asigs_normalizadas.nunique()
            print('Unique count: ' + str(asigs_calc))
            
            # Show what values are being filtered
            print('\nFirst 5 original values:')
            for i in range(min(5, len(all_vals))):
                print(f'  {i}: {repr(all_vals.iloc[i])}')