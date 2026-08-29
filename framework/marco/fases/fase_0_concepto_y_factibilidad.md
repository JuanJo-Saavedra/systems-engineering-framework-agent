---
phase_id: F0
phase_name: Concepto y factibilidad
question: "¿Conviene hacer esto?"
lifecycle_scope: preproyecto_presupuesto
allowed_maturity:
  - preliminar
default_maturity: preliminar
review: MCR / Concept Review
baseline: No aplica baseline formal
next_gate: F1 preliminar
transversal_processes:
  - requisitos
  - riesgos
  - decisiones_tecnicas
  - datos_y_documentacion
---

# Fase 0 - Concepto y factibilidad

## Objetivo operativo
Transformar una necesidad, problema u oportunidad en una definición preliminar de misión, alcance, viabilidad y continuidad suficiente para decidir si conviene avanzar con un presupuesto.

## Rol en la plantilla
Es la fase de apertura del preproyecto. Debe reducir incertidumbre inicial sin exigir todavía definición técnica propia de `F2`.

## Entradas mínimas
- necesidad detectada
- solicitud de cliente o sponsor
- contexto preliminar
- restricciones iniciales conocidas

## Actividades guía
- capturar la necesidad u oportunidad
- identificar stakeholders iniciales
- formular el problema
- construir CONOPS preliminar
- estimar plazo y costo ROM
- identificar riesgos iniciales
- recomendar Go / No-Go

## Salidas esperadas
- problema enunciado de forma clara
- viabilidad preliminar documentada
- riesgos iniciales identificados
- recomendación formal de continuidad

## Artefactos obligatorios
- registro de oportunidad o necesidad
- stakeholder map inicial
- CONOPS preliminar
- lista preliminar de necesidades
- registro inicial de riesgos
- estimación ROM
- informe de factibilidad / continuidad

## Review y baseline
- Review asociada: `MCR / Concept Review`
- Baseline: no aplica baseline formal

## Registros transversales a tocar
- `riesgos`
- `decisiones_tecnicas`, si una decisión temprana afecta la factibilidad
- `requisitos`, solo al nivel de necesidad preliminar

## Criterios de cierre
- existe una definición preliminar del problema
- existe una recomendación Go / No-Go
- existen riesgos iniciales visibles
- hay material suficiente para abrir `F1 preliminar`

## Guía para el subagente de fase
Prioriza claridad del problema, factibilidad y límites del presupuesto. No intentes resolver todavía el diseño técnico del sistema.
