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
            
            # Calcular creditos totales del programa
            creditos_total = 0
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
                
                #优先: buscar fila con "Total" en Semestre
                if semestre_col and creditos_col:
                    filas_total = estrategias[estrategias[semestre_col].astype(str).str.contains('Total', na=False)]
                    if len(filas_total) > 0:
                        creditos_total = pd.to_numeric(filas_total[creditos_col].iloc[0], errors='coerce')
                    # Si no hay fila Total, calcular suma de creditos por asignatura
                    elif nombre_col:
                        creditos_unicos = estrategias.groupby(nombre_col)[creditos_col].first()
                        creditos_validos = creditos_unicos[pd.to_numeric(creditos_unicos, errors='coerce') <= 30]
                        creditos_total = float(pd.to_numeric(creditos_validos, errors='coerce').sum())
            
            programs.append({
                'nombre': data['metadata']['programa'],
                'data': data,
                'indicadores': indicadores,
                'tematicas': tematicas,
                'creditos_total': creditos_total
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
        ["🏠 Inicio", "📊 Programas", "🏷️ Temáticas", "📈 Comparativa", "📋 Estrategias Micro"]
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

        # Calcular también métricas normalizadas por créditos
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

        # Dos listas desplegables para comparar
        program_names = [p['nombre'] for p in programs]
        
        col1, col2 = st.columns(2)
        
        with col1:
            prog1_name = st.selectbox(
                "Programa 1",
                program_names,
                index=0 if len(program_names) > 0 else 0
            )
        
        with col2:
            prog2_name = st.selectbox(
                "Programa 2",
                program_names,
                index=1 if len(program_names) > 1 else 0
            )

        if prog1_name == prog2_name:
            st.warning("Selecciona dos programas diferentes")
            return

        # Obtener datos de los programas seleccionados
        prog1 = next((p for p in programs if p['nombre'] == prog1_name), None)
        prog2 = next((p for p in programs if p['nombre'] == prog2_name), None)

        if prog1 is None or prog2 is None:
            st.error("Error al cargar los programas")
            return

        # Radar chart
        st.subheader("🕸️ Comparativa de Indicadores")

        categories = ['Score Calidad', 'Completitud', 'Índice Complejidad',
                     'Cobertura Comp.', 'Diversidad Met.']

        fig_radar = go.Figure()

        for prog in [prog1, prog2]:
            if prog is None:
                continue
            ind = prog.get('indicadores')
            if ind is None:
                continue

            values = [
                ind.get('score_calidad', 0),
                ind.get('completitud', {}).get('completitud_total', 0),
                ind.get('complejidad_cognitiva', {}).get('indice_complejidad', 0),
                ind.get('cobertura_competencias', {}).get('porcentaje_cobertura', 0),
                min(100, ind.get('diversidad_metodologica', {}).get('num_estrategias_unicas', 0) * 8)
            ]

            fig_radar.add_trace(go.Scatterpolar(
                r=values,
                theta=categories,
                fill='toself',
                name=prog.get('nombre', 'Unknown')
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
        for prog in [prog1, prog2]:
            if prog is None:
                continue
            ind = prog.get('indicadores')
            if ind is None:
                continue
            datos_comparativa.append({
                'Programa': prog.get('nombre', 'Unknown'),
                'Score': ind.get('score_calidad', 0),
                'Competencias': ind.get('resumen', {}).get('total_competencias', 0),
                'RA (Asignaturas)': ind.get('resumen', {}).get('total_ra', 0),
                'Creditos': int(prog.get('creditos_total', 0)),
                'Completitud %': ind.get('completitud', {}).get('completitud_total', 0),
                'Complejidad Avanzado %': ind.get('complejidad_cognitiva', {}).get('Avanzado', 0),
                'Num Tematicas': prog.get('tematicas', {}).get('num_tematicas', 0)
            })

        if len(datos_comparativa) > 0:
            df_comparativa = pd.DataFrame(datos_comparativa)
            st.dataframe(df_comparativa, use_container_width=True, hide_index=True)

            # Comparar créditos entre los dos programas
            if prog1 is not None and prog2 is not None:
                cred1 = prog1.get('creditos_total', 0)
                cred2 = prog2.get('creditos_total', 0)
                
                diff = abs(cred1 - cred2)
                diff_pct = (diff / max(cred1, cred2) * 100) if max(cred1, cred2) > 0 else 0
                
                if cred1 == cred2:
                    st.success(f"✓ Los dos programas tienen la misma cantidad de creditos: **{int(cred1)}** creditos")
                else:
                    st.warning(f"⚠ Los programas tienen creditos diferentes: **{prog1.get('nombre')}** tiene {int(cred1)} creditos y **{prog2.get('nombre')}** tiene {int(cred2)} creditos (Diferencia: {int(diff)} creditos / {diff_pct:.1f}%)")

        # Comparativa de Temáticas
        st.markdown("---")
        st.subheader("🏷️ Comparativa de Temáticas")

        datos_tematicas = []
        for prog in [prog1, prog2]:
            tematicas = prog['tematicas']
            row = {'Programa': prog['nombre']}
            for tema, datos in tematicas['resumen'].items():
                if datos['presente']:
                    row[tema] = datos['asignaturas_con_tematica']
            datos_tematicas.append(row)

        df_tematicas = pd.DataFrame(datos_tematicas)
        if len(df_tematicas) > 0:
            # Llenar NaN con 0
            numeric_cols = df_tematicas.select_dtypes(include='number').columns
            df_tematicas[numeric_cols] = df_tematicas[numeric_cols].fillna(0)
            st.dataframe(df_tematicas, use_container_width=True, hide_index=True)

        # Similitud entre programas
        st.markdown("---")
        st.subheader("🔗 Similitud entre Programas")

        # Calcular TF-IDF y cosine similarity
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
            from sklearn.metrics.pairwise import cosine_similarity
        except ImportError:
            st.info("Instala scikit-learn para analisis de similitud")
            st.stop()

        from pathlib import Path as PathLib
        from src.extractor import ExcelExtractor
        
        input_folder = PathLib(INPUT_FOLDER)
        
        similitud_data = []
        programas_texto = []
        
        for prog in [prog1, prog2]:
            file_name = None
            for f in input_folder.glob('*.xlsx'):
                if prog['nombre'] in f.name:
                    file_name = str(f)
                    break
            
            if file_name:
                extractor = ExcelExtractor(file_name)
                data = extractor.extract_all()
                estr = data.get('estrategias_micro')
                
                if estr is not None and len(estr) > 0:
                    textos = []
                    for _, row in estr.iterrows():
                        texto = ''
                        for col in ['Actividades de aprendizaje', 'Actividades de evaluacion', 'Nucleos tematicos']:
                            if col in estr.columns:
                                val = row.get(col)
                                if pd.notna(val):
                                    texto += ' ' + str(val)
                        if texto.strip():
                            textos.append(texto)
                    
                    texto_programa = ' '.join(textos)
                    similitud_data.append(texto_programa)
                    programas_texto.append(prog['nombre'])

        if len(similitud_data) == 2:
            # TF-IDF
            try:
                import numpy as np
                vectorizer = TfidfVectorizer(max_features=100, stop_words='spanish')
                tfidf = vectorizer.fit_transform(similitud_data)
                
                # Cosine similarity
                sim_matrix = cosine_similarity(tfidf)
                similitud = float(sim_matrix[0][1])

                col1, col2 = st.columns(2)
                col1.metric("Similitud (TF-IDF)", f"{similitud:.1%}")
                
                # Terminos mas similares
                feature_names = vectorizer.get_feature_names_out()
                tfidf_dense = tfidf.toarray()
                
                # Terminos comunes con mayor peso
                comun = tfidf_dense[0] * tfidf_dense[1]
                comun_nonzero = comun[comun > 0]
                top_common = [str(feature_names[i]) for i in range(len(comun)) if comun[i] > 0]
                
                col2.metric("Terminos en comun", str(len(top_common)))
                
            except Exception as e:
                st.warning(f"Error calculando similitud: {e}")

            # Gráfico de comparación de estrategias
            st.markdown("#### Comparación de Estrategias Pedagógicas")
            
            datos_estrategias = []
            for prog in [prog1, prog2]:
                file_name = next((f.name for f in input_folder.glob('*.xlsx') if prog['nombre'] in f.name), None)
                if file_name:
                    extractor = ExcelExtractor(str(input_folder / file_name))
                    data = extractor.extract_all()
                    estr = data['estrategias_micro']
                    
                    keywords = ['taller', 'caso', 'problema', 'proyecto', 'laboratorio', 
                               'lectura', 'exposición', 'debate', 'simulación', 'ejercicio']
                    
                    texto = ' '.join(estr['Actividades de aprendizaje'].dropna().str.lower())
                    
                    for kw in keywords:
                        count = texto.count(kw)
                        datos_estrategias.append({
                            'Programa': prog['nombre'],
                            'Estrategia': kw.title(),
                            'Cantidad': count
                        })

            df_estr = pd.DataFrame(datos_estrategias)
            if not df_estr.empty:
                fig_estr = px.bar(
                    df_estr,
                    x='Estrategia',
                    y='Cantidad',
                    color='Programa',
                    barmode='group',
                    title='Comparación de Estrategias Pedagógicas',
                    color_discrete_sequence=['#1f77b4', '#ff7f0e']
                )
                fig_estr.update_layout(height=400)
                st.plotly_chart(fig_estr, use_container_width=True)

    # ========================================================================
    # PÁGINA: ESTRATEGIAS MICRO
    # ========================================================================
    elif page == "📋 Estrategias Micro":
        st.title("📋 Análisis de Estrategias Microcurriculares")
        st.markdown("---")

        st.subheader("📊 Distribución Tipo de Saber por Programa")
        
        # Cargar datos de estrategias micro para todos los programas
        from src.extractor import ExcelExtractor
        from pathlib import Path
        
        input_folder = Path(INPUT_FOLDER)
        excel_files = list(input_folder.glob('*.xlsx'))
        
        datos_tipo_saber = []
        datos_tipologia = []
        datos_horas = []
        datos_estrategias = []
        
        for file_path in excel_files:
            try:
                extractor = ExcelExtractor(str(file_path))
                estrategias_micro = extractor.extract_estrategias_micro()
                nombre_prog = extractor.programa_nombre
                
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
