---
name: build-entrega
description: Gera a build de um jogo Unity para entregar. Use quando o pedido for "gerar a build", "me dá um atalho para jogar", "manda uma versão para o colega" ou ao fechar uma rodada com build. Faz a build pela fila do Unity, cria o atalho na área de trabalho, zipa com data e commit quando for para colega e registra a linha em docs/builds.md ou no changelog.
---

# Build para entregar

A build é a única coisa que o dono (ou o colega) joga, então ela tem de ser a do commit que se diz entregar, gerada pela fila e conferida. O motor trava o projeto: build fora da fila, ou com o jogo de alguém aberto, corrompe `resources.assets`.

## Passos

1. **Ponto de partida.** `git status` e `git log -1`: a build sai do que está no disco, então Assets/ProjectSettings sem commit entram na build sem constar no registro. Leia no `CLAUDE.md` e em `docs/ferramentas.md` (ou `docs/builds.md`) do jogo qual método gera a build, em que pasta ela cai e quais argumentos ela aceita (hoje: Galinha `Galinha.Editor.BuildGalinha.BuildDev|BuildJogo`, Fang `FangYou.Editor.Build.Jogo` com `-notas`, GobbleGoblin `GoblinBuild.BuildJogo`). Não chute o nome do método.
2. **Build pela fila**, em segundo plano e **sem `timeout` nem matar o wrapper** (o Unity fica órfão segurando `Temp/UnityLockfile`):
   `python Ferramentas/unity_batch.py <Classe.Metodo> --log Logs/build.log --quem build`
   Espera a vez sozinha; sai com 3 se desistiu da fila e com o código do Unity senão. Se o exe do jogo estiver aberto, a fila espera: avise o dono em vez de forçar. Leia o fim do log (`Build succeeded`/`error CS`), não só o código de saída.
3. **Achar o resultado.** `python -I "${CLAUDE_SKILL_DIR}/scripts/entrega.py" achar` mostra o `.exe` mais novo de `Builds/` com data; confira que é posterior à build que você acabou de pedir.
4. **Atalho na área de trabalho** (para o dono jogar já):
   `powershell -NoProfile -File "${CLAUDE_SKILL_DIR}/scripts/atalho.ps1" -Procurar -Projeto <raiz> -Nome "<Jogo> (<rodada ou versão>)" [-Argumentos "-mapa X -fps"] [-Log "Logs/jogo.log"]`
   Use `-Exe <caminho>` para uma build específica e `-DryRun -Pasta <pasta de teste>` para testar. Atalho com o mesmo nome é atualizado, não duplicado.
5. **Zip datado, só quando for para colega.** `python -I "${CLAUDE_SKILL_DIR}/scripts/entrega.py" zip [pasta-da-build] [--nome Jogo]` gera `Builds/Entregas/<Nome>-AAAA-MM-DD-HHMM-<commit>.zip` sem símbolos do Burst, `.pdb`, logs e crash handler. Recusa (código 2) com mudança sem commit em Assets, `.exe` mais velho que o último commit ou arquivo com cara de segredo; `--forcar` só com motivo dito no relatório. O zip fica em `Builds/`, fora do git: quem manda é o dono, por fora do repositório. Sócio (Emanuel) recebe o zip, não precisa do VogelStack.
6. **Registro.** `python -I "${CLAUDE_SKILL_DIR}/scripts/entrega.py" linha --versao vX.Y --notas "o que mudou" --anexar docs/builds.md` acrescenta a linha (versão, data, commit, notas) na tabela de builds. Onde o jogo usa `docs/changelog.md` no lugar, escreva a entrada no formato dele, com o commit. Notas em português, no que o jogador percebe.

## O que não fazer

- Não commitar `Builds/`, o zip nem o `.lnk`. A linha do `docs/builds.md` entra no commit da entrega (regra de commit do repo: Cajuice e pessoal commitam sozinhos, adicionando por caminho; 2morrow só sob pedido, com código JIRA).
- Não gerar build com a bateria ou outro agente na fila sem avisar: a fila serializa, mas uma build leva minutos e atrasa quem espera.
- Não afirmar "entregue" sem ter aberto o resultado: o `.exe` existe, é novo, o log terminou sem erro. Se der para rodar com `-batchmode`/smoke que o jogo já tenha (ex.: `Ferramentas/smoke.py` no GobbleGoblin), rode uma vez.

Relatório ao fim: método e log, caminho do `.exe` e data, atalho criado, zip (nome e tamanho) se houver, linha registrada, e o que ficou sem verificar.
