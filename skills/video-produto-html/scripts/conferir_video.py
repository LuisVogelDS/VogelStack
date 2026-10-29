#!/usr/bin/env python3
"""Confere um MP4 renderizado: duração, resolução, fps, codec, faststart, áudio e quadros pretos.

Uso:
    python conferir_video.py video.mp4 --duracao 75 [--largura 1920 --altura 1080 --fps 30] [--audio | --mudo]
    python conferir_video.py video.mp4 --duracao 75 --audio --preto-ate-inicio 0.5 --preto-ate-fim 0.5

Cada verificação imprime OK ou FALHA com o motivo. Sai com código 1 se qualquer uma falhar, para o laço do passo de
verificação saber que precisa corrigir e rerenderizar. Usa ffprobe se existir; sem ele, lê o que o ffmpeg informa.
Quadro preto = trecho de pelo menos --preto-min segundos com luminância abaixo de --preto-limiar; o que cai no
começo ou no fim do vídeo e cabe nas margens --preto-ate-inicio/--preto-ate-fim (fade proposital) é aceito.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path


def achar(nome: str) -> str | None:
    env = os.environ.get(nome.upper())
    if env and Path(env).exists():
        return env
    if (c := shutil.which(nome)):
        return c
    if nome == "ffmpeg":
        for pasta in [Path.cwd(), *Path.cwd().parents]:
            c = pasta / "node_modules" / "ffmpeg-static" / ("ffmpeg.exe" if os.name == "nt" else "ffmpeg")
            if c.exists():
                return str(c)
        try:
            import imageio_ffmpeg
            return imageio_ffmpeg.get_ffmpeg_exe()
        except Exception:
            pass
    return None


def info(video: Path, ffprobe: str | None, ffmpeg: str) -> dict:
    """{'duracao','largura','altura','fps','codec','pix_fmt','audio'}"""
    if ffprobe:
        j = json.loads(subprocess.run([ffprobe, "-v", "error", "-print_format", "json", "-show_format", "-show_streams", str(video)],
                                      capture_output=True, text=True, check=True).stdout)
        v = next((s for s in j["streams"] if s["codec_type"] == "video"), {})
        a = next((s for s in j["streams"] if s["codec_type"] == "audio"), None)
        num, den = (v.get("avg_frame_rate") or "0/1").split("/")
        return {"duracao": float(j["format"]["duration"]), "largura": v.get("width"), "altura": v.get("height"),
                "fps": float(num) / float(den or 1), "codec": v.get("codec_name"), "pix_fmt": v.get("pix_fmt"),
                "audio": a["codec_name"] if a else None}
    saida = subprocess.run([ffmpeg, "-hide_banner", "-i", str(video)], capture_output=True, text=True).stderr
    d = re.search(r"Duration: (\d+):(\d+):([\d.]+)", saida)
    v = re.search(r"Video: (\w+)[^\n]*?, (\w+)[^\n]*?, (\d+)x(\d+)[^\n]*?, ([\d.]+) fps", saida)
    a = re.search(r"Audio: (\w+)", saida)
    return {"duracao": int(d[1]) * 3600 + int(d[2]) * 60 + float(d[3]) if d else 0.0,
            "largura": int(v[3]) if v else None, "altura": int(v[4]) if v else None, "fps": float(v[5]) if v else 0.0,
            "codec": v[1] if v else None, "pix_fmt": v[2] if v else None, "audio": a[1] if a else None}


def faststart(video: Path) -> bool:
    """O átomo 'moov' vem antes do 'mdat' (o MP4 toca na web sem baixar tudo)."""
    with video.open("rb") as f:
        pos, tam_arq = 0, video.stat().st_size
        while pos < tam_arq:
            f.seek(pos)
            cab = f.read(16)
            if len(cab) < 8:
                return False
            tam, tipo = int.from_bytes(cab[:4], "big"), cab[4:8]
            if tipo == b"moov":
                return True
            if tipo == b"mdat":
                return False
            if tam == 1:
                tam = int.from_bytes(cab[8:16], "big")
            if tam < 8:
                return False
            pos += tam
    return False


def pretos(ffmpeg: str, video: Path, minimo: float, limiar: float) -> list[tuple[float, float]]:
    r = subprocess.run([ffmpeg, "-hide_banner", "-i", str(video), "-vf", f"blackdetect=d={minimo}:pix_th={limiar}", "-an", "-f", "null", "-"],
                       capture_output=True, text=True)
    return [(float(a), float(b)) for a, b in re.findall(r"black_start:([\d.]+) black_end:([\d.]+)", r.stderr)]


def volume_medio(ffmpeg: str, video: Path) -> float | None:
    r = subprocess.run([ffmpeg, "-hide_banner", "-i", str(video), "-vn", "-af", "volumedetect", "-f", "null", "-"], capture_output=True, text=True)
    m = re.search(r"mean_volume: (-?[\d.]+|-inf) dB", r.stderr)
    return None if not m else (-120.0 if m[1] == "-inf" else float(m[1]))


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("video")
    ap.add_argument("--duracao", type=float, required=True, help="duração esperada, em segundos")
    ap.add_argument("--tolerancia", type=float, default=0.5, help="diferença aceita na duração (padrão 0,5 s)")
    ap.add_argument("--largura", type=int, default=1920)
    ap.add_argument("--altura", type=int, default=1080)
    ap.add_argument("--fps", type=float, default=30)
    grupo = ap.add_mutually_exclusive_group()
    grupo.add_argument("--audio", action="store_true", help="exige trilha de áudio audível")
    grupo.add_argument("--mudo", action="store_true", help="exige vídeo sem áudio")
    ap.add_argument("--volume-minimo", type=float, default=-50.0, help="volume médio mínimo (dB) para o áudio contar como audível")
    ap.add_argument("--preto-min", type=float, default=0.5, help="duração mínima de um trecho preto (s)")
    ap.add_argument("--preto-limiar", type=float, default=0.10, help="luminância (0 a 1) abaixo da qual o quadro é preto")
    ap.add_argument("--preto-ate-inicio", type=float, default=0.0, help="preto aceito no começo (fade de entrada), em s")
    ap.add_argument("--preto-ate-fim", type=float, default=0.0, help="preto aceito no fim (fade de saída), em s")
    args = ap.parse_args()
    for fluxo in (sys.stdout, sys.stderr):
        try:
            fluxo.reconfigure(encoding="utf-8")
        except Exception:
            pass

    video = Path(args.video)
    if not video.exists() or video.stat().st_size == 0:
        sys.exit(f"FALHA: {video} não existe ou está vazio")
    ffmpeg = achar("ffmpeg")
    if not ffmpeg:
        sys.exit("ffmpeg não encontrado: defina FFMPEG, ponha no PATH ou `pip install imageio-ffmpeg`")
    i = info(video, achar("ffprobe"), ffmpeg)
    falhas: list[str] = []

    def conferir(ok: bool, texto: str, motivo: str = ""):
        print(("OK     " if ok else "FALHA  ") + texto + ("" if ok else f" ({motivo})"))
        if not ok:
            falhas.append(texto)

    conferir(abs(i["duracao"] - args.duracao) <= args.tolerancia, f"duração {i['duracao']:.2f} s",
             f"esperado {args.duracao:.2f} s ± {args.tolerancia}")
    conferir((i["largura"], i["altura"]) == (args.largura, args.altura), f"resolução {i['largura']}x{i['altura']}",
             f"esperado {args.largura}x{args.altura}")
    conferir(abs(i["fps"] - args.fps) < 0.01, f"fps {i['fps']:.2f}", f"esperado {args.fps}")
    conferir(i["codec"] == "h264" and i["pix_fmt"] == "yuv420p", f"codec {i['codec']} / {i['pix_fmt']}", "esperado h264 / yuv420p")
    conferir(faststart(video), "faststart (moov antes do mdat)", "refaça com -movflags +faststart")
    if args.mudo:
        conferir(i["audio"] is None, "sem áudio", f"tem trilha {i['audio']}")
    if args.audio:
        conferir(i["audio"] is not None, f"áudio {i['audio']}", "sem trilha de áudio")
        if i["audio"]:
            v = volume_medio(ffmpeg, video)
            conferir(v is not None and v >= args.volume_minimo, f"volume médio {v} dB", f"abaixo de {args.volume_minimo} dB: áudio mudo ou quase")
    inesperados = []
    for a, b in pretos(ffmpeg, video, args.preto_min, args.preto_limiar):
        no_comeco = a <= 0.05 and b <= args.preto_ate_inicio + 0.05
        no_fim = b >= i["duracao"] - 0.1 and a >= i["duracao"] - args.preto_ate_fim - 0.05
        if not (no_comeco or no_fim):
            inesperados.append(f"{a:.2f}-{b:.2f} s")
    conferir(not inesperados, "sem quadros pretos fora das margens", "pretos em " + ", ".join(inesperados))
    print("RESULTADO:", "aprovado" if not falhas else f"reprovado em {len(falhas)} verificação(ões)")
    sys.exit(1 if falhas else 0)


if __name__ == "__main__":
    main()
