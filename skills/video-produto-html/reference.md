# Vídeo de produto em HTML: referência

Complemento do [SKILL.md](SKILL.md). Os exemplos vêm de dois vídeos feitos assim: o do Presto (Cajuice, 09 a 11/10/2026) e o do Guaraci (USP, 10/2026). Os detalhes de cada um ficam no README da pasta do próprio vídeo.

## Quando usar, e quando não

Serve ao vídeo de produto: mostrar um app ou site real funcionando, em 16:9, para página de venda, YouTube e e-mail de abordagem. Use quando o produto roda no navegador (ou tem demonstração que roda), quando o vídeo precisa existir em mais de um idioma ou versão sem refilmar e quando a tela precisa sair nítida e sempre igual. Vídeo de canal (curiosidade, devlog, ficção) parte de desenho e personagem criados para o vídeo e segue a esteira completa do repositório de conteúdo.

## Estrutura de pastas

```
<produto>/divulgacao/video/
  roteiro.md                 plano cena a cena e regras de direção
  README.md                  o como: comandos, voz, trilha, o que já saiu
  playwright.config.ts       captura (testMatch "*.captura.ts", 1 worker, URL base, fuso)
  capturar.captura.ts        dirige o produto e grava as tomadas
  palco/                     index.html, palco.js, palco.css, fontes/, logo e ícone em SVG
  textos/<idioma>.json       duração de cada cena e textos de tela (e blocos de fala, se narrado)
  render.py                  monta a linha do tempo (cenas, âncoras, trilha) e chama render_palco.py
  _midia/                    fora do git: tomadas/, linha-<idioma>.js, out/, voz/, trilha.mp3
```

A mídia pesada fica fora do git. As fontes ficam em `palco/fontes/`, servidas do disco, para o render não depender de rede. Versão nova ganha sufixo (`-v2`, `-v3`) em captura, textos, palco e saídas.

## Contrato do palco

- `window.seek(t)` posiciona tudo no instante `t`, em segundos. Pode devolver promessa; o render a espera.
- `window.stageReady` resolve quando fontes e imagens carregaram. Sem ele, o primeiro quadro pode sair sem fonte.
- Tudo é função de `t`: sem `Math.random`, `Date.now` nem animação CSS por tempo real. Quem anima em tempo real quebra o determinismo e o mesmo `t` deixa de dar o mesmo quadro.
- Modo `?render` esconde barra de arrastar e controles; sem ele, a mesma página toca em tempo real (prévia).
- A linha do tempo vem de um `_midia/linha-<idioma>.js` (`window.LINHA = {...}`, com `"total"`), gerado pelo `render.py` do projeto. `render_palco.py --linha` lê o `total` dali.

## Voz e sincronia

- **Duas passadas.** Ajuste roteiro e palco com a voz-guia (`edge`, gratuita). A voz paga só depois da prévia aprovada.
- **Ferramenta:** `ferramentas/voz/voz.py` no VogelStack (ver o README ao lado dela). No modo `take`, uma chamada só por idioma, `completa.mp3` e `completa.json` com o tempo de cada palavra. `--emendar` refaz só da primeira frase alterada em diante. Teto de caracteres em `gasto.json`. A chave vem de `ELEVENLABS_API_KEY`, nunca de arquivo versionado.
- **Cortar a fala por cena.** O `render.py` do projeto corta a narração no meio das pausas entre blocos e põe cada trecho na sua cena. A cena dura respiro + fala + o que vem depois, ou o mínimo.
- **Âncoras.** Cada âncora prende um instante da coreografia a uma palavra falada; o palco deforma o tempo da cena em trechos lineares para o instante cair na palavra. O `render.py` imprime, por cena, a duração e o segundo de cada âncora: é a conferência da sincronia, e se refaz sempre que o texto mudar.
- **Trilha.** Opcional, só com licença comercial conferida na fonte; nada de música gerada por IA em vídeo de produto. Na versão narrada, a trilha abaixa cerca de 12 dB sob a fala e volta nas pausas; a voz sobe cerca de 4 dB.

## Regras de qualidade

- **Dinâmico:** nenhum plano parado por mais de uns 3 s; cada cena nasce da anterior em vez de cortar; movimento com assentamento curto no fim, sem quique.
- **Legível:** o celular ocupa uns 75% da altura do quadro; a tela aparece inteira por um instante e depois vem o zoom no trecho que importa.
- **Vende para cada perfil:** mostre uma vez o que muda para quem paga, para quem atende e para o cliente final.
- **Assinatura da marca** discreta no canto o vídeo todo e no título de abertura.
- **Texto público sem travessão:** vale para texto de tela, título, descrição, legenda e e-mail.
- **Dado fictício:** em outro idioma, nomes e moeda se convertem por regra, não à mão; o que ficou sem tradução vai para um arquivo de pendências.
- **Entrega com texto de postagem** em cada idioma, na mesma resposta que entrega o vídeo.

## Captura, em duas formas

O mesmo princípio vale em TypeScript (`@playwright/test`, como o Presto) e em Python (`playwright.sync_api`, como o Guaraci): app no ar com dados de demonstração, um script que o dirige e grava JPEGs numerados mais um `meta.json`. Site estático em outro idioma: sirva por HTTP local em vez de abrir como arquivo, para o tradutor da página funcionar. Mantenha a captura determinística (mesmo banco de partida, mesmo fuso, animações do app esperando acabar antes da foto).

## Verificação além do script

O `conferir_video.py` pega o que se mede. Não pega texto cortado, sobreposição, tomada errada nem fala fora da cena. Para isso: folha de contato, e ouvir a narração junto da imagem em dois ou três pontos de âncora.

## Pendências

- **9:16 (30 s, 1080x1920) para Instagram e WhatsApp:** não existe como opção pronta. O palco precisa de layout vertical e a captura precisa de viewport de celular. `render_palco.py --largura 1080 --altura 1920` já renderiza o que o palco entregar nesse tamanho, e `conferir_video.py` aceita as mesmas medidas. Trate como trabalho novo.
- **Voz em outro idioma ou outro motor:** o `voz.py` fala edge-tts e ElevenLabs; outro serviço exige estender o script.
