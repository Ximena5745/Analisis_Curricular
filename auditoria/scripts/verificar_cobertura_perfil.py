"""
Auditoría independiente - Etapa 4 (cobertura del perfil, Tabla 5).

1. Circularidad: % de celdas del perfil (Saber, SaberHacer, SaberSer) cuyo texto
   reaparece en 'SaberAsociado' del Paso 3 o en el texto de los RA, que forman
   parte del corpus contra el que se mide la cobertura.
2. Alertas de brecha con el código del proyecto (src/perfil_coverage_analyzer.py)
   bajo distintas unidades y corpus:
     A  actual: elementos divididos (9 campos) vs corpus completo
     B  D3: una celda = un registro (9 campos) vs corpus completo
     C  D3 solo perfil profesional y ocupacional (100) vs corpus completo
     D  como B pero sin las fuentes derivadas del perfil (SaberAsociado y textos de RA)
     E  como C pero sin las fuentes derivadas del perfil

Uso: python auditoria/scripts/verificar_cobertura_perfil.py
"""
import glob
import json
import logging
import os
import re
import sys
import unicodedata
import warnings
from collections import Counter, defaultdict

warnings.filterwarnings('ignore')
logging.disable(logging.CRITICAL)
sys.path.insert(0, '.')
import pandas as pd  # noqa: E402
from sklearn.feature_extraction.text import TfidfVectorizer  # noqa: E402

import src.perfil_coverage_analyzer as pc  # noqa: E402
from src.extractor import ExcelExtractor  # noqa: E402

CAMPOS = ['Perfil profesional', 'Perfil ocupacional', 'Saber', 'SaberHacer', 'SaberSer',
          'Áreas profesionales', 'Tareas profesionales', 'Poblaciones actuación', 'Valor agregado']


def k(t):
    t = unicodedata.normalize('NFKD', str(t)).encode('ascii', 'ignore').decode().lower()
    return re.sub(r'[^a-z0-9 ]', '', re.sub(r'\s+', ' ', t)).strip()


def puntuar(elementos, corpus):
    if len(corpus) < 3:
        return [0.0] * len(elementos)
    vec = TfidfVectorizer(**pc.TFIDF_KWARGS)
    mat = vec.fit_transform(corpus)
    return [pc.calcular_cobertura_elemento(e['elemento_norm'], corpus, None, vec, mat)[0] for e in elementos]


def main():
    res = defaultdict(lambda: Counter())
    por_campo = defaultdict(lambda: defaultdict(Counter))
    circ = Counter()
    detalle_d = []   # escenario D (D9): un registro por elemento, para listados y ejemplos
    for f in sorted(glob.glob('data/raw/FORMATOS RA CICLO UNO RC/*.xlsx')):
        d = ExcelExtractor(f).extract_all()
        p1, p3, p5 = d['perfil_egreso'], d['resultados_aprendizaje'], d['estrategias_micro']

        # 1. Circularidad
        saber_asoc = {k(x) for x in p3.get('SaberAsociado', pd.Series(dtype=str)).dropna()}
        ra_txt = ' || '.join(k(x) for x in p3.get('Resultados Aprendizaje', pd.Series(dtype=str)).dropna())
        for campo in ['Saber', 'SaberHacer', 'SaberSer']:
            for v in p1.get(campo, pd.Series(dtype=str)).dropna():
                kv = k(v)
                if not kv:
                    continue
                circ[(campo, 'total')] += 1
                circ[(campo, 'en_saber_asociado')] += kv in saber_asoc
                circ[(campo, 'en_texto_ra')] += kv in ra_txt

        # 2. Corpus completo y corpus sin fuentes derivadas del perfil
        corpus_full, _ = pc.construir_corpus_curriculo(p5, p3)
        p5_sin = p5.drop(columns=[c for c in ['Resultado de aprendizaje'] if c in p5.columns])
        corpus_sin, _ = pc.construir_corpus_curriculo(p5_sin, pd.DataFrame())

        elem_a = pc.extraer_elementos_perfil(p1)
        elem_b = [{'campo': c, 'elemento': str(v), 'elemento_norm': pc._normalizar_texto(v)}
                  for c in CAMPOS if c in p1.columns for v in p1[c].dropna() if str(v).strip()]
        elem_c = [e for e in elem_b if e['campo'] in ('Perfil profesional', 'Perfil ocupacional')]
        for nombre, elems, corpus in [('A', elem_a, corpus_full), ('B', elem_b, corpus_full), ('C', elem_c, corpus_full),
                                      ('D', elem_b, corpus_sin), ('E', elem_c, corpus_sin)]:
            for e, s in zip(elems, puntuar(elems, corpus)):
                brecha = s < pc._umbral_para_campo(e['campo'])
                res[nombre]['total'] += 1
                res[nombre]['alertas'] += brecha
                por_campo[nombre][e['campo']]['total'] += 1
                por_campo[nombre][e['campo']]['alertas'] += brecha
                if nombre == 'D':
                    detalle_d.append({'matriz': os.path.basename(f)[10:-5], 'campo': e['campo'], 'elemento': e['elemento'][:300],
                                      'score': round(float(s), 4), 'umbral': pc._umbral_para_campo(e['campo']), 'alerta': bool(brecha)})
        print(os.path.basename(f), flush=True)

    dd = pd.DataFrame(detalle_d)
    por_matriz_d = (dd.groupby('matriz')['alerta'].agg(['size', 'sum'])
                    .assign(cobertura=lambda x: (100 * (1 - x['sum'] / x['size'])).round(1)).reset_index().to_dict('records'))
    salida = {
        'detalle_D': detalle_d,
        'por_matriz_D': por_matriz_d,
        'circularidad': {c: {'celdas': circ[(c, 'total')], 'identicas_en_SaberAsociado': circ[(c, 'en_saber_asociado')],
                             'contenidas_en_texto_RA': circ[(c, 'en_texto_ra')]} for c in ['Saber', 'SaberHacer', 'SaberSer']},
        'escenarios': {n: {'total': v['total'], 'alertas': v['alertas'], 'pct_alertas': round(100 * v['alertas'] / v['total'], 1)}
                       for n, v in res.items()},
        'por_campo': {n: {c: {'total': x['total'], 'alertas': x['alertas'],
                              'pct': round(100 * x['alertas'] / x['total'], 1) if x['total'] else None}
                          for c, x in campos.items()} for n, campos in por_campo.items()},
    }
    json.dump(salida, open('auditoria/evidencia_cobertura_perfil.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    sys.stdout.reconfigure(encoding='utf-8')
    print(json.dumps({k_: salida[k_] for k_ in ['circularidad', 'escenarios']}, ensure_ascii=False, indent=1))
    for n in 'BD':
        print(n, {c: x['pct'] for c, x in salida['por_campo'][n].items()})


if __name__ == '__main__':
    main()
