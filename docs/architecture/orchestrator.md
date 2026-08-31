---
document_type: arquitectura
language: es
version: 0.3
status: propuesta
---
# Arquitectura del orquestador

> Conciliada con [PRD 1](../prd/prd-001-one-shot-codex-scaffolder.md) (aprobado): el producto es el paquete Python `se_agent` (CLI `se-agent`), scaffolder one-shot; el enfoque `installer/windows/` quedó obsoleto y el registry operativo se mantiene a mano con verificación CI.

## Propósito

Definir el arnés objetivo: un orquestador **harness-neutral** con Codex como primer adaptador. El dominio de ingeniería de sistemas (`framework/marco/`, instalado como `marco/`) y la instancia de proyecto (`proyecto/`) no dependen de ningún harness; los adaptadores traducen contratos canónicos a artefactos ejecutables.

## Principio rector

> El dominio define **qué** se hace. La arquitectura de capacidades define **qué asistencia** existe. El registry operativo define **qué skill** está disponible. El harness define **cómo** se ejecuta. Ninguna capa inferior puede redefinir el significado de la superior.

## Capas y responsabilidades

| Capa                        | Ubicación                                                                          | Responsabilidad                                                          |
| --------------------------- | ---------------------------------------------------------------------------------- | ------------------------------------------------------------------------ |
| Dominio (marco)             | `framework/marco/` (instalado como `marco/`)                                       | Proceso, fases, reviews, baselines, glosario                             |
| Instancia de proyecto       | `proyecto/` (en el proyecto destino)                                               | Estado, hitos y registros autoritativos                                  |
| Arquitectura de capacidades | `framework/guias/skill-architecture.md`                                            | Qué asistencia existe y cuándo usarla (diseño)                           |
| Registry operativo          | `runtime/catalogo/skill-registry.md` (instalado como `catalogo/skill-registry.md`) | Qué skill está disponible en runtime (mantenido a mano; verificación CI) |
| Contratos canónicos         | fuente harness-neutral                                                             | Contrato entre dominio y ejecución                                       |
| Skills de fase              | `runtime/skills/` (contratos ejecutables)                                          | Procedimiento operativo por capacidad                                    |
| Orquestador padre           | sesión padre                                                                       | Leer estado, elegir skill, delegar, escribir                             |
| Subagentes                  | subagentes                                                                         | Trabajo aislado o paralelo acotado                                       |
| Adaptador Codex             | `adapters/codex/`                                                                  | Traducir contratos →`.agents/`, `.codex/`                                |
| Integraciones MCP           | MCP                                                                                | Herramientas y memoria                                                   |
| Memoria dual                | Markdown + Engram + RAG                                                            | Persistencia autoritativa y suplementaria                                |
| Pruebas de comportamiento   | `tests/{unit,integration,fixtures}`                                                | Validar selección, degradación y fronteras                               |

## Diagrama de capas

```text
                    ┌────────────────────────────────────────┐
                    │       Dominio (framework/marco/)        │
                    │   fases · reviews · baselines          │
                    └───────────────────┬────────────────────┘
                                        │ define significado
                    ┌───────────────────▼────────────────────┐
                    │  Arquitectura de capacidades            │
                    │  framework/guias/skill-architecture.md  │
                    │  capacidades + cuándo usarlas (diseño)  │
                    └───────────────────┬────────────────────┘
                                        │ guía la selección
                    ┌───────────────────▼────────────────────┐
                    │  Registry operativo                     │
                    │  runtime/catalogo/skill-registry.md     │
                    │  skills disponibles (runtime)           │
                    └───────────────────┬────────────────────┘
                                        │ resuelve/carga
                    ┌───────────────────▼────────────────────┐
                    │        Orquestador padre               │
                    │  lee estado → elige skill → delega     │
                    └───────┬───────────────────┬────────────┘
                            │                   │
              ┌─────────────▼────────┐   ┌──────▼──────────────┐
              │ Skills de fase       │   │ Subagentes          │
              │ (procedimiento)      │   │ (aislamiento)       │
              └─────────────┬────────┘   └──────┬──────────────┘
                            │                   │
              ┌─────────────▼───────────────────▼──────────────┐
              │  Adaptador Codex (harness-neutral → Codex)     │
              │  .agents/skills · .codex/agents · config.toml  │
              └─────────────┬──────────────────────────────────┘
                            │
              ┌─────────────▼──────────────────────────────────┐
              │  MCP: Engram (memoria) · RAG (recuperación)    │
              └────────────────────────────────────────────────┘
```

## Carga de skills dirigida por estado

Codex usa **progressive disclosure**: expone la metadata de una skill para que el agente decida si cargarla. Eso **no** significa que Codex evalúe nativamente los disparadores de fase de un YAML.

| Responsabilidad                       | Quién la cumple              |
| ------------------------------------- | ---------------------------- |
| Exponer metadata de skill             | Adaptador Codex              |
| Leer estado autoritativo del proyecto | Orquestador padre            |
| Seleccionar la skill de fase correcta | Orquestador padre            |
| Cargar/ejecutar la skill              | Harness (inline o subagente) |

> No reclamar que Codex "evalúa triggers de fase nativamente". El padre lee `proyecto/estado/*` y elige la capacidad según la arquitectura de capacidades (`framework/guias/skill-architecture.md`, durante el diseño); en runtime resuelve/carga la skill solo desde el registry operativo (`runtime/catalogo/skill-registry.md`) + metadata del harness. El harness solo ejecuta la skill ya seleccionada.

## Asignación de capacidades

| Tipo de capacidad           | Default | Promoción a subagente solo si…                                                                                   |
| --------------------------- | ------- | ---------------------------------------------------------------------------------------------------------------- |
| Asistencia de fase          | Skill   | — (es skill, no agente por defecto)                                                                              |
| Transversal / tarea puntual | Inline  | hay aislamiento de contexto, especialización, frontera de herramienta segura o trabajo paralelo de solo lectura  |

Candidatos iniciales de subagente (sin declarar subagente a toda capacidad transversal):

- `scout` / `context-builder` para exploración pesada de contexto.
- Un `worker` acotado para escritura de un artefacto.
- Un agente de solo lectura para gap/review que devuelva salida estructurada.

> Un agente de solo lectura devuelve salida estructurada al padre; un runner externo la captura. **No** se le exige escribir un archivo de reporte.

## Árbol fuente vs runtime instalado

Separar los contratos fuente harness-neutral de los artefactos Codex instalados. Existe **un único** contrato de runtime (`runtime/AGENTS.md`, instalado como `AGENTS.md`); el desarrollo del arnés es externo a la plantilla de runtime, se describe como estructura de implementación futura en `runtime/agents/`, `adapters/codex/` y el paquete `se_agent`, y no es una elección que el orquestador deba hacer durante la operación.

```text
fuente (harness-neutral, repo de producto)        runtime instalado (Codex, proyecto destino)
├── framework/marco/ (dominio)                  ├── marco/ (desde framework/marco/)
├── framework/guias/skill-architecture.md       │   (no se instala)
│   (arquitectura de capacidades; diseño)       │
├── runtime/catalogo/skill-registry.md          ├── catalogo/skill-registry.md (copia exacta, propiedad del consumidor)
├── runtime/                                    ├── .agents/skills/<skill>/SKILL.md (desde runtime/skills/)
│   ├── AGENTS.md (contrato instalable)         ├── .codex/agents/*.toml (desde adapters/codex/)
│   ├── skills/ (contratos ejecutables)         ├── .codex/config.toml (desde adapters/codex/)
│   └── agents/ (contratos harness-neutral)     └── AGENTS.md (instalado, desde runtime/AGENTS.md)
├── adapters/codex/ (plantillas)
├── se_agent/ (paquete del scaffolder; implementación pendiente)
└── tests/{unit,integration,fixtures}
```

> Las rutas del lado fuente son las rutas vigentes del repositorio (reestructuración ejecutada). Ver [product.md](product.md). Los nombres exactos de implementación se fijan al implementar el adaptador.

## Hechos de Codex (a confirmar en cada versión)

| Concepto                   | Ubicación / regla                                     |
| -------------------------- | ----------------------------------------------------- |
| Skills de repo             | `.agents/skills/<skill>/SKILL.md`                     |
| Agentes de proyecto        | `.codex/agents/*.toml`                                |
| Configuración de proyecto  | `.codex/config.toml`                                  |
| Guía persistente           | `AGENTS.md`                                           |
| Herencia                   | Los agentes heredan los settings omitidos             |
| Agente custom mínimo       | `name`, `description`, `developer_instructions`       |

Restricciones de herramientas built-in: **no asumir** un allowlist genérico en el TOML salvo que la documentación oficial indique una clave específica. Para aislar herramientas, usar sandbox, settings MCP por agente y habilitar/deshabilitar tools MCP. Mantenerlo como una preocupación abierta del adaptador.

## Slice vertical mínimo

El slice vertical del MVP está definido en [PRD 1](../prd/prd-001-one-shot-codex-scaffolder.md) (§3, §10). En términos de este documento:

1. Un contrato de fase canónico (ej. `F0`) y una skill F0 **funcional** en `runtime/skills/` (implementación pendiente).
2. Los artefactos del adaptador en `adapters/codex/` (`.codex/config.toml` + agentes; por crear).
3. `se-agent init --harness codex --target .` instala el payload one-shot (paquete `se_agent`; implementación pendiente).
4. Un test de comportamiento: dado estado `preproyecto_presupuesto` y fase `F0`, el padre selecciona `f0_factibilidad`.

## Validación por comportamiento

- Test de selección de ruta: estado → capacidad.
- Test de fallo cerrado ante estado ausente o corrupto.
- Test de degradado sin Engram/RAG.
- Test de frontera: ningún artefacto Codex reescribe dominio.

Ver [domain-harness-boundary.md](domain-harness-boundary.md) y [memory.md](memory.md).

## Relacionado

- [quickstart.md](../guides/quickstart.md) — flujo mínimo.
- [domain-harness-boundary.md](domain-harness-boundary.md) — autoridad y dependencias.
- [memory.md](memory.md) — persistencia.
- [agents-contract.md](../decisions/agents-contract.md) — decisión canónica: contrato único de `AGENTS.md`.
- [skill-artifacts.md](../decisions/skill-artifacts.md) — arquitectura de capacidades vs registry operativo.
- [skill-architecture.md](../../framework/guias/skill-architecture.md) — arquitectura de capacidades.
