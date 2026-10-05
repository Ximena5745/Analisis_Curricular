"""
Módulo de análisis de indicadores curriculares.

Calcula indicadores de calidad curricular:
- Balance de tipos de saber
- Complejidad cognitiva
- Cobertura de competencias
- Diversidad metodológica
- Completitud de datos
- Score general de calidad
"""

import logging
import unicodedata
from typing import Dict
import pandas as pd
import numpy as np
from collections import Counter

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from config import (
    TAXONOMIA_BLOOM,
    TIPOS_SABER,
    COMPLEJIDAD_THRESHOLDS,
    QUALITY_WEIGHTS,
    PROGRESIONES_TAXONOMICAS,
    COLUMNAS_COMPLETITUD,
)
import re
from difflib import SequenceMatcher


def _clave_texto(texto) -> str:
    """Minúsculas, sin tildes, espacios comprimidos y sin puntuación final."""
    t = unicodedata.normalize('NFKD', str(texto)).encode('ascii', 'ignore').decode().lower()
    return re.sub(r'[\s\.;,:]+$', '', re.sub(r'\s+', ' ', t).strip())


def _clave_letras(texto) -> str:
    return re.sub(r'[^a-z]', '', _clave_texto(texto))

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class CurricularAnalyzer:
    """
    Analiza indicadores de calidad curricular.

    Procesa datos de un programa académico y calcula métricas cuantitativas
    y cualitativas sobre el diseño curricular.

    Attributes:
        programa_data (Dict): Datos extraídos del programa
        programa_nombre (str): Nombre del programa
        competencias (pd.DataFrame): DataFrame de competencias
        ra (pd.DataFrame): DataFrame de resultados de aprendizaje

    Example:
        >>> analyzer = CurricularAnalyzer(programa_data)
        >>> balance = analyzer.calcular_balance_tipo_saber()
        >>> print(balance)
        {'Saber': 38.5, 'SaberHacer': 30.8, 'SaberSer': 30.8}
    """

    def __init__(self, programa_data: Dict):
        """
        Inicializa el analizador con datos del programa.

        Args:
            programa_data (Dict): Salida de ExcelExtractor.extract_all()
        """
        self.programa_data = programa_data
        self.programa_nombre = programa_data['metadata']['programa']
        self.competencias = programa_data['competencias']
        self.ra = programa_data['resultados_aprendizaje']
        self.estrategias_meso = programa_data.get('estrategias_meso', pd.DataFrame())
        self.estrategias_micro = programa_data.get('estrategias_micro', pd.DataFrame())

        logger.info(f"Analizador inicializado para: {self.programa_nombre}")

    def _ra_unicos(self) -> pd.DataFrame:
        """RA únicos de la matriz (decisión D4, ajustada en D23): una fila por redacción
        distinta de 'Resultados Aprendizaje' sin mayúsculas, tildes ni puntuación, conservando la primera."""
        if self.ra.empty or 'Resultados Aprendizaje' not in self.ra.columns:
            return self.ra
        ra = self.ra[self.ra['Resultados Aprendizaje'].notna()].copy()
        ra['_clave_ra'] = ra['Resultados Aprendizaje'].map(
            lambda t: re.sub(r'\s+', ' ', re.sub(r'[^a-z0-9 ]', ' ', _clave_texto(t))).strip())
        return ra.drop_duplicates('_clave_ra').drop(columns='_clave_ra')

    def calcular_balance_tipo_saber(self) -> Dict[str, float]:
        """
        Calcula la distribución de tipos de saber (Saber, SaberHacer, SaberSer).

        Returns:
            Dict con estructura:
            {
                'Saber': 38.5,
                'SaberHacer': 30.8,
                'SaberSer': 30.8,
                'desviacion_estandar': 4.5,
                'balanceado': True  # Si desviación < 10%
            }

        Example:
            >>> balance = analyzer.calcular_balance_tipo_saber()
            >>> print(f"Saber: {balance['Saber']:.1f}%")
        """
        if self.ra.empty or 'TipoSaber' not in self.ra.columns:
            logger.warning("No hay datos de TipoSaber para analizar")
            result = {tipo: 0.0 for tipo in TIPOS_SABER}
            result['desviacion_estandar'] = 0.0
            result['balanceado'] = True
            return result

        # Contar por tipo sobre RA únicos (D4; auditoría E3-4)
        ra = self._ra_unicos()
        tipo_counts = ra['TipoSaber'].map(
            lambda t: {'saber': 'Saber', 'saberhacer': 'SaberHacer', 'saberser': 'SaberSer'}.get(_clave_letras(t), t)
        ).value_counts()
        total = len(ra)

        # Calcular porcentajes
        balance = {}
        for tipo in TIPOS_SABER:
            count = tipo_counts.get(tipo, 0)
            porcentaje = (count / total * 100) if total > 0 else 0
            balance[tipo] = round(porcentaje, 1)

        # Calcular desviación estándar
        valores = list(balance.values())
        desviacion = np.std(valores) if valores else 0

        # Determinar si está balanceado (desviación < 10%)
        balanceado = desviacion < 10.0

        balance['desviacion_estandar'] = round(desviacion, 1)
        balance['balanceado'] = balanceado

        logger.info(f"Balance tipo saber: {balance}")
        return balance

    def _get_nivel_taxonomico(self, verbo: str, nivel_dominio: str,
                              taxonomia: str = None, dominio: str = None) -> float:
        """
        Determina el nivel de exigencia (escala común 1-6) de un RA.

        ADR-04: Nivel Dominio es la fuente primaria. El nivel declarado se
        ubica en la progresión de su taxonomía y dominio
        (config.PROGRESIONES_TAXONOMICAS) y se traduce a 1-6 según su
        posición: 1 + (posición - 1) × 5 / (n.º de niveles - 1). Si el nivel no
        se reconoce, se usa el verbo en la taxonomía de Bloom (auditoría E3-2).

        Args:
            verbo (str): Verbo del RA
            nivel_dominio (str): Nivel de dominio declarado (p. ej. 'AnálisisBAK')
            taxonomia (str): 'Bloom' o 'BAK'
            dominio (str): Dominio asociado (p. ej. 'ProcedimentalBAK')

        Returns:
            float: Nivel en la escala 1-6
        """
        # 1. Nivel declarado, según la progresión de su taxonomía y dominio
        if not pd.isna(nivel_dominio):
            tax = 'bak' if 'bak' in _clave_letras(taxonomia or nivel_dominio) else 'bloom'
            dom = next((d for d in ('cognitivo', 'procedimental', 'actitudinal')
                        if d in _clave_letras(dominio or '')), 'cognitivo')
            progresion = PROGRESIONES_TAXONOMICAS[(tax, None if tax == 'bloom' else dom)]
            base = re.sub(r'(bak|b)$', '', _clave_letras(nivel_dominio))
            if base.startswith('conocimiento'):
                base = 'conocimiento'
            if base in progresion:
                posicion = progresion.index(base) + 1
                return round(1 + (posicion - 1) * 5 / (len(progresion) - 1), 2)

        # 2. Fallback: buscar en taxonomía de Bloom
        if not pd.isna(verbo):
            verbo_lower = str(verbo).lower().strip()
            for nivel_nombre, config in TAXONOMIA_BLOOM.items():
                verbos_nivel = [v.lower() for v in config['verbos']]
                if verbo_lower in verbos_nivel:
                    return config['nivel']

        # Nivel por defecto
        return 2

    def _contar_asignaturas_unicas(self) -> int:
        """
        Cuenta asignaturas únicas del programa desde Paso 5 (Estrategias Micro).

        Lógica correcta:
        1. Leer columna "Nombre asignatura o módulo" de Paso 5
        2. Filtrar valores no nulos
        3. Excluir filas de totales (valores numéricos)
        4. Normalizar nombres (acentos, espacios)
        5. Contar únicos

        Returns:
            int: Número de asignaturas únicas
        """
        if self.estrategias_micro.empty:
            logger.warning("Paso 5 (estrategias_micro) está vacío. Retornando 0.")
            return 0

        # Función auxiliar para normalizar nombres de columnas
        def _normalize_column_name(name):
            """Normaliza nombres de columnas removiendo acentos y espacios."""
            if pd.isna(name):
                return ''
            normalized = unicodedata.normalize('NFKD', str(name))
            normalized = ''.join(c for c in normalized if not unicodedata.combining(c))
            return normalized.lower().replace(' ', '').replace('_', '').replace('-', '')

        # Buscar columna de asignaturas en Paso 5
        nombre_asig_col = None
        for col in self.estrategias_micro.columns:
            col_norm = _normalize_column_name(col)
            if 'nombreasignaturaomodulo' in col_norm:
                nombre_asig_col = col
                break

        if nombre_asig_col is None:
            logger.warning(f"Columna 'Nombre asignatura o módulo' no encontrada en Paso 5. "
                           f"Columnas disponibles: {self.estrategias_micro.columns.tolist()}")
            return 0

        # Obtener valores no nulos
        all_vals = self.estrategias_micro[nombre_asig_col].dropna()

        if len(all_vals) == 0:
            logger.warning("No hay valores en columna de asignaturas")
            return 0

        # Clasificar: asignaturas vs filas de totales (valores numéricos)
        asignaturas = []
        for v in all_vals:
            v_str = str(v).strip()
            # Excluir valores que son solo números (filas de totales)
            try:
                float(v_str)
                # Es un número, se excluye
                continue
            except ValueError:
                # No es número, es asignatura válida
                asignaturas.append(v)

        if len(asignaturas) == 0:
            logger.warning("No hay asignaturas válidas después de filtrar totales")
            return 0

        # Normalizar nombres (aplicar misma lógica que test_generar_excel.py)
        def _normalize_value(value):
            """Normaliza nombres de asignaturas para comparación."""
            normalized = unicodedata.normalize('NFKD', str(value))
            normalized = ''.join(c for c in normalized if not unicodedata.combining(c))
            normalized = normalized.lower()
            normalized = ''.join(c for c in normalized if c.isalnum())
            return normalized

        asigs_normalizadas = pd.Series(asignaturas).apply(_normalize_value)
        asignaturas_unicas = asigs_normalizadas.nunique()

        logger.info(f"Conteo de asignaturas: total={len(all_vals)}, "
                   f"limpios={len(asignaturas)}, unicos={asignaturas_unicas}")

        return int(asignaturas_unicas)

    def calcular_complejidad_cognitiva(self) -> Dict[str, float]:
        """
        Calcula la distribución de niveles de complejidad cognitiva según Bloom.

        Returns:
            Dict con estructura:
            {
                'Básico': 7.7,       # Recordar, Comprender
                'Intermedio': 30.8,  # Aplicar, Analizar
                'Avanzado': 61.5,    # Evaluar, Crear
                'nivel_promedio': 4.5,
                'indice_complejidad': 75.0  # Score 0-100
            }

        Example:
            >>> complejidad = analyzer.calcular_complejidad_cognitiva()
            >>> print(f"Nivel avanzado: {complejidad['Avanzado']:.1f}%")
        """
        if self.ra.empty:
            return {
                'Básico': 0.0,
                'Intermedio': 0.0,
                'Avanzado': 0.0,
                'nivel_promedio': 0.0,
                'indice_complejidad': 0.0
            }

        # Obtener niveles (escala común 1-6) de los RA únicos (D4)
        niveles = []
        for _, row in self._ra_unicos().iterrows():
            nivel = self._get_nivel_taxonomico(row.get('Verbo RA', ''), row.get('Nivel Dominio', ''),
                                               row.get('Taxonomía'), row.get('Dominio Asociado'))
            niveles.append(nivel)

        total = len(niveles)

        # Clasificar por complejidad. Con niveles reescalados (p. ej. 2,25 o
        # 4,33) se usan los cortes continuos equivalentes a las bandas enteras
        # 1-2 / 3-4 / 5-6: básico < 2,5 ≤ intermedio < 4,5 ≤ avanzado.
        corte_bajo = (COMPLEJIDAD_THRESHOLDS['BASICO'][1] + COMPLEJIDAD_THRESHOLDS['INTERMEDIO'][0]) / 2
        corte_alto = (COMPLEJIDAD_THRESHOLDS['INTERMEDIO'][1] + COMPLEJIDAD_THRESHOLDS['AVANZADO'][0]) / 2
        basico = sum(1 for n in niveles if n < corte_bajo)
        intermedio = sum(1 for n in niveles if corte_bajo <= n < corte_alto)
        avanzado = sum(1 for n in niveles if n >= corte_alto)

        # Calcular porcentajes
        promedio = float(np.mean(niveles)) if niveles else 0
        resultado = {
            'Básico': round((basico / total * 100), 1) if total > 0 else 0,
            'Intermedio': round((intermedio / total * 100), 1) if total > 0 else 0,
            'Avanzado': round((avanzado / total * 100), 1) if total > 0 else 0,
            'nivel_promedio': round(promedio, 1)
        }

        # Calcular índice de complejidad (0-100)
        # Fórmula: (promedio - 1) / 5 * 100
        indice = ((promedio - 1) / 5 * 100) if promedio > 0 else 0
        resultado['indice_complejidad'] = round(indice, 1)

        logger.info(f"Complejidad cognitiva: {resultado}")
        return resultado

    def calcular_cobertura_competencias(self) -> Dict[str, float]:
        """
        Calcula el % de competencias con al menos 1 RA asociado.

        Returns:
            Dict con estructura:
            {
                'total_competencias': 5,
                'competencias_con_ra': 5,
                'porcentaje_cobertura': 100.0,
                'promedio_ra_por_competencia': 2.6
            }
        """
        if self.competencias.empty or self.ra.empty:
            return {
                'total_competencias': len(self.competencias),
                'competencias_con_ra': 0,
                'porcentaje_cobertura': 0.0,
                'promedio_ra_por_competencia': 0.0
            }

        # Emparejar cada competencia del Paso 2 con los RA que la citan en
        # 'Competencia por desarrollar' (auditoría E3-5). El Paso 3 suele citar
        # la competencia abreviada, por eso se acepta prefijo o similitud ≥ 0,80.
        if 'Redacción competencia' in self.competencias.columns:
            comps = [_clave_texto(c) for c in self.competencias['Redacción competencia'].dropna()]
        else:
            comps = []
        citas = ([_clave_texto(c) for c in self.ra['Competencia por desarrollar'].dropna()]
                 if 'Competencia por desarrollar' in self.ra.columns else [])

        def _cita_a(comp: str, cita: str) -> bool:
            return (comp.startswith(cita) or cita.startswith(comp)
                    or (len(cita) > 15 and cita[:25] in comp)
                    or SequenceMatcher(None, comp, cita).ratio() >= 0.80)

        ra_por_comp = pd.Series([sum(_cita_a(c, x) for x in citas) for c in comps], dtype=float)
        competencias_con_ra = int((ra_por_comp > 0).sum())

        total_comp = len(comps)
        porcentaje = (competencias_con_ra / total_comp * 100) if total_comp > 0 else 0
        promedio_ra = ra_por_comp.mean() if not ra_por_comp.empty else 0

        resultado = {
            'total_competencias': total_comp,
            'competencias_con_ra': competencias_con_ra,
            'porcentaje_cobertura': round(porcentaje, 1),
            'promedio_ra_por_competencia': round(promedio_ra, 1)
        }

        logger.info(f"Cobertura competencias: {resultado}")
        return resultado

    def calcular_diversidad_metodologica(self) -> Dict[str, any]:
        """
        Calcula la diversidad de estrategias pedagógicas.

        Returns:
            Dict con estructura:
            {
                'num_estrategias_unicas': 12,
                'estrategias_mas_frecuentes': [('Taller', 15), ('Caso', 10), ('Proyecto', 8)],
                'porcentaje_metodologias_activas': 65.0
            }
        """
        if self.estrategias_micro.empty:
            return {
                'num_estrategias_unicas': 0,
                'estrategias_mas_frecuentes': [],
                'porcentaje_metodologias_activas': 0.0
            }

        # Buscar columnas de estrategias
        estrategias_col = None
        for col_name in ['Actividades de aprendizaje', 'Estrategias de enseñanza aprendizaje', 'Estrategias']:
            if col_name in self.estrategias_micro.columns:
                estrategias_col = col_name
                break

        # Keywords de estrategias para buscar
        keywords_estrategias = [
            'clase magistral', 'taller', 'laboratorio', 'caso', 'estudio de caso',
            'problema', 'proyecto', 'simulación', 'debate', 'ejercicio',
            'lectura', 'seminario', 'tutoría', 'investigación', 'exposición',
            'charla', 'demonstración', 'demostración', 'mapeo', 'analogía'
        ]

        # Buscar columnas de evaluación también
        for col_name in ['Actividades de evaluación', 'Estrategias de evaluación']:
            if col_name in self.estrategias_micro.columns:
                break

        # Extraer y contar keywords de estrategias
        todas_estrategias = []

        if estrategias_col:
            for texto in self.estrategias_micro[estrategias_col].dropna():
                texto_lower = str(texto).lower()
                for kw in keywords_estrategias:
                    if kw in texto_lower:
                        todas_estrategias.append(kw.title())

        # Contar keywords encontradas
        if todas_estrategias:
            frecuencias = Counter(todas_estrategias)
            mas_frecuentes = frecuencias.most_common(10)
            num_unicas = len(frecuencias)

            # Calcular porcentaje de metodologías activas
            metodologias_activas = ['Taller', 'Laboratorio', 'Caso', 'Problema', 'Proyecto', 'Simulación', 'Debate']
            activas_count = sum(frecuencias.get(m, 0) for m in metodologias_activas)
            porcentaje_activas = (activas_count / len(todas_estrategias) * 100) if todas_estrategias else 0
        else:
            mas_frecuentes = []
            num_unicas = 0
            porcentaje_activas = 0.0

        resultado = {
            'num_estrategias_unicas': num_unicas,
            'estrategias_mas_frecuentes': mas_frecuentes,
            'porcentaje_metodologias_activas': round(porcentaje_activas, 1)
        }

        logger.info(f"Diversidad metodológica: {resultado}")
        return resultado

    def calcular_completitud(self) -> Dict[str, float]:
        """
        Calcula el % de completitud de datos.

        Returns:
            Dict con estructura:
            {
                'completitud_competencias': 95.0,
                'completitud_ra': 98.0,
                'completitud_estrategias_meso': 80.0,
                'completitud_estrategias_micro': 85.0,
                'completitud_total': 89.5
            }
        """
        def calcular_completitud_df(df: pd.DataFrame, columnas) -> float:
            """% de celdas diligenciadas en las columnas clave (una columna
            ausente cuenta como vacía) sobre las filas de la unidad del paso."""
            if df.empty:
                return 0.0
            llenas = sum(int(df[c].notna().sum()) if c in df.columns else 0 for c in columnas)
            total_cells = len(df) * len(columnas)
            return (llenas / total_cells * 100) if total_cells > 0 else 0.0

        def filas_con(df: pd.DataFrame, col: str) -> pd.DataFrame:
            return df[df[col].notna()] if col in df.columns else df.iloc[0:0]

        # Unidades (auditoría E3-3; decisiones D4-D6): una fila por competencia,
        # por RA único, por estrategia declarada y por asignatura (sin la fila
        # de totales ni los espacios electivos, que no declaran contenido; N1).
        competencias = filas_con(self.competencias, 'Redacción competencia')
        estrategias = filas_con(self.estrategias_meso, 'Estrategia del programa')
        asignaturas = filas_con(self.estrategias_micro, 'Nombre asignatura o módulo')
        if not asignaturas.empty:
            nombres = asignaturas['Nombre asignatura o módulo'].astype(str).str.strip()
            asignaturas = asignaturas[~nombres.str.fullmatch(r'[\d\.\s]+')
                                      & ~nombres.str.lower().str.startswith('electiva')]

        comp_competencias = calcular_completitud_df(competencias, COLUMNAS_COMPLETITUD['competencias'])
        comp_ra = calcular_completitud_df(self._ra_unicos(), COLUMNAS_COMPLETITUD['ra'])
        comp_meso = calcular_completitud_df(estrategias, COLUMNAS_COMPLETITUD['estrategias_meso'])
        comp_micro = calcular_completitud_df(asignaturas, COLUMNAS_COMPLETITUD['estrategias_micro'])

        # Promedio ponderado (más peso a competencias y RA)
        completitud_total = (
            comp_competencias * 0.3 +
            comp_ra * 0.4 +
            comp_meso * 0.15 +
            comp_micro * 0.15
        )

        resultado = {
            'completitud_competencias': round(comp_competencias, 1),
            'completitud_ra': round(comp_ra, 1),
            'completitud_estrategias_meso': round(comp_meso, 1),
            'completitud_estrategias_micro': round(comp_micro, 1),
            'completitud_total': round(completitud_total, 1)
        }

        logger.info(f"Completitud: {resultado}")
        return resultado

    def calcular_score_calidad(self) -> float:
        """
        Calcula un score general de calidad (0-100).

        Combina los tres componentes que discriminan entre programas:
        exigencia (40 %), equilibrio de saberes (30 %) y variedad de
        estrategias (30 %). Completitud y cobertura de competencias se
        reportan como condiciones verificadas (generar_reporte_indicadores) y
        no entran al puntaje: valen 100 % en todo el corpus (auditoría E3-7).

        Returns:
            float: Score de calidad (0-100)
        """
        return self.desglose_score_calidad()['total']

    def desglose_score_calidad(self) -> Dict:
        """Componentes del score de calidad: valor de entrada, puntaje 0-100, peso, aporte y regla."""
        complejidad = self.calcular_complejidad_cognitiva()
        balance = self.calcular_balance_tipo_saber()
        diversidad = self.calcular_diversidad_metodologica()

        # Normalizar indicadores a 0-100
        score_complejidad = complejidad['indice_complejidad']
        score_balance = 100 - balance['desviacion_estandar'] * 5  # Menor desviación = mejor
        score_balance = max(0, min(100, score_balance))
        score_diversidad = min(100, diversidad['num_estrategias_unicas'] * 8)  # 13+ estrategias = 100

        componentes = [
            ('Exigencia de los RA', f"nivel medio en escala 1–6 → índice {score_complejidad:.1f}",
             score_complejidad, QUALITY_WEIGHTS['complejidad_cognitiva'],
             'Índice = (nivel medio de los RA únicos − 1) / 5 × 100'),
            ('Equilibrio de tipos de saber', f"desviación estándar {balance['desviacion_estandar']:.1f} puntos",
             score_balance, QUALITY_WEIGHTS['balance_tipo_saber'],
             '100 − 5 × desviación estándar de Saber, SaberHacer y SaberSer (0–100)'),
            ('Variedad de estrategias', f"{diversidad['num_estrategias_unicas']} estrategias distintas",
             score_diversidad, QUALITY_WEIGHTS['diversidad_metodologica'],
             '8 puntos por estrategia distinta, máximo 100'),
        ]
        filas = [{'componente': c, 'entrada': e, 'puntaje': round(p, 1), 'peso': w, 'aporte': round(p * w, 1),
                  'regla': r} for c, e, p, w, r in componentes]
        return {'componentes': filas, 'total': round(sum(p * w for _, _, p, w, _ in componentes), 1)}

    def generar_reporte_indicadores(self) -> Dict:
        """
        Genera reporte completo de todos los indicadores.

        Returns:
            Dict con todos los indicadores calculados:
            {
                'programa': str,
                'score_calidad': float,
                'balance_tipo_saber': Dict,
                'complejidad_cognitiva': Dict,
                'cobertura_competencias': Dict,
                'diversidad_metodologica': Dict,
                'completitud': Dict,
                'resumen': {
                    'total_competencias': int,
                    'total_ra': int,
                    'total_estrategias_micro': int
                }
            }

        Example:
            >>> reporte = analyzer.generar_reporte_indicadores()
            >>> print(f"Score: {reporte['score_calidad']}/100")
        """
        logger.info(f"Generando reporte de indicadores para {self.programa_nombre}")

        reporte = {
            'programa': self.programa_nombre,
            'score_calidad': self.calcular_score_calidad(),
            'score_desglose': self.desglose_score_calidad(),
            'balance_tipo_saber': self.calcular_balance_tipo_saber(),
            'complejidad_cognitiva': self.calcular_complejidad_cognitiva(),
            'cobertura_competencias': self.calcular_cobertura_competencias(),
            'diversidad_metodologica': self.calcular_diversidad_metodologica(),
            'completitud': self.calcular_completitud(),
            # Condiciones que el formato garantiza (100 % en el corpus): se
            # informan, no puntúan (auditoría E3-7)
            'condiciones_verificadas': {
                'completitud_total': self.calcular_completitud()['completitud_total'],
                'cobertura_competencias': self.calcular_cobertura_competencias()['porcentaje_cobertura'],
            },
            # Unidades de las decisiones D4-D6 de la auditoría
            'resumen': {
                'total_competencias': int(self.competencias['Redacción competencia'].notna().sum())
                if 'Redacción competencia' in self.competencias.columns else len(self.competencias),
                'total_ra': len(self._ra_unicos()),
                'total_estrategias_meso': int(self.estrategias_meso['Estrategia del programa'].notna().sum())
                if 'Estrategia del programa' in self.estrategias_meso.columns else len(self.estrategias_meso),
                'total_estrategias_micro': self._contar_asignaturas_unicas()
            }
        }

        logger.info(f"Reporte generado. Score: {reporte['score_calidad']}/100")
        return reporte

    def generar_reporte_textual(self) -> str:
        """
        Genera reporte textual formateado.

        Returns:
            str: Reporte en formato texto
        """
        reporte = self.generar_reporte_indicadores()

        texto = f"""
╔═══════════════════════════════════════════════════════════════╗
║  REPORTE DE INDICADORES CURRICULARES                         ║
╚═══════════════════════════════════════════════════════════════╝

Programa: {reporte['programa']}
Score de Calidad: {reporte['score_calidad']}/100

═══════════════════════════════════════════════════════════════

📊 BALANCE DE TIPOS DE SABER

  Saber:       {reporte['balance_tipo_saber']['Saber']:>5.1f}%  {'█' * int(reporte['balance_tipo_saber']['Saber'] / 5)}
  SaberHacer:  {reporte['balance_tipo_saber']['SaberHacer']:>5.1f}%  {'█' * int(reporte['balance_tipo_saber']['SaberHacer'] / 5)}
  SaberSer:    {reporte['balance_tipo_saber']['SaberSer']:>5.1f}%  {'█' * int(reporte['balance_tipo_saber']['SaberSer'] / 5)}

  Desviación estándar: {reporte['balance_tipo_saber']['desviacion_estandar']:.1f}%
  Estado: {'✅ Balanceado' if reporte['balance_tipo_saber']['balanceado'] else '⚠️  Desbalanceado'}

═══════════════════════════════════════════════════════════════

🧠 COMPLEJIDAD COGNITIVA (Taxonomía de Bloom)

  Básico:       {reporte['complejidad_cognitiva']['Básico']:>5.1f}%  {'█' * int(reporte['complejidad_cognitiva']['Básico'] / 5)}
  Intermedio:   {reporte['complejidad_cognitiva']['Intermedio']:>5.1f}%  {'█' * int(reporte['complejidad_cognitiva']['Intermedio'] / 5)}
  Avanzado:     {reporte['complejidad_cognitiva']['Avanzado']:>5.1f}%  {'█' * int(reporte['complejidad_cognitiva']['Avanzado'] / 5)}

  Nivel promedio: {reporte['complejidad_cognitiva']['nivel_promedio']:.1f}/6
  Índice de complejidad: {reporte['complejidad_cognitiva']['indice_complejidad']:.1f}/100

═══════════════════════════════════════════════════════════════

📌 COBERTURA DE COMPETENCIAS

  Total competencias: {reporte['cobertura_competencias']['total_competencias']}
  Competencias con RA: {reporte['cobertura_competencias']['competencias_con_ra']}
  Cobertura: {reporte['cobertura_competencias']['porcentaje_cobertura']:.1f}%
  Promedio RA/competencia: {reporte['cobertura_competencias']['promedio_ra_por_competencia']:.1f}

═══════════════════════════════════════════════════════════════

🎯 DIVERSIDAD METODOLÓGICA

  Estrategias únicas: {reporte['diversidad_metodologica']['num_estrategias_unicas']}
  Metodologías activas: {reporte['diversidad_metodologica']['porcentaje_metodologias_activas']:.1f}%

  Top 5 estrategias:
"""
        for estrategia, count in reporte['diversidad_metodologica']['estrategias_mas_frecuentes']:
            texto += f"    - {estrategia}: {count} veces\n"

        texto += f"""
═══════════════════════════════════════════════════════════════

✅ COMPLETITUD DE DATOS

  Competencias: {reporte['completitud']['completitud_competencias']:.1f}%
  Resultados de Aprendizaje: {reporte['completitud']['completitud_ra']:.1f}%
  Estrategias Meso: {reporte['completitud']['completitud_estrategias_meso']:.1f}%
  Estrategias Micro: {reporte['completitud']['completitud_estrategias_micro']:.1f}%

  Completitud Total: {reporte['completitud']['completitud_total']:.1f}%

═══════════════════════════════════════════════════════════════
"""

        return texto


# ============================================================================
# EJEMPLO DE USO
# ============================================================================

if __name__ == '__main__':
    print("╔═══════════════════════════════════════════════════════════╗")
    print("║  ANALIZADOR DE INDICADORES CURRICULARES                  ║")
    print("╚═══════════════════════════════════════════════════════════╝\n")

    print("Para usar el analizador:")
    print("""
from src.extractor import ExcelExtractor
from src.analyzer import CurricularAnalyzer

# Extraer datos
extractor = ExcelExtractor('archivo.xlsx')
data = extractor.extract_all()

# Analizar
analyzer = CurricularAnalyzer(data)

# Obtener indicadores
reporte = analyzer.generar_reporte_indicadores()
print(f"Score: {reporte['score_calidad']}/100")

# O reporte textual
print(analyzer.generar_reporte_textual())
    """)
