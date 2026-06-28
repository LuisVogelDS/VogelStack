# Vogel Stack — Instruções para Agentes

Vogel Stack é um conjunto de documentos-base para projetos que usam agentes de IA como parte real do fluxo. Os documentos canônicos da stack estão em `vogel-stack/` (pasta interna deste repositório).

## Documentos canônicos

- [[vogel-stack/principios|Princípios Gerais]]
- [[vogel-stack/documentacao-e-versionamento|Documentação e Versionamento]]
- [[vogel-stack/operacao-agentes|Operação de Agentes]]
- [[vogel-stack/registro-e-evidencias|Registro e Evidências Operacionais]]
- [[vogel-stack/evolucao-produto|Evolução de Produto e Arquitetura]]
- [[vogel-stack/templates|Templates de Documentação]]
- [[vogel-stack/operacao-leve|Operação Documental (wikilinks + link checker + agente sob demanda)]]

## Como projetos consomem a Vogel Stack

A stack é geralmente instalada como submódulo em `vogel-stack/` no projeto-alvo. Wikilinks no projeto-alvo apontam para `[[vogel-stack/vogel-stack/<doc>]]`.

O **modelo de operação documental é único e leve**: wikilinks curados + link checker determinístico + auditoria por agente sob demanda. **Sem ferramentas externas obrigatórias** — não há orientação a Graphify nem a Obsidian versionado. O detalhamento está em [[vogel-stack/operacao-leve]]; a justificativa, nos princípios nº 19 ([[vogel-stack/principios|Problema, não tecnologia]]) e nº 11 ([[vogel-stack/principios|Modos de execução suportados devem ser explícitos]]).

## Regras de operação

- A relação entre documentos vive em **wikilinks curados**; o hub humano é o `README`/índice de docs do projeto.
- Para auditoria estrutural (órfão, weak link, comunidade isolada), invocar o agente explicitamente com o prompt-template de [[vogel-stack/operacao-leve]].
- Antes de fechar rodada que tocou em arquivos `.md`, rodar `pwsh ./scripts/check-wikilinks.ps1` (a GitHub Action `check-malha` valida no push/PR para `main`).
- O backlog vive num quadro único `docs/handoffs/_QUADRO.md` (ver [[vogel-stack/operacao-agentes]]); validar com `pwsh ./scripts/check-quadro.ps1`.

## Em qualquer projeto

- Documentos novos nascem **já conectados** via wikilinks reais (princípio nº 18). Sem links decorativos.
- Wikilinks usam a sintaxe `[[caminho/sem/extensao]]` ou `[[caminho|alias]]` — convenção de links da stack, que **não requer o app Obsidian**.
- Visualizar o grafo num app (ex.: Obsidian) é opcional e **local não-versionado** — nunca pré-requisito nem artefato do repo.
- Quando este repositório for atualizado, os projetos que o consomem como submódulo recebem o upgrade via `git submodule update --remote --merge vogel-stack`.
