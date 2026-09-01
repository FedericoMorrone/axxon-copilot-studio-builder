---
name: skill-procedure-designer
description: >
  Escribe las Skills (procedimientos reusables) de un Agente de Microsoft Copilot Studio
  (GitHub Copilot harness) como InlineAgentSkill YAML bajo behaviors/, a partir de los casos de
  uso que behavior-spec-writer clasificó como Skill. Usar después de `behavior-spec-writer`,
  cuando el usuario diga "escribí el procedimiento para X", "necesito una skill que guíe al
  usuario en Y", o cuando .cs-project.md tenga casos de uso clasificados como Skill sin YAML
  generado todavía.
---

# Skill Procedure Designer

Quinta skill del ciclo. Toma los casos de uso que `behavior-spec-writer` clasificó como
**Skill** — procedimientos reusables de varios pasos — y los escribe como componentes
`InlineAgentSkill` bajo `behaviors/`.

## Paso 0 — Gate

```bash
python skills/agent-intake/scripts/validate_cs_project.py .cs-project.md --require "Casos de uso relevados"
```

Confirmá también que `settings.mcs.yml` exista. Antes de escribir, leé qué Tools ya están
creadas en `capabilities/tools/` (si `tools-and-connectors-catalog` ya corrió) — una Skill que
llama a una Tool tiene que referenciarla por su nombre real, no inventar una.

## Cuándo una Skill vale la pena — no generes de más

Adaptado (no copiado) del criterio de `copilot-studio-architect` de `microsoft/copilot-studio-
plugin` para el mismo harness:

- **Solo creá una Skill cuando el caso de uso genuinamente necesita un procedimiento** — una
  secuencia específica de pasos, preguntas de aclaración, o lógica de dominio. Si el modelo ya
  puede resolverlo con conocimiento general (sin guía específica), no hace falta Skill —
  volvé a `behavior-spec-writer` y reclasificalo como Instruction si aplica.
- **Preferí pocas Skills bien acotadas antes que una sola que abarque todo.** Cada Skill cubre
  un procedimiento claro; no agrupes varios casos de uso sueltos en una Skill "paraguas".
- **No generes Skills especulativas** que dupliquen lo que ya cubre una Knowledge (ver el
  matiz Knowledge vs. Skill documentado en `behavior-spec-writer/SKILL.md`) o una Instruction
  general.

## YAML — InlineAgentSkill

`behaviors/<nombre-slug>_<id>.mcs.yml`:

```yaml
mcs.metadata:
  componentName: <nombre-del-procedimiento-en-kebab-case>
  description: <una línea: qué procedimiento guía y cuándo se activa>
kind: InlineAgentSkill
content: |
  ---
  name: <nombre-del-procedimiento-en-kebab-case>
  description: <misma descripción de arriba, en el frontmatter del skill content>
  ---
  <instrucciones del procedimiento en Markdown>
```

El contenido Markdown interno de `content` tiene que cubrir, como mínimo:

1. **Trigger / cuándo usarla**: qué tipo de pedido activa este procedimiento.
2. **Inputs requeridos**: qué datos necesita del usuario antes de avanzar.
3. **Preguntas de aclaración**: qué preguntar si falta algo, en qué orden.
4. **Pasos de uso de Tools**: qué Tool llamar en qué momento (referenciada por su
   `componentName` real, tomado de `capabilities/tools/` — nunca inventada).
5. **Reglas de confirmación para efectos secundarios**: si el procedimiento crea, modifica,
   envía, o paga algo, tiene que pedir confirmación explícita antes de ejecutar — cruzá esto
   con `.cs-project.md > Restricciones conocidas > Seguridad / Autenticación`.
6. **Output esperado**: qué le queda claro al usuario al terminar.
7. **Fallback/escalamiento**: qué hacer si el procedimiento no puede completarse (falta un
   dato, la Tool falla, el caso queda fuera de alcance).

## Convención de nombres

Slug del nombre + sufijo corto único, igual que el resto de los componentes `.mcs.yml`. Al
editar una Skill existente, conservá el sufijo generado.

## Restricciones

- No referencies una Tool que no existe todavía en `capabilities/tools/` — si el procedimiento
  necesita una Tool que aún no se creó, derivá a `tools-and-connectors-catalog` primero, o
  documentá la dependencia como pendiente en la Skill.
- No agregues lógica de variables persistentes ni Power Fx — no existen en este harness; si el
  procedimiento necesita "recordar" algo entre pasos, instruí al agente para que lo haga vía
  contexto de la conversación, no vía una variable formal.
- No dupliques procedimientos — revisá `behaviors/` antes de crear uno nuevo por si ya existe
  algo equivalente.

## Actualizar `.cs-project.md`

Para cada Skill generada, marcá la fila correspondiente en `Casos de uso relevados` como
resuelta con el path del `.mcs.yml`. Si alguna quedó bloqueada por falta de una Tool, marcala
explícitamente como "pendiente — depende de Tool no creada".

## Al finalizar

Resumí cuántas Skills quedaron creadas y cuáles quedaron bloqueadas. Si ya corrieron las tres
skills de esta etapa (`knowledge-source-catalog`, `tools-and-connectors-catalog`,
`skill-procedure-designer`), decíselo al usuario y sugerí seguir con `publish-and-channels` o
`agent-alm` según corresponda.
