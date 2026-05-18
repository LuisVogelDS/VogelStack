# Quickstart: Vogel Stack + Graphify

Este guia mostra o fluxo recomendado para instalar a Vogel Stack em outro repositório, usar Codex como auditor principal da documentação e materializar um Knowledge Graph navegável com Graphify.

A estratégia padrão é **Codex-led, Graphify-assisted**:

1. **Submódulo:** trazer a Vogel Stack para o ambiente local.
2. **Auditoria Codex:** pedir ao Codex para ler o projeto, a Vogel Stack e criar links reais entre processos técnicos e regras da stack.
3. **Materialização do grafo:** rodar Graphify para gerar `graph.json`, `GRAPH_REPORT.md` e `graph.html`.
4. **Correção de weak links:** usar o relatório para uma segunda auditoria Codex focada em órfãos, comunidades fracas e links ausentes.
5. **Selo final:** regenerar o grafo e aceitar a saída só se ela melhorou ou preservou a qualidade do mapa.

Gemini fica como fallback econômico para repositórios grandes, exploração descartável ou situações em que custo é mais importante do que precisão. A saída do Gemini não deve virar mapa canônico sem revisão.

## Conexões Principais

Este guia operacional se conecta diretamente a:

- [[vogel-stack/principios|Princípios Gerais]]
- [[vogel-stack/documentacao-e-versionamento|Documentação e Versionamento]]
- [[vogel-stack/operacao-agentes|Operação de Agentes]]
- [[vogel-stack/registro-e-evidencias|Registro e Evidências Operacionais]]
- [[vogel-stack/evolucao-produto|Evolução de Produto e Arquitetura]]
- [[vogel-stack/templates|Templates de Documentação]]
- [[AGENTS|Graphify Knowledge Graph Tool]]

## Fluxo Principal

### 1. Instalar a Vogel Stack como submódulo

No repositório alvo:

```powershell
Set-Location "C:\caminho\para\repo-alvo"
git submodule add https://github.com/LuisVogelDS/VogelStack vogel-stack
git submodule update --init --recursive
```

Esse comando instala o repositório inteiro da Vogel Stack dentro de `vogel-stack/`.

Com a estrutura atual deste repositório, os documentos-base ficam em:

```text
vogel-stack/
  vogel-stack/
    principios.md
    documentacao-e-versionamento.md
    operacao-agentes.md
    registro-e-evidencias.md
    evolucao-produto.md
    templates.md
```

Antes de criar links, confirme qual caminho o projeto alvo vai usar:

- se a pasta interna continuar assim, use links com o prefixo `vogel-stack/vogel-stack/`, por exemplo para `principios`;
- se o projeto expuser ou sincronizar a pasta interna no root, use links como `[[vogel-stack/principios]]`;
- o importante é que o link aponte para um arquivo real que Graphify consiga ler.

### 2. Auditoria Codex: criar links reais antes do grafo

Use Codex para ler a documentação do projeto e inserir wikilinks explícitos onde houver dependência real com a Vogel Stack.

```text
Baseado na Vogel Stack instalada neste repositório, revise README, AGENTS.md, CLAUDE.md, quickstart.md, docs/arquitetura.md, docs/operacao.md, docs/versionamento.md, docs/changelog.md e outros guias de desenvolvimento existentes.

Objetivo: conectar o núcleo técnico e operacional deste projeto aos princípios fundamentais da Vogel Stack sem inventar dependências.

Tarefas:

1. Leia a documentação do projeto e os arquivos da Vogel Stack antes de editar.
2. Insira links explícitos para arquivos reais da Vogel Stack sempre que um processo, script, job, pipeline, dashboard, artefato ou contrato precisar seguir uma regra específica da stack.
3. Quando criar ou revisar um documento, garanta que ele já nasça conectado: inclua wikilinks para documentos canônicos, processos, artefatos, contratos e evidências relacionadas.
4. Não adicione links decorativos. Cada link deve representar uma dependência real entre o projeto e uma regra da stack.
5. Se a stack estiver instalada como submódulo em `vogel-stack/` contendo outra pasta `vogel-stack/`, ajuste os links para o prefixo `vogel-stack/vogel-stack/`.

Use estes destinos como guia:

- [[vogel-stack/principios]] para princípios permanentes, fontes de verdade, contratos, identificadores canônicos, observabilidade e semântica de saída.
- [[vogel-stack/documentacao-e-versionamento]] para papéis dos documentos, quickstart, arquitetura, versionamento, changelog e docs oficiais.
- [[vogel-stack/operacao-agentes]] para execuções por agentes, comandos caros, handoffs, logs persistentes e política de custo.
- [[vogel-stack/registro-e-evidencias]] para registry, manifestos por run, artefatos operacionais, rastreabilidade e evidências de execução.
- [[vogel-stack/evolucao-produto]] para mudanças de produto, dashboards, brainstorm, concepção, wireframe e evolução arquitetural.
- [[vogel-stack/templates]] para criar ou corrigir documentos padrão.

Ao terminar, liste:

1. arquivos alterados;
2. links adicionados;
3. lacunas documentais encontradas;
4. comandos recomendados para validar e gerar o grafo.
```

### 3. Materializar o Knowledge Graph com Graphify

Depois da auditoria Codex:

```powershell
Set-Location "C:\caminho\para\repo-alvo"
graphify extract .
```

Se o projeto já tiver `graphify-out/graph.json` e você só precisar regenerar relatório e visualização:

```powershell
graphify cluster-only .
```

Depois da geração:

```powershell
Get-Content .\graphify-out\GRAPH_REPORT.md
```

Artefatos esperados:

- `graphify-out/GRAPH_REPORT.md`
- `graphify-out/graph.json`
- `graphify-out/graph.html`
- `graphify-out/manifest.json`

Para navegar pelo grafo:

```powershell
graphify query "Como os processos operacionais deste projeto se conectam com a Vogel Stack?"
graphify path "Nome do script ou artefato" "Registro e Evidências Operacionais"
graphify explain "Nome do conceito"
```

### 4. Segunda auditoria Codex: resolver weak links

Use o relatório recém-gerado para uma auditoria focada. Esse é o ponto em que Codex deve ir direto nas dores do grafo.

```text
Leia graphify-out/GRAPH_REPORT.md e use o Knowledge Graph recém-extraído como mapa do repositório.

Objetivo: resolver nós órfãos, comunidades finas e conexões fracas sem inventar dependências. O núcleo técnico e operacional deste projeto deve ser puxado para perto dos princípios fundamentais da Vogel Stack no grafo.

Tarefas:

1. Identifique no GRAPH_REPORT.md os órfãos, comunidades fracas, hubs e perguntas sugeridas.
2. Leia os arquivos fonte relacionados antes de editar.
3. Insira links explícitos para arquivos reais da Vogel Stack sempre que um processo, script, job, pipeline, dashboard, artefato ou contrato precisar seguir uma regra específica da stack.
4. Verifique se documentos recém-criados já têm wikilinks suficientes para entrar no Knowledge Graph sem uma limpeza posterior.
5. Não adicione links decorativos. Cada link deve representar uma dependência real entre o projeto e uma regra da stack.
6. Quando um órfão não deveria ser conectado, documente por que ele é isolado em vez de criar um link falso.
7. Ao terminar, liste arquivos alterados, links adicionados, órfãos resolvidos, órfãos mantidos e comandos de validação.
```

### 5. Selo final: regenerar e comparar

Depois da segunda auditoria:

```powershell
graphify extract .
Get-Content .\graphify-out\GRAPH_REPORT.md
```

Aceite o novo grafo apenas se:

- órfãos diminuíram ou foram justificados;
- comunidades fracas foram fortalecidas ou explicadas;
- os hubs centrais continuam fazendo sentido;
- `nodes` e `edges` não despencaram sem motivo;
- os documentos técnicos se aproximaram de `Princípios Gerais`, `Operação de Agentes`, `Registro e Evidências Operacionais` e `Documentação e Versionamento`;
- nenhuma chave de API foi versionada.

Se a qualidade cair, restaure o grafo anterior e investigue antes de commitar.

## Fallback Gemini

Gemini pode ser útil como scanner barato em repositórios grandes, mas não deve ser o caminho canônico quando qualidade semântica importa mais do que custo.

Use Gemini quando:

- o repositório é grande e você quer uma primeira varredura barata;
- a extração é exploratória ou descartável;
- você quer comparar resultados contra a curadoria Codex;
- não há orçamento/tokens para uma auditoria forte.

Configure a chave:

```powershell
$env:GEMINI_API_KEY = "<SUA_CHAVE_DO_GOOGLE_AI_STUDIO>"
```

Ou persista no Windows:

```powershell
[Environment]::SetEnvironmentVariable("GEMINI_API_KEY", "<SUA_CHAVE_DO_GOOGLE_AI_STUDIO>", "User")
```

Rode:

```powershell
graphify extract . --backend gemini
```

Antes de aceitar a saída Gemini, compare com o grafo anterior:

- `nodes` não deve cair drasticamente;
- `edges` não deve despencar;
- órfãos e weak links não devem aumentar;
- hubs principais precisam continuar coerentes;
- `GRAPH_REPORT.md` precisa ficar melhor, não apenas diferente.

Se a saída piorar, não commite. Restaure o grafo anterior e use Codex para auditoria.

## Guias De Apoio

### Atualizar o submódulo em um repositório alvo

Quando a Vogel Stack mudar:

```powershell
Set-Location "C:\caminho\para\repo-alvo"
git submodule update --remote --merge vogel-stack
git status
```

Depois, registre no repositório alvo o ponteiro atualizado do submódulo:

```powershell
git add vogel-stack
git commit -m "Update VogelStack submodule"
git push
```

Depois disso, revise se os links continuam apontando para arquivos reais e rode Graphify novamente.

### Regenerar o Graphify deste repositório

Use este passo apenas quando estiver mantendo o próprio repositório VogelStack, não quando estiver adotando a stack em outro projeto.

```powershell
Set-Location "C:\caminho\para\VogelStack"
graphify cluster-only .
```

`cluster-only` regenera `graphify-out/GRAPH_REPORT.md` e `graphify-out/graph.html` a partir de `graphify-out/graph.json`, sem custo de LLM.

### Quando usar `graphify update`

Use `graphify update .` quando a mudança for code-only e o objetivo for atualizar extração estrutural sem custo de LLM.

Para mudanças de documentação, links semânticos, prompts, guias ou conhecimento operacional, prefira uma auditoria Codex seguida de:

```powershell
graphify extract .
```
