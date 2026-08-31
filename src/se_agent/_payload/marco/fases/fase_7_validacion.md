---
phase_id: F7
phase_name: Validación
question: "¿Cumple su propósito en el entorno real o representativo?"
lifecycle_scope: proyecto_formal
allowed_maturity:
  - formal
default_maturity: formal
review: Validation Review / SAR
baseline: Configuración validada
next_gate: F8
transversal_processes:
  - vv
  - configuracion
  - riesgos
  - datos_y_documentacion
  - decisiones_tecnicas
---

# Fase 7 - Validación

## Objetivo operativo
Demostrar que el producto satisface la necesidad operativa y el propósito para el cual fue desarrollado.

## Entradas mínimas
- sistema verificado
- plan de validación
- criterios de aceptación del cliente
- entorno operativo o representativo

## Actividades guía
- ejecutar ensayos externos o de campo
- validar comportamiento en contexto de uso
- relevar feedback de usuario o cliente
- evaluar adecuación operacional
- consolidar hallazgos
- formalizar aceptación o desvíos residuales

## Salidas esperadas
- adecuación al uso demostrada o discutida
- aceptación del cliente o usuario
- lista de acciones residuales
- autorización para liberar, producir o transferir

## Artefactos obligatorios
- validation plan
- procedimientos de validación
- validation report
- actas de aceptación
- registro de hallazgos operativos
- lista de acciones post-validación

## Review y baseline
- Review asociada: `Validation Review / SAR`
- Baseline asociada: `Configuración validada`

## Registros transversales a tocar
- `vv`
- `configuracion`
- `riesgos`
- `decisiones_tecnicas`

## Criterios de cierre
- propósito del sistema evaluado
- resultado de aceptación o rechazo documentado
- desvíos residuales explícitos y tratados
- decisión de liberación o re-trabajo tomada

## Guía para el subagente de fase
No confundas validación con verificación. Aquí importa adecuación al uso y aceptación, no solo conformidad técnica.
