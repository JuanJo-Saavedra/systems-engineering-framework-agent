---
document_type: propuesta
language: es
version: 0.2
status: propuesta
---
# Memoria dual

## Propósito

Definir cómo conviven:

- **Markdown autoritativo versionado** (estado y registros del proyecto), y
- **Memoria semántica** vía Engram MCP, con RAG como recuperación/indexación (no autoridad).

## Orden de autoridad

```text
Markdown autoritativo (proyecto/)
   ↑ gana en conflicto
Engram (resúmenes, descubrimientos, rationale, preferencias, punteros)
   ↑ suplemento
RAG (indexación / recuperación)
```

## Flujos de lectura/escritura

| Acción                       | Flujo                                                       |
| ----------------------------- | ----------------------------------------------------------- |
| Hecho o decisión de proyecto | Escribir Markdown**primero**; luego resumen en Engram |
| Descubrimiento o rationale    | Engram, con puntero al Markdown de origen                   |
| Recuperación de contexto     | RAG sobre Markdown; Engram para señales semánticas        |

## Política de conflicto

- **Markdown gana** siempre.
- Las discrepancias se **hacen visibles**, nunca se reconcilian en silencio.
- Engram no es la única copia de la verdad del proyecto; guarda resúmenes y punteros, no el único ejemplar de los hechos.

## Modos degradados

| Falla                                     | Comportamiento                              |
| ----------------------------------------- | ------------------------------------------- |
| Engram no disponible                      | Continuar solo con Markdown                 |
| RAG no disponible                         | Lectura directa de archivos                 |
| Documento autoritativo ausente o corrupto | **Fallar cerrado**                    |
| Engram + RAG caídos                      | Operación auditable si Markdown está sano |

## Privacidad, alcance, retención y procedencia

- **Alcance**: memoria por proyecto, nunca global sin permiso.
- **Privacidad**: no persistir secretos, credenciales, datos personales ni contenido crudo no confiable.
- **Retención**: resúmenes y punteros; no duplicar documentos autoritativos.
- **Procedencia**: registrar fuente y revisión cuando exista.

## Campos recomendados del registro de memoria

| Campo               | Obligatorio | Notas                                                    |
| ------------------- | ----------- | -------------------------------------------------------- |
| `project`         | sí         | Alcance de proyecto                                      |
| `type`            | sí         | resumen, descubrimiento, rationale, preferencia, puntero |
| `topic_key`       | sí         | Clave estable para upserts                               |
| `source_paths`    | sí         | Rutas de origen                                          |
| `source_revision` | no          | Hash/commit cuando esté disponible                      |
| `timestamps`      | sí         | Creación y actualización                               |

## Configuración MCP en Codex

El nombre oficial de tabla es `[mcp_servers.<name>]`. Los valores reales de Engram (comando, URL, auth, nombres de tools) **deben confirmarse**; no se inventan.

### STDIO

```toml
[mcp_servers.engram]
enabled = true          # opción de despliegue
required = false        # la memoria es suplemento, no bloquea el arranque
command = "<comando-real-de-engram>"   # a confirmar
args = ["<args-reales>"]               # a confirmar
env = { "<VAR>" = "<valor>" }          # solo si aplica
# timeout y allowlist de tools: opciones de despliegue a confirmar
```

### Streamable HTTP

```toml
[mcp_servers.engram]
enabled = true
required = false
url = "<url-real-del-servidor>"        # a confirmar
# headers/auth, timeout y allowlist de tools: a confirmar
```

> `enabled`, `required = false`, timeouts y allowlist de tools son **opciones de despliegue**; la clave exacta de allowlist/timeout debe confirmarse contra la versión del adaptador Codex y no asumirse como built-in genérico.

## Checklist de reconciliación operativa

- [ ] Markdown autoritativo actualizado antes que Engram.
- [ ] Sin secretos ni datos personales en memoria.
- [ ] Los punteros de Engram apuntan a rutas válidas.
- [ ] Ante una discrepancia, se informa y gana Markdown.
- [ ] Revisión/hash registrado cuando está disponible.

## Escenarios de prueba MVP

| Escenario                            | Esperado                                    |
| ------------------------------------ | ------------------------------------------- |
| Escribir hecho con Engram disponible | Markdown primero, resumen después          |
| Engram caído                        | Operación continúa solo con Markdown      |
| RAG caído                           | Lectura directa                             |
| Documento ausente/corrupto           | Fallar cerrado                              |
| Conflicto Engram vs Markdown         | Gana Markdown y se registra la discrepancia |

## Relacionado

- [arquitectura-orquestador.md](arquitectura-orquestador.md) — capas.
- [frontera-dominio-harness.md](frontera-dominio-harness.md) — autoridad.
- [quickstart-agentes.md](quickstart-agentes.md) — flujo mínimo.
- [reestructuracion-agents.md](reestructuracion-agents.md) — decisión canónica: contrato único de `AGENTS.md`.
