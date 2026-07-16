# ADR 0001 — Adotar operação documental leve neste repositório

- **Status:** Aceito — a dualidade de famílias que motivou esta escolha foi removida pelo [[0002-remover-familia-padrao|ADR 0002]] (2026-07-16). A operação adotada aqui continua valendo: deixou de ser "uma família entre duas" e passou a ser a via única da stack.
- **Data:** 2026-06-12
- **Decisor:** LuisVogelDS
- **Princípios aplicáveis:** nº 19 ([[vogel-stack/principios|Problema, não tecnologia]]) e nº 11 ([[vogel-stack/principios|Modos de execução suportados devem ser explícitos]])

## Contexto

Este repositório (a própria Vogel Stack) operava de fato no **caminho padrão (Codex-led + Graphify-assisted)**: mantinha `graphify-out/` versionado, `.obsidian/` versionado, uma regra `always_on` e hooks (Claude e Codex) que mandavam todo agente ler `graphify-out/GRAPH_REPORT.md` antes de responder.

Esse aparato estava **desatualizado e incoerente**:

- Os artefatos de `graphify-out/` estavam congelados em 2026-05-18 — anteriores à reformulação de 2026-05-28 que rebaixou o Graphify de default obrigatório para uma de duas famílias. O grafo materializado nem conhecia o `operacao-leve.md` nem o princípio nº 19.
- O perfil deste repositório é o caso-escola da família leve: ~12 documentos `.md` (muito abaixo do limiar de ~80), agente forte sempre disponível e alta volatilidade documental (a stack está em evolução constante).
- Manter `graphify-out/` versionado feria o princípio nº 1 ([[vogel-stack/principios|comportamento documentado reflete o sistema real]]): o `GRAPH_REPORT.md` commitado descrevia um estado que não existia mais.

## Decisão

Adotar a **família leve** ([[vogel-stack/operacao-leve|Operação Leve]]) para este repositório.

Substituições problema-a-problema:

| Problema | Antes (padrão) | Agora (leve) |
|---|---|---|
| Sumário canônico para agente | `graphify-out/GRAPH_REPORT.md` | `CLAUDE.md`/`AGENTS.md` + [[vogel-stack/README|README da stack]] |
| Detecção de link quebrado | implícito no fluxo Graphify | `scripts/check-wikilinks.ps1` + Action `check-malha` |
| Visualização do grafo | `graph.html` + Obsidian versionado | Obsidian local não-versionado (`.gitignore`) |
| Auditoria estrutural | `graphify cluster-only` | agente sob demanda (prompt-template em [[vogel-stack/operacao-leve]]) |

## Consequências

- Removidos do versionamento: `graphify-out/`, `.obsidian/`, `.agents/rules/graphify.md`, `.agents/workflows/graphify.md`. Hooks de Graphify em `.claude/settings.json` e `.codex/hooks.json` esvaziados. `graphify-out/` e `.obsidian/` adicionados ao `.gitignore`.
- 61 ocorrências de wikilink (13 conceitos órfãos da era Graphify, sem arquivo) foram resolvidas: religadas a documentos/seções canônicas onde havia casa real, ou delinkadas para texto onde não havia.
- Não há mais `GRAPH_REPORT.md`: auditoria estrutural passa a ser pedido explícito a um agente.
- Perde-se a visualização interativa "para todos" e as edges inferidas — aceitável dado o perfil do repositório.

## Gatilhos para reabrir (voltar ao caminho padrão)

Reavaliar quando qualquer um disparar (ver gatilhos detalhados em [[vogel-stack/operacao-leve|Operação Leve]]):

1. Volume cruzar ~80 docs ou ~500KB de markdown.
2. Surgir `docs/raw/` ou `intake/` com material bruto extenso.
3. Múltiplos agentes externos passarem a consumir o repo sem contexto carregado.
4. Auditoria estrutural virar pedido frequente o suficiente para justificar o custo de regeneração.

Reverter é trivial: rodar `graphify extract .` uma vez, remover `graphify-out/` do `.gitignore` e reativar a regra original.
