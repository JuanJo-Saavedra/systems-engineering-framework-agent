---
phase_id: F5
phase_name: Integración y modelo de ingeniería
question: "¿El sistema integrado funciona de manera coherente con el diseño?"
lifecycle_scope: proyecto_formal
allowed_maturity:
  - formal
default_maturity: formal
review: SIR / EMR
baseline: Product Baseline en ejecución controlada
next_gate: F6
transversal_processes:
  - configuracion
  - riesgos
  - interfaces
  - datos_y_documentacion
  - vv
---

# Fase 5 - Integración y modelo de ingeniería

## Objetivo operativo
Construir e integrar un modelo representativo del sistema para reducir riesgo de integración antes de la verificación formal.

## Entradas mínimas
- Product Baseline liberada
- partes fabricadas o compradas
- documentación liberada
- procedimientos de integración
- releases SW/FW

## Actividades guía
- adquirir o fabricar partes
- ensamblar subconjuntos
- integrar CIs
- realizar bring-up HW/SW/FW
- ejecutar ensayos funcionales preliminares
- resolver incompatibilidades
- registrar anomalías
- controlar configuración del EM

## Salidas esperadas
- EM integrado
- conocimiento del comportamiento real del sistema
- anomalías identificadas
- readiness para verificación formal

## Artefactos obligatorios
- engineering model
- logs de integración
- reportes de integración
- lista de NCRs o anomalías
- configuración exacta del EM
- actualización de riesgos
- evidencia funcional preliminar

## Review y baseline
- Review asociada: `SIR / EMR`
- Baseline asociada: `Product Baseline en ejecución controlada`

## Registros transversales a tocar
- `configuracion`
- `riesgos`
- `interfaces`
- `vv`

## Criterios de cierre
- integración básica lograda
- funcionamiento del sistema comprobado
- configuración exacta conocida
- readiness técnica para ensayos formales

## Guía para el subagente de fase
No pierdas el registro de configuración real integrada. Si el sistema funciona pero no sabes exactamente qué se ensayó, la fase no está cerrada.
