# Axxon Copilot Studio Builder

Plugin de Axxon Consulting para acompañar el ciclo completo de construcción de un **Agente en Microsoft Copilot Studio** — desde el intake de casos de uso hasta la publicación y el ALM de la solución.

Es un plugin **independiente** del resto de la suite Axxon (`axxon-dataverse-architect`, `axxon-fde-agent`, `axxon-sprint0-suite`, etc.) — cubre específicamente la capa de diseño y construcción del agente en sí, no el backend de Dataverse ni la etapa de pre-venta/discovery.

## Decisiones de arquitectura

- **Harness: GitHub Copilot** (modelo agentic-loop), no el standard harness clásico de Topics. Se eligió porque es donde Microsoft invierte el tooling nuevo (`pac copilot`, Foundry IQ, Fabric IQ, Work IQ) — ver `skills/agent-intake/SKILL.md` para el detalle de la decisión y sus trade-offs.
- **Consecuencia directa**: en este harness no existen Topics determinísticos, variables globales/de Topic, Power Fx, ni **Adaptive Cards** (confirmado contra la documentación oficial — Adaptive Cards es una feature exclusiva del standard harness). Todo requerimiento se clasifica en cuatro cajones: **Instructions / Knowledge / Tools / Skills**.
- **Generación de YAML propia, no delegada.** Evaluamos depender de **`mcs-assistant`** (repo [`microsoft/copilot-studio-plugin`](https://github.com/microsoft/copilot-studio-plugin)), el toolkit experimental del equipo Microsoft Copilot Studio CAT para este harness, pero **su único flujo (`/migrate`) es de migración de un agente clásico existente al modelo nuevo** — no cubre construcción desde cero, que es nuestro caso de uso principal. Decisión: las skills de este plugin generan el YAML directamente, adaptando (con crédito, sin copiar literal) la metodología de clasificación de `copilot-studio-architect.md` de ese repo — el árbol de decisión Instructions/Knowledge/Tools/Skills y el schema de carpetas (`settings.mcs.yml`, `capabilities/knowledge/`, `capabilities/tools/`, `behaviors/`). La sincronización con Dataverse sigue siendo vía `pac copilot init/clone/pull/push`, que es independiente de `mcs-assistant`.
- **`mcs-assistant` queda como dependencia opcional futura**, solo para el día en que un cliente pida migrar un bot clásico existente (fuera del alcance actual de este plugin).

## Catálogo de skills

| # | Skill | Alcance |
|---|-------|---------|
| 0 | `csb-orchestrator` | Punto de entrada. Detecta en qué etapa del ciclo está el pedido y delega. Mantiene `.cs-project.md`. |
| 1 | `agent-intake` | Objetivo, audiencia, canal destino, casos de uso y fuentes de referencia (RFP, notas, transcripciones, matrices). Genera `.cs-project.md`. |
| 2 | `behavior-spec-writer` | Clasifica cada caso de uso en Instruction/Knowledge/Tool/Skill (metodología adaptada de `copilot-studio-architect.md`) y escribe `settings.mcs.yml` con las instructions. *(pendiente)* |
| 3 | `knowledge-source-catalog` | Releva SharePoint/Dataverse/archivos con clasificación FSI y escribe los YAML bajo `capabilities/knowledge/`. *(pendiente)* |
| 4 | `tools-and-connectors-catalog` | Junta con el cliente los datos concretos (connector ID, operation ID, auth mode) y escribe los YAML bajo `capabilities/tools/` — conectores estándar/custom, Power Automate, MCP, IQ connectors. *(pendiente)* |
| 5 | `skill-procedure-designer` | Identifica qué casos de uso son procedimiento reusable (Skill) vs. instrucción global vs. tool call directo, y escribe los YAML bajo `behaviors/`. *(pendiente)* |
| 6 | `publish-and-channels` | Teams, Web, Omnichannel/D365 Contact Center, autenticación Entra ID — vía `pac copilot push` + publicación de canal. *(pendiente)* |
| 7 | `agent-alm` | Versionado de solución, promoción DEV→TEST→PROD con gate de aprobación, sobre `settings.mcs.yml`/`capabilities/`/`.mcs/`. *(pendiente)* |

## Convenciones

- Español, con terminología técnica de Copilot Studio en inglés (Instructions, Knowledge, Tools, Skills).
- Contexto persistente en `.cs-project.md` en la raíz del workspace del cliente — todas las skills lo leen antes de trabajar.
- Ninguna skill downstream trabaja sin que `agent-intake` haya pasado el gate estructural mínimo (ver `skills/agent-intake/SKILL.md`).
- El deploy DEV→TEST→PROD (`agent-alm`) sigue el mismo principio de gate de aprobación humana que `solution-packager` en `axxon-dataverse-architect` — nunca automático.
