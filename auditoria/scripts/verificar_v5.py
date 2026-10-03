"""
V5 (indicadores de resultado e impacto) sobre las 391 estrategias declaradas (D5).

Estructura del Paso 4: cada estrategia es un bloque (B, C y E combinadas) con varias
filas de RA; los indicadores (D) e instrumentos (F) ocupan filas propias del bloque.

  A. Cálculo del artículo: % de FILAS con RA que tienen indicador en la misma fila.
  B. % de estrategias con al menos un indicador (cualquier fila del bloque).
  C. Clasificación de cada indicador:
       logro      — declara un resultado o desempeño de los estudiantes (puntaje,
                    promedio, aprobación, nivel alcanzado, resultados de pruebas…)
       percepción — valoración, satisfacción o percepción de participantes
       gestión    — ejecución de la actividad (número de participantes, eventos,
                    veces que se realiza…)
     y % de estrategias con al menos un indicador de logro.

Uso: python auditoria/scripts/verificar_v5.py
Salida: auditoria/evidencia_v5.json
"""
import glob
import json
import os
import re
import statistics as st
import sys
import unicodedata
import warnings
from collections import Counter

import openpyxl

warnings.filterwarnings('ignore')
sys.stdout.reconfigure(encoding='utf-8')

# Clasificación en cuatro clases (cadena de valor: producto → resultado → logro → impacto):
#   producto  — lo que la estrategia entrega o genera: ejecuciones, eventos, talleres,
#               documentos, publicaciones, ponencias (cuenta la oferta, no al estudiante).
#   resultado — efecto inmediato en los participantes: participación / cobertura y su
#               valoración o percepción de la estrategia.
#   logro     — desempeño de aprendizaje del estudiante con criterio, umbral o comparación
#               (puntajes, aprobación, nivel alcanzado, pruebas Saber).
#   impacto   — efecto posterior o externo a la formación: empleabilidad, inserción o
#               vinculación laboral, egresados, efecto en el entorno o la comunidad.
# Se evalúa en orden impacto → logro → resultado → producto.
IMPACTO = re.compile(r'egresados? (vinculad|emplead|contratad|ubicad)|emplea|insercion|vinculad[oa]s? laboral|laboralmente|contratad|ubicacion laboral|'
                     r'emprendimientos? creados?|impacto en (la|el|las|los) (comunidad|entorno|sector|region)|'
                     r'beneficiari|convenios? (firmad|suscrit)|transferencia')
LOGRO = re.compile(r'puntaje|promedio|aprueb|aprobaci|desempe|nivel de (logro|dominio|desarrollo|competencia)|'
                   r'calificaci|\bnota\b|alcanzan|superan|igual o superior|superior a|por encima|mejora en|rubrica|'
                   r'resultados? (de|en) (las? )?prueba|saber (pro|tyt)')
RESULTADO = re.compile(r'valoraci|\bvalora\b|satisfacci|percepci|opini|apreciaci|nivel de contribuci|'
                       r'estudiantes? (del programa )?que (participan|asisten)|participaci[oó]n de (los )?estudiantes|'
                       r'numero de (estudiantes|participantes|asistentes|docentes|tutores|profesores)|porcentaje de (estudiantes|participantes)')
CLASES = ('producto', 'resultado', 'logro', 'impacto')


def norm(t):
    t = unicodedata.normalize('NFKD', str(t)).encode('ascii', 'ignore').decode('ascii').lower()
    return re.sub(r'\s+', ' ', t).strip()


def ne(v):
    return v is not None and str(v).strip() not in ('', 'nan', 'None')


def clase(ind):
    t = norm(ind)
    if IMPACTO.search(t):
        return 'impacto'
    if LOGRO.search(t):
        return 'logro'
    if RESULTADO.search(t):
        return 'resultado'
    return 'producto'



# Clasificación vigente (D17, aprobada 2026-10-03): todos los indicadores del Paso 4 son
# indicadores de logro del RA (modelo institucional); se clasifican por NIVEL DE EVIDENCIA
# (Kirkpatrick con nivel previo de implementación) y TIPO DE EVIDENCIA:
#   N1 Implementación          — ejecución, cobertura, producción o articulación            (indirecta)
#   N2 Percepción y reacción   — valoración, satisfacción, utilidad o aporte percibido      (indirecta)
#   N3 Aprendizaje demostrado  — conocimiento, habilidad o desempeño evaluado con criterios (directa)
#   N4 Transferencia           — aplicación evaluada en práctica, trabajo o contexto auténtico (directa)
#   N5 Efecto externo          — trayectoria profesional, efecto organizacional, sectorial o comunitario
#                                (se reporta aparte: evidencia de impacto, no del logro del RA)
# Reglas de decisión:
#   1. Simulación = N3; N4 solo en contexto auténtico (práctica real, empresa, usuarios reales).
#   2. Contar participantes en una práctica es N1; N4 exige evaluar la aplicación.
#   3. Indicador compuesto: se asigna el nivel más alto que mida explícitamente (orden N5 → N1).
#   4. Productos académicos sin criterio de calidad son N1; con arbitraje o rúbrica, N3.
PERCEPCION = re.compile(r'valoraci|\bvalora\b|satisfacci|percepci|opini|apreciaci|utilidad percibida|nivel de contribuci')
APRENDIZAJE = re.compile(LOGRO.pattern + r'|sustentaci|jurad|evaluad[oa]s? con (rubrica|criterios)|arbitrad|indexad')
TRANSFERENCIA = re.compile(r'(evaluaci|desempe|calificaci|valoracion del (tutor|jefe|empleador))[^.]*'
                           r'(practica (empresarial|profesional|laboral)|pasanti|contexto real|escenario real|en la empresa|usuarios reales)')
NIVELES = ('N1 Implementación', 'N2 Percepción y reacción', 'N3 Aprendizaje demostrado', 'N4 Transferencia', 'N5 Efecto externo')


def nivel(ind):
    t = norm(ind)
    if IMPACTO.search(t):
        return NIVELES[4]
    if TRANSFERENCIA.search(t) and 'simulad' not in t:
        return NIVELES[3]
    if APRENDIZAJE.search(t):
        return NIVELES[2]
    if PERCEPCION.search(t):
        return NIVELES[1]
    return NIVELES[0]


def evidencia(n):
    return {'N3': 'Directa', 'N4': 'Directa', 'N5': 'Efecto externo'}.get(n[:2], 'Indirecta')


estrategias, por_matriz = [], []
for f in sorted(glob.glob('data/raw/FORMATOS RA CICLO UNO RC/*.xlsx')):
    nombre = os.path.basename(f)[10:-5]
    wb = openpyxl.load_workbook(f, read_only=True, data_only=True)
    p4 = next(wb[s] for s in wb.sheetnames if s.strip().startswith('Paso 4'))
    bloques, b = [], None
    filas_ra = filas_ra_ind = 0
    for r in p4.iter_rows(min_row=3, values_only=True):
        if not r or len(r) < 6:
            continue
        if ne(r[1]):
            b = {'matriz': nombre, 'estrategia': str(r[1]).strip(), 'indicadores': []}
            bloques.append(b)
        if b is None:
            continue
        if ne(r[3]):
            b['indicadores'].append(str(r[3]).strip())
        if ne(r[0]):
            filas_ra += 1
            filas_ra_ind += ne(r[3])
    wb.close()
    for b in bloques:
        b['clases'] = [clase(i) for i in b['indicadores']]
        b['con_indicador'] = bool(b['indicadores'])
        b['con_logro'] = 'logro' in b['clases']
        b['con_logro_impacto'] = bool({'logro', 'impacto'} & set(b['clases']))
        b['niveles'] = [nivel(i) for i in b['indicadores']]
        b['con_directa'] = any(evidencia(n) == 'Directa' for n in b['niveles'])
        b['nivel_max'] = max(b['niveles']) if b['niveles'] else None
    estrategias += bloques
    n = len(bloques)
    por_matriz.append({'matriz': nombre, 'sede': nombre.rsplit('_', 1)[1], 'estrategias': n,
                       'A_filas': round(100 * filas_ra_ind / filas_ra, 1) if filas_ra else None,
                       'B_estrategias': round(100 * sum(b['con_indicador'] for b in bloques) / n, 1) if n else None,
                       'C_logro': round(100 * sum(b['con_logro'] for b in bloques) / n, 1) if n else None,
                       'V5_directa': round(100 * sum(b['con_directa'] for b in bloques) / n, 1) if n else None,
                       'C_logro_impacto': round(100 * sum(b['con_logro_impacto'] for b in bloques) / n, 1) if n else None})


def resumen(clave, filas):
    v = [m[clave] for m in filas if m[clave] is not None]
    return {'n': len(v), 'media': round(st.mean(v), 1), 'mediana': round(st.median(v), 1),
            'desv': round(st.stdev(v), 1) if len(v) > 1 else None, 'min': min(v), 'max': max(v)}


SEDES = ['PBOG', 'PMED', 'VNAL', 'HMED', 'HBOG']
inds = [(c, i) for b in estrategias for c, i in zip(b['clases'], b['indicadores'])]
EV = {
    'estrategias': len(estrategias), 'indicadores': len(inds),
    'A_articulo_filas': {s: resumen('A_filas', [m for m in por_matriz if m['sede'] == s]) for s in SEDES} | {'Total': resumen('A_filas', por_matriz)},
    'B_estrategias_con_indicador': round(100 * sum(b['con_indicador'] for b in estrategias) / len(estrategias), 1),
    'C_clases_indicadores': dict(Counter(c for c, _ in inds)),
    'C_estrategias_con_logro': {'global': round(100 * sum(b['con_logro'] for b in estrategias) / len(estrategias), 1),
                                'por_matriz': resumen('C_logro', por_matriz),
                                'por_sede': {s: resumen('C_logro', [m for m in por_matriz if m['sede'] == s]) for s in SEDES}},
    'C_estrategias_con_logro_o_impacto': {'global': round(100 * sum(b['con_logro_impacto'] for b in estrategias) / len(estrategias), 1),
                                          'n': sum(b['con_logro_impacto'] for b in estrategias),
                                          'por_matriz': resumen('C_logro_impacto', por_matriz),
                                          'por_sede': {s: resumen('C_logro_impacto', [m for m in por_matriz if m['sede'] == s]) for s in SEDES}},
    'V5_oficial': {'definicion': '% de estrategias con al menos un indicador de evidencia directa (N3 o N4)',
                   'estrategias': len(estrategias), 'con_directa': sum(b['con_directa'] for b in estrategias),
                   'global': round(100 * sum(b['con_directa'] for b in estrategias) / len(estrategias), 1),
                   'por_matriz': resumen('V5_directa', por_matriz),
                   'por_sede': {s: resumen('V5_directa', [m for m in por_matriz if m['sede'] == s]) for s in SEDES}},
    'niveles_indicadores': dict(Counter(nivel(i) for _, i in inds)),
    'nivel_maximo_por_estrategia': dict(Counter(b['nivel_max'] for b in estrategias)),
    'estrategias_por_clase_presente': {k: sum(k in b['clases'] for b in estrategias) for k in CLASES},
    'ejemplos': {k: Counter(i for c, i in inds if c == k).most_common(15) for k in CLASES},
    'por_matriz': por_matriz,
}
json.dump(EV, open('auditoria/evidencia_v5.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(json.dumps({k: v for k, v in EV.items() if k not in ('por_matriz', 'ejemplos')}, ensure_ascii=False, indent=1))
for k, ej in EV['ejemplos'].items():
    print(f'\n== {k}')
    for t, n in ej:
        print(f'  {n:3d} | {t[:120]}')
