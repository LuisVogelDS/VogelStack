# voz.py

Narração para vídeo com edge-tts (gratuito) ou ElevenLabs (pago), numa ferramenta só. Um arquivo, só biblioteca padrão mais `edge-tts` (`pip install edge-tts`) e um ffmpeg (`FFMPEG`, PATH, `ffmpeg-static` numa pasta acima, ou `imageio-ffmpeg`).

## Regras de custo

- `--checar` não gasta nada. Mostra os caracteres, o que seria gerado (o resto está em cache), os créditos estimados, o gasto acumulado contra o teto e, se houver chave, a conta e a voz. Rode antes de toda geração paga e mostre ao dono.
- **Teto:** `--teto N` ou `VOZ_TETO` (padrão 3000 caracteres). Cada geração ElevenLabs soma em `gasto.json` (`{"total", "chamadas": [...]}`) e a seguinte é recusada se passar do teto, antes de qualquer chamada paga. Subir o teto exige autorização de quem paga.
- **Cache:** nada que já foi gerado é pago de novo; a chave de cache é o hash do texto (e dos parâmetros de voz), então regerar o mesmo texto não custa.
- **Chave:** `ELEVENLABS_API_KEY` no ambiente. Na falta, lê só essa variável de um `.env` (`--env`, `VOZ_ENV`, ou `.env` na pasta do projeto e nas acima). Nunca é impressa, gravada ou copiada. O edge-tts não usa chave.
- Créditos estimados = caracteres (x0,5 em `flash`/`turbo`). É estimativa: confira no painel do ElevenLabs.
- **Guarda:** o plugin traz `hooks/guard-voz.py`, que barra `--motor elevenlabs` sem `--checar` e a chamada direta à API de texto para voz. Com o custo já aprovado, prefixe o comando com `GUARD_VOZ_OK=1`.

## Modos

| modo | entrada | saída | cache |
|---|---|---|---|
| `esteira` (padrão com pasta) | `voz.py <pasta>` com `roteiro.md` | `midia/audio/p01.mp3..`, `voz.mp3`, `paragrafos.json`; na pasta, `timings.json` e `voz.md` | hash de cada parágrafo (`--refazer 2,3`) |
| `take` (padrão sem pasta) | `textos/v3-<idioma>.json` ou `textos/<idioma>.json` (lista `blocos` com `id` e `texto`) | `_midia/voz/<idioma>/completa.mp3`, `completa.json` (palavras com tempo), `voz-cache.json` | hash do texto inteiro; `--emendar` refaz da primeira frase alterada em diante |
| `blocos` | o mesmo JSON | um `<id>.mp3` por bloco e `blocos.json` | hash de cada bloco (`--refazer b02`) |

`--exportar-texto` não chama API: grava `texto-elevenlabs.txt` com `<break time="Xs" />` a partir de `pausa_depois` (s) e `pausas_dentro` (`[["trecho", s]]`) de cada bloco, para colar na interface web do ElevenLabs (os modelos multilingual_v2, turbo_v2_5 e flash_v2_5 aceitam a tag; o eleven_v3 não).

## Padrões

1. **Motor:** sempre `edge` (gratuito), inclusive em take/blocos. Para pago, `--motor elevenlabs` explícito.
2. **Voz padrão do ElevenLabs:** uma voz da biblioteca compartilhada (`m151rjrbWXbBqyq56tly`); troque com `--voz`. Estabilidade e estilo: 0,45/0,15 no modo esteira, 0,5/0,1 em take/blocos.
3. **Teto vale em todos os modos**, inclusive `--emendar`, que confere o teto sobre o trecho refeito.
4. **`--checar` não altera a conta:** só consulta. A voz da biblioteca é adicionada à conta na geração.
5. **`gasto.json`** guarda `quando`, `modo` e `motor` de cada chamada, além de `total` e `chamadas`. O modo esteira grava o seu em `midia/audio/gasto.json`; take e blocos, em `_midia/voz/gasto.json`.
6. **Edge em take/blocos grava tempo por palavra** (`completa.json`), que o render prefere ao Whisper. Se o serviço não devolver fronteiras, não grava `completa.json` e o render cai no Whisper.
7. **`--lang`** aceita qualquer idioma. O aviso de publicação com voz gratuita não é repetido no `voz.md`: essa decisão fica na documentação do canal ou do produto.
8. **Cauda da emenda:** `completa-anterior.mp3` e `cauda.mp3`.

## Local do projeto

`--base` (padrão: a pasta do script, se tiver `textos/`; senão a pasta atual). Copie o `voz.py` para a pasta do vídeo para rodar `python voz.py --lang pt` ali, ou rode do canônico com `--base`.
