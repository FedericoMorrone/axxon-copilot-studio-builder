---
name: agent-intake
description: >
  Levanta el contexto inicial para construir un Agente en Microsoft Copilot Studio sobre el
  GitHub Copilot harness: objetivo, audiencia, canal de publicación destino, environment, y
  casos de uso funcionales a partir de cualquier tipo de archivo de referencia (RFP, notas de
  reunión, transcripciones de Teams, documentos de definición funcional, matrices de casos de
  uso en Excel/CSV, PDFs). Genera el archivo de contexto .cs-project.md que todas las demás
  skills del plugin Axxon Copilot Studio Builder (behavior-spec-writer, knowledge-source-catalog,
  tools-and-connectors-catalog, skill-procedure-designer, publish-and-channels, agent-alm)
  requieren como precondición. Usar SIEMPRE al arrancar el diseño de un agente nuevo, cuando el
  usuario diga "quiero construir un agente para X", "arranquemos un Copilot Studio nuevo",
  adjunte documentación funcional o casos de uso, o cuando cualquier otra skill de este plugin
  detecte que falta el archivo .cs-project.md.
---

# Agent Intake

Primera skill del ciclo de construcción. Su único objetivo es producir un contexto
estructurado y verificado — nunca inventado — que sirva de fundación para todo lo que sigue:
especificación de comportamiento, Knowledge, Tools/MCP/IQ, Skills, publicación y ALM.

## Decisión de arquitectura — harness fijo y generación propia de YAML

Este plugin targetea exclusivamente el **GitHub Copilot harness** (modelo agentic-loop), no el
standard harness clásico de Topics. Es una decisión ya tomada a nivel de plugin, no algo que
se pregunte por agente — en la sección `Agente` de `.cs-project.md` el campo Harness se
completa directo como `GitHub Copilot`, sin preguntarlo. Motivo: es el harness donde Microsoft
invierte el tooling nuevo (`pac copilot`, Foundry IQ, Fabric IQ, Work IQ), a cambio de perder
Topics determinísticos, variables y Adaptive Cards.

Además, este plugin **genera el YAML del agente directamente** — se evaluó depender de
`mcs-assistant` (`microsoft/copilot-studio-plugin`), pero ese toolkit solo cubre **migración**
de un agente clásico existente, no construcción desde cero. Las skills de este plugin adaptan
(con crédito, no copia literal) la metodología de clasificación de su `copilot-studio-
architect.md` como referencia de diseño. Si en algún momento un caso de cliente necesita
explícitamente features del standard harness (Topics determinísticos, Adaptive Cards), avisale
al usuario que está fuera del alcance de este plugin tal como está diseñado hoy — no lo
fuerces.

## Paso 0 — Gate obligatorio

Ninguna otra skill de este plugin puede procesar un pedido sin que este gate pase. Se valida
de forma determinística con `scripts/validate_cs_project.py`, no a ojo — dos capas:

1. **Validez estructural**: todas las secciones requeridas (`Agente`, `Objetivo y audiencia`,
   `Fuentes de referencia`, `Casos de uso relevados`, `Restricciones conocidas`, `Estado`)
   están presentes. Si falta una sección completa, el archivo está corrupto o incompleto —
   siempre corresponde derivar a `agent-intake`.
2. **Completitud de campos específicos**: cada skill downstream declara con
   `--require "Nombre de sección"` qué secciones necesita con contenido real (no `(pendiente)`)
   para poder trabajar. Ej.: `behavior-spec-writer` exige `--require "Casos de uso relevados"`;
   `tools-and-connectors-catalog` exige `--require "Restricciones conocidas"`.

```bash
python skills/agent-intake/scripts/validate_cs_project.py .cs-project.md --require "<sección>"
```

Exit code `0` = gate pasado. Exit code `1` = leer `blocking_reasons` del JSON de salida y
actuar: si `structurally_valid` es `false`, reparar formato acá mismo; si el bloqueo es una
sección puntual en `(pendiente)`, no hace falta rehacer todo el intake — solo completar ese
dato con el usuario.

## Fuentes de input — cualquier tipo de archivo de referencia

El insumo llega de la combinación de lo que haya disponible en cada momento — no hay un único
formato esperado. Aceptá y procesá:

- **Documentos funcionales**: RFP, propuesta aprobada, documento de definición funcional (FDD),
  especificación de casos de uso — vía las skills `docx`/`pdf`/`file-reading` ya disponibles
  para la ingesta; esta skill no reimplementa el parsing de esos formatos.
- **Transcripciones**: de reuniones de descubrimiento, workshops de casos de uso, o calls de
  kickoff con el cliente.
- **Matrices de casos de uso**: Excel/CSV con columnas tipo Caso de uso / Actor / Resultado
  esperado — leer vía `xlsx` skill.
- **Interactivo en el chat**: el usuario cuenta el contexto y va respondiendo preguntas
  puntuales cuando no hay material previo.
- **Combinación + refinamiento**: lo más común — el archivo arranca con lo que haya de
  documentos/transcripciones y se completa sesión a sesión, nunca de una sola vez.

Extraé todo lo que puedas del material ya provisto antes de preguntar. Si el usuario pega una
transcripción larga o adjunta un documento extenso, no le pidas que resuma él mismo lo que ya
está ahí — leelo vos y proponé qué campos completa.

## Modo de arranque

Antes de preguntar todas las dimensiones, resolvé una sola cosa primero: **¿llega con
material, o llega con las manos vacías?**

**Primera pregunta siempre:** "¿Tenés algo para arrancar — RFP, documento funcional,
transcripción de algún workshop, una matriz de casos de uso — o es la primera vez que
hablamos de este agente?"

### Rama A — Con material

Pedile que lo pegue o adjunte, extraé todo lo que puedas vos mismo (objetivo, casos de uso,
audiencia, sistemas mencionados), y mostrale un resumen de qué quedó completo y qué quedó
`(pendiente)`. No le preguntes por datos que ya están en el documento.

### Rama B — Arranque en limpio

Solo estas 3 preguntas mínimas, nunca todas las dimensiones de una vez:

1. ¿Qué problema o proceso va a resolver el agente, en una frase?
2. ¿Quién lo va a usar — empleados internos, clientes finales, ambos?
3. ¿Ya saben en qué canal se va a publicar (Teams, Web, Omnichannel/D365 Contact Center), o
   todavía no está definido?

Todo lo demás queda `(pendiente)` a propósito — el detalle de Knowledge sources o de
conectores no vive en la cabeza de quien arranca el intake, va a salir de las etapas
siguientes.

## Qué información se levanta

1. **Agente**: nombre de trabajo, environment de Dataverse destino, harness (`GitHub Copilot`,
   fijo — ver Decisión de arquitectura arriba), idioma principal, canal(es) de publicación
   destino.
2. **Objetivo y audiencia**: qué resuelve el agente, para quién, en lenguaje del negocio — no
   lo traduzcas todavía a Instructions/Knowledge/Tools/Skills (eso lo hacen las etapas
   siguientes).
3. **Fuentes de referencia**: tabla con cada archivo/fuente usado, tipo, resumen de qué aportó,
   y fecha — para que `behavior-spec-writer` pueda trazar de qué caso de uso salió cada
   componente del agente.
4. **Casos de uso relevados**: uno por fila, con la fuente de donde salió y un componente
   candidato tentativo (Instruction / Knowledge / Tool / Skill — sin comprometerse al diseño
   final, esa clasificación definitiva la hace `behavior-spec-writer`).
5. **Restricciones conocidas**, categorizadas — igual que en otras skills de Axxon, no como
   lista plana, porque `tools-and-connectors-catalog` y `publish-and-channels` filtran sobre
   esto después:
   - **Seguridad / Autenticación**: requisitos de Entra ID, on-behalf-of, roles.
   - **Compliance / Regulatorio**: marcos aplicables (ej. BCRA/UIF si es FSI Argentina).
   - **Técnicas / Plataforma**: Copilot Credits (este harness factura por créditos, no por el
     modelo de capacidad del standard harness), límites de canal, sistemas legacy a integrar.
   Si una categoría fue relevada y no hay restricciones, marcá `(ninguna identificada)` — es
   un dato confirmado, distinto de `(pendiente)` que significa "todavía no se preguntó".
6. **Estado**: fase actual del ciclo (arranca en "Intake") y fecha de última actualización.

## Cómo conducir el intake

- Arrancá siempre por el Modo de arranque — determiná primero si hay material o no.
- Nunca completes un campo con un supuesto. Sin confirmar: `(pendiente)`. Confirmado que no
  aplica: `(ninguna identificada)`.
- Si el campo ya tenía un valor confirmado (no `(pendiente)`) y el usuario da uno nuevo, no lo
  pises en silencio: mostrale el contraste ("tenía cargado X, ahora das Y — ¿reemplaza al
  anterior?") y, si confirma, registralo en `## Historial de cambios` antes de sobrescribir.

## Formato de salida — `.cs-project.md`

```markdown
# Copilot Studio Agent — Contexto del proyecto

## Agente
- Nombre:
- Environment (Dataverse):
- Harness: GitHub Copilot
- Idioma principal:
- Canal(es) de publicación destino:

## Objetivo y audiencia
-

## Fuentes de referencia
| Archivo/fuente | Tipo | Resumen | Fecha |
|---|---|---|---|

## Casos de uso relevados
| Caso de uso | Fuente | Componente candidato (Instruction/Knowledge/Tool/Skill) | Estado |
|---|---|---|---|

## Restricciones conocidas
### Seguridad / Autenticación
-

### Compliance / Regulatorio
-

### Técnicas / Plataforma
-

## Estado
- Fase actual: Intake
- Última actualización: [fecha]

## Historial de cambios
| Fecha | Sección/campo | Valor anterior | Valor nuevo | Motivo |
|---|---|---|---|---|
```

Guardá el archivo en la raíz del workspace del cliente como `.cs-project.md`. Confirmá con el
usuario qué secciones quedaron `(pendiente)` y sugerí en qué próxima instancia conviene
cerrarlas.

## Al finalizar

Decile al usuario explícitamente qué sigue: normalmente `behavior-spec-writer`, para clasificar
los casos de uso relevados en Instructions/Knowledge/Tools/Skills y empezar a escribir el YAML
real del agente (`settings.mcs.yml` y, según corresponda, los archivos bajo `capabilities/` y
`behaviors/`).
