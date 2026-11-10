#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Testes do guard-git.py: alimenta JSONs por stdin e confere a decisao.

Cobre as regras fixas, o prefixo e o repo protegido vindos de configuracao (do repo,
do usuario com HOME/USERPROFILE temporario, e de VOGEL_GUARD_GIT) e a ausencia de
configuracao.
"""
import json
import os
import subprocess
import sys
import tempfile
import time

HOOK = os.path.join(os.path.dirname(os.path.abspath(__file__)), "guard-git.py")

CONFIG = {
    "repos_protegidos": [
        {"remote": "bitbucket.org/acme/monolito",
         "operacoes": ["pull", "commit", "push", "checkout", "switch", "merge", "rebase", "reset"]},
    ],
    "prefixo_commit": [
        {"remote": "bitbucket.org/acme/*", "regex": "^(PROJ|OPS)-\\d{3,}",
         "mensagem": "a mensagem precisa comecar com PROJ-### ou OPS-###"},
    ],
}


def repo(base, nome, remote):
    d = os.path.join(base, nome)
    os.makedirs(d)
    subprocess.run(["git", "init", "-q", d], check=True)
    if remote:
        subprocess.run(["git", "-C", d, "remote", "add", "origin", remote], check=True)
    return d


def grava(caminho, dados):
    os.makedirs(os.path.dirname(caminho), exist_ok=True)
    with open(caminho, "w", encoding="utf-8") as fh:
        json.dump(dados, fh)


def ambiente(home, extra=None):
    env = dict(os.environ)
    env["HOME"] = home
    env["USERPROFILE"] = home
    env.pop("VOGEL_GUARD_GIT", None)
    if extra:
        env.update(extra)
    return env


def roda(cmd, cwd, env):
    p = json.dumps({"hook_event_name": "PreToolUse", "cwd": cwd, "tool_name": "Bash",
                    "tool_input": {"command": cmd}})
    t = time.time()
    r = subprocess.run([sys.executable, HOOK], input=p, capture_output=True, text=True, env=env)
    ms = (time.time() - t) * 1000
    dec = None
    if r.stdout.strip():
        dec = json.loads(r.stdout)["hookSpecificOutput"]["permissionDecision"]
    return r.returncode, dec, ms


def main():
    base = tempfile.mkdtemp(prefix="guardgit-")
    casa_vazia = os.path.join(base, "home-vazia")          # sem ~/.claude/guard-git.json
    casa_cfg = os.path.join(base, "home-cfg")              # com a configuracao do usuario
    os.makedirs(casa_vazia)
    grava(os.path.join(casa_cfg, ".claude", "guard-git.json"), CONFIG)

    mono = repo(base, "monolito", "git@bitbucket.org:acme/monolito.git")
    outro = repo(base, "servicos", "https://user@bitbucket.org/acme/servicos.git")
    pess = repo(base, "pessoal", "https://github.com/exemplo/x.git")
    sem = repo(base, "semremote", None)
    # config no proprio repo: so o prefixo, para um remote que ninguem mais cobre
    local = repo(base, "local", "https://git.exemplo.net/time/app.git")
    grava(os.path.join(local, ".claude", "guard-git.json"),
          {"prefixo_commit": [{"remote": "git.exemplo.net/time/*", "regex": "^\\[app\\] "}]})
    # arquivo extra por variavel
    extra_arq = os.path.join(base, "extra.json")
    grava(extra_arq, {"repos_protegidos": [{"remote": "github.com/exemplo/x", "operacoes": ["push"]}]})

    vazio = ambiente(casa_vazia)
    cfg = ambiente(casa_cfg)
    com_extra = ambiente(casa_vazia, {"VOGEL_GUARD_GIT": extra_arq})

    heredoc = ("git commit -m \"$(cat <<'EOF'\n%s\n\nCorpo it's aqui\nEOF\n)\"")
    casos = [
        # (descricao, cmd, cwd, ambiente, esperado)
        # --- regras fixas (valem sem configuracao nenhuma)
        ("force --force", "git push --force origin main", pess, vazio, "deny"),
        ("force -f", "git push -f", pess, vazio, "deny"),
        ("force lease", "git push --force-with-lease origin x", pess, vazio, "deny"),
        ("force via -C", "git -C . push -f", pess, vazio, "deny"),
        ("force +refspec", "git push origin +main", pess, vazio, "deny"),
        ("force cluster -fu", "git push -fu origin x", pess, vazio, "deny"),
        ("force composto", "cd /tmp && git status && git push --force", pess, vazio, "deny"),
        ("force ignora escape", "GUARD_GIT_OK=1 git push -f", pess, vazio, "deny"),
        ("push normal", "git push origin main", pess, vazio, None),
        ("push -u ok", "git push -u origin feature-fix", pess, vazio, None),
        ("co-authored", 'git commit -m "x\n\nCo-Authored-By: Claude <noreply@anthropic.com>"', pess, vazio, "deny"),
        ("generated with", 'git commit -m "x" -m "Generated with Claude Code"', sem, vazio, "deny"),
        ("co-authored humano ok", 'git commit -m "x\n\nCo-Authored-By: Ana <ana@example.com>"', pess, vazio, None),
        ("add pem", "git add chave.pem", pess, vazio, "deny"),
        ("add .env", "git add src/.env", pess, vazio, "deny"),
        ("add .env.local", "git add .env.local", pess, vazio, "deny"),
        ("add id_rsa.pub", "git add ~/.ssh/id_rsa.pub", pess, vazio, "deny"),
        ("add key", "git add a.txt server.key", pess, vazio, "deny"),
        ("add normal", "git add src/main.py README.md", pess, vazio, None),
        ("add -A ok", "git add -A", pess, vazio, None),
        ("add .env.example ok", "git add .env.example", pess, vazio, None),
        ("nao e git", "echo git push --force", pess, vazio, None),
        ("git em texto", 'echo "git push --force"', pess, vazio, None),
        ("comando vazio", "", pess, vazio, None),
        # --- sem configuracao: as regras de repo nao existem
        ("sem config: pull no monolito", "git pull", mono, vazio, None),
        ("sem config: commit sem prefixo", 'git commit -m "corrige bug"', outro, vazio, None),
        # --- configuracao do usuario (HOME temporario): repo protegido
        ("protegido pull", "git pull", mono, cfg, "deny"),
        ("protegido checkout", "git checkout -b x", mono, cfg, "deny"),
        ("protegido via cd", "cd '%s' && git rebase main" % mono, pess, cfg, "deny"),
        ("protegido via -C", "git -C '%s' reset --hard" % mono, pess, cfg, "deny"),
        ("protegido status ok", "git status", mono, cfg, None),
        ("protegido log ok", "git log --oneline | head", mono, cfg, None),
        ("protegido escape", "GUARD_GIT_OK=1 git pull", mono, cfg, None),
        ("outro repo do dono pull ok", "git pull", outro, cfg, None),
        ("repo pessoal pull ok", "git pull", pess, cfg, None),
        # --- prefixo de commit via configuracao do usuario
        ("prefixo ausente", 'git commit -m "corrige bug"', outro, cfg, "deny"),
        ("prefixo ok", 'git commit -m "PROJ-1234 corrige bug"', outro, cfg, None),
        ("prefixo OPS ok", 'git commit -am "OPS-99999: x"', outro, cfg, None),
        ("prefixo heredoc ruim", heredoc % "sem codigo", outro, cfg, "deny"),
        ("prefixo heredoc ok", heredoc % "PROJ-4321 algo", outro, cfg, None),
        ("commit sem -m (amend)", "git commit --amend --no-edit", outro, cfg, None),
        ("commit pessoal sem prefixo ok", 'git commit -m "qualquer"', pess, cfg, None),
        ("commit sem remote ok", 'git commit -m "qualquer"', sem, cfg, None),
        # --- configuracao dentro do repo e arquivo extra
        ("repo: prefixo ausente", 'git commit -m "qualquer"', local, vazio, "deny"),
        ("repo: prefixo ok", 'git commit -m "[app] qualquer"', local, vazio, None),
        ("extra: push protegido", "git push origin main", pess, com_extra, "deny"),
        ("extra: pull livre", "git pull", pess, com_extra, None),
        ("extra: escape", "GUARD_GIT_OK=1 git push origin main", pess, com_extra, None),
    ]
    falhas = 0
    lentos = []
    for desc, cmd, cwd, env, esp in casos:
        rc, dec, ms = roda(cmd, cwd, env)
        ok = rc == 0 and dec == esp
        if not ok:
            falhas += 1
        if ms > 600:
            lentos.append((desc, ms))
        print("%s %-32s -> %s (esperado %s) %.0f ms" % ("OK  " if ok else "FAIL", desc, dec, esp, ms))

    # entrada invalida e configuracao quebrada: fail-open
    r = subprocess.run([sys.executable, HOOK], input="nao e json", capture_output=True, text=True, env=vazio)
    ok = r.returncode == 0 and not r.stdout.strip()
    falhas += 0 if ok else 1
    print("%s %-32s" % ("OK  " if ok else "FAIL", "stdin invalido (fail-open)"))

    quebrada = os.path.join(base, "home-quebrada")
    os.makedirs(os.path.join(quebrada, ".claude"))
    with open(os.path.join(quebrada, ".claude", "guard-git.json"), "w") as fh:
        fh.write("{ isto nao e json")
    rc, dec, _ = roda('git commit -m "qualquer"', outro, ambiente(quebrada))
    ok = rc == 0 and dec is None
    falhas += 0 if ok else 1
    print("%s %-32s" % ("OK  " if ok else "FAIL", "config quebrada (fail-open)"))

    print("\n%d falha(s); casos >600 ms: %s" % (falhas, lentos or "nenhum"))
    sys.exit(1 if falhas else 0)


if __name__ == "__main__":
    main()
