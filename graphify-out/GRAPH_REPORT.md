# Graph Report - .  (2026-05-18)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 26 nodes · 86 edges · 3 communities
- Extraction: 95% EXTRACTED · 5% INFERRED · 0% AMBIGUOUS · INFERRED: 4 edges (avg confidence: 0.9)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `385ca404`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- [[_COMMUNITY_Community 0|Community 0]]
- [[_COMMUNITY_Community 1|Community 1]]
- [[_COMMUNITY_Community 2|Community 2]]

## God Nodes (most connected - your core abstractions)
1. `Princípios Gerais` - 15 edges
2. `Vogel Stack README` - 14 edges
3. `Documentação e Versionamento` - 13 edges
4. `Registro e Evidências Operacionais` - 13 edges
5. `Templates de Documentação` - 13 edges
6. `Operação de Agentes` - 12 edges
7. `Graphify Knowledge Graph Tool` - 10 edges
8. `Quickstart Vogel Stack Graphify` - 8 edges
9. `Evolução de Produto e Arquitetura` - 8 edges
10. `Knowledge Graph` - 8 edges

## Surprising Connections (you probably didn't know these)
- `Quickstart Vogel Stack Graphify` --references--> `Princípios Gerais`  [EXTRACTED]
  quickstart.md → vogel-stack/principios.md
- `Quickstart Vogel Stack Graphify` --references--> `Documentação e Versionamento`  [EXTRACTED]
  quickstart.md → vogel-stack/documentacao-e-versionamento.md
- `Quickstart Vogel Stack Graphify` --references--> `Evolução de Produto e Arquitetura`  [EXTRACTED]
  quickstart.md → vogel-stack/evolucao-produto.md
- `Quickstart Vogel Stack Graphify` --references--> `Templates de Documentação`  [EXTRACTED]
  quickstart.md → vogel-stack/templates.md
- `Community 10` --references--> `Princípios Gerais`  [EXTRACTED]
  _COMMUNITY_Community 10.md → vogel-stack/principios.md

## Communities (3 total, 0 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.47
Nodes (9): AGENTS.md Document Pattern, Identificadores Canônicos, Manifesto por Run, Observabilidade e Logs, Pasta docs/raw e intake, Registry de Execuções, Documentação e Versionamento, Princípios Gerais (+1 more)

### Community 1 - "Community 1"
Cohesion: 0.56
Nodes (7): Google AI Studio API Key, Graphify Knowledge Graph Tool, Knowledge Graph, Regra de Juros Compostos, Quickstart Vogel Stack Graphify, Operação de Agentes, Registro e Evidências Operacionais

### Community 2 - "Community 2"
Cohesion: 0.43
Nodes (8): Community 10, Community 7, Handoff Padrão de Execução, Método Brainstorm-Concepção-Wireframe-Implementação, PowerShell Logging Pattern, Vogel Stack, Evolução de Produto e Arquitetura, Templates de Documentação

## Knowledge Gaps
- **2 isolated node(s):** `Observabilidade e Logs`, `Vogel Stack`
  These have ≤1 connection - possible missing edges or undocumented components.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Princípios Gerais` connect `Community 0` to `Community 1`, `Community 2`?**
  _High betweenness centrality (0.206) - this node is a cross-community bridge._
- **Why does `Templates de Documentação` connect `Community 2` to `Community 0`, `Community 1`?**
  _High betweenness centrality (0.195) - this node is a cross-community bridge._
- **Why does `Vogel Stack README` connect `Community 0` to `Community 1`, `Community 2`?**
  _High betweenness centrality (0.121) - this node is a cross-community bridge._
- **What connects `Observabilidade e Logs`, `Vogel Stack` to the rest of the system?**
  _2 weakly-connected nodes found - possible documentation gaps or missing edges._