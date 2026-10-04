"""
Validación de la tabla de asociación perfil–contenido entregada por otra IA (AdmonEmpresas_PBOG).

Cada fila (atributo × capa × entidad) se clasifica contra la matriz cruda:
  V  válida: la entidad desarrolla el concepto del atributo de forma explícita o parcial
  G  genérica: competencia genérica institucional (C5) o RA genérico (su «RA2»)
  T  temática o sin respaldo: la entidad es del mismo campo, pero no menciona el concepto
Criterios de cálculo:
  A  tal como la entrega la otra IA (toda fila cuenta)
  B  sin entidades genéricas
  C  solo filas V (sin genéricas ni temáticas)
Nota: la otra IA numera los RA distinto de la matriz e incluye el RA genérico como RA2
(su RA3→RA2 real, RA4→RA3, RA5→RA4, RA6→RA5, RA7→RA6).

Uso: python auditoria/scripts/validar_asociacion_otra_ia.py
Salida: auditoria/Validacion_asociacion_otra_IA.xlsx
"""
import sys

import pandas as pd

sys.stdout.reconfigure(encoding='utf-8')

# (ID_atributo, Capa) -> {entidad: veredicto}; entidades con la numeración de la otra IA
V = {
    ('PP1', 'Competencia'): {'C2': 'V'},
    ('PP1', 'RA'): {'RA1': 'V', 'RA5': 'V'},
    ('PP1', 'Asignatura'): {'Análisis Estratégico': 'V', 'Gestión Estratégica': 'V', 'Prospectiva Estratégica': 'V',
                            'Tendencias Estratégicas': 'T', 'Consultorio Empresarial': 'V'},
    ('PP2', 'Competencia'): {'C2': 'V'},
    ('PP2', 'RA'): {'RA1': 'V', 'RA3': 'V', 'RA4': 'V', 'RA5': 'T'},
    ('PP2', 'Asignatura'): {'Proceso Administrativo': 'V', 'Teoría de las Organizaciones': 'V', 'Gestión del Talento Humano': 'V',
                            'Gerencia Financiera': 'V', 'Gerencia de Producción': 'V', 'Sistemas Integrados de Gestión (HSEQ)': 'V'},
    ('PP3', 'Competencia'): {'C1': 'T', 'C2': 'T', 'C5': 'G'},
    ('PP3', 'RA'): {'RA1': 'T', 'RA2': 'G', 'RA5': 'T'},
    ('PP3', 'Asignatura'): {'Razonamiento Cuantitativo': 'V', 'Análisis y Visualización de Datos': 'V', 'Análisis Descriptivo de Datos': 'V',
                            'Estadística Predictiva': 'V', 'Taller Financiero Aplicado a BI': 'V', 'Administración 4.0': 'V'},
    ('PP4', 'Competencia'): {'C1': 'V', 'C3': 'T'},
    ('PP4', 'RA'): {'RA1': 'T', 'RA3': 'V', 'RA4': 'V'},
    ('PP4', 'Asignatura'): {'Microeconomía': 'T', 'Macroeconomía': 'T', 'Costos y Presupuestos': 'V', 'Matemáticas Financieras': 'T',
                            'Gerencia Financiera': 'T', 'Evaluación de Proyectos': 'V', 'Riesgo Operativo y LA/FT': 'T'},
    ('PP5', 'Competencia'): {'C2': 'T', 'C3': 'V'},
    ('PP5', 'RA'): {'RA3': 'V', 'RA5': 'T', 'RA6': 'T'},
    ('PP5', 'Asignatura'): {'Gerencia Estratégica de Proyectos en Cascada': 'V', 'Gerencia Estratégica de Proyectos Ágiles': 'V',
                            'Consultorio Empresarial': 'T', 'Prácticas': 'T', 'Liderazgo y Pensamiento Estratégico': 'V'},
    ('PP6', 'Competencia'): {'C4': 'V', 'C5': 'G'},
    ('PP6', 'RA'): {'RA2': 'G', 'RA4': 'V', 'RA5': 'T', 'RA7': 'V'},
    ('PP6', 'Asignatura'): {'Desarrollo Sostenible': 'V', 'Gerencia de Desarrollo Sostenible': 'V', 'Oportunidades para Emprender': 'V',
                            'Comercio Internacional': 'T', 'Gerencia de Producción': 'T'},
    ('PP7', 'Competencia'): {'C2': 'V', 'C4': 'T'},
    ('PP7', 'RA'): {'RA4': 'V', 'RA5': 'T', 'RA7': 'T'},
    ('PP7', 'Asignatura'): {'Gerencia Financiera': 'V', 'Gestión Estratégica': 'T', 'Gerencia de Desarrollo Sostenible': 'V',
                            'Consultorio Empresarial': 'T', 'Prácticas': 'T'},
    ('PP8', 'Competencia'): {'C1': 'T', 'C5': 'G'},
    ('PP8', 'RA'): {'RA1': 'T', 'RA2': 'G', 'RA4': 'T'},
    ('PP8', 'Asignatura'): {'Pensamiento Crítico y Ciudadanías Activas': 'V', 'Cultura, Política y Sociedad': 'T',
                            'Análisis Estratégico': 'T', 'Tendencias Estratégicas': 'T', 'Administración 4.0': 'T'},
    ('PP9', 'Competencia'): {'C1': 'V', 'C5': 'G'},
    ('PP9', 'RA'): {'RA1': 'V', 'RA2': 'G', 'RA4': 'V'},
    ('PP9', 'Asignatura'): {'Derecho Comercial y Laboral': 'V', 'Gobierno Corporativo y Compilance': 'V',
                            'Sistemas Integrados de Gestión (HSEQ)': 'V', 'Riesgo Operativo y LA/FT': 'V', 'Comercio Internacional': 'T'},
    ('PO1', 'Competencia'): {'C2': 'V'},
    ('PO1', 'RA'): {'RA1': 'V', 'RA5': 'V'},
    ('PO1', 'Asignatura'): {'Análisis Estratégico': 'V', 'Gestión Estratégica': 'V', 'Prospectiva Estratégica': 'V',
                            'Tendencias Estratégicas': 'T', 'Consultorio Empresarial': 'V'},
    ('PO2', 'Competencia'): {'C2': 'V'},
    ('PO2', 'RA'): {'RA1': 'T', 'RA3': 'V', 'RA4': 'T', 'RA5': 'T'},
    ('PO2', 'Asignatura'): {'Proceso Administrativo': 'V', 'Gestión del Talento Humano': 'V', 'Fundamentos de Mercadeo': 'V',
                            'Gerencia Financiera': 'V', 'Gerencia de Producción': 'V', 'Gerencia de Desarrollo Sostenible': 'T'},
    ('PO3', 'Competencia'): {'C3': 'V'},
    ('PO3', 'RA'): {'RA3': 'V', 'RA6': 'V'},
    ('PO3', 'Asignatura'): {'Gestión del Talento Humano': 'V', 'Liderazgo y Pensamiento Estratégico': 'V', 'Proceso Administrativo': 'V',
                            'Consultorio Empresarial': 'T', 'Prácticas': 'T'},
    ('PO4', 'Competencia'): {'C2': 'V'},
    ('PO4', 'RA'): {'RA1': 'V', 'RA5': 'V'},
    ('PO4', 'Asignatura'): {'Análisis Estratégico': 'V', 'Gestión Estratégica': 'V', 'Prospectiva Estratégica': 'V', 'Consultorio Empresarial': 'V'},
    ('PO5', 'Competencia'): {'C2': 'T', 'C3': 'T'},
    ('PO5', 'RA'): {'RA3': 'T', 'RA5': 'T'},
    ('PO5', 'Asignatura'): {'Gestión Estratégica': 'V', 'Gerencia de Producción': 'T', 'Gerencia Estratégica de Proyectos en Cascada': 'T',
                            'Gerencia Estratégica de Proyectos Ágiles': 'T'},
    ('PO6', 'Competencia'): {'C2': 'T', 'C3': 'T'},
    ('PO6', 'RA'): {'RA3': 'V', 'RA4': 'T'},
    ('PO6', 'Asignatura'): {'Proceso Administrativo': 'V', 'Gerencia de Producción': 'V', 'Sistemas Integrados de Gestión (HSEQ)': 'V', 'Prácticas': 'T'},
    ('PO7', 'Competencia'): {'C1': 'T', 'C2': 'T'},
    ('PO7', 'RA'): {'RA1': 'T', 'RA3': 'T', 'RA4': 'T'},
    ('PO7', 'Asignatura'): {'Sistemas Integrados de Gestión (HSEQ)': 'V', 'Gestión Estratégica': 'V', 'Riesgo Operativo y LA/FT': 'V',
                            'Gobierno Corporativo y Compilance': 'T', 'Administración 4.0': 'T'},
    ('PO8', 'Competencia'): {'C4': 'V'},
    ('PO8', 'RA'): {'RA2': 'G', 'RA5': 'V', 'RA7': 'V'},
    ('PO8', 'Asignatura'): {'Oportunidades para Emprender': 'V', 'Fundamentos de Mercadeo': 'V', 'Tendencias Estratégicas': 'V',
                            'Prospectiva Estratégica': 'T', 'Comercio Internacional': 'T'},
    ('PO9', 'Competencia'): {'C4': 'V'},
    ('PO9', 'RA'): {'RA5': 'V', 'RA7': 'V'},
    ('PO9', 'Asignatura'): {'Oportunidades para Emprender': 'V', 'Evaluación de Proyectos': 'V', 'Gerencia Financiera': 'T',
                            'Consultorio Empresarial': 'T', 'Prácticas': 'V'},
    ('PO10', 'Competencia'): {'C2': 'V', 'C4': 'T'},
    ('PO10', 'RA'): {'RA4': 'V', 'RA5': 'T', 'RA7': 'T'},
    ('PO10', 'Asignatura'): {'Gerencia Financiera': 'V', 'Gerencia de Desarrollo Sostenible': 'V', 'Evaluación de Proyectos': 'T',
                             'Consultorio Empresarial': 'T', 'Comercio Internacional': 'T'},
}
CAPAS = ('Competencia', 'RA', 'Asignatura')
filas = [{'ID_atributo': a, 'Perfil': 'Profesional' if a.startswith('PP') else 'Ocupacional', 'Capa': c, 'ID_entidad': e, 'Veredicto': v}
         for (a, c), ents in V.items() for e, v in ents.items()]
d = pd.DataFrame(filas)
print('Filas:', len(d), '|', d['Veredicto'].value_counts().to_dict())

asoc = []
for (a, c), ents in V.items():
    vs = list(ents.values())
    asoc.append({'ID_atributo': a, 'Perfil': 'Profesional' if a.startswith('PP') else 'Ocupacional', 'Capa': c,
                 'A': bool(vs), 'B': any(v != 'G' for v in vs), 'C': any(v == 'V' for v in vs)})
s = pd.DataFrame(asoc)
res = []
for perfil, g in list(s.groupby('Perfil')) + [('Resultado general', s)]:
    for crit, nombre in (('A', 'A. Otra IA tal cual'), ('B', 'B. Sin genérica'), ('C', 'C. Sin genérica ni temática')):
        r = {'Perfil': perfil, 'Criterio': nombre}
        for c in CAPAS:
            r[f'% {c}'] = round(100 * g.loc[g.Capa == c, crit].mean(), 1)
        tres = g.pivot(index='ID_atributo', columns='Capa', values=crit).all(axis=1)
        r['% en las tres capas'] = round(100 * tres.mean(), 1)
        r['Atributos'] = int(tres.size)
        res.append(r)
res = pd.DataFrame(res)
print(res.to_string(index=False))
sin = s[~s['C']][['ID_atributo', 'Capa']]
print('\nAtributo × capa sin respaldo válido (criterio C):')
print(sin.groupby('ID_atributo')['Capa'].apply(', '.join).to_string())
with pd.ExcelWriter('auditoria/Validacion_asociacion_otra_IA.xlsx') as xw:
    res.to_excel(xw, sheet_name='Resumen', index=False)
    d.to_excel(xw, sheet_name='Filas_veredicto', index=False)
    s.to_excel(xw, sheet_name='Atributo_capa', index=False)
    pd.DataFrame({'Veredicto': ['V', 'G', 'T'],
                  'Definición': ['La entidad desarrolla el concepto del atributo de forma explícita o parcial.',
                                 'Competencia genérica institucional (C5) o RA genérico: regla común a 40 matrices, no diseño del programa.',
                                 'Relación temática o inexistente: la entidad es del campo, pero no menciona el concepto del atributo.']}
                 ).to_excel(xw, sheet_name='Definiciones', index=False)
