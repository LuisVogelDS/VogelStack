#!/usr/bin/env python3
"""Monta uma grade (contact sheet) das capturas novas de Capturas/ e resume os relatorio.txt, para ler tudo numa imagem só.

Ler imagem custa contexto a cada chamada seguinte; uma grade de 12 a 20 fotos custa uma imagem em vez de vinte.

Uso (dentro do projeto, ou com --projeto):
    python -I grade.py                          # PNG/JPG novos desde a última grade (ou da última hora)
    python -I grade.py --desde 30m              # janela: 45s, 30m, 2h, 1d, ou data 2026-10-28T15:00
    python -I grade.py Capturas/luz_periodos    # só esta pasta (repetível; padrão: Capturas/ inteira)
    python -I grade.py --tudo --por-pasta 3     # tudo, no máximo 3 fotos por pasta (as mais novas)
    python -I grade.py --colunas 4 --celula 360 --por-pagina 12 --saida Capturas/_grades/minha

Grava Capturas/_grades/grade-AAAAMMDD-HHMMSS-<n>.png (uma por página) e marca Capturas/.ultima-grade, de onde a
próxima chamada continua. Sem Pillow, grava o mesmo em HTML (abrir no navegador). Nunca escreve fora de Capturas/
e nunca mexe no git: Capturas/ é efêmera e fica fora do repositório.

Saída: 0 ok; 1 uso; 2 relatório com falha (a grade sai assim mesmo); 3 nenhuma captura no recorte.
"""
import argparse
import datetime
import html
import os
import re
import sys
import time

EXT = (".png", ".jpg", ".jpeg", ".webp")
FALHA = re.compile(r"^\s*(FALHA|FALHOU|ERRO|FAIL)", re.I)
RESUMO = re.compile(r"^\s*(OK:|FALHOU:)")


def achar_projeto(explicito=None):
    d = os.path.abspath(explicito or os.getcwd())
    while not os.path.isdir(os.path.join(d, "Capturas")):
        if os.path.dirname(d) == d:
            sys.exit("não achei uma pasta Capturas/ subindo da pasta atual; use --projeto")
        d = os.path.dirname(d)
    return d


def parse_desde(txt):
    m = re.fullmatch(r"(\d+)\s*([smhd])", txt.strip().lower())
    if m:
        return time.time() - int(m.group(1)) * {"s": 1, "m": 60, "h": 3600, "d": 86400}[m.group(2)]
    try:
        return datetime.datetime.fromisoformat(txt).timestamp()
    except ValueError:
        sys.exit(f"--desde não entendido: {txt!r} (use 30m, 2h, 1d ou uma data ISO)")


def coletar(pastas, desde, por_pasta):
    achados = {}
    for base in pastas:
        for dp, dn, fn in os.walk(base):
            dn[:] = [d for d in dn if d != "_grades" and not d.startswith(".")]
            for f in fn:
                if f.lower().endswith(EXT):
                    p = os.path.join(dp, f)
                    t = os.path.getmtime(p)
                    if desde is None or t >= desde:
                        achados.setdefault(dp, []).append((t, p))
    saida = []
    for dp in sorted(achados):
        fotos = sorted(achados[dp], key=lambda x: x[1])          # ordem do nome: 01-, 02-... contam uma história
        if por_pasta and len(fotos) > por_pasta:
            fotos = sorted(sorted(fotos, reverse=True)[:por_pasta], key=lambda x: x[1])   # as N mais novas
        saida += [p for _, p in fotos]
    return saida


def relatorios(pastas_das_fotos):
    """Resumo dos relatorio.txt ao lado das fotos: (pasta, resumo, linhas de falha)."""
    vistos, res = set(), []
    for pasta in sorted({os.path.dirname(p) for p in pastas_das_fotos}):
        arq = os.path.join(pasta, "relatorio.txt")
        if arq in vistos or not os.path.isfile(arq):
            continue
        vistos.add(arq)
        with open(arq, encoding="utf-8", errors="replace") as fh:
            linhas = [l.rstrip() for l in fh]
        resumo = next((l for l in reversed(linhas) if RESUMO.match(l)), "(sem linha de resumo)")
        res.append((pasta, resumo, [l for l in linhas if FALHA.match(l) and not RESUMO.match(l)]))
    return res


def rotulo(p, raiz):
    rel = os.path.relpath(p, raiz).replace("\\", "/")
    return rel[len("Capturas/"):] if rel.startswith("Capturas/") else rel


def grade_png(fotos, destino_base, raiz, colunas, celula, por_pagina):
    from PIL import Image, ImageDraw, ImageFont
    fonte = ImageFont.load_default()
    altura_rotulo = 28
    paginas = [fotos[i:i + por_pagina] for i in range(0, len(fotos), por_pagina)]
    saidas = []
    for n, pag in enumerate(paginas, 1):
        miniaturas = []
        for p in pag:
            try:
                with Image.open(p) as im:
                    im = im.convert("RGBA")
                    im.thumbnail((celula - 6, celula - 6))
                    fundo = Image.new("RGBA", im.size, (24, 24, 28, 255))
                    fundo.alpha_composite(im)       # PNG com transparência não vira preto ilegível
                    miniaturas.append(fundo.convert("RGB"))
            except Exception as e:                  # imagem corrompida: avisa na célula e segue
                miniaturas.append(e.__class__.__name__)
        alt = max([m.height for m in miniaturas if not isinstance(m, str)] or [40]) + 4   # altura da célula = a da foto mais alta da página
        linhas = -(-len(pag) // colunas)
        folha = Image.new("RGB", (colunas * celula, linhas * (alt + altura_rotulo)), (24, 24, 28))
        d = ImageDraw.Draw(folha)
        for i, (p, mini) in enumerate(zip(pag, miniaturas)):
            x, y = (i % colunas) * celula, (i // colunas) * (alt + altura_rotulo)
            if isinstance(mini, str):
                d.text((x + 6, y + 6), f"ilegível: {mini}", fill=(255, 120, 120), font=fonte)
            else:
                folha.paste(mini, (x + (celula - mini.width) // 2, y + 2))
            nome = rotulo(p, raiz)
            maxc = max(10, celula // 6)
            if len(nome) > maxc * 2:
                nome = "…" + nome[-(maxc * 2 - 1):]
            d.text((x + 4, y + alt + 1), nome[:maxc], fill=(235, 235, 235), font=fonte)
            if len(nome) > maxc:
                d.text((x + 4, y + alt + 13), nome[maxc:maxc * 2], fill=(235, 235, 235), font=fonte)
        saida = f"{destino_base}-{n}.png"
        os.makedirs(os.path.dirname(saida), exist_ok=True)
        folha.save(saida)
        saidas.append((saida, len(pag), folha.size))
    return saidas


def grade_html(fotos, destino_base, raiz, colunas, celula):
    saida = destino_base + ".html"
    os.makedirs(os.path.dirname(saida), exist_ok=True)
    itens = "".join(
        f'<figure><img src="file:///{os.path.abspath(p).replace(os.sep, "/")}" width="{celula}"><figcaption>{html.escape(rotulo(p, raiz))}</figcaption></figure>'
        for p in fotos)
    with open(saida, "w", encoding="utf-8") as fh:
        fh.write(f'<meta charset="utf-8"><style>body{{background:#181a1c;color:#eee;font:12px sans-serif;display:grid;'
                 f'grid-template-columns:repeat({colunas},{celula}px);gap:8px}}figure{{margin:0}}</style>{itens}')
    return [(saida, len(fotos), None)]


def main():
    for fluxo in (sys.stdout, sys.stderr):
        if hasattr(fluxo, "reconfigure"):
            fluxo.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("pastas", nargs="*", help="pastas ou arquivos dentro de Capturas/ (padrão: Capturas/ inteira)")
    ap.add_argument("--projeto", default=None)
    ap.add_argument("--desde", default=None, help="30m, 2h, 1d ou data ISO (padrão: desde a última grade, ou 1h)")
    ap.add_argument("--tudo", action="store_true", help="ignora o recorte de tempo")
    ap.add_argument("--por-pasta", type=int, default=0, help="no máximo N fotos por pasta (as mais novas)")
    ap.add_argument("--colunas", type=int, default=4)
    ap.add_argument("--celula", type=int, default=320, help="lado de cada célula, em pixels")
    ap.add_argument("--por-pagina", type=int, default=12)
    ap.add_argument("--saida", default=None, help="prefixo dos arquivos (padrão Capturas/_grades/grade-<data>)")
    ap.add_argument("--dry-run", action="store_true", help="lista o que entraria, sem gravar nada")
    ap.add_argument("--html", action="store_true", help="força a saída em HTML")
    a = ap.parse_args()

    raiz = achar_projeto(a.projeto)
    cap = os.path.join(raiz, "Capturas")
    marca = os.path.join(cap, ".ultima-grade")
    if a.tudo:
        desde = None
    elif a.desde:
        desde = parse_desde(a.desde)
    elif os.path.isfile(marca):
        desde = os.path.getmtime(marca)
    else:
        desde = time.time() - 3600
    pastas = [os.path.abspath(p) for p in a.pastas] or [cap]
    for p in pastas:
        if not os.path.commonpath([cap, p]) == cap:
            sys.exit(f"{p} fica fora de Capturas/; a grade só lê e grava lá")
    fotos = []
    for p in pastas:
        fotos += [p] if os.path.isfile(p) and p.lower().endswith(EXT) else coletar([p], desde, a.por_pasta)
    if not fotos:
        print("nenhuma captura no recorte (use --desde 1d ou --tudo)")
        return 3
    if a.por_pagina < 1 or a.colunas < 1:
        sys.exit("--colunas e --por-pagina precisam ser >= 1")
    rels = relatorios(fotos)
    print(f"{len(fotos)} capturas em {len({os.path.dirname(f) for f in fotos})} pasta(s)")
    falhou = False
    for pasta, resumo, falhas in rels:
        print(f"  {rotulo(pasta, raiz)}: {resumo}")
        for l in falhas[:6]:
            print(f"      {l[:160]}")
        if len(falhas) > 6:
            print(f"      ... e mais {len(falhas) - 6} linhas de falha")
        falhou = falhou or bool(falhas) or resumo.startswith("FALHOU")
    if a.dry_run:
        for f in fotos:
            print("   ", rotulo(f, raiz))
        return 2 if falhou else 0
    base = a.saida or os.path.join(cap, "_grades", "grade-" + datetime.datetime.now().strftime("%Y%m%d-%H%M%S"))
    if not os.path.isabs(base):
        base = os.path.join(raiz, base)
    if not os.path.commonpath([cap, os.path.abspath(base)]) == cap:
        sys.exit("--saida precisa ficar dentro de Capturas/")
    try:
        if a.html:
            raise ImportError
        saidas = grade_png(fotos, base, raiz, a.colunas, a.celula, a.por_pagina)
    except ImportError:
        if not a.html:
            print("Pillow ausente: gravando HTML. Para PNG: python -m pip install pillow", file=sys.stderr)
        saidas = grade_html(fotos, base, raiz, a.colunas, a.celula)
    for caminho, n, tam in saidas:
        print(f"grade: {caminho} ({n} fotos" + (f", {tam[0]}x{tam[1]}" if tam else "") + ")")
    open(marca, "w").close()
    return 2 if falhou else 0


if __name__ == "__main__":
    sys.exit(main())
