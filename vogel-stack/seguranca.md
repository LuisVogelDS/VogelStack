# Segurança e Privacidade

Este documento define os guardrails de segurança da stack e a **checagem objetiva** que precede qualquer exposição de um sistema a usuários, rede ou terceiros.

Ele não pretende cobrir segurança ofensiva, conformidade formal ou auditoria externa. O alvo é outro e mais modesto: **evitar as brechas previsíveis** — as que aparecem por descuido de fronteira, não por ataque sofisticado. Todas as regras aqui são verificáveis; nenhuma depende de julgamento subjetivo, conforme [[principios|Princípios Gerais]] nº 3.

Cada seção declara **quando se aplica**. Projeto sem login não precisa da seção de autenticação; projeto sem dado pessoal não precisa da de privacidade. Aplicar tudo em tudo é ruído.

## 1. Os quatro princípios de fronteira

Quase toda brecha real observada em projetos desta stack viola um destes quatro. Eles vêm antes de qualquer checklist.

**1.1. Perímetro de rede não é controle de acesso.** VPN, firewall e Security Group reduzem *quem alcança* o sistema. Eles não autenticam, não autorizam e não deixam trilha. Um sistema cuja única defesa é a rede tem **defesa em profundidade zero**: uma credencial de VPN vazada, um host interno comprometido ou uma regra editada por engano expõem tudo de uma vez. Rede é uma camada, nunca *a* camada.

**1.2. Tudo que vai ao cliente é público.** Bundle, JavaScript, HTML e variáveis embutidas em build (`VITE_*`, `NEXT_PUBLIC_*`, `REACT_APP_*`) são legíveis por qualquer visitante — por construção, não por falha. Segredo em variável de cliente é segredo publicado.

**1.3. Validação no cliente não é fronteira.** O que roda no browser é experiência do usuário, não enforcement. Qualquer verificação client-side pode ser removida editando o JS ou chamando a API direto. Toda decisão de acesso é do servidor, sempre.

**1.4. O gate precisa estar no caminho do dado.** Um gate protege apenas o que passa por ele. Se a autenticação vive num processo e o dado é servido por outro (ex.: nginx servindo arquivo estático), o gate é **cosmético**: esconde na interface e entrega no `curl`. Gate de UI e gate de dado são coisas diferentes.

## 2. Segredos

**Aplica-se a:** todo projeto.

- Segredo nunca em variável exposta ao cliente (`VITE_*`, `NEXT_PUBLIC_*`, `REACT_APP_*`). Se o cliente precisa "verificar" algo assinado, a verificação está no lugar errado — mova para o servidor (princípio 1.2/1.3).
- Segredo nunca versionado. Arquivo de credencial fica no `.gitignore`, com um `*.example` sem segredo como referência versionada.
- Chave simétrica (HS256) **assina e verifica com a mesma chave** — só pode existir onde o token é *emitido* ou *verificado no servidor*. Se as duas pontas não são confiáveis, use assimétrico (RS256/JWKS): a pública verifica, a privada assina.
- Segredo vazado exige **rotação**; remover do código ou do histórico não invalida a cópia que já saiu.
- Segredo compartilhado entre sistemas amplia o raio: vazar num vaza em todos.

## 3. Autenticação

**Aplica-se a:** projeto com login próprio ou que consome token de terceiro.

- **Onde se valida:** no servidor. Sempre.
- **Algoritmo travado:** ao verificar JWT, fixe `algorithms: ["HS256"]` (ou o que for). Aceitar o `alg` do token permite `alg: none` e confusão RS256→HS256.
- **Valide as claims:** assinatura, `exp`, `iss`, `aud`. Assinatura válida não basta — token de outro serviço também tem assinatura válida.
- **Token em header** (`Authorization`, ou header próprio), nunca em **query string**: URL vaza em log de servidor, log de proxy/CDN, header `Referer` e histórico do browser.
- **Limite de tentativas:** rate limit por IP **e** por conta nos endpoints de login, troca e recuperação de senha. Sem isso, senha de 8 caracteres cai por força bruta. Lockout progressivo (ou atraso incremental) para a conta.
- **Não revele existência de conta:** mensagem genérica ("usuário ou senha inválidos") **e** tempo de resposta equalizado (rode um hash descartável quando o usuário não existir — senão o *timing* entrega). Vale igual para cadastro e "esqueci a senha".
- **Superfície não construída é superfície segura:** recuperação de senha self-service é um vetor; se o reset manual atende, é uma escolha legítima.
- **MFA:** exigível quando há dado pessoal, dado financeiro ou acesso administrativo. Não é obrigatório em ferramenta interna de baixo impacto — mas a decisão deve ser explícita.

## 4. Sessão

**Aplica-se a:** projeto com sessão de usuário.

- **Logout precisa invalidar do lado do servidor.** Apagar cookie ou limpar `localStorage` remove a credencial *daquele browser* — o token continua válido até expirar. JWT puro é *stateless*: sem lista de revogação (ou versão de sessão por usuário), não existe logout real.
- **TTL curto** quando não há revogação. Sete dias sem revogação significa sete dias de acesso para um token copiado.
- **Cookie:** `HttpOnly` (fora do alcance de XSS), `SameSite=Lax` ou `Strict`, e `Secure` sempre que houver TLS. Cookie de sessão é preferível a `localStorage`, que é legível por qualquer script.

## 5. Autorização

**Aplica-se a:** projeto com mais de um usuário, perfil ou cliente.

- **Deny-by-default e falha-fechada:** sem política carregada ou sem segredo configurado, negue. Nunca "libera enquanto não configura" — é assim que produção sobe aberta.
- **Autenticar ≠ autorizar.** Saber *quem é* não diz *o que pode ver*. Verifique posse do objeto a cada requisição (é a falha nº 1 do OWASP API: acesso a objeto de outro usuário trocando o id na URL).
- **O gate no caminho do dado** (princípio 1.4): se o dado sai por arquivo estático, ou o servidor de arquivo aplica a política, ou o dado sai de trás de um handler que aplica. Esconder item na interface não é controle.
- **Modo de desenvolvimento não pode virar bypass em produção.** Se a proteção depende de uma env estar setada, o deploy tem que falhar quando ela falta — não ficar aberto silenciosamente.

## 6. Transporte

**Aplica-se a:** todo sistema que trafega credencial, sessão ou dado pessoal — inclusive em rede interna.

- **TLS não é opcional para credencial e dado pessoal.** "Está atrás da VPN" não substitui: rede interna é sniffável, e o comprometimento de um host interno é o cenário mais comum.
- Sem TLS, o cookie não pode ter `Secure`, e a sessão trafega em claro. Um puxa o outro.
- Com TLS, adicione HSTS.

## 7. Dados pessoais

**Aplica-se a:** projeto que armazena ou serve dado de pessoa física (LGPD).

- **Minimize o que sai:** envie os campos necessários àquela tela, não a linha inteira. Agregar no servidor (em vez de mandar o grão cru e agregar no cliente) resolve *ao mesmo tempo* peso e exposição.
- **Criptografar o payload da API não resolve "dados demais".** Para o cliente decriptar, a chave estaria no cliente — ou seja, pública (princípio 1.2). Quem protege o transporte é TLS; quem resolve excesso é **enviar menos** e **autorizar por objeto/campo**. Criptografia de aplicação só faz sentido quando o servidor **não deve** ver o dado — raro fora de mensageria.
- **Dado pessoal exige gate de aplicação e trilha de acesso.** Perímetro de rede não é controle de acesso (1.1) e não produz log de quem leu o quê. Sem isso, não há como responder "quem acessou?" — pergunta central em incidente e em auditoria LGPD.
- Defina **retenção**: dado que não precisa existir é risco sem contrapartida.
- Nunca registre dado pessoal ou segredo em log, em mensagem de erro devolvida ao cliente, ou em stack trace exposta.

## 8. Consulta e execução

**Aplica-se a:** projeto que consulta banco ou executa processo.

- **Valores viram parâmetros**, sempre (`$1` no `pg`, `request.input()` no `mssql`). Nunca interpolação de string com valor externo.
- **Identificadores** (tabela, coluna) não aceitam parâmetro: resolva contra o catálogo (`information_schema`) ou contra uma allowlist fixa, e aplique o quoting do dialeto (`"` com escape `""` no PostgreSQL, `[` `]` com escape `]]` no T‑SQL).
- **Numérico externo:** coaja e limite (`Math.floor(Number(x))` + faixa) antes de qualquer uso.
- **Processo:** `spawn` com array de argumentos, nunca `shell: true` com string montada. Argumento derivado de entrada externa precisa ser validado para não virar flag.
- **Não devolva `stderr`/`stdout` cru ao cliente:** vaza caminho, host, nome de banco e versão.

## 9. Fronteira do browser

**Aplica-se a:** aplicação web.

- **CSP é header HTTP.** `frame-ancestors`, `report-uri` e `sandbox` são **ignorados** quando entregues por `<meta>` — a meta tag como "fallback" é falsa sensação de segurança. Se o app é embedável, `frame-ancestors` precisa sair da borda que serve o HTML (nginx/CDN), não do servidor de desenvolvimento.
- **A CSP do dev não protege produção.** Header configurado no dev/preview server não existe num `dist/` servido por nginx. Configuração de borda é parte do deploy e precisa ser versionada.
- **CORS não é um cadeado — é a chave que afrouxa a trava.** O browser já bloqueia leitura cross-origin por padrão; CORS *permite*. Portanto:
  - **ausência de CORS = postura restritiva** (correto na maioria dos casos);
  - o risco é CORS **permissivo** (`*`, ou refletir qualquer `Origin`), sobretudo com `Allow-Credentials`;
  - **CORS não protege API alguma** — só existe dentro do browser; `curl` o ignora. Nunca use CORS como substituto de autenticação.
- **postMessage:** valide a origem na entrada e use `targetOrigin` específico na saída (nunca `*`). Cuidado com matcher de wildcard que aceite `evil-dominio.com.br`.
- Headers baratos que valem sempre: `X-Content-Type-Options: nosniff`, `Referrer-Policy`, e uma CSP com `default-src`/`script-src` (a de `frame-ancestors` sozinha não mitiga XSS).

## 10. Dependências

**Aplica-se a:** todo projeto com gerenciador de pacotes.

- Instale por manifesto (`npm ci`), não por resolução livre.
- Rode `npm audit` (ou equivalente) na rodada que mexer em dependência; trate `high`/`critical` como bloqueio.
- Dependência nova é superfície nova: prefira o que já existe no projeto ([[principios|Princípios Gerais]] nº 19, "Problema, não tecnologia").

## 11. Checagem antes de expor

Rodar **antes de** publicar, abrir acesso ou mudar fronteira (auth, deploy, dado servido, endpoint novo). O agente executa o que for automatizável e apresenta o resto conforme [[operacao-agentes|Operação de Agentes]]. Cada resposta é verificável — "acho que sim" reprova.

| # | Pergunta | Como verificar | Reprova se |
|---|---|---|---|
| 1 | Algum segredo em variável de cliente? | `grep -rE "VITE_\|NEXT_PUBLIC_\|REACT_APP_" src/ \| grep -iE "secret\|key\|token\|password"` | qualquer resultado |
| 2 | O segredo chegou ao bundle? | buildar e procurar o valor em `dist/assets/*.js` | encontrado |
| 3 | Algum segredo versionado? | `git ls-files \| grep -iE "\.env$\|config.json\|\.pem$\|\.key$"` | qualquer resultado |
| 4 | O gate está no caminho do dado? | `curl` no dado **sem** credencial, contra o que serve em produção | responde 200 |
| 5 | Dado pessoal tem gate de aplicação (não só rede)? | identificar quem serve o arquivo/rota com PII | só a rede protege |
| 6 | Login tem rate limit e lockout? | `grep -riE "rate.?limit\|throttl\|lockout\|429"` | nada encontrado |
| 7 | Erro de login revela existência de conta? | comparar corpo **e tempo** de resposta: usuário inexistente × senha errada | diferem |
| 8 | Logout invalida no servidor? | usar o token **depois** do logout | continua válido |
| 9 | Token em query string? | `grep -rE "\?token=\|access_token=\|location.search"` | token vindo da URL |
| 10 | JWT com algoritmo travado e `exp`/`iss`/`aud`? | ler a chamada de verificação | `algorithms` ausente |
| 11 | TLS ativo onde trafega credencial/PII? | `grep -rE "listen 443\|ssl_certificate"` na config de borda | ausente |
| 12 | Cookie com `HttpOnly` + `SameSite` (+ `Secure` se há TLS) | ler o `Set-Cookie` | faltando |
| 13 | SQL com valor interpolado? | `grep -rE "SELECT.*\\$\{"` | valor (não identificador) interpolado |
| 14 | Proteção depende de env que pode faltar? | ler o fallback quando a env está vazia | fica aberto em vez de falhar |
| 15 | CSP/`frame-ancestors` sai como **header** da borda? | `curl -I` no host real | só existe em `<meta>` ou só no dev |
| 16 | CORS permissivo? | `grep -riE "Allow-Origin.*\*\|cors"` | `*` com credenciais |
| 17 | Resposta devolve `stderr`/stack ao cliente? | ler o handler de erro | devolve cru |
| 18 | Dependências com vulnerabilidade conhecida? | `npm audit` | `high`/`critical` |

**Registro:** o resultado da checagem entra na rodada como evidência, conforme [[registro-e-evidencias|Registro e Evidências Operacionais]]. Item reprovado que **não** será corrigido agora vira linha explícita no quadro de trabalho — risco aceito é decisão, e decisão fica registrada ([[operacao-agentes|Operação de Agentes]] §7.1.1).

## 12. Como reportar problema encontrado

- **Achado vai para o responsável, no canal de trabalho** — com evidência (`arquivo:linha`), risco concreto e correção proposta.
- **O repositório documenta o guardrail, não o incidente.** Changelog, quadro e mensagem de commit registram a convenção resultante ("`config.json` é local e usa cofre"), redigida de forma neutra e prospectiva. Narrar a falha no repo confunde quem lê depois e não agrega defesa.
- **Segredo exposto exige rotação, não só remoção.** Tirar do código ou reescrever o histórico não invalida o que já foi copiado. Sem rotação, a limpeza é cosmética.
- Nunca cole segredo, credencial ou dado pessoal em issue, log, changelog ou mensagem de commit.

## Documentos relacionados

- [[principios|Princípios Gerais]] — clareza operacional (nº 3), contratos explícitos (nº 5), "Problema, não tecnologia" (nº 19).
- [[operacao-agentes|Operação de Agentes]] — quando o agente executa e quando prepara o comando; o quadro de trabalho.
- [[registro-e-evidencias|Registro e Evidências Operacionais]] — onde fica a evidência da checagem.
- [[documentacao-e-versionamento|Documentação e Versionamento]] — como a convenção entra no changelog.
- [[evolucao-produto|Evolução de Produto e Arquitetura]] — quando a correção é estrutural e não patch.
