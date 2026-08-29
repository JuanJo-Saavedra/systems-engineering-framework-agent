---
document_type: guia
language: es
version: 1.0
status: canonico
---

# Project Init del marco de ingeniería

## Propósito

Este instructivo sirve para arrancar un proyecto nuevo usando la plantilla de forma consistente. No automatiza todavía el proceso; define la secuencia mínima para que el repositorio quede bien ubicado desde el primer día.

## Cuándo usarlo

- al iniciar un proyecto nuevo,
- al reutilizar la plantilla para otra oportunidad,
- cuando un proyecto existente se migra a este marco,
- cuando el equipo necesita reordenar un proyecto que empezó fuera del sistema.

## Resultado esperado

Al finalizar esta guía debería quedar claro:

- en qué estado global está el trabajo,
- qué fase está activa,
- qué madurez corresponde,
- qué registros transversales deben abrirse primero,
- qué faltaría para avanzar de fase sin romper el marco.

## Paso 1. Confirmar el tipo de arranque

Antes de tocar archivos, identificar cuál de estos escenarios aplica:

### Escenario A. Oportunidad nueva o pedido de presupuesto

Usar cuando:

- todavía no hay aprobación del trabajo,
- se necesita evaluar factibilidad y cotizar.

Estado inicial recomendado:

- `project_status: preproyecto_presupuesto`
- `active_phase: F0`
- `active_maturity: preliminar`
- `approval_handoff_status: pendiente`

### Escenario B. Trabajo ya aprobado que entra directamente al marco

Usar cuando:

- el trabajo ya fue vendido o aprobado,
- existe información previa fuera del repositorio.

Estado inicial recomendado:

- `project_status: aprobado_en_transicion`
- `active_phase: F1`
- `active_maturity: formal`
- `approval_handoff_status: aprobado`

### Escenario C. Proyecto formal ya en marcha y se migra al marco

Usar cuando:

- ya existen artefactos técnicos,
- se necesita ordenar trazabilidad y estado.

Estado inicial recomendado:

- elegir la fase real más madura disponible,
- cargar el estado con criterio conservador,
- abrir un gap analysis antes de avanzar.

## Paso 2. Completar el estado base del proyecto

Revisar y actualizar:

- `proyecto/estado/proyecto_actual.md`
- `proyecto/estado/estado_fases.md`

Checklist mínimo:

- definir estado global,
- definir fase activa,
- definir madurez esperada,
- marcar qué fases están en progreso, cerradas o no iniciadas,
- dejar un próximo paso esperado.

## Paso 3. Evaluar si corresponde abrir el hito de aprobación

### Si el proyecto está en presupuesto

- dejar `proyecto/hitos/hito_aprobacion_trabajo.md` en `pendiente`,
- no completar información ficticia de aprobación.

### Si el trabajo ya fue aprobado

- completar el hito de aprobación con:
  - decisión,
  - fecha,
  - alcance aprobado,
  - restricciones contractuales,
  - insumos heredados desde presupuesto,
  - vacíos a cerrar antes de `F2`.

Regla:

- si el hito de aprobación no está completo, no considerar que la transición está cerrada.

## Paso 4. Abrir los registros transversales mínimos

No hace falta llenarlos por completo el primer día, pero sí dejar claro cuáles ya tienen información y cuáles están vacíos.

Revisar:

- `proyecto/registros/requisitos.md`
- `proyecto/registros/riesgos.md`
- `proyecto/registros/configuracion.md`
- `proyecto/registros/interfaces.md`
- `proyecto/registros/vv.md`
- `proyecto/registros/decisiones_tecnicas.md`
- `proyecto/registros/lecciones_aprendidas.md`

Prioridad recomendada por escenario:

### Si arranca en presupuesto

- requisitos,
- riesgos,
- decisiones técnicas,
- interfaces externas preliminares.

### Si arranca aprobado o migrado

- requisitos,
- riesgos,
- configuración,
- interfaces,
- V&V.

## Paso 5. Elegir la capacidad correcta

Para diseñar y seleccionar la capacidad se usa [skill-architecture.md](skill-architecture.md), la arquitectura de capacidades del framework. Es base de diseño y **no** se instala en el proyecto destino; en runtime, la skill disponible se resuelve desde el registry operativo instalado (`catalogo/skill-registry.md`).

Regla práctica:

- si hay que entender el siguiente paso general, usar `orquestacion_del_proyecto`,
- si hay que madurar la fase actual, usar la capacidad de fase correspondiente,
- si hay que chequear consistencia, usar una capacidad transversal,
- si hay que preparar un documento o review, usar una capacidad de tarea puntual.

## Paso 6. Validar que el proyecto no salte gates

Antes de declarar que el proyecto está listo para avanzar, validar:

### De F0 a F1 preliminar

- hay problema entendido,
- hay riesgos iniciales,
- hay recomendación de continuidad para cotizar.

### De F1 preliminar a aprobado_en_transicion

- existe aprobación real del trabajo,
- existe hito formal de aprobación.

### De F1 formal a F2

- stakeholders críticos identificados,
- restricciones externas consolidadas,
- escenarios de uso relevantes,
- criterios de aceptación de alto nivel claros.

## Paso 7. Dejar una primera traza de trabajo

Aunque el proyecto recién arranque, dejar evidencia mínima de que se inicializó correctamente.

Recomendación:

- actualizar estado general,
- actualizar estado de fases,
- registrar al menos un riesgo o supuesto,
- registrar al menos una necesidad o requisito preliminar,
- si aplica, completar o abrir el hito de aprobación.

## Preguntas que el orquestador debería responder al final

- ¿En qué estado está el trabajo hoy?
- ¿Qué fase está realmente activa?
- ¿La madurez esperada es preliminar o formal?
- ¿Qué registro transversal necesita atención inmediata?
- ¿Qué entregable o decisión debería producirse a continuación?

## Anti-patrones a evitar

- abrir `F2` solo porque el cliente aprobó comercialmente,
- cargar aprobaciones ficticias para que el flujo "avance",
- separar presupuesto y proyecto en registros paralelos que rompan continuidad,
- usar `F1 preliminar` como si ya fuera un set completo de requerimientos formales,
- dejar riesgos y decisiones solo en minutas externas al repositorio.

## Recomendación de uso en capacitación

Para entrenar al equipo:

1. tomar una oportunidad ficticia,
2. correr este instructivo manualmente,
3. simular la aprobación,
4. completar el handoff,
5. verificar por qué todavía no se puede abrir `F2` si `F1 formal` queda incompleta.
