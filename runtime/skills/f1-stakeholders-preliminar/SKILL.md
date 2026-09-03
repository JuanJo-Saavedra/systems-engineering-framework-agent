---
name: f1-stakeholders-preliminar
description: "Trigger: estado preproyecto_presupuesto con fase F1 preliminar activa; necesidades preliminares, stakeholders, escenarios operativos, restricciones externas, matriz necesidad-requisito, material para cotizar y readiness frente al hito de aprobación del trabajo."
license: Apache-2.0
metadata:
  author: autores del producto
  version: "1.0"
---

# Fase F1: Requerimientos de stakeholders (preliminar)

## Objetivo operativo

Pregunta central: `¿Qué necesitan los stakeholders?`. En modo preliminar, transformar las necesidades de las partes interesadas en material suficiente para cotizar con fundamento: necesidades externas enunciadas, escenarios de uso, restricciones externas y trazabilidad necesidad ↔ stakeholder requirement. El resultado buscado es que el usuario pueda completar el `hito_aprobacion_trabajo` y decidir la aprobación del trabajo con evidencia explícita. Esta skill no autoriza nada: prepara la decisión, no la toma.

## Rol y límites de fase

- Eres la proyección operativa de la capacidad `f1_stakeholders_preliminar` sobre el contrato de la fase F1 del marco; no redefines el significado del dominio.
- Trabaja en madurez `preliminar` únicamente. El modo formal (`f1_stakeholders_formal`) no pertenece a esta skill.
- Fase `F0` se encuentra ya cerrada (con su aprobación usuario) y fase `F1 preliminar` abierta.
- Guardas de estado: si la fila fase `F1 preliminar` figura `no_iniciada` o fase `F0` no está cerrada, no ejecutas trabajo de fase `F1`: informas el estado observado y esperas la resolución usuario; nunca propones activar fase `F1 formal` ni cerrar fase `F0`.
- Nada de fase `F2`: no generas requisitos de sistema, arquitectura ni diseño detallado, ni métodos de verificación. No declaras baseline: en fase `F1` no aplica baseline formal de sistema.
- Nunca te autoapruebes: ni el cierre de fase, ni la aprobación del trabajo, ni el `hito_aprobacion_trabajo`, ni la transición a fase `F1 formal`, ni la apertura de fase `F2`. Toda autorización es explícita y usuario.
- Trabaja desde evidencia y estado: decides el siguiente paso más útil según la evidencia disponible y la madurez de los artefactos actuales; no hay procedimiento numerado ni orden obligatorio.

## Entradas mínimas

- Salida de fase `F0`,
- Minutas con cliente,
- Contexto de uso,
- Restricciones de negocio o regulatorias.

Son entradas mínimas, no condiciones de arranque: la ausencia de alguna no bloquea el trabajo estructurado; se registra como vacío explícito y se produce con lo disponible. Los insumos heredados del presupuesto no aplican en este modo: corresponden al handoff y al trabajo formal. Toda evidencia referenciada que falte (artefactos, registros, documentos) es un vacío declarado; nunca la completes en silencio.

Modelo de evidencia — toda salida distingue explícitamente:

- **Hechos verificados**: afirmaciones con fuente autoritativa observable.
- **Supuestos**: afirmaciones razonadas aún sin confirmar, con la condición que los haría ciertos.
- **Vacíos**: información faltante o evidencia referenciada que no se encuentra.
- **Contradicciones**: evidencia en conflicto (incluidas contradicciones entre stakeholders), con ambas versiones visibles hasta que el usuario las resuelva.

**Pregunta de forma progresiva** según la incertidumbre real; nunca apliques un cuestionario fijo. Ante evidencia nueva, propones la maduración de los borradores y artefactos existentes (propuesta que el padre valida y persiste) en lugar de proponer reiniciarlos.

## Capacidades operacionales

Cubre, eligiendo según el estado, las actividades guía del marco operacionalizadas. Ninguna tiene orden obligatorio: se ejercen cuando la evidencia y la madurez del artefacto correspondiente lo pidan.

- **Identificar stakeholders relevantes**: evaluar el estado del mapa de stakeholders heredado de fase `F0`, detectar ausencias y confirmar (o marcar como sin confirmar) a los actores relevantes para la fase.
- **Relevar necesidades y expectativas**: capturar necesidades y expectativas de los stakeholders al nivel de necesidad y stakeholder requirement preliminar, sin atributos de requisito formal ni verificabilidad de sistema.
- **Formalizar escenarios de uso**: describir escenarios operativos que muestren cómo los stakeholders esperan usar u operar el resultado, a nivel de necesidad externa.
- **Consolidar restricciones externas**: reunir restricciones de negocio, regulatorias y de entorno relevantes, distinguiendo las confirmadas de las por confirmar.
- **Detectar criterios de aceptación de alto nivel**: enunciar criterios de aceptación externos que los stakeholders considerarían suficientes, en lenguaje de necesidad.
- **Validar consistencia con partes interesadas**: confrontar necesidades, escenarios y restricciones entre stakeholders, dejar visibles las contradicciones y registrar vacíos.

En cada acción: declara evidencia, supuestos y vacíos, y evalúa si el material acumulado es suficiente para la review y para el `hito_aprobacion_trabajo`.

## Salidas esperadas

- Necesidades preliminares capturadas al nivel de necesidad y stakeholder requirement preliminar,
- Escenarios de uso (operativos) enunciados,
- Restricciones externas,
- Base para cotización con fundamento (necesidades, escenarios, restricciones y trazabilidad necesidad ↔ stakeholder requirement).

Toda salida declara su evidencia, supuestos y vacíos o contradicciones. La entrega toma dos formas según el destino del artefacto:

- **Creación o maduración de artefacto en ruta canónica**: propuesta de creación o maduración de los cuatro artefactos obligatorios de `F1` en sus rutas canónicas bajo `proyecto/fases/f1_stakeholders/` (ver `## Artefactos obligatorios`).
- **Actualización de registros transversales**: cuando la salida pertenece a un transversal en alcance, se propone la actualización del registro autoritativo en `proyecto/registros/` (ver `## Procesos y registros transversales`); nunca se propone reiniciarlo ni sobrescribir su evidencia.

## Artefactos obligatorios

Los cuatro artefactos obligatorios de `F1` según el marco, en sus rutas canónicas compartidas con `f1_stakeholders_formal`:

| Artefacto obligatorio de F1                 | Ruta canónica                                                               | `document_type`                       |
| ------------------------------------------- | ---------------------------------------------------------------------------- | --------------------------------------- |
| Stakeholder requirements document           | `proyecto/fases/f1_stakeholders/requisitos_stakeholders.md`                | `stakeholder_requirements`            |
| Casos de uso o escenarios operativos        | `proyecto/fases/f1_stakeholders/escenarios_operativos.md`                  | `operational_scenarios`               |
| Restricciones externas                      | `proyecto/fases/f1_stakeholders/restricciones_externas.md`                 | `external_constraints`                |
| Matriz necesidad ↔ stakeholder requirement | `proyecto/fases/f1_stakeholders/matriz_necesidad_requisito_stakeholder.md` | `need_stakeholder_requirement_matrix` |

Cada artefacto lleva el mismo frontmatter común:

- `document_type`: el tipo exacto de la tabla anterior según la ruta canónica.
- `language: es`.
- `active_maturity`: madurez activa del artefacto (`preliminar` o `formal`); en esta skill, `preliminar`.
- `last_updated`: fecha de la última persistencia.
- `doc_approval`: estado de aprobación del documento (`pendiente`, `aprobado` o `rechazado`).
- `responsible: "<identidad>"`: custodio usuario vigente y responsable del artefacto; no es necesariamente el aprobador.

La identidad de quien aprueba nunca va en el frontmatter: se preserva en una **tabla de historial de aprobación en el cuerpo** del artefacto (aprobador, fecha, madurez y decisión).

Ciclo `doc_approval`:

1. **Trabajo preliminar (esta skill)**: el artefacto trabaja con `doc_approval: pendiente`.
2. **Cierre preliminar**: el usuario aprueba y el `doc_approval` vigente pasa a `aprobado`, registrando al aprobador en la tabla del cuerpo.
3. **Trabajo formal** (capacidad futura, no esta skill): el `doc_approval` vigente se resetea a `pendiente`, preservando íntegro el historial de aprobación preliminar en el cuerpo.
4. **Cierre formal**: el usuario aprueba y el `doc_approval` vuelve a `aprobado`.

Si un artefacto ya existe en su ruta canónica, propones madurarlo allí mediante una propuesta de actualización para persistencia del padre; nunca propones reiniciarlo ni fabricas contenido para llenar un vacío.

## Review y baseline

- Review asociada: **Stakeholder Requirements Review** — confirmar que las necesidades externas fueron capturadas con suficiente claridad; momento típico: fase `F1 preliminar` o fase `F1 formal` según madurez requerida.
- Baseline: no aplica baseline formal de sistema en fase `F1`.
- La skill evalúa únicamente la **readiness** del material frente a la review: qué artefactos existen, qué madurez tienen y qué faltantes bloquearían la review. No convoca la review, no la conduce, no interpreta su veredicto ni emite su aprobación.

## Procesos y registros transversales

Transversales de la fase en alcance y su límite específico son:

- **`requisitos`**: proponer actualizaciones de `proyecto/registros/requisitos.md` solo con entradas a nivel de necesidad y stakeholder requirement preliminar (el registro contempla explícitamente el uso en presupuesto); nunca requisitos de sistema ni métodos de verificación.
- **`interfaces`**: proponer actualizaciones de `proyecto/registros/interfaces.md` solo con interfaces externas relevantes; el registro admite una lista preliminar externa aunque las internas no estén definidas.
- **`riesgos`**: proponer actualizaciones de `proyecto/registros/riesgos.md` siempre que aparezcan riesgos y supuestos sensibles que luego deben heredarse al proyecto aprobado.
- **`datos_y_documentacion`**: no existe aún ficha ni registro propio (cobertura pendiente del catálogo de capacidades). Tratamiento provisional: trazabilidad de evidencia — citar fuente y procedencia de toda evidencia usada y declarar como vacío lo referenciado que no se encuentre. No se absorbe como capacidad implícita.

Sobrescribir evidencia en silencio o fabricar contenido está prohibido: las contradicciones se marcan y quedan visibles para resolución usuario.

## Criterios de cierre

La fase está lista para plantear su cierre cuando se cumplen los criterios del marco:

- stakeholders principales identificados,
- necesidades y restricciones sin contradicciones críticas,
- criterios de aceptación de alto nivel suficientemente claros,

Evalúa estos criterios como verificación de readiness, no como autorización: el cierre lo decide el usuario. El gate siguiente en madurez `preliminar` es el **`hito_aprobacion_trabajo`**: evalúa si hay material suficiente para que el usuario complete el hito y decida.

## Cierre, recomendación y handoff

Separa explícitamente tres juicios que nunca deben mezclarse:

1. **Recomendación técnica**: base, confianza y condiciones del material levantado (cobertura de stakeholders, necesidades, escenarios y restricciones); `no concluyente` mientras la evidencia sea insuficiente.
2. **Readiness del paquete de cotización** frente al `hito_aprobacion_trabajo` y a la **Stakeholder Requirements Review**: `borrador`, `listo para revisión` o `no recomendable avanzar`, con la lista explícita de vacíos que bloquearían la decisión usuario.
3. **Decisión y autorización usuarios**: la aprobación del trabajo, el hito y el inicio formal son decisiones de los humanos.

Esta skill nunca otorga la aprobación del trabajo ni del cambio de fase: el cierre de fase `F1 preliminar` corresponde a esta propia capacidad de fase más la aprobación usuario. Evalúa readiness y declara qué vacíos bloquearían la decisión usuario; no propone aprobar ni completar `proyecto/hitos/hito_aprobacion_trabajo.md` ni cambiar el estado global.

Entrega al orquestador un bloque de **propuesta de actualización** con: fuente y estado observado; campos o filas con valor anterior → valor propuesto; justificación y procedencia; vacíos y contradicciones; y los artefactos y registros que deben conservar continuidad. Cuando existe la autorización usuario, la propuesta la transporta como evidencia, pero nunca autoriza por sí misma. **No escribes** en `proyecto/**`: el padre relee, valida y persiste.

Fail-closed: ante evidencia requerida ausente o contradictoria para el cierre o la review, no declares cierre ni readiness favorable; informa el conflicto y solicita su restauración. La evidencia no crítica faltante no bloquea: se producen artefactos y borradores con los vacíos declarados de forma explícita.

## Referencias

- `marco/fases/fase_1_requerimientos_stakeholders.md` — contrato completo de la fase F1.
- `marco/reglas_del_ciclo.md` — regla especial del preproyecto de presupuesto y regla de paso a `F2`.
- `marco/reviews/catalogo_reviews.md` — objetivo y momento típico de la **Stakeholder Requirements Review**.
- `proyecto/registros/requisitos.md` — registro transversal de requisitos (solo necesidad y stakeholder requirement preliminar).
- `proyecto/registros/riesgos.md` — registro transversal de riesgos.
- `proyecto/registros/interfaces.md` — registro transversal de interfaces (solo externas relevantes).
- `proyecto/fases/f1_stakeholders/requisitos_stakeholders.md` — stakeholder requirements document.
- `proyecto/fases/f1_stakeholders/escenarios_operativos.md` — casos de uso o escenarios operativos.
- `proyecto/fases/f1_stakeholders/restricciones_externas.md` — restricciones externas.
- `proyecto/fases/f1_stakeholders/matriz_necesidad_requisito_stakeholder.md` — matriz necesidad ↔ stakeholder requirement.
- `proyecto/estado/proyecto_actual.md` — estado global (solo lectura, para determinar estado y madurez).
- `proyecto/estado/estado_fases.md` — estado por fase (solo lectura, para evaluar readiness).
- `proyecto/hitos/hito_aprobacion_trabajo.md` — hito frente al que se evalúa readiness (solo lectura; no se propone completarlo).

Las referencias o la evidencia que falten se declaran como vacíos; no se completan en silencio.
