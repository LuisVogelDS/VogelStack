# Graph Report - .  (2026-05-18)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 26 nodes · 92 edges · 4 communities
- Extraction: 96% EXTRACTED · 4% INFERRED · 0% AMBIGUOUS · INFERRED: 4 edges (avg confidence: 0.9)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `8abea06f`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- [[_COMMUNITY_Community 0|Community 0]]
- [[_COMMUNITY_Community 1|Community 1]]
- [[_COMMUNITY_Community 2|Community 2]]
- [[_COMMUNITY_Community 3|Community 3]]

## God Nodes (most connected - your core abstractions)
1. `Princípios Gerais` - 17 edges
2. `Documentação e Versionamento` - 15 edges
3. `Vogel Stack README` - 15 edges
4. `Operação de Agentes` - 14 edges
5. `Registro e Evidências Operacionais` - 14 edges
6. `Templates de Documentação` - 13 edges
7. `Knowledge Graph` - 9 edges
8. `Evolução de Produto e Arquitetura` - 8 edges
9. `Graphify Knowledge Graph Tool` - 8 edges
10. `Quickstart Vogel Stack Graphify` - 7 edges

## Surprising Connections (you probably didn't know these)
- `Quickstart Vogel Stack Graphify` --references--> `Documentação e Versionamento`  [EXTRACTED]
  quickstart.md → vogel-stack/documentacao-e-versionamento.md
- `Quickstart Vogel Stack Graphify` --references--> `Operação de Agentes`  [EXTRACTED]
  quickstart.md → vogel-stack/operacao-agentes.md
- `Quickstart Vogel Stack Graphify` --references--> `Evolução de Produto e Arquitetura`  [EXTRACTED]
  quickstart.md → vogel-stack/evolucao-produto.md
- `Quickstart Vogel Stack Graphify` --references--> `Templates de Documentação`  [EXTRACTED]
  quickstart.md → vogel-stack/templates.md
- `Community 10` --references--> `Princípios Gerais`  [EXTRACTED]
  _COMMUNITY_Community 10.md → vogel-stack/principios.md

## Communities (4 total, 0 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.53
Nodes (7): Graphify Knowledge Graph Tool, Knowledge Graph, Linkagem Semântica no Nascimento, Regra de Juros Compostos, Quickstart Vogel Stack Graphify, Princípios Gerais, Registro e Evidências Operacionais

### Community 1 - "Community 1"
Cohesion: 0.67
Nodes (6): Community 7, Handoff Padrão de Execução, Observabilidade e Logs, PowerShell Logging Pattern, Operação de Agentes, Vogel Stack README

### Community 2 - "Community 2"
Cohesion: 0.4
Nodes (6): AGENTS.md Document Pattern, Manifesto por Run, Pasta docs/raw e intake, Registry de Execuções, Vogel Stack, Documentação e Versionamento

### Community 3 - "Community 3"
Cohesion: 0.7
Nodes (5): Community 10, Identificadores Canônicos, Método Brainstorm-Concepção-Wireframe-Implementação, Evolução de Produto e Arquitetura, Templates de Documentação

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Princípios Gerais` connect `Community 0` to `Community 1`, `Community 2`, `Community 3`?**
  _High betweenness centrality (0.180) - this node is a cross-community bridge._
- **Why does `Templates de Documentação` connect `Community 3` to `Community 0`, `Community 1`, `Community 2`?**
  _High betweenness centrality (0.142) - this node is a cross-community bridge._
- **Why does `Documentação e Versionamento` connect `Community 2` to `Community 0`, `Community 1`, `Community 3`?**
  _High betweenness centrality (0.126) - this node is a cross-community bridge._