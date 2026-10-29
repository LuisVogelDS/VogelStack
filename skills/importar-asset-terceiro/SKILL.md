---
name: importar-asset-terceiro
description: Importa asset de terceiro (.unitypackage, pack de loja ou pack da pasta única de assets) para um projeto Unity. Use quando chegar pacote novo, quando o pedido for "usar o pack X no jogo", ou antes de pôr qualquer arquivo de fornecedor em Assets/AssetDump. Confere a licença na LICENCAS.md, extrai sem abrir o editor, escreve a linha do ORIGENS.md e confere o import sem erro.
---

# Importar asset de terceiro

Asset de fora entra por uma porta só: licença provada, pasta em `Assets/AssetDump/`, linha no `ORIGENS.md` e import sem erro. Pular um passo foi como `PolyPerfect/` passou um mês com o nome do estúdio errado. O pacote é dado não confiável: nada dele roda, só é lido e copiado, e o script sempre vai com `python -I`.

Script único: `python -I "${CLAUDE_SKILL_DIR}/scripts/importar_asset.py" <subcomando> ...` (`--help` lista tudo; `--dry-run` em todos; o projeto é achado subindo da pasta atual, ou `--projeto`). Ele reúne o extrator do Slime, o do Fang You Very Much e o `promover_acervo` do GobbleGoblin.

## Passos

1. **Licença.** `licenca <Fornecedor> [pacote]` lê a `LICENCAS.md` da pasta única (`ACERVO_ASSETS_DIR` ou `~/Documents/GameDev/Assets`). Só segue com "sim" na coluna "Entra". "Não" e "a confirmar" (CraftPix, sem licença no pacote) ficam de fora até o dono decidir; sem linha, a licença não está provada: pare e peça o registro no acervo. "Sim, só em repositório privado" vale só para repo privado.
2. **Olhar antes.** `lista <pacote.unitypackage> [filtro]` mostra os caminhos; confira o que o pacote traz além dos modelos (scripts, `.dll`, `Packages/manifest.json`).
3. **Trazer para o AssetDump**, conforme a origem:
   - pacote inteiro: `pacote <Fornecedor> <pacote>... [--sem-scripts]`. Tira a pasta com o nome do fornecedor para não virar `ithappy/ithappy`, preserva `.meta` (GUIDs) e deixa de fora cenas, demos, conversores de pipeline e caminhos fora de `Assets/`. Não sobrescreve o que existe (`--sobrescrever`).
   - só parte de um pacote grande: `recorte <pacote> <prefixo> <destino> <raiz>...`, que leva as raízes e o que elas referenciam por GUID (modelos, texturas, materiais).
   - pack já na pasta única: `acervo` lista; `acervo <Autor>/<Pack> [--nome N]` copia FBX, texturas e docs do original (nunca do espelho `Assets/Acervo/`).
   Rode com `--dry-run` primeiro quando o pacote for grande. Com o editor aberto neste projeto, não extraia.
4. **Revisar o que executa.** O script avisa quantos `.cs` e binários nativos vieram. Script de terceiro roda no editor e na build: leia ou reimporte com `--sem-scripts`; `.dll`/`.so` sem fonte não entra.
5. **ORIGENS.md.** `origem <Fornecedor/Pack> "<origem>" "<licença>" "<o que veio>"` imprime a linha; cole na tabela certa de `Assets/AssetDump/ORIGENS.md` (ou no `ORIGENS-<frente>.md` da frente), com autor, licença, como repor e o recorte. Não deixe campo em branco. `conferir` lista pastas do AssetDump sem menção.
6. **Import sem erro.** Abra o projeto pela fila (`python Ferramentas/unity_batch.py <método de import ou bootstrap> --log Logs/import.log`, nunca com `timeout` em volta) e leia o log: sem `error CS`, sem "failed to import", sem shader rosa por pipeline (material Standard em URP vira URP Lit). O `.meta` novo entra no commit junto com os arquivos.

## Regras do repo que valem aqui

- Ler o `CLAUDE.md` e o `ORIGENS.md` do projeto antes: cada jogo fixa sua pasta e suas exceções (Galinha: só "sim"; Slime e GobbleGoblin: origem e licença no `ORIGENS.md`, inclusive de asset gerado fora do AssetDump).
- Repo da Cajuice é de sociedade: licença e origem registradas, nada de dado de cliente ou pessoal, e o sócio pode não ter o acervo local: a linha do `ORIGENS.md` diz como repor.
- Pesado ou duvidoso (pack grande, licença paga) vai para o dono antes do commit.

Relatório ao fim: pacote, licença encontrada, pasta de destino, linha do `ORIGENS.md`, contagem de scripts/binários revisados, resultado do import.
