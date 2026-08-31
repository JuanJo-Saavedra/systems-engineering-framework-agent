---
phase_id: F4
phase_name: Diseño detallado y preparación de implementación
question: "¿Cómo queda completamente definido para construirlo?"
lifecycle_scope: proyecto_formal
allowed_maturity:
  - formal
default_maturity: formal
review: CDR
baseline: Product Baseline
next_gate: F5
transversal_processes:
  - configuracion
  - interfaces
  - requisitos
  - vv
  - decisiones_tecnicas
---

# Fase 4 - Diseño detallado y preparación de implementación

## Objetivo operativo
Completar la definición técnica build-to, code-to e integrate-to del producto.

## Entradas mínimas
- arquitectura aprobada
- Allocated Baseline disponible
- decisiones make/buy/reuse identificadas
- tecnologías seleccionadas

## Actividades guía
- diseñar HW, SW/FW y mecánica en detalle
- cerrar interfaces
- definir PBS final
- preparar integración
- completar V&V
- liberar documentación técnica

## Salidas esperadas
- definición final del producto
- documentación suficiente para construir, integrar y ensayar
- preparación de implementación física

## Artefactos obligatorios
- diseño detallado liberable
- PBS final
- ICDs finales
- BOM
- esquemas y planos
- baseline de SW/FW
- plan de integración
- V&V plan completo
- RTM/VCRM actualizada
- plan de configuración
- procedimientos preliminares de ensayo

## Review y baseline
- Review asociada: `CDR`
- Baseline asociada: `Product Baseline`

## Registros transversales a tocar
- `configuracion`
- `interfaces`
- `requisitos`
- `vv`
- `decisiones_tecnicas`

## Criterios de cierre
- diseño completo y consistente
- interfaces críticas cerradas
- PBS final definida
- documentación liberable bajo configuración
- preparación lista para implementación

## Guía para el subagente de fase
Tu foco es que la definición sea construible y auditable, no solo conceptualmente correcta.
