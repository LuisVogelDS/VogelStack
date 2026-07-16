# Vogel Stack — Instruções para Agentes

Vogel Stack é um conjunto de documentos-base para projetos que usam agentes de IA como parte real do fluxo. Os documentos canônicos da stack estão em `vogel-stack/` (pasta interna deste repositório).

## Documentos canônicos

- [[vogel-stack/principios|Princípios Gerais]]
- [[vogel-stack/documentacao-e-versionamento|Documentação e Versionamento]]
- [[vogel-stack/operacao-agentes|Operação de Agentes]]
- [[vogel-stack/registro-e-evidencias|Registro e Evidências Operacionais]]
- [[vogel-stack/evolucao-produto|Evolução de Produto e Arquitetura]]
- [[vogel-stack/templates|Templates de Documentação]]
- [[vogel-stack/operacao-leve|Operação Documental]]

## Como projetos consomem a Vogel Stack

A stack é geralmente instalada como submódulo em `vogel-stack/` no projeto-alvo. Wikilinks no projeto-alvo apontam para `[[vogel-stack/vogel-stack/<doc>]]`.

A operação documental é **uma só**, descrita em [[vogel-stack/operacao-leve|Operação Documental]]: wikilinks curados como malha, link checker determinístico como piso de integridade, e agente sob demanda para auditoria estrutural. O passo a passo de adoção está em [[quickstart]].

Até 2026-07-16 a stack oferecia duas famílias, uma delas apoiada em ferramenta de knowledge graph materializado. Essa dualidade foi removida — ver [[docs/adr/0002-remover-familia-padrao|ADR 0002]].

## Operação deste repositório

Este repositório (a própria Vogel Stack) segue a mesma operação que prescreve. Histórico da decisão: [[docs/adr/0001-adotar-operacao-leve|ADR 0001]] (adoção) e [[docs/adr/0002-remover-familia-padrao|ADR 0002]] (remoção da dualidade).

Regras de operação aqui:

- Entrar por este arquivo + [[vogel-stack/README|README da stack]] e por [[quickstart]]. **Não** há `docs/contexto.md` nem `docs/README.md`: a estrutura é `vogel-stack/` (docs canônicos) + arquivos-raiz.
- Para auditoria estrutural (órfão, weak link, comunidade isolada), invocar o agente explicitamente com o prompt-template de [[vogel-stack/operacao-leve]].
- Antes de fechar rodada que tocou em arquivos `.md`, rodar `pwsh ./scripts/check-wikilinks.ps1` (a GitHub Action `check-malha` valida no push/PR para `main`).

## Em qualquer projeto

- Documentos novos nascem **já conectados** via wikilinks reais (princípio nº 18). Sem links decorativos.
- Wikilinks usam a sintaxe `[[caminho/sem/extensao]]` ou `[[caminho|alias]]`.
- Quando este repositório for atualizado, os projetos que o consomem como submódulo recebem o upgrade via `git submodule update --remote --merge vogel-stack`.
