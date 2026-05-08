# Diccionario de Datos (Tabla de Resumen)

Resumen de tablas, campos y claves.

## Tabla: programas
- `id` (PRIMARY KEY)
- `nombre` (Texto)
- `modalidad` (Texto)
- `sede` (Texto)
- `nivel_formacion` (Texto) opcional: Pregrado/Posgrado cuando esté disponible
- `creditos_total` (Número)
- `metricas_json` (JSON) opcional

## Tabla: competencias
- `id` (PRIMARY KEY)
- `programa_id` (FK)
- `numero` (Texto)
- `verbo` (Texto)
- `objeto` (Texto)
- `finalidad` (Texto)
- `tipo` (Texto)

## Tabla: resultados_aprendizaje
- `id` (PRIMARY KEY)
- `competencia_id` (FK)
- `numero` (Texto)
- `verbo` (Texto)
- `resultado` (Texto)
- `tipo_saber` (Texto)
- `nivel_dominio` (Texto)

## Tabla: estrategias_micro
- `id` (PRIMARY KEY)
- `programa_id` (FK)
- `tipo_de_saber` (Texto)
- `estrategia` (Texto)
- `recursos` (Texto)
- `horas_autonomo` (Número)
- `horas_presencial` (Número)
- `criterios_evaluacion` (Texto)
- `acciones_retroalimentacion` (Texto)
- `nivel` (Texto) — `Pregrado` o `Posgrado`
- `componente_academico` (Texto) — B. Institucional, B. Disciplinar, B. Electivo, C. Fundamentación, C. Profundización
- `modalidad` (Texto)
- `sede` (Texto)

## Recomendación
Usar el campo `nivel` para distinguir formación y evitar dividir la estructura en dos tablas separadas por nivel académico. Esto permite consultar, filtrar y agrupar los datos en una sola fuente.
