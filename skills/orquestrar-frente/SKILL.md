---
name: orquestrar-frente
description: Divide um trabalho em frentes paralelas e delega a subagentes, com contrato, teto de turnos e critério de pronto. Use quando for disparar vários agentes, planejar delegação, escolher tipo/modelo/esforço de subagente, escrever o prompt de disparo, recolher e conferir o que voltou, ou quando o usuário mandar uma lista de pedidos para avaliar. Cobre plano, executor, validador e corretor.
---

# Orquestrar frentes

## 1. Dividir ou não

Divida quando as frentes são independentes (ou só se encontram no fim), cada uma cabe num contexto e volta como conclusão curta, e a conclusão vale mais ao orquestrador que o material bruto.

Não divida quando a tarefa cabe num contexto só, as frentes tocam os mesmos arquivos, ou cada passo depende do anterior. Medida de "cabe": o orquestrador faz direto o que fecha em umas 15 chamadas e sem recurso caro de máquina; acima disso, vai para um tipo.

## 2. Coletar, diagnosticar, planejar

- Enquanto o usuário manda pedidos, a sessão está em coleta: registre as palavras dele num documento do projeto e espere. Na dúvida se a lista acabou, pergunte.
- Depois, diagnóstico numa leva só, um leitor por território de código (não por pedido). Pergunta nova sobre território já lido vai ao agente que o leu.
- O custo de cada item sai do diagnóstico, nunca de palpite. Item de gosto vira pergunta de design ao dono.
- O plano nasce também do registro vivo de pendências do projeto (o quadro), não só da última fala. Antes de disparar, varra o que ficou estacionado em rodadas anteriores sobre cada território. A frente que remonta algo do zero recebe essas pendências no contrato, e confere se as correções feitas só na versão velha passaram para a nova. No fechamento, o quadro é atualizado. Em 09/11/2026, seis pedidos de um jogo voltaram como repetidos porque a remontagem do mapa leu só a fala do dia.
- Antes de disparar, diga ao usuário quantas frentes e a ordem de grandeza do custo.

## 3. Contrato de frente (um por frente)

1. Entrega: o que volta, numa frase.
2. Território: arquivos e recursos que só ela altera; o que só lê.
3. Formato de retorno: conclusão, lista estruturada ou diff. Nunca despejo de arquivo.
4. Critério de pronto: como o orquestrador saberá que terminou bem.
5. Orçamento: teto de turnos (em geral 2; o segundo fecha sem pedir terceiro), cada teste roda uma vez, poucas imagens, o que cortar primeiro. Vai no prompt do primeiro disparo.

Frente que altera território vizinho trabalha num worktree próprio; frente que só lê não precisa. Frentes que dividem recurso caro (motor de jogo, build, bateria) não o usam: escrevem código e testes, conferem com checagem barata e entregam. O orquestrador roda tudo numa sessão só e chama o corretor apenas para o que falhar.

Frente em repo Unity: se o plugin `vogel-stack-gamedev` estiver instalado, o prompt de disparo começa pelo bloco fixo da skill `vogel-stack-gamedev:brief-repo-unity` (repo e versão, leitura obrigatória, regra da fila, git, formato do relatório); o contrato acima vem depois dele.

## 4. Tipo, modelo e esforço

Os tipos de subagente (executor, corretor, leitor, mecânico, especialista, arquiteto, validador) têm modelos em `vogel-stack/agentes/` (o `README.md` de lá explica cada tipo), para copiar em `~/.claude/agents`; o roteamento de modelo mora na definição de cada agente. Escolha o tipo pelo trabalho e não copie a tabela.

- O plano traz o tipo por item delegado e o disparo o segue. Discordar exige motivo na descrição (`[opus: física do corpo]`).
- Sobe-se um degrau só por sinal objetivo: bateria ou teste reprovado, build quebrado, recusa do usuário. Esforço antes de modelo.
- Corretor que falhou duas vezes (a segunda com evidência nova) sobe para especialista, sem tentativa do orquestrador no meio.
- Prompt de correção traz sintoma e evidência; a hipótese vai marcada como hipótese. As falhas da mesma rodada vão juntas.
- Muitas imagens vão para um leitor. O orquestrador lê só as 2 ou 3 que vão ao dono e confere as aprovadas por amostra.
- O tipo vale por turno: o turno que só compila, testa e relata desce para executor.

Fluxo típico: plano, executor, validador (quando o risco justifica), corretor (só se reprovar).

### Modo extensivo (sobra de cota)

Esta subseção só vale quando o dono pede, com essas palavras ou parecidas, para gastar a sobra. Fora disso, vale o resto do §4 e ela pode ser ignorada.

Quando o dono pede para aproveitar a sobra da cota ("gastar o crédito", rodada noturna, "não economizar"), a sobra compra mais escopo, e não modelo mais caro. Assim, entram mais frentes, mais revisão independente, mais teste de borda e as frentes extras do plano. Já o roteamento de modelo das definições de agente continua valendo: executor e corretor em Sonnet; leitor, mecânico e validador em Haiku.

- Opus fica para o trabalho que de fato o pede: especialista (física, câmera, concorrência, depuração que já falhou), arquiteto, e frente visual cujo critério de pronto é julgamento de imagem. Cada frente em Opus leva o motivo na descrição, como em `[opus: câmera no ar]`.
- Esforço alto pode subir junto com o escopo; modelo, não.
- O contexto de cada frente fica abaixo de uns 150 mil tokens. Acima disso, a frente reveza (skill `revezar-turno`), porque cada chamada relê o contexto inteiro.
- Frente não espera recurso caro (Unity, build, bateria) em primeiro plano por mais de alguns minutos: a regra do §3 continua, e a sobra de cota não a suspende.
- Antes de disparar, o orquestrador diz ao dono quantas frentes vão em Opus e por quê.

Origem: numa rodada de 29 frentes (noite de 08 para 09/11/2026), "gastar o crédito" virou Opus com esforço alto em todas elas, inclusive leitores, mecânicos e corretor. A noite levou 34 pontos da cota semanal, e a medição posterior estimou que a mesma entrega caberia em cerca de metade. As duas frentes em Sonnet entregaram o pedido sem perda de qualidade.

## 5. Quem delega recolhe

- Entregue o resultado integrado, não "disparei e aguardo". Não encerre com frente rodando.
- Frente que diz "pronto" sem evidência (teste, saída, caminho) conta como não verificada.
- O relato chega ao orquestrador; o que importa ao usuário sai na síntese.
- Entrega que sai da máquina (publicação, deploy, texto a cliente, área sensível): checagem determinística primeiro, depois revisão por frente de contexto limpo, que recebe só o pedido e o resultado.
- Decisão de desenho: algumas frentes com ângulos diferentes, sem ver umas às outras, e síntese. A discordância vai ao usuário.
- Correção do dono que vale para todo trabalho do tipo vira regra por escrito no mesmo dia, com data, exemplo e porquê.

Revezamento de frente longa: skill `revezar-turno`. Ponto de partida do repositório: skill `antes-de-editar`.

Referência completa: `vogel-stack/operacao-agentes.md` §1.5 e §2.3.
