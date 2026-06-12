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

## Família adotada por ESTE repositório: leve

Este repositório (a própria Vogel Stack) opera no **caminho leve**, decisão registrada em [[docs/adr/0001-adotar-operacao-leve|ADR 0001]] (princípios nº 19 e nº 11). Perfil que justifica: ~12 docs, agente forte sempre disponível, alta volatilidade documental.

Regras de operação aqui:

- **Não** procurar `graphify-out/` — não existe mais neste repo (removido na migração; ver ADR 0001). Graphify e Obsidian, se usados, são ferramentas **locais não-versionadas** (estão no `.gitignore`).
- Entrar por este arquivo + [[vogel-stack/README|README da stack]] e por [[quickstart]] (como escolher família). **Não** há `docs/contexto.md` nem `docs/README.md`: a estrutura é `vogel-stack/` (docs canônicos) + arquivos-raiz.
- Para auditoria estrutural (órfão, weak link, comunidade isolada), invocar o agente explicitamente com o prompt-template de [[vogel-stack/operacao-leve]]. Este repo não materializa `GRAPH_REPORT.md`.
- Antes de fechar rodada que tocou em arquivos `.md`, rodar `pwsh ./scripts/check-wikilinks.ps1` (a GitHub Action `check-malha` valida no push/PR para `main`).

## Caminho padrão (referência para projetos consumidores)

A família **padrão (Codex-led + Graphify-assisted)** — Graphify materializa `graphify-out/`, Obsidian é a camada visual, e o agente lê `GRAPH_REPORT.md` antes de buscar em arquivos-fonte — está documentada em [[quickstart]]. Indicada para projetos com ≥ ~80 docs, material bruto extenso ou agentes externos frios. **Este repositório não a adota**, mas a mantém documentada para quem a escolher.

## Em qualquer caminho

- Documentos novos nascem **já conectados** via wikilinks reais (princípio nº 18). Sem links decorativos.
- Wikilinks usam sintaxe Obsidian: `[[caminho/sem/extensao]]` ou `[[caminho|alias]]`.
- Quando este repositório for atualizado, os projetos que o consomem como submódulo recebem o upgrade via `git submodule update --remote --merge vogel-stack`.
