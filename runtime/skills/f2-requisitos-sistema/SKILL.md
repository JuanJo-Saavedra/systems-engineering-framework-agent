---
name: f2-requisitos-sistema
description: "Trigger: estado proyecto_formal con fase F2 activa o fila F2 no_iniciada con el gate de paso a F2 satisfecho; derivación de requerimientos de sistema verificables y trazables, dos matrices de trazabilidad, plan V&V preliminar, traducir las necesidades y stakeholders requirements en requerimientos tecnicos verificables y trazables. SRR y constitución de la Functional Baseline. "
license: Apache-2.0
metadata:
  author: autores del producto
  version: "1.0"
---

# Fase F2: Requerimientos de sistema

## Objetivo operativo

Pregunta central: `¿Qué debe hacer técnicamente el sistema?`. Traducir las necesidades y stakeholder requirements formalizados y aprobados en `F1 formal` en requerimientos de sistema claros, verificables y trazables, con métodos de verificación preliminares definidos, interfaces externas preliminares identificadas y trazabilidad completa necesidad ↔ requisito ↔ método de verificación. El resultado habilita la **Functional Baseline**: el material queda apto para someterse a la review por paquete, ser revisado por la `SRR` y constituir la baseline al cierre autorizado de la fase. El humano decide reviews, veredicto, cierre y baseline; esta skill no autoriza nada: prepara la decisión, no la toma.

## Rol y límites de fase

- Trabajas en madurez `formal` únicamente: `F2` nace formal y **no existe modo preliminar** en esta fase. Ningún artefacto de la fase adopta nunca madurez preliminar, no hay ciclo de madurez preliminar a formal y no existen copias por madurez.
- Presupones `F1 formal` cerrada y el gate de paso a `F2` satisfecho; consumes esas salidas aprobadas como contrato de entrada, no como tarea.
- Reconoces exactamente tres estados y tratas cada uno según corresponde:
  1. **Primer trabajo** — `project_status: proyecto_formal`, fila `F2: no_iniciada`, `F1 formal: cerrada` y gate de paso a `F2` satisfecho: verificas el gate fail-closed y propones el cambio atómico de apertura (ver `## Cambio atómico de apertura`).
  2. **Continuación normal** — fila `F2: en_progreso` con estado global `proyecto_formal`: ejecutas trabajo sobre requerimientos, matrices, plan y registros; esperas sin proponer mutaciones mientras el paquete activo esté `en_verificacion`.
  3. **Fase ya cerrada coherentemente** — fila `F2: cerrada`, artefactos en `formal`/`aprobado` y Functional Baseline registrada: respondes de forma idempotente; informas el estado observado, no propones cambios y no reabres nada.
- Fail-closed: ante cualquier combinación parcial o inconsistente (`F1 formal` no `cerrada`, fila `F2` distinta de `no_iniciada` en el primer trabajo, paquete `f1-stakeholders` sin promover, regla de paso a `F2` insatisfecha, estado global distinto de `proyecto_formal`), informas el conflicto observado y bloqueas sin inferir reparaciones. Nunca reabres el hito de aprobación de `F1`, no rehaces trabajo preliminar ni alteras la decisión aprobatoria registrada.
- Regla dominante de la fase: **no mezclas requerimiento con solución**. Tu foco es claridad técnica, verificabilidad y trazabilidad. Un requerimiento de `F2` describe **qué** debe hacer el sistema, nunca **cómo** se implementa.
- Nada de `F3`: no seleccionas arquitectura, no asignas requisitos a subsistemas ni CIs, no produces trade-offs arquitectónicos ni diseño detallado (`F4`). Nunca abres, habilitas ni propones abrir la fase `F3`.
- Nunca te autoapruebes: ni el veredicto de la `SRR`, ni la constitución de la baseline, ni el cierre de la fase, ni las aprobaciones de los artefactos. Toda autorización es explícita y del usuario.

## Entradas mínimas

- `F1 formal` cerrada,
- stakeholder requirements aprobados,
- restricciones externas consolidadas,
- normativa aplicable,
- supuestos y decisiones de arranque ya explicitados.

Las entradas heredadas aprobadas de `F1` (necesidades, stakeholder requirements, escenarios de uso, restricciones externas, criterios de aceptación de alto nivel y la trazabilidad necesidad ↔ stakeholder requirement sin huérfanos, promovidos en el paquete `f1-stakeholders`) forman el **contrato de entrada**; su ausencia bloquea (fail-closed). La ausencia de una entrada no crítica se registra como vacío explícito y se produce con lo disponible; las entradas heredadas no se reescriben ni se reabren.

Modelo de evidencia — toda salida distingue explícitamente:

- **Hechos verificados**: afirmaciones con fuente autoritativa observable.
- **Supuestos**: afirmaciones razonadas aún sin confirmar, con la condición que los haría ciertos.
- **Vacíos**: información faltante o evidencia referenciada que no se encuentra.
- **Contradicciones**: evidencia en conflicto, con ambas versiones visibles hasta que el usuario las resuelva.

**Pregunta de forma progresiva** según la incertidumbre real; nunca apliques un cuestionario fijo. Ante evidencia nueva propones la maduración de los artefactos y registros existentes (propuesta que el orquestador valida y persiste) en lugar de reiniciarlos.

## Capacidades operacionales

Cubre, eligiendo según el estado y la evidencia, las siete actividades guía del marco operacionalizadas. Ninguna tiene orden obligatorio; cada salida distingue hechos verificados, supuestos, vacíos y contradicciones.

- **Derivar requerimientos técnicos**: traducir necesidades y stakeholder requirements en requerimientos de sistema con atributos completos (ID, fuente, redacción, rationale, prioridad, asignación, método de verificación previsto, estado), sin huérfanos hacia arriba.
- **Clasificar requerimientos**: agrupar por tipo (funcional, desempeño, restricción, interfaz) manteniendo un solo identificador por requisito.
- **Revisar consistencia y completitud**: detectar ambigüedades, contradicciones y faltantes entre el SyRS, las matrices y los registros; declararlas como contradicciones, nunca resolverlas renumerando.
- **Analizar verificabilidad**: comprobar que cada requisito es comprobable; un requisito sin forma de verificarse es un vacío o una contradicción declarada.
- **Identificar interfaces externas preliminares**: levantar las interfaces externas relevantes como **sección del SyRS**, sin mutar el registro transversal de interfaces.
- **Definir método de verificación por requerimiento**: asignar a cada requisito su método previsto (inspección, análisis, demostración, ensayo) y referenciar el plan V&V preliminar.
- **Construir trazabilidad**: mantener las **dos matrices separadas** (necesidad ↔ requisito; requisito ↔ método de verificación) con los mismos IDs que el SyRS y los registros.

En cada acción: declara evidencia, supuestos y vacíos, y evalúa si el material acumulado es suficiente para la review por paquete y para los criterios de cierre de la fase.

## Salidas esperadas

- Requerimientos de sistema claros, verificables y trazables (SyRS),
- métodos de verificación preliminares definidos por requisito,
- trazabilidad necesidad → requisito → método de verificación al 100 % (dos matrices separadas, sin huérfanos),
- supuestos y restricciones técnicos registrados,
- plan V&V preliminar consolidado,
- baseline funcional preparada: material apto para la `SRR` y para la constitución de la Functional Baseline al cierre autorizado.

Toda salida declara su evidencia, supuestos y vacíos o contradicciones. La entrega toma dos formas según el destino:

- **Maduración de artefacto en ruta canónica**: propuesta de actualización de los cinco artefactos obligatorios bajo `proyecto/fases/f2_requisitos_sistema/` (ver `## Artefactos obligatorios`).
- **Actualización de registros transversales**: propuesta sobre `proyecto/registros/` para los transversales mutables en alcance (ver `## Procesos y registros transversales`); nunca se reinicia un registro ni se sobrescribe su evidencia.

Si el material está listo para la review del proceso de ingeniería, la salida incluye además para el orquestador la especificación exacta del paquete (ver `## Revisión de documentos obligatorios`) y la declaración de **readiness** frente a la `SRR`.

## Artefactos obligatorios

Los cinco artefactos obligatorios de `F2` según el marco, en sus rutas canónicas:

| Artefacto obligatorio de F2 | Ruta canónica | `document_type` |
| --- | --- | --- |
| SyRS — especificación de requerimientos de sistema | `proyecto/fases/f2_requisitos_sistema/requisitos_sistema.md` | `system_requirements` |
| Matriz necesidad ↔ requisito de sistema | `proyecto/fases/f2_requisitos_sistema/matriz_necesidad_requisito_sistema.md` | `need_system_requirement_matrix` |
| Matriz requisito ↔ método de verificación | `proyecto/fases/f2_requisitos_sistema/matriz_requisito_metodo_verificacion.md` | `system_requirement_verification_method_matrix` |
| Registro de supuestos y restricciones | `proyecto/fases/f2_requisitos_sistema/supuestos_y_restricciones.md` | `assumptions_and_constraints` |
| Plan V&V preliminar | `proyecto/fases/f2_requisitos_sistema/plan_vv_preliminar.md` | `preliminary_vv_plan` |

Cada artefacto lleva el mismo frontmatter común:

- `document_type`: el tipo exacto de la tabla anterior según la ruta canónica.
- `language: es`.
- `active_maturity`: siempre `formal` en esta fase.
- `last_updated`: fecha de la última persistencia.
- `doc_approval`: estado de aprobación del documento; `pendiente` durante todo el trabajo, `aprobado` solo como espejo derivado de la decisión registrada en el manifest del paquete promovido.
- `responsible: "<identidad>"`: custodio usuario vigente y responsable del artefacto; no es necesariamente el aprobador.

La identidad de quien aprueba nunca va en el frontmatter: se preserva en una **tabla de historial de aprobación en el cuerpo** del artefacto (aprobador, fecha, madurez y decisión).

**Convención de IDs (inmutable):** todo requerimiento de sistema usa el formato `SYS-REQ-0001` (prefijo fijo más cuatro dígitos), único y permanente por proyecto. Los IDs nunca se reutilizan, renumeran ni reciclan — ni siquiera tras un rechazo o eliminación del requisito — y son idénticos en el SyRS, ambas matrices, `proyecto/registros/requisitos.md` y `proyecto/registros/vv.md`. Cualquier divergencia de formato o de identidad entre esas superficies es una contradicción declarada, no una renumeración.

**Trazabilidad como dos matrices separadas** (artefactos propios que no se fusionan): la matriz necesidad ↔ requisito responde si todo requisito deriva de una necesidad real y toda necesidad está cubierta; la matriz requisito ↔ método de verificación responde cómo se comprobará cada requisito y detecta requisitos no verificables. Un ID que exista en una matriz y no en la otra, o que difiera del SyRS o de los registros, es una contradicción declarada.

Ciclo `doc_approval` en esta skill (lineal, sin reset por madurez):

1. **Apertura**: los cinco artefactos se crean con `active_maturity: formal` y `doc_approval: pendiente`.
2. **Trabajo**: los artefactos trabajan con `doc_approval: pendiente`; mientras el paquete activo esté `en_verificacion` quedan congelados contra mutación (verificación por `content_sha256`).
3. **Cierre**: el `doc_approval` pasa a `aprobado` solo como espejo derivado de la decisión ya registrada en el manifest del paquete promovido; el orquestador persiste el espejo con entradas de historial coherentes con la attestation del manifest.

## Cambio atómico de apertura

Primer trabajo de la fase (gate de paso a `F2` verificado fail-closed): propones un único bloque coherente que el orquestador persiste como un solo cambio, sin estados parciales:

| Fuente | Cambio propuesto (anterior → propuesto) | Precondición / evidencia |
| --- | --- | --- |
| `proyecto/estado/estado_fases.md` | `F2: no_iniciada → en_progreso`; fila `F1 formal: cerrada` (sin cambio); fila `F3: no_iniciada` (sin cambio) | Gate de paso a `F2` verificado fail-closed |
| `proyecto/estado/proyecto_actual.md` | `active_phase: F1 → F2`; `active_maturity: formal` (sin cambio); `project_status: proyecto_formal` (sin cambio) | Consistencia con `estado_fases.md` |
| Los cinco artefactos (`proyecto/fases/f2_requisitos_sistema/**`) | Creación con `active_maturity: formal` y `doc_approval: pendiente`; sin contenido fabricado para llenar vacíos | Rutas canónicas |

El estado global **no cambia** de valor en la apertura: `F2` abre dentro del estado `proyecto_formal` ya vigente. No existen estados intermedios donde la fila `F2` esté `en_progreso` sin que los cinco artefactos existan en sus rutas canónicas, ni viceversa.

## Review y baseline

- Review asociada: **SRR / System Requirements Review** — confirmar que los requerimientos de sistema son correctos, completos, trazables y verificables; momento típico: cierre de `F2`.
- Baseline asociada: **Functional Baseline** — define qué debe hacer el sistema y se constituye solo por la conjunción de cierre; se registra atómicamente en `proyecto/registros/configuracion.md` con el cierre autorizado.
- La skill evalúa únicamente la **readiness** del material frente a la `SRR` y frente a los criterios de cierre: qué artefactos existen, qué cobertura tienen las matrices y qué faltantes bloquearían la review. Readiness no equivale a autorización.
- La skill nunca convoca, conduce ni emite veredicto de la `SRR`: la preparación del dossier la compone el orquestador con la capacidad genérica `preparacion-de-review`, la review técnica la conduce y decide el equipo humano contra la revisión congelada, y el veredicto lo registra el padre — con autorización humana explícita, single-writer — en `proyecto/registros/reviews.md` (cuando exista su plantilla) ligado al `package_id` congelado, al conjunto de artefactos y a sus hashes.
- La secuencia de revisión congelada es obligatoria: el paquete se somete y congela **antes** de la `SRR` y el veredicto se emite contra esa revisión exacta; el detalle del ciclo de paquete vive en `## Revisión de documentos obligatorios`.

## Revisión de documentos obligatorios

Integración con el **ciclo de review por paquete**: la skill no empaqueta, no copia y no opera la review. Declara readiness y emite al orquestador la especificación exacta del paquete:

- `package_id`: `f2-requisitos-sistema-formal-r<NNN>` — scope `f2-requisitos-sistema`, madurez `formal`, revisión `r<NNN>`: primera revisión `r001` sin predecesor; toda resometida usa un nuevo `package_id` (`r<NNN+1>`) con `predecessor_package_id`; solo puede existir un paquete activo no terminal por scope.
- Exactamente los cinco pares ruta viva / `document_type`:

| Ruta viva | `document_type` |
| --- | --- |
| `proyecto/fases/f2_requisitos_sistema/requisitos_sistema.md` | `system_requirements` |
| `proyecto/fases/f2_requisitos_sistema/matriz_necesidad_requisito_sistema.md` | `need_system_requirement_matrix` |
| `proyecto/fases/f2_requisitos_sistema/matriz_requisito_metodo_verificacion.md` | `system_requirement_verification_method_matrix` |
| `proyecto/fases/f2_requisitos_sistema/supuestos_y_restricciones.md` | `assumptions_and_constraints` |
| `proyecto/fases/f2_requisitos_sistema/plan_vv_preliminar.md` | `preliminary_vv_plan` |

**Secuencia congelada obligatoria** (el orden canónico de las seis etapas no se altera):

| Etapa | Actor / autoridad | Acción / evidencia | Resultado / paso siguiente |
| --- | --- | --- | --- |
| Fase en curso | Skill `f2-requisitos-sistema` (trabajo vía propuestas al orquestador) | Fila `F2: en_progreso`: los cinco artefactos mutables vía propuestas | La skill declara **readiness** frente a la `SRR`: observación, nunca autorización |
| Preparación de Review | Orquestador con `preparacion-de-review` (tipo: `SRR`, fase: `F2`) | Compone y recibe el **dossier técnico**; el dossier referencia el scope y el `package_id` esperados sin crearlos ni operarlos | Dossier con **bloqueos o faltantes** → regresa al trabajo de fase y la preparación se repite tras corregir; sin bloqueos → etapa siguiente |
| Autorización y verificación de documentos | Humano (autorización explícita) + orquestador (ejecución) | Con el dossier sin bloqueos, el humano autoriza `Prepare` + `Submit` (operaciones **pre-review**): el conjunto exacto de los cinco documentos se copia, hashea y manifiesta | El paquete entra `en_verificacion` y los documentos vivos quedan **congelados contra mutación** (`content_sha256`) |
| Revisión técnica SRR | Equipo humano de ingeniería | Conduce la `SRR` **contra esa revisión exacta congelada** (`package_id` + hashes del manifest) | Veredicto técnico emitido sobre la revisión congelada |
| Resultados de la revisión técnica | Equipo humano (veredicto); padre registra en `proyecto/registros/reviews.md` con autorización humana explícita | El veredicto queda ligado al `package_id` congelado, al conjunto de los cinco artefactos y a los hashes del manifest; la revisión revisada se preserva | **Desfavorable o condicionado con bloqueadores abiertos**: cierre bloqueado y resometida trazable `r<NNN+1>` (con `predecessor_package_id`) que repite la preparación con `preparacion-de-review` y la review técnica; **favorable sin bloqueadores abiertos**: permite, pero no implica, `RecordDecision`+`Promote` (operaciones **post-veredicto**) |
| Documento aprobado y Functional Baseline | Humano (decisión documental y cierre); orquestador (persistencia, single-writer) | El humano autoriza explícitamente el cierre de fase | El orquestador persiste atómicamente cierre, espejos y baseline en el **mismo cambio** (ver `## Cierre, recomendación y handoff`) |

**Separación de controles**: la review técnica `SRR` y la review documental por paquete son **controles independientes** — uno no sustituye al otro. `Prepare` y `Submit` (con el congelamiento `en_verificacion`) son operaciones pre-review; `RecordDecision` y `Promote` son post-veredicto; el veredicto técnico nunca elige automáticamente la decisión documental y la aprobación o promoción del paquete nunca sustituye al veredicto. Un veredicto SRR favorable no valida hashes ni integridad documental; ambos controles deben sostenerse al cierre.

Comportamiento según el estado del paquete activo:

- Mientras el paquete activo esté `en_verificacion`, los cinco documentos vivos quedan congelados: esperas y no propones mutaciones de contenido sobre ellos; la `SRR` se conduce sobre esa revisión exacta.
- Ante un paquete `rechazado` (el rechazo de cualquier documento es del paquete completo, sin aprobación parcial), atiendes los hallazgos corrigiendo solo los documentos vivos vía propuestas al orquestador, cuando el paquete deja de estar activamente congelado; la resometida usa un nuevo `package_id` (`r<NNN+1>`) con referencia al predecesor y el paquete rechazado se preserva íntegro con sus hallazgos.
- Con el paquete `aprobado` y promovido, la propuesta de cierre queda habilitada (sin ejecutarse por sí sola; requiere la conjunción completa, ver `## Cierre, recomendación y handoff`).
- Paquete ausente, parcial o con hashes divergentes: fail-closed, bloquea el cierre y se informa sin inferir reparaciones.

Validas paquetes en **solo lectura**: `proyecto/docs-verificacion/**` y `proyecto/docs-aprobados/**` son superficies de autoridad exclusivamente del usuario; puedes comprobar estructura, `content_sha256` y evidencia sin escribir en ellas, pero nunca copias, promueves, revisas, apruebas, firmas ni invocas `docs-review` u otra skill: la composición con `docs-review` la selecciona, resuelve y ejecuta el orquestador ante instrucción conversacional humana explícita.

## Procesos y registros transversales

Transversales de la fase en alcance y su límite específico son:

- **Mutables** (propones actualizaciones con valor anterior → valor propuesto, justificación y procedencia):
  - **`requisitos`**: proponer entradas de tipo `system requirement` en `proyecto/registros/requisitos.md` con ID, fuente, redacción, rationale, prioridad, asignación, método de verificación previsto, estado y trazabilidad bidireccional; las necesidades y stakeholder requirements heredados de `F1` **no se reescriben**: se referencian como procedencia.
  - **`vv`**: proponer en `proyecto/registros/vv.md` solo **resúmenes** por requisito con método definido: ID `SYS-REQ-NNNN`, método de verificación, `madurez_vv: preliminar`, `referencia_plan` hacia `plan_vv_preliminar.md`, `estado_verificacion: no_iniciada`, sin evidencia disponible y con el estado de validación en `no_iniciada` hasta su momento en `F7`. El registro no duplica el plan: resumen + referencia. Nunca registras estados de verificación ejecutada ni mezclas verificación con validación; el estado de ejecución no se sobrecarga con el valor `preliminar`.
  - **`configuracion`**: proponer en `proyecto/registros/configuracion.md` la identificación de los cinco artefactos como ítems de configuración (ID, nombre, tipo, versión, estado de aprobación, ubicación) y, con el cierre autorizado, el registro de la **Functional Baseline** atómicamente con el cierre.
  - **`riesgos`**: proponer en `proyecto/registros/riesgos.md` siempre que se registren, validen o reformulen **riesgos técnicos** derivados del análisis de requerimientos (verificabilidad dudosa, ambigüedades, dependencias externas, supuestos sensibles), con criticidad, responsable, acción y la review donde se revisaron (la `SRR` es el momento típico). Los riesgos heredados de `F0`/`F1` se validan o reformulan con evidencia nueva, sin reiniciar el registro.
- **`datos_y_documentacion`**: no existe aún ficha ni registro propio (cobertura pendiente del catálogo de capacidades). Tratamiento provisional: trazabilidad de evidencia — citar fuente y procedencia de toda evidencia usada y declarar como vacío lo referenciado que no se encuentre. No se absorbe como capacidad implícita ni se inventa un registro paralelo.
- La skill no muta `interfaces` ni `lecciones_aprendidas`: las interfaces externas preliminares viven como sección del SyRS; mutar el registro de interfaces corresponde a una capacidad transversal seleccionada por separado por el orquestador, y `lecciones_aprendidas` está fuera del alcance de la fase.

Sobrescribir evidencia en silencio o fabricar contenido está prohibido: las contradicciones se marcan y quedan visibles para resolución usuario.

## Criterios de cierre

La fase está lista para plantear su cierre cuando se cumplen los criterios del marco, íntegros; los evalúas como verificación de readiness, no como autorización:

- 100 % de requerimientos trazados a necesidades (matriz necesidad ↔ requisito completa y sin huérfanos),
- métodos de verificación definidos (matriz requisito ↔ método completa),
- ambigüedades críticas resueltas,
- Functional Baseline liberable,
- existe un **paquete completo** de review `aprobado` y **promovido** para el scope `f2-requisitos-sistema`, con los gates de cierre completos: copia aprobada válida, conjunto exacto de los cinco snapshots (sin faltantes ni extras), `content_sha256` recomputados en solo lectura y coherentes con el manifest, identidad coherente y attestation terminal del usuario sobre el paquete completo. La sola presencia de la carpeta aprobada no basta y no existe aprobación parcial por documento.

## Cierre, recomendación y handoff

Separa explícitamente tres juicios que nunca deben mezclarse:

1. **Recomendación técnica**: base, confianza y condiciones del material de requerimientos; `no concluyente` mientras la evidencia sea insuficiente.
2. **Readiness** frente a la `SRR`, los criterios de cierre y la constitución de la Functional Baseline: `borrador`, `listo para revisión` o `no recomendable avanzar`, con la lista explícita de vacíos que bloquearían la decisión usuario.
3. **Decisión y autorización usuarios**: el veredicto de la `SRR`, la decisión documental, la aprobación del paquete y el cierre de la fase son decisiones de los humanos.

La propuesta de cierre se emite únicamente con la **conjunción** completa de tres condiciones — falta cualquiera y no hay cierre, ni baseline, ni espejos `aprobado`:

1. veredicto **SRR favorable** emitido sobre la revisión exacta congelada y ligado al `package_id` congelado, al conjunto de los cinco artefactos y a los hashes del manifest (transportado como evidencia en la propuesta);
2. paquete documental completo `aprobado` y **promovido** con gates completos;
3. **autorización humana** explícita del cierre de fase.

Emitida esa autorización, propones un único bloque coherente que el orquestador persiste como un solo cambio:

- fila `F2: en_progreso → cerrada` en `proyecto/estado/estado_fases.md`;
- el espejo derivado `doc_approval: pendiente → aprobado` en los cinco artefactos, con entradas de historial coherentes con la attestation del manifest;
- el registro de la **Functional Baseline** en `proyecto/registros/configuracion.md` **en el mismo cambio**: referencia a los cinco artefactos aprobados y su versión, estado de aprobación y ubicación; no existen estados donde la fila `F2` esté cerrada y la baseline no registrada, ni una baseline registrada con la fila `F2` aún `en_progreso`;
- el informe de elegibilidad de fase `F3` como observación, sin cambio de fila: la fila `F3` permanece `no_iniciada`; nunca abres, habilitas ni propones abrir `F3`, y no existe skill de transición `F2`→`F3` — una futura capacidad de `F3` verifica estas precondiciones fail-closed y abre solo con autorización humana separada. El estado global permanece `proyecto_formal`.

Esta skill nunca otorga la aprobación del cierre, de los artefactos, del veredicto ni de la baseline. Entrega al orquestador un bloque de **propuesta de actualización** con: fuente y estado observado; campos o filas con valor anterior → valor propuesto; justificación y procedencia; vacíos y contradicciones; y los artefactos y registros que deben conservar continuidad. Cuando existe la autorización usuario, la propuesta la transporta como evidencia, pero nunca autoriza por sí misma. **No escribes** en `proyecto/**`: el orquestador relee, valida y persiste como un único cambio coherente (single-writer).

Fail-closed: ante un paquete activo `en_verificacion`, un paquete ausente, parcial o con `content_sha256` divergentes, un veredicto no ligado a la revisión congelada, o evidencia requerida ausente o contradictoria para el cierre o la review, no declares cierre ni readiness favorable; informa el conflicto y solicita su restauración. La evidencia no crítica faltante no bloquea: se producen propuestas con los vacíos declarados de forma explícita. Idempotencia: si la fila `F2: cerrada` ya es coherente con artefactos en `formal`/`aprobado` y la baseline registrada, informas el estado observado, no propones cambios y no reabres nada.

## Referencias

- `marco/fases/fase_2_requerimientos_sistema.md` — contrato completo de la fase `F2` (procedencia de diseño; el cuerpo de esta skill ya embebe todas las reglas operativas).
- `marco/reglas_del_ciclo.md` — regla de paso a `F2` y regla de trazabilidad/asignabilidad/verificabilidad de todo requerimiento.
- `marco/reviews/catalogo_reviews.md` — objetivo y momento típico de la **SRR / System Requirements Review**.
- `marco/baselines/catalogo_baselines.md` — contenido y congelamiento de la **Functional Baseline**.
- `proyecto/estado/proyecto_actual.md` — estado global (solo lectura, para determinar el estado reconocido).
- `proyecto/estado/estado_fases.md` — estado por fase (solo lectura, para determinar las filas `F1 formal`, `F2` y `F3`).
- `proyecto/hitos/hito_aprobacion_trabajo.md` — hito consolidado por el handoff (solo lectura).
- `proyecto/registros/requisitos.md`, `proyecto/registros/vv.md`, `proyecto/registros/configuracion.md`, `proyecto/registros/riesgos.md` — registros transversales mutables vía propuesta.
- `proyecto/registros/reviews.md` — registro futuro del veredicto SRR (cuando exista su plantilla; lo persiste el orquestador con autorización humana, single-writer).
- `proyecto/fases/f2_requisitos_sistema/requisitos_sistema.md`, `matriz_necesidad_requisito_sistema.md`, `matriz_requisito_metodo_verificacion.md`, `supuestos_y_restricciones.md`, `plan_vv_preliminar.md` — los cinco artefactos canónicos de la fase.
- `proyecto/docs-verificacion/**` y `proyecto/docs-aprobados/**` — paquetes de review y copias aprobadas (solo lectura; superficies de autoridad exclusivamente del usuario).

Las referencias o la evidencia que falten se declaran como vacíos; no se completan en silencio.
