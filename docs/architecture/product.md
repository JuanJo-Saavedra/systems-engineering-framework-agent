---
document_type: arquitectura_producto
language: es
version: 3.0
status: adoptada
---

# Arquitectura del producto `systems-engineering-framework-agent`

## Decisión ejecutiva

**PRD 1 ([`docs/prd/prd-001-one-shot-codex-scaffolder.md`](../prd/prd-001-one-shot-codex-scaffolder.md), aprobado) define el MVP.** Esta v3.0 concilia la arquitectura con ese PRD y **supersede la v2.2** en todo lo que contradiga: distribución, comandos, propiedad de archivos instalados y modelo del registry.

El producto se distribuye como **paquete Python `se_agent` (CLI `se-agent`, Python `>=3.12`) instalable con `pipx` desde el ZIP expuesto por un tag SemVer inmutable de GitHub**. Sin PyPI y sin EXE portátil en el MVP. Es un **scaffolder one-shot**: `se-agent init --harness codex --target .` escribe exactamente el payload declarado (PRD 1, §7) y termina. Los archivos instalados son **100 % propiedad del consumidor** desde el momento posterior a `init`: no hay manifiesto, hashes, `.framework-agent/`, `update`, `doctor`, `uninstall`, migraciones, copias gestionadas ni detección de deriva. El ciclo de vida gestionado queda registrado como **propuesta futura**, no como comportamiento parcial del MVP.

El producto **nunca** accede ni modifica `proyecto/`, sus registros, hitos, entregables, evidencia ni esquemas de proyecto. `framework/guias/` **no** se instala en consumidores: es base de diseño, comportamiento y accionamiento del producto. El repositorio `proyecto-base` no es fuente canónica del marco: es un **fixture de consumo y aceptación** con copias instaladas propiedad del consumidor.

| Punto | Decisión adoptada |
| --- | --- |
| Autoridad de requisitos | PRD 1 aprobado ([`docs/prd/prd-001-one-shot-codex-scaffolder.md`](../prd/prd-001-one-shot-codex-scaffolder.md)); este documento concilia la arquitectura con él. |
| Producto/CLI | `se-agent`; módulo Python `se_agent`; Python `>=3.12` (implementación pendiente). |
| Distribución | `pipx` instala el ZIP del tag SemVer inmutable de GitHub. Sin PyPI, sin EXE portátil. Tag, versión del paquete y `se-agent --version` coinciden. |
| Modelo de instalación | One-shot. `init` escribe el payload (PRD 1, §7) y termina; lo instalado es del consumidor. |
| Comandos en MVP | `se-agent init --harness codex --target .` y `se-agent --version`. Nada más. |
| Manifiesto / hashes / `update` / `doctor` / `uninstall` / migraciones / deriva / generador de registry | **Ninguno existe en el MVP.** Ciclo de vida gestionado = propuesta futura. |
| Frontera de escritura | Solo el payload de §7 del PRD. Preflight completo antes de la primera escritura; colisiones `[y/N]` en interactivo, `--force` en no interactivo; `--force` no escapa del write-set; `proyecto/` intocable siempre; se rechazan escapes por `..` y symlinks. |
| Registry operativo | `runtime/catalogo/skill-registry.md`, **mantenido a mano** por los autores del producto. CI/tests verifican coherencia bidireccional con `runtime/skills/` y nunca generan ni modifican el registry. |
| Árbol de implementación | Árbol por capas ejecutado: `framework/`, `runtime/`, `adapters/codex/`, `tests/{unit,integration,fixtures}`, `release/`, `docs/`. |
| Dominio canónico | `framework/marco/`; se instala como `marco/`. |
| Guías canónicas del framework | `framework/guias/`; **no** se instalan en consumidores. |
| Arquitectura de capacidades | `framework/guias/skill-architecture.md` (autoridad de significado conceptual; separada del registry operativo). |
| Contrato instalable | `runtime/AGENTS.md` es la **única** fuente; no hay `AGENTS.md` en raíz del repo de producto; en el consumidor se instala como `AGENTS.md` de raíz. |
| Skills | `runtime/skills/` → `.agents/skills/`. **Implementación pendiente**: exactamente una skill F0 funcional en el MVP. |
| Contratos runtime harness-neutral | `runtime/agents/`. Sin destino de instalación definido en el MVP (seguimiento abierto, PRD 1 §12); no se instala. |
| Específico de Codex | `adapters/codex/` (`.codex/config.toml`, `.codex/agents/*.toml`). Artefactos **por crear**; exponen mecanismos, nunca reglas de dominio. |
| Instalador | El enfoque `installer/windows/` (comandos y empaquetado portable EXE) quedó **obsoleto** con PRD 1; lo sustituye el paquete Python `se_agent`. |
| Tests | `tests/{unit,integration,fixtures}` (estructura creada; pruebas de comportamiento pendientes). |
| Publicación | `release/` contiene fuentes de publicación; el artefacto de distribución es el ZIP del tag (fuente automática de GitHub). Sin manifiesto ni hashes de release. |
| Histórico | `docs/history/` completo es deprecated, histórico, no autoritativo y no participa en generación. |
| Write-set instalado | `marco/`, `AGENTS.md` raíz, `catalogo/skill-registry.md`, `.agents/skills/`, `.codex/` (PRD 1, §7). |
| Superficie prohibida | `proyecto/`, registros, hitos, entregables, evidencia, esquemas de proyecto; todo archivo fuera del write-set. |
| Submódulos | No se usan. |
| `proyecto-base` | Fixture de consumo y aceptación, no fuente canónica. |

## Propósito

Este documento es el handoff de arquitectura para el repositorio `systems-engineering-framework-agent`. Fija qué se construye, qué se instala y qué queda fuera, y registra la frontera que impide que la herramienta toque datos de proyecto. La v2.0 adoptó la **topología por capas**; la v2.1 añadió la separación entre **arquitectura de capacidades** y **registry operativo**; la v2.2 registró la reestructuración física ejecutada; la **v3.0 concilia la arquitectura con PRD 1 aprobado** (scaffolder one-shot, distribución pipx, propiedad del consumidor, registry manual).

## Autoridad y ruta de revisión

- **Autoridad de requisitos**: PRD 1, aprobado. Este documento registra la arquitectura conciliada con él; no reabre decisiones del PRD.
- **Estado**: `adoptada` (v3.0). Supersede la v2.2 y anteriores en lo que contradiga PRD 1. Cambios posteriores se tramitan por revisión normal del repositorio de producto.
- **Ruta de revisión**: los artefactos de implementación que se deriven (paquete `se_agent`, payload del adaptador, verificaciones de CI) se revisan contra PRD 1 y este documento.
- **Qué revisar primero**: la decisión ejecutiva, la separación arquitectura de capacidades vs registry operativo (sección 3 y `docs/decisions/skill-artifacts.md`), la topología (sección 4), los árboles fuente e instalado (sección 5), la frontera de escritura y propiedad (sección 6), los riesgos (sección 13) y los pendientes de implementación (sección 14).

## 1. Contexto: tres subsistemas y alcance del MVP

El sistema completo se compone de tres subsistemas con responsabilidades distintas. El MVP cubre **solo** los dos primeros.

| Subsistema | Ubicación lógica | Responsabilidad | ¿En el MVP? |
| --- | --- | --- | --- |
| Framework (dominio) | `framework/marco/` (instalado como `marco/`) | Proceso de ingeniería: fases `F0`–`F8`, reviews, baselines, glosario, reglas. | Sí (empaquetado en el payload). |
| Agente/runtime Codex | `runtime/` + `adapters/codex/` (instalados por `se-agent`) | Contrato, skills y artefactos que Codex usa para ejecutar el proceso; el scaffolder solo los instala. | Sí (implementación pendiente). |
| Proyecto consumidor | `proyecto/` en el destino | Instancia viva: estado, hitos, registros, entregables, evidencia. | No (es el fixture de aceptación; el producto no lo gestiona). |

> El producto `systems-engineering-framework-agent` reúne **framework + runtime/agente + scaffolder `se-agent`**. El proyecto consumidor no se empaqueta ni se migra; el producto lo respeta como intocable durante `init` (y en cualquier otro comando, porque solo existen `init` y `--version`).

## 2. Alcance del producto y no-objetivos

### Alcance (MVP, según PRD 1)

- Paquete Python `se_agent` con CLI `se-agent`, distribuible vía `pipx` (ZIP del tag de GitHub).
- Payload completo del marco + dominio instalado en el destino (PRD 1, §7).
- Contrato `AGENTS.md` canónico instalado en la raíz del destino.
- Registry de skills mantenido manualmente, con verificación de coherencia bidireccional en CI.
- Una skill F0 **funcional** en runtime.
- Artefactos del adaptador Codex (`.codex/config.toml`, `.codex/agents/*.toml`) instalados en `.codex/`.
- Protocolo de colisiones, frontera de escritura estricta y preflight antes de la primera escritura.

### No-objetivos (fuera del MVP)

- RAG, SharePoint y Power Automate.
- Migraciones de proyectos existentes.
- Gestionar o modificar `proyecto/` o cualquier dato de proyecto.
- Submódulos de Git.
- Manifiesto, hashes SHA-256, `.framework-agent/`, `update`, `doctor`, `uninstall`, detección de deriva, copias gestionadas read-only.
- Generador del registry (comando de build); el registry se edita a mano y CI solo verifica.
- CI que modifica el repositorio.
- PyPI y EXE portátil de Windows.
- Más de un harness: el dominio y los contratos runtime son harness-neutral, pero el único adaptador es Codex.

## 3. Capas y dirección de dependencias

El dominio define **qué** se hace; el agente define **cómo** se ejecuta; el proyecto consumidor contiene los **hechos**. La dependencia apunta hacia abajo: lo inferior puede depender de lo superior, nunca al revés.

```text
dominio (framework/marco/ + framework/guias/skill-architecture.md)
   ↑ autoridad de significado
contrato de runtime (runtime/AGENTS.md) + contratos harness-neutral (runtime/agents/)
   ↑ comportamiento portable
registry operativo (runtime/catalogo/skill-registry.md, mantenido a mano)
   ↑ disponibilidad de skills instaladas
adaptador Codex (adapters/codex/ → skills · agentes · config)
   ↑ traducción a artefactos ejecutables
scaffolder se-agent (paquete se_agent/ → instalación one-shot del payload)
   ↑ ejecución acotada al write-set
write-set instalado, propiedad del consumidor (marco/ · AGENTS.md · catalogo/skill-registry.md · .agents/ · .codex/)
   ↑ lectura/uso libre
proyecto consumidor (proyecto/) — intocable por la herramienta
```

| Capa | Es autoridad sobre | No es autoridad sobre |
| --- | --- | --- |
| Dominio (`framework/marco/` + `framework/guias/skill-architecture.md`) | Significado del proceso y arquitectura de capacidades | Ejecución, herramientas, disponibilidad runtime |
| Contrato de runtime (`runtime/AGENTS.md`) y contratos harness-neutral (`runtime/agents/`) | Comportamiento portable del agente | Significado del dominio |
| Registry operativo (`runtime/catalogo/skill-registry.md`) | Inventario de skills disponibles y accesibles (mantenido a mano) | Significado del dominio, algoritmo de routing, guardrails |
| Adaptador Codex (`adapters/codex/`) | Artefactos ejecutables Codex | Significado, arquitectura de capacidades |
| Scaffolder `se-agent` | Instalar el write-set declarado, una sola vez | Datos de proyecto, contenido fuera del write-set |
| Proyecto consumidor | Hechos del proyecto | Proceso (lo respeta) |

> El dominio no importa Codex; el adaptador sí importa el dominio. Esta frontera se conserva de `docs/architecture/domain-harness-boundary.md`.

## 4. Topología: repo fuente canónico vs proyecto consumidor instalado

Existen **dos** repositorios con roles distintos, y **una** autoridad de fuente.

| Repo | Rol | Contenido |
| --- | --- | --- |
| `systems-engineering-framework-agent` | Fuente canónica del producto | `framework/` (`marco/` + `guias/`), `runtime/` (`AGENTS.md`, `catalogo/skill-registry.md`, `skills/`, `agents/`), `adapters/codex/`, `tests/`, `release/`, `docs/` (incluye `docs/prd/`). |
| Proyecto destino (p. ej. `proyecto-base`) | Consumidor/instalado | Archivos instalados **propiedad del consumidor** (`marco/`, `AGENTS.md`, `catalogo/skill-registry.md`, `.agents/skills/`, `.codex/`) + `proyecto/` intocable. |

Reglas:

- **Sin submódulos.** El repo de producto es un único repositorio; el consumidor recibe archivos instalados por `se-agent init`, no referencias Git.
- **Una única autoridad de fuente.** El marco, la arquitectura de capacidades, el registry operativo y el contrato de runtime se editan solo en el repo de producto. En el consumidor son archivos instalados; no existe una segunda autoridad editable del producto.
- **Un contrato semántico de runtime.** `runtime/AGENTS.md` (fuente en el repo de producto) y el `AGENTS.md` instalado en el consumidor representan el **mismo** contrato semántico, no dos contratos editados por separado. Tras `init`, la copia es del consumidor; una re-instalación trata las diferencias como colisiones explícitas (PRD 1, §9), no como "deriva" que bloquea nada.
- **Sin `AGENTS.md` en la raíz del producto.** La única fuente del contrato instalable vive en `runtime/AGENTS.md`; el `AGENTS.md` en raíz aparece únicamente como artefacto instalado en el consumidor.

> Nota sobre el diagrama: `docs/history/diagrama-mvp.png` es **ideación histórica** del arnés y contiene preguntas ya resueltas. Queda **superado** donde sus decisiones difieran de PRD 1 y de este documento. No se usa como referencia final.

## 5. Árboles: fuente e instalado

### 5.1 Árbol fuente (vigente)

```text
systems-engineering-framework-agent/
├── framework/
│   ├── marco/                          # dominio canónico → se instala como marco/
│   └── guias/                          # guías canónicas del framework; NO se instalan en consumidores
│       ├── skill-architecture.md       # arquitectura de capacidades (autoridad de significado)
│       └── project-init.md             # guía de arranque (curada desde el histórico)
├── runtime/
│   ├── AGENTS.md                       # única fuente del contrato instalable (no hay AGENTS.md en raíz)
│   ├── skills/                         # skills ejecutables → .agents/skills/<skill>/SKILL.md (skill F0 pendiente)
│   ├── agents/                         # contratos runtime harness-neutral (sin destino de instalación definido)
│   └── catalogo/
│       └── skill-registry.md           # registry operativo (bootstrap 0 skills, manual) → catalogo/skill-registry.md
├── adapters/
│   └── codex/                          # artefactos Codex (por crear): config.toml + agents/*.toml
├── installer/
│   └── windows/                        # OBSOLETO (enfoque EXE portátil retirado por PRD 1)
├── tests/
│   ├── unit/
│   ├── integration/
│   └── fixtures/
├── release/                            # fuentes de publicación (tag SemVer → ZIP)
├── docs/
│   ├── architecture/
│   ├── decisions/
│   ├── guides/
│   ├── prd/                            # PRD 1 (autoridad de requisitos del MVP)
│   └── history/                        # deprecated, histórico, no autoritativo
├── dist/                               # generado, NO versionado
└── .gitignore
```

> `.atl/` (índice técnico del harness) es solo desarrollo, está en `.gitignore` y no forma parte del árbol empaquetado.

> El paquete Python `se_agent` (código de la CLI) no existe todavía; su ubicación interna se define al implementarlo y no altera las rutas canónicas del payload.

### 5.2 Árbol instalado (proyecto destino)

```text
<proyecto-destino>/
├── AGENTS.md                          # instalado (copia exacta de runtime/AGENTS.md; propiedad del consumidor)
├── marco/                             # instalado (copia recursiva de framework/marco/; propiedad del consumidor)
├── catalogo/
│   └── skill-registry.md              # instalado (copia exacta del registry operativo; propiedad del consumidor)
├── .agents/skills/<skill>/SKILL.md    # instalado (desde runtime/skills/; propiedad del consumidor)
├── .codex/agents/*.toml               # instalado (desde adapters/codex/; propiedad del consumidor)
├── .codex/config.toml                 # instalado (desde adapters/codex/; propiedad del consumidor)
└── proyecto/                          # NO gestionado; permanece byte a byte intacto
```

> No existe `.framework-agent/`: PRD 1 elimina el manifiesto y los hashes. No se escribe ningún archivo de estado, caché ni lockfile.

## 6. Frontera de escritura y propiedad

Tras `init` exitoso, el consumidor es dueño absoluto de todo lo instalado. La herramienta no mantiene, vigila ni actualiza nada después.

Reglas duras (PRD 1, §8; verificables por test):

- **Lista blanca.** Solo los destinos del payload (PRD 1, §7) pueden crearse o sobrescribirse: `marco/`, `AGENTS.md`, `catalogo/skill-registry.md`, `.agents/skills/<skill>/SKILL.md`, `.codex/config.toml`, `.codex/agents/*.toml`.
- **Preflight total.** Antes de la primera escritura se calcula y valida el plan completo: destino, resolución segura de rutas, colisiones. Cualquier fallo ⇒ **cero escrituras**.
- **Colisiones.** Interactivo: se listan todas y se pregunta `[y/N]`; cualquier otra respuesta o EOF aborta sin escribir. No interactivo: aborta y sugiere `--force`. Con `--force` se sobrescriben solo las colisiones del write-set.
- **`proyecto/` intocable.** Ninguna operación, en ningún modo (incluido `--force`), crea, modifica ni elimina nada bajo `proyecto/`.
- **Resolución segura.** Se rechaza con error duro: `..` que escape de la raíz destino, rutas absolutas fuera del target y symlinks cuyo objetivo quede fuera del árbol destino.
- **Nunca se elimina ni "ordena"** contenido fuera del write-set.
- **Fallo a mitad de escritura:** la herramienta se detiene en el primer error, no revierte (lo escrito ya es del consumidor), reporta rutas escritas y pendientes, y termina con código distinto de cero.

Superficie prohibida (nunca se accede para escribir):

- `proyecto/` y todo su contenido.
- Registros, hitos, entregables, evidencia y esquemas de proyecto.
- Cualquier archivo fuera del write-set.

## 7. Distribución y comandos

- **Formato**: paquete Python `se_agent` (CLI `se-agent`, Python `>=3.12`), instalable con `pipx` desde el ZIP que GitHub expone automáticamente para cada tag SemVer **inmutable**. **Sin PyPI y sin EXE portátil en el MVP.**
- **Coherencia de versión**: el tag `vX.Y.Z`, la versión de `pyproject.toml` y la salida de `se-agent --version` coinciden.
- **Prerrequisito**: Codex está **preinstalado y autenticado** en la máquina destino; el producto no instala ni autentica Codex. (La versión mínima de Codex queda **por definir**.)
- **Comandos en MVP**:

| Comando | Comportamiento |
| --- | --- |
| `se-agent init --harness codex --target .` | Preflight (destino, rutas, colisiones) e instala el write-set (PRD 1, §7). Sin manifiesto ni estado adicional. |
| `se-agent --version` | Imprime la versión SemVer, idéntica al tag y a `pyproject.toml`. |

- **No existen en el MVP**: `update`, `doctor`, `uninstall`, migraciones, generación de registry. El ciclo de vida gestionado (actualización con copias administradas) queda como **propuesta futura** a tratar en su propio PRD; nada del MVP lo implementa parcialmente.
- La organización/URL real de GitHub queda por definir (seguimiento abierto, PRD 1 §12).

## 8. Publicación

| Artefacto | Rol |
| --- | --- |
| Tag `vX.Y.Z` inmutable | Referencia de versión; el ZIP que GitHub expone automáticamente es el artefacto de instalación vía `pipx`. |
| `NOTES.md` (opcional) | Notas de release. |

No hay manifiesto, ni `hashes.sha256`, ni binario EXE. `release/` conserva las fuentes de notas/configuración de publicación; los outputs generados van a `dist/` y no se versionan.

## 9. Responsabilidad del adaptador Codex y frontera harness-neutral

- **Adaptador**: traduce el contrato de runtime (`runtime/AGENTS.md`) y el registry operativo (`runtime/catalogo/skill-registry.md`) a artefactos Codex (`.agents/skills/`, `.codex/agents/*.toml`, `.codex/config.toml`). Es un mapeo ejecutable, nunca una autoridad de significado. La arquitectura de capacidades (`framework/guias/skill-architecture.md`) guía el diseño; no se empaqueta ni se instala.
- **Separación runtime/adaptador**: `runtime/agents/` contiene contratos runtime **harness-neutral**; `adapters/codex/` contiene solo lo específico de Codex. El dominio no depende de ninguno de los dos.
- **Progressive disclosure**: las skills se cargan en tres niveles — metadata (`name`/`description`), instrucciones (`SKILL.md`) y recursos bajo demanda — para reducir consumo de contexto.
- **Frontera de dominio**: el dominio (`framework/marco/`) permanece harness-neutral. Codex no evalúa disparadores de fase nativamente; el agente lee el estado del proyecto, selecciona la capacidad según la arquitectura de capacidades durante el diseño y, en runtime, resuelve/carga solo desde el registry operativo + metadata/SKILL. Ningún artefacto Codex redefine el dominio.
- **No duplicar reglas de dominio en TOML**: la configuración Codex expone mecanismos, no re-escribe el proceso.

## 10. Slice vertical del MVP

El slice vertical y los criterios de aceptación medibles del MVP están definidos en **PRD 1** (§3, §5, §10) y son la autoridad. Resumen de referencia:

1. Paquete Python `se_agent` con CLI `se-agent`, distribuible vía `pipx`.
2. Payload completo instalado en el destino (PRD 1, §7).
3. Contrato `AGENTS.md` canónico en la raíz del destino.
4. Registry mantenido manualmente + verificación de coherencia bidireccional en CI.
5. Una skill F0 **funcional** (no placeholder), conforme a `framework/guias/skill-architecture.md` (`f0_factibilidad`), `AGENTS.md` y `marco/fases/fase_0_concepto_y_factibilidad.md`.
6. Artefactos del adaptador Codex en `.codex/`.
7. Protocolo de colisiones, frontera de escritura estricta y preflight (PRD 1, §8–9).

La verificación detallada de cada criterio (AC-1…AC-12) vive en PRD 1, §10; este documento no duplica ni altera esa lista.

## 11. Registro de transición ejecutada

La migración plana dejó los activos en el repositorio y la **transición al árbol por capas está ejecutada** (registro histórico conservado de la v2.2). Quedó completado:

- [x] Preservar el trabajo local (sin operaciones destructivas).
- [x] Reubicar el dominio `marco/` → `framework/marco/` y situar las guías canónicas del framework en `framework/guias/` (separadas de `docs/history/`).
- [x] Separar arquitectura de capacidades del registry operativo: `catalogo/skill-registry.md` → `framework/guias/skill-architecture.md`; curar `docs/history/guias/project-init.md` → `framework/guias/project-init.md`. `framework/guias/` **no** se instala en consumidores.
- [x] Crear `runtime/catalogo/skill-registry.md` como bootstrap del registry operativo (0 skills).
- [x] Reubicar el contrato de runtime `AGENTS.md` raíz → `runtime/AGENTS.md`.
- [x] Reorganizar skills y contratos runtime: `skills/` → `runtime/skills/`; `agent/` → `runtime/agents/`.
- [x] Separar lo específico de Codex: `adapter/codex/` → `adapters/codex/`.
- [x] Consolidar publicación en `release/`; outputs generados en `dist/`, no versionados.
- [x] Estructurar tests como `tests/{unit,integration,fixtures}`.
- [x] Marcar `docs/history/` como deprecated/no autoritativo.
- [x] Confirmar sin submódulos: un único repo de producto.

Con PRD 1 aprobado y esta v3.0, quedan además conciliados: distribución pipx/ZIP (sustituye EXE portátil), modelo one-shot con propiedad del consumidor (sustituye copias gestionadas/deriva), registry manual (sustituye registry generado) y write-set sin `.framework-agent/`.

## 12. Recuperación de decisiones desde Engram (bootstrap, en su mayoría ejecutado)

Esta sección registra el procedimiento de traspaso de memoria usado al iniciar este repositorio. Queda como referencia de bootstrap; no es una autoridad sobre las decisiones ya fijadas en PRD 1 y en este documento.

Engram conserva memoria por proyecto. Al abrir `systems-engineering-framework-agent`, el agente no debe asumir que las observaciones guardadas bajo `proyecto-base` aparecerán en el contexto del nuevo repo. El traspaso se realiza como **recuperación curada**, no como una importación ciega ni como sustitución de los documentos versionados.

### Orden de autoridad durante el traspaso

1. PRD 1 y las fuentes Markdown referenciadas son la autoridad.
2. Las observaciones de Engram aportan resumen, justificación y punteros.
3. Si una memoria contradice el Markdown vigente, se informa la discrepancia y prevalece Markdown.
4. Las memorias originales de `proyecto-base` se conservan; no se eliminan ni se trasladan destructivamente.

### Procedimiento de recuperación

Desde una sesión abierta en el nuevo repositorio:

1. Consultar el contexto del proyecto nuevo. Un resultado vacío es esperable y no implica que las memorias históricas se hayan perdido.
2. Buscar explícitamente en el proyecto de origen `proyecto-base` por nombre de producto, decisiones y claves de tema.
3. Si el nombre de proyecto no resuelve o se desconoce, repetir la búsqueda con alcance de todos los proyectos.
4. Recuperar el contenido completo de cada observación seleccionada por su identificador.
5. Contrastar cada memoria con PRD 1 y este documento antes de usarla.
6. Guardar una memoria curada en `systems-engineering-framework-agent`, manteniendo la clave temática estable y registrando la procedencia (`proyecto-base`, ID de observación y ruta fuente).
7. No copiar prompts, secretos, datos personales ni contenido obsoleto. Una memoria marcada para revisión se trata como contexto no confiable hasta verificarla.

Cuando el runtime exponga las herramientas de Engram usadas en este repositorio, la secuencia equivalente es:

```text
mem_context(project="systems-engineering-framework-agent")

mem_search(
  query="systems-engineering-framework-agent MVP arquitectura distribución repositorios",
  project="proyecto-base",
  scope="project",
  match_mode="any"
)

# Fallback si no se conoce o no resuelve el proyecto de origen:
mem_search(
  query="systems-engineering-framework-agent framework-agent",
  all_projects=true,
  scope="project",
  match_mode="any"
)

mem_get_observation(id=<id_recuperado>)

mem_save(
  project="systems-engineering-framework-agent",
  scope="project",
  type="<architecture|decision|discovery>",
  topic_key="<clave_estable>",
  title="<título curado>",
  content="<decisión verificada + procedencia + rutas fuente>"
)
```

> Los nombres y parámetros exactos de las herramientas deben confirmarse contra la integración Engram disponible en la sesión. Si Engram no está disponible, el arranque continúa con PRD 1 y el Markdown versionado; la memoria es suplementaria.

### Memorias de arranque conocidas

| ID en `proyecto-base` | `topic_key` | Uso al iniciar el repo nuevo |
| --- | --- | --- |
| `2162` | `architecture/mvp-distribution-boundaries` | Contexto de los tres subsistemas y fronteras iniciales. |
| `2163` | `architecture/sharepoint-approval-sync` | Contexto futuro, fuera del MVP, sobre SharePoint y aprobaciones. |
| `2164` | `architecture/mvp-scope` | Alcance exclusivo del MVP framework-agent. |
| `2165` | `architecture/mvp-distribution-contract` | Contexto histórico del contrato de distribución (sustituido por PRD 1). |
| `2166` | `architecture/repository-topology` | Separación entre repo de producto y `proyecto-base`. |
| `2167` | `architecture/framework-agent-product` | Resumen del documento de arquitectura y sus pendientes. |
| `2168` | `migration/framework-agent-source-state` | Estado Git verificado antes de iniciar la migración. |
| `2169` | `architecture/installed-skill-catalog` | Brecha entre el catálogo requerido por `AGENTS.md` y el layout instalado. |

Los IDs son ayudas de bootstrap de la instancia Engram actual, no claves de dominio. La recuperación durable debe poder encontrarse también por `topic_key`, título, contenido y proyecto de origen.

## 13. Riesgos y mitigaciones

| Riesgo | Mitigación |
| --- | --- |
| Sin deriva ni manifiesto, un consumidor puede editar archivos instalados y desalinearse del marco | Aceptado por diseño (one-shot): el proyecto es del consumidor. La re-instalación con `init` + colisiones explícitas es el único mecanismo de refresco. |
| Escritura accidental en `proyecto/` o fuera del write-set | Frontera dura + preflight + tests (PRD 1, §8 y AC-4/5/8/9). |
| Escapes de ruta vía symlink preexistente en el destino | RNF-3 del PRD + AC-8 con tests dedicados. |
| `init` re-ejecutado dispara colisiones masivas | Comportamiento definido (listado completo, `[y/N]`, `--force`); sin diff ni migración en MVP. |
| Fuentes canónicas duplicadas | Fuente única en el repo de producto; en el consumidor son archivos instalados, no segunda autoridad editable del producto. |
| Codex Desktop ausente o versión insuficiente | Prerrequisito documentado (preinstalado/autenticado); versión mínima por definir. |
| Confundir árbol fuente con árbol instalado | Este documento fija ambos árboles (sección 5); el árbol fuente es la única autoridad editable del producto. |

### Decisiones ya resueltas (no abiertas)

Árbol por capas ejecutado, `runtime/AGENTS.md` como única fuente sin `AGENTS.md` en raíz, separación entre arquitectura de capacidades (`framework/guias/skill-architecture.md`) y registry operativo (`runtime/catalogo/skill-registry.md`), `framework/guias/` no instalado, `docs/history/` deprecated, sin submódulos, `proyecto-base` como fixture de aceptación, y RAG/SharePoint/Power Automate fuera del MVP. Con PRD 1 aprobado, además: producto `se-agent`/`se_agent` en Python `>=3.12`, distribución `pipx` + ZIP de tag (sin PyPI ni EXE), modelo one-shot con propiedad del consumidor, sin manifiesto/hashes/`update`/`doctor`/deriva, registry manual con verificación CI, y `installer/windows/` obsoleto.

### Únicamente pendientes (no se inventan)

| Dato pendiente | Por qué queda abierto |
| --- | --- |
| Implementación del paquete `se_agent` (CLI, payload, preflight) | Trabajo de implementación del MVP; no se decide aquí. |
| Organización/URL de GitHub | Placeholder en PRD 1 (seguimiento abierto, §12). |
| Destino de `runtime/agents/` (instalado o no) | Sin resolución; excluido del payload (seguimiento abierto, PRD 1 §12). |
| Matriz de sistemas operativos objetivo | pipx es multiplataforma; por confirmar (seguimiento abierto, PRD 1 §12). |
| Versión mínima de Codex | Prerrequisito documental ("preinstalado y autenticado"); se marca por definir. |

## 14. Pendientes de implementación

- [ ] Implementar el paquete `se_agent` con CLI `se-agent` (`init` y `--version`), preflight, protocolo de colisiones y frontera de escritura estricta (PRD 1, §5, §8–9).
- [ ] Configurar el pipeline de publicación: tag SemVer inmutable → ZIP → `pipx`; coherencia de versión (PRD 1, AC-1/AC-2).
- [ ] Poblar `runtime/skills/` con la skill F0 funcional y su entrada en el registry (PRD 1, AC-12).
- [ ] Crear los artefactos del adaptador Codex en `adapters/codex/` (`.codex/config.toml` + agentes).
- [ ] Implementar la verificación de coherencia bidireccional registry ↔ `runtime/skills/` en tests/CI (PRD 1, AC-10), sin generación del registry.
- [ ] Añadir las pruebas de comportamiento (payload exacto, `proyecto/` byte a byte, write-set, escapes de ruta, colisiones) según PRD 1, §10.
- [ ] Definir la organización/URL de GitHub y sustituir el placeholder de PRD 1.
- [ ] Confirmar la matriz de sistemas operativos objetivo.
- [ ] Decidir el destino de los contratos harness-neutral de `runtime/agents/` (instalados o no).

## 15. Referencias (rutas relativas al repositorio)

Rutas presentes en el árbol vigente:

- `../prd/prd-001-one-shot-codex-scaffolder.md` — PRD 1 (autoridad de requisitos del MVP).
- `../decisions/agents-contract.md` — decisión del contrato único de `AGENTS.md`.
- `../decisions/skill-artifacts.md` — decisión sobre arquitectura de capacidades vs registry operativo.
- `../history/decisions/tradeoff-codex-pi.md` — análisis histórico Codex vs Pi (deprecated, no autoritativo).
- `../architecture/orchestrator.md` — capas del orquestador (referencia de fronteras).
- `../architecture/domain-harness-boundary.md` — autoridad y dirección de dependencias.
- `../architecture/memory.md` — política de persistencia/autoridad.
- `../guides/quickstart.md` — flujo mínimo del orquestador.
- `../history/README.md` — aviso de deprecación del histórico (no autoritativo).
- `../../framework/guias/skill-architecture.md` — arquitectura de capacidades del framework (autoridad de significado; no se instala).
- `../../framework/guias/project-init.md` — guía de arranque (curada desde el histórico).
- `../../framework/marco/README.md` — contenido del dominio.
- `../../runtime/AGENTS.md` — contrato de runtime canónico.
- `../../runtime/catalogo/skill-registry.md` — registry operativo (bootstrap 0 skills; mantenido a mano).
- `../../README.md` — resumen del producto.

`runtime/skills/` es la ubicación vigente de las skills ejecutables (poblado pendiente) y no se lista como referencia individual.

El estado autoritativo del proyecto vivo no vive en este repositorio: reside en el fixture `proyecto-base` (por ejemplo `proyecto/estado/proyecto_actual.md`, `proyecto/estado/estado_fases.md`, `proyecto/hitos/hito_aprobacion_trabajo.md`), y el producto lo respeta como intocable.
