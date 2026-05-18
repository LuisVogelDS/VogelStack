## graphify

This project has a [[Graphify Knowledge Graph Tool|knowledge graph]] at graphify-out/ with god nodes, community structure, and cross-file relationships.

Core VogelStack links: [[vogel-stack/principios|Princípios Gerais]], [[vogel-stack/documentacao-e-versionamento|Documentação e Versionamento]], [[vogel-stack/operacao-agentes|Operação de Agentes]], [[vogel-stack/registro-e-evidencias|Registro e Evidências Operacionais]].

Rules:
- ALWAYS read `graphify-out/GRAPH_REPORT.md` before reading source files, running grep/glob searches, or answering codebase questions. The graph report is the primary map of this repository.
- Expected checked-in graph artifacts are `graphify-out/GRAPH_REPORT.md`, `graphify-out/graph.json`, `graphify-out/graph.html`, and `graphify-out/manifest.json`.
- `graphify-out/wiki/index.md` is not produced by the current local Graphify CLI; only use it if a future run explicitly creates that directory.
- For cross-module "how does X relate to Y" questions, prefer `graphify query "<question>"`, `graphify path "<A>" "<B>"`, or `graphify explain "<concept>"` over grep. These traverse the graph's EXTRACTED + INFERRED edges instead of scanning files.
- If `GRAPH_REPORT.md` is missing but `graph.json` exists, run `graphify cluster-only .` to regenerate `GRAPH_REPORT.md` and `graph.html` before continuing.
- After code-only changes, run `graphify update .` to keep the graph current without LLM cost. After documentation or knowledge-graph changes, run `graphify extract .` with an available LLM API key, then commit the refreshed `graphify-out/` artifacts.
