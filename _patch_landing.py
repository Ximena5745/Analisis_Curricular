"""Script para reemplazar el bloque landing page completo."""
import re

NEW_BLOCK = '''    # ── Sin archivos: mostrar banner + uploader ──────────────────────────
    if not uploaded_files:
        st.markdown("""
        <style>
        /* ══ HEADER ════════════════════════════════════════════════════════ */
        .page-header { margin-bottom: 20px; }
        .page-header h1 { margin: 0; font-size: 2.6rem; color: #0f3460; line-height: 1.05; }
        .page-header p  { margin: 10px 0 0; color: #475569; font-size: 0.98rem; line-height: 1.7; max-width: 800px; }

        /* ══ HERO PANEL ════════════════════════════════════════════════════ */
        .hero-area {
            background: linear-gradient(135deg, #1a3a52 0%, #1e5080 60%, #2a6494 100%) !important;
            border-radius: 22px !important;
            padding: 44px 52px 40px !important;
            color: #fff !important;
            display: grid !important;
            grid-template-columns: 1.6fr 1fr !important;
            gap: 40px !important;
            align-items: center !important;
            margin-bottom: 8px !important;
            box-shadow: 0 20px 60px rgba(15,23,42,.2) !important;
            border: 1px solid rgba(31,178,222,.18) !important;
        }
        .hero-bar  { width:5px; height:52px; background:#1fb2de; border-radius:3px; margin-bottom:18px; }
        .hero-label {
            display: block !important; font-size:.75rem !important; font-weight:800 !important;
            text-transform:uppercase !important; letter-spacing:.16em !important;
            color:#9dd3ff !important; margin-bottom:12px !important;
        }
        .hero-area h2 {
            margin:0 0 12px !important; font-size:1.85rem !important; line-height:1.15 !important;
            font-weight:700 !important; color:#fff !important;
        }
        .hero-area > div > p {
            margin:0 0 28px !important; color:#c0d9ff !important;
            font-size:.94rem !important; line-height:1.65 !important;
        }
        .hero-actions { display:flex; flex-direction:column; gap:12px; }
        .hero-btn {
            display:inline-flex; align-items:center; justify-content:center; gap:8px;
            padding:12px 26px; border-radius:10px; font-weight:700; font-size:.92rem;
            cursor:pointer; min-height:44px; transition:all .22s ease; border:none; width:fit-content;
        }
        .hero-btn.primary { background:#1fb2de; color:#0f2d44; }
        .hero-btn.primary:hover { background:#19a0cc; transform:translateY(-2px); box-shadow:0 8px 22px rgba(31,178,222,.35); }
        .hero-btn.secondary { background:transparent; border:1.5px solid #7dd3f0 !important; color:#fff; }
        .hero-btn.secondary:hover { background:rgba(31,178,222,.15); border-color:#fff !important; }

        /* ══ UPLOAD RIGHT PANEL ════════════════════════════════════════════ */
        .hero-right {
            border:2px dashed rgba(31,178,222,.45) !important; border-radius:18px !important;
            padding:32px 20px !important; background:rgba(31,178,222,.08) !important;
            display:flex !important; flex-direction:column !important;
            align-items:center !important; justify-content:center !important;
            gap:12px !important; text-align:center !important;
        }
        .upload-icon-box {
            width:54px; height:54px; border-radius:14px; background:rgba(31,178,222,.22);
            display:flex; align-items:center; justify-content:center;
        }
        .hero-right h4 { margin:6px 0 2px; font-size:.97rem; font-weight:700; color:#fff !important; }
        .hero-right span { color:rgba(255,255,255,.65); font-size:.82rem; }

        /* ══ FILE UPLOADER NATIVO ══════════════════════════════════════════ */
        [data-testid="stFileUploader"] { border-radius:14px !important; margin-bottom:28px !important; }
        [data-testid="stFileUploader"] > div {
            border:1.5px dashed #1fb2de !important; border-radius:14px !important; background:#f0faff !important;
        }
        [data-testid="stFileUploader"] section { background:transparent !important; }

        /* ══ FEATURE CARDS ══════════════════════════════════════════════════ */
        .feature-grid { display:grid; grid-template-columns:repeat(4,1fr); gap:16px; margin-bottom:18px; }
        .feature-grid.row-2 { grid-template-columns:repeat(2,1fr); max-width:50%; }
        .feature-card {
            background:#fff; border-radius:18px; padding:20px;
            box-shadow:0 8px 24px rgba(15,23,42,.07);
            min-height:165px; display:flex; flex-direction:column; justify-content:space-between;
            border:1px solid #e8f1ff; transition:all .25s ease;
            border-top:4px solid var(--card-color,#1fb2de);
        }
        .feature-card:hover { transform:translateY(-4px); box-shadow:0 16px 40px rgba(15,23,42,.12); }
        .feature-icon-box {
            width:42px; height:42px; border-radius:10px; display:flex; align-items:center;
            justify-content:center; margin-bottom:12px; background:var(--card-bg,#e8f8ff);
        }
        .feature-card h3 { margin:0 0 9px; font-size:.96rem; font-weight:700; color:#0d314e; }
        .feature-card p  { margin:0; color:#6c7a93; font-size:.86rem; line-height:1.5; flex:1; }
        .feature-meta { display:flex; justify-content:space-between; align-items:center; margin-top:14px; font-size:.76rem; font-weight:700; }
        .feature-meta .status { color:var(--card-color,#0f3460); }
        .feature-meta .status.alert { color:#d93025; }
        .feature-meta .arrow { color:#b0c4de; }

        /* ══ DIALOG MODAL (HTML5 nativo) ════════════════════════════════════ */
        dialog#estructuraModal {
            border:none; border-radius:20px; padding:0; width:min(92vw,860px);
            max-height:82vh; overflow:hidden; box-shadow:0 30px 90px rgba(0,0,0,.28);
        }
        dialog#estructuraModal::backdrop { background:rgba(0,0,0,.5); backdrop-filter:blur(4px); }
        .dialog-inner { padding:36px 40px; overflow-y:auto; max-height:80vh; }
        .dialog-header {
            display:flex; justify-content:space-between; align-items:center;
            margin-bottom:24px; padding-bottom:18px; border-bottom:2px solid #f0f4ff;
        }
        .dialog-header h2 { margin:0; color:#0f3460; font-size:1.6rem; }
        .dialog-close {
            background:#f0f4ff; border:none; border-radius:50%; width:38px; height:38px;
            cursor:pointer; font-size:22px; color:#0f3460; display:flex; align-items:center;
            justify-content:center; transition:all .2s;
        }
        .dialog-close:hover { background:#1fb2de; color:#fff; }
        .dialog-section { margin-bottom:28px; }
        .dialog-section h3 { color:#1a3a52; font-size:1.1rem; margin:0 0 14px; }
        .dialog-section ol { margin:0; padding-left:20px; color:#334155; font-size:.93rem; line-height:1.9; }
        .dialog-section ol li { margin-bottom:8px; }
        .dialog-table { width:100%; border-collapse:collapse; font-size:.91rem; margin-top:10px; }
        .dialog-table th, .dialog-table td { border:1px solid #e2e8f0; padding:11px 14px; text-align:left; color:#334155; }
        .dialog-table th { background:linear-gradient(135deg,#1fb2de,#1a9cc6); color:#fff; font-weight:700; }
        .dialog-table tbody tr:hover { background:#f0f9ff; }
        .dialog-table tbody tr:nth-child(even) { background:#f8fcff; }
        </style>

        <dialog id="estructuraModal">
            <div class="dialog-inner">
                <div class="dialog-header">
                    <h2>Estructura del archivo Excel</h2>
                    <button class="dialog-close" onclick="document.getElementById(\'estructuraModal\').close()">&#215;</button>
                </div>
                <div class="dialog-section">
                    <h3>Como empezar</h3>
                    <ol>
                        <li><strong>Sube uno o mas archivos Excel (.xlsx)</strong> usando el selector de archivos.</li>
                        <li><strong>El archivo debe contener la hoja \'Paso 5 Estrategias micro\'</strong> con encabezados en la fila 2.</li>
                        <li><strong>El analisis se ejecuta automaticamente</strong> al cargar los archivos.</li>
                        <li><strong>Navega por las secciones</strong> usando el menu lateral izquierdo.</li>
                        <li><strong>Puedes cargar varios programas a la vez</strong> para analisis comparativos.</li>
                    </ol>
                </div>
                <div class="dialog-section">
                    <h3>Columnas requeridas en el Excel</h3>
                    <table class="dialog-table">
                        <thead><tr><th>Columna</th><th>Descripcion</th><th>Ejemplo</th></tr></thead>
                        <tbody>
                            <tr><td><strong>Tipo de Saber</strong></td><td>Clasificacion del saber</td><td>Saber / SaberHacer / SaberSer</td></tr>
                            <tr><td><strong>Resultado de aprendizaje</strong></td><td>Texto con verbo de accion</td><td>"Analiza los fundamentos..."</td></tr>
                            <tr><td><strong>Nombre asignatura o modulo</strong></td><td>Nombre de la asignatura</td><td>"Calculo Diferencial"</td></tr>
                            <tr><td><strong>Indicadores de logro</strong></td><td>Indicadores de evaluacion del RA</td><td>"Resuelve ejercicios con precision"</td></tr>
                            <tr><td><strong>Nucleos tematicos</strong></td><td>Temas separados por coma</td><td>"Derivadas, Integrales, Limites"</td></tr>
                            <tr><td><strong>Semestre</strong></td><td>Numero de semestre</td><td>1, 2, 3...</td></tr>
                            <tr><td><strong>Creditos</strong></td><td>Creditos academicos</td><td>3</td></tr>
                        </tbody>
                    </table>
                </div>
            </div>
        </dialog>
        """, unsafe_allow_html=True)

        # Header
        st.markdown("""
        <div class="page-header">
            <h1>An&#225;lisis Microcurricular basada en datos</h1>
            <p>Optimice sus procesos de dise&#241;o curricular a trav&#233;s del uso de herramientas avanzadas de Inteligencia Artificial para visualizar brechas y tendencias en tiempo real.</p>
        </div>
        """, unsafe_allow_html=True)

        # Hero panel
        icon_upload = render_icon_svg(\'upload\', \'#1fb2de\', 40)
        st.markdown(f"""
        <div class="hero-area">
            <div>
                <div class="hero-bar"></div>
                <span class="hero-label">Sistema de An&#225;lisis Microcurricular</span>
                <h2>Cargar Matriz de Resultados de aprendizaje</h2>
                <p>Inicia el an&#225;lisis masivo de tu archivo (.XLSX) para obtener m&#233;tricas instant&#225;neas.</p>
                <div class="hero-actions">
                    <button class="hero-btn primary" id="btnSeleccionar">Seleccionar Archivos</button>
                    <button class="hero-btn secondary" onclick="document.getElementById(\'estructuraModal\').showModal()">Estructura del archivo</button>
                </div>
            </div>
            <div class="hero-right">
                <div class="upload-icon-box">{icon_upload}</div>
                <h4>Selecciona tus archivos</h4>
                <span>200MB por archivo &middot; XLSX &middot; M&#250;ltiples archivos</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # File uploader nativo (visible y funcional)
        nuevo_upload = st.file_uploader(
            "Cargar archivos Excel (.xlsx)",
            type=[\'xlsx\'],
            accept_multiple_files=True,
            key="uploader_main"
        )

        # JS: conectar boton hero al input file con MutationObserver
        st.markdown("""
        <script>
        (function() {
            function connectHeroBtn() {
                var btn = document.getElementById(\'btnSeleccionar\');
                var inp = document.querySelector(\'input[type="file"]\');
                if (btn && inp) {
                    btn.onclick = function(e) { e.preventDefault(); inp.click(); };
                    return true;
                }
                return false;
            }
            if (!connectHeroBtn()) {
                var obs = new MutationObserver(function() {
                    if (connectHeroBtn()) obs.disconnect();
                });
                obs.observe(document.body, { childList: true, subtree: true });
            }
        })();
        </script>
        """, unsafe_allow_html=True)

        # Feature cards con colores por seccion
        icon_document = render_icon_svg(\'document\', \'#0077C8\', 22)
        icon_trend    = render_icon_svg(\'trend\',    \'#1fb2de\', 22)
        icon_bloom    = render_icon_svg(\'bloom\',    \'#7c3aed\', 22)
        icon_search   = render_icon_svg(\'search\',   \'#059669\', 22)
        icon_grid     = render_icon_svg(\'grid\',     \'#d97706\', 22)
        icon_settings = render_icon_svg(\'settings\', \'#dc2626\', 22)

        st.markdown(f"""
        <div class="feature-grid">
            <div class="feature-card" style="--card-color:#0077C8;--card-bg:#e8f3ff;">
                <div>
                    <div class="feature-icon-box">{icon_document}</div>
                    <h3>Resumen Ejecutivo</h3>
                    <p>Visi&#243;n general del estado de la Matriz de RA y cumplimiento de metas institucionales.</p>
                </div>
                <div class="feature-meta"><span class="status">85% COMPLETADO</span><span class="arrow">&#8250;</span></div>
            </div>
            <div class="feature-card" style="--card-color:#1fb2de;--card-bg:#e0f6ff;">
                <div>
                    <div class="feature-icon-box">{icon_trend}</div>
                    <h3>Tendencias Globales</h3>
                    <p>Comparativa con est&#225;ndares internacionales y tem&#225;ticas emergentes en la industria.</p>
                </div>
                <div class="feature-meta"><span class="status">12 NUEVAS</span><span class="arrow">&#8250;</span></div>
            </div>
            <div class="feature-card" style="--card-color:#7c3aed;--card-bg:#f3e8ff;">
                <div>
                    <div class="feature-icon-box">{icon_bloom}</div>
                    <h3>Bloom &amp; Integraci&#243;n</h3>
                    <p>Niveles taxon&#243;micos detectados en las competencias y resultados de aprendizaje.</p>
                </div>
                <div class="feature-meta"><span class="status">NIVEL: CREAR</span><span class="arrow">&#8250;</span></div>
            </div>
            <div class="feature-card" style="--card-color:#059669;--card-bg:#d1fae5;">
                <div>
                    <div class="feature-icon-box">{icon_search}</div>
                    <h3>Miner&#237;a de Texto</h3>
                    <p>Descubrimiento de patrones y nubes de palabras clave en el contenido curricular.</p>
                </div>
                <div class="feature-meta"><span class="status">PROCESADO</span><span class="arrow">&#8250;</span></div>
            </div>
        </div>
        <div class="feature-grid row-2">
            <div class="feature-card" style="--card-color:#d97706;--card-bg:#fef3c7;">
                <div>
                    <div class="feature-icon-box">{icon_grid}</div>
                    <h3>Tipo de Saber</h3>
                    <p>An&#225;lisis de la balanza entre saber, saber hacer y saber ser en los programas.</p>
                </div>
                <div class="feature-meta"><span class="status">&#8212;</span><span class="arrow">&#8250;</span></div>
            </div>
            <div class="feature-card" style="--card-color:#dc2626;--card-bg:#fee2e2;">
                <div>
                    <div class="feature-icon-box">{icon_settings}</div>
                    <h3>Cobertura Tem&#225;tica</h3>
                    <p>Detecci&#243;n de redundancias o vac&#237;os tem&#225;ticos en la malla curricular institucional.</p>
                </div>
                <div class="feature-meta"><span class="status alert">ALERTA BRECHAS</span><span class="arrow">&#8250;</span></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Procesar si se subieron archivos
        if nuevo_upload is not None and len(nuevo_upload) > 0:
            st.session_state[\'archivos_subidos\'] = nuevo_upload
            st.rerun()

        st.stop()
'''

# Leer el archivo
with open('dashboard_tematico.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Buscar el bloque usando marcadores únicos
start_marker = '    # ── Sin archivos: mostrar banner + uploader ──────────────────────────\n    if not uploaded_files:'
end_marker = '        st.stop()\n\n    # Procesar archivos'

start_idx = content.find(start_marker)
end_idx = content.find(end_marker)

if start_idx == -1:
    print("ERROR: No se encontró el marcador de inicio")
elif end_idx == -1:
    print("ERROR: No se encontró el marcador de fin")
else:
    # Incluir el fin_marker sin "# Procesar archivos" en el reemplazo
    end_pos = end_idx + len('        st.stop()')
    
    new_content = content[:start_idx] + NEW_BLOCK + content[end_pos:]
    
    # Hacer backup
    with open('dashboard_tematico.py.bak', 'w', encoding='utf-8') as f:
        f.write(content)
    
    # Escribir nuevo contenido
    with open('dashboard_tematico.py', 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"OK: Bloque reemplazado. Original {len(content.splitlines())} lineas -> {len(new_content.splitlines())} lineas")
    
    # Verificar compilación
    import py_compile
    try:
        py_compile.compile('dashboard_tematico.py', doraise=True)
        print("OK: Compilacion exitosa sin errores de sintaxis")
    except py_compile.PyCompileError as e:
        print(f"ERROR sintaxis: {e}")
        # Restaurar backup si hay error
        import shutil
        shutil.copy('dashboard_tematico.py.bak', 'dashboard_tematico.py')
        print("Backup restaurado")
