---
name: f0_factibilidad
description: "Trigger: fase F0 activa o estado preproyecto_presupuesto; formular el problema, stakeholders iniciales, CONOPS preliminar, estimación ROM, riesgos iniciales o recomendación Go/No-Go. Ejecuta la fase F0 (Concepto y factibilidad) del marco."
---

# f0_factibilidad — Fase F0: Concepto y factibilidad

## Disparador

Activa esta skill cuando la fase activa sea `F0`, el estado del proyecto sea `preproyecto_presupuesto`, o la persona usuaria pida formular el problema, el mapa de stakeholders inicial, el CONOPS preliminar, la lista preliminar de necesidades, la estimación ROM, los riesgos iniciales o la recomendación Go / No-Go.

## Autoridad

Esta skill es un adaptador ejecutable: guía la ejecución de la fase F0 pero nunca es autoridad sobre el significado del dominio. La autoridad del dominio vive en `AGENTS.md` y en `marco/`; el Markdown autoritativo de `proyecto/` gana cualquier conflicto. No inventes el estado del proyecto: léelo primero desde `proyecto/estado/`.

## Fuentes autoritativas (leer primero)

1. `AGENTS.md` — contrato de runtime y guardrails comunes.
2. `marco/fases/fase_0_concepto_y_factibilidad.md` — contrato completo de la fase F0.
3. `proyecto/registros/riesgos.md` — registro de riesgos.
4. `proyecto/registros/decisiones_tecnicas.md` — registro de decisiones técnicas.

Las rutas bajo `proyecto/` son estado escrito por el runtime: solicítalas y léelas si existen; nunca las inventes ni las crees desde esta skill.

## Procedimiento

Ejecuta las actividades guía y produce los artefactos obligatorios definidos en `marco/fases/fase_0_concepto_y_factibilidad.md`:

1. Captura la necesidad u oportunidad y su contexto preliminar.
2. Identifica los stakeholders iniciales y construye el stakeholder map inicial.
3. Formula el problema y construye el CONOPS preliminar.
4. Elabora la lista preliminar de necesidades.
5. Identifica los riesgos iniciales y propón su registro en `proyecto/registros/riesgos.md` (single-writer: el orquestador padre consolida los documentos autoritativos).
6. Estima plazo y costo ROM.
7. Produce el informe de factibilidad / continuidad con recomendación formal Go / No-Go.

Respeta la madurez `preliminar`: prioriza claridad del problema, factibilidad y límites del presupuesto; no fuerces detalle técnico propio de F2. La transición `F0` → `F1` preliminar requiere necesidad entendible y recomendación de continuidad para cotizar.

## Guardrails de cierre

Cierra F0 solo cuando existan: definición preliminar del problema, recomendación Go / No-Go, riesgos iniciales visibles y material suficiente para abrir `F1` preliminar. Aplica los guardrails comunes heredados del contrato de runtime (`AGENTS.md`): no inventar estado, entregables ni evidencia; sin evidencia autoritativa, señalarlo y pedirla; no abrir la fase siguiente si el criterio de cierre no está satisfecho.
