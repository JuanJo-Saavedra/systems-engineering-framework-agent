---
document_type: project_state
project_status: preproyecto_presupuesto
active_phase: F0
active_maturity: preliminar
approval_handoff_status: pendiente
last_updated: YYYY-MM-DD
---
# Estado actual del proyecto

## Cómo usar este archivo

Actualiza este archivo cada vez que cambie el estado global del trabajo. El orquestador lo usa como fuente principal para decidir si está guiando presupuesto, transición o proyecto formal.

## Estados permitidos

- `preproyecto_presupuesto`
- `aprobado_en_transicion`
- `proyecto_formal`
- `cerrado`

## Estados permitidos de `approval_handoff_status`

Solo existen dos valores:

- `pendiente` (valor inicial): todavía no hay handoff de aprobación consolidado.
- `consolidado`: la transición de presupuesto a proyecto aprobado ya consolidó el handoff.

Este campo complementa al estado global; no lo reemplaza.

## Estado actual

- Estado global: `preproyecto_presupuesto`
- Fase activa: `F0`
- Madurez activa: `preliminar`
- Hito de aprobación: `pendiente`

## Regla de lectura

- Si el estado es `preproyecto_presupuesto`, se trabaja `F0` y `F1 preliminar`.
- Si el estado es `aprobado_en_transicion`, el handoff ya quedó consolidado y el próximo trabajo enrutado es `F1 formal`.
- Si el estado es `proyecto_formal`, se permite avanzar en `F2`-`F8`.

## Próximo paso esperado

Completar la información de `F0` y definir si corresponde abrir `F1 preliminar`.
