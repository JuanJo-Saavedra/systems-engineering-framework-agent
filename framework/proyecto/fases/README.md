# Artefactos de fase del proyecto

Esta carpeta contiene las instancias concretas de cada fase del proyecto.

## Uso sugerido

- mantener aquí documentos vivos por fase,
- mantener nombres y estructura consistentes con los contratos definidos en `marco/fases/`,
- referenciar desde aquí a los registros transversales cuando un artefacto dependa de ellos.

## Artefactos canónicos de `F1` (`f1_stakeholders/`)

Los cuatro artefactos obligatorios de `F1` viven en rutas canónicas; son **únicos por proyecto**: `F1 preliminar` los crea y los entrega en madurez `preliminar`, y `F1 formal` madura **el mismo archivo** a `formal`. Nunca se crean copias por madurez; la madurez activa queda en `active_maturity`, el estado de aprobación vigente en `doc_approval`, y la trayectoria de aprobaciones en el `## Historial de aprobación` del cuerpo de cada documento.

| Artefacto obligatorio de F1                 | Archivo canónico                                          | `document_type`                  |
| ------------------------------------------- | --------------------------------------------------------- | -------------------------------- |
| Stakeholder requirements document           | [requisitos_stakeholders.md](f1_stakeholders/requisitos_stakeholders.md) | `stakeholder_requirements`       |
| Casos de uso o escenarios operativos        | [escenarios_operativos.md](f1_stakeholders/escenarios_operativos.md)     | `operational_scenarios`          |
| Restricciones externas                      | [restricciones_externas.md](f1_stakeholders/restricciones_externas.md)   | `external_constraints`           |
| Matriz necesidad ↔ stakeholder requirement  | [matriz_necesidad_requisito_stakeholder.md](f1_stakeholders/matriz_necesidad_requisito_stakeholder.md) | `need_stakeholder_requirement_matrix` |

Cada artefacto lleva el frontmatter común (`document_type`, `language: es`, `active_maturity`, `last_updated`, `doc_approval`, `responsible`) y documenta el ciclo `doc_approval` (`pendiente`, `aprobado`, `rechazado`): `pendiente` durante el trabajo preliminar, `aprobado` al cierre preliminar, **reseteado a `pendiente`** al iniciar el trabajo formal preservando el historial, y `aprobado` al cierre formal. `responsible` identifica al custodio humano vigente; nunca al aprobador.

## Ejemplos futuros

- `f0_factibilidad/`
- `f2_requisitos_sistema/`
