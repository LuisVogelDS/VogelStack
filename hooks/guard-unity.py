#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Guardrail de gamedev/Unity (PreToolUse em Bash). Materializa regras dos
CLAUDE.md dos jogos (slime, fang-you-very-much, GobbleGoblin).

Regras:
  1. `timeout`/`gtimeout` envolvendo unity_batch.py ou Unity.exe -> deny, sem
     escape. A fila do Unity espera a vez; matar o wrapper deixa o Unity orfao
     segurando Temp/UnityLockfile ate reiniciar a maquina (aconteceu em 06/10,
     slime/CLAUDE.md). Para limitar tempo: run_in_background.
  2. taskkill / Stop-Process / kill / pkill / killall mirando Unity, o PID da
     fila (Logs/unity-batch.lock) ou o python da fila -> deny. Escape quando o
     usuario pediu de fato: prefixar o comando com GUARD_UNITY_OK=1.
  3. `git commit` em repo Unity (Assets/ + ProjectSettings/) cujo indice adiciona
     arquivos sob Assets/**/AssetDump/** sem tocar um ORIGENS.md de uma pasta
     ancestral (Assets/AssetDump/ORIGENS.md no slime e no GobbleGoblin, ORIGENS.md
     na raiz no fang-you-very-much) -> deny. Mesmo escape GUARD_UNITY_OK=1.
     Enxerga tambem `git add ... && git commit` no mesmo comando (git add -n).

Fail-open em erro interno (exit 0). O git so e consultado em `git commit`.
"""
import json
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _comum as c  # noqa: E402

ESCAPE_VAR = "GUARD_UNITY_OK"
KILLERS = {"taskkill", "stop-process", "kill", "pkill", "killall", "spps"}


def eh_timeout(tokens):
    return c.nome(tokens[0]) in ("timeout", "gtimeout")


def regra1(tokens):
    if not eh_timeout(tokens):
        return
    resto = " ".join(tokens[1:]).lower().replace("\\", "/")
    if "unity_batch" in resto or "unity.exe" in resto or resto.endswith("/unity"):
        c.responde(
            "Nunca envolver a fila do Unity em `timeout` (slime/CLAUDE.md): se o timeout "
            "matar o wrapper python, o Unity fica orfao segurando Temp/UnityLockfile e so "
            "sai com reinicio da maquina (aconteceu em 06/10). A fila espera a vez por "
            "conta propria. Rode `python Ferramentas/unity_batch.py ...` direto; se "
            "precisar nao travar a conversa, use run_in_background e acompanhe o log. "
            "Para limitar tempo, use o parametro timeout da ferramenta Bash, nunca o "
            "comando `timeout`.")


def raiz_unity(base):
    """Sobe de base ate achar pasta com Assets/ e ProjectSettings/."""
    d = base
    for _ in range(12):
        if os.path.isdir(os.path.join(d, "Assets")) and os.path.isdir(os.path.join(d, "ProjectSettings")):
            return d
        pai = os.path.dirname(d)
        if pai == d:
            break
        d = pai
    return None


def pid_da_fila(base):
    raiz = raiz_unity(base)
    if not raiz:
        return None, False
    lock = os.path.join(raiz, "Logs", "unity-batch.lock")
    try:
        with open(lock, encoding="utf-8") as fh:
            return str(json.load(fh).get("pid")), True
    except Exception:
        return None, os.path.exists(lock)


def regra2(tokens, envs, base):
    if c.nome(tokens[0]) not in KILLERS:
        return
    if envs.get(ESCAPE_VAR) == "1":
        return
    texto = " ".join(tokens[1:]).lower()
    pid, tem_lock = pid_da_fila(base)
    mira = None
    if "unity" in texto:
        mira = "Unity"
    elif pid and re.search(r"(?<!\d)%s(?!\d)" % re.escape(pid), texto):
        mira = "o PID %s da fila (Logs/unity-batch.lock)" % pid
    elif tem_lock and re.search(r"\bpython(w|3)?(\.exe)?\b", texto):
        mira = "o python da fila (ha Logs/unity-batch.lock)"
    if mira:
        c.responde(
            "Nao matar %s: a regra do repo (slime/CLAUDE.md) e nunca matar o wrapper da "
            "fila nem o Unity, porque deixa o Unity orfao segurando Temp/UnityLockfile "
            "ate reiniciar a maquina. Espere a fila (unity_batch.py --status mostra quem "
            "esta na vez) ou rode em segundo plano. Se o usuario pediu de fato para "
            "matar, repita o comando prefixado com %s=1." % (mira, ESCAPE_VAR))


# ---------------------------------------------------------------- regra 3
def git(args, cwd, timeout=8):
    return subprocess.run(["git", "-C", cwd] + args, capture_output=True, timeout=timeout)


def raiz_git(d):
    if not os.path.isdir(d):
        return None
    r = git(["rev-parse", "--show-toplevel"], d)
    if r.returncode != 0:
        return None
    return os.path.normpath(r.stdout.decode("utf-8", "replace").strip())


def lista_z(bruto):
    return [p for p in bruto.decode("utf-8", "replace").split("\0") if p]


def sob_assetdump(p):
    partes = p.split("/")
    return len(partes) > 2 and partes[0].lower() == "assets" and any(
        x.lower() == "assetdump" for x in partes[1:-1])


def e_origens(p):
    b = p.rsplit("/", 1)[-1].lower()
    return b in ("origens.md", "origens.md.meta")


def cobertos_por_origens(novo, tocados):
    d = novo.rsplit("/", 1)[0] if "/" in novo else ""
    while True:
        alvo = (d + "/ORIGENS.md").lower() if d else "origens.md"
        if alvo in tocados:
            return True
        if not d:
            return False
        d = d.rsplit("/", 1)[0] if "/" in d else ""


def adds_pendentes(alvo, raiz, add_args):
    """Arquivos que um `git add <args>` anterior no mesmo comando poria no indice."""
    r = git(["add", "-n"] + add_args, alvo)
    novos, todos = [], []
    if r.returncode != 0:
        return novos, todos
    for linha in r.stdout.decode("utf-8", "replace").splitlines():
        m = re.match(r"^add '(.*)'$", linha.strip())
        if not m:
            continue
        rel = os.path.relpath(os.path.join(alvo, m.group(1)), raiz).replace("\\", "/")
        todos.append(rel)
        if not git(["ls-files", "--error-unmatch", "--", rel], raiz).returncode == 0:
            novos.append(rel)
    return novos, todos


def regra3(raiz, adicionados, tocados):
    sem = []
    for p in sorted(set(adicionados)):
        if sob_assetdump(p) and not e_origens(p) and not cobertos_por_origens(p, tocados):
            sem.append(p)
    if not sem:
        return
    pastas = sorted({"/".join(p.split("/")[:4]) for p in sem})
    c.responde(
        "Asset novo sem ORIGENS.md: este commit adiciona %d arquivo(s) sob AssetDump "
        "(%s%s) e nao altera nenhum ORIGENS.md (Assets/AssetDump/ORIGENS.md, ou "
        "ORIGENS.md da raiz no fang-you-very-much). Todo asset de terceiros entra com "
        "origem, licenca e como regerar. Registre no ORIGENS.md, `git add` nele e "
        "commite de novo. Se o usuario pediu para commitar sem registrar, repita "
        "prefixado com %s=1."
        % (len(sem), ", ".join(pastas[:3]), "..." if len(pastas) > 3 else "", ESCAPE_VAR))


def main():
    payload = c.le_payload()
    cmd = (payload.get("tool_input") or {}).get("command") or ""
    if not cmd:
        sys.exit(0)
    low = cmd.lower()
    cwd = c.msys_para_win(payload.get("cwd") or os.getcwd())

    # regras 1 e 2: qualquer subcomando, inclusive dentro de bash -c "..."
    if any(k in low for k in ("timeout", "kill", "stop-process", "spps")):
        base = cwd
        for toks, envs, _seg in c.segmentos(cmd):
            if toks[0] == "cd" and len(toks) >= 2:
                base = c.resolve_dir(base, toks[1])
                continue
            regra1(toks)
            regra2(toks, envs, base)

    # regra 3: git commit
    if "commit" in low and "git" in low:
        atual = cwd
        pend_novos, pend_todos = [], []
        for seg in c.divide_comando(cmd):
            toks = c.tokeniza(seg)
            toks, envs = c.tira_prefixos(toks)
            if not toks:
                continue
            if toks[0] in ("cd", "pushd") and len(toks) >= 2:
                atual = c.resolve_dir(atual, toks[1])
                continue
            if c.nome(toks[0]) != "git":
                continue
            i, dir_c = 1, None
            while i < len(toks) and toks[i].startswith("-"):
                if toks[i] == "-C" and i + 1 < len(toks):
                    dir_c = toks[i + 1]
                    i += 2
                elif toks[i] in ("-c", "--git-dir", "--work-tree", "--namespace", "--exec-path"):
                    i += 2
                else:
                    i += 1
            if i >= len(toks):
                continue
            sub, args = toks[i], toks[i + 1:]
            alvo = c.resolve_dir(atual, dir_c) if dir_c else atual
            raiz = raiz_git(alvo)
            if not raiz or not raiz_unity(raiz) or raiz_unity(raiz) != raiz:
                continue
            if sub == "add":
                n, t = adds_pendentes(alvo, raiz, args)
                pend_novos += n
                pend_todos += t
            elif sub == "commit":
                if envs.get(ESCAPE_VAR) == "1":
                    continue
                novos = lista_z(git(["diff", "--cached", "--name-only", "--diff-filter=A", "-z"], raiz).stdout)
                todos = lista_z(git(["diff", "--cached", "--name-only", "-z"], raiz).stdout)
                tocados = {p.replace("\\", "/").lower() for p in todos + pend_todos}
                regra3(raiz, [p.replace("\\", "/") for p in novos] + pend_novos, tocados)
    sys.exit(0)


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except Exception:
        sys.exit(0)  # fail-open em erro interno
