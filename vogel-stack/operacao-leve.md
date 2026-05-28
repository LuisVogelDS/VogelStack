# Operação Leve — Sem Graphify e Sem Obsidian Versionado

Este documento define um caminho **alternativo ao fluxo Codex-led + Graphify-assisted** do [[quickstart|quickstart]] padrão. Aplica-se a projetos que conseguem resolver os mesmos problemas com ferramentas mais simples.

A escolha entre os dois caminhos é declarada por projeto, em coerência com o princípio nº 19 ([[principios|Problema, não tecnologia]]) e nº 11 ([[principios|Modos de execução suportados devem ser explícitos]]).

## Quando o caminho leve faz sentido

Adote este caminho quando, **simultaneamente**, valerem todos os pontos abaixo:

- O projeto tem **menos de ~80 documentos** ou **~500KB de markdown**. O hub humano cabe na cabeça e em uma leitura do agente.
- Existe **agente de IA forte** com acesso constante ao repo (Claude Code Max ou High, GPT Codex pago) capaz de fazer auditoria estrutural sob demanda.
- A **maioria dos consumidores** do repo entra com agente já carregado ou lê hub humano curado. Não há fluxo recorrente de "agente frio que precisa de mapa pronto".
- A **volatilidade documental é alta** (fase de arranque, refactor pesado, brainstorm contínuo) — regenerar grafo em cada mudança paga LLM sem retorno proporcional.
- Não há **material bruto extenso** em `docs/raw/` ou `intake/` precisando de inferência LLM para conectar com docs canônicos.

Quando qualquer um desses pontos deixar de valer, mude para o caminho do [[quickstart|quickstart]] (Codex-led + Graphify-assisted).

## O que o caminho leve adota

| Problema | Solução |
|---|---|
| Relacionamento entre docs | Wikilinks curados (estilo Obsidian, sintaxe `[[node]]`) |
| Detecção de link quebrado | Link checker determinístico + GitHub Action (sem LLM) |
| Hub navegável | `docs/README.md` curado |
| Síntese semântica do projeto | `docs/contexto.md` curado |
| Mapa rápido para agente | `AGENTS.md` curado |
| Auditoria estrutural (órfão, weak link, comunidade) | Agente IA sob demanda, com prompt explícito |
| Visualização gráfica | Obsidian local do usuário, **não versionado** |

O submódulo da Vogel Stack continua presente — princípios, templates, operação de agentes e registro/evidências continuam herdados. Só a camada de Graphify + Obsidian versionado é substituída.

## O que o caminho leve **não** entrega

Sou honesto sobre as perdas:

- **Disponibilidade do mapa sem agente.** Sem `GRAPH_REPORT.md`, qualquer auditoria fora de uma sessão de agente vira leitura manual.
- **Visualização interativa "para todos".** Obsidian fica como ferramenta de um humano específico, não de todos os consumidores.
- **Edges inferidas (relações implícitas).** Wikilinks são explícitos; nada além disso é detectado automaticamente.
- **Detecção de comunidades isoladas** sem agente. Em projeto pequeno, isso se vê na estrutura de pastas; em projeto grande, deixa de funcionar.

Se essas perdas começarem a doer, é hora de migrar para o caminho do [[quickstart|quickstart]].

## Receita: remover Graphify e Obsidian versionado de um projeto existente

Use esta receita quando o projeto já adotou o caminho padrão e quer migrar para o caminho leve. Pode ser executado por agente de IA ou humano.

### Pré-condições

- Repo tem submódulo Vogel Stack em `vogel-stack/` (ou caminho equivalente).
- Repo tem ao menos um dos seguintes: `graphify-out/`, `.obsidian/` versionado, regra de "ler GRAPH_REPORT.md" no `AGENTS.md` / `CLAUDE.md`.

### Passo 1 — Validar que o caminho leve faz sentido

Conferir os 5 critérios da seção "Quando o caminho leve faz sentido" acima. Se algum não bater, **não migrar**.

### Passo 2 — Registrar a decisão como ADR

Criar um ADR no projeto (numerar conforme a sequência local) com:

- Contexto (estado atual com Graphify/Obsidian).
- Decisão (adotar caminho leve, listar substituições).
- Gatilhos para reabrir (~80 docs, raw/ extenso, agentes externos sem contexto, auditoria frequente).
- Consequências (sem `graphify-out/`, sem `.obsidian/` versionado).
- Referenciar este documento ([[operacao-leve]]) e o princípio nº 19 de [[principios]].

### Passo 3 — Remover artefatos

Deletar do controle de versão:

```powershell
# Remover artefatos do Graphify (se versionados)
git rm -rf graphify-out/

# Remover vault Obsidian se estiver versionado
git rm -rf .obsidian/

# Atualizar .gitignore para ignorar futuras gerações locais
@'

# Operação leve: artefatos locais que não vão para o repo
graphify-out/
.obsidian/
'@ | Add-Content -Path .gitignore -Encoding UTF8
```

### Passo 4 — Adicionar link checker

Criar `scripts/check-wikilinks.ps1` (referência: a versão usada no projeto Alquimia, que valida `[[wikilink]]`, suporta `[[alvo|alias]]` e `[[alvo#secao]]`, ignora blocos de código, exit code 1 em quebra).

Criar `.github/workflows/check-malha.yml` que roda o checker em push/PR para `main`.

Rodar o checker localmente — corrigir todo wikilink quebrado **antes do commit de migração**. É comum encontrar links que dependiam do `GRAPH_REPORT.md` ou de seções do vault `.obsidian/`.

### Passo 5 — Atualizar `AGENTS.md` / `CLAUDE.md`

Substituir regras que pressupõem Graphify por regras do caminho leve.

Antes (típico):

```markdown
- ALWAYS read graphify-out/GRAPH_REPORT.md before reading source files...
- For cross-module questions, prefer graphify query / path / explain over grep.
```

Depois:

```markdown
- Entrar pelo docs/contexto.md (síntese) e docs/README.md (hub).
- Para auditoria estrutural (órfão, weak link, comunidade), pedir explicitamente
  ao agente com escopo claro. Este projeto não materializa GRAPH_REPORT.md.
- Antes de fechar rodada que tocou em .md, rodar:
    pwsh ./scripts/check-wikilinks.ps1
```

### Passo 6 — Atualizar documentação do projeto

- `docs/operacao.md` ganha seção sobre o checker e o template de prompt para auditoria sob demanda (ver exemplo no Alquimia).
- `docs/reference-vogelstack.md` (ou equivalente) ganha tabela "o que este projeto adota diferente da stack", com justificativa.
- `docs/changelog.md` recebe entrada nova no topo descrevendo a migração.
- Documentos que linkavam para Graphify ou Obsidian-vault ficam atualizados para refletir o novo estado.

### Passo 7 — Commit e validação

```powershell
pwsh ./scripts/check-wikilinks.ps1   # tem que passar
git add scripts/ .github/ AGENTS.md CLAUDE.md docs/ .gitignore
git commit -m "X.Y.Z — Migrar para operação leve (sem Graphify e sem Obsidian versionado)"
git push
```

CI deve passar no primeiro push. Se não passar, é wikilink quebrado — corrigir.

## Prompt-template para auditoria estrutural sob demanda

Quando o caminho leve está adotado e você precisa do equivalente a um `GRAPH_REPORT.md`, pedir ao agente:

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

## Custo comparativo

- **Graphify-assisted:** custo de LLM cada `graphify extract .` + ruído de diff + setup de CLI/env/API key. Em troca: cache de sumário sempre fresco e disponível sem agente.
- **Operação leve:** custo de tokens cada vez que pedimos auditoria ao agente + risco de não detectar weak link entre auditorias. Em troca: zero ferramenta extra, zero ruído de diff, qualidade semântica superior na auditoria.

A escolha não é "qual é melhor", é **qual encaixa no contexto deste projeto**.

## Quando voltar para o caminho padrão

Reverter para [[quickstart|quickstart]] (Codex-led + Graphify-assisted) quando qualquer um disparar:

1. Volume cruza ~80 docs ou ~500KB de markdown.
2. `docs/raw/` (ou `intake/`) passa de 5 itens com volume não trivial.
3. Múltiplos agentes externos passam a consumir o repo sem contexto carregado.
4. Auditoria estrutural vira pedido frequente o suficiente para que materializar valha o custo de regeneração.

Quando o gatilho disparar, materializar Graphify é trivial: rodar `graphify extract .` uma vez, remover `graphify-out/` do `.gitignore`, ajustar `AGENTS.md` para a regra original. Não há barreira irreversível.
