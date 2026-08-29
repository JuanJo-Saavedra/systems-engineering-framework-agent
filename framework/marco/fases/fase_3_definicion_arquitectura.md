---
phase_id: F3
phase_name: Definición de arquitectura
question: "¿Qué arquitectura resuelve el problema?"
lifecycle_scope: proyecto_formal
allowed_maturity:
  - formal
default_maturity: formal
review: PDR
baseline: Allocated Baseline
next_gate: F4
transversal_processes:
  - requisitos
  - interfaces
  - riesgos
  - decisiones_tecnicas
  - configuracion
---

# Fase 3 - Definición de arquitectura

## Objetivo operativo
Definir la solución técnica candidata capaz de satisfacer los requerimientos del sistema con riesgo aceptable.

## Entradas mínimas
- SyRS aprobada
- restricciones de implementación
- alternativas tecnológicas relevantes
- riesgos técnicos conocidos

## Actividades guía
- desarrollar arquitectura funcional
- desarrollar arquitectura lógica
- desarrollar arquitectura física preliminar
- identificar CIs
- asignar preliminarmente requerimientos
- identificar interfaces
- realizar trade-offs
- definir estrategia preliminar de integración y V&V

## Salidas esperadas
- arquitectura seleccionada y justificada
- requisitos asignados preliminarmente
- interfaces principales identificadas
- base para diseño detallado

## Artefactos obligatorios
- architecture description
- PBS preliminar
- ICDs preliminares
- trade-off reports
- matriz requisito <-> CI
- plan preliminar de integración
- V&V plan actualizado
- risk register actualizado

## Review y baseline
- Review asociada: `PDR`
- Baseline asociada: `Allocated Baseline`

## Registros transversales a tocar
- `requisitos`
- `interfaces`
- `riesgos`
- `decisiones_tecnicas`
- `configuracion`

## Criterios de cierre
- arquitectura seleccionada formalmente
- CIs identificados
- interfaces principales definidas
- riesgos técnicos principales tratados
- estrategia de integración definida

## Guía para el subagente de fase
Documenta por qué una arquitectura es preferible frente a otras. Toda elección importante debe dejar rastro en decisiones técnicas.
