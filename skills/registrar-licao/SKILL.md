---
name: registrar-licao
description: Transforma um erro repetido em melhoria permanente do sistema, e não só em correção do caso. Use quando o usuário corrigir o agente pela segunda vez na mesma coisa, quando um teste, hook ou build falhar pelo mesmo motivo de antes, ou quando o usuário disser "anota isso", "isso de novo" ou "não esquece".
---

# Registrar lição

Corrigir o caso não basta: a mesma falha volta na próxima sessão, no outro notebook ou na mão do sócio. Conserte o caso e depois conserte o sistema, com a menor mudança que pegue a falha.

## Passos

1. **Uma frase.** Escreva a lição como regra verificável ("nunca envolver a fila Unity em timeout"), e não como história.
2. **Já está registrada?** Procure em `CLAUDE.md`/`AGENTS.md` do repo, skills do plugin e do repo, hooks e memória. Se estava, descubra por que não pegou: no lugar errado (só em outro repo), longe do ponto de uso, vaga, ou instrução onde precisava de garantia.
3. **Escolha o mecanismo** pela tabela de `vogel-stack/mecanismos.md`: fato do repo vai para o `CLAUDE.md`/`AGENTS.md`; procedimento que se repete vira passo de skill; "toda vez, sem exceção" vira hook.
4. **Aplique a mudança mínima.** Uma linha no `CLAUDE.md` do repo, um passo numa skill existente, ou um arquivo novo. **Hook e skill nova são propostos ao usuário antes de criar**: diga o gatilho, o mecanismo e o motivo em poucas linhas e espere o sim. Linha de regra e passo em skill existente podem ir direto.
5. **Registre no repo certo.** Fato de um projeto fica no repo dele; o que serve a vários repos fica no plugin `vogel-stack`. Commite segundo a regra do `CLAUDE.md` global, que diz quando pode ser sozinho (repo pessoal) e quando só sob pedido (repo da 2morrow, com código JIRA).
6. **Nunca só na auto-memória.** Ela é local da máquina; o outro notebook e o sócio não a veem. Memória fica para preferência pessoal que não afeta o repo.

## Exemplo

A regra "nunca envolver a fila Unity em timeout" existia só no `CLAUDE.md` do slime, e foi violada 130 vezes em outros jogos, que não carregam aquele arquivo. Era regra mecânica, de "toda vez, sem exceção", e por isso virou hook no plugin `vogel-stack`, que vale em todo repo.

Referência: `vogel-stack/mecanismos.md`.
