# Ferramentas canônicas

Scripts que várias pastas de projeto usavam em cópias que foram se afastando umas das outras. Aqui mora a versão única de cada um; os repos recebem cópia pelo `scripts/sincronizar-ferramentas.py`, com cabeçalho "cópia gerada do VogelStack/ferramentas/...; edite lá", para continuarem autocontidos (o sócio que clona um jogo da Cajuice não precisa do VogelStack). Quem corrige um bug corrige aqui e sincroniza.

| Pasta | O que tem | Onde vai |
|---|---|---|
| `unity/` | `unity_batch.py` (fila do Unity), `compilar_fora.py` (compilação fora do editor), `unity_comum.py` (base de ambos) | `Ferramentas/` de cada jogo Unity, com `Ferramentas/unity.json` por repo |
| `medicao/` | `medir_tokens.py` (onde os tokens dos subagentes foram) | `Ferramentas/` dos jogos que já o tinham |

O mapa ferramenta -> repos -> caminho é o `manifesto.json`. Para uma ferramenta nova (por exemplo `voz/voz.py`, do vídeo): criar `ferramentas/<pasta>/`, acrescentar um bloco em `ferramentas` do manifesto (`origem`, `arquivos`, `destino`, `repos`, e `config.gerador` só se cada repo precisar de um arquivo de configuração) e rodar o script com `--dry-run`.

```
python scripts/sincronizar-ferramentas.py            # prévia (igual a --dry-run)
python scripts/sincronizar-ferramentas.py --checar   # divergência; sai com 1 se houver
python scripts/sincronizar-ferramentas.py --aplicar  # escreve cópias e a configuração que falta
```

O script não faz commit nem push: depois de `--aplicar`, cada repo (e cada worktree, que tem a própria árvore) recebe o seu commit pela regra de dono do repo. Repo que não existe na máquina é pulado, pois o Luis alterna entre dois notebooks.

## Configuração por projeto (`Ferramentas/unity.json`)

Todas as chaves são opcionais; sem o arquivo valem os padrões. Primeira sincronização: o script gera o arquivo lendo a versão antiga do `unity_batch.py` e da `compilar_fora.py` do repo.

| Chave | Padrão | Uso |
|---|---|---|
| `unity_versao` | `m_EditorVersion` de `ProjectSettings/ProjectVersion.txt` | pasta do editor no Hub |
| `unity_exe` | `C:\Program Files\Unity\Hub\Editor\<versão>\Editor\Unity.exe` | caminho completo, vence a versão |
| `unity_editores` | `C:\Program Files\Unity\Hub\Editor` | pasta dos editores |
| `jogo_exe` | `productName` sem espaços + `.exe` (adivinha; configure) | exe da build; só uma BUILD espera ele fechar |
| `palavra_build` | `build` | trecho do método que o conta como build |
| `espera_padrao` | 1800 | segundos de espera na fila |
| `trava` | `Logs/unity-batch.lock` | lockfile |
| `prefixo_assembly` | nenhum | assemblies do jogo (`Galinha`, `Slime`...), que a `compilar_fora` compila em vez de usar a DLL do Unity |
| `alvos_padrao` | `<prefixo>.Runtime`, `<prefixo>.Editor` | o que a `compilar_fora` compila sem argumento |

Variáveis: `UNITY_PROJETO` (raiz, no lugar de `--projeto`), `UNITY_CONFIG` (outro arquivo de configuração), `COMPILAR_SAIDA` (pasta das DLLs, para agentes em paralelo), `CLAUDE_SESSAO` (nome gravado na trava).

## Diferenças que havia entre as cópias de `unity_batch.py`

Sete versões distintas em 16 arquivos (as worktrees `slime-r*` e `galinha-*` são iguais à principal, só mudam o fim de linha).

| Versão | Onde | Como difere |
|---|---|---|
| GobbleGoblin (a mais antiga, 23/09) | `GobbleGoblin` | vê processos por `tasklist`; filtra o Unity de outro projeto por substring da linha de comando (06/10), e linha ilegível conta como deste projeto; **sem `--sem-quit`** (sempre `-quit`), sem `--projeto`, sem janela oculta; exe da build `GobbleGoblin.exe` |
| Slime | `slime`, `slime-r24g`, `slime-r25`, `slime-r29fogo` | uma consulta CIM só; ganhou `--sem-quit` (teste em Play sai sozinho) e janela oculta (23/10); linha de comando ilegível **não** conta e, sem PowerShell, nada conta; docstring ainda cita o GobbleGoblin |
| `_build-slime` | clone de build do Slime | o Slime sem a janela oculta (cópia anterior a 23/10) |
| Fang You Very Much | `fang-you-very-much` | o Slime mais `--projeto` (rodar numa cópia, com trava própria); sem janela oculta; Unity 6000.6.0f1; `FangYou.exe` |
| Duct Tape | `duct-tape` | o Slime sem janela oculta e sem `--projeto`; Unity 6000.6.0f1; `DuctTape.exe` |
| Galinha | `galinha`, `galinha-*` | o Slime mais `_cita_projeto`, que exige fronteira depois do caminho (`games/nuvem` não casa com `games/nuvem-jogo`); `Galinha.exe` |
| Nuvem | `nuvem` | igual à Galinha com `Nuvem.exe` |

Configuração por projeto de fato: versão do Unity, nome do exe da build, textos de exemplo. Todo o resto era a mesma lógica. A canônica fica com o melhor de cada uma: `--sem-quit` e janela oculta (Slime), `--projeto` (Fang), fronteira de caminho (Galinha), e a postura conservadora do GobbleGoblin para linha de comando ilegível (conta como deste projeto) e PowerShell fora do ar (todo `Unity.exe` conta). O registro do GobbleGoblin, "a fila agora ignora o Unity do slime", continua valendo: a fila é por projeto e só conta o `Unity.exe` cuja linha de comando cita este `-projectPath`, e o exe da build só barra uma BUILD, não um bootstrap ou teste.

Mudanças de comportamento da canônica, todas para o lado seguro: o nome do exe é comparado sem diferença de maiúscula; Unity ou projeto não encontrado sai com código 4 e mensagem (antes, traceback); `--dry-run` mostra configuração e comando sem esperar a vez; `--espera` sem valor usa `espera_padrao` do `unity.json`. Códigos de saída: o do Unity; 3 desistiu da fila; 4 projeto ou Unity.exe ausente; 2 uso errado.

## Diferenças em `compilar_fora.py`

| Versão | Como difere |
|---|---|
| Galinha, Nuvem, Slime (e worktrees) | a mais completa: `.asmref`, fonte do `.asmdef` inteiro, referências do `.asmdef` fora do `.csproj` (23/10), `Galinha.Teste` sem `.csproj` ainda, janela oculta (no Slime, só o prefixo muda) |
| `_build-slime` | o Slime de antes dessas quatro coisas |
| Fang, Duct Tape | também sem `.asmref`/referências do `.asmdef`/janela oculta; Roslyn no layout do 6000.6 (`DotNetSdk/sdk/*/Roslyn/bincore`) |
| GobbleGoblin | a mais antiga: completa as fontes só pelas pastas que o `.csproj` lista, sem `.asmdef`/`.asmref` |

A canônica traz tudo isso, detecta o layout do Roslyn pelo disco (serve aos dois Unity) e, sem `.asmdef` para o assembly, cai no varrer-pastas-do-csproj do GobbleGoblin. Configuração real: só o prefixo dos assemblies e os alvos padrão.

## `medir_tokens.py`

Duas versões em 12 pastas: a do Slime (4 cópias, 153 linhas) e a da Galinha e da Nuvem (8 cópias, 161 linhas, de 26/10). A segunda conta a saída pela última linha de cada resposta (a anterior pegava a primeira e subcontava a saída em cerca de 30 vezes). A canônica é a segunda, sem configuração por projeto, e agora imprime o uso quando falta argumento. Ela procura o registro de roteamento do HarpyNest no caminho de uma das máquinas; em máquina sem ele, simplesmente não reparte por origem.
