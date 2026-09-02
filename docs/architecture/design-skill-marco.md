---
document_type: arquitectura_plantilla_skills
language: es
version: 1.0
status: canonico
---
# Plantilla canónica para diseñar skills operativas desde el marco

## Regla adoptada

> **Cada skill operativa incorpora íntegramente el contrato de su capacidad en `framework/marco`, lo operacionaliza y compone las capacidades transversales y de tarea puntual afectadas, sin exigir un orden fijo de ejecución.**

Este documento es la **plantilla duradera** para diseñar toda skill operativa futura a partir de `framework/marco`. Define el modelo de capas, el contrato de transformación marco→skill, el cruce con el catálogo de capacidades, la estructura de skill, las reglas operacionales, la política de tests y el flujo de implementación y revisión. F0 no es una excepción: es el primer caso de una transformación sistemática de todo el marco en capacidades ejecutables.

## Quick path

1. Identificar la capacidad en el [catálogo](../../framework/guias/skill-architecture.md) y su tipo.
2. Completar la [hoja de diseño](#hoja-de-diseño-previa-a-la-implementación).
3. Escribir la skill con la [plantilla de secciones](#plantilla-de-skill-de-fase) y sus contratos.
4. Seguir el [flujo de implementación](#flujo-de-implementación-y-checklist-pre-commit).
5. Validar con tests generales y una revisión humana de fidelidad semántica.

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

**Artefactos de inventario que NO son capas de autoridad:**

- **Registry operativo** (`runtime/catalogo/skill-registry.md`, instalado como `catalogo/skill-registry.md`): inventario **manual** de skills disponibles. CI y tests verifican su coherencia bidireccional con `runtime/skills/` y nunca lo generan ni modifican. No duplica el routing ni las guardas.
- **Índice técnico del harness** (`.atl/skill-registry.md`): índice **generado**, exclusivo del harness de desarrollo, de alcance técnico. No se empaqueta, no se instala y no debe fusionarse con el catálogo.

Regla: ninguna capa inferior (skill, subagente, índice, adaptador) es autoridad sobre el significado del dominio. El marco es fuente del dominio conceptual; el catálogo, del significado y routing; el registry, de la disponibilidad.

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
| Tarea puntual | `redaccion_de_artefacto`, `preparacion_de_review` | Producir o revisar un artefacto concreto. |

Reglas de mapeo:

- **Una fase puede mapear a varias capacidades.** `F1` se divide en `f1_stakeholders_preliminar` (fase, madurez `preliminar`), `handoff_presupuesto_a_proyecto` (transición) y `f1_stakeholders_formal` (fase, madurez `formal`). El diseño decide por capacidad ejecutable, no por fase.
- **Una skill de fase compone, no duplica.** Indica qué transversales y tareas puntuales entran en su alcance y con qué alcance específico (p. ej., en F0 `riesgos` siempre, `requisitos` solo a nivel de necesidad preliminar); no reproduce la técnica completa de la capacidad transversal.
- **Cobertura pendiente:** `datos_y_documentacion` y `lecciones_aprendidas` no existen como fichas del catálogo y reciben tratamientos provisionales distintos. `datos_y_documentacion` puede manejarse provisionalmente solo como trazabilidad de evidencia (procedencia y cita de fuente) cuando la fase lo requiera, sin fingir que existe una capacidad dedicada. `lecciones_aprendidas` sigue siendo una decisión de cobertura pendiente: no se absorbe implícitamente y sus registros autoritativos específicos de fase solo se tocan cuando el marco o el catálogo lo exigen explícitamente.

## Plantilla de skill de fase

Estas son las **once secciones por defecto de toda skill de fase**. Las demás capacidades (transversales, tareas puntuales, transiciones, control) adaptan su estructura a partir de su ficha del catálogo y de su fuente de dominio; no están obligadas a estas secciones.

| # | Sección | Debe contener | Evitar |
| -- | ---------------------------------- | ------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------ |
| 1 | Objetivo operativo | La pregunta central de la fase, el resultado buscado y para qué humano decide. | Copiar el objetivo textual sin definir el resultado operativo. |
| 2 | Rol y límites de fase | Vínculo con la capacidad del catálogo, madurez, qué no pertenece a la fase y qué nunca autoriza la skill. | Redefinir el dominio; ampliar el alcance a fases posteriores. |
| 3 | Entradas mínimas | Entradas del marco y regla ante ausencia (vacío declarado, no bloqueo); modelo de evidencia. | Convertir entradas mínimas en cuestionario bloqueante. |
| 4 | Capacidades operacionales | Las actividades guía operacionalizadas, seleccionables según estado, sin orden obligatorio. | Checklist fija, orden numerado obligatorio o duplicación del contenido del marco. |
| 5 | Salidas esperadas | Resultados esperados y forma de entrega (actualizar artefacto autoritativo o borrador estructurado). | Entregables vagos sin destino ni evidencia declarada. |
| 6 | Artefactos obligatorios | Los artefactos del marco y la política de ubicación (autoritativa o `ubicación pendiente`). | Inventar rutas canónicas; fabricar contenido para llenar vacíos. |
| 7 | Review y baseline | Review asociada (nombre y momento típico), tratamiento de baseline y alcance exacto de la skill (solo readiness). | Convocar, conducir o aprobar la review; declarar baselines que el marco no asigna. |
| 8 | Procesos y registros transversales | Cada transversal del alcance con su registro autoritativo y su límite de alcance en esta fase. | Tocar registros fuera del alcance; reproducir la técnica transversal completa. |
| 9 | Criterios de cierre | Los criterios del marco, íntegros, como verificación de readiness. | Añadir o quitar criterios; tratar el cierre como autorización. |
| 10 | Cierre, recomendación y handoff | Los tres juicios separados (recomendación técnica, readiness, decisión humana) y los vacíos que bloquean el handoff. | Autoaprobar cierre, transición o presupuesto; mezclar recomendación con decisión. |
| 11 | Referencias | Fuentes autoritativas de dominio y registros, en las rutas instaladas (`marco/…`, `proyecto/…`). | Referencias no instaladas o inventadas; silenciar faltantes. |

## Reglas operacionales transversales

Toda skill operativa respeta estas reglas, sin repetir justificación en cada una:

| Regla | Contrato |
| ------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Comportamiento adaptativo y consciente del estado | La skill decide el siguiente paso más útil según la evidencia disponible y la madurez de los artefactos; no hay procedimiento numerado ni orden obligatorio. |
| Modelo de evidencia | Toda salida distingue explícitamente `hechos verificados`, `supuestos`, `vacíos` y `contradicciones`. |
| Preguntas progresivas | Se pregunta según la incertidumbre real; nunca se aplica un cuestionario fijo. |
| Maduración de artefactos | Ante evidencia nueva se maduran los borradores y artefactos existentes; nunca se reinicia trabajo ya maduro ni se sobrescribe evidencia en silencio. |
| Rutas autoritativas | Si el artefacto tiene ubicación autoritativa en `proyecto/`, se lee y se madura allí. |
| `ubicación pendiente` | Si un artefacto obligatorio no tiene ubicación autoritativa, se entrega como borrador estructurado marcado `ubicación pendiente`, sin inventar rutas. |
| No inventar | No se inventan estado, entregables, rutas, evidencia ni contenido para llenar un vacío; los faltantes se declaran. |
| Single-writer | Solo el orquestador padre consolida actualizaciones en los documentos autoritativos; los ejecutables producen salidas que el padre integra. |
| Fail-closed | La evidencia no crítica faltante no bloquea: se producen borradores estructurados con los vacíos declarados de forma explícita. La ausencia de evidencia requerida sí bloquea el cierre de fase, las reviews y baselines formales y las transiciones; se solicita su restauración. La disponibilidad de skills no cambia esta regla. |

## Review, baseline y handoff: autoridad y separación

Las skills **pueden evaluar** readiness; **nunca se autoaprueban** reviews, baselines, presupuestos ni transiciones de fase. Toda autorización es explícita y humana. Tres juicios que nunca se mezclan:

| Juicio | Quién | Ejemplo F0 |
| --------------------------------- | ---------------------------------------------------------------- | ------------------------------------------------------------------------------ |
| Recomendación técnica | La skill, con base, confianza y condiciones. | `Go`, `No-Go` o `no concluyente` mientras la evidencia sea insuficiente. |
| Readiness del dossier | La skill, como evaluación explícita de preparación y vacíos. | `borrador`, `listo para revisión` o `no recomendable avanzar`. |
| Decisión y autorización humanas | Los humanos. | Continuidad, presupuesto, veredicto de la MCR, apertura de F1. |

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
- Decisiones de persistencia: <qué registros actualiza y dónde; borradores `ubicación pendiente`>
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
- [ ] La skill preserva los 12 elementos del contrato de transformación.
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
