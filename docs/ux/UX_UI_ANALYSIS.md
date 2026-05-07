# Análisis UX/UI

## Stack Visual

| Componente | Tecnología |
|-----------|-----------|
| Framework UI | Streamlit |
| Gráficos | plotly |
| Temas | light/dark |

## Pantallas

| Pantalla | Descripción |
|---------|-----------|
| Principal | Título + upload + métricas |
| Upload | Subida de archivos Excel |
| Overview | KPIs globales |
| Competencias | Vista por competencia |
| RA | Vista por resultado |
| Calidad | Validación y scores |

## Patrones UI

- Upload de archivo (drag & drop)
- Métricas en tarjetas (st.metric)
- Gráficos de barras
- Gráficos circulares (distribución)
- DataFrames interactivos
- Tabs de navegación
- Botones de descarga

## Consistencia

| Aspecto | Estado |
|---------|--------|
| Colores | Paleta predefinida en `config.py` |
| Tipografía | Streamlit default |
| Espaciado | Streamlit default |
| Temas | Light/Dark configurable |

## Accesibilidad

- Soporte clavier Streamlit
- Contraste adecuado en gráficos
- Responsive (adaptable móvil)

## Pendientes

- [ ] Temas personalizados
- [ ] Componentes reutilizables
- [ ] Internacionalización
- [ ] UI más interactiva