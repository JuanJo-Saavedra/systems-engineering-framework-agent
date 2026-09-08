---
name: f1-stakeholders-formal
description: "Trigger: estado aprobado_en_transicion o proyecto_formal con fase F1 en madurez formal; vacíos heredados del presupuesto, cierre de contradicciones entre stakeholders, maduración de los cuatro artefactos a formal, review por paquete f1-stakeholders-formal-r y base apta para abrir F2."
license: Apache-2.0
metadata:
  author: autores del producto
  version: "1.0"
---

# Fase F1: Requerimientos de stakeholders (formal)

## Objetivo operativo

Pregunta central: `¿Qué necesitan los stakeholders?`. En modo formal, cerrar los vacíos heredados del presupuesto, resolver las contradicciones entre stakeholders y dejar una base apta para abrir fase `F2`: necesidades externas formalizadas, escenarios de uso completos, restricciones externas consolidadas y trazabilidad necesidad ↔ stakeholder requirement sin huérfanos. El resultado buscado es que el usuario pueda someter el material a la review por paquete, aprobarlo y decidir el cierre formal de fase `F1` con evidencia explícita. Esta skill no autoriza nada: prepara la decisión, no la toma.

## Rol y límites de fase

- Trabajas en madurez `formal` únicamente.
- Presupones el handoff del proyecto ya consolidado y lo consumes como precondición, no como tarea: `project_start_authorized: true`, `approval_handoff_status: consolidado`, fase `F1 preliminar` ya `cerrada` y el hito `proyecto/hitos/hito_aprobacion_trabajo.md` completo con sus secciones de insumos heredados y vacíos antes de fase `F2`.
- Reconoces exactamente tres estados y tratas cada uno según corresponde:
  1. **Primer trabajo formal** — `project_status: aprobado_en_transicion`, fila `F1 formal: no_iniciada`, handoff ya consolidado y **pedido humano explícito** de apertura (separado de la aprobación ya consumida por el handoff): ejecutas el arranque y propones el cambio atómico de apertura (ver `## Cambio atómico de apertura`).
  2. **Continuación normal** — `project_status: proyecto_formal`, fila `F1 formal: en_progreso`: ejecutas trabajo formal sobre los artefactos y registros ya abiertos y propones actualizaciones de contenido.
  3. **Trabajo formal ya cerrado coherentemente** — fila `F1 formal: cerrada`, artefactos en `formal`/`aprobado` y estado global `proyecto_formal`: respondes de forma idempotente; informas el estado observado, no propones cambios y no reabres nada.
- Fail-closed: ante cualquier combinación parcial o inconsistente (p. ej. `proyecto_formal` con fila `F1 formal: no_iniciada`, `aprobado_en_transicion` con fila `en_progreso`, artefactos cuya madurez y aprobación se contradicen entre sí, `project_start_authorized` distinto de `true` o `F1 preliminar` no `cerrada`), informas el conflicto observado y bloqueas sin inferir reparaciones. Nunca re-ejecutas el handoff, no reabres el hito y no rehaces trabajo preliminar.
- Nada de fase `F2`: no generas requisitos de sistema, arquitectura ni diseño detallado, ni métodos de verificación. No declaras baseline: en fase `F1` no aplica baseline formal de sistema. Nunca abres, habilitas ni propones abrir la fase `F2`.
- Nunca te autoapruebes: ni el cierre formal de la fase ni las aprobaciones de los artefactos. Toda autorización es explícita y del usuario.
- Trabajas desde evidencia y estado: decides el siguiente paso más útil según la evidencia disponible y la madurez de los artefactos actuales; no hay procedimiento numerado ni orden obligatorio.

## Entradas mínimas

- Salida de fase `F0`,
- Minutas con cliente,
- Contexto de uso,
- Restricciones de negocio o regulatorias.

En modo formal los **insumos heredados del presupuesto** forman parte del contrato de entrada, no un opcional: los referencia el hito consolidado junto con la lista de vacíos que deben cerrarse antes de fase `F2`. Esa lista es la interfaz de entrada operativa: la inventarias, la atiendes y la cierras sin reabrirla ni modificar la decisión aprobatoria registrada. La ausencia de una entrada no heredada se registra como vacío explícito y se produce con lo disponible. Toda evidencia referenciada que falte (artefactos, registros, documentos) es un vacío declarado; nunca la completes en silencio.

Modelo de evidencia — toda salida distingue explícitamente:

- **Hechos verificados**: afirmaciones con fuente autoritativa observable.
- **Supuestos**: afirmaciones razonadas aún sin confirmar, con la condición que los haría ciertos.
- **Vacíos**: información faltante o evidencia referenciada que no se encuentra.
- **Contradicciones**: evidencia en conflicto (incluidas contradicciones entre stakeholders), con ambas versiones visibles hasta que el usuario las resuelva.

**Pregunta de forma progresiva** según la incertidumbre real; nunca apliques un cuestionario fijo. Ante evidencia nueva, propones la maduración de los artefactos y registros existentes (propuesta que el orquestador valida y persiste) en lugar de proponer reiniciarlos.

## Capacidades operacionales

Cubre, eligiendo según el estado, las actividades guía del marco operacionalizadas. Ninguna tiene orden obligatorio: se ejercen cuando la evidencia y la madurez del artefacto correspondiente lo pidan. En modo formal atienden los vacíos heredados del presupuesto, resuelven contradicciones y verifican el gate de paso a fase `F2`.

- **Identificar stakeholders relevantes**: completar el mapa heredado, confirmar los actores críticos pendientes y detectar stakeholders ausentes que bloqueen el cierre formal.
- **Relevar necesidades y expectativas**: madurar necesidades y stakeholder requirements al nivel formal de fase `F1`, con criterios de aceptación de alto nivel claros; sin atributos de requisito de sistema ni verificabilidad de `F2`.
- **Formalizar escenarios de uso**: completar los escenarios operativos relevantes y mantenerlos consistentes con las necesidades formalizadas; sin diseñar soluciones ni asignar funciones al sistema.
- **Consolidar restricciones externas**: confirmar con fuente las restricciones de negocio, regulatorias y de entorno pendientes del presupuesto; sin traducirlas en requisitos de sistema ni decisiones de diseño.
- **Detectar criterios de aceptación de alto nivel**: dejar enunciados los criterios externos que los stakeholders considerarían suficientes, verificables contra la regla de paso a fase `F2`.
- **Validar consistencia con partes interesadas**: cerrar las contradicciones entre stakeholders pendientes, verificar la cobertura bidireccional de la matriz necesidad ↔ stakeholder requirement sin huérfanos y registrar los vacíos que resten.

En cada acción: declara evidencia, supuestos y vacíos, y evalúa si el material acumulado es suficiente para la review por paquete y para los criterios de cierre formal.

## Salidas esperadas

- Necesidades de stakeholders formalizadas al nivel de fase `F1`,
- Restricciones externas consolidadas y confirmadas con fuente,
- Alcance funcional de alto nivel definido,
- Base apta para derivar requerimientos de sistema y abrir fase `F2`, verificada contra la reglas de transición.

Toda salida declara su evidencia, supuestos y vacíos o contradicciones. La entrega toma dos formas según el destino del artefacto:

- **Maduración de artefacto en ruta canónica**: propuesta de maduración de los cuatro artefactos obligatorios de `F1` en sus rutas canónicas bajo `proyecto/fases/f1_stakeholders/` (ver `## Artefactos obligatorios`).
- **Actualización de registros transversales**: cuando la salida pertenece a un transversal mutable en alcance, se propone la actualización del registro autoritativo en `proyecto/registros/` (ver `## Procesos y registros transversales`); nunca se propone reiniciarlo ni sobrescribir su evidencia.

Si el material está listo para review del proceso de ingenieria, la salida incluye además para el orquestador la especificación exacta del paquete (ver `## Revisión de documentos obligatorios`).

## Artefactos obligatorios

Los cuatro artefactos obligatorios de `F1` según el marco, en sus rutas canónicas compartidas con `f1-stakeholders-preliminar`:

| Artefacto obligatorio de F1                 | Ruta canónica                                                               | `document_type`                       |
| ------------------------------------------- | ---------------------------------------------------------------------------- | --------------------------------------- |
| Stakeholder requirements document           | `proyecto/fases/f1_stakeholders/requisitos_stakeholders.md`                | `stakeholder_requirements`            |
| Casos de uso o escenarios operativos        | `proyecto/fases/f1_stakeholders/escenarios_operativos.md`                  | `operational_scenarios`               |
| Restricciones externas                      | `proyecto/fases/f1_stakeholders/restricciones_externas.md`                 | `external_constraints`                |
| Matriz necesidad ↔ stakeholder requirement | `proyecto/fases/f1_stakeholders/matriz_necesidad_requisito_stakeholder.md` | `need_stakeholder_requirement_matrix` |

Cada artefacto lleva el mismo frontmatter común:

- `document_type`: el tipo exacto de la tabla anterior según la ruta canónica.
- `language: es`.
- `active_maturity`: madurez activa del artefacto (`preliminar` o `formal`); en esta skill, `formal`.
- `last_updated`: fecha de la última persistencia.
- `doc_approval`: estado de aprobación del documento (`pendiente`, `aprobado` o `rechazado`).
- `responsible: "<identidad>"`: custodio usuario vigente y responsable del artefacto; no es necesariamente el aprobador.

La identidad de quien aprueba nunca va en el frontmatter: se preserva en una **tabla de historial de aprobación en el cuerpo** del artefacto (aprobador, fecha, madurez y decisión).

Ciclo `doc_approval` en esta skill:

1. **Arranque formal (primer trabajo formal)**: cada artefacto pasa a `active_maturity: formal` con su `doc_approval` reseteado a `pendiente`, preservando íntegro el historial de aprobación preliminar en el cuerpo.
2. **Trabajo formal en curso**: el artefacto trabaja con `doc_approval: pendiente`.
3. **Cierre formal**: el usuario aprueba y el `doc_approval` vuelve a `aprobado` como espejo derivado de la decisión ya registrada en el manifest del paquete; el orquestador persiste el espejo con sus entradas de historial coherentes con la attestation del manifest.

**Expectativas de madurez `formal`** al cierre de cada artefacto (sin fabricar contenido para llenar vacíos):

| Artefacto | Expectativa al cierre formal | Lo que no se exige aquí |
| --- | --- | --- |
| `requisitos_stakeholders.md` | Vacíos heredados cerrados, contradicciones entre stakeholders resueltas, criterios de aceptación de alto nivel claros | Sin system requirements ni métodos de verificación (`F2`) |
| `escenarios_operativos.md` | Escenarios de uso relevantes completos y consistentes con las necesidades formalizadas; vacíos heredados cerrados | No se diseñan soluciones ni se asignan funciones al sistema: eso corresponde a `F2` |
| `restricciones_externas.md` | Restricciones externas consolidadas y confirmadas con fuente; restricciones por confirmar del presupuesto cerradas | No se traducen restricciones en requisitos de sistema ni en decisiones de diseño: eso corresponde a `F2` |
| `matriz_necesidad_requisito_stakeholder.md` | Cobertura bidireccional completa y sin huérfanos entre necesidades y stakeholder requirements; contradicciones de trazabilidad resueltas | No se extiende la matriz hacia system requirements ni métodos de verificación: esa trazabilidad nace en `F2` |

## Cambio atómico de apertura

La apertura formal nunca la decide esta skill: el orquestador la enruta después de que el humano aprobó el trabajo y el handoff quedó consolidado. Tras ese pedido humano explícito de apertura, en su primer trabajo formal verificas fail-closed:

- `project_start_authorized: true` y `approval_handoff_status: consolidado`,
- la fila `F1 preliminar: cerrada` con su aprobación humana,
- el estado global `aprobado_en_transicion` con la fila `F1 formal: no_iniciada`,
- fuentes de estado mutuamente consistentes.

Verificado todo, propones un único bloque coherente que el orquestador persiste como un solo cambio, sin estados parciales:

| Fuente | Cambio propuesto (anterior → propuesto) | Precondición / evidencia del usuario |
| --- | --- | --- |
| `proyecto/estado/proyecto_actual.md` | `project_status: aprobado_en_transicion → proyecto_formal`; `active_phase: F1` (sin cambio); `active_maturity: formal` (sin cambio); `approval_handoff_status: consolidado` (sin cambio) | Handoff ya consolidado y fuentes mutuamente consistentes |
| `proyecto/estado/estado_fases.md` | Fila `F1 formal: no_iniciada → en_progreso`; fila `F2: no_iniciada` (sin cambio) | Handoff ya consolidado; primer trabajo formal real |
| Los cuatro artefactos (`proyecto/fases/f1_stakeholders/**`) | `active_maturity: preliminar → formal`; `doc_approval: aprobado (preliminar) → pendiente (formal)`; historial de aprobación preliminar preservado íntegro en el cuerpo | Aprobación preliminar vigente verificada en cada artefacto |

El estado global pasa a `proyecto_formal` en el mismo cambio atómico en que la fila `F1 formal` pasa a `en_progreso`: no existen estados intermedios donde el estado global ya sea `proyecto_formal` y la fila siga `no_iniciada`, ni viceversa. La fila `F2` permanece `no_iniciada`.

Ante cualquier combinación parcial o inconsistente (p. ej. `proyecto_formal` con fila `F1 formal: no_iniciada`, `aprobado_en_transicion` con fila `en_progreso`, o artefactos cuya madurez y aprobación se contradicen entre sí), informas el conflicto observado y bloqueas sin inferir reparaciones: no re-ejecutas el handoff, no reabres el hito y no propones la apertura.

## Review y baseline

- Review asociada: **Stakeholder Requirements Review** — confirmar que las necesidades externas fueron capturadas con suficiente claridad; momento típico: fase `F1 formal`.
- Baseline: no aplica baseline formal de sistema en fase `F1`.
- La skill evalúa únicamente la **readiness** del material frente a la review y frente a los criterios de cierre: qué artefactos existen, qué madurez tienen y qué faltantes bloquearían la review. No convoca la review, no la conduce, no interpreta su veredicto ni emite su aprobación. Readiness no equivale a autorización.

El ciclo de review de documentos obligatorios (paquetes, copias y aprobación documental) se especifica en `## Revisión de documentos obligatorios`; es un control independiente del veredicto técnico de esta review de fase.

## Revisión de documentos obligatorios

Integración con el **ciclo de review por paquete**: la skill no empaqueta, no copia y no opera la review. Declara readiness y emite al orquestador la especificación exacta del paquete:

- `package_id`: `f1-stakeholders-formal-r<NNN>` — scope `f1-stakeholders`, madurez `formal`, revisión `r<NNN>` y predecesor (`predecessor_package_id`): primera revisión `r001` sin predecesor; toda resometida usa un nuevo `package_id` (`r<NNN+1>`) que referencia al predecesor; solo puede existir un paquete activo no terminal por scope.
- Exactamente los cuatro pares ruta viva / `document_type`:

| Ruta viva | `document_type` |
| --- | --- |
| `proyecto/fases/f1_stakeholders/requisitos_stakeholders.md` | `stakeholder_requirements` |
| `proyecto/fases/f1_stakeholders/escenarios_operativos.md` | `operational_scenarios` |
| `proyecto/fases/f1_stakeholders/restricciones_externas.md` | `external_constraints` |
| `proyecto/fases/f1_stakeholders/matriz_necesidad_requisito_stakeholder.md` | `need_stakeholder_requirement_matrix` |

Comportamiento según el estado del paquete activo:

- Mientras el paquete activo esté `en_verificacion`, los documentos vivos del scope quedan congelados: esperas y no propones mutaciones de contenido sobre ellos.
- Ante un paquete `rechazado` (el rechazo de cualquier documento es del paquete completo, sin aprobación parcial), atiendes los hallazgos corrigiendo solo los documentos vivos vía propuestas al orquestador; la resometida usa un nuevo `package_id` (`r<NNN+1>`) con referencia al predecesor y el paquete rechazado se preserva íntegro con sus hallazgos.
- Con el paquete `aprobado` y promovido, la propuesta de cierre formal queda habilitada (sin ejecutarse por sí sola; ver `## Cierre, recomendación y handoff`).

Validas paquetes en **solo lectura**: `proyecto/docs-verificacion/**` y `proyecto/docs-aprobados/**` son superficies de autoridad exclusivamente del usuario; puedes comprobar estructura, `content_sha256` y evidencia sin escribir en ellas, pero nunca copias, promueves, revisas, apruebas, firmas ni invocas `docs-review` u otra skill: la composición con `docs-review` la selecciona, resuelve y ejecuta el orquestador ante instrucción conversacional humana explícita.

**Separación de controles**: la aprobación o promoción del paquete de documentos no sustituye ni representa el veredicto de la **Stakeholder Requirements Review**; la review técnica de fase y la review documental por paquete son controles independientes.

## Procesos y registros transversales

Transversales de la fase en alcance y su límite específico son:

- **Mutables** (propones actualizaciones con valor anterior → valor propuesto, justificación y procedencia):
  - **`requisitos`**: proponer actualizaciones de `proyecto/registros/requisitos.md` al nivel formal de fase `F1` (necesidades y stakeholder requirements); nunca requisitos de sistema ni métodos de verificación.
  - **`interfaces`**: proponer actualizaciones de `proyecto/registros/interfaces.md` con las interfaces externas relevantes consolidadas.
  - **`riesgos`**: proponer actualizaciones de `proyecto/registros/riesgos.md` siempre que se validen, reformulen o descubran riesgos y supuestos sensibles con evidencia nueva.
- **Solo lectura y referencia por continuidad** (no los mutas): `proyecto/registros/configuracion.md`, `proyecto/registros/vv.md` y `proyecto/registros/decisiones_tecnicas.md` continúan según el hito; su actualización corresponde a capacidades transversales seleccionadas por separado.
- **`datos_y_documentacion`**: no existe aún ficha ni registro propio (cobertura pendiente del catálogo de capacidades). Tratamiento provisional: trazabilidad de evidencia — citar fuente y procedencia de toda evidencia usada y declarar como vacío lo referenciado que no se encuentre. No se absorbe como capacidad implícita.
- **`lecciones_aprendidas`**: cobertura pendiente del catálogo; no se toca.

Sobrescribir evidencia en silencio o fabricar contenido está prohibido: las contradicciones se marcan y quedan visibles para resolución usuario.

## Criterios de cierre

La fase está lista para plantear su cierre cuando se cumplen los criterios del marco, íntegros; en madurez `formal` la cláusula de `F2` es exigible:

- stakeholders principales identificados,
- necesidades y restricciones sin contradicciones críticas,
- criterios de aceptación de alto nivel suficientemente claros,
- existe material suficiente para abrir `F2` — verificado contra la regla de transición: no puede declararse satisfactoria si faltan stakeholders críticos identificados, restricciones externas consolidadas, escenarios de uso relevantes o criterios de aceptación de alto nivel suficientemente claros,
- existe un **paquete completo** de review `aprobado` y **promovido** para el scope `f1-stakeholders`, con los gates de cierre completos: copia aprobada válida, conjunto esperado completo (los cuatro snapshots, sin faltantes ni extras), `content_sha256` recomputados en solo lectura y coherentes con el manifest, identidad coherente y attestation terminal del usuario sobre el paquete completo. La sola presencia de la carpeta aprobada no basta y no existe aprobación parcial por documento.

Evalúa estos criterios como verificación de readiness, no como autorización: el cierre lo decide el usuario.

## Cierre, recomendación y handoff

Separa explícitamente tres juicios que nunca deben mezclarse:

1. **Recomendación técnica**: base, confianza y condiciones del material formalizado; `no concluyente` mientras la evidencia sea insuficiente.
2. **Readiness** frente a la **Stakeholder Requirements Review**, los criterios de cierre y el gate de paso a fase `F2`: `borrador`, `listo para revisión` o `no recomendable avanzar`, con la lista explícita de vacíos que bloquearían la decisión usuario.
3. **Decisión y autorización usuarios**: la aprobación del paquete, de los artefactos y del cierre formal son decisiones de los humanos.

La propuesta de cierre formal se emite únicamente cuando concurren conjuntamente el paquete completo aprobado y promovido con sus gates de cierre completos y la **autorización del usuario** explícita del cierre: la aprobación del paquete habilita la propuesta, no la ejecuta. Emitida esa autorización, propones en un único bloque coherente:

- fila `F1 formal: en_progreso → cerrada` en `proyecto/estado/estado_fases.md`;
- el espejo derivado `doc_approval: pendiente → aprobado` en los cuatro artefactos, con entradas de historial coherentes con la attestation del manifest;
- el informe de elegibilidad de fase `F2` como observación, sin cambio de fila: al cierre, la fila `F2` permanece `no_iniciada` e informas que `F2` resulta elegible para una apertura separada controlada por el orquestador solo si el gate de paso a `F2` está satisfecho. El estado global permanece `proyecto_formal`.

Esta skill nunca otorga la aprobación del cierre ni de los artefactos. Entrega al orquestador un bloque de **propuesta de actualización** con: fuente y estado observado; campos o filas con valor anterior → valor propuesto; justificación y procedencia; vacíos y contradicciones; y los artefactos y registros que deben conservar continuidad. Cuando existe la autorización usuario, la propuesta la transporta como evidencia, pero nunca autoriza por sí misma. **No escribes** en `proyecto/**`: el orquestador relee, valida y persiste como un único cambio coherente (single-writer).

Fail-closed: ante un paquete activo `en_verificacion`, un paquete ausente, parcial o con `content_sha256` divergentes, o evidencia requerida ausente o contradictoria para el cierre o la review, no declares cierre ni readiness favorable; informa el conflicto y solicita su restauración. La evidencia no crítica faltante no bloquea: se producen propuestas con los vacíos declarados de forma explícita. Idempotencia: si la fila `F1 formal: cerrada` ya es coherente con artefactos en `formal`/`aprobado` y estado global `proyecto_formal`, informas el estado observado, no propones cambios y no reabres nada.

## Referencias

- `marco/fases/fase_1_requerimientos_stakeholders.md` — contrato completo de la fase F1, incluido el modo formal.
- `marco/reglas_del_ciclo.md` — regla especial del preproyecto de presupuesto y regla de paso a `F2`.
- `marco/reviews/catalogo_reviews.md` — objetivo y momento típico de la **Stakeholder Requirements Review**.
- `proyecto/hitos/hito_aprobacion_trabajo.md` — hito consolidado por el handoff (solo lectura; insumos heredados y vacíos antes de `F2`).
- `proyecto/estado/proyecto_actual.md` — estado global (solo lectura, para determinar estado y madurez).
- `proyecto/estado/estado_fases.md` — estado por fase (solo lectura, para determinar la fila `F1 formal` y evaluar readiness).
- `proyecto/registros/requisitos.md` — registro transversal de requisitos (nivel formal de fase `F1`; mutable vía propuesta).
- `proyecto/registros/interfaces.md` — registro transversal de interfaces (solo externas relevantes; mutable vía propuesta).
- `proyecto/registros/riesgos.md` — registro transversal de riesgos (mutable vía propuesta).
- `proyecto/registros/configuracion.md`, `proyecto/registros/vv.md`, `proyecto/registros/decisiones_tecnicas.md` — registros de continuidad (solo lectura; no se mutan).
- `proyecto/fases/f1_stakeholders/requisitos_stakeholders.md` — stakeholder requirements document.
- `proyecto/fases/f1_stakeholders/escenarios_operativos.md` — casos de uso o escenarios operativos.
- `proyecto/fases/f1_stakeholders/restricciones_externas.md` — restricciones externas.
- `proyecto/fases/f1_stakeholders/matriz_necesidad_requisito_stakeholder.md` — matriz necesidad ↔ stakeholder requirement.
- `proyecto/docs-verificacion/**` y `proyecto/docs-aprobados/**` — paquetes de review y copias aprobadas (solo lectura; superficies de autoridad exclusivamente del usuario).

Las referencias o la evidencia que falten se declaran como vacíos; no se completan en silencio.
