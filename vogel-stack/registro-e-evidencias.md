# Registro e Evidências Operacionais

Este documento define um padrão para projetos que executam pipelines, jobs, agentes, integrações ou análises recorrentes e precisam manter evidência material do que foi rodado.

## 1. O que este documento cobre

Ele complementa:

- [[documentacao-e-versionamento|documentacao-e-versionamento.md]], que define papéis dos documentos;
- [[operacao-agentes|operacao-agentes.md]], que define quem prepara, quem executa e como colaborar;
- [[principios|principios.md]], que define rastreabilidade como princípio.

Aqui o foco é:

- como registrar execuções;
- como ligar entradas, saídas e artefatos;
- como distinguir histórico de execução de changelog e versionamento.

## 2. Changelog não substitui registry

Cada artefato tem papel diferente:

- `docs/changelog.md`: o que foi entregue ao produto ou ao repositório;
- `docs/versionamento.md`: como o produto evoluiu por versão;
- [[Registry de Execuções|`registry` de execução]]: o que foi rodado, quando, com qual escopo, com quais artefatos e com qual resultado.

Projetos com jobs, pipelines, modelos, agentes ou automações recorrentes não devem depender só de changelog para auditoria operacional.

## 3. Quando um registry é recomendado

O padrão passa a ser fortemente recomendado quando houver:

- pipelines de dados;
- treinos ou avaliações de modelos;
- execuções por ambiente, cliente ou escopo;
- jobs com múltiplos estágios;
- artefatos persistidos em diretórios por rodada;
- automações acionadas por agentes;
- necessidade de reproduzir uma execução específica sem memória oral.

## 4. Campos mínimos de um registro de execução

O formato exato pode variar, mas o registro deveria capturar pelo menos:

- timestamp da execução;
- `run_id` único;
- `pipeline_run_id` ou correlato para agrupar estágios;
- estágio ou tipo de execução;
- escopo, ambiente, cliente ou fonte;
- versão, algoritmo ou modo de execução, quando aplicável;
- intervalo temporal ou filtros principais;
- fingerprint ou referência do input;
- localização dos artefatos gerados;
- status, confiança ou observação operacional.

## 5. Manifesto por run

Quando a execução gera múltiplos arquivos, vale manter um [[Manifesto por Run|manifesto por run]].

Esse manifesto deve responder:

- quais arquivos foram gerados;
- quais são finais e quais são auxiliares;
- o que estava ausente;
- se houve saída parcial.

## 6. Estrutura prática recomendada

Modelo simples e reutilizável:

```text
reports/
  runs/
    <run_id>/
      summary.json
      artifacts.json
      <artefatos>
  registry.csv
```

O diretório por run concentra o contexto local da rodada.

O `registry.csv` ou equivalente materializa o [[Registry de Execuções]] e serve para comparação transversal entre execuções.

## 7. Relação com agentes

Projetos agent-friendly ganham muito quando o [[Registry de Execuções|registry]] já existe, porque o agente pode:

- comparar execuções sem inferir demais;
- localizar artefatos rapidamente;
- resumir progresso por estágio;
- detectar lacunas de cobertura entre escopos;
- evitar repetir trabalho já materializado.

## 7.1 [[Regra de Juros Compostos]]

Cada execução registrada deve aumentar o valor do segundo cérebro do projeto e reforçar o [[Knowledge Graph]].

Sempre que um novo diretório de artefato for criado em:

```text
reports/
  runs/
    <run_id>/
```

o agente responsável deve garantir que esse resultado possa ser lido pela próxima indexação do [[Knowledge Graph]].

Regras práticas:

- todo diretório `reports/runs/<run_id>/` deve conter um resumo legível por humanos e agentes, como `summary.md` ou `summary.json`;
- `artifacts.json` ou equivalente deve apontar os arquivos finais, auxiliares, parciais e ausentes;
- artefatos binários importantes devem ter uma descrição textual mínima;
- o `registry.csv` deve referenciar o diretório da run;
- a próxima execução de [[Graphify Knowledge Graph Tool|Graphify]] deve conseguir capturar a relação entre run, escopo, decisão, métrica, relatório e artefato;
- se uma run corrigiu, confirmou ou contradisse uma hipótese anterior, essa relação deve aparecer no resumo.

Esse é o efeito de juros compostos da stack: execuções operacionais passadas deixam de ser arquivos mortos e passam a funcionar como memória de longo prazo.

## 8. Qualidade mínima da evidência

Uma boa evidência operacional deve permitir responder:

1. o que foi executado;
2. com qual escopo;
3. quais entradas foram usadas;
4. quais saídas foram produzidas;
5. onde estão os artefatos;
6. qual foi o resultado principal;
7. o que ainda ficou pendente ou parcial.

## 9. O que não fazer

Evitar:

- deixar artefatos soltos sem identificador de execução;
- salvar múltiplas saídas finais sobrescrevendo contexto sem nenhum histórico;
- misturar runbook, changelog e evidência operacional no mesmo documento;
- depender de nomes manuais ou memória humana para descobrir o que foi rodado.

## 10. Template mínimo de registry

```text
recorded_at_utc,run_id,pipeline_run_id,stage,scope,mode,input_fingerprint,status,artifact_dir,note
```

Campos extras podem ser adicionados conforme o domínio, por exemplo:

- métricas;
- versão de schema;
- thresholds;
- ambiente;
- links para dashboards;
- usuário ou automação que disparou a rodada.
