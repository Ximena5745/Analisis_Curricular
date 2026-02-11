# ⚡ Inicio Rápido - 5 Minutos

## 📋 Checklist Rápido

```
☐ 1. Instalar Python 3.10+
☐ 2. Crear entorno virtual
☐ 3. Instalar dependencias
☐ 4. Colocar archivos Excel en data/raw/
☐ 5. Ejecutar análisis
```

---

## 🚀 Pasos

### 1️⃣ Instalación (2 minutos)

```bash
# Navegar al proyecto
cd proyecto_analisis_microcurricular

# Crear entorno virtual
python -m venv venv

# Activar
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Instalar
pip install -r requirements.txt
```

### 2️⃣ Preparar Datos (1 minuto)

```bash
# Copiar tus archivos Excel a:
data/raw/

# Ejemplo:
# data/raw/FormatoRA_AdmonEmpresas_PBOG.xlsx
# data/raw/FormatoRA_IngSistemas_PBOG.xlsx
# ... (resto de archivos)
```

### 3️⃣ Validar Archivos (30 segundos)

```bash
python validate_files.py
```

✅ Si todo está OK, continúa
⚠️ Si hay errores, corrige los archivos

### 4️⃣ Ejecutar Análisis (1-2 minutos)

```bash
python run_analysis.py
```

**Espera a que termine. Verás:**
```
[1/50] ✅ Completado - Score: 88.5/100
[2/50] ✅ Completado - Score: 92.1/100
...
```

### 5️⃣ Ver Resultados

**Opción A - Dashboard Interactivo:**
```bash
streamlit run dashboard/app.py
```

**Opción B - Archivos Generados:**
```
data/output/
├── reportes/          # HTML y JSON por programa
├── matrices/          # Matriz de temáticas Excel
└── consolidado/       # Indicadores consolidados Excel
```

---

## 📊 Qué Obtienes

### ✅ Por Programa:
- Score de calidad (0-100)
- Balance de tipos de saber
- Complejidad cognitiva
- Temáticas detectadas
- Reporte HTML visual

### ✅ Consolidado:
- Matriz Programas × Temáticas
- Ranking de programas por calidad
- Estadísticas institucionales
- Dashboard interactivo

---

## 🆘 Troubleshooting Rápido

### Error: "ModuleNotFoundError"
```bash
pip install -r requirements.txt
```

### Error: "No se encontraron archivos"
- Verifica que los archivos estén en `data/raw/`
- Verifica que sean archivos `.xlsx`

### Dashboard no abre
```bash
python -m streamlit run dashboard/app.py
```

---

## 📖 Siguiente Paso

Lee la [Guía de Usuario Completa](docs/guia_usuario.md) para:
- Interpretar resultados
- Casos de uso avanzados
- Personalizar configuración

---

## 💡 Ejemplo Completo

```bash
# 1. Activar entorno
venv\Scripts\activate

# 2. Validar archivos
python validate_files.py

# 3. Ejecutar análisis
python run_analysis.py

# 4. Ver dashboard
streamlit run dashboard/app.py

# 5. Abrir navegador en:
# http://localhost:8501
```

**¡Listo!** 🎉
