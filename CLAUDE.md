# Vogel Stack — Instruções para Agentes

Vogel Stack é um conjunto de documentos-base para projetos que usam agentes de IA como parte real do fluxo. Os documentos canônicos da stack estão em `vogel-stack/` (pasta interna deste repositório).

## Documentos canônicos

- [[vogel-stack/principios|Princípios Gerais]]
- [[vogel-stack/documentacao-e-versionamento|Documentação e Versionamento]]
- [[vogel-stack/operacao-agentes|Operação de Agentes]]
- [[vogel-stack/registro-e-evidencias|Registro e Evidências Operacionais]]
- [[vogel-stack/evolucao-produto|Evolução de Produto e Arquitetura]]
- [[vogel-stack/templates|Templates de Documentação]]
- [[vogel-stack/operacao-leve|Operação Leve (alternativa sem Graphify)]]

## Como projetos consomem a Vogel Stack

A stack é geralmente instalada como submódulo em `vogel-stack/` no projeto-alvo. Wikilinks no projeto-alvo apontam para `[[vogel-stack/vogel-stack/<doc>]]`.

Cada projeto declara qual **família de operação documental** adota:

- **Padrão (Codex-led + Graphify-assisted)** — descrita em [[quickstart]]. Usa Graphify para materializar knowledge graph em `graphify-out/` e Obsidian como camada de visualização. Indicada para projetos com ≥ ~80 docs, material bruto extenso, agentes externos frios.
- **Leve (wikilinks + link checker + agente sob demanda)** — descrita em [[vogel-stack/operacao-leve]]. Sem Graphify, sem Obsidian versionado. Indicada para projetos pequenos com agente forte (Claude Code Max, Codex pago) constantemente disponível.

A escolha é **declarada explicitamente** pelo projeto, em coerência com o princípio nº 19 ([[vogel-stack/principios|Problema, não tecnologia]]) e nº 11 ([[vogel-stack/principios|Modos de execução suportados devem ser explícitos]]).

## Regras quando o projeto adota o caminho padrão

Quando este repositório (ou um projeto que usa a stack) opera no caminho padrão com Graphify:

- Antes de ler arquivos-fonte, fazer grep/glob ou responder perguntas estruturais do repo, ler `graphify-out/GRAPH_REPORT.md`.
- Artefatos esperados em `graphify-out/`: `GRAPH_REPORT.md`, `graph.json`, `graph.html`, `manifest.json`.
- Para perguntas cross-módulo "como X se relaciona com Y", preferir `graphify query "<pergunta>"`, `graphify path "<A>" "<B>"`, `graphify explain "<conceito>"` em vez de grep cego. Esses comandos atravessam edges extraídas + inferidas.
- Se `GRAPH_REPORT.md` está ausente mas `graph.json` existe, rodar `graphify cluster-only .` para regenerar relatório e visualização sem custo de LLM.
- Após code-only changes, rodar `graphify update .` (sem custo LLM). Após documentação ou mudanças de knowledge graph, rodar `graphify extract .` com API key disponível e commitar `graphify-out/` atualizado.

## Regras quando o projeto adota o caminho leve

Quando o projeto declara o caminho leve em ADR próprio (referenciando [[vogel-stack/operacao-leve]]):

- Entrar pelo `docs/contexto.md` (síntese) e `docs/README.md` (hub humano curado).
- **Não** procurar `graphify-out/` — ele não existe nesse caminho.
- Para auditoria estrutural (órfão, weak link, comunidade), o agente é invocado explicitamente com escopo claro pelo humano ou por outro agente. Ver prompt-template em [[vogel-stack/operacao-leve]].
- Antes de fechar rodada que tocou em arquivos `.md`, rodar `pwsh ./scripts/check-wikilinks.ps1` (ou aguardar GitHub Action equivalente).

## Em qualquer caminho

- Documentos novos nascem **já conectados** via wikilinks reais (princípio nº 18). Sem links decorativos.
- Wikilinks usam sintaxe Obsidian: `[[caminho/sem/extensao]]` ou `[[caminho|alias]]`.
- Quando este repositório for atualizado, os projetos que o consomem como submódulo recebem o upgrade via `git submodule update --remote --merge vogel-stack`.
