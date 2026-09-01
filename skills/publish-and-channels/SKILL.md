---
name: publish-and-channels
description: >
  Publica un Agente de Microsoft Copilot Studio (GitHub Copilot harness) sincronizando el
  workspace local con Dataverse y activando la versión publicada, vía pac copilot push +
  pac copilot publish. Documenta la configuración de canales (Teams, Web, Omnichannel/D365
  Contact Center) y autenticación Entra ID como paso manual en el portal, porque no hay
  comando CLI equivalente confirmado. Usar después de que knowledge-source-catalog,
  tools-and-connectors-catalog y skill-procedure-designer terminaron, cuando el usuario diga
  "publicá el agente", "subí los cambios a Dataverse", "activá el agente en Teams", o similar.
---

# Publish and Channels

Sexta skill del ciclo. Sincroniza el workspace local (YAML escrito por las skills 2-5) con el
agente real en Dataverse, publica la versión, y guía la configuración de canales.

## Paso 0 — Gate

```bash
python skills/agent-intake/scripts/validate_cs_project.py .cs-project.md --require "Casos de uso relevados"
```

Además, recorré la tabla `Casos de uso relevados` de `.cs-project.md`: si hay filas sin
resolver (sin un `.mcs.yml` generado ni marcadas explícitamente como "pendiente"), avisale al
usuario antes de publicar — publicar un agente a medio construir sin que el usuario lo sepa es
peor que preguntar antes.

## Paso 1 — Sincronizar el workspace con Dataverse

```bash
pac copilot push --project-dir <workspace>
```

Esto sube los cambios locales (`settings.mcs.yml`, `capabilities/`, `behaviors/`) al agente en
el environment configurado en `.cs-project.md`. Si `push` reporta un conflicto (el agente
cambió en el servidor desde el último `pull`), no lo fuerces — corré `pac copilot pull`
primero, resolvé el conflicto con el usuario, y reintentá el push.

Si `push` reporta que no hay cambios ("no local changes"), avisale al usuario — puede que ya
estuviera todo sincronizado, o que falte correr alguna de las skills 2-5 antes.

## Paso 2 — Publicar la versión

```bash
pac copilot publish --bot <schema-name-o-id> --environment <environment-id>
```

Esto activa la última versión subida para los usuarios del agente. Confirmá con el usuario que
quiere publicar ahora (no es una acción silenciosa — afecta a quien ya esté usando el agente
en producción) antes de correrlo, salvo que ya haya dado esa confirmación explícita al pedir
la publicación.

## Paso 3 — Canales — gap de investigación, paso manual

No encontramos un comando `pac copilot` que configure canales (Teams, Web, Omnichannel/D365
Contact Center) ni autenticación de canal — esa configuración vive en el portal de Copilot
Studio, pestaña **Channels**. Guiá al usuario ahí en vez de prometer que esta skill lo hace
automáticamente:

1. **Teams / Microsoft 365 Copilot**: pestaña Channels → "Microsoft Teams & Microsoft 365
   Copilot" → Add channel. Requiere elegir método de autenticación (Entra ID recomendado sobre
   "No authentication" para uso interno) y, para hacerlo visible a toda la organización,
   aprobación del admin de Teams.
2. **Web (Bot Framework Web Chat)**: canal por defecto al crear el agente; confirmar la
   versión de Adaptive Cards soportada si el agente usó alguna (recordá: este harness no usa
   Adaptive Cards, así que este punto normalmente no aplica).
3. **Omnichannel for Customer Service / D365 Contact Center**: requiere licencia de Omnichannel
   y configuración del lado de D365 Customer Service — fuera del alcance de este plugin;
   coordinar con la implementación de D365 CE si Axxon la está llevando en paralelo.

Si en el futuro se confirma un mecanismo vía API/CLI para canales, actualizá esta sección en
vez de seguir tratando el paso como manual por default.

## Cruce con Restricciones conocidas

Antes de guiar la configuración de autenticación de canal, revisá
`.cs-project.md > Restricciones conocidas > Seguridad / Autenticación` — si el cliente ya
definió requisitos de Entra ID específicos (roles, on-behalf-of), asegurate de que la
configuración de canal los respete en vez de sugerir "No authentication" por default.

## Actualizar `.cs-project.md`

Registrá en `## Historial de cambios` la fecha de publicación y qué canales quedaron
configurados (o pendientes, con el paso manual que falta).

## Al finalizar

Confirmá qué se publicó y qué canales quedaron activos vs. pendientes de configuración manual.
Si todo quedó resuelto, sugerí `agent-alm` para versionar formalmente la solución antes de
promover a TEST/PROD si el cliente tiene más de un environment.
