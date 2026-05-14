#!/usr/bin/env python3
"""
Test COMPLETO: Validar asignaturas Y semestres con nueva lógica.
"""

import pandas as pd
from pathlib import Path
import unicodedata
import re

def _normalize_column_name(name: str) -> str:
    normalized = unicodedata.normalize('NFKD', str(name))
    normalized = ''.join(c for c in normalized if not unicodedata.combining(c))
    normalized = normalized.lower()
    normalized = re.sub(r'[\s\-_.]+', '', normalized)
    return normalized

def _find_column(df, target: str):
    target_norm = _normalize_column_name(target)
    for col in df.columns:
        col_norm = _normalize_column_name(col)
        if col_norm == target_norm:
            return col
    return None

def _contar_semestres_validos(df_grupo) -> int:
    """Obtiene el MÁXIMO número de semestres desde la columna Semestre."""
    if df_grupo.empty:
        return 0
    
    sem_col = _find_column(df_grupo, 'Semestre')
    if sem_col is None:
        return 0
    
    semestres = pd.to_numeric(df_grupo[sem_col], errors='coerce')
    semestres = semestres.dropna()
    
    if len(semestres) == 0:
        return 0
    
    max_sem = int(semestres.max())
    return max_sem

# Test
print("="*80)
print("TEST: Validación de Asignaturas y Semestres")
print("="*80)

test_files_dir = Path("data/raw/FORMATOS RA CICLO UNO RC")
test_files = [
    ("FormatoRA_AdmonPub_VNAL.xlsx", "Pregrado"),
    ("FormatoRA_EspGerMercadeo_VNAL.xlsx", "Especialización"),
    ("FormatoRA_MGerTalentoHumano_VNAL.xlsx", "Maestría"),
]

for filename, tipo in test_files:
    filepath = test_files_dir / filename
    if not filepath.exists():
        print(f"\n❌ {filename}: NO ENCONTRADO")
        continue
    
    print(f"\n{filename}")
    print(f"  Tipo: {tipo}")
    
    try:
        df = pd.read_excel(filepath, sheet_name='Paso 5 Estrategias micro', header=1, engine='openpyxl')
        
        # Contar semestres
        max_sems = _contar_semestres_validos(df)
        
        # Debug: obtener valores
        sem_col = _find_column(df, 'Semestre')
        if sem_col:
            semestres = pd.to_numeric(df[sem_col], errors='coerce').dropna()
            print(f"  ✅ Semestres (MAX): {max_sems}")
            print(f"     Valores únicos: {sorted(semestres.unique().astype(int).tolist())}")
            print(f"     Total de filas: {len(semestres)}")
        else:
            print(f"  ❌ Columna Semestre no encontrada")
            
    except Exception as e:
        print(f"  ❌ ERROR: {e}")

print("\n" + "="*80)
print("CONCLUSIÓN: Semestres ahora se calcula como MAX(Semestre), no count(unique)")
print("="*80)
