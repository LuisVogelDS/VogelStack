# Quickstart: Vogel Stack + Graphify

Este guia ajuda a instalar a Vogel Stack em outro repositório, revisar a documentação com ajuda de LLM e gerar um Knowledge Graph navegável com Graphify.

O fluxo principal é:

1. instalar a Vogel Stack como submódulo;
2. configurar uma chave gratuita do Google AI Studio;
3. pedir a um LLM para revisar a documentação e inserir links reais para a stack;
4. rodar Graphify;
5. usar outro passe de LLM para resolver órfãos e comunidades fracas;
6. rodar Graphify de novo e fechar a rodada.

As rotinas para atualizar o Graphify deste próprio repositório ficam no fim, como guia de manutenção.

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

### 2. Criar uma chave gratuita no Google AI Studio

1. Acesse [Google AI Studio API keys](https://ai.google.dev/gemini-api/docs/api-key).
2. Crie uma API key gratuita.
3. Configure a variável apenas na sessão atual do PowerShell:

```powershell
$env:GEMINI_API_KEY = "<SUA_CHAVE_DO_GOOGLE_AI_STUDIO>"
```

Para persistir no Windows:

```powershell
[Environment]::SetEnvironmentVariable("GEMINI_API_KEY", "<SUA_CHAVE_DO_GOOGLE_AI_STUDIO>", "User")
```

Não salve a chave em `README.md`, `AGENTS.md`, exemplos versionados ou qualquer arquivo do repositório.

### 3. Pedir ao LLM para revisar e conectar a documentação

Depois de instalar a stack, peça ao Codex, Claude ou outro agente para revisar os documentos do repositório alvo antes de rodar Graphify.

Use este prompt como base e ajuste o prefixo dos links conforme o caminho real instalado no passo 1.

```text
Baseado na Vogel Stack instalada neste repositório, revise o README, AGENTS.md, CLAUDE.md, quickstart.md, docs/arquitetura.md, docs/operacao.md, docs/versionamento.md, docs/changelog.md e outros guias de desenvolvimento existentes.

Insira links explícitos para arquivos reais da Vogel Stack dentro dos documentos de projeto sempre que um processo, script, job, pipeline, dashboard, artefato ou contrato precisar seguir uma regra específica da stack.

Use estes destinos como guia. Se a stack estiver instalada como submódulo em `vogel-stack/` contendo outra pasta `vogel-stack/`, ajuste os links para o prefixo `vogel-stack/vogel-stack/`.

- [[vogel-stack/principios]] para princípios permanentes, fontes de verdade, contratos, identificadores canônicos, observabilidade e semântica de saída.
- [[vogel-stack/documentacao-e-versionamento]] para papéis dos documentos, quickstart, arquitetura, versionamento, changelog e docs oficiais.
- [[vogel-stack/operacao-agentes]] para execuções por agentes, comandos caros, handoffs, logs persistentes e política de custo.
- [[vogel-stack/registro-e-evidencias]] para registry, manifestos por run, artefatos operacionais, rastreabilidade e evidências de execução.
- [[vogel-stack/evolucao-produto]] para mudanças de produto, dashboards, brainstorm, concepção, wireframe e evolução arquitetural.
- [[vogel-stack/templates]] para criar ou corrigir documentos padrão.

Objetivo: fazer o núcleo técnico e operacional deste projeto ser puxado para perto dos princípios fundamentais no grafo, sem adicionar links decorativos. Cada link deve explicar uma dependência real entre um processo do projeto e uma regra da stack.

Ao terminar, liste:

1. arquivos alterados;
2. links adicionados;
3. lacunas documentais encontradas;
4. comandos recomendados para validar e regenerar o grafo.
```

### 4. Rodar Graphify no repositório alvo

Com a chave configurada:

```powershell
Set-Location "C:\caminho\para\repo-alvo"
$env:GEMINI_API_KEY = "<SUA_CHAVE_DO_GOOGLE_AI_STUDIO>"
graphify extract . --backend gemini
```

Depois da extração:

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

### 5. Resolver órfãos e melhorar links do grafo

Depois da primeira extração, use `graphify-out/GRAPH_REPORT.md` para identificar `Knowledge Gaps`, comunidades finas e nós órfãos. Em seguida, peça a outro LLM para revisar os links.

```text
Leia graphify-out/GRAPH_REPORT.md e use o Knowledge Graph recém-extraído como mapa do repositório.

Objetivo: resolver nós órfãos, comunidades finas e conexões fracas sem inventar dependências.

Tarefas:

1. Identifique documentos, scripts, jobs, artefatos, contratos ou conceitos que aparecem isolados no grafo.
2. Leia os arquivos fonte relacionados antes de editar.
3. Adicione links Obsidian explícitos para a Vogel Stack apenas quando houver uma relação real.
4. Use este mapa de decisão:
   - execução, custo, comandos longos ou agentes -> [[vogel-stack/operacao-agentes]]
   - registry, manifests, runs, reports, evidências ou artefatos -> [[vogel-stack/registro-e-evidencias]]
   - README, arquitetura, quickstart, versionamento ou changelog -> [[vogel-stack/documentacao-e-versionamento]]
   - contratos, fontes de verdade, identificadores, observabilidade ou semântica de saída -> [[vogel-stack/principios]]
   - produto, dashboard, brainstorm, concepção, wireframe ou evolução estrutural -> [[vogel-stack/evolucao-produto]]
5. Ajuste o prefixo dos links se a stack estiver instalada em outro caminho, por exemplo usando `vogel-stack/vogel-stack/operacao-agentes`.
6. Quando um órfão não deveria ser conectado, documente por que ele é isolado em vez de criar um link falso.
7. Ao final, rode novamente `graphify extract . --backend gemini` ou entregue esse comando para o usuário executar.

Resultado esperado: o grafo deve mostrar como o núcleo técnico do projeto se conecta aos princípios, operação e evidências da Vogel Stack.
```

### 6. Rodar Graphify novamente e fechar

Depois da revisão dos órfãos:

```powershell
$env:GEMINI_API_KEY = "<SUA_CHAVE_DO_GOOGLE_AI_STUDIO>"
graphify extract . --backend gemini
Get-Content .\graphify-out\GRAPH_REPORT.md
```

Checklist mínimo antes de encerrar:

- `graphify-out/GRAPH_REPORT.md` existe e foi lido;
- `graphify-out/graph.json` e `graphify-out/graph.html` foram atualizados;
- `graphify-out/manifest.json` reflete os documentos atuais;
- links para a Vogel Stack apontam para caminhos reais, seja com o prefixo `vogel-stack/` ou `vogel-stack/vogel-stack/`;
- órfãos remanescentes foram resolvidos ou justificados;
- nenhuma chave de API foi versionada.

## Guias De Apoio

### Atualizar o submódulo em um repositório alvo

Quando a Vogel Stack mudar:

```powershell
Set-Location "C:\caminho\para\repo-alvo"
git submodule update --remote --merge vogel-stack
```

Depois disso, revise se os links continuam apontando para arquivos reais e rode Graphify novamente.

### Regenerar o Graphify deste repositório

Use este passo apenas quando estiver mantendo o próprio repositório VogelStack, não quando estiver adotando a stack em outro projeto.

```powershell
Set-Location "C:\caminho\para\VogelStack"
graphify cluster-only .
```

`cluster-only` regenera `graphify-out/GRAPH_REPORT.md` e `graphify-out/graph.html` a partir de `graphify-out/graph.json`, sem custo de LLM.

Para uma extração semântica completa:

```powershell
$env:GEMINI_API_KEY = "<SUA_CHAVE_DO_GOOGLE_AI_STUDIO>"
graphify extract . --backend gemini
```

### Quando usar `graphify update`

Use `graphify update .` quando a mudança for code-only e o objetivo for atualizar extração estrutural sem custo de LLM.

Para mudanças de documentação, links semânticos, prompts, guias ou conhecimento operacional, prefira:

```powershell
graphify extract . --backend gemini
```
