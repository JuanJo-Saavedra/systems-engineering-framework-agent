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
| `f1-stakeholders-preliminar` | estado preproyecto_presupuesto con fase F1 preliminar activa; necesidades preliminares, stakeholders, escenarios operativos, restricciones externas, matriz necesidad-requisito, material para cotizar y readiness frente al hito de aprobación del trabajo. | fase | `.agents/skills/f1-stakeholders-preliminar/SKILL.md` |
| `handoff-presupuesto-a-proyecto` | decisión aprobatoria del usuario sobre el trabajo emitida con F1 preliminar cerrada; consolidación del hito de aprobación del trabajo (insumos heredados y vacíos antes de F2) y transición de `preproyecto_presupuesto` a `aprobado_en_transicion`. | transición | `.agents/skills/handoff-presupuesto-a-proyecto/SKILL.md` |
| `docs-review` | instrucción humana explícita para preparar, someter, registrar una decisión, promover o validar un paquete documental versionado; requiere especificación exacta resuelta por el padre. | tarea puntual (revision y aprobacion de documentos) | `.agents/skills/docs-review/SKILL.md` |

## Protocolo de carga

1. Leer el estado del proyecto y clasificar la tarea.
2. Seleccionar la skill de fase y madurez correspondiente como contexto primario.
3. Añadir únicamente las skills transversales o de tarea puntual afectadas por la salida; no cargar todas por defecto.
4. Cargar el `SKILL.md` exacto de cada skill seleccionada, leyendo la ruta instalada indicada en este registry, antes de actuar.
5. Si la skill que la tarea requiere no figura aquí, declarar la ausencia de forma explícita: no inventar estado, evidencia ni instrucciones.
