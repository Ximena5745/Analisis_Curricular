# Análisis de Base de Datos

## Motores y Almacenamiento

| Tipo | Uso |
|------|-----|
| SQLite | Base de datos local (`microcurricular.db`) |
| Excel | Archivos de entrada (`data/raw/*.xlsx`) |
| Archivos | Resultados (`data/output/*.*`) |

## Modelo de Datos

### sqlite: microcurricular.db

**Opcional:** Sistema puede funcionar sin base de datos (modo archivos).

```
Tablas conceptuales (si se usa SQLite):
├── programas
│   ├── id (PRIMARY KEY)
│   ├── nombre
│   ├── fecha_analisis
│   └── métricas_json
├── competencias
│   ├── id (PRIMARY KEY)
│   ├── programa_id (FK)
│   ├── numero
│   ├── verbo
│   ├── objeto
│   ├── finalidad
│   └── tipo
├── resultados_aprendizaje
│   ├── id (PRIMARY KEY)
│   ├── competencia_id (FK)
│   ├── numero
│   ├── verbo
│   ├── resultado
│   └── tipo_saber
├── métricas
│   ├── id (PRIMARY KEY)
│   ├── programa_id (FK)
│   ├── completeness
│   ├── distribution
│   └── score
└── estrategias_micro
    ├── id (PRIMARY KEY)
    ├── programa_id (FK)
    ├── tipo_de_saber
    ├── estrategia
    ├── recursos
    ├── horas_autonomo
    ├── horas_presencial
    ├── criterios_evaluacion
    ├── acciones_retroalimentacion
    ├── nivel
    ├── componente_academico
    ├── modalidad
    └── sede
```

### Excel: data/raw/*.xlsx

Estructura de archivos de entrada (formato institucional):

```
FormatoRA_*.xlsx
├── Hoja: "Paso1 Analisis perfil egreso"
│   └── Perfil de egreso del programa
├── Hoja: "Paso 2 Redacción competen"
│   ├── No.
│   ├── Verbo competencia
│   ├── Objeto conceptual
│   ├── Finalidad
│   ├── Condición de contexto o referencia
│   ├── Redacción competencia
│   └── Tipo de competencia
├── Hoja: "Paso 3 Redacción RA"
│   ├── Competencia por desarrollar
│   ├── Número de resultado
│   ├── TipoSaber
│   ├── SaberAsociado
│   ├── Taxonomía
│   ├── Dominio Asociado
│   ├── Nivel Dominio
│   ├── Verbo RA
│   └── Resultados Aprendizaje
├── Hoja: "Paso 4 Estrategias mesocurricu"
│   ├── Resultado de aprendizaje
│   ├── Estrategia del programa
│   ├── Descripción
│   ├── Indicador de Impacto
│   └── Acciones de retroalimentación
└── Hoja: "Paso 5 Estrategias micro"
    ├── Tipo de Saber
    ├── Estrategias de enseñanza aprendizaje
    ├── Recursos
    ├── Horas de trabajo autónomo
    ├── Horas de trabajo presencial
    ├── Criterios de evaluación
    ├── Acciones de retroalimentación
    ├── Nivel
    └── Componente académico

**Clasificación de componentes académicos por nivel:**
- Programas de Pregrado: `B. Institucional`, `B. Disciplinar`, `B. Electivo`
- Programas de Posgrado: `C. Fundamentación`, `C. Profundización`

**Nota de diseño:** Se recomienda guardar estos atributos en la misma tabla `estrategias_micro` y usar filtros sobre `Nivel` en lugar de dividir la estructura de tablas por nivel académico.
```

## Índices

- Primary keys en `id` de cada tabla
- Foreign keys en `programa_id`, `competencia_id`
- Índices implícitos en pandas (DataFrame)

## Relaciones

```
programa (1) ──→ (N) competencias
programa (1) ──→ (N) resultados_aprendizaje
competencia (1) ──→ (N) resultados_aprendizaje
```

## Migraciones

- No hay migraciones formales (SQLite)
- Modo desarrollo: Auto-creación de DB si no existe

## Semillas (Seeds)

- No hay seed data
- Datos viene de archivos Excel subidos por usuario

## Calidad de Datos

| Aspecto | Validación |
|---------|-----------|
| Completitud | ≥70% campos llenos (configurable) |
| Consistencia | Verbos según taxonomía |
| Estructura | Columnas esperadas por hoja |

## Rendimiento

- SQLite: rápido para datasets pequeños (<1000 filas)
- Excel: depende de tamaño de archivo
- Procesamiento paralelo: configurable `MAX_WORKERS`

## Respaldo

- Archivos Excel en `data/raw/`
- Resultados en `data/output/`
- Recomendado: versionar en Git

## Pendientes

- [ ] Definir schema formal si se usa SQLite
- [ ] Migraciones con Alembic
- [ ] Índices adicionales para rendimiento
- [ ] Data warehouse para analítica