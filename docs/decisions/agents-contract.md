---
document_type: decision
language: es
version: 2.2
status: adoptada
---

# AGENTS.md — decisión canónica: un único contrato de runtime

## Propósito

Registrar la decisión adoptada sobre `AGENTS.md`: existe **un único** contrato canónico de runtime, cuya fuente vive en `runtime/AGENTS.md` y que se instala en el consumidor como `AGENTS.md` de raíz. Esta v2.2 **supersede explícitamente la v2.1** y concilia el contrato con [PRD 1](../prd/prd-001-one-shot-codex-scaffolder.md): tras `se-agent init` exitoso, la copia instalada es **propiedad total del consumidor** (sin copia gestionada ni bloqueo por deriva; no existe `update` en el MVP), y el registry operativo se mantiene **a mano** con verificación de coherencia en CI.

## Decisión adoptada

| Punto | Decisión |
| ----- | -------- |
| Número de contratos | Uno solo: el contrato de runtime. |
| Fuente canónica | `runtime/AGENTS.md`. **No hay** `AGENTS.md` en la raíz del repo de producto. |
| Destino instalado | En el consumidor se instala como `AGENTS.md` de raíz (copia exacta; **propiedad del consumidor** tras `init`). |
| Rol del contrato | Contrato de runtime del orquestador de ingeniería de sistemas (plantilla a probar en Codex). |
| Qué **no** es | Guía de desarrollo del arnés. El desarrollo del arnés es externo a este contrato. |
| Selección de capacidad | Delegada a `catalogo/skill-registry.md` (registry operativo instalado); sin catálogo duplicado en el contrato. |
| Registry instalado | `catalogo/skill-registry.md` se instala como copia exacta de `runtime/catalogo/skill-registry.md` (registry operativo **mantenido a mano**; verificación de coherencia en CI). |
| Arquitectura de capacidades | Vive en `framework/guias/skill-architecture.md`; **no** es la ruta a la que apunta `AGENTS.md` en runtime. |
| Rutas | Solo rutas relativas al repositorio. |
| Identidad | Neutral respecto del harness; no se codifica gentle-pi ni gentle-ai como identidad de runtime. |
| Prevención de deriva | No aplica en el MVP: tras `init`, la copia instalada es del consumidor. Una re-instalación trata las diferencias como colisiones explícitas (PRD 1, §9); no existe `update` ni bloqueo por deriva. |

## Supersede a versiones anteriores

La v1.0 fijó el contrato único en la **raíz del repositorio de producto**. La v2.0 mantuvo la regla de contrato único y precisó su ubicación:

- La fuente se traslada a `runtime/AGENTS.md`.
- Deja de existir `AGENTS.md` en la raíz del repo de producto.
- El `AGENTS.md` de raíz aparece únicamente como **artefacto instalado** en el consumidor.

La v2.1 separó la arquitectura de capacidades del registry operativo:

- `catalogo/skill-registry.md` era arquitectura de capacidades; pasó a `framework/guias/skill-architecture.md`.
- El registry operativo vive en `runtime/catalogo/skill-registry.md` (bootstrap con 0 skills) y se instala como `catalogo/skill-registry.md`.
- `AGENTS.md` (fuente e instalado) apunta a `catalogo/skill-registry.md` — el registry operativo instalado —, **no** a `framework/guias/skill-architecture.md`.

La v2.2 mantiene todo lo anterior y lo concilia con PRD 1:

- La copia instalada de `AGENTS.md` pasa a ser **propiedad del consumidor** tras `se-agent init`; la cláusula "deriva local bloquea la actualización" queda retirada (no existe `update` en el MVP).
- El registry operativo se reclasifica de "generado" a "mantenido a mano con verificación CI" ([skill-artifacts.md](skill-artifacts.md)).

El resto (un contrato, no dos; catálogo no duplicado; rutas relativas; identidad harness-neutral) sigue vigente.

## Por qué se rechaza la separación en dos artefactos

La propuesta previa separaba un "`AGENTS.md` de fuente" (desarrollar el orquestador) de un "`AGENTS.md` de runtime" (operar el proyecto). Se rechaza porque:

- Introduce dos contratos donde el runtime necesita uno solo para operar.
- Mezcla la responsabilidad de desarrollo (externa a la plantilla de runtime) con la operación.
- La plantilla de runtime es la que se instala y se prueba; duplicarla crea deriva.
- La frontera correcta no es "fuente vs runtime", sino "contrato de runtime (`runtime/AGENTS.md`) vs documentación y contratos harness-neutrales (`docs/`, `runtime/agents/` y `adapters/codex/`)".

## Diagnóstico que motivó el cambio (sigue vigente)

| Problema | Resolución en el contrato único |
| -------- | ------------------------------- |
| Ambigüedad producto vs operación | El contrato se declara runtime; su documentación vive en `docs/` y los contratos harness-neutrales, en `runtime/agents/`. |
| Responsabilidades monolíticas | El contrato separa persona, carga de skills, memoria y contrato operativo en secciones escaneables. |
| Catálogo duplicado | Se elimina el mapa de subagentes; la selección se delega al registry operativo instalado (`catalogo/skill-registry.md`). |
| Rutas absolutas Windows rotas | Solo rutas relativas. |
| Sin fronteras testeables | Las reglas de estado/transición y la carga de skills quedan como contratos verificables por comportamiento. |

## Propiedad tras `init`

- **Fuente única**: el contrato se edita solo en `runtime/AGENTS.md` del repo de producto.
- **Propiedad del consumidor**: en el consumidor, `AGENTS.md` de raíz es una copia instalada por `se-agent init`; después de `init` no hay autoridad que la vigile ni la actualice. Si el consumidor la edita, sigue siendo válida para su proyecto; una re-instalación la trata como colisión explícita (PRD 1, §9).
- **Sin chequeo de deriva**: no existe `update` ni manifiesto en el MVP; el ciclo de vida gestionado queda como propuesta futura (PRD 1, §7).
- **Registry instalado**: `catalogo/skill-registry.md` se instala como copia exacta del registry operativo mantenido a mano; el consumidor es su dueño tras `init`.

## Secuencia de transición (aplicada)

- [x] Mover `AGENTS.md` de la raíz a `runtime/AGENTS.md`; confirmar que no queda `AGENTS.md` en raíz del producto.
- [x] Mantener el contrato instalado como `AGENTS.md` de raíz en el consumidor (destino definido; `init` de `se-agent` pendiente).
- [x] Separar la arquitectura de capacidades (`framework/guias/skill-architecture.md`) del registry operativo (`runtime/catalogo/skill-registry.md`); `AGENTS.md` apunta al registry operativo instalado (`catalogo/skill-registry.md`), no a la arquitectura.
- [x] Conservar rutas relativas y la identidad harness-neutral.
- [x] Mantener la documentación operativa y de arquitectura en `docs/`, los contratos harness-neutrales en `runtime/agents/` y lo específico de Codex en `adapters/codex/`.
- [ ] Validar por comportamiento: lectura de estado, selección de capacidad y gate `F1` formal → `F2` (pruebas de comportamiento pendientes).

## Criterios de aceptación

- [x] Existe un único `AGENTS.md` canónico de runtime en `runtime/AGENTS.md`.
- [x] No hay `AGENTS.md` en la raíz del repo de producto.
- [ ] En el consumidor, `AGENTS.md` de raíz es una copia exacta de `runtime/AGENTS.md` propiedad del consumidor (destino definido; depende de `init` de `se-agent`, pendiente).
- [x] Un lector distingue el contrato de runtime de su documentación (`docs/`), de los contratos harness-neutrales (`runtime/agents/`) y de lo específico de Codex (`adapters/codex/`).
- [x] No hay catálogo de capacidades ni registry duplicado en `runtime/AGENTS.md`.
- [x] No hay rutas absolutas Windows.
- [x] El contrato define persona, carga de skills, memoria y contrato operativo de forma escaneable.
- [x] `AGENTS.md` apunta al registry operativo instalado (`catalogo/skill-registry.md`), no a `framework/guias/skill-architecture.md`.
- [ ] El registry operativo se instala como copia exacta desde `runtime/catalogo/skill-registry.md`, propiedad del consumidor (destino definido; depende de `init`, pendiente).

## No-objetivos

- No se reescribe el dominio (`framework/marco/`).
- No se convierte `framework/guias/skill-architecture.md` en la ruta instalada a la que apunta `AGENTS.md`.
- El registry operativo no se genera: se mantiene a mano y CI verifica su coherencia ([skill-artifacts.md](skill-artifacts.md), PRD 1 §11).
- No existe `update` ni chequeo de deriva en el MVP; la propiedad de la copia instalada pasa al consumidor tras `init`.
- No se codifica un harness concreto como identidad de runtime.
- No se declara subagente a toda capacidad transversal.

## Relacionado

- [architecture/orchestrator.md](../architecture/orchestrator.md) — capas y adaptador.
- [architecture/domain-harness-boundary.md](../architecture/domain-harness-boundary.md) — autoridad.
- [guides/quickstart.md](../guides/quickstart.md) — flujo mínimo.
- [architecture/memory.md](../architecture/memory.md) — persistencia.
- [skill-artifacts.md](skill-artifacts.md) — arquitectura de capacidades vs registry operativo.
- [../prd/prd-001-one-shot-codex-scaffolder.md](../prd/prd-001-one-shot-codex-scaffolder.md) — PRD 1 (autoridad de requisitos del MVP).
- [skill-architecture.md](../../framework/guias/skill-architecture.md) — arquitectura de capacidades.
