"""
Vías para elevar el acuerdo del método de asociación (src/asociacion_perfil.py) con la referencia experta,
e indicador de atributos sin asociación en ninguna capa.

  A. Parámetros comunes (situación actual).
  B. Umbrales por capa (competencia, RA y asignatura con su propio umbral).
  C. Indicador por ítem «sin asociación en ninguna capa»: acuerdo, kappa y % método frente a referencia.
  D. Zona de duda: el método decide solo si la evidencia es clara (cobertura muy alta o muy baja); los casos
     intermedios quedan para validación humana. Se informa la proporción decidida y su acuerdo.

Uso: python auditoria/scripts/mejorar_acuerdo_asociacion.py
Salida: auditoria/evidencia_mejora_acuerdo.json
"""
import json
import sys

import numpy as np

src = open('auditoria/scripts/calibrar_asociacion_perfil.py', encoding='utf-8').read().split('PRM = calibrar(CASOS)')[0]
exec(src)   # CASOS, pred, kappa, calibrar, EXPLICITA, PARCIAL, SEMANTICA, ap
sys.stdout.reconfigure(encoding='utf-8')

y = np.array([c[6] for c in CASOS])
capa = np.array([c[2] for c in CASOS])
item = np.array([f'{c[1]}|{c[7]}' for c in CASOS])
enf = np.array([c[0] for c in CASOS])
CMAX = np.array([float(c[4].max()) if len(c[4]) else 0.0 for c in CASOS])      # cobertura con núcleo
SMAX = np.array([float(c[5].max()) if len(c[5]) else 0.0 for c in CASOS])


def acuerdo(p, idx=None):
    idx = np.arange(len(y)) if idx is None else idx
    return round(float(np.mean(p[idx] == y[idx])), 3), kappa(y[idx], p[idx])


# A. Parámetros comunes
PRM = calibrar(CASOS)
pA = np.array([pred(c, PRM) for c in CASOS])
R = {'A_comun': {'parametros': PRM, 'acuerdo_kappa': acuerdo(pA)}}

# B. Umbrales por capa (cada capa calibrada por separado, objetivo kappa promedio por enfoque)
pB = pA.copy()
prm_capa = {}
for k in ap.CAPAS:
    idx = np.where(capa == k)[0]
    prm_capa[k] = calibrar([CASOS[i] for i in idx])
    pB[idx] = [pred(CASOS[i], prm_capa[k]) for i in idx]
R['B_por_capa'] = {'parametros': prm_capa, 'acuerdo_kappa': acuerdo(pB),
                   'por_capa': {k: acuerdo(pB, np.where(capa == k)[0]) for k in ap.CAPAS}}

# C. Sin asociación en ninguna capa (por ítem)
def ninguna(p):
    out = {}
    for i, it in enumerate(item):
        out.setdefault(it, []).append(p[i])
    return {it: int(not any(v)) for it, v in out.items()}


ref_n, met_n = ninguna(y), ninguna(pB)
its = sorted(ref_n)
yr, pm = np.array([ref_n[i] for i in its]), np.array([met_n[i] for i in its])
R['C_sin_asociacion'] = {'items': len(its), 'referencia_%': round(100 * yr.mean(), 1), 'metodo_%': round(100 * pm.mean(), 1),
                         'acuerdo': round(float(np.mean(yr == pm)), 3), 'kappa': kappa(yr, pm),
                         'por_matriz': {}}
for m in sorted({i.split('|')[0] for i in its}):
    sel = [k for k, i in enumerate(its) if i.startswith(m + '|')]
    R['C_sin_asociacion']['por_matriz'][m] = {'items': len(sel), 'referencia_%': round(100 * yr[sel].mean(), 1),
                                              'metodo_%': round(100 * pm[sel].mean(), 1)}

# D. Zona de duda: decide si la cobertura es claramente alta o baja
zonas = []
for bajo in np.round(np.arange(0.0, 0.31, 0.05), 2):
    for alto in np.round(np.arange(0.2, 0.71, 0.05), 2):
        if alto <= bajo:
            continue
        decide = (CMAX >= alto) | (CMAX < bajo)
        if decide.sum() == 0:
            continue
        p = (CMAX >= alto).astype(int)
        idx = np.where(decide)[0]
        a, kp = acuerdo(p, idx)
        zonas.append({'bajo': float(bajo), 'alto': float(alto), 'decide_%': round(100 * decide.mean(), 1), 'acuerdo': a, 'kappa': kp})
zonas = [z for z in zonas if z['acuerdo'] >= 0.80]
R['D_zona_de_duda'] = sorted(zonas, key=lambda z: -z['decide_%'])[:8]

json.dump(R, open('auditoria/evidencia_mejora_acuerdo.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=str)
print(json.dumps({k: v for k, v in R.items() if k != 'C_sin_asociacion'}, ensure_ascii=False, indent=1, default=str))
print(json.dumps({k: v for k, v in R['C_sin_asociacion'].items() if k != 'por_matriz'}, ensure_ascii=False))
for m, v in R['C_sin_asociacion']['por_matriz'].items():
    print('  ', m, v)
