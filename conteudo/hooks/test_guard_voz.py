#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Testes do guard-voz.py: alimenta JSONs por stdin e confere a decisao."""
import json
import os
import subprocess
import sys
import tempfile
import time

HOOK = os.path.join(os.path.dirname(os.path.abspath(__file__)), "guard-voz.py")


def roda(cmd, cwd, entrada=None):
    p = entrada if entrada is not None else json.dumps(
        {"hook_event_name": "PreToolUse", "cwd": cwd, "tool_name": "Bash",
         "tool_input": {"command": cmd}})
    t = time.time()
    r = subprocess.run([sys.executable, HOOK], input=p, capture_output=True, text=True)
    ms = (time.time() - t) * 1000
    dec = None
    if r.stdout.strip():
        dec = json.loads(r.stdout)["hookSpecificOutput"]["permissionDecision"]
    return r.returncode, dec, ms


def main():
    base = tempfile.mkdtemp(prefix="guardvoz-")
    video = os.path.join(base, "video-exemplo")
    os.makedirs(video)

    casos = [
        ("motor padrao (edge)", "python ferramentas/voz/voz.py --lang pt", video, None),
        ("edge explicito", "python voz.py --lang pt --motor edge", video, None),
        ("elevenlabs sem checar", "python voz.py --lang pt --motor elevenlabs", video, "deny"),
        ("elevenlabs com =", "python voz.py --lang pt --motor=elevenlabs", video, "deny"),
        ("elevenlabs por caminho", 'python "%s" --motor elevenlabs' % os.path.join(video, "voz.py"), base, "deny"),
        ("elevenlabs cd &&", "cd '%s' && python voz.py --motor elevenlabs" % video, base, "deny"),
        ("elevenlabs em bash -c", 'bash -c "python voz.py --motor elevenlabs"', video, "deny"),
        ("elevenlabs com checar", "python voz.py --motor elevenlabs --checar", video, None),
        ("elevenlabs exportar-texto", "python voz.py --motor elevenlabs --exportar-texto", video, None),
        ("elevenlabs escape", "GUARD_VOZ_OK=1 python voz.py --motor elevenlabs", video, None),
        ("curl TTS direto", 'curl -X POST https://api.elevenlabs.io/v1/text-to-speech/abc -d "{}"', video, "deny"),
        ("python -c TTS", "python -c \"import requests; requests.post('https://api.elevenlabs.io/v1/text-to-speech/abc')\"", video, "deny"),
        ("curl TTS escape", "GUARD_VOZ_OK=1 curl https://api.elevenlabs.io/v1/text-to-speech/abc", video, None),
        ("curl outra rota livre", "curl https://api.elevenlabs.io/v1/user/subscription", video, None),
        ("grep voz.py", "grep -n checar voz.py", video, None),
        ("outro script", "python narrar.py --motor elevenlabs", video, None),
        ("comando vazio", "", video, None),
    ]

    falhas = 0
    lentos = []
    for desc, cmd, cwd, esp in casos:
        rc, dec, ms = roda(cmd, cwd)
        ok = rc == 0 and dec == esp
        falhas += 0 if ok else 1
        if ms > 600:
            lentos.append((desc, int(ms)))
        print("%s %-30s -> %s (esperado %s) %.0f ms" % ("OK  " if ok else "FAIL", desc, dec, esp, ms))

    rc, dec, _ = roda("", base, entrada="nao e json")
    ok = rc == 0 and dec is None
    falhas += 0 if ok else 1
    print("%s %-30s" % ("OK  " if ok else "FAIL", "stdin invalido (fail-open)"))

    print("\n%d falha(s); casos >600 ms: %s" % (falhas, lentos or "nenhum"))
    sys.exit(1 if falhas else 0)


if __name__ == "__main__":
    main()
