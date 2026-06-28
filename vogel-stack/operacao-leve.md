# Operação Documental

Este documento define **o modelo de operação documental da Vogel Stack**: wikilinks curados + link checker determinístico + auditoria por agente sob demanda. É um modelo **leve por design** — resolve relacionamento entre docs, detecção de link quebrado e auditoria estrutural **sem ferramentas externas obrigatórias** (sem Graphify, sem Obsidian versionado).

A escolha por esse modelo é coerente com o princípio nº 19 ([[principios|Problema, não tecnologia]]) e nº 11 ([[principios|Modos de execução suportados devem ser explícitos]]): ferramenta é meio, não fim — adota-se a mais simples que resolve o problema real.

## O que o modelo adota

| Problema | Solução |
|---|---|
| Relacionamento entre docs | Wikilinks curados (sintaxe `[[node]]`) |
| Detecção de link quebrado | Link checker determinístico + GitHub Action (sem LLM) |
| Hub navegável | `README`/índice de docs curado |
| Síntese do projeto | `README` + docs canônicos curados |
| Backlog | Quadro único `docs/handoffs/_QUADRO.md` (ver [[operacao-agentes]]) |
| Auditoria estrutural (órfão, weak link, comunidade) | Agente IA sob demanda, com prompt explícito |
| Visualização gráfica (opcional) | App local do usuário (ex.: Obsidian), **não versionado** |

Premissa: existe um **agente de IA forte** com acesso ao repo (Claude Code, Codex) capaz de fazer auditoria estrutural sob demanda quando preciso — em vez de manter um mapa materializado sempre atualizado.

## Auditoria estrutural sob demanda (prompt-template)

Quando precisar do equivalente a um relatório de grafo, peça ao agente:

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

Saída desejada: relatório textual que humano (ou outro agente) revisa antes de aplicar.

## Link checker

Cada projeto mantém `scripts/check-wikilinks.ps1` (valida `[[wikilink]]`, suporta `[[alvo|alias]]` e `[[alvo#secao]]`, ignora blocos de código, exit code 1 em quebra) e uma GitHub Action (`check-malha.yml`) que roda em push/PR para `main`. Antes de fechar rodada que tocou em `.md`, rodar o checker localmente e corrigir todo link quebrado.

## Apêndice — migrar um projeto que ainda tenha Graphify/Obsidian versionado

Se um projeto legado ainda versiona `graphify-out/` ou `.obsidian/`, remova-os:

```powershell
git rm -rf graphify-out/ .obsidian/    # se versionados
@'

# Ferramentas locais não versionadas
graphify-out/
.obsidian/
'@ | Add-Content -Path .gitignore -Encoding UTF8
```

Depois: garanta o `scripts/check-wikilinks.ps1` + a Action, rode o checker e religue todo wikilink que dependia de artefatos removidos (era comum links apontarem para `GRAPH_REPORT.md` ou seções do vault). Registre a remoção no `docs/changelog.md`. Veja o histórico dessa migração na própria stack em [[docs/adr/0001-adotar-operacao-leve|ADR 0001]] e [[docs/adr/0002-aposentar-familia-graphify|ADR 0002]].
