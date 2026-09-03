---
document_type: operational_scenarios
language: es
active_maturity: preliminar
last_updated: YYYY-MM-DD
doc_approval: pendiente
responsible: "<identidad>"
---

# Escenarios operativos

## Objetivo

Formalizar los casos de uso y escenarios operativos que muestran cómo los stakeholders usarán o interactuarán con el sistema en su contexto, en el nivel de abstracción propio de `F1`: escenarios de uso de alto nivel que fundamentan las necesidades, sin derivar funciones ni diseño de sistema.

## Madurez compartida (preliminar y formal)

Este archivo es **único por proyecto**: `F1 preliminar` lo crea y lo entrega en madurez `preliminar`, y `F1 formal` madura **el mismo archivo** a `formal`. No se crean copias por madurez. La madurez activa queda en `active_maturity`, el estado de aprobación vigente en `doc_approval`, y la trayectoria de aprobaciones en la sección [`## Historial de aprobación`](#historial-de-aprobación).

## Expectativas por madurez

| Madurez      | Qué se espera                                                                                              | Qué no se exige                                                                                              |
| ------------ | ---------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------ |
| `preliminar` | Escenarios de uso representativos del contexto de operación, suficientes para entender el alcance y cotizar. | No se exige cobertura exhaustiva de escenarios, ni flujo detallado paso a paso, ni casos de error completos. |
| `formal`     | Escenarios de uso relevantes completos y consistentes con las necesidades formalizadas; vacíos heredados cerrados. | No se diseñan soluciones ni se asignan funciones al sistema: eso corresponde a `F2`.                          |

## Estructura del documento

### Índice de escenarios

| ID (ESC-NNN) | Nombre del escenario | Actor(es) / Stakeholder(es) | Objetivo del actor | Contexto de uso | Clase de evidencia |
| ------------ | -------------------- | ----------------------------- | ------------------ | --------------- | ------------------ |
| ESC-001      |                      |                               |                    |                 |                    |

### Detalle de escenario (repetir por escenario)

#### ESC-NNN — `<nombre del escenario>`

- Actor(es) principal(es):
- Objetivo del actor:
- Precondiciones:
- Flujo principal (pasos a alto nivel):
- Flujos alternativos o excepciones relevantes:
- Resultado esperado (criterio de aceptación de alto nivel, si aplica):
- Fuente:
- Clase de evidencia:

## Clasificación de la evidencia

Toda entrada se clasifica en una de cuatro clases, en la columna o campo `Clase de evidencia`:

| Clase | Significado |
| ------------------- | ----------------------------------------------------------------------------------------------- |
| `hechos verificados` | Escenario observado o respaldado por una fuente consultable y verificada (minutas, sitio, operación real). |
| `supuestos` | Escenario asumido como probable sin verificación aún; debe citarse como tal. |
| `vacíos` | Contexto de uso u operación relevante sin escenario capturado; se declara explícitamente, sin fabricar contenido. |
| `contradicciones` | Escenarios o contextos incompatibles entre stakeholders o fuentes; se registran visibles para resolución humana. |

Los `vacíos` y `contradicciones` pendientes se listan en esta sección al cierre de cada madurez:

- Vacíos abiertos:
- Contradicciones abiertas:

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
