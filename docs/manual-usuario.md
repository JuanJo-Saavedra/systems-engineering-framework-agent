---
document_type: manual_usuario
language: es
version: 1.1.0
status: propuesta
compatible_package_version: 0.1.1
last_updated: 2026-08-31
---
# Manual de usuario — `se-agent` (Windows)

Este manual le enseña, paso a paso y sin suponer experiencia previa, a instalar y usar `se-agent` en **Windows** con PowerShell. `se-agent` es un **scaffolder de una sola ejecución** (one-shot): instala un conjunto de archivos del marco de ingeniería de sistemas en su proyecto y termina; los archivos instalados pasan a ser **100 % suyos**. No hay manifiesto, no hay actualizador, no hay registros ocultos.

> **Alcance.** Este manual documenta la versión del paquete **0.1.1** (tag `v0.1.1`). Otros sistemas operativos no están cubiertos aquí. No necesita saber programar en Python para seguirlo: solo copiar y pegar comandos en PowerShell.

## Historial de cambios

| Versión del documento | Fecha | Cambios |
| --- | --- | --- |
| 1.1.0 | 2026-08-31 | Agrega el Modo C: clonar un tag del repositorio e instalarlo localmente con pipx. |
| 1.0.0 | 2026-08-31 | Primera versión: instalación por pipx (vía pública ZIP y vía privada SSH), uso de `init`, colisiones, códigos de salida, solución de problemas. Compatible con paquete 0.1.1. |

---

## Ruta rápida

Si solo quiere el resultado, siga estos cinco pasos (cada uno se explica en detalle después):

1. Instale **Python 3.12 o superior** desde [python.org](https://www.python.org/downloads/windows/) marcando la casilla *"Add python.exe to PATH"*.
2. Instale **pipx** y habilite su ruta: `py -m pip install --user pipx` y luego `py -m pipx ensurepath`. Cierre y reabra PowerShell.
3. Instale `se-agent` desde el tag de la versión (elija la vía según cómo accede su máquina al repositorio — vea el detalle en el [Paso 5](#paso-5--instalar-se-agent-tres-modos)):

   - **Vía pública (ZIP del tag; no requiere SSH):**

     ```powershell
     pipx install 'se-agent @ https://github.com/JuanJo-Saavedra/systems-engineering-framework-agent/archive/refs/tags/v0.1.1.zip'
     ```

   - **Vía privada directa (si el repositorio es privado o su acceso exige SSH):**

     ```powershell
     pipx install 'se-agent @ git+ssh://git@github.com/JuanJo-Saavedra/systems-engineering-framework-agent.git@v0.1.1'
     ```

   - **Vía local (clonar primero e instalar manualmente):**

     ```powershell
     git clone git@github.com:JuanJo-Saavedra/systems-engineering-framework-agent.git
     cd systems-engineering-framework-agent
     git checkout v0.1.1
     pipx install .
     ```

4. Verifique la instalación:

   ```powershell
   se-agent --version
   ```

   Debe imprimir exactamente `0.1.1`.
5. Desde la raíz de su proyecto, instale el marco:

   ```powershell
   se-agent init --harness codex --target .
   ```

Si los cinco pasos funcionaron, ya terminó: `se-agent` escribió los archivos del marco y desapareció de la ecuación. El resto de este manual explica cada paso, qué hacer si algo falla y qué esperar exactamente de cada comando.

---

## Prerrequisitos

| Requisito | Detalle |
| --- | --- |
| Sistema operativo | Windows 10 u 11 (este manual cubre solo Windows). |
| Terminal | PowerShell (viene incluido en Windows). |
| Python | Versión **3.12 o superior**. Se explica cómo instalarlo abajo. |
| pipx | Instalador de aplicaciones Python aisladas. Se explica cómo instalarlo abajo. |
| Git | Necesario para los modos B y C. Instálelo desde [git-scm.com/download/win](https://git-scm.com/download/win/) y verifique con `git --version`. |
| Codex | Debe estar **ya instalado y autenticado** si piensa usar los artefactos `.codex/` que `se-agent` instala. `se-agent` **no** instala ni autentica Codex; solo copia sus archivos de configuración. |
| Conexión a red | Solo durante la instalación del paquete. `se-agent init` funciona **sin conexión**: todo viaja dentro del paquete instalado. |

---

## Paso 1 — Instalar Python 3.12 o superior de forma segura

### De dónde descargarlo

Descargue el instalador **solo desde el sitio oficial**: [https://www.python.org/downloads/windows/](https://www.python.org/downloads/windows/). Elija la última versión estable **3.12 o mayor** (por ejemplo, 3.12.x o 3.13.x). Evite instaladores de terceros o enlaces reenviados.

### Instalación

1. Ejecute el instalador descargado.
2. **Importante:** en la primera pantalla, marque la casilla **"Add python.exe to PATH"** antes de pulsar *Install Now*. Sin ella, Windows no encontrará `py` ni `python` en la terminal.
3. Espere a que termine y pulse *Close*.

### Verificación

Abra **una ventana nueva de PowerShell** y ejecute:

```powershell
py --version
python --version
```

Ambos deben imprimir algo como `Python 3.12.6` (el número exacto puede variar; lo que importa es que sea **3.12 o mayor**).

### ¿Cuál es la diferencia entre `py` y `python`?

| Comando | Qué es |
| ---------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `py` | El**Python launcher** de Windows. Un pequeño programa que busca e invoca la versión de Python que tenga instalada. Es la forma recomendada de llamar a Python en Windows. |
| `python` | El intérprete directamente. Funciona igual, pero depende de que la casilla*"Add python.exe to PATH"* se haya marcado en la instalación. |

En este manual usamos `py` porque es el más fiable en Windows. Si `py --version` falla pero `python --version` funciona, puede sustituir `py` por `python` en los comandos de instalación de pipx.

---

## Paso 2 — Entornos virtuales: el concepto (y por qué pipx le ahorra uno)

### Qué es un entorno virtual

Un **entorno virtual** (virtual environment o *venv*) es una carpeta con su propia copia aislada de Python y sus propias librerías. Sirve para que las herramientas de un proyecto no mezclen sus dependencias con las de otro proyecto ni con las del sistema. Es como una caja de herramientas por proyecto: lo que instala en una caja no ensucia las demás.

Con Python puro, los tres comandos básicos en PowerShell son:

```powershell
# Crear un entorno virtual en la carpeta .venv del proyecto actual
py -m venv .venv

# Activarlo (PowerShell)
.venv\Scripts\Activate.ps1

# Desactivarlo (cuando termine)
deactivate
```

Cuando un entorno está activado, el indicador de la terminal muestra `(.venv)` al inicio y todo lo que instale con `pip` queda dentro de esa carpeta.

### Lo importante para usted: con pipx NO necesita crear entornos virtuales

**pipx gestiona sus propios entornos aislados automáticamente.** Cada aplicación que instala con `pipx` (como `se-agent`) vive en su propio entorno virtual privado, creado y administrado por pipx sin que usted haga nada. Usted **no** necesita ejecutar `py -m venv`, ni activar nada, ni preocuparse por aislamiento: pipx ya lo resuelve.

Los comandos de la sección anterior (`py -m venv ...`) se incluyen solo para que **entienda el concepto**; no son parte del flujo de instalación de `se-agent`. Regla práctica: **librerías** de un proyecto → entornos virtuales a mano; **aplicaciones** de línea de comandos → pipx, sin pasos extra.

---

## Paso 3 — Instalar, actualizar y verificar pipx

### Instalación

En PowerShell:

```powershell
py -m pip install --user pipx
py -m pipx ensurepath
```

- El primer comando instala pipx en su perfil de usuario (sin necesitar permisos de administrador).
- `pipx ensurepath` agrega la carpeta donde pipx pone los ejecutables a su `PATH`.

Después de `ensurepath`, **cierre y vuelva a abrir PowerShell** para que el nuevo `PATH` surta efecto.

### Verificación

```powershell
pipx --version
pipx list
```

`pipx --version` debe imprimir un número de versión. `pipx list` muestra las aplicaciones instaladas con pipx (al principio estará vacía; después de instalar `se-agent` aparecerá ahí).

### Actualización de pipx

```powershell
py -m pip install --user --upgrade pipx
```

---

## Paso 4 (opcional) — Preparar SSH para GitHub

Esta sección es necesaria para el **Modo B** y para el **Modo C tal como está escrito**, porque ambos usan una URL SSH de GitHub. Si usa el Modo A (ZIP público), puede saltarla por completo.

### Concepto

SSH le permite a su máquina demostrar a GitHub **quién es usted** mediante un par de claves criptográficas: una **clave privada** (que nunca sale de su computadora) y una **clave pública** (que usted registra en GitHub). Cuando instala desde un repositorio **privado**, GitHub exige ese tipo de autenticación.

> Este resumen es deliberadamente de alto nivel. El comportamiento exacto depende de la **configuración local de Git y SSH** de su máquina (claves existentes, `~/.ssh/config`, `known_hosts`, agentes SSH). Si su organización tiene reglas propias, siga su guía interna. La guía oficial de GitHub: [https://docs.github.com/es/authentication/connecting-to-github-with-ssh](https://docs.github.com/es/authentication/connecting-to-github-with-ssh).

### Pasos a alto nivel

1. Compruebe si ya tiene claves: busque archivos como `id_ed25519.pub` en la carpeta `C:\Users\<su-usuario>\.ssh\`.
2. Si no las tiene, genere un par:

   ```powershell
   ssh-keygen -t ed25519 -C "su-correo@ejemplo.com"
   ```

   Acepte la ubicación sugerida. La clave privada queda en su máquina; **nunca la comparta ni la pegue en ningún sitio**.
3. Copie el **contenido del archivo `.pub`** (la clave pública) y regístrelo en GitHub en *Settings → SSH and GPG keys → New SSH key*.
4. Pruebe la conexión:

   ```powershell
   ssh -T git@github.com
   ```

   La primera vez GitHub le pedirá confirmar la huella del servidor (responda `yes`). Si todo está bien, verá un saludo con su nombre de usuario.

Si `ssh -T` falla, el problema está en la configuración SSH local, no en `se-agent`. Resuélvalo antes de intentar la vía privada (o use la vía pública, que no necesita SSH).

---

## Paso 5 — Instalar `se-agent` (tres modos)

Elija el modo **según la visibilidad del repositorio, el acceso de su máquina y cuánto control quiera sobre la descarga**: use el ZIP para una instalación pública directa; la referencia `git+ssh` para una instalación privada directa; o clone primero el repositorio si prefiere inspeccionar y seleccionar manualmente el tag antes de instalar. Ninguna vía es "mejor" en general: las tres instalan el paquete correspondiente al tag `v0.1.1`; la diferencia es cómo se obtiene y verifica el código.

### Modo A — Público: ZIP del tag de GitHub

```powershell
pipx install 'se-agent @ https://github.com/JuanJo-Saavedra/systems-engineering-framework-agent/archive/refs/tags/v0.1.1.zip'
```

- Funciona si el repositorio es público o si la URL del archivo es accesible para usted.
- No requiere SSH, claves ni configuración de Git.
- Descarga el ZIP que GitHub genera automáticamente para el tag **`v0.1.1`** (cada tag inmutable genera su ZIP; no hay que construir nada).

### Modo B — Privado: repositorio autenticado por SSH

```powershell
pipx install 'se-agent @ git+ssh://git@github.com/JuanJo-Saavedra/systems-engineering-framework-agent.git@v0.1.1'
```

- Use este modo si el repositorio es **privado** o su red le exige pasar por SSH.
- Requiere que la sección anterior (SSH) funcione: pipx usará Git por SSH para clonar el tag `v0.1.1`.
- **Nota honesta:** que esto funcione depende de la configuración local de Git/SSH (clave registrada en GitHub, `known_hosts`, agente SSH). Si obtiene `Permission denied (publickey)` o un error de autenticación, revise el Paso 4 o su configuración SSH; el comando es correcto pero la autenticación es responsabilidad de su entorno local.

### Modo C — Manual: clonar primero e instalar localmente

Este modo tiene más pasos, pero permite inspeccionar el repositorio y confirmar el tag antes de instalarlo. El comando mostrado requiere **Git** y la configuración SSH del Paso 4, incluso si el repositorio es público, porque usa la URL `git@github.com:`.

```powershell
git clone git@github.com:JuanJo-Saavedra/systems-engineering-framework-agent.git
cd systems-engineering-framework-agent
git checkout v0.1.1
pipx install .
```

Qué hace cada comando:

1. `git clone` crea una copia local del repositorio.
2. `cd` entra en esa copia.
3. `git checkout v0.1.1` selecciona la versión publicada, en lugar de instalar accidentalmente el código más reciente de una rama.
4. `pipx install .` construye e instala el paquete desde el directorio actual (`.`).

También puede instalar desde una ruta local sin entrar al directorio:

```powershell
pipx install 'C:\ruta\al\systems-engineering-framework-agent'
```

Si la ruta contiene espacios, manténgala entre comillas simples. Antes de instalar desde una ruta existente, confirme que ese clon se encuentra en el tag correcto con `git describe --tags --exact-match`.

### ¿Por qué los comandos remotos llevan comillas simples?

La parte `se-agent @ https://...` sigue el formato estándar de *referencia directa* de pip (PEP 508): nombre del paquete, `@` y la URL exacta de donde instalarlo. Las **comillas simples** le dicen a PowerShell: *toma todo lo que está entre ellas como un solo texto literal, sin interpretar nada*. Eso evita que caracteres como `@` o `:` se malinterpreten. En PowerShell, use comillas simples siempre que quiera que el texto se tome tal cual (las comillas dobles en PowerShell **sí** interpretan variables como `$HOME` dentro del texto, lo que aquí no queremos).

### ¿Qué es `git pull`? ¿Y una "pull request"? (aclaración rápida)

- **`git pull`** es un comando para descargar cambios nuevos dentro de un clon existente. El Modo C necesita `git clone` la primera vez, pero no necesita `git pull` para instalar el tag `v0.1.1`.
- Una **pull request** de GitHub es una **propuesta de cambios** que alguien envía para que se revisen e integren. No tiene nada que ver con instalar.

Una pull request nunca es un paso de instalación. `git pull` solamente sería necesario más adelante si quisiera actualizar su clon local.

---

## Paso 6 — Verificar la instalación

```powershell
se-agent --version
```

Salida esperada:

```text
0.1.1
```

La versión se imprime **sin la `v`** (el tag es `v0.1.1`, el comando imprime `0.1.1`). Si imprime eso y no hay error, la instalación es correcta.

> `se-agent` también puede ejecutarse como módulo: `py -m se_agent --version`. Es la misma herramienta; el comando corto `se-agent` es la forma normal.

---

## Paso 7 — Usar `se-agent`

### Comandos disponibles

El MVP tiene **exactamente** estos comandos. No existen otros (ni `update`, ni `doctor`, ni `uninstall` propios de la herramienta; el desinstalado se hace con pipx, ver más abajo).

| Comando | Qué hace |
| ------------------------------------------------ | ---------------------------------------------------------------- |
| `se-agent --version` | Imprime la versión instalada (por ejemplo`0.1.1`) y termina. |
| `se-agent init --harness codex --target <dir>` | Instala el conjunto de archivos del marco en`<dir>` y termina. |

### Banderas de `init`

| Bandera | ¿Obligatoria? | Valores | Significado |
| ------------- | -------------- | ------------------ | ------------------------------------------------------------------------------------------------------------------------------- |
| `--harness` | Sí | Solo`codex` | Harness destino. En el MVP únicamente`codex` es válido; cualquier otro valor es un error de uso. |
| `--target` | Sí | Ruta de directorio | Carpeta de destino que recibirá los archivos del marco. |
| `--force` | No | (sin valor) | Sobrescribe las rutas en colisión**sin preguntar**. Solo afecta colisiones; jamás relaja las protecciones de seguridad. |

### Ejemplos seguros

**Ejemplo 1 — Probar en una carpeta de ensayo (recomendado la primera vez):**

```powershell
# 1. Cree una carpeta vacía de prueba y entre en ella
mkdir proyecto-demo
cd proyecto-demo

# 2. Instale el marco ahí
se-agent init --harness codex --target .
```

Verá algo como:

```text
Installed 20 file(s):
.agents/skills/f0-factibilidad/SKILL.md
.codex/agents/orchestrator.toml
.codex/config.toml
AGENTS.md
catalogo/skill-registry.md
marco/README.md
marco/baselines/catalogo_baselines.md
marco/fases/README.md
marco/fases/fase_0_concepto_y_factibilidad.md
... (fases 1 a 7, en el mismo orden)
marco/fases/fase_8_produccion_transferencia_soporte.md
marco/glosario.md
marco/reglas_del_ciclo.md
marco/reviews/catalogo_reviews.md
```

(El listado completo contiene las 20 rutas; aquí solo se recortan las fases intermedias. El orden mostrado **es el orden real de la herramienta**: lexicográfico por las partes de cada ruta, que pone primero `.agents/`, luego `.codex/`, y después el resto.) El código de salida es `0` y la herramienta termina: los archivos son suyos.

**Ejemplo 2 — En la raíz de su proyecto real:**

```powershell
cd C:\ruta\a\su\proyecto
se-agent init --harness codex --target .
```

**Ejemplo 3 — Apuntando a otra carpeta sin salir de donde está:**

```powershell
se-agent init --harness codex --target C:\ruta\a\otro\proyecto
```

> Si la ruta tiene espacios, póngala entre comillas: `--target "C:\Mis Documentos\proyecto"`.

### Qué instala exactamente (write-set)

`init` solo puede crear o sobrescribir estas rutas, y **nada más**:

| Destino                        | Contenido                                                                                 |
| ------------------------------ | ----------------------------------------------------------------------------------------- |
| `AGENTS.md`                  | Contrato del agente, en la raíz del destino.                                             |
| `marco/`                     | Marco de ingeniería de sistemas (15 archivos: fases 0–8, glosario, reglas, catálogos). |
| `catalogo/skill-registry.md` | Registry de capacidades/skills.                                                           |
| `.agents/skills/`            | Skills instalables (en v0.1.1:`f0-factibilidad/SKILL.md`).                              |
| `.codex/`                    | Artefactos del adaptador Codex (`config.toml`, `agents/orchestrator.toml`).           |

Ningún otro archivo del destino se crea, modifica ni elimina. En especial, una carpeta `proyecto/` que usted tenga queda **intocable siempre**, incluso con `--force`.

---

## Colisiones: qué pasa si los archivos ya existen

Una **colisión** es una ruta del write-set que ya existe en el destino. `se-agent` detecta **toda** la lista de colisiones **antes de escribir el primer byte**, y decide según su sesión:

| Situación | Comportamiento |
| --------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Sin colisiones | Escribe todo sin preguntar. |
| Con colisiones, sesión**interactiva** (terminal normal) | Lista**todas** las colisiones y pregunta `Overwrite the listed path(s)? [y/N]`. Solo `y` o `yes` (mayúsculas o minúsculas) continúa; cualquier otra respuesta, o EOF (Ctrl+D), **aborta dentro de la decisión de colisiones con código `1`, sin escribir nada**. Si pulsa Ctrl+C, en cambio, se lanza una interrupción (`KeyboardInterrupt`) que el CLI traduce al código `130` (ver [Códigos de salida](#códigos-de-salida)); ambas vías garantizan cero escrituras **solo si** ocurren antes de la primera escritura — en el flujo con colisiones, la decisión siempre es anterior a la primera escritura. |
| Con colisiones, sesión**no interactiva** (sin terminal, p. ej. un script automatizado) | **Aborta** con código distinto de 0, lista las colisiones y sugiere `Re-run with --force to overwrite.` |
| Con colisiones +`--force` | Sobrescribe**únicamente** las rutas en colisión que pertenecen al write-set, sin preguntar. |

Reglas de oro:

- `--force` **no compra privilegios**: solo puede sobrescribir rutas del write-set. Nunca lo autoriza a salirse de esa lista, saltarse las comprobaciones de seguridad ni tocar `proyecto/` o cualquier archivo ajeno.
- Las protecciones de seguridad (rechazo de rutas absolutas, `..` que escapen del destino, symlinks que apunten fuera del árbol destino) se aplican **siempre**, con o sin `--force`.
- Si contesta algo distinto de `y`/`yes` en el prompt (o cierra stdin con EOF), no se ha escrito nada: puede revisar con calma y decidir después. Ctrl+C es un camino distinto (interrupción, código `130`), no parte del prompt de colisiones.

---

## Códigos de salida

| Código | Significado |
| ------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `0` | Éxito: todas las escrituras planificadas se completaron (o`--version` imprimió la versión). |
| `1` | Fallo operacional: destino inválido, error de seguridad/preflight, aborto por colisiones, fallo a mitad de escritura, o metadatos de versión no disponibles. El mensaje de error**nombra el archivo o la regla violada**. |
| `2` | Error de uso: bandera desconocida,`--harness` inválido o `--target` ausente. Revisa la sintaxis; no se tocó nada. |
| `130` | Interrumpido con Ctrl+C. Garantía de cero escrituras**solo si** la interrupción ocurrió antes de la primera escritura. |

Los errores de uso (código 2) se detectan antes de tocar el sistema de archivos: un comando mal escrito nunca modifica nada.

---

## Escritura parcial: qué pasa si falla a mitad de camino

Si ocurre un error del sistema (permisos, disco lleno…) durante la escritura:

1. `se-agent` se **detiene en el primer error**.
2. **No intenta revertir ni borrar** lo ya escrito: esos archivos ya son suyos y se conservan.
3. Imprime dos bloques: `written:` (rutas ya escritas) y `pending:` (rutas del plan que quedaron sin escribir), y termina con código `1`.
4. Puede re-ejecutar `se-agent init` más tarde: las rutas ya escritas se tratarán como colisiones del protocolo normal (listado, `[y/N]` o `--force`).

Nunca verá un "éxito" con escrituras pendientes: si el código de salida es 0, todo el plan se completó.

---

## Desinstalar y actualizar

### Desinstalar

pipx se encarga; la herramienta no necesita ningún comando propio:

```powershell
pipx uninstall se-agent
```

Esto elimina la herramienta y su entorno aislado. Los archivos que `init` instaló en sus proyectos **no se tocan**: siguen siendo suyos.

### Actualizar a un tag nuevo

No existe comando `update` de la herramienta (decisión de diseño: one-shot, sin actualizador). Para pasar a un tag más reciente, **desinstale e instale desde la URL del tag nuevo**:

```powershell
pipx uninstall se-agent
pipx install 'se-agent @ https://github.com/JuanJo-Saavedra/systems-engineering-framework-agent/archive/refs/tags/vX.Y.Z.zip'
se-agent --version
```

(Vía privada directa: misma idea con la forma `git+ssh://...@vX.Y.Z`. Vía local: actualice el clon, ejecute `git checkout vX.Y.Z` y vuelva a instalar desde esa ruta.) Si re-ejecuta `init` sobre un proyecto ya scaffoldeado, verá las colisiones del protocolo normal: ahí decide si sobrescribe.

---

## Solución de problemas

| Síntoma | Causa probable | Solución |
| ----------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------ |
| `se-agent: The term 'se-agent' is not recognized...` | El`PATH` no incluye la carpeta de ejecutables de pipx, o no reabrió la terminal. | Ejecute`py -m pipx ensurepath`, **cierre y reabra PowerShell**, reintente. Verifique con `pipx list`. |
| `pipx: command not found` (o no reconocido) | pipx no instalado o terminal vieja. | `py -m pip install --user pipx`, reabra la terminal. |
| `py: command not found` (o no reconocido) | Python sin "Add to PATH" o no instalado. | Reinstale Python desde python.org marcando*"Add python.exe to PATH"*; si `python --version` sí funciona, use `python` en lugar de `py`. |
| La instalación de pipx falla con`error: Microsoft Visual C++ ...` o similar | No debería ocurrir: pipx es Python puro. | Actualice pip:`py -m pip install --upgrade pip` y reintente. |
| Al instalar por la vía pública: error de descarga/red | Sin acceso a github.com, o proxy corporativo. | Compruebe que la URL del ZIP abre en el navegador. En redes corporativas, configure el proxy de pip según su guía interna. |
| Al instalar por la vía privada:`Permission denied (publickey)` | SSH no autentica: clave no generada o no registrada en GitHub. | Revise el Paso 4 (SSH) y pruebe`ssh -T git@github.com`. O use la vía pública si aplica. |
| `se-agent --version` falla con `package 'se-agent' is not installed` | El paquete no está (bien) instalado en el entorno de pipx. | Reinstale:`pipx uninstall se-agent` y repita el Paso 5. |
| `init` aborta listando colisiones en una sesión no interactiva | Comportamiento esperado sin terminal. | Si está seguro, re-ejecute con`--force`; o ejecute `init` en una terminal interactiva y conteste el prompt. |
| `init` falla con `violated rule 'symlink-escape'` (u otra regla) | Un symlink del destino apunta fuera del árbol destino: protección activa. | No es un defecto: la herramienta se niega a escribir a través de ese enlace. Revise o elimine el symlink y reintente. |
| `init` falla a mitad de escritura (`written:` / `pending:`) | Error del sistema: permisos o disco lleno. | Libere espacio o corrija permisos, y re-ejecute`init` (las escritas serán colisiones). |
| `se-agent init: error: the following arguments are required: --harness, --target` | Faltan banderas obligatorias. | Complete la línea:`se-agent init --harness codex --target .` (código 2, nada se tocó). |
| `argument --harness: invalid choice: 'xyz' (choose from codex)` | `--harness` solo acepta `codex` en el MVP. | Use`--harness codex`. |

---

## Notas de seguridad

- **Verifique la URL** antes de instalar: el origen oficial es `https://github.com/JuanJo-Saavedra/systems-engineering-framework-agent`. Un ZIP de un tag de ese repositorio es el artefacto legítimo; evite URLs parecidas reenviadas por terceros.
- **Revise las colisiones antes de responder `y`.** El listado le dice exactamente qué archivos del write-set se sobrescribirán.
- **La herramienta solo escribe el write-set** descrito arriba. No crea manifiestos, carpetas ocultas de estado, cachés ni registros en su proyecto; no toca `proyecto/` jamás.
- **Su clave privada SSH nunca sale de su máquina.** Solo se registra en GitHub el contenido de la clave **pública** (archivo `.pub`).
- **No hay tests ni verificaciones que usted deba ejecutar.** La suite de pruebas es exclusiva de los desarrolladores y del CI del repositorio; como usuario no necesita (ni debería) correr nada más que los comandos de este manual.

---

## Checklist final de referencia rápida

- [ ] Python 3.12+ instalado; `py --version` y `python --version` funcionan.
- [ ] pipx instalado; `pipx --version` funciona (tras `ensurepath` y reabrir la terminal).
- [ ] (Solo vía privada) `ssh -T git@github.com` saluda con su usuario.
- [ ] La instalación elegida terminó sin error: ZIP público, referencia privada `git+ssh://...@v0.1.1` o clon local en `v0.1.1` seguido de `pipx install .`.
- [ ] `se-agent --version` imprime `0.1.1`.
- [ ] `se-agent init --harness codex --target .` en la raíz de su proyecto imprimió `Installed 20 file(s)` y el listado de rutas.
- [ ] Entiende: colisiones se listan antes de escribir; solo `y`/`yes` o `--force` sobrescriben; `--force` solo afecta rutas del write-set.
- [ ] Sabe desinstalar con `pipx uninstall se-agent` y actualizar instalando el tag nuevo mediante el mismo modo elegido.
- [ ] Recuerda: los archivos instalados son suyos al 100 %; no hay actualizador, manifiesto ni estado oculto.

## Próximos pasos

- Abra su proyecto con **Codex** (ya instalado y autenticado como prerrequisito): encontrará `AGENTS.md`, `marco/`, `catalogo/skill-registry.md`, `.agents/skills/` y `.codex/` listos para operar el marco de ingeniería de sistemas.
- Para entender cómo funciona la herramienta por dentro, lea [`arquitectura-python.md`](arquitectura-python.md).
- Para el contrato de requisitos completo, consulte [`prd/prd-001-one-shot-codex-scaffolder.md`](prd/prd-001-one-shot-codex-scaffolder.md).
