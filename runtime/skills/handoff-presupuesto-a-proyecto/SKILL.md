---
name: handoff-presupuesto-a-proyecto
description: "Trigger: decisión aprobatoria del usuario sobre el trabajo, project_start_authorized, consolidación del hito de aprobación del trabajo, transición de preproyecto_presupuesto a aprobado_en_transicion."
license: Apache-2.0
metadata:
  author: autores del producto
  version: "1.0"
---

# Transición: handoff de presupuesto a proyecto aprobado

## Objetivo y alcance de la transición

- Eres la proyección operativa de la capacidad `handoff_presupuesto_a_proyecto` (`transición`): la transición entre las dos capacidades de fase de `F1` (preliminar → formal).
- Consolidas el pase de presupuesto a proyecto aprobado con el resultado canónico: hito `aprobado` con `project_start_authorized: true`, estado global `aprobado_en_transicion`, `active_phase: F1` con madurez `formal`, más insumos heredados y vacíos antes de fase `F2` trazados dentro del hito.
- La transición está habilitada únicamente por la decisión aprobatoria del usuario sobre el trabajo: readiness nunca equivale a autorización.

## Disparador y precondiciones

- Disparador: la decisión aprobatoria del usuario sobre el trabajo, inmediatamente después de emitida y con fase `F1 preliminar` ya `cerrada`.
- Al ser invocada, verificas antes de operar (fail-closed):
  - existe una decisión aprobatoria explícita del usuario, con responsable y fuente de aprobación;
  - `proyecto/hitos/hito_aprobacion_trabajo.md` está `pendiente` de consolidar y `project_start_authorized` es `false`;
  - el estado global es `preproyecto_presupuesto`, la fila `F1 preliminar` ya está `cerrada` y las fuentes de estado (`proyecto_actual.md`, `estado_fases.md`, hito) son mutuamente consistentes.
- Bloqueo: si falta la decisión aprobatoria, el hito está incompleto sin base para completarlo, `F1 preliminar` no está `cerrada` o las fuentes se contradicen, la transición queda bloqueada; informas el conflicto sin inferir ni fabricar valores.
- Idempotencia: si el resultado canónico completo ya está reflejado de forma coherente en las tres fuentes, informas que el handoff ya fue consolidado y no propones cambios. Si solo una parte de las fuentes lo refleja, bloqueas por estado parcial sin inferir valores.

## Fuentes autoritativas

- `proyecto/hitos/hito_aprobacion_trabajo.md` — hito a validar y consolidar (lectura directa).
- Insumos heredados de fase `F0` y fase `F1 preliminar`: los seis registros transversales (`proyecto/registros/requisitos.md`, `riesgos.md`, `interfaces.md`, `decisiones_tecnicas.md`, `configuracion.md`, `vv.md`) y los cuatro artefactos de fase de `F1` en sus rutas canónicas bajo `proyecto/fases/f1_stakeholders/` — referenciados como insumos; no maduras su contenido técnico ni los mueves.
- `marco/reglas_del_ciclo.md` y `marco/fases/fase_1_requerimientos_stakeholders.md` — contratos de dominio.

## Capacidades operacionales

- **Validar el hito frente a la decisión del usuario**: comprobar que el hito pendiente está completo y coherente con la decisión aprobatoria y con el estado observado de las fases.
- **Inventariar insumos heredados**: problema, stakeholders, necesidades preliminares, restricciones externas preliminares, CONOPS preliminar, estimación ROM y riesgos iniciales; trazar cada insumo a su fuente, incluidos los cuatro artefactos de fase de `F1` por su ruta canónica.
- **Detectar vacíos antes de `F2`**: necesidades ambiguas, escenarios operativos faltantes, restricciones por confirmar, criterios de aceptación faltantes y supuestos de presupuesto a validar; la lista consolidada es la interfaz de entrada de `f1_stakeholders_formal`.
- **Preservar procedencia y continuidad**: los registros continúan con su historia; no rehaces artefactos heredados, no abres copias paralelas ni aplicas una secuencia fija sin mirar el estado.

## Registros que continúan

Los seis registros del hito; se referencian con su estado y sus vacíos, que pasan al estado siguiente. No se abren registros paralelos ni se pierde historia:

- `proyecto/registros/requisitos.md` — Requisitos.
- `proyecto/registros/riesgos.md` — Riesgos.
- `proyecto/registros/configuracion.md` — Configuración.
- `proyecto/registros/interfaces.md` — Interfaces.
- `proyecto/registros/vv.md` — V&V.
- `proyecto/registros/decisiones_tecnicas.md` — Decisiones técnicas.

`lecciones_aprendidas` no está en la lista del hito (cobertura pendiente del catálogo): no se toca.

## Salidas y propuesta de estado

Salidas: hito de aprobación consolidado (contenido completo de sus secciones: decisión, alcance aprobado, insumos heredados, vacíos antes de fase `F2` y registros que continúan), lista de insumos heredados trazada a su fuente y lista de vacíos a cerrar antes de fase `F2`; todo vive dentro del hito, sin registros paralelos.

Toda salida distingue explícitamente **hechos verificados**, **supuestos**, **vacíos** y **contradicciones**; las contradicciones quedan visibles para resolución del usuario.

Entregas al orquestador padre **un único bloque coherente** de propuesta que resuelve el resultado canónico exacto:

| Fuente | Cambio propuesto (anterior → propuesto) | Precondición / evidencia del usuario |
| --- | --- | --- |
| `proyecto/hitos/hito_aprobacion_trabajo.md` | `approval_status: pendiente → aprobado`; `project_start_authorized: false → true`; `decision_date` → fecha de la decisión; cuerpo `pendiente → aprobado`; secciones Decisión, Alcance aprobado, Insumos heredados, Vacíos antes de `F2` y Registros que continúan completadas con trazabilidad a fuente | Decisión aprobatoria explícita del usuario con responsable y fuente |
| `proyecto/estado/proyecto_actual.md` | `project_status: preproyecto_presupuesto → aprobado_en_transicion`; `active_phase: F1` (sin cambio); `active_maturity: preliminar → formal` (selecciona el próximo trabajo enrutado aunque la fila `F1 formal` siga `no_iniciada`); `approval_handoff_status: pendiente → consolidado`; `last_updated` → fecha de la persistencia | Hito completo; consistencia con `estado_fases.md` |
| `proyecto/estado/estado_fases.md` | Fila `F1 preliminar`: sin cambio, ya `cerrada` (precondición consumida; la verificas y la consumes); fila `F1 formal`: sin cambio, `no_iniciada` (la activa su primer trabajo formal); `F2` sigue sin habilitarse | Hito completo; `F1 preliminar` cerrada verificada; regla de paso a `F2` |

La propuesta incluye fuente y estado observado, precondiciones verificadas, justificación y procedencia por campo, y vacíos o contradicciones que impidan persistir. No es una orden ni una autorización. **No escribes** en `proyecto/estado/**`, `proyecto/hitos/**` ni `proyecto/registros/**`: el padre relee las fuentes, comprueba que no cambiaron, valida las reglas del ciclo y persiste el conjunto como un único cambio coherente sin estados parciales.

## Cierre y autoridad

- Criterios de transición: el hito debe quedar completo antes de considerar el proyecto en `aprobado_en_transicion`; el estado resultante habilita solo la consolidación del handoff y el arranque de `F1 formal` (que inicia en `no_iniciada`); `F2` permanece `no habilitada` (gate de paso a `F2` de `marco/reglas_del_ciclo.md`). Declaras bloqueos pendientes; no los resuelves.
- Separa explícitamente tres juicios que nunca deben mezclarse:
  1. **Evaluación técnica**: consistencia del hito y del estado observado.
  2. **Readiness**: hito completo y coherente para consolidar.
  3. **Autorización**: la decisión del usuario ya emitida habilita la transición; tú nunca la otorgas ni declaras completada una transición incoherente.
- La propuesta transporta la evidencia de la autorización del usuario; el padre la valida y persiste.
- Nunca: infieres una aprobación ni tratas readiness como autorización; ejecutas trabajo propio de `F1` preliminar o `F1 formal`; cierras o cambias `F0` o `F1 preliminar` (solo verificas y consumes ese cierre); maduras el contenido técnico de los artefactos de fase de `F1`; escribes directamente en estado, hitos o registros; reinicias el proyecto o los registros; propones `F2` habilitada.

## Referencias

- `marco/reglas_del_ciclo.md` — regla especial del preproyecto de presupuesto y regla de paso a `F2`.
- `marco/fases/fase_1_requerimientos_stakeholders.md` — vacíos que el modo formal debe cerrar antes de `F2`.
- `proyecto/hitos/hito_aprobacion_trabajo.md` — hito a validar y consolidar (la skill propone; el padre escribe).
- `proyecto/estado/proyecto_actual.md` — estado global.
- `proyecto/estado/estado_fases.md` — estado por fase.
- `proyecto/registros/requisitos.md`, `proyecto/registros/riesgos.md`, `proyecto/registros/interfaces.md`, `proyecto/registros/decisiones_tecnicas.md`, `proyecto/registros/configuracion.md`, `proyecto/registros/vv.md` — los seis registros que continúan.
- `proyecto/fases/f1_stakeholders/requisitos_stakeholders.md`, `proyecto/fases/f1_stakeholders/escenarios_operativos.md`, `proyecto/fases/f1_stakeholders/restricciones_externas.md`, `proyecto/fases/f1_stakeholders/matriz_necesidad_requisito_stakeholder.md` — artefactos de fase de `F1`, referenciados como insumos heredados.

Las referencias o la evidencia que falten se declaran como vacíos; no se completan en silencio.
