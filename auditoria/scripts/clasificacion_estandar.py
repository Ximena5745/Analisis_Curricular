"""
Propuesta de clasificación estandarizada y determinista de la oferta (sustituye al LDA, que queda
exploratorio). Tres niveles:

  1. Área de conocimiento — CINE-F 2013 (UNESCO): campo amplio y específico de cada programa;
     las asignaturas heredan el campo de su programa.
  2. Contribución a los ODS — diccionario por ODS (borrador construido a partir de las metas oficiales
     de cada objetivo; requiere validación institucional). Regla: un ODS se asigna a la asignatura si su
     nombre contiene al menos 1 término del ODS o su contenido (núcleos + indicadores) contiene al
     menos 2 términos distintos del ODS. Coincidencia por palabra completa, sin tildes.
  3. Indicador para GreenMetric — asignatura relacionada con sostenibilidad:
       ambiental: al menos un ODS ambiental (6, 7, 11, 12, 13, 14, 15) o la categoría transversal
                  «Sostenibilidad» (sostenibilidad, desarrollo sostenible, ambiental, ODS…);
       ampliada:  al menos un ODS cualquiera.

Unidad: asignatura sin electivas (D10), con su programa. Resultado reproducible: sin semillas.

Uso: python auditoria/scripts/clasificacion_estandar.py
Salida: auditoria/Clasificacion_estandar_oferta.xlsx y auditoria/evidencia_clasificacion_estandar.json
"""
import glob
import json
import logging
import os
import re
import sys
import unicodedata
import warnings
from collections import Counter, defaultdict

import openpyxl
import pandas as pd
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

warnings.filterwarnings('ignore')
logging.disable(logging.CRITICAL)
sys.path.insert(0, '.')
from src.extractor import ExcelExtractor  # noqa: E402
from src.shared_subjects_analyzer import consolidar_asignaturas  # noqa: E402

sys.stdout.reconfigure(encoding='utf-8')
NAVY = '0F385A'


def norm(t):
    t = unicodedata.normalize('NFKD', str(t)).encode('ascii', 'ignore').decode('ascii').lower()
    return re.sub(r'\s+', ' ', re.sub(r'[^a-z0-9 ]', ' ', t)).strip()


# ------------------------------------------------------------------ 1. CINE-F 2013 (campo amplio / específico)
AMPLIO = {'01': 'Educación', '02': 'Artes y humanidades', '03': 'Ciencias sociales, periodismo e información',
          '04': 'Administración de empresas y derecho', '05': 'Ciencias naturales, matemáticas y estadística',
          '06': 'Tecnologías de la información y la comunicación (TIC)', '07': 'Ingeniería, industria y construcción',
          '10': 'Servicios'}
ESPECIFICO = {'011': 'Educación', '021': 'Artes', '032': 'Periodismo e información', '041': 'Educación comercial y administración',
              '042': 'Derecho', '052': 'Medio ambiente', '054': 'Matemáticas y estadística', '061': 'TIC',
              '071': 'Ingeniería y profesiones afines', '101': 'Servicios personales', '104': 'Servicios de transporte'}
CINE = {  # código de archivo: (campo específico, a confirmar)
    'AdmonEmpresas': ('041', ''), 'AdmonHotelGastro': ('101', ''), 'AdmonPub': ('041', ''),
    'ComunicacionDigital': ('032', ''), 'ComunicacionSocial': ('032', ''), 'ComunicacionSocialPeriodismo': ('032', ''),
    'ContPub': ('041', ''), 'Derecho': ('042', ''), 'DisenoDigital': ('021', ''), 'DisenoGrafico': ('021', ''),
    'DisenoIndustrial': ('021', ''), 'DisenoInteractivo': ('021', ''), 'DisenoModas': ('021', ''),
    'Esp.LogisGestCadAbast': ('041', 'Alternativa: 104 Servicios de transporte'), 'EspGerMercadeo': ('041', ''),
    'EspGerTributaria': ('041', ''), 'EspGerenProyInteligenciaNegocios': ('041', ''), 'EspGestionEducativa': ('011', ''),
    'Ing.Telecomunicaciones': ('071', ''), 'IngIndustrial': ('071', 'Alternativa: 072 Industria y producción'),
    'IngSistemas': ('061', ''), 'IngSoftware': ('061', ''), 'LCS': ('011', ''), 'LicEduInfantil': ('011', ''),
    'LicEducacionBasicaPrimaria': ('011', ''), 'MCE': ('042', ''), 'MEDSTEM': ('011', ''), 'MGEM': ('041', ''),
    'MGerTalentoHumano': ('041', ''), 'MInnovacionEducativa': ('011', ''), 'Matemáticas': ('054', ''),
    'MercadeoyPublicidad': ('041', ''), 'NegIntl': ('041', ''), 'TecProfJudicial': ('042', ''),
    'TecnolDesarrolloSoftware': ('061', ''), 'TecnolGestAmbiental': ('052', ''), 'TecnolGuianzaTuris': ('101', ''),
    'TecnolLogistica': ('041', 'Alternativa: 104 Servicios de transporte'), 'TecnolMercadeoyPublicidad': ('041', ''),
}

# ------------------------------------------------------------------ 2. Diccionario ODS (borrador a validar)
ODS = {
    0: ('Sostenibilidad (transversal)', ['sostenibilidad', 'sostenible', 'desarrollo sostenible', 'ambiental', 'medio ambiente',
                                         'gestion ambiental', 'impacto ambiental', 'responsabilidad ambiental', 'ods', 'agenda 2030']),
    1: ('Fin de la pobreza', ['pobreza', 'vulnerabilidad', 'proteccion social', 'inclusion financiera', 'microfinanzas', 'microcredito']),
    2: ('Hambre cero', ['seguridad alimentaria', 'hambre', 'nutricion', 'agricultura sostenible', 'agroindustria', 'sistemas alimentarios']),
    3: ('Salud y bienestar', ['salud', 'bienestar', 'salud mental', 'seguridad y salud en el trabajo', 'enfermedad', 'prevencion', 'calidad de vida']),
    4: ('Educación de calidad', ['educacion', 'aprendizaje', 'pedagogia', 'pedagogico', 'didactica', 'docente', 'inclusion educativa', 'alfabetizacion', 'curriculo']),
    5: ('Igualdad de género', ['genero', 'equidad de genero', 'igualdad de genero', 'mujer', 'mujeres', 'violencia de genero', 'feminismo']),
    6: ('Agua limpia y saneamiento', ['agua', 'recurso hidrico', 'saneamiento', 'aguas residuales', 'cuencas', 'hidrologia']),
    7: ('Energía asequible y no contaminante', ['energia renovable', 'energias renovables', 'eficiencia energetica', 'energia solar', 'energia eolica', 'transicion energetica', 'energia limpia']),
    8: ('Trabajo decente y crecimiento económico', ['empleo', 'empleabilidad', 'trabajo decente', 'crecimiento economico', 'emprendimiento', 'productividad', 'derecho laboral', 'mercado laboral', 'formalizacion']),
    9: ('Industria, innovación e infraestructura', ['innovacion', 'infraestructura', 'industria', 'investigacion y desarrollo', 'tecnologia', 'transformacion digital', 'industrializacion']),
    10: ('Reducción de las desigualdades', ['desigualdad', 'desigualdades', 'inclusion', 'inclusion social', 'diversidad', 'discapacidad', 'migracion', 'equidad', 'derechos humanos']),
    11: ('Ciudades y comunidades sostenibles', ['ciudad', 'ciudades', 'urbano', 'movilidad', 'vivienda', 'patrimonio cultural', 'ordenamiento territorial', 'gestion del riesgo', 'territorio']),
    12: ('Producción y consumo responsables', ['consumo responsable', 'produccion sostenible', 'economia circular', 'residuos', 'reciclaje', 'cadena de suministro sostenible', 'compras sostenibles', 'huella']),
    13: ('Acción por el clima', ['cambio climatico', 'clima', 'carbono', 'emisiones', 'gases de efecto invernadero', 'adaptacion climatica', 'mitigacion', 'huella de carbono']),
    14: ('Vida submarina', ['oceano', 'oceanos', 'marino', 'marina', 'costero', 'pesca', 'ecosistemas marinos']),
    15: ('Vida de ecosistemas terrestres', ['biodiversidad', 'ecosistema', 'ecosistemas', 'bosques', 'deforestacion', 'conservacion', 'fauna', 'flora', 'suelo']),
    16: ('Paz, justicia e instituciones sólidas', ['paz', 'justicia', 'instituciones', 'transparencia', 'corrupcion', 'estado de derecho', 'conflicto', 'gobernanza', 'derechos', 'participacion ciudadana', 'ciudadania']),
    17: ('Alianzas para lograr los objetivos', ['alianzas', 'cooperacion internacional', 'cooperacion', 'alianzas estrategicas', 'responsabilidad social']),
}
AMBIENTALES = {0, 6, 7, 11, 12, 13, 14, 15}   # 0 = sostenibilidad transversal (no es un ODS)
PATRON = {o: [(t, re.compile(r'\b' + re.escape(norm(t)) + r'\b')) for t in ts] for o, (_, ts) in ODS.items()}


def asignar_ods(nombre, contenido):
    n, c = norm(nombre), norm(contenido)
    out = {}
    for o, pats in PATRON.items():
        en_nombre = [t for t, p in pats if p.search(n)]
        en_cont = sorted({t for t, p in pats if p.search(c)})
        if en_nombre or len(en_cont) >= 2:
            out[o] = sorted(set(en_nombre) | set(en_cont))
    return out


# ------------------------------------------------------------------ datos
nombres_prog, micro = {}, []
for f in sorted(glob.glob('data/raw/FORMATOS RA CICLO UNO RC/*.xlsx')):
    codigo = os.path.basename(f)[10:-5].rsplit('_', 1)[0]
    if codigo not in nombres_prog:
        wb = openpyxl.load_workbook(f, read_only=True, data_only=True)
        fila = list(wb[wb.sheetnames[0]].iter_rows(min_row=3, max_row=3, values_only=True))[0]
        nombres_prog[codigo] = str(fila[0]).strip() if fila and fila[0] else codigo
        wb.close()
    micro.append(ExcelExtractor(f).extract_estrategias_micro())
micro = pd.concat(micro, ignore_index=True)
asig = consolidar_asignaturas(micro)

filas = []
for _, r in asig.iterrows():
    esp, conf = CINE.get(r['Programa'], ('', 'Sin asignar'))
    ods = asignar_ods(r['asignatura'], r['texto'])
    filas.append({'Programa': nombres_prog.get(r['Programa'], r['Programa']), 'Código': r['Programa'], 'Sede': r['Codigo'],
                  'Asignatura': r['asignatura'], 'CINE-F amplio': f"{esp[:2]} {AMPLIO.get(esp[:2], '')}",
                  'CINE-F específico': f"{esp} {ESPECIFICO.get(esp, '')}",
                  'ODS asignados': ', '.join('Sostenibilidad' if o == 0 else f'ODS {o}' for o in sorted(ods)),
                  'Términos encontrados': ' | '.join(f"{'Sost.' if o == 0 else 'ODS ' + str(o)}: {', '.join(t)}" for o, t in sorted(ods.items())),
                  'Sostenibilidad ambiental': 'Sí' if set(ods) & AMBIENTALES else 'No',
                  'Sostenibilidad ampliada': 'Sí' if ods else 'No', '_ods': sorted(ods)})
d = pd.DataFrame(filas)

# ------------------------------------------------------------------ resúmenes
n = len(d)
por_ods = {o: int(d['_ods'].map(lambda x: o in x).sum()) for o in ODS}
EV = {'asignaturas': n, 'programas': d['Código'].nunique(),
      'cine_amplio': d['CINE-F amplio'].value_counts().to_dict(),
      'cine_especifico': d['CINE-F específico'].value_counts().to_dict(),
      'por_ods': {('Sostenibilidad transversal' if o == 0 else f'ODS {o} {ODS[o][0]}'): v for o, v in por_ods.items()},
      'sin_ods': int((d['Sostenibilidad ampliada'] == 'No').sum()),
      'greenmetric': {'ambiental': int((d['Sostenibilidad ambiental'] == 'Sí').sum()),
                      'ambiental_pct': round(100 * (d['Sostenibilidad ambiental'] == 'Sí').mean(), 1),
                      'ampliada': int((d['Sostenibilidad ampliada'] == 'Sí').sum()),
                      'ampliada_pct': round(100 * (d['Sostenibilidad ampliada'] == 'Sí').mean(), 1)}}
json.dump(EV, open('auditoria/evidencia_clasificacion_estandar.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

# ------------------------------------------------------------------ Excel
wb = openpyxl.Workbook()
cab_fill, cab_font = PatternFill('solid', fgColor=NAVY), Font(bold=True, color='FFFFFF')


def hoja(ws, columnas, datos, anchos):
    ws.append(columnas)
    for c in ws[1]:
        c.fill, c.font = cab_fill, cab_font
        c.alignment = Alignment(wrap_text=True, vertical='center')
    for x in datos:
        ws.append([x.get(k, '') if isinstance(x, dict) else x[i] for i, k in enumerate(columnas)])
    for i, a in enumerate(anchos, 1):
        ws.column_dimensions[get_column_letter(i)].width = a
    for fila in ws.iter_rows(min_row=2):
        for c in fila:
            c.alignment = Alignment(wrap_text=True, vertical='top')
    ws.freeze_panes = 'A2'
    ws.auto_filter.ref = ws.dimensions


ws = wb.active
ws.title = 'Propuesta'
hoja(ws, ['Nivel', 'Taxonomía', 'Unidad', 'Regla de asignación', 'Uso', 'Estado'], [
    ('1. Área de conocimiento', 'CINE-F 2013 (UNESCO): campo amplio y específico', 'Programa; la asignatura hereda',
     'Asignación del programa por su denominación (hoja CINE-F_programas)', 'Agrupación disciplinar comparable (SNIES, estadística internacional)',
     'Propuesta: 3 programas con alternativa a confirmar'),
    ('2. Contribución a los ODS', 'Objetivos de Desarrollo Sostenible (17)', 'Asignatura (núcleos + indicadores; sin electivas)',
     '≥ 1 término del ODS en el nombre o ≥ 2 términos distintos en el contenido; palabra completa, sin tildes',
     'Base para GreenMetric y reportes de sostenibilidad', 'Diccionario borrador a validar (hoja Diccionario_ODS)'),
    ('3. Indicador GreenMetric', 'Asignatura relacionada con sostenibilidad', 'Asignatura',
     'Ambiental: ≥ 1 ODS ambiental (6, 7, 11–15) o categoría transversal Sostenibilidad. Ampliada: ≥ 1 ODS o Sostenibilidad.',
     'Cociente de asignaturas de sostenibilidad sobre el total', 'Verificar la definición vigente de GreenMetric antes de reportar'),
    ('—', 'LDA de consenso (k = 13)', 'Asignatura', 'Modelo probabilístico (semillas)', 'Solo exploratorio', 'Decisión de la autora'),
], [22, 34, 26, 55, 40, 36])
hoja(wb.create_sheet('CINE-F_programas'), ['Código', 'Programa', 'Campo amplio', 'Campo específico', 'A confirmar'],
     [(c, nombres_prog.get(c, c), f'{e[:2]} {AMPLIO[e[:2]]}', f'{e} {ESPECIFICO[e]}', conf) for c, (e, conf) in sorted(CINE.items())],
     [30, 60, 45, 38, 40])
hoja(wb.create_sheet('Diccionario_ODS'), ['ODS', 'Nombre', 'Ambiental', 'Términos'],
     [(o, n_, 'Sí' if o in AMBIENTALES else 'No', ', '.join(ts)) for o, (n_, ts) in ODS.items()], [6, 40, 10, 110])
COLS = ['Programa', 'Código', 'Sede', 'Asignatura', 'CINE-F amplio', 'CINE-F específico', 'ODS asignados', 'Términos encontrados',
        'Sostenibilidad ambiental', 'Sostenibilidad ampliada', 'Validación ODS (experto)', 'Observación']
hoja(wb.create_sheet('Asignaturas'), COLS, d.to_dict('records'), [40, 22, 7, 40, 40, 34, 22, 60, 12, 12, 18, 30])

ws = wb.create_sheet('Resumen')
ws.append(['Indicador', 'Asignaturas', '% de ' + str(n)])
for k, v in [('Sostenibilidad ambiental (Sostenibilidad + ODS 6, 7, 11–15)', EV['greenmetric']['ambiental']),
             ('Sostenibilidad ampliada (≥ 1 ODS o Sostenibilidad)', EV['greenmetric']['ampliada']), ('Sin ODS asignado', EV['sin_ods'])]:
    ws.append([k, v, round(100 * v / n, 1)])
ws.append([])
ws.append(['ODS', 'Asignaturas', '%'])
for o, v in por_ods.items():
    ws.append([('Sostenibilidad (transversal)' if o == 0 else f'ODS {o} {ODS[o][0]}'), v, round(100 * v / n, 1)])
ws.append([])
ws.append(['CINE-F campo específico', 'Asignaturas', '%'])
for k, v in d['CINE-F específico'].value_counts().items():
    ws.append([k, int(v), round(100 * v / n, 1)])
ws.append([])
ws.append(['Programa', 'Asignaturas', 'Sostenibilidad ambiental', '%', 'Sostenibilidad ampliada', '%'])
g = d.groupby('Programa')
for p_, x in g:
    a_ = int((x['Sostenibilidad ambiental'] == 'Sí').sum())
    b_ = int((x['Sostenibilidad ampliada'] == 'Sí').sum())
    ws.append([p_, len(x), a_, round(100 * a_ / len(x), 1), b_, round(100 * b_ / len(x), 1)])
for fila in ws.iter_rows():
    if fila[0].value in ('Indicador', 'ODS', 'CINE-F campo específico', 'Programa'):
        for c in fila:
            if c.value is not None:
                c.fill, c.font = cab_fill, cab_font
for i, a in enumerate([55, 12, 22, 10, 22, 10], 1):
    ws.column_dimensions[get_column_letter(i)].width = a
wb.save('auditoria/Clasificacion_estandar_oferta.xlsx')
print(json.dumps(EV, ensure_ascii=False, indent=1))
