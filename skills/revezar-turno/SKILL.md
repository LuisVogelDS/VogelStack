---
name: revezar-turno
description: Encerra um turno de agente longo com nota de passagem e prepara o turno seguinte em agente novo. Use quando uma frente chega perto de 80 chamadas, quando o contexto de um subagente pesa, ao escrever o prompt de um turno 2, ou ao receber uma nota de passagem para continuar o trabalho.
---

# Revezar turno

Num agente longo quase todo o gasto é o contexto relido a cada chamada, e ele cresce com o quadrado do número de chamadas. A frente continua uma só, com o mesmo escopo e o mesmo item do plano; o que muda é o agente.

## Quem está encerrando (perto de 80 chamadas)

Pare e escreva a nota de passagem, curta:

- o que foi feito (com caminhos);
- o que falta;
- arquivos e trechos que importam (`arquivo:linha`);
- o que já se descartou e por quê;
- evidência pendente (teste a rodar, foto a conferir).

Entregue a nota ao orquestrador e termine. Não peça terceiro turno para fechar o que já estava no teto.

## Quem recebe

O turno seguinte é um agente novo, de contexto limpo, com o mesmo item do plano, que nasce da nota. Leia o trecho, não o arquivo. O tipo vale por turno: se o que resta é compilar, testar e relatar, use executor e registre o motivo na descrição (`[sonnet: turno 2 é compilar, testar e relatar]`).

## Conversa principal

A conversa do orquestrador segue no mesmo fio e compacta quando pesar; a passagem para conversa nova fica a critério do usuário. Assunto novo, que não depende do que a conversa sabe, vai melhor numa conversa nova.

Referência: `vogel-stack/operacao-agentes.md` §2.3 (Revezamento em vez de agente longo).
