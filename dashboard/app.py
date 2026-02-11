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
    page_icon="🎓",
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
    </style>
""", unsafe_allow_html=True)


@st.cache_data
def load_all_programs():
    """Carga todos los programas desde la carpeta de entrada."""
    input_folder = Path(INPUT_FOLDER)
    excel_files = list(input_folder.glob('*.xlsx'))

    if not excel_files:
        return []

    programs = []
    detector = ThematicDetector()

    for file_path in excel_files:
        try:
            extractor = ExcelExtractor(str(file_path))
            data = extractor.extract_all()
            analyzer = CurricularAnalyzer(data)
            indicadores = analyzer.generar_reporte_indicadores()
            tematicas = detector.analyze_programa(data)

            programs.append({
                'nombre': data['metadata']['programa'],
                'data': data,
                'indicadores': indicadores,
                'tematicas': tematicas
            })
        except Exception as e:
            st.warning(f"Error cargando {file_path.name}: {str(e)}")

    return programs


def main():
    """Función principal del dashboard."""

    # Sidebar
    st.sidebar.title("📚 Navegación")

    # Cargar programas
    with st.spinner("Cargando datos..."):
        programs = load_all_programs()

    if not programs:
        st.error(f"❌ No se encontraron archivos en: {INPUT_FOLDER}")
        st.info(f"Coloca archivos Excel en la carpeta '{INPUT_FOLDER}' y recarga la página.")
        return

    # Menú de navegación
    page = st.sidebar.radio(
        "Ir a:",
        ["🏠 Inicio", "📊 Programas", "🏷️ Temáticas", "📈 Comparativa"]
    )

    # ========================================================================
    # PÁGINA: INICIO
    # ========================================================================
    if page == "🏠 Inicio":
        st.title("🎓 Dashboard de Análisis Microcurricular")
        st.markdown("---")

        # KPIs principales
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                "Programas Analizados",
                len(programs),
                delta=None
            )

        total_comp = sum(p['indicadores']['resumen']['total_competencias'] for p in programs)
        with col2:
            st.metric(
                "Total Competencias",
                total_comp
            )

        total_ra = sum(p['indicadores']['resumen']['total_ra'] for p in programs)
        with col3:
            st.metric(
                "Total RA",
                total_ra
            )

        avg_score = sum(p['indicadores']['score_calidad'] for p in programs) / len(programs)
        with col4:
            st.metric(
                "Score Promedio",
                f"{avg_score:.1f}/100"
            )

        st.markdown("---")

        # Gráfico de cobertura de temáticas
        st.subheader("📊 Cobertura de Temáticas")

        # Calcular programas por temática
        tematicas_count = {t: 0 for t in TEMATICAS.keys()}

        for program in programs:
            for tematica in program['tematicas']['tematicas_presentes']:
                if tematica in tematicas_count:
                    tematicas_count[tematica] += 1

        df_tematicas = pd.DataFrame([
            {'Temática': k, 'Programas': v}
            for k, v in tematicas_count.items()
        ]).sort_values('Programas', ascending=True)

        fig_tematicas = px.bar(
            df_tematicas,
            x='Programas',
            y='Temática',
            orientation='h',
            title='Número de Programas por Temática',
            color='Programas',
            color_continuous_scale='Blues'
        )
        fig_tematicas.update_layout(height=500, showlegend=False)
        st.plotly_chart(fig_tematicas, use_container_width=True)

        # Distribución de scores
        st.markdown("---")
        st.subheader("📈 Distribución de Scores de Calidad")

        scores = [p['indicadores']['score_calidad'] for p in programs]
        nombres = [p['nombre'] for p in programs]

        df_scores = pd.DataFrame({
            'Programa': nombres,
            'Score': scores
        }).sort_values('Score', ascending=False)

        fig_scores = px.bar(
            df_scores,
            x='Score',
            y='Programa',
            orientation='h',
            title='Score de Calidad por Programa',
            color='Score',
            color_continuous_scale='RdYlGn',
            range_color=[0, 100]
        )
        fig_scores.update_layout(height=600)
        st.plotly_chart(fig_scores, use_container_width=True)

    # ========================================================================
    # PÁGINA: PROGRAMAS
    # ========================================================================
    elif page == "📊 Programas":
        st.title("📊 Análisis por Programa")
        st.markdown("---")

        # Selector de programa
        program_names = [p['nombre'] for p in programs]
        selected_program_name = st.selectbox(
            "Seleccionar programa:",
            program_names
        )

        # Obtener programa seleccionado
        selected_program = next(p for p in programs if p['nombre'] == selected_program_name)
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
            p for p in programs
            if tematica_seleccionada in p['tematicas']['tematicas_presentes']
        ]

        st.subheader(f"Programas que abordan: {tematica_seleccionada}")
        st.metric(
            "Total de programas",
            f"{len(programas_con_tematica)} de {len(programs)}"
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

        # Selector múltiple
        program_names = [p['nombre'] for p in programs]
        selected_programs = st.multiselect(
            "Seleccionar programas para comparar (2-5):",
            program_names,
            default=program_names[:2] if len(program_names) >= 2 else program_names
        )

        if len(selected_programs) < 2:
            st.warning("Selecciona al menos 2 programas para comparar")
            return

        # Obtener datos de programas seleccionados
        programas_comparar = [p for p in programs if p['nombre'] in selected_programs]

        # Radar chart de indicadores
        st.subheader("🕸️ Comparativa de Indicadores")

        categories = ['Score Calidad', 'Completitud', 'Índice Complejidad',
                     'Cobertura Comp.', 'Diversidad Met.']

        fig_radar = go.Figure()

        for prog in programas_comparar:
            ind = prog['indicadores']

            values = [
                ind['score_calidad'],
                ind['completitud']['completitud_total'],
                ind['complejidad_cognitiva']['indice_complejidad'],
                ind['cobertura_competencias']['porcentaje_cobertura'],
                min(100, ind['diversidad_metodologica']['num_estrategias_unicas'] * 8)
            ]

            fig_radar.add_trace(go.Scatterpolar(
                r=values,
                theta=categories,
                fill='toself',
                name=prog['nombre']
            ))

        fig_radar.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
            showlegend=True,
            height=500
        )

        st.plotly_chart(fig_radar, use_container_width=True)

        # Tabla comparativa
        st.markdown("---")
        st.subheader("📊 Tabla Comparativa")

        datos_comparativa = []
        for prog in programas_comparar:
            ind = prog['indicadores']
            datos_comparativa.append({
                'Programa': prog['nombre'],
                'Score': ind['score_calidad'],
                'Competencias': ind['resumen']['total_competencias'],
                'RA': ind['resumen']['total_ra'],
                'Completitud %': ind['completitud']['completitud_total'],
                'Complejidad Avanzado %': ind['complejidad_cognitiva']['Avanzado'],
                'Num Temáticas': prog['tematicas']['num_tematicas']
            })

        df_comparativa = pd.DataFrame(datos_comparativa)
        st.dataframe(df_comparativa, use_container_width=True, hide_index=True)


if __name__ == '__main__':
    main()
