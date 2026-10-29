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
- Antes de disparar, diga ao usuário quantas frentes e a ordem de grandeza do custo.

## 3. Contrato de frente (um por frente)

1. Entrega: o que volta, numa frase.
2. Território: arquivos e recursos que só ela altera; o que só lê.
3. Formato de retorno: conclusão, lista estruturada ou diff. Nunca despejo de arquivo.
4. Critério de pronto: como o orquestrador saberá que terminou bem.
5. Orçamento: teto de turnos (em geral 2; o segundo fecha sem pedir terceiro), cada teste roda uma vez, poucas imagens, o que cortar primeiro. Vai no prompt do primeiro disparo.

Frente que altera território vizinho trabalha num worktree próprio; frente que só lê não precisa. Frentes que dividem recurso caro (motor de jogo, build, bateria) não o usam: escrevem código e testes, conferem com checagem barata e entregam. O orquestrador roda tudo numa sessão só e chama o corretor apenas para o que falhar.

## 4. Tipo, modelo e esforço

Os tipos de subagente (executor, corretor, leitor, mecânico, especialista, arquiteto, validador) têm definição única no HarpyNest (`painel/motor/motor.py`, `TIPOS`, que gera `~/.claude/agents`). Escolha o tipo pelo trabalho e não copie a tabela.

- O plano traz o tipo por item delegado e o disparo o segue. Discordar exige motivo na descrição (`[opus: física do corpo]`).
- Sobe-se um degrau só por sinal objetivo: bateria ou teste reprovado, build quebrado, recusa do usuário. Esforço antes de modelo.
- Corretor que falhou duas vezes (a segunda com evidência nova) sobe para especialista, sem tentativa do orquestrador no meio.
- Prompt de correção traz sintoma e evidência; a hipótese vai marcada como hipótese. As falhas da mesma rodada vão juntas.
- Muitas imagens vão para um leitor. O orquestrador lê só as 2 ou 3 que vão ao dono e confere as aprovadas por amostra.
- O tipo vale por turno: o turno que só compila, testa e relata desce para executor.

Fluxo típico: plano, executor, validador (quando o risco justifica), corretor (só se reprovar).

## 5. Quem delega recolhe

- Entregue o resultado integrado, não "disparei e aguardo". Não encerre com frente rodando.
- Frente que diz "pronto" sem evidência (teste, saída, caminho) conta como não verificada.
- O relato chega ao orquestrador; o que importa ao usuário sai na síntese.
- Entrega que sai da máquina (publicação, deploy, texto a cliente, área sensível): checagem determinística primeiro, depois revisão por frente de contexto limpo, que recebe só o pedido e o resultado.
- Decisão de desenho: algumas frentes com ângulos diferentes, sem ver umas às outras, e síntese. A discordância vai ao usuário.
- Correção do dono que vale para todo trabalho do tipo vira regra por escrito no mesmo dia, com data, exemplo e porquê.

Revezamento de frente longa: skill `revezar-turno`. Ponto de partida do repositório: skill `antes-de-editar`.

Referência completa: `vogel-stack/operacao-agentes.md` §1.5 e §2.3.
