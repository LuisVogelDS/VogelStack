#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Testes do guard-conteudo.py: alimenta JSONs por stdin e confere a decisao."""
import json
import os
import subprocess
import sys
import tempfile
import time

HOOK = os.path.join(os.path.dirname(os.path.abspath(__file__)), "guard-conteudo.py")
EM = "—"   # travessao
EN = "–"   # meia-risca


def escreve(caminho, texto):
    os.makedirs(os.path.dirname(caminho), exist_ok=True)
    with open(caminho, "w", encoding="utf-8") as fh:
        fh.write(texto)


def chama(payload):
    t = time.time()
    r = subprocess.run([sys.executable, HOOK], input=json.dumps(payload), capture_output=True, text=True)
    ms = (time.time() - t) * 1000
    dec = None
    if r.stdout.strip():
        dec = json.loads(r.stdout)["hookSpecificOutput"]["permissionDecision"]
    return r.returncode, dec, ms


def main():
    base = tempfile.mkdtemp(prefix="guardconteudo-")
    cont = os.path.join(base, "Cajuice", "conteudo")
    vid = os.path.join(cont, "canais", "jogos", "videos", "2026-10-20-slime")
    # scripts de voz de mentira, com as flags dos reais
    presto = os.path.join(base, "presto", "divulgacao", "video")
    escreve(os.path.join(presto, "voz.py"), 'ap.add_argument("--checar", action="store_true")\n')
    esteira = os.path.join(cont, "esteira", "etapas", "03-voz")
    escreve(os.path.join(esteira, "voz.py"), 'ap.add_argument("--motor", choices=["edge", "elevenlabs"])\n')
    guaraci = os.path.join(base, "guaraci")
    escreve(os.path.join(guaraci, "texto_elevenlabs.py"), "print('so escreve txt')\n")
    comum = os.path.join(base, "comum")
    os.makedirs(comum)

    casos = []

    def arq(desc, tool, fp, ti, esp):
        casos.append((desc, {"hook_event_name": "PreToolUse", "tool_name": tool, "cwd": comum,
                             "tool_input": dict(ti, file_path=fp)}, esp))

    def bash(desc, cmd, cwd, esp):
        casos.append((desc, {"hook_event_name": "PreToolUse", "tool_name": "Bash", "cwd": cwd,
                             "tool_input": {"command": cmd}}, esp))

    # regra 4
    rot = os.path.join(vid, "roteiro.md")
    arq("roteiro Write com travessao", "Write", rot, {"content": "Ele pulou %s e caiu." % EM}, "deny")
    arq("roteiro Write meia-risca", "Write", rot, {"content": "de 42%s46 s" % EN}, "deny")
    arq("roteiro Write limpo", "Write", rot, {"content": "Ele pulou, e caiu."}, None)
    arq("roteiro Edit com travessao", "Edit", rot, {"old_string": "a", "new_string": "a %s b" % EM}, "deny")
    arq("roteiro Edit limpo", "Edit", rot, {"old_string": "a", "new_string": "a, b"}, None)
    arq("Edit corrige linha com travessao", "Edit", rot,
        {"old_string": "x %s y" % EM, "new_string": "x, y"}, None)
    arq("Edit mantem travessao antigo", "Edit", rot,
        {"old_string": "x %s y" % EM, "new_string": "x %s z" % EM}, None)
    arq("MultiEdit com travessao", "MultiEdit", rot,
        {"edits": [{"old_string": "a", "new_string": "b"}, {"old_string": "c", "new_string": "d%se" % EM}]}, "deny")
    arq("publicacao.md", "Write", os.path.join(vid, "publicacao.md"), {"content": "Titulo %s x" % EM}, "deny")
    arq("en/roteiro.md", "Write", os.path.join(vid, "en", "roteiro.md"), {"content": "a %s b" % EM}, "deny")
    arq("legenda srt", "Write", os.path.join(vid, "midia", "render", "en.srt"), {"content": "1\na %s b" % EM}, "deny")
    arq("descricao.txt", "Write", os.path.join(vid, "descricao.txt"), {"content": "a %s b" % EM}, "deny")
    arq("caminho Windows", "Write", rot.replace("/", "\\"), {"content": "a %s b" % EM}, "deny")
    arq("doc interno (voz.md)", "Write", os.path.join(vid, "voz.md"), {"content": "a %s b" % EM}, None)
    arq("doc do repo (docs/)", "Write", os.path.join(cont, "docs", "oficio-de-video.md"), {"content": "a %s b" % EM}, None)
    arq("codigo da esteira", "Write", os.path.join(esteira, "voz.py"), {"content": "# a %s b" % EM}, None)
    arq("roteiro fora do conteudo", "Write", os.path.join(base, "outro", "roteiro.md"), {"content": "a %s b" % EM}, None)
    arq("canal.md", "Write", os.path.join(cont, "canais", "jogos", "canal.md"), {"content": "a %s b" % EM}, None)

    # regra 5
    bash("subir.py", "python esteira/etapas/09-publicacao/subir.py canais/x/videos/y --conta a", cont, "deny")
    bash("subir.py simular", "python esteira/etapas/09-publicacao/subir.py canais/x --conta a --simular", cont, None)
    bash("drive.py upload", "python esteira/etapas/09-publicacao/drive.py", cont, "deny")
    bash("drive.py simular", "python esteira/etapas/09-publicacao/drive.py --simular", cont, None)
    bash("drive_local.py livre", "python esteira/etapas/09-publicacao/drive_local.py a b", cont, None)
    bash("youtube-upload CLI", "youtube-upload --title x video.mp4", cont, "deny")
    bash("tiktok-uploader CLI", "tiktok-uploader -v x.mp4", cont, "deny")
    bash("subir.py composto", "cd canais && python ../esteira/etapas/09-publicacao/subir.py x --conta a", cont, "deny")
    bash("subir.py escape", "GUARD_PUBLICAR_OK=1 python subir.py x --conta a", cont, None)
    bash("git add subir.py", "git add esteira/etapas/09-publicacao/subir.py", cont, None)
    bash("cat subir.py", "cat esteira/etapas/09-publicacao/subir.py", cont, None)
    bash("prontos.py livre", "python esteira/etapas/09-publicacao/prontos.py", cont, None)

    # regra 6
    bash("presto sem checar", "python voz.py --lang pt", presto, "deny")
    bash("presto com checar", "python voz.py --lang pt --checar", presto, None)
    bash("presto por caminho", 'python "%s" --lang pt --refazer' % os.path.join(presto, "voz.py"), comum, "deny")
    bash("presto cd &&", "cd '%s' && python voz.py --lang pt" % presto, comum, "deny")
    bash("presto escape", "GUARD_VOZ_OK=1 python voz.py --lang pt", presto, None)
    bash("esteira edge padrao", "python esteira/etapas/03-voz/voz.py canais/x/videos/y", cont, None)
    bash("esteira edge explicito", "python esteira/etapas/03-voz/voz.py canais/x/videos/y --motor edge", cont, None)
    bash("esteira elevenlabs", "python esteira/etapas/03-voz/voz.py canais/x/videos/y --motor elevenlabs --voz abc", cont, "deny")
    bash("esteira elevenlabs =", "python esteira/etapas/03-voz/voz.py y --motor=elevenlabs --voz abc", cont, "deny")
    bash("esteira elevenlabs escape", "GUARD_VOZ_OK=1 python esteira/etapas/03-voz/voz.py y --motor elevenlabs --voz a", cont, None)
    bash("futuro ferramentas/voz sem flag", "python ferramentas/voz/voz.py y", comum, "deny")
    bash("futuro ferramentas/voz --edge", "python ferramentas/voz/voz.py y --edge", comum, None)
    bash("texto_elevenlabs livre", "python texto_elevenlabs.py pt", guaraci, None)
    bash("curl TTS direto", 'curl -X POST https://api.elevenlabs.io/v1/text-to-speech/abc -d "{}"', comum, "deny")
    bash("curl outra rota livre", "curl https://api.elevenlabs.io/v1/user/subscription", comum, None)
    bash("grep voz.py", "grep -n checar voz.py", presto, None)

    # sem relacao
    bash("ls", "ls -la", comum, None)
    bash("comando vazio", "", comum, None)

    falhas = 0
    lentos = []
    for desc, payload, esp in casos:
        rc, dec, ms = chama(payload)
        ok = rc == 0 and dec == esp
        falhas += 0 if ok else 1
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
