# Operação de Agentes

Este documento define um padrão operacional para projetos que usam agentes de IA como parte do fluxo real de trabalho, conectado a [[registro-e-evidencias|Registro e Evidências Operacionais]].

## 1. Fluxo operacional padrão

Fluxo preferencial, também tratado como Handoff Padrão de Execução:

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

## 1.1 Checklist antes de começar uma alteração

A [[operacao-agentes#8. Checklist antes de concluir uma alteração|§8]] valida a **saída** de uma alteração. Ela não protege contra o caso inverso: a alteração é impecável, mas o **ponto de partida** estava errado. Trabalho correto sobre base velha sobrescreve trabalho novo — e passa em todo teste de saída, porque nada nele está errado.

Em projeto tocado de mais de uma máquina (ou por mais de um agente), o estado local **não sabe** o que foi publicado de outro lugar até alguém perguntar ao remoto. E o Git **não avisa por conta própria**: `git status` só reporta `behind` quando a branch tem upstream configurado. Sem upstream ele diz `working tree clean` — que se lê como "estou em dia", mas significa apenas "não modifiquei nada". A falha é **silenciosa**, contra o [[principios#3. Clareza operacional é tão importante quanto correção técnica|princípio nº 3]] (erros precisam ser visíveis), e a divergência local↔remoto vira dívida **invisível**, contra o [[principios#1. O comportamento documentado deve refletir o sistema real|princípio nº 1]].

Antes de implementar, editar código que vai para produção, ou deployar, confirmar:

1. **houve `git fetch` nesta sessão** — sem isso `origin/<branch>` é uma foto velha, e qualquer comparação mente com cara de verdade;
2. **a branch não está atrás**: `git log --oneline HEAD..origin/<branch>` sai **vazio**. Não usar o `git status` para responder isto;
3. **a branch tem upstream**: `git rev-parse --abbrev-ref '@{u}'` responde. Se não responde, o Git nunca reportará `behind` nessa branch — configurar com `git branch --set-upstream-to=origin/<branch>` antes de seguir. Clone sem upstream é dívida, não detalhe;
4. **o trabalho não commitado é meu**: pendência no working tree pode ser de outra frente ou sessão; separar antes de misturar com a alteração nova;
5. **ao chegar numa máquina**, `pull` antes de qualquer coisa — é o passo 0 da rotina, não uma otimização.

Sinal de perigo, a combinação que mais engana: **working tree limpo + branch sem upstream**. É o estado que mais parece seguro e menos garante que é.

Este piso é verificável por lint determinístico: `check-sync.ps1` (irmão do [[operacao-agentes#7.4 Link checker determinístico como piso da malha|link checker]]) falha quando a branch está sem upstream ou atrás do remoto. Disciplina humana não escala entre máquinas — script escala.

Projeto que consome a stack como submódulo **não precisa copiar o script**: roda direto do submódulo (`./vogel-stack/scripts/check-sync.ps1`), que detecta o superprojeto e checa **o projeto**, não a stack. Copiar criaria uma cópia por repositório para divergir depois — e a prática mostra que o método não pega: na adoção medida em 07/2026, o link checker estava copiado em 2 de 6 consumidores e o `check-quadro` em nenhum, apesar de ambos existirem há tempo. Distribuir pelo submódulo é o mesmo raciocínio do princípio nº 1 aplicado à ferramenta: uma fonte, sem cópia que envelhece calada.

Ao contrário do link checker, **este não é um checker de CI**: no CI o checkout é sempre fresco, e "atrás do remoto" nunca dispararia lá. É uma trava **local**, na máquina de quem vai implementar, antes de começar — que é exatamente onde a falha acontece.

O caso que originou esta seção mostra o custo: um agente preparou uma alteração sobre um working tree 23 commits atrás; subi-la teria revertido uma poda de payload já em produção, inflando os artefatos cerca de 7x, no momento exato em que se adicionava a maior carga da base. Nada teria acusado o erro: **teria parecido um sucesso**.

## 1.2 Mudança que exige ação na outra máquina

O git carrega código e configuração versionada entre máquinas. Não carrega o resto — e é no resto que a troca de máquina quebra em silêncio:

- pasta de projeto renomeada ou movida (qualquer ferramenta que case projeto por nome ou caminho de pasta perde o projeto do outro lado);
- diretório de dados ou configuração que vive **fora** do repositório e mudou de lugar;
- repositório novo que ainda precisa ser clonado do outro lado;
- dependência de ambiente nova (driver, runtime, chave, credencial em cofre local);
- dado que não pode atravessar por git e precisa chegar por outra via.

Nada disso aparece num `git status`, num `pull` ou num diff. A regra: **toda mudança dessa natureza deixa um recado num registro versionado, na origem, antes de encerrar a sessão** — com o que fazer do outro lado e, quando couber, uma verificação de disco que prove que foi feito (a pasta existe, a antiga não existe). O registro viaja com o repositório que o hospeda; na chegada à outra máquina, o passo 0 (`pull`) traz o recado, e um ritual de chegada o lê e confere contra o disco real. Recado que depende de alguém lembrar de abrir um arquivo não é recado — a entrega tem de ser ativa (impressa pela rotina de sync, mostrada no painel).

O que o hub do usuário adota para isso é um **relator** (no Cantin do Fôgueu, o `pombo-correio/`): um ledger com `feito` por máquina, uma CLI de chegada, e um parágrafo curto que todo agente recebe no prompt para saber que precisa avisar. Projeto que consome esta stack e opera de mais de uma máquina segue o mesmo desenho — o essencial é a regra, não a ferramenta.

Complementar à [[operacao-agentes#1.1 Checklist antes de começar uma alteração|§1.1]]: ela protege o ponto de partida do **código**; esta protege o ponto de partida do **ambiente**.

## 1.3 Convivência: mais de um agente no mesmo projeto

A [[operacao-agentes#1.1 Checklist antes de começar uma alteração|§1.1]] trata do outro que trabalhou **antes** de você, noutra máquina. Esta trata do outro que está trabalhando **agora**, no mesmo disco. É o caso mais perigoso dos dois, porque o Git não separa nada: dois agentes no mesmo clone dividem working tree, índice, branch, `node_modules`, pasta de build, porta do servidor de desenvolvimento, arquivo de lock e conexão de banco. Nenhuma ferramenta avisa que há outro ali. O primeiro sinal costuma ser o estrago: um `git add -A` que leva junto o trabalho pela metade do vizinho, um `git stash` que o faz sumir, um servidor derrubado no meio do teste de outro.

A regra de fundo é uma só: **o que você não começou não é seu.** Arquivo, processo, porta, pendência no working tree ou branch que outro agente abriu se lê, não se mexe, até ficar claro de quem é.

### Antes de começar: olhar e anunciar

1. **Procurar sinais de outro agente**: pendência no `git status` que esta sessão não fez, processo ou porta já ocupados, arquivo de lock recente, sessão ativa no painel ou no registro de presença.
2. **Anunciar a própria presença** num registro de presença local do projeto (arquivo fora do versionamento, por exemplo `.agentes/presenca.md` no `.gitignore`, ou o equivalente que o painel do usuário mantenha). Uma linha basta: quem é, qual frente, **quais arquivos ou áreas** vai tocar, **quais recursos** vai ocupar (porta, servidor, banco, migração) e desde quando. É o canal pelo qual os agentes se falam: quem chega lê, quem sai apaga a própria linha.
3. **Se houver sobreposição, resolver antes de editar**: escolher outra área, esperar, ou perguntar ao usuário. Nunca resolver editando por cima.

### Durante: dividir território, não disputar

- **Um dono por arquivo de cada vez.** A divisão ideal é por fronteira natural (módulo, pasta, camada) e não por tarefa miúda que atravessa tudo.
- **Arquivo comum a todos** (changelog, quadro, índice, manifesto de dependências, lockfile) recebe edição pequena e localizada, relida **imediatamente antes** de escrever. Nunca reescrever o arquivo inteiro a partir de uma leitura antiga.
- **Recurso compartilhado tem um dono só.** Quem subiu o servidor é quem o reinicia; quem precisa de outro usa outra porta. Não matar processo que você não iniciou. Migração de banco, instalação de dependência e build limpo (`clean`, apagar pasta de saída) são operações de um agente de cada vez, anunciadas antes.
- **No Git, só o que é seu**: commit por caminho, nunca `git add -A` às cegas; conferir o diff antes e depois de commitar; `git stash`, `reset`, `checkout -- <arquivo>`, `clean` e troca de branch afetam o vizinho e ficam proibidos enquanto houver outro agente ativo no clone. Antes do push, `pull --rebase`; conflito com trabalho alheio se reporta, não se "conserta".
- **Quando a sobreposição for grande, isolar em vez de coordenar**: um `git worktree` por agente dá a cada um seu próprio working tree e índice, e a conversa passa a acontecer só no merge. Isolamento é a coordenação mais barata que existe.

### Quando quem dispara é um orquestrador

Se um agente (ou o usuário) distribui trabalho para vários, o plano vem **antes** do disparo: frentes disjuntas, a ordem das que dependem uma da outra, e o dono de cada recurso compartilhado já decididos. Frente que precisa do resultado de outra espera por ele, não adivinha. O orquestrador é quem junta as partes e resolve os conflitos; os agentes da ponta não se corrigem entre si. Como dividir, planejar e recolher está na [[operacao-agentes#1.5 Orquestração: várias frentes em paralelo|§1.5]].

### Ao sair

Apagar a própria linha do registro de presença, liberar o que ocupou (parar o servidor que subiu, se ninguém mais o usa) e deixar dito o que ficou pela metade. Presença esquecida vale como área bloqueada para sempre.

O custo desta seção é uma linha num arquivo e alguns segundos de leitura. O custo de ignorá-la é trabalho alheio perdido sem rastro, que é o pior tipo de erro pelo [[principios#3. Clareza operacional é tão importante quanto correção técnica|princípio nº 3]]: não aparece, só falta.

## 1.4 Commit e publicação seguem o dono do repositório

Quando e quanto um agente commita e publica não é uma regra única: depende de **quem é dono do repositório**, e o dono se lê no remote, nunca no nome ou na posição da pasta.

- **Repositório próprio do usuário**: commitar e publicar ao fechar cada entrega coerente, sem esperar pedido. Trabalho que fica só no working tree, ou só num commit local, é trabalho que a outra máquina não vê e que um disco perdido leva junto. Commit por entrega, com mensagem que diga o que mudou; publicar logo em seguida; nunca force push.
- **Repositório de terceiros** (empregador, cliente, organização): commit e publicação só sob pedido explícito, seguindo a convenção da casa (código de ticket na mensagem, branch, revisão). Na dúvida sobre a convenção, perguntar; nunca inventar um código de ticket.
- **Em qualquer caso**: só o que a sessão tocou (ver [[operacao-agentes#1.3 Convivência: mais de um agente no mesmo projeto|§1.3]]), nada de segredo ou dado pessoal ([[seguranca|Segurança e Privacidade]]), e mensagem sem assinatura de máquina ([[principios#22. Texto que chega a humano não deve carregar assinatura de máquina|princípio nº 22]]).

A política concreta, com a lista de quais remotes são de quem, vive nas instruções locais do usuário, não aqui: esta stack é pública e não deve carregar o mapa de onde ele trabalha.

## 1.5 Orquestração: várias frentes em paralelo

A [[operacao-agentes#1.3 Convivência: mais de um agente no mesmo projeto|§1.3]] trata dos agentes que se encontram por acaso no mesmo projeto. Esta trata do caso deliberado: um trabalho que rende mais dividido em frentes simultâneas, sob um orquestrador (um agente ou o próprio usuário). Quando as frentes são independentes, paralelizar é o padrão. Fazer em fila o que não depende de fila não é prudência, é tempo do usuário jogado fora.

O nome das peças muda de ferramenta para ferramenta (subagente, sessão paralela, worktree, workflow). O que segue vale para qualquer uma delas, e é de propósito que não cita nenhuma.

### Quando dividir

Compensa dividir quando:

- as frentes não dependem do resultado uma da outra, ou só se encontram no fim;
- cada frente cabe inteira num contexto e volta como conclusão curta: pesquisa ampla, varredura de muitos arquivos, revisão por dimensões, implementação em módulos separados;
- o contexto de quem orquestra ganha mais com a conclusão do que com o material bruto.

Não compensa quando:

- a tarefa já cabe num contexto só. Dividir aí só acrescenta custo de costura;
- as frentes tocariam os mesmos arquivos o tempo todo;
- cada passo depende do anterior. Isso é sequência, não paralelo.

### Planejar junto, antes do disparo

O plano é a peça que mais pesa. Para cada frente, o orquestrador escreve um contrato curto:

1. **entrega**: o que volta, numa frase;
2. **território**: os arquivos, pastas ou recursos que só essa frente altera, e o que ela pode apenas ler;
3. **formato de retorno**: conclusão, lista estruturada ou diff. Despejo de arquivo nunca;
4. **critério de pronto**: como o orquestrador vai saber que a frente terminou bem.

Frente que altera arquivos em território vizinho de outra trabalha isolada num worktree próprio ([[operacao-agentes#1.3 Convivência: mais de um agente no mesmo projeto|§1.3]]). Frente que só lê não precisa de isolamento.

Planejar em conjunto também serve para decidir, não só para executar. Numa pergunta de desenho, algumas frentes independentes, com ângulos diferentes (custo, risco, simplicidade, o que já existe no projeto) e sem ver umas às outras, seguidas de uma síntese do orquestrador, reduzem o viés de uma leitura única. Discordância entre elas é informação: vai para o usuário, não é apagada na síntese.

### Quem delega recolhe

- A entrega do orquestrador é o resultado integrado, não "disparei e estou aguardando". Encerrar com frentes ainda rodando deixa o trabalho delas órfão.
- O que volta é conferido antes de ser repassado. Frente que diz "pronto" sem evidência (teste, saída, caminho do arquivo) conta como não verificada.
- O relato de cada frente chega ao orquestrador, não ao usuário. O que importa ao usuário precisa ser repassado na síntese.
- Delegar de novo o que já cabe numa frente só é profundidade sem ganho.

### Revisar com olhos que não escreveram

Quem produziu uma entrega carrega os mesmos vieses que a produziram, e a autocrítica tende a aprovar. Para entrega que sai da máquina (publicação, deploy, texto para cliente, mudança em área sensível), a revisão fica com uma frente de contexto limpo, que recebe só o pedido original e o resultado. Checagem determinística (teste, lint, link checker) vem antes e continua valendo: a revisão independente pega o que o script não pega, não substitui o script.

### Custo

Frentes em paralelo multiplicam o gasto. O orçamento da [[operacao-agentes#2.1 Orçamento de tokens e alerta antecipado|§2.1]] é da orquestração inteira, não de cada frente: antes de disparar, dizer ao usuário quantas frentes e a ordem de grandeza do custo. O custo não barra a orquestração; o que não pode é o usuário ser surpreendido por ele.

## 2. Política de custo e uso de recursos

Regras:

- evitar gasto desnecessário de créditos, tempo de máquina e recursos externos;
- não disparar instalações, downloads, treinos longos, cargas pesadas ou processos mecânicos sem necessidade real;
- preferir análise estática, comandos prontos e checklists antes de sugerir execuções caras;
- em execuções longas, pesadas ou ruidosas, preferir o padrão `agente prepara, usuário executa, agente interpreta` em vez de gastar créditos acompanhando toda a execução;
- quando uma execução custosa for necessária, explicitar por que ela destrava a tarefa.

## 2.1 Orçamento de tokens e alerta antecipado

O custo de uma tarefa deve ser previsto, não descoberto no fim. Regras:

- antes de mergulhar, **estimar o custo aproximado** de tokens/créditos da tarefa;
- se a projeção for alta (regra prática: acima de ~70k tokens, ou muito acima da média de tarefas similares), **avisar o usuário logo no início** — antes de executar — explicando o porquê e oferecendo recortes menores;
- deixar a decisão de gastar com o usuário; não assumir que escopo grande está autorizado só porque foi pedido em uma frase;
- calibração de referência: tarefas bem escopadas (uma feature, um bug, um conjunto coerente de edições) custam tipicamente uma fração disso. Estouro muito acima da média quase sempre indica escopo grande demais **ou** atrito de ambiente (ver 2.2), não trabalho útil;
- em orquestração com várias frentes ([[operacao-agentes#1.5 Orquestração: várias frentes em paralelo|§1.5]]), a estimativa é do conjunto. Tarefa paralelizada ultrapassa o limiar com facilidade, e o aviso existe para o usuário decidir sabendo, não para desestimular a divisão;
- o usuário reduz custo declarando a barra de aceitação no próprio pedido (ex.: "build verde basta"), apontando arquivos/caminhos relevantes e fatiando entregas grandes.

## 2.2 Resiliência a instabilidade de runtime

Ambiente de ferramentas instável é uma das maiores fontes de desperdício silencioso de créditos. Quando as ferramentas falharem de forma intermitente (ex.: erro de carga de biblioteca, flush de chamadas duplicadas, mesma saída repetida em bloco):

- **parar cedo e avisar o usuário** em vez de insistir contra a instabilidade;
- **não re-disparar comandos pesados** (build completo, scan de diretório inteiro, leitura de arquivos grandes) durante a instabilidade — cada saída grande permanece no contexto e é **re-cobrada a cada turno**, então re-execução cega multiplica o custo de forma composta;
- preferir buscas estreitas (arquivo ou linhas específicas) a varreduras amplas;
- quando o usuário souber de antemão que o ambiente está instável, sinalizar ao agente para que ele ajuste a tática desde o começo.

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

Quando a execução for longa, cara ou muito verbosa, o agente deve preferir entregar um comando ou script com logging persistente.

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

Projetos agent-friendly devem tratar logging como parte de [[principios#8. Observabilidade precisa existir desde cedo|observabilidade]] mínima e prever:

- logs persistidos em arquivo;
- retenção ou rotação;
- separação por superfície, por exemplo backend e frontend;
- mensagens suficientes para que o usuário compartilhe contexto sem precisar reconstruir o problema manualmente.

Em execuções entregues ao usuário, o log não é acessório: ele faz parte do contrato de colaboração entre agente e operador local.

## 7.1 Handoffs explícitos para áreas sensíveis

Quando um domínio do sistema for especialmente crítico, instável ou cheio de contexto acumulado, vale manter um documento de handoff específico.

Esse handoff deve concentrar:

- estado atual do domínio;
- contratos relevantes;
- arquivos-chave;
- checklist de mudança;
- comandos de validação;
- prompt-base para retomada futura, quando isso reduzir retrabalho.

## 7.1.1 Quadro de trabalho conciliado a partir das fontes de demanda

Projetos acumulam **fontes de demanda**: handoffs (§7.1, a fonte canônica), mas também issues, entradas de `intake/`, TODOs. Cada uma deixa "próximos passos" e "decisões em aberto" que envelhecem em ritmos diferentes: parte já foi entregue, parte ainda vale, parte morreu. Ler fonte a fonte para descobrir o que continua aberto é retrabalho, e fonte antiga lida como se fosse atual confunde plano com estado real.

O padrão é manter um **quadro único de trabalho** (ex.: `docs/handoffs/_QUADRO.md`, ou `docs/_QUADRO.md` quando não houver handoffs) conciliado a partir de todas as fontes. Não é um backlog paralelo: é a **projeção viva** do que segue aberto, derivada das fontes e checada contra o repositório. É uma **fila, não um arquivo** — mostra o presente em aberto, não guarda o histórico do que fechou.

**Backlog é status, não arquivo.** O ⚪ do quadro **é** o backlog do projeto: não mantenha um `IMPROVEMENTS.md`, `TODO.md` ou `BACKLOG.md` paralelo — um arquivo desses vira um segundo board competindo pela prioridade, exatamente o conflito que o quadro existe para eliminar. Quando um item precisa de mais que uma linha (um DDL, um plano de features, um diagnóstico), o detalhe vira um **spec doc por tema** — uma fonte de demanda como outra qualquer — e a linha do quadro **linka** a spec em vez de duplicá-la. Ideia crua ou spec funda vive no intake até ser **promovida** a ⚪ quando vira candidata real; a promoção passa pelo gate de [[evolucao-produto|Evolução de Produto e Arquitetura]] ("nem toda melhoria vale a pena depois que um brainstorm redefiniu a direção"). O quadro carrega o backlog **de registro**, não o depósito de "algum dia".

**Reconciliação — o que entra no quadro:**

- cada item é reconciliado contra o **estado real** — git, `reports/`, código, changelog —, não contra o que a fonte dizia que ia acontecer (instancia o [[principios#1. O comportamento documentado deve refletir o sistema real|princípio nº 1]]);
- item ainda aberto **sobe** para o quadro; fonte com tudo fechado **desce** para o arquivo (`docs/handoffs/legado/` ou equivalente) — arquivar não perde nada, porque o que estava aberto já foi capturado no quadro;
- classificar cada item por status legível: 🔴 prioridade · 🟡 em andamento · ⚪ pendente (backlog válido) · 🗄️ defasado (morto, mantido por memória) · ✅ concluído (transitório, ver abaixo);
- manter uma tabela **fonte → veredito** (ativo / legado-concluído / legado-defasado), para que arquivar uma fonte seja decisão auditável e não um sumiço;
- registrar a data da **última reconciliação** e a contagem de fontes (ativas vs legado-candidatas);
- a reconciliação é periódica e **disparada pelo usuário**, não automática: mover fonte para o legado é decisão de quem conhece o estado do projeto.

**Drenagem — para onde vai o item concluído:**

O ✅ é **transitório**: não é uma coluna onde tarefas se acumulam, é um marcador de "isto saiu, drena e remove". Deixar ✅ morar no quadro o transforma, devagar, num changelog ruim e desestruturado. O destino durável segue um **funil**:

- **sempre → changelog** (`docs/changelog.md`): toda entrega vira uma linha datada e granular. É o sink universal — um item do quadro ≈ uma entrada do changelog. Liga ao [[principios#9. Versionamento e rastreabilidade não são opcionais|princípio nº 9]] e ao [[documentacao-e-versionamento#3.05 Workflows com commit automático e mensagem genérica|protocolo de encerramento de rodada]];
- **quando vira arco de versão → versionamento** (`docs/versionamento.md`): se o conjunto de entregas constitui ou avança uma versão (nova capacidade, mudança de produto ou de arquitetura), o arco é registrado **no nível da versão** — escopo, motivação, status (estável/alpha/futuro). Não é cópia 1:1 do item: é o **rollup** editorializado das entregas que o changelog já logou;
- **depois → poda**: na reconciliação seguinte, a linha ✅ já registrada no changelog sai do quadro.

Changelog e versionamento **não se fundem** e têm cadências distintas: o changelog é drenado continuamente, item a item ("o quê / efeito / data"); o versionamento é reconciliado nas fronteiras de versão, resumindo o changelog desde a última versão ("por quê / escopo / status"). Essa divisão de trabalho é o que mantém os dois abastecidos sem duplo-registro manual — e evita a deriva clássica de changelog atrasado, que nada mais é do que trabalho concluído que nunca foi drenado.

Assim o quadro mantém honesta a distinção entre estado atual e legado de [[documentacao-e-versionamento#4. Distinção entre estado atual, experimental e futuro|Documentação e Versionamento §4]]: a fonte é o registro do momento; o quadro é o presente em aberto; changelog e versionamento são o passado materializado, rastreável contra [[registro-e-evidencias|evidência operacional]]. A drenagem e o frescor da reconciliação são verificáveis por um lint determinístico (`scripts/check-quadro.ps1`, irmão do [[operacao-agentes#7.4 Link checker determinístico como piso da malha|link checker]]): ele falha se o quadro acumula uma seção de concluídos em vez de drenar, ou se a reconciliação fica velha demais. Modelo copiável em [[templates|Templates]] (§7.1).

## 7.2 Registro mínimo de execução

Quando o projeto gera artefatos, relatórios, exportações ou resultados por rodada, vale manter um [[registro-e-evidencias|registro explícito de execução]].

Esse registro deve permitir ao agente e ao usuário localizar:

- `run_id`;
- escopo;
- estágio;
- artefatos gerados;
- resultado principal;
- observações de execução.

Isso reduz retrabalho e evita que o agente trate como desconhecido algo que já foi materializado.

## 7.2.1 Regra de Juros Compostos

Quando o agente criar ou orientar a criação de um diretório `reports/runs/<run_id>/`, ele deve tratar essa run como memória futura do projeto e entrada para a malha de documentação.

Regras:

- criar ou atualizar um resumo legível dentro da run;
- registrar quais artefatos foram finais, auxiliares, parciais ou ausentes;
- garantir que o `registry` aponte para o diretório da run;
- escrever nomes e descrições que humanos e agentes consigam encontrar depois;
- deixar explícitas relações com decisões, hipóteses, métricas, erros ou serviços avaliados;
- conectar esses artefatos à malha por wikilinks reais.

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

## 7.4 Link checker determinístico como piso da malha

Wikilink quebrado é dívida visível ([[principios|princípio nº 19]]). Recomendação base para qualquer projeto que use wikilinks como contrato de navegação:

- manter um **link checker determinístico** (script, sem dependência de LLM) que valida que todo `[[wikilink]]` aponta para arquivo existente;
- rodar o checker localmente antes de fechar rodada documental;
- rodar o checker em CI (GitHub Action ou equivalente) em push/PR para branch principal;
- falhar a CI em link quebrado — wikilink que aponta para nada confunde tanto humano quanto agente.

Esse piso é essencial, não acessório: não há relatório materializado para acusar inconsistência, então o checker é a única rede automática da malha ([[operacao-leve|Operação Documental]]).

Implementação de referência (PowerShell, ignora blocos de código, suporta `[[alvo|alias]]` e `[[alvo#secao]]`, com resolução em três pontos âncora) disponível em `scripts/check-wikilinks.ps1` desta stack. Projeto que a consome como submódulo roda o script de lá (`./vogel-stack/scripts/check-wikilinks.ps1`), sem copiar: chamado do submódulo, ele checa o projeto e trata os documentos da stack só como alvo de link.

## 8. Checklist antes de concluir uma alteração

Antes de encerrar uma entrega, validar:

1. se o fluxo principal do projeto continua abrindo;
2. se imports e caminhos continuam válidos;
3. se a documentação foi atualizada quando necessário;
4. se nenhum segredo novo foi exposto;
5. se a mudança não introduziu regressão óbvia nas áreas principais;
6. se o projeto usa workflow de commit automático com mensagem genérica (ver [[documentacao-e-versionamento#3.05 Workflows com commit automático e mensagem genérica|Workflows com commit automático]]), entrada nova no topo de `docs/changelog.md` é parte do encerramento e deve sair antes do sync;
7. se o projeto tem submódulos e o script de sync não entra neles, o `git push` dentro do submódulo precisa ser feito manualmente antes do sync principal, ou o repositório pai vai empurrar um ponteiro para commit inexistente no remoto;
8. se a rodada tocou em `.md`, o **link checker** ([[operacao-agentes#7.4 Link checker determinístico como piso da malha|seção 7.4]]) passou — wikilinks novos resolvem para arquivos reais;
9. se a rodada criou ou alterou algo que passa a **rodar no ambiente** (script de deploy, config de servidor web, `cron`, `systemd`, job agendado), o artefato entrou versionado no repositório — ou a exceção ficou registrada com o motivo. Ver [[principios#21. O ambiente de execução deve ser reconstruível a partir do repositório|princípio nº 21]];
10. se a rodada escreveu texto para humano (documentação, mensagem de commit, relatório, página publicada), ele saiu **sem travessão** e sem os tiques vizinhos, pelo [[principios#22. Texto que chega a humano não deve carregar assinatura de máquina|princípio nº 22]]. Um `grep` por `—` antes de fechar resolve.
11. se a rodada dividiu o projeto com outro agente, a linha no registro de presença foi apagada e os recursos ocupados foram liberados ([[operacao-agentes#1.3 Convivência: mais de um agente no mesmo projeto|§1.3]]);
12. se o repositório é do próprio usuário, a entrega saiu commitada **e publicada** ([[operacao-agentes#1.4 Commit e publicação seguem o dono do repositório|§1.4]]);
13. se a rodada foi orquestrada em frentes, nenhuma ficou rodando sem ser recolhida, e a entrega que sai da máquina passou por revisão de contexto limpo ([[operacao-agentes#1.5 Orquestração: várias frentes em paralelo|§1.5]]);
14. se a rodada removeu de propósito algo que outro agente poderia recriar, a remoção ficou registrada onde se lê antes de implementar ([[documentacao-e-versionamento#4.1 O que foi removido de propósito|Documentação e Versionamento §4.1]]).

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
