---
document_type: quickstart
language: es
version: 0.2
status: propuesta
---

# Quickstart del orquestador de agentes

## Propósito y estado

Este documento describe el **MVP objetivo** de un orquestador Codex-first y harness-neutral. **No describe funcionalidad ya implementada**: hoy el repo contiene el marco de ingeniería y su catálogo de capacidades, no un orquestador ejecutable.

El orquestador de runtime siempre **opera un proyecto de ingeniería**; no elige entre "desarrollar" y "operar". El desarrollo del arnés es externo a la plantilla de runtime y se describe como estructura de implementación futura en `implementacion/` (arquitectura, adaptadores, tests), fuera del flujo de operación. Ver [reestructuracion-agents.md](reestructuracion-agents.md).

## Flujo mínimo recomendado

1. **Leer el estado autoritativo**: `proyecto/estado/proyecto_actual.md`, `proyecto/estado/estado_fases.md`, `proyecto/hitos/hito_aprobacion_trabajo.md` y los registros transversales relevantes.
2. **Seleccionar capacidad** desde [skill-registry.md](skill-registry.md).
3. **Cargar la skill** correspondiente a la capacidad elegida.
4. **Decidir inline vs subagente** según la regla de asignación (ver [arquitectura-orquestador.md](arquitectura-orquestador.md)).
5. **Actuar** produciendo la salida esperada de la capacidad.
6. **Actualizar los registros autoritativos** (Markdown) antes de dar por cerrada la tarea.
7. **Opcional**: guardar memoria semántica en Engram (resúmenes, descubrimientos, punteros). Ver [memoria-dual.md](memoria-dual.md).

## Tres rutas

| Ruta | Cuándo usarla | Capacidad de entrada |
| --- | --- | --- |
| Coordinación general | Decidir siguiente paso, fase activa, madurez o regla de avance | `orquestacion_del_proyecto` |
| Trabajo directo de fase | Madurar una fase concreta | `f0_factibilidad` … `f8_transferencia` |
| Soporte especializado | Consistencia transversal o artefacto puntual | capacidades transversales o de tarea puntual |

## Tabla de decisión

| Señal | Ruta | Primera acción |
| --- | --- | --- |
| "¿En qué estado está el trabajo?" | Coordinación general | Leer estado y confirmar fase activa |
| "Necesito madurar F3" | Trabajo directo de fase | Cargar contrato de fase y skill de fase |
| "¿Qué falta para cerrar F2?" | Soporte especializado | `gap_analysis_de_fase` |
| "Preparar review PDR" | Soporte especializado | `preparacion_de_review` |
| "¿Qué subagente conviene?" | Coordinación general | Consultar `skill-registry.md` |

## Entradas y salidas esperadas

| Paso | Entradas esperadas | Salidas esperadas |
| --- | --- | --- |
| Estado | `proyecto_actual.md`, `estado_fases.md`, hito de aprobación | Estado interpretado, fase confirmada, siguiente decisión |
| Fase | Contrato de fase + registros transversales | Artefacto de fase consistente |
| Transversal | Registros transversales relevantes | Registro/matriz actualizado o hueco detectado |
| Tarea puntual | Contrato + registros | Entregable puntual |

## Comportamiento degradado

| Fallo | Comportamiento esperado |
| --- | --- |
| Engram no disponible | Seguir solo con Markdown autoritativo; no detener la operación |
| RAG no disponible | Lectura directa de archivos Markdown |
| Documento autoritativo ausente o corrupto | **Fallar cerrado** y solicitar restauración |
| Engram y RAG caídos | Operar si Markdown está sano; la auditoría no depende de memoria |

La política completa está en [memoria-dual.md](memoria-dual.md).

## No-objetivos del MVP

- No implementa todavía plantillas ni scripts de exportación (ver [retomar_automatizacion.md](retomar_automatizacion.md)).
- No define modelos concretos ni credenciales.
- No reemplaza `guias/skill-registry.md` como catálogo canónico.
- No declara subagente a toda capacidad transversal.

## Relacionado

- [arquitectura-orquestador.md](arquitectura-orquestador.md) — capas y contratos.
- [frontera-dominio-harness.md](frontera-dominio-harness.md) — autoridad y dependencias.
- [memoria-dual.md](memoria-dual.md) — Markdown + Engram + RAG.
- [reestructuracion-agents.md](reestructuracion-agents.md) — decisión canónica: contrato único de `AGENTS.md`.
- [skill-registry.md](skill-registry.md) — catálogo canónico.
