# Instalacion MVP VENG

Este flujo es para entregar un ZIP de prueba a un usuario de VENG y permitirle
levantar `se-agent` rapido, sin publicar todavia un release formal en GitHub.

El usuario **no** necesita saber que es pipx. El instalador lo instala si falta.

## Objetivo

El usuario recibe un archivo ZIP, lo descomprime, ejecuta un instalador de
Windows y luego inicializa el framework en el proyecto donde quiere trabajar.

El MVP mantiene la decision de producto: `se-agent` es un paquete Python y se
instala aislado con `pipx`. Los scripts solo reducen friccion de uso.

En la raiz del ZIP viaja `README-INSTALACION.md` (instrucciones cortas). Este
documento es el manual completo.

## Requisitos del usuario

- Windows con PowerShell.
- Python 3.12 o superior. Validado con Python 3.12.10 (`py` y `python`).
- Codex instalado y autenticado, si luego va a usar el framework desde Codex.
- Permiso para instalar paquetes Python en el perfil de usuario.
- Red la primera vez (pipx y el build de hatchling). Despues, `se-agent init`
  funciona offline: el payload viaja dentro del paquete.

## Crear el ZIP para prueba

Desde la raiz de `systems-engineering-framework-agent`:

```powershell
.\release\windows\crear-zip-mvp.ps1
```

Salida esperada:

```text
dist\se-agent-mvp-<version>.zip
```

El script copia contenido real (no placeholders OneDrive/reparse), valida que
el staging y el ZIP tengan `pyproject.toml`, `src/se_agent/_payload/` con
archivos de tamano > 0, y `release/windows/*.ps1`.

El ZIP tiene una carpeta raiz `se-agent-mvp-<version>/`. Al descomprimir,
`release\windows\1-instalar.ps1` queda dos niveles debajo de `pyproject.toml`.

Opciones utiles (no hace falta editar los scripts):

```powershell
.\release\windows\crear-zip-mvp.ps1 -Version 0.1.1-german -OutputDir C:\temp -ZipName se-agent-prueba.zip
.\release\windows\crear-zip-mvp.ps1 -SourceRoot D:\clean\systems-engineering-framework-agent
```

## Instrucciones para el usuario final

1. Descomprimir el ZIP. Entrar a la carpeta `se-agent-mvp-<version>` (tiene
   que existir `pyproject.toml` ahi). Por ejemplo:

   ```text
   C:\VENG\se-agent-mvp-0.1.1
   ```

2. Abrir PowerShell en esa carpeta.

3. Ejecutar:

   ```powershell
   .\release\windows\1-instalar.ps1
   ```

   Si PowerShell bloquea scripts:

   ```powershell
   Set-ExecutionPolicy -Scope Process Bypass
   .\release\windows\1-instalar.ps1
   ```

4. Leer el final del instalador.

   - Si dice **ACCION OBLIGATORIA**: pipx o el PATH realmente cambiaron, o
     esta terminal no tiene el PATH nuevo. **Cerra esa terminal y abri una
     nueva.** Windows no refresca el PATH en la misma sesion. Seguir en la
     terminal vieja es el error que mas tiempo hace perder.
   - Si dice que pipx y el PATH ya estaban en esta sesion, podes seguir aca.

5. Abrir PowerShell en la carpeta del proyecto consumidor, por ejemplo:

   ```text
   C:\VENG\mi-proyecto
   ```

6. Ejecutar el inicializador (ruta absoluta a la carpeta descomprimida):

   ```powershell
   C:\VENG\se-agent-mvp-0.1.1\release\windows\2-inicializar-en-proyecto.ps1 -Target .
   ```

   Eso corre `se-agent init --harness codex --target <target>`.

   Si `-Target` no existe, el script **crea** el directorio. Si existe y no
   es un directorio, aborta con error claro.

   Para sobrescribir colisiones del write-set declarado:

   ```powershell
   C:\VENG\se-agent-mvp-0.1.1\release\windows\2-inicializar-en-proyecto.ps1 -Target . -Force
   ```

## Configuracion rapida

Los scripts aceptan parametros para no tener que editar archivos:

| Script | Parametro | Uso |
| --- | --- | --- |
| `1-instalar.ps1` | `-PackageSource` | Ruta local del paquete Python. Por defecto: raiz del ZIP descomprimido (`pyproject.toml` dos niveles arriba de `release/windows`). |
| `1-instalar.ps1` | `-PythonCommand` | Comando Python a usar. Por defecto intenta `py -3.12` y luego `python`. |
| `1-instalar.ps1` | `-SkipEnsurePath` | Evita correr `pipx ensurepath`, util para diagnostico. |
| `2-inicializar-en-proyecto.ps1` | `-Target` | Carpeta donde instalar el framework. Por defecto `.`. Si no existe, se crea. |
| `2-inicializar-en-proyecto.ps1` | `-Force` | Pasa `--force` a `se-agent init`. |
| `crear-zip-mvp.ps1` | `-Version` | Sufijo/version del ZIP. Por defecto lee `pyproject.toml`. |
| `crear-zip-mvp.ps1` | `-OutputDir` | Carpeta donde dejar el ZIP. Por defecto `dist/`. |
| `crear-zip-mvp.ps1` | `-ZipName` | Nombre del archivo ZIP. Por defecto `se-agent-mvp-<version>.zip`. |
| `crear-zip-mvp.ps1` | `-SourceRoot` | Origen a empaquetar. Por defecto: raiz del repo (dos niveles arriba de `release/windows`). |

## Criterio de aceptacion del MVP

El paquete es apto para prueba si:

- el ZIP se genera con un comando y contiene el paquete real (no placeholders);
- el usuario puede ejecutar `1-instalar.ps1` sin conocer `pipx`;
- el mensaje de terminal nueva aparece **solo cuando pipx o el PATH cambiaron**,
  o cuando esta sesion no tiene el PATH nuevo;
- `2-inicializar-en-proyecto.ps1` ejecuta `se-agent init --harness codex --target <target>`;
- el target queda con `AGENTS.md`, `marco/`, `catalogo/`, `.agents/` y `.codex/`;
- no se toca `proyecto/` en el consumidor.

`installer/windows/` esta obsoleto (enfoque EXE). El camino de este MVP es
`release/windows/`.
