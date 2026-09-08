---
version: 2.0
description: "Registry de skills instaladas: localiza la skill aplicable al contexto y la tarea, y expone la ruta exacta de cada SKILL.md a cargar antes de actuar."
---

# Registry de skills instaladas

## Contrato

Este registry es el índice de disponibilidad de skills instaladas. Su función es localizar la skill aplicable para el contexto y la tarea del orquestador.

- No redefine el dominio ni el procedimiento de ninguna fase ni capacidad.
- Cada `SKILL.md` referenciado es la única fuente de instrucciones operativas de su skill; este registry no las sustituye ni las resume.

## Skills disponibles

| Skill / id | Contexto o trigger | Tipo / alcance | Ruta instalada |
| ---------- | ------------------ | -------------- | -------------- |
| `f0-factibilidad` | Fase F0 activa / estado `preproyecto_presupuesto`; necesidad, problema, stakeholders, CONOPS, ROM, riesgos, factibilidad, Go/No-Go y readiness de MCR | fase | `.agents/skills/f0-factibilidad/SKILL.md` |
| `f1-stakeholders-preliminar` | estado preproyecto_presupuesto con `F0` cerrada y aprobada, fila F1 preliminar `no_iniciada` y pedido humano explícito de apertura (cambio atómico de apertura); o fase F1 preliminar activa en continuación (`en_progreso`); necesidades preliminares, stakeholders, escenarios operativos, restricciones externas, matriz necesidad-requisito, material para cotizar y readiness frente al hito de aprobación del trabajo. | fase | `.agents/skills/f1-stakeholders-preliminar/SKILL.md` |
| `handoff-presupuesto-a-proyecto` | decisión aprobatoria del usuario sobre el trabajo emitida con F1 preliminar cerrada; consolidación del hito de aprobación del trabajo (insumos heredados y vacíos antes de F2) y transición de `preproyecto_presupuesto` a `aprobado_en_transicion`. | transición | `.agents/skills/handoff-presupuesto-a-proyecto/SKILL.md` |
| `f1-stakeholders-formal` | primer trabajo: estado `aprobado_en_transicion` con fila `F1 formal: no_iniciada`, handoff consolidado y pedido humano explícito de apertura formal; o continuación: estado `proyecto_formal` con fase F1 en madurez formal (`en_progreso`); vacíos heredados del presupuesto, cierre de contradicciones entre stakeholders, maduración de los cuatro artefactos a formal, review por paquete `f1-stakeholders-formal-r<NNN>` y base apta para abrir F2. | fase | `.agents/skills/f1-stakeholders-formal/SKILL.md` |
| `f2-requisitos-sistema` | primer trabajo: estado `proyecto_formal` con fila `F2: no_iniciada`, gate de paso a F2 satisfecho y pedido humano explícito de apertura; o continuación: fase F2 activa (`en_progreso`); derivación de requerimientos de sistema verificables y trazables, dos matrices de trazabilidad, plan V&V preliminar, traducir las necesidades y stakeholders requirements en requerimientos tecnicos verificables y trazables. SRR y constitución de la Functional Baseline. | fase | `.agents/skills/f2-requisitos-sistema/SKILL.md` |
| `docs-review` | instrucción humana explícita para preparar, someter, registrar una decisión, promover o validar un paquete documental versionado; requiere especificación exacta resuelta por el padre. | tarea puntual (revision y aprobacion de documentos) | `.agents/skills/docs-review/SKILL.md` |
| `preparacion-de-review` | instrucción humana explícita de preparar una review formal o readiness declarada por la skill de fase; con tipo de review y fase activa arma el dossier técnico de review (inventario de evidencia, criterios de entrada/salida, bloqueos, agenda, conclusión de readiness) para las diez reviews del catálogo; solo lectura, nunca emite veredicto ni opera el paquete documental. | tarea puntual (preparación de reviews formales) | `.agents/skills/preparacion-de-review/SKILL.md` |

## Protocolo de carga

1. Leer el estado del proyecto y clasificar la tarea.
2. Seleccionar la skill de fase y madurez correspondiente como contexto primario.
3. Añadir únicamente las skills transversales o de tarea puntual afectadas por la salida; no cargar todas por defecto.
4. Cargar el `SKILL.md` exacto de cada skill seleccionada, leyendo la ruta instalada indicada en este registry, antes de actuar.
5. Si la skill que la tarea requiere no figura aquí, declarar la ausencia de forma explícita: no inventar estado, evidencia ni instrucciones.
