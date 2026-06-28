# Quickstart — Adotar a Vogel Stack num projeto

A Vogel Stack é consumida como **submódulo** e define um modelo de operação documental **único e leve**: wikilinks curados + link checker determinístico + auditoria por agente sob demanda. **Sem ferramentas externas obrigatórias** (sem Graphify, sem Obsidian versionado). Visão completa em [[vogel-stack/operacao-leve|Operação Documental]].

## 1. Adicionar a stack como submódulo

```powershell
git submodule add https://github.com/LuisVogelDS/VogelStack vogel-stack
```

Wikilinks do projeto-alvo apontam para `[[vogel-stack/vogel-stack/<doc>]]`.

## 2. Estrutura mínima do projeto

- `README.md` — porta de entrada (reflete a versão atual; sem backlog futuro tratado como pronto).
- `AGENTS.md` / `CLAUDE.md` — diretrizes para agentes (modelo em [[vogel-stack/templates]]).
- `docs/` — documentação canônica (arquitetura, operação, versionamento, fontes…), conectada por wikilinks.
- `docs/handoffs/_QUADRO.md` — backlog único (ver [[vogel-stack/operacao-agentes]]).
- `CHANGELOG.md` — histórico legível por humanos.
- `scripts/check-wikilinks.ps1` + `.github/workflows/check-malha.yml` — checagem da malha de links.

Todos os modelos estão em [[vogel-stack/templates]].

## 3. Convenções

- Documentos nascem **já conectados** por wikilinks reais (princípio nº 18), sintaxe `[[caminho|alias]]` — convenção de links, **não requer o app Obsidian**.
- O backlog vive no quadro único `_QUADRO.md` — sem `TODO`/`IMPROVEMENTS` paralelo.
- Antes de fechar rodada que tocou em `.md`: `pwsh ./scripts/check-wikilinks.ps1`. Quadro: `pwsh ./scripts/check-quadro.ps1`.

## 4. Auditoria estrutural

Sob demanda, via agente — prompt-template em [[vogel-stack/operacao-leve]]. Não há mapa materializado (`GRAPH_REPORT.md`); a auditoria é pedida explicitamente quando necessária.

## 5. Atualizar a stack

```powershell
git submodule update --remote --merge vogel-stack
```

## Documentos canônicos

- [[vogel-stack/principios|Princípios Gerais]]
- [[vogel-stack/documentacao-e-versionamento|Documentação e Versionamento]]
- [[vogel-stack/operacao-agentes|Operação de Agentes]]
- [[vogel-stack/registro-e-evidencias|Registro e Evidências Operacionais]]
- [[vogel-stack/evolucao-produto|Evolução de Produto e Arquitetura]]
- [[vogel-stack/templates|Templates de Documentação]]
- [[vogel-stack/operacao-leve|Operação Documental]]
