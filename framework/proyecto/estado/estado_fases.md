# Estado por fase

## Convenciones

- `no_iniciada`
- `en_progreso`
- `cerrada`
- `bloqueada`
- `no_aplica`

## Tabla base

| Fase          | Nombre                                             | Estado      | Madurez esperada | Review asociada                        | Observaciones                                                                                 |
| ------------- | -------------------------------------------------- | ----------- | ---------------- | -------------------------------------- | --------------------------------------------------------------------------------------------- |
| F0            | Concepto y factibilidad                            | en_progreso | preliminar       | MCR                                    | Base para presupuesto                                                                         |
| F1 preliminar | Requerimientos de stakeholders (presupuesto)       | no_iniciada | preliminar       | Stakeholder Requirements Review        | Se cierra por su propia capacidad de fase más la aprobación humana; el handoff no la cierra |
| F1 formal     | Requerimientos de stakeholders (proyecto aprobado) | no_iniciada | formal           | Stakeholder Requirements Review        | Se abre después del handoff;`F2` no se abre hasta cerrarla                                 |
| F2            | Requerimientos de sistema                          | no_iniciada | formal           | SRR                                    | No abrir hasta cerrar F1 formal                                                               |
| F3            | Definición de arquitectura                        | no_iniciada | formal           | PDR                                    |                                                                                               |
| F4            | Diseño detallado                                  | no_iniciada | formal           | CDR                                    |                                                                                               |
| F5            | Integración y modelo de ingeniería               | no_iniciada | formal           | SIR / EMR                              |                                                                                               |
| F6            | Verificación                                      | no_iniciada | formal           | TRR / Verification Review              |                                                                                               |
| F7            | Validación                                        | no_iniciada | formal           | Validation Review / SAR                |                                                                                               |
| F8            | Producción / transferencia / soporte inicial      | no_iniciada | formal           | Production Readiness / Transfer Review |                                                                                               |

## Regla clave

Cuando el trabajo sea aprobado:

1. `F1 preliminar` ya debe estar `cerrada`: la cierra su propia capacidad de fase de `F1` (preliminar) más la aprobación humana.
2. `F1 formal` permanece `no_iniciada` (la activa su primer trabajo formal).
3. no habilites `F2` hasta cerrar `F1 formal` junto con los vacíos heredados del presupuesto.
