# Ferramentas canônicas

Scripts que várias pastas de projeto usavam em cópias que foram se afastando umas das outras. Aqui mora a versão única de cada um; os repos recebem cópia pelo `scripts/sincronizar-ferramentas.py`, com cabeçalho "cópia gerada do VogelStack/ferramentas/...; edite lá", para continuarem autocontidos (quem clona um projeto não precisa ter a stack). Quem corrige um bug corrige aqui e sincroniza.

Esta pasta tem `medicao/` e o sincronizador. As demais ferramentas moram nos plugins opcionais da stack (a de Unity no de gamedev, a de narração no de conteúdo), cada uma com o seu README.

| Pasta | O que tem | Onde vai |
|---|---|---|
| `medicao/` | `medir_tokens.py` (onde os tokens dos subagentes foram) | `Ferramentas/` dos projetos que o usam |

## Manifesto

O mapa ferramenta -> repos -> caminho é um manifesto que pertence a quem usa a stack, não à stack: ele cita caminhos de máquina e nomes de projeto. O sincronizador não tem manifesto padrão; indique o arquivo com `--manifesto <arquivo>` ou com a variável `VOGEL_MANIFESTO`. O modelo é o `manifesto.example.json`: copie para fora deste repo e preencha.

Para uma ferramenta nova: criar `ferramentas/<pasta>/` (ou a pasta do plugin que a leva), acrescentar um bloco em `ferramentas` do manifesto (`origem`, `arquivos`, `destino`, `repos`, e `config.gerador` só se cada repo precisar de um arquivo de configuração) e rodar o script com `--dry-run`.

```
python scripts/sincronizar-ferramentas.py --manifesto meu-manifesto.json            # prévia (igual a --dry-run)
python scripts/sincronizar-ferramentas.py --manifesto meu-manifesto.json --checar   # divergência; sai com 1 se houver
python scripts/sincronizar-ferramentas.py --manifesto meu-manifesto.json --aplicar  # escreve cópias e a configuração que falta
```

O script não faz commit nem push: depois de `--aplicar`, cada repo (e cada worktree, que tem a própria árvore) recebe o seu commit pela regra de dono do repo. Repo que não existe na máquina é pulado, o que serve a quem alterna entre dois computadores.

Estados de cada arquivo: `ok` (igual à canônica), `novo` (não existe no repo), `antiga` (existe sem cabeçalho: versão escrita à mão, será substituída) e `diverge` (tem cabeçalho mas difere: a canônica mudou, ou alguém editou a cópia).

## `medicao/medir_tokens.py`

Lê as transcrições JSONL dos subagentes e reparte onde os tokens foram: custo direto por chamada e peso de cada resultado de ferramenta no contexto. A saída é contada pela última linha de cada resposta (a leitura pela primeira linha subcontava a saída em cerca de 30 vezes). Não tem configuração por projeto e imprime o uso quando falta argumento.

Com `--agregado`, junta os subagentes de várias sessões e reparte por faixa de chamadas, modelo, esforço e classe de trabalho. Se a variável `VOGEL_ROTEAMENTO` apontar para os registros de roteamento (um JSONL por máquina, com padrão de arquivo, por exemplo `/caminho/logs/roteamento.*.jsonl`), reparte também pela origem da escolha e pela entrega; sem ela, simplesmente não reparte por origem.
