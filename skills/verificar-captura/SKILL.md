---
name: verificar-captura
description: Confere as capturas de verificação (PNG e relatorio.txt em Capturas/) de um jogo Unity lendo uma grade em vez de cada foto. Use depois de rodar um teste em Play ou etapa de fotos que grava em Capturas/, ao conferir visualmente uma entrega, ou sempre que houver mais de 3 ou 4 imagens para olhar.
---

# Verificar capturas

Cada imagem lida fica no contexto e é relida a cada chamada seguinte (`vogel-stack/gamedev.md` §6). Vinte fotos soltas pesam vinte imagens para sempre; uma grade pesa uma. As capturas são efêmeras: o agente lê, anota e descarta, e **nunca commita** (`Capturas/` está no `.gitignore` dos jogos).

## Passos

1. **Rodar a etapa que grava em Capturas/**, pela fila do Unity e em segundo plano, sem `timeout` em volta (veja o `CLAUDE.md` do jogo: costuma ser `python Ferramentas/testar.py <grupo ou roteiro>`, que chama `unity_batch.py`). Frente sem direito ao motor não roda: confere o que o orquestrador deixou em `Capturas/`. Anote o horário antes de rodar.
2. **Montar a grade** das capturas novas:
   `python -I "${CLAUDE_SKILL_DIR}/scripts/grade.py" [--desde 30m] [pasta-de-Capturas ...] [--por-pasta 4]`
   Sem argumentos, pega o que é novo desde a última grade (ou da última hora), imprime o resumo de cada `relatorio.txt` (linha `OK:`/`FALHOU:` e as linhas `FALHA`) e grava `Capturas/_grades/grade-<data>-<n>.png`, 12 fotos por página. `--dry-run` só lista; `--tudo` ignora o recorte de tempo; `--por-pasta N` guarda as N mais novas de cada pasta. Sem Pillow, grava HTML e avisa. Código 2 = algum relatório com falha (a grade sai mesmo assim); 3 = nada novo.
3. **Ler o relatório antes das imagens.** Falha de checagem manda: a foto só ajuda a entender o porquê. Depois leia a grade (uma imagem por página; em geral 1 a 3). Só abra uma foto inteira quando a grade levantar dúvida, e uma por vez.
4. **Julgar pelo que o jogador vê.** O critério nasce da foto pela câmera do jogo, não do número: enquadramento, o que está cortado, cor e luz, o que sumiu ou atravessa. Item de gosto (forma, cor, feel) não se aprova sozinho: vai ao dono como pergunta.
5. **Anotar no relatório da frente**: pasta, quantas fotos, resumo do `relatorio.txt`, e uma linha por foto relevante (o que se vê, contra o critério, ok ou problema). Falha repetida de uma bateria é uma linha só com a contagem. Se as capturas forem decidir algo para o dono, cite o caminho de 2 ou 3 e deixe o resto.
6. **Higiene.** `git status` não pode listar `Capturas/`; se listar, o `.gitignore` do repo está errado: avise, não adicione. Capturas e grades ficam onde estão ou são apagadas ao fim da rodada.

Em rodada com várias frentes, as fotos vão para um leitor de modelo menor (`vogel-stack/operacao-agentes.md` §2.3); o orquestrador lê só a grade dele e confere por amostra.
