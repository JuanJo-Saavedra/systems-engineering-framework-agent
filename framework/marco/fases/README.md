# Contratos operativos de fase

Cada archivo de esta carpeta describe una fase formal del ciclo de vida como contrato operativo para humanos y agentes.

## Qué contiene cada fase
- metadatos mínimos legibles por scripts,
- objetivo y pregunta dominante,
- entradas y salidas,
- artefactos obligatorios,
- review y baseline asociadas,
- relación con procesos transversales,
- criterio de cierre,
- guía de actuación para el subagente de fase.

## Regla especial de la plantilla
- `F0` opera en presupuesto.
- `F1` admite dos madureces:
  - `preliminar` para presupuesto,
  - `formal` para proyecto aprobado.
- `F2-F8` solo operan en proyecto formal.
