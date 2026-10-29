#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Testes do guard-processo.py: um python dormindo faz o papel do motor."""
import json
import os
import subprocess
import sys
import tempfile

HOOK = os.path.join(os.path.dirname(os.path.abspath(__file__)), "guard-processo.py")


def roda(cmd, arquivo, ferramenta="Bash"):
    p = json.dumps({"hook_event_name": "PreToolUse", "cwd": os.getcwd(), "tool_name": ferramenta,
                    "tool_input": {"command": cmd}})
    env = dict(os.environ, GUARD_HARPYNEST_PROTEGIDOS=arquivo)
    r = subprocess.run([sys.executable, HOOK], input=p.encode("utf-8"), capture_output=True, env=env, timeout=20)
    out = r.stdout.decode("utf-8", "replace").strip()
    return json.loads(out)["hookSpecificOutput"]["permissionDecision"] if out else "allow"


def main():
    motor = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(120)"])
    falhas = 0
    try:
        d = tempfile.mkdtemp()
        arq = os.path.join(d, "protegidos.json")
        with open(arq, "w", encoding="utf-8") as fh:
            json.dump({"motor": motor.pid, "app": 4999999}, fh)
        vazio = os.path.join(d, "nao-existe.json")
        m = motor.pid
        casos = [
            # (comando, arquivo, ferramenta, esperado)
            ("taskkill //PID 38228 //F; taskkill //PID %d //F" % m, arq, "Bash", "deny"),
            ("taskkill /PID %d /T /F" % m, arq, "Bash", "deny"),
            ("Stop-Process -Id %d -Force" % m, arq, "PowerShell", "deny"),
            ("powershell -Command \"Stop-Process -Id %d -Force\"" % m, arq, "Bash", "deny"),
            ("kill -9 %d" % m, arq, "Bash", "deny"),
            ("taskkill /IM python.exe /F", arq, "Bash", "deny"),
            ("Stop-Process -Name python -Force", arq, "PowerShell", "deny"),
            ("Get-Process python | Stop-Process -Force", arq, "PowerShell", "deny"),
            ("taskkill /IM harpynest.exe /F", vazio, "Bash", "deny"),
            ("GUARD_HARPYNEST_OK=1 taskkill /PID %d /F" % m, arq, "Bash", "allow"),
            ("taskkill //PID 38228 //F", arq, "Bash", "allow"),
            ("taskkill /IM bcp.exe /F", arq, "Bash", "allow"),
            ("taskkill /IM python.exe /F", vazio, "Bash", "allow"),     # motor fora: python por nome passa
            ("taskkill /PID 4999999 /F", arq, "Bash", "allow"),          # PID do app que nao existe mais
            ("taskkill /PID %d /F" % m, vazio, "Bash", "allow"),         # sem arquivo, nada protegido
            ("git status", arq, "Bash", "allow"),
        ]
        for cmd, a, ferr, esperado in casos:
            obtido = roda(cmd, a, ferr)
            ok = obtido == esperado
            falhas += not ok
            print("%s  %-6s %s" % ("ok " if ok else "FALHOU", esperado, cmd))
    finally:
        motor.kill()
    print("falhas:", falhas)
    sys.exit(1 if falhas else 0)


if __name__ == "__main__":
    main()
