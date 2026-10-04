"""
Alineación de cada perfil de egreso (profesional y ocupacional) con el contenido del programa.

Unidad de análisis: ATRIBUTO del perfil, por matriz.
  Perfil profesional: oraciones del texto narrativo (col. C, ≥ 5 palabras) y sus componentes
                      Saber / SaberHacer / SaberSer (cols. E–G).
  Perfil ocupacional: oraciones del texto narrativo (col. D) y los ítems de Áreas profesionales,
                      Tareas profesionales y Poblaciones de actuación (cols. H–J, un ítem por línea).
  (El criterio «celda = registro» de la auditoría del Paso 1 sigue rigiendo los conteos del perfil;
  aquí se divide en atributos porque el objetivo es saber QUÉ parte del perfil está o no alineada.)

Capas de contenido (sin fuentes copiadas del perfil, para evitar circularidad):
  Competencias  Paso 2, «Redacción competencia»
  RA            Paso 3, texto del RA único (D4), sin «SaberAsociado»
  Asignaturas   Paso 5: nombre, indicadores, núcleos y actividades de evaluación (corpus de D9)

Puntaje: método híbrido de src/perfil_coverage_analyzer (0,6 coseno TF-IDF top-3 + 0,4 BM25),
umbral del campo (UMBRALES_POR_CAMPO; oraciones narrativas = umbral del perfil, 0,28).
Un atributo está ALINEADO con una capa si su puntaje ≥ umbral; el umbral está calibrado sobre el
corpus de asignaturas, por lo que en competencias y RA (corpus pequeños) el resultado es exploratorio.

Uso: python auditoria/scripts/alineacion_perfiles.py
Salida: auditoria/evidencia_alineacion_perfiles.json y auditoria/Alineacion_perfiles.xlsx
"""
import glob
import json
import logging
import os
import re
import sys
import warnings

import openpyxl
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer

warnings.filterwarnings('ignore')
logging.disable(logging.CRITICAL)
sys.path.insert(0, '.')
sys.stdout.reconfigure(encoding='utf-8')
import src.perfil_coverage_analyzer as pc  # noqa: E402
from config import UMBRALES_POR_CAMPO  # noqa: E402
from src.extractor import ExcelExtractor  # noqa: E402

CAPAS = ('Competencias', 'RA', 'Asignaturas')


def ne(v):
    return v is not None and str(v).strip() not in ('', 'nan', 'None') and not str(v).strip().startswith('[')


def oraciones(texto):
    partes = re.split(r'(?<=[.;:])\s+|\n+', str(texto))
    return [p.strip() for p in partes if len(p.split()) >= 5]


def items(texto):
    return [p.strip(' .-•\t') for p in re.split(r'\n+', str(texto)) if len(p.strip(' .-•\t')) > 3]


def hoja(wb, pref):
    return next(wb[s] for s in wb.sheetnames if s.strip().startswith(pref) and 'backup' not in s.lower())


def capa(textos):
    corpus = [pc._normalizar_texto(t) for t in textos if ne(t)]
    corpus = [c for c in corpus if len(c) > 3]
    if len(corpus) < 3:
        return corpus, None, None
    kw = dict(pc.TFIDF_KWARGS)
    if len(corpus) < 20:
        kw['max_df'] = 1.0
    vec = TfidfVectorizer(**kw)
    return corpus, vec, vec.fit_transform(corpus)


filas, MATRICES = [], []
for f in sorted(glob.glob('data/raw/FORMATOS RA CICLO UNO RC/*.xlsx')):
    matriz = os.path.basename(f)[10:-5]
    programa, sede = matriz.rsplit('_', 1)
    wb = openpyxl.load_workbook(f, read_only=True, data_only=True)
    atributos = []
    for r in hoja(wb, 'Paso1').iter_rows(min_row=3, values_only=True):
        r = list(r) + [None] * 12
        if ne(r[2]):
            atributos += [('Perfil profesional', 'Narrativo', o) for o in oraciones(r[2])]
        if ne(r[3]):
            atributos += [('Perfil ocupacional', 'Narrativo', o) for o in oraciones(r[3])]
        for j, campo in ((4, 'Saber'), (5, 'SaberHacer'), (6, 'SaberSer')):
            if ne(r[j]) and 'fenomenos contemporaneos' not in pc._preprocesar_ascii(r[4] or ''):
                atributos.append(('Perfil profesional', campo, str(r[j]).strip()))
        for j, campo in ((7, 'Áreas profesionales'), (8, 'Tareas profesionales'), (9, 'Poblaciones actuación')):
            if ne(r[j]):
                atributos += [('Perfil ocupacional', campo, i) for i in items(r[j])]
    comp = [r[5] for r in hoja(wb, 'Paso 2').iter_rows(min_row=3, values_only=True)
            if len(r) > 5 and ne(r[5]) and not pc._preprocesar_ascii(r[5]).startswith('redaccion')]
    ra = list({str(r[8]).strip().lower(): r[8] for r in hoja(wb, 'Paso 3').iter_rows(min_row=3, values_only=True)
               if len(r) > 8 and ne(r[8]) and pc._preprocesar_ascii(r[8]) != 'resultados aprendizaje'}.values())
    wb.close()
    micro = ExcelExtractor(f).extract_estrategias_micro()
    corpus_asig, fuente_asig = pc.construir_corpus_curriculo(micro, pd.DataFrame())
    vec_a = TfidfVectorizer(**pc.TFIDF_KWARGS)
    capas = {'Competencias': capa(comp), 'RA': capa(ra),
             'Asignaturas': (corpus_asig, vec_a, vec_a.fit_transform(corpus_asig))}
    for perfil, campo, texto in atributos:
        umbral = UMBRALES_POR_CAMPO.get('Perfil profesional' if campo == 'Narrativo' and perfil == 'Perfil profesional'
                                        else 'Perfil ocupacional' if campo == 'Narrativo' else campo, 0.35)
        norm = pc._normalizar_texto(texto)
        fila = {'Matriz': matriz, 'Programa': programa, 'Sede': sede, 'Perfil': perfil, 'Campo': campo,
                'Atributo': texto, 'Umbral': umbral}
        for nombre in CAPAS:
            corpus, vec, mat = capas[nombre]
            if vec is None:
                fila[f'{nombre} puntaje'], fila[f'{nombre} alineado'] = None, None
                continue
            fuente = fuente_asig if nombre == 'Asignaturas' else None
            s, _, asig, doc = pc.calcular_cobertura_elemento(norm, corpus, fuente, vec, mat)
            fila[f'{nombre} puntaje'] = round(s, 3)
            fila[f'{nombre} alineado'] = s >= umbral
            if nombre == 'Asignaturas':
                fila['Asignatura más afín'] = asig
        fila['_norm'] = norm
        filas.append(fila)
    MATRICES.append((matriz, programa, capas))
    print('ok', matriz, len(atributos))

# --- Calibración del umbral por capa con controles (corpus de tamaño muy distinto entre capas) ---
#   Positivos: componentes del perfil profesional con vínculo formal conocido (lista desplegable):
#              Saber/SaberHacer/SaberSer → competencias; Saber → RA (SaberAsociado).
#   Negativos: los mismos componentes frente a la capa de otro programa (matriz siguiente de otro programa).
#   Umbral = máximo índice de Youden (sensibilidad − tasa de falsos positivos).
import numpy as np  # noqa: E402
otra = {}
for i, (m, prog, _) in enumerate(MATRICES):
    otra[m] = next(MATRICES[(i + k) % len(MATRICES)][2] for k in range(1, len(MATRICES))
                   if MATRICES[(i + k) % len(MATRICES)][1] != prog)
POSITIVOS = {'Competencias': ('Saber', 'SaberHacer', 'SaberSer'), 'RA': ('Saber',),
             'Asignaturas': ('Saber', 'SaberHacer', 'SaberSer')}
CALIBRACION = {}
for nombre in CAPAS:
    pos, neg = [], []
    for fila in filas:
        if fila['Perfil'] == 'Perfil profesional' and fila['Campo'] in POSITIVOS[nombre] and fila[f'{nombre} puntaje'] is not None:
            corpus, vec, mat = otra[fila['Matriz']][nombre]
            if vec is None:
                continue
            pos.append(fila[f'{nombre} puntaje'])
            neg.append(pc.calcular_cobertura_elemento(fila['_norm'], corpus, None, vec, mat)[0])
    pos, neg = np.array(pos), np.array(neg)
    grid = np.round(np.arange(0.05, 0.80, 0.01), 2)
    youden = [((pos >= u).mean() - (neg >= u).mean(), u) for u in grid]
    j, u = max(youden)
    CALIBRACION[nombre] = {'umbral': float(u), 'youden': round(float(j), 3), 'sensibilidad': round(float((pos >= u).mean()), 3),
                           'falsos_positivos': round(float((neg >= u).mean()), 3), 'n': int(len(pos)),
                           'mediana_positivos': round(float(np.median(pos)), 3), 'mediana_negativos': round(float(np.median(neg)), 3)}
    for fila in filas:
        if fila[f'{nombre} puntaje'] is not None:
            fila[f'{nombre} alineado'] = fila[f'{nombre} puntaje'] >= u
print('CALIBRACION', json.dumps(CALIBRACION, ensure_ascii=False))
for fila in filas:
    fila.pop('_norm')
    fila['Umbral'] = ' / '.join(f"{c[:4]} {CALIBRACION[c]['umbral']}" for c in CAPAS)

d = pd.DataFrame(filas)
al = [f'{c} alineado' for c in CAPAS]
d['Capas alineadas'] = d[al].fillna(False).sum(axis=1)
d['Estado'] = d['Capas alineadas'].map({0: 'Sin alinear', 1: 'Parcial', 2: 'Parcial', 3: 'Alineado'})


def resumen(g):
    out = {'atributos': int(len(g))}
    for c in CAPAS:
        v = g[f'{c} alineado'].dropna().astype(float)
        out[c] = round(100 * v.mean(), 1) if len(v) else None
    out['sin_alinear'] = int((g['Capas alineadas'] == 0).sum())
    return out


EV = {'atributos': len(d), 'calibracion': CALIBRACION,
      'por_perfil': {p: resumen(g) for p, g in d.groupby('Perfil')},
      'por_perfil_campo': {f'{p} | {c}': resumen(g) for (p, c), g in d.groupby(['Perfil', 'Campo'])},
      'por_matriz': {m: {p: resumen(g2) for p, g2 in g.groupby('Perfil')} for m, g in d.groupby('Matriz')}}
json.dump(EV, open('auditoria/evidencia_alineacion_perfiles.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

pm = (d.groupby(['Matriz', 'Programa', 'Sede', 'Perfil'])
       .apply(lambda g: pd.Series({'Atributos': len(g), **{f'% alineado {c}': round(100 * g[f'{c} alineado'].dropna().astype(float).mean(), 1)
                                                         for c in CAPAS}, 'Sin alinear': int((g['Capas alineadas'] == 0).sum())}))
       .reset_index())
with pd.ExcelWriter('auditoria/Alineacion_perfiles.xlsx') as xw:
    pd.DataFrame([{'Perfil / campo': k, **v} for k, v in EV['por_perfil'].items()] +
                 [{'Perfil / campo': k, **v} for k, v in EV['por_perfil_campo'].items()]).to_excel(xw, sheet_name='Resumen', index=False)
    pm.to_excel(xw, sheet_name='Por_matriz', index=False)
    d.sort_values(['Matriz', 'Perfil', 'Capas alineadas']).to_excel(xw, sheet_name='Atributos', index=False)
    pd.DataFrame({'Elemento': ['Unidad', 'Capas', 'Puntaje', 'Alineado', 'Estado', 'Limitación'],
                  'Definición': ['Atributo del perfil: oración del texto narrativo (≥ 5 palabras) o componente/ítem desagregado del Paso 1. '
                                 'Se excluye la competencia genérica institucional.',
                                 'Competencias (Paso 2), RA únicos (Paso 3, sin SaberAsociado) y asignaturas (Paso 5: nombre, indicadores, núcleos, evaluación).',
                                 '0,6 × coseno TF-IDF (top-3 ponderado) + 0,4 × BM25 normalizado (src/perfil_coverage_analyzer).',
                                 'Puntaje ≥ umbral calibrado por capa (máximo de Youden: componentes con vínculo formal frente a la capa de otro programa).',
                                 'Alineado = 3 capas; Parcial = 1–2; Sin alinear = 0.',
                                 'Umbral calibrado con controles positivos (vínculo formal) y negativos (otro programa); ver evidencia_alineacion_perfiles.json. '
                                 'Mide similitud léxica, no suficiencia formativa: requiere validación del comité curricular.']}
                 ).to_excel(xw, sheet_name='Definiciones', index=False)
print(json.dumps({k: v for k, v in EV.items() if k != 'por_matriz'}, ensure_ascii=False, indent=1))
