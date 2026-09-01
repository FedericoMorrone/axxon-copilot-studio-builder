---
name: behavior-spec-writer
description: >
  Clasifica cada caso de uso relevado de un Agente de Microsoft Copilot Studio (GitHub Copilot
  harness) en uno de cuatro componentes — Instructions, Knowledge, Tools, o Skills — y escribe
  las instructions estáticas del agente en settings.mcs.yml. Es el primer paso que toca el
  workspace de archivos real del agente: si todavía no existe, lo inicializa con
  `pac copilot init`. Usar después de `agent-intake`, cuando el usuario diga "clasificá estos
  casos de uso", "escribí las instructions del agente", "arrancá el workspace del agente", o
  cuando cualquier skill de las etapas 3-5 (knowledge-source-catalog,
  tools-and-connectors-catalog, skill-procedure-designer) detecte que un caso de uso todavía no
  tiene componente candidato definitivo en .cs-project.md.
---

# Behavior Spec Writer

Segunda skill del ciclo de construcción, primera que produce YAML real. Convierte los casos de
uso en bruto de `agent-intake` en una clasificación definitiva por componente, y deja escritas
las instructions del agente. No escribe Knowledge, Tools, ni Skills en detalle — eso lo hacen
`knowledge-source-catalog`, `tools-and-connectors-catalog`, y `skill-procedure-designer`
respectivamente; esta skill solo decide **a cuál de los tres le corresponde cada caso**, y
escribe la parte que es exclusivamente suya: las Instructions.

## Paso 0 — Gate

```bash
python skills/agent-intake/scripts/validate_cs_project.py .cs-project.md --require "Casos de uso relevados"
```

Si el exit code es `1`, resolvé el bloqueo antes de seguir (ver `agent-intake/SKILL.md`) — no
clasifiques casos de uso a medio relevar.

## Paso 0.5 — Bootstrap del workspace, si no existe

Esta es la primera skill del plugin que toca archivos reales del agente, no solo
`.cs-project.md`. Antes de clasificar nada, confirmá si el workspace ya existe:

1. Buscá `settings.mcs.yml` en la raíz del workspace del cliente.
2. Si existe, continúá — no lo reinicialices ni lo pises.
3. Si no existe, inicializalo con el bootstrap en un paso, usando los datos ya confirmados en
   `.cs-project.md` (sección `Agente`):

```bash
pac copilot init \
  --name "<Agente > Nombre>" \
  --publisher-prefix axx \
  --authoring-mode cli-copilot \
  --environment "<Agente > Environment (Dataverse)>"
```

El publisher prefix es siempre `axx` (convención Axxon, nunca `axxon` ni `new`) — no lo
preguntes, no lo derives de otra cosa. Si `Agente > Environment (Dataverse)` en
`.cs-project.md` todavía está `(pendiente)`, pará y pedile ese dato al usuario antes de
continuar: sin environment no hay dónde crear el agente en Dataverse. Después de correr el
comando, confirmá que `settings.mcs.yml` quedó creado antes de seguir — si no está, deténte y
reportá el error tal cual lo devolvió `pac`, no lo reintentes a ciegas.

## Metodología de clasificación

Adaptada (no copiada) del criterio de diseño que usa `copilot-studio-architect` de
`microsoft/copilot-studio-plugin` para el mismo harness. La pregunta correcta no es "¿qué
componente mencionó el usuario?" sino **"¿qué trabajo tiene que hacer el agente acá, y cuál es
el componente más seguro y confiable para ese trabajo?"**

Usá este árbol de decisión para cada caso de uso de la tabla:

```text
¿Es una regla global de comportamiento, tono, alcance o política que aplica a TODA la
conversación (no a un caso puntual)?
→ Instruction

¿Es información factual que el agente debe buscar/citar/fundamentar una respuesta en ella?
→ Knowledge

¿Requiere una acción externa, una consulta en vivo, un cambio de estado, o un cálculo
determinista?
→ Tool

¿Describe un procedimiento reusable de varios pasos, un "cómo hacer" experto?
→ Skill (puede apoyarse en una Tool ya definida)
```

Matices importantes que hay que aplicar con criterio, no mecánicamente:

- **Knowledge vs. Skill sobre la misma fuente**: si el objetivo es que el agente *busque* dentro
  de un documento para fundamentar una respuesta (RAG), es Knowledge. Si el objetivo es que el
  agente *guíe al usuario* a través de un procedimiento que ese documento describe (ej. un
  instructivo paso a paso), es una Skill que usa una Tool para traer el archivo completo — no
  Knowledge, porque ahí no se está buscando semánticamente, se está usando como fuente de
  verdad de un procedimiento.
- **Tool vs. Skill**: si se puede expresar como una función con inputs/outputs concretos
  (`consultar_saldo(cuenta)`, `crear_reclamo(motivo)`), es una Tool. Si es un procedimiento de
  varios pasos que puede llamar a una o más Tools en el camino ("gestionar un reclamo",
  "recomendar el mejor producto"), es una Skill.
- **No hay Topics determinísticos, variables, ni Power Fx en este harness.** Si un caso de uso
  parece pedir eso ("en este paso exacto, guardar la variable X"), no lo fuerces a un Topic —
  traducilo a una Skill con instrucciones explícitas, o a una Instruction si es una regla
  general de manejo de contexto.
- **Evitá solapamiento**: no generes una Skill y una Knowledge redundantes para el mismo tema
  (ej. "Skill: responder preguntas de seguros" + "Knowledge: preguntas de seguros"). El patrón
  correcto es Knowledge = la fuente de hechos, Skill = el procedimiento que la usa (si hace
  falta un procedimiento; muchas veces alcanza con la Knowledge sola).

## Cómo aplicar la clasificación

1. Recorré la tabla `Casos de uso relevados` de `.cs-project.md` fila por fila.
2. Para cada una, aplicá el árbol de decisión y reemplazá el valor tentativo de la columna
   `Componente candidato` por la clasificación definitiva.
3. Si un caso de uso es ambiguo incluso aplicando los matices de arriba, no lo resuelvas
   inventando — preguntale al usuario con la pregunta puntual (ej. "para el caso 'consultar
   política de cancelación', ¿el agente debe buscar y citar la política, o guiar paso a paso el
   proceso de cancelación?") en vez de asumir.
4. Un caso de uso puede generar más de un componente (ej. una Skill que además necesita una
   Tool nueva) — en ese caso, agregá una fila por componente resultante, todas trazables al
   mismo caso de uso original vía la columna `Fuente`.

## Qué escribe esta skill (y qué no)

**Sí escribe:** las instructions estáticas del agente en `settings.mcs.yml`, bajo
`configuration.agentSettings.instructions.segments` con `kind: StaticSegment`. Ahí van: rol y
persona del agente, alcance, tono, reglas de seguridad/privacidad, política de escalamiento,
política de cuándo usar tools, política de confirmación antes de acciones con efecto
(crear/modificar/enviar/pagar — cruzá esto con `Restricciones conocidas > Seguridad /
Autenticación` de `.cs-project.md`), y qué hacer cuando una pregunta cae fuera de alcance.
Redactalas en español (o el idioma principal que diga `.cs-project.md`), tono de Solution
Architect, sin relleno genérico.

**No escribe:** el detalle de ningún componente Knowledge/Tool/Skill — eso queda para las
skills de las etapas 3, 4 y 5. No inventes esos archivos ni sus carpetas.

## Actualizar `.cs-project.md`

Después de clasificar, actualizá la tabla `Casos de uso relevados` con la clasificación
definitiva en la columna `Componente candidato`, y agregá una línea en `## Historial de
cambios` resumiendo cuántos casos quedaron en cada categoría (ej. "3 Instructions incorporadas
al agente, 2 Knowledge, 4 Tools, 1 Skill" — no hace falta detallar cada fila, la tabla ya lo
muestra). No cambies `Estado > Fase actual` vos misma/o — dejá que lo actualice la skill que
cierra el ciclo completo (`agent-alm`); mientras tanto, referite a esta etapa en prosa si el
usuario pregunta en qué está el agente.

## Al finalizar

Resumí cuántos casos quedaron clasificados en cada componente, y decile al usuario
explícitamente qué sigue: si hay casos Knowledge, `knowledge-source-catalog`; si hay Tools,
`tools-and-connectors-catalog`; si hay Skills, `skill-procedure-designer`. Pueden correr en
cualquier orden entre sí (no son secuenciales unas de otras) — solo dependen de que esta skill
haya corrido primero.
