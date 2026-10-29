#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Guardrail da divisao de conteudo da Cajuice (PreToolUse em Write/Edit/MultiEdit
e em Bash). Regras do Cajuice/conteudo/CLAUDE.md.

Regras:
  4. Texto publico sem travessao: Write/Edit em roteiro/publicacao/titulo/
     descricao/legenda (.md, .txt, .srt, .vtt) sob canais/** (ou prontos/**) cujo
     conteudo novo traz U+2014 ou U+2013 -> deny. Em Edit/MultiEdit so conta
     travessao a MAIS no texto novo do que no antigo (corrigir uma linha que ja
     tinha travessao nao e barrado). Docs internos, codigo e esteira/ ficam fora.
  5. Publicacao: "nenhum agente publica". Bash que roda subir.py / drive.py (sem
     --simular) ou CLI de upload (youtube-upload, tiktok-upload...) -> PUBLICAR_DECISAO.
     Escape: GUARD_PUBLICAR_OK=1 (usuario pediu de fato).
  6. Narracao paga: voz.py do presto (ElevenLabs por padrao) sem --checar, voz.py da
     esteira com `--motor elevenlabs`, ou ferramentas/voz/voz.py sem modo gratuito,
     e chamada direta a api.elevenlabs.io/v1/text-to-speech -> deny. Escape:
     GUARD_VOZ_OK=1. texto_elevenlabs.py so escreve um .txt (nao chama a API): livre.

Fail-open em erro interno (exit 0).
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _comum as c  # noqa: E402

# Ver "Limitacoes" no relatorio: `ask` de hook nao e garantido em -p/bypass; por
# isso o padrao e deny (comportamento igual em todos os modos), com escape.
PUBLICAR_DECISAO = "deny"
ESC_PUBLICAR = "GUARD_PUBLICAR_OK"
ESC_VOZ = "GUARD_VOZ_OK"

TRAVESSOES = ("—", "–")
NOME_PUBLICO = re.compile(
    r"^(roteiro|publicacao|publicação|titulo|título|descricao|descrição|legenda|hashtags?)"
    r"[^/]*\.(md|txt)$|\.(srt|vtt)$", re.I)

INTERPRETES = {"python", "python3", "pythonw", "py", "uv", "node", "bash", "sh"}
CLI_UPLOAD = re.compile(r"^(youtube|tiktok|instagram|ig|yt)[-_]?(upload|uploader|post|publish)\w*$")
FLAGS_VOZ_LIVRES = {"--checar", "--edge", "--gratis", "--simular", "--dry-run"}


# ---------------------------------------------------------------- regra 4
def caminho_publico(fp):
    p = fp.replace("\\", "/").lower()
    if "/node_modules/" in p:
        return False
    m = re.search(r"/conteudo/(canais|prontos)/", p)
    if not m:
        return False
    return bool(NOME_PUBLICO.search(os.path.basename(p)))


def pedacos(tool, ti):
    """[(antigo, novo)] do que a ferramenta vai gravar."""
    if tool == "Write":
        return [("", ti.get("content") or "")]
    if tool == "Edit":
        return [(ti.get("old_string") or "", ti.get("new_string") or "")]
    if tool == "MultiEdit":
        return [(e.get("old_string") or "", e.get("new_string") or "") for e in ti.get("edits") or []]
    return []


def conta(t):
    return sum(t.count(x) for x in TRAVESSOES)


def regra4(payload):
    tool = payload.get("tool_name")
    ti = payload.get("tool_input") or {}
    fp = ti.get("file_path") or ""
    if tool not in ("Write", "Edit", "MultiEdit") or not caminho_publico(fp):
        return
    for antigo, novo in pedacos(tool, ti):
        if conta(novo) > conta(antigo):
            i = next(k for k, ch in enumerate(novo) if ch in TRAVESSOES)
            trecho = novo[max(0, i - 25): i + 25].replace("\n", " ")
            c.responde(
                "Texto publico sem travessao (Cajuice/conteudo/CLAUDE.md): roteiro, titulo, "
                "descricao e legenda nao levam — nem –. Reescreva com virgula, ponto ou "
                "dois-pontos. Trecho: “...%s...” (%s)" % (trecho, os.path.basename(fp)))


# ---------------------------------------------------------------- regras 5 e 6
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


def regra5(tokens, envs):
    if envs.get(ESC_PUBLICAR) == "1":
        return
    alvo = None
    script = script_do_segmento(tokens)
    if script:
        b = os.path.basename(script.replace("\\", "/")).lower()
        if b in ("subir.py", "drive.py"):
            if "--simular" not in tokens:
                alvo = b
        elif CLI_UPLOAD.match(c.nome(script)):
            alvo = os.path.basename(script)
    if alvo:
        c.responde(
            "Nenhum agente publica (Cajuice/conteudo/CLAUDE.md): quem aprova e publica um "
            "video e uma pessoa. `%s` sobe conteudo para fora da maquina; peca ao usuario "
            "para rodar, ou para autorizar explicitamente. Para ensaiar sem enviar, use "
            "--simular. Se o usuario pediu este envio, repita o comando prefixado com %s=1."
            % (alvo, ESC_PUBLICAR), PUBLICAR_DECISAO)


def fonte_do_script(script, base):
    try:
        p = c.resolve_dir(base, script)
        if os.path.isfile(p):
            with open(p, encoding="utf-8", errors="replace") as fh:
                return fh.read(200000)
    except Exception:
        pass
    return None


def regra6(tokens, envs, base, seg):
    if envs.get(ESC_VOZ) == "1":
        return
    script = script_do_segmento(tokens)
    args = [a.lower() for a in tokens[1:]]
    # chamada direta a API de TTS (curl/wget/python -c)
    if "api.elevenlabs.io/v1/text-to-speech" in seg.lower():
        motivo_api = True
    else:
        motivo_api = False
    pago = False
    if script:
        b = os.path.basename(script.replace("\\", "/")).lower()
        norm = script.replace("\\", "/").lower()
        if b == "voz.py":
            livre = any(a in FLAGS_VOZ_LIVRES for a in args) or any(
                a.startswith("--motor") and "edge" in a for a in args) or (
                "--motor" in args and args[args.index("--motor") + 1: args.index("--motor") + 2] == ["edge"])
            src = fonte_do_script(script, base) or ""
            if "--motor" in src:                       # voz.py da esteira: edge e o padrao
                eleven = ("--motor=elevenlabs" in args) or (
                    "--motor" in args and args[args.index("--motor") + 1: args.index("--motor") + 2] == ["elevenlabs"])
                pago = eleven and "--checar" not in args
            elif "--checar" in src or "presto" in norm or "ferramentas/voz" in norm:
                pago = not livre                      # padrao pago: so --checar/--edge liberam
    if pago or motivo_api:
        c.responde(
            "Narracao paga (ElevenLabs gasta credito): rode antes com --checar e "
            "mostre ao usuario o custo estimado; so gere depois da aprovacao. Para voz "
            "gratuita use edge-tts (voz.py da esteira sem --motor elevenlabs, ou --edge). "
            "Se o usuario ja aprovou o custo, repita o comando prefixado com %s=1." % ESC_VOZ)


def main():
    payload = c.le_payload()
    tool = payload.get("tool_name")
    if tool in ("Write", "Edit", "MultiEdit"):
        regra4(payload)
        sys.exit(0)
    cmd = (payload.get("tool_input") or {}).get("command") or ""
    if not cmd:
        sys.exit(0)
    cwd = c.msys_para_win(payload.get("cwd") or os.getcwd())
    base = cwd
    for toks, envs, seg in c.segmentos(cmd):
        if toks[0] == "cd" and len(toks) >= 2:
            base = c.resolve_dir(base, toks[1])
            continue
        regra5(toks, envs)
        regra6(toks, envs, base, seg)
    sys.exit(0)


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except Exception:
        sys.exit(0)  # fail-open em erro interno
