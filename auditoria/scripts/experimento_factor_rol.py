"""
Experimento: efecto de suavizar la regla de rol (FACTOR_ROL) en el acuerdo con la referencia y en el indicador
«sin asociación en ninguna capa». Recalibra los parámetros para cada factor.

Uso: python auditoria/scripts/experimento_factor_rol.py
Salida: auditoria/evidencia_factor_rol.json
"""
import json
import sys

import numpy as np

sys.path.insert(0, '.')
import src.asociacion_perfil as ap  # noqa: E402

CAL = open('auditoria/scripts/calibrar_asociacion_perfil.py', encoding='utf-8').read().split('PRM = calibrar(CASOS)')[0]
R = {}
for factor in (0.0, 0.5, 1.0):
    ap.FACTOR_ROL = factor
    ns = {}
    exec(CAL, ns)
    casos, pred, kappa, calibrar = ns['CASOS'], ns['pred'], ns['kappa'], ns['calibrar']
    prm = calibrar(casos)
    y = np.array([c[6] for c in casos])
    p = np.array([pred(c, prm) for c in casos])
    item = [f'{c[1]}|{c[7]}' for c in casos]
    yi, pi = {}, {}
    for k, it in enumerate(item):
        yi.setdefault(it, []).append(y[k])
        pi.setdefault(it, []).append(p[k])
    its = sorted(yi)
    yn = np.array([int(not any(yi[i])) for i in its])
    pn = np.array([int(not any(pi[i])) for i in its])
    R[str(factor)] = {'parametros': prm, 'acuerdo': round(float((y == p).mean()), 3), 'kappa': kappa(y, p),
                      'sin_asociacion': {'referencia_%': round(100 * yn.mean(), 1), 'metodo_%': round(100 * pn.mean(), 1),
                                         'acuerdo': round(float((yn == pn).mean()), 3), 'kappa': kappa(yn, pn)},
                      'por_capa': {cp: (round(float((y[ix] == p[ix]).mean()), 3), kappa(y[ix], p[ix]))
                                   for cp in ap.CAPAS for ix in [np.array([c[2] == cp for c in casos])]}}
    print(factor, json.dumps(R[str(factor)], ensure_ascii=False), flush=True)
json.dump(R, open('auditoria/evidencia_factor_rol.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
