import ast
try:
    src = open('dashboard_tematico.py', encoding='utf-8').read()
    ast.parse(src)
    print('OK - sin errores de sintaxis')
except SyntaxError as e:
    print(f'Error linea {e.lineno}: {e.msg}')
    lines = src.splitlines()
    for i in range(max(0, e.lineno-4), min(len(lines), e.lineno+3)):
        print(f'{i+1}: {lines[i]!r}')
