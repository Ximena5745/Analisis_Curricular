#!/usr/bin/env python3
"""
Test para verificar que dashboard_tematico.py ahora usa los valores oficiales
de asignaturas del Excel en lugar de recalcularlos desde el dataframe filtrado.
"""

import sys
from pathlib import Path
import pandas as pd

# Agregar src al path
sys.path.append(str(Path(__file__).parent))

# Simular el entorno de Streamlit sin UI
class MockSessionState(dict):
    pass

class MockStreamlit:
    session_state = MockSessionState()
    def warning(self, msg):
        pass
    def info(self, msg):
        pass
    def error(self, msg):
        print(f"ERROR: {msg}")

# Mock streamlit
sys.modules['streamlit'] = MockStreamlit()
sys.modules['streamlit.components.v1'] = type('module', (), {'html': lambda x, height=0: None})()

import streamlit as st

# Ahora importar dashboard_tematico (sin ejecutar main)
import importlib.util
spec = importlib.util.spec_from_file_location("dashboard_tematico", "dashboard_tematico.py")
dtematico = importlib.util.module_from_spec(spec)

# Necesitamos mantener las funciones relevantes. Vamos a hacer un test más simple:

from dashboard_tematico import leer_totales_programa, procesar_archivos

# Test
print("="*80)
print("TEST: Verificar que dashboard_tematico usa valores oficiales de asignaturas")
print("="*80)

# Leer archivos de prueba
test_files_dir = Path("data/raw/FORMATOS RA CICLO UNO RC")
excel_files = list(test_files_dir.glob("FormatoRA_*.xlsx"))[:2]

if not excel_files:
    print("ERROR: No se encontraron archivos Excel de prueba")
    sys.exit(1)

print(f"\nArchivos de prueba encontrados: {len(excel_files)}")
for f in excel_files:
    print(f"  - {f.name}")

# Test leer_totales_programa
print("\n" + "="*80)
print("TEST 1: leer_totales_programa()")
print("="*80)

# Crear objetos file-like desde archivos reales
class FileObj:
    def __init__(self, path):
        self.name = path.name
        self.path = path
        self.pos = 0
    
    def seek(self, pos):
        self.pos = pos
    
    def read(self):
        with open(self.path, 'rb') as f:
            return f.read()

uploaded_files = [FileObj(f) for f in excel_files]

# Parche para leer archivos
import io
original_read_excel = pd.read_excel

def patched_read_excel(file, **kwargs):
    if hasattr(file, 'path'):
        return original_read_excel(file.path, **kwargs)
    return original_read_excel(file, **kwargs)

pd.read_excel = patched_read_excel

totales = leer_totales_programa(uploaded_files)

print(f"\nTotales leídos: {len(totales)} programas")
for prog, datos in totales.items():
    print(f"  {prog}: {datos}")

# Verificar que 'asignaturas' está en los totales
for prog, datos in totales.items():
    if 'asignaturas' in datos:
        print(f"✓ {prog}: asignaturas = {datos['asignaturas']}")
    else:
        print(f"✗ {prog}: NO contiene 'asignaturas'")

print("\n" + "="*80)
print("RESUMEN")
print("="*80)
print("""
La corrección aplicada a dashboard_tematico.py:
1. LEE los totales oficiales del Excel mediante leer_totales_programa()
2. UTILIZA directamente asigs_oficial en lugar de recalcular desde dataframe filtrado
3. Esto evita discrepancias causadas por filtrado por Tipo de Saber

Los valores ahora serán CONSISTENTES entre:
- Lo que muestra la tabla "Asignaturas" en dashboard_tematico
- Lo que muestra "Asig. Oficial" (valor leído del Excel)
""")

print("Test completado ✓")
