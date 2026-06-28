# Princípios Gerais

Este documento reúne princípios que devem permanecer válidos em diferentes projetos, independentemente da stack técnica específica.

## 1. O comportamento documentado deve refletir o sistema real

Documentação aspiracional só é útil quando está explicitamente marcada como futura, mantendo coerência com [[documentacao-e-versionamento|Documentação e Versionamento]].

Regra prática:

- `README.md` descreve o estado operacional atual;
- `docs/arquitetura.md` descreve a arquitetura existente;
- docs de futuro devem ser separados e claramente rotulados como planejados ou experimentais;
- qualquer divergência entre código e documentação deve ser tratada como dívida visível.

## 2. Toda aplicação precisa de fontes de verdade explícitas

Cada projeto deve declarar quais são suas fontes de verdade, por exemplo:

- APIs externas;
- banco de dados;
- cache local;
- arquivos de configuração;
- sessão/autenticação;
- filas ou eventos.

Toda mudança deve preservar a coerência entre essas camadas.

## 3. Clareza operacional é tão importante quanto correção técnica

Um sistema pode estar tecnicamente certo e ainda assim ser difícil de operar, auditar ou explicar.

Princípios:

- interfaces devem priorizar leitura útil, não apenas exibição de dados;
- permissões e restrições devem ser auditáveis;
- erros precisam ser visíveis;
- filtros, estados e fluxos precisam ser previsíveis;
- relatórios e dashboards devem responder perguntas reais de operação.

## 4. Evolução estrutural deve ser progressiva

Reescrita total raramente é o primeiro passo certo.

Sequência preferencial:

1. documentar o estado atual com honestidade;
2. extrair regras de negócio da interface;
3. criar contratos internos e serviços reutilizáveis;
4. introduzir novas camadas sem quebrar o fluxo atual;
5. migrar a operação quando a nova camada estiver estável.

## 5. Mudanças seguras exigem contratos explícitos

Antes de alterar um módulo, validar:

- se o contrato de dados mudou;
- se a autenticação ou autorização foi impactada;
- se nomes, listas, filtros ou métricas exibidas mudaram;
- se a interpretação de gráficos, KPIs ou indicadores mudou;
- se documentação, changelog e versão precisam ser atualizados.

## 6. Configuração deve ser centralizada e auditável

Boas práticas:

- preferir variáveis de ambiente para novas configurações sensíveis;
- concentrar configuração compartilhada em um ponto explícito;
- não espalhar valores operacionais importantes em múltiplos arquivos;
- documentar cada variável relevante e seu efeito.

## 7. Segredos não devem virar conteúdo documental

Regras mínimas:

- não publicar tokens, senhas ou chaves em `README`, exemplos ou docs técnicos;
- não introduzir novos segredos hardcoded em código novo;
- se um segredo existente ainda não foi migrado, registrar isso como limitação conhecida, não como padrão.

## 8. Observabilidade precisa existir desde cedo

Mesmo em protótipos, o projeto deve oferecer algum grau de [[principios#8. Observabilidade precisa existir desde cedo|observabilidade]] e rastreabilidade.

Base recomendada:

- logs de backend;
- logs de frontend ou cliente, quando aplicável;
- rotação ou retenção;
- mensagens suficientes para diagnosticar falhas sem depender de memória humana.

## 9. Versionamento e rastreabilidade não são opcionais

Mudanças relevantes precisam aparecer em algum lugar claro:

- `docs/versionamento.md` para evolução funcional e arquitetural;
- `docs/changelog.md` para entregas concretas já realizadas.

## 10. Produto deve ser pensado pelas respostas que precisa entregar

Especialmente em dashboards, o ponto de partida não deve ser o gráfico atual.

A pergunta correta é:

- quais perguntas o usuário precisa conseguir responder;
- o que exige atenção imediata;
- qual nível de detalhe confirma ou explica a leitura principal.

O visual deve nascer dessa necessidade, não do legado da ferramenta anterior.

## 11. Modos de execução suportados devem ser explícitos

Projetos maduros quase sempre têm mais de um caminho possível de execução, mas nem todos têm o mesmo nível de suporte.

Padrão recomendado:

- declarar no `README.md` qual é o caminho oficialmente suportado;
- marcar explicitamente o que está em `WIP`, `alpha`, `experimental` ou `legacy`;
- evitar documentar fluxos secundários como se fossem equivalentes ao fluxo principal;
- manter comandos de validação coerentes com o caminho oficialmente suportado.

## 12. Contratos declarativos são melhores que comportamento implícito

Quando o projeto expõe parâmetros, filtros, jobs ou automações, o contrato deve ser declarativo e reaproveitável.

Boas práticas:

- definir schemas ou contratos em um ponto explícito;
- derivar UI, API ou automações desse contrato quando possível;
- rejeitar parâmetros desconhecidos por padrão;
- distinguir claramente campos obrigatórios, opcionais, técnicos e derivados.

## 13. Identificadores canônicos devem prevalecer

Aliases convenientes demais costumam gerar ambiguidade entre código, API, documentação e operação. Por isso, [[principios#13. Identificadores canônicos devem prevalecer|Identificadores Canônicos]] são parte do contrato de clareza.

Regra prática:

- escolher nomes canônicos para entidades expostas externamente;
- usar esses nomes na documentação, API, UI e persistência;
- só introduzir aliases quando houver motivo forte de compatibilidade;
- quando houver alias, documentar o motivo, o escopo e a estratégia de depreciação.

## 14. UX de filtros deve separar intenção de negócio e refinamento técnico

Quando uma interface expõe filtros, o bloco principal deve priorizar o que o usuário realmente entende como consulta principal.

Padrão útil:

- filtros nativos da fonte ou do domínio ficam no fluxo básico;
- refinamentos locais, tuning técnico e overrides vão para uma seção avançada;
- campos fundamentais de destino, saída ou escopo não devem ficar escondidos atrás de opções avançadas.

## 15. Semântica de saída deve ser estável e auditável

Projetos que geram artefatos, exportações ou resultados intermediários precisam manter contratos de saída compreensíveis.

Base recomendada:

- definir quais artefatos são sempre esperados;
- distinguir resultado final, material bruto, manifestos e avisos;
- tornar rastreável quando houve saída parcial, truncada ou só parcialmente exportada;
- documentar os campos de saída que clientes, usuários e agentes podem confiar.

## 16. Evidência operacional deve ser persistida

Quando o projeto executa jobs, pipelines, automações ou agentes recorrentes, não basta ter código e documentação conceitual.

Também é preciso materializar:

- o que foi rodado;
- com qual escopo;
- quando foi rodado;
- quais artefatos foram gerados;
- qual foi o resultado principal.

Em projetos com esse perfil, manter um [[registro-e-evidencias|registry]] e [[registro-e-evidencias|manifestos por execução]] deixa de ser luxo e passa a ser parte da rastreabilidade mínima, como detalhado em [[registro-e-evidencias|Registro e Evidências Operacionais]].

## 17. Descoberta semântica deve anteceder implementações relevantes

Antes de implementar novos serviços, painéis, integrações ou mudanças estruturais, equipe e agentes devem **cruzar relações semânticas** entre:

- documentos oficiais;
- entradas brutas em docs/raw/ ou intake/;
- artefatos de runs anteriores descritos em [[registro-e-evidencias|Registro e Evidências Operacionais]];
- decisões de produto;
- contratos de dados;
- módulos e superfícies existentes.

Essa etapa revela dependências, decisões antigas, hipóteses já testadas e relações que uma busca textual comum não mostra.

A malha de navegação é feita por **wikilinks curados** (o mapa), com **link checker determinístico** garantindo a integridade e **auditoria estrutural por agente sob demanda** quando preciso — sem ferramentas externas obrigatórias. Detalhes em [[operacao-leve|Operação Documental]].

**O princípio se mantém**: descoberta semântica não elimina análise técnica, mas melhora seu ponto de partida.

## 18. Documentos novos já devem nascer conectados

Sempre que um novo documento, guia, handoff, runbook, resumo de execução ou artefato textual for criado, ele deve incluir wikilinks reais para os documentos e conceitos que o tornam compreensível.

Regra prática:

- ligar documentos operacionais a [[operacao-agentes|Operação de Agentes]] quando envolverem agentes, comandos, handoffs, custo ou execução;
- ligar evidências, relatórios, runs e artefatos a [[registro-e-evidencias|Registro e Evidências Operacionais]];
- ligar README, arquitetura, quickstart, versionamento e changelog a [[documentacao-e-versionamento|Documentação e Versionamento]];
- ligar contratos, fontes de verdade, identificadores, observabilidade e semântica de saída a este documento;
- ligar decisões de produto, dashboards e evolução arquitetural a [[evolucao-produto|Evolução de Produto e Arquitetura]].

O objetivo é reduzir retrabalho: cada documento novo deve entrar no repositório já rastreável e navegável — pronto para ser consumido por humano ou agente sem investigação extra. Os wikilinks já são o contrato de navegação suficiente.

Links não devem ser decorativos. Cada wikilink precisa representar uma relação real de dependência, explicação, evidência, contrato, origem ou continuidade operacional.

## 19. Problema, não tecnologia

Cada projeto adota a **solução mais simples que resolve o problema operacional real** — não herda ferramenta por convenção nem por hype.

Regra prática:

- Antes de adotar qualquer ferramenta (Graphify, Obsidian versionado, um banco a mais, etc.), conferir que o **problema** que ela resolve existe no projeto em magnitude suficiente para justificar o custo.
- A Vogel Stack resolve a navegação documental com o modelo leve (wikilinks + link checker + agente sob demanda — ver [[operacao-leve|Operação Documental]]); ferramentas mais pesadas **não são orientadas pela stack**.
- Se um projeto adotar algo diferente, **declarar em ADR**, listar a substituição problema-a-problema e referenciar este princípio — em coerência com o princípio nº 1 ([[principios|comportamento documentado reflete o sistema real]]).

Como a stack resolve cada problema de navegação documental:

| Problema | Solução da stack |
|---|---|
| Sumário canônico para agente | Hub humano (`README`/índice) + agente sob demanda |
| Detecção de link quebrado | Link checker determinístico (`check-wikilinks.ps1`) |
| Visualização do grafo | App local do usuário (ex.: Obsidian), opcional e **não-versionado** |
| Auditoria estrutural | Agente de IA com prompt explícito ([[operacao-leve]]) |

## 20. Integrações de dados devem partir da fonte primária

Quando o projeto integra dados externos, a fonte primária oficial (API governamental, FTP institucional, banco do órgão produtor, registro público mantido pela autoridade que emite o dado) deve ser preferida sobre intermediários, re-curadores ou réplicas, mesmo quando o intermediário oferece UX, SQL ou conveniência de consulta melhor.

Esse princípio complementa o [[principios#2. Toda aplicação precisa de fontes de verdade explícitas|Princípio 2]] qualificando *qual* fonte de verdade declarar quando há mais de uma camada disponível, e dialoga com o princípio nº 19 ([[principios|Problema, não tecnologia]]): a conveniência de consulta de um intermediário é um problema operacional que o projeto pode optar por resolver internamente em vez de delegar a um terceiro privado.

Motivação:

- intermediários adicionam delay de curadoria (de semanas a meses) entre a publicação oficial e o que o consumidor vê;
- podem ficar desatualizados, parados ou degradados sem aviso, criando assimetria invisível entre o sistema e o estado real da fonte oficial;
- removem a responsabilidade direta entre o consumidor do dado e o emissor oficial, dificultando reclamação, auditoria e correção;
- introduzem dependência operacional sobre um terceiro privado que pode mudar contrato, preço, política de acesso ou simplesmente desligar.

Regras práticas:

- declarar no [[documentacao-e-versionamento|README ou docs/arquitetura]] quais fontes primárias o projeto integra (URL, protocolo, formato, ritmo esperado de atualização);
- usar intermediários apenas como fallback explícito e documentado (ex.: histórico que a fonte oficial não mais serve), nunca como caminho default;
- registrar como [[principios#1. O comportamento documentado deve refletir o sistema real|limitação conhecida]] quando o caminho atual depende de intermediário e o motivo (ex.: dados anteriores ao lançamento da API oficial);
- preferir formato cru oficial mesmo que exija pós-processamento local sobre formato pré-tratado por terceiros que possa ter perdido fidelidade.

A vantagem operacional do intermediário (filtro server-side, SQL, UX) deve ser reconstruída no próprio projeto quando relevante, em vez de ser razão para abandonar a fonte primária. Ver [[operacao-agentes|Operação de Agentes]] para a política de handoff em coletas custosas a partir de fontes primárias instáveis.
