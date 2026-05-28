# Vogel Stack

`Vogel Stack` é um conjunto de documentos-base para repositórios que usam agentes de IA como parte real do fluxo de desenvolvimento, documentação e operação.

O objetivo desta pasta é transformar práticas testadas em um projeto específico em um padrão reutilizável para outros contextos, sem depender de regras subjetivas ou conhecimento tribal.

## Propósito

Esta stack ajuda a manter:

- documentação coerente com o código real, conforme [[documentacao-e-versionamento|Documentação e Versionamento]];
- regras operacionais claras para agentes e humanos, conforme [[operacao-agentes|Operação de Agentes]];
- matriz explícita do que é suportado, experimental ou apenas legado;
- contratos de entrada e saída mais estáveis para UI, API e automações;
- evolução arquitetural controlada;
- versionamento e changelog auditáveis;
- critérios mais objetivos para mudanças de produto e dashboard;
- guardrails para custo, execução e [[Observabilidade e Logs|observabilidade]];
- economia de créditos via [[Handoff Padrão de Execução|handoff]] de execuções caras com scripts e [[PowerShell Logging Pattern|logs persistentes]].

## Estrutura

- [[vogel-stack/vogel-stack/principios]]: princípios permanentes para qualquer projeto.
- [[vogel-stack/vogel-stack/operacao-agentes]]: política operacional para uso de agentes, comandos e execuções.
- [[vogel-stack/vogel-stack/registro-e-evidencias]]: padrão para [[Registry de Execuções|registry]], [[Manifesto por Run|manifestos]] e rastreabilidade de execuções.
- [[vogel-stack/vogel-stack/documentacao-e-versionamento]]: papéis dos docs, regras de atualização e convenções de versionamento.
- [[vogel-stack/vogel-stack/evolucao-produto]]: método para evoluir arquitetura, produto e dashboards sem ficar preso ao legado atual.
- [[vogel-stack/vogel-stack/templates]]: modelos de documentos para iniciar novos repositórios com o mesmo padrão.

## Descoberta visual

Com [[Graphify Knowledge Graph Tool|Graphify]], a Vogel Stack deixa de ser apenas um conjunto de rotas manuais de documentação e passa a operar como um segundo cérebro do projeto.

A interface do Obsidian é a camada oficial de visualização do [[Knowledge Graph]].

Neste repositório, a integração local do Graphify é materializada em:

- `graphify-out/GRAPH_REPORT.md`: relatório textual que agentes devem ler primeiro;
- `graphify-out/graph.json`: grafo consultável por `graphify query`, `graphify path` e `graphify explain`;
- `graphify-out/graph.html`: visualização HTML navegável;
- `graphify-out/manifest.json`: hashes dos arquivos indexados.

O CLI local atual não gera `graphify-out/wiki/index.md` por padrão. Se esse diretório existir em um projeto futuro, ele pode ser usado como camada adicional de navegação, mas não é pré-requisito da Vogel Stack.

Antes de iniciar a implementação de novos serviços, painéis, integrações ou refatores relevantes, equipe e agentes devem usar as conexões visuais do grafo para cruzar referências entre:

- documentos oficiais;
- material bruto em [[Pasta docs/raw e intake|docs/raw/ ou intake/]];
- runs e artefatos operacionais descritos em [[registro-e-evidencias|Registro e Evidências Operacionais]];
- decisões de produto;
- contratos, módulos e superfícies de UI ou API.

Essa descoberta visual não substitui leitura técnica, testes ou revisão de código. Ela orienta onde procurar primeiro e reduz o risco de reinventar decisões que o projeto já materializou.

## Como usar

Forma mínima de adoção em outro projeto:

1. ler `quickstart.md` na raiz deste repositório para instalar a stack, configurar Graphify e gerar links semânticos;
2. copiar esta pasta ou instalá-la como submódulo no novo repositório;
3. adaptar [[vogel-stack/vogel-stack/templates]] para gerar [[AGENTS.md Document Pattern|AGENTS.md]], `README.md`, `quickstart.md`, `docs/arquitetura.md`, `docs/versionamento.md` e `docs/changelog.md`;
4. ajustar fontes de verdade, fluxo de deploy, autenticação, matriz de suporte de ambiente e contratos do projeto alvo;
5. manter os documentos atualizados no mesmo ciclo em que o comportamento do produto mudar.

## Escopo

Esta stack não tenta impor uma linguagem, framework ou arquitetura única.

Ela define:

- critérios de clareza;
- disciplina de documentação;
- padrão operacional de agentes, ligado a [[operacao-agentes|Operação de Agentes]];
- padrão de evidência operacional e rastreabilidade de runs, ligado a [[registro-e-evidencias|Registro e Evidências Operacionais]];
- disciplina de contratos, schemas e identificadores canônicos;
- método de evolução de produto;
- guardrails para evitar desperdício, opacidade e retrabalho.
