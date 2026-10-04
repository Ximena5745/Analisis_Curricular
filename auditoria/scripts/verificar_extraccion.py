"""
Auditoría independiente - Etapa 1: Extracción.

Recalcula desde los archivos crudos (solo lectura) los conteos del corpus
reportados en el artículo (afirmaciones A1-A6) y guarda la evidencia en
auditoria/evidencia_extraccion.json, que consumen los generadores de
Excel y Word.

Uso (desde la raíz del proyecto):
    python auditoria/scripts/verificar_extraccion.py
"""
import glob
import hashlib
import json
import logging
import os
import re
import sys
import unicodedata
import warnings
from collections import Counter
from datetime import datetime

import openpyxl

warnings.filterwarnings('ignore')
logging.disable(logging.CRITICAL)
sys.path.insert(0, '.')

RAW = 'data/raw/FORMATOS RA CICLO UNO RC'
OUT = 'auditoria/evidencia_extraccion.json'

# Campos del perfil tal como los espera el código (config.COLUMNAS_PERFIL)
CAMPOS_PERFIL = ['Perfil profesional', 'Perfil ocupacional', 'Saber', 'SaberHacer',
                 'SaberSer', 'Áreas profesionales', 'Tareas profesionales',
                 'Poblaciones actuación', 'Valor agregado']


def ne(v):
    return v is not None and str(v).strip() != ''


def nk(s):
    s = unicodedata.normalize('NFKD', str(s)).encode('ascii', 'ignore').decode()
    return re.sub(r'[^a-z]', '', s.lower())


def hoja(wb, prefijo):
    return wb[[s for s in wb.sheetnames if s.startswith(prefijo) and 'Backup' not in s][0]]


def sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        h.update(f.read())
    return h.hexdigest()


def split_perfil(valor):
    """Réplica de src.perfil_coverage_analyzer._split_elementos_perfil."""
    from src.perfil_coverage_analyzer import _split_elementos_perfil
    return _split_elementos_perfil(valor)


def main():
    files = sorted(glob.glob(RAW + '/*.xlsx'))
    ev = {'fecha': datetime.now().strftime('%Y-%m-%d %H:%M'), 'carpeta': RAW,
          'archivos': [], 'filas_totales_p5': [], 'ejemplos_p4': [], 'perfil_columnas': []}
    ra_textos = set()

    for f in files:
        nombre = os.path.basename(f)
        m = re.match(r'FormatoRA_(.+?)_([A-Z]{4})\.xlsx$', nombre)
        wb = openpyxl.load_workbook(f, data_only=True)
        r = {'archivo': nombre, 'programa_codigo': m.group(1), 'sede': m.group(2),
             'sha256': sha256(f), 'tamano_bytes': os.path.getsize(f),
             'hojas': ' | '.join(wb.sheetnames),
             'tiene_backup_paso3': any('Backup' in s for s in wb.sheetnames)}

        # --- Paso 3: RA. Encabezado en fila 2, datos desde fila 3, columna I.
        ws = hoja(wb, 'Paso 3 Redacción RA')
        textos = [str(row[8]).strip() for row in ws.iter_rows(min_row=3, values_only=True)
                  if len(row) > 8 and ne(row[8])]
        r['p3_ra_registros'] = len(textos)
        clave_ra = lambda t: re.sub(r'\s+', ' ', re.sub(r'[^a-z0-9 ]', ' ', unicodedata.normalize('NFKD', t)
                                    .encode('ascii', 'ignore').decode().lower())).strip()  # D4 (D23)
        r['p3_ra_unicos'] = len({clave_ra(t) for t in textos})
        ra_textos.update((nombre, clave_ra(t)) for t in textos)

        # --- Paso 4: meso. Fila 1 = instrucciones, fila 2 = encabezado real, datos desde fila 3.
        ws = hoja(wb, 'Paso 4')
        filas = list(ws.iter_rows(min_row=3, values_only=True))
        r['p4_fila1_instrucciones'] = str(ws.cell(1, 1).value)[:60]
        r['p4_fila2_encabezado'] = ' | '.join(str(ws.cell(2, c).value) for c in range(1, 4))
        r['p4_filas_con_ra'] = sum(ne(x[0]) for x in filas)
        r['p4_filas_con_estrategia'] = sum(ne(x[0]) and ne(x[1]) for x in filas)
        r['p4_filas_sin_estrategia'] = r['p4_filas_con_ra'] - r['p4_filas_con_estrategia']
        r['p4_estrategias_distintas'] = len({str(x[1]).strip().lower() for x in filas if ne(x[1])})
        if len(ev['ejemplos_p4']) < 8:
            for i, x in enumerate(filas[:6], start=3):
                ev['ejemplos_p4'].append({'archivo': nombre, 'fila_excel': i,
                                          'A_resultado_aprendizaje': str(x[0])[:120] if ne(x[0]) else '(vacío)',
                                          'B_estrategia_programa': str(x[1])[:120] if ne(x[1]) else '(vacío)',
                                          'C_descripcion': str(x[2])[:120] if ne(x[2]) else '(vacío)',
                                          'D_indicador': str(x[3])[:120] if len(x) > 3 and ne(x[3]) else '(vacío)'})

        # --- Paso 5: micro. Encabezado en fila 2, datos desde fila 3, columna D = asignatura.
        ws = hoja(wb, 'Paso 5')
        con_asig = tot = sin_ra = 0
        for i, x in enumerate(ws.iter_rows(min_row=3, values_only=True), start=3):
            if not ne(x[3]):
                continue
            con_asig += 1
            if re.fullmatch(r'[\d\.\s]+', str(x[3]).strip()):
                tot += 1
                ev['filas_totales_p5'].append({'archivo': nombre, 'fila_excel': i,
                                               'C_texto': str(x[2]), 'D_valor': str(x[3]),
                                               'creditos': str(x[9]) if len(x) > 9 else ''})
            elif not ne(x[1]):
                sin_ra += 1
        r['p5_filas_col_D'] = con_asig
        r['p5_filas_totales'] = tot
        r['p5_registros_asignatura'] = con_asig - tot
        r['p5_asignaturas_sin_ra'] = sin_ra

        # --- Paso 1: perfil. Encabezado en fila 2, datos desde fila 3.
        ws = hoja(wb, 'Paso1')
        enc = [ws.cell(2, c).value for c in range(1, ws.max_column + 1)]
        idx = {nk(v): j for j, v in enumerate(enc) if ne(v)}
        omitidos, el_codigo, el_total = [], 0, 0
        for campo in CAMPOS_PERFIL:
            j = idx.get(nk(campo))
            if j is None:
                continue
            exacto = str(enc[j]).strip() == campo
            n = sum(len(split_perfil(x[j])) for x in ws.iter_rows(min_row=3, values_only=True)
                    if len(x) > j and ne(x[j]))
            el_total += n
            if exacto:
                el_codigo += n
            else:
                omitidos.append(f'{enc[j]} (≠ {campo}): {n}')
        r['p1_encabezado'] = 'Estándar' if not omitidos else 'Variante'
        r['p1_elementos_codigo'] = el_codigo
        r['p1_elementos_reales'] = el_total
        r['p1_elementos_perdidos'] = el_total - el_codigo
        ev['perfil_columnas'].append({'archivo': nombre, 'encabezado': r['p1_encabezado'],
                                      'columnas_omitidas_por_el_codigo': '; '.join(omitidos) or '—',
                                      'elementos_contados': el_codigo, 'elementos_reales': el_total,
                                      'perdidos': el_total - el_codigo})
        ev['archivos'].append(r)

    A = ev['archivos']
    s = lambda k: sum(a[k] for a in A)
    progs = Counter(a['programa_codigo'] for a in A)
    ev['totales'] = {
        'archivos': len(A), 'programas': len(progs),
        'programas_multisede': {k: v for k, v in progs.items() if v > 1},
        'sedes': dict(Counter(a['sede'] for a in A)),
        'ra_registros': s('p3_ra_registros'), 'ra_unicos_por_archivo': s('p3_ra_unicos'),
        'ra_unicos_global': len({t for _, t in ra_textos}),
        'p4_filas_con_ra': s('p4_filas_con_ra'), 'p4_con_estrategia': s('p4_filas_con_estrategia'),
        'p4_sin_estrategia': s('p4_filas_sin_estrategia'),
        'p5_filas_col_D': s('p5_filas_col_D'), 'p5_totales': s('p5_filas_totales'),
        'p5_registros': s('p5_registros_asignatura'), 'p5_sin_ra': s('p5_asignaturas_sin_ra'),
        'p1_codigo': s('p1_elementos_codigo'), 'p1_reales': s('p1_elementos_reales'),
        'p1_archivos_variante': sum(a['p1_encabezado'] == 'Variante' for a in A),
    }
    with open(OUT, 'w', encoding='utf-8') as fh:
        json.dump(ev, fh, ensure_ascii=False, indent=1)
    print(json.dumps(ev['totales'], ensure_ascii=False, indent=1))


if __name__ == '__main__':
    main()
