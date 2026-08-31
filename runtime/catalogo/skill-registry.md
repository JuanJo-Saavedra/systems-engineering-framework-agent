---
document_type: registry_operativo
language: es
version: 1.1
status: manual
maintained_by: autores del producto
skills_source: runtime/skills/*/SKILL.md
installed_as: catalogo/skill-registry.md
skills_available: 0
---

# Registry operativo de skills

> **Mantenido a mano — no se genera.** Este archivo es el inventario operativo de skills disponibles. Lo editan manualmente los autores del producto al añadir, renombrar o retirar skills en `runtime/skills/`; CI/tests verifican su coherencia bidireccional con ese directorio y **nunca lo generan ni lo modifican** (PRD 1, §11).

## Fuente y destino

| Dato | Valor |
| --- | --- |
| Skills fuente | `runtime/skills/*/SKILL.md` |
| Destino instalado | `catalogo/skill-registry.md` (copia exacta; propiedad del consumidor tras `se-agent init`) |
| Mantenimiento | Manual y versionado; sin comando de build ni generación |

## Skills disponibles

**Cero (0) skills disponibles.**

`runtime/skills/` aún no contiene ningún `SKILL.md`, por lo que este registro no declara ninguna skill disponible. No se inventan entradas. El poblado corresponde a la skill F0 funcional del slice vertical de PRD 1 (**implementación pendiente**).

## Estado de la verificación

La verificación de coherencia bidireccional (registry ↔ `runtime/skills/`: entradas exactas, sin duplicados, faltantes ni obsoletos) en tests/CI está **pendiente de implementación** (PRD 1, AC-10). Mientras tanto, la coherencia se mantiene por revisión manual al editar cualquiera de los dos lados.
