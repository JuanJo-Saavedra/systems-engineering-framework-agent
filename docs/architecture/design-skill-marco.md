---
document_type: arquitectura_plantilla_skills
language: es
version: 1.4
status: canonico
---
# Plantilla canónica para diseñar skills operativas desde el marco

## Regla adoptada

> **Cada skill operativa incorpora íntegramente el contrato de su capacidad en `framework/marco` y lo operacionaliza sin exigir un orden fijo de ejecución. Una skill de fase declara readiness y la especificación de paquete aplicable; el orquestador padre compone las capacidades transversales o de tarea puntual ya resueltas.**

Este documento es la **plantilla duradera** para diseñar toda skill operativa futura a partir de `framework/marco`. Define el modelo de capas, el contrato de transformación marco→skill, el cruce con el catálogo de capacidades, la estructura de skill, las reglas operacionales, la política de tests y el flujo de implementación y revisión. F0 no es una excepción: es el primer caso de una transformación sistemática de todo el marco en capacidades ejecutables.

## Quick path

1. Identificar la capacidad en el [catálogo](../../framework/guias/skill-architecture.md) y su tipo.
2. Consultar el contrato de dominio en `framework/marco/**` y las plantillas de los archivos de proyecto afectados en `framework/proyecto/**`.
3. Completar la [hoja de diseño](#hoja-de-diseño-previa-a-la-implementación).
4. Escribir la skill con la plantilla correspondiente a su tipo y sus contratos.
5. Seguir el [flujo de implementación](#flujo-de-implementación-y-checklist-pre-commit).
6. Validar con tests generales y una revisión humana de fidelidad semántica.

## Modelo de cuatro capas y sus autoridades

```text
framework/marco/**
    Autoridad conceptual y de dominio
    (fases, reviews, baselines, reglas del ciclo, glosario)
              ↓ transformación operacional
framework/guias/skill-architecture.md
    Autoridad de catálogo, routing y binding
    (qué capacidad existe, cuándo aplica, enlaces ejecutables)
              ↓ proyección
runtime/skills/**/SKILL.md
    Proyección operacional autocontenida para el orquestador
    (fuente editable de las skills)
              ↓ sincronización mecánica
src/se_agent/_payload/**
    Espejo de empaquetado generado; nunca se edita a mano
```

| Capa | Ruta | Autoridad | Mantenimiento |
| ------------------------ | ----------------------------------------- | --------------------------------------------------------------------------------------------------------------------- | ---------------------------------- |
| Marco conceptual | `framework/marco/**` | Significado del dominio: contratos de fase, artefactos, reviews, baselines y guardas del método. | Equipo de ingeniería de sistemas. |
| Catálogo de capacidades | `framework/guias/skill-architecture.md` | Qué asistencia existe, cuándo aplica, qué entradas/salidas y guardas exige; define ids conceptuales y `bindings`. | Autores del producto. |
| Skills operativas | `runtime/skills/**/SKILL.md` | Comportamiento ejecutable de una capacidad. Implementa; nunca redefine el dominio. | Autores del producto. |
| Espejo de empaquetado | `src/se_agent/_payload/**` | Ninguna. Copia byte a byte de lo instalable. | Generado por el packager. |

**Contratos complementarios que no agregan una capa a la transformación:**

- **Plantilla de proyecto** (`framework/proyecto/**`): fuente de consulta para las rutas, la estructura y el vocabulario común de los archivos que cada proyecto administra. Define la forma esperada, no el estado real de una ejecución.
- **Instancia de proyecto** (`proyecto/**`): autoridad sobre el contenido vivo del proyecto concreto —estado, hitos, artefactos y registros—. Cada proyecto es propietario de estos archivos y conserva continuidad histórica sobre la plantilla común.

La skill se diseña consultando `framework/proyecto/**`, pero en runtime lee la instancia `proyecto/**`; nunca presenta la plantilla como evidencia del proyecto ni escribe en `framework/proyecto/**`.

**Artefactos de inventario que NO son capas de autoridad:**

- **Registry operativo** (`runtime/catalogo/skill-registry.md`, instalado como `catalogo/skill-registry.md`): inventario **manual** de skills disponibles. CI y tests verifican su coherencia bidireccional con `runtime/skills/` y nunca lo generan ni modifican. No duplica el routing ni las guardas.
- **Índice técnico del harness** (`.atl/skill-registry.md`): índice **generado**, exclusivo del harness de desarrollo, de alcance técnico. No se empaqueta, no se instala y no debe fusionarse con el catálogo.

Regla: ninguna capa inferior (skill, subagente, índice, adaptador) es autoridad sobre el significado del dominio. El marco es fuente del dominio conceptual; el catálogo, del significado y routing; `framework/proyecto/**`, de la plantilla común; la instancia `proyecto/**`, del estado y la evidencia del proyecto; el registry, de la disponibilidad.

## Contrato de transformación marco → skill

"Pasar el marco" **no significa copiarlo literalmente**. La skill es autosuficiente durante la ejecución: contiene la capacidad relevante transformada al lenguaje operativo del agente, no un enlace al documento del marco ni un resumen.

La transformación **preserva** estos elementos del contrato de dominio:

| Elemento preservado | En la skill |
| --------------------- | ------------------------------------------------------------------------------------------------ |
| Objetivo | Enunciado como resultado operativo verificable. |
| Alcance y madurez | Límites de fase y nivel (`preliminar`/`formal`) explícitos. |
| Entradas | Entradas mínimas del marco, sin convertirlas en condiciones de arranque bloqueantes. |
| Capacidades | Las `Actividades guía` del marco, operacionalizadas como comportamiento consciente del estado. |
| Salidas | Resultados esperados, con forma de entrega según el destino del artefacto. |
| Artefactos | Los obligatorios del marco, con su política de ubicación. |
| Transversales | Los registros transversales dentro del alcance declarado de la fase. |
| Review / baseline | La review asociada y el tratamiento de baseline del marco, sin añadir ni quitar. |
| Madurez | La madurez esperada de la ficha del catálogo. |
| Criterios de cierre | Los del marco, íntegros y sin modificaciones. |
| Handoff | La preparación de la fase siguiente, separada de la autorización. |
| Estado e hitos | Las fuentes de estado que consulta y la propuesta estructurada que entrega al padre, sin escritura autónoma. |
| Límites de autoridad | Guardas, gates y reglas de decisión humana. |

Lo que **cambia es la forma**: de descripción de dominio a comportamiento que actúa. Ejemplos aprobados:

| Frase del marco | Comportamiento operativo en la skill |
| ----------------------------- | -------------------------------------------------------------------------------- |
| "Identificar stakeholders" | Evaluar el estado del mapa, detectar ausencias y producirlo o actualizarlo. |
| "Estimar ROM" | Construir o madurar un rango trazable, con supuestos e incertidumbre declaradas. |
| "Identificar riesgos" | Consultar y actualizar el registro transversal con evidencia y procedencia. |
| "Recomendar Go/No-Go" | Emitir una recomendación técnica separada de la decisión humana. |
| "Material suficiente para F1" | Evaluar explícitamente la preparación y los vacíos del handoff. |

Evitar los dos extremos: una skill demasiado resumida que no sabe ejecutar la fase, o un manual secuencial que obliga a seguir pasos independientemente del estado.

## Cruce con el catálogo de capacidades

El catálogo usa **seis tipos** de capacidad, no tres familias:

| Tipo del catálogo | Ejemplo | Papel en el diseño de skills |
| --------------------- | ---------------------------------------------------------------------- | -------------------------------------------------------- |
| Orquestación general | `orquestacion_del_proyecto` | Decide siguiente paso, fase activa y modo de ejecución. |
| Control de avance | `gap_analysis_de_fase` | Reporta faltantes y bloqueos; no cierra ni aprueba. |
| Fase | `f0_factibilidad`, `f2_requisitos_sistema` | Proyección principal de un contrato de fase. |
| Transición | `handoff_presupuesto_a_proyecto` | Consolida hitos y vacíos entre estados del proyecto. |
| Transversal | `riesgos_y_oportunidades`, `trazabilidad`, `decisiones_tecnicas` | Registros y prácticas reutilizados en varias fases. |
| Tarea puntual | `redaccion_de_artefacto`, `preparacion_de_review`, `docs_review` | Producir un artefacto, preparar un REVIEW formal del marco o gobernar el ciclo genérico de un paquete documental. |

Reglas de mapeo:

- **Una fase puede mapear a varias capacidades.** `F1` se divide en `f1_stakeholders_preliminar` (fase, madurez `preliminar`), `handoff_presupuesto_a_proyecto` (transición) y `f1_stakeholders_formal` (fase, madurez `formal`). El diseño decide por capacidad ejecutable, no por fase. En este caso el handoff se ejecuta después de la decisión humana de aprobación y consolida el pase desde presupuesto hacia `F1 formal`; no sustituye ninguno de los dos modos de fase.
- **Una skill de fase declara, no invoca ni duplica.** Indica al padre qué transversales y tareas puntuales aplican, con su alcance específico, readiness y cualquier especificación exacta requerida (p. ej., en F0 `riesgos` siempre; para un paquete documental, scope, madurez y artefactos). El padre selecciona, resuelve, carga y compone las capacidades aplicables; la fase nunca llama a otra skill ni reproduce su técnica.
- **Cobertura pendiente:** `datos_y_documentacion` y `lecciones_aprendidas` no existen como fichas del catálogo y reciben tratamientos provisionales distintos. `datos_y_documentacion` puede manejarse provisionalmente solo como trazabilidad de evidencia (procedencia y cita de fuente) cuando la fase lo requiera, sin fingir que existe una capacidad dedicada. `lecciones_aprendidas` sigue siendo una decisión de cobertura pendiente: no se absorbe implícitamente y sus registros autoritativos específicos de fase solo se tocan cuando el marco o el catálogo lo exigen explícitamente.

## Plantilla de skill de fase

Estas son las **once secciones principales por defecto de toda skill de fase**, más la subsección obligatoria `### Cambio atómico de apertura` dentro de `## Artefactos obligatorios`. Las demás capacidades (transversales, tareas puntuales, transiciones, control) adaptan su estructura a partir de su ficha del catálogo y de su fuente de dominio; no están obligadas a estas secciones.

El cambio atómico de apertura hace visible el comportamiento específico del **primer trabajo**: la skill reconoce las precondiciones y el estado anterior, y propone al orquestador un solo bloque coherente con todas las transiciones de estado y creaciones iniciales. La skill no persiste ese bloque ni deja estados parciales; el orquestador relee, valida y escribe como single-writer.

| # | Sección | Debe contener | Evitar |
| -- | ---------------------------------- | ------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------ |
| 1 | Objetivo operativo | La pregunta central de la fase, el resultado buscado y para qué humano decide. | Copiar el objetivo textual sin definir el resultado operativo. |
| 2 | Rol y límites de fase | Vínculo con la capacidad del catálogo, madurez, qué no pertenece a la fase y qué nunca autoriza la skill. | Redefinir el dominio; ampliar el alcance a fases posteriores. |
| 3 | Entradas mínimas | Entradas del marco y regla ante ausencia (vacío declarado, no bloqueo); modelo de evidencia. | Convertir entradas mínimas en cuestionario bloqueante. |
| 4 | Capacidades operacionales | Las actividades guía operacionalizadas, seleccionables según estado, sin orden obligatorio. | Checklist fija, orden numerado obligatorio o duplicación del contenido del marco. |
| 5 | Salidas esperadas | Resultados esperados y forma de entrega (actualizar artefacto autoritativo o borrador estructurado). | Entregables vagos sin destino ni evidencia declarada. |
| 6 | Artefactos obligatorios | Los artefactos del marco y la política de ubicación (autoritativa o `ubicación pendiente`). | Inventar rutas canónicas; fabricar contenido para llenar vacíos. |
| 7 | Cambio atómico de apertura | El estado reconocido de primer trabajo; precondiciones fail-closed; fuentes autoritativas; valores anteriores → propuestos para la fila de fase, fase o madurez activa, estado global cuando aplique y creación de artefactos iniciales; invariante de que todo se persiste como un único bloque coherente por el orquestador. | Dispersar la apertura entre secciones; proponer estados intermedios; inferir transiciones o autorizaciones; escribir autónomamente; fabricar contenido inicial para llenar vacíos. |
| 8 | Review y baseline | Review asociada (nombre y momento típico), tratamiento de baseline y alcance exacto de la skill (solo readiness). Cuando la fase aplica el [ciclo de review por paquete](design-document-review-lifecycle.md), la skill añade tras esta una sección dedicada `Revisión de documentos obligatorios` con el ciclo completo del paquete y su frontera de autoridad; es un control independiente del veredicto de esta review. | Convocar, conducir o aprobar la review; declarar baselines que el marco no asigna; copiar, promover, revisar o aprobar paquetes; tratar readiness para someter como autorización. |
| 9 | Procesos y registros transversales | Cada transversal del alcance con su registro autoritativo y su límite de alcance en esta fase. | Tocar registros fuera del alcance; reproducir la técnica transversal completa. |
| 10 | Criterios de cierre | Los criterios del marco, íntegros, como verificación de readiness. Cuando la fase aplica el [ciclo de review por paquete](design-document-review-lifecycle.md), la existencia de un paquete aprobado promovido con gates satisfechos es una condición adicional del cierre. | Añadir o quitar criterios; tratar el cierre como autorización; sustituir los gates del paquete por la sola presencia de la carpeta aprobada. |
| 11 | Cierre, recomendación y handoff | Los tres juicios separados (recomendación técnica, readiness, decisión humana) y los vacíos que bloquean el handoff. | Autoaprobar cierre, transición o presupuesto; mezclar recomendación con decisión. |
| 12 | Referencias | Fuentes autoritativas de dominio y registros, en las rutas instaladas (`marco/…`, `proyecto/…`). | Referencias no instaladas o inventadas; silenciar faltantes. |

## Plantilla de skill de transición

Una transición no ejecuta el contrato completo de una fase: consolida un cambio de estado ya autorizado, preserva lo heredado y explicita los vacíos de entrada al estado siguiente. Estas son sus secciones por defecto; puede adaptarlas cuando la ficha del catálogo o el marco exijan información adicional, sin omitir el contrato de estado.

| # | Sección | Debe contener | Evitar |
| -- | --------------------------------------- | ------------------------------------------------------------------------------------------------------------------ | --------------------------------------------------------------------- |
| 1 | Objetivo y alcance de la transición | Estado de origen, estado de destino, resultado de la consolidación y decisión humana que la habilita. | Ejecutar trabajo propio de las fases de origen o destino. |
| 2 | Disparador y precondiciones | Hito o decisión requerida, consistencia mínima de estado y regla fail-closed ante evidencia ausente. | Inferir una aprobación o tratar readiness como autorización. |
| 3 | Fuentes autoritativas | Archivos vivos de `proyecto/estado/`, `proyecto/hitos/`, artefactos heredados y registros afectados. | Usar `framework/proyecto/**` como si fuera evidencia de la instancia. |
| 4 | Capacidades operacionales | Validar el hito, inventariar insumos, detectar vacíos y preservar procedencia y continuidad. | Rehacer artefactos heredados o aplicar una secuencia fija sin mirar estado. |
| 5 | Registros que continúan | Registros transversales que siguen activos, su estado y los vacíos que pasan al estado siguiente. | Abrir registros paralelos o perder historia. |
| 6 | Salidas y propuesta de estado | Handoff consolidado y bloque estructurado de actualizaciones propuestas para que el padre las valide e integre. | Escribir directamente estado, hitos o registros. |
| 7 | Cierre y autoridad | Criterios de transición, bloqueos pendientes y separación entre evaluación técnica, readiness y autorización humana. | Autoaprobar o declarar completada una transición incoherente. |
| 8 | Referencias | Contratos del marco, ficha del catálogo y rutas instaladas de la instancia. | Referencias inventadas o solo disponibles en el repositorio fuente. |

## Reglas operacionales transversales

Toda skill operativa respeta estas reglas, sin repetir justificación en cada una:

| Regla | Contrato |
| ------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Comportamiento adaptativo y consciente del estado | La skill decide el siguiente paso más útil según la evidencia disponible y la madurez de los artefactos; no hay procedimiento numerado ni orden obligatorio. |
| Modelo de evidencia | Toda salida distingue explícitamente `hechos verificados`, `supuestos`, `vacíos` y `contradicciones`. |
| Preguntas progresivas | Se pregunta según la incertidumbre real; nunca se aplica un cuestionario fijo. |
| Maduración de artefactos | Ante evidencia nueva se maduran los borradores y artefactos existentes; nunca se reinicia trabajo ya maduro ni se sobrescribe evidencia en silencio. |
| Rutas autoritativas | `framework/proyecto/**` define la plantilla común; en runtime, si el artefacto tiene ubicación autoritativa en la instancia `proyecto/`, se lee y se madura allí. |
| `ubicación pendiente` | Si un artefacto obligatorio no tiene ubicación autoritativa en la instancia, se entrega como borrador estructurado marcado `ubicación pendiente`, sin inventar rutas. La existencia de una carpeta reservada en la plantilla no basta para inventar un archivo. |
| No inventar | No se inventan estado, entregables, rutas, evidencia ni contenido para llenar un vacío; los faltantes se declaran. |
| Single-writer | Solo el orquestador padre consolida actualizaciones en los documentos autoritativos de la instancia; las skills producen propuestas estructuradas con base y procedencia. Las superficies de review humana (`docs-verificacion/**`) y de aprobación (`docs-aprobados/**`) quedan fuera de esta escritura: pertenecen a la [autoridad particionada de review](design-document-review-lifecycle.md#actores-y-autoridad) y las reserva el ingeniero humano, cuya ejecución mecánica puede delegar conversacionalmente en Codex bajo instrucción explícita (ningún agente elige `aprobado` ni `rechazado`). |
| Consistencia de estado | Una transición que afecta estado global, estado de fase e hito se propone como un único cambio coherente; el padre valida sus precondiciones y evita estados parciales antes de persistirlo. |
| Fail-closed | La evidencia no crítica faltante no bloquea: se producen borradores estructurados con los vacíos declarados de forma explícita. La ausencia de evidencia requerida sí bloquea el cierre de fase, las reviews y baselines formales y las transiciones; se solicita su restauración. La disponibilidad de skills no cambia esta regla. |

## Contrato de estado, hitos y actualizaciones propuestas

Las plantillas de `framework/proyecto/**` fijan las rutas y la forma común que las skills deben conocer. Sus equivalentes dentro de la instancia contienen el estado real:

| Archivo de la instancia | Contrato que aporta | Uso por las skills |
| ----------------------------------------------- | --------------------------------------------------------------------------------- | ------------------------------------------------------------------------------ |
| `proyecto/estado/proyecto_actual.md` | Estado global, fase y madurez activas, estado del handoff y fecha de actualización. | Determinar routing y proponer el estado global resultante. |
| `proyecto/estado/estado_fases.md` | Estado por fase, madurez esperada, review asociada y observaciones. | Evaluar readiness de la fase y proponer cambios de estado o madurez. |
| `proyecto/hitos/hito_aprobacion_trabajo.md` | Decisión humana, autorización de inicio, alcance aprobado, insumos heredados, vacíos y registros que continúan. | Validar o consolidar el pasaje de presupuesto a proyecto aprobado. |
| `proyecto/fases/**` | Instancias concretas de los artefactos de fase que el proyecto haya creado. | Madurar solo artefactos existentes; si no existe ruta autoritativa, usar `ubicación pendiente`. |
| `proyecto/registros/**` | Registros transversales continuos durante todo el ciclo de vida. | Proponer actualizaciones sobre los mismos registros, sin abrir copias paralelas. |

### Salida de skill hacia el orquestador padre

Cuando una capacidad pueda afectar el estado, su salida incluye un bloque reconocible de **propuesta de actualización**, con:

- fuente y estado observado;
- precondiciones verificadas y evidencia de la decisión humana requerida;
- campos o filas cuyo cambio se propone, expresados como valor anterior → valor propuesto;
- justificación y procedencia;
- vacíos, contradicciones o bloqueos que impiden persistir el cambio;
- artefactos y registros que deben conservar continuidad.

La propuesta no es una orden ni una autorización. El padre relee las fuentes autoritativas, comprueba que no hayan cambiado, valida las reglas del ciclo y recién entonces integra el cambio de manera coherente. La skill nunca modifica por sí sola `proyecto_actual.md`, `estado_fases.md` ni un hito de aprobación.

### Transición de presupuesto a proyecto aprobado

El flujo canónico de F1 separa claramente preparación, decisión, consolidación y ejecución formal:

1. `f1_stakeholders_preliminar` reúne material para cotizar y evalúa readiness frente al `hito_aprobacion_trabajo`; no aprueba el trabajo.
2. Un humano emite la decisión de aprobación y autoriza —o no— el inicio formal.
3. `handoff_presupuesto_a_proyecto` se activa ante esa decisión aprobatoria, consolida el hito, los insumos heredados, los vacíos antes de `F2` y los registros transversales que continúan.
4. El orquestador padre persiste de forma consistente el hito completo, el estado global `aprobado_en_transicion` y el enrutamiento `active_phase: F1` + `active_maturity: formal`; la fila `F1 formal` permanece `no_iniciada` hasta que su propia capacidad de fase comience el trabajo formal.
5. `f1_stakeholders_formal` completa los vacíos heredados. `F2` permanece `no habilitada` —su fila sigue `no_iniciada`, protegida por el gate de paso a `F2`— hasta que se cumplan los criterios de cierre formal de F1; su estado de fase no adopta el valor `bloqueada`.

Si falta la decisión aprobatoria, `project_start_authorized` no es verdadero, el hito está incompleto o las fuentes de estado se contradicen, la transición queda bloqueada y la skill informa el conflicto sin inferir ni fabricar valores.

## Review, baseline y handoff: autoridad y separación

Las skills **pueden evaluar** readiness; **nunca se autoaprueban** reviews, baselines, presupuestos ni transiciones de fase. Toda autorización es explícita y humana. Tres juicios que nunca se mezclan:

| Juicio | Quién | Ejemplo F0 |
| --------------------------------- | ---------------------------------------------------------------- | ------------------------------------------------------------------------------ |
| Recomendación técnica | La skill, con base, confianza y condiciones. | `Go`, `No-Go` o `no concluyente` mientras la evidencia sea insuficiente. |
| Readiness del dossier | La skill, como evaluación explícita de preparación y vacíos. | `borrador`, `listo para revisión` o `no recomendable avanzar`. |
| Decisión y autorización humanas | Los humanos. | Continuidad, presupuesto, veredicto de la MCR, apertura de F1. |

### Autoridad particionada sobre review y aprobación

Cuando una fase aplique el [ciclo de vida de review por paquete](design-document-review-lifecycle.md), la superficie de escritura se **particiona** por superficie, sin debilitar el single-writer:

| Superficie | Autoridad de escritura (ejecución mecánica delegable) |
| --------------------------------------------------------- | ------------------------------------------------------------------ |
| Documentos vivos y estado (`proyecto/fases/**`, `proyecto/estado/**`, `proyecto/hitos/**`, `proyecto/registros/**`) | El orquestador padre (como siempre). |
| Superficie de verificación (`proyecto/docs-verificacion/**`) y de aprobados (`proyecto/docs-aprobados/**`) | El ingeniero humano: única autoridad del sometimiento, la decisión y la attestation. Arma el paquete, somete, revisa, decide y promueve **conversacionalmente**, delegando la ejecución mecánica (copiar, computar `content_sha256`, completar el manifest, promover) en Codex bajo instrucción explícita. |

Una skill de fase que implemente esta integración evalúa readiness para someter y valida estructura y evidencia de paquetes existentes en solo lectura; **nunca** copia, promueve, revisa, aprueba, firma, elige `aprobado` ni `rechazado`, ni trata readiness como autorización. El padre persiste los espejos derivados (`doc_approval`, historial de aprobación) tras decisiones humanas ya registradas en el manifest autoritativo del paquete; jamás decide un estado de review por sí mismo. Esta partición es **autoridad particionada**, no una excepción al single-writer: cada superficie conserva exactamente un escritor autorizado, y la delegación de ejecución mecánica a Codex transfiere ejecución, nunca autoridad.

La capacidad implementada de **tarea puntual** `docs_review` (skill `docs-review`) rige el ciclo genérico de paquetes documentales. Es reutilizable entre fases, pero su único tipo de catálogo es `tarea puntual`; su hoja completa, acciones mecánicas y fronteras están en [design-document-review-lifecycle.md](design-document-review-lifecycle.md). No se duplica aquí. Es estrictamente distinta de `preparacion_de_review`: esta última queda reservada para preparar los REVIEWS formales de ingeniería de sistemas (MCR, SRR, PDR, CDR, SIR/EMR, TRR, SAR y transfer review), sin alias ni repurpose.

Una fase que aplica el ciclo declara readiness y entrega al padre la especificación exacta; el padre lógico, ejecutado por Codex, selecciona/resuelve/carga/compone `docs-review`. Codex ejecuta el contrato ya seleccionado, no decide el routing. El usuario no escribe comandos; toda mecánica requiere instrucción conversacional humana explícita. La aprobación de herramientas nunca equivale a aprobación de dominio.

**Frontera veraz de implementación:** el núcleo genérico `docs-review` está implementado en runtime, con backend PowerShell, contrato JSON canónico del manifest, registry, catálogo conceptual, payload y pruebas estáticas. El gate estático Linux actual pasó 8/8; falta ejecutar `tests/powershell/docs_review.tests.ps1` en Windows PowerShell Desktop 5.1, y no hay CI Windows por decisión humana. Las skills ya implementadas (`f0-factibilidad`, `f1-stakeholders-preliminar`, `handoff-presupuesto-a-proyecto`) no adquieren este contrato automáticamente. La primera consumidora, `f1_stakeholders_formal` ([hoja de diseño](design-f1-stakeholders-handoff.md)), ya está implementada como skill de fase pura: se integra por emisión y no compone ni opera `docs-review`; la composición la ejecuta el padre ante instrucción humana explícita. No se añadieron plantillas en `framework/proyecto/docs-*`; el backend crea paquetes bajo `proyecto/docs-verificacion/**` y `proyecto/docs-aprobados/**` a demanda.

## Nombres, bindings y madurez de implementación

| Nivel | Convención | Ejemplo | Estabilidad |
| ---------------------------------------------------------------------------- | -------------- | ------------------- | ------------------------------------------------------------------- |
| Id conceptual de capacidad (encabezado de ficha y `bindings` del catálogo) | `snake_case` | `f0_factibilidad` | Estable: no cambia al renombrar el ejecutable. |
| Nombre ejecutable (directorio, frontmatter `name`, `id` en el registry) | `kebab-case` | `f0-factibilidad` | Cambia solo con edición explícita del registry y del `bindings`. |

- **`description`**: orientada al disparador — fase/estado del proyecto, conceptos y salidas que activan la selección. Es metadata de selección, no publicidad.
- **Binding**: se declara en el campo `bindings` de la ficha del catálogo y se refleja en el registry operativo; ningún `SKILL.md` lo redefine.
- **Madurez del enlace** (`estado_implementacion` de la ficha):
  - `definida`: la capacidad existe en el dominio y está descrita en el catálogo; sin ejecutable verificado (valor por defecto global).
  - `mapeada`: existe un enlace declarado a una skill o subagente, sin verificación de comportamiento completa.
  - `verificada`: el enlace pasó pruebas de comportamiento (selección, degradación, fronteras).
- **Coherencia registry ↔ skills**: el registry se mantiene **a mano**; la verificación es bidireccional (cada skill tiene exactamente una entrada válida, cada entrada resuelve a una skill existente, sin duplicados ni obsoletos) y corre en tests/CI sin generar ni modificar el archivo.

## Política de tests generales

Los tests verifican **invariantes estructurales**, no decisiones editoriales.

**Tests de skill y registry** (`tests/unit/test_registry_coherence.py` + `tests/helpers/registry_check.py`):

- Descubren dinámicamente las skills en `runtime/skills/*/SKILL.md` — sin ids ni cantidades fijas.
- Validan metadata estructural del frontmatter: `name` es string no vacío e igual al nombre del directorio (que debe ser `kebab-case`); `description` es string no vacío.
- Verifican coherencia bidireccional del registry: filas exactas, `ruta` exacta (`.agents/skills/<id>/SKILL.md`), `skills_available` igual al número de filas, sin duplicados, faltantes, obsoletos ni filas malformadas.
- El verificador es de solo lectura: el registry y las fuentes quedan byte a byte idénticos tras cada verificación.
- Los casos negativos usan mutaciones dinámicas y fixtures sintéticos; nunca tocan el registry canónico.

**Exclusiones explícitas** — los tests generales NO deben exigir: headings particulares, términos o palabras concretas, artefactos específicos, veredictos concretos, cantidades fijas de skills, identidad fija de una skill, idioma o contenido semántico del cuerpo. El cuerpo no se inspecciona; hoy no existe aserción de cuerpo no vacío y no debe añadirse como invariante genérico.

**Coherencia del payload** (`tests/unit/test_payload_coherence.py`):

- El mapa fuente→espejo se define una sola vez en `tools/sync_payload.py` (`FILE_MAP` + `DIR_MAP`: `framework/marco`→`marco`, `runtime/skills`→`.agents/skills`, `runtime/AGENTS.md`→`AGENTS.md`, `runtime/catalogo/skill-registry.md`→`catalogo/skill-registry.md`, `adapters/codex`→`.codex`).
- El espejo `src/se_agent/_payload/` debe contener **exactamente** la expansión mapeada (sin archivos extra ni faltantes) y ser **byte a byte idéntico** a las fuentes canónicas.
- `tools/sync_payload.py` es el único escritor del espejo y un script de desarrollo: CI/los tests solo verifican, nunca regeneran.

## Hoja de diseño previa a la implementación

Completar esta hoja antes de escribir código; las respuestas provienen del catálogo y del marco, no de la intuición:

```markdown
## Hoja de diseño: <capacidad>

- Id y tipo de capacidad: <snake_case> / <fase|transición|transversal|tarea puntual|control de avance|orquestación general>
- Fichas del catálogo implicadas: <ids y madurez esperada>
- Fuentes del marco: <rutas de framework/marco/** que definen el contrato>
- Disparadores (estado/madurez): <cuándo seleccionar la capacidad>
- Entradas mínimas: <del contrato de dominio>
- Salidas y artefactos: <esperados> + ubicación autoritativa o `ubicación pendiente`
- Transversales en alcance: <cuáles, con qué alcance específico por fase>
- Review y baseline: <review asociada, momento típico, tratamiento de baseline>
- Criterios de cierre: <los del marco, íntegros>
- Cierre y handoff: <qué evalúa la skill; qué decide el humano>
- Límites de autoridad: <qué nunca autoriza la skill>
- Nombre ejecutable: <kebab-case> (directorio + frontmatter + registry)
- Fuentes de estado e hitos: <rutas de `proyecto/estado/**` y `proyecto/hitos/**` que consulta>
- Propuesta de actualización: <campos o filas que podría proponer al padre, precondiciones y evidencia humana requerida>
- Decisiones de persistencia: <qué registros propone actualizar y dónde; continuidad histórica; borradores `ubicación pendiente`>
- Gaps sin resolver: <cobertura pendiente del catálogo, decisiones abiertas>
```

## Flujo de implementación y checklist pre-commit

Flujo secuencial (es una plantilla de mantenedor, no un procedimiento de runtime):

1. **Cruce con el catálogo**: confirmar ficha, tipo, fuentes y binding; completar la hoja de diseño.
2. **Runtime skill**: escribir `runtime/skills/<nombre>/SKILL.md` con la plantilla de secciones.
3. **Registry manual**: añadir/actualizar la fila en `runtime/catalogo/skill-registry.md` a mano (id, trigger, ruta) y el `bindings` en la ficha del catálogo.
4. **Payload sync**: regenerar el espejo con `tools/sync_payload.py` si las rutas tocadas están mapeadas.
5. **Tests**: ejecutar la suite del proyecto:

   ```bash
   .venv/bin/python -BIm pytest -p no:cacheprovider --basetemp=/tmp/se-agent-pytest tests
   ```

6. **Revisión humana de fidelidad**: verificar que la transformación preserva los elementos del contrato y que ninguna decisión semántica quedó oculta.
7. **Estado de implementación**: actualizar la ficha (`mapeada` al declarar el enlace; `verificada` solo tras pruebas de comportamiento).

Checklist pre-commit:

- [ ] La ficha del catálogo existe y su binding refleja la realidad del enlace.
- [ ] La skill preserva todos los elementos del contrato de transformación, incluido el contrato de estado e hitos cuando aplica.
- [ ] Las rutas y estructuras consultadas coinciden con `framework/proyecto/**`, sin tratar la plantilla como evidencia viva.
- [ ] Toda mutación de estado o hito se expresa como propuesta para el padre, con precondiciones y autoridad humana explícitas.
- [ ] El registry fue actualizado a mano y es coherente con `runtime/skills/`.
- [ ] El espejo del payload está sincronizado (o no hay rutas mapeadas tocadas).
- [ ] La suite de tests pasa.
- [ ] Un humano revisó la fidelidad semántica respecto al marco.
- [ ] `estado_implementacion` de la ficha es veraz.

## Cobertura pendiente del catálogo

`datos_y_documentacion` y `lecciones_aprendidas` permanecen como **decisiones de cobertura pendientes** del catálogo: no existen como fichas y ninguna skill puede absorberlas implícitamente. Sus tratamientos provisionales son distintos:

- **`datos_y_documentacion`**: mientras el catálogo no la defina, puede manejarse provisionalmente solo como trazabilidad de evidencia (citar fuente y procedencia, y declarar como vacío lo referenciado que no se encuentre) cuando la fase lo requiera, sin fingir que existe una capacidad dedicada.
- **`lecciones_aprendidas`**: sigue siendo una decisión de cobertura pendiente; no se absorbe implícitamente y sus registros autoritativos específicos de fase solo se tocan cuando el marco o el catálogo lo exigen explícitamente.

## Ejemplo de referencia: F0

`f0-factibilidad` (v3, aprobada) es el patrón de esta plantilla, no un caso aislado:

- Mapea la capacidad `f0_factibilidad` → skill `f0-factibilidad`; ficha con `estado_implementacion: mapeada` y binding declarado.
- Demuestra las once secciones por defecto, el modelo de evidencia (`hechos verificados` / `supuestos` / `vacíos` / `contradicciones`), la política de `ubicación pendiente` para artefactos sin ruta, la persistencia en registros transversales (`riesgos`, `requisitos` a nivel de necesidad preliminar, `decisiones_tecnicas` condicional) y la separación de los tres juicios (recomendación técnica, readiness del dossier frente a la MCR, decisión humana).
- Fuente: [`runtime/skills/f0-factibilidad/SKILL.md`](../../runtime/skills/f0-factibilidad/SKILL.md). No duplica el contrato completo de la fase; lo proyecta desde `marco/fases/fase_0_concepto_y_factibilidad.md`.

## Relacionado

- [`docs/architecture/design-document-review-lifecycle.md`](design-document-review-lifecycle.md) — ciclo de vida de review humana por paquete versionado (`docs-verificacion` → `docs-aprobados`), autoridad particionada y gates de cierre; núcleo `docs-review` implementado con verificación conductual PS5.1 pendiente.
- [`docs/architecture/design-f1-stakeholders-handoff.md`](design-f1-stakeholders-handoff.md) — diseño concreto de las tres capacidades de `F1`: `f1_stakeholders_preliminar`, `f1_stakeholders_formal` y `handoff_presupuesto_a_proyecto` (hojas de diseño completas).
- [`framework/guias/skill-architecture.md`](../../framework/guias/skill-architecture.md) — catálogo canónico de capacidades, routing y bindings.
- [`docs/decisions/skill-artifacts.md`](../decisions/skill-artifacts.md) — decisión canónica de las capas de autoridad y el registry operativo.
- [`docs/decisions/agents-contract.md`](../decisions/agents-contract.md) — decisión canónica del contrato único de `AGENTS.md`.
- [`docs/architecture/orchestrator.md`](orchestrator.md) — capas del orquestador y carga de skills dirigida por estado.
- [`docs/architecture/domain-harness-boundary.md`](domain-harness-boundary.md) — frontera dominio-harness y matriz de responsabilidades.
- [`docs/architecture/memory.md`](memory.md) — autoridad de memoria.
- [`docs/architecture/product.md`](product.md) — arquitectura del producto.
- [`docs/guides/quickstart.md`](../guides/quickstart.md) — flujo mínimo de uso.
- [`runtime/AGENTS.md`](../../runtime/AGENTS.md) — contrato de runtime (instalado como `AGENTS.md`).
- [`framework/marco/README.md`](../../framework/marco/README.md) — índice del marco metodológico.
- [`framework/proyecto/estado/proyecto_actual.md`](../../framework/proyecto/estado/proyecto_actual.md) — plantilla del estado global de una instancia.
- [`framework/proyecto/estado/estado_fases.md`](../../framework/proyecto/estado/estado_fases.md) — plantilla del estado por fase.
- [`framework/proyecto/hitos/hito_aprobacion_trabajo.md`](../../framework/proyecto/hitos/hito_aprobacion_trabajo.md) — plantilla del hito que habilita el handoff desde presupuesto.
