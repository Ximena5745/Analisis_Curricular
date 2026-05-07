# Análisis del Frontend / Dashboard

## Stack Tecnológico

| Componente | Tecnología |
|-----------|-----------|
| Framework | Streamlit |
| Visualización | plotly |
| Datos | pandas |
| Temas | light/dark |

## Estructura

```
dashboard/
├── __init__.py
└── app.py          # Aplicación principal
```

## app.py - Funcionalidades

### 1. Página Principal
- Título y descripción del sistema
- Indicaciones de uso

### 2. Sección de Carga
- Widget de subida de archivos Excel
- Validación de formato

### 3. Sección de Análisis
- Métricas globales (programas, competencias, RA)
- Distribución por tipo de saber
- Gráficos de barras y pastel

### 4. Sección de Tabs
- Tab 1: Vista por competencia
- Tab 2: Vista por resultado de aprendizaje
- Tab 3: Métricas de calidad

### 5. Sección de Exportación
- Botones de descarga por formato

## Componentes Visuales

| Componente | Descripción |
|-----------|-----------|
| `st.title` | Título principal |
| `st.file_uploader` | Carga de archivos Excel |
| `st.metric` | KPIs numéricos |
| `st.bar_chart` | Gráfico de barras |
| `st.plotly_chart` | Gráfico interactivo |
| `st.dataframe` | Tabla de datos |
| `st.tabs` | Pestañas de navegación |
| `st.download_button` | Descarga de archivos |

## Flujo de Usuario

```
1. Abre dashboard (streamlit run dashboard/app.py)
2. Sube archivo Excel
3. Sistema procesa automáticamente
4. Visualiza métricas en tiempo real
5. Explora tabs por competencia/RA
6. Exporta en formato deseado
```

## Navegación

```
├── Overview (métricas generales)
├── Competencias (vista detallada)
├── Resultados de Aprendizaje
├── Calidad (validación)
└── Descarga (exportar)
```

## Gestión de Estado

- `st.session_state` para datos cargados
- Recálculo automático al subir nuevo archivo

## Personalización

```python
# config.py
CONFIG = {
    'DASHBOARD_PORT': 8501,
    'DASHBOARD_THEME': 'light',  # o 'dark'
}
```

## Responsividad

- Adaptable a diferentes tamaños de pantalla
- Mobile-friendly (Streamlit maneja esto)

## Accesibilidad

- Soporte básico de keyboard navigation
- Colores con contraste adecuado

## Pendientes

- [ ] Autenticación de usuarios
- [ ] Dashboard multi-archivo
- [ ] Temas personalizados
- [ ] Internacionalización (i18n)
- [ ] Más visualizaciones interactivas