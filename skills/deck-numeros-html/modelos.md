# Modelos do deck

Quatro arquivos em branco para a pasta do deck. Copie o bloco, preencha e apague o que não se aplica.

## ROTEIRO.md

```markdown
# Roteiro: <tema do deck>

Público: <quem assiste e o que já sabe>. Quem apresenta: <pessoa ou área, ou "circula sem apresentador">.

Contexto (<quem encomendou>, <data>): <por que este deck existe agora>. O deck quer, nesta
ordem: <primeiro objetivo>; <segundo objetivo>.

Números: <script de medição>, <fonte primária>, medida em <data>. <Restrições: um deck por
cliente, nenhum número de outro cliente, nomes de tabela fora etc.>

Cor: <base; cor do cliente como assinatura; cores de módulo ou camada, com o tom de cada uma;
o que fica neutro>.

A confirmar antes de mandar: <afirmações sobre o produto ou o negócio que alguém precisa validar>.

### 1 · <título do slide, que o objeto deve provar>

Pergunta: <a pergunta de quem assiste que este slide responde>
Mecanismo: <o que no mundo real faz o número ser esse>
Objeto: <a coisa do mundo do cliente que se comporta como o número>
Obedece a: <que medida define tamanho, quantidade ou velocidade; ou "nada medido", dito por quê>
Cor: <que cor cada parte do objeto veste, e por quê>
Fases: 1 <o que o objeto faz>; 2 <...>; 3 <...>
Prova: <o que se entende olhando só o objeto na última fase>
Parado: <o estado final, para impressão e PDF>
Histórico: <o que esta ficha já foi e por que mudou; apague se não houver>
```

O `montar.py` do kit só monta se cada ficha tiver Mecanismo, Objeto e Prova preenchidos.

Exemplo de ficha preenchida (deck de custo de infraestrutura):

```markdown
### 3 · O extrator relê tudo

Pergunta: a replicação é incremental?
Mecanismo: a cada rodada ele lê a tabela inteira para achar as poucas linhas que mudaram
Objeto: um livro de páginas empilhadas, um feixe que varre todas, uma página nova acesa
Obedece a: quantidade de páginas proporcional às linhas lidas; a página nova às mudadas
Cor: a do cliente para o livro; verde só na página nova, que é o que se quer achar
Fases: 1 o feixe varre e o contador sobe; 2 a página nova acende; 3 a razão aparece
Prova: sem ler a legenda, dá para ver que se lê tudo para achar uma página
Parado: livro inteiro com a página acesa e os três números
```

## README do deck

```markdown
# Deck: <tema> (<dd/mm/aaaa>)

<Uma ou duas frases: para quem, para decidir o quê.>

Regra: <restrições de sigilo>.

| arquivo | o que é |
|---|---|
| `ROTEIRO.md` | a ficha de cada slide (mecanismo, objeto, prova) |
| `<medir.py>` | mede na fonte primária e grava `dados.json` |
| `dados.json` | os números do deck, com a data da medição |
| `template.html` | o deck com os marcadores de montagem |
| `saida/<arquivo>.html` | o deck montado, autocontido; é o que se manda |
| `PASSAGEM.md` | estado do trabalho para retomar |
| `REUNIAO-<data>.md` | **interno**: registro de cada reunião |
| `<outro>.md` | **interno**: viabilidade, definição de produto; não vai para o cliente |

Montar:

    <comando de medição>
    <comando de montagem e conferência>
```

## REUNIAO-<data>.md (interno)

```markdown
# Reunião de <dd/mm/aaaa>: <tema> (interno)

Presentes: <nomes e áreas>. Fonte: <transcrição, anotação, gravação; onde está, e se fica fora do repositório>.
Vem depois de: <reunião ou rodada anterior, se houver>.

## A dor
- <o problema que a área descreveu, com as palavras dela>

## O que mudou no nosso entendimento
- <o que contradiz ou ajusta o que o deck ou o documento de produto dizia>

## Perguntas em aberto
1. <pergunta>

## Decidido
- <decisão>, por <quem>.

## Combinados
- <o quê>, <quem>, <até quando>.

## O que muda no material
- <deck, documento de produto, roteiro: o que mexer e o que espera decisão>
```

As perguntas se numeram para a resposta poder dizer "pergunta 7".

## PASSAGEM.md

```markdown
# Nota de passagem (<dd/mm/aaaa>, fim da rodada <n>)

Para retomar o deck numa conversa ou sessão nova.

## Estado
- Deck montado em `<saida/arquivo.html>`, com <n> slides e o apêndice. A ordem: <lista curta>.
- Medição: `<script>` gera `<dados.json>`, medida em <data>, de <fonte>.
- Variantes: <interna, cliente, idioma>, e o que cada uma não leva.

## Rodadas
- **Rodada 1** (<data>, <quem pediu>): <o que se pediu e o que foi feito>.

## Pendências
- <o que falta fazer>
- <o que não foi testado>

## A confirmar com <pessoa ou área>
- <afirmação ou decisão que espera resposta>

## Números
- <número>: <o que é>, <de onde vem>, <data da medição>.
```

Atualize ao fim de cada sessão, não só no fim do projeto: é por ela que a próxima conversa começa.
