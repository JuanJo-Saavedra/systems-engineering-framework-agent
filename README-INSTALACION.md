# se-agent — instalacion MVP (Windows)

Esta carpeta es el paquete. No hace falta Git ni PyPI. El instalador usa pipx por vos.

1. Abri PowerShell **dentro de esta carpeta** (tiene que existir `pyproject.toml` aca).
2. Instala:

   ```powershell
   .\release\windows\1-instalar.ps1
   ```

3. **Si el instalador dice que pipx o el PATH cambiaron: cerra ESTA terminal y abri una NUEVA.** Windows no refresca el PATH en la misma sesion. No sigas en la terminal vieja.
4. En el proyecto donde quieras el framework:

   ```powershell
   <esta-carpeta>\release\windows\2-inicializar-en-proyecto.ps1 -Target .
   ```

Eso corre `se-agent init --harness codex --target <target>`. No toca `proyecto/`.

Si PowerShell bloquea scripts: `Set-ExecutionPolicy -Scope Process Bypass` y repetí el paso 2.

Manual completo: `docs/guides/instalacion-mvp-veng.md`.
