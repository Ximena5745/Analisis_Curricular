"""Reproducibilidad, configuración y robustez de src/asociacion_perfil.py y src/calibracion_asociacion.py."""
import copy
import io
import os

import openpyxl
import pandas as pd
import pytest

from src import asociacion_perfil as ap
from src import calibracion_asociacion as ca

MATRIZ = 'data/raw/FORMATOS RA CICLO UNO RC/FormatoRA_MEDSTEM_VNAL.xlsx'
hay_matriz = pytest.mark.skipif(not os.path.exists(MATRIZ), reason='matriz de ejemplo no disponible')


@pytest.fixture
def config_original():
    cfg = ap.config_actual()
    yield cfg
    ap.aplicar_config(cfg)


def test_config_externa_se_carga():
    cfg = ap.cargar_config()
    assert {'PARAMS', 'SINONIMOS', 'FACTOR_ROL', 'VERSION'} <= set(cfg)
    assert ap.PARAMS == cfg['PARAMS']


def test_huella_estable_y_sensible_a_cambios(config_original):
    h1 = ap.config_actual()['HUELLA']
    assert h1 == ap.config_actual()['HUELLA']
    cfg = copy.deepcopy(config_original)
    cfg['SINONIMOS']['casino'] = ['juego', 'apuesta']
    cfg['VERSION'] = 'prueba'
    ap.aplicar_config(cfg)
    assert ap.config_actual()['HUELLA'] != h1
    assert ap.VERSION_CONFIG == 'prueba'
    assert ap.SINONIMOS['casino'] == {'juego', 'apuesta'}


def _matriz_incompleta() -> io.BytesIO:
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = 'Paso1 Analisis perfil egreso'
    ws.append(['instrucciones'])
    ws.append(['encabezado'])
    ws.append([None, None, 'El egresado diseña estrategias de mercadeo digital.', 'Se desempeña como analista de mercadeo.',
               None, None, None, 'Analista de mercadeo', 'Diseñar campañas digitales', 'Empresas de comercio'])
    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    return buf


def test_matriz_con_hojas_faltantes_no_falla_y_avisa():
    m = ap.leer_matriz(_matriz_incompleta())
    assert any('Paso 2' in a for a in m['avisos'])
    assert any('Paso 3' in a for a in m['avisos'])
    assert any('Paso 5' in a for a in m['avisos'])
    assert m['componentes']
    assert all(not m['entidades'][c] for c in ap.CAPAS)


@hay_matriz
def test_misma_matriz_mismo_resultado():
    a, b = ap.asociar(MATRIZ), ap.asociar(MATRIZ)
    assert pd.DataFrame(a).equals(pd.DataFrame(b))


def test_kappa_y_referencia_invalida():
    assert ca.kappa([1, 0, 1, 0], [1, 0, 1, 0]) == 1.0
    with pytest.raises(ValueError):
        ca.leer_referencia(io.StringIO('Matriz;Inicio_item\nX;algo\n'))
