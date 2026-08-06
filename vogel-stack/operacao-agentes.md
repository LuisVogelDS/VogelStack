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

Implementação de referência (PowerShell, ignora blocos de código, suporta `[[alvo|alias]]` e `[[alvo#secao]]`, com resolução em três pontos âncora) disponível em `scripts/check-wikilinks.ps1` no projeto Alquimia, que pode servir de template para outros projetos.

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
9. se a rodada criou ou alterou algo que passa a **rodar no ambiente** (script de deploy, config de servidor web, `cron`, `systemd`, job agendado), o artefato entrou versionado no repositório — ou a exceção ficou registrada com o motivo. Ver [[principios#21. O ambiente de execução deve ser reconstruível a partir do repositório|princípio nº 21]].

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
