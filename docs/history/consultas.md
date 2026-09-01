# Consulta 1

> Entender mas a profundidad de la codificacion implementada, tanto de python como la burocracia de CI de github ? realmente es necesario para nuestro proyecto mvp ? es una practica recomendada ? que hace exactamente nuestro ci.yml ?

Sí: hay una parte esencial y otra deliberadamente más rigurosa que lo habitual para un MVP.

## 1. Qué implementamos realmente en Python

 El producto es pequeño: 9 módulos, Python 3.12 y cero dependencias de runtime.

 El flujo principal es:

 ```text
   se-agent init
       ↓
   cli.py
       ↓
   init_flow.py
       ├── planning.py      define exactamente qué archivos instalar
       ├── safety.py        valida rutas, directorios y symlinks
       ├── collision.py     detecta archivos existentes
       ├── writer.py        copia el payload
       └── payload.py       accede al contenido empaquetado
 ```

### Piezas principales

 - src/se_agent/cli.py
   Define la interfaz de línea de comandos, argumentos, --version, códigos de salida y el comando init.

 - src/se_agent/planning.py
   Construye una lista determinística de archivos a instalar. Las rutas salen exclusivamente del payload empaquetado; el usuario no puede inyectar rutas
   arbitrarias.

 - src/se_agent/safety.py
   Rechaza:
     - destinos absolutos;
     - rutas con ..;
     - symlinks que escapen del proyecto;
     - destinos que ya sean symlinks;
     - padres que existan pero no sean directorios.

   Esto sí es importante: la aplicación escribe dentro de proyectos ajenos.

 - src/se_agent/collision.py
   Detecta todos los conflictos antes de escribir:
     - --force: acepta sobrescribir solamente archivos del plan;
     - terminal interactiva: muestra conflictos y pregunta;
     - entorno no interactivo: aborta salvo que se use --force.

 - src/se_agent/writer.py
   Copia los archivos en orden determinístico. Si falla a mitad de camino:
     - se detiene;
     - informa qué escribió y qué quedó pendiente;
     - no hace rollback.

   La ausencia de rollback es una simplificación razonable para un MVP.

 - src/se_agent/init_flow.py
   Orquesta todo en este orden:

   ```text
     resolver destino
     → construir plan
     → validar seguridad
     → detectar colisiones
     → pedir autorización
     → escribir
     → informar resultado
   ```

 - src/se_agent/payload.py
   Usa importlib.resources para acceder al framework empaquetado dentro del wheel. Por eso funciona offline después de instalarse.

 - pyproject.toml
   Define:
     - paquete se-agent;
     - versión 0.1.1;
     - entry point se-agent = se_agent.cli:main;
     - build con Hatchling;
     - Python >=3.12;
     - cero dependencias productivas.

## 2. Qué hace exactamente ci.yml

 Archivo: .github/workflows/ci.yml

 Tiene dos jobs: test y version-tag.

### Cuándo se ejecuta

 ```yaml
   push:
     branches: ["**"]
     tags: ["v*"]
   pull_request:
 ```

 Por lo tanto:

 - cada push a cualquier rama ejecuta CI;
 - cada pull request ejecuta CI;
 - cada tag v* ejecuta el control de versión.

 Un push a una rama con PR abierto puede producir dos ejecuciones: una por push y otra por pull_request.

 ────────────────────────────────────────────────────────────────────────────────

## 3. Job test

 Se ejecuta en pushes de ramas y pull requests, pero no en tags.

### 1. Restringe permisos

 ```yaml
   permissions:
     contents: read
 ```

 El token de GitHub solamente puede leer el repositorio.

### 2. Hace checkout

 Usa actions/checkout fijado a un SHA exacto:

 ```yaml
   uses: actions/checkout@11bd...
   persist-credentials: false
 ```

 Esto evita:

 - que una actualización inesperada de la action cambie nuestro CI;
 - que las credenciales de GitHub queden disponibles para comandos posteriores.

### 3. Instala Python 3.12

 También usa actions/setup-python fijado a un SHA exacto.

### 4. Comprueba que el checkout comienza limpio

 Ejecuta:

 ```bash
   git status --porcelain=v1 \
     --untracked-files=all \
     --ignored=matching
 ```

 No sólo mira archivos modificados: también detecta archivos nuevos e incluso archivos ignorados por .gitignore.

### 5. Construye un wheel

 ```bash
   python -Im pip install "build>=1.2"
   python -Im build --wheel --outdir "$RUNNER_TEMP/dist"
 ```

 El wheel se genera fuera del repositorio.

### 6. Instala el producto real

 ```bash
   python -Im pip install \
     $RUNNER_TEMP/dist/se_agent-*.whl \
     pytest
 ```

 Esto es importante: no prueba únicamente el código fuente. Prueba el artefacto instalable que recibiría el usuario.

 En este proyecto, donde el payload debe incluirse correctamente en el paquete, esta verificación tiene bastante valor.

### 7. Ejecuta los tests

 ```bash
   python -BIm pytest \
     -p no:cacheprovider \
     --basetemp="$RUNNER_TEMP/pytest" \
     tests
 ```

 Significado:

 - -B: no genera bytecode .pyc;
 - -I: modo aislado de Python;
 - -m pytest: ejecuta pytest como módulo;
 - -p no:cacheprovider: evita .pytest_cache;
 - --basetemp: manda archivos temporales fuera del checkout.

### 8. Demuestra que CI no modificó el repositorio

 Vuelve a ejecutar git status y compara el resultado inicial contra el final.

 Si apareció cualquier archivo —incluso uno ignorado—, el job falla.

 Esto implementa la garantía de CI read-only que quedó especificada como AC-11.

 ────────────────────────────────────────────────────────────────────────────────

## 4. Job version-tag

 Sólo se ejecuta para tags v*.

 Hace tres cosas:

 1. checkout con permisos mínimos;
 2. verifica que el repositorio siga limpio;
 3. compara:

 ```text
   tag v0.1.1
            ↕
   pyproject.toml version = 0.1.1
 ```

 Si publicaras v0.2.0 mientras pyproject.toml todavía dice 0.1.1, falla.

 Este job no publica nada, no genera releases y no sube paquetes. Sólo valida consistencia.

 ────────────────────────────────────────────────────────────────────────────────

 5. Qué NO hace nuestro CI

 Actualmente no hay:

 - Ruff, Flake8 ni otro linter;
 - formateo automático;
 - ejecución de Pyright, aunque existe configuración en pyproject.toml;
 - cobertura mínima;
 - matriz de múltiples versiones de Python;
 - análisis de vulnerabilidades;
 - publicación automática;
 - deployment;
 - caché de dependencias.

 Por eso no es un CI enorme. Es angosto, pero muy estricto respecto de una propiedad específica: no modificar el checkout.

 6. ¿Es necesario para un MVP?

 Sí mantendría

 Para este proyecto:

 1. ejecutar tests en cada PR;
 2. construir e instalar el wheel;
 3. probar el producto instalado;
 4. permisos contents: read;
 5. persist-credentials: false;
 6. verificar tag contra versión.

 La construcción del wheel es particularmente relevante porque nuestro producto consiste, en buena medida, en empaquetar correctamente un payload. Un test
 desde src/ podría pasar aunque el wheel estuviera incompleto.

 No es obligatorio para un MVP genérico

 La prueba completa de checkout read-only:

 - snapshot inicial;
 - snapshot final;
 - detección de ignorados;
 - -B;
 - variable PYTHONDONTWRITEBYTECODE;
 - desactivación del caché de pytest;
 - temporales externos;

 es más rigurosa que la práctica habitual de un MVP.

 No está mal: fue una decisión de alta garantía vinculada a AC-11. Pero tiene costo cognitivo.

 Conclusión

 CI sí es recomendable para el MVP. Esta CI exacta no sería indispensable para cualquier MVP.

 En nuestro caso:

 - la arquitectura Python está bien proporcionada porque protege operaciones de escritura;
 - construir y probar el wheel está totalmente justificado;
 - permisos mínimos y acciones fijadas son buenas prácticas baratas;
 - la demostración exhaustiva de “checkout inmutable” es especificación y defensa en profundidad, no necesidad universal.

 La llamaría ingeniería conservadora, no burocracia inútil. Pero si quisiéramos optimizar simplicidad, podríamos reducir aproximadamente un tercio del YAML sin
 perder la protección principal.

# Consulta 2

> entiendo que los tests no se ejecutan ni se comprueban en produccion solo en el CI ? como se ejecuta un CI ? es automatico ? cada accion de push, cada pull y tag, lo ejecuta en automatico ? que control tengo yo como programador ? al ser un repo opensource, tengo vulnerabilidad de extraños a que intervenga mi codigo ? explicarme soy un junior programador.

 Correcto: los tests no se ejecutan en producción. Se ejecutan:

 1. localmente, cuando vos decidís;
 2. automáticamente en GitHub Actions, por medio del CI.

 En nuestro proyecto tampoco existe un servidor de producción: el “producto” es el paquete se-agent que instala el usuario.

## 1. ¿Qué es CI?

 CI significa Continuous Integration, integración continua.

 Es un robot temporal que GitHub levanta para verificar un commit:

 ```text
   Subís código
       ↓
   GitHub detecta el evento
       ↓
   Crea una máquina virtual limpia
       ↓
   Descarga el repositorio
       ↓
   Instala Python
       ↓
   Construye el paquete
       ↓
   Ejecuta los tests
       ↓
   Informa ✅ éxito o ❌ fallo
       ↓
   Destruye la máquina virtual
 ```

 No es un servidor permanente ni forma parte del programa instalado por el usuario.
    
## 2. ¿Se ejecuta automáticamente?

 Sí. Lo determina .github/workflows/ci.yml.

### Push a cualquier rama

 ```bash
   git push origin mi-rama
 ```

 Activa el job test.

### Pull request

 Crear o actualizar un PR también activa el job test.

 Importante: pull_request significa el evento de GitHub, no ejecutar git pull en tu computadora.

 Si hacés push sobre una rama que tiene un PR abierto, posiblemente veas dos ejecuciones:

 - una por push;
 - otra por actualización del pull_request.

### Tag de versión

 ```bash
   git push origin v0.1.1
 ```

 Activa version-tag, que comprueba:

 ```text
   tag v0.1.1 == versión 0.1.1 de pyproject.toml
 ```

 En los tags, el job completo de tests se saltea por decisión explícita del workflow.

 3. ¿Qué control tenés vos?

### Desde el código

 Controlás .github/workflows/ci.yml. Podés decidir:

 - qué eventos lo activan;
 - qué versiones de Python probar;
 - qué comandos ejecutar;
 - qué tests correr;
 - qué permisos recibe;
 - si construye, publica o solamente verifica.

 Modificar el workflow requiere un commit y queda sujeto a revisión como cualquier otro código.

### Desde GitHub

 En la pestaña Actions podés:

 - ver cada ejecución;
 - inspeccionar logs;
 - cancelar una ejecución;
 - volver a ejecutar un job;
 - desactivar un workflow;
 - ejecutar manualmente workflows que tengan workflow_dispatch.

 Nuestro ci.yml actualmente no tiene ejecución manual mediante workflow_dispatch.

### Desde las reglas de la rama

 En GitHub podés proteger main para exigir:

 - que CI esté en verde;
 - que exista un pull request;
 - una o más aprobaciones;
 - que no se pueda hacer force-push;
 - que las conversaciones estén resueltas;
 - que nadie pueda mergear mientras fallen los tests.

 Esto es fundamental:

 │ Tener CI no significa automáticamente que esté prohibido mergear código roto.

 Para convertir CI en una barrera obligatoria, tenés que configurar sus checks como requeridos en las reglas de protección de main.

## 4. ¿Podés ejecutar los tests localmente?

 Sí:

 ```bash
   python -m pytest tests
 ```

 O reproduciendo de manera más aproximada el CI:

 ```bash
   python -m build --wheel
   python -m pip install dist/se_agent-*.whl
   python -BIm pytest -p no:cacheprovider tests
 ```

 La regla práctica es:

 ```text
   Local: feedback rápido antes del push
   CI: verificación independiente y reproducible
 ```

 CI no reemplaza los tests locales. Confirma que el commit funciona en una máquina limpia y no solamente en tu computadora.

## 5. ¿Los tests se ejecutan en producción?

 No.

 Cuando alguien instala:

 ```bash
   pipx install 'se-agent @ ...'
 ```

 se instala el paquete construido. Los tests no viajan como un proceso que se ejecute permanentemente.

 El proceso normal es:

 ```text
   Código → tests locales → push → CI → merge → tag → release → usuario
 ```

 CI verifica el código antes de publicarlo, pero no observa lo que sucede después en la computadora del usuario.

## 6. ¿Un extraño puede modificar tu código por ser open source?

### Puede leerlo y copiarlo

 Si el repositorio es público, cualquier persona puede:

 - ver el código;
 - clonarlo;
 - crear un fork;
 - proponer cambios mediante un pull request;
 - reportar issues.

 Eso es parte del modelo open source.

### No puede modificar tu rama main directamente

 Una persona desconocida no puede hacer:

 ```bash
   git push origin main
 ```

 salvo que vos le hayas dado permisos de escritura.

 Normalmente un colaborador externo trabaja así:

 ```text
   Fork propio
       ↓
   Realiza cambios
       ↓
   Abre pull request hacia tu repositorio
       ↓
   Vos revisás
       ↓
   Vos aceptás o rechazás
 ```

 Un pull request es solamente una propuesta. No modifica main hasta que alguien autorizado lo mergea.

## 7. ¿Puede un pull request malicioso atacar el CI?

 Existe riesgo porque CI ejecuta código. Por ejemplo, un extraño podría agregar un test malicioso:

 ```python
   def test_malicioso():
       # intentar leer información o consumir recursos
       ...
 ```

 Ese código se ejecutaría en una máquina temporal de GitHub, no directamente en tu computadora ni en producción.

 GitHub aplica protecciones adicionales a PRs provenientes de forks:

 - normalmente no entrega secretos del repositorio;
 - el GITHUB_TOKEN tiene permisos restringidos;
 - puede exigir aprobación antes de ejecutar workflows de colaboradores nuevos;
 - el runner temporal se destruye al terminar.

 Nuestro workflow agrega defensas:

 ```yaml
   permissions:
     contents: read
 ```

 El token solamente puede leer.

 También:

 ```yaml
   persist-credentials: false
 ```

 Las credenciales no quedan guardadas en el checkout.

 Y no usamos el evento más peligroso:

 ```yaml
   pull_request_target
 ```

 Usamos pull_request, que es la opción adecuada para ejecutar tests de contribuciones externas con permisos restringidos.

## 8. Qué deberías revisar como propietario

 En GitHub, verificá:

### Rulesets o branch protection para main

 Recomiendo:

 - exigir pull request;
 - exigir que pase el check test;
 - bloquear force-push;
 - impedir borrado de main;
 - exigir al menos una aprobación si aparecen colaboradores.

### Actions → General

 Revisá:

 - permisos predeterminados del GITHUB_TOKEN: read-only;
 - aprobación de workflows provenientes de forks;
 - qué actions externas están permitidas.

### Colaboradores

 No entregues permisos Write, Maintain o Admin sin necesidad.

### Secretos

 No agregues tokens sensibles a workflows de pull requests externos. Actualmente nuestro workflow no necesita secretos explícitos.

 Modelo mental sencillo

 Pensalo así:

 ```text
   Repositorio público:
       cualquiera puede mirar

   Pull request:
       cualquiera puede proponer

   CI:
       GitHub prueba la propuesta en una caja descartable

   Merge:
       solamente alguien autorizado acepta la propuesta

   Producción/release:
       ocurre después, mediante una decisión separada
 ```

 El riesgo cero no existe, pero un repositorio open source bien configurado no permite que un extraño modifique directamente tu producto. El control principal
 sigue siendo tuyo: permisos, revisión, CI obligatorio y decisión de merge.

---

# Consulta 3

> mi repo era privado, pero lo tuvimos que hacer publico por la instalcion con pipx, esto es realmente necesario ? o podemos hacer y trabajarlo de manera privada ?

No: pipx no exige que el repositorio sea público.

 Lo que ocurrió es más específico:

 │ Nuestro método actual de instalación usa una URL pública del ZIP generado por GitHub.

 ```bash
   pipx install \
     'se-agent @ https://github.com/JuanJo-Saavedra/systems-engineering-framework-agent/archive/refs/tags/v0.1.1.zip'
 ```

 Esa URL funciona sin autenticación solamente si el repositorio es público. Fue una decisión del PRD, no una limitación general de pipx.

 Opciones con repositorio privado

## 1. Instalar mediante SSH

 Cada usuario autorizado configura su clave SSH en GitHub y ejecuta:

 ```bash
   pipx install \
     'se-agent @ git+ssh://git@github.com/JuanJo-Saavedra/systems-engineering-framework-agent.git@v0.1.1'
 ```

 Flujo:

 ```text
   Usuario autorizado
       ↓
   GitHub valida su clave SSH
       ↓
   pipx descarga el tag privado
       ↓
   Construye e instala se-agent
 ```

 Un extraño sin acceso al repositorio no puede instalarlo.

 Esta sería mi recomendación para un proyecto privado de equipo reducido.

## 2. Clonar primero e instalar localmente

 Es más manual pero muy fácil de entender:

 ```bash
   git clone git@github.com:JuanJo-Saavedra/systems-engineering-framework-agent.git
   cd systems-engineering-framework-agent
   git checkout v0.1.1
   pipx install .
 ```

 También podés instalar desde una ruta sin entrar al directorio:

 ```bash
   pipx install /ruta/al/systems-engineering-framework-agent
 ```

## 3. Descargar un wheel privado

 Podríamos generar:

 ```text
   se_agent-0.1.1-py3-none-any.whl
 ```

 Un usuario autorizado lo descarga e instala:

 ```bash
   pipx install ./se_agent-0.1.1-py3-none-any.whl
 ```

 Esto separa:

 - el código fuente privado;
 - el artefacto distribuible;
 - el mecanismo de instalación.

 Para crecer como producto privado, suele ser mejor usar un registro privado de paquetes o un sistema de artefactos.

 Lo que no recomiendo

 No pongas un Personal Access Token directamente en el comando:

 ```bash
   # Evitar
   pipx install 'https://USUARIO:TOKEN@github.com/...'
 ```

 El token podría quedar expuesto en:

 - historial del shell;
 - logs;
 - capturas;
 - configuración;
 - lista de procesos.

 Es mejor usar SSH o un gestor de credenciales.

 ¿El CI funciona con un repositorio privado?

 Sí. GitHub Actions funciona perfectamente en repositorios privados.

 Continuaría ejecutándose automáticamente en:

 - pushes;
 - pull requests;
 - tags.

 La diferencia puede estar en los límites y minutos incluidos en tu plan de GitHub. En repositorios públicos, GitHub suele ofrecer condiciones más generosas
 para Actions; en privados se consume la cuota correspondiente a la cuenta.

## 4. Público versus privado

### Mantenelo privado si:

 - todavía está en desarrollo;
 - lo usan solamente vos o un equipo autorizado;
 - el framework tiene valor propietario;
 - no necesitás instalaciones anónimas;
 - todavía no definiste licencia ni modelo de contribución.

### Mantenelo público si:

 - querés que cualquiera pueda instalarlo;
 - buscás contribuciones externas;
 - el producto será verdaderamente open source;
 - aceptás que código, historial, documentación y payload sean visibles;
 - querés una instalación anónima de una sola línea.

 Mi recomendación para este MVP

 Si el MVP es para vos o para un grupo reducido, puede y probablemente debería continuar privado.

 Usaría:

 ```bash
   pipx install \
     'se-agent @ git+ssh://git@github.com/JuanJo-Saavedra/systems-engineering-framework-agent.git@v0.1.1'
 ```

 Si el objetivo es distribuirlo públicamente, mantener el repositorio público es coherente, aunque a futuro publicar en PyPI daría una experiencia más
 convencional:

 ```bash
   pipx install se-agent
 ```

 Una advertencia importante

 Si volvés el repositorio privado, eso evita accesos futuros, pero no despublica mágicamente lo que ya estuvo disponible. Alguien podría haber:

 - clonado el repositorio;
 - descargado un tag;
 - creado un fork;
 - conservado archivos localmente.

 No veo indicios de que hayamos publicado secretos, pero si alguna vez existió una credencial dentro del historial, volver el repositorio privado no alcanza:
 habría que revocarla.

 En resumen:

 ```text
   pipx + ZIP anónimo de GitHub → repositorio público
   pipx + SSH/autenticación     → repositorio privado
   pipx + wheel privado         → repositorio privado
   pipx + PyPI público          → repositorio público o fuente privada
 ```

 La apertura fue necesaria para nuestro comando actual sin autenticación, no para pipx en general.

---

# Consulta 4

> Y explicarme a que se refiere cuando un pr se necesita un issue. Siempre debe hacerse eso ? cuando se tiene commit de documentacion hay que hacer todo el flujo de publicacion CI ? o solo despues de un cambio de fix o feature ?

## ¿Todo PR necesita un issue?

 GitHub no lo exige. Es una política que decide cada proyecto.

 En el flujo Gentle que veníamos usando, la regla es:

 ```text
   Issue aprobado → rama → cambios → PR vinculado → CI → merge
 ```

 El issue sirve para acordar antes:

 - qué problema resolvemos;
 - alcance y criterios de aceptación;
 - qué queda fuera;
 - quién aprobó avanzar;
 - por qué existe el PR.

 Para vincularlos se escribe en el PR:

 ```markdown
   Closes #23
 ```

 Al mergear el PR, GitHub cierra automáticamente el issue.

## Para nuestro repositorio

 Actualmente el repositorio sólo tiene .github/workflows/ci.yml. No tiene un workflow versionado que compruebe automáticamente issues, ni plantilla de PR o CONTRIBUTING.md.

 Por lo tanto, “todo PR necesita issue aprobado” es actualmente una política de nuestro proceso Gentle, no una restricción técnica aplicada por GitHub.

### ¿Siempre conviene?

 No necesariamente. Para un proyecto personal pequeño propondría:

 ┌─────────────────────────┬───────────────────┐
 │ Cambio                  │ ¿Issue previo?    │
 ├─────────────────────────┼───────────────────┤
 │ Nueva feature           │ Sí                │
 ├─────────────────────────┼───────────────────┤
 │ Bug o regresión         │ Sí                │
 ├─────────────────────────┼───────────────────┤
 │ Cambio arquitectónico   │ Sí                │
 ├─────────────────────────┼───────────────────┤
 │ Cambio de CI/release    │ Sí                │
 ├─────────────────────────┼───────────────────┤
 │ Documentación extensa   │ Recomendable      │
 ├─────────────────────────┼───────────────────┤
 │ Typo de una línea       │ No necesariamente │
 ├─────────────────────────┼───────────────────┤
 │ Ajuste mecánico trivial │ No necesariamente │
 └─────────────────────────┴───────────────────┘

 Pero si mantenemos la política Gentle actual, entonces todo PR, incluso type:docs, debe vincular un issue aprobado.

 Commit, push, PR, CI y release son cosas distintas

 ```text
   Commit local
       ↓
   Push
       ↓
   PR opcional
       ↓
   Merge
       ↓
   Tag/release opcional
 ```

### Commit local

 Es lo que acabamos de hacer.

 - No contacta GitHub.
 - No ejecuta GitHub Actions.
 - No publica nada.

### Push

 Al ejecutar:

 ```bash
   git push origin main
 ```

 GitHub recibe el commit. Nuestro ci.yml se activa automáticamente porque escucha pushes a cualquier rama:

 ```yaml
   push:
     branches: ["**"]
 ```

 Actualmente no distingue entre código y documentación. Por eso un push documental también ejecutará los tests Python.

### Pull request

 Al crear o actualizar un PR, CI vuelve a ejecutarse debido a:

 ```yaml
   pull_request:
 ```

 Si una rama tiene un PR abierto, un push puede generar:

 - una ejecución por push;
 - otra por pull_request.

### Tag

 Cuando se publica un tag v*:

 ```bash
   git push origin v0.1.2
 ```

 se ejecuta version-tag, que compara el tag con la versión de pyproject.toml.

 ¿Un cambio documental necesita release?

 Normalmente, no.

 Este commit:

 - no cambia Python;
 - no cambia el payload;
 - no cambia el comportamiento del paquete;
 - no requiere una nueva versión de se-agent;
 - no necesita un nuevo tag;
 - no necesita reinstalar mediante pipx;
 - no necesita GitHub Release.

 Sólo necesita publicar el commit, ya sea mediante push directo o PR.

 ¿Cuándo corresponde una publicación completa?

 ### Feature o fix que cambia el paquete distribuido

 ```text
   Issue
   → implementación
   → tests
   → PR
   → CI
   → merge
   → incremento de versión
   → tag
   → verificación de instalación
   → release
 ```

 ### Documentación solamente

 ```text
   Commit
   → push o PR
   → CI automático
   → merge
 ```

 Sin tag ni nueva versión del paquete, salvo que la documentación forme parte de una entrega versionada específica.

 Sobre nuestro commit actual

 Como está en main local, tenemos dos caminos:

 1. Push directo a main: simple; CI se ejecutará automáticamente.
 2. Publicarlo mediante PR: habría que mover el commit a una rama docs/..., vincular un issue según nuestra política y abrir el PR.

 No haré push ni reestructuraré la rama sin tu autorización.