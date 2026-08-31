---
phase_id: F2
phase_name: Requerimientos de sistema
question: "¿Qué debe hacer técnicamente el sistema?"
lifecycle_scope: proyecto_formal
allowed_maturity:
  - formal
default_maturity: formal
review: SRR
baseline: Functional Baseline
next_gate: F3
transversal_processes:
  - requisitos
  - vv
  - configuracion
  - riesgos
---

# Fase 2 - Requerimientos de sistema

## Objetivo operativo
Traducir necesidades de stakeholders en requerimientos técnicos verificables y trazables.

## Rol en la plantilla
Es la primera fase técnica del proyecto formal. No debe abrirse hasta haber completado `F1 formal`.

## Entradas mínimas
- `F1 formal` cerrada
- stakeholder requirements
- restricciones externas consolidadas
- normativa aplicable
- supuestos y decisiones de arranque ya explicitados

## Actividades guía
- derivar requerimientos técnicos
- clasificar requerimientos
- revisar consistencia y completitud
- analizar verificabilidad
- identificar interfaces externas preliminares
- definir método de verificación por requerimiento
- construir trazabilidad

## Salidas esperadas
- requerimientos técnicos claros y verificables
- métodos de verificación preliminares definidos
- trazabilidad desde necesidad a requisito
- baseline funcional preparada

## Artefactos obligatorios
- SyRS
- matriz necesidad <-> requisito
- matriz requisito <-> método de verificación
- registro de supuestos y restricciones
- V&V plan preliminar

## Review y baseline
- Review asociada: `SRR`
- Baseline asociada: `Functional Baseline`

## Registros transversales a tocar
- `requisitos`
- `vv`
- `configuracion`
- `riesgos`

## Criterios de cierre
- 100% de requerimientos trazados a necesidades
- métodos de verificación definidos
- ambigüedades críticas resueltas
- Functional Baseline liberable

## Guía para el subagente de fase
No mezcles requerimiento con solución. Tu foco es claridad técnica, verificabilidad y trazabilidad.
