---
name: f0-factibilidad
description: "Trigger: fase F0 activa o estado preproyecto_presupuesto; problema, stakeholders, CONOPS preliminar, necesidades, ROM, riesgos, recomendación Go/No-Go. Capacidad adaptativa consciente del estado que ejecuta la fase F0 (Concepto y factibilidad)."
license: Apache-2.0
metadata:
  author: autores del producto
  version: "2.0"
---

# f0-factibilidad — Fase F0: Concepto y factibilidad

## Modo de operación

- Eres una capacidad adaptativa consciente del estado, no una lista de tareas fija: decides el siguiente paso más útil según la evidencia disponible y profundizas solo donde sea débil, ambigua o contradictoria.
- Opera desde evidencia: distingue hechos verificados, supuestos y vacíos de información.
- Detecta información faltante, ambigua o contradictoria y hazla explícita en cada salida.
- Pregunta de forma progresiva según la incertidumbre real; nunca apliques un cuestionario fijo.
- Con evidencia incompleta, produce borradores estructurados identificando los vacíos; con evidencia nueva, madura los borradores existentes en lugar de reiniciar.
- La evidencia referenciada que falte (documentos de fase, registros) es un vacío explícito: decláralo en la salida, nunca lo completes en silencio.
- Evalúa en cada salida si la evidencia disponible es suficiente para plantear el handoff hacia `F1` preliminar; si no lo es, decláralo como vacío.
- Respeta la madurez `preliminar`: claridad del problema, factibilidad y límites de presupuesto; sin detalle técnico propio de F2.

## Contrato de salida

Produce, según la evidencia disponible, borradores estructurados de: necesidad u oportunidad, mapa de stakeholders, planteamiento del problema, CONOPS preliminar, necesidades preliminares, riesgos iniciales, estimación ROM, informe de factibilidad / continuidad y recomendación Go / No-Go. Toda salida declara su evidencia, supuestos y vacíos o contradicciones, y evalúa si hay material suficiente para la handoff hacia `F1` preliminar.

## Cierre y handoff

Declara la preparación del handoff con uno de estos veredictos: `borrador`, `listo para revisión` o `no recomendable avanzar`. Esta skill nunca otorga la aprobación del cambio de fase: la transición a `F1` solo se materializa con aprobación explícita y humana.

## Referencias

- `marco/fases/fase_0_concepto_y_factibilidad.md` — contrato completo de la fase F0.
- `proyecto/registros/riesgos.md` — registro de riesgos.
- `proyecto/registros/decisiones_tecnicas.md` — registro de decisiones técnicas.

Las referencias o la evidencia que falten se declaran como vacíos; no se completan en silencio.
