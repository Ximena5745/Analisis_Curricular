"""
Tendencias del sector empresarial y educativo: fuente única de la lista y de la regla de asignación.

La lista oficial está en config_tendencias.json (15 tendencias; auditoría D21). Una tendencia está
presente en una asignatura si algún término aparece en su NOMBRE, o si su CONTENIDO suma al menos
`contenido_min_puntos` (término de varias palabras = 2 puntos; de una palabra = 1). La coincidencia es
por palabra completa y sin tildes, para evitar falsos positivos como «ia» dentro de «sociales».
"""

import json
import re
import unicodedata
from functools import lru_cache
from pathlib import Path
from typing import Dict, List, Tuple

RUTA_CONFIG = Path(__file__).resolve().parent.parent / 'config_tendencias.json'
REGLA_DEFECTO = {'nombre_min_terminos': 1, 'contenido_min_puntos': 2,
                 'peso_termino_compuesto': 2, 'peso_termino_simple': 1}


def normalizar(texto) -> str:
    t = unicodedata.normalize('NFKD', str(texto)).encode('ascii', 'ignore').decode('ascii').lower()
    return re.sub(r'\s+', ' ', re.sub(r'[^a-z0-9. ]', ' ', t)).strip()


def cargar_config(ruta: Path = RUTA_CONFIG) -> Tuple[Dict, Dict]:
    """Devuelve (tendencias, regla) desde config_tendencias.json."""
    data = json.loads(Path(ruta).read_text(encoding='utf-8'))
    return data['TENDENCIAS_GLOBALES'], {**REGLA_DEFECTO, **data.get('REGLA', {})}


@lru_cache(maxsize=4096)
def _patron(termino: str):
    return re.compile(r'(?<![a-z0-9])' + re.escape(normalizar(termino)) + r'(?![a-z0-9])')


def terminos_presentes(nombre: str, contenido: str, keywords: List[str], regla: Dict = None) -> List[str]:
    """Términos que activan la tendencia, o [] si no se cumple la regla."""
    regla = {**REGLA_DEFECTO, **(regla or {})}
    n, c = normalizar(nombre), normalizar(contenido)
    en_nombre = [k for k in keywords if _patron(k).search(n)]
    en_cont = [k for k in keywords if _patron(k).search(c)]
    puntos = sum(regla['peso_termino_compuesto'] if ' ' in k.strip() else regla['peso_termino_simple'] for k in en_cont)
    if len(en_nombre) >= regla['nombre_min_terminos'] or puntos >= regla['contenido_min_puntos']:
        return sorted(set(en_nombre) | set(en_cont))
    return []


def tendencia_presente(nombre: str, contenido: str, keywords: List[str], regla: Dict = None) -> bool:
    return bool(terminos_presentes(nombre, contenido, keywords, regla))
