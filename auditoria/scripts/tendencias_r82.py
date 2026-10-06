"""
R8.2 (D30): tendencias en dos niveles, total y sin el núcleo común institucional, e IA desagregada.

Base: auditoria/Tendencias_integradas_15.xlsx (tendencias_integradas.py con la lista depurada D30).
- Núcleo común: denominaciones presentes en el mayor número de programas, separadas del resto por el mayor salto en
  el número de programas (se calcula, no se fija un umbral).
- T15 (formación ciudadana, humanística, investigativa y práctica) se informa aparte como formación transversal: sus
  términos describen componentes curriculares, no tendencias del sector.
- IA validada en las fuentes: integrada si la IA está en un núcleo temático (se enseña); se excluyen las asignaturas que
  solo la mencionan en un indicador de logro (Diseño e Innovación Curricular). Dedicada si la asignatura estudia las
  técnicas de IA en sí.

Uso: python auditoria/scripts/tendencias_r82.py
Salida: auditoria/evidencia_tendencias_r82.json
"""
import json
import re
import sys
import unicodedata

import pandas as pd

sys.stdout.reconfigure(encoding='utf-8')
n = lambda t: re.sub(r'\s+', ' ', unicodedata.normalize('NFKD', str(t)).encode('ascii', 'ignore').decode().lower()).strip()  # noqa: E731

d = pd.read_excel('auditoria/Tendencias_integradas_15.xlsx', sheet_name='Asignaturas')
d['k'] = d['Asignatura'].map(n)
N_ASIG, N_PROG = len(d), d['Programa'].nunique()

prog_por_den = d.groupby('k')['Programa'].nunique().sort_values(ascending=False)
saltos = prog_por_den.diff(-1).iloc[:-1]
corte = saltos.values.argmax() + 1
COMUN = set(prog_por_den.index[:corte])

IA_SOLO_MENCION = {'diseno e innovacion curricular'}
IA_DEDICADA = {'machine learning', 'machine learning para las tic', 'modelos de inteligencia artificial para las tic'}
IA_COMUN = {'analisis y visualizacion de datos'}

d['tend'] = d['Tendencias'].fillna('').map(lambda s: re.findall(r'(T\d\d) ', s))
d.loc[d['k'].isin(IA_SOLO_MENCION), 'tend'] = d.loc[d['k'].isin(IA_SOLO_MENCION), 'tend'].map(
    lambda t: [x for x in t if x != 'T01'])
nombres = {m.group(1): m.group(2).strip() for s in d['Tendencias'].dropna() for m in re.finditer(r'(T\d\d) ([^,]+(?:, [^T,][^,]*)*)', s)}

por = {}
for k in sorted({x for t in d['tend'] for x in t}):
    x = d[d['tend'].map(lambda t: k in t)]
    propia = x[~x['k'].isin(COMUN)]
    por[k] = {'nombre': nombres.get(k, k), 'asignaturas': len(x), 'pct': round(100 * len(x) / N_ASIG, 1),
              'programas': int(x['Programa'].nunique()), 'programas_propia': int(propia['Programa'].nunique()),
              'asignaturas_propia': len(propia)}

ia = d[d['tend'].map(lambda t: 'T01' in t)]
p_comun = set(ia.loc[ia['k'].isin(IA_COMUN), 'Programa'])
p_integ = set(ia.loc[~ia['k'].isin(IA_COMUN | IA_DEDICADA), 'Programa'])
p_ded = set(ia.loc[ia['k'].isin(IA_DEDICADA), 'Programa'])
EV = {'asignaturas': N_ASIG, 'programas': N_PROG,
      'cobertura_pct': round(100 * (d['tend'].map(len) > 0).mean(), 1),
      'nucleo_comun': {k: int(prog_por_den[k]) for k in sorted(COMUN)},
      'siguiente_denominacion': {prog_por_den.index[corte]: int(prog_por_den.iloc[corte])},
      'por_tendencia': por,
      'IA': {'asignaturas': len(ia), 'pct': round(100 * len(ia) / N_ASIG, 1), 'programas': len(p_comun | p_integ | p_ded),
             'programas_solo_comun': len(p_comun - p_integ - p_ded), 'programas_integrada_propia': len(p_integ),
             'programas_dedicada': len(p_ded), 'programas_dedicada_sin_integrada': len(p_ded - p_integ),
             'asignaturas_comun': int(ia['k'].isin(IA_COMUN).sum()),
             'asignaturas_integrada_propia': int((~ia['k'].isin(IA_COMUN | IA_DEDICADA)).sum()),
             'asignaturas_dedicada': int(ia['k'].isin(IA_DEDICADA).sum()),
             'integrada_propia': sorted(set(ia.loc[~ia['k'].isin(IA_COMUN | IA_DEDICADA), 'Asignatura'])),
             'excluida_solo_mencion': sorted(IA_SOLO_MENCION)}}
json.dump(EV, open('auditoria/evidencia_tendencias_r82.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(json.dumps(EV, ensure_ascii=False, indent=1))
