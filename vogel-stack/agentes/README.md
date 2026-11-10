# Modelos de subagente

Sete definições de subagente do Claude Code, prontas para copiar. Cada arquivo vai para `~/.claude/agents/` (vale em todo projeto da máquina) ou para `.claude/agents/` do repositório (vale só nele). A regra de quando usar cada tipo, com o porquê, está na [[operacao-agentes|Operação de Agentes]] (§2.3, "Tipo de trabalho define modelo e esforço") e a skill `orquestrar-frente` a aplica no plano. Aqui ficam só os moldes, para a regra não se afastar do que roda.

| Tipo | Para quê | Modelo e esforço |
|---|---|---|
| `executor` | implementar o que já tem plano ou padrão a seguir (feature, tela, módulo, teste) | sonnet, médio |
| `corretor` | corrigir na raiz uma falha que já está à mão (bateria, teste ou build reprovado) | sonnet, alto |
| `leitor` | levantamento só de leitura, com conclusão curta e `arquivo:linha` | haiku, médio, sem edição |
| `mecanico` | trabalho mecânico sem decisão (changelog, quadro, renomear, conferir lista) | haiku, baixo |
| `especialista` | domínio difícil ou depuração que já falhou (física, câmera, concorrência) | opus, médio |
| `arquiteto` | planejar antes de mudança que atravessa camadas, devolvendo o plano e não o código | opus, alto, sem edição |
| `validador` | conferir uma lista de validações pronta e devolver um laudo curto | haiku, médio, sem edição |

O roteamento de modelo mora na definição do agente (campos `model` e `effort` do cabeçalho), e não num hook nem no prompt de quem delega. Trocar o modelo de um tipo é editar o arquivo dele, e o plano ainda pode discordar do padrão de um item, com o motivo na descrição. Os campos `tools` e `disallowedTools` fecham o que cada tipo pode fazer: leitor, arquiteto e validador não editam, e o validador não passa de 30 turnos.

Os modelos não trazem ferramenta específica de um ambiente (um MCP de navegador, por exemplo). Quem precisar dela acrescenta o nome à linha `tools` da sua cópia. Depois de copiar, vale ajustar a `description`, porque é ela que o Claude lê para decidir quando delegar a cada tipo.
