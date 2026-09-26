# Apresentações que mostram de onde vem cada número

Método para montar a apresentação de uma reunião de decisão quando a conversa depende de
números: quantos são, quanto devem, quantos serão afetados. O formato é uma página HTML
autocontida, que anda por fases quando quem apresenta pede e que lê os números de um
arquivo gerado pela medição.

Este documento descreve o método. A ferramenta que o implementa (núcleo de estilo, motor
de fases, montagem e verificação) fica **fora da stack**, num kit próprio de quem adota,
pelo mesmo motivo do princípio nº 19 ([[principios#19. Problema, não tecnologia|Problema, não tecnologia]]):
a stack diz o que resolver e como saber se ficou resolvido, não carrega o aparato.

## 1. Quando usar

Vale o trabalho quando:

- a reunião vai **decidir** algo e cada lado chega com um número diferente de cabeça;
- o público mistura quem conhece o dado e quem só conhece a operação;
- alguém vai precisar, depois, responder "de onde saiu esse número?".

Não vale quando a mensagem cabe num texto de cinco linhas, quando não há número em
disputa ou quando o público só precisa de um status. Uma planilha resolve melhor um
relatório de acompanhamento.

## 2. As perguntas

Cada passo abaixo responde a uma pergunta que, sem ele, volta como interrupção no meio da
reunião. **O que se reaproveita de um deck para o outro são as perguntas.** A forma entre
parênteses é a que funcionou no primeiro caso (uma decisão sobre a base de sócios de um
clube) e está aqui para mostrar que a pergunta tem resposta visual, não para ser repetida:
a forma de cada deck sai do §3.

1. **O que aconteceu.** Serve para quem chegou agora entender por que a situação está como
   está. (Lá: linha do tempo com o volume de cada evento.)
2. **Onde cada um está hoje.** A composição do todo em partes **mutuamente exclusivas**:
   cada unidade cai em exatamente uma, e as partes somam o total. Se somam mais, há dupla
   contagem; se somam menos, há alguém fora de todas. Essa regra vale sempre; a forma não.
   (Lá: barra empilhada, tabela e painel de detalhe.)
3. **O que se dizia e o que os dados mostram.** A frase dita antes (na reunião anterior, no
   e-mail) contra o número medido. É o slide que mais muda a decisão, e só existe quando
   houve frase de verdade: frase inventada para ter o que desmentir é espantalho.
   (Lá: cartões que viram.)
4. **Como a coisa funciona, ou o caminho de cada caso.** O mecanismo que produz o número:
   por que custa o que custa, para onde cada unidade vai depois da decisão. É aqui que o
   deck mais ganha com o §3. (Lá: mapa de estados com um marcador andando pelas setas.)
5. **O que precisamos.** O que é nosso, o que precisa do OK de alguém, o que ainda precisa
   ser decidido e até quando.
6. **Apêndice de fontes.** Cada número com a regra que o define e a consulta que o
   produziu. Ninguém lê durante a reunião; todo mundo abre depois.

Nem todo deck tem as seis, e a ordem pode mudar. Um deck sobre custo pode ser quase todo
passo 4, um slide por mecanismo.

## 3. A forma sai do mecanismo

O slide que fica na memória de quem assistiu é o que transforma o mecanismo por trás do
número num **objeto do mundo do cliente que se comporta como o número**. Não é
decoração: o objeto é o argumento. Um deck sobre o custo de um banco de dados gerenciado
achou quatro, e cada um responde a uma pergunta diferente:

| o mecanismo | o objeto | o que ele prova sem legenda |
|---|---|---|
| o banco cobra por ficar ligado, e só uma fatia é trabalho | um **tanque** com piso cinza fixo e a parte do trabalho por cima, na proporção medida | cortar frequência só mexe na fatia de cima |
| o extrator relê a tabela inteira a cada rodada para achar o que mudou | um **livro** de páginas empilhadas com um feixe varrendo todas, e uma única página nova acesa | a razão entre o lido e o mudado, antes do número aparecer |
| pagar por operação contra plano fechado | dois **taxímetros**: um correndo, outro parado no valor fixo | onde fica o ponto de virada |
| um cliente novo tem quantas vezes o tamanho do anterior | dois **prédios** na mesma escala | o custo de entrada escala com a altura |

Nenhum desses quatro serve a outro domínio. O que se transporta é o jeito de chegar a eles:

1. **Qual é o mecanismo?** Não o número: o que no mundo real faz o número ser esse.
   "Paga-se por hora ligado", "compra-se pela intuição e o que sobra vence", "relê-se tudo".
2. **Que objeto do mundo do cliente se comporta assim?** De preferência algo que quem
   assiste já viu funcionar: gôndola, balança, taxímetro, livro, caixa, fila, relógio de
   ponto. Objeto do mundo **dele**, não do nosso: para um mercado, o que ele vê todo dia.
3. **O objeto obedece aos dados?** Tamanho, quantidade e velocidade saem do `dados`, na
   proporção medida. Um tanque desenhado à mão que não muda quando a medição roda de novo é
   ilustração, e ilustração mente quando o número mudar.
4. **O que cada fase faz o objeto fazer?** As fases andam o mecanismo (o feixe varre, a
   página nova acende, o número conta), não revelam blocos de texto.
5. **O que ele prova?** Dá para dizer o título do slide só olhando o objeto na última
   fase. Se não dá, ele é enfeite e o slide volta a ser tabela.
6. **Qual é a versão parada?** Na impressão e sob movimento reduzido, o estado final
   desenhado de uma vez.

**Componente genérico é apoio, não protagonista.** Barra, tabela, cartão e três colunas
resolvem o número exato, o apêndice e o fechamento. Quando mais da metade dos slides é
componente pronto com dado trocado, o deck foi montado por cópia (princípio nº 23,
[[principios#23. Exemplo passa adiante o porquê, não a forma|exemplo passa adiante o porquê]]),
e vai parecer com o anterior mesmo que cada número esteja certo.

**A ficha vem antes do código.** Para cada slide que responde a uma pergunta, anotar
mecanismo, objeto e o que ele prova, e só então abrir o template. É nessa ficha que quem
encomendou o deck consegue dizer "isso não é a cara deles" antes de o trabalho estar
feito.

## 4. Regras

- **O número sai da medição, nunca do texto.** Um script mede na fonte primária
  ([[principios#20. Integrações de dados devem partir da fonte primária|princípio nº 20]])
  e grava um arquivo de dados. Título, legenda e porcentagem são montados a partir dele.
  Número escrito à mão é o primeiro que fica velho quando a medição roda de novo.
- **A medição é evidência.** O script e o arquivo de dados ficam versionados junto do
  deck, com data e ambiente, conforme [[registro-e-evidencias|Registro e Evidências Operacionais]].
- **Nada anda sozinho.** A seta lateral troca de slide; a vertical anda uma fase dentro
  do slide. Animação que toca no ritmo do autor atropela a pergunta de quem assiste.
- **Fase é estado.** Cada fase redesenha o slide inteiro no estado dela; voltar uma fase
  funciona sem código extra, e entrar num slide pela esquerda mostra o estado final.
- **Detalhe mora atrás de um ícone.** O cartão tem título, número e até três tópicos; a
  explicação longa abre ao passar o mouse no ⓘ. Tópico em vez de frase emendada com
  ponto e vírgula.
- **Cor diz o que significa.** Um conjunto pequeno de cores semânticas (bom, atenção,
  alerta, neutro) usado igual em todos os slides, inclusive nos gráficos.
- **Texto sem assinatura de máquina** ([[principios#22. Texto que chega a humano não deve carregar assinatura de máquina|princípio nº 22]]),
  conferido no artefato montado.

## 5. Públicos e variantes

A mesma apresentação costuma ter mais de um público: a equipe interna, o cliente, às
vezes outro idioma. Cada variante:

- é **derivada** da principal por um script de trocas conferidas. Cada troca afirma que o
  trecho original existe; se a principal mudar e a troca deixar de casar, a derivação
  para, em vez de sair uma variante meio traduzida ou meio desatualizada;
- declara o que **não pode** sair nela: nome de pessoa que disse cada frase, número
  interno, slide de trabalho (um simulador, um calendário). A checagem roda no **arquivo**
  entregue, não só na tela, porque o código-fonte de uma página HTML é legível por quem a
  recebe. Um nome que só existe nos dados de um cartão ainda vai junto;
- nunca é editada à mão depois de gerada.

O que separa a versão interna da externa é uma fronteira de exposição e segue
[[seguranca|Segurança e Privacidade]]: dado pessoal de terceiro não entra nem na versão
interna, só agregados.

## 6. Antes de sair da máquina

1. Rodar a medição de novo e remontar todas as variantes.
2. Verificar cada arquivo montado: nenhum travessão no texto (incluindo as strings do
   script, que é de onde sai o texto das fases), nenhum marcador de montagem sobrando,
   nenhum padrão de dado pessoal, nenhum nome da lista de proibidos da variante.
3. Percorrer todos os slides e todas as fases num navegador automatizado, clicando no que
   é clicável, e reprovar se a página lançar erro.
4. Tirar print de cada slide no estado final e olhar. Sobreposição de texto, rótulo que
   quebra e barra que não cresce só aparecem assim.
5. Olhando os prints em sequência, aplicar o teste do vizinho: trocando o nome do cliente,
   esse deck serviria a outro negócio de outro ramo? Se serve, a forma não saiu do §3.

## 7. Onde cada coisa fica

- O **deck** mora no projeto que ele descreve, ao lado do script de medição, porque a
  medição usa as regras e o acesso daquele projeto.
- O **kit** (estilo, motor, montagem, verificação) mora num repositório de quem adota,
  que pode ser o mesmo dos outros artefatos visuais dele. Se ele guarda também o acervo
  de decks já apresentados, esse repositório é **privado**, e o acervo fica fora de
  qualquer rotina de publicação: tem números reais de cliente. O acervo se consulta pelo
  mecanismo que cada slide tornou visível (§3), nunca como pasta a copiar.
- A **stack** guarda só este método. Nenhum deck real, nenhum dado de cliente, nenhum
  exemplo que identifique alguém.

## 7. Como o agente chega aqui

O método só serve se o agente o encontra **no momento do pedido**, e o pedido quase nunca
diz "use o método de apresentações". Diz "monta uma apresentação", "faz um HTML para eu
visualizar", "prepara uns slides". Sem um apontamento, o agente resolve com o que tem à mão:
uma página de painel, rolável, com gráficos, que não anda por fases, não segue o arco e
não tem apêndice de fontes. Foi o que aconteceu na primeira adoção medida (09/2026): o
método estava no submódulo e o kit no repositório de quem adota, e nada no projeto em que
o pedido chegou apontava para nenhum dos dois.

Por isso, quem adota registra, **no `AGENTS.md` de cada projeto** e, se tiver, nas
instruções globais do seu agente:

- que pedido de apresentação, deck, slides ou "HTML para uma reunião" segue este método;
- **onde fica o kit** (caminho local e, se houver, o repositório), porque a stack não o
  carrega;
- onde fica o acervo de decks já apresentados, para o agente ver o padrão antes de montar.

E o agente, diante de um pedido assim, **procura o método e o kit antes de escolher o
formato**. Se não achar o kit, pergunta onde ele está, em vez de improvisar uma página.
Uma página de painel pode ser o que se quer, mas é uma escolha dita, não o padrão silencioso.

