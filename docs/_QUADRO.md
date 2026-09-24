# Quadro de Trabalho — VogelStack

> **O que é:** backlog vivo da própria VogelStack (metodologia de documentação: wikilinks curados + link checker + ADRs + quadro de ciclo de vida). Formato de quadro VogelStack. Lido pelo painel Ninho do Vogel (card do projeto).
> **Origem deste quadro:** bootstrap em 2026-07-21 pelo Ninho do Vogel (F19) a partir do estado do repo (branches, ADRs, commits) — **pautas reais, a refinar pelo dono.**
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
| **Checadores rodando do submódulo nos consumidores** (`check-wikilinks`, `check-quadro`) | rodada de adoção, 24/09 | Até 24/09 os dois resolviam a raiz pela pasta do script e, rodados de `vogel-stack/scripts/`, checavam a própria stack (OK falso). Corrigidos para detectar o superprojeto, como o `check-sync`. Falta: consumidores com cópia local (Volvo, MemoriasPostumas, vitrine, Alquimia, Memória Ram, IntraAct) trocarem a cópia pela chamada ao submódulo, e CI de consumidor fazer checkout com `submodules: true`. |
| **`check-sync` deterministico rodando do submódulo** (sem cópia por projeto) | commits `cc7524d`/`8f1780a` | Garantir que todos os consumidores usem a via única. |
| **Princípio nº 21 (ambiente reconstruível a partir do repo)** — adoção pelos consumidores | pedido do dono, 05/08 | Nasceu de um caso concreto: config de servidor web viva na máquina de produção divergindo da versionada, e `refresh-data.sh` rodando fora do repo. **Verificar se os outros consumidores têm o mesmo buraco** — o padrão "script/config só na máquina" tende a se repetir onde há servidor próprio. |

| **Princípio nº 22 (texto sem assinatura de máquina)**, adoção pelos consumidores e limpeza do acervo | caso concreto na `vitrine`, 21/09 | Nasceu de uma proposta comercial: o travessão virou o sinal mais citado de texto gerado, e numa peça que precisa parecer feita à mão ele derruba o resto da entrega junto. A `vitrine` já tem o documento próprio (`docs/REDACAO.md`) e reprova travessão no pacote publicado via `conferir.py`. **Os documentos desta stack ainda estão sujos** (`operacao-agentes` 26, `seguranca` 25, `quickstart` 14, `operacao-leve` 12, `principios` 11, `templates` 6, `README` 4): limpar em passagem própria, sem misturar com mudança de conteúdo, para o diff continuar legível. Verificar também se os consumidores com superfície publicada têm como checar isso automaticamente. |

## 🗄️ Parking
- _(nada por enquanto)_
