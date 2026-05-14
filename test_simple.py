import pandas as pd
import unicodedata

def _norm(s):
    return unicodedata.normalize('NFKD', str(s).strip().lower()).encode('ascii', 'ignore').decode('ascii')

# Test simple - leer un archivo VNAL y mostrar la estructura
file = 'data/raw/FORMATOS RA CICLO UNO RC/FormatoRA_AdmonPub_VNAL.xlsx'

raw = pd.read_excel(file, sheet_name='Paso 5 Estrategias micro', header=None, engine='openpyxl')

# Buscar celdas que contengan "total" y "asignatura" o "modulo"
print("Buscando filas con 'Total':")
for r in range(raw.shape[0]):
    for c in range(min(10, raw.shape[1])):
        cell = raw.iloc[r, c]
        if pd.notna(cell):
            cn = _norm(str(cell))
            if 'total' in cn and ('asignatura' in cn or 'modulo' in cn):
                print(f"Fila {r}, Col {c}: '{cell}'")
                if c+1 < raw.shape[1]:
                    print(f"  Valor en col {c+1}: {raw.iloc[r, c+1]} (tipo: {type(raw.iloc[r, c+1])})")