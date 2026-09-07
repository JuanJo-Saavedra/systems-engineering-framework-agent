---
document_type: propuesta
language: es
version: 0.5
status: propuesta
---
# Frontera dominio-harness

> Conciliada con [PRD 1](../prd/prd-001-one-shot-codex-scaffolder.md) (aprobado): el registry operativo se mantiene a mano con verificación CI; CI nunca lo genera ni lo modifica.

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
| Nueva skill disponible                    | `runtime/skills/` + actualizar a mano la entrada en `runtime/catalogo/skill-registry.md` (CI verifica la coherencia; nunca genera el registro) |
| Nuevo procedimiento de ejecución          | Skill                       |
| Nueva configuración/agente Codex          | Adaptador                   |
| Nueva integración de herramienta          | MCP                         |
| Hecho nuevo del proyecto                   | `proyecto/` (Markdown)    |

## Padre vs delegable

| Solo el orquestador padre                           | Delegable                 |
| --------------------------------------------------- | ------------------------- |
| Leer estado autoritativo                            | Exploración de contexto  |
| Elegir ruta/capacidad                               | Redacción acotada        |
| Actualizar documentos vivos y estado del proyecto (single-writer) | Análisis de solo lectura |
| Decidir gates y transiciones                        | Preparar borrador         |

**Single-writer**: el padre es el único escritor de los documentos vivos y el estado del proyecto: `proyecto/fases/**`, `proyecto/estado/**`, `proyecto/hitos/**` y `proyecto/registros/**`. Los subagentes producen salidas; el padre consolida.

**Distinción de review:** los snapshots de paquetes en `proyecto/docs-verificacion/**` y `proyecto/docs-aprobados/**` son superficies de autoridad humana. El orquestador padre lógico, ejecutado dentro de Codex, dirige las operaciones mecánicas solo bajo instrucción conversacional humana explícita, sin transferir autoridad de aprobación. El backend implementado `runtime/skills/docs-review/scripts/docs_review.ps1` es un detalle de la skill de runtime `docs-review` (Windows PowerShell 5.1 + .NET), nunca lógica de dominio: el dominio no lo importa ni conoce, el padre lo ordena dentro del contrato ya compuesto y Codex lo ejecuta. El núcleo genérico cuenta con skill, contrato, catálogo, registry, payload y pruebas estáticas; el gate estático Linux pasó 8/8, pero falta ejecutar su suite nativa en Windows PowerShell Desktop 5.1 y no hay CI Windows por decisión humana. La integración de F1 está implementada como skill de fase pura (`runtime/skills/f1-stakeholders-formal`), integrada solo por emisión; la composición con `docs-review` la ejecuta el padre ante instrucción humana explícita; ver [design-document-review-lifecycle.md](design-document-review-lifecycle.md).

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
