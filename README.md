# Axxon Copilot Studio Builder

Plugin de Axxon Consulting para acompañar el ciclo completo de construcción de un **Agente en Microsoft Copilot Studio** — desde el intake de casos de uso hasta la publicación y el ALM de la solución.

Es un plugin **independiente** del resto de la suite Axxon (`axxon-dataverse-architect`, `axxon-fde-agent`, `axxon-sprint0-suite`, etc.) — cubre específicamente la capa de diseño y construcción del agente en sí, no el backend de Dataverse ni la etapa de pre-venta/discovery.

## Decisiones de arquitectura

- **Harness: GitHub Copilot** (modelo agentic-loop), no el standard harness clásico de Topics. Se eligió porque es donde Microsoft invierte el tooling nuevo (`pac copilot`, Foundry IQ, Fabric IQ, Work IQ) — ver `skills/agent-intake/SKILL.md` para el detalle de la decisión y sus trade-offs.
- **Consecuencia directa**: en este harness no existen Topics determinísticos, variables globales/de Topic, Power Fx, ni **Adaptive Cards** (confirmado contra la documentación oficial — Adaptive Cards es una feature exclusiva del standard harness). Todo requerimiento se clasifica en cuatro cajones: **Instructions / Knowledge / Tools / Skills**.
- **Generación de YAML delegada, no propia**: este plugin no reimplementa la lógica de clasificación ni el schema YAML del agente. Depende de **`mcs-assistant`** (repo [`microsoft/copilot-studio-plugin`](https://github.com/microsoft/copilot-studio-plugin)), el toolkit experimental del equipo Microsoft Copilot Studio CAT para ese harness. Las skills de Axxon preparan el input (casos de uso, fuentes, restricciones) que el `copilot-studio-architect` de `mcs-assistant` necesita para no inventar nada, y dejan el ALM/gobernanza encima.

### Prerequisito de instalación

```
/plugin marketplace add microsoft/copilot-studio-plugin
/plugin install mcs-assistant@copilot-studio-plugin
```

Sin `mcs-assistant` instalado, las skills de las etapas 2 a 5 (ver catálogo) no pueden generar YAML real — deben avisarlo explícitamente en vez de improvisar.

## Catálogo de skills

| # | Skill | Alcance |
|---|-------|---------|
| 0 | `csb-orchestrator` | Punto de entrada. Detecta en qué etapa del ciclo está el pedido y delega. Mantiene `.cs-project.md`. |
| 1 | `agent-intake` | Objetivo, audiencia, canal destino, casos de uso y fuentes de referencia (RFP, notas, transcripciones, matrices). Genera `.cs-project.md`. |
| 2 | `behavior-spec-writer` | Convierte los casos de uso relevados en la "detailed behavior description" que exige `copilot-studio-architect` como input — no genera YAML, prepara el brief. *(pendiente)* |
| 3 | `knowledge-source-catalog` | Releva SharePoint/Dataverse/archivos con clasificación FSI y se lo entrega al architect, que decide si es Knowledge o en realidad Tool+Skill. *(pendiente)* |
| 4 | `tools-and-connectors-catalog` | Junta con el cliente los datos concretos (connector ID, operation ID, auth mode) que el architect exige completos antes de crear un Tool — conectores estándar/custom, Power Automate, MCP, IQ connectors. *(pendiente)* |
| 5 | `skill-procedure-designer` | Identifica qué casos de uso son procedimiento reusable (Skill) vs. instrucción global vs. tool call directo, usando el mismo árbol de decisión del architect. *(pendiente)* |
| 6 | `publish-and-channels` | Teams, Web, Omnichannel/D365 Contact Center, autenticación Entra ID — dispara `copilot-studio-manage` de mcs-assistant. *(pendiente)* |
| 7 | `agent-alm` | Versionado de solución, promoción DEV→TEST→PROD con gate de aprobación, sobre `settings.mcs.yml`/`capabilities/`/`.mcs/`. *(pendiente)* |

## Convenciones

- Español, con terminología técnica de Copilot Studio en inglés (Instructions, Knowledge, Tools, Skills).
- Contexto persistente en `.cs-project.md` en la raíz del workspace del cliente — todas las skills lo leen antes de trabajar.
- Ninguna skill downstream trabaja sin que `agent-intake` haya pasado el gate estructural mínimo (ver `skills/agent-intake/SKILL.md`).
- El deploy DEV→TEST→PROD (`agent-alm`) sigue el mismo principio de gate de aprobación humana que `solution-packager` en `axxon-dataverse-architect` — nunca automático.
