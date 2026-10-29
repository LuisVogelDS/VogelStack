# Pendências do fortalecimento da stack (28 e 29/10/2026)

Na noite de 28/10, enquanto o Luis estava ausente, a stack ganhou nove skills, cinco hooks, ferramentas canônicas de Unity, de medição e de voz, e um CLAUDE.md no HarpyNest. O que está abaixo ficou para decisão dele, porque mexia em repo com trabalho alheio no meio, em organização de terceiros ou em comportamento que ele usa todo dia.

## Distribuir as ferramentas canônicas

O `scripts/sincronizar-ferramentas.py` só mostrou a prévia (28 destinos com pendência) e nada foi escrito nos jogos. Como a rodada 4 da galinha estava em andamento e o Emanuel também trabalha nesses repos, a cópia ficou para um momento calmo:

1. `python scripts/sincronizar-ferramentas.py` (prévia) e depois `--aplicar`, repo por repo.
2. Conferir o `Ferramentas/unity.json` gerado em cada jogo (o `jogo_exe` vem das versões antigas; o palpite automático erra).
3. Commitar em cada repo e em cada worktree (`slime-r*`, `galinha-*` têm árvore própria).
4. O `voz.py` ainda não está no manifesto. A entrada sugerida está no relatório da frente de vídeo e muda o padrão para edge-tts (o pago vira `--motor elevenlabs`). O Presto passa a precisar de `ELEVENLABS_API_KEY` ou `VOZ_ENV`. O Guaraci é da organização `autoaihub`, então confirmar antes de incluir.
5. `importar_asset.py` exige a `LICENCAS.md` do acervo; na máquina do Emanuel, ele precisa apontar `ACERVO_LICENCAS`.

## CLAUDE.md dos jogos que não foram editados

Ficaram de fora por trabalho alheio no working tree ou por estar atrás do remoto. O texto proposto:

- **slime:** o working tree está em HEAD destacado (`2919e169`, fora de qualquer branch). A proposta está em `2026-10-28-slime-CLAUDE.md.patch`, ao lado deste arquivo.
- **fang-you-very-much** (há `.asset` de URP e `ReferenceImages/` modificados): na linha 7, a fila nunca leva `timeout` nem mata o wrapper, porque o Unity fica órfão segurando `Temp/UnityLockfile`; `Capturas/` nunca é commitada e se lê pela grade (`/verificar-captura`); a linha do Git Bash e as três skills.
- **duct-tape** (um commit atrás do remoto): linha do Git Bash e as skills.
- **GobbleGoblin** (dezenas de `.mat`, `.asset` e `.meta` modificados): regra da fila; build `python Ferramentas/unity_batch.py GoblinBuild.BuildJogo --log Logs/build.log --quem <nome>`; smoke `python Ferramentas/smoke.py [segundos]` sobre `Builds/Jogo/GobbleGoblin.exe` (o CLAUDE.md atual cita `Gobble/Build de desenvolvimento`, conferir); Git Bash e as skills. Em `docs/mcps-e-custos.md:23`, trocar "PixelLab irrelevante" por "PixelLab (assinatura ativa): pixel art 2D, usada para sprites de partícula e efeitos (pixellab_baixar.py, pixellab_para_particula.py); irrelevante para o 3D".
- **Cajuice/conteudo** (dois arquivos de `short-rabiscado` modificados): Short em 1080x1920 a 30 fps e canal longo em 16:9; o render final sai com erro se faltar `midia/audio/trilha.mp3` (`--sem-trilha` libera); vídeo de produto em 1920x1080 a 30 fps, H.264 `-crf 17 +faststart`; o 9:16 do Presto continua pendente.

## Guia de apresentações da 2ms

O `hub-2ms` é pessoal (`LuisVogelDS/hub-2ms`), mas não foi editado. O `README.md` e o `09-com-um-agente.md` do guia deveriam apontar para `vogel-stack/apresentacoes.md` e para a skill `deck-numeros-html`; os arquivos 01 a 08 podem virar resumo, ficando só o que é identidade da empresa (`04`).

## Decisões de comportamento

- **Auto mode no lugar do bypass:** a recomendação atual da Anthropic. Precisa de uma lista do que pode rodar sem perguntar (`/auto-mode-setup` rascunha). Não foi trocado.
- **Escapes dos hooks** (`GUARD_GIT_OK`, `GUARD_UNITY_OK`, `GUARD_PUBLICAR_OK`, `GUARD_VOZ_OK`): o agente consegue pôr o prefixo sozinho, então são aviso e não trava. Para trava absoluta, tirar o escape do hook correspondente.
- **Publicar com confirmação:** em sessão `-p` o "ask" vira recusa mesmo em bypass, por isso ficou "deny" com escape. A troca é a constante `PUBLICAR_DECISAO` em `hooks/guard-conteudo.py`.
- **HyperFrames ou Remotion:** aparecem como alternativas em `Cajuice/conteudo/docs/caixa-de-ferramentas.md`; decidir antes de investir mais no `render.mjs` próprio.

## Outra máquina

Os recados `20261028-02` (primeiro pull do centro de atualizações no HarpyNest) e `20261028-03` (plugin vogel-stack e regras de git no `settings.json`) estão no Pombo-Correio.
