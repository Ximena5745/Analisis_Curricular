import pandas as pd
import unicodedata

def test_exact_logic():
    # Simular exactamente la lógica del test
    filepath = 'data/raw/FORMATOS RA CICLO UNO RC/FormatoRA_AdmonPub_VNAL.xlsx'
    
    # Test: Leer con header=1, sin normalizar_columnas
    df = pd.read_excel(filepath, sheet_name='Paso 5 Estrategias micro', header=1, engine='openpyxl')
    
    # Normalizar columnas como el test
    def _normalize_column_name(name):
        if pd.isna(name):
            return ''
        normalized = unicodedata.normalize('NFKD', str(name))
        normalized = ''.join(c for c in normalized if not unicodedata.combining(c))
        return normalized.lower().replace(' ', '').replace('_', '').replace('-', '')
    
    df.columns = [_normalize_column_name(c) for c in df.columns]
    
    # Buscar columna
    asig_col = None
    for c in df.columns:
        if 'nombreasignaturaomodulo' in c:
            asig_col = c
            break
    
    # Contar como el test
    if asig_col:
        all_vals = df[asig_col].dropna()
        
        asignaturas = []
        for v in all_vals:
            v_str = str(v).strip()
            try:
                float(v_str)
            except:
                asignaturas.append(v)
        
        def _normalize_value(value):
            normalized = unicodedata.normalize('NFKD', str(value))
            normalized = ''.join(c for c in normalized if not unicodedata.combining(c))
            normalized = normalized.lower()
            normalized = ''.join(c for c in normalized if c.isalnum())
            return normalized
        
        asigs_normalizadas = pd.Series(asignaturas).apply(_normalize_value)
        asigs_calc = asigs_normalizadas.nunique()
        
        print(f'Test logic: {asigs_calc}')
    
    # Ahora probar con lógica del dashboard
    def normalizar_columnas(df):
        nuevos_nombres = {}
        for col in df.columns:
            nfkd = unicodedata.normalize('NFKD', str(col))
            sin_acentos = ''.join(c for c in nfkd if not unicodedata.combining(c))
            nuevos_nombres[col] = sin_acentos
        return df.rename(columns=nuevos_nombres)
    
    df2 = pd.read_excel(filepath, sheet_name='Paso 5 Estrategias micro', header=1, engine='openpyxl')
    df2 = normalizar_columnas(df2)
    
    def _normalize_column_name_dash(name):
        normalized = unicodedata.normalize('NFKD', str(name))
        normalized = ''.join(c for c in normalized if not unicodedata.combining(c))
        normalized = normalized.lower()
        import re
        normalized = re.sub(r'[\s\-_.]+', '', normalized)
        return normalized
    
    df2.columns = [_normalize_column_name_dash(c) for c in df2.columns]
    
    asig_col2 = None
    for c in df2.columns:
        if 'nombreasignaturaomodulo' in c:
            asig_col2 = c
            break
    
    if asig_col2:
        all_vals2 = df2[asig_col2].dropna()
        
        asignaturas2 = []
        for v in all_vals2:
            v_str = str(v).strip()
            try:
                float(v_str)
            except:
                asignaturas2.append(v)
        
        asigs_normalizadas2 = pd.Series(asignaturas2).apply(_normalize_value)
        asigs_calc2 = asigs_normalizadas2.nunique()
        
        print(f'Dashboard logic: {asigs_calc2}')

test_exact_logic()