---
document_type: prd
language: es
version: 1.0
status: aprobada
prd_id: PRD-1
---

# PRD 1 — `se-agent`: scaffolder one-shot para Codex

**Resultado esperado:** un usuario ejecuta `pipx install <zip-de-tag>`, luego `se-agent init --harness codex --target .` dentro de un proyecto, y obtiene el marco de ingeniería de sistemas, el contrato `AGENTS.md`, el registry de skills y los artefactos Codex instalados y **de su propiedad absoluta**. No hay manifiesto, no hay actualizador, no hay copias gestionadas: la herramienta es un **scaffolder de una sola ejecución** que escribe un conjunto de archivos declarado y desaparece de la ecuación.

> **Alcance de este documento.** Este PRD fija requisitos y comportamiento observable del MVP. No es un diseño de implementación: no elige librerías, ni estructura interna de código, ni protocolos internos. Donde contradice documentación anterior, **este PRD es la autoridad de requisitos**; los documentos activos se conciliaron para dejar de describir el modelo anterior (sección 12).

## Ruta rápida de revisión

1. **Lea primero:** la tabla de decisiones (siguiente sección) y los no-objetivos (§3).
2. **Verifique el contrato duro:** la tabla fuente→destino del payload (§7) y las reglas de frontera de escritura (§8).
3. **Verifique el comportamiento:** protocolo de colisiones y fallos (§9), criterios de aceptación medibles (§10).
4. **Cierre:** riesgos (§13) y estado de la conciliación documental (§12).

## 1. Decisiones ejecutivas

| Punto | Decisión aprobada |
| --- | --- |
| Nombre de producto/CLI | `se-agent` |
| Módulo Python | `se_agent` |
| Lenguaje e implementación | Python, `>=3.12` |
| Distribución | `pipx` instala el ZIP expuesto automáticamente por un tag SemVer inmutable de GitHub. **Sin PyPI, sin EXE portátil** en el MVP. |
| URL de GitHub | `https://github.com/JuanJo-Saavedra/systems-engineering-framework-agent` |
| Modelo de instalación | One-shot: `se-agent init --harness codex --target .` instala el payload y **termina**. Los archivos instalados pasan a ser 100 % propiedad del consumidor. |
| Comandos en MVP | `init` y `--version` únicamente. |
| Manifiesto / hashes / doctor / update / migración / detección de deriva / generador de registry | **Ninguno existe en el MVP.** |
| Registry de skills | Mantenido **manualmente** por los autores del producto en `runtime/catalogo/skill-registry.md`; sin comando de build. CI solo verifica coherencia. |
| Harness | Solo Codex (slice vertical completo). Los contratos de dominio permanecen harness-neutrales. |
| Frontera de escritura | Solo los archivos del payload declarado (§7) se crean o sobrescriben explícitamente. Todo lo demás es intocable, en especial `proyecto/`. |

### 1.1 Sustitución explícita de la documentación vigente

Este PRD, aprobado, **sustituye** los siguientes supuestos del MVP anterior. Los documentos afectados fueron conciliados para dejar de describirlos (ver §12).

| Supuesto vigente (docs actuales) | Reemplazado por PRD 1 |
| --- | --- |
| Ejecutable portátil de Windows vía GitHub Releases (`product.md` v2.2, `README.md`) | Distribución Python vía `pipx` + ZIP de tag GitHub |
| Copias gestionadas read-only, deriva bloquea actualización (`product.md` §6, `agents-contract.md` v2.1) | Archivos consumidor-propietarios desde el momento posterior a `init` |
| Comandos `update` / `doctor` y manifiesto + SHA-256 (`product.md` §7–9) | Fuera del MVP; no existen |
| Registry operativo "generado — no editar manualmente" (`skill-artifacts.md` v1.0, cabecera de `runtime/catalogo/skill-registry.md`) | Registry **mantenido a mano**; CI verifica coherencia, nunca edita |
| Instalador en `installer/windows/` con transacción fail-closed | Instalador Python one-shot con preflight (§9); el empaquetado portable queda obsoleto |

## 2. Problema y usuario

Los equipos que adoptan el marco de ingeniería de sistemas necesitan arrancar un proyecto con el proceso, el contrato de agente y las skills ya en su repositorio, sin instalar agentes residentes, sin registrar el proyecto en ningún lado y sin depender de que una herramienta siga presente para que el proyecto funcione. El valor entregado es el **andamiaje**: después de `init`, el proyecto es un repositorio normal cuyo único acoplamiento es que sus archivos instalados describen el proceso a seguir.

**Usuario objetivo:** un ingeniero líder que crea (o adopta) un repositorio de proyecto y quiere el marco operativo en menos de cinco minutos, con Codex ya instalado y autenticado en su máquina.

## 3. Alcance y no-objetivos

### Alcance del MVP (slice vertical completo de Codex)

1. Paquete Python `se_agent` con CLI `se-agent`, distribuible vía `pipx`.
2. Payload completo del marco + dominio instalado en el destino (§7).
3. Contrato `AGENTS.md` canónico instalado en la raíz del destino.
4. Registry de skills mantenido manualmente, con verificación de coherencia bidireccional en CI.
5. Una skill F0 **funcional** en runtime (no un placeholder).
6. Artefactos del adaptador Codex (config, agentes) instalados en `.codex/`.
7. Protocolo de colisiones, frontera de escritura estricta y preflight antes de la primera escritura.

### No-objetivos explícitos del MVP

| No-objetivo | Nota |
| --- | --- |
| `update`, `doctor`, `uninstall`, migraciones | No existen como comandos. `init` re-ejecutado se comporta según §9. |
| Manifiesto, hashes, `.framework-agent/` | No se escribe ningún registro de instalación en el destino. |
| Detección de deriva / copias gestionadas | Los archivos instalados son del consumidor; nadie los vigila después. |
| Generador del registry (comando de build) | El registry se edita a mano; solo hay verificación en CI. |
| CI que modifica el repositorio | CI **solo** ejecuta verificaciones y tests; jamás escribe en el repo. |
| PyPI | La distribución es exclusivamente el ZIP del tag de GitHub. |
| EXE portátil de Windows | Sustituido por la distribución Python; el enfoque `installer/windows/` queda obsoleto. |
| Más harnesses | Solo Codex. |
| Modificar `proyecto/` o cualquier contenido fuera del payload | Prohibición absoluta, incluso con `--force`. |

## 4. Journey del usuario (camino feliz)

1. El usuario tiene Codex instalado y autenticado (prerrequisito; el producto no instala ni autentica Codex).
2. Desde la raíz de su repositorio de proyecto, ejecuta:

   ```bash
   pipx install 'se-agent @ https://github.com/JuanJo-Saavedra/systems-engineering-framework-agent/archive/refs/tags/vX.Y.Z.zip'
   se-agent --version        # imprime X.Y.Z
   se-agent init --harness codex --target .
   ```

3. La herramienta valida el plan completo (destino, rutas, colisiones) **antes de escribir nada**.
4. Si no hay colisiones: escribe exactamente los archivos del payload (§7), imprime un resumen de lo instalado (rutas creadas), y termina con código 0.
5. El usuario abre Codex en el repositorio; `AGENTS.md`, `marco/`, `catalogo/skill-registry.md`, `.agents/skills/` y `.codex/` están en su lugar, y `proyecto/` (si existe) está byte a byte intacto.
6. Fin de la interacción con la herramienta. El proyecto pertenece al consumidor.

## 5. Requisitos funcionales

| ID | Requisito |
| --- | --- |
| RF-1 | `se-agent --version` imprime la versión SemVer del paquete, idéntica a la de `pyproject.toml` y al tag de publicación. |
| RF-2 | `se-agent init --harness codex --target <dir>` instala el payload completo (§7) en `<dir>`. `--harness` solo acepta `codex` en el MVP. |
| RF-3 | Antes de la primera escritura, la herramienta calcula y valida el **plan completo** de escrituras (rutas origen→destino, colisiones, seguridad de rutas). Cualquier fallo de validación ⇒ **cero escrituras**. |
| RF-4 | Solo los archivos del payload pueden crearse o sobrescribirse explícitamente. Ningún otro archivo o directorio del destino se crea, modifica, mueve ni elimina. |
| RF-5 | Colisiones se detectan y listan completas antes de escribir (protocolo §9). |
| RF-6 | El registry instalado (`catalogo/skill-registry.md`) es copia exacta del registry fuente mantenido a mano. |
| RF-7 | Las skills instaladas en `.agents/skills/` corresponden 1:1 con las skills presentes en `runtime/skills/` en el momento de publicación. |
| RF-8 | Los artefactos Codex (`.codex/config.toml`, `.codex/agents/*.toml`) se instalan desde `adapters/codex/` y exponen mecanismos, sin redefinir reglas de dominio. |
| RF-9 | La herramienta no requiere conexión a red durante `init` (todo el payload viaja dentro del paquete instalado). |
| RF-10 | Al terminar con éxito, imprime la lista de rutas instaladas. No escribe ningún archivo extra de estado (sin manifiesto, sin caché, sin lockfile). |

## 6. Requisitos no funcionales

| ID | Requisito |
| --- | --- |
| RNF-1 | Python `>=3.12`; instalable con `pipx` sin pasos manuales adicionales. |
| RNF-2 | `init` en un proyecto limpio termina en segundos; no descarga nada en runtime. |
| RNF-3 | Resolución de destinos segura: se rechazan escapes por `..`, rutas absolutas fuera del target y symlinks que apunten fuera del árbol destino. |
| RNF-4 | Fallos son explícitos: código de salida distinto de cero y mensaje que nombre el archivo o la regla violada. Nunca un fallo silencioso ni una escritura parcial tras un preflight fallido. |
| RNF-5 | El payload es determinista: dado el mismo tag, dos ejecuciones de `init` sobre destinos equivalentes producen bytes idénticos. |

## 7. Payload: contrato de escritura (fuente → destino)

Tabla derivada de las rutas canónicas vigentes del repositorio de producto. **No se inventan archivos**: los orígenes listados existen hoy, salvo los marcados como "por crear", cuya creación es parte de este slice vertical.

| # | Fuente canónica (repo producto) | Destino en consumidor | Estado de la fuente | Regla |
| --- | --- | --- | --- | --- |
| 1 | `framework/marco/**` (15 archivos: `README.md`, `glosario.md`, `reglas_del_ciclo.md`, `fases/README.md`, `fases/fase_0..8_*.md`, `reviews/catalogo_reviews.md`, `baselines/catalogo_baselines.md`) | `marco/**` (misma estructura relativa) | Existente | Copia exacta, recursiva |
| 2 | `runtime/AGENTS.md` | `AGENTS.md` (raíz del destino) | Existente | Copia exacta |
| 3 | `runtime/catalogo/skill-registry.md` | `catalogo/skill-registry.md` | Existente (reformateado a mantenimiento manual, §12) | Copia exacta |
| 4 | `runtime/skills/<skill>/SKILL.md` | `.agents/skills/<skill>/SKILL.md` | **Por crear**: exactamente una skill F0 funcional en el MVP | Copia por skill; el nombre de directorio de la skill se fija al implementarla |
| 5 | `adapters/codex/config.toml` | `.codex/config.toml` | **Por crear** (ya declarado como destino en `product.md` §5–6) | Copia exacta |
| 6 | `adapters/codex/agents/*.toml` | `.codex/agents/*.toml` | **Por crear**: al menos un agente en el MVP | Copia exacta |

Exclusiones explícitas (no forman parte del payload, con la razón):

| Ruta fuente | ¿Se instala? | Razón |
| --- | --- | --- |
| `framework/guias/**` | No | Base de diseño del producto, no artefacto de consumo (decisión vigente que PRD 1 conserva). |
| `runtime/agents/**` | No | Contratos harness-neutrales **sin destino de instalación definido** en la documentación vigente; no se inventa uno. Conciliación en §12. |
| `.atl/**` | No | Índice técnico de desarrollo; nunca se empaqueta. |
| `docs/**`, `tests/**`, `installer/**`, `release/**` | No | Del repo de producto, no del consumidor. |
| `.framework-agent/` | No existe | PRD 1 elimina el manifiesto; no se escribe ningún directorio de estado. |

**Contrato del write-set:** el conjunto exacto de rutas destino que `init` tiene permiso de crear/sobrescribir es la unión de los destinos de la tabla §7. Cualquier intento de escritura fuera de ese conjunto es un bug de la herramienta, no un comportamiento aceptable.

## 8. Frontera de escritura estricta

Reglas duras, verificables por test:

1. **Lista blanca.** Solo destinos declarados en §7 pueden crearse o sobrescribirse.
2. **`proyecto/` intocable.** Ninguna operación, en ningún modo (incluido `--force`), lee con intención de escribir, crea, modifica ni elimina nada bajo `proyecto/`.
3. **Resolución segura de destinos.** Cada destino se resuelve contra la raíz del target. Se rechaza con error duro: `..` que escape de la raíz destino, rutas absolutas fuera del target, y symlinks (preexistentes o creados por el plan) cuyo objetivo quede fuera del árbol destino.
4. **Nunca se elimina ni limpia** contenido no perteneciente al write-set. `init` no "ordena" el destino.
5. **`--force` no compra privilegios.** `--force` solo autoriza sobrescribir colisiones declaradas en el write-set (§9). Jamás autoriza salirse del write-set, saltarse la resolución segura ni tocar `proyecto/`.

## 9. Colisiones, interactividad y comportamiento ante fallo

### 9.1 Protocolo de colisiones

| Paso | Comportamiento observable |
| --- | --- |
| Detección | Se calcula la lista **completa** de rutas destino que ya existen antes de la primera escritura. |
| Sin colisiones | Procede sin preguntar. |
| Con colisiones, sesión interactiva | Se listan **todas** las rutas en conflicto y se pregunta `[y/N]`. Solo `y`/`yes` (insensible a mayúsculas) procede; cualquier otra respuesta o EOF aborta con **cero escrituras**. |
| Con colisiones, sesión no interactiva (sin TTY) | **Aborta** con código distinto de cero, lista las colisiones y sugiere `--force`. |
| Con colisiones + `--force` | Sobrescribe únicamente las rutas en conflicto **dentro del write-set**; las protecciones de §8 siguen plenamente vigentes. |

### 9.2 Preflight y fallo durante la escritura

- **Preflight total antes de la primera escritura (RF-3):** destino válido, todas las rutas del plan resueltas con seguridad, todas las colisiones resueltas (o abortadas). Un plan inválido ⇒ error y **cero escrituras**.
- **Fallo de escritura a mitad de ejecución** (p. ej. permisos, disco lleno): la herramienta se detiene en el primer error, **no intenta revertir ni borrar** lo ya escrito (esos archivos ya son del consumidor), reporta cuáles rutas quedaron escritas y cuáles del plan faltan, y termina con código distinto de cero. El usuario puede re-ejecutar `init` (las rutas ya escritas se tratarán como colisiones según §9.1).
- **Nunca** se deja un estado donde la herramienta afirme éxito con escrituras pendientes del plan.

## 10. Criterios de aceptación medibles

Verificación en el MVP (por dónde se demuestra cada criterio: manual para la experiencia de instalación, automatizado para contratos):

| ID | Criterio | Verificación |
| --- | --- | --- |
| AC-1 | `pipx install <url-zip-de-tag-vX.Y.Z>` instala la CLI `se-agent` funcional; `se-agent --version` imprime `X.Y.Z`. | Manual sobre un tag real de prueba |
| AC-2 | `X.Y.Z` de `se-agent --version` == versión en `pyproject.toml` == tag `vX.Y.Z` publicado. | Test automatizado + checklist de release |
| AC-3 | `init` sobre un destino vacío crea **exactamente** la expansión publicada del payload de §7 (15 archivos de marco + `AGENTS.md` + registry + skills + artefactos Codex) y **ninguna** otra ruta. | Test de integración que compara el árbol completo contra el payload de la versión |
| AC-4 | `init` sobre un fixture con `proyecto/` poblado deja `proyecto/` **byte a byte idéntico** (hash recursivo antes/después). | Test de integración |
| AC-5 | `init` no crea manifiesto, `.framework-agent/`, ni ningún archivo fuera del write-set. | Test de integración |
| AC-6 | Colisión con respuesta `N` (o EOF) ⇒ código ≠ 0 y cero escrituras (comparación de árbol completa). | Test de integración |
| AC-7 | Colisión en modo no interactivo sin `--force` ⇒ código ≠ 0, lista de colisiones en stderr, cero escrituras. | Test de integración |
| AC-8 | `--force` sobrescribe solo las colisiones del write-set; un plan que intente escribir fuera del write-set, escapar por `..`/symlink, o tocar `proyecto/` falla con error duro **incluso con `--force`**. | Tests unitarios + integración |
| AC-9 | Plan inválido (cualquier causa) ⇒ cero escrituras (árbol destino invariado). | Test de integración |
| AC-10 | Coherencia registry↔skills (§11): cada skill de `runtime/skills/` tiene exactamente una entrada correcta; cada entrada resuelve y el nombre coincide; duplicados, faltantes y entradas obsoletas hacen fallar la verificación. | Tests automatizados |
| AC-11 | CI ejecuta solo verificación/tests y no modifica el repositorio. | Revisión de configuración de CI |
| AC-12 | La skill F0 instalada es funcional: guía la ejecución de la fase F0 según el contrato `AGENTS.md`, el documento de fase `marco/fases/fase_0_concepto_y_factibilidad.md` y la capacidad `f0_factibilidad` definida en `framework/guias/skill-architecture.md` (sección `Capacidades por fase`), sin referencias rotas a recursos inexistentes. | Revisión manual + test de integridad de referencias |

## 11. Registry de skills: mantenimiento manual y verificación

| Punto | Decisión |
| --- | --- |
| Fuente | `runtime/catalogo/skill-registry.md`, editado **a mano** por los autores del producto. |
| Generación | Ninguna. No existe comando de build del registry. |
| Verificación (bidireccional) | 1) Toda skill bajo `runtime/skills/*/SKILL.md` tiene **exactamente una** entrada en el registry con nombre y ruta correctos. 2) Toda entrada del registry resuelve a una skill existente y su nombre coincide. |
| Rechazos | Entradas duplicadas, skills sin entrada (faltantes) y entradas sin skill (obsoletas) **fallan** la verificación. |
| Momento | La verificación corre en tests y CI sobre el repo de producto; también se satisface trivialmente en el consumidor porque `init` instala skills y registry del mismo tag. |
| CI | Solo ejecuta verificación y tests. **CI nunca edita el repositorio** (sin regeneración, sin commits automáticos). |

## 12. Trabajo de seguimiento: conciliación documental (explícito, no silencioso)

Con la aprobación de este PRD, la conciliación documental quedó definida. Las filas 1–5 se **aplicaron** (documentación activa reconciliada); las filas 6–8 quedan como **seguimiento abierto**, con su propio cambio revisable:

| # | Documento | Cambio requerido |
| --- | --- | --- |
| 1 | `docs/architecture/product.md` | ✅ Conciliado: v3.0 supersede la v2.2 — distribución pipx/ZIP de tag, modelo one-shot, eliminación de manifiesto/hashes/`update`/`doctor`/deriva, registry manual, árbol instalado sin `.framework-agent/`. |
| 2 | `README.md` | ✅ Conciliado: EXE portátil sustituido por el modelo PRD 1. |
| 3 | `docs/decisions/agents-contract.md` | ✅ Conciliado: cláusula "deriva local bloquea la actualización" retirada; la propiedad pasa al consumidor tras `init`. |
| 4 | `docs/decisions/skill-artifacts.md` | ✅ Conciliado: registry operativo reclasificado de "generado" a "mantenido manualmente con verificación CI". |
| 5 | `runtime/catalogo/skill-registry.md` | ✅ Conciliado: cabecera actualizada a mantenimiento manual. El contenido se puebla al implementar la skill F0 (implementation pending). |
| 6 | `runtime/agents/` | Decidir destino (instalado o no) de los contratos harness-neutrales; hoy sin resolución, excluido del payload §7. |
| 7 | Publicación | ✅ URL GitHub real definida: `https://github.com/JuanJo-Saavedra/systems-engineering-framework-agent`. Pendiente: crear el tag inmutable `v0.1.0` y ejecutar la verificación manual de AC-1/AC-2 (§10, checklist de release). |
| 8 | Soporte de SO | Confirmar la matriz de sistemas operativos objetivo de la CLI (pipx es multiplataforma; los docs previos asumían Windows). |

## 13. Riesgos

| Riesgo | Mitigación |
| --- | --- |
| Documentación activa que contradiga este PRD | La conciliación documental (§12, filas 1–5) se aplicó; cualquier contradicción residual es un defecto a corregir. Filas 6–8 quedan como seguimiento abierto explícito. |
| Sin deriva ni manifiesto, un consumidor puede editar archivos instalados y desalinearse del marco | Aceptado por diseño (one-shot): el proyecto es del consumidor. La re-instalación con `init` + colisiones explícitas es el único mecanismo de refresco. |
| URL de GitHub sin definir (resuelto) | La URL real ya está definida (§1) y ya no es bloqueante. AC-1/AC-2 siguen pendientes únicamente hasta que exista el tag `v0.1.0` y se ejecute la verificación manual. |
| `init` re-ejecutado sobre un proyecto ya scaffoldeado dispara colisiones masivas | Comportamiento definido en §9 (listado completo, `[y/N]`, `--force`); no se implementan diff ni migración en MVP. |
| Versión mínima de Codex sin definir | Queda como prerrequisito documental ("preinstalado y autenticado"), igual que en los docs vigentes. |
| Escapes de ruta vía symlink preexistente en el destino | RNF-3 + AC-8 con tests dedicados. |

## 14. Checklist de aprobación

Aprobado por el líder del producto.

- [x] La tabla de decisiones (§1) refleja exactamente lo aprobado.
- [x] Los no-objetivos (§3) cubren todo lo que el MVP anterior prometía y este PRD retira.
- [x] La tabla payload (§7) solo contiene rutas canónicas existentes o declaradas como "por crear" del slice.
- [x] Las protecciones de §8 se consideran suficientes (especialmente `proyecto/` y `--force`).
- [x] El plan de conciliación (§12) se acepta como trabajo de seguimiento (filas 1–5 aplicadas; 6–8 abiertas).

## 15. Referencias

- `docs/architecture/product.md` — arquitectura vigente a conciliar (§12, fila 1).
- `docs/decisions/agents-contract.md`, `docs/decisions/skill-artifacts.md` — decisiones vigentes a conciliar (§12, filas 3–4).
- `framework/marco/` — dominio canónico (fuente del payload).
- `runtime/AGENTS.md` — contrato de runtime canónico (fuente del payload).
- `runtime/catalogo/skill-registry.md` — registry operativo (fuente del payload, mantenimiento manual).
- `adapters/codex/` — artefactos Codex (fuente del payload, por poblar).
