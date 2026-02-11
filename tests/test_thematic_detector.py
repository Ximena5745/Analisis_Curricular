"""
Tests unitarios para el módulo ThematicDetector.

Ejecutar con:
    pytest tests/test_thematic_detector.py -v
"""

import unittest
import sys
from pathlib import Path

# Agregar src al path
sys.path.append(str(Path(__file__).parent.parent))

from src.thematic_detector import ThematicDetector


class TestThematicDetector(unittest.TestCase):
    """Tests para la clase ThematicDetector."""

    def setUp(self):
        """Configuración inicial para cada test."""
        self.detector = ThematicDetector()

    def test_detector_initialization(self):
        """Test que el detector se inicializa correctamente."""
        self.assertIsNotNone(self.detector)
        self.assertIsInstance(self.detector.tematicas_config, dict)
        self.assertGreater(len(self.detector.tematicas_config), 0)

    def test_detect_sostenibilidad(self):
        """Test detección de sostenibilidad."""
        texto = "Analizar dimensiones sostenibles y responsabilidad ambiental"

        resultado = self.detector.detect_in_text(texto)

        self.assertIn('SOSTENIBILIDAD', resultado)
        self.assertTrue(resultado['SOSTENIBILIDAD']['presente'])
        self.assertGreater(resultado['SOSTENIBILIDAD']['num_coincidencias'], 0)
        self.assertIn('sostenibles', resultado['SOSTENIBILIDAD']['keywords_encontradas'])

    def test_detect_inteligencia_artificial(self):
        """Test detección de IA."""
        texto = "Implementar algoritmos de machine learning e inteligencia artificial"

        resultado = self.detector.detect_in_text(texto)

        self.assertTrue(resultado['INTELIGENCIA ARTIFICIAL']['presente'])
        self.assertGreater(resultado['INTELIGENCIA ARTIFICIAL']['num_coincidencias'], 0)

    def test_no_detection_in_empty_text(self):
        """Test que texto vacío no detecta temáticas."""
        resultado = self.detector.detect_in_text("")

        for tematica, data in resultado.items():
            self.assertFalse(data['presente'])
            self.assertEqual(data['num_coincidencias'], 0)

    def test_normalize_text(self):
        """Test normalización de texto."""
        texto_con_tildes = "Análisis de gestión"
        normalizado = self.detector._normalize_text(texto_con_tildes)

        self.assertEqual(normalizado, "analisis de gestion")
        self.assertNotIn('á', normalizado)

    def test_extract_context(self):
        """Test extracción de contexto."""
        texto = "Este programa aborda la sostenibilidad ambiental en contextos empresariales"
        contexto = self.detector._extract_context(texto, "sostenibilidad", window=20)

        self.assertIsInstance(contexto, str)
        self.assertGreater(len(contexto), 0)
        self.assertIn("sostenibilidad", contexto.lower())

    def test_multiple_keywords_in_same_text(self):
        """Test detección de múltiples keywords."""
        texto = "Programa sostenible con responsabilidad ambiental y desarrollo sustentable"

        resultado = self.detector.detect_in_text(texto)

        self.assertTrue(resultado['SOSTENIBILIDAD']['presente'])
        # Debe detectar al menos 2 variantes (sostenible, ambiental, sustentable)
        self.assertGreaterEqual(resultado['SOSTENIBILIDAD']['num_coincidencias'], 2)


class TestThematicDetectorDataFrame(unittest.TestCase):
    """Tests para detección en DataFrames."""

    def setUp(self):
        """Configuración inicial."""
        self.detector = ThematicDetector()

    def test_detect_in_dataframe_basic(self):
        """Test detección básica en DataFrame."""
        import pandas as pd

        df = pd.DataFrame({
            'Texto': [
                'Desarrollo sostenible y ambiental',
                'Inteligencia artificial y machine learning',
                'Texto sin temáticas específicas'
            ]
        })

        df_resultado = self.detector.detect_in_dataframe(df, ['Texto'])

        # Verificar que se agregaron columnas de temáticas
        self.assertIn('SOSTENIBILIDAD_presente', df_resultado.columns)
        self.assertIn('INTELIGENCIA ARTIFICIAL_presente', df_resultado.columns)

        # Verificar detecciones
        self.assertTrue(df_resultado.loc[0, 'SOSTENIBILIDAD_presente'])
        self.assertTrue(df_resultado.loc[1, 'INTELIGENCIA ARTIFICIAL_presente'])


def run_tests():
    """Ejecuta todos los tests."""
    unittest.main(argv=[''], exit=False, verbosity=2)


if __name__ == '__main__':
    run_tests()
