---
document_type: stakeholder_requirements
language: es
active_maturity: preliminar
last_updated: YYYY-MM-DD
doc_approval: pendiente
responsible: "<identidad>"
---

# Requisitos de stakeholders

## Objetivo

Formalizar las necesidades y expectativas de los stakeholders del proyecto (cliente, usuario, operación, negocio, normativa y entorno) en un nivel de abstracción propio de `F1`: necesidades y stakeholder requirements, sin descender a requerimientos de sistema.

## Madurez compartida (preliminar y formal)

Este archivo es **único por proyecto**: `F1 preliminar` lo crea y lo entrega en madurez `preliminar`, y `F1 formal` madura **el mismo archivo** a `formal`. No se crean copias por madurez. La madurez activa queda en `active_maturity`, el estado de aprobación vigente en `doc_approval`, y la trayectoria de aprobaciones en la sección [`## Historial de aprobación`](#historial-de-aprobación).

## Expectativas por madurez

| Madurez      | Qué se espera                                                                                                    | Qué no se exige                                                                                    |
| ------------ | ---------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------- |
| `preliminar` | Necesidades y expectativas a alto nivel, capturadas con fuente; base suficiente para cotizar y decidir la aprobación del trabajo. | No se exigen requisitos exhaustivos, ni descomposición técnica, ni criterios de verificación por requisito. |
| `formal`     | Vacíos heredados cerrados, contradicciones entre stakeholders resueltas y criterios de aceptación de alto nivel claros; base apta para abrir `F2`. | No se generan aquí requerimientos de sistema ni métodos de verificación formales: eso corresponde a `F2`.   |

## Estructura del documento

### Stakeholders y necesidades

| ID (NEC-NNN) | Stakeholder | Necesidad o expectativa | Fuente | Clase de evidencia | Prioridad |
| ------------ | ----------- | ----------------------- | ------ | ------------------ | --------- |
| NEC-001      |             |                         |        |                    |           |

### Stakeholder requirements

| ID (SR-NNN) | Necesidad vinculada (NEC-NNN) | Stakeholder(s) | Redacción | Fuente | Clase de evidencia | Prioridad | Criterio de aceptación de alto nivel |
| ----------- | ----------------------------- | -------------- | --------- | ------ | ------------------ | --------- | ------------------------------------ |
| SR-001      |                               |                |           |        |                    |           |                                      |

### Nivel de abstracción

- Válido en este documento: `necesidad` y `stakeholder requirement`.
- Fuera de nivel (no escribir aquí): `system requirement`, arquitectura, diseño detallado ni métodos de verificación. Pertenecen a `F2`.

## Clasificación de la evidencia

Toda entrada se clasifica en una de cuatro clases, en la columna `Clase de evidencia`:

| Clase | Significado |
| ------------------- | ---------------------------------------------------------------------- |
| `hechos verificados` | Afirmación respaldada por una fuente consultable y verificada. |
| `supuestos` | Afirmación asumida sin verificación aún; debe citarse como tal. |
| `vacíos` | Necesidad o stakeholder esperado cuya información falta; se declara explícitamente, sin fabricar contenido. |
| `contradicciones` | Afirmaciones incompatibles entre stakeholders o fuentes; se registran visibles para resolución humana. |

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
