"""Pruebas de la extracción de atributos del perfil de egreso (src/atributos_perfil.py)."""
from src.atributos_perfil import extraer_atributos

LEX = {'formular', 'ejecutar', 'integrar', 'liderar', 'promover', 'desarrollar', 'gestionar', 'dirigir',
       'implementar', 'administrar', 'identificar', 'convertir', 'participar', 'publicar'}

PROF = ("El profesional en Administración de Empresas del Politécnico Grancolombiano formula y ejecuta estrategias "
        "organizacionales innovadoras, integrando conocimientos en gestión organizacional con metodologías de análisis de "
        "información. Su formación integral le permite tomar decisiones informadas en contextos cambiantes, liderar proyectos "
        "empresariales, y promover modelos de negocio sostenibles, aportando a la generación de valor organizacional. Se "
        "caracteriza por su pensamiento crítico y compromiso con el desarrollo organizacional, según las dinámicas del entorno "
        "y el marco legal vigente.")


def _textos(atributos, tipo=None):
    return [a[2] for a in atributos if tipo is None or a[0] == tipo]


def test_acciones_y_verbos_coordinados():
    acc = _textos(extraer_atributos(PROF, LEX), 'Acción')
    assert 'formula estrategias organizacionales innovadoras' in acc
    assert 'ejecuta estrategias organizacionales innovadoras' in acc
    assert 'tomar decisiones informadas en contextos cambiantes' in acc
    assert 'liderar proyectos empresariales' in acc
    assert 'promover modelos de negocio sostenibles' in acc


def test_rasgos():
    assert _textos(extraer_atributos(PROF, LEX), 'Rasgo') == ['pensamiento crítico', 'compromiso con el desarrollo organizacional']


def test_roles_y_funciones_nominales():
    a = extraer_atributos('El egresado podrá desempeñarse como asesor, analista, investigador o consultor. '
                          'Posee conocimientos en algoritmia, programación, bases de datos y redes.', LEX)
    assert _textos(a, 'Rol') == ['asesor', 'analista', 'investigador', 'consultor']
    assert _textos(a, 'Conocimiento') == ['algoritmia', 'programación', 'bases de datos', 'redes']


def test_vinetas_bajo_como():
    a = extraer_atributos('Puede desempeñarse en:\nEn el sector público como:\n- Funcionario público\n- Contratista o interventor', LEX)
    assert _textos(a, 'Rol') == ['Funcionario público', 'Contratista o interventor']


def test_tilde_no_verbal():
    a = extraer_atributos('Gestiona proyectos de la administración pública y privada.', LEX)
    assert all(v != 'publicar' for _, v, _ in a)


def test_adjetivos_coordinados_y_relativa():
    a = extraer_atributos('Está capacitado para implementar planes estratégicos, tácticos y operativos, y convertirlas en '
                          'iniciativas productivas que generen valor en distintos sectores.', LEX | {'generar'})
    acc = _textos(a, 'Acción')
    assert {'implementar planes estratégicos', 'implementar planes tácticos', 'implementar planes operativos'} <= set(acc)
    assert 'generar valor en distintos sectores' in acc


def test_normativo_finalidad_medios_y_rasgo():
    lex = LEX | {'evaluar', 'asesorar', 'ejercer'}
    a = extraer_atributos('Evalúa la calidad de la información financiera de personas naturales, jurídicas y organizaciones, '
                          'con el propósito de garantizar el cumplimiento normativo y dar soporte a la toma de decisiones. '
                          'Asesora a los usuarios mediante la interpretación de datos, el análisis de riesgos y la verificación '
                          'de la información. Ejerce su rol con responsabilidad frente a la fe pública, según el marco legal vigente.', lex)
    assert _textos(a, 'Finalidad') == ['garantizar el cumplimiento normativo', 'dar soporte a la toma de decisiones']
    assert {'interpretación de datos', 'análisis de riesgos'} <= set(_textos(a, 'Función'))
    assert 'responsabilidad frente a la fe pública' in _textos(a, 'Rasgo')
    assert _textos(a, 'Normativo') == ['actuar conforme al marco legal vigente']


def test_forma_breve():
    from src.atributos_perfil import forma_breve
    assert forma_breve('Acción', 'promover', 'promover modelos de negocio sostenibles', 'tercera') == 'Promueve modelos de negocio sostenibles'
    assert forma_breve('Acción', 'evaluar', 'evalúa la información de personas naturales, jurídicas y organizaciones, '
                       'con el propósito de garantizar', 'tercera') == 'Evalúa información de personas naturales, jurídicas y organizaciones'
    assert forma_breve('Acción', 'ejercer', 'Ejerce su rol con responsabilidad frente a la fe pública y con una perspectiva',
                       'tercera') == 'Ejerce su rol con responsabilidad frente a la fe pública'
    assert forma_breve('Acción', 'gestionar', 'gestionar áreas funcionales clave con visión sostenible') == 'Gestionar áreas funcionales clave'


def test_texto_vacio():
    assert extraer_atributos('', LEX) == []
