#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Guardrail dos processos do HarpyNest (PreToolUse em Bash e PowerShell).

Em 29/10/2026 um agente do DeVirada rodou `taskkill //PID 23016 //F` achando que o
python.exe de 233 MB era a subida dele. Era o motor do HarpyNest: as sessoes de todos
os projetos cairam e as tarefas de fundo se perderam.

O motor anota em ~/.harpynest/protegidos.json o PID dele e o do app (harpynest.exe).

Regras:
  1. taskkill / Stop-Process / kill / pkill / killall / spps com um PID protegido
     -> deny (o PID so conta se o processo ainda existe e e um python ou o
     harpynest, para nao barrar um PID reaproveitado).
  2. Matar por nome o harpynest, ou python/pythonw enquanto o motor esta vivo
     (`taskkill /IM python.exe`, `Stop-Process -Name python`, `pkill python`)
     -> deny: derruba o motor junto.

Escape quando o usuario pediu de fato: prefixar o comando com GUARD_HARPYNEST_OK=1.
Fail-open em erro interno (exit 0).
"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _comum as c  # noqa: E402

ESCAPE_VAR = "GUARD_HARPYNEST_OK"
KILLERS = {"taskkill", "stop-process", "kill", "pkill", "killall", "spps", "tskill"}
ARQUIVO = os.environ.get("GUARD_HARPYNEST_PROTEGIDOS") or os.path.join(
    os.path.expanduser("~"), ".harpynest", "protegidos.json")
PYTHONS = {"python", "pythonw", "python3", "py"}


def imagem_do_pid(pid):
    """Nome do executavel do PID (minusculo, sem .exe), "" se nao existe, None se nao deu para saber."""
    if os.name != "nt":
        try:
            os.kill(pid, 0)
            return None
        except OSError:
            return ""
    try:
        import ctypes
        from ctypes import wintypes
        k32 = ctypes.windll.kernel32
        k32.OpenProcess.restype = wintypes.HANDLE
        h = k32.OpenProcess(0x1000, False, pid)   # PROCESS_QUERY_LIMITED_INFORMATION
        if not h:
            return ""
        try:
            buf = ctypes.create_unicode_buffer(1024)
            n = wintypes.DWORD(1024)
            if not k32.QueryFullProcessImageNameW(h, 0, buf, ctypes.byref(n)):
                return None
            vivo = wintypes.DWORD()
            if k32.GetExitCodeProcess(h, ctypes.byref(vivo)) and vivo.value != 259:   # STILL_ACTIVE
                return ""
            return c.nome(buf.value)
        finally:
            k32.CloseHandle(h)
    except Exception:
        return None


def protegidos():
    """{pid: rotulo} dos processos do HarpyNest que estao de pe."""
    try:
        with open(ARQUIVO, encoding="utf-8") as fh:
            d = json.load(fh)
    except Exception:
        return {}
    out = {}
    for chave, rotulo, nomes in (("motor", "o motor do HarpyNest", PYTHONS), ("app", "o app HarpyNest", {"harpynest"})):
        try:
            pid = int(d.get(chave))
        except (TypeError, ValueError):
            continue
        img = imagem_do_pid(pid)
        if img == "":
            continue
        if img is None or img in nomes:
            out[pid] = rotulo
    return out


def nomes_alvo(tokens):
    """Os nomes de imagem que o comando mata por nome (/IM, -Name, pkill/killall)."""
    k = c.nome(tokens[0])
    nomes = []
    resto = tokens[1:]
    if k in ("pkill", "killall"):
        nomes = [t for t in resto if not t.startswith("-")]
    else:
        for i, t in enumerate(resto):
            tl = t.lower()
            if tl in ("/im", "//im", "-im", "-name", "-processname") and i + 1 < len(resto):
                nomes += resto[i + 1].split(",")
            elif k in ("stop-process", "spps") and i == 0 and not t.startswith("-") and not t.isdigit():
                nomes.append(t)
    return [c.nome(n.strip("'\"")).replace("*", "") for n in nomes if n.strip()]


def pids_alvo(tokens):
    return {int(m) for t in tokens[1:] for m in re.findall(r"(?<![\w.])(\d{2,7})(?![\w.])", t)}


def decide(tokens, envs, prot):
    if c.nome(tokens[0]) not in KILLERS or envs.get(ESCAPE_VAR) == "1":
        return None
    for pid in sorted(pids_alvo(tokens) & set(prot)):
        return "%s (PID %d)" % (prot[pid], pid)
    for n in nomes_alvo(tokens):
        if n.startswith("harpynest"):
            return "o app HarpyNest (por nome)"
        if n in PYTHONS and any(r.startswith("o motor") for r in prot.values()):
            return "todo %s.exe, e o motor do HarpyNest e um deles" % n
    return None


def main():
    p = c.le_payload()
    cmd = (p.get("tool_input") or {}).get("command") or ""
    low = cmd.lower()
    if not any(k in low for k in ("kill", "stop-process", "spps")):
        sys.exit(0)
    prot = protegidos()
    motor_vivo = any(r.startswith("o motor") for r in prot.values())
    # `Get-Process python | Stop-Process`: o alvo vem pelo pipe, nao pelos argumentos
    if (motor_vivo and ESCAPE_VAR + "=1" not in cmd and "stop-process" in low
            and re.search(r"get-process\s+(-name\s+)?['\"]?pythonw?(\.exe)?(\s|\||$)", low)):
        c.responde(
            "Nao matar todo python.exe: o motor do HarpyNest e um deles e roda as sessoes de todos "
            "os projetos. Filtre pelo PID ou pela linha de comando do seu processo. Se o usuario "
            "pediu de fato, repita o comando prefixado com %s=1." % ESCAPE_VAR)
    for tokens, envs, _ in c.segmentos(cmd):
        mira = decide(tokens, envs, prot)
        if mira:
            c.responde(
                "Nao matar %s: ele roda as sessoes de todos os projetos, e derruba-lo corta os "
                "agentes no meio do turno (aconteceu em 29/10, um taskkill no PID errado). Confira "
                "o PID pela linha de comando antes de matar (Get-CimInstance Win32_Process -Filter "
                "\"ProcessId=<pid>\" | Select CommandLine) e mate so o seu processo. Se o usuario "
                "pediu de fato, repita o comando prefixado com %s=1." % (mira, ESCAPE_VAR))
    sys.exit(0)


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except Exception:
        sys.exit(0)
