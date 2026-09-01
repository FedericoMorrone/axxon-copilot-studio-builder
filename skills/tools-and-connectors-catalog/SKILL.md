---
name: tools-and-connectors-catalog
description: >
  Releva con el usuario los datos concretos (connector ID, operation ID, auth mode, connection
  reference) que necesita cada Tool de un Agente de Microsoft Copilot Studio (GitHub Copilot
  harness) y escribe los YAML bajo capabilities/tools/ — conectores estándar y custom, Power
  Automate/Agent Flows, servidores MCP, conectores IQ (Foundry IQ, Fabric IQ, Work IQ). Usar
  después de `behavior-spec-writer`, cuando el usuario diga "agregá una tool para X", "conectá
  este connector", "sumá un servidor MCP", o cuando .cs-project.md tenga casos de uso
  clasificados como Tool sin YAML generado todavía.
---

# Tools and Connectors Catalog

Cuarta skill del ciclo. Toma los casos de uso que `behavior-spec-writer` clasificó como
**Tool** y los convierte en componentes ejecutables reales bajo `capabilities/tools/`.

## Paso 0 — Gate

```bash
python skills/agent-intake/scripts/validate_cs_project.py .cs-project.md --require "Casos de uso relevados"
```

Confirmá también que `settings.mcs.yml` exista (lo crea `behavior-spec-writer`). Si no existe,
derivá ahí primero.

## Regla de oro — nunca inventar datos de conector

Esta es la restricción más importante de la skill: un `ConnectorTool` necesita
`connectorId`, `operationId`, `authMode` y `connectionReference` **exactos** — no aproximados,
no "parece que sería este". Si no tenés esos cuatro datos confirmados para un caso de uso, no
generes el YAML todavía. Las formas válidas de conseguirlos:

1. El usuario los pasa directo (ya sabe el connector y la operación).
2. Buscás en la documentación oficial del conector (Microsoft Learn) el `connectorId`
   (`/providers/Microsoft.PowerApps/apis/shared_<nombre>`) y el `operationId` válido para la
   acción que el caso de uso necesita.
3. Si hace falta una `connectionReference` nueva y no existe una conexión activa en el
   environment, decíselo al usuario explícitamente: tiene que crearla en Power Apps/Power
   Automate para ese connector antes de que el Tool pueda funcionar en runtime. No inventes un
   logical name de conexión que no verificaste.

## YAML — Connector Tool (dato confirmado)

`capabilities/tools/<nombre-slug>_<id>.mcs.yml`:

```yaml
mcs.metadata:
  componentName: <Nombre de la acción, en lenguaje de negocio>
  description: <una línea: qué hace y cuándo el agente debería usarla>
kind: ConnectorTool
authMode: <Invoker | otro según el conector>
connectionReference: <schemaName>.cr.<connector>
connectorId: /providers/Microsoft.PowerApps/apis/shared_<connector>
operationId: <OperationId exacto>
toolInputs:
  - name: <nombre del input>
    value:
      kind: ValueReference
      type: "{\"type\":\"string\"}"
      defaultValue: "\"<valor de ejemplo si aplica>\""
```

La `description` importa mucho más acá que en un flujo clásico — el orquestador del agente
agentic-loop decide cuándo llamar cada Tool basándose en esta descripción, no en un trigger
explícito. Escribila específica, no genérica ("Consulta el saldo de una cuenta bancaria dado
el número de cuenta", no "Herramienta de consulta").

## Agent Flows / Power Automate

Si el Tool es un Agent Flow o flow de Power Automate ya existente, se representa como
`WorkflowTool` (no `ConnectorTool`). Necesitás el `flowId` del flow real — mismo criterio: sin
dato confirmado, no lo generes. Si el flow todavía no existe, avisale al usuario que primero
hay que crearlo (fuera del alcance de esta skill) antes de poder referenciarlo acá.

## MCP servers e IQ connectors — gap de investigación abierto

A diferencia del `ConnectorTool`, **todavía no confirmamos el schema YAML exacto** que usa un
workspace CLI-authored para representar un servidor MCP o un conector IQ (Foundry IQ, Fabric
IQ, Work IQ) dentro de `capabilities/tools/`. Lo que sabemos con certeza (de la documentación
oficial) es cómo se agregan desde el portal — pestaña Tools → "Add a tool" → Model Context
Protocol / Foundry IQ / Fabric IQ / Work IQ, con su propio wizard de auth (None / API key /
OAuth 2.0 para MCP; tipos específicos por IQ connector) — pero no cómo se ve eso serializado en
un archivo `.mcs.yml` local.

Mientras no lo verifiquemos contra un `pac copilot clone` real de un agente con un MCP/IQ tool
ya conectado:

1. No inventes el YAML para estos casos.
2. Documentá el requerimiento en `.cs-project.md` (qué servidor MCP o IQ connector hace
   falta, y para qué caso de uso) como pendiente de implementación manual.
3. Avisale al usuario que, por ahora, este tipo de Tool se agrega manualmente desde el portal
   de Copilot Studio (pestaña Tools) hasta que confirmemos el formato de archivo.
4. Nota para vos mismo/a como skill: la próxima vez que alguien corra un `pac copilot clone`
   sobre un agente real con un MCP o IQ tool conectado, es la oportunidad de inspeccionar el
   YAML resultante y cerrar este gap actualizando esta sección.

Nota sobre Foundry IQ / Fabric IQ específicamente: según la documentación, estas dos requieren
el harness "GitHub Copilot" en su variante más nueva (a veces referida como agentes creados
con el "GitHub Copilot harness" en su experiencia más reciente) — si el agente quedó
inicializado con `pac copilot init --authoring-mode cli-copilot` sin más detalle, confirmá con
el usuario que la variante de harness soporta estos dos conectores antes de prometerlos.

## Convención de nombres

Slug del nombre + sufijo corto único, igual que el resto de los componentes `.mcs.yml`. Al
editar un Tool existente, conservá el sufijo generado.

## Restricciones

- Nunca inventes `connectorId`, `operationId`, `flowId`, ni `connectionReference`.
- No generes YAML para MCP/IQ tools hasta cerrar el gap de investigación de arriba.
- No dupliques un Tool que ya cubre lo mismo que otro existente — revisá `capabilities/tools/`
  antes de crear uno nuevo.

## Actualizar `.cs-project.md`

Para cada Tool generado, marcá la fila correspondiente en `Casos de uso relevados` como
resuelta con el path del `.mcs.yml`. Para los casos MCP/IQ bloqueados por el gap, marcalos
explícitamente como "pendiente — requiere alta manual en portal" en vez de dejarlos ambiguos.

## Al finalizar

Resumí cuántos Tools quedaron creados, cuáles quedaron bloqueados por falta de datos de
conector, y cuáles quedaron pendientes de alta manual por el gap de MCP/IQ.
