---
document_type: diseno_concreto_capacidades
language: es
version: 1.0
status: propuesto
---
# Diseño concreto: F1 preliminar y handoff de presupuesto a proyecto aprobado

Este documento completa la [hoja de diseño](design-skill-marco.md#hoja-de-diseño-previa-a-la-implementación) para las capacidades del desdoblamiento de `F1`: las dos capacidades de fase — `f1_stakeholders_preliminar` (madurez `preliminar`) y, como frontera futura, `f1_stakeholders_formal` (madurez `formal`) — más la transición **`handoff_presupuesto_a_proyecto`** entre ambas. El handoff no es un tercer modo de `F1`: es la transición entre sus dos capacidades de fase. Es un artefacto de diseño: define contratos, límites, lecturas, salidas propuestas y criterios de aceptación para la implementación posterior de las skills. **No implementa** `runtime/skills/**`, bindings, registry, payload sync ni tests; eso corresponde a cambios futuros.

## Decisión resumida

| Aspecto                      | Decisión                                                                                                                                                                                                                                                                                                                                             |
| ---------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Desdoblamiento de `F1`      | Dos capacidades de fase: `f1_stakeholders_preliminar` (madurez `preliminar`, presupuesto) y `f1_stakeholders_formal` (fase futura; aquí solo frontera e interfaz), más la transición `handoff_presupuesto_a_proyecto` entre ambas. El handoff no es un modo de `F1`: es la transición entre sus dos capacidades de fase.                 |
| Papel de la skill preliminar | Reúne material para cotizar, produce y madura los artefactos de fase en sus rutas canónicas y **evalúa readiness** frente al `hito_aprobacion_trabajo`; emite una propuesta estructurada que transporta la evidencia de la autorización humana. No autoriza nada.                                                                          |
| Papel del handoff            | Se activa **solo ante la decisión aprobatoria humana** y consolida el pase con el resultado canónico: hito `aprobado`, `project_start_authorized: true`, `approval_handoff_status: consolidado`, estado global `aprobado_en_transicion`, `active_phase: F1` con madurez `formal` (selecciona el próximo trabajo enrutado aunque la fila `F1 formal` siga `no_iniciada`), `F1` preliminar ya `cerrada` (cierre por su propia capacidad de fase más la aprobación humana; el handoff no la cierra) y `F1` formal `no_iniciada`. |
| Escritura                    | Las skills **proponen** con evidencia; el humano **autoriza**; el orquestador padre **relee, valida y persiste** como un único cambio coherente (single-writer). Ninguna skill autoriza por sí misma ni escribe en `proyecto/estado/**`, `proyecto/hitos/**` ni en los registros directamente.                                 |
| Artefactos de fase F1        | Los cuatro artefactos obligatorios viven en rutas canónicas bajo `proyecto/fases/f1_stakeholders/`, compartidas y maduras por ambas skills de fase, con frontmatter común y ciclo `doc_approval`. El handoff los **referencia** como insumos heredados; no madura su contenido técnico.                                                   |
| Bloqueo de `F2`             | `F2` permanece `no habilitada` (fila `no_iniciada`, protegida por el gate de paso a `F2`) hasta que `f1_stakeholders_formal` cierre los vacíos heredados y se cumplan los criterios de cierre formal de `F1` (regla de paso a `F2` de `marco/reglas_del_ciclo.md`).                                                                                                                                         |

## Alcance y no metas

**En alcance de este documento:**

- Hoja de diseño completa de `f1_stakeholders_preliminar` y `handoff_presupuesto_a_proyecto`.
- Límite y secuencia del flujo canónico de `F1`, incluida la frontera con `f1_stakeholders_formal`.
- Ubicación canónica, frontmatter común y ciclo de aprobación de los artefactos obligatorios de fase de `F1`, compartidos por ambas capacidades de fase.
- Esquemas de secciones de los futuros `SKILL.md`, criterios de aceptación de implementación y decisiones diferidas.

**Fuera de alcance (no metas):**

- Escribir los `SKILL.md`, el registry operativo, los `bindings` de las fichas o el espejo del payload.
- El diseño completo de `f1_stakeholders_formal` (solo se define su frontera e interfaz).
- Cambiar `framework/proyecto/**`, `framework/marco/**` o el catálogo de capacidades: este documento **consume** su semántica, no la redefine.
- Definir la política de la review `Stakeholder Requirements Review` más allá de lo que el catálogo de reviews ya declara.

## Límite y secuencia del flujo de `F1`

Secuencia canónica (fuente: [`design-skill-marco.md`](design-skill-marco.md#transición-de-presupuesto-a-proyecto-aprobado) y [`marco/reglas_del_ciclo.md`](../../framework/marco/reglas_del_ciclo.md)):

```text
F1 preliminar ──► readiness frente al hito ──► DECISIÓN HUMANA ──► cierre de F1 preliminar ──► handoff ──► padre valida y persiste ──► F1 formal ──► cierre F1 formal ──► F2
 (presupuesto)     (no aprueba)                 (aprobación)       (capacidad de fase        (consolida;      (single-writer)          (cierra vacíos)   (regla de
                                                                                    + aprobación humana)      no cierra fases)                                            paso a F2)
```

1. **`f1_stakeholders_preliminar`** reúne material para cotizar, produce los artefactos de fase y evalúa readiness frente al `hito_aprobacion_trabajo`; no aprueba el trabajo. Presupone `F0` ya cerrada (con su aprobación humana) y `F1 preliminar` ya abierta y persistida; no activa fases ni propone cambios sobre `F0`.
2. **Un humano** emite la decisión de aprobación y autoriza —o no— el inicio formal. Sin esta decisión, el flujo no avanza.
3. **El cierre de `F1 preliminar`** corresponde a su propia capacidad de fase (preliminar) más la aprobación humana: la fase queda `cerrada` antes del handoff. El handoff no cierra fases; **consume** ese estado ya cerrado y no cambia `F0`.
4. **`handoff_presupuesto_a_proyecto`** se activa ante la decisión aprobatoria con `F1 preliminar` ya `cerrada`; valida el hito y consolida: insumos heredados, vacíos antes de `F2` y registros transversales que continúan.
5. **El orquestador padre** relee las fuentes, valida las reglas del ciclo y persiste de forma consistente el hito completo, el estado global `aprobado_en_transicion`, `active_phase: F1` con madurez `formal` (que selecciona el próximo trabajo enrutado aunque la fila `F1 formal` siga `no_iniciada`) y la fila `F1 formal` en `no_iniciada`. Si falta la decisión aprobatoria, `project_start_authorized` no es verdadero, el hito está incompleto, `F1 preliminar` no está `cerrada` o las fuentes de estado se contradicen, la transición queda **bloqueada** y la skill informa el conflicto sin inferir ni fabricar valores (fail-closed).
6. **`f1_stakeholders_formal`** completa los vacíos heredados. `F2` permanece `no habilitada` (fila `no_iniciada`, protegida por el gate de paso a `F2`) hasta que se cumplan los criterios de cierre formal de `F1`; su estado de fase no adopta el valor `bloqueada`.

Regla de separación de juicios (válida para ambas capacidades): recomendación técnica, readiness y decisión humana nunca se mezclan. Una skill nunca autoriza por sí misma: emite una propuesta estructurada que transporta la evidencia de la autorización humana cuando esta existe; el humano autoriza; el padre persiste.

## Artefactos de fase de `F1`: rutas canónicas, frontmatter y ciclo de aprobación

Las dos capacidades de fase de `F1` (`f1_stakeholders_preliminar` y `f1_stakeholders_formal`) comparten y maduran los mismos cuatro artefactos obligatorios en rutas canónicas bajo `proyecto/fases/f1_stakeholders/`:

| Artefacto obligatorio de F1                 | Ruta canónica                                                               | `document_type`                       |
| ------------------------------------------- | ---------------------------------------------------------------------------- | --------------------------------------- |
| Stakeholder requirements document           | `proyecto/fases/f1_stakeholders/requisitos_stakeholders.md`                | `stakeholder_requirements`            |
| Casos de uso o escenarios operativos        | `proyecto/fases/f1_stakeholders/escenarios_operativos.md`                  | `operational_scenarios`               |
| Restricciones externas                      | `proyecto/fases/f1_stakeholders/restricciones_externas.md`                 | `external_constraints`                |
| Matriz necesidad ↔ stakeholder requirement | `proyecto/fases/f1_stakeholders/matriz_necesidad_requisito_stakeholder.md` | `need_stakeholder_requirement_matrix` |

La skill preliminar los crea y los entrega en madurez `preliminar`; la skill formal los madura a `formal`. El handoff de aprobación los **referencia** como insumos heredados y no madura su contenido técnico: eso corresponde exclusivamente a las capacidades de fase.

### Frontmatter común de los artefactos de fase de `F1`

Cada uno de los cuatro artefactos lleva el mismo frontmatter:

| Campo | Valor / semántica |
| ------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `document_type` | Tipo exacto del artefacto, según la ruta canónica: `stakeholder_requirements` (`requisitos_stakeholders.md`), `operational_scenarios` (`escenarios_operativos.md`), `external_constraints` (`restricciones_externas.md`), `need_stakeholder_requirement_matrix` (`matriz_necesidad_requisito_stakeholder.md`). |
| `language: es` | Idioma del contenido. |
| `active_maturity` | Madurez activa del artefacto: `preliminar` o `formal`. |
| `last_updated` | Fecha de la última persistencia. |
| `doc_approval` | Estado de aprobación del documento: `pendiente`, `aprobado` o `rechazado`. |
| `responsible: "<identidad>"` | Custodio humano actual y responsable de cuenta del artefacto. No es necesariamente el aprobador. |

`responsible` identifica al custodio humano vigente: la persona accountable de que el artefacto esté actualizado y coherente. La identidad de quien aprueba se preserva por separado, en una **tabla de historial de aprobación en el cuerpo** del artefacto (aprobador, fecha, madurez y decisión), nunca en el frontmatter.

### Ciclo de aprobación (`doc_approval`)

Valores permitidos: `pendiente`, `aprobado`, `rechazado`.

1. **Trabajo preliminar:** el artefacto trabaja con `doc_approval: pendiente`.
2. **Cierre preliminar:** el humano aprueba y el `doc_approval` vigente pasa a `aprobado`.
3. **Trabajo formal:** al iniciar el trabajo formal, el `doc_approval` vigente se **resetea a `pendiente`**; el historial de aprobación preliminar se preserva íntegro en la tabla del cuerpo.
4. **Cierre formal:** el humano aprueba y el `doc_approval` vuelve a `aprobado`.

---

## Hoja de diseño: `f1_stakeholders_preliminar`

- **Id y tipo de capacidad:** `f1_stakeholders_preliminar` / `fase`.
- **Fichas del catálogo implicadas:** `f1_stakeholders_preliminar` (fase, `F1`, madurez esperada `preliminar`, [`framework/guias/skill-architecture.md`](../../framework/guias/skill-architecture.md)). Transversales en alcance con ficha: `riesgos_y_oportunidades`, `interfaces`; la trazabilidad aplica aquí a nivel de matriz necesidad ↔ stakeholder requirement; `datos_y_documentacion` no tiene ficha (cobertura pendiente, tratamiento provisional como trazabilidad de evidencia).
- **Fuentes del marco:**

  - `marco/fases/fase_1_requerimientos_stakeholders.md` — contrato completo de la fase (instalado desde `framework/marco/fases/…`).
  - `marco/reglas_del_ciclo.md` — regla especial del preproyecto de presupuesto y regla de paso a `F2`.
  - `marco/reviews/catalogo_reviews.md` — `Stakeholder Requirements Review`.
- **Disparadores (estado/madurez):** estado global `preproyecto_presupuesto` con `F1 preliminar` activa. Precondiciones estructurales: `F0` ya cerrada (con su aprobación humana, gestionada por la capacidad de fase `F0` correspondiente) y `F1 preliminar` ya abierta y persistida en el estado. Si la fila `F1 preliminar` figura `no_iniciada` o `F0` no está cerrada, esta capacidad no ejecuta trabajo de `F1`: informa el estado observado y espera la resolución humana; nunca propone activar `F1` ni cerrar `F0`. Si el estado global ya es `aprobado_en_transicion`, esta capacidad no aplica (corresponde el handoff o `F1 formal`).
- **Entradas mínimas** (del contrato de la fase; entradas mínimas, no condiciones de arranque bloqueantes): salida de `F0`; minutas con cliente; contexto de uso; restricciones de negocio o regulatorias. *Los insumos heredados del presupuesto solo aplican al modo formal.* La ausencia de alguna se registra como vacío explícito y se produce con lo disponible.
- **Salidas y artefactos:** necesidades preliminares, escenarios de uso, restricciones externas, base para cotización. Los cuatro artefactos obligatorios del marco se crean y maduran en sus **rutas canónicas** bajo `proyecto/fases/f1_stakeholders/` (ver [Artefactos de fase de `F1`](#artefactos-de-fase-de-f1-rutas-canónicas-frontmatter-y-ciclo-de-aprobación)), con el frontmatter común y el ciclo `doc_approval`; trabajan en `pendiente` durante esta capacidad.
- **Transversales en alcance** (con registro autoritativo y límite específico en esta fase):

  - **`requisitos`** → `proyecto/registros/requisitos.md`: entradas a nivel de necesidad y stakeholder requirement preliminar (el registro contempla explícitamente el uso en presupuesto); nunca requisitos de sistema ni métodos de verificación (`F2`).
  - **`interfaces`** → `proyecto/registros/interfaces.md`: solo interfaces externas relevantes (el registro admite una lista preliminar externa aunque las internas no estén definidas).
  - **`riesgos`** → `proyecto/registros/riesgos.md`: siempre; riesgos y supuestos sensibles que luego deben heredarse al proyecto aprobado.
  - **`datos_y_documentacion`** → sin ficha ni registro propio (cobertura pendiente del catálogo). Tratamiento provisional: trazabilidad de evidencia — citar fuente y procedencia de toda evidencia usada, y declarar como vacío lo referenciado que no se encuentre. No se absorbe como capacidad implícita.
- **Review y baseline:** review asociada **Stakeholder Requirements Review** — confirmar que las necesidades externas fueron capturadas con suficiente claridad; momento típico: `F1` preliminar o `F1` formal según madurez requerida. Baseline: **no aplica baseline formal de sistema** en `F1`. La skill evalúa únicamente la readiness del material frente a la review y frente al hito de aprobación; no convoca, no conduce ni aprueba.
- **Criterios de cierre** (los del marco, íntegros, como verificación de readiness):

  - stakeholders principales identificados;
  - necesidades y restricciones sin contradicciones críticas;
  - criterios de aceptación de alto nivel suficientemente claros;
  - si la madurez es `formal`, existe material suficiente para abrir `F2` *(cláusula que en modo preliminar no aplica; se verifica como vacío declarado, no como criterio exigido)*.

  El gate siguiente en madurez `preliminar` es el **`hito_aprobacion_trabajo`**: la skill evalúa si hay material suficiente para que un humano complete el hito y decida.
- **Cierre y handoff:** la skill evalúa readiness del paquete de cotización frente al hito y declara qué vacíos bloquearían la decisión humana. El humano decide la aprobación; el cierre de la fase `F1 preliminar` corresponde a esta propia capacidad de fase más la aprobación humana; el handoff es una capacidad separada que **consume** ese estado cerrado (la transición entre las dos capacidades de fase de `F1`).
- **Límites de autoridad:** nunca autoriza el cierre de fase, la aprobación del trabajo, el hito de aprobación, la transición a `F1 formal` ni la apertura de `F2`. Nunca propone activar `F1`, cerrar `F0` ni cambiar el estado de `F0`: el cierre de `F0` pertenece exclusivamente a la capacidad de fase `F0` y a su aprobación humana. No genera requisitos de sistema, arquitectura ni diseño detallado. No declara baseline. Trabaja en madurez `preliminar` únicamente.
- **Nombre ejecutable:** `f1-stakeholders-preliminar` (directorio + frontmatter `name` + `id` en el registry; se declara en un cambio de implementación posterior).
- **Fuentes de estado e hitos que consulta:** `proyecto/estado/proyecto_actual.md`, `proyecto/estado/estado_fases.md` y `proyecto/hitos/hito_aprobacion_trabajo.md` — **solo lectura**, para determinar estado, madurez y evaluar readiness frente al hito. En el repo de producto, la plantilla común vive en `framework/proyecto/**`; en runtime se lee la instancia `proyecto/**`.
- **Propuesta de actualización:** propone valor anterior → valor propuesto sobre `proyecto/registros/requisitos.md`, `proyecto/registros/riesgos.md`, `proyecto/registros/interfaces.md` y los cuatro artefactos de fase en sus rutas canónicas, con justificación, procedencia, vacíos y contradicciones. El informe de readiness frente al hito es una observación, no una propuesta de aprobación. La skill produce el bloque para el padre y **no escribe** en `proyecto/**`. No propone aprobar ni completar `proyecto/hitos/hito_aprobacion_trabajo.md`: eso corresponde a la decisión humana y al handoff.
- **Decisiones de persistencia:** madurar los registros transversales existentes en lugar de reiniciarlos, preservando continuidad histórica y evidencia ya registrada. Los cuatro artefactos obligatorios de fase se crean y maduran en sus rutas canónicas compartidas con `f1_stakeholders_formal`, con frontmatter común y `doc_approval: pendiente` durante el trabajo preliminar; sin fabricar contenido para llenar vacíos.
- **Gaps sin resolver:** cobertura de `datos_y_documentacion`.

### Esquema de secciones del `SKILL.md` (plantilla de fase, once secciones)

| #  | Sección                           | Contenido clave en esta skill                                                                                                                                                                                                                                                                                                                |
| -- | ---------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1  | Objetivo operativo                 | Pregunta central «¿Qué necesitan los stakeholders?», en modo preliminar: material para cotizar con fundamento; el humano decide la aprobación.                                                                                                                                                                                          |
| 2  | Rol y límites de fase             | Proyección de `f1_stakeholders_preliminar`; madurez `preliminar` única; el modo formal no pertenece a esta skill; presupone `F0` cerrada y `F1` preliminar abierta y persistida; nada de `F2+`.                                                                                                                                   |
| 3  | Entradas mínimas                  | Salida de `F0`, minutas con cliente, contexto de uso, restricciones de negocio/regulatorias; vacío declarado ante ausencia; modelo de evidencia de cuatro clases.                                                                                                                                                                          |
| 4  | Capacidades operacionales          | Actividades guía del marco operacionalizadas y seleccionables según estado: identificar stakeholders relevantes, relevar necesidades y expectativas, formalizar escenarios de uso, consolidar restricciones externas, detectar criterios de aceptación de alto nivel, validar consistencia con partes interesadas. Sin orden obligatorio. |
| 5  | Salidas esperadas                  | Necesidades preliminares, escenarios, restricciones externas, base para cotización; forma de entrega: madurar registro autoritativo o crear/madurar artefacto en su ruta canónica.                                                                                                                                                         |
| 6  | Artefactos obligatorios            | Los cuatro del marco en sus rutas canónicas bajo `proyecto/fases/f1_stakeholders/`, compartidas con `f1_stakeholders_formal`; frontmatter común y ciclo `doc_approval` (`pendiente` durante el trabajo preliminar, `aprobado` al cierre preliminar); `responsible` como custodio humano.                                        |
| 7  | Review y baseline                  | `Stakeholder Requirements Review` (momento típico según madurez); sin baseline formal de sistema; solo readiness.                                                                                                                                                                                                                        |
| 8  | Procesos y registros transversales | `requisitos` (nivel necesidad/stakeholder requirement preliminar), `interfaces` (solo externas relevantes), `riesgos` (siempre), `datos_y_documentacion` como trazabilidad de evidencia provisional.                                                                                                                                 |
| 9  | Criterios de cierre                | Los del marco íntegros, con la cláusula de `F2` marcada como no aplicable en preliminar; verificación de readiness, no autorización.                                                                                                                                                                                                    |
| 10 | Cierre, recomendación y handoff   | Tres juicios separados; readiness frente al `hito_aprobacion_trabajo`; vacíos que bloquean la decisión humana; nunca autoaprobación.                                                                                                                                                                                                     |
| 11 | Referencias                        | `marco/fases/fase_1_requerimientos_stakeholders.md`, `marco/reglas_del_ciclo.md`, `marco/reviews/catalogo_reviews.md`, los tres registros, los cuatro artefactos canónicos y los tres archivos de estado/hito — rutas instaladas.                                                                                                    |

Frontmatter: `name: f1-stakeholders-preliminar`; `description` orientada al disparador (estado `preproyecto_presupuesto`, F1 preliminar, cotización, necesidades preliminares, escenarios, restricciones externas, hito de aprobación), como metadata de selección.

### Criterios de aceptación para la implementación

- [ ] La skill se selecciona ante estado global `preproyecto_presupuesto` con `F1 preliminar` activa, `F0` ya cerrada y la apertura de `F1 preliminar` ya persistida. Si la fila `F1 preliminar` figura `no_iniciada` o `F0` no está cerrada, no ejecuta trabajo de `F1` y no propone activar `F1` ni cerrar `F0`: informa y espera resolución humana. Se abstiene ante `aprobado_en_transicion` o `proyecto_formal`.
- [ ] Toda salida distingue explícitamente `hechos verificados`, `supuestos`, `vacíos` y `contradicciones`.
- [ ] Los cuatro artefactos obligatorios de fase se crean y maduran en sus rutas canónicas bajo `proyecto/fases/f1_stakeholders/`, con el frontmatter común (`document_type`, `language: es`, `active_maturity`, `last_updated`, `doc_approval`, `responsible`) y el historial de aprobación en el cuerpo; trabaja con `doc_approval: pendiente` y registra al aprobador en la tabla del cuerpo al cierre preliminar.
- [ ] Solo propone actualizaciones sobre los tres registros en alcance y los cuatro artefactos canónicos, con valor anterior → valor propuesto y procedencia; no escribe directamente en ningún archivo de `proyecto/**` fuera de esas rutas y nunca toca el estado de `F0`.
- [ ] Evalúa readiness frente al `hito_aprobacion_trabajo` como observación y declara vacíos bloqueantes; no propone cambiar el hito ni el estado global.
- [ ] Separa recomendación técnica, readiness y decisión humana; su salida transporta evidencia de la autorización humana cuando existe, pero nunca autoriza por sí misma.
- [ ] Ante evidencia requerida ausente o contradictoria para el cierre o la review, falla cerrado y solicita restauración; la evidencia no crítica faltante produce artefactos con vacíos declarados.

---

## Hoja de diseño: `handoff_presupuesto_a_proyecto`

- **Id y tipo de capacidad:** `handoff_presupuesto_a_proyecto` / `transición`. No es un modo de `F1`: es la transición entre sus dos capacidades de fase (preliminar → formal).
- **Fichas del catálogo implicadas:** `handoff_presupuesto_a_proyecto` (transición, fase objetivo `F1`, madurez esperada `formal`); hereda material de `f0_factibilidad` y `f1_stakeholders_preliminar` como insumos, no como capacidades a re-ejecutar.
- **Fuentes del marco:**

  - `marco/reglas_del_ciclo.md` — regla especial: ante aprobación no se reinicia el proyecto; se consolida un hito formal, se completa `F1` formal, luego `F2`–`F8`.
  - `marco/fases/fase_1_requerimientos_stakeholders.md` — definición de los vacíos que el modo formal debe cerrar antes de `F2`.
  - Plantillas de estado: `framework/proyecto/hitos/hito_aprobacion_trabajo.md`, `framework/proyecto/estado/proyecto_actual.md`, `framework/proyecto/estado/estado_fases.md` (forma común; en runtime se lee la instancia).
- **Disparadores y precondiciones:** se activa **inmediatamente después de la decisión humana aprobatoria** del trabajo, una vez que `F1 preliminar` ya quedó `cerrada` por su propia capacidad de fase más la aprobación humana. Precondiciones que la skill verifica antes de operar (fail-closed):

  - existe una decisión aprobatoria con responsable y fuente de aprobación;
  - el hito `proyecto/hitos/hito_aprobacion_trabajo.md` está `pendiente` de consolidar y `project_start_authorized` es `false`;
  - el estado global es `preproyecto_presupuesto`, la fila `F1 preliminar` ya está `cerrada` (cierre por su propia capacidad de fase más la aprobación humana; el handoff no cierra fases ni cambia `F0`) y las fuentes de estado (`proyecto_actual.md`, `estado_fases.md`, hito) son mutuamente consistentes.

  Si falta la decisión aprobatoria, el hito está incompleto sin base para completarlo, `F1 preliminar` no está `cerrada` o las fuentes se contradicen, la transición queda **bloqueada**: la skill informa el conflicto sin inferir ni fabricar valores. Readiness nunca equivale a autorización.
- **Resultado canónico del handoff:** el resultado que la skill propone y el padre persiste como un único cambio coherente es exactamente:

  - `proyecto/hitos/hito_aprobacion_trabajo.md`: `approval_status: aprobado` y `project_start_authorized: true`, con cuerpo consolidado;
  - `proyecto/estado/proyecto_actual.md`: `project_status: aprobado_en_transicion`, `active_phase: F1`, `active_maturity: formal` (selecciona el próximo trabajo enrutado aunque la fila `F1 formal` siga `no_iniciada`), `approval_handoff_status: consolidado`;
  - `proyecto/estado/estado_fases.md`: fila `F1 preliminar` ya `cerrada` (precondición consumida, sin cambio); fila `F1 formal` `no_iniciada` (sin cambio; la activa su primer trabajo formal).

  **Comportamiento idempotente:** si ese resultado completo ya está reflejado de forma coherente en las tres fuentes, la skill informa que el handoff ya fue consolidado y no propone cambios. Si solo una parte de las fuentes refleja ese resultado, bloquea por estado parcial sin inferir valores.
- **Fuentes autoritativas que lee (conjunto de lectura):**

  - `proyecto/hitos/hito_aprobacion_trabajo.md` — hito a validar y consolidar;
  - `proyecto/estado/proyecto_actual.md` y `proyecto/estado/estado_fases.md` — estado global y por fase;
  - salidas heredadas de `F0` y `F1 preliminar`: los registros transversales (`proyecto/registros/requisitos.md`, `riesgos.md`, `interfaces.md`, `decisiones_tecnicas.md`, `configuracion.md`, `vv.md`) y los cuatro artefactos de fase de `F1` en sus rutas canónicas bajo `proyecto/fases/f1_stakeholders/` — **referenciados, sin madurar su contenido técnico**;
  - `marco/reglas_del_ciclo.md` y `marco/fases/fase_1_requerimientos_stakeholders.md` como contratos de dominio.

  Nunca usa `framework/proyecto/**` como evidencia de la instancia.
- **Capacidades operacionales:** validar el hito frente a la decisión humana; inventariar los insumos heredados (problema, stakeholders, necesidades preliminares, restricciones externas preliminares, CONOPS preliminar, estimación ROM, riesgos iniciales); detectar los vacíos que deben cerrarse antes de `F2` (necesidades ambiguas, escenarios operativos faltantes, restricciones por confirmar, criterios de aceptación faltantes, supuestos de presupuesto a validar); preservar procedencia y continuidad de los registros. No rehace artefactos heredados ni aplica una secuencia fija sin mirar estado.
- **Salidas y artefactos:**

  - **hito de aprobación consolidado** — contenido completo de las secciones del hito (decisión, alcance aprobado, insumos heredados, vacíos antes de `F2`, registros que continúan); ubicación autoritativa: `proyecto/hitos/hito_aprobacion_trabajo.md` (la skill propone; el padre escribe);
  - **lista de insumos heredados** — vive dentro del hito, trazando cada insumo a su fuente, incluidos los cuatro artefactos de fase de `F1` por su ruta canónica;
  - **lista de vacíos a cerrar antes de `F2`** — vive dentro del hito y es la interfaz de entrada de `f1_stakeholders_formal`.
- **Registros que continúan** (secciones del hito; no se abren registros paralelos ni se pierde historia): Requisitos, Riesgos, Configuración (`proyecto/registros/configuracion.md`), Interfaces, V&V, Decisiones técnicas. `lecciones_aprendidas` no está en la lista del hito y es una cobertura pendiente del catálogo: no se toca.
- **Salida hacia el padre — propuesta de actualización estructurada:** un único bloque coherente que resuelve el resultado canónico:

  | Fuente | Cambio propuesto (anterior → propuesto) | Precondición / evidencia humana |
  | --------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------ |
  | `proyecto/hitos/hito_aprobacion_trabajo.md` | `approval_status: pendiente → aprobado`; `project_start_authorized: false → true`; `decision_date` → fecha de la decisión; estado/resultado del cuerpo `pendiente → aprobado`; secciones Decisión, Alcance aprobado, Insumos heredados, Vacíos antes de `F2` y Registros que continúan completadas con trazabilidad a fuente | Decisión aprobatoria explícita y humana con responsable y fuente |
  | `proyecto/estado/proyecto_actual.md` | `project_status: preproyecto_presupuesto → aprobado_en_transicion`; `active_phase: F1` (sin cambio; con `active_maturity: formal` selecciona el próximo trabajo enrutado aunque la fila `F1 formal` siga `no_iniciada`); `active_maturity: preliminar → formal`; `approval_handoff_status: pendiente → consolidado`; `last_updated` → fecha de la persistencia | Hito completo; consistencia con `estado_fases.md` |
  | `proyecto/estado/estado_fases.md` | Fila `F1 preliminar`: sin cambio, ya `cerrada` antes del handoff (cierre por su propia capacidad de fase más la aprobación humana; el handoff la verifica y la consume); fila `F1 formal`: sin cambio, `no_iniciada` (el trabajo formal arranca después del handoff); `F2` sigue sin habilitarse hasta cerrar `F1` formal | Hito completo; `F1 preliminar` cerrada verificada; regla de paso a `F2` |

  La propuesta incluye: fuente y estado observado, precondiciones verificadas, justificación y procedencia de cada campo, vacíos o contradicciones que impidan persistir, y los artefactos y registros que deben conservar continuidad. No es una orden ni una autorización: el padre relee las fuentes, comprueba que no cambiaron, valida las reglas del ciclo y persiste el conjunto como **un único cambio coherente** sin estados parciales.

- **Criterios de transición:** el hito debe quedar completo antes de considerar que el proyecto está en `aprobado_en_transicion`; el estado global resultante habilita solo la consolidación del handoff y el arranque de `F1 formal` (que inicia en `no_iniciada` y cuyo trabajo la habilita); `F2` permanece `no habilitada` (gate de paso a `F2`). La skill declara bloqueos pendientes; no los resuelve.
- **Cierre y autoridad:** separación estricta entre evaluación técnica (consistencia de hito y estado), readiness (hito completo y coherente) y autorización (la decisión humana ya emitida habilita la transición; la skill nunca la otorga ni declara completada una transición incoherente). La propuesta de la skill transporta la evidencia de esa autorización humana; el padre la valida y persiste.
- **Límites de autoridad:** nunca infiere una aprobación, ni trata readiness como autorización, ni ejecuta trabajo propio de `F1` preliminar o `F1 formal`, ni cierra `F0` ni `F1 preliminar` (el cierre de `F1 preliminar` pertenece a su propia capacidad de fase más la aprobación humana; el handoff solo lo verifica y lo consume), ni madura el contenido técnico de los artefactos de fase de `F1` (solo los referencia), ni escribe directamente en estado, hitos o registros, ni reinicia el proyecto ni los registros.
- **Nombre ejecutable:** `handoff-presupuesto-a-proyecto` (directorio + frontmatter `name` + `id` en el registry; se declara en un cambio posterior).
- **Fuentes de estado e hitos:** `proyecto/hitos/hito_aprobacion_trabajo.md`, `proyecto/estado/proyecto_actual.md`, `proyecto/estado/estado_fases.md` — lectura directa; escritura solo como propuesta estructurada al padre.
- **Decisiones de persistencia:** todo cambio de estado global, estado de fase e hito se propone como un único cambio coherente; los seis registros que continúan se referencian con su estado y vacíos, sin abrir copias paralelas; los cuatro artefactos de fase de `F1` se referencian por su ruta canónica, sin madurar su contenido técnico ni moverlos.

### Esquema de secciones del `SKILL.md` (plantilla de transición, ocho secciones)

| # | Sección                             | Contenido clave en esta skill                                                                                                                                                                                                                                                                                                                                                                |
| - | ------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1 | Objetivo y alcance de la transición | Origen `preproyecto_presupuesto`, destino `aprobado_en_transicion`; transición entre las dos capacidades de fase de `F1`; consolidación del hito, insumos heredados y vacíos; habilitada por la decisión humana aprobatoria.                                                                                                                                                        |
| 2 | Disparador y precondiciones          | Decisión aprobatoria con responsable y fuente; `F1 preliminar` ya `cerrada` (por su propia capacidad de fase más la aprobación humana); hito `pendiente`; consistencia mínima de estado; resultado canónico definido; idempotencia cuando el resultado completo ya es coherente; fail-closed ante estado parcial o evidencia ausente o contradictoria.                                                                                                                            |
| 3 | Fuentes autoritativas                | Hitos y estado de la instancia, salidas heredadas de `F0` y `F1 preliminar` (incluidos los cuatro artefactos canónicos, solo como referencia), registros afectados; nunca la plantilla como evidencia.                                                                                                                                                                                   |
| 4 | Capacidades operacionales            | Validar el hito, inventariar insumos, detectar vacíos antes de `F2`, preservar procedencia y continuidad.                                                                                                                                                                                                                                                                                  |
| 5 | Registros que continúan             | Los seis del hito (Requisitos, Riesgos, Configuración, Interfaces, V&V, Decisiones técnicas), su estado y los vacíos que pasan al estado siguiente.                                                                                                                                                                                                                                       |
| 6 | Salidas y propuesta de estado        | Handoff consolidado + bloque estructurado que resuelve el resultado canónico (`approval_status: aprobado`, `project_start_authorized: true`, `approval_handoff_status: consolidado`, `project_status: aprobado_en_transicion`, `active_phase: F1`, `active_maturity: formal`, fila `F1 preliminar` ya `cerrada` consumida sin cambio, fila `F1 formal` `no_iniciada`) para que el padre valide e integre. |
| 7 | Cierre y autoridad                   | Criterios de transición, bloqueos pendientes, separación de los tres juicios; nunca autoaprobar una transición incoherente.                                                                                                                                                                                                                                                               |
| 8 | Referencias                          | `marco/reglas_del_ciclo.md`, `marco/fases/fase_1_requerimientos_stakeholders.md`, ficha del catálogo, rutas instaladas de la instancia, rutas canónicas de los artefactos de `F1`.                                                                                                                                                                                                   |

Frontmatter: `name: handoff-presupuesto-a-proyecto`; `description` orientada al disparador (decisión de aprobación del trabajo, `project_start_authorized`, consolidación del hito de aprobación, insumos heredados de presupuesto, vacíos antes de `F2`), como metadata de selección.

### Criterios de aceptación para la implementación

- [ ] La skill se activa solo ante una decisión humana aprobatoria verificable y con `F1 preliminar` ya `cerrada` (por su propia capacidad de fase más la aprobación humana); no cierra ni modifica `F0` ni `F1 preliminar`, solo verifica y consume ese cierre. Ante ausencia de aprobación, hito incompleto sin base, `F1 preliminar` no `cerrada` o fuentes contradictorias, queda bloqueada sin inferir valores. Ante el resultado canónico completo ya coherente en las tres fuentes, responde sin cambios de forma idempotente; si solo una parte lo refleja, bloquea por estado parcial.
- [ ] Produce **un único bloque coherente** de propuesta que cubre hito, estado global y estado de fase y resuelve el resultado canónico exacto: `approval_status: aprobado`, `project_start_authorized: true`, `approval_handoff_status: consolidado`, `project_status: aprobado_en_transicion`, `active_phase: F1`, `active_maturity: formal`, fila `F1 preliminar` ya `cerrada` (sin cambio, consumida como precondición) y fila `F1 formal` `no_iniciada`, con valor anterior → valor propuesto, justificación y procedencia por campo.
- [ ] No escribe directamente en `proyecto/estado/**`, `proyecto/hitos/**` ni `proyecto/registros/**`; el padre relee, valida y persiste.
- [ ] Referencia los cuatro artefactos de fase de `F1` por su ruta canónica bajo `proyecto/fases/f1_stakeholders/` como insumos heredados, sin madurar su contenido técnico.
- [ ] Los insumos heredados y los vacíos antes de `F2` quedan trazados a su fuente; los registros que continúan se preservan sin copias paralelas ni reinicio del proyecto.
- [ ] No ejecuta trabajo de `F1 preliminar` ni de `F1 formal`; no cierra ni cambia `F0` ni `F1 preliminar`; `F2` no se propone como habilitada.
- [ ] Toda salida conserva las cuatro clases de evidencia; las contradicciones quedan visibles para resolución humana.

---

## Frontera e interfaz de `f1_stakeholders_formal`

`f1_stakeholders_formal` (fase, `F1`, madurez `formal`) es una **capacidad futura**: aquí solo se fija su frontera, no su diseño.

- **Frontera:** opera después del handoff (estado `aprobado_en_transicion`, y luego `proyecto_formal`); no re-ejecuta la transición, no reabre el hito ni rehace el trabajo preliminar. Arranca con la fila `F1` formal en `no_iniciada`, tal como la dejó el handoff.
- **Artefactos:** madura los mismos cuatro artefactos de fase en sus rutas canónicas bajo `proyecto/fases/f1_stakeholders/`. Al iniciar el trabajo formal, resetea el `doc_approval` vigente de cada artefacto a `pendiente`, preservando en el cuerpo el historial de aprobación preliminar; al cierre formal, el humano aprueba y el `doc_approval` pasa a `aprobado`.
- **Interfaz de entrada:** la lista de vacíos antes de `F2` consolidada en `proyecto/hitos/hito_aprobacion_trabajo.md`, más los insumos heredados; completa y limpia esos vacíos, cierra contradicciones entre stakeholders, formaliza restricciones y criterios de aceptación de alto nivel.
- **Interfaz de salida:** base apta para abrir `F2`. El gate de cierre es la regla de paso a `F2` de `marco/reglas_del_ciclo.md`: no se abre `F2` si faltan stakeholders críticos identificados, restricciones externas consolidadas, escenarios de uso relevantes o criterios de aceptación de alto nivel suficientemente claros.
- **Fuentes autoritativas según el catálogo:** `marco/fases/fase_1_requerimientos_stakeholders.md`, `proyecto/hitos/hito_aprobacion_trabajo.md`, `proyecto/registros/requisitos.md`, `proyecto/registros/interfaces.md`, `proyecto/registros/riesgos.md`.

## Decisiones diferidas y gaps

| Tema | Estado | Nota |
| ---------------------------------------------------------------- | -------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Diseño completo de `f1_stakeholders_formal` | Diferido | Capa de fase futura; solo frontera e interfaz definidas aquí. |
| Cobertura de `datos_y_documentacion` y `lecciones_aprendidas` | Abierta | Decisiones de cobertura pendientes del catálogo; tratamientos provisionales según `design-skill-marco.md`. |
| Implementación ejecutable | Diferido | `runtime/skills/**`, bindings, registry, payload sync y tests se abordan en cambios posteriores siguiendo el flujo de implementación de `design-skill-marco.md`. |
