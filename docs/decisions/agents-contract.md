---
document_type: decision
language: es
version: 1.0
status: adoptada
---

# AGENTS.md — decisión canónica: un único contrato de runtime

## Propósito

Registrar la decisión adoptada sobre `AGENTS.md`: existe **un único** contrato canónico de runtime en la raíz del repositorio, no dos artefactos separados (fuente vs runtime). Este documento reemplaza la propuesta anterior de separación y conserva el diagnóstico útil y los criterios de migración.

## Decisión adoptada

| Punto | Decisión |
| ----- | -------- |
| Número de contratos | Uno solo: `AGENTS.md` en la raíz. |
| Rol del `AGENTS.md` | Contrato de runtime del orquestador de ingeniería de sistemas (plantilla a probar en Codex). |
| Qué **no** es | Guía de desarrollo del arnés. El desarrollo del arnés es externo a este contrato. |
| Catálogo de capacidades | Delegado a `guias/skill-registry.md`; sin catálogo duplicado en `AGENTS.md`. |
| Rutas | Solo rutas relativas al repositorio. |
| Identidad | Neutral respecto del harness; no se codifica gentle-pi ni gentle-ai como identidad de runtime. |

## Por qué se rechaza la separación en dos artefactos

La propuesta previa separaba un "`AGENTS.md` de fuente" (desarrollar el orquestador) de un "`AGENTS.md` de runtime" (operar el proyecto). Se rechaza porque:

- Introduce dos contratos donde el runtime necesita uno solo para operar.
- Mezcla la responsabilidad de desarrollo (externa a la plantilla de runtime) con la operación.
- El `AGENTS.md` de raíz ya es la plantilla que se instala y se prueba; duplicarlo crea deriva.
- La frontera correcta no es "fuente vs runtime", sino "contrato de runtime (`AGENTS.md`) vs documentación y futura implementación del arnés (`guias/` e `implementacion/`)".

## Diagnóstico que motivó el cambio (sigue vigente)

| Problema | Resolución en el contrato único |
| -------- | ------------------------------- |
| Ambigüedad producto vs operación | `AGENTS.md` se declara contrato de runtime; su documentación vive en `guias/` y la futura implementación del arnés, en `implementacion/`. |
| Responsabilidades monolíticas | El contrato separa persona, carga de skills, memoria y contrato operativo en secciones escaneables. |
| Catálogo duplicado | Se elimina el mapa de subagentes; la selección se delega a `guias/skill-registry.md`. |
| Rutas absolutas Windows rotas | Solo rutas relativas. |
| Sin fronteras testeables | Las reglas de estado/transición y la carga de skills quedan como contratos verificables por comportamiento. |

## Secuencia de migración (adoptada)

1. Reemplazar el `AGENTS.md` previo por el contrato único de runtime.
2. Eliminar el mapa de subagentes duplicado; apuntar a `guias/skill-registry.md`.
3. Convertir rutas absolutas a rutas relativas.
4. Mantener la documentación operativa y de arquitectura en `guias/`, y la futura implementación del arnés en `implementacion/`.
5. Validar por comportamiento: lectura de estado, selección de capacidad, gate `F1` formal → `F2`, degradación de memoria.

## Criterios de aceptación

- [ ] Existe un único `AGENTS.md` canónico de runtime.
- [ ] Un lector distingue el contrato de runtime de su documentación (`guias/`) y de la futura implementación del arnés (`implementacion/`).
- [ ] No hay catálogo de capacidades duplicado en `AGENTS.md`.
- [ ] No hay rutas absolutas Windows.
- [ ] El contrato define persona, carga de skills, memoria y contrato operativo de forma escaneable.
- [ ] El catálogo canónico sigue siendo `guias/skill-registry.md`.

## No-objetivos

- No se reescribe el dominio (`marco/`).
- No se reemplaza `guias/skill-registry.md` como catálogo canónico.
- No se codifica un harness concreto como identidad de runtime.
- No se declara subagente a toda capacidad transversal.

## Relacionado

- [arquitectura-orquestador.md](arquitectura-orquestador.md) — capas y adaptador.
- [frontera-dominio-harness.md](frontera-dominio-harness.md) — autoridad.
- [quickstart-agentes.md](quickstart-agentes.md) — flujo mínimo.
- [memoria-dual.md](memoria-dual.md) — persistencia.
- [skill-registry.md](skill-registry.md) — catálogo canónico.
