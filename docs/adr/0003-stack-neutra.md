# ADR 0003 — A stack é metadocumentação neutra

- **Status:** Aceito
- **Data:** 2026-11-10
- **Decisor:** LuisVogelDS
- **Relação:** complementa o [[0002-remover-familia-padrao|ADR 0002]]: aquele tirou da stack a ferramenta que ninguém usava, este tira o que só fazia sentido no ambiente de quem a escreveu
- **Princípios aplicáveis:** nº 19 ([[vogel-stack/principios|Problema, não tecnologia]]) e nº 23 ([[vogel-stack/principios|exemplo passa adiante o porquê, não a forma]])

## Contexto

A Vogel Stack nasceu de práticas testadas nos projetos do autor, e por isso carregava marcas dessa origem: caminhos de máquina, nomes de projetos, de empresas e de pessoas, códigos de chamado de um empregador, o nome do painel e do relator que o autor usa no dia a dia. Nada disso ajuda quem adota a stack, pois ninguém além do autor tem aquelas pastas, aqueles repositórios ou aquele painel. Já o repositório é público, e dado de ambiente pessoal ali é exposição sem ganho.

Havia também um segundo efeito: a stack apontava para código e configuração que moram fora dela (a definição dos tipos de subagente, por exemplo), de modo que a regra escrita aqui dependia de um arquivo que o leitor não podia abrir.

## Decisão

**A stack descreve o método e oferece moldes executáveis parametrizados, sem nome nem caminho de ninguém.**

- O texto explica a regra e o porquê. O que se executa (skills, hooks, conferidores e modelos de agente, como os de [[vogel-stack/agentes/README|vogel-stack/agentes/]]) vem como molde, com parâmetros no lugar do que era específico de um ambiente.
- **Quem instancia é o projeto.** Caminho, nome de repositório, convenção de ticket e a escolha de ferramenta ficam no `AGENTS.md`, no ADR ou nas instruções locais de quem adota.
- **O que é do ambiente de um usuário mora fora da stack**, num plugin privado dele. Isso inclui o painel que ele usa, o relator da sua rede de máquinas e as skills que só servem aos jogos ou clientes dele.
- **Exemplo real é anonimizado, não apagado.** O caso continua sendo evidência, com o fato, a data e o número, e troca-se só o nome pela descrição ("uma rodada de um jogo Unity com nove frentes"). O mesmo projeto recebe sempre a mesma descrição dentro de um documento.
- **Um conferidor no CI barra a regressão.** `scripts/check-neutralidade.py` procura os termos proibidos nos arquivos da stack, e o push que os reintroduz falha.

## Consequências

- Os documentos de `vogel-stack/`, o `quickstart`, o quadro, os ADRs e as skills foram reescritos para esta regra. Referências a código externo passaram a apontar para moldes dentro do repositório.
- Os sete modelos de subagente entram em `vogel-stack/agentes/`, de modo que a regra de escolha de tipo e o arquivo que a executa vivem lado a lado, e o roteamento de modelo continua na definição do agente.
- Quem quiser as peças que saíram (ferramentas de jogo, hooks específicos, o brief de repositório Unity) as instala por um plugin à parte, e a stack não depende dele.
- Um caso real novo só entra nos documentos já anonimizado. Se o conferidor reprovar um termo legítimo, a lista de exceções do próprio conferidor é o lugar de declará-lo.

## Gatilhos para reabrir

Reavaliar se o anonimato empobrecer a evidência a ponto de o leitor não confiar no caso, ou se surgir um termo próprio da stack que o conferidor trate como proibido por engano.
