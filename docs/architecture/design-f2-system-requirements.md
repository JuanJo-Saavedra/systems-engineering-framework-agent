---
document_type: diseno_concreto_capacidades
language: es
version: 1.2
status: propuesto
---

# Diseño concreto: capacidad de fase `f2_requisitos_sistema` y constitución de la Functional Baseline

Este documento completa la [hoja de diseño](design-skill-marco.md#hoja-de-diseño-previa-a-la-implementación) para la capacidad de fase **`f2_requisitos_sistema`** (fase `F2`, madurez `formal`): la primera fase técnica del proyecto formal, que traduce las necesidades de stakeholders en requerimientos de sistema verificables y trazables, y cuya preparación habilita la constitución de la **Functional Baseline**. Es un artefacto de diseño: define contratos, límites, invariantes de estado, salidas propuestas y criterios de aceptación de la futura skill implementada `f2-requisitos-sistema`. **No implementa nada**: la ficha del catálogo permanece en `estado_implementacion: definida` (valor por defecto global, sin anulación) y no se crea ningún `SKILL.md`, registry ni plantilla en esta unidad. El núcleo genérico de review `docs_review`/`docs-review` ya está implementado; F2 lo consume por composición del padre, exactamente como lo hace [`f1_stakeholders_formal`](../../runtime/skills/f1-stakeholders-formal/SKILL.md), y nunca lo invoca ni lo opera por sí misma.

**Autocontención y procedencia de diseño (v1.1).** Las futuras skills operativas son **autocontenidas** frente a la metodología del marco: la composición de runtime es `AGENTS.md` (reglas generales del agente) + el `SKILL.md` completo de la capacidad (comportamiento específico) + la evidencia viva `proyecto/**` (estado, hitos, artefactos y registros). `framework/marco/**` es **procedencia de diseño y auditoría**: nunca es una lectura requerida de runtime, y `src/se_agent/_payload/**` es un espejo de empaquetado generado, sin autoridad, que nunca se cita como normativa. La preparación de la review técnica `SRR` tampoco es tarea de esta skill de fase: el padre la compone con la capacidad genérica de tarea puntual **`preparacion_de_review`** (futura skill `preparacion-de-review`, [diseño genérico](design-preparacion-de-review.md)); F2 declara readiness, la capacidad genérica prepara el dossier técnico de review, el humano autoriza `Prepare`+`Submit` para congelar la revisión exacta del paquete documental, y el humano conduce la `SRR` **contra esa revisión congelada** y decide.

## Camino rápido de revisión

1. **Primero**: la tabla [Decisión resumida](#decisión-resumida) — captura las nueve decisiones de diseño en una pantalla.
2. **Después**: [Flujo canónico](#flujo-canónico-de-f2) e [Invariantes de estado](#invariantes-de-estado-y-persistencia-atómica) — el comportamiento del ciclo y qué se persiste atómicamente.
3. **Luego**: los cinco [artefactos obligatorios](#artefactos-obligatorios-de-f2-rutas-canónicas-frontmatter-y-ciclo), las [dos matrices de trazabilidad](#las-dos-matrices-de-trazabilidad) y la [conjunción de cierre de la Functional Baseline](#srr-y-review-documental-controles-independientes-y-conjunción-de-la-functional-baseline) — el corazón técnico de la fase.
4. **Después**: la [composición con `preparacion_de_review`](#preparación-de-la-srr-composición-con-preparacion_de_review) — cómo se arma el dossier de la `SRR` sin que la skill de fase conduzca la review, con la secuencia congelada (dossier → `Prepare`+`Submit` → `SRR` contra la revisión congelada → veredicto → decisión documental separada) — y las [decisiones adoptadas de la v1.1](#decisiones-adoptadas-y-trabajo-diferido) (IDs `SYS-REQ-0001`, registro `reviews.md`, esquema V&V).
5. **Al final**: la [hoja de diseño completa](#hoja-de-diseño-f2_requisitos_sistema) con el esquema del futuro `SKILL.md` y los [criterios de aceptación](#criterios-de-aceptación-para-la-implementación) para la sesión de implementación.

**Fuera de alcance de esta revisión**: no se toca `framework/marco/**`, `framework/proyecto/**`, `framework/guias/skill-architecture.md`, `runtime/skills/**`, `runtime/catalogo/skill-registry.md` ni `src/se_agent/_payload/**`. Este documento consume su semántica; no la redefine.

## Decisión resumida

| Aspecto | Decisión |
| --- | --- |
| Capacidad | Una sola capacidad de fase: `f2_requisitos_sistema` (tipo `fase`, fase objetivo `F2`, madurez esperada `formal`). `F2` no se desdobla por madurez: el marco declara `allowed_maturity: [formal]` y `default_maturity: formal`; no existe modo preliminar de `F2`. |
| Ejecutable futuro | Skill `f2-requisitos-sistema` (kebab-case; directorio + frontmatter `name` + `id` en el registry), declarada en un cambio de implementación posterior junto con el `bindings` de la ficha. |
| Artefactos | Los cinco artefactos obligatorios del marco viven en rutas canónicas bajo `proyecto/fases/f2_requisitos_sistema/`, con frontmatter común y ciclo `doc_approval`. A diferencia de `F1`, **no hay reset de madurez**: `F2` nace formal y los artefactos se crean en el cambio atómico de apertura. |
| Trazabilidad | **Dos matrices separadas**, tal como las exige el marco: necesidad ↔ requisito de sistema y requisito de sistema ↔ método de verificación. No se fusionan en una sola matriz: cada una responde una pregunta distinta y se verifica por separado. |
| V&V | El **plan V&V preliminar es artefacto de fase** (`plan_vv_preliminar.md`); el registro transversal `vv` se actualiza además con **resúmenes** por requisito (método, estado y referencia al plan). El registro no duplica el plan: lo referencia. |
| Cierre y baseline | La **Functional Baseline** se constituye solo por la **conjunción** de tres condiciones: veredicto favorable de la `SRR` **emitido contra la revisión exacta congelada del paquete**, paquete documental completo `aprobado` y `promovido` con gates completos, y **decisión humana explícita** de cierre. La baseline se registra **atómicamente con el cierre** en `proyecto/registros/configuracion.md`. Ninguna condición sola constituye nada. |
| Controles independientes | La review técnica `SRR` y la review documental por paquete (`docs-review`) son **controles independientes**: uno no sustituye al otro, pero la **secuencia canónica sí es obligatoria** (v1.2): primero el paquete documental se somete y congela (`Prepare`+`Submit`, estado `en_verificacion`), y la `SRR` se conduce **contra esa revisión exacta congelada**; la decisión documental (`RecordDecision`+`Promote`) es **post-veredicto**, separada y explícita — el veredicto técnico nunca la elige automáticamente y la aprobación documental nunca sustituye al veredicto. La skill `f2-requisitos-sistema` es una **skill de fase pura**: declara readiness y emite la especificación de paquete; el orquestador padre compone con `docs-review` ante instrucción humana explícita. La skill nunca invoca otra skill ni se autoautoriza. |
| Preparación de la SRR | La skill de fase declara readiness frente a la `SRR` y **nunca convoca, conduce ni emite veredicto**. Con readiness declarada, el padre compone la capacidad genérica de tarea puntual `preparacion_de_review` (futura skill `preparacion-de-review`, [diseño genérico](design-preparacion-de-review.md)), que arma el dossier técnico, evalúa criterios de entrada/salida y propone agenda. Si el dossier reporta **bloqueos**, el flujo regresa al trabajo de fase; si concluye readiness sin bloqueos, el humano autoriza `Prepare`+`Submit`, el conjunto exacto de los cinco documentos se copia, hashea y manifiesta y entra `en_verificacion` congelado. El humano conduce la `SRR` **contra esa revisión congelada** y decide; el veredicto, **ligado al `package_id` congelado, al conjunto de artefactos y a sus hashes**, se registra por el padre —con autorización humana, single-writer— en el registro futuro `proyecto/registros/reviews.md` (plantilla diferida, no creada en esta unidad). |
| Riesgos técnicos | Los **riesgos técnicos son mutables en `F2`**: se registran, validan y reformulan en `proyecto/registros/riesgos.md` con evidencia nueva derivada del análisis de requerimientos. `datos_y_documentacion` sigue siendo un vacío de cobertura del catálogo: se trata solo como **trazabilidad de evidencia** (fuente y procedencia citadas; lo referenciado y no encontrado se declara vacío), sin inventar una capacidad. |

## Alcance y no metas

**En alcance de este documento:**

- Hoja de diseño completa de la capacidad `f2_requisitos_sistema`, incluida la frontera con `F1` (entrada), `F3` (salida) y `F4` (fuera de todo alcance de `F2`).
- Flujo canónico de `F2` con las transiciones de entrada, apertura, trabajo, readiness y cierre, y sus invariantes de estado exactos.
- Ubicación canónica, frontmatter, ciclo de aprobación y relaciones de los cinco artefactos obligatorios de fase, incluida su integración con el [ciclo de review por paquete](design-document-review-lifecycle.md).
- Propuesta de scope, id y especificación de paquete `docs-review` para `F2`, sin duplicar el protocolo genérico.
- Comportamiento propuesto sobre los registros transversales `requisitos`, `vv`, `configuracion` y `riesgos`, y tratamiento del vacío `datos_y_documentacion`.
- Conjunción exacta de constitución de la Functional Baseline y su registro atómico.
- Composición con la capacidad genérica de tarea puntual [`preparacion_de_review`](design-preparacion-de-review.md) antes de la `SRR` y la **secuencia canónica de revisión congelada** (v1.2: dossier sin bloqueos → `Prepare`+`Submit` autorizados → congelamiento `en_verificacion` → `SRR` contra la revisión congelada → veredicto → decisión documental separada → cierre), las decisiones adoptadas de la v1.1 (convención de IDs `SYS-REQ-0001`, registro futuro `proyecto/registros/reviews.md`, esquema V&V con madurez separada de la ejecución) y la inexistencia deliberada de una skill de transición `F2`→`F3`.

**Fuera de alcance (no metas):**

- Escribir `runtime/skills/f2-requisitos-sistema/SKILL.md`, el registry operativo, el `bindings` de la ficha o el espejo del payload: todo eso pertenece a la sesión de implementación futura.
- Crear plantillas en `framework/proyecto/fases/f2_requisitos_sistema/` o en cualquier otra ruta de plantilla: las rutas canónicas que este documento propone para la **instancia** no se materializan ahora.
- Cambiar `framework/marco/**`, `framework/guias/skill-architecture.md` o el catálogo de capacidades: la ficha `f2_requisitos_sistema` permanece en `definida` hasta que una implementación declare su enlace.
- Definir la política de la review `SRR` más allá de lo que el [catálogo de reviews](../../framework/marco/reviews/catalogo_reviews.md) ya declara, ni duplicar el [protocolo genérico del paquete](design-document-review-lifecycle.md).
- Crear `proyecto/registros/reviews.md` ni su plantilla: el registro de reviews es una **superficie futura**; su esquema de diseño vive en [design-preparacion-de-review.md](design-preparacion-de-review.md) y su materialización pertenece a un cambio posterior con autorización humana.
- Ejecutar el trabajo de `F2` sobre una instancia concreta: este documento diseña la capacidad, no la aplica.

## Fronteras F1 / F3 / F4

| Frontera | Qué entra a `F2` | Qué queda fuera y a quién pertenece |
| --- | --- | --- |
| **Desde `F1` (entrada)** | Necesidades y stakeholder requirements formalizados, escenarios de uso completos, restricciones externas consolidadas, criterios de aceptación de alto nivel claros y trazabilidad necesidad ↔ stakeholder requirement sin huérfanos — todo ya aprobado y promovido en el paquete `f1-stakeholders`. | `F2` no reabre el hito de aprobación, no rehace trabajo preliminar ni reabre vacíos heredados ya cerrados; no re-ejecuta el handoff ni modifica la decisión aprobatoria registrada. |
| **Hacia `F3` (salida)** | Requerimientos de sistema claros, verificables y trazables; métodos de verificación preliminares por requisito; interfaces externas preliminares identificadas; Functional Baseline liberable. `F3` consume la baseline, no la redefine. | `F2` no selecciona arquitectura, no asigna requisitos a subsistemas ni CIs, no produce trade-offs arquitectónicos: eso corresponde a `F3`. `F2` nunca abre ni habilita `F3`; su fila permanece `no_iniciada`. **No existe skill de transición `F2`→`F3`** (decisión v1.1): el hito técnico lo constituye la conjunción de veredicto SRR favorable, paquete documental promovido, Functional Baseline registrada y cierre de `F2`; una futura capacidad de `F3` valida estas precondiciones y abre solo con autorización humana separada. |
| **Desde `F4` (límite duro)** | Nada. | `F2` no produce diseño build-to/code-to, ni PBS, ni ICDs, ni decisiones de implementación física: eso corresponde a `F4`. Un requerimiento de `F2` describe **qué** debe hacer el sistema, nunca **cómo** se implementa. |

Regla dominante de la fase (del marco): **no mezclar requerimiento con solución**. El foco es claridad técnica, verificabilidad y trazabilidad.

## Flujo canónico de `F2`

```text
F1 formal cerrada ──► gate de paso a F2 ──► APERTURA atómica ──► trabajo sobre
(gate del ciclo)      (verificación         (fila F2 + cinco     requerimientos ──► readiness ──► dossier de la SRR
                       fail-closed)          artefactos)          (matrices, V&V)    (observación)  (`preparacion-de-review`;
                                                                                                      ¿bloqueos? → volver al trabajo)
                                                                                                                       │ sin bloqueos
                                                                                                                       ▼
                                                                                        `Prepare`+`Submit` autorizados (humano)
                                                                                        ──► `en_verificacion`: revisión exacta congelada
                                                                                        (manifest + hashes; vivos contra mutación)
                                                                                                                       │
                                                                                                                       ▼
                                                                                        SRR humana contra la revisión congelada ──► VEREDICTO
                                                                                        (→ `reviews.md`, ligado al `package_id` congelado)
                                                                                                                       │ favorable
                                                                                                                       ▼
                                                                                        `RecordDecision`+`Promote` (decisión documental separada)
                                                                                                                       │
                                                                                                                       ▼
                                                                                        CONJUNCIÓN de cierre: SRR favorable
                                                                                        + paquete aprobado y promovido
                                                                                        + decisión humana de cierre
                                                                                        ──► CIERRE atómico + Functional Baseline
```

### Entrada (gate de paso a `F2`)

Precondiciones estructurales, verificadas **fail-closed** antes de cualquier trabajo (fuentes: [reglas del ciclo](../../framework/marco/reglas_del_ciclo.md) y [estado por fase](../../framework/proyecto/estado/estado_fases.md)):

- estado global `proyecto_formal`;
- fila `F1 formal: cerrada` con sus cuatro artefactos en `formal`/`aprobado`;
- fila `F2: no_iniciada`;
- regla de paso a `F2` satisfecha: stakeholders críticos identificados, restricciones externas consolidadas, escenarios de uso relevantes y criterios de aceptación de alto nivel suficientemente claros;
- paquete `f1-stakeholders` aprobado y promovido, con evidencia trazable.

Ante cualquier combinación parcial o inconsistente (p. ej. `F1 formal: en_progreso`, fila `F2` distinta de `no_iniciada`, paquete `f1-stakeholders` sin promover), la capacidad no ejecuta trabajo de `F2`: informa el conflicto observado y espera resolución humana. Nunca propone activar `F1 formal` ni alterar su cierre.

### Apertura (cambio atómico de apertura)

El primer trabajo de `F2` propone **un único bloque coherente** que el padre persiste como un solo cambio, sin estados parciales:

| Fuente | Cambio propuesto (anterior → propuesto) | Precondición |
| --- | --- | --- |
| `proyecto/estado/estado_fases.md` | Fila `F2: no_iniciada → en_progreso` | Gate de paso a `F2` verificado; fila `F1 formal: cerrada` |
| `proyecto/estado/proyecto_actual.md` | `active_phase: F1 → F2`; `active_maturity: formal` (sin cambio); `project_status: proyecto_formal` (sin cambio) | Consistencia con `estado_fases.md` |
| `proyecto/fases/f2_requisitos_sistema/**` | Creación de los cinco artefactos obligatorios con frontmatter común, `active_maturity: formal` y `doc_approval: pendiente` | Rutas canónicas; sin contenido fabricado para llenar vacíos |

El estado global **no cambia** de valor en la apertura: `F2` abre dentro del estado `proyecto_formal` ya vigente desde el primer trabajo formal de `F1`. No existen estados intermedios donde la fila `F2` esté `en_progreso` sin que los cinco artefactos existan en sus rutas canónicas, ni viceversa.

### Trabajo

Con la fila `en_progreso`, la capacidad ejecuta las actividades guía del marco operacionalizadas (derivar, clasificar, revisar consistencia y completitud, analizar verificabilidad, identificar interfaces externas preliminares, definir método de verificación por requerimiento, construir trazabilidad), **sin orden obligatorio** y seleccionando según la evidencia. Cada salida distingue `hechos verificados`, `supuestos`, `vacíos` y `contradicciones`.

### Readiness

La capacidad evalúa, como **observación** y nunca como autorización:

- **readiness técnica** frente a la `SRR`: requerimientos correctos, completos, trazables y verificables, contra los criterios de cierre del marco;
- **readiness documental** frente al ciclo de paquete: los cinco artefactos listos para snapshots coherentes.

Emite al padre: recomendación técnica, readiness con vacíos bloqueantes y —si el material está listo— la especificación exacta del paquete (ver [especificación de paquete](#integración-con-el-ciclo-de-review-por-paquete-scope-id-y-especificación)). Readiness no equivale a autorización.

Con readiness declarada, el padre —no la skill— compone la capacidad genérica **`preparacion_de_review`** para armar el dossier técnico de la `SRR` (ver [Preparación de la SRR](#preparación-de-la-srr-composición-con-preparacion_de_review)). La skill de fase no prepara, convoca ni conduce la review.

Si el dossier reporta **bloqueos o faltantes**, el flujo regresa al trabajo de fase: la corrección ocurre en los documentos vivos, la readiness se re-evalúa tras corregir y la preparación se repite. Si el dossier concluye readiness **sin bloqueos**, el humano autoriza explícitamente `Prepare`+`Submit`; el conjunto exacto de los cinco documentos se copia, hashea y manifiesta, el paquete entra `en_verificacion` y los documentos vivos quedan **congelados contra mutación**: es sobre esa revisión exacta congelada que se conduce la `SRR`.

### Cierre (conjunción y cambio atómico)

Detallado en [SRR y review documental](#srr-y-review-documental-controles-independientes-y-conjunción-de-la-functional-baseline). Resumen: la propuesta de cierre se emite solo con las **tres condiciones conjuntas** (SRR favorable + paquete aprobado y promovido con gates completos + autorización humana explícita del cierre), y se resuelve en **un único cambio coherente** que incluye la fila `F2: en_progreso → cerrada`, los espejos `doc_approval: pendiente → aprobado` en los cinco artefactos y el **registro de la Functional Baseline** en `proyecto/registros/configuracion.md`.

## Invariantes de estado y persistencia atómica

Invariantes que la capacidad verifica y el padre garantiza al persistir:

1. **Gate de entrada**: no existe trabajo de `F2` con `project_status` distinto de `proyecto_formal`, con `F1 formal` no `cerrada`, o con la regla de paso a `F2` insatisfecha.
2. **Fila y artefactos coherentes**: la fila `F2: en_progreso` implica exactamente los cinco artefactos existentes en `proyecto/fases/f2_requisitos_sistema/` con `active_maturity: formal`; no hay fila `en_progreso` sin artefactos ni artefactos sin fila abierta.
3. **Sin modo preliminar**: ningún artefacto de `F2` adopta nunca `active_maturity: preliminar`; no existe ciclo preliminar→formal de madurez en esta fase.
4. **`doc_approval` espejo derivado**: mientras el paquete activo esté `en_verificacion`, los cinco documentos vivos quedan **congelados** (`content_sha256` comparables contra el manifest); el `doc_approval` vivo permanece `pendiente` (no se introduce un cuarto valor); pasa a `aprobado` solo como espejo de la decisión ya registrada en el manifest del paquete promovido, con entrada de historial coherente con la attestation.
5. **Cierre conjuntivo**: no existe cierre de `F2` sin las tres condiciones conjuntas; la sola presencia de la carpeta aprobada, un paquete parcial, hashes divergentes o un veredicto SRR aislado no habilitan nada.
6. **Baseline atómica con el cierre**: la entrada de la Functional Baseline en `proyecto/registros/configuracion.md` se persiste en el **mismo cambio coherente** que la fila `F2: cerrada`. No existe un estado donde `F2` esté cerrada y la baseline no registrada, ni una baseline registrada con `F2` aún `en_progreso`.
7. **Single-writer**: la skill nunca escribe en `proyecto/**`; solo emite bloques de propuesta con valor anterior → valor propuesto, justificación, procedencia y vacíos. El padre relee las fuentes, comprueba que no cambiaron, valida las reglas del ciclo y persiste.
8. **Fail-closed**: evidencia requerida ausente o contradictoria (estado, paquete, hashes, veredicto) bloquea el cierre y la review; la evidencia no crítica faltante produce borradores con vacíos declarados. La disponibilidad de skills no cambia esta regla.
9. **Idempotencia de cierre**: con fila `F2: cerrada`, artefactos en `formal`/`aprobado` y baseline registrada coherentemente, la capacidad informa el estado observado, no propone cambios y no reabre nada.
10. **Veredicto ligado a la revisión congelada**: el veredicto de la `SRR` solo es consumible por la conjunción de cierre si está vinculado al `package_id` exacto que estuvo `en_verificacion` (o a su estado terminal coherente), al conjunto de los cinco artefactos y a los hashes del manifest; un veredicto emitido sobre una revisión distinta, no congelada o no identificable es una contradicción fail-closed y no habilita nada. Un veredicto desfavorable, o condicionado con bloqueadores abiertos, mantiene el cierre bloqueado y la revisión revisada preservada; las correcciones vuelven a los documentos vivos solo cuando el paquete deja de estar activamente congelado, seguidas de una resometida trazable `r<NNN+1>` que repite preparación y review.

## Artefactos obligatorios de `F2`: rutas canónicas, frontmatter y ciclo

Los cinco artefactos obligatorios del marco ([contrato de fase](../../framework/marco/fases/fase_2_requerimientos_sistema.md)) viven en rutas canónicas bajo `proyecto/fases/f2_requisitos_sistema/` — espejo del patrón aprobado para [`f1_stakeholders/`](../../framework/proyecto/fases/README.md):

| Artefacto obligatorio de F2 | Ruta canónica propuesta | `document_type` propuesto |
| --- | --- | --- |
| SyRS — especificación de requerimientos de sistema | `proyecto/fases/f2_requisitos_sistema/requisitos_sistema.md` | `system_requirements` |
| Matriz necesidad ↔ requisito de sistema | `proyecto/fases/f2_requisitos_sistema/matriz_necesidad_requisito_sistema.md` | `need_system_requirement_matrix` |
| Matriz requisito ↔ método de verificación | `proyecto/fases/f2_requisitos_sistema/matriz_requisito_metodo_verificacion.md` | `system_requirement_verification_method_matrix` |
| Registro de supuestos y restricciones | `proyecto/fases/f2_requisitos_sistema/supuestos_y_restricciones.md` | `assumptions_and_constraints` |
| Plan V&V preliminar | `proyecto/fases/f2_requisitos_sistema/plan_vv_preliminar.md` | `preliminary_vv_plan` |

> Estas rutas y `document_type` son **propuestas de diseño** para la instancia; se materializan solo cuando una sesión de implementación (skill) o una ejecución real de proyecto las cree. No se crean ahora en `framework/proyecto/**` ni en ninguna instancia.

### Frontmatter común de los artefactos de fase de `F2`

Cada uno de los cinco artefactos lleva el mismo frontmatter, heredado del patrón de `F1`:

| Campo | Valor / semántica |
| --- | --- |
| `document_type` | Tipo exacto del artefacto según la tabla anterior. |
| `language: es` | Idioma del contenido. |
| `active_maturity` | Siempre `formal`: `F2` no tiene modo preliminar. |
| `last_updated` | Fecha de la última persistencia. |
| `doc_approval` | Estado de aprobación vigente: `pendiente` durante todo el trabajo; `aprobado` solo como espejo derivado de la decisión registrada en el manifest del paquete promovido. |
| `responsible: "<identidad>"` | Custodio humano vigente y responsable del artefacto; nunca el aprobador. |

La identidad de quien aprueba se preserva en la **tabla de historial de aprobación en el cuerpo** del artefacto (aprobador, fecha, madurez y decisión), nunca en el frontmatter.

### Ciclo de aprobación (`doc_approval`) en `F2`

A diferencia de `F1`, no hay reset por madurez: el ciclo es lineal.

1. **Apertura**: los cinco artefactos se crean con `doc_approval: pendiente` y `active_maturity: formal`.
2. **Trabajo**: los artefactos trabajan con `doc_approval: pendiente`; mientras el paquete activo esté `en_verificacion` quedan congelados (verificación por `content_sha256`).
3. **Cierre**: con el paquete completo aprobado y promovido, el padre persiste el espejo derivado `doc_approval: pendiente → aprobado` en los cinco artefactos, con entradas de historial coherentes con la attestation del manifest, en el mismo cambio atómico del cierre de fase y del registro de la baseline.

### Relaciones entre los artefactos

```text
F1 (entrada aprobada)                     F2                                  registros transversales
─────────────────────                     ──────────────────────────────      ───────────────────────────
necesidades y stakeholder requirements ──► SyRS (requisitos_sistema.md) ───► requisitos.md (entradas system requirement)
       │                                        │
       │   matriz_necesidad_requisito_          │  matriz_requisito_metodo_
       └─► sistema.md  ◄───────────────────────┘  verificacion.md ◄── plan_vv_preliminar.md ◄─► vv.md (resumen + referencia)
                                                │
                           supuestos_y_restricciones.md ◄── restricciones externas de F1, supuestos de F0/F1
                                                │
                                    configuracion.md (identificación de ítems + Functional Baseline al cierre)
                                    riesgos.md (riesgos técnicos derivados)
```

- El **SyRS** es el documento central: contiene los requerimientos de sistema con sus atributos (ID, fuente, redacción, rationale, prioridad, asignación, método de verificación previsto, estado) y la sección de **interfaces externas preliminares**.
- La **matriz necesidad ↔ requisito** conecta cada requisito con la necesidad o stakeholder requirement de `F1` que lo origina (hacia arriba) y detecta huérfanos en ambas direcciones.
- La **matriz requisito ↔ método de verificación** conecta cada requisito con su método de verificación (inspección, análisis, demostración, ensayo — el conjunto clásico; los nombres concretos no están fijados por el marco) y es la base del plan V&V preliminar.
- **Supuestos y restricciones** captura lo que condiciona los requerimientos sin ser requisito en sí: hereda las restricciones externas consolidadas de `F1` como **referencia** (no las reescribe) y registra los supuestos nuevos que el análisis técnico introduce.
- El **plan V&V preliminar** consolida estrategia y criterios preliminares de verificación; alimenta el registro `vv` y la sección de criterios preliminares de verificación de la Functional Baseline.

## Las dos matrices de trazabilidad

Decisión de diseño: **dos matrices separadas**, cada una como artefacto obligatorio propio, tal como el contrato de fase las lista. No se fusionan.

| | Matriz 1 — necesidad ↔ requisito de sistema | Matriz 2 — requisito ↔ método de verificación |
| --- | --- | --- |
| Artefacto | `matriz_necesidad_requisito_sistema.md` | `matriz_requisito_metodo_verificacion.md` |
| `document_type` | `need_system_requirement_matrix` | `system_requirement_verification_method_matrix` |
| Pregunta que responde | ¿Todo requisito deriva de una necesidad real, y toda necesidad está cubierta técnicamente? | ¿Cómo se comprobará cada requisito, y hay algún requisito sin forma de verificarse? |
| Filas | Requerimientos de sistema del SyRS | Requerimientos de sistema del SyRS |
| Columnas hacia arriba | Necesidad / stakeholder requirement de `F1` (referencia a `proyecto/fases/f1_stakeholders/**` y al registro `requisitos`) | Método de verificación previsto (y referencia a `plan_vv_preliminar.md`) |
| Cobertura exigida al cierre | 100 % de los requerimientos trazados a necesidades (criterio de cierre del marco), sin huérfanos en ninguna dirección | 100 % de los requerimientos con método de verificación definido (criterio de cierre del marco) |
| Errores que detecta | Requisitos sin origen (solución disfrazada de requisito), necesidades sin cobertura técnica | Requisitos no verificables, métodos sin dueño, verificación ambigua |
| Relación con registros | Procedencia trazable en `proyecto/registros/requisitos.md` (campo trazabilidad) | Resumen de método/estado/referencia en `proyecto/registros/vv.md` |

Reglas de consistencia entre ambas:

- Las dos matrices usan los **mismos IDs de requisito** que el SyRS y el registro `requisitos`; un ID que exista en una y no en otra es una contradicción declarada.
- **Convención de IDs (decisión v1.1):** todo requerimiento de sistema usa el formato inmutable **`SYS-REQ-0001`** (prefijo fijo + cuatro dígitos), único y permanente por proyecto. Los IDs **nunca se reutilizan, renumeran ni reciclan** — ni siquiera tras un rechazo o eliminación del requisito — y son **idénticos** en el SyRS, ambas matrices, `proyecto/registros/requisitos.md` y `proyecto/registros/vv.md`. Cualquier divergencia de formato o de identidad entre esas cinco superficies es una contradicción declarada, no una renumeración.
- Ninguna matriz sustituye al registro transversal `requisitos`: la matriz es el artefacto de fase de trazabilidad; el registro es la fuente continua de entradas con todos sus campos.
- Al cierre, ambas coberturas se verifican al 100 % como parte del criterio de cierre, y su estado queda reflejado en los resúmenes de los registros transversales.

## Comportamiento de los registros transversales

Los transversales declarados por el contrato de fase son `requisitos`, `vv`, `configuracion` y `riesgos`; el tratamiento propuesto por registro:

| Registro | Papel de la capacidad de `F2` | Límite específico en esta fase |
| --- | --- | --- |
| `proyecto/registros/requisitos.md` | **Mutable**: propone entradas de tipo `system requirement` con los campos mínimos del registro (ID único, tipo, fuente, redacción, rationale, prioridad, asignación, método de verificación previsto, estado, trazabilidad bidireccional). | Las entradas de necesidad y stakeholder requirement heredadas de `F1` **no se reescriben**: se referencian como procedencia. La trazabilidad hacia arriba apunta a ellas; nunca se reabre el trabajo de `F1`. |
| `proyecto/registros/vv.md` | **Mutable con resúmenes**: por cada requisito con método definido, propone una entrada resumida con el esquema de madurez separado de la ejecución (decisión v1.1): ID de requisito `SYS-REQ-NNNN`, método de verificación, `madurez_vv: preliminar`, `referencia_plan` hacia `plan_vv_preliminar.md`, `estado_verificacion: no_iniciada`, **sin evidencia disponible** y con el estado de validación en `no_iniciada`. | El registro no duplica el plan: resumen + referencia. No registra evidencia disponible ni estados de verificación ejecutada: eso comienza en `F6`. Se respeta la regla del registro: no mezclar verificación con validación; en `F2` solo hay criterios **preliminares** de verificación, sin estados de cumplimiento. El estado de ejecución **no se sobrecarga** con el valor `preliminar` (la madurez vive en `madurez_vv`), y la validación no se declara «inaplicable»: queda `no_iniciada` hasta su momento en `F7`. La ampliación retrocompatible de la plantilla `framework/proyecto/registros/vv.md` es trabajo diferido (ver [Decisiones adoptadas](#decisiones-adoptadas-y-trabajo-diferido)). |
| `proyecto/registros/configuracion.md` | **Mutable**: identifica los cinco artefactos de fase como ítems de configuración (ID, nombre, tipo, versión, estado de aprobación, ubicación) a medida que se producen, y registra la **Functional Baseline** atómicamente con el cierre. | La baseline se registra con su contenido definido por el [catálogo de baselines](../../framework/marco/baselines/catalogo_baselines.md): requerimientos funcionales, desempeño, interfaces externas relevantes, restricciones principales y criterios preliminares de verificación — es decir, la referencia a los cinco artefactos aprobados. No se inventan tags ni releases de Git: el registro del proyecto es la autoridad (regla especial del registro). |
| `proyecto/registros/riesgos.md` | **Mutable**: los **riesgos técnicos son mutables en `F2`**. Registra, valida y reformula riesgos técnicos derivados del análisis de requerimientos (verificabilidad dudosa, ambigüedades, dependencias externas, supuestos sensibles), con criticidad, responsable y acción. | Cada riesgo técnico registra la review donde se revisó (campo del registro): la `SRR` es el momento típico de su revisión formal. Riesgos heredados de `F0`/`F1` se validan o reformulan con evidencia nueva; no se reinicia el registro. |
| `datos_y_documentacion` | **Sin ficha ni registro propio** (vacío de cobertura del catálogo). Tratamiento provisional: **trazabilidad de evidencia** — citar fuente y procedencia de toda evidencia usada, y declarar como vacío lo referenciado que no se encuentre. | No se inventa una capacidad ni un registro paralelo; no se absorbe implícitamente. |
| `interfaces` | **No es transversal de `F2`** según el contrato de fase. Las interfaces externas preliminares identificadas en `F2` viven como **sección del SyRS**. Si un proyecto necesita mutar `proyecto/registros/interfaces.md`, el padre selecciona la capacidad transversal `interfaces` por separado (regla del routing: añadir solo los transversales afectados). | La skill de fase nunca muta el registro de interfaces ni compone esa capacidad por sí misma. |
| `lecciones_aprendidas` | Fuera de alcance: cobertura pendiente del catálogo; no se toca. | — |

## SRR y review documental: controles independientes y conjunción de la Functional Baseline

### Dos controles independientes, una secuencia canónica congelada

La revisión del material de `F2` pasa por **dos controles independientes** — uno no sustituye al otro — con una **secuencia canónica obligatoria** fijada por la v1.2:

1. **Review técnica `SRR`** (System Requirements Review): confirmar que los requerimientos de sistema son correctos, completos, trazables y verificables; momento típico: cierre de `F2`. Su veredicto es una decisión humana sobre la calidad de ingeniería del material, emitida **contra la revisión exacta congelada** de los documentos.
2. **Review documental por paquete** ([ciclo `docs-review`](design-document-review-lifecycle.md)): aprobar la integridad, integridad de hashes y trazabilidad de la **versión exacta** de los cinco documentos, mediante la mecánica ya implementada (`Prepare`, `Submit`, `RecordDecision`, `Promote`, `Validate`).

**Orden canónico congelado (obligatorio, de v1.2):**

1. Trabajo de fase en curso: fila `F2: en_progreso`, cinco artefactos mutables.
2. La skill declara **readiness** frente a la `SRR`: observación, nunca autorización.
3. El padre compone `preparacion-de-review` y recibe el **dossier técnico**; el dossier referencia el scope y el `package_id` esperados del paquete, sin crearlo ni operarlo. Si el dossier reporta **bloqueos**, el flujo regresa al trabajo de fase (paso 1) y la preparación se repite tras corregir.
4. Con el dossier **sin bloqueos**, el humano autoriza explícitamente `Prepare`+`Submit` (operaciones **pre-review**): el conjunto exacto esperado de los cinco documentos se copia, hashea y manifiesta, el paquete entra `en_verificacion` y los documentos vivos quedan **congelados contra mutación**.
5. El equipo humano de ingeniería conduce la `SRR` **contra esa revisión exacta congelada** (`package_id` + hashes del manifest).
6. El veredicto humano oficial se registra/propone para `proyecto/registros/reviews.md`, **vinculado al `package_id` congelado, al conjunto de artefactos y a sus hashes**.
7. **Desfavorable o condicionado con bloqueadores abiertos**: el cierre permanece bloqueado y la revisión revisada se preserva; las correcciones vuelven a los documentos vivos solo cuando el paquete deja de estar activamente congelado; luego se crea una nueva revisión trazable del paquete (`r<NNN+1>` con `predecessor_package_id`) y se repiten la preparación y la review.
8. **Favorable sin bloqueadores abiertos**: **permite, pero no implica**, una decisión documental humana separada mediante `RecordDecision`+`Promote` (operaciones **post-veredicto**).
9. El humano autoriza explícitamente el cierre de fase.
10. El padre persiste atómicamente el cierre de fase, los espejos `doc_approval: pendiente → aprobado` y la **Functional Baseline**.
11. La fila `F3` deviene elegible y permanece **sin abrir**.

La separación de momentos es estricta: `Prepare` y `Submit` (con el congelamiento `en_verificacion`) son operaciones **pre-review**; `RecordDecision` y `Promote` son operaciones **post-veredicto**. Un veredicto técnico nunca elige automáticamente la decisión documental — `RecordDecision` solo transcribe y valida una decisión humana ya dictada, y `Promote` exige orden humana explícita — y la aprobación o promoción del paquete no representa ni sustituye el veredicto de la `SRR`; un veredicto SRR favorable no valida hashes ni integridad documental. Ambos controles deben sostenerse al cierre.

**Composición por el padre.** `f2-requisitos-sistema` es una **skill de fase pura**: declara readiness, evalúa el estado del paquete activo en solo lectura y emite al padre la especificación exacta del paquete. El orquestador padre —no la skill, no Codex por sí solo— selecciona, resuelve, carga y compone `docs-review` ante instrucción humana explícita, distinguiendo los dos momentos: **pre-review** (`Prepare`+`Submit` y congelamiento, p. ej. «Presentemos F2 a verificación») y **post-veredicto** (`RecordDecision`+`Promote`, p. ej. «Veredicto favorable registrado: procede la decisión documental»). La skill **nunca invoca otra skill** ni ejecuta mecánica de paquetes ni se autoautoriza; los comportamientos de paquete (congelamiento, rechazo completo sin aprobación parcial, resometida con `r<NNN+1>` y `carried_forward_from`, espejos derivados) son los del protocolo genérico y **no se duplican aquí**.

### Preparación de la SRR: composición con `preparacion_de_review`

La preparación del dossier técnico de la `SRR` no es trabajo de la skill de fase. La secuencia canónica (contrato completo en [design-preparacion-de-review.md](design-preparacion-de-review.md)):

1. `f2-requisitos-sistema` declara **readiness** frente a la `SRR` y los criterios de cierre: es una observación, no una autorización.
2. Ante instrucción humana explícita, el padre compone la capacidad genérica de tarea puntual `preparacion-de-review` con el tipo de review (`SRR`) y la fase activa (`F2`); la capacidad, en solo lectura, arma el **dossier técnico de review** (inventario de evidencia, evaluación de criterios de entrada/salida, bloqueos, hallazgos y riesgos abiertos, agenda propuesta, conclusión de readiness). El dossier referencia el scope esperado (`f2-requisitos-sistema`) y el patrón de `package_id` (`f2-requisitos-sistema-formal-r<NNN>`); cuando el paquete ya fue sometido, referencia el `package_id` congelado y los hashes del manifest. **No** crea ni opera el paquete: es un documento lógico estructurado, sin manifest ni snapshots propios, y no es una superficie de autoridad.
3. Si el dossier reporta **bloqueos o faltantes**, el flujo regresa al trabajo de fase: se corrige en los documentos vivos, se re-evalúa readiness y se repite la preparación. Si concluye readiness **sin bloqueos**, el humano autoriza explícitamente `Prepare`+`Submit`; el conjunto exacto de los cinco documentos se copia, hashea y manifiesta y entra `en_verificacion` congelado.
4. El **humano conduce la `SRR`** con esa agenda y **contra la revisión exacta congelada**, y emite el veredicto: la capacidad de preparación y la skill de fase nunca lo emiten ni lo interpretan.
5. El padre persiste el veredicto —con identidad, fecha, fuente y el `package_id` congelado, el conjunto de artefactos y los hashes revisados— en `proyecto/registros/reviews.md` (registro futuro; su plantilla se materializa en un cambio posterior) como **único escritor**, bajo autorización humana explícita. Hasta que esa plantilla exista, la evidencia del veredicto se transporta en la propuesta de cierre y en la entrada de baseline de `configuracion.md`, como ya lo define la conjunción.

Esta preparación es un **servicio de apoyo a la review** — `preparacion-de-review` prepara el dossier; la review técnica en sí la conduce y decide el equipo humano de ingeniería —, no un tercer control de veredicto: los controles con autoridad de decisión siguen siendo dos (review técnica `SRR` y review documental por paquete), independientes y con la secuencia canónica congelada fijada arriba.

### Conjunción exacta del cierre y constitución de la Functional Baseline

La **Functional Baseline** — que «define qué debe hacer el sistema» y «se congela al cierre de `SRR`» según el [catálogo de baselines](../../framework/marco/baselines/catalogo_baselines.md) — se constituye **solo** cuando concurren conjuntamente:

| # | Condición | Evidencia exigible |
| --- | --- | --- |
| 1 | Veredicto favorable de la `SRR` **sobre la revisión exacta congelada** | Decisión humana de la review técnica, con responsable, fecha y fuente, registrada y trazable en `proyecto/registros/reviews.md` (registro futuro; su persistencia la ejecuta el padre con autorización humana, single-writer) y **vinculada al `package_id` exacto congelado revisado, al conjunto de los cinco artefactos y a los hashes del manifest**; transportada en la propuesta de cierre |
| 2 | Paquete documental completo `aprobado` y **promovido** | Copia aprobada válida en `proyecto/docs-aprobados/f2-requisitos-sistema/`, conjunto exacto de los cinco snapshots, `content_sha256` recomputados en solo lectura y coherentes, identidad coherente, attestation terminal humana; resultado de la decisión documental separada y explícita (`RecordDecision`+`Promote`) posterior al veredicto |
| 3 | Decisión humana explícita de cierre de fase | Autorización explícita del cierre emitida por el humano, transportada como evidencia en la propuesta |

Falta cualquiera de las tres → no hay cierre, no hay baseline, no hay espejos `aprobado`. Readiness, veredicto técnico favorable y paquete aprobado **habilitan** la propuesta de cierre; solo la decisión humana la ejecuta.

### Cambio atómico de cierre + registro de baseline

Con la conjunción verificada y la autorización humana emitida, la capacidad propone **un único bloque coherente** que el padre persiste como un solo cambio:

| Fuente | Cambio propuesto (anterior → propuesto) | Precondición |
| --- | --- | --- |
| `proyecto/estado/estado_fases.md` | Fila `F2: en_progreso → cerrada` | Conjunción completa verificada |
| `proyecto/fases/f2_requisitos_sistema/**` (cinco artefactos) | `doc_approval: pendiente → aprobado` (espejo derivado del manifest), con entradas de historial coherentes con la attestation | Paquete promovido con gates completos |
| `proyecto/registros/configuracion.md` | Registro de la **Functional Baseline**: ítem de baseline con su contenido (referencias a los cinco artefactos aprobados y su versión), estado de aprobación, ubicación | Mismo cambio; la baseline queda identificable per [reglas del ciclo](../../framework/marco/reglas_del_ciclo.md) |
| `proyecto/estado/proyecto_actual.md` | `active_phase: F2` (sin cambio tras el cierre; la selección del siguiente trabajo la resuelve el padre); `project_status: proyecto_formal` (sin cambio) | — |

La fila `F3` permanece `no_iniciada`: la capacidad informa, como observación, que `F3` resulta elegible para una apertura separada controlada por el padre. Nunca abre, habilita ni propone abrir `F3`.

## Integración con el ciclo de review por paquete: scope, id y especificación

El protocolo genérico (máquina de estados, manifest estricto JSON canónico, hashes, promoción, gates) vive en [design-document-review-lifecycle.md](design-document-review-lifecycle.md) y **no se repite**. Aquí solo se fija lo que `F2` aporta como consumidora:

| Campo | Valor propuesto |
| --- | --- |
| `scope` | `f2-requisitos-sistema` |
| `phase` | `F2` |
| `maturity` | `formal` (única posible) |
| `package_id` | `f2-requisitos-sistema-formal-r<NNN>` — conserva el esquema genérico `<scope>-<madurez>-r<NNN>` sin cambiar el contrato; primera revisión `r001` sin predecesor; toda resometida usa `r<NNN+1>` con `predecessor_package_id`; un solo paquete activo no terminal por scope |
| Artefactos del paquete | Exactamente los cinco pares ruta viva / `document_type` de la [tabla de artefactos](#artefactos-obligatorios-de-f2-rutas-canónicas-frontmatter-y-ciclo) — sin faltantes ni extras |

Comportamiento de la capacidad según el estado del paquete activo (idéntico al patrón de `f1_stakeholders_formal`, ver [referencia implementada](../../runtime/skills/f1-stakeholders-formal/SKILL.md)):

- **`en_verificacion`**: los cinco documentos vivos congelados; la capacidad espera y no propone mutaciones de contenido sobre ellos. Es sobre esta revisión exacta congelada que se conduce la `SRR`.
- **`rechazado`** (el rechazo de cualquier documento es del paquete completo, sin aprobación parcial): corresponde a un veredicto desfavorable o condicionado con bloqueadores abiertos, con el cierre bloqueado y la revisión revisada preservada; atiende los hallazgos corrigiendo solo los documentos vivos vía propuestas al padre — corrección que procede cuando el paquete deja de estar activamente congelado, tras la decisión documental humana —; la resometida usa un nuevo `package_id` (`r<NNN+1>`) referenciando al predecesor, el paquete rechazado se preserva íntegro con sus hallazgos, y con la resometida se repiten la preparación (`preparacion-de-review`) y la review técnica.
- **`aprobado` y promovido**: habilita —sin ejecutar por sí sola— la propuesta de cierre, que sigue requiriendo la conjunción completa con el veredicto SRR favorable sobre la revisión congelada y la decisión humana.
- Paquete ausente, parcial o con hashes divergentes: **fail-closed**, bloquea el cierre y se informa sin inferir reparaciones.

## Hoja de diseño: `f2_requisitos_sistema`

- **Id y tipo de capacidad:** `f2_requisitos_sistema` / `fase`.
- **Fichas del catálogo implicadas:** `f2_requisitos_sistema` (fase, `F2`, madurez esperada `formal`, [catálogo](../../framework/guias/skill-architecture.md)). Transversales en alcance con ficha: `trazabilidad` (materializada aquí en las dos matrices), `riesgos_y_oportunidades`, `configuracion_y_baselines`, `verificacion_y_validacion`. El proceso `requisitos` se materializa en su registro pero no existe como ficha homónima. `datos_y_documentacion` no tiene ficha (cobertura pendiente): tratamiento provisional como trazabilidad de evidencia. `lecciones_aprendidas` fuera de alcance. Capacidad de tarea puntual compuesta por el padre para la preparación de la `SRR`: **`preparacion_de_review`** (ficha en `definida`, sin `bindings`; ver [diseño genérico](design-preparacion-de-review.md)) — no es transversal de `F2` ni parte de la skill de fase: el padre la compone puntualmente. **La ficha `f2_requisitos_sistema` permanece en `estado_implementacion: definida` y sin `bindings` hasta el cambio de implementación**; este diseño no altera el catálogo.
- **Fuentes del marco (procedencia de diseño; no runtime):**
  > Las rutas siguientes documentan **de dónde proviene cada regla operativa** de esta hoja y del futuro `SKILL.md`. Son **procedencia de diseño y auditoría**: el runtime no las lee. La futura skill es autocontenida — su cuerpo embebe todas las reglas operativas específicas de `F2` — y las fuentes del marco solo pueden aparecer en su sección final de **Referencias no operativas**. Las reglas generales del agente viven en `AGENTS.md` y no se duplican; `src/se_agent/_payload/**` es un espejo generado, sin autoridad, que nunca se cita como normativa.
  - `marco/fases/fase_2_requerimientos_sistema.md` — contrato completo de la fase: entradas mínimas, actividades guía, salidas, cinco artefactos obligatorios, review, baseline, transversales, criterios de cierre.
  - `marco/reglas_del_ciclo.md` — regla de paso a `F2`; regla de trazabilidad/asignabilidad/verificabilidad de todo requerimiento.
  - `marco/reviews/catalogo_reviews.md` — `SRR / System Requirements Review`: objetivo y momento típico (cierre de `F2`).
  - `marco/baselines/catalogo_baselines.md` — contenido y congelamiento de la Functional Baseline al cierre de `SRR`.
- **Disparadores (estado/madurez):** estado global `proyecto_formal`, `active_phase: F2` (tras la apertura) o fila `F2: no_iniciada` con el gate de paso a `F2` satisfecho (primer trabajo). Tres estados reconocidos:
  1. **Primer trabajo** — fila `F2: no_iniciada`, `F1 formal: cerrada`, gate satisfecho: verifica el gate fail-closed y propone el **cambio atómico de apertura** (fila + cinco artefactos).
  2. **Continuación normal** — fila `F2: en_progreso`, estado global `proyecto_formal`: trabajo sobre requerimientos, matrices, plan y registros; espera ante paquete `en_verificacion`.
  3. **Fase ya cerrada coherentemente** — fila `F2: cerrada`, artefactos `formal`/`aprobado`, baseline registrada: idempotente; informa el estado observado, no propone cambios y no reabre nada.
  Cualquier combinación parcial o inconsistente se trata fail-closed: informa el conflicto sin inferir reparaciones.
- **Entradas mínimas** (del contrato de fase; entradas mínimas, no cuestionario bloqueante): `F1 formal` cerrada; stakeholder requirements; restricciones externas consolidadas; normativa aplicable; supuestos y decisiones de arranque ya explicitados. La ausencia de una entrada se registra como vacío explícito y se produce con lo disponible; las entradas heredadas aprobadas de `F1` son el contrato de entrada y su ausencia sí bloquea (fail-closed).
- **Salidas y artefactos:** requerimientos de sistema claros y verificables; métodos de verificación preliminares definidos; trazabilidad desde necesidad a requisito (dos matrices); baseline funcional preparada. Los cinco artefactos en sus rutas canónicas bajo `proyecto/fases/f2_requisitos_sistema/`, con frontmatter común y ciclo `doc_approval` lineal.
- **Transversales en alcance** (con límite específico):
  - `requisitos` → `proyecto/registros/requisitos.md`: entradas `system requirement` con trazabilidad bidireccional; no reescribe necesidades ni stakeholder requirements de `F1`.
  - `vv` → `proyecto/registros/vv.md`: resúmenes de método/estado/referencia al plan; sin estados de verificación ejecutada ni mezcla verificación/validación.
  - `configuracion` → `proyecto/registros/configuracion.md`: identificación de ítems y registro atómico de la Functional Baseline con el cierre.
  - `riesgos` → `proyecto/registros/riesgos.md`: riesgos técnicos siempre; con la review donde se revisaron registrada.
  - `datos_y_documentacion`: trazabilidad de evidencia provisional (sin ficha, sin registro, sin capacidad inventada).
- **Review y baseline:** review asociada **SRR** (cierre de `F2`); baseline asociada **Functional Baseline**. La skill evalúa solo **readiness** frente a ambas; no convoca, no conduce, no aprueba la review y no declara ni congela la baseline por sí misma: la baseline se registra por el padre, atómicamente con el cierre autorizado, según la conjunción. La preparación del dossier técnico de la `SRR` corresponde a la capacidad genérica `preparacion-de-review`, compuesta por el padre; la skill de fase solo declara readiness. La secuencia congelada es obligatoria: el paquete se somete y congela (`Prepare`+`Submit`, `en_verificacion`) **antes** de la `SRR`, el veredicto se emite contra la revisión congelada, y `RecordDecision`+`Promote` son una decisión documental humana post-veredicto, separada y explícita.
- **Criterios de cierre** (los del marco, íntegros, como verificación de readiness):
  - 100 % de requerimientos trazados a necesidades;
  - métodos de verificación definidos;
  - ambigüedades críticas resueltas;
  - Functional Baseline liberable;
  - *(integración con el ciclo de paquete)* existe un **paquete completo** aprobado y promovido para el scope `f2-requisitos-sistema`, con los gates de cierre completos; la sola presencia de la carpeta aprobada no basta y no existe aprobación parcial por documento.
- **Cierre y handoff:** tres juicios separados (recomendación técnica, readiness, decisión humana). La propuesta de cierre exige la conjunción de las tres condiciones — con el veredicto ligado al `package_id` congelado y sus hashes — y se resuelve atómicamente con el registro de la baseline. Handoff: `F3` informada como elegible, fila sin cambio.
- **Límites de autoridad:** nunca autoriza el cierre, las aprobaciones de artefactos, el veredicto SRR ni la constitución de la baseline; nunca copia, promueve, revisa, aprueba, firma ni decide paquetes; nunca escribe en `proyecto/docs-verificacion/**` ni `proyecto/docs-aprobados/**` (solo lectura); nunca invoca otra skill ni se autoautoriza; nunca abre ni habilita `F3`; nunca genera arquitectura, asignación a CIs ni diseño detallado; nunca muta `interfaces` ni `lecciones_aprendidas`; nunca reinicia registros ni rehace trabajo de `F1`; no declara `active_maturity: preliminar` en ningún artefacto.
- **Nombre ejecutable:** `f2-requisitos-sistema` (directorio + frontmatter `name` + `id` en el registry; se declara en el cambio de implementación posterior, junto con el `bindings` de la ficha y la actualización del catálogo a `mapeada`).
- **Fuentes de estado e hitos que consulta:** `proyecto/estado/proyecto_actual.md`, `proyecto/estado/estado_fases.md` y `proyecto/hitos/hito_aprobacion_trabajo.md` — solo lectura; `proyecto/docs-verificacion/**` y `proyecto/docs-aprobados/**` — solo lectura (validación de paquetes y gates). En el repo de producto, la plantilla común vive en `framework/proyecto/**`; en runtime se lee la instancia `proyecto/**`.
- **Propuesta de actualización:** tres formas — cambio atómico de apertura; actualizaciones de contenido en curso (registros mutables + cinco artefactos); propuesta de cierre con baseline (conjunción + autorización). Siempre valor anterior → valor propuesto, justificación, procedencia, vacíos y contradicciones. La skill produce el bloque para el padre y **no escribe** en `proyecto/**`. El veredicto SRR no es una propuesta de esta skill: su entrada en `proyecto/registros/reviews.md` la produce la capacidad genérica `preparacion-de-review` y la persiste el padre con autorización humana (single-writer), transportando el `package_id` congelado, el conjunto de artefactos y los hashes revisados.
- **Decisiones de persistencia:** madurar registros existentes sin reiniciarlos; artefactos únicos por proyecto (sin copias por madurez; no aplica en `F2` pero se mantiene la convención); sin fabricar contenido; single-writer; baseline atómica con cierre; veredicto SRR persistido por el padre en `proyecto/registros/reviews.md` (registro futuro) bajo autorización humana, nunca por la skill de fase.
- **Gaps sin resolver:** cobertura de `datos_y_documentacion` (decisión pendiente del catálogo). Las tres preguntas abiertas de la v1.0 quedaron resueltas en la v1.1: ver [Decisiones adoptadas y trabajo diferido](#decisiones-adoptadas-y-trabajo-diferido). La secuencia de revisión congelada quedó decidida en la v1.2, sin gaps abiertos derivados de ella.

### Esquema de secciones del futuro `SKILL.md` (plantilla de fase, doce secciones)

`F2` aplica el [ciclo de review por paquete](design-document-review-lifecycle.md), por lo que añade la sección dedicada tras «Review y baseline» (regla de la [plantilla de skill de fase](design-skill-marco.md#plantilla-de-skill-de-fase)):

| # | Sección | Contenido clave en esta skill |
| --- | --- | --- |
| 1 | Objetivo operativo | Pregunta central «¿Qué debe hacer técnicamente el sistema?»; requerimientos verificables y trazables que habiliten la Functional Baseline; el humano decide reviews, cierre y baseline. |
| 2 | Rol y límites de fase | Proyección de `f2_requisitos_sistema`; madurez `formal` única (sin modo preliminar); presupone `F1 formal` cerrada y gate de paso a `F2` satisfecho; no mezcla requerimiento con solución; nada de `F3+` (sin arquitectura, sin asignación a CIs, sin diseño). |
| 3 | Entradas mínimas | Las cinco del marco; insumos aprobados de `F1` como contrato de entrada (fail-closed si faltan); modelo de evidencia de cuatro clases; preguntas progresivas. |
| 4 | Capacidades operacionales | Las siete actividades guía del marco operacionalizadas y seleccionables sin orden: derivar requerimientos técnicos, clasificarlos, revisar consistencia y completitud, analizar verificabilidad, identificar interfaces externas preliminares (sección del SyRS), definir método de verificación por requerimiento, construir trazabilidad (dos matrices). |
| 5 | Salidas esperadas | Requerimientos claros y verificables; métodos preliminares; trazabilidad necesidad → requisito; baseline funcional preparada; forma de entrega según destino (artefacto canónico o registro transversal vía propuesta). |
| 6 | Artefactos obligatorios | Los cinco del marco en sus rutas canónicas; frontmatter común; ciclo `doc_approval` lineal (sin reset de madurez); creación en el cambio atómico de apertura; expectativas al cierre por artefacto. |
| 7 | Review y baseline | `SRR` (momento típico: cierre de `F2`); Functional Baseline como baseline asociada; solo readiness frente a ambas; la baseline se constituye por conjunción y se registra atómicamente con el cierre autorizado; la preparación del dossier SRR corresponde a `preparacion-de-review` compuesta por el padre — la skill nunca convoca, conduce ni emite veredicto; el paquete se somete y congela (`Prepare`+`Submit`, `en_verificacion`) antes de la `SRR` y el veredicto se emite contra la revisión congelada. |
| 8 | Revisión de documentos obligatorios | Ciclo de paquete: scope `f2-requisitos-sistema`, id `f2-requisitos-sistema-formal-r<NNN>`, exactamente los cinco pares ruta/tipo; operaciones **pre-review** (`Prepare`+`Submit` y congelamiento `en_verificacion`) antes de la `SRR`, y **post-veredicto** (`RecordDecision`+`Promote`) separadas y explícitas; espera ante `en_verificacion`; corrección vía propuestas ante `rechazado` (paquete completo, tras descongelar) y resometida `r<NNN+1>` que repite preparación y review; habilitación del cierre con paquete promovido; validación solo lectura; nunca invoca `docs-review`: la compone el padre ante instrucción humana explícita; controles independientes de la SRR con la secuencia congelada obligatoria. |
| 9 | Procesos y registros transversales | Mutables: `requisitos` (system requirements con trazabilidad), `vv` (resúmenes + referencia al plan), `configuracion` (ítems + baseline atómica), `riesgos` (riesgos técnicos siempre). `datos_y_documentacion` como trazabilidad de evidencia provisional. `interfaces` y `lecciones_aprendidas` fuera del alcance de mutación de la skill. |
| 10 | Criterios de cierre | Los del marco íntegros (100 % trazados, métodos definidos, ambigüedades críticas resueltas, baseline liberable) más el paquete completo aprobado y promovido; verificación de readiness, no autorización. |
| 11 | Cierre, recomendación y handoff | Conjunción exacta de cierre (SRR favorable **sobre la revisión congelada** + paquete promovido + decisión humana); veredicto registrado en `proyecto/registros/reviews.md` por el padre con autorización humana, ligado al `package_id` congelado y sus hashes; cambio atómico de cierre con fila, espejos y baseline; `F3` como observación de elegibilidad, sin abrir y sin skill de transición dedicada; tres juicios separados; nunca autoaprobación. |
| 12 | Referencias | **Sección final no operativa**: las rutas del marco (`marco/fases/fase_2_requerimientos_sistema.md`, `marco/reglas_del_ciclo.md`, `marco/reviews/catalogo_reviews.md`, `marco/baselines/catalogo_baselines.md`) aparecen solo aquí, como procedencia de diseño; el cuerpo ya embebe todas las reglas operativas de `F2`. Además: los cuatro registros mutables (más `reviews.md` cuando exista), los cinco artefactos canónicos y los archivos de estado/hito. |

Frontmatter de la skill: `name: f2-requisitos-sistema`; `description` orientada al disparador (estado `proyecto_formal`, fase `F2`, derivación de requerimientos de sistema, verificabilidad, trazabilidad, SRR, Functional Baseline), como metadata de selección; licencia y metadata idénticas a las skills existentes.

### Criterios de aceptación para la implementación

- [ ] La skill distingue exactamente los tres estados reconocidos (primer trabajo con gate satisfecho, continuación normal, fase ya cerrada coherentemente) y ante el tercero responde de forma idempotente sin proponer cambios ni reabrir nada.
- [ ] El gate de paso a `F2` se verifica fail-closed antes del primer trabajo: `project_status: proyecto_formal`, fila `F1 formal: cerrada`, fila `F2: no_iniciada`, regla de paso a `F2` satisfecha y paquete `f1-stakeholders` promovido; ante cualquier inconsistencia informa el conflicto sin inferir reparaciones.
- [ ] La apertura propone un único bloque coherente y atómico: fila `F2: no_iniciada → en_progreso`, `active_phase: F1 → F2` con `project_status` y `active_maturity` sin cambio, y creación de los cinco artefactos en sus rutas canónicas con `active_maturity: formal` y `doc_approval: pendiente`. No existen estados intermedios de ese conjunto.
- [ ] Ningún artefacto de `F2` adopta nunca `active_maturity: preliminar`; no hay ciclo preliminar→formal ni copias por madurez.
- [ ] Toda salida distingue explícitamente `hechos verificados`, `supuestos`, `vacíos` y `contradicciones`; no fabrica contenido para llenar vacíos.
- [ ] La trazabilidad se produce como **dos matrices separadas** con los IDs exactos del SyRS y del registro `requisitos`; una discrepancia de IDs entre SyRS, matrices y registros se declara como contradicción.
- [ ] El registro `vv` recibe solo resúmenes (método, estado preliminar, referencia al plan); nunca estados de verificación ejecutada ni mezcla verificación/validación.
- [ ] Solo propone actualizaciones sobre `requisitos`, `vv`, `configuracion` y `riesgos` y sobre los cinco artefactos canónicos; no muta `interfaces` ni `lecciones_aprendidas`; no escribe directamente en ningún archivo de `proyecto/**` (single-writer: el padre relee, valida y persiste atómicamente).
- [ ] Integra el ciclo de review por paquete: emite la especificación exacta de `f2-requisitos-sistema-formal-r<NNN>` (scope, madurez, revisión/predecesor y exactamente los cinco pares ruta/tipo); espera sin proponer mutaciones mientras el paquete activo esté `en_verificacion`; valida estructura, hashes y evidencia solo en lectura. Nunca copia, promueve, revisa, aprueba, firma ni invoca `docs-review` u otra skill; la composición la ejecuta el padre ante instrucción humana explícita.
- [ ] La secuencia congelada es obligatoria: el paquete se somete y congela (`Prepare`+`Submit`, `en_verificacion`) **antes** de la `SRR` y la review técnica se conduce contra esa revisión exacta; las operaciones **pre-review** (`Prepare`, `Submit`, congelamiento) y **post-veredicto** (`RecordDecision`, `Promote`) quedan distinguidas; el veredicto técnico nunca elige automáticamente la decisión documental y la aprobación documental nunca sustituye al veredicto.
- [ ] Un veredicto desfavorable, o condicionado con bloqueadores abiertos, mantiene el cierre bloqueado y la revisión revisada preservada; las correcciones vuelven a los documentos vivos solo cuando el paquete deja de estar activamente congelado, seguidas de una resometida trazable `r<NNN+1>` (con `predecessor_package_id`) que repite la preparación con `preparacion-de-review` y la review técnica.
- [ ] La propuesta de cierre se emite únicamente con la conjunción completa (veredicto SRR favorable trazable **y ligado al `package_id` exacto de la revisión congelada, al conjunto de los cinco artefactos y a los hashes del manifest** + paquete completo aprobado y promovido con gates completos + autorización humana explícita del cierre) y resuelve en un único bloque coherente: fila `F2: en_progreso → cerrada`, espejos `doc_approval: pendiente → aprobado` en los cinco artefactos con historial coherente con la attestation, y **registro de la Functional Baseline en `proyecto/registros/configuracion.md` en el mismo cambio** (fila cerrada sin baseline registrada, o baseline registrada con fase abierta, son estados prohibidos).
- [ ] Nunca abre, habilita ni propone abrir `F3`: al cierre, la fila `F3` permanece `no_iniciada` y la elegibilidad se informa solo como observación sujeta a una apertura separada controlada por el padre; el estado global permanece `proyecto_formal`.
- [ ] Los riesgos técnicos se registran y reformulan en `proyecto/registros/riesgos.md` con la review donde se revisaron; los riesgos heredados se validan o reformulan sin reiniciar el registro.
- [ ] `datos_y_documentacion` se trata solo como trazabilidad de evidencia (fuente y procedencia citadas; lo referenciado y no encontrado se declara vacío), sin inventar una capacidad ni un registro.
- [ ] Los IDs de requisito usan el formato inmutable `SYS-REQ-0001` (prefijo fijo, cuatro dígitos), único por proyecto, nunca reutilizado ni renumerado, e idéntico en SyRS, ambas matrices, `requisitos.md` y `vv.md`; toda divergencia se declara como contradicción, nunca se resuelve renumerando.
- [ ] La entrada de resumen `vv` usa el esquema de madurez separado de la ejecución: `madurez_vv: preliminar`, `referencia_plan` y `estado_verificacion: no_iniciada`, sin evidencia disponible y con validación `no_iniciada`; nunca sobrecarga el estado de ejecución con `preliminar` ni declara la validación inaplicable.
- [ ] La skill declara readiness frente a la `SRR` y nunca convoca, conduce ni emite veredicto: la preparación del dossier la compone el padre con `preparacion-de-review`; un dossier con bloqueos devuelve el flujo al trabajo de fase y la preparación se repite; el veredicto se registra en `proyecto/registros/reviews.md` (cuando exista su plantilla) por el padre, con autorización humana explícita, como único escritor y ligado al `package_id` congelado, al conjunto de artefactos y a sus hashes.
- [ ] El cuerpo del `SKILL.md` es autocontenido: ninguna regla operativa de `F2` exige leer `framework/marco/**` en runtime; las fuentes del marco aparecen solo en la sección final de Referencias no operativas, y las reglas generales del agente no se duplican desde `AGENTS.md`.

## Deuda aceptada visible

| Deuda | Estado | Tratamiento |
| --- | --- | --- |
| Ejecución nativa de `tests/powershell/docs_review.tests.ps1` en **Windows PowerShell Desktop 5.1** | **Pendiente** (deuda aceptada, preexistente) | La cobertura estática Linux del núcleo `docs-review` pasó 8/8, pero la conducta del backend PowerShell en su entorno objetivo no ha sido verificada y no hay CI Windows por decisión humana. Esta deuda **no bloquea el diseño de `F2`** — `F2` consume el contrato genérico ya aprobado — pero **no debe olvidarse**: la primera ejecución real de un paquete `f2-requisitos-sistema` en un proyecto Windows hereda íntegramente este riesgo. Permanece registrada como deuda aceptada en [design-document-review-lifecycle.md](design-document-review-lifecycle.md) y aquí como referencia visible desde el diseño de la consumidora. |

## Decisiones adoptadas y trabajo diferido

Las tres preguntas abiertas de la v1.0 quedaron **resueltas** con decisión aprobada (v1.1):

| Tema (pregunta v1.0) | Decisión adoptada | Nota |
| --- | --- | --- |
| Esquema concreto de IDs de requerimiento | **`SYS-REQ-0001`** — formato inmutable, prefijo fijo + cuatro dígitos, único y permanente por proyecto; nunca reutilizado ni renumerado; idéntico en SyRS, ambas matrices, `requisitos.md` y `vv.md`. | Regla operativa de la skill (cuerpo del futuro `SKILL.md`); toda divergencia entre superficies es contradicción declarada, no renumeración. |
| Ubicación canónica del registro del veredicto SRR | **Registro futuro `proyecto/registros/reviews.md`**, común a todas las reviews formales del catálogo. La capacidad genérica `preparacion-de-review` puede **proponer** la entrada; la persiste el padre (single-writer) bajo autorización humana explícita; el veredicto nunca lo emite una skill. | El esquema del registro (id estable `REV-<TYPE>-<PHASE>-<NNN>`, veredicto, condiciones, criterios, artefactos, baseline asociada) está diseñado en [design-preparacion-de-review.md](design-preparacion-de-review.md). Su **plantilla se difiere**: no se crea `proyecto/registros/reviews.md` ni plantilla en `framework/proyecto/**` en esta unidad. Hasta que exista, la evidencia del veredicto se transporta en la propuesta de cierre y en la entrada de baseline de `configuracion.md`. |
| Ampliación del registro `vv` para estados preliminares | **Madurez separada de la ejecución**: la entrada de resumen de `F2` usa `madurez_vv: preliminar`, `referencia_plan` hacia `plan_vv_preliminar.md` y `estado_verificacion: no_iniciada`, sin evidencia disponible y con el estado de validación en `no_iniciada`. El estado de ejecución **no se sobrecarga** con `preliminar` y la validación **no se declara inaplicable**: queda `no_iniciada` hasta `F7`. | La ampliación **retrocompatible** de la plantilla `framework/proyecto/registros/vv.md` (campos dedicados `madurez_vv`/`referencia_plan`/`estado_verificacion`) es un cambio de plantilla diferido; hasta entonces las entradas transportan estos valores explícitos sin alterar el registro. |

**Decisión adoptada (v1.2): secuencia de revisión congelada.** La orden canónica queda fijada sin gaps abiertos: trabajo → readiness → dossier de `preparacion-de-review` (¿bloqueos? → volver al trabajo) → `Prepare`+`Submit` autorizados → congelamiento `en_verificacion` → `SRR` contra la revisión exacta congelada → veredicto ligado al `package_id`, al conjunto de artefactos y a los hashes → decisión documental separada (`RecordDecision`+`Promote`) → autorización humana de cierre → persistencia atómica de cierre, espejos y baseline. El detalle normativo vive en [SRR y review documental](#srr-y-review-documental-controles-independientes-y-conjunción-de-la-functional-baseline) y el diseño genérico espejo en [design-preparacion-de-review.md](design-preparacion-de-review.md) (v1.1).

**Diferido por diseño** (la evidencia sí lo decide; se lista para trazabilidad): implementación de `runtime/skills/f2-requisitos-sistema/SKILL.md`, fila en `runtime/catalogo/skill-registry.md`, `bindings` y `estado_implementacion: mapeada` en la ficha, sync de payload y suite de tests — todo según el [flujo de implementación](design-skill-marco.md#flujo-de-implementación-y-checklist-pre-commit). Superficies futuras adicionales decididas aquí: la plantilla de `proyecto/registros/reviews.md` (registro de reviews) y la ampliación retrocompatible de la plantilla `framework/proyecto/registros/vv.md` — ambas materializables en cambios posteriores con autorización humana. Cobertura de `datos_y_documentacion` y `lecciones_aprendidas`: decisión de cobertura pendiente del catálogo, sin cambios aquí.

## Relacionado

- [design-preparacion-de-review.md](design-preparacion-de-review.md) — diseño genérico de la capacidad de tarea puntual `preparacion_de_review` / futura skill `preparacion-de-review`: mapa completo de reviews, protocolo operativo, frontera de autoridad y esquema del registro futuro `reviews.md`.
- [design-skill-marco.md](design-skill-marco.md) — plantilla canónica de skills de fase, contrato de transformación marco→skill y flujo de implementación.
- [design-f1-stakeholders-handoff.md](design-f1-stakeholders-handoff.md) — diseño de las capacidades de `F1`, productor de las entradas de `F2`.
- [design-document-review-lifecycle.md](design-document-review-lifecycle.md) — ciclo de review por paquete (`docs_review`/`docs-review`), protocolo genérico y gates de cierre; núcleo implementado con verificación conductual PS5.1 pendiente.
- [domain-harness-boundary.md](domain-harness-boundary.md) — frontera dominio-harness, single-writer y dirección de dependencias.
- [skill-architecture.md](../../framework/guias/skill-architecture.md) — catálogo canónico de capacidades; ficha `f2_requisitos_sistema` (permanece `definida`).
- [fase_2_requerimientos_sistema.md](../../framework/marco/fases/fase_2_requerimientos_sistema.md) — contrato de dominio de la fase `F2`.
- [reglas_del_ciclo.md](../../framework/marco/reglas_del_ciclo.md) — regla de paso a `F2` y reglas del ciclo de vida.
- [catalogo_reviews.md](../../framework/marco/reviews/catalogo_reviews.md) — `SRR / System Requirements Review`.
- [catalogo_baselines.md](../../framework/marco/baselines/catalogo_baselines.md) — contenido y congelamiento de la Functional Baseline.
- [fases/README.md](../../framework/proyecto/fases/README.md) — convención de artefactos canónicos por fase en la plantilla de proyecto.
- [requisitos.md](../../framework/proyecto/registros/requisitos.md) · [vv.md](../../framework/proyecto/registros/vv.md) · [configuracion.md](../../framework/proyecto/registros/configuracion.md) · [riesgos.md](../../framework/proyecto/registros/riesgos.md) — registros transversales mutables en `F2`.
- [proyecto_actual.md](../../framework/proyecto/estado/proyecto_actual.md) · [estado_fases.md](../../framework/proyecto/estado/estado_fases.md) — plantillas de estado que la capacidad consulta (solo lectura).
- [SKILL.md de `f1-stakeholders-formal`](../../runtime/skills/f1-stakeholders-formal/SKILL.md) — patrón de referencia implementado: skill de fase pura integrada al ciclo de paquete por emisión.
