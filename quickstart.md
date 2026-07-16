# Quickstart: Vogel Stack

Este guia mostra como instalar a Vogel Stack em outro repositório e operar a documentação no padrão dela.

A operação documental é **uma só**, descrita em [[vogel-stack/operacao-leve|Operação Documental]]: wikilinks curados como malha, link checker determinístico como piso de integridade, e agente de IA sob demanda para auditoria estrutural. **Não há família a escolher** — até 2026-07-16 havia duas, e a dualidade foi removida ([[docs/adr/0002-remover-familia-padrao|ADR 0002]]).

Se o projeto tiver um problema que essa operação não resolve, o princípio nº 19 ([[vogel-stack/principios|Problema, não tecnologia]]) manda declarar a solução alternativa em ADR **do próprio projeto** — não herdar ferramenta por convenção, nem esperar que a stack carregue o aparato por antecipação.

## Conexões principais

- [[vogel-stack/principios|Princípios Gerais]]
- [[vogel-stack/documentacao-e-versionamento|Documentação e Versionamento]]
- [[vogel-stack/operacao-agentes|Operação de Agentes]]
- [[vogel-stack/registro-e-evidencias|Registro e Evidências Operacionais]]
- [[vogel-stack/evolucao-produto|Evolução de Produto e Arquitetura]]
- [[vogel-stack/templates|Templates de Documentação]]
- [[vogel-stack/operacao-leve|Operação Documental]]

## 1. Instalar a stack como submódulo

No repositório alvo:

```powershell
Set-Location "C:\caminho\para\repo-alvo"
git submodule add https://github.com/LuisVogelDS/VogelStack vogel-stack
git submodule update --init --recursive
```

Isso instala o repositório inteiro da Vogel Stack dentro de `vogel-stack/`. Com a estrutura atual, os documentos-base ficam em:

```text
vogel-stack/
  vogel-stack/
    principios.md
    documentacao-e-versionamento.md
    operacao-agentes.md
    registro-e-evidencias.md
    evolucao-produto.md
    templates.md
    operacao-leve.md
```

Por causa dessa pasta interna, os wikilinks do projeto-alvo usam o prefixo `vogel-stack/vogel-stack/` — por exemplo `[[vogel-stack/vogel-stack/principios]]`. O que importa é que o link aponte para um arquivo real que o checker consiga resolver.

## 2. Conectar o projeto à stack por wikilinks reais

Peça a um agente forte que leia a documentação do projeto e insira wikilinks explícitos onde houver dependência real:

```text
Baseado na Vogel Stack instalada neste repositório, revise README, AGENTS.md, CLAUDE.md,
quickstart.md, docs/arquitetura.md, docs/operacao.md, docs/versionamento.md,
docs/changelog.md e outros guias existentes.

Objetivo: conectar o núcleo técnico e operacional deste projeto aos princípios da
Vogel Stack sem inventar dependências.

Tarefas:

1. Leia a documentação do projeto e os arquivos da stack antes de editar.
2. Insira links explícitos para arquivos reais da stack sempre que um processo, script,
   job, pipeline, dashboard, artefato ou contrato precisar seguir uma regra específica.
3. Todo documento novo ou revisado deve nascer conectado (princípio nº 18).
4. Nada de link decorativo — cada link representa dependência real.
5. Se a stack está em `vogel-stack/` contendo outra pasta `vogel-stack/`, use o
   prefixo `vogel-stack/vogel-stack/`.

Destinos-guia:

- [[vogel-stack/principios]] — princípios permanentes, fontes de verdade, contratos,
  identificadores canônicos, observabilidade, semântica de saída.
- [[vogel-stack/documentacao-e-versionamento]] — papéis dos documentos, quickstart,
  arquitetura, versionamento, changelog.
- [[vogel-stack/operacao-agentes]] — execuções por agentes, comandos caros, handoffs,
  logs persistentes, política de custo.
- [[vogel-stack/registro-e-evidencias]] — registry, manifestos por run, rastreabilidade.
- [[vogel-stack/evolucao-produto]] — mudanças de produto, dashboards, concepção.
- [[vogel-stack/templates]] — criar ou corrigir documentos padrão.

Ao terminar, liste: arquivos alterados, links adicionados, lacunas documentais
encontradas e comandos recomendados para validar.
```

## 3. Instalar o piso: link checker + CI

A malha só é contrato se link quebrado quebrar a build.

- Criar `scripts/check-wikilinks.ps1` — valida todo `[[wikilink]]`, suporta `[[alvo|alias]]` e `[[alvo#secao]]`, ignora blocos de código e sai com código 1 em quebra. A implementação de referência é a deste repositório.
- Criar `.github/workflows/check-malha.yml` para rodar o checker em push/PR para `main`.
- Rodar localmente e corrigir tudo **antes** do commit:

```powershell
pwsh ./scripts/check-wikilinks.ps1
```

## 4. Declarar as decisões do projeto em ADR

Pelo princípio nº 19, o projeto declara em ADR próprio qualquer solução que adote diferente da que a stack descreve — listando a substituição problema-a-problema e referenciando o princípio. Modelos em [[vogel-stack/templates|Templates de Documentação]].

Se o projeto simplesmente segue a operação da stack, não é preciso ADR para isso: o default é o que está descrito aqui.

## 5. Auditoria estrutural sob demanda

Não há relatório de grafo materializado. Quando precisar do equivalente — órfãos, weak links, comunidades isoladas — invoque o agente com o prompt-template de [[vogel-stack/operacao-leve|Operação Documental]] e revise a saída antes de aplicar.

## Guias de apoio

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
git commit -m "Atualiza submodulo VogelStack"
```

Feito isso, confirme que os wikilinks continuam apontando para arquivos reais:

```powershell
pwsh ./scripts/check-wikilinks.ps1
```

### Quadro de trabalho

Projetos da stack mantêm um `_QUADRO.md` (backlog vivo, formato padronizado) validado por `scripts/check-quadro.ps1`. Ver [[vogel-stack/templates|Templates de Documentação]].
