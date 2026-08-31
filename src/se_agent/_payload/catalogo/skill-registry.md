---
document_type: registry_operativo
language: es
version: 1.2
status: manual
maintained_by: autores del producto
skills_source: runtime/skills/*/SKILL.md
installed_as: catalogo/skill-registry.md
skills_available: 1
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

| id | trigger | ruta |
| -- | ------- | ---- |
| `f0_factibilidad` | Fase F0 activa / estado `preproyecto_presupuesto`; problema, CONOPS, ROM, riesgos, Go/No-Go | `.agents/skills/f0_factibilidad/SKILL.md` |

## Estado de la verificación

La verificación de coherencia bidireccional (registry ↔ `runtime/skills/`: entradas exactas, sin duplicados, faltantes ni obsoletos) está implementada en `tests/unit/test_registry_coherence.py` con el verificador de solo lectura `tests/helpers/registry_check.py`, y corre en tests/CI (PRD 1, AC-10). Esta verificación **nunca genera ni modifica** este archivo (PRD 1, §11); la edición manual sigue siendo la única forma de cambiarlo.
