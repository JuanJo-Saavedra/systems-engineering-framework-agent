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
| `f0-factibilidad` | Fase F0 activa / estado `preproyecto_presupuesto`; necesidad, problema, stakeholders, CONOPS, ROM, riesgos, factibilidad, Go/No-Go y readiness de MCR | Skill de fase (F0) | `.agents/skills/f0-factibilidad/SKILL.md` |

## Protocolo de carga

1. Leer el estado del proyecto y clasificar la tarea.
2. Seleccionar la skill de fase y madurez correspondiente como contexto primario.
3. Añadir únicamente las skills transversales o de tarea puntual afectadas por la salida; no cargar todas por defecto.
4. Cargar el `SKILL.md` exacto de cada skill seleccionada, leyendo la ruta instalada indicada en este registry, antes de actuar.
5. Si la skill que la tarea requiere no figura aquí, declarar la ausencia de forma explícita: no inventar estado, evidencia ni instrucciones.
