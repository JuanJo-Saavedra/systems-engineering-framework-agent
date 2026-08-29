---
document_type: decision
language: es
version: 1.0
status: adoptada
---

# Artefactos de skills — arquitectura de capacidades vs registry operativo

## Decisión adoptada

Las skills del producto se describen en **dos** artefactos con autoridades distintas, más un índice técnico del harness de desarrollo que no forma parte del producto:

| Artefacto | Ruta | Rol | ¿Se instala? |
| --- | --- | --- | --- |
| Arquitectura de capacidades | `framework/guias/skill-architecture.md` | Autoridad de significado: qué asistencia existe, cuándo aplica, entradas/salidas y guardas. | No |
| Registry operativo | `runtime/catalogo/skill-registry.md` (se instala como `catalogo/skill-registry.md`) | Inventario/registro generado de skills disponibles y accesibles. | Sí (read-only) |
| Índice técnico del harness | `.atl/skill-registry.md` | Índice de desarrollo para seleccionar skills del harness local. | No |

Regla rectora: **la arquitectura de capacidades es fuente de significado; el registry operativo es fuente de disponibilidad.** Ninguno sustituye al otro.

## Qué es cada artefacto

- **Arquitectura de capacidades** (`framework/guias/skill-architecture.md`): define el modelo de capacidades del framework (fases, transversales, tareas puntuales, orquestación), sus condiciones de uso, fuentes autoritativas, salidas y guardas. Es base de diseño, comportamiento y accionamiento del producto. **No** se empaqueta ni se instala en consumidores.
- **Registry operativo** (`runtime/catalogo/skill-registry.md`): enumera las skills realmente disponibles y accesibles al agente en runtime. Es **inventario operativo generado**, no un "catálogo canónico de capacidades". No duplica el algoritmo de routing, las guardas ni las fichas completas de capacidades.
- **Índice técnico del harness** (`.atl/skill-registry.md`): exclusivo del harness de desarrollo. No se empaqueta, no se instala y no es autoridad del producto.

## Autoridad

| Pregunta | Respuesta |
| --- | --- |
| ¿Dónde se decide **qué** asistencia existe? | `framework/guias/skill-architecture.md`. |
| ¿Dónde se decide **qué** skill está disponible en runtime? | `runtime/catalogo/skill-registry.md`, generado desde `runtime/skills/*/SKILL.md`. |
| ¿Dónde apunta `AGENTS.md` instalado? | `catalogo/skill-registry.md` (registry operativo instalado). |
| ¿Dónde **no** apunta `AGENTS.md`? | `framework/guias/skill-architecture.md` (no es ruta instalada). |
| ¿Qué es `.atl/skill-registry.md`? | Índice técnico del harness de desarrollo; sin rol de producto. |

## Generación del registry operativo

- **Input**: frontmatter de cada `runtime/skills/*/SKILL.md`.
- **Output**: `runtime/catalogo/skill-registry.md` **versionado**.
- **Mantenimiento**: generado, **no** editado a mano.
- **Destino instalado**: `catalogo/skill-registry.md` read-only y gestionado.
- **Estado actual**: `runtime/skills/` existe pero está vacío y `runtime/catalogo/skill-registry.md` es un bootstrap con **0 skills**. El generador y su validación por CI siguen **pendientes**; no se declaran skills disponibles.

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
| Registry ↔ skills fuente | Build/CI | Falla si `runtime/catalogo/skill-registry.md` no coincide con el frontmatter de `runtime/skills/*/SKILL.md`. |
| Registry instalado ↔ skills instaladas | `doctor` | Falla si el registry instalado no refleja las skills instaladas. |
| Registry instalado ↔ manifiesto/hashes | `doctor` | Falla si el registry instalado difiere de su hash registrado. |

## No-objetivos

- No se mantiene el registry operativo a mano.
- No se instala `framework/guias/` en consumidores.
- No se empaqueta ni se instala `.atl/skill-registry.md`.
- No se convierte el registry operativo en autoridad de significado del dominio.
- No se declaran skills disponibles mientras `runtime/skills/` esté vacío.

## Relacionado

- [product.md](../architecture/product.md) — arquitectura del producto (v2.2).
- [agents-contract.md](agents-contract.md) — contrato único de `AGENTS.md` y su apunte al registry operativo instalado.
- [orchestrator.md](../architecture/orchestrator.md) — selección conceptual vs resolución runtime.
- [domain-harness-boundary.md](../architecture/domain-harness-boundary.md) — autoridad de arquitectura vs disponibilidad runtime.
