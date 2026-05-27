# Operação de Agentes

Este documento define um padrão operacional para projetos que usam agentes de IA como parte do fluxo real de trabalho, conectado a [[registro-e-evidencias|Registro e Evidências Operacionais]].

## 1. Fluxo operacional padrão

Fluxo preferencial, também tratado como [[Handoff Padrão de Execução]]:

1. agente prepara;
2. usuário executa;
3. agente interpreta.

Esse fluxo é o padrão quando a etapa for:

- repetitiva;
- custosa;
- longa;
- dependente de credenciais;
- dependente do ambiente local do usuário;
- sensível do ponto de vista operacional.

## 2. Política de custo e uso de recursos

Regras:

- evitar gasto desnecessário de créditos, tempo de máquina e recursos externos;
- não disparar instalações, downloads, treinos longos, cargas pesadas ou processos mecânicos sem necessidade real;
- preferir análise estática, comandos prontos e checklists antes de sugerir execuções caras;
- em execuções longas, pesadas ou ruidosas, preferir o padrão `agente prepara, usuário executa, agente interpreta` em vez de gastar créditos acompanhando toda a execução;
- quando uma execução custosa for necessária, explicitar por que ela destrava a tarefa.

## 3. Quando o agente deve executar por conta própria

O agente pode executar diretamente quando a ação for:

- curta;
- local;
- barata;
- reversível;
- suficiente para validar estrutura, sintaxe ou consistência básica.

Exemplos:

- leitura de arquivos;
- inspeção do repositório;
- checagem estática;
- compilação leve;
- validação de imports e caminhos.

## 4. Quando o agente deve preparar para o usuário

O agente deve preferir preparar comandos e instruções quando a ação envolver:

- instalação de dependências;
- execução prolongada;
- uso intenso de CPU, memória ou rede;
- acesso a ambiente autenticado;
- acesso a infraestrutura externa;
- builds pesados de Docker ou containers;
- suites longas de teste, benchmark ou migração;
- deploy, publicação ou operação sensível.

## 5. Convenção para comandos

Padrão recomendado:

- fornecer comandos prontos para copiar e executar;
- preferir `PowerShell` em ambientes Windows;
- quando houver diferença relevante entre `bash` e `PowerShell`, documentar a variante correta;
- em rotinas locais, variáveis de ambiente, filesystem e execução de serviços no Windows, usar `PowerShell` como primeira opção.

## 5.1 Matriz de suporte antes de executar

Antes de propor ou executar comandos, o agente deve identificar:

- qual é o caminho oficialmente suportado;
- quais fluxos são apenas experimentais ou incompletos;
- se o comando sugerido valida o caminho principal ou um caminho secundário.

O agente não deve promover um fluxo `WIP` como padrão só porque ele parece mais simples no momento.

## 5.2 Padrão de handoff para execução custosa

Quando a execução for longa, cara ou muito verbosa, o agente deve preferir entregar um comando ou script com [[PowerShell Logging Pattern|logging persistente]].

O handoff ideal deve incluir:

- comando idempotente quando possível;
- criação explícita do diretório de logs;
- nome de arquivo com timestamp;
- captura conjunta de `stdout` e `stderr`;
- preservação do código de saída do processo;
- indicação clara de onde o log será encontrado;
- lista breve dos artefatos ou sinais esperados ao final.

Base recomendada em `PowerShell`:

```powershell
New-Item -ItemType Directory -Force -Path .\logs | Out-Null
$ts = Get-Date -Format 'yyyyMMdd-HHmmss'
$log = ".\logs\run-$ts.log"

& <comando> 2>&1 | Tee-Object -FilePath $log
$exitCode = $LASTEXITCODE

Write-Host "Log salvo em: $log"
exit $exitCode
```

Quando a rotina envolver múltiplas etapas, preparação de ambiente ou comandos encadeados, também vale usar `Start-Transcript` para capturar contexto adicional da sessão.

## 6. Atualizações de progresso

Durante trabalhos maiores, o agente deve:

- informar o que está fazendo;
- informar o que aprendeu;
- explicar o próximo passo;
- avisar antes de editar arquivos;
- separar claramente análise, implementação e validação.

## 7. Logging como parte da colaboração

Projetos agent-friendly devem tratar logging como parte de [[Observabilidade e Logs|observabilidade]] mínima e prever:

- logs persistidos em arquivo;
- retenção ou rotação;
- separação por superfície, por exemplo backend e frontend;
- mensagens suficientes para que o usuário compartilhe contexto sem precisar reconstruir o problema manualmente.

Em execuções entregues ao usuário, o log não é acessório: ele faz parte do contrato de colaboração entre agente e operador local.

## 7.1 Handoffs explícitos para áreas sensíveis

Quando um domínio do sistema for especialmente crítico, instável ou cheio de contexto acumulado, vale manter um documento de [[Handoff Padrão de Execução|handoff]] específico.

Esse handoff deve concentrar:

- estado atual do domínio;
- contratos relevantes;
- arquivos-chave;
- checklist de mudança;
- comandos de validação;
- prompt-base para retomada futura, quando isso reduzir retrabalho.

## 7.2 Registro mínimo de execução

Quando o projeto gera artefatos, relatórios, exportações ou resultados por rodada, vale manter um [[Registry de Execuções|registro explícito de execução]].

Esse registro deve permitir ao agente e ao usuário localizar:

- `run_id`;
- escopo;
- estágio;
- artefatos gerados;
- resultado principal;
- observações de execução.

Isso reduz retrabalho e evita que o agente trate como desconhecido algo que já foi materializado.

## 7.2.1 [[Regra de Juros Compostos]]

Quando o agente criar ou orientar a criação de um diretório `reports/runs/<run_id>/`, ele deve tratar essa run como memória futura do projeto e entrada para o [[Knowledge Graph]].

Regras:

- criar ou atualizar um resumo legível dentro da run;
- registrar quais artefatos foram finais, auxiliares, parciais ou ausentes;
- garantir que o `registry` aponte para o diretório da run;
- escrever nomes e descrições que possam ser indexados pelo [[Knowledge Graph]];
- deixar explícitas relações com decisões, hipóteses, métricas, erros ou serviços avaliados;
- orientar a próxima atualização do [[Graphify Knowledge Graph Tool|Graphify]] para incluir esses artefatos.

A disciplina de log continua rígida, mas agora tem um ganho acumulativo: cada execução bem registrada vira material de aprendizado para a próxima varredura semântica.

## 7.3 Arquivos privados do usuário e da AI stack

Projetos com uso intenso de agentes costumam acumular:

- prompts pessoais;
- notas privadas;
- arquivos locais de credenciais;
- material auxiliar de AI stack que não faz parte do contrato oficial do repositório.

Regra recomendada:

- esses arquivos devem ser explicitamente classificados como privados ou locais;
- não devem ser promovidos automaticamente para docs oficiais;
- não devem entrar em commit, release ou PR sem intenção clara do usuário;
- o projeto deve manter distinção entre stack compartilhada e apoio individual.

## 8. Checklist antes de concluir uma alteração

Antes de encerrar uma entrega, validar:

1. se o fluxo principal do projeto continua abrindo;
2. se imports e caminhos continuam válidos;
3. se a documentação foi atualizada quando necessário;
4. se nenhum segredo novo foi exposto;
5. se a mudança não introduziu regressão óbvia nas áreas principais;
6. se o projeto usa workflow de commit automático com mensagem genérica (ver [[documentacao-e-versionamento#3.05 Workflows com commit automático e mensagem genérica|Workflows com commit automático]]), entrada nova no topo de `docs/changelog.md` é parte do encerramento e deve sair antes do sync;
7. se o projeto tem submódulos e o script de sync não entra neles, o `git push` dentro do submódulo precisa ser feito manualmente antes do sync principal, ou o repositório pai vai empurrar um ponteiro para commit inexistente no remoto.

## 9. Resultado esperado de uma boa operação com agentes

O uso do agente deve reduzir:

- execução mecânica;
- retrabalho;
- inconsistência documental;
- dependência de contexto implícito;
- custos operacionais desnecessários.

Ao mesmo tempo, deve aumentar:

- clareza;
- rastreabilidade;
- velocidade de diagnóstico;
- consistência entre código, docs e operação.
