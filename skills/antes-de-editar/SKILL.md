---
name: antes-de-editar
description: Confere o ponto de partida antes de implementar, editar código que vai para produção, deployar ou commitar num repositório. Use ao começar qualquer alteração em repo, ao chegar numa máquina, ao ver pendência no git status que a sessão não fez, ou quando houver outro agente no mesmo clone. Cobre fetch, upstream, branch atrás do remoto, trabalho alheio e convivência.
---

# Antes de editar

Trabalho correto sobre base velha sobrescreve trabalho novo, e nenhum teste de saída acusa isso. O `git status` diz "working tree clean" mesmo atrás do remoto quando a branch não tem upstream.

## 1. Ponto de partida (nesta ordem)

1. `git fetch` nesta sessão. Sem ele, `origin/<branch>` é foto velha.
2. `git log --oneline HEAD..origin/<branch>` sai vazio. Não use o `git status` para isto.
3. `git rev-parse --abbrev-ref "@{u}"` responde. Se não, `git branch --set-upstream-to=origin/<branch>` antes de seguir.
4. Pendência no working tree que esta sessão não fez fica de fora: separe antes de misturar.
5. Ao chegar numa máquina, `pull` antes de qualquer coisa.

Atalho determinístico: `pwsh "${CLAUDE_SKILL_DIR}/../../scripts/check-sync.ps1"` rodado dentro do repo a checar (`-NoFetch` usa a foto local). Falha se a branch está sem upstream ou atrás. Working tree limpo com branch sem upstream é o estado que mais engana.

Se a branch está atrás, `pull --rebase` só quando for trivial. Conflito ou dúvida, pare e avise. Nunca force push.

## 2. Outro agente no mesmo clone

O que você não começou não é seu.

1. Procure sinais: pendência alheia no `git status`, processo ou porta ocupados, lock recente, sessão ativa no painel ou no registro de presença.
2. Anuncie-se no registro de presença local do projeto (por exemplo `.agentes/presenca.md`, no `.gitignore`): quem é, frente, arquivos ou áreas, recursos (porta, servidor, banco) e desde quando.
3. Havendo sobreposição, escolha outra área, espere ou pergunte. Nunca edite por cima.

Durante o trabalho:

- Um dono por arquivo de cada vez. Arquivo comum (changelog, quadro, lockfile) recebe edição pequena, relida logo antes de escrever.
- Recurso compartilhado tem dono único: não mate processo que você não subiu; migração, instalação de dependência e build limpo são de um agente por vez, anunciados.
- Git só com o que é seu: commit por caminho, nunca `git add -A` às cegas. `stash`, `reset`, `checkout -- <arquivo>`, `clean` e troca de branch ficam proibidos enquanto houver outro agente no clone.
- Sobreposição grande: isole com um `git worktree` por agente.

Ao sair, apague a sua linha de presença, libere o que ocupou e deixe dito o que ficou pela metade.

## 3. Mudança que a outra máquina precisa repetir

Pasta movida, config fora do repo, repo a clonar, dependência de ambiente, dado que não vai por git: deixe recado num registro versionado antes de encerrar, com o que fazer do outro lado e uma verificação de disco.

## Commit e publicação

Quem decide é o dono do repositório, lido no `git remote -v`. A política concreta está nas instruções locais do usuário (CLAUDE.md global); não a repita aqui. Em qualquer caso: só o que a sessão tocou, sem segredo, sem assinatura de máquina na mensagem.

Referência completa: `vogel-stack/operacao-agentes.md` §1.1 a §1.4 na stack.
