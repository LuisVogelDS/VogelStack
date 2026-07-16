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
- guardrails para custo, execução e [[principios#8. Observabilidade precisa existir desde cedo|observabilidade]];
- fronteiras de segurança e privacidade verificáveis antes de expor, conforme [[seguranca|Segurança e Privacidade]];
- economia de créditos via handoff de execuções caras com scripts e logs persistentes.

## Estrutura

- [[vogel-stack/vogel-stack/principios]]: princípios permanentes para qualquer projeto, incluindo o princípio nº 19 ("Problema, não tecnologia").
- [[vogel-stack/vogel-stack/operacao-agentes]]: política operacional para uso de agentes, comandos e execuções.
- [[vogel-stack/vogel-stack/registro-e-evidencias]]: padrão para [[registro-e-evidencias|registry]], [[registro-e-evidencias|manifestos]] e rastreabilidade de execuções.
- [[vogel-stack/vogel-stack/documentacao-e-versionamento]]: papéis dos docs, regras de atualização e convenções de versionamento.
- [[vogel-stack/vogel-stack/evolucao-produto]]: método para evoluir arquitetura, produto e dashboards sem ficar preso ao legado atual.
- [[vogel-stack/vogel-stack/templates]]: modelos de documentos para iniciar novos repositórios com o mesmo padrão.
- [[vogel-stack/vogel-stack/operacao-leve]]: a operação documental da stack — wikilinks curados + link checker determinístico + agente sob demanda.
- [[vogel-stack/vogel-stack/seguranca]]: guardrails de segurança e privacidade, com os quatro princípios de fronteira e a checagem objetiva que precede qualquer exposição.

## Descoberta semântica

Antes de iniciar a implementação de novos serviços, painéis, integrações ou refatores relevantes, equipe e agentes devem cruzar referências entre:

- documentos oficiais;
- material bruto em docs/raw/ ou intake/;
- runs e artefatos operacionais descritos em [[registro-e-evidencias|Registro e Evidências Operacionais]];
- decisões de produto;
- contratos, módulos e superfícies de UI ou API.

A malha que materializa essa descoberta é a de **wikilinks curados**, validada por link checker determinístico e auditada por agente sob demanda — ver [[vogel-stack/vogel-stack/operacao-leve|Operação Documental]]. Fluxo de adoção em [[quickstart]].

Se um projeto concluir que esse arranjo não resolve o problema dele, o princípio nº 19 ([[vogel-stack/vogel-stack/principios|Problema, não tecnologia]]) manda declarar a solução alternativa em ADR próprio — a stack não herda ferramenta por convenção.

Descoberta semântica não substitui leitura técnica, testes ou revisão de código — ela orienta onde procurar primeiro e reduz o risco de reinventar decisões que o projeto já materializou.

## Como usar

Forma mínima de adoção em outro projeto:

1. ler `quickstart.md` na raiz deste repositório para o passo a passo de adoção;
2. instalar a Vogel Stack como submódulo no projeto-alvo;
3. adaptar [[vogel-stack/vogel-stack/templates]] para gerar AGENTS.md, `README.md`, `quickstart.md`, `docs/arquitetura.md`, `docs/versionamento.md` e `docs/changelog.md`;
4. ajustar fontes de verdade, fluxo de deploy, autenticação, matriz de suporte de ambiente e contratos do projeto alvo;
5. **declarar em ADR próprio** qualquer solução que o projeto adote diferente da que a stack descreve (regra do princípio nº 19);
6. manter os documentos atualizados no mesmo ciclo em que o comportamento do produto mudar.

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
