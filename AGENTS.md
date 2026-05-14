## graphify

This project has a [[Graphify Knowledge Graph Tool|knowledge graph]] at graphify-out/ with god nodes, community structure, and cross-file relationships.

Core VogelStack links: [[vogel-stack/principios|Princípios Gerais]], [[vogel-stack/documentacao-e-versionamento|Documentação e Versionamento]], [[vogel-stack/operacao-agentes|Operação de Agentes]], [[vogel-stack/registro-e-evidencias|Registro e Evidências Operacionais]].

Rules:
- ALWAYS read graphify-out/GRAPH_REPORT.md before reading any source files, running grep/glob searches, or answering codebase questions. The graph is your primary map of the codebase.
- IF graphify-out/wiki/index.md EXISTS, navigate it instead of reading raw files
- For cross-module "how does X relate to Y" questions, prefer `graphify query "<question>"`, `graphify path "<A>" "<B>"`, or `graphify explain "<concept>"` over grep — these traverse the graph's EXTRACTED + INFERRED edges instead of scanning files
- After modifying code, run `graphify update .` to keep the graph current (AST-only, no API cost).
