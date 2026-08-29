# Systems Engineering Framework Agent

Producto que empaqueta en un único repositorio **el marco de ingeniería de sistemas y el agente que lo ejecuta**, y lo distribuye como ejecutable portátil de Windows vía GitHub Releases.

## Qué integra

- el marco de ingeniería de sistemas (`framework/marco/`, instalado como `marco/`);
- el contrato runtime del agente (`runtime/AGENTS.md`, instalado como `AGENTS.md` de raíz);
- la **arquitectura de capacidades** (`framework/guias/skill-architecture.md`): qué asistencia existe, cuándo aplica y qué guardas la limitan; base de diseño, **no** se instala;
- el **registry operativo** (`runtime/catalogo/skill-registry.md`, bootstrap con 0 skills): inventario generado de skills disponibles, instalado read-only como `catalogo/skill-registry.md`;
- las skills ejecutables (`runtime/skills/` → `.agents/skills/`, vacío por ahora);
- los contratos runtime harness-neutral (`runtime/agents/`) y el adaptador Codex (`adapters/codex/`);
- el instalador y actualizador para Windows (`installer/windows/`, implementación pendiente).

## Árbol

```text
framework/
├── marco/                     # dominio canónico → se instala como marco/
└── guias/                     # base de diseño; NO se instala en consumidores
    ├── skill-architecture.md  # arquitectura de capacidades (autoridad de significado)
    └── project-init.md        # guía de arranque (curada desde el histórico)
runtime/
├── AGENTS.md                  # única fuente del contrato instalable (no hay AGENTS.md en raíz)
├── skills/                    # → .agents/skills/ (vacío por ahora)
├── agents/                    # contratos runtime harness-neutral
└── catalogo/
    └── skill-registry.md      # registry operativo (bootstrap 0 skills) → catalogo/skill-registry.md (read-only)
adapters/
└── codex/                     # lo específico de Codex
installer/
└── windows/                   # init/update/doctor/version + empaquetado portable (pendiente)
tests/
├── unit/
├── integration/
└── fixtures/
release/                       # fuentes de manifiesto/hashes/notas/config de publicación
docs/
├── architecture/
├── decisions/
├── guides/
└── history/                   # deprecated, histórico, no autoritativo
dist/                          # outputs generados, no versionados
```

## Autoridad

- **Arquitectura y topología**: `docs/architecture/product.md` (v2.2 adoptada).
- **Contrato de runtime**: `runtime/AGENTS.md` — no existe `AGENTS.md` en la raíz del producto.
- **Arquitectura de capacidades**: `framework/guias/skill-architecture.md`.
- **Registry operativo**: `runtime/catalogo/skill-registry.md` (bootstrap con 0 skills; generador/CI pendiente), instalado read-only como `catalogo/skill-registry.md`.
- **Índice técnico del harness**: `.atl/skill-registry.md` (solo desarrollo; no se empaqueta ni instala).
- **Histórico**: `docs/history/` es deprecated y no autoritativo.

## Estado

La reestructuración física al árbol por capas **está ejecutada**: el repositorio ya no contiene el árbol plano transitorio (`AGENTS.md` raíz, `marco/`, `catalogo/`, `adapter/`, `agent/`, `skills/`, `manifest/`). Siguen pendientes de implementación: poblado de `runtime/skills/`, generador/CI del registry, comandos `init`/`update`/`doctor`/`version`, adaptador Codex, pruebas de comportamiento y publicación del EXE. Ver [docs/architecture/product.md](docs/architecture/product.md), sección 12.

## Alcance del MVP

El producto administra únicamente su superficie instalada: `marco/`, `AGENTS.md`, `catalogo/skill-registry.md`, `.agents/skills/`, `.codex/` y `.framework-agent/` (manifiesto y hashes). Nunca modifica los datos de proyecto (`proyecto/`). Integridad por SHA-256, transacción fail-closed y sin submódulos.
