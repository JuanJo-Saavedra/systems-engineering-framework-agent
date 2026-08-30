---
document_type: decision
language: es
version: 1.1
status: adoptada
---

# Artefactos de skills — arquitectura de capacidades vs registry operativo

> **v1.1:** conciliada con [PRD 1](../prd/prd-001-one-shot-codex-scaffolder.md) (§11): el registry operativo pasa de "generado" a **mantenido manualmente** por los autores del producto, con verificación de coherencia bidireccional en CI/tests. CI nunca genera ni modifica el registry.

## Decisión adoptada

Las skills del producto se describen en **dos** artefactos con autoridades distintas, más un índice técnico del harness de desarrollo que no forma parte del producto:

| Artefacto | Ruta | Rol | ¿Se instala? |
| --- | --- | --- | --- |
| Arquitectura de capacidades | `framework/guias/skill-architecture.md` | Autoridad de significado: qué asistencia existe, cuándo aplica, entradas/salidas y guardas. | No |
| Registry operativo | `runtime/catalogo/skill-registry.md` (se instala como `catalogo/skill-registry.md`) | Inventario de skills disponibles y accesibles, **mantenido a mano**. | Sí (copia exacta, propiedad del consumidor) |
| Índice técnico del harness | `.atl/skill-registry.md` | Índice de desarrollo para seleccionar skills del harness local. | No |

Regla rectora: **la arquitectura de capacidades es fuente de significado; el registry operativo es fuente de disponibilidad.** Ninguno sustituye al otro.

## Qué es cada artefacto

- **Arquitectura de capacidades** (`framework/guias/skill-architecture.md`): define el modelo de capacidades del framework (fases, transversales, tareas puntuales, orquestación), sus condiciones de uso, fuentes autoritativas, salidas y guardas. Es base de diseño, comportamiento y accionamiento del producto. **No** se empaqueta ni se instala en consumidores.
- **Registry operativo** (`runtime/catalogo/skill-registry.md`): enumera las skills realmente disponibles y accesibles al agente en runtime. Es **inventario operativo mantenido a mano**, no un "catálogo canónico de capacidades". No duplica el algoritmo de routing, las guardas ni las fichas completas de capacidades.
- **Índice técnico del harness** (`.atl/skill-registry.md`): exclusivo del harness de desarrollo. No se empaqueta, no se instala y no es autoridad del producto.

## Autoridad

| Pregunta | Respuesta |
| --- | --- |
| ¿Dónde se decide **qué** asistencia existe? | `framework/guias/skill-architecture.md`. |
| ¿Dónde se decide **qué** skill está disponible en runtime? | `runtime/catalogo/skill-registry.md`, editado a mano por los autores del producto. |
| ¿Dónde apunta `AGENTS.md` instalado? | `catalogo/skill-registry.md` (registry operativo instalado). |
| ¿Dónde **no** apunta `AGENTS.md`? | `framework/guias/skill-architecture.md` (no es ruta instalada). |
| ¿Qué es `.atl/skill-registry.md`? | Índice técnico del harness de desarrollo; sin rol de producto. |

## Mantenimiento del registry operativo

- **Fuente de verdad del inventario**: `runtime/catalogo/skill-registry.md`, **editado a mano** por los autores del producto.
- **Generación**: ninguna. No existe comando de build del registry; CI **nunca** genera ni modifica el registro.
- **Verificación (bidireccional, en tests y CI)**: 1) toda skill bajo `runtime/skills/*/SKILL.md` tiene exactamente una entrada en el registry con nombre y ruta correctos; 2) toda entrada del registry resuelve a una skill existente y su nombre coincide. Duplicados, faltantes y entradas obsoletas **fallan** la verificación.
- **Destino instalado**: `catalogo/skill-registry.md` como copia exacta, propiedad del consumidor tras `se-agent init`.
- **Estado actual**: `runtime/skills/` existe pero está vacío y `runtime/catalogo/skill-registry.md` es un bootstrap con **0 skills**. La verificación y la skill F0 son **implementación pendiente**; no se declaran skills disponibles.

## Campos mínimos del registry

| Campo | Obligatorio | Qué captura |
| --- | --- | --- |
| nombre/id de skill | sí | Identificador estable de la skill. |
| descripción/trigger | sí | Para qué sirve y cuándo aplica (metadata para selección). |
| path instalado relativo | sí | Ruta relativa donde la skill queda instalada. |
| scope/compatibilidad | solo si existe | Alcance o restricción de compatibilidad cuando aplica. |

El registry **no** duplica:

- el algoritmo de routing (vive en `AGENTS.md` y en la arquitectura de capacidades);
- las guardas de dominio;
- las fichas completas de capacidades (viven en `framework/guias/skill-architecture.md`);
- las instrucciones ejecutables (viven en cada `SKILL.md`).

## Validaciones

| Validación | Responsable | Condición |
| --- | --- | --- |
| Registry ↔ skills fuente (bidireccional) | Tests y CI | Falla si hay skills sin entrada, entradas sin skill, nombres/rutas incorrectos, duplicados u entradas obsoletas. |
| Coherencia del instalado | Por construcción | `se-agent init` instala skills y registry del mismo tag (PRD 1, §11); no existe `doctor` en el MVP. |

## No-objetivos

- No se genera el registry operativo (sin comando de build); CI nunca lo modifica, solo verifica su coherencia.
- No se instala `framework/guias/` en consumidores.
- No se empaqueta ni se instala `.atl/skill-registry.md`.
- No se convierte el registry operativo en autoridad de significado del dominio.
- No se declaran skills disponibles mientras `runtime/skills/` esté vacío.

## Relacionado

- [product.md](../architecture/product.md) — arquitectura del producto (v3.0, conciliada con PRD 1).
- [agents-contract.md](agents-contract.md) — contrato único de `AGENTS.md` y su apunte al registry operativo instalado.
- [../prd/prd-001-one-shot-codex-scaffolder.md](../prd/prd-001-one-shot-codex-scaffolder.md) — PRD 1 (autoridad de requisitos; §11 registry manual y verificación).
- [orchestrator.md](../architecture/orchestrator.md) — selección conceptual vs resolución runtime.
- [domain-harness-boundary.md](../architecture/domain-harness-boundary.md) — autoridad de arquitectura vs disponibilidad runtime.
