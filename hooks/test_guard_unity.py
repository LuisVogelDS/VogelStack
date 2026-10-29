#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Testes do guard-unity.py: alimenta JSONs por stdin e confere a decisao."""
import json
import os
import subprocess
import sys
import tempfile
import time

HOOK = os.path.join(os.path.dirname(os.path.abspath(__file__)), "guard-unity.py")


def escreve(caminho, texto="x"):
    os.makedirs(os.path.dirname(caminho), exist_ok=True)
    with open(caminho, "w", encoding="utf-8") as fh:
        fh.write(texto)


def git(d, *a):
    subprocess.run(["git", "-C", d] + list(a), check=True, capture_output=True)


def repo_unity(base, nome, origens_em):
    """Repo com Assets/ e ProjectSettings/. origens_em: caminho relativo do ORIGENS.md."""
    d = os.path.join(base, nome)
    os.makedirs(d)
    subprocess.run(["git", "init", "-q", d], check=True)
    git(d, "config", "user.email", "t@t")
    git(d, "config", "user.name", "t")
    escreve(os.path.join(d, "ProjectSettings", "ProjectVersion.txt"))
    escreve(os.path.join(d, "Assets", "_Jogo", "a.cs"))
    escreve(os.path.join(d, origens_em), "# Origens\n")
    git(d, "add", "-A")
    git(d, "commit", "-qm", "base")
    return d


def roda(cmd, cwd):
    p = json.dumps({"hook_event_name": "PreToolUse", "cwd": cwd, "tool_name": "Bash",
                    "tool_input": {"command": cmd}})
    t = time.time()
    r = subprocess.run([sys.executable, HOOK], input=p, capture_output=True, text=True)
    ms = (time.time() - t) * 1000
    dec = None
    if r.stdout.strip():
        dec = json.loads(r.stdout)["hookSpecificOutput"]["permissionDecision"]
    return r.returncode, dec, ms


def main():
    base = tempfile.mkdtemp(prefix="guardunity-")
    slime = repo_unity(base, "slime", "Assets/AssetDump/ORIGENS.md")
    fang = repo_unity(base, "fang", "ORIGENS.md")
    comum = os.path.join(base, "comum")
    os.makedirs(comum)
    subprocess.run(["git", "init", "-q", comum], check=True)
    # fila ativa no slime: PID 4242 (Logs/ fica fora do git neste teste)
    escreve(os.path.join(slime, "Logs", "unity-batch.lock"), json.dumps({"pid": 4242, "quem": "t"}))
    escreve(os.path.join(slime, ".git", "info", "exclude"), "Logs/\n")

    def novo(d, rel):
        escreve(os.path.join(d, rel))
        git(d, "add", "--", rel)

    def limpa(d):
        git(d, "reset", "-q")
        git(d, "checkout", "-q", "--", ".")
        subprocess.run(["git", "-C", d, "clean", "-fdq", "--", "Assets"], check=True)

    casos = []

    def c(desc, cmd, cwd, esp, prep=None):
        casos.append((desc, cmd, cwd, esp, prep))

    # regra 1
    c("timeout unity_batch", "timeout 60 python unity_batch.py x", comum, "deny")
    c("timeout -s KILL", "timeout -s KILL 30 python Ferramentas/unity_batch.py compilar", comum, "deny")
    c("gtimeout", "gtimeout 10m python Ferramentas/unity_batch.py x", comum, "deny")
    c("timeout Unity.exe", 'timeout 120 "C:/Program Files/Unity/Hub/Editor/6000/Editor/Unity.exe" -batchmode', comum, "deny")
    c("timeout --kill-after", "timeout --kill-after=5 60 python unity_batch.py x", comum, "deny")
    c("timeout em bash -c", 'bash -c "timeout 60 python unity_batch.py x"', comum, "deny")
    c("timeout composto", "cd slime && timeout 60 python unity_batch.py x | tail", comum, "deny")
    c("timeout env prefix", "CLAUDE_SESSAO=a timeout 60 python unity_batch.py x", comum, "deny")
    c("unity_batch sem timeout", "python Ferramentas/unity_batch.py x", comum, None)
    c("unity_batch --status", "python Ferramentas/unity_batch.py --status", comum, None)
    c("timeout outro comando", "timeout 60 pytest -q", comum, None)
    c("timeout windows (sleep)", "timeout /t 5 && python unity_batch.py x", comum, None)
    c("timeout seguido de pipe", "timeout 5 cat x | python unity_batch.py", comum, None)
    # regra 2
    c("taskkill Unity.exe", "taskkill /F /IM Unity.exe", comum, "deny")
    c("taskkill unity minusculo", "taskkill /f /im unity.exe /t", comum, "deny")
    c("Stop-Process via powershell", 'powershell -Command "Stop-Process -Name Unity -Force"', comum, "deny")
    c("Stop-Process direto", "Stop-Process -Name Unity", comum, "deny")
    c("pkill unity_batch", "pkill -f unity_batch", comum, "deny")
    c("kill PID da fila", "kill -9 4242", slime, "deny")
    c("taskkill PID da fila", "taskkill /PID 4242 /F", slime, "deny")
    c("taskkill python com fila", "taskkill /F /IM python.exe", slime, "deny")
    c("kill PID via cd", "cd '%s' && kill 4242" % slime, comum, "deny")
    c("kill PID outro", "kill -9 999", slime, None)
    c("kill PID substring", "kill 42420", slime, None)
    c("taskkill python sem fila", "taskkill /F /IM python.exe", comum, None)
    c("taskkill chrome", "taskkill /F /IM chrome.exe", comum, None)
    c("kill escape", "GUARD_UNITY_OK=1 taskkill /F /IM Unity.exe", comum, None)
    c("echo kill", 'echo "taskkill Unity.exe"', comum, None)
    c("skill nao e kill", "python skill_tool.py unity", comum, None)
    # regra 3
    c("asset novo sem origens", "git commit -m 'x'", slime, "deny",
      lambda: novo(slime, "Assets/AssetDump/Pack/modelo.fbx"))
    c("asset novo com origens", "git commit -m 'x'", slime, None,
      lambda: (novo(slime, "Assets/AssetDump/Pack/modelo.fbx"),
               escreve(os.path.join(slime, "Assets/AssetDump/ORIGENS.md"), "# Origens\nPack\n"),
               git(slime, "add", "Assets/AssetDump/ORIGENS.md")))
    c("add && commit sem origens", "git add Assets && git commit -m 'x'", slime, "deny",
      lambda: escreve(os.path.join(slime, "Assets/AssetDump/Pack/m.fbx")))
    c("add && commit com origens", "git add Assets && git commit -m 'x'", slime, None,
      lambda: (escreve(os.path.join(slime, "Assets/AssetDump/Pack/m.fbx")),
               escreve(os.path.join(slime, "Assets/AssetDump/ORIGENS.md"), "# Origens\nPack\n")))
    c("commit via -C", "git -C '%s' commit -m x" % slime, comum, "deny",
      lambda: novo(slime, "Assets/AssetDump/P/m.fbx"))
    c("commit via cd", "cd '%s' && git commit -m x" % slime, comum, "deny",
      lambda: novo(slime, "Assets/AssetDump/P/m.fbx"))
    c("origens da raiz (fang)", "git commit -m 'x'", fang, None,
      lambda: (novo(fang, "Assets/AssetDump/Kenney/m.fbx"),
               escreve(os.path.join(fang, "ORIGENS.md"), "# Origens\nKenney\n"),
               git(fang, "add", "ORIGENS.md")))
    c("fang sem origens", "git commit -m 'x'", fang, "deny",
      lambda: novo(fang, "Assets/AssetDump/Kenney/m.fbx"))
    c("asset fora do AssetDump", "git commit -m 'x'", slime, None,
      lambda: novo(slime, "Assets/_Jogo/b.cs"))
    c("editar arquivo existente", "git commit -m 'x'", slime, None,
      lambda: (escreve(os.path.join(slime, "Assets/_Jogo/a.cs"), "y"), git(slime, "add", "-u")))
    c("commit escape", "GUARD_UNITY_OK=1 git commit -m 'x'", slime, None,
      lambda: novo(slime, "Assets/AssetDump/Pack/modelo.fbx"))
    c("repo nao Unity", "git commit -m 'x'", comum, None,
      lambda: (escreve(os.path.join(comum, "Assets", "AssetDump", "m.fbx")), git(comum, "add", "-A")))
    c("git status", "git status", slime, None)
    c("comando vazio", "", slime, None)

    falhas = 0
    lentos = []
    for desc, cmd, cwd, esp, prep in casos:
        for d in (slime, fang):
            limpa(d)
        if prep:
            prep()
        rc, dec, ms = roda(cmd, cwd)
        ok = rc == 0 and dec == esp
        if not ok:
            falhas += 1
        if ms > 600:
            lentos.append((desc, int(ms)))
        print("%s %-30s -> %s (esperado %s) %.0f ms" % ("OK  " if ok else "FAIL", desc, dec, esp, ms))

    r = subprocess.run([sys.executable, HOOK], input="nao e json", capture_output=True, text=True)
    ok = r.returncode == 0 and not r.stdout.strip()
    falhas += 0 if ok else 1
    print("%s %-30s" % ("OK  " if ok else "FAIL", "stdin invalido (fail-open)"))

    print("\n%d falha(s); casos >600 ms: %s" % (falhas, lentos or "nenhum"))
    sys.exit(1 if falhas else 0)


if __name__ == "__main__":
    main()
