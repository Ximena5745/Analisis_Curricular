"""
Módulo de generación de reportes.

Genera reportes en múltiples formatos:
- HTML (individual y consolidado)
- Excel (matrices y tablas)
- PDF (requiere weasyprint)
- JSON (datos estructurados)
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
import pandas as pd
import numpy as np
import json

import sys
sys.path.append(str(Path(__file__).parent.parent))

from config import OUTPUT_FOLDER, TEMPLATES_DIR

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def convert_to_native_types(obj: Any) -> Any:
    """
    Convierte tipos numpy a tipos nativos de Python para serialización JSON.

    Args:
        obj: Objeto a convertir

    Returns:
        Objeto con tipos nativos de Python
    """
    if isinstance(obj, dict):
        return {k: convert_to_native_types(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_to_native_types(item) for item in obj]
    elif isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.bool_):
        return bool(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    else:
        return obj


class ReportGenerator:
    """
    Generador de reportes en múltiples formatos.

    Example:
        >>> generator = ReportGenerator()
        >>> generator.generate_html_report(data, indicadores, 'reporte.html')
    """

    def __init__(self, output_folder: Optional[str] = None,
                 templates_folder: Optional[str] = None):
        """
        Inicializa el generador de reportes.

        Args:
            output_folder: Carpeta de salida para reportes
            templates_folder: Carpeta con templates HTML
        """
        self.output_folder = Path(output_folder or OUTPUT_FOLDER)
        self.templates_folder = Path(templates_folder or TEMPLATES_DIR)
        self.output_folder.mkdir(parents=True, exist_ok=True)

        logger.info(f"ReportGenerator inicializado. Output: {self.output_folder}")

    def generate_html_report(self, programa_data: Dict,
                            indicadores: Dict,
                            output_path: str) -> str:
        """
        Genera reporte HTML individual por programa.

        Args:
            programa_data (Dict): Datos del programa
            indicadores (Dict): Indicadores calculados
            output_path (str): Ruta de salida del HTML

        Returns:
            str: Ruta del archivo generado
        """
        programa = programa_data['metadata']['programa']
        logger.info(f"Generando reporte HTML para {programa}")

        # Construir HTML
        html_content = f"""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Reporte Curricular - {programa}</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 40px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }}
        h2 {{
            color: #34495e;
            margin-top: 30px;
        }}
        .metric {{
            display: inline-block;
            background-color: #ecf0f1;
            padding: 15px 25px;
            margin: 10px;
            border-radius: 5px;
            min-width: 200px;
        }}
        .metric-value {{
            font-size: 2em;
            font-weight: bold;
            color: #3498db;
        }}
        .metric-label {{
            font-size: 0.9em;
            color: #7f8c8d;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        th {{
            background-color: #3498db;
            color: white;
        }}
        .progress-bar {{
            background-color: #ecf0f1;
            border-radius: 5px;
            height: 25px;
            position: relative;
            margin: 10px 0;
        }}
        .progress-fill {{
            background-color: #3498db;
            height: 100%;
            border-radius: 5px;
            display: flex;
            align-items: center;
            padding-left: 10px;
            color: white;
            font-weight: bold;
        }}
        .footer {{
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
            text-align: center;
            color: #7f8c8d;
            font-size: 0.9em;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 Reporte de Análisis Curricular</h1>
        <h2>{programa}</h2>
        <p><strong>Fecha de generación:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>

        <h2>🎯 Score General de Calidad</h2>
        <div class="metric">
            <div class="metric-value">{indicadores['score_calidad']}/100</div>
            <div class="metric-label">Score de Calidad</div>
        </div>

        <h2>📈 Resumen del Programa</h2>
        <div class="metric">
            <div class="metric-value">{indicadores['resumen']['total_competencias']}</div>
            <div class="metric-label">Competencias</div>
        </div>
        <div class="metric">
            <div class="metric-value">{indicadores['resumen']['total_ra']}</div>
            <div class="metric-label">Resultados de Aprendizaje</div>
        </div>
        <div class="metric">
            <div class="metric-value">{indicadores['resumen']['total_estrategias_micro']}</div>
            <div class="metric-label">Estrategias Microcurriculares</div>
        </div>

        <h2>📊 Balance de Tipos de Saber</h2>
        <p><strong>Saber:</strong> {indicadores['balance_tipo_saber']['Saber']}%</p>
        <div class="progress-bar">
            <div class="progress-fill" style="width: {indicadores['balance_tipo_saber']['Saber']}%">
                {indicadores['balance_tipo_saber']['Saber']}%
            </div>
        </div>

        <p><strong>SaberHacer:</strong> {indicadores['balance_tipo_saber']['SaberHacer']}%</p>
        <div class="progress-bar">
            <div class="progress-fill" style="width: {indicadores['balance_tipo_saber']['SaberHacer']}%">
                {indicadores['balance_tipo_saber']['SaberHacer']}%
            </div>
        </div>

        <p><strong>SaberSer:</strong> {indicadores['balance_tipo_saber']['SaberSer']}%</p>
        <div class="progress-bar">
            <div class="progress-fill" style="width: {indicadores['balance_tipo_saber']['SaberSer']}%">
                {indicadores['balance_tipo_saber']['SaberSer']}%
            </div>
        </div>

        <h2>🧠 Complejidad Cognitiva (Taxonomía de Bloom)</h2>
        <p><strong>Básico:</strong> {indicadores['complejidad_cognitiva']['Básico']}%</p>
        <p><strong>Intermedio:</strong> {indicadores['complejidad_cognitiva']['Intermedio']}%</p>
        <p><strong>Avanzado:</strong> {indicadores['complejidad_cognitiva']['Avanzado']}%</p>
        <p><strong>Índice de Complejidad:</strong> {indicadores['complejidad_cognitiva']['indice_complejidad']}/100</p>

        <h2>📌 Competencias del Programa</h2>
        <table>
            <thead>
                <tr>
                    <th>No.</th>
                    <th>Redacción Competencia</th>
                    <th>Tipo</th>
                </tr>
            </thead>
            <tbody>
"""
        # Agregar competencias
        for _, row in programa_data['competencias'].iterrows():
            html_content += f"""
                <tr>
                    <td>{row.get('No.', '')}</td>
                    <td>{row.get('Redacción competencia', '')}</td>
                    <td>{row.get('Tipo de competencia', '')}</td>
                </tr>
"""

        html_content += """
            </tbody>
        </table>

        <div class="footer">
            <p>Generado automáticamente por Sistema de Análisis Microcurricular</p>
        </div>
    </div>
</body>
</html>
"""

        # Guardar archivo
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

        logger.info(f"Reporte HTML generado: {output_path}")
        return str(output_path)

    def generate_excel_matrix(self, matriz: pd.DataFrame, output_path: str) -> str:
        """
        Genera matriz Excel de Programas × Temáticas.

        Args:
            matriz (pd.DataFrame): Matriz de temáticas
            output_path (str): Ruta de salida del Excel

        Returns:
            str: Ruta del archivo generado
        """
        logger.info(f"Generando matriz Excel")

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Guardar con formato
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            matriz.to_excel(writer, sheet_name='Matriz Temáticas', index=False)

            # Obtener worksheet para aplicar formato
            worksheet = writer.sheets['Matriz Temáticas']

            # Auto-ajustar anchos de columna
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = min(max_length + 2, 50)
                worksheet.column_dimensions[column_letter].width = adjusted_width

        logger.info(f"Matriz Excel generada: {output_path}")
        return str(output_path)

    def generate_json_report(self, programa_data: Dict,
                            indicadores: Dict,
                            tematicas: Dict,
                            output_path: str) -> str:
        """
        Genera reporte en formato JSON.

        Args:
            programa_data (Dict): Datos del programa
            indicadores (Dict): Indicadores calculados
            tematicas (Dict): Temáticas detectadas
            output_path (str): Ruta de salida del JSON

        Returns:
            str: Ruta del archivo generado
        """
        logger.info(f"Generando reporte JSON")

        # Construir estructura JSON
        reporte_json = {
            'programa': programa_data['metadata']['programa'],
            'fecha_generacion': datetime.now().isoformat(),
            'archivo_origen': programa_data['metadata']['archivo'],
            'indicadores': indicadores,
            'tematicas': {
                'presentes': tematicas.get('tematicas_presentes', []),
                'num_tematicas': tematicas.get('num_tematicas', 0),
                'resumen': tematicas.get('resumen', {})
            },
            'resumen': {
                'total_competencias': len(programa_data['competencias']),
                'total_ra': len(programa_data['resultados_aprendizaje']),
                'total_estrategias_micro': len(programa_data.get('estrategias_micro', []))
            }
        }

        # Convertir tipos numpy a tipos nativos de Python
        reporte_json = convert_to_native_types(reporte_json)

        # Guardar JSON
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(reporte_json, f, ensure_ascii=False, indent=2)

        logger.info(f"Reporte JSON generado: {output_path}")
        return str(output_path)

    def generate_consolidated_excel(self, all_reportes: List[Dict],
                                    output_path: str) -> str:
        """
        Genera Excel consolidado con todos los programas.

        Args:
            all_reportes (List[Dict]): Lista de reportes de todos los programas
            output_path (str): Ruta de salida del Excel

        Returns:
            str: Ruta del archivo generado
        """
        logger.info(f"Generando Excel consolidado con {len(all_reportes)} programas")

        # Crear DataFrame consolidado
        rows = []
        for reporte in all_reportes:
            row = {
                'Programa': reporte['programa'],
                'Score_Calidad': reporte['score_calidad'],
                'Total_Competencias': reporte['resumen']['total_competencias'],
                'Total_RA': reporte['resumen']['total_ra'],
                'Saber_%': reporte['balance_tipo_saber']['Saber'],
                'SaberHacer_%': reporte['balance_tipo_saber']['SaberHacer'],
                'SaberSer_%': reporte['balance_tipo_saber']['SaberSer'],
                'Complejidad_Basico_%': reporte['complejidad_cognitiva']['Básico'],
                'Complejidad_Intermedio_%': reporte['complejidad_cognitiva']['Intermedio'],
                'Complejidad_Avanzado_%': reporte['complejidad_cognitiva']['Avanzado'],
                'Indice_Complejidad': reporte['complejidad_cognitiva']['indice_complejidad'],
                'Completitud_%': reporte['completitud']['completitud_total']
            }
            rows.append(row)

        df_consolidado = pd.DataFrame(rows)

        # Guardar en Excel
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            df_consolidado.to_excel(writer, sheet_name='Indicadores Consolidados', index=False)

        logger.info(f"Excel consolidado generado: {output_path}")
        return str(output_path)


if __name__ == '__main__':
    print("╔═══════════════════════════════════════════════════════════╗")
    print("║  GENERADOR DE REPORTES                                   ║")
    print("╚═══════════════════════════════════════════════════════════╝\n")

    print("Para usar el generador:")
    print("""
from src.extractor import ExcelExtractor
from src.analyzer import CurricularAnalyzer
from src.report_generator import ReportGenerator

# Extraer y analizar
extractor = ExcelExtractor('archivo.xlsx')
data = extractor.extract_all()
analyzer = CurricularAnalyzer(data)
indicadores = analyzer.generar_reporte_indicadores()

# Generar reportes
generator = ReportGenerator()
generator.generate_html_report(data, indicadores, 'reporte.html')
generator.generate_json_report(data, indicadores, {}, 'reporte.json')
    """)
