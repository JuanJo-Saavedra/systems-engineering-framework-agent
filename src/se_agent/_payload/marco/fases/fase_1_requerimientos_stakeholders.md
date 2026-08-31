---
phase_id: F1
phase_name: Requerimientos de stakeholders
question: "¿Qué necesitan los stakeholders?"
lifecycle_scope:
  - preproyecto_presupuesto
  - proyecto_formal
allowed_maturity:
  - preliminar
  - formal
default_maturity: preliminar
review: Stakeholder Requirements Review
baseline: No aplica baseline formal de sistema
next_gate:
  preliminar: hito_aprobacion_trabajo
  formal: F2
transversal_processes:
  - requisitos
  - interfaces
  - riesgos
  - datos_y_documentacion
---

# Fase 1 - Requerimientos de stakeholders

## Objetivo operativo
Capturar y formalizar qué necesitan cliente, usuario, operación, negocio, normativa y entorno.

## Rol en la plantilla
`F1` tiene dos niveles de madurez y es la fase puente entre presupuesto y proyecto formal.

## Modo preliminar para presupuesto
Usar `F1 preliminar` cuando el trabajo todavía no fue aprobado.

### Qué debe lograr
- comprender necesidades y restricciones externas a alto nivel
- definir alcance funcional preliminar
- reunir insumos suficientes para cotizar con fundamento

### Qué no debe exigir
- descomposición técnica completa
- redacción exhaustiva de requerimientos de sistema
- criterios de verificación formales por requisito

## Modo formal para proyecto aprobado
Usar `F1 formal` cuando el hito de aprobación ya fue emitido como `Aprobado`.

### Qué debe lograr
- completar y limpiar los vacíos heredados del presupuesto
- cerrar contradicciones entre stakeholders
- formalizar restricciones y criterios de aceptación de alto nivel
- dejar una base apta para abrir `F2`

## Entradas mínimas
- salida de `F0`
- minutas con cliente
- contexto de uso
- restricciones de negocio o regulatorias
- insumos heredados del presupuesto, si el trabajo ya fue aprobado

## Actividades guía
- identificar stakeholders relevantes
- relevar necesidades y expectativas
- formalizar escenarios de uso
- consolidar restricciones externas
- detectar criterios de aceptación de alto nivel
- validar consistencia con partes interesadas

## Salidas esperadas
- necesidades de stakeholders formalizadas
- restricciones externas identificadas
- alcance funcional de alto nivel definido
- base para derivar requerimientos de sistema

## Artefactos obligatorios
- stakeholder requirements document
- casos de uso o escenarios operativos
- restricciones externas
- matriz necesidad <-> stakeholder requirement

## Review y baseline
- Review asociada: `Stakeholder Requirements Review`
- Baseline: todavía no aplica baseline formal de sistema

## Registros transversales a tocar
- `requisitos`
- `interfaces`, al menos para interfaces externas relevantes
- `riesgos`

## Criterios de cierre
- stakeholders principales identificados
- necesidades y restricciones sin contradicciones críticas
- criterios de aceptación de alto nivel suficientemente claros
- si la madurez es `formal`, existe material suficiente para abrir `F2`

## Guía para el subagente de fase
Distingue siempre si estás en `F1 preliminar` o `F1 formal`. En preliminar, ayuda a cotizar. En formal, ayuda a preparar una transición sólida hacia requerimientos de sistema.
