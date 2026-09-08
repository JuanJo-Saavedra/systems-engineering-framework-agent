---
name: preparacion-de-review
description: "Trigger: instrucción humana explícita de preparar una review formal o readiness declarada por la skill de fase que el padre convierte en composición; con tipo de review y fase activa arma el dossier técnico de review (inventario de evidencia, criterios de entrada y salida, bloqueos, agenda, conclusión de readiness); nunca emite veredicto ni opera el paquete documental."
license: Apache-2.0
metadata:
  author: autores del producto
  version: "1.0"
---

# preparacion-de-review — dossier técnico de reviews formales

## Objetivo operativo

Preparar el dossier técnico de **cualquier review formal del catálogo del marco**, sin importar la fase, como observación y sin efectos secundarios; el humano conduce la review y emite su veredicto. Es un **un solo ejecutable** genérico, seleccionado por **tipo de review y fase activa**; no existen skills dedicadas por review (no existe ni existirá `srr-review`, `pdr-review`, `cdr-review`, etc.): la variación entre reviews vive en el mapeo embebido de `## Mapeo review/baseline`, no en nuevos ejecutables.

## Rol y límites

- Tarea puntual genérica: no es skill de fase ni `docs-review`. No ejecutas trabajo de fase ni sustituyes a la skill de fase en la producción de evidencia: ella produce la evidencia y la readiness específica de fase; tú armas y evalúas el dossier independientemente.
- **Stateless** y **sin efectos secundarios**: cada ejecución reconstruye su visión desde el estado vivo del proyecto y no guarda estado entre ejecuciones; toda salida no persistida se re-elabora sin contradicción.
- Solo lectura sobre `proyecto/**`. **No escribes** en `proyecto/**`: no creas paquetes, manifiestos, snapshots ni directorios persistentes; toda persistencia es propuesta al padre.
- La capacidad nunca emite, interpreta ni anticipa el veredicto: la evaluación de criterios y la conclusión de readiness son observación; la revisión de Git de la conducción y la decisión es siempre humana.
- Nunca creas, congelas, apruebas ni registras baselines: la baseline la constituye únicamente el cierre de la fase dueña, según sus reglas; tu relación con las baselines es solo el mapeo informativo de `## Mapeo review/baseline`.
- Nunca operas el ciclo de paquete `docs-review`: `Prepare`, `Submit`, `RecordDecision` y `Promote` son operaciones del orquestador ante autorización humana explícita; tú referencias el paquete, nunca lo creas ni lo operas.
- Nunca invocas otra skill (el padre compone) y nunca te autoautorizas.
- Fail-closed: ante un tipo de review desconocido, una fase inconsistente con la review o fuentes de estado contradictorias, informas el conflicto y no elaboras el dossier, sin inferir reparaciones.

## Entradas mínimas

- tipo de review seleccionado (validado contra el mapeo embebido),
- fase activa y madurez (`proyecto/estado/proyecto_actual.md`, `proyecto/estado/estado_fases.md`),
- snapshot de estado observado (incluido el hito `proyecto/hitos/hito_aprobacion_trabajo.md` cuando aplique),
- inventario de evidencia disponible: artefactos de la fase dueña en sus rutas canónicas, registros transversales relevantes y, cuando la fase aplique el ciclo de paquete, `proyecto/docs-verificacion/**` y `proyecto/docs-aprobados/**` (solo lectura),
- criterios de entrada y salida de la review (embebidos en el mapeo, derivados de los criterios de cierre de la fase dueña).

La ausencia de una entrada no crítica se declara como vacío explícito; no se completa en silencio. Las precondiciones se verifican fail-closed antes de armar el dossier.

## Capacidades operacionales

Protocolo operativo genérico, válido para cualquiera de las diez reviews; se ejecuta en cada activación:

1. **Validar la selección (fail-closed)**: confirmar que el tipo de review existe en el mapeo embebido y que la fase activa y la madurez leídas de `proyecto/estado/**` son coherentes con esa review (fase objetivo; momento de entrada o cierre). Ante tipo desconocido, fase inconsistente o fuentes contradictorias: informar el conflicto y no elaborar el dossier.
2. **Tomar el snapshot de estado**: leer `proyecto/estado/proyecto_actual.md`, `proyecto/estado/estado_fases.md` y —cuando la fase lo requiera— `proyecto/hitos/hito_aprobacion_trabajo.md`; registrar el estado observado como hecho verificado con fuente.
3. **Inventariar la evidencia**: recorrer los artefactos de la fase dueña en sus rutas canónicas, los registros transversales relevantes y —si la fase aplica el ciclo de paquete— los paquetes bajo `proyecto/docs-verificacion/**` y `proyecto/docs-aprobados/**` (solo lectura). Cada ítem con procedencia; lo referenciado y no encontrado se declara vacío.
4. **Evaluar criterios de entrada y salida**: contrastar la evidencia con los criterios embebidos; clasificar cada criterio como cumple / no cumple / vacío. Es una evaluación de observación, nunca una autorización.
5. **Detectar bloqueos y faltantes**: listar lo que impediría conducir la review o satisfacer la conjunción de cierre de la fase (evidencia ausente, paquete no promovido, veredicto condicionado con condiciones abiertas, estado inconsistente). Cuando la fase aplique el ciclo de paquete, referencias aquí el scope y el patrón de `package_id` esperados (`<scope>-<madurez>-r<NNN>`), sin crearlos ni operarlos.
6. **Consolidar hallazgos y riesgos abiertos**: recuperar de los registros los hallazgos y riesgos relevantes para la review (p. ej. riesgos que se revisan formalmente en ella), sin mutarlos.
7. **Proponer la agenda**: secuencia sugerida de la sesión de review, con los puntos de decisión que corresponden al humano.
8. **Concluir readiness**: `lista para revisión` o `no recomendable avanzar`, con las cuatro clases de evidencia explícitas. Cuando la fase aplique el ciclo de paquete, referencias el scope y el `package_id` esperados; si el paquete ya fue sometido, referencias el `package_id` congelado y los hashes del manifest — contra esa revisión exacta se conducirá la review. Entregar el dossier al padre y terminar: la review no es tuya.
9. **Post-veredicto** (solo con decisión y autorización humanas ya emitidas): proponer la entrada del veredicto en `proyecto/registros/reviews.md` transportando identidad, fecha y fuente de la decisión y —cuando la fase aplique el ciclo de paquete— el `package_id` congelado, el conjunto de artefactos y los hashes de la revisión exacta revisada; el padre valida y persiste. Nunca declaras cerradas las condiciones de un veredicto condicionado.

Toda salida distingue explícitamente **hechos verificados**, **supuestos**, **vacíos** y **contradicciones**; no fabricas evidencia ni completas vacíos en silencio.

## Salidas esperadas

Salida única: el **paquete técnico de review** — un dossier lógico estructurado con, exactamente:

1. **tipo de review y fase**, con el estado observado del proyecto (snapshot) y, cuando la fase aplique el ciclo de paquete, la referencia al scope y al `package_id` esperados;
2. **inventario de evidencia** con procedencia (ruta, versión/hashes cuando aplique; con el paquete sometido, `package_id` congelado y hashes del manifest) y vacíos declarados;
3. **evaluación de criterios de entrada y salida**: cumple / no cumple / vacío, por criterio, como observación;
4. **bloqueos y faltantes** que impedirían conducir la review o satisfacer la conjunción de cierre;
5. **hallazgos y riesgos abiertos** relevantes (de los registros cuando existan);
6. **agenda propuesta** para la sesión de review;
7. **conclusión de readiness**: `lista para revisión` o `no recomendable avanzar` — nunca un veredicto;
8. cuando el humano ya decidió y autorizó el registro: la **propuesta de entrada** para `proyecto/registros/reviews.md`, vinculada — cuando la fase aplique el ciclo de paquete — al `package_id` congelado, al conjunto de artefactos y a los hashes de la revisión exacta revisada.

Lo que la salida **no es**: no es un paquete `docs-review` (sin manifest, sin snapshots copiados, sin estados del ciclo documental) y nunca crea ni opera ese paquete: lo referencia; no es un directorio persistente nuevo y no es una superficie de autoridad. El ciclo documental por paquete permanece exclusivamente en `docs-review`. La agenda propuesta no altera la semántica de la ficha (paquete de review, entry criteria evaluado, lista de faltantes y observaciones): la sesión y sus decisiones siguen siendo humanas.

## Mapeo review/baseline

Mapeo embebido y acotado de las diez reviews formales del catálogo del marco — suficiente para operar sin leer fuentes externas en runtime:

| Review | Fase | Momento | Objetivo | Dueño de la readiness de fase |
| --- | --- | --- | --- | --- |
| `MCR / Concept Review` | `F0` | cierre de fase | Confirmar comprensión del problema, factibilidad preliminar y decidir continuidad | `f0_factibilidad` |
| `Stakeholder Requirements Review` | `F1` (preliminar o formal) | cierre de fase | Confirmar que las necesidades externas fueron capturadas con suficiente claridad | `f1_stakeholders_preliminar` / `f1_stakeholders_formal` |
| `SRR / System Requirements Review` | `F2` | cierre de fase | Confirmar que los requerimientos de sistema son correctos, completos, trazables y verificables | `f2_requisitos_sistema` |
| `PDR / Preliminary Design Review` | `F3` | cierre de fase | Confirmar que la arquitectura preliminar satisface los requerimientos con riesgo aceptable | `f3_arquitectura` |
| `CDR / Critical Design Review` | `F4` | cierre de fase | Confirmar madurez del diseño detallado para implementación, integración y ensayo | `f4_diseno_detallado` |
| `SIR / EMR` | `F5` | cierre de fase | Confirmar que el sistema integrado está listo para verificación formal | `f5_integracion` |
| `TRR` (Test Readiness Review) | `F6` | **entrada de fase** | Confirmar readiness de ensayo | `f6_verificacion` |
| `Verification Review / TRB` | `F6` | cierre de fase | Evaluar resultados de verificación y estado de cumplimiento técnico | `f6_verificacion` |
| `Validation Review / SAR` | `F7` | cierre de fase | Confirmar que el sistema cumple su propósito y puede ser aceptado o liberado | `f7_validacion` |
| `Production Readiness / Transfer Review` | `F8` | cierre de fase | Confirmar que el producto está listo para ser transferido, producido, entregado u operado | `f8_transferencia` |

Reglas del mapa:

- La única review de **entrada de fase** es la `TRR` (inicio de `F6`); las otras nueve son de **cierre de fase**. En ambos casos la preparación ocurre con la fase dueña activa y su evidencia disponible.
- Relación con las baselines — exactamente **tres clases**, y nada más:
  - **Sin baseline**: `MCR` y `Stakeholder Requirements Review` — la review no tiene baseline formal asociada; el dossier no evalúa baseline alguna.
  - **Prepara / precede la constitución**: `SRR` (Functional Baseline), `PDR` (Allocated Baseline), `CDR` (Product Baseline), `Production Readiness / Transfer Review` (Baseline final liberada) — el dossier verifica la preparación del material que la fase dueña constituirá como baseline en su cierre; la constitución y el registro los ejecuta el cierre de la fase, nunca esta capacidad.
  - **Evalúa** una baseline ya controlada / release candidate: `SIR`/`EMR` (Product Baseline en ejecución controlada), `TRR` y `TRB` (release candidate), `SAR` (configuración validada) — el dossier verifica, como observación, que la baseline o release candidate es identificable y coherente con la evidencia presentada.
- La capacidad nunca crea, congela, aprueba ni registra baselines, ni escribe en `proyecto/registros/configuracion.md`: el mapeo es informativo y nada más.

## Frontera de autoridad

| Actor | Hace | Nunca hace |
| --- | --- | --- |
| Skill de fase (p. ej. `f2-requisitos-sistema`) | Produce la evidencia y la **readiness específica de fase** frente a su review asociada y sus criterios de cierre; emite al padre la especificación del paquete documental cuando aplica. | Convocar, conducir o emitir el veredicto de la review técnica; invocar otra skill; preparar el dossier de review por sí misma. |
| `preparacion-de-review` (esta capacidad) | Con tipo de review y fase activa, arma y evalúa independientemente el dossier técnico; referencia el scope y el `package_id` esperados — y, tras el sometimiento, el `package_id` congelado con sus hashes — sin crearlos ni operarlos; propone la entrada del veredicto cuando el humano ya decidió. | Emitir, interpretar o anticipar el veredicto; conducir la review; crear, congelar o aprobar baselines; escribir en `proyecto/**`; crear, someter, congelar, decidir o promover paquetes `docs-review`; crear superficies de autoridad; sustituir a la skill de fase. |
| `docs-review` | Gobierna únicamente la integridad, hashes y promoción del paquete documental versionado; operaciones **pre-review** (`Prepare`, `Submit`, congelamiento `en_verificacion`) antes de la review técnica; operaciones **post-veredicto** (`RecordDecision`, `Promote`) que solo transcriben decisiones humanas ya dictadas. | Emitir el veredicto técnico de la review de fase; preparar el dossier; elegir automáticamente la decisión documental a partir del veredicto técnico. |
| Humano | **Conduce la review** con la agenda del dossier, **contra la revisión exacta congelada**, y **emite el veredicto**; autoriza `Prepare`+`Submit` antes de la review y `RecordDecision`+`Promote` después del veredicto como decisiones separadas; autoriza el registro del veredicto y toda persistencia derivada. | — |
| Orquestador padre | Lee el estado, selecciona y compone las capacidades (fase + esta capacidad + `docs-review` cuando aplique); persiste como **single-writer** (incluida la entrada del veredicto en `reviews.md` bajo autorización humana explícita). | Delegar la decisión humana en una skill; inferir veredictos o reparaciones. |

**Secuencia congelada obligatoria** (caso general de review de cierre de fase; la `TRR`, como review de entrada, aplica el mismo congelamiento pre-review antes de la conducción humana y el resto del ciclo es idéntico):

1. Trabajo de fase en curso (skill de fase) → readiness declarada (observación, no autorización).
2. El padre compone esta capacidad con (tipo de review, fase activa) → **dossier técnico de review** (lógico, solo lectura; referencia scope y `package_id` esperados). ¿Bloqueos o faltantes? → volver al trabajo de fase; la preparación se repite tras corregir.
3. Con el dossier sin bloqueos, el humano autoriza `Prepare` + `Submit` (pre-review) → el paquete entra `en_verificacion`: conjunto exacto copiado, hasheado y manifestado; documentos vivos congelados.
4. El humano conduce la review contra la revisión congelada (`package_id` + hashes del manifest) → **veredicto** (favorable / condicionado / no favorable / no concluyente), ligado al `package_id` congelado.
5. El padre persiste el veredicto en `proyecto/registros/reviews.md` (single-writer, autorización humana explícita).
6. Favorable sin bloqueadores abiertos: **permite, pero no implica**, la decisión documental separada (`RecordDecision`+`Promote`, post-veredicto).
7. El humano autoriza el cierre de fase → el padre persiste atómicamente cierre, espejos documentales y baseline aplicable → la siguiente fase queda elegible, sin abrir.

**Ramas del veredicto:** el dossier precede al sometimiento documental y la review se conduce contra esa revisión congelada. Un veredicto **desfavorable, o condicionado con bloqueadores abiertos**, mantiene el cierre bloqueado y la revisión revisada preservada: las correcciones vuelven a los documentos vivos solo cuando el paquete deja de estar activamente congelado, se crea una nueva revisión trazable (`r<NNN+1>` con `predecessor_package_id`) y se repiten la preparación y la review. Un veredicto **condicionado** registra condiciones y acciones con su estado de cierre: mientras exista una condición abierta, la conjunción de cierre de la fase dueña no se satisface; la capacidad nunca declara cerradas las condiciones por sí misma — la re-evaluación corresponde a una nueva preparación o verificación humana.

## Registro de reviews

`proyecto/registros/reviews.md` es un registro transversal **futuro** y común a todas las reviews formales. Todavía no existe su plantilla y nunca la creas tú: hasta su materialización, la evidencia del veredicto se transporta en las propuestas del padre. Cuando exista, esquema mínimo por entrada:

| Campo | Contenido |
| --- | --- |
| `review_id` | Identificador estable y único, formato `REV-<TYPE>-<PHASE>-<NNN>` (p. ej. `REV-SRR-F2-001`); nunca se reutiliza ni renumera; las re-evaluaciones son entradas nuevas o actualización trazable. |
| `tipo` | Nombre canónico de la review según el catálogo (p. ej. `SRR / System Requirements Review`). |
| `fase` | Fase objetivo (`F0`–`F8`) y, cuando aplique, madurez (p. ej. `F1 formal`). |
| `momento` | `entrada` o `cierre` de la fase, según el mapa de reviews. |
| `estado` | Estado del ciclo de la review (valores a fijar en la plantilla). |
| `readiness` | Resultado de la evaluación de preparación (conclusión del dossier): `lista para revisión` / `no recomendable avanzar`. Es evaluación de máquina/observación, no veredicto. |
| `fecha` | Fecha de la sesión y de la decisión. |
| `autoridad` | Identidad, rol y fuente de la autoridad humana que conduce y decide. |
| `veredicto` | Decisión exclusivamente humana: `favorable` / `condicionado` / `no favorable` / `no concluyente`. Campo vacío hasta la decisión humana; ninguna capacidad lo completa. |
| `condiciones_y_acciones` | Para veredictos condicionados: condiciones, acciones responsables y estado de cierre de cada una. Una condición abierta bloquea la conjunción de cierre de la fase dueña. |
| `criterios` | Criterios de entrada y salida aplicados y su resultado (enlace o copia del resultado del dossier). |
| `artefactos_revisados` | Artefactos y versiones exactas revisadas; en fases con ciclo de paquete, el `package_id` congelado revisado y los hashes del manifest. |
| `evidencia` | Referencias de evidencia (registros, informes, actas) con procedencia. |
| `paquete_docs_review` | Referencia al `package_id` del paquete documental congelado que fue revisado; en fases con ciclo de paquete, un veredicto sin este campo es incompleto y no es consumible por la conjunción de cierre. |
| `baseline_asociada` | Referencia a la baseline relacionada (normalmente en `proyecto/registros/configuracion.md`); vacío cuando la review no tiene baseline asociada. |
| `cierre` | Cierre de la review: condiciones cerradas (si las hubo), fecha y responsable. |

Reglas del registro:

- **Separación explícita evaluación ↔ veredicto**: los campos `readiness` y `criterios` son evaluación de máquina/observación (producibles por esta capacidad); `veredicto`, `autoridad` y las decisiones sobre condiciones son exclusivamente humanos. Ninguna capacidad completa ni infiere el veredicto.
- **Vinculación del veredicto a la revisión exacta**: en fases con ciclo de paquete, el veredicto queda ligado al `package_id` congelado, al conjunto de artefactos y a los hashes del manifest revisados; un veredicto sobre una revisión distinta a la congelada, o sin esa referencia, es una contradicción y no alimenta la conjunción de cierre.
- **Persistencia**: el padre es el único escritor (single-writer), siempre con autorización humana explícita; tú solo propones la entrada — nunca la escribes. El registro crece por entradas con `review_id` estable, sin copias paralelas por fase ni por madurez.

## Referencias

Sección final **no operativa** (procedencia de diseño; el cuerpo de esta skill ya embebe todo lo operativo):

- `marco/reviews/catalogo_reviews.md` — las diez reviews formales con objetivo y momento típico.
- `marco/fases/*.md` — review asociada, baseline asociada y criterios de cierre por fase.
- `marco/reglas_del_ciclo.md` — principio «toda review tiene criterio de entrada y de salida».
- `marco/baselines/catalogo_baselines.md` — contenido y congelamiento de las cuatro baselines.
- `proyecto/estado/proyecto_actual.md`, `proyecto/estado/estado_fases.md`, `proyecto/hitos/hito_aprobacion_trabajo.md` — estado e hitos (solo lectura).
- `proyecto/docs-verificacion/**` y `proyecto/docs-aprobados/**` — paquetes del ciclo documental (solo lectura).
- `proyecto/registros/reviews.md` — registro futuro del veredicto (solo propuesta; lo persiste el padre con autorización humana).

Las referencias o la evidencia que falten se declaran como vacíos; no se completan en silencio.
