"""
Dashboard interactivo de análisis microcurricular con Streamlit.

Uso:
    streamlit run dashboard/app.py
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import sys

# Agregar src al path
sys.path.append(str(Path(__file__).parent.parent))

from src.extractor import ExcelExtractor
from src.analyzer import CurricularAnalyzer
from src.thematic_detector import ThematicDetector
from config import INPUT_FOLDER, OUTPUT_FOLDER, TEMATICAS

# Configuración de la página
st.set_page_config(
    page_title="Análisis Microcurricular",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado
st.markdown("""
    <style>
    .main {
        padding: 0rem 1rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
    }
    h1 {
        color: #1f77b4;
    }
    .hero-panel {
        border-radius: 22px;
        border: 1px solid #dbeafe;
        background: linear-gradient(180deg, #ffffff 0%, #f8fbff 100%);
        padding: 26px;
        box-shadow: 0 24px 60px rgba(15, 23, 42, 0.08);
    }
    .feature-card {
        border-radius: 20px;
        border: 1px solid #e2e8f0;
        background: #ffffff;
        padding: 20px;
        min-height: 170px;
        box-shadow: 0 12px 30px rgba(15, 23, 42, 0.04);
    }
    .feature-card h3 {
        margin: 0.75rem 0 0.4rem;
        color: #0f3460;
        font-size: 1.05rem;
    }
    .feature-card p {
        margin: 0;
        color: #475569;
        font-size: 0.95rem;
        line-height: 1.6;
    }
    .feature-grid {
        display: grid;
        grid-template-columns: repeat(3, minmax(240px, 1fr));
        gap: 18px;
    }
    .hero-action {
        border-radius: 16px;
        background: #f8fbff;
        border: 1px solid #dbeafe;
        padding: 22px;
    }
    .hero-action h2 {
        margin-top: 0;
        margin-bottom: 8px;
        color: #0f3460;
    }
    .hero-action p {
        margin: 0;
        color: #475569;
        font-size: 0.95rem;
        line-height: 1.7;
    }
    .action-box {
        border: 2px dashed #bfdbfe;
        border-radius: 18px;
        background: #ffffff;
        padding: 24px;
        text-align: center;
        min-height: 170px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        gap: 12px;
        color: #0f3460;
    }
    .cta-row {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
        gap: 12px;
        margin-top: 18px;
    }
    .cta-button {
        border-radius: 14px;
        border: 1px solid #dbeafe;
        background: #ffffff;
        color: #0f3460;
        padding: 12px 14px;
        font-weight: 700;
        text-align: center;
    }
    .content-block {
        display: grid;
        grid-template-columns: 1.2fr 1fr;
        gap: 24px;
        margin-top: 32px;
    }
    .steps-list {
        list-style: none;
        padding: 0;
        margin: 0;
    }
    .steps-list li {
        margin-bottom: 14px;
        font-size: 0.98rem;
        color: #334155;
    }
    .steps-list li strong {
        color: #0f3460;
    }
    .table-card {
        border-radius: 20px;
        background: #ffffff;
        border: 1px solid #e2e8f0;
        padding: 24px;
    }
    .structured-table {
        border-collapse: collapse;
        width: 100%;
        font-size: 0.95rem;
    }
    .structured-table th,
    .structured-table td {
        border: 1px solid #e2e8f0;
        padding: 12px 14px;
        text-align: left;
        color: #334155;
    }
    .structured-table th {
        background: #eff6ff;
        color: #0f3460;
    }
    .structured-table tbody tr:nth-child(even) {
        background: #f8fafc;
    }
    </style>
""", unsafe_allow_html=True)


def render_icon_svg(name: str, color: str = "#0f3460", size: int = 36) -> str:
    icons = {
        'document': f'''<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M6 2H14L18 6V22H6V2Z" fill="{color}" fill-opacity="0.12"/><path d="M14 2V6H18" stroke="{color}" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/><path d="M6 2H14L18 6V22H6V2Z" stroke="{color}" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/><path d="M9 12H15" stroke="{color}" stroke-width="1.8" stroke-linecap="round"/><path d="M9 16H15" stroke="{color}" stroke-width="1.8" stroke-linecap="round"/></svg>''',
        'trend': f'''<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M4 16L9 11L13 15L20 8" stroke="{color}" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/><path d="M4 20H20" stroke="{color}" stroke-width="1.8" stroke-linecap="round"/><path d="M4 4V20" stroke="{color}" stroke-width="1.8" stroke-linecap="round"/></svg>''',
        'bloom': f'''<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><rect x="4" y="4" width="16" height="16" rx="4" fill="{color}" fill-opacity="0.12"/><path d="M8 15H16" stroke="{color}" stroke-width="1.8" stroke-linecap="round"/><path d="M8 11H14" stroke="{color}" stroke-width="1.8" stroke-linecap="round"/><path d="M8 7H12" stroke="{color}" stroke-width="1.8" stroke-linecap="round"/></svg>''',
        'search': f'''<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><circle cx="11" cy="11" r="6" stroke="{color}" stroke-width="1.8"/><path d="M16.5 16.5L20 20" stroke="{color}" stroke-width="1.8" stroke-linecap="round"/></svg>''',
        'gear': f'''<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><circle cx="12" cy="12" r="3" stroke="{color}" stroke-width="1.8"/><path d="M19.4 15A1.66 1.66 0 0 0 20 13.7 1.67 1.67 0 0 0 19.4 12.4L21 10.6 19.4 8.8 17.5 9.1A1.67 1.67 0 0 0 16 8 1.67 1.67 0 0 0 14.5 9.1L12.6 8.8 11 10.6 12.6 12.4A1.67 1.67 0 0 0 12 13.7 1.67 1.67 0 0 0 12.5 15L11 16.9 12.6 18.7 14.5 18.4A1.67 1.67 0 0 0 16 20 1.67 1.67 0 0 0 17.5 18.9L19.4 19.2 21 17.4 19.4 15Z" stroke="{color}" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>''',
        'grid': f'''<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><rect x="4" y="4" width="6" height="6" rx="1.5" fill="{color}" fill-opacity="0.16" stroke="{color}" stroke-width="1.8"/><rect x="14" y="4" width="6" height="6" rx="1.5" fill="{color}" fill-opacity="0.08" stroke="{color}" stroke-width="1.8"/><rect x="4" y="14" width="6" height="6" rx="1.5" fill="{color}" fill-opacity="0.08" stroke="{color}" stroke-width="1.8"/><rect x="14" y="14" width="6" height="6" rx="1.5" fill="{color}" fill-opacity="0.16" stroke="{color}" stroke-width="1.8"/></svg>''',
        'upload': f'''<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M12 3V15" stroke="{color}" stroke-width="1.8" stroke-linecap="round"/><path d="M8 7L12 3L16 7" stroke="{color}" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/><path d="M6 21H18" stroke="{color}" stroke-width="1.8" stroke-linecap="round"/></svg>''',
    }
    return icons.get(name, '')


@st.cache_data

def load_all_programs():
    """Carga todos los programas desde la carpeta de entrada.
    
    Returns:
        programs: lista de programas cargados exitosamente
        failed_files: lista de archivos que fallaron con {nombre, causa}
    """
    input_folder = Path(INPUT_FOLDER)
    excel_files = list(input_folder.glob('*.xlsx'))

    if not excel_files:
        return [], []

    programs = []
    failed_files = []
    detector = ThematicDetector()

    for file_path in excel_files:
        # Extraer modalidad y sede del nombre del archivo
        metadata = extract_modality_sede(file_path.name)
        
        try:
            extractor = ExcelExtractor(str(file_path))
            data = extractor.extract_all()
            analyzer = CurricularAnalyzer(data)
            indicadores = analyzer.generar_reporte_indicadores()
            tematicas = detector.analyze_programa(data)
            
            # ... (rest of existing code)
            
            # Calcular creditos totales del programa
            creditos_total = 0.0
            estrategias = data.get('estrategias_micro')
            if estrategias is not None and len(estrategias) > 0:
                # Buscar columnas
                semestre_col = None
                creditos_col = None
                nombre_col = None
                for col in estrategias.columns:
                    if 'Semestre' in col:
                        semestre_col = col
                    if 'Creditos' in col or ('Cr' in col and 'ditos' in col):
                        creditos_col = col
                    if 'Nombre' in col and 'asignatura' in col.lower():
                        nombre_col = col
                
                # Primero: buscar fila con "Total" in Semestre
                if semestre_col and creditos_col:
                    try:
                        filas_total = estrategias[estrategias[semestre_col].astype(str).str.contains('Total', na=False)]
                        if len(filas_total) > 0:
                            creditos_total = float(pd.to_numeric(filas_total[creditos_col].iloc[0], errors='coerce') or 0)
                        # Si no hay fila Total, calcular suma de creditos por asignatura
                        elif nombre_col:
                            creditos_unicos = estrategias.groupby(nombre_col)[creditos_col].first()
                            creditos_validos = pd.to_numeric(creditos_unicos, errors='coerce')
                            # Sin filtro de exclusión: todos los créditos válidos se suman
                            creditos_validos = creditos_validos[creditos_validos > 0]
                            creditos_total = float(creditos_validos.sum() or 0)
                    except Exception:
                        creditos_total = 0.0
            
            programs.append({
                'nombre': data['metadata']['programa'],
                'archivo': file_path.name,
                'modalidad': metadata['modalidad'],
                'sede': metadata['sede'],
                'codigo': metadata['codigo'],
                'data': data,
                'indicadores': indicadores,
                'tematicas': tematicas,
                'creditos_total': creditos_total
            })
        except Exception as e:
            error_msg = str(e)
            # Limpiar mensaje de error para mostrar
            if 'multiple' in error_msg.lower() or 'found' in error_msg.lower():
                causa = "Hoja no encontrada o formato inválido"
            elif 'empty' in error_msg.lower():
                causa = "Archivo vacío o sin datos"
            elif 'permission' in error_msg.lower():
                causa = "Archivo en uso por otra aplicación"
            else:
                causa = error_msg[:80] if len(error_msg) > 80 else error_msg
            
            failed_files.append({
                'nombre': file_path.name,
                'causa': causa
            })

    return programs, failed_files


def extract_modality_sede(filename):
    """Extrae modalidad y sede del nombre del archivo.
    
    Args:
        filename: nombre del archivo (ej: FormatoRA_AdmonEmpresas_PBOG.xlsx)
    
    Returns:
        dict: {modalidad, sede, codigo}
    """
    # Extraer últimos 4 caracteres antes de .xlsx
    base_name = filename.replace('.xlsx', '').replace('.xls', '')
    codigo = base_name[-4:] if len(base_name) >= 4 else ""
    
    # Mapas de códigos
    sede_map = {
        'PBOG': 'Bogotá',
        'PMED': 'Medellín',
        'VNAL': 'Nacional',
        'HBOG': 'Bogotá',
        'HMED': 'Medellín',
        'HVAL': 'Virtual',
    }
    
    modalidad_map = {
        'P': 'Presencial',
        'V': 'Virtual',
    }
    
    # Parsear código (ej: PBOG -> P + BOG)
    modalidad_codigo = codigo[0] if codigo else ""
    sede_codigo = codigo[1:] if len(codigo) > 1 else ""
    
    modalidad = modalidad_map.get(modalidad_codigo, 'No identificado')
    sede = sede_map.get(codigo, sede_codigo if sede_codigo else 'No identificado')
    
    return {
        'modalidad': modalidad,
        'sede': sede,
        'codigo': codigo
    }


def main():
    """Función principal del dashboard."""

    # Sidebar
    st.sidebar.title("📚 Navegación")

    # Cargar programas
    with st.spinner("Cargando datos..."):
        programs, failed_files = load_all_programs()

    # Mostrar mensaje de carga Y ERRORES PRIMERO (siempre visible)
    total_en_carpeta = len(programs) + len(failed_files)
    
    # Mensaje de resumen
    if total_en_carpeta > 0:
        st.info(f"📂 Archivos en carpeta: **{total_en_carpeta}** | ✅ Cargados: **{len(programs)}** | ❌ Error: **{len(failed_files)}**")
        
    #SIEMPRE mostrar lista de archivos (para verificar qué se detectó)
    all_files = list(Path(INPUT_FOLDER).glob('*.xlsx'))
    st.caption(f"DEBUG: Archivos encontrados en carpeta = {[f.name for f in all_files]}")
    
    # Siempre mostrar errores si existen
    if failed_files:
        st.markdown("### ⚠️ Archivos con errores:")
        for f in failed_files:
            st.warning(f"❌ **{f['nombre']}**: {f['causa']}")
    elif len(all_files) > len(programs):
        st.markdown("### ⚠️ Archivos que no se cargaron (posibles errores):")
        loaded_names = [p['archivo'] for p in programs]
        for f in all_files:
            if f.name not in loaded_names:
                st.warning(f"❌ **{f.name}**: (causa no detectada - revisar formato)")
        
    if not programs:
        st.error(f"❌ No se encontraron archivos para procesar en: {INPUT_FOLDER}")
        st.info(f"Coloca archivos Excel en la carpeta '{INPUT_FOLDER}' y recarga la página.")
        return

    # Menú de navegación
    page = st.sidebar.radio(
        "Ir a:",
        ["🏠 Inicio", "📊 Programas", "🏷️ Temáticas", "📈 Comparativa", "📋 Estrategias Micro"]
    )

    # ========================================================================
    # FILTROS DE MODALIDAD Y SEDE
    # ========================================================================
    st.sidebar.markdown("---")
    st.sidebar.subheader("🔍 Filtros")
    
    # Obtener valores únicos
    modalidades = sorted(list(set(p['modalidad'] for p in programs)))
    sedes = sorted(list(set(p['sede'] for p in programs)))
    
    # Agregar opción "Todos"
    modalidad_sel = st.sidebar.selectbox(
        "Modalidad",
        ["Todos"] + modalidades
    )
    
    sede_sel = st.sidebar.selectbox(
        "Sede",
        ["Todos"] + sedes
    )
    
    # Aplicar filtros
    filtered_programs = programs
    if modalidad_sel != "Todos":
        filtered_programs = [p for p in filtered_programs if p['modalidad'] == modalidad_sel]
    if sede_sel != "Todos":
        filtered_programs = [p for p in filtered_programs if p['sede'] == sede_sel]
    
    # Indicador de filtros activos
    if modalidad_sel != "Todos" or sede_sel != "Todos":
        st.sidebar.info(f"📊 Mostrando {len(filtered_programs)} de {len(programs)} programas")

    # ========================================================================
    # PÁGINA: INICIO
    # ========================================================================
    if page == "🏠 Inicio":
        st.markdown("""
        <div style="margin-bottom:30px;">
            <div style="display:flex; flex-wrap:wrap; gap:28px; align-items:flex-start;">
                <div style="flex:1; min-width:320px; max-width:720px;">
                    <div style="font-size:3.2rem; font-weight:700; line-height:1.02; color:#0f3460; margin-bottom:14px;">Análisis Microcurricular Basado en Datos</div>
                    <div style="font-size:1.05rem; color:#475569; max-width:740px; line-height:1.75;">
                        Optimice los procesos de diseño, actualización y evaluación curricular mediante el uso de analítica avanzada e Inteligencia Artificial, permitiendo identificar brechas, tendencias, niveles de alineación y oportunidades de mejora en tiempo real para fortalecer la toma de decisiones académicas y la calidad educativa.
                    </div>
                </div>
                <div style="flex:0 0 380px; min-width:300px;">
                    <div class="hero-action">
                        <div style="display:flex; align-items:center; gap:14px; margin-bottom:16px;">
                            <div style="width:44px; height:44px; border-radius:14px; display:flex; align-items:center; justify-content:center; background:#e0efff;">
                                {render_icon_svg('upload', '#0f3460', 24)}
                            </div>
                            <div>
                                <div style="font-size:1rem; font-weight:700; color:#0f3460; margin-bottom:4px;">Cargar Matriz de Resultados de aprendizaje</div>
                                <div style="font-size:0.92rem; color:#64748b; line-height:1.5;">Inicie el análisis masivo de su archivo (.XLSX) para obtener métricas instantáneas.</div>
                            </div>
                        </div>
                        <div class="action-box">
                            <div style="font-size:2.2rem;">{render_icon_svg('document', '#0f3460', 40)}</div>
                            <div style="font-weight:700;">Arrastre archivos aquí</div>
                            <div style="color:#64748b;">200MB por archivo · XLSX</div>
                        </div>
                        <div class="cta-row">
                            <div class="cta-button">Seleccionar Archivos</div>
                            <div class="cta-button">Ver guía de carga</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <div class="feature-grid" style="margin-bottom:34px;">
            <div class="feature-card">
                <div>{render_icon_svg('document', '#0f3460', 28)}</div>
                <h3>Resumen Ejecutivo</h3>
                <p>Visión general del estado de la Matriz de RA y cumplimiento de metas institucionales.</p>
            </div>
            <div class="feature-card">
                <div>{render_icon_svg('trend', '#0f3460', 28)}</div>
                <h3>Tendencias Globales</h3>
                <p>Comparativa con estándares internacionales y temáticas emergentes en la industria.</p>
            </div>
            <div class="feature-card">
                <div>{render_icon_svg('bloom', '#0f3460', 28)}</div>
                <h3>Bloom e Integración</h3>
                <p>Niveles taxonómicos detectados en las competencias y resultados de aprendizaje.</p>
            </div>
            <div class="feature-card">
                <div>{render_icon_svg('search', '#0f3460', 28)}</div>
                <h3>Minería de Texto</h3>
                <p>Descubrimiento de patrones y nubes de palabras clave en el contenido curricular.</p>
            </div>
            <div class="feature-card">
                <div>{render_icon_svg('grid', '#0f3460', 28)}</div>
                <h3>Tipo de Saber</h3>
                <p>Análisis de la balanza entre saber, saber hacer y saber ser en los programas.</p>
            </div>
            <div class="feature-card">
                <div>{render_icon_svg('gear', '#0f3460', 28)}</div>
                <h3>Cobertura Temática</h3>
                <p>Detección de redundancias o vacíos temáticos en la malla curricular institucional.</p>
            </div>
        </div>

        <div class="content-block">
            <div>
                <h2 style="font-size:1.5rem; color:#0f3460; margin-bottom:12px;">Cómo empezar</h2>
                <ul class="steps-list">
                    <li><strong>1.</strong> Suba uno o más archivos Excel (.xlsx) en la carpeta de entrada.</li>
                    <li><strong>2.</strong> Los archivos deben contener la hoja "Paso 5 Estrategias micro" con encabezados en la fila 2.</li>
                    <li><strong>3.</strong> El análisis se ejecuta automáticamente al cargar los archivos.</li>
                    <li><strong>4.</strong> Navegue por las secciones usando el menú lateral.</li>
                    <li><strong>5.</strong> Puede cargar varios programas a la vez para análisis comparativos.</li>
                </ul>
            </div>
            <div class="table-card">
                <h2 style="font-size:1.25rem; color:#0f3460; margin-bottom:14px;">Estructura esperada del Excel</h2>
                <table class="structured-table">
                    <thead>
                        <tr>
                            <th>Columna</th>
                            <th>Descripción</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr><td>Tipo de Saber</td><td>Saber / SaberHacer / SaberSer</td></tr>
                        <tr><td>Resultado de aprendizaje</td><td>Texto del resultado de aprendizaje (verbo de acción)</td></tr>
                        <tr><td>Nombre asignatura o módulo</td><td>Nombre de la asignatura o módulo</td></tr>
                        <tr><td>Indicadores de logro</td><td>Indicadores de evaluación del RA</td></tr>
                        <tr><td>Núcleos temáticos</td><td>Temas separados por coma o punto y coma</td></tr>
                        <tr><td>Semestre</td><td>Número de semestre (1, 2, 3,...)</td></tr>
                        <tr><td>Créditos</td><td>Créditos académicos de la asignatura</td></tr>
                    </tbody>
                </table>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ========================================================================
    # PÁGINA: PROGRAMAS
    # ========================================================================
    elif page == "📊 Programas":
        st.title("📊 Análisis por Programa")
        st.markdown("---")

        # Selector de programa
        program_names = [p['nombre'] for p in filtered_programs]
        if not program_names:
            st.warning("No hay programas que coincidan con los filtros seleccionados.")
            return
            
        selected_program_name = st.selectbox(
            "Seleccionar programa:",
            program_names
        )

        # Obtener programa seleccionado
        selected_program = next(p for p in filtered_programs if p['nombre'] == selected_program_name)
        ind = selected_program['indicadores']

        # Score de calidad
        st.subheader(f"🎯 Score de Calidad: {ind['score_calidad']}/100")

        # Métricas
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Competencias", ind['resumen']['total_competencias'])

        with col2:
            st.metric("Resultados de Aprendizaje", ind['resumen']['total_ra'])

        with col3:
            st.metric("Completitud", f"{ind['completitud']['completitud_total']:.1f}%")

        st.markdown("---")

        # Balance de tipos de saber
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("📚 Balance de Tipos de Saber")

            df_saber = pd.DataFrame([
                {'Tipo': 'Saber', 'Porcentaje': ind['balance_tipo_saber']['Saber']},
                {'Tipo': 'SaberHacer', 'Porcentaje': ind['balance_tipo_saber']['SaberHacer']},
                {'Tipo': 'SaberSer', 'Porcentaje': ind['balance_tipo_saber']['SaberSer']}
            ])

            fig_saber = px.pie(
                df_saber,
                values='Porcentaje',
                names='Tipo',
                title='Distribución de Tipos de Saber',
                color_discrete_sequence=['#1f77b4', '#ff7f0e', '#2ca02c']
            )
            st.plotly_chart(fig_saber, use_container_width=True)

        with col2:
            st.subheader("🧠 Complejidad Cognitiva")

            df_complejidad = pd.DataFrame([
                {'Nivel': 'Básico', 'Porcentaje': ind['complejidad_cognitiva']['Básico']},
                {'Nivel': 'Intermedio', 'Porcentaje': ind['complejidad_cognitiva']['Intermedio']},
                {'Nivel': 'Avanzado', 'Porcentaje': ind['complejidad_cognitiva']['Avanzado']}
            ])

            fig_complejidad = px.pie(
                df_complejidad,
                values='Porcentaje',
                names='Nivel',
                title='Niveles de Complejidad (Bloom)',
                color_discrete_sequence=['#d62728', '#ff7f0e', '#2ca02c']
            )
            st.plotly_chart(fig_complejidad, use_container_width=True)

        # Temáticas detectadas
        st.markdown("---")
        st.subheader("🏷️ Temáticas Detectadas")

        tematicas_presentes = selected_program['tematicas']['tematicas_presentes']

        if tematicas_presentes:
            cols = st.columns(3)
            for idx, tematica in enumerate(tematicas_presentes):
                col_idx = idx % 3
                with cols[col_idx]:
                    st.success(f"✅ {tematica}")
        else:
            st.info("No se detectaron temáticas específicas")

        # Tabla de competencias
        st.markdown("---")
        st.subheader("📋 Competencias del Programa")

        df_comp = selected_program['data']['competencias']
        if not df_comp.empty:
            st.dataframe(
                df_comp[['No.', 'Redacción competencia', 'Tipo de competencia']],
                use_container_width=True,
                hide_index=True
            )

    # ========================================================================
    # PÁGINA: TEMÁTICAS
    # ========================================================================
    elif page == "🏷️ Temáticas":
        st.title("🏷️ Análisis de Temáticas")
        st.markdown("---")

        # Selector de temática
        tematica_seleccionada = st.selectbox(
            "Seleccionar temática:",
            list(TEMATICAS.keys())
        )

        # Filtrar programas con esa temática
        programas_con_tematica = [
            p for p in filtered_programs
            if tematica_seleccionada in p['tematicas']['tematicas_presentes']
        ]

        st.subheader(f"Programas que abordan: {tematica_seleccionada}")
        st.metric(
            "Total de programas",
            f"{len(programas_con_tematica)} de {len(filtered_programs)}"
        )

        if programas_con_tematica:
            # Tabla de programas
            datos_tabla = []
            for p in programas_con_tematica:
                resumen = p['tematicas']['resumen'][tematica_seleccionada]
                datos_tabla.append({
                    'Programa': p['nombre'],
                    'En Competencias': resumen['frecuencia_competencias'],
                    'En RA': resumen['frecuencia_ra'],
                    'Total': resumen['total_coincidencias']
                })

            df_tabla = pd.DataFrame(datos_tabla).sort_values('Total', ascending=False)
            st.dataframe(df_tabla, use_container_width=True, hide_index=True)

        else:
            st.info(f"Ningún programa aborda {tematica_seleccionada}")

    # ========================================================================
    # PÁGINA: COMPARATIVA
    # ========================================================================
    elif page == "📈 Comparativa":
        st.title("📈 Comparativa de Programas")
        st.markdown("---")
        st.info(
            "Compara los programas académicos en indicadores de calidad, créditos, "
            "competencias y temáticas. Usa las pestañas para comparar dos programas "
            "específicos o ver una visión general de todos los programas cargados."
        )

        tab_dos, tab_todos = st.tabs([
            "🔀 Comparar 2 Programas",
            "📊 Vista General — Todos los Programas"
        ])

        # ── TAB 1: Comparar 2 Programas ──────────────────────────────────────
        with tab_dos:
            program_names = [p['nombre'] for p in filtered_programs]
            
            if len(program_names) < 2:
                st.warning("Se necesitan al menos 2 programas para comparar. Selecciona más programas en los filtros.")
                return
            
            prog1_name = st.selectbox(
                "Programa 1:",
                program_names,
                index=0 if len(program_names) > 0 else 0
            )

            prog2_name = st.selectbox(
                "Programa 2:",
                program_names,
                index=1 if len(program_names) > 1 else 0
            )

            # Obtener programas
            prog1 = next((p for p in filtered_programs if p['nombre'] == prog1_name), None)
            prog2 = next((p for p in filtered_programs if p['nombre'] == prog2_name), None)

            if prog1 is None or prog2 is None:
                st.error("Error al cargar los programas.")
            else:
                    # Radar chart
                    st.subheader("🕸️ Perfil de Indicadores")
                    st.caption(
                        "El gráfico de radar muestra el perfil de cada programa en 5 dimensiones. "
                        "El área cubierta refleja la fortaleza global del programa."
                    )
                    categories = ['Score Calidad', 'Completitud', 'Índice Complejidad',
                                  'Cobertura Comp.', 'Diversidad Met.']
                    fig_radar = go.Figure()
                    for prog in [prog1, prog2]:
                        ind = prog.get('indicadores', {})
                        values = [
                            ind.get('score_calidad', 0),
                            ind.get('completitud', {}).get('completitud_total', 0),
                            ind.get('complejidad_cognitiva', {}).get('indice_complejidad', 0),
                            ind.get('cobertura_competencias', {}).get('porcentaje_cobertura', 0),
                            min(100, ind.get('diversidad_metodologica', {}).get('num_estrategias_unicas', 0) * 8)
                        ]
                        fig_radar.add_trace(go.Scatterpolar(
                            r=values, theta=categories,
                            fill='toself', name=prog.get('nombre', '')
                        ))
                    fig_radar.update_layout(
                        polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
                        showlegend=True, height=500
                    )
                    st.plotly_chart(fig_radar, use_container_width=True)

                    # Tabla comparativa
                    st.markdown("---")
                    st.subheader("📊 Tabla Comparativa")
                    datos_comparativa = []
                    for prog in [prog1, prog2]:
                        ind = prog.get('indicadores', {})
                        datos_comparativa.append({
                            'Programa': prog.get('nombre', ''),
                            'Score Calidad': ind.get('score_calidad', 0),
                            'Competencias': ind.get('resumen', {}).get('total_competencias', 0),
                            'RA (Asignaturas)': ind.get('resumen', {}).get('total_ra', 0),
                            'Créditos': int(prog.get('creditos_total', 0)),
                            'Completitud %': round(ind.get('completitud', {}).get('completitud_total', 0), 1),
                            'Complejidad Avanzado %': round(ind.get('complejidad_cognitiva', {}).get('Avanzado', 0), 1),
                            'N° Temáticas': prog.get('tematicas', {}).get('num_tematicas', 0)
                        })
                    df_comp2 = pd.DataFrame(datos_comparativa)
                    st.dataframe(df_comp2, use_container_width=True, hide_index=True)

                    cred1 = prog1.get('creditos_total', 0)
                    cred2 = prog2.get('creditos_total', 0)
                    diff = abs(cred1 - cred2)
                    diff_pct = (diff / max(cred1, cred2) * 100) if max(cred1, cred2) > 0 else 0
                    if cred1 == cred2:
                        st.success(f"✅ Ambos programas tienen **{int(cred1)}** créditos.")
                    else:
                        st.warning(
                            f"⚠️ Diferencia de créditos: **{prog1_name}** tiene {int(cred1)} "
                            f"y **{prog2_name}** tiene {int(cred2)} ({diff_pct:.1f}% de diferencia)."
                        )

                    # Comparativa de Temáticas
                    st.markdown("---")
                    st.subheader("🏷️ Comparativa de Temáticas Detectadas")
                    st.caption("Número de asignaturas por programa que abordan cada temática.")
                    datos_tematicas = []
                    for prog in [prog1, prog2]:
                        tematicas = prog['tematicas']
                        row = {'Programa': prog['nombre']}
                        for tema, datos in tematicas['resumen'].items():
                            row[tema] = datos.get('asignaturas_con_tematica', 0) if datos.get('presente') else 0
                        datos_tematicas.append(row)
                    df_tem2 = pd.DataFrame(datos_tematicas).fillna(0)
                    st.dataframe(df_tem2, use_container_width=True, hide_index=True)

                    # Similitud entre los dos programas
                    st.markdown("---")
                    st.subheader("🔗 Similitud de Contenidos entre Programas")
                    st.caption(
                        "Mide qué tan parecidos son los textos de estrategias de los dos programas "
                        "usando TF-IDF y similitud coseno. Alta similitud puede indicar contenidos compartidos."
                    )
                    try:
                        from sklearn.feature_extraction.text import TfidfVectorizer
                        from sklearn.metrics.pairwise import cosine_similarity
                        from pathlib import Path as PathLib

                        input_folder = PathLib(INPUT_FOLDER)
                        similitud_data = []
                        for prog in [prog1, prog2]:
                            for f in input_folder.glob('*.xlsx'):
                                if prog['nombre'] in f.name:
                                    extractor_s = ExcelExtractor(str(f))
                                    data_s = extractor_s.extract_all()
                                    estr_s = data_s.get('estrategias_micro')
                                    if estr_s is not None and len(estr_s) > 0:
                                        textos = []
                                        for _, row in estr_s.iterrows():
                                            texto = ''
                                            for col in ['Actividades de aprendizaje', 'Actividades de evaluacion', 'Nucleos tematicos']:
                                                if col in estr_s.columns and pd.notna(row.get(col)):
                                                    texto += ' ' + str(row.get(col))
                                            if texto.strip():
                                                textos.append(texto)
                                        similitud_data.append(' '.join(textos))
                                    break

                        if len(similitud_data) == 2:
                            vectorizer = TfidfVectorizer(max_features=100, stop_words='spanish')
                            tfidf = vectorizer.fit_transform(similitud_data)
                            sim_matrix = cosine_similarity(tfidf)
                            similitud = float(sim_matrix[0][1])
                            feature_names = vectorizer.get_feature_names_out()
                            tfidf_dense = tfidf.toarray()
                            comun = tfidf_dense[0] * tfidf_dense[1]
                            top_common = [str(feature_names[i]) for i in range(len(comun)) if comun[i] > 0]

                            col1, col2 = st.columns(2)
                            col1.metric("Similitud de contenidos (TF-IDF)", f"{similitud:.1%}",
                                        help="1.0 = idénticos, 0.0 = completamente distintos")
                            col2.metric("Términos en común", str(len(top_common)),
                                        help="Número de términos con peso positivo en ambos programas")
                    except Exception as e:
                        st.warning(f"No se pudo calcular similitud: {e}")

                    # Estrategias pedagógicas
                    st.markdown("#### Comparación de Estrategias Pedagógicas")
                    st.caption("Frecuencia de palabras clave de metodologías activas en las actividades de aprendizaje.")
                    datos_estrategias = []
                    try:
                        for prog in [prog1, prog2]:
                            for f in input_folder.glob('*.xlsx'):
                                if prog['nombre'] in f.name:
                                    ext2 = ExcelExtractor(str(f))
                                    d2 = ext2.extract_all()
                                    estr2 = d2['estrategias_micro']
                                    kws = ['taller', 'caso', 'problema', 'proyecto', 'laboratorio',
                                           'lectura', 'exposición', 'debate', 'simulación', 'ejercicio']
                                    texto2 = ' '.join(estr2['Actividades de aprendizaje'].dropna().str.lower())
                                    for kw in kws:
                                        datos_estrategias.append({
                                            'Programa': prog['nombre'],
                                            'Estrategia': kw.title(),
                                            'Cantidad': texto2.count(kw)
                                        })
                                    break
                    except Exception:
                        pass
                    if datos_estrategias:
                        df_estr = pd.DataFrame(datos_estrategias)
                        fig_estr = px.bar(
                            df_estr, x='Estrategia', y='Cantidad', color='Programa',
                            barmode='group', title='Frecuencia de Estrategias Pedagógicas',
                            color_discrete_sequence=['#1f77b4', '#ff7f0e']
                        )
                        fig_estr.update_layout(height=400)
                        st.plotly_chart(fig_estr, use_container_width=True)

        # ── TAB 2: Vista General de Todos los Programas ───────────────────────
        with tab_todos:
            st.subheader("Panorama General de Todos los Programas")
            st.caption(
                "Visión consolidada de los indicadores de calidad para todos los programas "
                "cargados. Permite identificar cuáles requieren mayor atención y cuáles "
                "son referentes de buenas prácticas."
            )

            # ── Tabla resumen completa ──────────────────────────────────────
            st.markdown("#### 📋 Tabla Resumen de Indicadores")
            datos_todos = []
            for prog in programs:
                ind = prog.get('indicadores', {})
                datos_todos.append({
                    'Programa': prog.get('nombre', ''),
                    'Score Calidad': ind.get('score_calidad', 0),
                    'Créditos': int(prog.get('creditos_total', 0)),
                    'Competencias': ind.get('resumen', {}).get('total_competencias', 0),
                    'RA': ind.get('resumen', {}).get('total_ra', 0),
                    'Completitud %': round(ind.get('completitud', {}).get('completitud_total', 0), 1),
                    'Complejidad Avanzado %': round(ind.get('complejidad_cognitiva', {}).get('Avanzado', 0), 1),
                    'N° Temáticas': prog.get('tematicas', {}).get('num_tematicas', 0),
                    'SaberHacer %': round(ind.get('balance_tipo_saber', {}).get('SaberHacer', 0), 1),
                    'SaberSer %': round(ind.get('balance_tipo_saber', {}).get('SaberSer', 0), 1),
                })
            df_todos = pd.DataFrame(datos_todos).sort_values('Score Calidad', ascending=False)

            # Semáforo de score
            def color_score(val):
                if isinstance(val, (int, float)):
                    if val >= 75:
                        return 'background-color: #d4edda; color: #155724'
                    elif val >= 50:
                        return 'background-color: #fff3cd; color: #856404'
                    else:
                        return 'background-color: #f8d7da; color: #721c24'
                return ''

            st.dataframe(
                df_todos.style.applymap(color_score, subset=['Score Calidad']),
                use_container_width=True, hide_index=True
            )
            st.caption("🟢 Score ≥ 75 (bueno) · 🟡 50–74 (mejorable) · 🔴 < 50 (requiere atención)")

            # ── Radar comparativo todos los programas ───────────────────────
            st.markdown("---")
            st.subheader("🕸️ Radar Comparativo — Todos los Programas")
            st.caption(
                "Superpone el perfil de todos los programas. Permite identificar fortalezas "
                "y debilidades relativas de cada uno en las mismas dimensiones."
            )
            categories_all = ['Score Calidad', 'Completitud', 'Índice Complejidad',
                               'Cobertura Comp.', 'Diversidad Met.']
            fig_radar_all = go.Figure()
            for prog in programs:
                ind = prog.get('indicadores', {})
                values = [
                    ind.get('score_calidad', 0),
                    ind.get('completitud', {}).get('completitud_total', 0),
                    ind.get('complejidad_cognitiva', {}).get('indice_complejidad', 0),
                    ind.get('cobertura_competencias', {}).get('porcentaje_cobertura', 0),
                    min(100, ind.get('diversidad_metodologica', {}).get('num_estrategias_unicas', 0) * 8)
                ]
                fig_radar_all.add_trace(go.Scatterpolar(
                    r=values, theta=categories_all,
                    fill='toself', name=prog.get('nombre', ''), opacity=0.7
                ))
            fig_radar_all.update_layout(
                polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
                showlegend=True, height=550
            )
            st.plotly_chart(fig_radar_all, use_container_width=True)

            # ── Ranking de scores ───────────────────────────────────────────
            st.markdown("---")
            col_rank1, col_rank2 = st.columns(2)

            with col_rank1:
                st.subheader("🏆 Ranking por Score de Calidad")
                df_rank = df_todos[['Programa', 'Score Calidad']].sort_values(
                    'Score Calidad', ascending=True
                )
                fig_rank = px.bar(
                    df_rank, y='Programa', x='Score Calidad',
                    orientation='h', color='Score Calidad',
                    color_continuous_scale='RdYlGn', range_color=[0, 100],
                    text='Score Calidad',
                    labels={'Score Calidad': 'Score (/100)'}
                )
                fig_rank.update_traces(texttemplate='%{text:.0f}', textposition='outside')
                fig_rank.update_layout(height=400, xaxis_range=[0, 110])
                st.plotly_chart(fig_rank, use_container_width=True)

            with col_rank2:
                st.subheader("🎓 Créditos por Programa")
                df_cred = df_todos[['Programa', 'Créditos']].sort_values(
                    'Créditos', ascending=True
                )
                fig_cred = px.bar(
                    df_cred, y='Programa', x='Créditos',
                    orientation='h', color='Créditos',
                    color_continuous_scale='Blues', text='Créditos',
                    labels={'Créditos': 'Total Créditos'}
                )
                fig_cred.update_traces(texttemplate='%{text}', textposition='outside')
                fig_cred.update_layout(height=400)
                st.plotly_chart(fig_cred, use_container_width=True)

            # ── Tipo de Saber consolidado ───────────────────────────────────
            st.markdown("---")
            st.subheader("📚 Tipo de Saber por Programa")
            st.caption(
                "Distribución de Saber, SaberHacer y SaberSer en cada programa. "
                "Referencia: SaberHacer ≥ 40%, SaberSer ≥ 10%."
            )
            datos_saber_todos = []
            for prog in programs:
                ind = prog.get('indicadores', {})
                balance = ind.get('balance_tipo_saber', {})
                for tipo in ['Saber', 'SaberHacer', 'SaberSer']:
                    datos_saber_todos.append({
                        'Programa': prog.get('nombre', ''),
                        'Tipo': tipo,
                        'Porcentaje': round(balance.get(tipo, 0), 1)
                    })
            df_saber_todos = pd.DataFrame(datos_saber_todos)
            if not df_saber_todos.empty:
                fig_saber_todos = px.bar(
                    df_saber_todos, x='Programa', y='Porcentaje', color='Tipo',
                    barmode='stack',
                    color_discrete_map={
                        'Saber': '#3498DB',
                        'SaberHacer': '#E67E22',
                        'SaberSer': '#8E44AD'
                    },
                    text='Porcentaje',
                    labels={'Porcentaje': '%'}
                )
                fig_saber_todos.update_traces(texttemplate='%{text:.0f}%', textposition='inside')
                fig_saber_todos.add_hline(
                    y=40, line_dash='dot', line_color='gray', opacity=0.5,
                    annotation_text='Ref. 40%', annotation_position='top right'
                )
                fig_saber_todos.update_layout(height=400, yaxis_title='Porcentaje (%)')
                st.plotly_chart(fig_saber_todos, use_container_width=True)

            # ── Temáticas de todos los programas ───────────────────────────
            st.markdown("---")
            st.subheader("🏷️ Temáticas Detectadas — Todos los Programas")
            st.caption(
                "Número de asignaturas por programa que abordan cada temática. "
                "Celdas vacías (0) indican que el programa no cubre esa temática."
            )
            datos_tem_todos = []
            for prog in programs:
                row_t = {'Programa': prog.get('nombre', '')}
                temas = prog.get('tematicas', {}).get('resumen', {})
                for tema, datos in temas.items():
                    row_t[tema] = datos.get('asignaturas_con_tematica', 0) if datos.get('presente') else 0
                datos_tem_todos.append(row_t)
            df_tem_todos = pd.DataFrame(datos_tem_todos).fillna(0)
            st.dataframe(df_tem_todos, use_container_width=True, hide_index=True)

            # ── Alertas de calidad ──────────────────────────────────────────
            st.markdown("---")
            st.subheader("🚦 Alertas de Calidad")
            st.caption("Programas que requieren atención según umbrales de referencia.")
            alertas = []
            for prog in programs:
                ind = prog.get('indicadores', {})
                nombre = prog.get('nombre', '')
                score = ind.get('score_calidad', 0)
                completitud = ind.get('completitud', {}).get('completitud_total', 0)
                saber_ser = ind.get('balance_tipo_saber', {}).get('SaberSer', 0)
                avanzado = ind.get('complejidad_cognitiva', {}).get('Avanzado', 0)
                creditos = int(prog.get('creditos_total', 0))

                if score < 50:
                    alertas.append({'Programa': nombre, 'Alerta': f'⚠️ Score de calidad bajo ({score:.0f}/100)', 'Prioridad': 'Alta'})
                if completitud < 70:
                    alertas.append({'Programa': nombre, 'Alerta': f'📋 Completitud baja ({completitud:.0f}%) — revisa campos vacíos en el microcurrículo', 'Prioridad': 'Media'})
                if saber_ser < 8:
                    alertas.append({'Programa': nombre, 'Alerta': f'🟣 SaberSer muy bajo ({saber_ser:.1f}%) — poca formación en valores/actitudes', 'Prioridad': 'Media'})
                if avanzado < 15:
                    alertas.append({'Programa': nombre, 'Alerta': f'🧠 Pocos RA de nivel avanzado en Bloom ({avanzado:.1f}%) — predominio de niveles básicos', 'Prioridad': 'Baja'})
                if creditos == 0:
                    alertas.append({'Programa': nombre, 'Alerta': '💳 No se detectaron créditos — verifica la estructura del archivo', 'Prioridad': 'Alta'})

            if alertas:
                df_alertas = pd.DataFrame(alertas).sort_values(
                    'Prioridad', key=lambda x: x.map({'Alta': 0, 'Media': 1, 'Baja': 2})
                )
                st.dataframe(df_alertas, use_container_width=True, hide_index=True)
            else:
                st.success("✅ Todos los programas superan los umbrales de calidad definidos.")

    # ========================================================================
    # PÁGINA: ESTRATEGIAS MICRO
    # ========================================================================
    elif page == "📋 Estrategias Micro":
        st.title("📋 Análisis de Estrategias Microcurriculares")
        st.markdown("---")

        st.subheader("📊 Distribución Tipo de Saber por Programa")
        
        # Usar programas filtrados en lugar de recargar archivos
        datos_tipo_saber = []
        datos_tipologia = []
        datos_horas = []
        datos_estrategias = []
        
        for p in filtered_programs:
            try:
                estrategias_micro = p['data'].get('estrategias_micro')
                if estrategias_micro is None or estrategias_micro.empty:
                    continue
                    
                nombre_prog = p['nombre']
                modalidad = p.get('modalidad', '')
                sede = p.get('sede', '')
                
                if not estrategias_micro.empty:
                    # Tipo de Saber
                    tipo_saber_counts = estrategias_micro['Tipo de Saber'].value_counts()
                    for tipo, count in tipo_saber_counts.items():
                        if pd.notna(tipo):
                            datos_tipo_saber.append({
                                'Programa': f"{nombre_prog} ({modalidad} - {sede})",
                                'Tipo de Saber': tipo,
                                'Cantidad': count
                            })
                    
                    # Tipología (omitir vacíos)
                    tipologia = estrategias_micro['Tipología'].dropna()
                    if len(tipologia) > 0:
                        tipologia_counts = tipologia.value_counts()
                        for tipo, count in tipologia_counts.items():
                            datos_tipologia.append({
                                'Programa': nombre_prog,
                                'Tipología': tipo,
                                'Cantidad': count
                            })
                
                if not estrategias_micro.empty:
                    # Tipo de Saber
                    tipo_saber_counts = estrategias_micro['Tipo de Saber'].value_counts()
                    for tipo, count in tipo_saber_counts.items():
                        if pd.notna(tipo):
                            datos_tipo_saber.append({
                                'Programa': nombre_prog,
                                'Tipo de Saber': tipo,
                                'Cantidad': count
                            })
                    
                    # Tipología (omitir vacíos)
                    tipologia = estrategias_micro['Tipología'].dropna()
                    if len(tipologia) > 0:
                        tipologia_counts = tipologia.value_counts()
                        for tipo, count in tipologia_counts.items():
                            datos_tipologia.append({
                                'Programa': nombre_prog,
                                'Tipología': tipo,
                                'Cantidad': count
                            })
                    
                    # Horas
                    estrategias_micro['HorasDirectas'] = pd.to_numeric(
                        estrategias_micro['Número de horas trabajo directo'], errors='coerce'
                    )
                    estrategias_micro['HorasIndep'] = pd.to_numeric(
                        estrategias_micro['Número de horas trabajo independiente'], errors='coerce'
                    )
                    estrategias_micro['Creditos'] = pd.to_numeric(
                        estrategias_micro['Créditos'], errors='coerce'
                    )
                    
                    ht = estrategias_micro['HorasDirectas'].dropna()
                    hi = estrategias_micro['HorasIndep'].dropna()
                    cr = estrategias_micro['Creditos'].dropna()
                    
                    if len(ht) > 0 and len(hi) > 0:
                        datos_horas.append({
                            'Programa': nombre_prog,
                            'Horas Directas (Promedio)': ht.mean(),
                            'Horas Independientes (Promedio)': hi.mean(),
                            'Créditos (Promedio)': cr.mean() if len(cr) > 0 else 0,
                            'Ratio Indep/Directo': hi.mean() / ht.mean() if ht.mean() > 0 else 0
                        })
                    
                    # Estrategias de Aprendizaje - contar keywords
                    acts = estrategias_micro['Actividades de aprendizaje'].dropna().str.lower().str.cat(sep=' ')
                    
                    keywords_aprendizaje = [
                        'clase magistral', 'taller', 'laboratorio', 'caso', 'problema',
                        'proyecto', 'exposición', 'lectura', 'simulación', 'seminario',
                        'tutoría', 'investigación', 'debate', 'ejercicio', 'estudio'
                    ]
                    
                    for kw in keywords_aprendizaje:
                        count = acts.count(kw)
                        if count > 0:
                            datos_estrategias.append({
                                'Programa': nombre_prog,
                                'Estrategia': kw.title(),
                                'Cantidad': count
                            })
                            
            except Exception as e:
                st.warning(f"Error procesando {file_path.name}: {str(e)}")

        # 1. Gráfico Tipo de Saber por Programa
        if datos_tipo_saber:
            df_tipo_saber = pd.DataFrame(datos_tipo_saber)
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Barras agrupadas
                fig_saber_bar = px.bar(
                    df_tipo_saber,
                    x='Programa',
                    y='Cantidad',
                    color='Tipo de Saber',
                    title='Distribución Tipo de Saber por Programa',
                    barmode='group',
                    color_discrete_sequence=['#1f77b4', '#ff7f0e', '#2ca02c']
                )
                fig_saber_bar.update_layout(height=400)
                st.plotly_chart(fig_saber_bar, use_container_width=True)
            
            with col2:
                # Pie consolidado
                total_tipo = df_tipo_saber.groupby('Tipo de Saber')['Cantidad'].sum().reset_index()
                fig_saber_pie = px.pie(
                    total_tipo,
                    values='Cantidad',
                    names='Tipo de Saber',
                    title='Distribución Consolidada de Tipo de Saber',
                    color_discrete_sequence=['#1f77b4', '#ff7f0e', '#2ca02c']
                )
                st.plotly_chart(fig_saber_pie, use_container_width=True)
        
        st.markdown("---")
        
        # 2. Tipología por Programa
        st.subheader("🏷️ Tipología de Asignaturas por Programa (sin vacíos)")
        
        if datos_tipologia:
            df_tipologia = pd.DataFrame(datos_tipologia)
            
            col1, col2 = st.columns(2)
            
            with col1:
                fig_tipo_bar = px.bar(
                    df_tipologia,
                    x='Programa',
                    y='Cantidad',
                    color='Tipología',
                    title='Tipología por Programa',
                    barmode='group',
                    color_discrete_sequence=px.colors.qualitative.Set2
                )
                fig_tipo_bar.update_layout(height=400)
                st.plotly_chart(fig_tipo_bar, use_container_width=True)
            
            with col2:
                total_tipologia = df_tipologia.groupby('Tipología')['Cantidad'].sum().reset_index()
                fig_tipo_pie = px.pie(
                    total_tipologia,
                    values='Cantidad',
                    names='Tipología',
                    title='Distribución Consolidada de Tipología',
                    color_discrete_sequence=px.colors.qualitative.Set2
                )
                st.plotly_chart(fig_tipo_pie, use_container_width=True)
        else:
            st.info("No hay datos de tipología disponibles")
        
        st.markdown("---")
        
        # 3. Análisis de Horas
        st.subheader("⏰ Análisis de Horas de Trabajo")
        
        if datos_horas:
            df_horas = pd.DataFrame(datos_horas)
            
            col1, col2 = st.columns(2)
            
            with col1:
                fig_horas = px.bar(
                    df_horas,
                    x='Programa',
                    y=['Horas Directas (Promedio)', 'Horas Independientes (Promedio)'],
                    title='Horas Promedio por Programa',
                    barmode='group',
                    color_discrete_sequence=['#3498db', '#e74c3c']
                )
                fig_horas.update_layout(height=400)
                st.plotly_chart(fig_horas, use_container_width=True)
            
            with col2:
                fig_ratio = px.bar(
                    df_horas,
                    x='Programa',
                    y='Ratio Indep/Directo',
                    title='Ratio Trabajo Independiente / Directo',
                    color='Ratio Indep/Directo',
                    color_continuous_scale='RdYlGn'
                )
                fig_ratio.update_layout(height=400)
                st.plotly_chart(fig_ratio, use_container_width=True)
            
            # Tabla de horas
            st.subheader("📋 Detalle de Horas")
            st.dataframe(
                df_horas.style.format({
                    'Horas Directas (Promedio)': '{:.1f}',
                    'Horas Independientes (Promedio)': '{:.1f}',
                    'Créditos (Promedio)': '{:.1f}',
                    'Ratio Indep/Directo': '{:.2f}'
                }),
                use_container_width=True
            )
        else:
            st.info("No hay datos de horas disponibles")
        
        st.markdown("---")
        
        # 4. Estrategias de Aprendizaje - Frecuencia de Palabras
        st.subheader("📚 Frecuencia de Estrategias de Aprendizaje")
        
        if datos_estrategias:
            df_estrategias = pd.DataFrame(datos_estrategias)
            
            # Consolidado por estrategia
            estrategia_total = df_estrategias.groupby('Estrategia')['Cantidad'].sum().reset_index()
            estrategia_total = estrategia_total.sort_values('Cantidad', ascending=False)
            
            col1, col2 = st.columns(2)
            
            with col1:
                fig_estrategias_bar = px.bar(
                    estrategia_total.head(10),
                    x='Cantidad',
                    y='Estrategia',
                    orientation='h',
                    title='Top 10 Estrategias de Aprendizaje (Frecuencia Total)',
                    color='Cantidad',
                    color_continuous_scale='Blues'
                )
                fig_estrategias_bar.update_layout(height=400, showlegend=False)
                st.plotly_chart(fig_estrategias_bar, use_container_width=True)
            
            with col2:
                fig_estrategias_prog = px.sunburst(
                    df_estrategias,
                    path=['Programa', 'Estrategia'],
                    values='Cantidad',
                    title='Estrategias por Programa'
                )
                fig_estrategias_prog.update_layout(height=400)
                st.plotly_chart(fig_estrategias_prog, use_container_width=True)
            
            # Tabla detallada
            st.subheader("📋 Detalle de Estrategias por Programa")
            
            pivot_estrategias = df_estrategias.pivot_table(
                index='Programa',
                columns='Estrategia',
                values='Cantidad',
                fill_value=0,
                aggfunc='sum'
            ).reset_index()
            
            st.dataframe(pivot_estrategias, use_container_width=True)
        else:
            st.info("No hay datos de estrategias de aprendizaje disponibles")


if __name__ == '__main__':
    main()
