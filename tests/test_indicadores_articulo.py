"""Indicadores V1–V5 y contrastes R6–R7 (src/indicadores_articulo.py)."""
import os

import pytest

from src import indicadores_articulo as ia

MATRIZ = 'data/raw/FORMATOS RA CICLO UNO RC/FormatoRA_MEDSTEM_VNAL.xlsx'


def test_nombre_matriz():
    assert ia.nombre_matriz('FormatoRA_ContPub_PBOG.xlsx') == ('ContPub_PBOG', 'ContPub', 'PBOG')
    assert ia.nombre_matriz('FormatoRA_Otro.xlsx')[2] == 'ND'


def _fila(matriz, sede, v1, v2, v4, v5):
    return {'Matriz': matriz, 'Sede': sede, 'V1 %': v1, 'V2': v2, 'V4 %': v4, 'V5 %': v5}


def test_contrastes_pocas_matrices_explica_motivo():
    out = ia.contrastes([_fila('A_PBOG', 'PBOG', 60, 'Sí', 80, 0)])
    assert not out['spearman'] and out['motivos']


def test_contrastes_excluye_constantes_y_sedes_unitarias():
    filas = [_fila(f'P{i}_{s}', s, 50 + i, 'Sí', 70 + (i % 5), 0) for i, s in
             enumerate(['PBOG'] * 6 + ['VNAL'] * 6 + ['HBOG'])]
    out = ia.contrastes(filas)
    pares = {d['Par'] for d in out['spearman']}
    assert pares == {'V1–V4'}                       # V2 y V5 constantes
    assert any('HBOG' in m for m in out['motivos'])  # sede con una sola matriz
    assert {d['Variable'] for d in out['kruskal']} == {'V1', 'V4'}


@pytest.mark.skipif(not os.path.exists(MATRIZ), reason='matriz de ejemplo no disponible')
def test_calcular_indicadores_con_v1_externo():
    r = ia.calcular_indicadores([(os.path.basename(MATRIZ), MATRIZ)], v1={'MEDSTEM_VNAL': (14, 18)})
    g = r['globales']
    assert not r['errores'] and g['matrices'] == 1
    assert g['V1'] == round(100 * 14 / 18, 1)
    assert r['por_matriz'][0]['V1 %'] == g['V1']
    assert g['RA_competencia'] is not None and 0 <= g['V4'] <= 100
