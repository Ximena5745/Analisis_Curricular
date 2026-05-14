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

# Load files like the dashboard does
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
        df = normalizar_columnas(df)
        df.columns = [_normalize_column_name(c) for c in df.columns]
        
        # Get program name from file
        prog_key = nombre.replace('FormatoRA_', '').replace('Formato RA_', '').replace('.xlsx', '')
        for sufijo in ['_PBOG', '_VNAL', '_PMED', '_HBOG', '_HMED', '_HVAL']:
            prog_key = prog_key.replace(sufijo, '')
        
        # Try to get real name
        try:
            uploaded_file.seek(0)
            df_perfil = pd.read_excel(uploaded_file, sheet_name='Paso1 Analisis perfil egreso', header=None, nrows=10, engine='openpyxl')
            if df_perfil is not None and len(df_perfil) > 2:
                val = df_perfil.iloc[2, 0]
                if val is not None and str(val).strip():
                    prog_key = str(val).strip()
        except:
            pass
        
        # Determine metadata from filename
        modalidad = 'Presencial'
        sede = 'Bogota'
        nivel = 'Pregrado'
        
        if 'VNAL' in nombre or 'Virtual' in nombre:
            sede = 'Virtual - Nacional'
        if 'HMED' in nombre or 'HBOG' in nombre or 'H' in nombre.split('_')[-1].replace('.xlsx',''):
            if 'H' in nombre.split('_')[-1].replace('.xlsx',''):
                modalidad = 'Hibrido'
        if 'PMED' in nombre or 'PBOG' in nombre:
            modalidad = 'Presencial'
        
        if 'Maestria' in prog_key or 'Especializacion' in prog_key:
            nivel = 'Posgrado'
        
        # Add source file info
        df['SourceFile'] = nombre
        
        df['Programa'] = prog_key
        df['Modalidad'] = modalidad
        df['Sede'] = sede
        df['Nivel'] = nivel
        
        all_data.append((nombre, df))
    except Exception as e:
        print('Error: ' + nombre + ' - ' + str(e))

# Now test: find Admin Publica group and count
df_consolidado = pd.concat([d for _, d in all_data], ignore_index=True)
print('Total rows: ' + str(len(df_consolidado)))

# Find AdmonPub group
group = df_consolidado[df_consolidado['Programa'].str.contains('Admin', case=False, na=False)]
print('\nPrograms found: ' + str(group['Programa'].unique()[:5]))

# Check specific group
target = df_consolidado[(df_consolidado['Programa'].str.contains('Administración Pública', case=False, na=False))]
print('\nAdmon Pub rows: ' + str(len(target)))
print('Source files: ' + str(target['SourceFile'].unique()))

if len(target) > 0:
    asig_col = _find_column(target, 'Nombre asignatura o modulo')
    if asig_col:
        vals = target[asig_col].dropna()
        print('Non-null values: ' + str(len(vals)))
        
        # Count like test
        asigs = []
        for v in vals:
            try:
                float(str(v).strip())
            except:
                asigs.append(v)
        
        asigs_norm = pd.Series(asigs).apply(_normalize_value)
        print('Unique (nunique): ' + str(asigs_norm.nunique()))