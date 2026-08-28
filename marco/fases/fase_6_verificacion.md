---
phase_id: F6
phase_name: Verificación
question: "¿Cumple con las especificaciones?"
lifecycle_scope: proyecto_formal
allowed_maturity:
  - formal
default_maturity: formal
review: TRR y Verification Review / TRB
baseline: Release candidate bajo configuración controlada
next_gate: F7
transversal_processes:
  - vv
  - configuracion
  - riesgos
  - datos_y_documentacion
  - requisitos
---

# Fase 6 - Verificación

## Objetivo operativo
Demostrar con evidencia objetiva que el producto cumple los requerimientos especificados.

## Entradas mínimas
- engineering model integrado
- test plan
- test procedures
- baseline liberada
- instrumentación y bancos disponibles

## Actividades guía
- realizar TRR
- ejecutar ensayos planificados
- registrar evidencia objetiva
- consolidar resultados por requerimiento
- cerrar NCRs
- actualizar matriz de verificación
- preparar release candidate

## Salidas esperadas
- cumplimiento técnico demostrado
- evidencia organizada por requerimiento
- estado claro de NCRs
- readiness para validación

## Artefactos obligatorios
- test plan aprobado
- test procedures
- test readiness package
- internal test report o verification report
- matriz requisito <-> evidencia
- registro de NCRs
- release candidate

## Review y baseline
- Review asociada: `TRR y Verification Review / TRB`
- Baseline asociada: `Release candidate bajo configuración controlada`

## Registros transversales a tocar
- `vv`
- `configuracion`
- `riesgos`
- `requisitos`

## Criterios de cierre
- ensayos completados
- evidencia trazable a requerimientos
- NCRs críticas cerradas
- estado de cumplimiento técnico consolidado

## Guía para el subagente de fase
Tu foco es trazabilidad completa entre requisito, método, resultado y evidencia. Evita toda ambigüedad sobre la configuración ensayada.
