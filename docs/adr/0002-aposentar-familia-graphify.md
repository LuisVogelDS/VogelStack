# ADR 0002 — Aposentar a família "padrão (Graphify/Obsidian-assisted)"

**Status:** aceito · **Data:** 2026-06-28 · **Relacionado:** [[docs/adr/0001-adotar-operacao-leve|ADR 0001]]

## Contexto

A [[docs/adr/0001-adotar-operacao-leve|ADR 0001]] adotou o caminho leve para a própria Vogel Stack, mas **manteve a família "padrão (Codex-led + Graphify-assisted)" documentada** como opção para projetos consumidores (≥ ~80 docs, material bruto extenso, agentes externos frios).

Na prática, nenhum projeto consumidor usa mais Graphify ou Obsidian versionado, e manter duas famílias: (a) duplicava a orientação em ~13 arquivos; (b) reintroduzia, via "caminho padrão", a orientação a ferramentas que não são mais necessárias; (c) tensionava o próprio princípio nº 19 ("Problema, não tecnologia") ao sugerir ferramenta por convenção.

## Decisão

A Vogel Stack passa a ter **um único modelo de operação documental** (o antigo "leve"): wikilinks curados + link checker determinístico + auditoria por agente sob demanda. A família "padrão (Graphify/Obsidian-assisted)" é **aposentada** — a stack não orienta mais o uso de Graphify nem de Obsidian versionado.

- `vogel-stack/operacao-leve.md` reposicionado como **"Operação Documental"** (o modelo, não uma alternativa).
- `quickstart.md`, `CLAUDE.md`/`AGENTS.md`, `vogel-stack/README.md` e `vogel-stack/principios.md` reescritos para o modelo único; menções incidentais a Graphify/Knowledge Graph/“duas famílias” removidas dos docs canônicos.
- Graphify/Obsidian permanecem citados apenas como **exemplo do que NÃO adotar sem um problema real** (princípio nº 19) e como ferramentas **locais opcionais não-versionadas**.
- A sintaxe `[[wikilink]]` permanece como convenção de links da stack — **não requer o app Obsidian**.

## Consequências

- Documentação mais enxuta, sem a ambiguidade de "qual família".
- Projetos não declaram mais "família de operação" — há um só modelo.
- A receita de remoção de Graphify/Obsidian de projetos legados vira apêndice utilitário em [[vogel-stack/operacao-leve|Operação Documental]].

## Reverter

Se um projeto futuro precisar de mapa materializado para agentes frios em escala (≥ ~80 docs), pode adotar Graphify **localmente** e declarar isso em ADR próprio — mas isso é decisão do projeto, não orientação da stack.
