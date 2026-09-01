---
name: agent-alm
description: >
  Versiona y promueve la solución de un Agente de Microsoft Copilot Studio (GitHub Copilot
  harness) entre environments DEV→TEST→PROD, empaquetando el workspace con pac copilot pack
  y desplegando con pac solution import — siempre con gate de aprobación humana, nunca
  automático. Usar cuando el usuario diga "promové el agente a TEST", "empaquetá la solución",
  "prepará el deploy a PROD", o antes de cualquier promoción entre environments.
---

# Agent ALM

Séptima y última skill del ciclo de construcción. Convierte el workspace de archivos en una
solución de Dataverse versionada y gestiona su promoción entre environments, con el mismo
principio de gate humano que `solution-packager` en `axxon-dataverse-architect`: **nunca
importa directo a TEST/PROD** sin aprobación explícita.

## Paso 0 — Gate

```bash
python skills/agent-intake/scripts/validate_cs_project.py .cs-project.md --require "Casos de uso relevados"
```

Además, confirmá que `publish-and-channels` ya corrió al menos una vez sobre DEV (el agente
tiene que estar publicado y probado en el environment de desarrollo antes de empaquetarlo para
promoción) — si no, derivá ahí primero.

## Paso 1 — Empaquetar la solución

```bash
pac copilot pack \
  --publisher-prefix axx \
  --project-dir <workspace> \
  --output-path <carpeta-de-salida>
```

Esto es una operación **local**, sin autenticación ni environment — lee el workspace y escribe
un `.zip` de solución. Seguría para correr en cualquier momento, no muta nada en Dataverse.

## Paso 2 — Versionar

Antes de promover, confirmá con el usuario el número de versión de la solución (siguiendo la
convención de versionado que ya use el proyecto D365 del cliente, si Axxon también está
llevando esa implementación en paralelo con `axxon-dataverse-architect`). Registrá la versión
y la fecha de empaquetado en `.cs-project.md > Historial de cambios`.

## Paso 3 — Promoción — gate de aprobación humana obligatorio

**Nunca ejecutes `pac solution import` contra TEST o PROD sin que el usuario lo haya aprobado
explícitamente para esa promoción puntual** — no alcanza con que el usuario haya aprobado una
promoción anterior; cada import a TEST/PROD es una confirmación nueva.

1. **DEV → TEST**: mostrá al usuario qué cambió desde el último empaquetado (nuevos
   Knowledge/Tools/Skills, cambios de Instructions) y pedile confirmación explícita antes de
   correr:
   ```bash
   pac solution import --path <solucion.zip> --environment <environment-id-test>
   ```
2. **TEST → PROD**: mismo criterio, con un nivel extra de rigor — confirmá que el agente fue
   probado en TEST (pedile evidencia o confirmación al usuario, no lo asumas) antes de ofrecer
   el comando de import a PROD. Si el cliente tiene un pipeline de Azure DevOps ya armado para
   esto (como en `axxon-dataverse-architect`), preferilo sobre un `pac solution import` manual
   — preguntale al usuario si existe antes de sugerir el comando directo.

## Restricciones

- No promuevas nunca sin confirmación explícita del usuario para esa promoción puntual.
- No inventes un número de versión — confirmalo con el usuario.
- No mezcles este ALM con el de Dataverse general (`axxon-dataverse-architect:solution-
  packager`) — son soluciones distintas (una es el agente de Copilot Studio, otra puede ser el
  resto de la implementación D365 del mismo cliente) aunque compartan el mismo environment.

## Actualizar `.cs-project.md`

Registrá cada promoción en `## Historial de cambios`: versión, environment destino, fecha, y
quién aprobó.

## Al finalizar

Confirmá el estado final: en qué environment(s) quedó desplegado el agente y qué versión. Si
quedó pendiente la promoción a un environment superior, decíselo explícitamente en vez de dar
por cerrado el ciclo.
