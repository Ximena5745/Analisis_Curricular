# Modelo de Datos (Diccionario)

Descripción general del modelo de datos y diccionario de entidades relevantes.

## Objetivo
Documentar la estructura de datos de la plataforma de análisis curricular, incluyendo la nueva clasificación de componentes académicos por nivel de formación.

## Clasificación académica
- Programas de Pregrado:
  - B. Institucional
  - B. Disciplinar
  - B. Electivo
- Programas de Posgrado:
  - C. Fundamentación
  - C. Profundización

## Estructura recomendada de datos
Se recomienda mantener una única tabla de `estrategias_micro` con campos adicionales en lugar de separar tablas por nivel académico. Esta opción reduce duplicidad y facilita filtros transversales.

### Tablas principales
- `programas`
  - Identifica el programa académico y sus metadatos generales.
- `competencias`
  - Contiene competencias declaradas en Paso 2.
- `resultados_aprendizaje`
  - Contiene RA declarados en Paso 3.
- `estrategias_micro`
  - Contiene las filas de Paso 5, con un nuevo campo `Nivel` para Pregrado/Posgrado y un campo de clasificación de componentes.

## Campo `Nivel`
- `Nivel` debe ser un campo obligatorio en la tabla de estrategias microcurriculares.
- Valores esperados:
  - `Pregrado`
  - `Posgrado`

## Campo `Componente académico`
- Valores asociados a cada nivel:
  - Pregrado: `B. Institucional`, `B. Disciplinar`, `B. Electivo`
  - Posgrado: `C. Fundamentación`, `C. Profundización`
- Este campo sirve para clasificar la estrategia o asignatura dentro de la propuesta formativa.

## Reglas de negocio
- Cada registro de Paso 5 se asocia a un solo `Programa` y a un solo `Nivel`.
- La clasificación académica debe estar disponible para:
  - filtrado en la interfaz de usuario,
  - agregación de indicadores por `Nivel`,
  - reportes de cobertura y diseño curricular.
- No se recomienda dividir las tablas según Pregrado/Posgrado si la única diferencia es la clasificación; mejor usar un atributo `Nivel`.

## Interfaz de usuario
- Debe incorporarse un filtro `Nivel` en la UI.
- El filtro debe poder combinarse con `Modalidad` y `Sede`.
- En la página `Paso 5 – Estrategias micro`, los reportes deben poder segmentarse por `Pregrado` y `Posgrado`.
