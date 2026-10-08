# Desenvolvimento de jogos com agentes

Diretrizes permanentes para projetos de jogo em motor com editor pesado (Unity hoje, qualquer um que trave o projeto numa instância só). Nasceram na rodada 7 do Slime, da Cajuice Games, em 07/10/2026. Com cinco frentes de agentes dividindo uma única instância do Unity, cada frente passou de uma hora na fila, e a bateria de 28 testes pagou a abertura do projeto 28 vezes. Como em [[apresentacoes|Apresentações]], a stack descreve o método; a implementação de referência mora no projeto que a criou (§6).

Complementam a [[operacao-agentes|Operação de Agentes]], que já manda tirar do agente as execuções caras e deixar script e log persistentes.

## 1. Uma sessão do motor, vários testes

Abrir o editor custa perto de um minuto (carregar o projeto, recompilar, abrir a cena) e não diz nada sobre o jogo. Por isso o executor de testes em Play aceita **uma lista de roteiros** e roda todos na mesma sessão, trocando de cena entre um e outro, com um resumo único no fim. Abrir o editor de novo para cada roteiro só se justifica quando o roteiro precisa de um editor limpo, e então isso fica marcado no próprio roteiro.

No Slime, três roteiros saíram em 1 min 38 s, dos quais 56 s eram de jogo: a abertura passou a ser paga uma vez.

O mesmo vale para o que vem antes do teste. Gerar cena e prefab (o bootstrap) e testar em seguida são **uma sessão**, não duas: o executor monta e já roda a lista. Montar só uma parte das etapas economiza mais, mas só quando a frente não mexe no que as outras etapas consomem (a cena principal, por exemplo); na dúvida, monta tudo, ainda na mesma sessão.

## 2. Regressão seletiva durante a rodada, completa no fechamento

Cada frente tem um **grupo de roteiros** que cobre o território dela, registrado num lugar só (o script da bateria). Durante a rodada, a frente roda só o próprio grupo e o roteiro novo que escreveu. A bateria inteira é do orquestrador e roda **uma vez, no fechamento**, depois da montagem de todas as frentes.

Assim, cada frente deixa de pagar os testes das outras, e o fechamento ainda pega a interação entre elas. Roteiro novo entra no grupo da frente no mesmo commit em que nasce.

## 3. A instância do motor é um recurso com fila

O editor trava o projeto: dois processos no mesmo projeto se atropelam ou deixam o motor órfão. Daí três regras.

- **Uma fila por projeto**, num wrapper que espera a vez sozinho. Ninguém abre o editor por fora dela.
- **Nunca matar nem envolver a fila em `timeout`.** O motor fica órfão segurando o lockfile, e no Windows isso pode exigir reiniciar a máquina. Para limitar tempo, use o timeout da própria ferramenta do agente ou rode em segundo plano.
- **Paralelismo vem de cópias do projeto**, não de forçar a fila. Uma segunda pasta com um clone do repositório tem o seu próprio `Library` e o seu próprio editor. Ela serve para gerar build só com o que está commitado, enquanto as frentes seguem editando a árvore principal, e serve para dar uma fila a uma frente pesada. O custo é a primeira importação (uma vez) e a memória de dois editores abertos: confira a máquina antes de abrir a terceira.

Durante uma bateria longa, a árvore de trabalho fica congelada para quem testa. Uma frente que edite código no meio quebra a compilação e invalida o resto da bateria (aconteceu na mesma rodada 7). O orquestrador avisa quando a fila é dele, ou a bateria roda na cópia.

## 4. Regulagem de gosto se decide jogando

Agente não acerta feel por tentativa: forma, força, tempos de reação, alcance, cor. Cada rodada de teste empírico gasta tempo e não converge, porque o critério está na mão de quem joga. A regra:

- o agente escolhe um ponto de partida razoável e expõe o valor (Inspector e **painel de desenvolvedor dentro do jogo**);
- o painel lista todos os ajustes registrados, agrupados por frente, com deslizante, valor, restaurar, e vale na hora, sem pausar;
- o valor mexido fica salvo num arquivo fora do repositório e é reaplicado nas sessões seguintes; os testes automáticos ignoram o arquivo e partem do valor do asset;
- quando o dono decide, o agente lê o arquivo e grava os valores no gerador do asset, num commit;
- os testes automáticos cobrem só o que é objetivo: não tremer, não atravessar, não entalar, conservar massa.

O relatório da frente lista as regulagens que ela deixou no painel, para o dono saber o que julgar.

## 5. Medir antes de estimar

Tempo de bateria, de build e de frente sai do log (horário de início e fim de cada passo), não de impressão. Na rodada 7 a estimativa dita foi de duas horas para a bateria e a build. O log mostrou 44 min e 3 min, e o que pesava de verdade era a fila dividida (§3), não os testes. Estimativa errada leva a otimizar o lugar errado.

## 6. Implementação de referência

No Slime (`github.com/cajuice/game-slime`), a ordem segue a das seções:

- **§1:** `Assets/_Slime/Editor/TestePlay.cs` (executor com `-roteiro a,b,c`).
- **§2:** `Ferramentas/testar.py` (grupos por frente, `todos` para o fechamento).
- **§3:** `Ferramentas/unity_batch.py` (a fila).
- **§4:** `Assets/_Slime/Scripts/Nucleo/AjustesDev.cs` com `Scripts/UI/PainelDev.cs` (painel no F1).

O contrato de uso está em `docs/arquitetura.md` do projeto.
