---
document_type: arquitectura_producto
language: es
version: 1.1
status: decision_adoptada
---

# Arquitectura del producto `systems-engineering-framework-agent`

## Decisión ejecutiva

Se crea un nuevo repositorio de producto, `systems-engineering-framework-agent`, que empaqueta en un único repo **el marco de ingeniería de sistemas y el agente que lo ejecuta**. El producto se distribuye como **ejecutable portátil de Windows vía GitHub Releases** y, en un proyecto destino, instala y mantiene únicamente un conjunto acotado de archivos gestionados: `/marco` (solo lectura), el `AGENTS.md` de raíz, las skills de Codex, los artefactos de adaptador/configuración de Codex y el manifiesto/hashes en `.framework-agent/`. El producto **nunca** accede ni modifica `proyecto/`, sus registros, hitos, entregables, evidencia ni esquemas de proyecto. El repositorio actual `proyecto-base` deja de ser fuente canónica del marco y pasa a ser un **fixture de consumo y aceptación** con copias instaladas gestionadas.

| Punto | Decisión adoptada |
| --- | --- |
| Repositorio de producto | `systems-engineering-framework-agent` (nuevo, único repo). |
| Alcance del MVP | Solo `framework + agente` (el producto). No incluye el proyecto consumidor. |
| Distribución | Ejecutable portátil de Windows vía GitHub Releases. |
| Superficie gestionada | `/marco`, `AGENTS.md`, skills de Codex, adaptador/configuración de Codex, `.framework-agent/`. |
| Superficie prohibida | `proyecto/`, registros, hitos, entregables, evidencia, esquemas de proyecto. |
| Autoridad de `AGENTS.md` | Un único contrato semántico de runtime; el repo de producto es la fuente canónica. |
| Integridad | Manifiesto + SHA-256 (integridad, **no** firma de código). |
| Submódulos | No se usan. |
| `proyecto-base` | Fixture de consumo y aceptación, no fuente canónica. |

## Propósito

Este documento es el handoff de arquitectura y migración para iniciar el repositorio `systems-engineering-framework-agent`. Fija qué se construye, qué se instala y qué queda fuera, y deja registrada la frontera que impide que el instalador/actualizador toque datos de proyecto.

## Autoridad y ruta de revisión

- **Autoridad de la decisión**: la persona que lidera el producto. Este documento registra decisiones ya adoptadas; no abre nuevas bifurcaciones.
- **Estado**: `decision_adoptada` (v1.0). Cambios posteriores se tramitan por revisión normal del repositorio de producto.
- **Ruta de revisión**: este documento es la fuente para el commit inicial del nuevo repo; los artefactos de implementación que se deriven (código del agente, plantillas del adaptador, esquema de manifiesto) se revisan contra lo aquí fijado.
- **Qué revisar primero**: la frontera de propiedad (sección 6), la transacción de instalación/actualización (sección 8) y el plan de migración (sección 12).

## 1. Contexto: tres subsistemas y alcance del MVP

El sistema completo se compone de tres subsistemas con responsabilidades distintas. El MVP cubre **solo** los dos primeros.

| Subsistema | Ubicación lógica | Responsabilidad | ¿En el MVP? |
| --- | --- | --- | --- |
| Framework (dominio) | `marco/` | Proceso de ingeniería: fases `F0`–`F8`, reviews, baselines, glosario, reglas. | Sí (empaquetado y gestionado). |
| Agente (framework-agent) | repo de producto | Runtime/orquestador + adaptador Codex que ejecuta el proceso según `AGENTS.md` y el catálogo. | Sí (es el producto). |
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
- Más de un harness en el MVP: el dominio es harness-neutral, pero el único adaptador inicial es Codex.

## 3. Capas y dirección de dependencias

El dominio define **qué** se hace; el agente define **cómo** se ejecuta; el proyecto consumidor contiene los **hechos**. La dependencia apunta hacia abajo: lo inferior puede depender de lo superior, nunca al revés.

```text
dominio (marco/ + catálogo de capacidades)
   ↑ autoridad de significado
contrato de runtime (AGENTS.md)
   ↑ comportamiento portable
adaptador Codex (skills · agentes · config)
   ↑ traducción a artefactos ejecutables
agente (runtime del producto)
   ↑ ejecución
superficie gestionada instalada (marco/ · AGENTS.md · .agents/ · .codex/ · .framework-agent/)
   ↑ lectura/escritura acotada
proyecto consumidor (proyecto/) — solo lectura por el runtime; intocable por init/update/doctor
```

| Capa | Es autoridad sobre | No es autoridad sobre |
| --- | --- | --- |
| Dominio (`marco/` + catálogo) | Significado del proceso | Ejecución, herramientas |
| Contrato de runtime (`AGENTS.md`) | Comportamiento portable del agente | Significado del dominio |
| Adaptador Codex | Artefactos ejecutables Codex | Significado, catálogo |
| Agente (producto) | Instalar/actualizar superficie gestionada | Datos de proyecto |
| Proyecto consumidor | Hechos del proyecto | Proceso (lo respeta) |

> El dominio no importa Codex; el adaptador sí importa el dominio. Esta frontera se conserva de `guias/frontera-dominio-harness.md`.

## 4. Topología: repo fuente canónico vs repo consumidor instalado

Existen **dos** repositorios con roles distintos, y **una** autoridad de fuente.

| Repo | Rol | Contenido |
| --- | --- | --- |
| `systems-engineering-framework-agent` | Fuente canónica del producto | `marco/`, `AGENTS.md` canónico, catálogo, skills, adaptador, implementación del agente, esquema de manifiesto, tests. |
| Proyecto destino (p. ej. `proyecto-base`) | Consumidor/instalado | Copias gestionadas (`/marco`, `AGENTS.md`, `.agents/skills/`, `.codex/`, `.framework-agent/`) + `proyecto/` intocable. |

Reglas:

- **Sin submódulos.** El repo de producto es un único repositorio; el consumidor recibe copias gestionadas por el agente, no referencias Git.
- **Una única autoridad de fuente.** El marco y el `AGENTS.md` se editan solo en el repo de producto. En el consumidor son copias instaladas; no existe una segunda autoridad editable.
- **Un contrato semántico de runtime.** El `AGENTS.md` de raíz del repo de producto (fuente) y el `AGENTS.md` instalado en el consumidor representan el **mismo** contrato semántico, no dos contratos editados por separado. La deriva local en el consumidor bloquea la actualización (sección 6).

> Nota sobre el diagrama: `implementacion/diagrama-mvp.png` es **ideación histórica** del arnés y contiene preguntas ya resueltas. Queda **superado** donde sus decisiones difieren de las aquí adoptadas (distribución EXE portátil vía GitHub Releases, `/marco` gestionado, manifiesto/hashes, sin submódulos, `proyecto-base` como fixture). No se usa como referencia final.

## 5. Árboles propuestos

### 5.1 Árbol fuente (nuevo repo de producto)

```text
systems-engineering-framework-agent/
├── AGENTS.md                    # contrato de runtime canónico (fuente única)
├── marco/                       # dominio canónico: fases, reviews, baselines, glosario, reglas
├── catalogo/
│   └── skill-registry.md        # catálogo canónico de capacidades (consumido por el agente)
├── skills/                      # skills ejecutables → .agents/skills/<skill>/SKILL.md en destino
├── adapter/
│   └── codex/                   # artefactos del adaptador Codex (plantillas)
│       ├── config.toml          #   plantilla de configuración
│       └── agents/              #   plantillas de agentes .toml
├── agent/                       # implementación del agente (lenguaje por definir)
├── manifest/                    # esquema de manifiesto + generación de hashes
├── tests/                       # pruebas de comportamiento y de instalación/actualización
├── docs/                        # arquitectura y handoffs
├── dist/                        # generado, no versionado: binario + artefactos de release
└── .gitignore
```

> El catálogo (`catalogo/skill-registry.md`) es un activo de dominio consumido por el agente; no se instala como archivo editable independiente en el destino para evitar una segunda autoridad con deriva.

### 5.2 Árbol instalado (proyecto destino)

```text
<proyecto-destino>/
├── AGENTS.md                          # instalado (copia gestionada del fuente)
├── marco/                             # instalado, solo lectura (copia gestionada)
├── .agents/skills/<skill>/SKILL.md    # instalado (gestionado)
├── .codex/agents/*.toml               # instalado (gestionado)
├── .codex/config.toml                 # instalado (gestionado)
├── .framework-agent/
│   ├── manifest.json                  # versión instalada + hashes (se escribe al final)
│   └── hashes.sha256                  # integridad de archivos gestionados
└── proyecto/                          # NO gestionado; permanece intacto
```

## 6. Contrato de propiedad gestionada

El producto es dueño exclusivo de un conjunto cerrado de archivos. Fuera de ese conjunto, no escribe.

| Superficie gestionada | Rol en destino | Comportamiento ante deriva local |
| --- | --- | --- |
| `/marco` | Copia instalada, solo lectura para el agente | Deriva → bloquea actualización |
| `AGENTS.md` (raíz) | Copia instalada del contrato único; **propiedad total** del producto | Deriva (edición local) → bloquea actualización |
| `.agents/skills/<skill>/SKILL.md` | Copias instaladas de skills Codex | Deriva → bloquea actualización |
| `.codex/agents/*.toml`, `.codex/config.toml` | Artefactos del adaptador | Deriva → bloquea actualización |
| `.framework-agent/manifest.json` + `hashes.sha256` | Estado de instalación; lo escribe el agente al final | No editable por el usuario; se regenera |

Superficie prohibida (nunca se accede ni modifica durante `init`/`update`/`doctor`):

- `proyecto/` y todo su contenido.
- Registros, hitos, entregables, evidencia y esquemas de proyecto.
- Cualquier archivo fuera de la superficie gestionada.

Reglas duras:

- **Deriva local bloquea la actualización.** Si un archivo gestionado difiere de su hash instalado, `update` se detiene y reporta las diferencias. **No hay sobrescritura silenciosa.**
- **Propiedad total de `AGENTS.md`.** El producto reemplaza y mantiene el `AGENTS.md` de raíz; no coexiste con un `AGENTS.md` editado a mano.
- **Un solo contrato semántico.** La fuente (`repo de producto`) y la copia instalada representan el mismo contrato; la deriva es un error a resolver, no una segunda autoridad.

## 7. Distribución y comandos

- **Formato**: ejecutable portátil de Windows, publicado en GitHub Releases. (El nombre final del binario y la organización de GitHub quedan **por definir**; no se fijan aquí.)
- **Prerrequisito**: Codex Desktop está **preinstalado y autenticado** en la máquina destino; el producto no instala ni autentica Codex. (La versión mínima de Codex queda **por definir**.)
- **Firma**: no hay infraestructura de firma de código en el MVP; la integridad se cubre solo con SHA-256.

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
{ "path": "marco/fases/fase_0_concepto_y_factibilidad.md", "sha256": "<hash>" }
  ]
}
```

> `version` y `released_at` son ilustrativos. `codex_min_version: null` marca que la versión mínima de Codex está por definir.

### 9.2 Artefactos de release

| Artefacto | Rol |
| --- | --- |
| `<binario>.exe` | Ejecutable portátil de Windows (nombre por definir). |
| `manifest.json` | Versión y hashes de los archivos gestionados. |
| `hashes.sha256` | Lista `sha256  ruta` de los artefactos de la release. |
| `NOTES.md` | Notas de release y cambios. |

## 10. Responsabilidad del adaptador Codex y frontera harness-neutral

- **Adaptador**: traduce contratos canónicos (`AGENTS.md` + catálogo) a artefactos Codex (`.agents/skills/`, `.codex/agents/*.toml`, `.codex/config.toml`). Es un mapeo ejecutable, nunca una autoridad de significado.
- **Progressive disclosure**: las skills se cargan en tres niveles — metadata (`name`/`description`), instrucciones (`SKILL.md`) y recursos bajo demanda — para reducir consumo de contexto.
- **Frontera de dominio**: el dominio (`marco/`) permanece harness-neutral. Codex no evalúa disparadores de fase nativamente; el agente lee el estado del proyecto, selecciona la capacidad según el catálogo y enruta. Ningún artefacto Codex redefine el dominio.
- **No duplicar reglas de dominio en TOML**: la configuración Codex expone mecanismos, no re-escribe el proceso.

## 11. Slice vertical del MVP y criterios de aceptación medibles

### Slice vertical

1. Un contrato de fase canónico (p. ej. `F0`).
2. Una skill de fase mapeada a una capacidad del catálogo.
3. Un adaptador que genera `.codex/config.toml` + un agente.
4. `init --harness codex --target .` instala la superficie gestionada y escribe el manifiesto.
5. `update` corre transaccionalmente y deja `proyecto/` byte a byte sin cambios.

### Criterios de aceptación medibles

- [ ] `init` produce la superficie gestionada y el manifiesto; `doctor` pasa sin observaciones.
- [ ] `update` sin deriva local actualiza la versión del manifiesto al final.
- [ ] `update` con deriva local en un archivo gestionado **bloquea** y reporta las diferencias; no sobrescribe.
- [ ] `update` con SHA-256 que no coincide **falla cerrado** y deja los archivos gestionados previos intactos.
- [ ] `proyecto/` permanece **byte a byte idéntico** durante `update`: se calcula un hash recursivo del árbol `proyecto/` antes y después y se exige igualdad.
- [ ] `doctor` detecta Codex Desktop ausente y lo reporta.
- [ ] Existe un único contrato semántico de `AGENTS.md`; la copia instalada es idéntica a la fuente canónica.

## 12. Plan de migración del repositorio

Precondición y pasos, en orden:

1. **Preservar el trabajo no confirmado de `proyecto-base` primero.** Antes de cualquier movimiento, confirmar o capturar en snapshot los cambios sin confirmar actuales (rama `feature/orchestrator`). Ninguna operación destructiva (`reset`, `clean`, `checkout` forzado).
2. **Crear el repo nuevo** `systems-engineering-framework-agent` (vacío).
3. **Copiar los activos canónicos** desde `proyecto-base`: `marco/`, el `AGENTS.md` de raíz, el catálogo (`guias/skill-registry*.md` → `catalogo/`) y las guías relevantes (`guias/*` → `docs/`).
4. **Establecer el árbol fuente del producto** (sección 5.1): `skills/`, `adapter/codex/`, `agent/`, `manifest/`, `tests/`, `docs/`.
5. **Verificar fuente única.** Tras la copia, el marco y `AGENTS.md` se editan **solo** en el repo de producto. En `proyecto-base`, `/marco` y `AGENTS.md` pasan a ser copias instaladas gestionadas; no quedan dos fuentes editables.
6. **Configurar `proyecto-base` como fixture de aceptación**: ejecutar `init`/`update` contra una copia para validar que la instalación produce los archivos gestionados sin tocar `proyecto/`.
7. **Confirmar sin submódulos**: un único repo de producto; el consumidor recibe copias gestionadas.
8. **Transferir el contexto semántico de Engram** mediante el procedimiento de la sección 13; no copiar memorias sin verificarlas contra este documento y las fuentes Markdown.

## 13. Recuperación de decisiones desde Engram en el nuevo repositorio

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

> Los nombres y parámetros exactos de las herramientas deben confirmarse contra la integración Engram disponible en la nueva sesión. Si Engram no está disponible, el arranque continúa con este documento y el Markdown versionado; la memoria es suplementaria.

### Memorias de arranque conocidas

| ID en `proyecto-base` | `topic_key` | Uso al iniciar el repo nuevo |
| --- | --- | --- |
| `2162` | `architecture/mvp-distribution-boundaries` | Contexto de los tres subsistemas y fronteras iniciales. |
| `2163` | `architecture/sharepoint-approval-sync` | Contexto futuro, fuera del MVP, sobre SharePoint y aprobaciones. |
| `2164` | `architecture/mvp-scope` | Alcance exclusivo del MVP framework-agent. |
| `2165` | `architecture/mvp-distribution-contract` | `/marco` gestionado, propiedad de `AGENTS.md` y EXE portátil. |
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

### Decisiones ya resueltas (no abiertas)

Ejecutable portátil, GitHub Releases, `/marco` gestionado, propiedad total de `AGENTS.md`, manifiesto/hashes, comando `update`, sin migraciones de proyecto, sin submódulos, `proyecto-base` como fixture de aceptación, y RAG/SharePoint/Power Automate fuera del MVP.

### Únicamente pendientes (no se inventan)

| Dato pendiente | Por qué queda abierto |
| --- | --- |
| Lenguaje de implementación del agente | No se decide aquí. |
| Organización de GitHub | No se fija. |
| Nombre final del binario | Se usa `<binario>` hasta definirlo. |
| Versión mínima de Codex | Se marca `null`/por definir. |
| Infraestructura de firma de código | Fuera del MVP; SHA-256 es solo integridad. |

## 15. Checklist inmediato para crear el nuevo repo

- [ ] Confirmar/snapshot del trabajo no confirmado de `proyecto-base`.
- [ ] Crear `systems-engineering-framework-agent` (vacío).
- [ ] Copiar `marco/` y `AGENTS.md` como fuente canónica.
- [ ] Reubicar catálogo y guías relevantes en `catalogo/` y `docs/`.
- [ ] Recuperar y verificar las memorias Engram de arranque; guardarlas de forma curada bajo el proyecto nuevo.
- [ ] Crear `skills/`, `adapter/codex/`, `agent/`, `manifest/`, `tests/`.
- [ ] Fijar el esquema de manifiesto (`framework-agent.manifest/v1`) y la generación de hashes.
- [ ] Implementar `init`, `update`, `doctor`, `version` con la transacción fail-closed.
- [ ] Añadir la prueba byte a byte de `proyecto/`.
- [ ] Configurar el build y la publicación del EXE portátil en GitHub Releases.

## 16. Referencias (rutas relativas al repositorio)

- `AGENTS.md` — contrato de runtime actual (fuente que migra al repo de producto).
- `README.md` — descripción de la plantilla.
- `marco/README.md` — contenido del dominio.
- `guias/arquitectura-orquestador.md` — capas del orquestador (referencia de fronteras).
- `guias/frontera-dominio-harness.md` — autoridad y dirección de dependencias.
- `guias/memoria-dual.md` — política de persistencia/autoridad.
- `guias/quickstart-agentes.md` — flujo mínimo del orquestador.
- `guias/reestructuracion-agents.md` — decisión canónica de contrato único de `AGENTS.md`.
- `guias/skill-registry-v2.md` — catálogo canónico de capacidades.
- `implementacion/tradeoff-cdex-pi-infraestructura-agent.md` — análisis Codex vs Pi y superficie de extensión de Codex.
- `implementacion/diagrama-mvp.png` — ideación histórica (superada en lo que difiera de este documento).
- `proyecto/estado/proyecto_actual.md`, `proyecto/estado/estado_fases.md`, `proyecto/hitos/hito_aprobacion_trabajo.md` — estado autoritativo actual (fixture).
