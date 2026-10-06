"""Informes PDF del Resumen Ejecutivo (src/informes_pdf.py)."""
from src import indicadores_articulo as ia
from src import informes_pdf as ip

FILA = {'Matriz': 'Prog_PBOG', 'Programa': 'Prog', 'Sede': 'PBOG', 'Competencias': 4, 'RA únicos': 10,
        'Estrategias': 3, 'V1 %': 80.0, 'RA con competencia %': 100.0, 'V2': 'No', 'Verbos repetidos': 'analizar',
        'V3 %': 90.0, 'V4 %': 70.0, 'RA sin estrategia': 3, 'V5 %': 100.0, 'Evidencia directa %': 0.0,
        'Estrategias con indicador e instrumento': 2, 'Indicadores por nivel': {'N1': 2, 'N2': 3}}


def test_texto_sustituye_caracteres_fuera_de_latin1():
    assert ip.texto('**V1–V5** ≥ 0,80 → κ…') == 'V1-V5 >= 0,80 -> kappa...'
    assert ip.texto('Núcleos «temáticos»') == 'Núcleos «temáticos»'


def test_recomendaciones_solo_para_criterios_no_cumplidos():
    estados = {'V1': 'Parcial', 'V2': 'No cumple', 'V3': 'Cumple', 'V4': 'Parcial', 'V5': 'Parcial'}
    recs = ip.recomendaciones_matriz(estados, FILA, n_sin_perfil=2, n_ra_no_eval=0, n_est_incompletas=1)
    prefijos = [r.split(':')[0] for r in recs]
    assert prefijos == ['V1 Perfil', 'V2 Coherencia', 'V4 Trazabilidad', 'V5 Indicadores',
                        'Evidencia (recomendación, sin criterio en la plantilla)']
    assert 'analizar' in recs[1] and '3 RA' in recs[2]


def test_informes_generan_pdf():
    val = ia.valorar_matriz(FILA, 20.0, 45.0, ia.referencias_conjunto([FILA]), 30.0)
    estados = {v['Variable']: v['Estado'] for v in val if v['Variable'] != '—'}
    prioridad = {'Matriz': 'Prog_PBOG', 'Programa': 'Prog', **estados, 'No cumple': 1, 'Parcial': 3}
    general = ip.informe_general({
        'alcance': 'Filtros: ninguno', 'kpis': [('Programas', '1')], 'criterios': ia.CRITERIOS,
        'globales': {'matrices': 1, 'V1': 80.0, 'V2': 0.0, 'V3': 90.0, 'V4': 70.0, 'V5': 100.0},
        'conteo_criterios': [('V1 Perfil alineado', {'Parcial': 1})], 'lectura': ['**1 de 1** matrices'],
        'prioridades': [prioridad], 'alertas': [], 'programas': [],
        'tendencias': [{'Tendencia': 'IA', 'Asignaturas': 0, '% de asignaturas': 0.0, 'Programas': 0,
                        '% de programas': 0.0}]})
    programa = ip.informe_programa({
        'programa': 'Programa – prueba', 'kpis': [('RA únicos', '10')], 'criterios': ia.CRITERIOS,
        'matrices': [{'matriz': 'Prog_PBOG', 'sede': 'PBOG', 'valoracion': val, 'recomendaciones': ['Revisar'],
                      'sin_alineacion': [['Profesional', 'Funciones', 'Gestionar proyectos']],
                      'ra_no_evaluables': [['Comprender la teoría', 'verbo no observable']],
                      'ra_sin_estrategia': ['Diseñar planes'], 'estrategias_incompletas': [['Proyecto', 'instrumento']]}],
        'tipo_saber': [{'Tipo': 'Saber', 'Programa': 40.0, 'Mediana': 33.3}],
        'tendencias_presentes': ['IA'], 'tendencias_ausentes': [], 'alertas': []})
    for pdf in (general, programa):
        assert pdf.startswith(b'%PDF') and len(pdf) > 2000
