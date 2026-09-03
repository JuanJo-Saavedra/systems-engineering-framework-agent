---
document_type: external_constraints
language: es
active_maturity: preliminar
last_updated: YYYY-MM-DD
doc_approval: pendiente
responsible: "<identidad>"
---

# Restricciones externas

## Objetivo

Registrar las restricciones impuestas al proyecto desde fuera del sistema: normativa, regulación, negocio, contractuales, del entorno o de operación, en el nivel de abstracción propio de `F1`: restricciones identificadas con su fuente y obligatoriedad, sin derivar decisiones de diseño ni soluciones.

## Madurez compartida (preliminar y formal)

Este archivo es **único por proyecto**: `F1 preliminar` lo crea y lo entrega en madurez `preliminar`, y `F1 formal` madura **el mismo archivo** a `formal`. No se crean copias por madurez. La madurez activa queda en `active_maturity`, el estado de aprobación vigente en `doc_approval`, y la trayectoria de aprobaciones en la sección [`## Historial de aprobación`](#historial-de-aprobación).

## Expectativas por madurez

| Madurez      | Qué se espera                                                                                                   | Qué no se exige                                                                                                  |
| ------------ | ---------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------- |
| `preliminar` | Restricciones externas a alto nivel con su fuente, suficientes para acotar el alcance y cotizar; supuestos marcados como tales. | No se exige citar normativa completa ni confirmar cada restricción con su fuente legal definitiva.                 |
| `formal`     | Restricciones externas consolidadas y confirmadas con fuente; restricciones por confirmar del presupuesto cerradas. | No se traducen restricciones en requisitos de sistema ni en decisiones de diseño: eso corresponde a `F2`.          |

## Estructura del documento

### Registro de restricciones

| ID (RES-NNN) | Tipo de restricción | Descripción | Fuente | Obligatoriedad | Estado de confirmación | Clase de evidencia |
| ------------ | ------------------- | ----------- | ------ | -------------- | ---------------------- | ------------------ |
| RES-001      |                     |             |        |                |                        |                    |

Tipos de restricción sugeridos: `normativa`, `regulatoria`, `legal`, `contractual`, `negocio`, `entorno`, `operación`.

Valores de `Obligatoriedad` sugeridos: `obligatoria`, `condicionada`, `recomendación`.

Valores de `Estado de confirmación` sugeridos: `confirmada`, `por confirmar`.

## Clasificación de la evidencia

Toda entrada se clasifica en una de cuatro clases, en la columna `Clase de evidencia`:

| Clase | Significado |
| ------------------- | ------------------------------------------------------------------------------------------------ |
| `hechos verificados` | Restricción respaldada por una fuente consultable y verificada (norma, contrato, política). |
| `supuestos` | Restricción asumida sin verificación aún; debe citarse como tal y quedar `por confirmar`. |
| `vacíos` | Ámbito externo relevante cuya situación de restricciones se desconoce; se declara explícitamente, sin fabricar contenido. |
| `contradicciones` | Restricciones o fuentes incompatibles entre sí o entre stakeholders; se registran visibles para resolución humana. |

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
