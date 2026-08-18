# Documentação e Versionamento

Este documento define um padrão de documentação para projetos que precisam permanecer legíveis para humanos e agentes, em diálogo direto com [[principios|Princípios Gerais]].

## 1. Conjunto mínimo de documentos

Para projetos com alguma complexidade, o conjunto mínimo recomendado é:

- `README.md`
- `quickstart.md`
- `AGENTS.md`
- `docs/arquitetura.md`
- `docs/versionamento.md`
- `docs/changelog.md`

Documentos complementares devem existir quando o projeto tiver fluxos específicos, por exemplo:

- autenticação;
- deploy;
- Docker;
- integrações externas;
- dashboards;
- brainstorms e wireframes de produto;
- pasta de entrada bruta, como `docs/raw/` ou `intake/`.

Para projetos com API, UI dinâmica, múltiplas integrações ou uso intenso de agentes, também vale padronizar:

- `docs/api.md` ou equivalente;
- `docs/ui.md` ou equivalente;
- `docs/fontes-e-filtros.md` ou equivalente;
- `docs/ai-handoff-<dominio>.md` para áreas críticas.
- `docs/operacao.md` ou equivalente, quando houver jobs, pipelines ou automações recorrentes.

## 2. Papel de cada documento

### `README.md`

Deve responder:

- o que o projeto faz;
- qual é o estado atual;
- como rodar em visão resumida;
- qual é a versão atual;
- quais são as superfícies principais do produto.

### `quickstart.md`

Deve responder:

- como sair de zero até o sistema rodando localmente;
- qual comando entra na pasta correta do projeto;
- quais dependências precisam ser instaladas;
- como iniciar, reiniciar e validar o caminho oficialmente suportado;
- quais problemas comuns impedem o primeiro uso.

O `quickstart.md` deve ser operacional, direto e copiável. Ele não substitui o `README.md`: o README explica o produto, enquanto o quickstart reduz fricção de instalação e execução.

### `AGENTS.md`

Deve responder:

- como agentes devem operar no repositório;
- quais guardrails existem;
- quais documentos precisam permanecer coerentes;
- quais áreas são mais sensíveis.

### `docs/arquitetura.md`

Deve descrever:

- arquitetura atual;
- fluxos principais;
- módulos e responsabilidades;
- pontos de atenção reais;
- limitações e decisões já assumidas.

Também é um bom lugar para deixar explícito:

- caminho oficialmente suportado de execução;
- fluxos experimentais ou legados;
- contratos principais de entrada e saída;
- como UI, API e automações derivam ou não do mesmo schema.

### `docs/versionamento.md`

Deve registrar:

- evolução funcional do produto;
- versões estáveis, alphas e versões futuras;
- motivação e escopo de cada etapa.

### `docs/changelog.md`

Deve registrar:

- entregas concretas já implementadas;
- mudanças funcionais e técnicas relevantes;
- estado materializado do sistema.

### Documentos complementares por domínio

Quando existirem, devem responder:

- `docs/api.md`: quais contratos HTTP ou RPC são públicos e estáveis;
- `docs/ui.md`: como a interface organiza filtros, ações, estados e feedback;
- `docs/fontes-e-filtros.md`: quais parâmetros existem, em que fase atuam e quais são canônicos;
- `docs/ai-handoff-<dominio>.md`: qual contexto um agente precisa para retomar um domínio sem depender de memória oral.
- `docs/operacao.md`: como rodar, validar, registrar e localizar evidências operacionais do sistema.

## 2.1 Registry, manifests e evidência operacional

Quando o projeto executa pipelines, jobs, análises ou agentes recorrentes, a documentação deve distinguir:

- documentação conceitual;
- histórico de release;
- evidência operacional de execução.

Boas práticas:

- manter um [[registro-e-evidencias|registry de execuções]] ou equivalente;
- manter [[registro-e-evidencias|manifesto por run]] quando houver múltiplos artefatos;
- documentar onde esses registros vivem e como consultá-los;
- não tratar changelog como substituto de rastreabilidade operacional.

## 2.2 Pasta de entrada bruta: `docs/raw/` ou `intake/`

Projetos que usam agentes e Knowledge Graph devem ter um lugar explícito para despejar material ainda desorganizado.

Essa pasta serve para receber:

- transcrições;
- brainstorms;
- notas soltas;
- entrevistas;
- rascunhos de produto;
- referências externas;
- fragmentos que ainda não pertencem a um documento oficial.

Padrão recomendado:

```text
docs/
  raw/
    <material-bruto>
```

ou, quando fizer mais sentido para o projeto:

```text
intake/
  <material-bruto>
```

Regras:

- `docs/raw/` ou `intake/` não substitui documentação oficial;
- conteúdo bruto deve ser tratado como material de entrada, não como fonte canônica final;
- a IA deve ler essa pasta de forma autônoma antes de concluir que um assunto não existe no projeto;
- a IA deve classificar, resumir e propor promoção de conteúdo bruto para documentos oficiais quando houver valor recorrente;
- os wikilinks devem conectar essas relações a brainstorms, transcrições, decisões e artefatos;
- material sensível, privado ou local deve ser marcado antes de entrar nessa pasta.

Bem conectada, essa pasta vira uma camada de captura do segundo cérebro do projeto.

O objetivo não é exigir organização perfeita no momento da captura. O objetivo é permitir que nosso exército digital de manutenção leia o material bruto, encontre relações, preserve contexto e ajude a transformar sinal disperso em documentação confiável.

## 3. Quando a documentação deve ser atualizada

Atualizar docs no mesmo ciclo sempre que houver:

- mudança na origem dos dados;
- mudança em autenticação ou autorização;
- nova feature com impacto funcional;
- nova página, rota ou módulo relevante;
- mudança de deploy;
- mudança no caminho oficialmente suportado de execução;
- mudança em schema, contrato, nomes canônicos ou semântica de saída;
- mudança de variáveis de ambiente;
- nova limitação conhecida;
- mudança de versão.

## 3.05 Workflows com commit automático e mensagem genérica

Alguns projetos usam scripts de sincronização que executam `git add -A`, `git commit` e `git push` em lote, normalmente com mensagem genérica do tipo `sync: <maquina> <data>`. Exemplos: scripts de sincronização multi-repositório (`sync-repos.ps1`), automações de backup local, hooks de "save on quit".

Quando esse tipo de workflow estiver em uso:

- a mensagem do commit não descreve o que foi entregue;
- `git log` deixa de ser fonte legível de histórico funcional;
- `docs/changelog.md` passa a ser o **registro real** da entrega.

Implicação operacional:

- atualizar `docs/changelog.md` é parte obrigatória do encerramento da rodada, não opcional;
- a entrada do changelog deve sair antes da execução do script de sync, para que o próprio commit automático carregue o registro junto;
- o agente que prepara a entrega não pode considerar a rodada concluída sem confirmar:
  - existe entrada nova no topo do changelog;
  - a entrada usa o `## 8. Template de changelog` desta página;
  - `Entradas principais` lista arquivos tocados e efeito observável;
  - `Estado` registra verificações executadas e o que continua não suportado;
  - documentação relacionada (arquitetura, fontes, dashboards, operação) foi atualizada quando o contrato mudou.

Quando o projeto usa submódulos e o script de sync não entra neles, o agente deve avisar explicitamente o usuário de que o `git push` dentro do submódulo precisa ser manual antes do sync principal — caso contrário o repositório pai vai apontar para um commit inexistente no remoto.

Essa regra mantém a malha de documentação, handoffs e auditoria operacional consistentes mesmo em projetos onde o histórico do Git foi deliberadamente trocado por automação leve.

## 3.06 Piso de integridade da malha — link checker

Wikilinks são contrato de navegação ([[principios|princípio nº 19]]). Wikilink quebrado é dívida visível.

Recomendação para qualquer projeto:

- manter um **link checker determinístico** (script sem LLM) que valida todo `[[wikilink]]` no repo;
- rodar em CI (GitHub Action ou equivalente) em push/PR para branch principal;
- falhar a CI em link quebrado.

Os wikilinks são a **única** infra de navegação semântica da stack — não há camada posterior que reconstrua a malha por inferência ([[operacao-leve|Operação Documental]]). Detalhes operacionais em [[operacao-agentes#7.4 Link checker determinístico como piso da malha|operacao-agentes seção 7.4]].

## 3.1 Linkagem semântica no nascimento

Todo documento novo deve nascer já conectado à malha de documentação do projeto.

Ao criar `README.md`, `quickstart.md`, `AGENTS.md`, `docs/arquitetura.md`, `docs/operacao.md`, `docs/versionamento.md`, `docs/changelog.md`, handoffs, registros de execução ou guias complementares, o autor ou agente deve inserir wikilinks reais para:

- documentos canônicos da própria documentação;
- regras relevantes da [[README|Vogel Stack]];
- processos, artefatos, contratos ou módulos citados no texto;
- evidências operacionais relacionadas, quando existirem;
- material bruto em `docs/raw/` ou `intake/`, quando o documento promover ou resumir uma entrada bruta.

Essa regra evita que a linkagem vire uma tarefa de limpeza posterior. O documento deve entrar no repositório já navegável por humanos e agentes.

Links não devem ser decorativos. Cada wikilink precisa representar uma relação real de dependência, explicação, evidência, contrato, origem ou continuidade operacional.

## 4. Distinção entre estado atual, experimental e futuro

Projetos em evolução costumam misturar três camadas:

- estado estável publicado;
- camada experimental ou alpha;
- direção futura ainda não materializada.

Essas camadas devem ser explicitadas.

Padrão recomendado:

- `README.md` deixa claro o que já está operando;
- `docs/versionamento.md` posiciona o que é estável, alpha ou futuro;
- documentos de exploração, concepção e wireframe ficam separados quando a solução futura ainda está sendo desenhada.

## 5. Política prática de versionamento

Regras recomendadas:

- toda feature relevante deve aparecer em `docs/versionamento.md`;
- mudanças internas grandes podem ser registradas como notas técnicas ou entradas de alpha;
- mudanças já entregues devem aparecer em `docs/changelog.md`;
- `README.md` deve refletir a versão que o usuário realmente encontra.

Quando o projeto tem contratos ou filtros expostos, também convém verificar:

- se a referência de API continua alinhada ao comportamento real;
- se a UI continua refletindo a organização semântica dos campos;
- se handoffs críticos ainda batem com o código atual.

## 6. Convenção para versões

Modelo útil para muitos projetos:

- `1.0`: versão inicial funcional;
- `1.x`: evolução estrutural e funcional da mesma linha de produto;
- `x.y alpha`: camada experimental já existente no repositório, mas ainda não oficial;
- `2.0`: reservar para uma mudança realmente major de produto, arquitetura ou experiência.

## 7. Template de versão

```text
## X.Y

Escopo:

- item 1
- item 2

Adições principais:

- impacto 1
- impacto 2

Motivação:

- motivo de negócio, produto ou operação

Status:

- estável | alpha | em andamento | futuro
```

## 8. Template de changelog

```text
## AAAA-MM-DD

### X.Y - título da entrega

Entradas principais:

- mudança 1
- mudança 2

Estado:

- observação operacional 1
- observação operacional 2
```

## 9. Critério de qualidade documental

Uma documentação madura é aquela em que:

- alguém novo entende o sistema sem depender de contexto oral;
- um agente consegue operar sem inferir demais;
- o documento não esconde limitações reais;
- o histórico de mudança é rastreável;
- o que é futuro não se confunde com o que já existe;
- os contratos principais continuam coerentes entre código, API, UI e docs.
