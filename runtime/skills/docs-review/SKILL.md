---
name: docs-review
description: "Trigger: revisión documental, paquete de review, someter documentos, registrar decisión, promover paquete o validar manifest. Gobierna mecánicamente el ciclo humano de un paquete documental versionado."
license: Apache-2.0
metadata:
  author: autores del producto
  version: "1.0"
---

# docs-review — ciclo de paquete documental

## Activation Contract

Activa la capacidad conceptual `docs_review` exclusivamente ante una instrucción humana explícita para preparar, someter, registrar una decisión, promover o validar un paquete documental. Requiere que el padre ya haya resuelto una especificación exacta del paquete. No sustituye `preparacion_de_review`, reservada para los REVIEWS formales del marco.

## Hard Rules

- Trata el paquete completo como unidad inmutable: sus únicos estados son `pendiente`, `en_verificacion`, `aprobado` y `rechazado`.
- El humano autoriza sometimiento y promoción, y dicta identidad, attestation, decisión y hallazgos. Nunca infieras, elijas ni completes esos valores.
- Invoca internamente el backend presente `scripts/docs_review.ps1` en Windows PowerShell 5.1, con `-Operation` y `-RequestPath`; el usuario nunca escribe comandos.
- Si el backend falta físicamente o devuelve un resultado bloqueado, falla cerrado, informa la causa y no lo sustituyas con Python, `pwsh`, Git, módulos, ejecutables externos ni operaciones manuales equivalentes.
- No modifiques documentos vivos, espejos derivados ni un paquete parcial, terminal o con integridad inválida.

## Decision Gates

| Situación | Acción |
| --- | --- |
| Especificación, autorización o attestation requerida ausente | Bloquea y solicita el dato humano explícito. |
| Paquete o hashes inválidos, estado incompatible o ruta fuera de la raíz | Bloquea sin reparar, borrar ni sobrescribir. |
| Operación disponible y contrato válido | Invoca internamente el backend correspondiente. |
| Backend ausente o resultado bloqueado | Declara modo bloqueado; conserva toda evidencia sin mutarla. |

## Execution Steps

1. Lee `references/manifest-contract.md` y valida el request v1 antes de cualquier invocación.
2. Selecciona solo `Prepare`, `Submit`, `RecordDecision`, `Promote` o `Validate` según la orden humana y el estado observado.
3. Invoca internamente el backend presente en Windows PowerShell 5.1 con el request JSON versionado mediante la ruta autorizada; interpreta un único objeto JSON de resultado y falla cerrado si falta o devuelve bloqueo.
4. Relee el resultado y reporta estado, ruta de paquete, bloqueo, errores e invariantes de integridad; el padre decide cualquier espejo vivo posterior.

## Output Contract

Reporta la operación solicitada, estado observado, `package_path` cuando exista, hechos verificados, vacíos y bloqueos. Distingue siempre la decisión humana registrada de la mecánica ejecutada. No declares aprobación, promoción o cierre por inferencia.

## References

- `references/manifest-contract.md` — contrato v1 estricto de request, resultado y `manifest.md`.
