#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Guardrail de git (PreToolUse em Bash). Materializa regras absolutas do
CLAUDE.md global ("Commit e push: quem decide e o dono do repositorio").

Regras:
  a. repo 2morrowSports/monolith: pull/commit/push/checkout/switch/merge/rebase/
     reset so com pedido explicito do usuario (MONOLITH_DECISAO abaixo);
  b. qualquer repo bitbucket.org/2morrowSports/*: `git commit -m` precisa
     comecar com SFT-#### ou STC-####;
  c. qualquer repo: mensagem de commit com assinatura de IA -> deny;
  d. `git add` explicito de segredo (*.pem, *.key, .env, id_rsa*) -> deny;
  e. force push (reforco do permissions.deny, que nao pega `git -C . push -f`).

Por que `deny` e nao `ask` na regra a: ver MONOLITH_DECISAO.

Fail-open em erro interno: qualquer excecao termina com exit 0. O settings.json
registra o hook com onFailure=block, que so age quando o proprio processo nao
roda (python ausente, timeout), nunca por erro tratado aqui.

O git so e consultado (remote get-url) quando o comando tem git de fato e a
regra depende do dono do repo.
"""
import fnmatch
import json
import os
import re
import shlex
import subprocess
import sys

# "deny" porque `ask` de hook nao esta documentado como prompt em
# bypassPermissions e, em -p/Agent SDK sem canUseTool, vira negativa de qualquer
# jeito. Com "deny" o comportamento e igual em todos os modos. Escape: o motivo
# manda repetir o comando com GUARD_GIT_OK=1 quando o usuario pediu de fato.
MONOLITH_DECISAO = "deny"
MONOLITH_OPS = {"pull", "commit", "push", "checkout", "switch", "merge", "rebase", "reset"}
ESCAPE_VAR = "GUARD_GIT_OK"

SEGREDOS = ("*.pem", "*.key", ".env", ".env.*", "id_rsa*")
SEGREDOS_OK = (".env.example", ".env.sample", ".env.template")

ASSINATURA_IA = re.compile(
    r"co-authored-by:\s*claude|generated\s+with\s+\[?claude|noreply@anthropic\.com",
    re.I)
JIRA = re.compile(r"^(SFT|STC)-\d{3,}\b")
REMOTE_2M = re.compile(r"bitbucket\.org[:/]+2morrowsports/([^/\s]+?)(?:\.git)?/?$", re.I)

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


def repo_2morrow(diretorio):
    """Nome do repo em bitbucket.org/2morrowSports/<nome> ou None."""
    if diretorio in _cache_remote:
        return _cache_remote[diretorio]
    nome = None
    try:
        if os.path.isdir(diretorio):
            out = subprocess.run(["git", "-C", diretorio, "remote", "get-url", "origin"],
                                 capture_output=True, text=True, timeout=3)
            if out.returncode == 0:
                m = REMOTE_2M.search(out.stdout.strip())
                if m:
                    nome = m.group(1).lower()
    except Exception:
        nome = None
    _cache_remote[diretorio] = nome
    return nome


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
            msg = a[a.index("m") + 1:]       # -mSFT-1 ou -amSFT-1
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

        # e. force push (nao depende do dono do repo)
        if sub == "push" and e_force_push(args):
            responde("force push proibido (CLAUDE.md global: nunca force push). "
                     "Se houver divergencia, parar e avisar o usuario.")

        # d. segredo no git add explicito
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

        # c. assinatura de IA na mensagem
        if sub == "commit" and ASSINATURA_IA.search(seg):
            responde("commit com assinatura de IA na mensagem bloqueado "
                     "(CLAUDE.md global: nunca mencionar IA/Claude em commit). "
                     "Remova Co-Authored-By/Generated with e tente de novo.")

        if sub not in MONOLITH_OPS and sub != "commit":
            continue

        repo = repo_2morrow(alvo)
        if repo is None:
            continue

        # a. monolith
        if repo == "monolith" and sub in MONOLITH_OPS and not env_ok:
            responde("monolith: so com pedido explicito do usuario (git %s). "
                     "Peca confirmacao ao usuario; se ele ja pediu esta operacao, "
                     "repita o comando prefixado com %s=1." % (sub, ESCAPE_VAR),
                     MONOLITH_DECISAO)

        # b. JIRA em repo da 2morrow
        if sub == "commit":
            msg = primeira_mensagem(seg, args)
            if msg is not None and not JIRA.match(msg):
                responde("mensagem precisa comecar com o codigo JIRA (SFT-#### ou "
                         "STC-####) em repo da 2morrow (%s). Sem o codigo, nao "
                         "commitar: pedir ao usuario. Nunca inventar." % repo)

    sys.exit(0)


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except Exception:
        sys.exit(0)   # fail-open em erro interno
