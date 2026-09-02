---
document_type: arquitectura_capacidades
language: es
version: 2.2
status: canonico
---

# Arquitectura canónica de capacidades del framework

## Propósito

Este archivo es el catálogo canónico, legible por humanos y versionado, de las capacidades de dominio del orquestador de runtime. Define qué asistencia puede dar el sistema, cuándo aplica, qué entradas autoritativas exige, qué salidas produce y qué guardas la limitan. No describe el estado de un proyecto puntual: eso vive en `proyecto/`.

> Rutas citadas en las fichas: `marco/…` y `AGENTS.md` son las **rutas instaladas** que el runtime lee en el proyecto destino. En el repo de producto, el dominio vive en `framework/marco/` (instalado como `marco/`) y el contrato de runtime en `runtime/AGENTS.md` (instalado como `AGENTS.md`).

## Qué es y qué no es

| Este catálogo es | Este catálogo NO es |
| --- | --- |
| Fuente de qué asistencia existe, cuándo aplica y qué exige. | Contrato de persona/comportamiento — eso es el contrato de runtime (`runtime/AGENTS.md`, instalado como `AGENTS.md`). |
| La base para **seleccionar** una capacidad según el estado del proyecto. | Un `SKILL.md` ejecutable ni instrucciones de procedimiento. |
| Fuente de dominio, junto con `framework/marco/` (instalado como `marco/`). | Una lista de skills/subagentes instalados. |
| Catálogo versionado y mantenido a mano. | Estado del proyecto — eso vive en `proyecto/`. |

## Contrato de transformación (marco → skill operativa)

Las skills operativas (`runtime/skills/**/SKILL.md`) son **proyecciones** de capacidades de este catálogo, no manuales ni checklists: conservan los conceptos relevantes de la capacidad del marco y los adaptan a comportamiento consciente del estado del proyecto — producir y actualizar artefactos, declarar preparación de review y explicitar cierre y handoff. La decisión de artefactos y capas de autoridad vive en [skill-artifacts.md](../../docs/decisions/skill-artifacts.md).

Contrato de nombres:

| Nivel | Convención | Ejemplo | Estabilidad |
| --- | --- | --- | --- |
| Identificador conceptual de capacidad (encabezado de ficha y `bindings` aquí) | `snake_case` | `f0_factibilidad` | Estable: no cambia al renombrar el ejecutable. |
| Nombre ejecutable (directorio de la skill, frontmatter `name`, `id` en el registry operativo) | `kebab-case` | `f0-factibilidad` | Cambia solo con edición explícita del registry y del `bindings` de la ficha. |

El **binding** entre ambos niveles se declara en el campo `bindings` de la ficha y en el registry operativo; ningún `SKILL.md` redefine el significado del dominio.

Reglas de la transformación:

- La estructura de `framework/marco/` se **preserva**: una skill de fase no reordena ni reescribe el contrato de su fase.
- Una skill de fase puede adaptar las `Actividades guía` del marco como **`Capacidades operacionales`**: la misma cobertura conceptual, expresada como comportamiento operativo (cuándo producir, actualizar, revisar y cerrar), sin duplicar el contenido de dominio del marco.
- Cobertura pendiente: `datos_y_documentacion` y `lecciones_aprendidas` **no** están cubiertas por este catálogo. Son decisiones de cobertura pendientes, no capacidades implícitas: no existen como fichas y ninguna skill puede asumirlas sin que este catálogo las defina antes.

## Selección vs ejecución

La selección de capacidad y el enlace con un ejecutable están separados:

1. **Selección (orquestador padre).** Lee el estado autoritativo del proyecto y este catálogo, y elige la capacidad que corresponde.
2. **Descubrimiento de ejecutables (harness).** La metadata de skills expuesta por el harness y los índices técnicos generados solo indican qué implementación ejecutable existe y dónde.
3. **Enlace / binding (adaptador).** El `SKILL.md` o el subagente exacto es un adaptador ejecutable; nunca redefine el significado del dominio.
4. **Enrutamiento (orquestador padre).** Un harness concreto (por ejemplo Codex) no evalúa nativamente los disparadores de fase; el padre lee `proyecto/estado/`, selecciona y enruta.

Regla: ninguna capa inferior (skill, subagente, índice, adaptador) es autoridad sobre el significado del dominio.

## Frente al generador de índice técnico de gentle-ai

`docs/history/skill-registry-gentle-ai.md` es la referencia **histórica** de una skill generadora: escanea rutas de `SKILL.md` instaladas y produce un registro técnico distinto. Un ejemplo de su salida es `.atl/skill-registry.md`, que es el índice técnico generado, **no** una ruta fuente que se escanea. Ese índice:

- descubre implementaciones ejecutables ya instaladas;
- es generado y de alcance técnico/operativo;
- **no** es el catálogo canónico del dominio y **no** debe fusionarse con este archivo.

Se usa como complemento de descubrimiento, nunca como fuente del significado de las capacidades.

## Algoritmo de enrutamiento

El orquestador padre aplica estos pasos en orden:

1. **Leer el estado global** desde `proyecto/estado/proyecto_actual.md`, `proyecto/estado/estado_fases.md` y `proyecto/hitos/hito_aprobacion_trabajo.md` (fase activa, madurez, aprobación).
2. **Clasificar la tarea**: madurar una fase, garantizar consistencia transversal, producir/revisar un artefacto puntual o coordinar.
3. **Elegir UNA capacidad primaria** según la clasificación y el estado.
4. **Añadir SOLO las capacidades transversales afectadas** por la salida (no todas).
5. **Resolver el enlace ejecutable disponible** a partir de la metadata del harness o del índice técnico generado.
6. **Cargar las instrucciones exactas** del enlace (su `SKILL.md`) antes de trabajar.
7. **Reportar honestamente** si el enlace está degradado o ausente (ver Modo degradado).

### Prioridad según estado

| Estado | Prioridad |
| --- | --- |
| `preproyecto_presupuesto` | `F0`, `F1 preliminar`, riesgos iniciales y handoff. |
| `aprobado_en_transicion` | Consolidación del hito de aprobación y cierre de vacíos de `F1 formal`. |
| `proyecto_formal` | Capacidad de la fase activa y transversales afectadas. |

Regla de tarea puntual: para producir o revisar un artefacto, usar primero la capacidad de tarea puntual y luego validar consistencia con la capacidad transversal afectada.

## Guardrails comunes

Todas las capacidades respetan estas guardas, sin repetirlas en cada ficha:

- No inventar estado, entregables ni evidencia.
- Sin evidencia autoritativa, señalarlo y pedirla; no asumir.
- Respetar los gates de fase y la madurez esperada; no abrir la fase siguiente si el criterio de cierre no está satisfecho.
- Tratar reviews y baselines como hitos formales.
- Single-writer: el padre actualiza los documentos autoritativos; los ejecutables producen salidas que el padre consolida.
- El Markdown autoritativo de `proyecto/` gana en cualquier conflicto.

## Modo degradado y fallos

| Situación | Comportamiento |
| --- | --- |
| Sin skill/subagente ejecutable para la capacidad | No autoriza inventar estado ni saltar gates. |
| Enlace ausente pero tarea segura | Proceder inline solo desde `AGENTS.md` + `marco/` + registros autoritativos, y declarar modo degradado. |
| Evidencia requerida ausente o corrupta (fase, review, baseline) | Fallar cerrado y solicitar restauración; la disponibilidad de skill no cambia esta regla. |

Las transiciones de fase, las reviews y las baselines permanecen fail-closed ante evidencia requerida ausente, independientemente de la disponibilidad de skills o subagentes.

## Esquema de ficha de capacidad

| Campo | Obligatorio | Qué captura |
| --- | --- | --- |
| `id` | sí | Identificador estable y único (el encabezado, p. ej. `f0_factibilidad`). No cambia al renombrar un ejecutable. |
| `tipo` | sí | Categoría: `orquestación general`, `control de avance`, `fase`, `transición`, `transversal` o `tarea puntual`. |
| `cuando_usarla` | sí | Condiciones de activación: estado, fase, madurez o tarea que la justifican. |
| `fuentes_autoritativas` | sí | Entradas obligatorias que leer antes de producir salida (rutas de dominio/registros). |
| `salidas_esperadas` | sí | Resultados que debe producir la capacidad. |
| `guardrails_cierre` | sí | Guardas y condiciones de salida específicas; si no difieren, se heredan las guardas comunes. |
| `fase_objetivo` | condicional | Solo para capacidades de `fase` o `transición`. |
| `madurez_esperada` | condicional | Solo cuando aplica (`preliminar` o `formal`). |
| `estado_implementacion` | sí | Nivel de madurez del enlace ejecutable: `definida`, `mapeada` o `verificada`. Valor por defecto global (`definida`); una ficha lo anula declarando su propio valor (v2.2). |
| `bindings` | sí | Mapeo a skill/subagente ejecutable cuando exista evidencia. Valor por defecto global (ninguno); una ficha lo anula declarando su propio binding (v2.2). Hoy ninguno está verificado. |

## Madurez de implementación

Las etiquetas describen hasta dónde llega el enlace ejecutable de una capacidad, no la calidad del dominio.

| Etiqueta | Significado |
| --- | --- |
| `definida` | La capacidad está definida en el dominio y descrita en este catálogo; aún no hay un ejecutable verificado. |
| `mapeada` | Existe un enlace declarado a una skill o subagente, sin verificación de comportamiento completa. |
| `verificada` | El enlace pasó pruebas de comportamiento (selección, degradación, fronteras). |

Estado por defecto: **todas las capacidades están en `definida` salvo anulación explícita en su ficha**. Este catálogo no declara ningún enlace ejecutable verificado; hoy solo `f0_factibilidad` declara un enlace (`mapeada`).

En v2.0, `estado_implementacion` y `bindings` se declaraban una sola vez de forma global cuando el valor era uniforme para todo el catálogo. Desde v2.2 la regla es **valor por defecto global + anulación por ficha**: una ficha que declara sus propios campos `estado_implementacion` y `bindings` anula el valor por defecto solo para esa capacidad; el resto del catálogo permanece bajo el valor global.

## Catálogo de capacidades

### Capacidades del orquestador

#### `orquestacion_del_proyecto`

- **Tipo**: orquestación general
- **Cuándo usarla**: siempre que se necesite decidir el siguiente paso, la fase activa, la madurez esperada o las reglas de avance.
- **Fuentes autoritativas**:
  - `AGENTS.md`
  - `proyecto/estado/proyecto_actual.md`
  - `proyecto/estado/estado_fases.md`
  - `proyecto/hitos/hito_aprobacion_trabajo.md`
- **Salidas esperadas**:
  - estado interpretado del proyecto,
  - fase activa confirmada,
  - siguiente decisión o entregable crítico,
  - capacidad recomendada y modo de ejecución (inline o delegado).
- **Guardrails**: no reemplaza la lectura del estado; no declara un subagente por defecto; no ejecuta transiciones de fase.

#### `gap_analysis_de_fase`

- **Tipo**: control de avance
- **Cuándo usarla**: antes de cerrar una fase, antes de una review o cuando no se sabe qué falta.
- **Fuentes autoritativas**:
  - contrato de fase en `marco/fases/`
  - estado de fase
  - registros transversales relevantes
- **Salidas esperadas**:
  - faltantes,
  - bloqueos,
  - riesgos de pasar de fase prematuramente.
- **Guardrails**: no cierra fases ni emite aprobaciones; reporta faltantes y, sin evidencia, falla cerrado.

### Capacidades por fase

#### `f0_factibilidad`

- **Tipo**: fase
- **Fase objetivo**: `F0`
- **Madurez esperada**: `preliminar`
- **Cuándo usarla**: para transformar una necesidad en problema, contexto, ROM, riesgos y recomendación Go/No-Go, y para declarar la preparación del dossier frente a la MCR.
- **Fuentes autoritativas**:
  - `marco/fases/fase_0_concepto_y_factibilidad.md`
  - `proyecto/registros/riesgos.md`
  - `proyecto/registros/requisitos.md`
  - `proyecto/registros/decisiones_tecnicas.md`
- **Salidas esperadas**:
  - problema formulado,
  - CONOPS preliminar,
  - estimación ROM con rango, base, supuestos, exclusiones y confianza,
  - riesgos iniciales,
  - recomendación de continuidad (`Go`, `No-Go` o `no concluyente`),
  - declaración de readiness del dossier para la `MCR / Concept Review`.
- **Guardrails de cierre**:
  - permanece en madurez `preliminar`; sin requisitos de sistema (`F2`), arquitectura (`F3`) ni diseño detallado (`F4`);
  - evalúa solo la readiness del dossier frente a la MCR: no la convoca, la conduce ni la aprueba; en `F0` no aplica baseline formal;
  - separa recomendación técnica (`Go`/`No-Go`/`no concluyente`), readiness del dossier (`borrador`, `listo para revisión`, `no recomendable avanzar`) y decisión humana; nunca se autoaprueba la transición a `F1 preliminar`;
  - un artefacto obligatorio de `F0` sin ruta autoritativa en `proyecto/` se entrega como borrador estructurado marcado `ubicación pendiente`: no se inventan rutas ni se fabrica o sobrescribe evidencia en silencio;
  - transversales dentro de su alcance: `riesgos` siempre; `requisitos` solo a nivel de necesidad preliminar; `decisiones_tecnicas` solo si una decisión temprana afecta la factibilidad.
- **Estado de implementación**: `mapeada` (anula el valor por defecto global de `definida`).
- **Bindings**: `f0_factibilidad` → skill `f0-factibilidad` (`runtime/skills/f0-factibilidad/SKILL.md`; instalada como `.agents/skills/f0-factibilidad/SKILL.md`).

#### `f1_stakeholders_preliminar`

- **Tipo**: fase
- **Fase objetivo**: `F1`
- **Madurez esperada**: `preliminar`
- **Cuándo usarla**: durante presupuesto, para capturar necesidades y restricciones a alto nivel sin forzar detalle técnico.
- **Fuentes autoritativas**:
  - `marco/fases/fase_1_requerimientos_stakeholders.md`
  - `proyecto/registros/requisitos.md`
  - `proyecto/registros/riesgos.md`
  - `proyecto/registros/interfaces.md`
- **Salidas esperadas**:
  - necesidades preliminares,
  - escenarios de uso,
  - restricciones externas,
  - base para cotización.

#### `handoff_presupuesto_a_proyecto`

- **Tipo**: transición
- **Fase objetivo**: `F1`
- **Madurez esperada**: `formal`
- **Cuándo usarla**: inmediatamente después de la aprobación del trabajo.
- **Fuentes autoritativas**:
  - `proyecto/hitos/hito_aprobacion_trabajo.md`
  - `proyecto/estado/proyecto_actual.md`
  - salidas heredadas de `F0` y `F1 preliminar`
- **Salidas esperadas**:
  - hito de aprobación consolidado,
  - lista de insumos heredados,
  - lista de vacíos a cerrar antes de `F2`.

#### `f1_stakeholders_formal`

- **Tipo**: fase
- **Fase objetivo**: `F1`
- **Madurez esperada**: `formal`
- **Cuándo usarla**: luego de la aprobación, para completar necesidades, restricciones y criterios de aceptación de alto nivel.
- **Fuentes autoritativas**:
  - `marco/fases/fase_1_requerimientos_stakeholders.md`
  - `proyecto/hitos/hito_aprobacion_trabajo.md`
  - `proyecto/registros/requisitos.md`
  - `proyecto/registros/interfaces.md`
  - `proyecto/registros/riesgos.md`
- **Salidas esperadas**:
  - stakeholder requirements formalizados,
  - contradicciones resueltas,
  - base apta para abrir `F2`.

#### `f2_requisitos_sistema`

- **Tipo**: fase
- **Fase objetivo**: `F2`
- **Madurez esperada**: `formal`
- **Cuándo usarla**: para derivar requerimientos técnicos verificables y trazables.
- **Fuentes autoritativas**:
  - `marco/fases/fase_2_requerimientos_sistema.md`
  - `proyecto/registros/requisitos.md`
  - `proyecto/registros/vv.md`
  - `proyecto/registros/configuracion.md`
- **Salidas esperadas**:
  - SyRS,
  - trazabilidad necesidad ↔ requisito,
  - método de verificación por requisito.

#### `f3_arquitectura`

- **Tipo**: fase
- **Fase objetivo**: `F3`
- **Madurez esperada**: `formal`
- **Cuándo usarla**: para seleccionar arquitectura, asignar requisitos e identificar interfaces.
- **Fuentes autoritativas**:
  - `marco/fases/fase_3_definicion_arquitectura.md`
  - `proyecto/registros/requisitos.md`
  - `proyecto/registros/interfaces.md`
  - `proyecto/registros/decisiones_tecnicas.md`
- **Salidas esperadas**:
  - arquitectura seleccionada,
  - CIs identificados,
  - trade-offs documentados,
  - base para `PDR`.

#### `f4_diseno_detallado`

- **Tipo**: fase
- **Fase objetivo**: `F4`
- **Madurez esperada**: `formal`
- **Cuándo usarla**: para preparar documentación build-to, code-to e integrate-to.
- **Fuentes autoritativas**:
  - `marco/fases/fase_4_diseno_detallado.md`
  - `proyecto/registros/configuracion.md`
  - `proyecto/registros/interfaces.md`
  - `proyecto/registros/vv.md`
- **Salidas esperadas**:
  - diseño liberable,
  - PBS final,
  - base para `CDR`.

#### `f5_integracion`

- **Tipo**: fase
- **Fase objetivo**: `F5`
- **Madurez esperada**: `formal`
- **Cuándo usarla**: para registrar configuración integrada, anomalías y readiness de verificación.
- **Fuentes autoritativas**:
  - `marco/fases/fase_5_integracion_y_modelo_de_ingenieria.md`
  - `proyecto/registros/configuracion.md`
  - `proyecto/registros/riesgos.md`
  - `proyecto/registros/interfaces.md`
- **Salidas esperadas**:
  - configuración del EM,
  - anomalías y NCRs,
  - readiness para `F6`.

#### `f6_verificacion`

- **Tipo**: fase
- **Fase objetivo**: `F6`
- **Madurez esperada**: `formal`
- **Cuándo usarla**: para organizar evidencia objetiva y estado de cumplimiento.
- **Fuentes autoritativas**:
  - `marco/fases/fase_6_verificacion.md`
  - `proyecto/registros/vv.md`
  - `proyecto/registros/requisitos.md`
  - `proyecto/registros/configuracion.md`
- **Salidas esperadas**:
  - matriz requisito ↔ evidencia,
  - estado de NCRs,
  - readiness para validación.

#### `f7_validacion`

- **Tipo**: fase
- **Fase objetivo**: `F7`
- **Madurez esperada**: `formal`
- **Cuándo usarla**: para confirmar adecuación al uso y aceptación.
- **Fuentes autoritativas**:
  - `marco/fases/fase_7_validacion.md`
  - `proyecto/registros/vv.md`
  - `proyecto/registros/riesgos.md`
  - `proyecto/registros/decisiones_tecnicas.md`
- **Salidas esperadas**:
  - escenarios validados,
  - hallazgos operativos,
  - aceptación o desvío residual.

#### `f8_transferencia`

- **Tipo**: fase
- **Fase objetivo**: `F8`
- **Madurez esperada**: `formal`
- **Cuándo usarla**: para consolidar baseline final, soporte inicial y cierre técnico.
- **Fuentes autoritativas**:
  - `marco/fases/fase_8_produccion_transferencia_soporte.md`
  - `proyecto/registros/configuracion.md`
  - `proyecto/registros/lecciones_aprendidas.md`
  - `proyecto/registros/decisiones_tecnicas.md`
- **Salidas esperadas**:
  - baseline final,
  - paquete de transferencia,
  - cierre técnico.

### Capacidades transversales

#### `trazabilidad`

- **Tipo**: transversal
- **Cuándo usarla**: cuando se deba conectar necesidad, requisito, CI, método de verificación y evidencia.
- **Fuentes autoritativas**:
  - `proyecto/registros/requisitos.md`
  - `proyecto/registros/vv.md`
- **Salidas esperadas**:
  - matriz o enlaces de trazabilidad completos,
  - huecos detectados.

#### `riesgos_y_oportunidades`

- **Tipo**: transversal
- **Cuándo usarla**: cuando aparezcan supuestos sensibles, decisiones de alto impacto o bloqueos de fase.
- **Fuentes autoritativas**:
  - `proyecto/registros/riesgos.md`
  - review o fase activa
- **Salidas esperadas**:
  - riesgo registrado,
  - criticidad,
  - acción y responsable.

#### `configuracion_y_baselines`

- **Tipo**: transversal
- **Cuándo usarla**: ante cambios de versiones, cortes de baseline o preparación de release/review.
- **Fuentes autoritativas**:
  - `proyecto/registros/configuracion.md`
  - `marco/baselines/catalogo_baselines.md`
- **Salidas esperadas**:
  - items identificados,
  - versionado claro,
  - baseline asociada.

#### `interfaces`

- **Tipo**: transversal
- **Cuándo usarla**: al aparecer nuevas interfaces o cambios entre disciplinas.
- **Fuentes autoritativas**:
  - `proyecto/registros/interfaces.md`
  - artefactos de arquitectura o diseño
- **Salidas esperadas**:
  - interfaz definida,
  - responsable,
  - impacto de cambio.

#### `verificacion_y_validacion`

- **Tipo**: transversal
- **Cuándo usarla**: para evitar mezcla entre verificación y validación o para planificar cierres.
- **Fuentes autoritativas**:
  - `proyecto/registros/vv.md`
  - fase activa
- **Salidas esperadas**:
  - estrategia de cierre clara,
  - evidencia esperada,
  - estado de cumplimiento.

#### `decisiones_tecnicas`

- **Tipo**: transversal
- **Cuándo usarla**: cuando haya trade-offs, selecciones tecnológicas, make/buy/reuse o aceptación de desvíos.
- **Fuentes autoritativas**:
  - `proyecto/registros/decisiones_tecnicas.md`
- **Salidas esperadas**:
  - decisión explicitada,
  - alternativas evaluadas,
  - criterio usado,
  - impacto técnico y programático.

### Capacidades de tarea puntual

#### `redaccion_de_artefacto`

- **Tipo**: tarea puntual
- **Cuándo usarla**: para redactar o reestructurar un documento concreto de fase.
- **Fuentes autoritativas**:
  - contrato de fase aplicable
  - registros transversales relevantes
- **Salidas esperadas**:
  - artefacto redactado de forma consistente con el marco.

#### `preparacion_de_review`

- **Tipo**: tarea puntual
- **Cuándo usarla**: antes de MCR, SRR, PDR, CDR, SIR/EMR, TRR, SAR o review de transferencia.
- **Fuentes autoritativas**:
  - `marco/reviews/catalogo_reviews.md`
  - fase activa
  - registros y artefactos relevantes
- **Salidas esperadas**:
  - paquete de review,
  - entry criteria evaluado,
  - lista de faltantes y observaciones.

## Mantenimiento

Este catálogo cambia cuando cambia la **semántica de una capacidad del dominio**: qué asistencia existe, cuándo aplica, qué entradas exige, qué salidas produce o qué guardas la limitan.

No es necesario tocar este archivo cuando solo cambia:

- una implementación ejecutable (contenido de un `SKILL.md`),
- una ruta instalada,
- un enlace de adaptador,
- el índice técnico generado (por ejemplo `.atl/skill-registry.md`).

Esos cambios pertenecen a los mapeos/índices técnicos y al adaptador, no necesariamente a este catálogo.

Reglas adicionales:

- Si el marco cambia de estructura, revisar rutas y fuentes autoritativas.
- Si una capacidad se vuelve demasiado grande, dividirla en dos: una de producción y otra de control.
- Ante una capacidad nueva, usar el esquema de ficha y dejarla en `definida` hasta que exista evidencia de enlace verificable.

## Relacionado

- [AGENTS.md](../../runtime/AGENTS.md) — contrato de runtime (fuente canónica).
- [orchestrator.md](../../docs/architecture/orchestrator.md) — capas y adaptador.
- [domain-harness-boundary.md](../../docs/architecture/domain-harness-boundary.md) — autoridad y dependencias.
- [memory.md](../../docs/architecture/memory.md) — autoridad de memoria.
- [quickstart.md](../../docs/guides/quickstart.md) — flujo mínimo.
- [agents-contract.md](../../docs/decisions/agents-contract.md) — decisión canónica: contrato único de `AGENTS.md`.
- [skill-registry-gentle-ai.md](../../docs/history/skill-registry-gentle-ai.md) — referencia histórica de la skill generadora del índice técnico (no canónica para el dominio).
- [skill-artifacts.md](../../docs/decisions/skill-artifacts.md) — decisión canónica: capas de autoridad (marco, catálogo, skills operativas, espejo de empaquetado) y registry operativo.
