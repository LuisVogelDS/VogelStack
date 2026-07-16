# ADR 0002 — Remover a família padrão e colapsar a stack numa via única

- **Status:** Aceito
- **Data:** 2026-06-28 (decisão, materializada em `4fe8079`) · 2026-07-16 (este registro consolidado)
- **Decisor:** LuisVogelDS
- **Relação:** supersede parcialmente o [[0001-adotar-operacao-leve|ADR 0001]] — mantém a operação escolhida lá, remove a dualidade que a cercava
- **Princípios aplicáveis:** nº 19 ([[vogel-stack/principios|Problema, não tecnologia]]) e nº 11 ([[vogel-stack/principios|Modos de execução suportados devem ser explícitos]])

> **Nota de registro (2026-07-16).** Esta decisão foi tomada e materializada em **2026-06-28** (commit `4fe8079`), sob um registro anterior — `0002-aposentar-familia-graphify.md`. Em 16/07 o mesmo arco foi refeito numa branch partida de base defasada, produzindo um **segundo** registro do mesmo `0002`, sem saber do primeiro. Na reconciliação ficou este texto, por ser o mais completo, mas com a **data real da decisão**; o registro anterior saiu por ser duplicata, não por mudança de mérito — o mérito nunca esteve em disputa, as duas versões decidiam o mesmo. O episódio motivou a [[vogel-stack/operacao-agentes#1.1 Checklist antes de começar uma alteração|§1.1 — Checklist antes de começar uma alteração]], que existe para impedir exatamente esse trabalho sobre base defasada.

## Contexto

Desde 2026-05-28 a stack oferecia **duas famílias de operação documental**:

- **padrão** — knowledge graph materializado em `graphify-out/`, com vault visual versionado;
- **leve** — wikilinks curados + link checker determinístico + agente sob demanda.

Na prática, **nenhum projeto do ecossistema adotou a família padrão**. O próprio repositório da stack migrou para a leve em 2026-06-12 ([[0001-adotar-operacao-leve|ADR 0001]]), e os consumidores (PlacarBI, CartaoVermelho, ScoutCamisa10, MemoriaRam, guaraci e demais) operam todos na leve.

O custo da dualidade era real e recorrente:

- ~115 menções à ferramenta padrão espalhadas por 13 arquivos, descrevendo um fluxo que ninguém executa;
- o [[quickstart]] era majoritariamente dedicado ao caminho não usado, empurrando o caminho real para o fim do documento;
- [[vogel-stack/operacao-leve|operacao-leve]] se definia **por contraste** ("sem X, sem Y") em vez de se definir pelo que é;
- todo projeto novo gastava uma decisão ("qual família?") cuja resposta já era sempre a mesma.

Isso feria o princípio nº 1 ([[vogel-stack/principios|comportamento documentado reflete o sistema real]]): a documentação descrevia uma capacidade que a prática não usava.

## Decisão

**Colapsar a stack para uma via única.** A operação antes chamada "leve" deixa de ser alternativa e passa a ser simplesmente **a operação documental da Vogel Stack**:

| Problema | Solução única |
|---|---|
| Relacionamento entre docs | Wikilinks curados (`[[node]]`) |
| Detecção de link quebrado | Link checker determinístico + CI (sem LLM) |
| Mapa para agente | `AGENTS.md` / `CLAUDE.md` + hub curado |
| Auditoria estrutural | Agente de IA sob demanda, com prompt explícito |
| Visualização gráfica | Ferramenta local do usuário, não versionada |

O princípio nº 19 ("Problema, não tecnologia") **não é revogado — é aplicado**: a stack deixa de carregar uma ferramenta por convenção e passa a declarar a solução que o problema real exige. O nº 11 segue valendo: há um modo de execução suportado, e ele é explícito.

## Consequências

- [[quickstart]] reescrito: descreve a adoção da via única, sem "como escolher família" e sem o fluxo de grafo materializado.
- [[vogel-stack/operacao-leve|operacao-leve]] reescrito: passa a se definir pelo que é. **O nome do arquivo foi mantido de propósito** — os projetos consumidores linkam `[[vogel-stack/vogel-stack/operacao-leve]]`, e renomear quebraria a malha de todos de uma vez. O nome é resquício histórico, não descrição.
- Princípios nº 17, 18 e 19 reformulados para descrever a via única. O nº 11 não foi tocado (já era genérico).
- `AGENTS.md`, `CLAUDE.md` e [[vogel-stack/README|README da stack]] perdem as seções de escolha de família.
- Projetos consumidores **não precisam agir**: já operavam nesta via. O que muda é que ela deixa de ser "uma opção" e passa a ser o padrão descrito.
- Perde-se a documentação do caminho com grafo materializado. Se algum projeto futuro precisar dele, a decisão volta como ADR **daquele projeto** (princípio nº 19), sem a stack carregar o aparato por antecipação.

## Gatilhos para reabrir

Reavaliar se algum dia: um projeto cruzar volume documental que torne a malha curada insuficiente (~80 docs ou ~500KB de markdown); surgir material bruto extenso exigindo inferência para conectar com docs canônicos; ou múltiplos agentes externos frios passarem a consumir os repos sem contexto carregado.

Nesse caso a solução é declarada **no projeto que tem o problema**, não reintroduzida na stack por padrão.
