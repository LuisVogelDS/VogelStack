---
name: video-produto-html
description: Produz vídeo de divulgação 16:9 de um app ou site real a partir de um palco HTML que desenha tudo em função do tempo, fotografado quadro a quadro com Playwright e codificado com FFmpeg. Use quando o pedido for vídeo de apresentação, demo ou divulgação de um produto que roda no navegador, com ou sem narração, em um ou mais idiomas. Não serve para vídeo de canal com personagem desenhado nem para gravar jogo em motor próprio.
when_to_use: Pedidos como faz um vídeo do produto, vídeo de divulgação do app, demo em vídeo do site, narrar o vídeo, renderizar o palco, ou vídeo vertical 9:16 (pendência, ver reference.md).
---

# Vídeo de produto em HTML

O vídeo é uma página que desenha cada quadro em função de `t`; um script a fotografa e entrega as imagens ao FFmpeg. A tela do produto é a matéria-prima, e o que se anima é moldura, texto, zoom e passagem entre cenas. Corrigir no palco custa minutos; depois do render custa o vídeo inteiro.

## Antes de começar

1. Procure `roteiro.md` e `README.md` na pasta do vídeo do projeto (`<produto>/divulgacao/video/` ou semelhante). Se já existe uma versão, a nova ganha sufixo (`-v2`) e a anterior fica intacta.
2. Confirme com o dono: para quem o vídeo vende, idioma(s), com ou sem voz, e o que o produto ainda não faz e o vídeo não pode mostrar.
3. Dado fictício na demonstração. Nenhum dado de cliente entra na tomada.

## Passos

Cada passo termina numa parada que só uma pessoa libera. Não avance sem o sim.

1. **Roteiro.** Tabela de cenas (número, tempo, o que acontece, texto de tela) mais a direção. Parada: o dono aprova o roteiro antes de qualquer captura.
2. **Captura.** Script Playwright do projeto dirige o app como usuário e grava JPEGs em `_midia/tomadas/<tomada>/` com um `meta.json` (quadros e caixas a destacar). Roteiro só fecha depois de olhar as tomadas: ele precisa caber no que o app sabe fazer.
3. **Palco.** `palco/index.html` expõe `window.seek(t)` (pode ser assíncrona) e `window.stageReady`; sem `Math.random` nem relógio de parede; fontes e imagens locais em `palco/`. Fora do modo `render`, toca em tempo real com barra de arrastar. Parada: prévia no navegador aprovada.
4. **Voz, opcional.** Duas passadas: o roteiro e o palco se ajustam com a voz-guia gratuita (`edge`); a paga só depois da prévia aprovada. Use `ferramentas/voz/voz.py` do VogelStack. Sempre `--checar` antes e mostre ao dono caracteres, créditos estimados, voz e teto. Parada: sem autorização escrita do gasto, o vídeo anda mudo ou com a voz-guia, e nenhuma amostra paga sai por conta própria.
5. **Render.** `python ${CLAUDE_SKILL_DIR}/scripts/render_palco.py --palco palco/index.html --linha _midia/linha-pt.js --consulta "render&lang=pt" --saida _midia/out/video-pt.mp4 [--audio voz.mp3]`. Saída: 1920x1080, 30 fps, H.264 `-crf 17`, `yuv420p`, `+faststart`. O render aborta requisição externa (sem rede) e sai com erro se o palco lançar exceção. Para conferir um trecho: `--de 49 --ate 61`.
6. **Verificação (laço, abaixo).**
7. **Folha de contato e capa** (um quadro a cada 2 a 3 s, lado a lado) para a revisão ser sobre quadros apontados. Parada: pessoa confere folha e arquivo final.
8. **Publicação é humana.** Entregue o vídeo com título, descrição e legenda no mesmo idioma de cada versão; quem publica ou envia a cliente é uma pessoa.

## Verificação (laço)

Rode depois de cada render completo:

```
python ${CLAUDE_SKILL_DIR}/scripts/conferir_video.py _midia/out/video-pt.mp4 --duracao <total da linha> [--audio | --mudo] [--preto-ate-fim 0.5]
```

Confere duração (±0,5 s), resolução, fps, `h264/yuv420p`, `faststart`, áudio presente e audível (ou ausente, em `--mudo`) e quadros pretos fora das margens de fade declaradas. Sai com código 1 se qualquer item falhar.

Se falhar, corrija na origem e rerenderize **a partir do passo que produz o defeito**, nunca remendando o MP4:

| falhou | volte ao passo |
|---|---|
| duração diferente da linha | 5 (veja se `--duracao` bate com a linha; se o palco encurtou, 3) |
| resolução, fps, codec, faststart | 5 (argumentos do render) |
| sem áudio ou mudo | 4 se a voz falta; 5 se o `--audio` não entrou |
| preto no meio | 3 (cena sem tomada ou `stageReady` resolvendo cedo); recapture em 2 se a tomada está vazia |
| erro de JavaScript ou rede abortada | 3 (fonte ou imagem fora de `palco/`) |

Teto: **3 rodadas** de corrigir e rerenderizar. Na terceira falha, pare e entregue ao dono o relatório do `conferir_video.py`, o que já foi tentado e a hipótese da causa. Passou no script ainda não é aprovado: olhe a folha de contato.

## O que fica no projeto

Captura (conhece as telas e o banco de demonstração), palco (cenas, atores, identidade visual), `textos/<idioma>.json`, e a montagem de linha do tempo e trilha. Os scripts desta skill fazem só o genérico: palco com `seek(t)` para MP4 e conferência do arquivo.

Estrutura de pastas, regras de qualidade do vídeo de produto, sincronia de voz com cena e pendências (9:16): [reference.md](reference.md). Leia quando for montar o palco, a voz ou a folha de contato.
