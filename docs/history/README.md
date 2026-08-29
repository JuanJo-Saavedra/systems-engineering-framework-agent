---
document_type: indice_historico
language: es
version: 1.0
status: deprecated
---

# `docs/history/` — histórico (deprecated, no autoritativo)

> **AVISO: este directorio está deprecated y no es autoritativo.**
>
> Todo el contenido de `docs/history/` es material **histórico** y queda **fuera de la arquitectura vigente**. No es fuente de verdad, no participa en la generación del producto y no debe usarse como referencia para implementar ni para tomar decisiones.

## Reglas de uso

- **No autoritativo**: nada de lo que hay aquí define comportamiento, rutas, contratos ni decisiones vigentes.
- **Solo lectura**: no se edita para derivar decisiones nuevas; si se corrige, se registra como corrección histórica, no como cambio de autoridad.
- **No participa en generación**: el instalador, el empaquetado, el manifiesto y las skills **no** se generan desde este directorio.
- **Fuente vigente**: la arquitectura actual está en `docs/architecture/product.md`; el contrato único de runtime está en `runtime/AGENTS.md`.

## Contenido actual

- `AGENTS-gentle-ai.md` — variante histórica de contrato (superada).
- `skill-registry-gentle-ai.md` — variante histórica del catálogo (superada).
- `diagrama-mvp.png` — ideación histórica del arnés (superada en lo que difiera de la arquitectura vigente).
- `decisions/tradeoff-codex-pi.md` — análisis histórico de infraestructura Codex vs Pi (superado por la arquitectura v2.0).
- `guias/retomar_automatizacion.md` — guía histórica.
- `guias/skill-registry-v0.md` — catálogo histórico.

> `guias/project-init.md` ya no está en este directorio: fue curada y movida a `framework/guias/project-init.md` durante la reestructuración. No queda copia histórica de esa guía aquí.

## Dónde está la autoridad vigente

- Arquitectura y topología: `../architecture/product.md`.
- Contrato de runtime: `../../runtime/AGENTS.md`.
- Arquitectura de capacidades: `../../framework/guias/skill-architecture.md`.
- Registry operativo: `../../runtime/catalogo/skill-registry.md` (bootstrap con 0 skills; generador/CI pendiente).
- Guías canónicas del framework: `../../framework/guias/`; `project-init.md` fue curada a `../../framework/guias/project-init.md`.
