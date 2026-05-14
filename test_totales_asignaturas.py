#!/usr/bin/env python3
"""
Test simple para verificar que los valores oficiales de asignaturas
se leen correctamente desde el Excel.
"""

import pandas as pd
from pathlib import Path
import unicodedata
import re

def _norm(s: str) -> str:
    return unicodedata.normalize('NFKD', str(s).strip().lower()).encode('ascii', 'ignore').decode('ascii')

def leer_totales_asignaturas_simple(excel_path) -> int:
    """Lee el valor oficial de asignaturas desde Paso 5."""
    try:
        raw = pd.read_excel(
            excel_path,
            sheet_name='Paso 5 Estrategias micro',
            header=None,
            engine='openpyxl'
        )
        
        asignaturas = None
        nrows, ncols = raw.shape
        
        for r in range(nrows):
            for c in range(ncols):
                cell = raw.iloc[r, c]
                if not pd.notna(cell):
                    continue
                cn = _norm(str(cell))
                
                # Buscar etiqueta de totales
                if 'total modulos' in cn or 'total asignaturas' in cn or 'total materias' in cn:
                    next_col = c + 1
                    if next_col < ncols:
                        raw_val = raw.iloc[r, next_col]
                        try:
                            if isinstance(raw_val, (int, float)):
                                val = int(raw_val)
                            elif pd.notna(raw_val):
                                val = int(float(str(raw_val).strip()))
                            else:
                                val = 0
                        except:
                            val = 0
                        if val > 0 and asignaturas is None:
                            asignaturas = val
                            break
            if asignaturas:
                break
        
        return asignaturas if asignaturas else 0
    except Exception as e:
        print(f"ERROR: {e}")
        return 0

# Test
print("="*80)
print("TEST: Lectura de valores oficiales de asignaturas desde Excel")
print("="*80)

test_files_dir = Path("data/raw/FORMATOS RA CICLO UNO RC")
test_files = [
    "FormatoRA_AdmonPub_VNAL.xlsx",
    "FormatoRA_AdmonEmpresas_PBOG.xlsx",
    "FormatoRA_ComunicacionDigital_PMED.xlsx",
    "FormatoRA_ComunicacionSocial_VNAL.xlsx"
]

for filename in test_files:
    filepath = test_files_dir / filename
    if filepath.exists():
        asigs = leer_totales_asignaturas_simple(filepath)
        print(f"{filename:50s}: {asigs} asignaturas")
    else:
        print(f"{filename:50s}: ARCHIVO NO ENCONTRADO")

print("\n" + "="*80)
print("RESUMEN")
print("="*80)
print("""
Los valores de "Asignaturas" en la tabla resumen de dashboard_tematico
ahora serán tomados directamente de estos valores oficiales del Excel.
""")
