---
document_type: arquitectura_ciclo_review
language: es
version: 1.3
status: propuesto
---
# Ciclo de vida de revisión documental: capacidad `docs_review`

**Decisión.** La revisión humana de documentos se organiza en un **paquete de review** versionado, completo e inmutable: se somete en `proyecto/docs-verificacion/<scope>/<package_id>/` y, tras aprobación humana, se promueve sin alteración a `proyecto/docs-aprobados/<scope>/<package_id>/`. El registro autoritativo es `manifest.md`; los espejos de los documentos vivos (`doc_approval` e historial) son derivados. Los únicos estados son `pendiente → en_verificacion → aprobado | rechazado`; la promoción es una acción humana posterior, no un estado.

La capacidad conceptual **de tarea puntual** es **`docs_review`** y su skill ejecutable es **`docs-review`**. Es reutilizable en varias fases, pero conserva exclusivamente el tipo de catálogo `tarea puntual`. Gobierna el ciclo conversacional genérico del paquete, sus gates de autoridad y la invocación de un script determinista incluido. Es distinta de **`preparacion_de_review`**, que sigue reservada para los REVIEWS formales de ingeniería de sistemas: MCR, SRR, PDR, CDR, SIR/EMR, TRR, SAR y transfer review. No son alias, ni una reemplaza o repurposa a la otra.

**Estado de implementación.** El núcleo genérico está implementado: capacidad `docs_review`, skill `runtime/skills/docs-review/SKILL.md`, backend único `runtime/skills/docs-review/scripts/docs_review.ps1`, contrato `references/manifest-contract.md`, catálogo conceptual, registry operativo, payload y pruebas estáticas. En Linux, el gate estático actual pasó **8/8** y los mirrors están presentes; esto **no** verifica el comportamiento en Windows. Sigue pendiente ejecutar `tests/powershell/docs_review.tests.ps1` en Windows PowerShell Desktop 5.1; no hay CI Windows por decisión humana. No se agregaron plantillas en `framework/proyecto/docs-*`: el backend crea paquetes bajo `proyecto/docs-verificacion/**` y `proyecto/docs-aprobados/**` a demanda. La primera consumidora diseñada, `f1_stakeholders_formal`, está implementada como skill de fase pura (`runtime/skills/f1-stakeholders-formal`) que emite al padre la especificación de paquete; la composición con este núcleo la selecciona y ejecuta el padre ante autorización humana explícita.

## Camino feliz

1. Una skill de fase declara **readiness** y emite al padre una especificación exacta del paquete; no convoca ni opera la review.
2. Ante una instrucción humana explícita, por ejemplo «Presentemos F1 formal a verificación», el **orquestador padre**, ejecutado dentro del harness Codex, selecciona, resuelve, carga y compone `docs-review` con `f1-stakeholders-formal`.
3. Codex ejecuta el contrato ya seleccionado y el script interno de `docs-review`; el usuario no escribe comandos. `Prepare` y `Submit` crean y someten el paquete únicamente con la autorización conversacional explícita ya recibida.
4. El revisor humano dicta `aprobado` o `rechazado`; `RecordDecision` solo transcribe y valida esa decisión, nunca la escoge.
5. Con paquete completo aprobado, una orden humana explícita habilita `Promote`; el padre refleja después los espejos en los vivos y evalúa el cierre.

## Actores y autoridad

| Actor | Responsabilidad | Nunca hace |
| --- | --- | --- |
| Ingeniero humano | Autoriza sometimiento, decisión y promoción; dicta identidad, rol, fecha, fuente, decisión y hallazgos. | Editar un paquete sometido/terminal o revertir una decisión terminal. |
| Orquestador padre lógico | Lee estado, selecciona/resuelve/carga/compone skills, dirige la ejecución y persiste únicamente los vivos y sus espejos derivados. | Delegar en una skill la decisión humana o inferir una reparación. |
| Codex | Harness y mecanismo de ejecución del contrato ya seleccionado por el padre, incluido el script interno. | Ser un router independiente, decidir qué skill invocar o escoger aprobar/rechazar. |
| `docs-review` | Rige el ciclo genérico, gates, máquina de estados y uso autorizado del backend mecánico. | Decidir el veredicto o modificar documentos vivos. |
| Skill de fase | Declara readiness y la especificación exacta; valida en solo lectura y propone cierres al padre. | Invocar `docs-review`, armar/copiar/promover paquetes o autorizar review. |

La partición de escritura no rompe el single-writer: el padre es único escritor de `proyecto/fases/**`, `proyecto/estado/**`, `proyecto/hitos/**` y `proyecto/registros/**`; las superficies `docs-verificacion/**` y `docs-aprobados/**` pertenecen a la autoridad humana, cuya mecánica se ejecuta mediante el contrato ya compuesto. El consentimiento de herramientas de Codex nunca equivale a aprobación de ingeniería.

## Hoja de diseño: `docs_review`

| Campo | Diseño decidido |
| --- | --- |
| Id y tipo | `docs_review` / `tarea puntual` para el ciclo genérico de paquete documental; reutilizable entre fases y distinta de `preparacion_de_review`. |
| Ejecutable y backend | `docs-review`; backend único implementado en `runtime/skills/docs-review/scripts/docs_review.ps1`. |
| Disparadores | Instrucción humana explícita para preparar, someter, registrar una decisión, promover o validar un paquete, después de que el padre haya resuelto una especificación de paquete válida. |
| Entradas | Raíz del proyecto; acción; especificación exacta de scope, madurez, artefactos y contexto de revisión; identidad/attestation humana cuando aplique; paquete existente cuando aplique. |
| Salidas | Paquete preparado/sometido, decisión registrada, paquete promovido o informe de validación determinista; siempre con estado observado, hashes y bloqueo explícito si falla. |
| Autoridades | El humano decide y autoriza; el padre selecciona/compone/dirige; la skill y el script realizan solo mecánica validada; Codex ejecuta el contrato ya seleccionado. |
| Fuentes de estado | `manifest.md` del paquete y snapshots; para gates, las copias de verificación/aprobadas y los documentos vivos en solo lectura. No requiere Git ni otra fuente externa. |
| Contrato de composición | La skill de fase entrega al padre readiness más especificación exacta. El padre, no Codex por sí solo ni la skill de fase, compone la fase con `docs-review`. Una fase nunca invoca otra skill. |
| No dependencia | Sin Python en operación posterior al scaffolding, `pwsh`, módulos o ejecutables externos, Git, MCP, daemon, BD, UI web ni parser o implementación YAML; el bloque se procesa como JSON con `ConvertFrom-Json` integrado. |

### Backend mecánico implementado

El único backend es `runtime/skills/docs-review/scripts/docs_review.ps1`, para **Windows PowerShell 5.1 integrado y .NET únicamente**. La instalación sigue siendo el flujo one-shot existente Python/pipx/`se-agent init`; después del scaffolding, operar la review documental no requiere Python. No hay fallback Python ni `pwsh`. La cobertura estática Linux pasó 8/8, pero la conducta del backend permanece pendiente de ejecutar con `tests/powershell/docs_review.tests.ps1` en Windows PowerShell Desktop 5.1; no existe CI Windows por decisión humana.

El padre puede ordenar a Codex la ejecución interna del `.ps1` solo bajo las instrucciones `docs-review` ya seleccionadas y una autorización conversacional humana explícita para la acción. El usuario nunca redacta ni ejecuta comandos. El script no aplica `ExecutionPolicy Bypass` automática ni indirectamente: si la política organizacional impide la ejecución, falla cerrado, lo informa y no sustituye la política.

Layout implementado:

```text
runtime/skills/docs-review/
├── SKILL.md
└── scripts/
    └── docs_review.ps1
```

### Acciones del script

| Acción | Precondiciones | Entrada y salida | Transición exacta | Idempotencia y fallo cerrado |
| --- | --- | --- | --- | --- |
| `Prepare` | Especificación válida, fuentes vivas existentes, ningún paquete activo incompatible. | Especificación exacta y raíz; crea paquete temporal y devuelve manifest/snapshots validados. | Crea `pendiente`; no somete. | Repetir sobre paquete coherente `pendiente` no lo muta; cualquier parcialidad, colisión o hash inválido bloquea. |
| `Submit` | Paquete `pendiente` completo y autorización de sometimiento. | Identidad/attestation de sometedor; devuelve manifest sometido. | `pendiente → en_verificacion`. | Repetir con mismo contenido y attestation ya registrada no cambia nada; datos distintos o estado distinto bloquean. |
| `RecordDecision` | Paquete íntegro `en_verificacion`, hashes válidos y decisión humana explícita. | Decisión `aprobado` o `rechazado`, attestation y hallazgos; devuelve manifest terminal. | `en_verificacion → aprobado` o `en_verificacion → rechazado`. | Repetir la misma decisión terminal es lectura idempotente; cualquier intento de sobrescribir, cambiar decisión o completar datos incompatibles bloquea. |
| `Promote` | Paquete completo `aprobado`, hashes válidos, destino ausente y orden humana explícita. | Paquete de verificación; devuelve ubicación aprobada validada. | Sin cambio de estado; publica copia idéntica en aprobados. | Si existe copia idéntica validada, informa éxito sin mutar; destino parcial, diferente o existente incompatible bloquea. |
| `Validate` | Ruta de paquete o de copia aprobada. | Paquete existente; devuelve informe solo lectura de estructura, manifest, hashes, estado y gates. | Ninguna. | Siempre sin escritura; cualquier ambigüedad, parcialidad o divergencia es resultado bloqueante. |

El script realiza mecánica, no juicio: jamás elige `aprobado` o `rechazado`, inventa attestation, repara, borra, infiere valores ni completa estados parciales.

### Seguridad, publicación e integridad

- **Confinamiento:** toda ruta se resuelve bajo la raíz de proyecto declarada. Se rechazan traversal, rutas absolutas como rutas relativas del paquete, ids inválidos, artefactos duplicados, archivos inesperados y cualquier escape mediante reparse point o symlink.
- **Publicación segura:** `Prepare` crea el paquete temporal en el mismo volumen del destino y lo publica solo tras validar el conjunto completo. Nunca sobrescribe una ruta terminal ni sustituye destinos existentes; no hay reparación, borrado ni limpieza inferida ante un fallo.
- **Estados:** se rechazan transiciones inválidas, estados parciales, sobreescritura terminal, manifiestos incompatibles y hash mismatches. El script no modifica un paquete `en_verificacion`, `aprobado` o `rechazado` salvo la transición permitida de decisión desde `en_verificacion`.
- **Contenido:** `content_sha256` se calcula sobre bytes crudos del snapshot y sigue siendo independiente de Git. Antes de `RecordDecision`, `Promote` y `Validate` se recomputa y compara. `source_git_revision`, si se registra, es solo procedencia opcional.
- **Texto generado:** manifest y texto generado son deterministas: UTF-8 sin BOM y saltos LF, evitando las codificaciones y CRLF predeterminados de Windows PowerShell 5.1.

### Manifest estricto, versionado y legible

Se conserva la decisión de `manifest.md` con frontmatter delimitado por YAML y cuerpo Markdown humano, pero el bloque de máquina es **un único objeto JSON canónico estricto**, que es un subconjunto válido de YAML 1.2, entre los delimitadores `---`. No se acepta YAML libre. El script implementado para Windows PowerShell 5.1 extrae exactamente ese bloque y usa el `ConvertFrom-Json` integrado; no implementa ni incorpora un parser YAML, módulo o ejecutable externo.

Tras convertirlo, valida por versión las claves conocidas, la estructura exacta, los tipos y los valores enumerados; reserializa la estructura validada en la forma JSON canónica y compara los bytes con el bloque original. La discrepancia bloquea. Con ello rechaza entradas no canónicas, claves duplicadas o desconocidas, estructuras adicionales y cualquier construcción YAML o JSON no admitida. La forma canónica usa las claves en el orden del esquema, dos espacios para cada nivel de indentación, `null` literal, cadenas JSON con escape estándar y LF; tanto el `manifest.md` completo como el bloque se emiten en UTF-8 sin BOM.

En cada entrada de `artifacts`, `carried_forward_from` es obligatorio y vale exactamente `null` o el objeto `{"package_id":"<id de paquete anterior>","path":"<ruta relativa del snapshot anterior>"}`. Ambos campos del objeto son cadenas no vacías: `package_id` identifica un paquete terminal anterior de la misma cadena lineal de `scope`, y `path` identifica una entrada de artefacto de ese manifest. En `r001` vale `null` para todos los artefactos. Si no es `null`, el snapshot actual debe ser byte a byte idéntico al referenciado y su `content_sha256` debe coincidir exactamente con el hash de ese snapshot anterior; cualquier referencia inexistente, ambigua o divergencia bloquea.

Esquema mínimo conceptual en JSON canónico:

```markdown
---
{
  "manifest_version": 1,
  "package_id": "f1-stakeholders-formal-r001",
  "scope": "f1-stakeholders",
  "phase": "F1",
  "maturity": "formal",
  "revision": 1,
  "predecessor_package_id": null,
  "state": "en_verificacion",
  "submitted_by": "<identidad>",
  "submitted_at": "<fecha>",
  "reviewer": null,
  "review_decision": null,
  "reviewed_at": null,
  "source_git_revision": null,
  "artifacts": [
    {
      "path": "requisitos_stakeholders.md",
      "document_type": "stakeholder_requirements",
      "source_path": "proyecto/fases/f1_stakeholders/requisitos_stakeholders.md",
      "carried_forward_from": null,
      "content_sha256": "<sha256 de bytes crudos>",
      "review_outcome": null
    },
    {
      "path": "escenarios_operativos.md",
      "document_type": "operational_scenarios",
      "source_path": "proyecto/fases/f1_stakeholders/escenarios_operativos.md",
      "carried_forward_from": null,
      "content_sha256": "<sha256 de bytes crudos>",
      "review_outcome": null
    },
    {
      "path": "restricciones_externas.md",
      "document_type": "external_constraints",
      "source_path": "proyecto/fases/f1_stakeholders/restricciones_externas.md",
      "carried_forward_from": null,
      "content_sha256": "<sha256 de bytes crudos>",
      "review_outcome": null
    },
    {
      "path": "matriz_necesidad_requisito_stakeholder.md",
      "document_type": "need_stakeholder_requirement_matrix",
      "source_path": "proyecto/fases/f1_stakeholders/matriz_necesidad_requisito_stakeholder.md",
      "carried_forward_from": null,
      "content_sha256": "<sha256 de bytes crudos>",
      "review_outcome": null
    }
  ]
}
---

## Propósito del paquete

## Attestation de sometimiento

## Attestation de revisión

## Hallazgos
```

El cuerpo conserva las attestations (identidad, rol, fecha, fuente), hallazgos por documento y referencia al predecesor. Una attestation v1 es explícita y no criptográfica.

## Semántica preservada del paquete

### Unidad, ids y snapshots

- La unidad de review es el paquete completo. Para F1 formal contiene exactamente cuatro snapshots: `requisitos_stakeholders.md`, `escenarios_operativos.md`, `restricciones_externas.md` y `matriz_necesidad_requisito_stakeholder.md`.
- El id es `<scope>-<madurez>-r<NNN>`; las resometidas usan un nuevo id y `predecessor_package_id`. La cadena es lineal por scope y solo puede existir un paquete activo no terminal por scope.
- Tras `Submit`, snapshots y manifiesto se congelan salvo la incorporación de la decisión humana permitida. Tras estado terminal el paquete completo es inmutable.
- Si se rechaza cualquier documento, se rechaza el paquete completo. Las correcciones ocurren solo en vivos; una resometida puede transportar snapshots no afectados byte-idénticos solo con la referencia `carried_forward_from` válida al paquete y ruta anteriores, conservando exactamente el `content_sha256` referenciado.

### Máquina de estados y congelamiento

```text
pendiente --Submit autorizado--> en_verificacion --RecordDecision humano--> aprobado | rechazado
                                                          aprobado --Promote autorizado--> copia aprobada idéntica
```

No existen `en_revision`, `promovido` ni `invalidado`. Durante `en_verificacion`, los documentos vivos del scope están congelados; comparar sus hashes con el snapshot detecta cambios y bloquea aprobación/cierre. Un paquete corrupto no cambia de estado: es contradicción fail-closed para disposición humana.

### Promoción, espejos y cierre

`Promote` vuelve a validar cada hash y publica una copia byte a byte idéntica. El padre, leyendo el paquete en solo lectura, puede reflejar la decisión ya humana en `doc_approval` e historial de los vivos. Un cierre formal exige conjuntamente:

1. copia aprobada válida;
2. conjunto exacto esperado, sin faltantes ni extras;
3. hashes recomputados e identidad/coherencia de manifest;
4. estado `aprobado` y attestation humana terminal completa;
5. copia aprobada idéntica a la de verificación;
6. gates de fase y dominio satisfechos.

La mera carpeta aprobada, un paquete parcial, hashes divergentes o espejos contradictorios no habilitan cierre. Validar un paquete coherente o una promoción ya idéntica es idempotente; nunca se infieren reparaciones.

## Ejemplo: F1 formal

`f1_stakeholders_formal` evalúa readiness y emite al padre una especificación exacta: scope `f1-stakeholders`, madurez `formal`, id propuesto/revisión y predecesor, y estos cuatro pares de ruta/tipo canónicos:

| Ruta viva | `document_type` |
| --- | --- |
| `proyecto/fases/f1_stakeholders/requisitos_stakeholders.md` | `stakeholder_requirements` |
| `proyecto/fases/f1_stakeholders/escenarios_operativos.md` | `operational_scenarios` |
| `proyecto/fases/f1_stakeholders/restricciones_externas.md` | `external_constraints` |
| `proyecto/fases/f1_stakeholders/matriz_necesidad_requisito_stakeholder.md` | `need_stakeholder_requirement_matrix` |

Implementada `f1-stakeholders-formal`, ante «Presentemos F1 formal a verificación» el padre la compone con `docs-review`. F1 no llama a la skill genérica ni ejecuta mecánica. Codex ejecuta el contrato ya compuesto y, con autorización humana explícita, el script ya seleccionado. La composición la dirige el padre; el núcleo genérico ya implementado conserva sus reglas de aprobación/rechazo, promoción y gates.

## Criterios de aceptación del diseño

- [ ] `docs_review`/`docs-review` tiene exclusivamente el tipo de catálogo `tarea puntual`, es reutilizable entre fases y permanece separada de `preparacion_de_review`, que conserva exclusivamente los REVIEWS formales del marco.
- [ ] El padre lógico dentro de Codex selecciona, resuelve, carga y compone skills; Codex ejecuta el contrato ya seleccionado y no enruta de forma independiente.
- [x] El backend único implementado es `runtime/skills/docs-review/scripts/docs_review.ps1`, Windows PowerShell 5.1 + .NET, sin Python operativo, `pwsh`, ejecutables/módulos externos, Git, MCP, daemon, BD, UI web ni bypass automático de ExecutionPolicy.
- [x] `Prepare`, `Submit`, `RecordDecision`, `Promote` y `Validate` están implementados con las precondiciones, salidas, transiciones, idempotencia y fail-closed definidos aquí; el script nunca decide un veredicto.
- [x] El gate estático Linux actual pasó 8/8, incluidos los mirrors requeridos.
- [ ] Ejecutar `tests/powershell/docs_review.tests.ps1` en Windows PowerShell Desktop 5.1 para verificar conducta; no hay CI Windows por decisión humana.
- [ ] Se rechazan escapes de ruta/reparse points, ids/transiciones inválidos, duplicados, extras, sobreescrituras terminales, parciales y divergencias de hash; no hay borrar, reparar ni inferir.
- [ ] Los hashes son SHA-256 de bytes crudos, Git-independientes; el texto generado es UTF-8 sin BOM y LF; el frontmatter delimitado por YAML contiene exclusivamente el objeto JSON canónico versionado, convertido con `ConvertFrom-Json`, validado y comparado byte a byte tras su reserialización canónica.
- [ ] Se preservan paquete completo, congelamiento, rechazo sin aprobación parcial, resometida con predecesor y transporte declarado por paquete+ruta con hash idéntico, promoción idéntica, espejos derivados y todos los gates de cierre.
- [x] La skill F1 formal emite al padre la especificación exacta de cuatro documentos y este compone `docs-review` tras la frase humana explícita; `runtime/skills/f1-stakeholders-formal` está implementada como skill de fase pura. F1 no invoca otra skill.

## Implicaciones diferidas

| Tema | Diferido a |
| --- | --- |
| Núcleo `docs-review`: `SKILL.md`, backend `.ps1`, contrato JSON canónico, catálogo, bindings, registry, payload y pruebas estáticas | Implementado. El gate estático Linux actual pasó 8/8; falta verificar conducta ejecutando la suite nativa en Windows PowerShell Desktop 5.1. |
| CI Windows | Diferido por decisión humana; no hay CI Windows para la suite nativa. |
| Plantillas en `framework/proyecto/docs-*` | No implementadas ni requeridas: el backend crea los paquetes bajo las rutas de proyecto a demanda. |
| Integración ejecutable de F1 formal | Implementada (skill de fase pura): `runtime/skills/f1-stakeholders-formal` emite la especificación de paquete; la composición con `docs-review` la ejecuta el padre ante autorización humana. |

## Relacionado

- [design-skill-marco.md](design-skill-marco.md) — reglas de composición y frontera entre capacidades.
- [design-f1-stakeholders-handoff.md](design-f1-stakeholders-handoff.md) — especificación F1 que alimenta este ciclo.
- [orchestrator.md](orchestrator.md) — padre lógico y Codex como mecanismo de ejecución.
- [domain-harness-boundary.md](domain-harness-boundary.md) — frontera entre dominio y detalle de runtime.
