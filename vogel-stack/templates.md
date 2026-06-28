# Templates de Documentação

Este arquivo traz modelos mínimos para iniciar novos repositórios com o padrão da [[README|Vogel Stack]].

Conexões fortes do grafo:

- AGENTS.md Document Pattern
- [[registro-e-evidencias|Registry de Execuções]]
- [[registro-e-evidencias|Manifesto por Run]]
- Handoff Padrão de Execução
- PowerShell Logging Pattern
- Método Brainstorm-Concepção-Wireframe-Implementação

## 1. Template de `AGENTS.md`

```text
# AGENTS: Diretrizes Operacionais do Projeto

## 1. Contexto do produto

- o que o produto faz
- para quem ele existe
- qual problema resolve

## 2. Matriz de suporte

- caminho oficialmente suportado
- fluxo experimental ou WIP
- fluxo legado, se existir

## 3. Fontes de verdade

- API
- banco
- cache
- configuração
- autenticação

## 4. Objetivo técnico

- o que a aplicação precisa continuar fazendo

## 5. Contratos obrigatórios

- onde o schema ou contrato principal vive
- quais superfícies derivam dele, por exemplo UI, API ou automações
- política para rejeitar parâmetros desconhecidos
- política para nomes canônicos e aliases

## 6. Princípios obrigatórios

- docs refletem código real
- credenciais não entram em docs
- mudanças de fonte, auth e deploy exigem atualização documental
- fluxo oficialmente suportado não pode ficar ambíguo
- semântica de saída precisa permanecer estável
- conexões relevantes devem ser materializadas no Knowledge Graph

## 7. Política de execução

- evitar gasto desnecessário de recursos
- preferir agente prepara, usuário executa, agente interpreta
- para execuções longas, caras ou muito verbosas, entregar script com logging persistente em vez de acompanhar tudo ao vivo pelo agente

## 8. Convenção de comandos

- PowerShell no Windows
- bash quando aplicável
- em rotinas pesadas, sempre informar onde o log será salvo e como o código de saída será preservado

## 9. Regras de UX e filtros

- o que fica no fluxo básico
- o que fica no bloco avançado
- quais campos de saída ou destino nunca devem ficar escondidos

## 10. Regras para docs

- quais arquivos devem permanecer coerentes
- quando atualizar cada um
- política para arquivos privados de AI stack, prompts e apoio pessoal
- todo documento novo deve nascer com wikilinks reais para a Vogel Stack, documentos canônicos, processos, artefatos e evidências relacionadas

## 11. Evidência operacional

- onde vive o [[registro-e-evidencias|registry de execuções]], se existir
- como runs e artefatos são identificados
- como localizar [[registro-e-evidencias|manifestos]] e saídas por rodada

## 12. Regras de mudança segura

- validar contratos
- validar auth
- validar impacto funcional
- validar necessidade de update documental

## 13. Checklist final

- app abre
- imports válidos
- docs coerentes
- sem segredos expostos
- sem regressão óbvia
```

## 2. Template de `quickstart.md`

````text
# Quickstart

## 1. Entrar na pasta do projeto

```powershell
Set-Location "<CAMINHO_DO_PROJETO>"
```

## 2. Instalar dependências

```powershell
<COMANDO_DE_INSTALACAO>
```

## 3. Iniciar o sistema

```powershell
<COMANDO_DE_START>
```

## 4. Validar funcionamento

- URL local, se existir
- comando de healthcheck, se existir
- sinal esperado de sucesso

## 5. Reiniciar

```powershell
<COMANDO_DE_RESTART_OU_PASSOS_PARA_PARAR_E_SUBIR>
```

## 6. Problemas comuns

- dependência ausente
- porta ocupada
- configuração local ausente
- credencial inválida
````

## 3. Template de `docs/arquitetura.md`

```text
# Arquitetura do Projeto

Estado atual resumido:

- versão estável
- camada experimental, se existir
- origem dos dados
- situação do deploy
- caminho oficialmente suportado de execução

## 1. Objetivo da aplicação

- perguntas que o sistema responde hoje

## 2. Fluxos principais

### 2.1 Fluxo atual

### 2.2 Fluxo experimental ou futuro, se já existir

## 3. Módulos e responsabilidades

- ponto de entrada
- configuração
- integrações externas
- transformação de dados
- autenticação
- backend
- frontend
- serviços
- utilitários

## 4. Fontes de verdade

## 5. Contratos principais

- schema ou contrato de entrada
- semântica de saída
- identificadores canônicos

## 6. Limitações conhecidas

## 7. Próximos passos já materializados ou assumidos
```

## 4. Template de `docs/versionamento.md`

```text
# Versionamento do Projeto

## Política de versionamento

- quando atualizar versão
- papel do README
- papel do changelog

## Histórico de versões

## 1.0

Escopo:

- item

Adições principais:

- item

Motivação:

- item

Status:

- estável
```

## 5. Template de `docs/changelog.md`

```text
# Changelog

## AAAA-MM-DD

### X.Y - título da entrega

Entradas principais:

- item
- item

Estado:

- observação
- observação
```

## 6. Template de `docs/fontes-e-filtros.md`

```text
# Fontes e Filtros

## 1. Convenções

- nomes canônicos expostos ao usuário
- política de aliases, se existir
- relação entre schema, API e UI

## 2. Fases de execução

- coleta
- refinamento local
- exportação

## 3. Parâmetros por fonte ou módulo

| Parâmetro | Tipo | Fase | Notas |
| --- | --- | --- | --- |
| exemplo | string | coleta | observação |

## 4. Regras de UX

- o que deve aparecer no fluxo básico
- o que deve aparecer no bloco avançado
- quais campos de destino ou saída ficam sempre visíveis

## 5. Notas operacionais

- limites conhecidos
- warnings esperados
- dicas de uso seguro
```

## 7. Template de `docs/ai-handoff-dominio.md`

````text
# AI Handoff: <domínio>

Este documento concentra o contexto mínimo para futuras conversas sobre uma área sensível do projeto.

## 1. Estado atual

- versão atual
- caminho oficialmente suportado
- escopo atual do domínio

## 2. Contrato atual

- entradas principais
- refinamentos opcionais
- semântica de saída
- warnings ou erros importantes

## 3. Regras de implementação

- invariantes que não podem quebrar
- contratos que precisam ser preservados
- testes mínimos
- docs que precisam ser atualizados no mesmo ciclo

## 4. Arquivos-chave

- arquivo 1
- arquivo 2

## 5. Checklist de mudança

1. atualizar schema ou contrato
2. ajustar fluxo de execução
3. preservar logs e rastreabilidade
4. validar artefatos de saída
5. atualizar testes e docs

## 6. Comandos de validação

```bash
# comandos oficiais do projeto
```

## 7. Prompt-base para retomada

- contexto mínimo para iniciar uma nova conversa sem perder o estado real
````

## 7.1 Template de `docs/handoffs/_QUADRO.md`

Quadro único conciliado a partir das fontes de demanda (handoffs, issues, `intake/`), descrito em [[operacao-agentes#7.1.1 Quadro de trabalho conciliado a partir das fontes de demanda|Operação de Agentes §7.1.1]]. Item ainda aberto sobe para o quadro; ✅ é transitório e drena para o `docs/changelog.md`; fonte com tudo fechado vai para `docs/handoffs/legado/`.

```text
# Quadro de Trabalho — <projeto>

> **O que é:** quadro único de trabalho, conciliado a partir das fontes de demanda
> (handoffs em `docs/handoffs/`, issues, `intake/`). Cada fonte tem seus "próximos passos /
> decisões em aberto" reconciliados contra o estado real do repo (git, `reports/`, código,
> changelog). É uma fila, não um arquivo: item aberto sobe pra cá; fonte com tudo fechado
> vai pra `docs/handoffs/legado/`. É o **backlog único** do projeto — sem `TODO`/`IMPROVEMENTS`
> paralelo; spec longa vira doc próprio, linkado da linha.
>
> **Drenagem:** ✅ é transitório — ao concluir, registre a entrega no `docs/changelog.md` (e o
> arco em `docs/versionamento.md`, se virou versão) e remova a linha na próxima reconciliação.
> O quadro mostra o presente em aberto; o passado materializado vive no changelog.
>
> **Última reconciliação:** AAAA-MM-DD — N fontes (A ativas, L legado-candidatas).
>
> **Legenda:** 🔴 Prioridade · 🟡 Em andamento · ⚪ Pendente (backlog válido) · 🗄️ Defasado (morto, mantido por memória) · ✅ Concluído (transitório → changelog)

## 🔴 Prioridade

| Item | Origem | Próxima ação / nota |
|---|---|---|
| <item aberto> | <fonte de origem> | <próximo passo concreto> |

## 🟡 Em andamento

| Item | Origem | Próxima ação / nota |
|---|---|---|
| <item> | <fonte de origem> | <estado e próximo passo> |

## ⚪ Pendente (backlog válido)

| Item | Origem | Nota |
|---|---|---|
| <item> | <fonte de origem> | <por que ainda não foi priorizado> |

## 🗄️ Defasado (morto — mantido por memória)

- <decisão superada> → <o que a substituiu>.

## Reconciliação por fonte → legado

**Ativo** = tem item aberto não-trivial cujo contexto vale ter à mão.
**Legado-concluído** = próximos passos já realizados. **Legado-defasado** = superado ou irrelevante.

| Fonte | Veredito | Itens abertos (já no quadro acima) |
|---|---|---|
| <fonte> | Ativo / Legado-concluído / Legado-defasado | <itens, ou —> |
```

## 8. Template de `docs/operacao.md`

Este template se conecta ao Handoff Padrão de Execução e ao PowerShell Logging Pattern.

```text
# Operação do Projeto

## 1. Caminho oficialmente suportado

- qual comando ou fluxo é o principal
- o que é experimental
- o que depende do ambiente do usuário

## 2. Pré-requisitos

- ambiente
- autenticação
- variáveis relevantes
- limites conhecidos

## 3. Execuções recorrentes

- jobs
- pipelines
- automações
- comandos padrão

## 4. Registry e evidências

- onde vive o registry
- quais campos mínimos ele contém
- onde ficam manifestos e artefatos por run

## 5. Diagnóstico

- logs principais
- mensagens esperadas
- falhas comuns
- como coletar contexto para repassar ao agente

## 5.1 Handoff para execuções custosas

- quando o usuário deve executar localmente
- quais comandos devem ser entregues prontos
- onde os logs são gravados
- como o projeto diferencia stdout, stderr, transcript e artefatos finais

## 6. Guardrails operacionais

- o que não deve ser rodado automaticamente
- o que exige confirmação
- o que deve ser executado pelo usuário localmente
```

## 8. Template de script PowerShell com log

```powershell
New-Item -ItemType Directory -Force -Path .\logs | Out-Null
$ts = Get-Date -Format 'yyyyMMdd-HHmmss'
$log = ".\logs\<nome-da-rotina>-$ts.log"

& <comando> 2>&1 | Tee-Object -FilePath $log
$exitCode = $LASTEXITCODE

Write-Host "Log salvo em: $log"
exit $exitCode
```

## 9. Template de brainstorm de dashboard

Este template implementa o Método Brainstorm-Concepção-Wireframe-Implementação descrito em [[evolucao-produto|Evolução de Produto e Arquitetura]].

```text
# Brainstorm do Novo Dashboard

## Perguntas que o produto precisa responder

- pergunta 1
- pergunta 2

## O que pode deixar de existir

- visual ou fluxo legado que não precisa ser preservado

## Módulos possíveis

- triage
- diagnóstico
- auditoria

## Ideias visuais

- mapa
- tendência
- composição
- tabela contextual
```

## 10. Template de concepção

```text
# Concepção do Novo Dashboard

## Respostas prioritárias

## Navegação proposta

## Módulos obrigatórios

## Ordem de leitura

## Direção visual
```

## 11. Template de wireframe textual

```text
# Wireframe da Nova Aba

## Linha 1

- módulo
- proporção
- função

## Linha 2

- módulo
- proporção
- função

## Linha 3

- módulo
- proporção
- função
```
