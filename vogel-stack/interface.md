# Interface com assinatura própria

Método para decidir a forma de uma interface (painel, página, deck, ferramenta interna) sem cair na cara média que o público já reconhece como feita por máquina. É a irmã visual do princípio nº 22 ([[principios#22. Texto que chega a humano não deve carregar assinatura de máquina|texto sem assinatura de máquina]]): lá o tique é o travessão, aqui é a cápsula.

Como em [[apresentacoes|Apresentações]], a stack descreve o método e não carrega o aparato. As implementações de referência ficam nos projetos que as criaram (§11).

## A premissa

Interface gerada tem uma cara média: fileira de cápsulas, cartão de canto arredondado com sombra grande sobre degradê, ícone num círculo colorido em cima de cada título, roxo saturado, vidro fosco sobre o nada, a tela explicando o próprio funcionamento. Nenhum desses elementos é errado sozinho. Juntos, dizem que ninguém decidiu nada.

A resposta **não é um molde** que troca essa cara por outra fixa: seria trocar um padrão por outro. A assinatura é o hábito de **decidir cada elemento pelo lugar onde ele está**, com liberdade para uma escolha arbitrária e com personalidade, desde que alguém a tenha feito olhando. Vale o teste do vizinho do princípio nº 23 ([[principios#23. Exemplo passa adiante o porquê, não a forma|o porquê, não a forma]]) aplicado à forma: se a tela serviria a outro produto trocando o nome, ela não foi desenhada para este.

Por isso há duas metades: as recusas (§1), que valem sempre, e os princípios (§2 a §10), que dizem como decidir, e não o que decidir.

## 1. O que denuncia máquina na forma

Cada item é **padrão a evitar**, não proibição. Pílula e squircle continuam valendo quando são escolha: há marca que pede o botão redondo e lugar onde o cartão arredondado é o certo. O defeito é o padrão repetido sem ninguém ter decidido.

| Tique | O que fazer no lugar |
|---|---|
| Fileira de botões em pílula para escolher uma opção | Dropdown sem moldura (§2) |
| Cartão de canto arredondado em tudo, o *squircle* | Raio decidido por lugar; para separar, fio em vez de caixa (§5) |
| Cartão com sombra grande sobre fundo degradê | Página chapada; colunas soltas separadas por fio de 1 px; fundo leve no hover em vez de elevação |
| Etiqueta em pílula para marcar destaque | Traço, sublinhado, peso do texto |
| Rótulo que explica a interface ("muda na hora", "ouvindo…") | O próprio elemento mostra o estado |
| Vidro fosco sem nada atrás | Vidro só onde há o que ver (§8) |
| Roxo saturado, neon, brilho em repouso | Cor contida; brilho só na interação (§7) |
| Degradê de brilho em barra, fita ou botão | Cor chapada |
| Simetria perfeita: três colunas iguais, ícone, título, duas linhas | Ritmo vindo do conteúdo |

## 2. Expor só o necessário

Poucas opções reconhecíveis à primeira vista (**até três**) ficam à vista, e de preferência lúdicas: só o ícone, com o nome no tooltip (tema claro, suave e escuro como sol, nuvem com sol e lua). **Mais que isso vai para um dropdown.** A pergunta que decide: *bater o olho e entender vale o espaço de tela que ocupa?*

Botões lado a lado têm lugar quando **mostrar todas as opções é a função** e há área para isso sem bagunçar.

O dropdown, em repouso, mostra só o valor atual em texto e um chevron pequeno, sem campo nem borda. Aberto, é um menu com check na opção ativa, e o menu é o único lugar com borda. Descrição de opção mora dentro do menu, não na superfície. Isso complementa o princípio nº 14 ([[principios#14. UX de filtros deve separar intenção de negócio e refinamento técnico|UX de filtros]]): o que é principal fica à vista, mas à vista não quer dizer em fileira.

## 3. Comparação fica aberta

Quando a escolha é de gosto (fonte, fundo, textura, cor), clicar aplica **na hora e no produto inteiro**, e o menu continua aberto para testar a próxima. Fecha com clique fora ou Esc.

## 4. O nome diz o que o controle faz

Rótulo genérico ("Estilo") vira o nome do efeito ("Transparência"). Eixo que mistura duas perguntas se separa ("Moldura" virou Contorno e Sombra). E controles se agrupam **pelo alvo, não pelo tipo**: o que muda cor e fundo junto, o que muda a forma do texto junto, o que vale para cartões e pop-ups junto.

## 5. Forma decidida por lugar

- O raio não é global: balão de fala pede curvatura, controle e menu ficam sem moldura, separação entre coisas é fio.
- Pílula (999 px) e círculo (50%) são, por padrão, forma funcional: status, avatar, contador.
- Controle miúdo leva canto curto (4 a 6 px); raio grande num alvo de 30 px vira pílula torta.
- Controle de navegação mora fora do conteúdo, sempre no mesmo lugar e com o mesmo desenho.

## 6. Textura é eixo próprio, separado da cor

A textura não guarda cor: **lê os tokens da superfície** onde é aplicada, e por isso funciona com qualquer paleta, inclusive personalizada. É **procedural** (gradiente CSS ou SVG em data-URI), nunca imagem, porque imagem não acompanha o tema.

Conjunto que funcionou, catalogado pelo mecanismo:

| Textura | Mecanismo |
|---|---|
| Grão de filme | ruído fractal, `multiply` no claro e `screen` no escuro. O mais versátil |
| Caderno pontilhado | ponto fino em grade; o mais discreto dos cadernos |
| Caderno pautado | linha horizontal e margem na cor do acento |
| Quadriculado | malha fina e malha forte sobrepostas |
| Papel de aquarela | grão de papel e manchas de pigmento em baixa frequência |
| Topográfico | curvas de nível de verdade, por *marching squares* sobre um campo suave |
| Céu | estrelas sorteadas com semente fixa e via-láctea recortada em faixa diagonal |

Arquitetura: camada própria (`aria-hidden`, sem eventos) em `z-index: -1` dentro de uma superfície com `isolation: isolate`, e `fixed` quando vai no corpo da página, para rolar sem repintar. Cada superfície pede a textura pelo nome e tem um dono só.

**A textura nunca compete com o texto.** Texto solto, direto sobre ela, precisa continuar legível; se não continuar, a intensidade baixa.

## 7. Claro e escuro se calibram separados

Nunca o mesmo alfa nos dois: traço claro sobre fundo escuro pede cerca de 1,35 vez mais opacidade. A mesma ideia pode pedir outra leitura em cada tema (nébula colorida sobre fundo claro parece mancha suja, então no claro o céu vira atlas celeste impresso). Acento de marca costuma pedir duas versões: aberto no escuro, onde é cor de fundo, e escurecido no claro, onde é cor de texto.

## 8. Vidro só existe se há algo atrás para ver

Desfoque alto apaga o traço fino de trás e deixa o vidro opaco (3 px de blur já espalham um traço de 1 px por uns 7 px). O vidro que funcionou: tinta de cerca de 24% da superfície, `backdrop-filter: blur(.7px) saturate(1.45)`, um reflexo diagonal, um fio de luz de 2 px no alto, tokens de reflexo e de fio diferentes por tema, e a borda fazendo a separação que o fosco fazia. Sem textura, foto ou movimento atrás, cartão sólido.

## 9. Cor derivada, com contraste validado

Cor de texto derivada de outra cor se calcula em **OKLCH**, com o contraste conferido contra o fundo real (anda-se a luminosidade até passar de 4,5:1). Paleta harmoniza pela saturação parecida, não pelo tom literal. A cor vem do domínio (a farda, a fachada, o produto), nunca da paleta padrão de uma ferramenta.

## 10. Processo: decide-se olhando

1. Antes de integrar, uma **prancha lado a lado**: claro e escuro, cartão sólido, cartão de vidro, texto solto.
2. Quem decide é uma pessoa olhando a prancha. A máquina monta as variantes e mede; não escolhe.
3. Depois de integrar, medição no navegador real, sobre o artefato montado.

## 11. Onde estão as implementações de referência

Fora da stack, nos projetos que as criaram em 01/10/2026:

- **HarpyNest** (`painel/`): `seletor.js` (dropdown sem moldura, com `manterAberto` para comparação), `texturas.js` e a prancha `refino-texturas.html`, e os blocos de vidro, contorno e sombra em `estacao.css`.
- **vitrine** (`base/texturas.js` e `docs/referencias/texturas/`): a mesma biblioteca de texturas lendo os tokens de proposta de cliente, e o documento `docs/ESTETICA.md`, que aplica este método a páginas que vestem a marca de outra empresa.
- **Memória Ram** (decks de setembro): a rodada que trocou cartões e cápsulas por colunas separadas por fio e dropdowns sem moldura.

Quem adota copia o andaime (a biblioteca, o seletor) e decide a forma no próprio domínio. Se o projeto decidir que uma recusa do §1 não se aplica a ele, declara em ADR, como pede o princípio nº 19.
