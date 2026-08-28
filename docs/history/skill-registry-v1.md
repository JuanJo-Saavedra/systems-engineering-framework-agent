# Skill Registry del proyecto

## Proposito
Este archivo funciona como catalogo de capacidades del marco. No define el estado de un proyecto puntual; define que tipo de asistencia puede dar el sistema, en que momento conviene usarla y que entradas debe consultar antes de actuar.

## Como usar este registro
- El orquestador debe leer este archivo al inicio de cada sesion relevante.
- Antes de delegar, debe elegir una capacidad segun:
  - estado global del proyecto,
  - fase activa,
  - madurez esperada,
  - tipo de tarea.
- Si una capacidad depende de registros transversales, debe consultarlos antes de producir una salida.
- Cuando aparezcan nuevas guias, plantillas, automatizaciones o convenciones, este registro debe actualizarse.

## Reglas de seleccion
- Si el trabajo esta en `preproyecto_presupuesto`, priorizar capacidades de `F0`, `F1 preliminar`, riesgos iniciales y handoff.
- Si el trabajo esta en `aprobado_en_transicion`, priorizar consolidacion del hito de aprobacion y cierre de vacios de `F1 formal`.
- Si el trabajo esta en `proyecto_formal`, priorizar capacidades de la fase activa y de los procesos transversales afectados.
- Si la tarea es producir o revisar un artefacto puntual, usar primero una capacidad de tarea puntual y luego validar consistencia con una capacidad transversal.

## Capacidades del orquestador

### `orquestacion_del_proyecto`
- Tipo: orquestacion general
- Cuando usarla: siempre que se necesite decidir siguiente paso, fase activa, madurez esperada o reglas de avance.
- Fuente principal:
  - `AGENTS.md`
  - `proyecto/estado/proyecto_actual.md`
  - `proyecto/estado/estado_fases.md`
  - `proyecto/hitos/hito_aprobacion_trabajo.md`
- Salidas esperadas:
  - estado interpretado del proyecto,
  - fase activa confirmada,
  - siguiente decision o entregable critico,
  - subagente recomendado.

### `gap_analysis_de_fase`
- Tipo: control de avance
- Cuando usarla: antes de cerrar una fase, antes de una review o cuando el equipo no sabe que falta.
- Fuente principal:
  - contrato de fase en `marco/fases/`
  - estado de fase
  - registros transversales relevantes
- Salidas esperadas:
  - faltantes,
  - bloqueos,
  - riesgos de pasar de fase prematuramente.

## Capacidades por fase

### `f0_factibilidad`
- Tipo: fase
- Fase objetivo: `F0`
- Madurez: `preliminar`
- Cuando usarla: para transformar una necesidad en problema, contexto, ROM, riesgos y recomendacion Go/No-Go.
- Fuente principal:
  - `marco/fases/fase_0_concepto_y_factibilidad.md`
  - `proyecto/registros/riesgos.md`
  - `proyecto/registros/decisiones_tecnicas.md`
- Salidas esperadas:
  - problema formulado,
  - CONOPS preliminar,
  - estimacion ROM,
  - recomendacion de continuidad.

### `f1_stakeholders_preliminar`
- Tipo: fase
- Fase objetivo: `F1`
- Madurez: `preliminar`
- Cuando usarla: durante presupuesto, para capturar necesidades y restricciones a alto nivel sin forzar detalle tecnico.
- Fuente principal:
  - `marco/fases/fase_1_requerimientos_stakeholders.md`
  - `proyecto/registros/requisitos.md`
  - `proyecto/registros/riesgos.md`
  - `proyecto/registros/interfaces.md`
- Salidas esperadas:
  - necesidades preliminares,
  - escenarios de uso,
  - restricciones externas,
  - base para cotizacion.

### `handoff_presupuesto_a_proyecto`
- Tipo: transicion
- Fase objetivo: `F1`
- Madurez: `formal`
- Cuando usarla: inmediatamente despues de la aprobacion del trabajo.
- Fuente principal:
  - `proyecto/hitos/hito_aprobacion_trabajo.md`
  - `proyecto/estado/proyecto_actual.md`
  - salidas heredadas de `F0` y `F1 preliminar`
- Salidas esperadas:
  - hito de aprobacion consolidado,
  - lista de insumos heredados,
  - lista de vacios a cerrar antes de `F2`.

### `f1_stakeholders_formal`
- Tipo: fase
- Fase objetivo: `F1`
- Madurez: `formal`
- Cuando usarla: luego de la aprobacion, para completar necesidades, restricciones y criterios de aceptacion de alto nivel.
- Fuente principal:
  - `marco/fases/fase_1_requerimientos_stakeholders.md`
  - `proyecto/hitos/hito_aprobacion_trabajo.md`
  - `proyecto/registros/requisitos.md`
  - `proyecto/registros/interfaces.md`
  - `proyecto/registros/riesgos.md`
- Salidas esperadas:
  - stakeholder requirements formalizados,
  - contradicciones resueltas,
  - base apta para abrir `F2`.

### `f2_requisitos_sistema`
- Tipo: fase
- Fase objetivo: `F2`
- Madurez: `formal`
- Cuando usarla: para derivar requerimientos tecnicos verificables y trazables.
- Fuente principal:
  - `marco/fases/fase_2_requerimientos_sistema.md`
  - `proyecto/registros/requisitos.md`
  - `proyecto/registros/vv.md`
  - `proyecto/registros/configuracion.md`
- Salidas esperadas:
  - SyRS,
  - trazabilidad necesidad <-> requisito,
  - metodo de verificacion por requisito.

### `f3_arquitectura`
- Tipo: fase
- Fase objetivo: `F3`
- Madurez: `formal`
- Cuando usarla: para seleccionar arquitectura, asignar requisitos e identificar interfaces.
- Fuente principal:
  - `marco/fases/fase_3_definicion_arquitectura.md`
  - `proyecto/registros/requisitos.md`
  - `proyecto/registros/interfaces.md`
  - `proyecto/registros/decisiones_tecnicas.md`
- Salidas esperadas:
  - arquitectura seleccionada,
  - CIs identificados,
  - trade-offs documentados,
  - base para `PDR`.

### `f4_diseno_detallado`
- Tipo: fase
- Fase objetivo: `F4`
- Madurez: `formal`
- Cuando usarla: para preparar documentacion build-to, code-to e integrate-to.
- Fuente principal:
  - `marco/fases/fase_4_diseno_detallado.md`
  - `proyecto/registros/configuracion.md`
  - `proyecto/registros/interfaces.md`
  - `proyecto/registros/vv.md`
- Salidas esperadas:
  - diseno liberable,
  - PBS final,
  - base para `CDR`.

### `f5_integracion`
- Tipo: fase
- Fase objetivo: `F5`
- Madurez: `formal`
- Cuando usarla: para registrar configuracion integrada, anomalias y readiness de verificacion.
- Fuente principal:
  - `marco/fases/fase_5_integracion_y_modelo_de_ingenieria.md`
  - `proyecto/registros/configuracion.md`
  - `proyecto/registros/riesgos.md`
  - `proyecto/registros/interfaces.md`
- Salidas esperadas:
  - configuracion del EM,
  - anomalias y NCRs,
  - readiness para `F6`.

### `f6_verificacion`
- Tipo: fase
- Fase objetivo: `F6`
- Madurez: `formal`
- Cuando usarla: para organizar evidencia objetiva y estado de cumplimiento.
- Fuente principal:
  - `marco/fases/fase_6_verificacion.md`
  - `proyecto/registros/vv.md`
  - `proyecto/registros/requisitos.md`
  - `proyecto/registros/configuracion.md`
- Salidas esperadas:
  - matriz requisito <-> evidencia,
  - estado de NCRs,
  - readiness para validacion.

### `f7_validacion`
- Tipo: fase
- Fase objetivo: `F7`
- Madurez: `formal`
- Cuando usarla: para confirmar adecuacion al uso y aceptacion.
- Fuente principal:
  - `marco/fases/fase_7_validacion.md`
  - `proyecto/registros/vv.md`
  - `proyecto/registros/riesgos.md`
  - `proyecto/registros/decisiones_tecnicas.md`
- Salidas esperadas:
  - escenarios validados,
  - hallazgos operativos,
  - aceptacion o desvio residual.

### `f8_transferencia`
- Tipo: fase
- Fase objetivo: `F8`
- Madurez: `formal`
- Cuando usarla: para consolidar baseline final, soporte inicial y cierre tecnico.
- Fuente principal:
  - `marco/fases/fase_8_produccion_transferencia_soporte.md`
  - `proyecto/registros/configuracion.md`
  - `proyecto/registros/lecciones_aprendidas.md`
  - `proyecto/registros/decisiones_tecnicas.md`
- Salidas esperadas:
  - baseline final,
  - paquete de transferencia,
  - cierre tecnico.

## Capacidades transversales

### `trazabilidad`
- Tipo: transversal
- Cuando usarla: cuando se deba conectar necesidad, requisito, CI, metodo de verificacion y evidencia.
- Fuente principal:
  - `proyecto/registros/requisitos.md`
  - `proyecto/registros/vv.md`
- Salidas esperadas:
  - matriz o enlaces de trazabilidad completos,
  - huecos detectados.

### `riesgos_y_oportunidades`
- Tipo: transversal
- Cuando usarla: cuando aparezcan supuestos sensibles, decisiones de alto impacto o bloqueos de fase.
- Fuente principal:
  - `proyecto/registros/riesgos.md`
  - review o fase activa
- Salidas esperadas:
  - riesgo registrado,
  - criticidad,
  - accion y responsable.

### `configuracion_y_baselines`
- Tipo: transversal
- Cuando usarla: ante cambios de versiones, cortes de baseline o preparacion de release/review.
- Fuente principal:
  - `proyecto/registros/configuracion.md`
  - `marco/baselines/catalogo_baselines.md`
- Salidas esperadas:
  - items identificados,
  - versionado claro,
  - baseline asociada.

### `interfaces`
- Tipo: transversal
- Cuando usarla: al aparecer nuevas interfaces o cambios entre disciplinas.
- Fuente principal:
  - `proyecto/registros/interfaces.md`
  - artefactos de arquitectura o diseno
- Salidas esperadas:
  - interfaz definida,
  - responsable,
  - impacto de cambio.

### `verificacion_y_validacion`
- Tipo: transversal
- Cuando usarla: para evitar mezcla entre verificacion y validacion o para planificar cierres.
- Fuente principal:
  - `proyecto/registros/vv.md`
  - fase activa
- Salidas esperadas:
  - estrategia de cierre clara,
  - evidencia esperada,
  - estado de cumplimiento.

### `decisiones_tecnicas`
- Tipo: transversal
- Cuando usarla: cuando haya trade-offs, selecciones tecnologicas, make/buy/reuse o aceptacion de desvios.
- Fuente principal:
  - `proyecto/registros/decisiones_tecnicas.md`
- Salidas esperadas:
  - decision explicitada,
  - alternativas evaluadas,
  - criterio usado,
  - impacto tecnico y programatico.

## Capacidades de tarea puntual

### `redaccion_de_artefacto`
- Tipo: tarea puntual
- Cuando usarla: para redactar o reestructurar un documento concreto de fase.
- Fuente principal:
  - contrato de fase aplicable,
  - registros transversales relevantes
- Salidas esperadas:
  - artefacto redactado de forma consistente con el marco.

### `preparacion_de_review`
- Tipo: tarea puntual
- Cuando usarla: antes de MCR, SRR, PDR, CDR, SIR/EMR, TRR, SAR o review de transferencia.
- Fuente principal:
  - `marco/reviews/catalogo_reviews.md`
  - fase activa
  - registros y artefactos relevantes
- Salidas esperadas:
  - paquete de review,
  - entry criteria evaluado,
  - lista de faltantes y observaciones.

## Mantenimiento del registro
- Actualizar este archivo si se crean nuevas guias o automatizaciones.
- Si el marco cambia de estructura, revisar rutas y fuentes principales.
- Si una capacidad se vuelve demasiado grande, dividirla en dos: una de produccion y otra de control.
