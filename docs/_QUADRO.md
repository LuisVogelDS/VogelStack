# Quadro de Trabalho — VogelStack

> **O que é:** backlog vivo da própria VogelStack (metodologia de documentação: wikilinks curados + link checker + ADRs + quadro de ciclo de vida). Formato de quadro VogelStack.
> **Origem deste quadro:** bootstrap em 2026-07-21 a partir do estado do repo (branches, ADRs, commits) — **pautas reais, a refinar pelo dono.**
> **Nota:** este é o quadro do *repositório* VogelStack (o backlog da metodologia). Não confundir com o quadro-modelo que a metodologia prega pros projetos consumidores.

**Legenda:** 🔴 prioridade · 🟡 em andamento · ⚪ backlog válido · 🗄️ parking.

Última reconciliação: 2026-09-24 · fontes: git (branches e ADRs) e a rodada de adoção nos 14 consumidores de 2026-09-24. A via "ciclo-de-vida do quadro" saiu da prioridade: a branch `docs/quadro-ciclo-de-vida` já está contida na `main` (`git merge-base --is-ancestor`).

## 🔴 Prioridade
| Item | Origem | Próxima ação / nota |
|---|---|---|

## 🟡 Em andamento
| Item | Origem | Próxima ação / nota |
|---|---|---|

## ⚪ Pendente (backlog válido)
| Item | Origem | Nota |
|---|---|---|
| **Segurança e Privacidade na stack** — promovida a documento de 1ª classe | commit `633bc48` | Recém-adicionada (`vogel-stack/seguranca.md`); avaliar cobertura e adoção pelos consumidores. |
| **Checadores rodando do submódulo nos consumidores** (`check-wikilinks`, `check-quadro`) | rodada de adoção, 24/09 | Até 24/09 os dois resolviam a raiz pela pasta do script e, rodados de `vogel-stack/scripts/`, checavam a própria stack (OK falso). Corrigidos para detectar o superprojeto, como o `check-sync`. Falta: consumidores com cópia local trocarem a cópia pela chamada ao submódulo, e CI de consumidor fazer checkout com `submodules: true`. |
| **`check-sync` deterministico rodando do submódulo** (sem cópia por projeto) | commits `cc7524d`/`8f1780a` | Garantir que todos os consumidores usem a via única. |
| **Guarda contra falha mascarada por pipe** (proposta, aguarda o sim do dono) | duas sessões no mesmo dia, 16/11/2026 | Num `teste \| tail && git commit`, o código de saída é o do `tail`, e o commit passa com o teste falhando. Uma sessão subiu um commit quebrado, com outras frentes rodando teste no mesmo clone. A falha é mecânica, e por isso a proposta é de hook: o `hooks/guard-git.py` nega `git commit` ou `git push` que venha depois de um `\|` no mesmo comando sem `set -o pipefail`, com caso em `test_guard_git.py`. No mesmo dia apareceram duas armadilhas de texto no Windows. A primeira pegou três sessões: texto com barra invertida passado no comando do Bash do agente sai alterado, pois a barra dupla chega como uma só, até entre aspas simples e em heredoc com delimitador entre aspas (provado com `od -c`, 16/11). Assim, um `"\r\n"` virou quebra literal, e um caminho de Windows foi para um documento de operação com form feed e backspace no lugar de `\f` e `\b`, sem nada aparecer no editor. A segunda é que `open(..., "w")` em modo texto converte todo `\n` em `\r\n`. A saída é gravar pela ferramenta de arquivo (Write ou Edit), usar `chr(92)` quando o script precisa do byte e abrir com `newline=""` ou `newline="\n"`. Como a primeira já se repetiu três vezes, a regra escrita sozinha tende a não pegar, e a decisão do dono inclui onde ela mora: linha no `CLAUDE.md` global, aviso de hook quando o comando do Bash grava arquivo com `\\`, ou as duas. Um consumidor fechou o caso com um teste barato, que reprova caractere de controle C0 (fora tab, LF e CR) em todo arquivo de texto versionado e prova a regra com o defeito plantado. Ele pode virar checador da stack, ao lado do `check-neutralidade`. |
| **Princípio nº 21 (ambiente reconstruível a partir do repo)** — adoção pelos consumidores | pedido do dono, 05/08 | Nasceu de um caso concreto: config de servidor web viva na máquina de produção divergindo da versionada, e `refresh-data.sh` rodando fora do repo. **Verificar se os outros consumidores têm o mesmo buraco** — o padrão "script/config só na máquina" tende a se repetir onde há servidor próprio. |

| **Princípio nº 22 (texto sem assinatura de máquina)**, adoção pelos consumidores e limpeza do acervo | caso concreto num site de propostas comerciais, 21/09 | Nasceu de uma proposta comercial: o travessão virou o sinal mais citado de texto gerado, e numa peça que precisa parecer feita à mão ele derruba o resto da entrega junto. Esse site já tem documento próprio de redação e reprova travessão no pacote publicado por um conferidor. **Os documentos desta stack ainda estão sujos** (`operacao-agentes` 26, `seguranca` 25, `quickstart` 14, `operacao-leve` 12, `principios` 11, `templates` 6, `README` 4): limpar em passagem própria, sem misturar com mudança de conteúdo, para o diff continuar legível. Verificar também se os consumidores com superfície publicada têm como checar isso automaticamente. |

## 🗄️ Parking
- _(nada por enquanto)_
