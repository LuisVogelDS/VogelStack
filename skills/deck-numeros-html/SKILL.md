---
name: deck-numeros-html
description: Monta slides HTML para reunião de decisão em que a conversa depende de números (quantos são, quanto custa, quantos serão afetados), com cada número lido de um arquivo gerado por script de medição e cada slide desenhado a partir do mecanismo do negócio. Use quando pedirem apresentação, deck, slides ou "um HTML para a reunião" com dados, ou quando for revisar um deck antes de mandar. Não use para status, acompanhamento ou mensagem que cabe em cinco linhas.
when_to_use: Pedidos como monta uma apresentação, faz uns slides com esses números, prepara o deck da reunião, HTML para eu mostrar ao cliente, de onde saiu esse número, ou revisão de deck antes de enviar.
---

# Deck de números em HTML

Sem apontamento, o caminho de menor esforço é uma página de painel, rolável, com gráficos, que não anda por fases, não responde às perguntas da reunião e não tem apêndice de fontes. Esta skill evita isso. O método completo, com as perguntas, a regra da forma e as regras do deck, está em `${CLAUDE_SKILL_DIR}/../../vogel-stack/apresentacoes.md`: leia antes do primeiro slide. Aqui ficam só os passos e as paradas.

## Antes de tudo

1. **Vale o trabalho?** A reunião decide algo, o público mistura quem conhece o dado e quem só conhece a operação, e alguém vai perguntar "de onde saiu esse número?". Se a mensagem cabe em cinco linhas, não há número em disputa ou basta um status, diga isso e proponha texto ou planilha. Uma página de painel só entra se o dono a escolher, dita em voz alta.
2. **Achar o kit.** Procure no `AGENTS.md`/`CLAUDE.md` do projeto onde ele está. Sem registro, o kit conhecido fica em `vitrine/apresentacoes/` (`ferramentas/montar.py`, `verificar.py`, `derivar.py`, `nucleo/`, `exemplos/cafe/` como manual do motor, `METAFORAS.md`, `LICOES.md`). A stack não carrega o kit e esta skill não o copia. Sem achar, **pergunte onde está**; não improvise uma página.
3. **Reúna o que o pedido precisa:** quem assiste e o que já sabe, quem apresenta (ou se circula sem apresentador), o que o deck quer na ordem de importância, restrições de sigilo, e a frase real que se quer desmentir, se houver (não invente).

## Passos

1. **ROTEIRO.md com ficha por slide**, antes de qualquer HTML ([modelos.md](modelos.md)). Cada ficha: pergunta, mecanismo, objeto do mundo do cliente, o que obedece ao dado, cor, fases, prova, versão parada. Leve dois ou três objetos candidatos para os slides principais. **Parada:** quem encomendou vê a ficha antes de o HTML existir ("isso não é a cara deles" custa uma conversa agora, o deck depois).
2. **`medir.py` gera os dados.** Mede na fonte primária e grava `dados.json` com data e ambiente; constantes (câmbio, preço) entram com a origem. Para se a tabela ou o formato de origem mudar. Título, legenda e porcentagem saem desse arquivo; número escrito à mão não existe. Modelo de script que lê tabelas de documentos e para se a forma mudar: `IntraAct/apresentacao/2026-10-08-atas/medir.py`.
3. **Montagem.** Do `exemplos/cafe/` vêm só o `deck.json` e o andaime do `template.html`. Os slides se escrevem do zero a partir do roteiro; o deck anterior não é ponto de partida, e o nome do cliente anterior entra nos proibidos. `python <kit>/ferramentas/montar.py <pasta-do-deck> --navegar`. O `montar.py` recusa sem ROTEIRO.md completo e roda o `verificar.py` em cada saída. Componente genérico (barra, tabela, cartão) é apoio; se for mais da metade dos slides, o deck foi copiado.
4. **Verificação (laço).** Abaixo.
5. **Conferência de sigilo.** Cada variante (interna, cliente, outro idioma) é derivada por `derivar.py` com trocas conferidas e nunca editada à mão. Declare a lista de proibidos (nomes de quem disse cada frase, outros clientes, números internos, nomes de tabela, projeto ainda não aprovado, o cliente do deck de onde veio o andaime) e rode a checagem no **arquivo entregue**, não só na tela. Dado pessoal de terceiro nem na versão interna: só agregados, e caso ilustrativo é fictício e declarado na tela.
6. **Ciclo de reunião.** Mande o HTML autocontido (nunca a pasta do projeto). Depois da reunião: `REUNIAO-<data>.md` interno, `PASSAGEM.md` atualizada, e congele o que foi apresentado com a data no nome. Detalhes na seção "Ciclo da reunião" de `apresentacoes.md`.

Ao responder, termine citando o caminho do HTML montado entre crases, como o `montar.py` imprime em `abrir`.

## Verificação (laço)

Depois de cada montagem:

1. `montar.py --navegar` (ou `verificar.py <html> --proibidos "a,b" --navegar`) sai sem problema: nenhum travessão (inclusive nas strings do script), nenhum marcador sobrando (`__X__`, `TODO`), nenhum padrão de CPF, e-mail ou telefone, nenhum proibido, nenhum erro de JavaScript ao percorrer todos os slides e fases.
2. Tire print de cada slide no estado final e **olhe**. Sobreposição, rótulo que quebra, barra que não cresce e dica que não abre só aparecem assim.
3. Percorra o checklist de arte ([ajustes-de-arte.md](ajustes-de-arte.md)) com os prints em sequência, incluindo o **teste do vizinho**: trocando o nome do cliente, o deck serviria a outro negócio de outro ramo? Se serve, a forma não saiu do mecanismo e o roteiro volta.
4. Meça de novo (`medir.py`), remonte todas as variantes e confira que o número na tela é o de hoje ou que a data da medição aparece.

Se algo falhar, corrija **na origem** e remonte; nunca edite o HTML gerado:

| falhou | corrija em |
|---|---|
| número errado ou velho | `medir.py` ou `dados.json`, depois remonte |
| travessão, proibido, marcador | template, script da variante ou `derivar.py` |
| erro de JS, fase que pula | template (reserve a altura do subtítulo pela maior fase) |
| teste do vizinho, deck genérico | ROTEIRO.md: ficha nova, objeto novo, e volte ao passo 1 |
| item de arte do checklist | template, e anote a correção como regra em `LICOES.md` do kit |

Teto: **3 rodadas** de corrigir e remontar. Na terceira falha, pare e entregue o que o `verificar.py` mostrou, o que foi tentado e a hipótese da causa. Passar no script não é aprovar: a decisão de mandar é de quem encomendou, com o que ficou pendente de confirmação dito por escrito.

## Arquivos ao lado

- [modelos.md](modelos.md): ficha do ROTEIRO, REUNIAO e PASSAGEM em branco, e o README da pasta do deck.
- [ajustes-de-arte.md](ajustes-de-arte.md): correções que quem encomenda pede de novo a cada deck. Leia antes de mostrar o deck.
