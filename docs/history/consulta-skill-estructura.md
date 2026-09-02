# Estructuracion de una skill

La skill no debe ejecutar mecánicamente siete pasos; debe aportar una capacidad especializada que el orquestador aplica sobre el estado actual del proyecto.

La separación correcta es:

 - Orquestador: lee el estado, selecciona f0-factibilidad y controla la transición.
 - Skill: interpreta evidencia F0, reduce incertidumbre y prepara el handoff.
 - Usuario: aprueba o rechaza avanzar a F1.
 - Templates futuros: orientarán la forma documental, pero no serán autoridad ni condición actual.

Comportamiento propuesto

 La skill debería:

 - trabajar con la evidencia disponible;
 - detectar información faltante o contradictoria;
 - formular preguntas progresivas, no un cuestionario fijo;
 - producir borradores estructurados cuando la evidencia sea incompleta;
 - madurar esos borradores conforme aparezca nueva información;
 - evaluar si existe material suficiente para presentar el handoff;
 - nunca aprobar por sí misma el cambio de fase.

Estados de la salida

 Sin inventar nuevos estados del proyecto, el resultado de una ejecución puede declararse como:

 - Borrador: faltan datos relevantes.
 - Listo para revisión: hay evidencia suficiente para que el usuario decida.
 - No recomendable avanzar: existen bloqueos o riesgos incompatibles con el handoff.

Aprobado no sería una conclusión de la skill. Solo puede surgir de una decisión explícita del usuario, que luego el orquestador registra.

Nueva estructura

 ```markdown
   ---
   name: f0-factibilidad
   description: "Trigger: fase F0, concepto y factibilidad, necesidad u oportunidad, CONOPS preliminar, ROM, riesgos iniciales o decisión Go/No-Go. Madura la
 evidencia necesaria para preparar el handoff hacia F1 preliminar."
   ---

   ## Propósito

   ## Modo de operación

   ## Contrato de salida

   ## Condiciones del handoff

   ## Referencias
 ```

El núcleo normativo de la skill, no una explicación secundaria.

Lo redactaría así:

 ```markdown
   ## Modo de operación

   - Trabaja con la evidencia disponible y distingue hechos, supuestos y faltantes.
   - Detecta información ausente, ambigua o contradictoria antes de formular conclusiones.
   - Formula preguntas progresivas según la incertidumbre encontrada; no aplica un cuestionario fijo.
   - Produce borradores estructurados cuando la evidencia sea incompleta e identifica explícitamente sus vacíos.
   - Madura los borradores conforme aparece nueva evidencia, sin reiniciar el análisis innecesariamente.
   - Evalúa si existe material suficiente para presentar el handoff hacia F1 preliminar.
   - Nunca aprueba el cambio de fase: presenta la evidencia y la recomendación para decisión explícita del usuario.
 ```

 Esto diferencia claramente tres responsabilidades:

 - la skill analiza y madura;
 - el orquestador coordina y registra;
 - el usuario aprueba la transición.

 Queda acordado como requisito obligatorio para esta skill y como patrón para las futuras skills de fase.

 ---

# Test

Están divididos en tres niveles:

 ### 1. Tests generalistas

 No dependen del contenido concreto:

 - nombres en kebab-case;
 - name igual al directorio;
 - coherencia skill ↔ registry;
 - rutas válidas;
 - ausencia de entradas duplicadas u obsoletas;
 - payload canónico y empaquetado byte-idénticos.

 Estos sirven para todas las skills futuras.

 ### 2. Tests del contrato F0

 Están ligados al comportamiento, no a cada frase:

 - debe trabajar adaptativamente;
 - debe permitir borradores;
 - debe preguntar progresivamente;
 - no debe contener un procedimiento/checklist;
 - debe producir las salidas F0;
 - debe evaluar el handoff;
 - nunca debe aprobar la transición.

 Podés mejorar la redacción sin cambiar los tests mientras conserves esos conceptos y las secciones acordadas. Sin embargo, actualmente algunas comprobaciones
 buscan encabezados y términos concretos como Modo de operación, vacíos o cuestionario fijo; por lo tanto, no son completamente independientes del texto.

 ### 3. Coherencia del payload

 Si modificás manualmente la skill canónica, no hay que reescribir el test, pero sí resincronizar:

 ```bash
   python tools/sync_payload.py
 ```

 De lo contrario, el test detectará que la skill fuente y la copia empaquetada difieren.

 Regla práctica

 - Corrección de redacción: normalmente no cambia tests.
 - Cambio de formato sin cambiar comportamiento: podría requerir ajustar alguna comprobación demasiado rígida.
 - Cambio del contrato funcional: sí debe cambiar primero el test.
 - Nueva skill: los verificadores generales deberían reutilizarse, pero habrá que retirar la condición MVP de “exactamente una skill” y agregar pruebas
   específicas para el nuevo contrato de fase.

 En resumen: son generalistas en estructura, semánticos para F0, y todavía tienen un acoplamiento moderado a ciertos encabezados y vocabulario. No están
 ligados palabra por palabra.