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

## 🗄️ Parking
- _(nada por enquanto)_
