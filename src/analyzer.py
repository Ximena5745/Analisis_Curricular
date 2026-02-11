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
from typing import Dict, List, Optional, Tuple
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
    BALANCE_IDEAL_SABER,
    QUALITY_WEIGHTS
)

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

        # Contar por tipo
        tipo_counts = self.ra['TipoSaber'].value_counts()
        total = len(self.ra)

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

    def _get_nivel_taxonomico(self, verbo: str, nivel_dominio: str) -> int:
        """
        Determina el nivel taxonómico (1-6) de un verbo.

        Args:
            verbo (str): Verbo del RA
            nivel_dominio (str): Nivel de dominio declarado

        Returns:
            int: Nivel taxonómico (1=Recordar, 6=Crear)
        """
        if pd.isna(verbo):
            return 1

        verbo_lower = str(verbo).lower().strip()

        # Buscar en taxonomía de Bloom
        for nivel_nombre, config in TAXONOMIA_BLOOM.items():
            verbos_nivel = [v.lower() for v in config['verbos']]
            if verbo_lower in verbos_nivel:
                return config['nivel']

        # Si no se encuentra, intentar inferir del nivel_dominio
        if not pd.isna(nivel_dominio):
            nivel_str = str(nivel_dominio).lower()

            if 'analisis' in nivel_str or 'analis' in nivel_str:
                return 4
            elif 'evalua' in nivel_str or 'critica' in nivel_str:
                return 5
            elif 'crea' in nivel_str or 'diseña' in nivel_str:
                return 6
            elif 'aplic' in nivel_str:
                return 3
            elif 'comprend' in nivel_str or 'entiend' in nivel_str:
                return 2

        # Nivel por defecto
        return 2

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

        # Obtener niveles taxonómicos
        niveles = []
        for _, row in self.ra.iterrows():
            verbo = row.get('Verbo RA', '')
            nivel_dominio = row.get('Nivel Dominio', '')
            nivel = self._get_nivel_taxonomico(verbo, nivel_dominio)
            niveles.append(nivel)

        total = len(niveles)

        # Clasificar por complejidad
        basico = sum(1 for n in niveles if COMPLEJIDAD_THRESHOLDS['BASICO'][0] <= n <= COMPLEJIDAD_THRESHOLDS['BASICO'][1])
        intermedio = sum(1 for n in niveles if COMPLEJIDAD_THRESHOLDS['INTERMEDIO'][0] <= n <= COMPLEJIDAD_THRESHOLDS['INTERMEDIO'][1])
        avanzado = sum(1 for n in niveles if COMPLEJIDAD_THRESHOLDS['AVANZADO'][0] <= n <= COMPLEJIDAD_THRESHOLDS['AVANZADO'][1])

        # Calcular porcentajes
        resultado = {
            'Básico': round((basico / total * 100), 1) if total > 0 else 0,
            'Intermedio': round((intermedio / total * 100), 1) if total > 0 else 0,
            'Avanzado': round((avanzado / total * 100), 1) if total > 0 else 0,
            'nivel_promedio': round(np.mean(niveles), 1) if niveles else 0
        }

        # Calcular índice de complejidad (0-100)
        # Fórmula: (promedio - 1) / 5 * 100
        indice = ((resultado['nivel_promedio'] - 1) / 5 * 100) if resultado['nivel_promedio'] > 0 else 0
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

        # Contar RA por competencia
        if 'Competencia por desarrollar' in self.ra.columns:
            ra_por_comp = self.ra['Competencia por desarrollar'].value_counts()
            competencias_con_ra = len(ra_por_comp)
        else:
            competencias_con_ra = 0
            ra_por_comp = pd.Series()

        total_comp = len(self.competencias)
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
                'estrategias_mas_frecuentes': [('ABP', 15), ('Estudio de caso', 10)],
                'porcentaje_metodologias_activas': 65.0
            }
        """
        if self.estrategias_micro.empty:
            return {
                'num_estrategias_unicas': 0,
                'estrategias_mas_frecuentes': [],
                'porcentaje_metodologias_activas': 0.0
            }

        # Extraer estrategias
        if 'Estrategias de enseñanza aprendizaje' in self.estrategias_micro.columns:
            estrategias = self.estrategias_micro['Estrategias de enseñanza aprendizaje'].dropna()

            # Contar únicas
            estrategias_unicas = estrategias.unique()
            num_unicas = len(estrategias_unicas)

            # Contar frecuencias
            frecuencias = Counter(estrategias)
            mas_frecuentes = frecuencias.most_common(5)

            # Detectar metodologías activas
            metodologias_activas_keywords = [
                'abp', 'aprendizaje basado en proyectos',
                'caso', 'estudio de caso',
                'problema', 'aprendizaje basado en problemas',
                'proyecto', 'simulación', 'debate', 'taller'
            ]

            activas_count = 0
            for estrategia in estrategias:
                estrategia_lower = str(estrategia).lower()
                if any(keyword in estrategia_lower for keyword in metodologias_activas_keywords):
                    activas_count += 1

            porcentaje_activas = (activas_count / len(estrategias) * 100) if len(estrategias) > 0 else 0

        else:
            num_unicas = 0
            mas_frecuentes = []
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
        def calcular_completitud_df(df: pd.DataFrame) -> float:
            """Calcula completitud de un DataFrame."""
            if df.empty:
                return 0.0

            total_cells = df.shape[0] * df.shape[1]
            filled_cells = df.count().sum()  # Cuenta celdas no-NaN

            return (filled_cells / total_cells * 100) if total_cells > 0 else 0.0

        comp_competencias = calcular_completitud_df(self.competencias)
        comp_ra = calcular_completitud_df(self.ra)
        comp_meso = calcular_completitud_df(self.estrategias_meso)
        comp_micro = calcular_completitud_df(self.estrategias_micro)

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

        Combina múltiples indicadores con pesos configurables.

        Returns:
            float: Score de calidad (0-100)
        """
        # Calcular todos los indicadores
        completitud = self.calcular_completitud()
        complejidad = self.calcular_complejidad_cognitiva()
        balance = self.calcular_balance_tipo_saber()
        cobertura = self.calcular_cobertura_competencias()
        diversidad = self.calcular_diversidad_metodologica()

        # Normalizar indicadores a 0-100
        score_completitud = completitud['completitud_total']
        score_complejidad = complejidad['indice_complejidad']
        score_balance = 100 - balance['desviacion_estandar'] * 5  # Menor desviación = mejor
        score_balance = max(0, min(100, score_balance))
        score_cobertura = cobertura['porcentaje_cobertura']
        score_diversidad = min(100, diversidad['num_estrategias_unicas'] * 8)  # 12+ estrategias = 100

        # Calidad de redacción (simplificado - requeriría validador)
        score_redaccion = 80.0  # Placeholder

        # Calcular score ponderado
        score_total = (
            score_completitud * QUALITY_WEIGHTS['completitud'] +
            score_complejidad * QUALITY_WEIGHTS['complejidad_cognitiva'] +
            score_balance * QUALITY_WEIGHTS['balance_tipo_saber'] +
            score_diversidad * QUALITY_WEIGHTS['diversidad_metodologica'] +
            score_cobertura * QUALITY_WEIGHTS['cobertura_competencias'] +
            score_redaccion * QUALITY_WEIGHTS['calidad_redaccion']
        )

        return round(score_total, 1)

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
            'balance_tipo_saber': self.calcular_balance_tipo_saber(),
            'complejidad_cognitiva': self.calcular_complejidad_cognitiva(),
            'cobertura_competencias': self.calcular_cobertura_competencias(),
            'diversidad_metodologica': self.calcular_diversidad_metodologica(),
            'completitud': self.calcular_completitud(),
            'resumen': {
                'total_competencias': len(self.competencias),
                'total_ra': len(self.ra),
                'total_estrategias_meso': len(self.estrategias_meso),
                'total_estrategias_micro': len(self.estrategias_micro)
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
