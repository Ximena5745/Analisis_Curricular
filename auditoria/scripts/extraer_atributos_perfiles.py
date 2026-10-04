"""
Atributos de los perfiles profesional y ocupacional de todas las matrices (src/atributos_perfil.py).

Uso: python auditoria/scripts/extraer_atributos_perfiles.py
Salida: auditoria/Atributos_perfiles.xlsx (hojas Resumen, Atributos, Textos, Reglas)
"""
import glob
import os
import sys

import openpyxl
import pandas as pd

sys.path.insert(0, '.')
sys.stdout.reconfigure(encoding='utf-8')
from src.atributos_perfil import extraer_atributos, forma_breve, lexico_de_matriz  # noqa: E402

attrs, textos = [], []
for f in sorted(glob.glob('data/raw/FORMATOS RA CICLO UNO RC/*.xlsx')):
    matriz = os.path.basename(f)[10:-5]
    programa, sede = matriz.rsplit('_', 1)
    wb = openpyxl.load_workbook(f, read_only=True, data_only=True)
    lex = lexico_de_matriz(wb)
    fila = list(wb['Paso1 Analisis perfil egreso'].iter_rows(min_row=3, max_row=3, values_only=True))[0]
    wb.close()
    for perfil, texto in (('Perfil profesional', fila[2]), ('Perfil ocupacional', fila[3])):
        a = extraer_atributos(texto or '', lex)
        palabras = len(str(texto or '').split())
        cubiertas = len({w for x in a for w in x[2].lower().split()} & set(str(texto or '').lower().split()))
        textos.append({'Matriz': matriz, 'Programa': programa, 'Sede': sede, 'Perfil': perfil, 'Texto': texto,
                       'Palabras': palabras, 'Atributos': len(a),
                       'Cobertura léxica': round(cubiertas / len(set(str(texto or '').lower().split())), 2) if palabras else 0,
                       'Revisar': 'Sí' if len(a) < 4 else ''})
        attrs += [{'Matriz': matriz, 'Programa': programa, 'Sede': sede, 'Perfil': perfil, 'N.º': i + 1, 'Tipo': t,
                   'Verbo': v, 'Forma breve': forma_breve(t, v, x, 'tercera' if perfil == 'Perfil profesional' else 'infinitivo'), 'Atributo': x, 'Validación (experto)': '', 'Corrección': ''}
                  for i, (t, v, x) in enumerate(a)]

A, T = pd.DataFrame(attrs), pd.DataFrame(textos)
res = (A.groupby(['Perfil', 'Tipo']).size().unstack(fill_value=0)
       .assign(Total=lambda x: x.sum(axis=1)).reset_index())
with pd.ExcelWriter('auditoria/Atributos_perfiles.xlsx') as xw:
    res.to_excel(xw, sheet_name='Resumen', index=False)
    A.to_excel(xw, sheet_name='Atributos', index=False)
    T.to_excel(xw, sheet_name='Textos', index=False)
    pd.DataFrame({'Tipo': ['Acción', 'Conocimiento', 'Función', 'Rol', 'Rasgo', 'Finalidad', 'Normativo', 'Forma breve'],
                  'Regla': ['Verbo que inicia predicado (léxico de verbos de la matriz, infinitivo o gerundio tras conector, '
                            'o primer verbo conjugado de la oración) + objeto; los verbos coordinados comparten objeto.',
                            'Ítem de una enumeración tras «posee / cuenta con conocimientos, saberes, formación o bases en…».',
                            'Ítem tras «habilidades / competencias para…», «en funciones, campos, áreas o cargos de…», '
                            '«actividades … como…», «abarca / comprende / incluye…», o viñeta sin verbo.',
                            'Ítem tras «desempeñarse / vincularse / actuar como…», «cargos tales como…», o viñeta bajo «como:».',
                            'Ítem tras «se caracteriza / distingue / destaca por…», dividido en «y»; o «con responsabilidad / ética / compromiso…» dentro de una acción.',
                            'Infinitivo tras «con el propósito / fin / objetivo de» o «a fin de» (uno por infinitivo coordinado).',
                            '«según / conforme a / de acuerdo con … marco legal, normativa, ley…» → actuar conforme a ….',
                            'Verbo (3.ª persona en el perfil profesional, infinitivo en el ocupacional) + núcleo del objeto, sin artículo inicial ni complementos de contexto; no corta enumeraciones ni deja objetos de una palabra.']}
                 ).to_excel(xw, sheet_name='Reglas', index=False)
print(res.to_string(index=False))
print('Perfiles a revisar (< 4 atributos):', int((T['Revisar'] == 'Sí').sum()), 'de', len(T))
