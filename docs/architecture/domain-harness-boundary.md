---
document_type: propuesta
language: es
version: 0.2
status: propuesta
---
# Frontera dominio-harness

## Propósito

Fijar la autoridad y la dirección de dependencias entre dominio, contratos canónicos, adaptadores de harness, herramientas/MCP y datos de proyecto, para que el harness no redefina el dominio.

> Las rutas `framework/marco/`, `framework/guias/skill-architecture.md` y `runtime/catalogo/skill-registry.md` son las rutas vigentes del repositorio (reestructuración ejecutada). Ver [product.md](product.md).

## Dirección de dependencias

```text
dominio (framework/marco/)
   ↑ autoridad de significado
arquitectura de capacidades (framework/guias/skill-architecture.md)
   ↑ selección conceptual
contratos canónicos harness-neutral
   ↑ traducción
registry operativo (runtime/catalogo/skill-registry.md)
   ↑ disponibilidad de skills
adaptador (Codex)
   ↑ ejecución
herramientas / MCP
   ↑ datos
instancia de proyecto (proyecto/)
```

Regla: la dependencia apunta **hacia abajo** (lo inferior puede depender de lo superior), nunca al revés. El dominio no importa Codex; el adaptador sí importa el dominio.

## Autoridad por capa

| Capa | Es autoridad sobre | No es autoridad sobre |
| --------------------------------- | -------------------------------- | ------------------------ |
| Dominio (`framework/marco/`) | Significado del proceso | Ejecución, herramientas |
| Arquitectura de capacidades (`framework/guias/skill-architecture.md`) | Qué asistencia existe y cuándo (diseño) | Significado del dominio, disponibilidad runtime |
| Contratos canónicos | Reglas de adaptación | Significado del dominio |
| Registry operativo (`runtime/catalogo/skill-registry.md`) | Disponibilidad de skills | Significado del dominio, routing, guardas |
| Adaptador | Artefactos ejecutables | Significado, arquitectura de capacidades |
| Herramientas/MCP | Capacidad técnica | Verdad del proyecto |
| Datos de proyecto (`proyecto/`) | Hechos del proyecto | Proceso (lo respeta) |

## Arquitectura de capacidades vs registry operativo vs ejecutables

`framework/guias/skill-architecture.md` es la **arquitectura de capacidades legible por humanos**: qué asistencia puede dar el framework y cuándo. `runtime/catalogo/skill-registry.md` es el **registry operativo** de skills disponibles en runtime.

- Las skills y los subagentes son **mapeos/adaptadores ejecutables**; el registry solo enumera su disponibilidad.
- Ni skills, ni subagentes, ni el registry se convierten en autoridad sobre el significado del dominio.
- Un cambio de dominio se refleja primero en `framework/marco/` y en la arquitectura de capacidades; después en skills, registry y adaptadores.

## Matriz de responsabilidades

| Responsabilidad                       | Dueño                                |
| ------------------------------------- | ------------------------------------- |
| Definir fase, regla o review          | Dominio (`framework/marco/`)        |
| Decidir qué capacidad corresponde    | Arquitectura de capacidades + orquestador padre |
| Ejecutar una capacidad                | Skill/subagente vía harness          |
| Guardar hecho o decisión de proyecto | Markdown autoritativo (`proyecto/`) |
| Recuperar o contextualizar            | RAG/Engram (sin autoridad)            |

## Dónde va cada cambio

| Cambio                                     | ¿Dónde pertenece?         |
| ------------------------------------------ | --------------------------- |
| Nueva regla de proceso                     | `framework/marco/`        |
| Nueva capacidad o ajuste de cuándo usarla | `framework/guias/skill-architecture.md` |
| Nueva skill disponible                    | `runtime/skills/` + regenerar `runtime/catalogo/skill-registry.md` |
| Nuevo procedimiento de ejecución          | Skill                       |
| Nueva configuración/agente Codex          | Adaptador                   |
| Nueva integración de herramienta          | MCP                         |
| Hecho nuevo del proyecto                   | `proyecto/` (Markdown)    |

## Padre vs delegable

| Solo el orquestador padre                           | Delegable                 |
| --------------------------------------------------- | ------------------------- |
| Leer estado autoritativo                            | Exploración de contexto  |
| Elegir ruta/capacidad                               | Redacción acotada        |
| Actualizar documentos autoritativos (single-writer) | Análisis de solo lectura |
| Decidir gates y transiciones                        | Preparar borrador         |

**Single-writer**: un único escritor (el padre) actualiza los documentos autoritativos del proyecto. Los subagentes producen salidas; el padre consolida.

## Reglas anti-corrupción

| Regla                                              | Razón                                        |
| -------------------------------------------------- | --------------------------------------------- |
| Sin configuración Codex en contratos de dominio   | El dominio debe seguir siendo harness-neutral |
| Sin reglas de dominio duplicadas en TOML           | Evitar doble autoridad y deriva               |
| Sin memoria Engram que sobrescriba estado Markdown | Markdown es la verdad; Engram es suplemento   |

Ver [memory.md](memory.md) para la política de autoridad de memoria.

## Relacionado

- [orchestrator.md](orchestrator.md) — capas.
- [memory.md](memory.md) — autoridad de memoria.
- [quickstart.md](../guides/quickstart.md) — flujo mínimo.
- [agents-contract.md](../decisions/agents-contract.md) — decisión canónica: contrato único de `AGENTS.md`.
- [skill-artifacts.md](../decisions/skill-artifacts.md) — arquitectura de capacidades vs registry operativo.
- [skill-architecture.md](../../framework/guias/skill-architecture.md) — arquitectura de capacidades.
