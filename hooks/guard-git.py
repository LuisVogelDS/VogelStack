#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Guardrail de git (PreToolUse em Bash).

Regras fixas, iguais para todo mundo:
  1. mensagem de commit com assinatura de IA (Co-Authored-By/Generated with) -> deny;
  2. `git add` explicito de segredo (*.pem, *.key, .env, .env.*, id_rsa*) -> deny,
     salvo .env.example/.env.sample/.env.template;
  3. force push (-f, --force*, +refspec), inclusive `git -C . push -f`, que a lista
     de permissoes do settings nao pega -> deny.
O escape GUARD_GIT_OK=1 vale so para repo protegido (regra a), nunca para estas.

Regras por configuracao (sem arquivo, elas simplesmente nao existem):
  a. repos protegidos: operacoes que exigem pedido explicito do usuario;
  b. prefixo obrigatorio na mensagem de `git commit -m`, por padrao de remote.

Onde a configuracao e lida, somando o que houver nos tres:
  1. <raiz do repo>/.claude/guard-git.json
  2. ~/.claude/guard-git.json
  3. o arquivo apontado pela variavel VOGEL_GUARD_GIT

Formato (hooks/guard-git.example.json tem um exemplo):
  {
    "repos_protegidos": [
      {"remote": "bitbucket.org/acme/monolito",
       "operacoes": ["pull", "commit", "push"],     # opcional; padrao = todas abaixo
       "motivo": "texto opcional que entra na mensagem"}
    ],
    "prefixo_commit": [
      {"remote": "bitbucket.org/acme/*",
       "regex": "^(PROJ|OPS)-\\d{3,}",              # re.match na 1a linha da mensagem
       "mensagem": "texto opcional que entra na mensagem"}
    ]
  }
  - "remote" e um padrao glob (fnmatch, sem diferenca de maiuscula) contra a URL do
    remote origin normalizada: sem esquema, sem usuario, sem ".git", com "/" no
    lugar do ":" do scp. `git@bitbucket.org:acme/x.git` vira `bitbucket.org/acme/x`.
  - operacoes possiveis: pull, commit, push, checkout, switch, merge, rebase, reset.
  - repo protegido: o escape e repetir o comando com GUARD_GIT_OK=1, so quando o
    usuario pediu aquela operacao de fato.
  - arquivo ilegivel ou entrada malformada e ignorado, nunca derruba o hook.

Por que `deny` e nao `ask`: `ask` de hook nao esta documentado como prompt em
bypassPermissions e, em -p/Agent SDK sem canUseTool, vira negativa de qualquer
jeito. Com `deny` o comportamento e igual em todos os modos.

Fail-open em erro interno: qualquer excecao termina com exit 0. O settings.json
registra o hook com onFailure=block, que so age quando o proprio processo nao
roda (python ausente, timeout), nunca por erro tratado aqui.

O git so e consultado (rev-parse, remote get-url) quando o comando e uma operacao
de git que alguma regra por configuracao poderia cobrir.
"""
import fnmatch
import json
import os
import re
import shlex
import subprocess
import sys

OPS_CONFIG = ("pull", "commit", "push", "checkout", "switch", "merge", "rebase", "reset")
DECISAO_PROTEGIDO = "deny"
ESCAPE_VAR = "GUARD_GIT_OK"
VAR_CONFIG = "VOGEL_GUARD_GIT"
NOME_CONFIG = "guard-git.json"

SEGREDOS = ("*.pem", "*.key", ".env", ".env.*", "id_rsa*")
SEGREDOS_OK = (".env.example", ".env.sample", ".env.template")

ASSINATURA_IA = re.compile(
    r"co-authored-by:\s*claude|generated\s+with\s+\[?claude|noreply@anthropic\.com",
    re.I)

# opcoes globais do git que consomem o argumento seguinte
GLOBAIS_COM_ARG = {"-C", "-c", "--git-dir", "--work-tree", "--namespace", "--exec-path"}


def responde(motivo, decisao="deny"):
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": decisao,
            "permissionDecisionReason": motivo,
        }
    }, ensure_ascii=False))
    sys.exit(0)


def divide_comando(cmd):
    """Divide em subcomandos por && || ; | & e quebra de linha FORA de aspas.

    Aspas simples/duplas e $( ) dentro de aspas duplas mantem o trecho inteiro,
    entao `git commit -m "$(cat <<'EOF' ... EOF)"` continua um unico segmento.
    """
    segs, atual = [], []
    q = None
    i, n = 0, len(cmd)
    while i < n:
        c = cmd[i]
        if q:
            atual.append(c)
            if c == "\\" and q == '"' and i + 1 < n:
                atual.append(cmd[i + 1])
                i += 1
            elif c == q:
                q = None
        elif c in "'\"":
            q = c
            atual.append(c)
        elif c == "\\" and i + 1 < n:
            atual.append(c)
            atual.append(cmd[i + 1])
            i += 1
        elif c in ";&|\n":
            segs.append("".join(atual))
            atual = []
            while i + 1 < n and cmd[i + 1] in ";&|":
                i += 1
        else:
            atual.append(c)
        i += 1
    segs.append("".join(atual))
    return [s.strip() for s in segs if s.strip()]


def tokeniza(seg):
    try:
        return shlex.split(seg, posix=True)
    except ValueError:
        return seg.split()


def msys_para_win(p):
    m = re.match(r"^/([a-zA-Z])(/.*)?$", p)
    if m and os.name == "nt":
        return "%s:%s" % (m.group(1).upper(), (m.group(2) or "/").replace("/", "\\"))
    return p


def resolve_dir(base, p):
    p = os.path.expanduser(msys_para_win(p))
    if not os.path.isabs(p):
        p = os.path.join(base, p)
    return os.path.normpath(p)


def analisa_git(tokens):
    """Retorna (subcomando, args, dir_C, env_ok) ou None se nao for git."""
    i = 0
    env_ok = False
    while i < len(tokens) and re.match(r"^[A-Za-z_][A-Za-z0-9_]*=", tokens[i]):
        if tokens[i].startswith(ESCAPE_VAR + "=1"):
            env_ok = True
        i += 1
    # wrappers simples
    while i < len(tokens) and tokens[i] in ("command", "builtin", "nohup", "time", "exec"):
        i += 1
    if i >= len(tokens) or os.path.basename(tokens[i]).lower() not in ("git", "git.exe"):
        return None
    i += 1
    dir_c = None
    while i < len(tokens) and tokens[i].startswith("-"):
        t = tokens[i]
        if t == "-C" and i + 1 < len(tokens):
            dir_c = tokens[i + 1]
            i += 2
        elif t in GLOBAIS_COM_ARG:
            i += 2
        else:
            i += 1
    if i >= len(tokens):
        return None
    return tokens[i], tokens[i + 1:], dir_c, env_ok


_cache_remote = {}
_cache_config = {}


def git_out(diretorio, *args):
    """Saida do git -C <diretorio> <args> ou None (erro, pasta ausente, timeout)."""
    try:
        if os.path.isdir(diretorio):
            out = subprocess.run(["git", "-C", diretorio] + list(args),
                                 capture_output=True, text=True, timeout=3)
            if out.returncode == 0:
                return out.stdout.strip()
    except Exception:
        pass
    return None


def normaliza_remote(url):
    """URL do remote -> host/dono/repo em minusculas (sem esquema, usuario, porta, .git)."""
    s = url.strip()
    s = re.sub(r"^[A-Za-z][A-Za-z0-9+.-]*://", "", s)
    s = re.sub(r"^[^@/]*@", "", s)
    s = re.sub(r"^([^/:]+):\d+/", r"\1/", s)        # ssh://host:7999/dono/repo
    s = re.sub(r"^([^/:]+):", r"\1/", s)            # scp: host:dono/repo
    s = re.sub(r"\.git/?$", "", s).rstrip("/")
    return s.lower()


def remote_de(diretorio):
    if diretorio not in _cache_remote:
        url = git_out(diretorio, "remote", "get-url", "origin")
        _cache_remote[diretorio] = normaliza_remote(url) if url else None
    return _cache_remote[diretorio]


def carrega_arquivo(caminho):
    try:
        with open(caminho, encoding="utf-8-sig") as fh:
            dados = json.load(fh)
        return dados if isinstance(dados, dict) else {}
    except Exception:
        return {}


def carrega_config(diretorio):
    """(repos_protegidos, prefixo_commit) somados: do repo, do usuario e de VOGEL_GUARD_GIT."""
    if diretorio in _cache_config:
        return _cache_config[diretorio]
    caminhos = []
    raiz = git_out(diretorio, "rev-parse", "--show-toplevel")
    if raiz:
        caminhos.append(os.path.join(raiz, ".claude", NOME_CONFIG))
    caminhos.append(os.path.join(os.path.expanduser("~"), ".claude", NOME_CONFIG))
    extra = os.environ.get(VAR_CONFIG)
    if extra:
        caminhos.append(os.path.expanduser(extra))
    protegidos, prefixos, vistos = [], [], set()
    for c in caminhos:
        chave = os.path.normcase(os.path.abspath(c))
        if chave in vistos:
            continue
        vistos.add(chave)
        dados = carrega_arquivo(c)
        for e in dados.get("repos_protegidos") or []:
            if isinstance(e, dict) and isinstance(e.get("remote"), str):
                protegidos.append(e)
        for e in dados.get("prefixo_commit") or []:
            if (isinstance(e, dict) and isinstance(e.get("remote"), str)
                    and isinstance(e.get("regex"), str)):
                prefixos.append(e)
    _cache_config[diretorio] = (protegidos, prefixos)
    return _cache_config[diretorio]


def casa_remote(padrao, remote):
    return fnmatch.fnmatchcase(remote, padrao.strip().lower())


def e_force_push(args):
    for a in args:
        if a == "--":
            break
        if a.startswith("--force"):          # --force, --force-with-lease, --force-if-includes
            return True
        if a.startswith("-") and not a.startswith("--") and "f" in a[1:]:
            return True                      # -f, -fu, -uf
        if a.startswith("+") and len(a) > 1:  # refspec +main
            return True
    return False


def primeira_mensagem(seg, args):
    """Primeira mensagem de commit (-m / --message) ou None se nao der para saber."""
    msg = None
    i = 0
    while i < len(args):
        a = args[i]
        if a == "-m" or a == "--message":
            msg = args[i + 1] if i + 1 < len(args) else None
            break
        if a.startswith("--message="):
            msg = a[len("--message="):]
            break
        if re.match(r"^-[a-zA-Z]*m.+$", a) and not a.startswith("--"):
            msg = a[a.index("m") + 1:]       # -mPROJ-1 ou -amPROJ-1
            break
        if re.match(r"^-[a-zA-Z]*m$", a) and not a.startswith("--") and i + 1 < len(args):
            msg = args[i + 1]                # -am "texto"
            break
        i += 1
    if msg is None:
        return None
    msg = msg.strip()
    if msg.startswith("$(") or msg.startswith("`"):
        # heredoc: primeira linha nao vazia depois da linha de abertura <<EOF
        m = re.search(r"<<-?\s*['\"]?(\w+)['\"]?[^\n]*\n(.*)", msg, re.S)
        if not m:
            return None                      # nao da para inspecionar: nao bloqueia
        for linha in m.group(2).splitlines():
            if linha.strip():
                return linha.strip()
        return None
    if msg.startswith("$"):
        return None                          # variavel: nao da para saber
    return msg


def main():
    try:
        payload = json.load(sys.stdin)
    except Exception:
        sys.exit(0)

    ti = payload.get("tool_input") or {}
    cmd = ti.get("command") or ""
    if "git" not in cmd.lower():
        sys.exit(0)

    cwd = payload.get("cwd") or os.getcwd()
    cwd = msys_para_win(cwd)

    atual = cwd
    for seg in divide_comando(cmd):
        tokens = tokeniza(seg)
        if not tokens:
            continue

        # cd x && git ...
        if tokens[0] == "cd" and len(tokens) >= 2:
            atual = resolve_dir(atual, tokens[1])
            continue
        if tokens[0] in ("pushd",) and len(tokens) >= 2:
            atual = resolve_dir(atual, tokens[1])
            continue

        info = analisa_git(tokens)
        if not info:
            continue
        sub, args, dir_c, env_ok = info
        alvo = resolve_dir(atual, dir_c) if dir_c else atual

        # 3. force push (nao depende do repo)
        if sub == "push" and e_force_push(args):
            responde("force push proibido (nunca force push). "
                     "Se houver divergencia, parar e avisar o usuario.")

        # 2. segredo no git add explicito
        if sub == "add":
            for a in args:
                if a.startswith("-"):
                    continue
                base = os.path.basename(a.replace("\\", "/")).lower()
                if base in SEGREDOS_OK:
                    continue
                if any(fnmatch.fnmatch(base, p) for p in SEGREDOS):
                    responde("git add de segredo (%s) bloqueado: nunca versionar .pem, "
                             ".key, .env ou credencial. Se for outro arquivo, adicione "
                             "por outro caminho; se for mesmo um segredo, nao versione." % a)

        # 1. assinatura de IA na mensagem
        if sub == "commit" and ASSINATURA_IA.search(seg):
            responde("commit com assinatura de IA na mensagem bloqueado "
                     "(nunca mencionar IA em mensagem de commit). "
                     "Remova Co-Authored-By/Generated with e tente de novo.")

        if sub not in OPS_CONFIG:
            continue
        protegidos, prefixos = carrega_config(alvo)
        if not protegidos and not prefixos:
            continue
        remote = remote_de(alvo)
        if remote is None:
            continue

        # a. repo protegido (configuracao)
        if not env_ok:
            for e in protegidos:
                ops = e.get("operacoes") or OPS_CONFIG
                if sub in ops and casa_remote(e["remote"], remote):
                    motivo = (" " + e["motivo"]) if isinstance(e.get("motivo"), str) else ""
                    responde("%s: so com pedido explicito do usuario (git %s).%s "
                             "Peca confirmacao ao usuario; se ele ja pediu esta operacao, "
                             "repita o comando prefixado com %s=1."
                             % (remote, sub, motivo, ESCAPE_VAR), DECISAO_PROTEGIDO)

        # b. prefixo obrigatorio na mensagem (configuracao)
        if sub == "commit":
            msg = primeira_mensagem(seg, args)
            if msg is not None:
                for e in prefixos:
                    if not casa_remote(e["remote"], remote):
                        continue
                    try:
                        ok = re.match(e["regex"], msg) is not None
                    except re.error:
                        continue
                    if not ok:
                        texto = e["mensagem"] if isinstance(e.get("mensagem"), str) else \
                            "a mensagem de commit precisa casar com %s" % e["regex"]
                        responde("%s (repo %s). Sem o prefixo, nao commitar: pedir ao "
                                 "usuario. Nunca inventar." % (texto, remote))

    sys.exit(0)


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except Exception:
        sys.exit(0)   # fail-open em erro interno
