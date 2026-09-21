# Quadro de Trabalho — VogelStack

> **O que é:** backlog vivo da própria VogelStack (metodologia de documentação: wikilinks curados + link checker + ADRs + quadro de ciclo de vida). Formato de quadro VogelStack. Lido pelo painel Ninho do Vogel (card do projeto).
> **Origem deste quadro:** bootstrap em 2026-07-21 pelo Ninho do Vogel (F19) a partir do estado do repo (branches, ADRs, commits) — **pautas reais, a refinar pelo dono.**
> **Nota:** este é o quadro do *repositório* VogelStack (o backlog da metodologia). Não confundir com o quadro-modelo que a metodologia prega pros projetos consumidores.

**Legenda:** 🔴 prioridade · 🟡 em andamento · ⚪ backlog válido · 🗄️ parking.

## 🔴 Prioridade
| Item | Origem | Próxima ação / nota |
|---|---|---|
| **Levar a via "ciclo-de-vida do quadro" pra `main`** — a branch `docs/quadro-ciclo-de-vida` tem o `scripts/check-quadro.ps1` + mudanças em AGENTS/CLAUDE/ADR 0002/check-sync/docs da stack, ainda **fora da main** | diagnóstico do hub (Cantin) 17/07 · confirmado 21/07 | Avaliar o merge na `main` **com o dono** (a versão de 16/07 já venceu num merge anterior — `d4d1d5f`). **Isto destrava** o item do Cantin "VogelStack no hub: submódulo" (que espera a via limpa na main). |

## 🟡 Em andamento
| Item | Origem | Próxima ação / nota |
|---|---|---|

## ⚪ Pendente (backlog válido)
| Item | Origem | Nota |
|---|---|---|
| **Segurança e Privacidade na stack** — promovida a documento de 1ª classe | commit `633bc48` | Recém-adicionada (`vogel-stack/seguranca.md`); avaliar cobertura e adoção pelos consumidores. |
| **`check-sync` deterministico rodando do submódulo** (sem cópia por projeto) | commits `cc7524d`/`8f1780a` | Garantir que todos os consumidores (PlacarBI, CartaoVermelho, ScoutCamisa10, Memória Ram, guaraci, Bem-te-vi, website…) usem a via única. |
| **Princípio nº 21 (ambiente reconstruível a partir do repo)** — adoção pelos consumidores | pedido do dono via PlacarBI, 05/08 | Nasceu de um caso concreto: config de nginx viva na EC2 divergindo da versionada, e `refresh-data.sh` rodando fora do repo. **Verificar se os outros consumidores têm o mesmo buraco** — o padrão "script/config só na máquina" tende a se repetir onde há servidor próprio. |

| **Princípio nº 22 (texto sem assinatura de máquina)**, adoção pelos consumidores e limpeza do acervo | caso concreto na `vitrine`, 21/09 | Nasceu de uma proposta comercial: o travessão virou o sinal mais citado de texto gerado, e numa peça que precisa parecer feita à mão ele derruba o resto da entrega junto. A `vitrine` já tem o documento próprio (`docs/REDACAO.md`) e reprova travessão no pacote publicado via `conferir.py`. **Os documentos desta stack ainda estão sujos** (`operacao-agentes` 26, `seguranca` 25, `quickstart` 14, `operacao-leve` 12, `principios` 11, `templates` 6, `README` 4): limpar em passagem própria, sem misturar com mudança de conteúdo, para o diff continuar legível. Verificar também se os consumidores com superfície publicada têm como checar isso automaticamente. |

## 🗄️ Parking
- _(nada por enquanto)_
