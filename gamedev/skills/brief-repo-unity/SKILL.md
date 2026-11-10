---
name: brief-repo-unity
description: Bloco fixo que abre o prompt de disparo de uma frente de trabalho em repo Unity. Use ao escrever o prompt de um subagente que vai mexer num jogo Unity (fila do Unity, território, regra de git, formato do relatório), preenchendo só o que está entre `<>`.
---

# Bloco fixo de brief para frente em repo Unity

Cole o bloco abaixo no início do prompt de disparo de toda frente que mexe num jogo Unity e preencha só o que está entre `<>`. O contrato da frente (entrega, território, retorno, critério de pronto, orçamento) vem depois dele. O bloco existe para o prompt não esquecer o que custa caro: abrir o motor sem a fila, ler arquivo inteiro e devolver relatório solto.

```
REPO: <caminho absoluto do repo ou da worktree> (branch <nome>). Unity <versão: m_EditorVersion de ProjectSettings/ProjectVersion.txt>, <pipeline de render, ex. URP>.
LEIA ANTES DE ESCREVER: o CLAUDE.md do repo, docs/arquitetura.md e docs/ferramentas.md (obrigatórios; o CLAUDE.md diz o que mais ler). Do resto, só o trecho do sistema que a frente toca: busca com contexto e leitura por faixa de linhas, não arquivo inteiro.
TERRITÓRIO: altera só <pastas/arquivos>; só lê <...>. Pasta vizinha de outra frente não se toca.
MOTOR E FILA: o editor trava o projeto, então uma instância por projeto e só pela fila (`python Ferramentas/unity_batch.py <Classe.Metodo> --log Logs/<x>.log --quem <frente>`). Nunca envolver a fila em `timeout`, nunca matar o wrapper: o Unity fica órfão segurando Temp/UnityLockfile e só sai reiniciando a máquina. <Esta frente NÃO abre o Unity: fecha com `python Ferramentas/compilar_fora.py` e deixa os roteiros no grupo dela, relatando o que espera de cada um. | Esta frente tem a fila: a bateria dela só, em segundo plano.> Em worktree, a fila é a da própria pasta.
FERRAMENTAS: Ferramentas/unity_batch.py, compilar_fora.py e medir_tokens.py são cópias geradas da stack (cabeçalho no topo): não edite aqui; a configuração do projeto está em Ferramentas/unity.json.
GIT: <regra de commit e push do repo: onde o agente commita sozinho, um commit por entrega, adicionando por caminho e sem menção a IA; onde só se commita sob pedido, a regra do dono, com o código de tarefa exigido>. Capturas/, Builds/, Logs/ e Library/ nunca entram. Asset de terceiro: skill importar-asset-terceiro.
RELATÓRIO (no fim, nesta ordem, sem despejo de arquivo): 1) conclusão em uma frase; 2) o que mudou, por arquivo, com o commit; 3) evidência (saída do compilar_fora, resumo do teste, caminho das capturas e a grade da skill verificar-captura); 4) regulagens de gosto deixadas no painel de ajustes do jogo, para o dono julgar; 5) o que ficou sem verificar e por quê; 6) o que o orquestrador precisa rodar no motor.
```

## Como preencher

- **Versão:** leia do `ProjectSettings/ProjectVersion.txt` do repo da frente; as cópias do mesmo repo (worktrees) costumam ter a mesma, mas jogos diferentes podem estar em versões diferentes do editor.
- **Motor ou não:** o padrão do orquestrador é a frente sem motor; o texto com motor só vale quando o plano da rodada disser, e então a frente trabalha numa worktree com Unity próprio.
- **Regra de git:** vem do remote do repo (`git remote -v`), não da pasta; confira antes de escrever a linha de GIT.
- Se o jogo tiver ferramenta de mapa por pasta de sistema (ex.: `docs/mapa-*.md`), acrescente a linha "atualize o mapa junto com o relatório".
