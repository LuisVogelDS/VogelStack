#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Testes do guard-git.py: alimenta JSONs por stdin e confere a decisao."""
import json
import os
import subprocess
import sys
import tempfile
import time

HOOK = os.path.join(os.path.dirname(os.path.abspath(__file__)), "guard-git.py")


def repo(base, nome, remote):
    d = os.path.join(base, nome)
    os.makedirs(d)
    subprocess.run(["git", "init", "-q", d], check=True)
    if remote:
        subprocess.run(["git", "-C", d, "remote", "add", "origin", remote], check=True)
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
    base = tempfile.mkdtemp(prefix="guardgit-")
    mono = repo(base, "monolith", "git@bitbucket.org:2morrowSports/monolith.git")
    views = repo(base, "views-bi", "https://user@bitbucket.org/2morrowSports/views-bi.git")
    pess = repo(base, "pessoal", "https://github.com/LuisVogelDS/x.git")
    sem = repo(base, "semremote", None)

    heredoc = ("git commit -m \"$(cat <<'EOF'\n%s\n\nCorpo it's aqui\nEOF\n)\"")
    casos = [
        # (descricao, cmd, cwd, esperado)
        ("force --force", "git push --force origin main", pess, "deny"),
        ("force -f", "git push -f", pess, "deny"),
        ("force lease", "git push --force-with-lease origin x", pess, "deny"),
        ("force via -C", "git -C . push -f", pess, "deny"),
        ("force +refspec", "git push origin +main", pess, "deny"),
        ("force cluster -fu", "git push -fu origin x", pess, "deny"),
        ("force composto", "cd /tmp && git status && git push --force", pess, "deny"),
        ("push normal", "git push origin main", pess, None),
        ("push -u ok", "git push -u origin feature-fix", pess, None),
        ("monolith pull", "git pull", mono, "deny"),
        ("monolith checkout", "git checkout -b x", mono, "deny"),
        ("monolith via cd", "cd '%s' && git rebase main" % mono, pess, "deny"),
        ("monolith via -C", "git -C '%s' reset --hard" % mono, pess, "deny"),
        ("monolith status ok", "git status", mono, None),
        ("monolith log ok", "git log --oneline | head", mono, None),
        ("monolith escape", "GUARD_GIT_OK=1 git pull", mono, None),
        ("outro repo 2m pull ok", "git pull", views, None),
        ("jira ausente", 'git commit -m "corrige bug"', views, "deny"),
        ("jira ok", 'git commit -m "SFT-1234 corrige bug"', views, None),
        ("jira STC ok", 'git commit -am "STC-99999: x"', views, None),
        ("jira heredoc ruim", heredoc % "sem codigo", views, "deny"),
        ("jira heredoc ok", heredoc % "SFT-4321 algo", views, None),
        ("commit sem -m (amend)", "git commit --amend --no-edit", views, None),
        ("commit pessoal sem jira ok", 'git commit -m "qualquer"', pess, None),
        ("commit sem remote ok", 'git commit -m "qualquer"', sem, None),
        ("co-authored", 'git commit -m "x\n\nCo-Authored-By: Claude <noreply@anthropic.com>"', pess, "deny"),
        ("generated with", 'git commit -m "x" -m "Generated with Claude Code"', sem, "deny"),
        ("co-authored humano ok", 'git commit -m "x\n\nCo-Authored-By: Emanuel <e@x.com>"', pess, None),
        ("add pem", "git add chave.pem", pess, "deny"),
        ("add .env", "git add src/.env", pess, "deny"),
        ("add .env.local", "git add .env.local", pess, "deny"),
        ("add id_rsa.pub", "git add ~/.ssh/id_rsa.pub", pess, "deny"),
        ("add key", "git add a.txt server.key", pess, "deny"),
        ("add normal", "git add src/main.py README.md", pess, None),
        ("add -A ok", "git add -A", pess, None),
        ("add .env.example ok", "git add .env.example", pess, None),
        ("nao e git", "echo git push --force", pess, None),
        ("git em texto", 'echo "git push --force"', pess, None),
        ("comando vazio", "", pess, None),
    ]
    falhas = 0
    lentos = []
    for desc, cmd, cwd, esp in casos:
        rc, dec, ms = roda(cmd, cwd)
        ok = rc == 0 and dec == esp
        if not ok:
            falhas += 1
        if ms > 400:
            lentos.append((desc, ms))
        print("%s %-28s -> %s (esperado %s) %.0f ms" % ("OK  " if ok else "FAIL", desc, dec, esp, ms))

    # entrada invalida: fail-open
    r = subprocess.run([sys.executable, HOOK], input="nao e json", capture_output=True, text=True)
    ok = r.returncode == 0 and not r.stdout.strip()
    falhas += 0 if ok else 1
    print("%s %-28s" % ("OK  " if ok else "FAIL", "stdin invalido (fail-open)"))

    print("\n%d falha(s); casos >400 ms: %s" % (falhas, lentos or "nenhum"))
    sys.exit(1 if falhas else 0)


if __name__ == "__main__":
    main()
