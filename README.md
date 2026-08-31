# Systems Engineering Framework Agent

Producto que empaqueta en un único repositorio **el marco de ingeniería de sistemas y el agente que lo ejecuta**, y lo distribuye como paquete Python (`se-agent`, Python `>=3.12`) instalable con `pipx` desde el ZIP expuesto por un tag SemVer inmutable de GitHub. Sin PyPI y sin EXE portátil en el MVP.

**Autoridad de requisitos: [PRD 1](docs/prd/prd-001-one-shot-codex-scaffolder.md)** (`se-agent`: scaffolder one-shot para Codex, aprobado).

## Modelo del producto

- **Scaffolder one-shot.** `se-agent init --harness codex --target .` instala el payload declarado en el proyecto destino y termina. Los archivos instalados pasan a ser **100 % propiedad del consumidor**; no hay manifiesto, hashes, `.framework-agent/`, `update`, `doctor`, `uninstall`, migraciones, copias gestionadas ni detección de deriva. El ciclo de vida gestionado queda como **propuesta futura**, no como comportamiento parcial del MVP.
- **Comandos en MVP:** `se-agent init --harness codex --target .` y `se-agent --version` únicamente.
- **Frontera de escritura estricta.** Solo los archivos del payload (PRD 1, §7) se crean o sobrescriben; preflight calcula destinos y colisiones antes de la primera escritura; `proyecto/` es intocable, incluso con `--force`. Interactivo: `[y/N]` ante colisiones; no interactivo: requiere `--force`. Se rechazan escapes por `..` y symlinks fuera del destino.
- **Registry manual.** `runtime/catalogo/skill-registry.md` se mantiene **a mano**; CI/tests verifican coherencia bidireccional (nombres, rutas, duplicados, faltantes, obsoletos) y nunca generan ni modifican el registry.
- **Slice vertical de Codex.** Solo Codex en el MVP; el dominio y los contratos runtime permanecen harness-neutral. Una skill F0 funcional (implementación pendiente).

## Qué integra

- el marco de ingeniería de sistemas (`framework/marco/`, instalado como `marco/`);
- el contrato runtime del agente (`runtime/AGENTS.md`, instalado como `AGENTS.md` de raíz);
- la **arquitectura de capacidades** (`framework/guias/skill-architecture.md`): qué asistencia existe, cuándo aplica y qué guardas la limitan; base de diseño, **no** se instala;
- el **registry operativo** (`runtime/catalogo/skill-registry.md`, bootstrap con 0 skills): inventario **mantenido a mano**, instalado como copia exacta en `catalogo/skill-registry.md`;
- las skills ejecutables (`runtime/skills/` → `.agents/skills/`; poblado de la skill F0 **pendiente**);
- los contratos runtime harness-neutral (`runtime/agents/`, sin destino de instalación definido en el MVP) y el adaptador Codex (`adapters/codex/`, artefactos **pendientes** de crear).

## Árbol

```text
framework/
├── marco/                     # dominio canónico → se instala como marco/
└── guias/                     # base de diseño; NO se instala en consumidores
    ├── skill-architecture.md  # arquitectura de capacidades (autoridad de significado)
    └── project-init.md        # guía de arranque (curada desde el histórico)
runtime/
├── AGENTS.md                  # única fuente del contrato instalable (no hay AGENTS.md en raíz)
├── skills/                    # → .agents/skills/ (skill F0 funcional pendiente)
├── agents/                    # contratos runtime harness-neutral
└── catalogo/
    └── skill-registry.md      # registry operativo (bootstrap 0 skills, manual) → catalogo/skill-registry.md
adapters/
└── codex/                     # lo específico de Codex (artefactos pendientes de crear)
installer/
└── windows/                   # OBSOLETO: enfoque EXE portátil retirado por PRD 1
tests/
├── unit/
├── integration/
└── fixtures/
release/                       # fuentes de publicación
docs/
├── architecture/
├── decisions/
├── guides/
├── prd/
└── history/                   # deprecated, histórico, no autoritativo
dist/                          # outputs generados, no versionados
```

## Autoridad

- **Requisitos de producto**: [PRD 1](docs/prd/prd-001-one-shot-codex-scaffolder.md) (aprobado; define el MVP).
- **Arquitectura y topología**: `docs/architecture/product.md` (v3.0 adoptada, conciliada con PRD 1).
- **Contrato de runtime**: `runtime/AGENTS.md` — no existe `AGENTS.md` en la raíz del producto.
- **Arquitectura de capacidades**: `framework/guias/skill-architecture.md`.
- **Registry operativo**: `runtime/catalogo/skill-registry.md` (bootstrap con 0 skills; mantenido a mano, verificación de coherencia en CI).
- **Índice técnico del harness**: `.atl/skill-registry.md` (solo desarrollo; no se empaqueta ni instala).
- **Histórico**: `docs/history/` es deprecated y no autoritativo.

## Estado

La reestructuración física al árbol por capas **está ejecutada**. PRD 1 está **aprobado** y la documentación activa fue conciliada con él. Pendiente de implementación: el paquete/CLI `se_agent`, el payload de publicación (tag SemVer → ZIP pipx), la skill F0 funcional (`runtime/skills/` y entradas del registry), los artefactos del adaptador Codex (`adapters/codex/`) y las verificaciones de CI (registry ↔ skills, frontera de escritura). Ver [PRD 1, §12](docs/prd/prd-001-one-shot-codex-scaffolder.md) y [docs/architecture/product.md](docs/architecture/product.md).

## Alcance del MVP

El producto escribe únicamente el payload declarado (PRD 1, §7): `marco/`, `AGENTS.md`, `catalogo/skill-registry.md`, `.agents/skills/`, `.codex/`. Nunca modifica los datos de proyecto (`proyecto/`), ni ningún archivo fuera del write-set, ni siquiera con `--force`. Tras `init` exitoso, todo lo instalado es del consumidor.
