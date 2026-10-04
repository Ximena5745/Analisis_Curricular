# Pendientes por definir (inicio de la etapa de Resultados)

Generado por auditoria/scripts/generar_entregables.py (2026-10-02 13:21). También en el Excel (hoja Pendientes) y en el Word.

| ID | Tema | Etapa | Qué falta definir |
|---|---|---|---|
| Tabla 16 | Tópicos del análisis temático | Resultados | Re-estimar con el LDA de consenso (k = 13; consolidado/topicos_lda.xlsx al correr run_analysis.py). Nota: el tópico 1 (mercadeo, comunicación, planeación) es dominante en 330 de 1.192 asignaturas y el tópico 11 en ninguna; confianza media 0,42. |
| A11 | IA en 79,5 % de los programas y 3,3 % de los registros | Resultados | Búsqueda por palabra completa ya corregida. Definir la base: con texto de RA 31/39; con núcleos + indicadores 32/39 y 86 de 1.616 asignaturas. |
| V1–V5 | Tabla 2 (variables) | Variables | V1 cerrada (D13); V2 cerrada (D14 = 90 %); V3 cerrada (D15 = 100 %, estructural); V4 cerrada (D16 = 87,1 %; 98,0 % sin RA genérico); V5 definida (D17 = 0,8 % de estrategias con evidencia directa; falta kappa). Pendientes: V5 constante por estrategia. Luego regenerar la Figura 1 sin V1. |
| P16 | Reportes por programa (Etapa 7) | Procedimiento | DECISIÓN: nombrar reporte_<Programa>_<Sede> (hoy 50 matrices → 39 informes por sobrescritura). Recomendado; no cambia cifras. |
| P17 | Versión de Python y bibliotecas (Tabla 6) | Procedimiento | DECISIÓN: indicar el entorno de la corrida final (Docker 3.10, entorno local 3.12.7; la auditoría usó 3.14) y generar requirements con versiones exactas (pip freeze). |
| P21 | Isolation Forest en la Tabla 6 | Procedimiento | DECISIÓN: no se usa (detectar_anomalias_nucleos no se invoca). Quitar de la Tabla 6 (recomendado) o integrarlo y describirlo en una etapa. |
| P20 | Registro de la estructuración generativa | Procedimiento | DECISIÓN: aportar el registro de entradas, salidas y decisiones humanas (fuera del repositorio) o eliminar la frase. |
| P22 | Nombre del aplicativo "CurriculoPoli" | Procedimiento | CONFIRMAR: el código titula la app "Analisis Tematico Microcurricular". Añadir "modalidad" a los filtros del texto. |
| P19 | Código documentado | Procedimiento | Falta versionar el cálculo de V3 y la fuente de las Tablas 16–17 originales; acotar la afirmación si no aparecen. |
| Corpus | Fuente del 63 % de la oferta | Corpus | Citar documento institucional, fecha de corte y total de programas. |
| Código | analisis_tematico_avanzado.py (núcleos) | Código | DECISIÓN: reconocer "Tipo de saber", no rellenar núcleos hacia abajo y quitar el filtro de tipo de saber (6.631 → 6.671). |
| Inferencia | Pruebas por sede/nivel | Resultados | Repetir con una matriz por programa: los 8 multisede comparten RA y 89–100 % de núcleos. |
| Dashboard | Cobertura del perfil por grupo | Código | Opcional: mostrar cobertura_por_grupo (D9) en dashboard_tematico.py. |
| Discusión | Validación de la Discusión auditada | Discusión | Revisar 4.1–4.5 (Textos_corregidos, Resultados_consolidado.docx). Confirmar citas (Liu et al., 2024; Pusporini & Nurdiyanto, 2024; NIST, 2023; Devia-Acevedo, 2024) y la definición de P3, P4 y P9 en el Marco. |
| CINE-F | Asignación CINE-F de los programas | Discusión / R8 | Validar la hoja CINE-F_programas (3 programas con alternativa). El contraste del puntaje académico (D22, Figura 7) y la propuesta GreenMetric dependen de ella; recalcular con verificar_score_academico.py si cambia. |
| Git | Publicación | Proyecto | Commits locales en auditoria/p2-extractor-encabezados; push a origin rechazado (403, cuenta PlaneacionPoli). Definir cuenta o remoto. |
| V1 | Validación de la lectura de referencia (V1) | Método / R1 | El comité curricular valida una muestra de las 1.287 decisiones de auditoria/referencia_asociacion_perfil.csv (40 revisadas el 2026-10-03). Hasta entonces se mantiene la Observación de la Etapa 4; recalibrar con calibrar_asociacion_perfil.py si cambia. |
| Referencias | Lista de referencias del artículo | Referencias | Aplicar REFERENCIAS_CAMBIOS (textos_articulo.py): retirar Robertson y Zaragoza (2009); agregar Butterfuss y Doran (2025), Duarte et al. (2023), Zaki et al. (2023), Cohen (1960), Reimers y Gurevych (2020) y Spärck Jones (1972). |
| Exigencia | Índice de exigencia de IngIndustrial (3 matrices) | Etapa 3 | comparar_exigencia.py deduplica los RA sin puntuación (índice 37,9); el aplicativo usa la regla D4, minúsculas, que da los 341 RA del artículo (índice 35,9). Unificar la regla en el script de auditoría. |
| V1 | Alcance de V1 | Método | Saber, SaberHacer, SaberSer y Valor agregado quedan fuera de V1. Decidir si se reincorporan como medida complementaria. |
