# Contrato versionado de paquete documental y `manifest.md`

## Alcance y versiones

Este documento define el contrato mecánico **v1** de `docs_review`. El único backend previsto es `scripts/docs_review.ps1`, ejecutado internamente en Windows PowerShell 5.1 con .NET. Recibe `-Operation` y `-RequestPath`; el usuario nunca redacta comandos. No hay compatibilidad implícita entre versiones: un request o manifest cuya versión no sea `1` se bloquea.

Las operaciones exactas son `Prepare`, `Submit`, `RecordDecision`, `Promote` y `Validate`. El backend escribe un único objeto JSON en stdout, en UTF-8 sin BOM y sin prosa adicional. No escribe diagnósticos en stdout. Toda validación falla cerrada: no repara, borra, sobrescribe ni infiere valores.

## Secuencia normativa de ejecución

Esta secuencia obliga al orquestador a seguir el proceso establecido. Conserva la autoridad humana: el backend ejecuta mecánica validada, pero no decide qué operación corresponde ni inventa autorizaciones, attestations o decisiones.

### Secuencia común y actores

| Actor                | Responsabilidad normativa y límite                                                                                                                                                                             |
| -------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Humano               | Expresa la intención y la autorización para la operación exacta, y aporta los datos de attestation o decisión cuando correspondan.                                                                          |
| Orquestador          | Selecciona, carga y compone`docs-review`; conserva el control de la secuencia, aplica sus gates, decide el routing y la próxima operación.                                                                  |
| Skill`docs-review` | Aporta el protocolo normativo, valida las precondiciones conversacionales, de request y de resultado, y ordena el uso exclusivo del backend. No elige la decisión humana ni llama autónomamente a otra skill. |
| `docs_review.ps1`  | Ejecuta solo mecánica determinista: valida y procesa el request, aplica el lock interno cuando corresponde y emite el resultado.                                                                               |

1. El humano expresa la intención y la autorización para la operación exacta, y aporta los datos de attestation o decisión cuando correspondan.
2. El orquestador, lee el estado aplicable, resuelve la especificación del paquete. Conserva el control de la secuencia, sus gates, el routing y la próxima operación.
3. Conforme al protocolo normativo aportado por `docs-review`, el orquestador verifica las precondiciones conversacionales para la operación: que la autorización humana la cubra exactamente y que estén presentes los datos requeridos. Pide únicamente los datos faltantes y nunca infiere una decisión, una attestation ni una autorización.
4. Bajo dirección del orquestador y del contrato `docs-review` ya seleccionado, se materializa un request JSON v1 temporal, controlado por el harness, fuera de cualquier paquete y codificado en UTF-8 sin BOM. El usuario no escribe comandos.
5. Bajo esa misma dirección, el orquestdor invoca exclusivamente el backend con `-Operation` y `-RequestPath`, sin bypass ni fallback. `docs_review.ps1` valida el request, toma su lock interno para las mutaciones, ejecuta solo la mecánica determinista y emite el resultado; el orquestador no copia, calcula hashes ni promueve manualmente.
6. Conforme al protocolo de `docs-review`, el orquestador separa el JSON de stdout de stderr, correlaciona operación, estado, ruta y exit code, relee y valida las precondiciones de resultado contra este contrato, y elimina únicamente el request temporal que el orquestador materializó bajo su dirección.
7. Ante `blocked`, error, stdout ambiguo o interrupción, el orquestador no reintenta la mutación ni intenta reparar. Puede observar con `Validate` solo si existe una ruta esperada y observarla es seguro; después se detiene y escala al humano.

El request se captura una sola vez y el lock es interno al backend; el orquestador no sustituye el request ni intenta coordinar la concurrencia por fuera. La idempotencia no habilita reintentos automáticos tras un resultado incierto: solo describe el resultado de una nueva invocación explícitamente autorizada.

### Composición explícita de operaciones

Nunca se encadenan operaciones por inferencia. Una frase humana puede autorizar una secuencia acotada y explícita —por ejemplo, `Prepare` seguido de `Submit`, o `RecordDecision` seguido de `Promote`—, pero cada operación requiere su propio request y su propia invocación. El orquestador valida el resultado previo antes de continuar; cualquier bloqueo, error, salida ambigua o interrupción corta la secuencia.

### Paso a paso por operación

En todas las operaciones, el request incluye `schema_version: 1`, `project_root` y una `package_specification` completa. Los campos adicionales, las precondiciones y los límites de continuación son los siguientes.

| Operación         | Campos requeridos y precondiciones                                                                                                                                                                                                                    | Qué valida o hace el backend                                                                                                                                                                                                | Resultado aceptable y siguiente acción                                                                                                                                                                                                                                                                                                                      |
| ------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `Prepare`        | No incluye`package_path`, `attestation` ni `decision`. Requiere autorización humana explícita para preparar, especificación válida, fuentes vivas existentes e íntegras y, si aplica, continuidad válida con el predecesor.               | Valida request, rutas, fuentes, cadena y colisiones; bajo lock crea el snapshot y el manifest completos mediante publicación atómica como`pendiente`.                                                                    | Aceptar solo resultado no bloqueado de`Prepare` con estado `pendiente` y ruta de verificación esperada. Después solo se permite observar con `Validate` o ejecutar `Submit` con autorización y attestation humanas explícitas; se prohíbe someter o copiar manualmente.                                                                         |
| `Submit`         | Incluye`package_path` de verificación y `attestation` completa; no incluye `decision`. Requiere autorización humana explícita para someter y paquete íntegro en `pendiente`.                                                              | Bajo lock revalida request, ruta, conjunto, manifest e integridad, y aplica únicamente`pendiente → en_verificacion`; los mismos datos pueden ser idempotentes, pero datos distintos bloquean.                            | Aceptar solo resultado no bloqueado de`Submit` con estado `en_verificacion` y ruta esperada. Después solo se permite observar o registrar una decisión humana explícita; se prohíbe inferir revisión o promover.                                                                                                                                    |
| `RecordDecision` | Incluye`package_path` de verificación y `decision` completa; no incluye `attestation`. Requiere autorización humana explícita para registrar esa decisión, paquete íntegro en `en_verificacion` y fuentes vivas congeladas coincidentes. | Bajo lock revalida request, manifest, hashes, fuentes y gates; aplica únicamente`en_verificacion → aprobado` o `en_verificacion → rechazado`, sin sobrescribir una decisión terminal.                                | Aceptar solo resultado no bloqueado de`RecordDecision` con estado terminal que coincida exactamente con la decisión humana y ruta esperada. Después el orquestador puede aplicar el contrato de fase de espejos vivos conforme a la sección siguiente; `Promote` solo puede seguir a `aprobado`, con autorización y attestation de promoción separadas. |
| `Promote`        | Incluye`package_path` de verificación y `attestation` de promoción completa; no incluye `decision`. Requiere autorización humana explícita para promover y paquete íntegro en `aprobado`.                                                | Bajo lock revalida origen, manifest, hashes, estado y destino; publica únicamente una copia byte a byte idéntica en aprobados. Una copia idéntica existente es idempotente; una parcial, distinta o incompatible bloquea. | Aceptar solo resultado no bloqueado de`Promote` con estado `aprobado` y ruta devuelta coherente con la publicación esperada. Después solo se permite observar; se prohíbe alterar manualmente la copia o el paquete fuente.                                                                                                                           |
| `Validate`       | Incluye`package_path` de verificación o aprobados; no incluye `attestation` ni `decision`. Requiere una ruta esperada cuya observación sea segura.                                                                                            | Sin mutar, valida rutas, conjunto exacto, manifest canónico, hashes, estado y gates; para paquetes activos también compara las fuentes vivas congeladas.                                                                   | Aceptar solo resultado no bloqueado de`Validate` cuya operación, estado y ruta coincidan con lo observado y esperado. No autoriza ninguna mutación, no determina una decisión y no habilita encadenamiento por sí misma.                                                                                                                               |

### Espejos vivos

`docs-review` no actualiza espejos vivos. Solo después de un `RecordDecision` exitoso el orquestador puede aplicar el contrato de fase correspondiente, y únicamente con la autorización humana que cubra esa aplicación y tras releer el estado y el resultado. Esa aplicación no se convierte en una operación automática del backend ni se infiere de una promoción; si falta autorización, datos o una condición del contrato de fase, el orquestador se detiene y escala al humano.

## Request JSON v1

El archivo indicado por `-RequestPath` contiene exactamente un objeto JSON. Sus claves de primer nivel, en este orden, son:

| Clave                     | Tipo   | Regla                                                                                               |
| ------------------------- | ------ | --------------------------------------------------------------------------------------------------- |
| `schema_version`        | entero | Obligatorio; vale exactamente`1`.                                                                 |
| `project_root`          | cadena | Obligatoria; ruta absoluta existente de la raíz del proyecto.                                      |
| `package_specification` | objeto | Obligatoria en todas las operaciones; debe cumplir el esquema siguiente.                            |
| `package_path`          | cadena | Obligatoria en`Submit`, `RecordDecision`, `Promote` y `Validate`; prohibida en `Prepare`. |
| `attestation`           | objeto | Obligatoria en`Submit` y `Promote`; prohibida en las demás operaciones.                        |
| `decision`              | objeto | Obligatoria en`RecordDecision`; prohibida en las demás operaciones.                              |

No se admiten claves desconocidas, duplicadas ni omitidas. Los campos condicionales solo pueden aparecer en su operación indicada. Las cadenas son Unicode no vacías, sin NUL ni saltos de línea, salvo que una regla más estricta indique otra cosa. El JSON de request puede usar espaciado normal; su semántica, claves y tipos sí son estrictos.

El backend captura, parsea y valida el objeto de `RequestPath` exactamente una vez antes de tomar un lock. Deriva de ese mismo objeto `project_root`, el scope del lock y el dispatch de la operación; un cambio posterior, reemplazo o nueva escritura de `RequestPath` no altera la operación en curso. Bajo el lock se revalida el filesystem, los destinos y el estado del paquete, pero nunca se relee ni se sustituye el request capturado.

`project_root` acepta solo un directorio existente en un volumen local Windows absoluto (`C:\...`); rechaza antes de normalizar UNC (`\\servidor\recurso`) y los prefijos device `\\?\` y `\\.\`. La normalización preserva la raíz de volumen (`C:\`, nunca `C:`) y comprueba desde `Path.GetPathRoot` hasta la raíz final que ningún ancestro ni la propia raíz sea symlink, junction u otro reparse point.

Toda ruta relativa de contrato usa exclusivamente `/`: no admite `\`, raíz, volumen ni segmentos vacíos, `.` o `..`. Cada segmento rechaza `:` (incluido ADS), caracteres inválidos de nombre Windows, nombres DOS reservados `CON`, `PRN`, `AUX`, `NUL`, `COM1`–`COM9` y `LPT1`–`LPT9` incluso con extensión, y punto o espacio final. Las rutas de artifacts, fuentes y paquetes son únicas con semántica case-insensitive efectiva. `package_path` se confina a `project_root` y no atraviesa symlinks o reparse points. Para `Submit` y `RecordDecision` debe identificar exactamente `proyecto/docs-verificacion/<scope>/<package_id>`; para `Promote` esa misma ruta; para `Validate` puede identificar esa ruta o `proyecto/docs-aprobados/<scope>/<package_id>`.

### `package_specification`

Las claves admitidas, en este orden, son:

| Clave                      | Tipo             | Regla                                                                                                                                    |
| -------------------------- | ---------------- | ---------------------------------------------------------------------------------------------------------------------------------------- |
| `package_id`             | cadena           | Debe ser exactamente`<scope>-<maturity>-r<NNN>`, con revisión decimal de tres o más dígitos.                                        |
| `scope`                  | cadena           | Identificador en minúsculas separado por guiones:`^[a-z0-9]+(-[a-z0-9]+)*$`.                                                          |
| `phase`                  | cadena           | Identificador no vacío de fase, formado por letras, dígitos,`_` o `-`; no contiene espacios.                                       |
| `maturity`               | cadena           | `preliminar` o `formal`.                                                                                                             |
| `revision`               | entero           | Mayor o igual que`1`; su representación decimal sin signo debe coincidir con `NNN` de `package_id`.                               |
| `predecessor_package_id` | cadena o`null` | `null` solo en la primera revisión de la cadena; de otro modo identifica el único predecesor terminal inmediato del mismo `scope`. |
| `source_git_revision`    | cadena o`null` | Procedencia opcional; nunca participa en hashes ni requiere Git. Si se omite, se materializa como`null` en el manifest.                |
| `artifacts`              | array no vacío  | Entradas completas, ordenadas estrictamente por`path` en orden ordinal, sin rutas ni tipos duplicados.                                 |

Cada entrada de `artifacts` admite exactamente estas claves, en este orden:

| Clave                    | Tipo              | Regla                                                                                                                                        |
| ------------------------ | ----------------- | -------------------------------------------------------------------------------------------------------------------------------------------- |
| `path`                 | cadena            | Ruta relativa normalizada con`/` del snapshot dentro del paquete; no es absoluta, no contiene `.` o `..`, ni escapa por reparse point. |
| `document_type`        | cadena            | Identificador no vacío en minúsculas, dígitos y`_`: `^[a-z0-9]+(_[a-z0-9]+)*$`.                                                       |
| `source_path`          | cadena            | Ruta relativa normalizada con`/` bajo `proyecto/`; identifica un archivo vivo existente, regular y sin reparse point.                    |
| `carried_forward_from` | `null` u objeto | En`r001` vale `null`. El objeto admite solo `package_id` y `path`, ambas cadenas no vacías.                                         |

El `package_id` citado por `carried_forward_from` debe ser un paquete terminal anterior de la misma cadena lineal de `scope`; `path` debe identificar uno de sus artifacts. El snapshot vivo actual debe ser byte a byte idéntico al snapshot citado y conservar su SHA-256. Una referencia inexistente, ambigua, no terminal o divergente bloquea `Prepare`.

### Attestations y decisión

`Submit.attestation` contiene exactamente `identity`, `role`, `at` y `source`, todas cadenas no vacías. `at` es una fecha-hora ISO 8601 con zona explícita. `source` declara la instrucción humana explícita; no es una firma criptográfica.

`Promote.attestation` contiene exactamente `identity`, `at` y `source`, con las mismas reglas de contenido. Solo autoriza la mecánica de promoción y no modifica la copia ni el manifest.

`RecordDecision.decision` contiene exactamente estas claves:

| Clave        | Tipo   | Regla                                                    |
| ------------ | ------ | -------------------------------------------------------- |
| `value`    | cadena | `aprobado` o `rechazado`.                            |
| `reviewer` | cadena | Identidad humana no vacía.                              |
| `role`     | cadena | Rol humano no vacío.                                    |
| `at`       | cadena | Fecha-hora ISO 8601 con zona explícita.                 |
| `source`   | cadena | Fuente no vacía de la decisión humana explícita.      |
| `findings` | array  | Hallazgos en orden estricto de ruta; puede estar vacío. |

Cada hallazgo admite exactamente `path`, `outcome` y `note`. `path` debe pertenecer a `artifacts`, `outcome` es `aprobado` o `rechazado`, `note` es una cadena no vacía, y no puede haber más de un hallazgo por ruta. Un hallazgo `rechazado` exige `value: "rechazado"`. La decisión es de paquete completo: no hay aprobación parcial.

### Ejemplos de request

`Prepare`:

```json
{
  "schema_version": 1,
  "project_root": "C:/proyectos/alpha",
  "package_specification": {
    "package_id": "alpha-formal-r001",
    "scope": "alpha",
    "phase": "ALPHA",
    "maturity": "formal",
    "revision": 1,
    "predecessor_package_id": null,
    "source_git_revision": null,
    "artifacts": [
      {
        "path": "uno.md",
        "document_type": "alpha_primary",
        "source_path": "proyecto/fases/alpha/uno.md",
        "carried_forward_from": null
      }
    ]
  }
}
```

`Submit` agrega:

```json
{
  "package_path": "proyecto/docs-verificacion/alpha/alpha-formal-r001",
  "attestation": {
    "identity": "author@example.test",
    "role": "author",
    "at": "2026-01-02T03:04:05Z",
    "source": "explicit human instruction"
  }
}
```

`RecordDecision` agrega `package_path` y:

```json
{
  "decision": {
    "value": "aprobado",
    "reviewer": "reviewer@example.test",
    "role": "independent reviewer",
    "at": "2026-01-03T03:04:05Z",
    "source": "explicit human decision",
    "findings": [
      { "path": "uno.md", "outcome": "aprobado", "note": "human finding" }
    ]
  }
}
```

`Promote` agrega `package_path` y una `attestation` de promoción. `Validate` agrega solamente `package_path`.

## Resultado JSON v1

Toda operación devuelve exactamente un objeto JSON con estas claves, en este orden:

| Clave            | Tipo             | Regla                                                                                                                |
| ---------------- | ---------------- | -------------------------------------------------------------------------------------------------------------------- |
| `ok`           | booleano         | `true` si la operación se completó; `false` ante bloqueo.                                                      |
| `operation`    | cadena           | Eco exacto de`Prepare`, `Submit`, `RecordDecision`, `Promote` o `Validate`.                                |
| `blocked`      | booleano         | Es el inverso de`ok`.                                                                                              |
| `state`        | cadena o`null` | Estado observado (`pendiente`, `en_verificacion`, `aprobado`, `rechazado`) o `null` si no pudo observarse. |
| `errors`       | array de cadenas | Vacío si`ok` es `true`; no vacío si `blocked` es `true`.                                                   |
| `package_path` | cadena           | Obligatoria cuando se identificó un paquete; relativa, normalizada con`/` y confinada a `project_root`.         |

No se permiten claves adicionales. Un resultado bloqueado conserva el estado previamente observado cuando sea seguro hacerlo y no publica una mutación parcial.

Ejemplo de éxito:

```json
{
  "ok": true,
  "operation": "Prepare",
  "blocked": false,
  "state": "pendiente",
  "errors": [],
  "package_path": "proyecto/docs-verificacion/alpha/alpha-formal-r001"
}
```

## Manifest estricto v1

Cada paquete contiene exactamente `manifest.md` y un snapshot por cada `artifacts[].path`; no admite archivos ni directorios adicionales. Los únicos directorios permitidos son los directorios orquestador derivados de esos artifact paths; por tanto también se bloquea un directorio adicional vacío. La promoción conserva este mismo conjunto exacto de archivos y directorios. Un manifest válido es UTF-8 sin BOM, usa solo LF y tiene exactamente esta forma:

```text
---
<objeto JSON canónico>
---
<cuerpo Markdown determinista>
```

El bloque entre delimitadores es un único objeto JSON, subconjunto válido de YAML 1.2. No se acepta YAML libre. El lector extrae exactamente el bloque, rechaza claves duplicadas o desconocidas, valida tipos y valores por versión, lo reserializa y compara sus bytes con el bloque original. Cualquier diferencia bloquea.

El objeto JSON tiene estas claves y orden exactos:

```json
{
  "manifest_version": 1,
  "package_id": "alpha-formal-r001",
  "scope": "alpha",
  "phase": "ALPHA",
  "maturity": "formal",
  "revision": 1,
  "predecessor_package_id": null,
  "state": "pendiente",
  "submitted_by": null,
  "submitted_at": null,
  "reviewer": null,
  "review_decision": null,
  "reviewed_at": null,
  "source_git_revision": null,
  "artifacts": []
}
```

Las reglas de `package_id`, `scope`, `phase`, `maturity`, `revision`, `predecessor_package_id`, `source_git_revision` y el orden de artifacts son las de `package_specification`. `manifest_version` vale `1`. `state` es uno de los cuatro estados. En `pendiente`, los seis campos de sometimiento/revisión son `null`; en `en_verificacion`, `submitted_by` y `submitted_at` son cadenas válidas y los cuatro campos de revisión son `null`; en estados terminales los seis son cadenas válidas y `review_decision` coincide con `state`.

Cada entrada de `artifacts` tiene este orden y solo estas claves:

```json
{
  "path": "uno.md",
  "document_type": "alpha_primary",
  "source_path": "proyecto/fases/alpha/uno.md",
  "carried_forward_from": null,
  "content_sha256": "<64 hexadecimales minúsculas>",
  "review_outcome": null
}
```

`content_sha256` es SHA-256 de los bytes crudos del snapshot. `review_outcome` es `null` antes de una decisión; después es el outcome del hallazgo de esa ruta, o `null` si no hubo hallazgo. Se recalcula antes de `RecordDecision`, `Promote` y `Validate`.

### JSON canónico y cuerpo Markdown

El JSON canónico usa dos espacios por nivel, claves en el orden de este documento, `null` literal, cadenas JSON con escape estándar, un único LF al final de cada línea y ningún espacio sobrante. Los arrays preservan el orden validado. La serialización del objeto mostrado, sus artifacts y todo manifest se hace con UTF-8 sin BOM y LF.

El cuerpo se genera por completo; no se aceptan secciones, texto o líneas adicionales. Contiene, en este orden, títulos H2 y listas con LF:

```markdown
## Propósito del paquete

- Scope: `<scope>`
- Fase: `<phase>`
- Madurez: `<maturity>`
- Revisión: `<revision>`
- Predecesor: `<predecessor_package_id>` o `ninguno`

## Attestation de sometimiento

`No registrada.` o, en este orden: identidad, rol, fecha y fuente de la attestation de Submit.

## Attestation de revisión

`No registrada.` o, en este orden: revisor, rol, fecha, fuente y decisión de RecordDecision.

## Hallazgos

`Sin hallazgos.` o una línea por hallazgo en orden de ruta: `- <path>: <outcome> — <note>`.
```

Los valores de Submit y RecordDecision que no tienen campo JSON equivalente (`role` y `source`) viven solo en este cuerpo y se validan contra la transición que los incorporó. Las comillas inversas y valores interpolados se escapan de forma determinista para que el cuerpo no cree Markdown estructural adicional.

## Estados, rutas, integridad y atomicidad

- `Prepare` exige especificación y fuentes vivas íntegras. Crea `proyecto/docs-verificacion/<scope>/<package_id>` en un directorio temporal del mismo volumen, calcula hashes y publica solo el conjunto completo como `pendiente`. Repetir el mismo request contra un paquete pendiente íntegro es lectura idempotente; una colisión o parcialidad bloquea.
- `Submit` exige paquete pendiente completo y `attestation` explícita. Solo permite `pendiente → en_verificacion`. Repetir los mismos datos es idempotente; datos distintos o cualquier otro estado bloquean.
- `RecordDecision` exige paquete íntegro `en_verificacion`, fuentes vivas congeladas con hashes coincidentes y `decision` humana explícita. Solo permite `en_verificacion → aprobado | rechazado`. La misma decisión terminal es lectura idempotente; nunca se sobrescribe una terminal.
- `Promote` exige paquete íntegro `aprobado` y attestation de promoción explícita. Publica una copia byte a byte idéntica en `proyecto/docs-aprobados/<scope>/<package_id>` usando publicación temporal en el mismo volumen. Una copia existente idéntica es éxito idempotente; una parcial, distinta o incompatible bloquea.
- `Validate` es solo lectura y acepta un paquete de verificación o aprobado. Comprueba rutas, conjunto exacto, manifest canónico, hashes, estado y gates sin mutar nada. Para un paquete de verificación activo (`pendiente` o `en_verificacion`) también exige que las fuentes vivas sigan coincidiendo con sus snapshots; para un histórico terminal o una copia aprobada valida snapshots y manifest sin exigir que los vivos actuales sigan iguales.

`Prepare`, `Submit`, `RecordDecision` y `Promote` se serializan por un lock exclusivo cooperativo de .NET con alcance `project_root + scope`. El lock persistente es `proyecto/docs-verificacion/<scope>/.docs-review.lock`, se abre con `FileShare.None` y bloqueo de byte; es infraestructura fuera del conjunto de archivos del paquete, no se borra para reparar y una caída deja un archivo reabrible, no un bloqueo lógico permanente. El lock se mantiene durante revalidación y publicación; inmediatamente antes de cada publicación se revalidan raíz, destino y ancestros. La publicación sigue usando staging en el mismo volumen y `File.Replace` cuando cambia el manifest. El lock coordina instancias cooperantes del backend, pero no protege contra escritores externos arbitrarios.

Toda ruta se resuelve bajo `project_root`; se rechazan traversal, rutas absolutas, escapes por symlink/reparse point, ids inválidos, duplicados, extras y destinos existentes incompatibles. La promoción no cambia el estado ni el contenido del paquete fuente. No hay estados `en_revision`, `promovido` o `invalidado`.
