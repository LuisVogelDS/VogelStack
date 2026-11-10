# -*- coding: utf-8 -*-
"""
Helpers compartilhados por guard-unity.py e guard-conteudo.py (PreToolUse).

O guard-git.py tem copia propria destas funcoes e nao depende deste modulo.
O Python poe a pasta do script em sys.path, entao `import _comum` funciona tanto
no repo quanto na copia em cache do plugin (a pasta hooks/ vai inteira).
"""
import json
import os
import re
import shlex
import sys

SHELLS = {"bash", "sh", "zsh", "dash", "pwsh", "powershell", "cmd"}
SHELL_FLAGS_C = {"-c", "-lc", "-ic", "-command", "-c:", "/c", "/k", "-encodedcommand"}
WRAPPERS = {"command", "builtin", "nohup", "time", "exec", "sudo", "env", "call", "start"}


def responde(motivo, decisao="deny"):
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": decisao,
            "permissionDecisionReason": motivo,
        }
    }, ensure_ascii=False))
    sys.exit(0)


def le_payload():
    try:
        return json.load(sys.stdin)
    except Exception:
        sys.exit(0)


def divide_comando(cmd):
    """Divide em subcomandos por && || ; | & e quebra de linha FORA de aspas."""
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


def nome(token):
    """Basename minusculo, sem .exe, tolerando barra invertida."""
    b = os.path.basename(token.replace("\\", "/")).lower()
    return b[:-4] if b.endswith(".exe") else b


def tira_prefixos(tokens):
    """Pula VAR=valor e wrappers simples. Devolve (tokens_restantes, envs)."""
    envs = {}
    i = 0
    while i < len(tokens):
        t = tokens[i]
        m = re.match(r"^([A-Za-z_][A-Za-z0-9_]*)=(.*)$", t)
        if m:
            envs[m.group(1)] = m.group(2)
            i += 1
        elif nome(t) in WRAPPERS:
            i += 1
        else:
            break
    return tokens[i:], envs


def segmentos(cmd, prof=0):
    """Gera (tokens, envs, seg_texto) de cada subcomando, entrando em `bash -c "..."`."""
    for seg in divide_comando(cmd):
        tokens = tokeniza(seg)
        rest, envs = tira_prefixos(tokens)
        if not rest:
            continue
        yield rest, envs, seg
        if prof < 3 and nome(rest[0]) in SHELLS:
            for j, t in enumerate(rest[1:], 1):
                if t.lower() in SHELL_FLAGS_C and j + 1 < len(rest):
                    for sub in segmentos(rest[j + 1], prof + 1):
                        sub[1].update({k: v for k, v in envs.items() if k not in sub[1]})
                        yield sub
                    break
