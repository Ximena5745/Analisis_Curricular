"""Control de núcleos con reglas explícitas (src.nucleos_cleaner.control_nucleos_reglas)."""
import pandas as pd

from src.nucleos_cleaner import control_nucleos_reglas


def _df():
    return pd.DataFrame({
        'matriz': ['A'] * 8,
        'asignatura': ['Cálculo Vectorial'] * 4 + ['Contabilidad'] * 4,
        'nucleo': ['Cálculo vectorial', 'Integrales de línea', 'Integrales de línea.', 'Teorema de Green',
                   'Efectivo; inversiones; deudores', 'Activos fijos', 'Pasivos',
                   ' '.join(['palabra'] * 40)],
    })


def test_reglas():
    d = control_nucleos_reglas(_df())
    assert d['igual_al_nombre'].tolist()[0] and d['igual_al_nombre'].sum() == 1
    assert d['duplicado'].tolist()[1:3] == [True, True] and d['duplicado'].sum() == 2
    assert d['varios_temas'].tolist()[4] and d['varios_temas'].sum() == 1
    assert d['extension_atipica'].tolist()[7] and d['extension_atipica'].sum() == 1
    assert d.loc[[3, 5, 6], 'revisar'].eq(False).all()


def test_determinista_y_no_excluye():
    a, b = control_nucleos_reglas(_df()), control_nucleos_reglas(_df())
    assert a.equals(b) and len(a) == len(_df())
