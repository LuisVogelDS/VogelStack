# Ferramentas Unity

Scripts Python sem dependências para trabalhar num projeto Unity pela linha de comando. Copie para `Ferramentas/` do jogo (as cópias não se editam no jogo) e configure em `Ferramentas/unity.json`.

| Arquivo | Para quê |
| --- | --- |
| `unity_batch.py` | Fila do Unity em batch: uma instância por projeto, espera a vez, grava o log e a trava `Logs/unity-batch.lock`. Nunca envolva em `timeout` nem mate o wrapper. `--status` mostra quem está na vez. |
| `compilar_fora.py` | Checa a compilação C# fora do editor, a partir dos `.csproj`/`.asmdef`, sem abrir o Unity. |
| `unity_comum.py` | Configuração compartilhada: lê `unity.json` (exe da build, prefixo dos assemblies etc.) e acha o editor. |

O plugin traz o guarda `hooks/guard-unity.py`, que barra `timeout` em volta da fila, o ato de matar o Unity ou o wrapper e commit de asset novo sem `ORIGENS.md`.
