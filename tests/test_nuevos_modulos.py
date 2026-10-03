"""
Tests básicos para módulos del Sprint 1-4.
"""

import pandas as pd
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))


def test_nucleos_cleaner():
    from src.nucleos_cleaner import (
        tokenizar_nucleo_celda, limpiar_nucleo, es_nucleo_valido,
        calcular_score_academico, filtrar_nucleos_dataframe
    )
    from config import NUCLEOS_CONFIG
    items = tokenizar_nucleo_celda('1. Tema A\n2. Tema B')
    assert len(items) == 2
    # Separación por numeración (D7): un núcleo con comas o en varias líneas es uno solo
    items = tokenizar_nucleo_celda('1. Oferta, demanda y\nequilibrio\n2.Costos')
    assert items == ['Oferta, demanda y equilibrio', 'Costos']
    # Celda sin numeración: una línea = un núcleo
    assert tokenizar_nucleo_celda('Mi empresa\nMi ciudad') == ['Mi empresa', 'Mi ciudad']
    assert limpiar_nucleo('1. Tema') == 'Tema'
    valido, razon = es_nucleo_valido('Analisis financiero')
    assert valido and razon == ''
    # Control mínimo, siempre activo
    assert not es_nucleo_valido('[Escribir los núcleos]')[0]
    assert not es_nucleo_valido('12.3')[0]
    # Filtros heurísticos: desactivados por defecto, activables por configuración
    assert es_nucleo_valido('Planeación')[0]
    NUCLEOS_CONFIG['FILTROS_ESTRICTOS'] = True
    try:
        invalido, _ = es_nucleo_valido('Salgamos')
        assert not invalido
    finally:
        NUCLEOS_CONFIG['FILTROS_ESTRICTOS'] = False
    score = calcular_score_academico('Analisis financiero de estados')
    assert 0 <= score <= 1
    df = pd.DataFrame({'Nucleos tematicos': ['1. Valido\n2. No']})
    df_filt = filtrar_nucleos_dataframe(df)
    assert 'nucleos_validos' in df_filt.columns
    assert 'nucleos_rechazados' in df_filt.columns
    print("test_nucleos_cleaner: OK")


def test_perfil_coverage():
    from src.perfil_coverage_analyzer import (
        analizar_cobertura_perfil_completa,
        _split_elementos_perfil,
        calcular_cobertura_elemento,
        construir_corpus_curriculo,
    )

    # Smart split: texto corto no se fragmenta
    partes = _split_elementos_perfil('Analisis financiero / gestion de costos')
    assert len(partes) == 1

    df_perfil = pd.DataFrame({
        'Programa': ['Test'],
        'Saber': ['Analisis financiero'],
        'SaberHacer': ['Aplica metodos cuantitativos'],
        'Areas profesionales': ['Gerencia administrativa'],
    })
    df_ra = pd.DataFrame({
        'SaberAsociado': [
            'analisis financiero de estados contables',
            'evaluacion economica de proyectos',
            'gestion de costos empresariales',
        ],
    })
    df_micro = pd.DataFrame({
        'Nombre asignatura o modulo': ['Contabilidad', 'Finanzas', 'Administracion'],
        'Indicadores de logro asignatura o modulo': [
            'aplica metodos cuantitativos en decisiones gerenciales',
            'analiza estados financieros de la empresa',
            'desarrolla gerencia administrativa organizacional',
        ],
        'Nucleos tematicos': ['finanzas', 'administracion', 'costos'],
    })

    corpus, fuentes = construir_corpus_curriculo(df_micro, df_ra)
    assert len(corpus) >= 3
    assert len(fuentes) == len(corpus)

    score, idx, asig, doc = calcular_cobertura_elemento(
        'analisis financiero', corpus, fuentes
    )
    assert 0 <= score <= 1
    if score > 0:
        assert asig or doc

    result = analizar_cobertura_perfil_completa(df_perfil, df_micro, df_ra)
    assert result['total_elementos'] > 0
    assert 0 <= result['cobertura_global'] <= 100
    assert 'cobertura_por_campo' in result
    assert isinstance(result['cobertura_por_campo'], dict)
    elem = result['elementos'][0]
    assert 'asignatura_trazable' in elem
    assert 'umbral' in elem
    assert 'doc_trazable' in elem
    print("test_perfil_coverage: OK")


def test_shared_subjects():
    from src.shared_subjects_analyzer import detectar_asignaturas_compartidas
    df = pd.DataFrame({
        'Programa': ['A', 'A', 'B'], 'Sede': ['X', 'Y', 'X'],
        'Codigo': ['P001', 'P002', 'P001'],
        'Nombre asignatura o modulo': ['Mate', 'Mate', 'Fisica'],
        'Indicadores de logro asignatura o modulo': ['a', 'a', 'b']
    })
    result = detectar_asignaturas_compartidas(df)
    assert result['resumen']['total_programas'] == 2
    print("test_shared_subjects: OK")


def test_topic_modeler():
    from src.topic_modeler import entrenar_lda
    corpus = [
        'analisis financiero de estados contables aplicacion de normas NIIF',
        'mercadeo estrategico plan de marketing investigacion de mercados',
        'gestion del talento humano desarrollo organizacional liderazgo',
        'programacion orientada a objetos desarrollo de software',
        'estadistica inferencial aplicada a la investigacion de mercados',
        'contabilidad de costos y presupuestos para la toma de decisiones',
    ]
    result = entrenar_lda(corpus, n_topics=2, n_top_words=5)
    assert len(result['topics']) == 2
    assert result['model'] is not None
    print("test_topic_modeler: OK")


def test_topicos_consenso():
    import pandas as pd
    from src.topic_modeler import modelar_topicos_consenso
    temas = ['1. Estados financieros\n2. Normas contables NIIF\n3. Presupuestos y costos',
             '1. Plan de mercadeo\n2. Investigación de mercados\n3. Marketing digital',
             '1. Programación orientada a objetos\n2. Bases de datos\n3. Desarrollo de software']
    filas = [{'Programa': f'P{i % 3}', 'Archivo': f'P{i % 3}_A.xlsx', 'Nombre asignatura o módulo': f'Asig {i}',
              'Núcleos temáticos': temas[i % 3]} for i in range(30)]
    # Una sede repetida del programa P0: debe excluirse del corpus
    filas += [{'Programa': 'P0', 'Archivo': 'P0_B.xlsx', 'Nombre asignatura o módulo': 'Asig repetida',
               'Núcleos temáticos': temas[0]}]
    r = modelar_topicos_consenso(pd.DataFrame(filas), k=3, semillas=(0, 1))
    assert len(r['topics']) == 3
    assert r['corpus_size'] == 30
    assert set(r['asignatura_topico']['Programa']) == {'P0', 'P1', 'P2'}
    print("test_topicos_consenso: OK")


def test_report_generator():
    from src.report_generator import ReportGenerator
    gen = ReportGenerator()
    assert gen is not None
    print("test_report_generator: OK")


if __name__ == '__main__':
    test_nucleos_cleaner()
    test_perfil_coverage()
    test_shared_subjects()
    test_topic_modeler()
    test_report_generator()
    print("\nAll tests passed!")
