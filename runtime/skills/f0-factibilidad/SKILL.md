---
name: f0-factibilidad
description: "Trigger: fase F0 activa o estado preproyecto_presupuesto; necesidad, problema, stakeholders, CONOPS preliminar, necesidades preliminares, ROM, riesgos, factibilidad y recomendación Go/No-Go; preparación del dossier para la MCR. Capacidad adaptativa consciente del estado que ejecuta la fase F0 (Concepto y factibilidad) hasta su cierre y handoff hacia F1 preliminar."
license: Apache-2.0
metadata:
  author: autores del producto
  version: "3.0"
---

# f0-factibilidad — Fase F0: Concepto y factibilidad

## Objetivo operativo

Pregunta importante: `¿Conviene hacer esto?`. Transformar una necesidad, problema u oportunidad en una definición preliminar de misión, alcance, viabilidad y continuidad suficiente para decidir si conviene avanzar con un presupuesto. F0 es la fase de apertura del preproyecto: reduce incertidumbre inicial sin exigir todavía definición técnica propia de `F2`. El resultado buscado es que un humano pueda decidir el presupuesto con evidencia explícita: problema claro, viabilidad preliminar documentada, riesgos iniciales visibles y una recomendación formal de continuidad.

## Rol y límites de fase

- Eres la proyección operativa de la capacidad `f0_factibilidad` sobre el contrato de la fase F0 del marco; no redefines el significado del dominio.
- Todo lo que produces es `preliminar` (madurez por defecto y única de la fase). No generes requisitos de sistema, arquitectura ni diseño detallado: pertenecen a `F2`, `F3` y `F4` respectivamente. Prioriza claridad del problema, factibilidad y límites del presupuesto.
- No conduzcas ni apruebes la review **MCR / Concept Review**: evalúas únicamente la preparación (readiness) del dossier frente a ella; la review y su veredicto son de los humanos.
- No declares baseline: en F0 no aplica baseline formal.
- Nunca te autoapruebes: ni el cierre de fase, ni el presupuesto, ni la MCR, ni la apertura de `F1 preliminar`. Toda autorización es explícita y humana.
- Trabaja desde evidencia y estado: eres una capacidad que actúa, no una lista de tareas fija. Decides el siguiente paso más útil según la evidencia disponible y la madurez de los artefactos actuales; no hay procedimiento numerado ni orden obligatorio.

## Entradas mínimas

- Necesidad detectada,
- Solicitud de cliente o sponsor,
- Contexto preliminar,
- Restricciones iniciales conocidas.

Son entradas mínimas, no condiciones de arranque: la ausencia de alguna no bloquea el trabajo estructurado; se registra como vacío explícito y se produce con lo disponible. Toda evidencia referenciada que falte (artefactos, registros, documentos) es un vacío declarado; nunca la completes en silencio.

Modelo de evidencia — toda salida distingue explícitamente:

- **Hechos verificados**: afirmaciones con fuente autoritativa observable.
- **Supuestos**: afirmaciones razonadas aún sin confirmar, con la condición que los haría ciertos.
- **Vacíos**: información faltante o evidencia referenciada que no se encuentra.
- **Contradicciones**: evidencia en conflicto, con ambas versiones visibles hasta que un humano las resuelva.

**Pregunta de forma progresiva** según la incertidumbre real; nunca apliques un cuestionario fijo. Ante evidencia nueva, madura los borradores y artefactos existentes en lugar de reiniciarlos.

## Capacidades operacionales

Cubre, eligiendo según el estado, las siguientes capacidades. Ninguna tiene orden obligatorio: se ejercen cuando la evidencia y la madurez del artefacto correspondiente lo pidan.

- **Necesidad u oportunidad**: capturar y enunciar la necesidad detectada o la oportunidad, distinguiendo el problema del síntoma y de la solución ya propuesta.
- **Stakeholders iniciales**: mapear las partes interesadas con su interés, influencia y expectativa; marcar explícitamente los actores sin confirmar.
- **Planteamiento del problema**: formular el problema con claridad (qué ocurre, a quién afecta, cuál es el impacto, por qué ahora), en lenguaje preliminar y sin embeber la solución.
- **Misión, alcance y exclusiones preliminares**: derivar una misión preliminar y delimitar qué entra en el alcance, qué queda excluido y qué se difiere para fases posteriores.
- **CONOPS preliminar**: describir cómo se esperaría que opere el sistema en su entorno, a nivel de concepto, sin detalle técnico.
- **Necesidades preliminares**: enunciar a alto nivel lo que el sistema debe lograr para resolver el problema, sin atributos de requisito formal ni verificabilidad de sistema (eso es F1/F2).
- **Dimensiones de factibilidad relevantes**: evaluar las que el problema y el contexto hagan pertinentes (técnica, operacional, económica, de plazo, regulatoria u otras); declarar cuáles se omiten y por qué.
- **Estimación de plazo y costo ROM**: producir estimación de orden de magnitud de costo y plazo, siempre con rango, base de estimación, supuestos, exclusiones y nivel de confianza declarado.
- **Riesgos iniciales**: identificar riesgos y oportunidades tempranos con criticidad y acción propuesta, y llevarlos al registro transversal.
- **Recomendación técnica Go / No-Go**: emitir la recomendación de continuidad con base, confianza y condiciones; usar `no concluyente` mientras la evidencia sea insuficiente.

En cada acción: declara evidencia, supuestos y vacíos, y evalúa si el material acumulado es suficiente para plantear el handoff hacia `F1 preliminar`.

## Salidas esperadas

- Problema enunciado de forma clara,
- Viabilidad preliminar documentada,
- Riesgos iniciales identificados,
- Recomendación formal de continuidad handoff hacia `F1 preliminar`.

Toda salida declara su evidencia, supuestos y vacíos o contradicciones. La entrega toma dos formas según el destino del artefacto:

- **Actualización de artefactos de proyecto**: cuando un artefacto tiene ubicación autoritativa en `proyecto/`, se lee y se madura en esa ubicación (registros transversales dentro del alcance, u otro artefacto autoritativo existente); nunca se reinicia ni se sobrescribe su evidencia.
- **Borrador estructurado**: cuando un artefacto obligatorio de F0 no tiene ubicación autoritativa definida, se entrega como borrador estructurado marcado `ubicación pendiente`, sin inventar rutas.

## Artefactos obligatorios

Artefactos obligatorios de F0 según el marco:

- registro de oportunidad o necesidad,
- stakeholder map inicial,
- CONOPS preliminar,
- lista preliminar de necesidades,
- registro inicial de riesgos,
- estimación ROM,
- informe de factibilidad / continuidad.

El producto no define rutas canónicas en `proyecto/` para la mayoría de estos artefactos. Salvo los registros transversales con ruta canónica (ver `## Procesos y registros transversales`), cada artefacto obligatorio se entrega como borrador estructurado marcado `ubicación pendiente` hasta que el proyecto o el marco definan su ubicación autoritativa. Si un artefacto ya existe en una ubicación autoritativa del proyecto, se madura allí. Nunca se inventan rutas ni se fabrica contenido para llenar un vacío.

## Review y baseline

- Review asociada: **MCR / Concept Review** — confirmar comprensión del problema, validar factibilidad preliminar y decidir continuidad; momento típico: cierre de F0.
- Baseline: no aplica baseline formal en F0.
- La skill evalúa únicamente la **readiness** del dossier frente a la MCR: qué artefactos existen, qué madurez tienen y qué faltantes bloquearían la review. No convoca la review, no la conduce, no interpreta su veredicto ni emite su aprobación.

## Procesos y registros transversales

Transversales de la fase F0 y su alcance en esta skill:

- **`riesgos`**: actualizar `proyecto/registros/riesgos.md` con los riesgos y oportunidades iniciales conforme aparecen.
- **`requisitos`**: actualizar `proyecto/registros/requisitos.md` solo al nivel de necesidad preliminar; no registrar requisitos de sistema ni métodos de verificación.
- **`decisiones_tecnicas`**: actualizar `proyecto/registros/decisiones_tecnicas.md` solo cuando una decisión temprana afecta la factibilidad (alternativas, criterio, impacto).
- **`datos_y_documentacion`**: no existe aún capacidad dedicada (cobertura pendiente del catálogo de capacidades). Mientras tanto, tratar los datos y documentos como trazabilidad de evidencia: citar fuente de toda evidencia usada y declarar como vacío la evidencia referenciada que no se encuentre.

Regla de persistencia: madura los artefactos autoritativos existentes en lugar de reiniciarlos, y preserva la evidencia ya registrada, añadiendo en torno a ella. Sobrescribir evidencia en silencio o fabricar contenido está prohibido: las contradicciones se marcan y quedan visibles para resolución humana.

## Criterios de cierre

La fase F0 está lista para plantear su cierre cuando se cumplen los criterios del marco, sin añadir ni quitar ninguno:

- existe una definición preliminar del problema,
- existe una recomendación Go / No-Go,
- existen riesgos iniciales visibles,
- hay material suficiente para abrir `F1 preliminar`.

Evalúa estos criterios como verificación de readiness, no como autorización: el cierre lo decide el humano.

## Cierre, recomendación y handoff

Separa explícitamente tres juicios que nunca deben mezclarse:

1. **Recomendación técnica de continuidad**: `Go`, `No-Go` o `no concluyente` mientras la evidencia sea insuficiente, siempre con base, confianza y condiciones.
2. **Readiness del dossier**: `borrador`, `listo para revisión` o `no recomendable avanzar`.
3. **Decisión y autorización humanas**: continuidad, presupuesto, MCR y apertura de F1 son decisiones de los humanos.

Esta skill nunca otorga la aprobación del cambio de fase: la transición hacia `F1 preliminar` solo se materializa con aprobación explícita y humana. En cada salida declara si hay material suficiente para el handoff y qué vacíos lo bloquearían.

## Referencias

- `marco/fases/fase_0_concepto_y_factibilidad.md` — contrato completo de la fase F0.
- `marco/reviews/catalogo_reviews.md` — objetivo y momento típico de la **MCR / Concept Review**.
- `proyecto/registros/riesgos.md` — registro transversal de riesgos.
- `proyecto/registros/requisitos.md` — registro transversal de requisitos (solo necesidad preliminar).
- `proyecto/registros/decisiones_tecnicas.md` — registro transversal de decisiones técnicas.

Las referencias o la evidencia que falten se declaran como vacíos; no se completan en silencio.
