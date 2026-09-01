---
name: knowledge-source-catalog
description: >
  Releva y escribe las fuentes de Knowledge de un Agente de Microsoft Copilot Studio (GitHub
  Copilot harness) — SharePoint, Dataverse, archivos subidos, sitios públicos — con
  clasificación de sensibilidad FSI, y genera los YAML bajo capabilities/knowledge/. Usar
  después de `behavior-spec-writer`, cuando el usuario diga "agregá conocimiento de X",
  "conectá este SharePoint", "callá este documento como fuente", o cuando .cs-project.md tenga
  casos de uso clasificados como Knowledge sin YAML generado todavía.
---

# Knowledge Source Catalog

Tercera skill del ciclo. Toma los casos de uso que `behavior-spec-writer` clasificó como
**Knowledge** en `.cs-project.md` y los convierte en fuentes de conocimiento reales, con
dos responsabilidades separadas: relevar el dato concreto de la fuente (dónde vive, qué
contiene, quién puede verla) y escribir el YAML bajo `capabilities/knowledge/`.

## Paso 0 — Gate

```bash
python skills/agent-intake/scripts/validate_cs_project.py .cs-project.md --require "Casos de uso relevados"
```

Además del gate estándar, confirmá que `settings.mcs.yml` ya existe en el workspace (lo crea
`behavior-spec-writer` en su Paso 0.5) — sin eso no hay dónde colgar `capabilities/knowledge/`.
Si no existe, derivá a `behavior-spec-writer` primero; no lo inicialices vos.

## Qué casos tomás

Filtrá la tabla `Casos de uso relevados` de `.cs-project.md` por los que quedaron con
Componente candidato = **Knowledge**. Si no hay ninguno, decíselo al usuario y no generes
nada — no toda solución necesita Knowledge.

## Relevamiento por fuente — con clasificación FSI

Para cada caso, antes de escribir YAML, confirmá con el usuario (o extraeé de las Fuentes de
referencia si ya está documentado):

1. **Tipo de fuente**: SharePoint, sitio público, archivo subido (PDF/DOCX/XLSX), Dataverse.
2. **Ubicación concreta**: URL de sitio/carpeta de SharePoint, URL pública, o el archivo en sí.
3. **Clasificación de sensibilidad** — esto es lo que un cliente FSI va a auditar, no lo
   saltees:
   - **Pública**: sin restricción (ej. sitio institucional, políticas publicadas).
   - **Interna**: uso interno del cliente, no regulada explícitamente.
   - **Regulada**: contiene datos alcanzados por un marco específico (cruzá con
     `.cs-project.md > Restricciones conocidas > Compliance / Regulatorio` — ej. BCRA/UIF,
     datos personales de clientes). Si una fuente cae acá, no la conectes sin confirmación
     explícita del usuario de que está aprobado exponerla como grounding conversacional —
     preguntalo, no asumas que porque el documento existe se puede usar.
4. **Alcance de búsqueda esperado**: qué tipo de preguntas debe responder esta fuente (para la
   `description` del componente, que el orquestador del agente usa para decidir cuándo
   consultarla).

## YAML — fuente SharePoint

`capabilities/knowledge/<schemaName>.<NombreAmigable>_<id>.mcs.yml`:

```yaml
mcs.metadata:
  componentName: <Nombre amigable>
  description: <una línea: qué tipo de preguntas responde esta fuente>
kind: KnowledgeSourceConfiguration
source:
  kind: SharePointKnowledgeSource
  siteUrl: <URL completa del sitio/carpeta>
  additionalSearchTerms:
  targetKind: Folder
```

## YAML — archivo subido

Copiá el archivo real a `capabilities/knowledge/files/`, y creá el sidecar
`<nombre-archivo>.<ext>.mcs.yml` al lado:

```yaml
mcs.metadata:
  componentName: <nombre-archivo.ext>
  description: <una línea: qué información contiene este archivo>
```

No generes el sidecar si no tenés el archivo binario disponible — si el usuario solo
describió que "existe un documento con X" pero no lo adjuntó, documentá la intención en
`.cs-project.md` como gap abierto en vez de inventar un archivo vacío.

## Convención de nombres

Slug del nombre + sufijo corto único (ej. `politica-reembolsos_a1b2c3.mcs.yml`), igual que el
resto de los componentes `.mcs.yml` del agente. Si editás un componente ya existente,
conservá el sufijo generado, no lo cambies.

## Restricciones

- Nunca inventes una `siteUrl` o el contenido de un archivo — si el dato concreto no está
  confirmado, no generes el YAML todavía; dejá el caso de uso marcado como pendiente en
  `.cs-project.md` con una nota de qué dato falta.
- No dupliques como Knowledge algo que en realidad es una Skill que usa un documento como guía
  de procedimiento (ver el matiz Knowledge vs. Skill en `behavior-spec-writer/SKILL.md`) — si
  al relevar la fuente te das cuenta de que el caso no es búsqueda semántica sino guía paso a
  paso, avisale al usuario y derivá a `skill-procedure-designer` en vez de generar Knowledge.
- No apruebes vos solo/a una fuente regulada — esa confirmación es siempre del usuario.

## Actualizar `.cs-project.md`

Para cada Knowledge generado, marcá la fila correspondiente en `Casos de uso relevados` como
resuelta (agregá el path del archivo `.mcs.yml` generado en la columna Estado). Si quedó
alguna fuente regulada pendiente de aprobación, documentála explícitamente ahí también.

## Al finalizar

Resumí cuántas fuentes de Knowledge quedaron creadas, cuáles quedaron pendientes de
aprobación o de archivo, y recordá al usuario que `knowledge-source-catalog`,
`tools-and-connectors-catalog` y `skill-procedure-designer` no dependen entre sí — pueden
correr en el orden que el usuario prefiera.
