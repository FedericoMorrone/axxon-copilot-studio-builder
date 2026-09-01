# Axxon Copilot Studio Builder

Plugin de Axxon Consulting para acompañar el ciclo completo de construcción de un **Agente en Microsoft Copilot Studio** — desde el intake de casos de uso hasta la publicación y el ALM de la solución.

Es un plugin **independiente** del resto de la suite Axxon (`axxon-dataverse-architect`, `axxon-fde-agent`, `axxon-sprint0-suite`, etc.) — cubre específicamente la capa de diseño conversacional y construcción del agente en sí, no el backend de Dataverse ni la etapa de pre-venta/discovery.

## Catálogo de skills

| # | Skill | Alcance |
|---|-------|---------|
| 0 | `csb-orchestrator` | Punto de entrada. Detecta en qué etapa del ciclo está el pedido y delega. Mantiene `.cs-project.md`. |
| 1 | `agent-intake` | Objetivo, audiencia, canal destino, casos de uso y fuentes de referencia (RFP, notas, transcripciones, matrices). Genera `.cs-project.md`. |
| 2 | `topic-designer` | Topics clásicos: trigger phrases, conversation nodes, entities/variables. *(pendiente)* |
| 3 | `knowledge-connector` | Generative Answers / Knowledge (SharePoint, Dataverse, archivos, sitios públicos). *(pendiente)* |
| 4 | `tools-and-connectors-builder` | Conectores estándar/custom, Power Automate, Dataverse actions/Custom APIs, servidores MCP, conectores IQ (Foundry IQ, Fabric IQ, Work IQ). *(pendiente)* |
| 5 | `agent-flow-designer` | Agent Flows determinísticos. *(pendiente)* |
| 6 | `adaptive-card-builder` | Tarjetas de respuesta (restricciones de compatibilidad con Copilot Studio). *(pendiente)* |
| 7 | `publish-and-channels` | Teams, Web, Omnichannel/D365 Contact Center, autenticación Entra ID. *(pendiente)* |
| 8 | `agent-alm` | Versionado de solución, promoción DEV→TEST→PROD con gate de aprobación. *(pendiente)* |

## Convenciones

- Español, con terminología técnica de Copilot Studio en inglés (Topics, Knowledge, Tools, Agent Flows, Adaptive Cards).
- Contexto persistente en `.cs-project.md` en la raíz del workspace del cliente — todas las skills lo leen antes de trabajar.
- Ninguna skill downstream trabaja sin que `agent-intake` haya pasado el gate estructural mínimo (ver `skills/agent-intake/SKILL.md`).
- El deploy DEV→TEST→PROD (`agent-alm`) sigue el mismo principio de gate de aprobación humana que `solution-packager` en `axxon-dataverse-architect` — nunca automático.
