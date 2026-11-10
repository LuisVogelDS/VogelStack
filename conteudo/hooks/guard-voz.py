#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Guardrail de narracao paga (PreToolUse em Bash).

Regra:
  Narracao paga: `voz.py` desta stack (ferramentas/voz/voz.py) com `--motor
  elevenlabs` sem `--checar` (nem `--exportar-texto`, que nao chama a API), ou
  chamada direta a api.elevenlabs.io/v1/text-to-speech (curl, wget, python -c)
  -> deny. O motor padrao do voz.py e o edge (gratuito) e passa livre.
  Escape quando o usuario ja aprovou o custo: prefixar o comando com GUARD_VOZ_OK=1.

Fail-open em erro interno (exit 0).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _comum as c  # noqa: E402

ESC_VOZ = "GUARD_VOZ_OK"
INTERPRETES = {"python", "python3", "pythonw", "py", "uv", "node", "bash", "sh"}
FLAGS_SEM_CUSTO = {"--checar", "--exportar-texto"}
URL_TTS = "api.elevenlabs.io/v1/text-to-speech"


def script_do_segmento(tokens):
    """Caminho do script que o segmento roda (python x.py, ./x.py) ou None."""
    if not tokens:
        return None
    if c.nome(tokens[0]) in INTERPRETES:
        for t in tokens[1:]:
            if t.startswith("-") or t == "run":
                continue
            return t
        return None
    return tokens[0]


def motor_pedido(args):
    """Valor de --motor na linha de comando (None se nao veio)."""
    for i, a in enumerate(args):
        if a.startswith("--motor="):
            return a.split("=", 1)[1]
        if a == "--motor" and i + 1 < len(args):
            return args[i + 1]
    return None


def regra(tokens, envs, seg):
    if envs.get(ESC_VOZ) == "1":
        return
    pago = URL_TTS in seg.lower()
    script = script_do_segmento(tokens)
    if script and os.path.basename(script.replace("\\", "/")).lower() == "voz.py":
        args = [a.lower() for a in tokens[1:]]
        if motor_pedido(args) == "elevenlabs" and not any(a in FLAGS_SEM_CUSTO for a in args):
            pago = True
    if pago:
        c.responde(
            "Narracao paga (ElevenLabs gasta credito): rode antes com --checar e "
            "mostre ao usuario o custo estimado; so gere depois da aprovacao. Para voz "
            "gratuita use o motor padrao (edge) do voz.py. Se o usuario ja aprovou o "
            "custo, repita o comando prefixado com %s=1." % ESC_VOZ)


def main():
    payload = c.le_payload()
    cmd = (payload.get("tool_input") or {}).get("command") or ""
    if not cmd:
        sys.exit(0)
    cwd = c.msys_para_win(payload.get("cwd") or os.getcwd())
    base = cwd
    for toks, envs, seg in c.segmentos(cmd):
        if toks[0] == "cd" and len(toks) >= 2:
            base = c.resolve_dir(base, toks[1])
            continue
        regra(toks, envs, seg)
    sys.exit(0)


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except Exception:
        sys.exit(0)  # fail-open em erro interno
