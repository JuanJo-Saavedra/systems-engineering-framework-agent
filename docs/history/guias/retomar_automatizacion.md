# Instructivo base para retomar automatización futura

## Objetivo
Dejar una guía simple para diseñar más adelante las plantillas documentales y los scripts de exportación, sin implementarlos todavía.

## Qué deberá existir más adelante
- Plantillas documentales corporativas por tipo de artefacto.
- Scripts de consolidación de contexto por fase o por review.
- Scripts de exportación desde la fuente del proyecto hacia documentos de salida.
- Validaciones mínimas de consistencia antes de exportar.

## Fuente que deberían leer los scripts
- Estado general del proyecto.
- Estado por fase.
- Hito de aprobación del trabajo.
- Contratos operativos de fase.
- Registros transversales.
- Artefactos específicos instanciados dentro del proyecto.

## Salidas que se espera poder generar
- Documentos de presupuesto.
- Paquetes de review.
- Documentos de requerimientos.
- Paquetes de arquitectura.
- Paquetes de integración, verificación y validación.
- Entregables de transferencia y cierre técnico.

## Prompt base para retomar este punto
Actúa como arquitecto de automatización documental para esta plantilla de ingeniería. Diseña primero el contrato entre fuente y salida antes de proponer scripts. Usa como fuente canónica los Markdown estructurados del repo y define:
- qué archivos deben leerse,
- qué campos mínimos son obligatorios,
- qué validaciones previas deben correrse,
- qué documento corporativo debe generarse,
- cómo separar fuente editable de salida derivada.

No implementes todavía lógica compleja si el contrato de datos aún no está claro.
