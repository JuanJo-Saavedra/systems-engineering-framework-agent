---
document_type: arquitectura
language: es
version: 0.2
status: propuesta
---
# Arquitectura del orquestador

## Propósito

Definir el arnés objetivo: un orquestador **harness-neutral** con Codex como primer adaptador. El dominio de ingeniería de sistemas (`marco/`, `proyecto/`) no depende de ningún harness; los adaptadores traducen contratos canónicos a artefactos ejecutables.

## Principio rector

> El dominio define **qué** se hace. El catálogo define **qué asistencia** existe. El harness define **cómo** se ejecuta. Ninguna capa inferior puede redefinir el significado de la superior.

## Capas y responsabilidades

| Capa                      | Ubicación                             | Responsabilidad                                |
| ------------------------- | -------------------------------------- | ---------------------------------------------- |
| Dominio (marco)           | `marco/`                             | Proceso, fases, reviews, baselines, glosario   |
| Instancia de proyecto     | `proyecto/` (en el proyecto destino) | Estado, hitos y registros autoritativos        |
| Catálogo de capacidades  | `guias/skill-registry.md`            | Qué asistencia existe y cuándo usarla        |
| Contratos canónicos      | fuente harness-neutral                 | Contrato entre dominio y ejecución            |
| Skills de fase            | `implementacion/skills/` (contratos ejecutables) | Procedimiento operativo por capacidad          |
| Orquestador padre         | sesión padre                          | Leer estado, elegir skill, delegar, escribir   |
| Subagentes                | subagentes                             | Trabajo aislado o paralelo acotado             |
| Adaptador Codex           | `implementacion/adapters/codex/`       | Traducir contratos →`.agents/`, `.codex/` |
| Integraciones MCP         | MCP                                    | Herramientas y memoria                         |
| Memoria dual              | Markdown + Engram + RAG                | Persistencia autoritativa y suplementaria      |
| Pruebas de comportamiento | `implementacion/tests/`                | Validar selección, degradación y fronteras   |

## Diagrama de capas

```text
                    ┌────────────────────────────────────────┐
                    │          Dominio (marco/)              │
                    │   fases · reviews · baselines          │
                    └───────────────────┬────────────────────┘
                                        │ define significado
                    ┌───────────────────▼────────────────────┐
                    │  Catálogo (guias/skill-registry.md)    │
                    │  capacidades + cuándo usarlas          │
                    └───────────────────┬────────────────────┘
                                        │ selecciona
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

| Responsabilidad                       | Quién la cumple             |
| ------------------------------------- | ---------------------------- |
| Exponer metadata de skill             | Adaptador Codex              |
| Leer estado autoritativo del proyecto | Orquestador padre            |
| Seleccionar la skill de fase correcta | Orquestador padre            |
| Cargar/ejecutar la skill              | Harness (inline o subagente) |

> No reclamar que Codex "evalúa triggers de fase nativamente". El padre lee `proyecto/estado/*` y elige la capacidad vía `skill-registry.md`; el harness solo ejecuta la skill ya seleccionada.

## Asignación de capacidades

| Tipo de capacidad           | Default | Promoción a subagente solo si…                                                                                 |
| --------------------------- | ------- | ---------------------------------------------------------------------------------------------------------------- |
| Asistencia de fase          | Skill   | — (es skill, no agente por defecto)                                                                             |
| Transversal / tarea puntual | Inline  | hay aislamiento de contexto, especialización, frontera de herramienta segura o trabajo paralelo de solo lectura |

Candidatos iniciales de subagente (sin declarar subagente a toda capacidad transversal):

- `scout` / `context-builder` para exploración pesada de contexto.
- Un `worker` acotado para escritura de un artefacto.
- Un agente de solo lectura para gap/review que devuelva salida estructurada.

> Un agente de solo lectura devuelve salida estructurada al padre; un runner externo la captura. **No** se le exige escribir un archivo de reporte.

## Árbol fuente vs runtime instalado

Separar los contratos fuente harness-neutral de los artefactos Codex generados/copiados. Existe **un único** contrato de runtime (`AGENTS.md`); el desarrollo del arnés es externo a la plantilla de runtime, se describe como estructura de implementación futura en `implementacion/` y no es una elección que el orquestador deba hacer durante la operación.

```text
fuente (harness-neutral)                     runtime instalado (Codex, proyecto destino)
├── guias/ (guías operativas y catálogo)    ├── .agents/skills/<skill>/SKILL.md
└── implementacion/ (estructura futura)     ├── .codex/agents/*.toml
    ├── arquitectura/                       ├── .codex/config.toml
    ├── adapters/codex/ (plantillas)        └── AGENTS.md (runtime, adaptado)
    ├── skills/ (contratos ejecutables)
    └── tests/
```

> Estructura ilustrativa de la implementación futura; los nombres exactos se fijan al implementar el adaptador.

## Hechos de Codex (a confirmar en cada versión)

| Concepto                   | Ubicación / regla                                    |
| -------------------------- | ----------------------------------------------------- |
| Skills de repo             | `.agents/skills/<skill>/SKILL.md`                   |
| Agentes de proyecto        | `.codex/agents/*.toml`                              |
| Configuración de proyecto | `.codex/config.toml`                                |
| Guía persistente          | `AGENTS.md`                                         |
| Herencia                   | Los agentes heredan los settings omitidos             |
| Agente custom mínimo      | `name`, `description`, `developer_instructions` |

Restricciones de herramientas built-in: **no asumir** un allowlist genérico en el TOML salvo que la documentación oficial indique una clave específica. Para aislar herramientas, usar sandbox, settings MCP por agente y habilitar/deshabilitar tools MCP. Mantenerlo como una preocupación abierta del adaptador.

## Slice vertical mínimo

1. Un contrato de fase canónico (ej. `F0`).
2. Una skill de fase traducida a `.agents/skills/`.
3. Un adaptador que genere `.codex/config.toml` + un agente.
4. Un test de comportamiento: dado estado `preproyecto_presupuesto` y fase `F0`, el padre selecciona `f0_factibilidad`.

## Validación por comportamiento

- Test de selección de ruta: estado → capacidad.
- Test de fallo cerrado ante estado ausente o corrupto.
- Test de degradado sin Engram/RAG.
- Test de frontera: ningún artefacto Codex reescribe dominio.

Ver [frontera-dominio-harness.md](frontera-dominio-harness.md) y [memoria-dual.md](memoria-dual.md).

## Relacionado

- [quickstart-agentes.md](quickstart-agentes.md) — flujo mínimo.
- [frontera-dominio-harness.md](frontera-dominio-harness.md) — autoridad y dependencias.
- [memoria-dual.md](memoria-dual.md) — persistencia.
- [reestructuracion-agents.md](reestructuracion-agents.md) — decisión canónica: contrato único de `AGENTS.md`.
- [skill-registry.md](skill-registry.md) — catálogo canónico.
