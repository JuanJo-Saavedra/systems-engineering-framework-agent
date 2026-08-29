---
document_type: arquitectura_producto
language: es
version: 2.2
status: adoptada
---

# Arquitectura del producto `systems-engineering-framework-agent`

## Decisión ejecutiva

**La reestructuración física al árbol por capas está ejecutada.** El repositorio ya no contiene el árbol plano migrado transitorio (con `marco/`, `AGENTS.md` raíz, `catalogo/skill-registry.md`, `adapter/`, `skills/`, `agent/`, `manifest/` y `tests/` a nivel raíz); esa superficie fue reubicada en el árbol canónico por capas: `framework/` (dominio y guías de diseño), `runtime/` (contrato, skills instalables y registry operativo), `adapters/codex/` (específico de Codex), `installer/windows/` (comandos y empaquetado), `tests/{unit,integration,fixtures}` y `release/` (fuentes de publicación). La v2.1 separó la **arquitectura de capacidades** (`framework/guias/skill-architecture.md`) del **registry operativo** (fuente `runtime/catalogo/skill-registry.md`, instalado como `catalogo/skill-registry.md`). La v2.2 registra que esa topología ya es el estado real del repositorio y convierte el antiguo plan de transición en un registro de transición ejecutada con pendientes de implementación explícitas.

El producto sigue distribuyéndose como **ejecutable portátil de Windows vía GitHub Releases** y, en un proyecto destino, instala y mantiene únicamente un conjunto acotado de archivos gestionados: `marco/` (solo lectura, desde `framework/marco/`), el `AGENTS.md` de raíz (desde `runtime/AGENTS.md`), `catalogo/skill-registry.md` (copia gestionada read-only, desde `runtime/catalogo/skill-registry.md`), las skills en `.agents/skills/` (desde `runtime/skills/`), los artefactos de configuración Codex en `.codex/` (desde `adapters/codex/`) y el manifiesto/hashes en `.framework-agent/`. `framework/guias/` **no** se instala en consumidores: es base de diseño, comportamiento y accionamiento del producto. El producto **nunca** accede ni modifica `proyecto/`, sus registros, hitos, entregables, evidencia ni esquemas de proyecto. El repositorio `proyecto-base` no es fuente canónica del marco: es un **fixture de consumo y aceptación** con copias instaladas gestionadas.

| Punto | Decisión adoptada |
| --- | --- |
| Árbol de implementación | Árbol por capas adoptado; la reestructuración física está ejecutada. |
| Dominio canónico | `framework/marco/`; se instala como `marco/`. |
| Guías canónicas del framework | `framework/guias/`; separadas de `docs/history/`; **no** se instalan en consumidores. |
| Arquitectura de capacidades | `framework/guias/skill-architecture.md`. |
| Registry operativo | `runtime/catalogo/skill-registry.md` (bootstrap con 0 skills; generador/CI pendiente); se instala como `catalogo/skill-registry.md` read-only. |
| Índice técnico del harness | `.atl/skill-registry.md`; solo desarrollo, no se empaqueta ni se instala. |
| Contrato instalable | `runtime/AGENTS.md` es la **única** fuente; no hay `AGENTS.md` en raíz del repo de producto. |
| Destino del contrato | En el consumidor se instala como `AGENTS.md` de raíz. |
| Skills | `runtime/skills/` → `.agents/skills/` (vacío por ahora; no se declaran skills disponibles). |
| Contratos runtime harness-neutral | `runtime/agents/`. |
| Específico de Codex | `adapters/codex/`. |
| Instalador | `installer/windows/` alojará `init`/`update`/`doctor`/`version` y el empaquetado portable (implementación pendiente). |
| Tests | `tests/{unit,integration,fixtures}` (estructura creada; pruebas de comportamiento pendientes). |
| Publicación | `release/` contiene fuentes de manifiesto/hashes/notas/config (estructura creada; build/publicación pendientes). |
| Histórico | `docs/history/` completo es deprecated, histórico, no autoritativo y no participa en generación. |
| Superficie gestionada | `marco/`, `AGENTS.md` raíz, `catalogo/skill-registry.md`, `.agents/skills/`, `.codex/`, `.framework-agent/`. |
| Superficie prohibida | `proyecto/`, registros, hitos, entregables, evidencia, esquemas de proyecto. |
| Autoridad de `AGENTS.md` | Un único contrato semántico de runtime; `runtime/AGENTS.md` es la fuente canónica. |
| Integridad | Manifiesto + SHA-256 (integridad, **no** firma de código). |
| Submódulos | No se usan. |
| `proyecto-base` | Fixture de consumo y aceptación, no fuente canónica. |

## Propósito

Este documento es el handoff de arquitectura para el repositorio `systems-engineering-framework-agent`. Fija qué se construye, qué se instala y qué queda fuera, y registra la frontera que impide que el instalador/actualizador toque datos de proyecto. La v2.0 adoptó la **topología por capas** que reemplaza al árbol plano migrado. La v2.1 añadió la separación entre **arquitectura de capacidades** y **registry operativo**. La v2.2 registra la reestructuración física ejecutada y deja explícitos los pendientes de implementación que restan.

## Autoridad y ruta de revisión

- **Autoridad de la decisión**: la persona que lidera el producto. Este documento registra decisiones ya adoptadas; no abre nuevas bifurcaciones.
- **Estado**: `adoptada` (v2.2). Supersede la v2.1 y anteriores. Cambios posteriores se tramitan por revisión normal del repositorio de producto.
- **Ruta de revisión**: este documento es la fuente de referencia del árbol vigente; los artefactos de implementación que se deriven (código del instalador, plantillas del adaptador, esquema de manifiesto, generador del registry) se revisan contra lo aquí fijado.
- **Qué revisar primero**: la decisión ejecutiva, la separación arquitectura de capacidades vs registry operativo (sección 3 y `docs/decisions/skill-artifacts.md`), la topología (sección 4), los árboles fuente e instalado (sección 5), la frontera de propiedad (sección 6) y el registro de transición y pendientes (secciones 12 y 15).

## 1. Contexto: tres subsistemas y alcance del MVP

El sistema completo se compone de tres subsistemas con responsabilidades distintas. El MVP cubre **solo** los dos primeros.

| Subsistema | Ubicación lógica | Responsabilidad | ¿En el MVP? |
| --- | --- | --- | --- |
| Framework (dominio) | `framework/marco/` (instalado como `marco/`) | Proceso de ingeniería: fases `F0`–`F8`, reviews, baselines, glosario, reglas. | Sí (empaquetado y gestionado). |
| Agente (framework-agent) | repo de producto | Runtime/orquestador + adaptador Codex que ejecuta el proceso según el contrato de runtime y el registry operativo. | Sí (es el producto). |
| Proyecto consumidor | `proyecto/` en el destino | Instancia viva: estado, hitos, registros, entregables, evidencia. | No (es el fixture de aceptación; el producto no lo gestiona). |

> El producto `systems-engineering-framework-agent` es la unión de **framework + agente**. El proyecto consumidor no se empaqueta ni se migra; el producto lo respeta como intocable durante `init`/`update`/`doctor`.

## 2. Alcance del producto y no-objetivos

### Alcance (MVP)

- Empaquetar framework + agente en un único repo, evolucionando juntos.
- Distribuir como ejecutable portátil de Windows vía GitHub Releases.
- Instalar y actualizar los archivos gestionados en un proyecto destino.
- Generar artefactos del adaptador Codex (skills, agentes, configuración).
- Verificar integridad con manifiesto + SHA-256.
- Instalar/actualizar de forma transaccional y con cierre seguro ante fallo (fail-closed).

### No-objetivos (fuera del MVP)

- RAG, SharePoint y Power Automate.
- Migraciones de proyectos existentes.
- Gestionar o modificar `proyecto/` o cualquier dato de proyecto.
- Submódulos de Git.
- Firma de código (SHA-256 es integridad, no autoría).
- Desinstalación (`uninstall`), salvo que se etiquete explícitamente como pendiente.
- Más de un harness en el MVP: el dominio y los contratos runtime son harness-neutrales, pero el único adaptador inicial es Codex.

## 3. Capas y dirección de dependencias

El dominio define **qué** se hace; el agente define **cómo** se ejecuta; el proyecto consumidor contiene los **hechos**. La dependencia apunta hacia abajo: lo inferior puede depender de lo superior, nunca al revés.

```text
dominio (framework/marco/ + framework/guias/skill-architecture.md)
   ↑ autoridad de significado
contrato de runtime (runtime/AGENTS.md) + contratos harness-neutral (runtime/agents/)
   ↑ comportamiento portable
registry operativo (runtime/catalogo/skill-registry.md)
   ↑ disponibilidad de skills instaladas
adaptador Codex (adapters/codex/ → skills · agentes · config)
   ↑ traducción a artefactos ejecutables
agente (installer/windows/ → runtime del producto)
   ↑ ejecución
superficie gestionada instalada (marco/ · AGENTS.md · catalogo/skill-registry.md · .agents/ · .codex/ · .framework-agent/)
   ↑ lectura/escritura acotada
proyecto consumidor (proyecto/) — solo lectura por el runtime; intocable por init/update/doctor
```

| Capa | Es autoridad sobre | No es autoridad sobre |
| --- | --- | --- |
| Dominio (`framework/marco/` + `framework/guias/skill-architecture.md`) | Significado del proceso y arquitectura de capacidades | Ejecución, herramientas, disponibilidad runtime |
| Contrato de runtime (`runtime/AGENTS.md`) y contratos harness-neutral (`runtime/agents/`) | Comportamiento portable del agente | Significado del dominio |
| Registry operativo (`runtime/catalogo/skill-registry.md`) | Inventario de skills disponibles y accesibles | Significado del dominio, algoritmo de routing, guardrails |
| Adaptador Codex (`adapters/codex/`) | Artefactos ejecutables Codex | Significado, arquitectura de capacidades |
| Agente (`installer/windows/`) | Instalar/actualizar superficie gestionada | Datos de proyecto |
| Proyecto consumidor | Hechos del proyecto | Proceso (lo respeta) |

> El dominio no importa Codex; el adaptador sí importa el dominio. Esta frontera se conserva de `docs/architecture/domain-harness-boundary.md`.

## 4. Topología: repo fuente canónico vs repo consumidor instalado

Existen **dos** repositorios con roles distintos, y **una** autoridad de fuente.

| Repo | Rol | Contenido |
| --- | --- | --- |
| `systems-engineering-framework-agent` | Fuente canónica del producto | `framework/` (`marco/` + `guias/`), `runtime/` (`AGENTS.md`, `catalogo/skill-registry.md`, `skills/`, `agents/`), `adapters/codex/`, `installer/windows/`, `tests/`, `release/`, `docs/`. |
| Proyecto destino (p. ej. `proyecto-base`) | Consumidor/instalado | Copias gestionadas (`marco/`, `AGENTS.md`, `catalogo/skill-registry.md`, `.agents/skills/`, `.codex/`, `.framework-agent/`) + `proyecto/` intocable. |

Reglas:

- **Sin submódulos.** El repo de producto es un único repositorio; el consumidor recibe copias gestionadas por el agente, no referencias Git.
- **Una única autoridad de fuente.** El marco, la arquitectura de capacidades, el registry operativo y el contrato de runtime se editan solo en el repo de producto. En el consumidor son copias instaladas; no existe una segunda autoridad editable.
- **Un contrato semántico de runtime.** `runtime/AGENTS.md` (fuente en el repo de producto) y el `AGENTS.md` instalado en el consumidor representan el **mismo** contrato semántico, no dos contratos editados por separado. La deriva local en el consumidor bloquea la actualización (sección 6).
- **Sin `AGENTS.md` en la raíz del producto.** La única fuente del contrato instalable vive en `runtime/AGENTS.md`; el `AGENTS.md` en raíz aparece únicamente como artefacto instalado en el consumidor.

> Nota sobre el diagrama: `docs/history/diagrama-mvp.png` es **ideación histórica** del arnés y contiene preguntas ya resueltas. Queda **superado** donde sus decisiones difieran de las aquí adoptadas (distribución EXE portátil vía GitHub Releases, `marco/` gestionado, `catalogo/skill-registry.md` gestionado, manifiesto/hashes, sin submódulos, `proyecto-base` como fixture). No se usa como referencia final.

## 5. Árboles: fuente e instalado (adoptado y ejecutado)

La reestructuración física está ejecutada; no existe un árbol plano transitorio. El árbol fuente vigente es el árbol por capas adoptado, y el árbol instalado describe la superficie gestionada en el proyecto destino.

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
│   ├── skills/                         # skills ejecutables → .agents/skills/<skill>/SKILL.md (vacío por ahora)
│   ├── agents/                         # contratos runtime harness-neutral
│   └── catalogo/
│       └── skill-registry.md           # registry operativo (bootstrap 0 skills) → se instala como catalogo/skill-registry.md
├── adapters/
│   └── codex/                          # lo específico de Codex (config + agentes)
├── installer/
│   └── windows/                        # init/update/doctor/version + empaquetado portable
├── tests/
│   ├── unit/
│   ├── integration/
│   └── fixtures/
├── release/                            # fuentes de manifiesto/hashes/notas/config de publicación
├── docs/
│   ├── architecture/
│   ├── decisions/
│   ├── guides/
│   └── history/                        # deprecated, histórico, no autoritativo
├── dist/                               # generado, NO versionado (outputs de release/binario)
└── .gitignore
```

> `.atl/` (índice técnico del harness) es solo desarrollo, está en `.gitignore` y no forma parte del árbol empaquetado.

> `release/` contiene las **fuentes** de manifiesto, hashes, notas y configuración de publicación; los outputs generados (binario, manifiesto resuelto, hashes de release) se escriben en `dist/` y no se versionan.

### 5.2 Árbol instalado (proyecto destino)

```text
<proyecto-destino>/
├── AGENTS.md                          # instalado (copia gestionada de runtime/AGENTS.md)
├── marco/                             # instalado, solo lectura (copia gestionada de framework/marco/)
├── catalogo/
│   └── skill-registry.md              # instalado, solo lectura (copia gestionada de runtime/catalogo/skill-registry.md)
├── .agents/skills/<skill>/SKILL.md    # instalado (gestionado; desde runtime/skills/)
├── .codex/agents/*.toml               # instalado (gestionado; desde adapters/codex/)
├── .codex/config.toml                 # instalado (gestionado; desde adapters/codex/)
├── .framework-agent/
│   ├── manifest.json                  # versión instalada + hashes (se escribe al final)
│   └── hashes.sha256                  # integridad de archivos gestionados
└── proyecto/                          # NO gestionado; permanece intacto
```

## 6. Contrato de propiedad gestionada

El producto es dueño exclusivo de un conjunto cerrado de archivos. Fuera de ese conjunto, no escribe.

| Superficie gestionada | Rol en destino | Comportamiento ante deriva local |
| --- | --- | --- |
| `marco/` | Copia instalada de `framework/marco/`, solo lectura para el agente | Deriva → bloquea actualización |
| `AGENTS.md` (raíz) | Copia instalada de `runtime/AGENTS.md`; **propiedad total** del producto | Deriva (edición local) → bloquea actualización |
| `catalogo/skill-registry.md` | Copia instalada read-only de `runtime/catalogo/skill-registry.md` (registry operativo) | Deriva → bloquea actualización |
| `.agents/skills/<skill>/SKILL.md` | Copias instaladas de skills Codex (desde `runtime/skills/`) | Deriva → bloquea actualización |
| `.codex/agents/*.toml`, `.codex/config.toml` | Artefactos del adaptador (desde `adapters/codex/`) | Deriva → bloquea actualización |
| `.framework-agent/manifest.json` + `hashes.sha256` | Estado de instalación; lo escribe el agente al final | No editable por el usuario; se regenera |

Superficie prohibida (nunca se accede ni modifica durante `init`/`update`/`doctor`):

- `proyecto/` y todo su contenido.
- Registros, hitos, entregables, evidencia y esquemas de proyecto.
- Cualquier archivo fuera de la superficie gestionada.

Reglas duras:

- **Deriva local bloquea la actualización.** Si un archivo gestionado difiere de su hash instalado, `update` se detiene y reporta las diferencias. **No hay sobrescritura silenciosa.**
- **Propiedad total de `AGENTS.md`.** El producto reemplaza y mantiene el `AGENTS.md` de raíz del consumidor; no coexiste con un `AGENTS.md` editado a mano.
- **Un solo contrato semántico.** La fuente (`runtime/AGENTS.md`) y la copia instalada representan el mismo contrato; la deriva es un error a resolver, no una segunda autoridad.
- **Registry operativo read-only.** `catalogo/skill-registry.md` se instala como copia gestionada de solo lectura del registry operativo (`runtime/catalogo/skill-registry.md`); no es una segunda fuente editable.

## 7. Distribución y comandos

- **Formato**: ejecutable portátil de Windows, publicado en GitHub Releases. (El nombre final del binario y la organización de GitHub quedan **por definir**; no se fijan aquí.)
- **Prerrequisito**: Codex Desktop está **preinstalado y autenticado** en la máquina destino; el producto no instala ni autentica Codex. (La versión mínima de Codex queda **por definir**.)
- **Firma**: no hay infraestructura de firma de código en el MVP; la integridad se cubre solo con SHA-256.

La superficie de comandos listada a continuación es la **definición del MVP**; su implementación en `installer/windows/` es **pendiente** (sección 15).

| Comando | Comportamiento |
| --- | --- |
| `init --harness codex --target .` | Instala la superficie gestionada en el destino y escribe el manifiesto. |
| `update` | Actualiza transaccionalmente la superficie gestionada; verifica integridad y deriva. |
| `doctor` | Verifica superficie gestionada, manifiesto, hashes y presencia de Codex Desktop. |
| `version` | Imprime la versión del producto. |
| `uninstall` | **Pendiente/futuro**; no forma parte del MVP. |

## 8. Instalación y actualización: seguridad transaccional

`update` (y la fase de reemplazo de `init`) sigue una secuencia fail-closed:

1. **Descarga por etapas** a un directorio temporal de staging; nunca se escribe directamente sobre los archivos gestionados.
2. **Verificación de integridad** SHA-256 de los artefactos en staging contra el manifiesto de la release.
3. **Chequeo de deriva** de los archivos gestionados instalados contra el manifiesto instalado. Si hay deriva local → **bloquear** y reportar; sin sobrescritura silenciosa.
4. **Plan**: calcular el conjunto exacto de archivos a reemplazar (solo superficie gestionada).
5. **Reemplazo acotado**: reemplazar únicamente los archivos gestionados (vía staging + intercambio atómico o reemplazo por archivo).
6. **Validación**: re-hashear los archivos instalados y verificar coincidencia con el manifiesto.
7. **Escribir el manifiesto al final** (`.framework-agent/manifest.json` + `hashes.sha256`) como último paso de éxito.
8. **Fail-closed**: ante cualquier fallo, dejar el estado previo intacto (o revertir) y reportar el error. Nunca dejar una instalación a medias marcada como válida.

Clarificación de integridad:

- **SHA-256 verifica integridad** (que los bytes no se corrompieron ni cambiaron respecto del manifiesto de la release).
- **SHA-256 no es firma de código.** No establece quién produjo el binario ni protege contra un actor que reemplace binario y manifiesto juntos. Hasta que exista infraestructura de firma (por definir), este límite se documenta como riesgo residual.

## 9. Ejemplo de manifiesto y artefactos de release

### 9.1 Manifiesto (ejemplo ilustrativo)

```json
{
  "schema": "framework-agent.manifest/v1",
  "product": "systems-engineering-framework-agent",
  "version": "0.1.0",
  "released_at": "YYYY-MM-DD",
  "harness": "codex",
  "codex_min_version": null,
  "managed_files": [
    { "path": "AGENTS.md", "sha256": "<hash>" },
    { "path": "catalogo/skill-registry.md", "sha256": "<hash>" },
    { "path": "marco/fases/fase_0_concepto_y_factibilidad.md", "sha256": "<hash>" }
  ]
}
```

> `version` y `released_at` son ilustrativos. `codex_min_version: null` marca que la versión mínima de Codex está por definir. Las rutas de `managed_files` son las **rutas instaladas** (p. ej. `marco/`, no `framework/marco/`).

### 9.2 Artefactos de release

| Artefacto | Rol |
| --- | --- |
| `<binario>.exe` | Ejecutable portátil de Windows (nombre por definir). |
| `manifest.json` | Versión y hashes de los archivos gestionados. |
| `hashes.sha256` | Lista `sha256  ruta` de los artefactos de la release. |
| `NOTES.md` | Notas de release y cambios. |

> Las **fuentes** de estos artefactos viven en `release/`; los outputs generados se escriben en `dist/` y no se versionan.

## 10. Responsabilidad del adaptador Codex y frontera harness-neutral

- **Adaptador**: traduce el contrato de runtime (`runtime/AGENTS.md`) y el registry operativo (`runtime/catalogo/skill-registry.md`) a artefactos Codex (`.agents/skills/`, `.codex/agents/*.toml`, `.codex/config.toml`). Es un mapeo ejecutable, nunca una autoridad de significado. La arquitectura de capacidades (`framework/guias/skill-architecture.md`) guía el diseño, no se empaqueta ni se instala.
- **Separación runtime/adaptador**: `runtime/agents/` contiene contratos runtime **harness-neutrales**; `adapters/codex/` contiene solo lo específico de Codex. El dominio no depende de ninguno de los dos.
- **Progressive disclosure**: las skills se cargan en tres niveles — metadata (`name`/`description`), instrucciones (`SKILL.md`) y recursos bajo demanda — para reducir consumo de contexto.
- **Frontera de dominio**: el dominio (`framework/marco/`) permanece harness-neutral. Codex no evalúa disparadores de fase nativamente; el agente lee el estado del proyecto, selecciona la capacidad según la arquitectura de capacidades (`framework/guias/skill-architecture.md`) durante el diseño y, en runtime, resuelve/carga solo desde el registry operativo + metadata/SKILL. Ningún artefacto Codex redefine el dominio.
- **No duplicar reglas de dominio en TOML**: la configuración Codex expone mecanismos, no re-escribe el proceso.

## 11. Slice vertical del MVP y criterios de aceptación medibles

### Slice vertical

1. Un contrato de fase canónico (p. ej. `F0`) bajo `framework/marco/fases/`.
2. Una arquitectura de capacidades bajo `framework/guias/skill-architecture.md`.
3. Una skill de fase bajo `runtime/skills/`, con frontmatter que alimenta el registry operativo.
4. Un registry operativo generado y versionado en `runtime/catalogo/skill-registry.md` que CI valida contra `runtime/skills/`.
5. Un adaptador que genera `.codex/config.toml` + un agente, desde `adapters/codex/`.
6. `init --harness codex --target .` instala la superficie gestionada y escribe el manifiesto.
7. `update` corre transaccionalmente y deja `proyecto/` byte a byte sin cambios.

### Criterios de aceptación medibles

- [ ] `init` produce la superficie gestionada y el manifiesto; `doctor` pasa sin observaciones.
- [ ] `update` sin deriva local actualiza la versión del manifiesto al final.
- [ ] `update` con deriva local en un archivo gestionado **bloquea** y reporta las diferencias; no sobrescribe.
- [ ] `update` con SHA-256 que no coincide **falla cerrado** y deja los archivos gestionados previos intactos.
- [ ] `proyecto/` permanece **byte a byte idéntico** durante `update`: se calcula un hash recursivo del árbol `proyecto/` antes y después y se exige igualdad.
- [ ] `doctor` detecta Codex Desktop ausente y lo reporta.
- [ ] Existe un único contrato semántico de `AGENTS.md`; la copia instalada es idéntica a la fuente `runtime/AGENTS.md`.
- [ ] `catalogo/skill-registry.md` se instala como copia gestionada read-only desde `runtime/catalogo/skill-registry.md`.
- [ ] El registry operativo generado coincide con `runtime/skills/`; CI falla si hay deriva.
- [ ] `doctor` valida registry instalado ↔ skills instaladas ↔ manifiesto/hashes.

## 12. Registro de transición ejecutada

La migración plana dejó los activos en el repositorio y la **transición al árbol por capas está ejecutada**. Quedó completado:

- [x] Preservar el trabajo local (sin operaciones destructivas).
- [x] Reubicar el dominio `marco/` → `framework/marco/` y situar las guías canónicas del framework en `framework/guias/` (separadas de `docs/history/`).
- [x] Separar arquitectura de capacidades del registry operativo: `catalogo/skill-registry.md` → `framework/guias/skill-architecture.md`; curar `docs/history/guias/project-init.md` → `framework/guias/project-init.md`. `framework/guias/` **no** se instala en consumidores.
- [x] Crear `runtime/catalogo/skill-registry.md` como bootstrap del registry operativo (0 skills). El `catalogo/skill-registry.md` de la raíz del producto dejó de existir como fuente.
- [x] Reubicar el contrato de runtime `AGENTS.md` raíz → `runtime/AGENTS.md`, de modo que **no queda** `AGENTS.md` en la raíz del producto.
- [x] Reorganizar skills y contratos runtime: `skills/` → `runtime/skills/`; `agent/` → `runtime/agents/` (contratos harness-neutrales).
- [x] Separar lo específico de Codex: `adapter/codex/` → `adapters/codex/`.
- [x] Consolidar publicación: `manifest/` → `release/` (fuentes de manifiesto/hashes/notas/config); los outputs generados van a `dist/`, no versionados.
- [x] Estructurar tests como `tests/{unit,integration,fixtures}`.
- [x] Marcar `docs/history/` como deprecated/no autoritativo y excluirlo de la generación.
- [x] Confirmar sin submódulos: un único repo de producto; el consumidor recibe copias gestionadas.

Verificación de fuente única (satisfecha para los artefactos ya presentes): el marco, la arquitectura de capacidades y `runtime/AGENTS.md` se editan **solo** en el repo de producto; el registry operativo nace en `runtime/catalogo/skill-registry.md`. En `proyecto-base`, `marco/`, `catalogo/skill-registry.md` y `AGENTS.md` pasan a ser copias instaladas gestionadas cuando `init` esté implementado (pendiente, sección 15).

## 13. Recuperación de decisiones desde Engram (bootstrap, en su mayoría ejecutado)

Esta sección registra el procedimiento de traspaso de memoria usado al iniciar este repositorio. Queda como referencia de bootstrap; no es una autoridad sobre las decisiones ya fijadas en este documento.

Engram conserva memoria por proyecto. Al abrir `systems-engineering-framework-agent`, el agente no debe asumir que las observaciones guardadas bajo `proyecto-base` aparecerán en el contexto del nuevo repo. El traspaso se realiza como una **recuperación curada**, no como una importación ciega ni como sustitución de los documentos versionados.

### Orden de autoridad durante el traspaso

1. Este documento y las fuentes Markdown referenciadas son la autoridad.
2. Las observaciones de Engram aportan resumen, justificación y punteros.
3. Si una memoria contradice el Markdown vigente, se informa la discrepancia y prevalece Markdown.
4. Las memorias originales de `proyecto-base` se conservan; no se eliminan ni se trasladan destructivamente.

### Procedimiento de recuperación

Desde una sesión abierta en el nuevo repositorio:

1. Consultar el contexto del proyecto nuevo. Un resultado vacío es esperable y no implica que las memorias históricas se hayan perdido.
2. Buscar explícitamente en el proyecto de origen `proyecto-base` por nombre de producto, decisiones y claves de tema.
3. Si el nombre de proyecto no resuelve o se desconoce, repetir la búsqueda con alcance de todos los proyectos.
4. Recuperar el contenido completo de cada observación seleccionada por su identificador.
5. Contrastar cada memoria con este documento y sus referencias antes de usarla.
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

> Los nombres y parámetros exactos de las herramientas deben confirmarse contra la integración Engram disponible en la sesión. Si Engram no está disponible, el arranque continúa con este documento y el Markdown versionado; la memoria es suplementaria.

### Memorias de arranque conocidas

| ID en `proyecto-base` | `topic_key` | Uso al iniciar el repo nuevo |
| --- | --- | --- |
| `2162` | `architecture/mvp-distribution-boundaries` | Contexto de los tres subsistemas y fronteras iniciales. |
| `2163` | `architecture/sharepoint-approval-sync` | Contexto futuro, fuera del MVP, sobre SharePoint y aprobaciones. |
| `2164` | `architecture/mvp-scope` | Alcance exclusivo del MVP framework-agent. |
| `2165` | `architecture/mvp-distribution-contract` | `marco/` gestionado, propiedad de `AGENTS.md` y EXE portátil. |
| `2166` | `architecture/repository-topology` | Separación entre repo de producto y `proyecto-base`. |
| `2167` | `architecture/framework-agent-product` | Resumen del documento de arquitectura y sus pendientes. |
| `2168` | `migration/framework-agent-source-state` | Estado Git verificado antes de iniciar la migración. |
| `2169` | `architecture/installed-skill-catalog` | Brecha entre el catálogo requerido por `AGENTS.md` y el layout instalado. |

Los IDs son ayudas de bootstrap de la instancia Engram actual, no claves de dominio. La recuperación durable debe poder encontrarse también por `topic_key`, título, contenido y proyecto de origen.

### Formato mínimo de la memoria curada

```text
What: decisión recuperada y verificada.
Why: razón arquitectónica conservada.
Where: rutas vigentes en el nuevo repositorio.
Source: proyecto-base, observation_id=<id>,
        implementacion/arquitectura-systems-engineering-framework-agent.md.
Learned: límites, riesgos o pendientes todavía válidos.
```

## 14. Riesgos y mitigaciones

| Riesgo | Mitigación |
| --- | --- |
| Deriva local en archivos gestionados | Chequeo de deriva; bloqueo y reporte; sin sobrescritura silenciosa. |
| Corrupción o manipulación en tránsito | SHA-256 contra manifiesto; nota explícita de que es integridad, no autoría. |
| Fallo a mitad de actualización | Transacción fail-closed; manifiesto se escribe al final; estado previo intacto. |
| Fuentes canónicas duplicadas | Fuente única en el repo de producto; copias instaladas gestionadas. |
| Escritura accidental en `proyecto/` | Frontera dura; prueba de aceptación byte a byte. |
| Codex Desktop ausente | `doctor` lo detecta; prerrequisito documentado (preinstalado/autenticado). |
| Suplantación sin firma de código | Residual hasta añadir firma; documentado como límite del MVP. |
| Confundir árbol fuente con árbol instalado | Este documento fija ambos árboles (sección 5); el árbol fuente es la única autoridad editable. |

### Decisiones ya resueltas (no abiertas)

Árbol por capas adoptado y ejecutado (`framework/`, `runtime/`, `adapters/codex/`, `installer/windows/`, `release/`, `tests/{unit,integration,fixtures}`), `runtime/AGENTS.md` como única fuente sin `AGENTS.md` en raíz, separación entre arquitectura de capacidades (`framework/guias/skill-architecture.md`) y registry operativo (`runtime/catalogo/skill-registry.md`), `catalogo/skill-registry.md` instalado read-only desde `runtime/catalogo/skill-registry.md`, `framework/guias/` no instalado, `docs/history/` deprecated, ejecutable portátil, GitHub Releases, `marco/` gestionado, propiedad total de `AGENTS.md`, manifiesto/hashes, comando `update`, sin migraciones de proyecto, sin submódulos, `proyecto-base` como fixture de aceptación, y RAG/SharePoint/Power Automate fuera del MVP.

### Únicamente pendientes (no se inventan)

| Dato pendiente | Por qué queda abierto |
| --- | --- |
| Lenguaje de implementación del agente | No se decide aquí. |
| Organización de GitHub | No se fija. |
| Nombre final del binario | Se usa `<binario>` hasta definirlo. |
| Versión mínima de Codex | Se marca `null`/por definir. |
| Infraestructura de firma de código | Fuera del MVP; SHA-256 es solo integridad. |

## 15. Checklist de pendientes de implementación

- [ ] Poblar `runtime/skills/` con skills ejecutables (hoy vacío; el registry declara 0 skills).
- [ ] Implementar el generador del registry operativo desde `runtime/skills/*/SKILL.md`.
- [ ] Configurar CI para que falle si el registry operativo no coincide con `runtime/skills/`.
- [ ] Implementar `init`, `update`, `doctor`, `version` en `installer/windows/` con la transacción fail-closed.
- [ ] Implementar el adaptador Codex (`.codex/config.toml` + agentes/skills) en `adapters/codex/`.
- [ ] Fijar el esquema de manifiesto (`framework-agent.manifest/v1`) y la generación de hashes.
- [ ] Añadir las pruebas de comportamiento (selección de ruta, degradación, frontera) y la prueba byte a byte de `proyecto/`.
- [ ] Validar `doctor`: registry instalado ↔ skills instaladas ↔ manifiesto/hashes.
- [ ] Configurar el build y la publicación del EXE portátil en GitHub Releases.

## 16. Referencias (rutas relativas al repositorio)

Rutas presentes en el árbol vigente:

- `../decisions/agents-contract.md` — decisión v2.1 del contrato único de `AGENTS.md`.
- `../decisions/skill-artifacts.md` — decisión sobre arquitectura de capacidades vs registry operativo.
- `../history/decisions/tradeoff-codex-pi.md` — análisis histórico Codex vs Pi (deprecated, no autoritativo).
- `../architecture/orchestrator.md` — capas del orquestador (referencia de fronteras).
- `../architecture/domain-harness-boundary.md` — autoridad y dirección de dependencias.
- `../architecture/memory.md` — política de persistencia/autoridad.
- `../guides/quickstart.md` — flujo mínimo del orquestador.
- `../history/README.md` — aviso de deprecación del histórico (no autoritativo).
- `../history/diagrama-mvp.png` — ideación histórica (superada en lo que difiera de este documento).
- `../../framework/guias/skill-architecture.md` — arquitectura de capacidades del framework (autoridad de significado; no se instala).
- `../../framework/guias/project-init.md` — guía de arranque (curada desde el histórico).
- `../../framework/marco/README.md` — contenido del dominio.
- `../../runtime/AGENTS.md` — contrato de runtime canónico.
- `../../runtime/catalogo/skill-registry.md` — registry operativo (bootstrap 0 skills; generador/CI pendiente).
- `../../README.md` — resumen del producto.

`runtime/skills/` es la ubicación vigente de las skills ejecutables (hoy vacía) y no se lista como referencia individual.

El estado autoritativo del proyecto vivo no vive en este repositorio: reside en el fixture `proyecto-base` (por ejemplo `proyecto/estado/proyecto_actual.md`, `proyecto/estado/estado_fases.md`, `proyecto/hitos/hito_aprobacion_trabajo.md`), y el producto lo respeta como intocable.
