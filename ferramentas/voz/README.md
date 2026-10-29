# voz.py

Narração para vídeo com edge-tts (gratuito) ou ElevenLabs (pago), numa ferramenta só. Substitui três scripts: `03-voz/voz.py` da esteira Cajuice, `voz.py` do vídeo do Presto e `texto_elevenlabs.py` + `narracao_guia.py` do vídeo do Guaraci. Um arquivo, só biblioteca padrão mais `edge-tts` (`pip install edge-tts`) e um ffmpeg (`FFMPEG`, PATH, `ffmpeg-static` numa pasta acima, ou `imageio-ffmpeg`).

## Regras de custo

- `--checar` não gasta nada. Mostra os caracteres, o que seria gerado (o resto está em cache), os créditos estimados, o gasto acumulado contra o teto e, se houver chave, a conta e a voz. Rode antes de toda geração paga e mostre ao dono.
- **Teto:** `--teto N` ou `VOZ_TETO` (padrão 3000 caracteres). Cada geração ElevenLabs soma em `gasto.json` (`{"total", "chamadas": [...]}`) e a seguinte é recusada se passar do teto, antes de qualquer chamada paga. Subir o teto exige autorização de quem paga.
- **Cache:** nada que já foi gerado é pago de novo. As chaves de cache são as dos scripts antigos, então o que já existe em `midia/`/`_midia/` continua valendo (conferido contra a assinatura real do Presto).
- **Chave:** `ELEVENLABS_API_KEY` no ambiente. Na falta, lê só essa variável de um `.env` (`--env`, `VOZ_ENV`, ou `.env` na pasta do projeto e nas acima). Nunca é impressa, gravada ou copiada. O edge-tts não usa chave.
- Créditos estimados = caracteres (x0,5 em `flash`/`turbo`). É estimativa: confira no painel do ElevenLabs.

## Modos

| modo | entrada | saída | cache |
|---|---|---|---|
| `esteira` (padrão com pasta) | `voz.py <pasta>` com `roteiro.md` | `midia/audio/p01.mp3..`, `voz.mp3`, `paragrafos.json`; na pasta, `timings.json` e `voz.md` | hash de cada parágrafo (`--refazer 2,3`) |
| `take` (padrão sem pasta) | `textos/v3-<idioma>.json` ou `textos/<idioma>.json` (lista `blocos` com `id` e `texto`) | `_midia/voz/<idioma>/completa.mp3`, `completa.json` (palavras com tempo), `voz-cache.json` | hash do texto inteiro; `--emendar` refaz da primeira frase alterada em diante |
| `blocos` | o mesmo JSON | um `<id>.mp3` por bloco e `blocos.json` | hash de cada bloco (`--refazer b02`) |

`--exportar-texto` não chama API: grava `texto-elevenlabs.txt` com `<break time="Xs" />` a partir de `pausa_depois` (s) e `pausas_dentro` (`[["trecho", s]]`) de cada bloco, para colar na interface web do ElevenLabs (os modelos multilingual_v2, turbo_v2_5 e flash_v2_5 aceitam a tag; o eleven_v3 não).

## Equivalência com os scripts antigos

| antes | agora |
|---|---|
| esteira: `voz.py canais/x/videos/y --voz V --taxa +8% --refazer 2,3` | igual. `--motor`, `--modelo`, `--estabilidade`, `--estilo`, `--pausa`, `--respiro`, `--pausa-marcada`, `--elenco`, `--sem-aparar` mantidos |
| Presto: `python voz.py --lang pt --checar / --refazer / --emendar` | igual, com `--motor elevenlabs` (o antigo era só ElevenLabs) |
| Guaraci: `python narracao_guia.py pt` | `python voz.py --modo take --lang pt --blocos textos/pt.json --saida narracao_guia/pt` (a voz vem de `voz_guia` do JSON) |
| Guaraci: `python texto_elevenlabs.py pt` | `python voz.py --exportar-texto --lang pt --blocos textos/pt.json --saida narracao/pt`, depois de mover as tabelas `ENTRE`/`DENTRO` para `pausa_depois`/`pausas_dentro` nos blocos |

## Diferenças em relação aos scripts antigos

1. **Padrão do motor:** sempre `edge` (gratuito), inclusive em take/blocos; o Presto antigo só chamava o ElevenLabs. Para pago, `--motor elevenlabs` explícito.
2. **Voz padrão do ElevenLabs:** a do Presto ("Carla", `m151rjrbWXbBqyq56tly`); a esteira antiga exigia `--voz`. Padrões de estabilidade/estilo: 0,45/0,15 na esteira, 0,5/0,1 em take/blocos (os de cada versão antiga).
3. **Teto agora vale em todos os modos.** A esteira antiga não tinha teto. No Presto antigo, `--emendar` não conferia o teto; agora confere sobre o trecho refeito.
4. **`--checar` não altera a conta.** O antigo do Presto adicionava a voz da biblioteca à conta; agora só consulta. A adição acontece na geração.
5. **Chave:** os antigos liam `.env` por caminho fixo (`conteudo/.env`). Agora o `.env` é procurado na pasta do projeto e nas acima. O Presto está fora da árvore de `Cajuice/conteudo`; defina `ELEVENLABS_API_KEY` ou `VOZ_ENV` apontando para esse `.env`.
6. **`gasto.json`** ganhou `quando`, `modo` e `motor` em cada chamada; `total` e `chamadas` seguem como antes. Esteira grava o seu em `midia/audio/gasto.json` (o Presto, em `_midia/voz/gasto.json`).
7. **Edge em take/blocos grava tempo por palavra** (`completa.json`), que o render do Presto já prefere ao Whisper. Se o serviço não devolver fronteiras, não grava `completa.json` e o render cai no Whisper.
8. **`--lang`** aceita qualquer idioma (o antigo só `pt`). `voz.md` não repete mais o aviso de publicação com edge-tts da Cajuice: essa decisão fica na documentação do canal.
9. **Cauda da emenda:** idêntica à antiga (`completa-anterior.mp3`, `cauda.mp3`).

## Local do projeto

`--base` (padrão: a pasta do script, se tiver `textos/`; senão a pasta atual). Copie o `voz.py` para a pasta do vídeo para o comportamento do Presto (`python voz.py --lang pt`), ou rode do canônico com `--base`.
