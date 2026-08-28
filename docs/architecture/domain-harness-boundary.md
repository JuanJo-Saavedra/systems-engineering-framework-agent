---
document_type: propuesta
language: es
version: 0.2
status: propuesta
---
# Frontera dominio-harness

## Propósito

Fijar la autoridad y la dirección de dependencias entre dominio, contratos canónicos, adaptadores de harness, herramientas/MCP y datos de proyecto, para que el harness no redefina el dominio.

## Dirección de dependencias

```text
dominio (marco/)
   ↑ autoridad de significado
catálogo canónico (guias/skill-registry.md)
   ↑ selección
contratos canónicos harness-neutral
   ↑ traducción
adaptador (Codex)
   ↑ ejecución
herramientas / MCP
   ↑ datos
instancia de proyecto (proyecto/)
```

Regla: la dependencia apunta **hacia abajo** (lo inferior puede depender de lo superior), nunca al revés. El dominio no importa Codex; el adaptador sí importa el dominio.

## Autoridad por capa

| Capa                              | Es autoridad sobre               | No es autoridad sobre    |
| --------------------------------- | -------------------------------- | ------------------------ |
| Dominio (`marco/`)              | Significado del proceso          | Ejecución, herramientas |
| Catálogo (`skill-registry.md`) | Qué asistencia existe y cuándo | Significado del dominio  |
| Contratos canónicos              | Reglas de adaptación            | Significado del dominio  |
| Adaptador                         | Artefactos ejecutables           | Significado, catálogo   |
| Herramientas/MCP                  | Capacidad técnica               | Verdad del proyecto      |
| Datos de proyecto (`proyecto/`) | Hechos del proyecto              | Proceso (lo respeta)     |

## Catálogo canónico vs ejecutables

`guias/skill-registry.md` es el **catálogo canónico legible por humanos** de qué asistencia puede dar el framework.

- Las skills y los subagentes son **mapeos/adaptadores ejecutables** del catálogo.
- No se convierten en autoridad sobre el significado del dominio.
- Un cambio de dominio se refleja primero en `marco/` y en el catálogo; después en skills y adaptadores.

## Matriz de responsabilidades

| Responsabilidad                       | Dueño                                |
| ------------------------------------- | ------------------------------------- |
| Definir fase, regla o review          | Dominio (`marco/`)                  |
| Decidir qué capacidad corresponde    | Catálogo + orquestador padre         |
| Ejecutar una capacidad                | Skill/subagente vía harness          |
| Guardar hecho o decisión de proyecto | Markdown autoritativo (`proyecto/`) |
| Recuperar o contextualizar            | RAG/Engram (sin autoridad)            |

## Dónde va cada cambio

| Cambio                                     | ¿Dónde pertenece?         |
| ------------------------------------------ | --------------------------- |
| Nueva regla de proceso                     | `marco/`                  |
| Nueva capacidad o ajuste de cuándo usarla | `guias/skill-registry.md` |
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

Ver [memoria-dual.md](memoria-dual.md) para la política de autoridad de memoria.

## Relacionado

- [arquitectura-orquestador.md](arquitectura-orquestador.md) — capas.
- [memoria-dual.md](memoria-dual.md) — autoridad de memoria.
- [quickstart-agentes.md](quickstart-agentes.md) — flujo mínimo.
- [reestructuracion-agents.md](reestructuracion-agents.md) — decisión canónica: contrato único de `AGENTS.md`.
- [skill-registry.md](skill-registry.md) — catálogo canónico.
