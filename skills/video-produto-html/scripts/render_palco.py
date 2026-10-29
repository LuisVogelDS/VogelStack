#!/usr/bin/env python3
"""Renderiza um palco HTML em MP4: abre a página, chama window.seek(t) a cada quadro e entrega as fotos ao FFmpeg.

O palco é uma página que desenha tudo em função do tempo t, sem relógio de parede nem Math.random, e expõe:
    window.seek(t)       posiciona a página no instante t (segundos), de forma síncrona
    window.stageReady    (opcional) promessa que resolve quando fontes e imagens carregaram

Uso:
    python render_palco.py --palco palco/index.html --duracao 75 --saida _midia/out/video.mp4
    python render_palco.py --palco palco/index.html --linha _midia/linha-pt.js --consulta "render&lang=pt" --saida out.mp4
    python render_palco.py --palco palco/index.html --duracao 75 --de 49 --ate 61 --saida trecho.mp4   # trecho para conferir
    python render_palco.py --palco palco/index.html --duracao 75 --audio voz.mp3 --saida out.mp4        # com áudio já pronto

Padrões: 1920x1080, 30 fps, H.264 -crf 17, yuv420p, -movflags +faststart. Sem rede: qualquer requisição que não seja
file:, data: ou blob: é abortada e conta como erro (fonte e imagem têm de estar no disco, ao lado do palco).
Sai com código 1 se o palco lançar erro de JavaScript ou pedir recurso de fora.
Dependências: playwright (com chromium instalado) e um ffmpeg (FFMPEG, PATH, ffmpeg-static ou imageio-ffmpeg).
"""
from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlparse


def achar_ffmpeg() -> str:
    candidatos = [os.environ.get("FFMPEG"), shutil.which("ffmpeg")]
    for pasta in [Path.cwd(), *Path.cwd().parents]:
        candidatos.append(str(pasta / "node_modules" / "ffmpeg-static" / ("ffmpeg.exe" if os.name == "nt" else "ffmpeg")))
    try:
        import imageio_ffmpeg
        candidatos.append(imageio_ffmpeg.get_ffmpeg_exe())
    except Exception:
        pass
    for c in candidatos:
        if c and Path(c).exists():
            return c
    sys.exit("ffmpeg não encontrado: defina FFMPEG, ponha no PATH ou `pip install imageio-ffmpeg`")


def duracao_da_linha(arq: Path) -> float:
    """Lê `"total": N` de um arquivo de linha do tempo (JSON ou .js com window.LINHA = {...})."""
    m = re.search(r'"total"\s*:\s*([0-9.]+)', arq.read_text(encoding="utf-8"))
    if not m:
        sys.exit(f"não achei \"total\" em {arq}")
    return float(m.group(1))


def url_do_palco(palco: str, consulta: str) -> str:
    base = palco if re.match(r"^(file|https?):", palco) else Path(palco).resolve().as_uri()
    return base + ("?" + consulta.lstrip("?") if consulta else "")


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--palco", required=True, help="arquivo HTML do palco (ou URL file:/http://localhost)")
    ap.add_argument("--consulta", default="render", help="query string da página (padrão: render)")
    ap.add_argument("--duracao", type=float, help="duração total, em segundos")
    ap.add_argument("--linha", help="arquivo com \"total\": N (alternativa a --duracao)")
    ap.add_argument("--saida", required=True, help="MP4 de saída")
    ap.add_argument("--audio", help="áudio já pronto para juntar (AAC 192k); sem ele o vídeo sai mudo")
    ap.add_argument("--fps", type=int, default=30)
    ap.add_argument("--largura", type=int, default=1920)
    ap.add_argument("--altura", type=int, default=1080, help="use --largura 1080 --altura 1920 para 9:16 (o palco precisa suportar)")
    ap.add_argument("--crf", type=int, default=17)
    ap.add_argument("--qualidade-jpeg", type=int, default=94)
    ap.add_argument("--de", type=float, default=0.0)
    ap.add_argument("--ate", type=float)
    ap.add_argument("--permitir-rede", action="store_true", help="não aborta requisições externas (evite: o render deve ser reprodutível offline)")
    args = ap.parse_args()
    for fluxo in (sys.stdout, sys.stderr):
        try:
            fluxo.reconfigure(encoding="utf-8")
        except Exception:
            pass

    total = args.duracao if args.duracao is not None else duracao_da_linha(Path(args.linha)) if args.linha else None
    if total is None:
        sys.exit("informe --duracao ou --linha")
    ate = min(args.ate if args.ate is not None else total, total)
    if args.de >= ate:
        sys.exit("--de precisa ser menor que --ate / a duração")
    quadros = int(round((ate - args.de) * args.fps))
    ffmpeg = achar_ffmpeg()
    destino = Path(args.saida)
    destino.parent.mkdir(parents=True, exist_ok=True)
    mudo = destino.with_name(destino.stem + "-mudo.mp4") if args.audio else destino

    from playwright.sync_api import sync_playwright

    problemas: list[str] = []
    ff = subprocess.Popen(
        [ffmpeg, "-y", "-loglevel", "error", "-f", "image2pipe", "-framerate", str(args.fps), "-c:v", "mjpeg", "-i", "-",
         "-vf", "scale=in_range=pc:out_range=tv,format=yuv420p", "-color_range", "tv",
         "-c:v", "libx264", "-preset", "medium", "-crf", str(args.crf), "-r", str(args.fps),
         "-movflags", "+faststart", str(mudo)],
        stdin=subprocess.PIPE)
    with sync_playwright() as p:
        browser = p.chromium.launch(args=["--run-all-compositor-stages-before-draw", "--disable-gpu-vsync"])
        page = browser.new_page(viewport={"width": args.largura, "height": args.altura})
        page.on("pageerror", lambda e: problemas.append(f"erro de JavaScript: {e}"))
        if not args.permitir_rede:
            def filtro(rota):
                esquema = urlparse(rota.request.url).scheme
                if esquema in ("file", "data", "blob"):
                    rota.continue_()
                else:
                    problemas.append(f"requisição externa abortada: {rota.request.url}")
                    rota.abort()
            page.route("**/*", filtro)
        page.goto(url_do_palco(args.palco, args.consulta))
        page.wait_for_load_state("load")
        page.evaluate("() => window.stageReady || null")
        if not page.evaluate("() => typeof window.seek === 'function'"):
            sys.exit("o palco não expõe window.seek(t)")
        for f in range(quadros):
            t = args.de + f / args.fps
            page.evaluate(f"window.seek({t:.4f})")
            ff.stdin.write(page.screenshot(type="jpeg", quality=args.qualidade_jpeg))
            if f % (args.fps * 10) == 0:
                print(f"  {t:6.1f} s / {ate:.1f} s", flush=True)
        browser.close()
    ff.stdin.close()
    ff.wait()
    if ff.returncode:
        sys.exit(f"ffmpeg saiu com erro {ff.returncode}")

    if args.audio:
        subprocess.run([ffmpeg, "-y", "-loglevel", "error", "-i", str(mudo), "-i", args.audio, "-map", "0:v", "-map", "1:a",
                        "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", str(destino)], check=True)
        mudo.unlink()
    for pb in sorted(set(problemas)):
        print("PROBLEMA:", pb)
    print(f"pronto: {destino} ({quadros} quadros, {quadros / args.fps:.2f} s)")
    sys.exit(1 if problemas else 0)


if __name__ == "__main__":
    main()
