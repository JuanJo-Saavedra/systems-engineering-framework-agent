---
document_type: decision
language: es
version: 1.2
status: adoptada
---

# Artefactos de skills — arquitectura de capacidades vs registry operativo

> **v1.1:** conciliada con [PRD 1](../prd/prd-001-one-shot-codex-scaffolder.md) (§11): el registry operativo pasa de "generado" a **mantenido manualmente** por los autores del producto, con verificación de coherencia bidireccional en CI/tests. CI nunca genera ni modifica el registry.
>
> **v1.2:** conciliada con la [arquitectura canónica de capacidades](../../framework/guias/skill-architecture.md): el modelo pasa de dos artefactos a **cuatro capas** (marco conceptual, catálogo de capacidades, skills operativas de runtime y espejo de empaquetado); se registra la primera skill operativa (`f0-factibilidad`) y se retira el estado "runtime vacío".

## Decisión adoptada

El conocimiento de skills del producto vive en **cuatro capas** con autoridades distintas, más dos artefactos de inventario cuyos roles adoptados se preservan sin cambios (registry operativo manual e índice técnico del harness):

| Capa | Ruta | Rol | Mantenimiento |
| --- | --- | --- | --- |
| Marco conceptual | `framework/marco/**` | Autoridad del dominio conceptual: fases, contratos de artefactos, reviews, baselines y guardas del método. | Equipo de ingeniería de sistemas. |
| Arquitectura de capacidades | `framework/guias/skill-architecture.md` | Autoridad de catálogo y routing: qué asistencia existe, cuándo aplica, entradas/salidas y guardas; define los identificadores conceptuales y los bindings. | Autores del producto. |
| Skills operativas de runtime | `runtime/skills/**/SKILL.md` | Proyección operativa **autocontenida** de una capacidad, para el orquestador de runtime. | Autores del producto. |
| Espejo de empaquetado | `src/se_agent/_payload/**` | Espejo **generado** del contenido instalable (skills, catalogo, marco); nunca se edita directamente. | Generación del packager. |

Se preservan sin cambios las distinciones ya adoptadas: el **registry operativo** (`runtime/catalogo/skill-registry.md`, instalado como `catalogo/skill-registry.md`) sigue siendo el inventario manual de disponibilidad, y `.atl/skill-registry.md` sigue siendo el índice técnico del harness de desarrollo, sin rol de producto.

### Proyección operativa

Las skills de `runtime/skills/**/SKILL.md` no copian ni resumen el marco: lo **proyectan**. Una proyección operativa conserva todos los conceptos relevantes de la capacidad del marco (contrato de fase, guardas, fuentes autoritativas, salidas esperadas) y los adapta a comportamiento consciente del estado del proyecto: decidir el siguiente paso más útil según la evidencia disponible, producir y actualizar artefactos, declarar la preparación de review, y explicitar el cierre y el handoff hacia la fase siguiente. Una skill operativa es una **capacidad que actúa**, no un manual ni una checklist: nunca aplica un cuestionario fijo ni reinicia trabajo ya maduro.

Regla rectora: **el marco es fuente del dominio conceptual; la arquitectura de capacidades es fuente de significado y routing; el registry operativo es fuente de disponibilidad.** Ninguna capa sustituye a otra.

## Qué es cada capa

- **Marco conceptual** (`framework/marco/**`): define el método de ingeniería de sistemas: fases, contratos de artefactos, reviews, baselines y reglas del ciclo. Es la autoridad conceptual mantenida por el equipo de ingeniería de sistemas; las demás capas la citan y proyectan, jamás la redefinen.
- **Arquitectura de capacidades** (`framework/guias/skill-architecture.md`): define el modelo de capacidades del framework (fases, transversales, tareas puntuales, orquestación), sus condiciones de uso, fuentes autoritativas, salidas y guardas. Es base de diseño, comportamiento y accionamiento del producto. **No** se empaqueta ni se instala en consumidores.
- **Skills operativas de runtime** (`runtime/skills/**/SKILL.md`): una por capacidad proyectada; autocontenidas para el orquestador (ver Proyección operativa). Cada skill ejecutable exige una entrada en el registry.
- **Espejo de empaquetado** (`src/se_agent/_payload/**`): copia generada de lo que se instala en el consumidor. Editar la fuente y regenerar; editar el espejo a mano está prohibido.
- **Registry operativo** (`runtime/catalogo/skill-registry.md`): enumera las skills realmente disponibles y accesibles al agente en runtime. Es **inventario operativo mantenido a mano**, no un "catálogo canónico de capacidades". No duplica el algoritmo de routing, las guardas ni las fichas completas de capacidades.
- **Índice técnico del harness** (`.atl/skill-registry.md`): exclusivo del harness de desarrollo. No se empaqueta, no se instala y no es autoridad del producto.

## Autoridad

| Pregunta | Respuesta |
| --- | --- |
| ¿Dónde se decide **qué significa** una capacidad en el dominio? | `framework/marco/**` (autoridad conceptual del equipo de ingeniería de sistemas). |
| ¿Dónde se decide **qué** asistencia existe y cómo se enruta? | `framework/guias/skill-architecture.md`. |
| ¿Dónde vive la **ejecución operativa**? | `runtime/skills/**/SKILL.md` (proyección autocontenida; nunca redefine el dominio). |
| ¿Se edita `src/se_agent/_payload/**` a mano? | Nunca: es espejo generado; se edita la fuente y se regenera. |
| ¿Dónde se decide **qué** skill está disponible en runtime? | `runtime/catalogo/skill-registry.md`, editado a mano por los autores del producto. |
| ¿Dónde apunta `AGENTS.md` instalado? | `catalogo/skill-registry.md` (registry operativo instalado). |
| ¿Dónde **no** apunta `AGENTS.md`? | `framework/guias/skill-architecture.md` (no es ruta instalada). |
| ¿Qué es `.atl/skill-registry.md`? | Índice técnico del harness de desarrollo; sin rol de producto. |

## Mantenimiento del registry operativo

- **Fuente de verdad del inventario**: `runtime/catalogo/skill-registry.md`, **editado a mano** por los autores del producto.
- **Generación**: ninguna. No existe comando de build del registry; CI **nunca** genera ni modifica el registro.
- **Verificación (bidireccional, en tests y CI)**: 1) toda skill bajo `runtime/skills/*/SKILL.md` tiene exactamente una entrada en el registry con nombre y ruta correctos; 2) toda entrada del registry resuelve a una skill existente y su nombre coincide. Duplicados, faltantes y entradas obsoletas **fallan** la verificación.
- **Destino instalado**: `catalogo/skill-registry.md` como copia exacta, propiedad del consumidor tras `se-agent init`.
- **Estado actual**: `runtime/skills/` contiene la primera skill operativa (`f0-factibilidad`) y el registry la declara disponible; la verificación bidireccional está implementada en tests/CI. El catálogo de capacidades **no** está completamente mapeado: solo `f0_factibilidad` tiene enlace ejecutable declarado (`mapeada`); el resto permanece en `definida` hasta que exista su skill operativa y su entrada en el registry.

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
- No se declara `mapeada` una capacidad sin skill ejecutable y entrada correspondiente en el registry; añadir una skill sin su entrada del registry rompe la verificación.
- No se edita `src/se_agent/_payload/**` a mano.

## Relacionado

- [product.md](../architecture/product.md) — arquitectura del producto (v3.0, conciliada con PRD 1).
- [agents-contract.md](agents-contract.md) — contrato único de `AGENTS.md` y su apunte al registry operativo instalado.
- [../prd/prd-001-one-shot-codex-scaffolder.md](../prd/prd-001-one-shot-codex-scaffolder.md) — PRD 1 (autoridad de requisitos; §11 registry manual y verificación).
- [orchestrator.md](../architecture/orchestrator.md) — selección conceptual vs resolución runtime.
- [domain-harness-boundary.md](../architecture/domain-harness-boundary.md) — autoridad de arquitectura vs disponibilidad runtime.
