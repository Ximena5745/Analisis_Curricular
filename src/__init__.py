"""
Paquete principal del sistema de análisis microcurricular.
"""

__version__ = "1.0.0"
__author__ = "Coordinación Académica"

from .extractor import ExcelExtractor
from .analyzer import CurricularAnalyzer
from .thematic_detector import ThematicDetector
from .validator import QualityValidator
from .report_generator import ReportGenerator

__all__ = [
    'ExcelExtractor',
    'CurricularAnalyzer',
    'ThematicDetector',
    'QualityValidator',
    'ReportGenerator'
]
