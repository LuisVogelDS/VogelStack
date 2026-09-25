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

## 2. O arco

A ordem abaixo funcionou para decisões sobre uma base (clientes, assinantes, contratos).
Cada passo responde a uma pergunta que, sem ele, volta como interrupção no meio da reunião.

1. **O que aconteceu.** Linha do tempo com o volume de cada evento. Serve para quem chegou
   agora entender por que a base está como está.
2. **Onde cada um está hoje.** Composição do todo em caixas **mutuamente exclusivas**: cada
   unidade cai em exatamente uma, e as caixas somam o total da base. Se somam mais, há
   dupla contagem; se somam menos, há alguém fora de todas. Barra empilhada para a
   proporção, tabela para o número exato, painel de detalhe ao clicar numa caixa.
3. **O que se dizia e o que os dados mostram.** Cada frase dita antes (na reunião
   anterior, no e-mail) num cartão; virado, o cartão mostra o número medido e se confere,
   confere em parte ou não confere. É o slide que mais muda a decisão.
4. **O caminho de cada caso.** Para cada tipo de unidade, o que acontece com ela a partir
   da decisão, passo a passo. Mapa de estados com um marcador que anda pelas setas, ou
   simulador quando há parâmetro a escolher.
5. **O que precisamos.** Três colunas: o que é nosso, o que precisa do OK de alguém, o que
   ainda precisa ser decidido e até quando.
6. **Apêndice de fontes.** Cada número com a regra que o define e a consulta que o
   produziu. Ninguém lê durante a reunião; todo mundo abre depois.

## 3. Regras

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

## 4. Públicos e variantes

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

## 5. Antes de sair da máquina

1. Rodar a medição de novo e remontar todas as variantes.
2. Verificar cada arquivo montado: nenhum travessão no texto (incluindo as strings do
   script, que é de onde sai o texto das fases), nenhum marcador de montagem sobrando,
   nenhum padrão de dado pessoal, nenhum nome da lista de proibidos da variante.
3. Percorrer todos os slides e todas as fases num navegador automatizado, clicando no que
   é clicável, e reprovar se a página lançar erro.
4. Tirar print de cada slide no estado final e olhar. Sobreposição de texto, rótulo que
   quebra e barra que não cresce só aparecem assim.

## 6. Onde cada coisa fica

- O **deck** mora no projeto que ele descreve, ao lado do script de medição, porque a
  medição usa as regras e o acesso daquele projeto.
- O **kit** (estilo, motor, montagem, verificação) mora num repositório de quem adota,
  que pode ser o mesmo dos outros artefatos visuais dele. Se ele guarda também o acervo
  de decks já apresentados, que é o que torna o kit útil de verdade, esse repositório é
  **privado**, e o acervo fica fora de qualquer rotina de publicação: tem números reais
  de cliente.
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

