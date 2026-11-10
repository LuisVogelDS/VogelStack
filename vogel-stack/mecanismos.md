# Qual mecanismo usar

Cada falha do agente deve virar melhoria permanente no sistema, e não só correção do caso (ciclo de Loop Engineering). O difícil é escolher onde a melhoria mora. Os gatilhos abaixo adaptam o guia oficial ([Extend Claude Code](https://code.claude.com/docs/en/features-overview), [Steering Claude Code](https://claude.com/blog/steering-claude-code-skills-hooks-rules-subagents-and-more)) a duas realidades: o usuário alterna entre máquinas e trabalha com outras pessoas. Sendo assim, o que precisa valer em todas as máquinas e para os colegas mora no git, e a auto-memória (local da máquina) não guarda fato de projeto. O procedimento de aplicar a escolha é a skill `registrar-licao`; o contexto geral está em [[vogel-stack/operacao-agentes|Operação de Agentes]] e em [[vogel-stack/principios|Princípios Gerais]].

## Gatilho e mecanismo

| Situação | Mecanismo | Observação |
| - | - | - |
| Fato que vale sempre no repo (comando, convenção, "nunca X") | `CLAUDE.md`/`AGENTS.md` do repo | Uma linha. Abaixo de 200 linhas; passou disso, mover para skill ou `.claude/rules/` com `paths:`. |
| O agente errou a mesma coisa 2 vezes | Linha no `CLAUDE.md`/`AGENTS.md` | Correção repetida no chat é edição de arquivo. |
| Procedimento colado pela 3ª vez | Skill | No plugin `vogel-stack` se serve a vários repos; em `.claude/skills/` do repo se é de um só. |
| "Toda vez, sem exceção" | Hook no plugin | Instrução é pedido, hook é garantia. Molde: `hooks/guard-git.py` com `test_guard_git.py`. |
| Saída que inunda o contexto, ou trabalho paralelo | Subagente | Definição dos tipos: modelos em [[vogel-stack/agentes/README|vogel-stack/agentes/]], para copiar em `~/.claude/agents`; o roteamento de modelo mora na definição. |
| Script igual em dois repos | `ferramentas/` do VogelStack + manifesto de cópias | Uma fonte, cópias listadas, para não divergirem. |
| Sistema externo (browser, banco, gerenciador de chamados) | MCP | A skill ensina a usar bem o que o MCP conecta. |

Auto-memória serve só a preferência pessoal que não afeta o repo. Fato de projeto na memória é fato que a outra máquina e os colegas não veem.

## Escolhas que se repetem

- Hook só quando a regra é mecânica e verificável por script. Se exige julgamento, é skill.
- Regra que vale só para parte do código: `.claude/rules/` com `paths:`, e não o `CLAUDE.md` global.
- Skill com efeito colateral (commit, deploy, apagar, publicar) leva `disable-model-invocation: true`: só roda quando o usuário a chama, e a descrição nem entra no contexto.
- A `description` da skill diz quando usar, com os gatilhos reais. Descrição vaga faz a skill não disparar ou disparar errada.
- Antes de criar mecanismo, procurar o que já existe e por que não pegou. Muitas vezes a regra existia e estava no lugar errado.

## Como avaliar uma skill

1. Escolher 3 a 5 prompts reais, dos casos em que a skill deveria atuar.
2. Rodar os mesmos prompts sem a skill e com ela, cada um em sessão nova (contexto limpo), e comparar o resultado.
3. Se o resultado não melhorou, a skill é ruído: ajustar a descrição ou o corpo, ou apagar.
4. Para o plugin inteiro, `claude plugin eval <caminho|plugin@marketplace>` roda casos de `evals/` e inclui um braço sem o plugin como base. Rodar só em plugin confiável.
5. `claude plugin details vogel-stack` mostra o inventário e o custo estimado em tokens.

## Onde ficam as coisas

| O quê | Caminho |
| - | - |
| Skills que servem a vários repos | `VogelStack/skills/<nome>/SKILL.md` |
| Hooks do plugin | `VogelStack/hooks/` (registro em `hooks.json`) |
| Scripts compartilhados | `VogelStack/ferramentas/` e `VogelStack/scripts/` |
| Skill de um repo só | `<repo>/.claude/skills/<nome>/SKILL.md` |
| Regra de um repo | `<repo>/CLAUDE.md` ou `AGENTS.md` |
| Regra com escopo de pasta | `<repo>/.claude/rules/*.md` com `paths:` |
| Agentes (modelos) | `VogelStack/vogel-stack/agentes/`, copiados para `~/.claude/agents` ou `<repo>/.claude/agents` |
| Preferência pessoal, vale em todo repo | `~/.claude/CLAUDE.md` |
| Auto-memória | local da máquina; nunca para fato de projeto |

## Instalar e atualizar o plugin nas duas máquinas

O marketplace `vogel-stack-local` aponta para a pasta do clone, então o plugin lê do diretório e não de cópia em cache: edição de skill vale na próxima sessão ou em `/reload-plugins`. Em cada máquina, uma vez (passo a passo em [[quickstart]]):

```powershell
claude plugin validate "C:\caminho\para\VogelStack"
claude plugin marketplace add "C:\caminho\para\VogelStack"
claude plugin install vogel-stack@vogel-stack-local
```

Para atualizar, `git pull` no clone e, se o Claude não enxergar a mudança, `claude plugin marketplace update vogel-stack-local`. Skill ou hook novo só chega à outra máquina depois de commit e push aqui e de pull lá.
