# Operação Documental

> **Nota de nome:** o arquivo se chama `operacao-leve.md` por razão histórica — nasceu como alternativa "leve" a um caminho pesado que a stack não oferece mais ([[0002-remover-familia-padrao|ADR 0002]]). O nome foi mantido de propósito: os projetos consumidores linkam para ele, e renomear quebraria a malha de todos de uma vez. É resquício histórico, não descrição.

Este documento define **a operação documental da Vogel Stack**: como a malha de documentos se mantém navegável, íntegra e auditável — para humanos e para agentes.

A operação se apoia em três peças, e só nelas:

1. **Wikilinks curados** — a malha. Explícita, escrita por quem conhece a relação real.
2. **Link checker determinístico** — o piso. Script sem LLM, roda em CI, falha em link quebrado.
3. **Agente de IA sob demanda** — a auditoria. Órfão, weak link e comunidade isolada viram pedido explícito, não relatório materializado.

## O que a operação adota

| Problema | Solução |
|---|---|
| Relacionamento entre docs | Wikilinks curados, sintaxe `[[node]]` |
| Detecção de link quebrado | Link checker determinístico + CI (sem LLM) |
| Hub navegável | `docs/README.md` curado (ou equivalente do projeto) |
| Síntese semântica do projeto | `docs/contexto.md` curado |
| Mapa rápido para agente | `AGENTS.md` / `CLAUDE.md` curado |
| Auditoria estrutural (órfão, weak link, comunidade) | Agente de IA sob demanda, com prompt explícito |
| Visualização gráfica | Ferramenta local do usuário, **não versionada** |

Os princípios herdados continuam valendo integralmente: [[principios|Princípios Gerais]], [[templates|Templates de Documentação]], [[operacao-agentes|Operação de Agentes]] e [[registro-e-evidencias|Registro e Evidências Operacionais]].

## Limites conhecidos

Honestidade sobre o que esta operação **não** entrega:

- **Mapa disponível sem agente.** Não há sumário materializado: auditoria fora de uma sessão de agente vira leitura manual.
- **Visualização interativa "para todos".** Quem quiser grafo visual usa ferramenta local; ela não é contrato do repositório.
- **Edges inferidas.** Wikilinks são explícitos — relação que ninguém escreveu não é detectada sozinha.
- **Detecção automática de comunidade isolada.** Em projeto pequeno isso se vê na estrutura de pastas; em projeto grande, deixaria de funcionar.

Esses limites são aceitáveis no perfil dos projetos que a stack atende: poucos documentos, agente forte constantemente disponível e alta volatilidade documental.

## Quando esta operação deixa de bastar

Se algum destes disparar, o projeto tem um **problema novo** e declara a solução em ADR próprio (princípio nº 19 — [[principios|Problema, não tecnologia]]). A stack não reintroduz ferramenta por antecipação:

1. Volume cruza ~80 documentos ou ~500KB de markdown.
2. `docs/raw/` ou `intake/` passa a ter material bruto extenso precisando ser conectado aos docs canônicos.
3. Múltiplos agentes externos frios passam a consumir o repo sem contexto carregado.
4. Auditoria estrutural vira pedido frequente o suficiente para que materializar um cache compense o custo.

## Piso de integridade — o link checker

Todo projeto que use wikilinks como contrato de navegação deve manter:

- `scripts/check-wikilinks.ps1` (ou equivalente) — valida que todo `[[wikilink]]` aponta para arquivo existente; suporta `[[alvo|alias]]` e `[[alvo#secao]]`; ignora blocos de código; sai com código 1 em quebra.
- Uma Action de CI (`check-malha` ou equivalente) rodando em push/PR para `main`.
- Execução local antes de fechar qualquer rodada que tenha tocado em `.md`.

Detalhes operacionais em [[operacao-agentes#7.4 Link checker determinístico como piso da malha|operacao-agentes seção 7.4]].

## Prompt-template para auditoria estrutural sob demanda

Quando precisar do equivalente a um relatório de grafo, pedir ao agente:

```text
Audite a malha de documentação deste projeto:

1. Liste documentos órfãos (não recebem nenhum wikilink de outros).
2. Liste documentos com apenas 1 link entrando (weak links).
3. Identifique comunidades isoladas — clusters de docs que só linkam
   entre si e não conectam com o núcleo do projeto.
4. Para cada item, proponha onde inserir wikilink fazendo sentido real
   (não decorativo). Não edite — só liste a sugestão.

Escopo: docs/ + AGENTS.md + README.md raiz. Ignorar vogel-stack/.
```

Saída desejada: relatório textual que um humano (ou outro agente) revisa antes de aplicar.

## Custo

O custo desta operação é de tokens, cada vez que se pede auditoria ao agente — mais o risco de não detectar um weak link entre auditorias. Em troca: zero ferramenta extra, zero ruído de diff, e qualidade semântica superior na auditoria (o agente entende o projeto; um extrator estrutural não).
