---
document_type: need_stakeholder_requirement_matrix
language: es
active_maturity: preliminar
last_updated: YYYY-MM-DD
doc_approval: pendiente
responsible: "<identidad>"
---

# Matriz necesidad ↔ stakeholder requirement

## Objetivo

Trazar cada necesidad de stakeholder registrada en [requisitos_stakeholders.md](requisitos_stakeholders.md) hacia los stakeholder requirements que la cubren, y viceversa, para detectar necesidades sin cobertura, requisitos huérfanos y contradicciones de trazabilidad, en el nivel de abstracción propio de `F1`.

## Madurez compartida (preliminar y formal)

Este archivo es **único por proyecto**: `F1 preliminar` lo crea y lo entrega en madurez `preliminar`, y `F1 formal` madura **el mismo archivo** a `formal`. No se crean copias por madurez. La madurez activa queda en `active_maturity`, el estado de aprobación vigente en `doc_approval`, y la trayectoria de aprobaciones en la sección [`## Historial de aprobación`](#historial-de-aprobación).

## Expectativas por madurez

| Madurez      | Qué se espera                                                                                                    | Qué no se exige                                                                                                  |
| ------------ | ---------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------- |
| `preliminar` | Trazabilidad completa de las necesidades capturadas a los stakeholder requirements preliminares; vacíos de cobertura declarados. | No se exige cobertura perfecta ni trazabilidad hacia system requirements: la derivación a `F2` no existe todavía.   |
| `formal`     | Cobertura bidireccional completa y sin huérfanos entre necesidades y stakeholder requirements; contradicciones de trazabilidad resueltas. | No se extiende la matriz hacia system requirements ni métodos de verificación: esa trazabilidad nace en `F2`.       |

## Estructura del documento

### Matriz de trazabilidad

| Necesidad (NEC-NNN) | Stakeholder(s) | Stakeholder requirement(s) (SR-NNN) | Cobertura | Observación / fuente |
| ------------------- | -------------- | ------------------------------------ | --------- | -------------------- |
| NEC-001             |                |                                      |           |                      |

Valores de `Cobertura` sugeridos: `completa`, `parcial`, `sin trazabilidad`.

### Verificación de trazabilidad

Al cierre de cada madurez, revisar y registrar aquí:

- Necesidades sin ningún stakeholder requirement vinculado (`sin trazabilidad`):
- Stakeholder requirements que no trazan a ninguna necesidad (huérfanos):
- Necesidades con múltiples requisitos contradictorios o incompatibles entre sí:

## Clasificación de la evidencia

Toda fila de la matriz debe poder justificarse; el estado de la trazabilidad se clasifica en una de cuatro clases, registradas en la verificación de trazabilidad y en `Observación / fuente` cuando aplique:

| Clase | Significado |
| ------------------- | -------------------------------------------------------------------------------------------------- |
| `hechos verificados` | Vínculo necesidad ↔ requirement respaldado por una fuente consultable (minuta, decisión validada con el stakeholder). |
| `supuestos` | Vínculo asumido sin validación con el stakeholder aún; debe citarse como tal. |
| `vacíos` | Necesidad sin cobertura o requirement huérfano; se declara explícitamente, sin fabricar vínculos. |
| `contradicciones` | Vínculos incompatibles entre sí o con lo declarado por los stakeholders; se registran visibles para resolución humana. |

## Ciclo de aprobación (`doc_approval`)

Valores permitidos: `pendiente`, `aprobado`, `rechazado`.

1. **Trabajo preliminar:** el documento trabaja con `doc_approval: pendiente`.
2. **Cierre preliminar:** el humano aprueba y `doc_approval` pasa a `aprobado`; la aprobación se registra en el historial.
3. **Trabajo formal:** al iniciar `F1 formal`, `doc_approval` se **resetea a `pendiente`**; el historial preliminar se preserva íntegro.
4. **Cierre formal:** el humano aprueba y `doc_approval` vuelve a `aprobado`.

El campo `responsible` del frontmatter identifica al **custodio humano vigente** del documento (quien responde por que esté actualizado y coherente); no es el aprobador. La identidad de quien aprueba se registra únicamente en el historial de aprobación.

## Historial de aprobación

| Madurez     | Estado     | Fecha       | Aprobador | Fuente |
| ----------- | ---------- | ----------- | --------- | ------ |
| preliminar  | pendiente  |             |           |        |
| formal      | pendiente  |             |           |        |
