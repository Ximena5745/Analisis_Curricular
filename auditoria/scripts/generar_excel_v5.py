"""
Excel de clasificación de los indicadores de logro del Paso 4 (V5, D17).

Todos los indicadores son indicadores de logro del RA (modelo institucional); se clasifican por
NIVEL DE EVIDENCIA (N1 Ejecución, N2 Reacción, N3 Desempeño, N4 Transferencia; Kirkpatrick
adaptado) y por TIPO DE EVIDENCIA (directa: N3–N4; indirecta: N1–N2).

Hojas:
  Libro_codigos — niveles, tipo de evidencia, condición, términos de la regla y ejemplos.
  Redacciones   — las redacciones distintas de indicador con su frecuencia, nivel asignado y
                  columnas para la doble codificación experta (unidad de validación: kappa).
  Indicadores   — los indicadores con su estrategia y matriz; heredan el nivel de su redacción.
  Resumen       — distribución por nivel, V5 y tabla por matriz.

Regla: auditoria/scripts/verificar_v5.py (funciones `nivel` y `evidencia`).
Uso: python auditoria/scripts/generar_excel_v5.py
Salida: auditoria/Clasificacion_indicadores_V5.xlsx
"""
import glob
import os
import re
import sys
import warnings
from collections import Counter, defaultdict

import openpyxl
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

warnings.filterwarnings('ignore')
src = open('auditoria/scripts/verificar_v5.py', encoding='utf-8').read().split('estrategias, por_matriz = [], []')[0]
V5 = {}
exec(compile(src, 'verificar_v5.py', 'exec'), V5)          # reglas y funciones, sin ejecutar el cálculo
norm, ne, nivel, evidencia = V5['norm'], V5['ne'], V5['nivel'], V5['evidencia']
REGLAS = {'N5 Efecto externo': V5['IMPACTO'], 'N4 Transferencia': V5['TRANSFERENCIA'],
          'N3 Aprendizaje demostrado': V5['APRENDIZAJE'], 'N2 Percepción y reacción': V5['PERCEPCION']}

NAVY = '0F385A'
COLOR = {'N1 Implementación': 'DCE6F0', 'N2 Percepción y reacción': 'D6F0F8', 'N3 Aprendizaje demostrado': 'FFF0C8',
         'N4 Transferencia': 'FDE3B0', 'N5 Efecto externo': 'FAD2E6'}
LIBRO = [
    ('N1 Implementación', 'Indirecta', 'Ejecución, cobertura, producción o articulación de la estrategia.',
     'Cuenta ejecuciones, eventos, participantes, empresas o productos sin criterio de calidad. Nivel por defecto.', '(nivel por defecto)',
     'Número de veces que se realiza la estrategia. / Número de estudiantes que participan. / Número de trabajos publicados.'),
    ('N2 Percepción y reacción', 'Indirecta', 'Valoración, satisfacción, utilidad o aporte percibido por los participantes.',
     'Mide una opinión o valoración, no un desempeño.', V5['PERCEPCION'].pattern,
     'Valoración del nivel de aporte de la estrategia a los resultados de aprendizaje del programa.'),
    ('N3 Aprendizaje demostrado', 'Directa', 'Conocimiento, habilidad o desempeño evaluado con criterios.',
     'Desempeño del estudiante con criterio, umbral, comparación o evaluación por jurados o rúbrica; incluye entornos simulados.',
     V5['APRENDIZAJE'].pattern,
     'Aprueban con promedio superior a 450/500 el módulo de práctica en ambiente simulado. / Resultados Saber TyT frente a la media. / '
     'Sustentación de argumentos ante jurados.'),
    ('N4 Transferencia', 'Directa', 'Aplicación del aprendizaje en práctica, trabajo o contexto auténtico.',
     'Evalúa la aplicación en un contexto real (práctica profesional, empresa, usuarios reales); contar participantes no basta.',
     V5['TRANSFERENCIA'].pattern, '(sin casos en el corpus)'),
    ('N5 Efecto externo', 'Efecto externo', 'Trayectoria profesional, efecto organizacional, sectorial o comunitario.',
     'Vinculación laboral, empleabilidad, egresados ubicados, efecto en la comunidad o el entorno. Se reporta aparte de V5.',
     V5['IMPACTO'].pattern, 'Estudiantes… vinculados laboralmente en actividades jurídicas.'),
]
REGLAS_DECISION = [
    ('Regla 1', 'Simulación = N3; N4 solo en contexto auténtico (práctica real, empresa, usuarios reales).'),
    ('Regla 2', 'Contar participantes en una práctica es N1; N4 exige evaluar la aplicación.'),
    ('Regla 3', 'Indicador compuesto: se asigna el nivel más alto que mida explícitamente (orden de evaluación N5 → N1).'),
    ('Regla 4', 'Productos académicos sin criterio de calidad son N1; con arbitraje o rúbrica, N3.'),
]


def termino(ind, n):
    if n not in REGLAS:
        return '—'
    m = REGLAS[n].search(norm(ind))
    return m.group(0) if m else '—'


def clave(t):
    return re.sub(r'\W+', ' ', norm(t)).strip()


filas = []
for f in sorted(glob.glob('data/raw/FORMATOS RA CICLO UNO RC/*.xlsx')):
    nombre = os.path.basename(f)[10:-5]
    programa, sede = nombre.rsplit('_', 1)
    wb = openpyxl.load_workbook(f, read_only=True, data_only=True)
    p4 = next(wb[s] for s in wb.sheetnames if s.strip().startswith('Paso 4'))
    est, n_est, fila_excel = None, 0, 2
    for r in p4.iter_rows(min_row=3, values_only=True):
        fila_excel += 1
        if not r or len(r) < 6:
            continue
        if ne(r[1]):
            n_est += 1
            est = str(r[1]).strip()
        if est is not None and ne(r[3]):
            ind = str(r[3]).strip()
            n = nivel(ind)
            filas.append({'Matriz': nombre, 'Programa': programa, 'Sede': sede, 'N.º estrategia': n_est,
                          'Estrategia': est, 'Fila Paso 4': fila_excel, 'Indicador': ind,
                          'Instrumento (misma fila)': str(r[5]).strip() if ne(r[5]) else '',
                          'Nivel de evidencia': n, 'Tipo de evidencia': evidencia(n), 'clave': clave(ind)})
    wb.close()

# Redacciones distintas (unidad de validación)
grupos = defaultdict(list)
for f in filas:
    grupos[f['clave']].append(f)
redacciones = []
for i, (k, g) in enumerate(sorted(grupos.items(), key=lambda x: -len(x[1])), 1):
    texto = Counter(x['Indicador'] for x in g).most_common(1)[0][0]
    n = g[0]['Nivel de evidencia']
    redacciones.append({'ID redacción': f'R{i:03d}', 'Redacción del indicador': texto, 'Frecuencia': len(g),
                        'Matrices': len({x['Matriz'] for x in g}), 'Nivel asignado': n, 'Tipo de evidencia': evidencia(n),
                        'Término que activa la regla': termino(texto, n)})
    for x in g:
        x['ID redacción'] = f'R{i:03d}'

wb = openpyxl.Workbook()
cab_fill, cab_font = PatternFill('solid', fgColor=NAVY), Font(bold=True, color='FFFFFF')


def hoja(ws, columnas, datos, anchos, colorear=None):
    ws.append(columnas)
    for c in ws[1]:
        c.fill, c.font = cab_fill, cab_font
        c.alignment = Alignment(wrap_text=True, vertical='center')
    for d in datos:
        ws.append([d.get(k, '') if isinstance(d, dict) else d[i] for i, k in enumerate(columnas)])
    for i, a in enumerate(anchos, 1):
        ws.column_dimensions[get_column_letter(i)].width = a
    for fila in ws.iter_rows(min_row=2):
        for c in fila:
            c.alignment = Alignment(wrap_text=True, vertical='top')
        if colorear is not None and fila[colorear].value in COLOR:
            fila[colorear].fill = PatternFill('solid', fgColor=COLOR[fila[colorear].value])
    ws.freeze_panes = 'A2'
    ws.auto_filter.ref = ws.dimensions


ws = wb.active
ws.title = 'Libro_codigos'
hoja(ws, ['Nivel de evidencia', 'Tipo de evidencia', 'Naturaleza', 'Condición para asignar', 'Términos de la regla (expresión regular)', 'Ejemplos de las matrices'],
     LIBRO, [24, 14, 45, 50, 55, 60], colorear=0)
ws.append([])
for etiqueta, texto in [
        ('Principio', 'Todos los indicadores del Paso 4 son indicadores de logro del RA (modelo institucional). Se clasifica la calidad de la evidencia que aportan.'),
        *REGLAS_DECISION,
        ('Orden de evaluación', 'N5 → N4 → N3 → N2 → N1: cada indicador recibe el primer nivel cuya condición cumple.'),
        ('Unidad de validación', 'Redacción distinta del indicador (hoja Redacciones); los indicadores heredan el nivel de su redacción.'),
        ('V5', '% de estrategias con al menos un indicador de evidencia directa (N3 o N4). N5 se reporta aparte.'),
        ('Validación', 'Dos expertos codifican las redacciones sin ver el nivel asignado; se calcula el kappa de Cohen (aceptable ≥ 0,70).'),
        ('Fuente de la regla', 'auditoria/scripts/verificar_v5.py')]:
    ws.append([etiqueta, texto])
    ws.cell(ws.max_row, 1).font = Font(bold=True, color=NAVY)

hoja(wb.create_sheet('Redacciones'),
     ['ID redacción', 'Redacción del indicador', 'Frecuencia', 'Matrices', 'Nivel asignado', 'Tipo de evidencia', 'Término que activa la regla',
      'Nivel experto 1', 'Nivel experto 2', 'Observación'],
     redacciones, [10, 80, 10, 9, 17, 12, 22, 15, 15, 30], colorear=4)

hoja(wb.create_sheet('Indicadores'),
     ['Matriz', 'Programa', 'Sede', 'N.º estrategia', 'Estrategia', 'Fila Paso 4', 'ID redacción', 'Indicador', 'Instrumento (misma fila)',
      'Nivel de evidencia', 'Tipo de evidencia'],
     filas, [26, 22, 7, 9, 38, 8, 10, 70, 28, 17, 12], colorear=9)

# Resumen
ws = wb.create_sheet('Resumen')
cnt = Counter(f['Nivel de evidencia'] for f in filas)
est = defaultdict(set)
for f in filas:
    est[(f['Matriz'], f['N.º estrategia'])].add(f['Nivel de evidencia'])
directa = lambda niveles: any(evidencia(n) == 'Directa' for n in niveles)
ws.append(['Nivel de evidencia', 'Tipo', 'Indicadores', '%', 'Redacciones distintas'])
for n in V5['NIVELES']:
    ws.append([n, evidencia(n), cnt[n], round(100 * cnt[n] / len(filas), 1), sum(r['Nivel asignado'] == n for r in redacciones)])
ws.append(['Total', '', len(filas), 100.0, len(redacciones)])
ws.append([])
n_dir = sum(directa(v) for v in est.values())
ws.append(['Estrategias', len(est)])
ws.append(['V5: estrategias con evidencia directa (N3–N4)', n_dir, round(100 * n_dir / len(est), 1)])
n_ext = sum(any(n.startswith('N5') for n in v) for v in est.values())
ws.append(['Estrategias con efecto externo (N5, aparte)', n_ext, round(100 * n_ext / len(est), 1)])
ws.append([])
ws.append(['Matriz', 'Sede', 'Estrategias', 'N1', 'N2', 'N3', 'N4', 'N5', 'Estrategias con evidencia directa', 'V5 (%)'])
cab = ws.max_row
for m in sorted({f['Matriz'] for f in filas}):
    fm = [f for f in filas if f['Matriz'] == m]
    em = [v for k, v in est.items() if k[0] == m]
    c = Counter(f['Nivel de evidencia'][:2] for f in fm)
    d = sum(directa(v) for v in em)
    ws.append([m, fm[0]['Sede'], len(em), c['N1'], c['N2'], c['N3'], c['N4'], c['N5'], d, round(100 * d / len(em), 1)])
for r in (1, cab):
    for c in ws[r]:
        if c.value is not None:
            c.fill, c.font = cab_fill, cab_font
for i, a in enumerate([44, 10, 12, 8, 8, 8, 8, 8, 18, 8], 1):
    ws.column_dimensions[get_column_letter(i)].width = a

wb.save('auditoria/Clasificacion_indicadores_V5.xlsx')
print('OK auditoria/Clasificacion_indicadores_V5.xlsx', len(filas), len(redacciones), dict(cnt), len(est), n_dir)
