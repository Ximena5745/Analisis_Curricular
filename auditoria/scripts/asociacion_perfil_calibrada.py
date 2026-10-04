"""
Calibra src/asociacion_perfil.py contra la reevaluación experta (AdmonEmpresas_PBOG) y lo aplica a Contaduría Pública.

Referencia: decisiones respaldado (1) / no respaldado (0) por ítem y capa, de la lectura de la matriz original
(funciones del texto narrativo, componentes esenciales y atributos del perfil profesional). Respaldo = explícito
o parcial; las relaciones solo temáticas y las entidades genéricas no cuentan.
Calibración: rejilla sobre el umbral léxico (común) y el semántico (por capa), maximizando el acuerdo.

Uso: python auditoria/scripts/asociacion_perfil_calibrada.py
Salida: auditoria/Asociacion_perfil_ContPub.xlsx y auditoria/evidencia_asociacion_calibrada.json
"""
import glob
import json
import logging
import os
import sys
import warnings

import numpy as np
import pandas as pd

warnings.filterwarnings('ignore')
logging.disable(logging.CRITICAL)
os.environ.setdefault('HF_HUB_OFFLINE', '1')
sys.path.insert(0, '.')
sys.stdout.reconfigure(encoding='utf-8')
import src.asociacion_perfil as ap  # noqa: E402

RAIZ = 'data/raw/FORMATOS RA CICLO UNO RC/'
# (inicio del ítem normalizado) -> (Competencia, RA, Asignatura)
REFERENCIA = {
    # Perfil ocupacional: texto narrativo
    'desarrollar estrategias corporativas': (1, 1, 1), 'gestionar areas funcionales': (1, 1, 1),
    'dirigir equipos de trabajo': (1, 1, 1), 'implementar planes estrategicos': (1, 1, 1),
    'implementar planes tacticos': (0, 0, 1), 'implementar planes operativos': (0, 1, 1),
    'administrar sistemas de gestion': (0, 0, 1), 'identificar oportunidades de negocio': (1, 1, 1),
    'convertir en iniciativas productivas': (1, 1, 1), 'generar valor en distintos sectores': (1, 1, 1),
    # Perfil ocupacional: componentes esenciales
    'gerencia administrativa': (1, 1, 1), 'gestion empresarial': (1, 1, 1), 'gestion de proyectos': (1, 0, 1),
    'analisis estrategico': (1, 1, 1), 'consultoria empresarial': (0, 0, 1),
    'coordinar o liderar areas': (1, 1, 1), 'estructurar e implementar planes': (1, 1, 1),
    'desarrollar proyectos empresariales': (1, 1, 1), 'realizar consultoria': (0, 0, 1),
    'emprender iniciativas empresariales': (1, 1, 1), 'gerenciar y administrar cualquier': (1, 1, 1),
    'gerenciar proyectos de cualquier': (1, 0, 1), 'empresas privadas o de economia': (1, 1, 1),
    'starups': (1, 1, 1), 'organizaciones no gubernamentales': (0, 0, 0), 'sector publico': (0, 0, 0),
    'ecosistemas de innovacion': (1, 1, 1),
    # Perfil profesional
    'pensamiento critico': (0, 0, 1), 'compromiso con el desarrollo': (1, 1, 1),
    'formula estrategias organizacionales': (1, 1, 1), 'ejecuta estrategias organizacionales': (1, 1, 1),
    'integra conocimientos en gestion': (1, 0, 1), 'toma decisiones informadas': (1, 1, 1),
    'lidera proyectos empresariales': (1, 1, 1), 'promueve modelos de negocio': (1, 1, 1),
    'aporta a la generacion de valor': (1, 1, 1), 'actua conforme al marco legal': (1, 1, 1),
}


def ref_de(item):
    n = ap._norm(item)
    return next((v for k, v in REFERENCIA.items() if n.startswith(k)), None)


def kappa(y, p):
    y, p = np.array(y), np.array(p)
    po = (y == p).mean()
    pe = y.mean() * p.mean() + (1 - y.mean()) * (1 - p.mean())
    return round(float((po - pe) / (1 - pe)), 3) if pe < 1 else 1.0


# 1. Calibración sobre AdmonEmpresas_PBOG
m = ap.leer_matriz(RAIZ + 'FormatoRA_AdmonEmpresas_PBOG.xlsx')
items = ap.items_perfil(m)
P = ap.puntajes(m, items)
idx = [(i, ref_de(it['item'])) for i, it in enumerate(items) if ref_de(it['item'])]
faltan = [k for k in REFERENCIA if not any(ap._norm(it['item']).startswith(k) for it in items)]
print('Ítems de referencia emparejados:', len(idx), 'de', len(REFERENCIA), '| sin emparejar:', faltan)


def predice(capa, i, prm):
    cob, sem = (P[capa]['cob_n'] if prm['nucleo'] else P[capa]['cob'])[i], P[capa]['sem'][i]
    return int(((cob >= prm['explicita']) | ((cob >= prm['parcial']) & (sem >= prm['semantica']))).any())


mejor = None
for nu in (False, True):
  for e in np.round(np.arange(0.20, 1.01, 0.05), 2):
    for pa in np.round(np.arange(0.05, e + 0.001, 0.05), 2):
        for se in np.round(np.arange(0.30, 0.91, 0.02), 2):
            prm = {'explicita': float(e), 'parcial': float(pa), 'semantica': float(se), 'nucleo': nu}
            acc = np.mean([predice(capa, i, prm) == r[c] for c, capa in enumerate(ap.CAPAS) for i, r in idx])
            if mejor is None or acc > mejor[0] + 1e-9:
                mejor = (acc, prm)
ACUERDO, PRM = mejor
CAL = {}
for c, capa in enumerate(ap.CAPAS):
    y = [r[c] for _, r in idx]
    pr = [predice(capa, i, PRM) for i, _ in idx]
    CAL[capa] = {'acuerdo': round(float(np.mean(np.array(pr) == np.array(y))), 3), 'kappa': kappa(y, pr),
                 'pred_%': round(100 * np.mean(pr), 1), 'ref_%': round(100 * np.mean(y), 1)}
yy = [r[c] for c, _ in enumerate(ap.CAPAS) for _, r in idx]
pp = [predice(capa, i, PRM) for capa in ap.CAPAS for i, _ in idx]
CAL['Global'] = {'acuerdo': round(float(ACUERDO), 3), 'kappa': kappa(yy, pp)}
print('Parámetros:', PRM)
print(json.dumps(CAL, ensure_ascii=False, indent=1))
discrepancias = []
for c, capa in enumerate(ap.CAPAS):
    for i, r in idx:
        p = predice(capa, i, PRM)
        if p != r[c]:
            k = int(np.argmax(P[capa]['cob'][i] + P[capa]['sem'][i]))
            discrepancias.append({'Ítem': items[i]['item'], 'Capa': capa, 'Referencia': r[c], 'Método': p,
                                  'Cobertura máx.': round(float(P[capa]['cob'][i].max()), 3),
                                  'Similitud máx.': round(float(P[capa]['sem'][i].max()), 3),
                                  'Entidad más cercana': m['entidades'][capa][k]['nombre'][:120],
                                  'Unidad': str(P[capa]['evidencia'][i][k])[:120]})
print('Discrepancias con la referencia:', len(discrepancias))
for d in discrepancias:
    print('  ', d)
U_LEX, U_SEM = PRM['explicita'], PRM


# 2. Aplicación a Contaduría Pública
def resumen(df, claves):
    out = []
    for k, g in df.groupby(claves):
        base = g.groupby(['item', 'capa'])['entidad'].apply(lambda s: (s != 'NINGUNA').any()).unstack()
        r = dict(zip(claves, k if isinstance(k, tuple) else (k,)))
        r['Ítems'] = len(base)
        for capa in ap.CAPAS:
            r[f'% {capa}'] = round(100 * base[capa].mean(), 1)
        r['% en las tres capas'] = round(100 * base.all(axis=1).mean(), 1)
        r['Sin asociación'] = int((~base.any(axis=1)).sum())
        out.append(r)
    return pd.DataFrame(out)


filas = []
for f in sorted(glob.glob(RAIZ + 'FormatoRA_ContPub_*.xlsx')):
    matriz = os.path.basename(f)[10:-5]
    for r in ap.asociar(f, PRM):
        filas.append({'Matriz': matriz, **r})
    print('ok', matriz)
d = pd.DataFrame(filas)
d['grupo'] = np.where(d['origen'] == 'Texto narrativo', d['perfil'] + ' · texto narrativo', 'Perfil ocupacional · componentes')
res = resumen(d, ['Matriz', 'grupo'])
res_comp = resumen(d[d['origen'] != 'Texto narrativo'], ['Matriz', 'origen'])
print(res.to_string(index=False))
print(res_comp.to_string(index=False))
sin = (d.groupby(['Matriz', 'perfil', 'origen', 'item', 'capa'])['entidad'].apply(lambda s: (s != 'NINGUNA').any())
       .unstack().reset_index())
with pd.ExcelWriter('auditoria/Asociacion_perfil_ContPub.xlsx') as xw:
    res.to_excel(xw, sheet_name='Resumen', index=False)
    res_comp.to_excel(xw, sheet_name='Componentes', index=False)
    sin.to_excel(xw, sheet_name='Item_x_capa', index=False)
    d.drop(columns='grupo').to_excel(xw, sheet_name='Detalle', index=False)
    pd.DataFrame([{'Capa': k, **v} for k, v in CAL.items()]).to_excel(xw, sheet_name='Calibracion', index=False)
    pd.DataFrame(discrepancias).to_excel(xw, sheet_name='Discrepancias_ref', index=False)
    pd.DataFrame({'Elemento': ['Alcance', 'Ítems', 'Entidades', 'Explícita', 'Parcial', 'Calibración', 'Limitación'],
                  'Definición': ['Cada matriz se compara solo con su propio contenido.',
                                 'Funciones del texto narrativo (extractor de atributos) y componentes esenciales del Paso 1 (una línea = un ítem).',
                                 'Competencias específicas, RA de programa y asignaturas no electivas; sin la competencia genérica ni su RA.',
                                 f"Cobertura del concepto (lemas del ítem ponderados por IDF de la matriz, con equivalencias) ≥ {PRM['explicita']}.",
                                 f"Cobertura ≥ {PRM['parcial']} y similitud semántica ≥ {PRM['semantica']}.",
                                 'Umbrales que maximizan el acuerdo con la reevaluación experta de AdmonEmpresas_PBOG (hoja Calibracion).',
                                 'Calibrado con un programa; requiere validación experta en Contaduría (hoja Detalle con evidencia).']}
                 ).to_excel(xw, sheet_name='Definiciones', index=False)
json.dump({'parametros': PRM, 'calibracion': CAL, 'discrepancias': discrepancias,
           'resumen_contpub': res.to_dict('records'), 'componentes_contpub': res_comp.to_dict('records')},
          open('auditoria/evidencia_asociacion_calibrada.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
