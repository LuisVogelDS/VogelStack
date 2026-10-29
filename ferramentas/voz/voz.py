#!/usr/bin/env python3
"""voz.py: narração para vídeo com edge-tts (gratuito) ou ElevenLabs (pago), numa ferramenta só.

Unifica três scripts: a voz-guia da esteira Cajuice (um áudio por parágrafo do roteiro.md), a narração
em uma chamada só do vídeo do Presto (textos/v3-<idioma>.json) e as duas peças do Guaraci (voz-guia
edge-tts e texto com pausas para o ElevenLabs). Documentação, diferenças e exemplos: README.md ao lado.

Três modos (--modo; o padrão é "esteira" se vier uma pasta e "take" se não vier):

  esteira   voz.py <pasta-do-video> [opções]
            lê <pasta>/roteiro.md, um áudio por parágrafo (cache por hash do parágrafo), monta o take e
            grava midia/audio/p01.mp3.., voz.mp3, paragrafos.json, e na pasta timings.json e voz.md.
  take      voz.py --lang pt [--blocos textos/v3-pt.json] [--saida DIR]
            junta os blocos do JSON e faz UMA chamada (a fala sai mais fluida). Grava completa.mp3 e
            completa.json (tempo de cada palavra) em _midia/voz/<idioma>/. --emendar refaz só da primeira
            frase alterada em diante.
  blocos    voz.py --modo blocos --lang pt --blocos textos/pt.json --saida narracao/pt
            um arquivo por bloco (<id>.mp3), com cache por hash de cada bloco: mudar um bloco regera só ele.

Custo e segurança:
  --checar         não gasta nada: mostra caracteres, o que seria gerado, estimativa em créditos, gasto
                   acumulado contra o teto e (se houver chave) a conta. Sempre rode antes de pagar.
  --teto N         limite de caracteres ElevenLabs somados em gasto.json (padrão 3000, ou VOZ_TETO).
  A chave vem de ELEVENLABS_API_KEY no ambiente; na falta, de um .env (--env, VOZ_ENV, ou .env na pasta
  do projeto e nas pastas acima). A chave nunca é impressa nem gravada.
"""
from __future__ import annotations

import argparse
import asyncio
import base64
import datetime as dt
import hashlib
import json
import math
import os
import re
import shutil
import subprocess
import sys
import unicodedata
import urllib.error
import urllib.request
from array import array
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent
TAXA_AMOSTRA = 24000          # o edge-tts entrega mp3 mono a 24 kHz
TICKS = 10_000_000            # o edge-tts mede tempo em unidades de 100 ns
TETO_PADRAO = 3000            # caracteres ElevenLabs no total, somando todas as gerações
MODELO_PADRAO = "eleven_v4"
VOZ_ELEVEN_PADRAO = "m151rjrbWXbBqyq56tly"   # "Carla - Inviting, Warm and Helpful" (biblioteca compartilhada)
VOZ_EDGE_PADRAO = {"pt": "pt-BR-AntonioNeural", "en": "en-US-GuyNeural"}
# créditos por caractere; o que não está aqui conta 1. Estimativa: confirme no painel do ElevenLabs.
CREDITO_POR_CARACTERE = {"eleven_flash_v2_5": 0.5, "eleven_turbo_v2_5": 0.5}


# ---------------------------------------------------------------- chave, ffmpeg, gasto

def _ler_chave_de(arq: Path) -> str | None:
    try:
        for linha in arq.read_text(encoding="utf-8").splitlines():
            if linha.strip().startswith("ELEVENLABS_API_KEY="):
                return linha.split("=", 1)[1].strip().strip('"').strip("'") or None
    except OSError:
        pass
    return None


def procurar_chave(extra_env: str | None, dirs: list[Path]) -> tuple[str | None, str]:
    """Devolve (chave, de onde veio). Nunca imprima a chave: só a origem."""
    k = os.environ.get("ELEVENLABS_API_KEY")
    if k:
        return k, "variável de ambiente ELEVENLABS_API_KEY"
    candidatos = [Path(p) for p in (extra_env, os.environ.get("VOZ_ENV")) if p]
    for d in dirs:
        for pasta in [d, *d.parents]:
            candidatos.append(pasta / ".env")
    vistos = set()
    for arq in candidatos:
        if arq in vistos:
            continue
        vistos.add(arq)
        if arq.exists() and (k := _ler_chave_de(arq)):
            return k, f"arquivo {arq}"
    return None, "não encontrada"


class Ambiente:
    """Chave e ffmpeg, resolvidos uma vez."""
    def __init__(self, extra_env: str | None, dirs: list[Path]):
        self.dirs = dirs
        self.chave, self.origem = procurar_chave(extra_env, dirs)
        self._ffmpeg = None

    def exigir_chave(self) -> str:
        if not self.chave:
            sys.exit("falta ELEVENLABS_API_KEY: defina a variável de ambiente (ou aponte um .env com --env/VOZ_ENV)")
        return self.chave

    def ffmpeg(self) -> str:
        if self._ffmpeg:
            return self._ffmpeg
        candidatos = [os.environ.get("FFMPEG"), os.environ.get("CAJUICE_FFMPEG")]
        for d in self.dirs:
            for pasta in [d, *d.parents]:
                candidatos.append(str(pasta / "node_modules" / "ffmpeg-static" / ("ffmpeg.exe" if os.name == "nt" else "ffmpeg")))
        candidatos.append(shutil.which("ffmpeg"))
        try:
            import imageio_ffmpeg
            candidatos.append(imageio_ffmpeg.get_ffmpeg_exe())
        except Exception:
            pass
        for c in candidatos:
            if c and Path(c).exists():
                self._ffmpeg = c
                return c
        sys.exit("ffmpeg não encontrado: defina FFMPEG, instale o ffmpeg no PATH ou `pip install imageio-ffmpeg`")


class Orcamento:
    """Soma os caracteres ElevenLabs em gasto.json e recusa o que passaria do teto."""
    def __init__(self, arq: Path, teto: int):
        self.arq, self.teto = arq, teto
        self.dados = json.loads(arq.read_text(encoding="utf-8")) if arq.exists() else {"total": 0, "chamadas": []}

    @property
    def total(self) -> int:
        return self.dados["total"]

    def cabe(self, n: int) -> bool:
        return self.total + n <= self.teto

    def conferir(self, n: int):
        if not self.cabe(n):
            sys.exit(f"recusado: passaria do teto de {self.teto} caracteres ({self.total} + {n}). "
                     f"Aumente com --teto ou VOZ_TETO só com a autorização de quem paga.")

    def somar(self, n: int, **info):
        self.dados["total"] += n
        self.dados["chamadas"].append({"caracteres": n, "quando": dt.datetime.now().isoformat(timespec="seconds"), **info})
        self.arq.parent.mkdir(parents=True, exist_ok=True)
        self.arq.write_text(json.dumps(self.dados, ensure_ascii=False, indent=1), encoding="utf-8")


# ---------------------------------------------------------------- ElevenLabs

def api(amb: Ambiente, caminho: str, corpo=None, metodo=None):
    req = urllib.request.Request(
        "https://api.elevenlabs.io" + caminho,
        data=json.dumps(corpo).encode("utf-8") if corpo is not None else None,
        headers={"xi-api-key": amb.exigir_chave(), "Content-Type": "application/json"},
        method=metodo,
    )
    try:
        with urllib.request.urlopen(req, timeout=180) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        sys.exit(f"ElevenLabs recusou ({e.code}) em {caminho}: {e.read().decode('utf-8', 'replace')[:400]}")


def consultar_voz(amb: Ambiente, voz: str) -> str | None:
    """Nome da voz se ela já está na conta; None se não está. Não altera nada."""
    req = urllib.request.Request(f"https://api.elevenlabs.io/v1/voices/{voz}", headers={"xi-api-key": amb.exigir_chave()})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.loads(r.read()).get("name")
    except urllib.error.HTTPError as e:
        if e.code in (400, 404):
            return None
        sys.exit(f"ElevenLabs recusou ({e.code}) ao consultar a voz: {e.read().decode('utf-8', 'replace')[:300]}")


def garantir_voz(amb: Ambiente, voz: str) -> str:
    """Se a voz da biblioteca compartilhada não está na conta, adiciona (não gasta caracteres)."""
    nome = consultar_voz(amb, voz)
    if nome:
        return nome
    achadas = api(amb, "/v1/shared-voices?page_size=100").get("voices", [])
    v = next((x for x in achadas if x.get("voice_id") == voz), None)
    if not v:
        sys.exit(f"a voz {voz} não está na conta nem na biblioteca compartilhada: parar e avisar (sem trocar de voz)")
    api(amb, f"/v1/voices/add/{v['public_owner_id']}/{voz}", {"new_name": v["name"]})
    return v["name"]


def fronteiras_do_alinhamento(al: dict) -> list[dict]:
    """A API devolve o tempo de cada caractere; a palavra é o trecho entre espaços ou quebras de linha."""
    fronteiras, atual = [], None
    for c, ini, fim in zip(al.get("characters", []), al.get("character_start_times_seconds", []),
                           al.get("character_end_times_seconds", [])):
        if c.isspace():
            if atual:
                fronteiras.append(atual)
            atual = None
            continue
        if atual is None:
            atual = {"texto": c, "inicio": ini, "fim": fim}
        else:
            atual["texto"] += c
            atual["fim"] = fim
    if atual:
        fronteiras.append(atual)
    return fronteiras


def eleven_tts(amb: Ambiente, texto: str, voz: str, modelo: str, ajustes: dict, anterior: str = "") -> tuple[bytes, list[dict]]:
    corpo = {"text": texto, "model_id": modelo, "voice_settings": ajustes}
    if anterior:
        corpo["previous_text"] = anterior
    resp = api(amb, f"/v1/text-to-speech/{voz}/with-timestamps?output_format=mp3_44100_128", corpo)
    return base64.b64decode(resp["audio_base64"]), fronteiras_do_alinhamento(resp.get("alignment") or resp["normalized_alignment"])


# ---------------------------------------------------------------- edge-tts

async def _edge(texto: str, voz: str, taxa: str, tom: str) -> tuple[bytes, list[dict]]:
    import edge_tts
    ultimo_erro = None
    for _ in range(3):
        try:
            com = edge_tts.Communicate(texto, voz, rate=taxa, pitch=tom, boundary="WordBoundary")
            audio, fronteiras = bytearray(), []
            async for pedaco in com.stream():
                if pedaco["type"] == "audio":
                    audio.extend(pedaco["data"])
                elif pedaco["type"] == "WordBoundary":
                    fronteiras.append({"texto": pedaco["text"], "inicio": pedaco["offset"] / TICKS,
                                       "fim": (pedaco["offset"] + pedaco["duration"]) / TICKS})
            if not audio:
                raise RuntimeError("o serviço não devolveu áudio")
            return bytes(audio), fronteiras
        except ImportError:
            sys.exit("falta o edge-tts: pip install edge-tts")
        except Exception as e:  # rede instável: tenta de novo
            ultimo_erro = e
            await asyncio.sleep(1.5)
    raise RuntimeError(f"falha ao sintetizar: {ultimo_erro}")


def edge_tts_sync(texto: str, voz: str, taxa: str, tom: str = "+0Hz") -> tuple[bytes, list[dict]]:
    return asyncio.run(_edge(texto, voz, taxa, tom))


# ---------------------------------------------------------------- texto e áudio (comum)

def normalizar(s: str) -> str:
    s = unicodedata.normalize("NFD", s.lower())
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9]", "", s)


def sha(*partes) -> str:
    return hashlib.sha1("|".join(str(p) for p in partes).encode("utf-8")).hexdigest()


def fmt(s: float) -> str:
    return f"{s:.2f}".replace(".", ",") + " s"


def palavras_lista(fronteiras: list[dict]) -> list[list]:
    return [[f["texto"], round(f["inicio"], 3), round(f["fim"], 3)] for f in fronteiras]


def decodificar(ffmpeg: str, mp3: Path, filtro: str | None = None) -> bytes:
    """PCM s16le mono 24 kHz (com o filtro de áudio do personagem, se houver)."""
    r = subprocess.run([ffmpeg, "-v", "error", "-i", str(mp3), *(["-af", filtro] if filtro else []),
                        "-f", "s16le", "-ac", "1", "-ar", str(TAXA_AMOSTRA), "-"], capture_output=True, check=True)
    return r.stdout


def codificar(ffmpeg: str, pcm: bytes, destino: Path) -> None:
    subprocess.run([ffmpeg, "-v", "error", "-y", "-f", "s16le", "-ac", "1", "-ar", str(TAXA_AMOSTRA), "-i", "-",
                    "-c:a", "libmp3lame", "-b:a", "128k", str(destino)], input=pcm, check=True)


def custo_texto(n: int, modelo: str) -> float:
    return n * CREDITO_POR_CARACTERE.get(modelo, 1.0)


def relatar_conta(amb: Ambiente, voz: str | None):
    """Parte do --checar que consulta a conta. Só leitura."""
    print(f"chave: {amb.origem}")
    if not amb.chave:
        print("conta: não consultada (sem chave)")
        return
    s = api(amb, "/v1/user/subscription")
    print(f"conta: {s.get('tier')}, {s.get('character_count')} de {s.get('character_limit')} caracteres usados no período")
    if voz:
        nome = consultar_voz(amb, voz)
        print(f"voz {voz}: " + (f"na conta ({nome})" if nome else "ainda não está na conta (a geração a adiciona da biblioteca, sem custo)"))


# ---------------------------------------------------------------- modo esteira (um áudio por parágrafo)

def ler_paragrafos(roteiro: Path) -> list[str]:
    texto = roteiro.read_text(encoding="utf-8")
    texto = re.sub(r"<!--.*?-->", "", texto, flags=re.S)
    linhas = ["" if l.lstrip().startswith("#") else l for l in texto.splitlines()]
    paragrafos = []
    for bloco in re.split(r"\n\s*\n", "\n".join(linhas)):
        p = " ".join(l.strip() for l in bloco.splitlines() if l.strip())
        p = re.sub(r"\s*\[[^\]]*\]", "", p)  # marcações de fonte [1], [fonte: x]
        p = re.sub(r"\s+", " ", p).strip()
        if p:
            paragrafos.append(p)
    return paragrafos


# fala de personagem: parágrafo que começa com o nome em maiúsculas e dois-pontos ("DONA CIDA: ...")
FALA = re.compile(r"^\*{0,2}([A-ZÀ-Ý][A-ZÀ-Ý0-9 ]{0,30}?)\*{0,2}:\*{0,2}\s+(.+)$")


def separar_fala(paragrafo: str) -> tuple[str | None, str]:
    m = FALA.match(paragrafo)
    return (m.group(1).strip(), m.group(2).strip()) if m else (None, paragrafo)


def ler_elenco(pasta: Path, caminho: str | None) -> dict:
    """elenco.json do canal (canais/<canal>/elenco.json, duas pastas acima do vídeo) ou o de --elenco."""
    arq = Path(caminho) if caminho else pasta.parents[1] / "elenco.json"
    if not arq.exists():
        if caminho:
            sys.exit(f"não achei o elenco {arq}")
        return {}
    dados = json.loads(arq.read_text(encoding="utf-8"))
    return {normalizar(k): {**v, "nome": k} for k, v in dados.items() if not k.startswith("_")}


def silabas(palavra: str) -> int:
    return max(1, len(re.findall(r"[aeiouáéíóúâêôãõày]+", palavra.lower())))


def aparar(pcm: bytes, respiro: float, borda_ini: float = 0.03, borda_fim: float = 0.08):
    """Tira o silêncio das bordas e encurta, no meio, todo silêncio interno maior que `respiro`.
    Devolve (pcm novo, cortes em segundos do áudio original)."""
    amostras = array("h")
    amostras.frombytes(pcm)
    janela = TAXA_AMOSTRA // 100  # 10 ms
    n = len(amostras) // janela
    if n < 3:
        return pcm, []
    rms = [math.sqrt(sum(x * x for x in amostras[k * janela:(k + 1) * janela]) / janela) for k in range(n)]
    limiar = max(120.0, 0.03 * max(rms))
    total = len(amostras) / TAXA_AMOSTRA
    cortes, k = [], 0
    while k < n:
        if rms[k] >= limiar:
            k += 1
            continue
        k0 = k
        while k < n and rms[k] < limiar:
            k += 1
        a, b = k0 * janela / TAXA_AMOSTRA, k * janela / TAXA_AMOSTRA
        if k0 == 0 and k == n:
            return pcm, []  # parágrafo mudo: não mexe
        if k0 == 0:
            if b - borda_ini > 0:
                cortes.append((0.0, b - borda_ini))
        elif k == n:
            if a + borda_fim < total:
                cortes.append((a + borda_fim, total))
        elif b - a > respiro:
            meio, sobra = (a + b) / 2, (b - a - respiro) / 2
            cortes.append((meio - sobra, meio + sobra))
    if not cortes:
        return pcm, []
    novo, pos = array("h"), 0
    for a, b in cortes:
        ia, ib = int(round(a * TAXA_AMOSTRA)), int(round(b * TAXA_AMOSTRA))
        novo.extend(amostras[pos:ia])
        pos = ib
    novo.extend(amostras[pos:])
    return novo.tobytes(), cortes


def remapear(t: float, cortes: list[tuple[float, float]]) -> float:
    return t - sum(min(max(0.0, t - a), b - a) for a, b in cortes)


def separar_pausas(texto: str) -> tuple[str, dict[int, int]]:
    """Tira os marcadores de pausa (`/` ou `//` soltos entre palavras). Devolve (texto limpo, {índice da palavra antes: barras})."""
    tokens, pausas = [], {}
    for t in texto.split(" "):
        if re.fullmatch(r"/+", t):
            if tokens:
                pausas[len(tokens) - 1] = pausas.get(len(tokens) - 1, 0) + len(t)
        elif t:
            tokens.append(t)
    return " ".join(tokens), pausas


def inserir_pausas(pcm: bytes, palavras: list[dict], pausas: dict[int, int], seg: float) -> bytes:
    """Insere `seg` segundos de silêncio por barra entre a palavra k e a k+1 (tempos locais ao parágrafo)."""
    if not pausas:
        return pcm
    amostras = bytearray(pcm)
    for k in sorted(pausas, reverse=True):  # do fim para o começo: as posições anteriores não andam
        if k + 1 >= len(palavras):
            amostras.extend(bytes(2 * int(round(seg * pausas[k] * TAXA_AMOSTRA))))
            continue
        fim, prox = palavras[k]["fim"], palavras[k + 1]["inicio"]
        t = (fim + prox) / 2 if prox > fim else fim
        extra = seg * pausas[k]
        pos = int(round(t * TAXA_AMOSTRA)) * 2
        amostras[pos:pos] = b"\x00\x00" * int(round(extra * TAXA_AMOSTRA))
        for w in palavras[k + 1:]:
            w["inicio"] += extra
            w["fim"] += extra
    return bytes(amostras)


def alinhar(paragrafo: str, fronteiras: list[dict], duracao: float, p_idx: int):
    """Casa as palavras do roteiro (com pontuação) com as fronteiras do serviço. Devolve (palavras, divergências, método)."""
    palavras = [{"p": p_idx, "texto": t, "norm": normalizar(t), "inicio": None, "fim": None} for t in paragrafo.split(" ")]
    divergencias, metodo = [], "WordBoundary"
    if fronteiras:
        cursor = 0
        for f in fronteiras:
            fn = normalizar(f["texto"])
            if not fn:
                continue
            achou = None
            for j in range(cursor, min(cursor + 4, len(palavras))):
                pn = palavras[j]["norm"]
                if pn and (pn == fn or pn.startswith(fn) or fn.startswith(pn)):
                    achou = j
                    break
            if achou is None:
                divergencias.append(f"parágrafo {p_idx}: fala '{f['texto']}' sem palavra correspondente no roteiro")
                continue
            w = palavras[achou]
            if w["inicio"] is None:
                w["inicio"] = f["inicio"]
            w["fim"] = f["fim"]
            cursor = achou if len(fn) < len(w["norm"]) else achou + 1  # número lido em partes mantém o cursor nele
    else:
        metodo = "proporcional-silabas"
    if metodo == "proporcional-silabas" or all(w["inicio"] is None for w in palavras):
        pesos = [silabas(w["texto"]) for w in palavras]
        total = sum(pesos) or 1
        margem = 0.08
        util = max(0.1, duracao - 2 * margem)
        t = margem
        for w, peso in zip(palavras, pesos):
            d = util * peso / total
            w["inicio"], w["fim"] = t, t + d * 0.92
            t += d
        return palavras, divergencias, "proporcional-silabas"
    for i, w in enumerate(palavras):  # palavra sem fronteira: interpola
        if w["inicio"] is not None:
            continue
        if w["norm"]:
            divergencias.append(f"parágrafo {p_idx}: '{w['texto']}' sem tempo próprio (interpolado)")
        antes = next((palavras[k]["fim"] for k in range(i - 1, -1, -1) if palavras[k]["fim"] is not None), 0.0)
        depois = next((palavras[k]["inicio"] for k in range(i + 1, len(palavras)) if palavras[k]["inicio"] is not None), duracao)
        w["inicio"], w["fim"] = antes, max(antes, depois)
    return palavras, divergencias, metodo


def json_legivel(dados: dict) -> str:
    """JSON indentado, uma palavra (e um parágrafo) por linha: diff curto no git."""
    nl = "\n"
    partes = []
    for k, v in dados.items():
        if isinstance(v, list) and v:
            itens = ("," + nl).join("  " + json.dumps(x, ensure_ascii=False) for x in v)
            partes.append(f" {json.dumps(k)}: [{nl}{itens}{nl} ]")
        else:
            partes.append(f" {json.dumps(k)}: {json.dumps(v, ensure_ascii=False)}")
    return "{" + nl + ("," + nl).join(partes) + nl + "}" + nl


def ajustes_eleven(args, taxa: str, estab_padrao: float, estilo_padrao: float) -> dict:
    return {"stability": args.estabilidade if args.estabilidade is not None else estab_padrao,
            "similarity_boost": 0.75,
            "style": args.estilo if args.estilo is not None else estilo_padrao,
            "use_speaker_boost": True,
            "speed": min(1.2, max(0.7, 1 + int(taxa[:-1]) / 100))}


def modo_esteira(args, amb: Ambiente):
    eleven = args.motor == "elevenlabs"
    pasta = Path(args.pasta).resolve()
    roteiro = pasta / "roteiro.md"
    if not roteiro.exists():
        sys.exit(f"não achei {roteiro}")
    paragrafos = ler_paragrafos(roteiro)
    if not paragrafos:
        sys.exit("roteiro.md sem parágrafos")
    elenco = ler_elenco(pasta, args.elenco)
    voz_padrao = args.voz or (VOZ_ELEVEN_PADRAO if eleven else VOZ_EDGE_PADRAO.get(args.lang, VOZ_EDGE_PADRAO["pt"]))
    ajustes = ajustes_eleven(args, args.taxa, 0.45, 0.15)

    dir_audio = pasta / "midia" / "audio"
    manifesto_p = dir_audio / "paragrafos.json"
    manifesto = json.loads(manifesto_p.read_text(encoding="utf-8")) if manifesto_p.exists() else {}
    refazer = set(range(1, len(paragrafos) + 1)) if args.refazer == "*" else {int(x) for x in args.refazer.split(",") if x.strip()}
    orc = Orcamento(Path(args.gasto) if args.gasto else dir_audio / "gasto.json", args.teto)

    unidades = []
    for i, bruto in enumerate(paragrafos, start=1):
        quem, texto = separar_fala(bruto)
        papel = elenco.get(normalizar(quem)) if quem else None
        if quem and elenco and not papel:
            sys.exit(f"parágrafo {i}: '{quem}' não está no elenco")
        if not papel:
            quem, texto = None, bruto
        texto, pausas = separar_pausas(texto)
        voz = (papel or {}).get("voz_elevenlabs" if eleven else "voz", voz_padrao)
        taxa, tom, filtro = (papel or {}).get("taxa", args.taxa), (papel or {}).get("tom", "+0Hz"), (papel or {}).get("filtro")
        # as fórmulas de chave são as dos scripts antigos: o cache de quem já gerou continua valendo
        if eleven:
            chave = sha("elevenlabs", args.modelo, voz, json.dumps(ajustes, sort_keys=True), texto)
        elif tom == "+0Hz" and not papel:
            chave = sha(voz, taxa, texto)
        else:
            chave = sha(voz, taxa, tom, texto)
        mp3 = dir_audio / f"p{i:02d}.mp3"
        reg = manifesto.get(str(i))
        regerar = not (mp3.exists() and reg and reg.get("chave") == chave and i not in refazer)
        unidades.append(dict(i=i, texto=texto, pausas=pausas, voz=voz, taxa=taxa, tom=tom, filtro=filtro, papel=papel,
                             quem=quem, chave=chave, mp3=mp3, reg=reg, regerar=regerar))

    a_gerar = sum(len(u["texto"]) for u in unidades if u["regerar"])
    total_chars = sum(len(u["texto"]) for u in unidades)
    print(f"modo esteira · {len(unidades)} parágrafos · {total_chars} caracteres · motor {args.motor} · voz {voz_padrao}")
    print(f"a gerar agora: {sum(u['regerar'] for u in unidades)} parágrafo(s), {a_gerar} caracteres"
          + (f" (parágrafos {', '.join(str(u['i']) for u in unidades if u['regerar'])})" if a_gerar else " (tudo em cache)"))
    if eleven:
        print(f"créditos estimados: {custo_texto(a_gerar, args.modelo):.0f} · gasto até aqui {orc.total} de {orc.teto} · "
              + ("cabe no teto" if orc.cabe(a_gerar) else "NÃO cabe no teto: a geração seria recusada"))
    else:
        print("custo: zero (edge-tts é gratuito)")
    if args.checar:
        if eleven:
            relatar_conta(amb, voz_padrao)
        return
    if eleven:
        orc.conferir(a_gerar)
        if a_gerar:
            print("voz:", garantir_voz(amb, voz_padrao))

    ffmpeg = amb.ffmpeg()
    dir_audio.mkdir(parents=True, exist_ok=True)
    pcm_total = bytearray()
    silencio = b"\x00\x00" * int(round(args.pausa * TAXA_AMOSTRA))
    todas, divergencias, metodos, resumo = [], [], set(), []
    gasto_agora = 0
    for u in unidades:
        i, mp3 = u["i"], u["mp3"]
        if not u["regerar"]:
            fronteiras, estado = u["reg"]["fronteiras"], "mantido"
        else:
            print(f"  parágrafo {i}: sintetizando...", flush=True)
            if eleven:
                audio, fronteiras = eleven_tts(amb, u["texto"], u["voz"], args.modelo, ajustes)
                gasto_agora += len(u["texto"])
            else:
                audio, fronteiras = edge_tts_sync(u["texto"], u["voz"], u["taxa"], u["tom"])
            mp3.write_bytes(audio)
            versao = (u["reg"] or {}).get("versao", 0) + 1
            manifesto[str(i)] = {"chave": u["chave"], "fronteiras": fronteiras, "versao": versao}
            estado = "gerado"
        pcm = decodificar(ffmpeg, mp3, u["filtro"])
        palavras, div, metodo = alinhar(u["texto"], fronteiras, len(pcm) / 2 / TAXA_AMOSTRA, i)
        cortes = []
        if not args.sem_aparar:
            pcm, cortes = aparar(pcm, args.respiro)
        duracao = len(pcm) / 2 / TAXA_AMOSTRA
        for w in palavras:
            w["inicio"] = min(remapear(w["inicio"], cortes), duracao)
            w["fim"] = min(remapear(w["fim"], cortes), duracao)
        pcm = inserir_pausas(pcm, palavras, u["pausas"], args.pausa_marcada)  # depois de aparar: o corte não come a pausa
        duracao = len(pcm) / 2 / TAXA_AMOSTRA
        deslocamento = len(pcm_total) / 2 / TAXA_AMOSTRA
        metodos.add(metodo)
        divergencias.extend(div)
        for w in palavras:
            w["inicio"], w["fim"] = round(w["inicio"] + deslocamento, 3), round(w["fim"] + deslocamento, 3)
            todas.append(w)
        papel = u["papel"]
        resumo.append({"indice": i, "texto": u["texto"], "fala": (papel or {}).get("id") or (normalizar(u["quem"]) if u["quem"] else None),
                       "quem": (papel or {}).get("nome"), "inicio": round(deslocamento, 3), "fim": round(deslocamento + duracao, 3),
                       "arquivo": f"midia/audio/{mp3.name}", "versao": manifesto[str(i)].get("versao", 1), "estado": estado})
        pcm_total.extend(pcm)
        if i < len(unidades):
            pcm_total.extend(silencio)

    if gasto_agora:
        orc.somar(gasto_agora, modo="esteira", motor="elevenlabs", modelo=args.modelo, pasta=pasta.name)
    manifesto = {k: v for k, v in manifesto.items() if int(k) <= len(unidades)}
    manifesto_p.write_text(json.dumps(manifesto, ensure_ascii=False, indent=1), encoding="utf-8")
    codificar(ffmpeg, bytes(pcm_total), dir_audio / "voz.mp3")
    duracao_total = round(len(pcm_total) / 2 / TAXA_AMOSTRA, 3)

    metodo = "WordBoundary" if metodos == {"WordBoundary"} else "proporcional-silabas"
    for i, w in enumerate(todas):
        w["i"] = i
    timings = {
        "versao": 1,
        "gerado_em": dt.datetime.now().isoformat(timespec="seconds"),
        "fonte": f"elevenlabs {args.modelo} {voz_padrao} {args.taxa}" if eleven else f"edge-tts {voz_padrao} {args.taxa}",
        "metodo": metodo,
        "audio": "midia/audio/voz.mp3",
        "duracao": duracao_total,
        "pausa_entre_paragrafos": args.pausa,
        "respiro_maximo": None if args.sem_aparar else args.respiro,
        "pausa_marcada": args.pausa_marcada,
        "paragrafos": [{k: r[k] for k in ("indice", "inicio", "fim", "texto", *(("fala",) if r["fala"] else ()))} for r in resumo],
        "palavras": [{"i": w["i"], "p": w["p"], "texto": w["texto"], "norm": w["norm"], "inicio": w["inicio"], "fim": w["fim"]} for w in todas],
        "divergencias": divergencias,
    }
    (pasta / "timings.json").write_text(json_legivel(timings), encoding="utf-8")

    linhas = [
        "# Voz", "",
        (f"> Gerada com ElevenLabs (`{args.modelo}`, estabilidade {ajustes['stability']}, estilo {ajustes['style']})." if eleven
         else "> Gerada com edge-tts (voz-guia gratuita)."),
        "",
        f"- Voz: `{voz_padrao}`",
        f"- Taxa: `{args.taxa}`",
        f"- Pausa entre parágrafos: {fmt(args.pausa)}; pausa marcada (`/` no roteiro): {fmt(args.pausa_marcada)}",
        "- Silêncio do serviço: " + ("mantido como veio" if args.sem_aparar else f"bordas aparadas; pausa interna de no máximo {fmt(args.respiro)}"),
        f"- Duração do take: {fmt(duracao_total)}",
        f"- Tempos das palavras: {metodo}" + ("" if metodo == "WordBoundary" else " (**estimativa**: o serviço não devolveu fronteiras de palavra)"),
        f"- Gerado em: {timings['gerado_em']}",
        "- Áudio: `midia/audio/` desta pasta (fora do git)",
        "",
        *([f"- Elenco: " + "; ".join(f"{v['nome']} = `{v['voz']}` {v.get('taxa', '+0%')} {v.get('tom', '+0Hz')}"
                                     + (f" (filtro `{v['filtro']}`)" if v.get("filtro") else "") for v in elenco.values()), ""] if elenco else []),
        "| # | Início | Fim | Versão | Nesta rodada | Texto |",
        "|---|---|---|---|---|---|",
    ]
    for r in resumo:
        linhas.append(f"| {r['indice']} | {fmt(r['inicio'])} | {fmt(r['fim'])} | v{r['versao']} | {r['estado']} | "
                      + (f"**{r['quem']}:** " if r["quem"] else "") + f"{r['texto']} |")
    linhas += ["", "## Divergências (etapa 04)", ""]
    linhas += [f"- {d}" for d in divergencias] or ["- nenhuma"]
    (pasta / "voz.md").write_text("\n".join(linhas) + "\n", encoding="utf-8")

    print(f"take: {dir_audio / 'voz.mp3'} ({duracao_total:.2f} s, {len(todas)} palavras, {metodo}) · gasto {gasto_agora} caracteres")
    if metodo != "WordBoundary":
        print("AVISO: tempos estimados por sílaba; o serviço não devolveu fronteiras de palavra.")
    if divergencias:
        print(f"{len(divergencias)} divergência(s): ver voz.md")


# ---------------------------------------------------------------- modos take e blocos (textos/<idioma>.json)

def achar_blocos(args, base: Path) -> tuple[Path, dict]:
    if args.blocos:
        arq = Path(args.blocos)
    else:
        arq = next((p for p in (base / "textos" / f"v3-{args.lang}.json", base / "textos" / f"{args.lang}.json") if p.exists()), None)
        if not arq:
            sys.exit(f"não achei textos/v3-{args.lang}.json nem textos/{args.lang}.json em {base} (use --blocos ARQUIVO)")
    dados = json.loads(arq.read_text(encoding="utf-8"))
    if not dados.get("blocos"):
        sys.exit(f"{arq} não tem a lista 'blocos' (cada bloco com 'id' e 'texto')")
    return arq, dados


def ponto_de_emenda(texto: str, velhas: list):
    """Índice da primeira frase alterada (começo de frase) e as palavras do texto novo; k == 0 se nada é aproveitável."""
    novas = list(re.finditer(r"\S+", texto))
    k = 0
    while k < min(len(velhas), len(novas)) and velhas[k][0] == novas[k].group():
        k += 1
    while k > 0 and not velhas[k - 1][0].endswith((".", "!", "?")):
        k -= 1
    return k, novas


def emendar(amb: Ambiente, texto: str, pasta: Path, velhas: list, k: int, novas, voz: str, modelo: str, ajustes: dict):
    """Mantém a leitura aprovada até a última frase igual e gera só o resto, emendando no silêncio anterior."""
    corte = (velhas[k - 1][2] + velhas[k][1]) / 2
    pausa = velhas[k][1] - corte
    resto = texto[novas[k].start():]
    audio, cauda_f = eleven_tts(amb, resto, voz, modelo, ajustes, texto[:novas[k].start()].strip()[-300:])
    cauda = palavras_lista(cauda_f)
    lead = max(0.0, cauda[0][1] - pausa)
    (pasta / "completa-anterior.mp3").write_bytes((pasta / "completa.mp3").read_bytes())
    (pasta / "cauda.mp3").write_bytes(audio)
    subprocess.run([amb.ffmpeg(), "-y", "-loglevel", "error", "-i", str(pasta / "completa-anterior.mp3"), "-i", str(pasta / "cauda.mp3"),
                    "-filter_complex", f"[0:a]atrim=0:{corte:.3f},asetpts=PTS-STARTPTS[a];[1:a]atrim=start={lead:.3f},asetpts=PTS-STARTPTS[b];[a][b]concat=n=2:v=0:a=1",
                    "-b:a", "128k", str(pasta / "completa.mp3")], check=True)
    desloc = corte - lead
    return resto, velhas[:k] + [[w, round(a + desloc, 3), round(b + desloc, 3)] for w, a, b in cauda]


def exportar_texto(blocos: list, destino: Path):
    """Texto para colar no ElevenLabs (web) com pausas <break>. Lê dos blocos: 'pausa_depois' (s) e
    'pausas_dentro' ([[trecho, s], ...]: pausa antes de cada trecho). Os modelos multilingual_v2, turbo_v2_5 e
    flash_v2_5 aceitam a tag; o eleven_v3 não."""
    pausa = lambda s: f' <break time="{s}s" /> '  # noqa: E731
    partes = []
    for b in blocos:
        texto = b["texto"]
        for trecho, s in b.get("pausas_dentro", []):
            assert trecho in texto, (b["id"], trecho)
            texto = texto.replace(" " + trecho, pausa(s) + trecho, 1)
        partes.append(texto.strip())
        if b.get("pausa_depois"):
            partes.append(pausa(b["pausa_depois"]).strip())
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text("\n".join(partes) + "\n", encoding="utf-8")
    print("texto com pausas:", destino)


def modo_take(args, amb: Ambiente, base: Path):
    eleven = args.motor == "elevenlabs"
    arq, dados = achar_blocos(args, base)
    blocos = dados["blocos"]
    saida = Path(args.saida) if args.saida else base / "_midia" / "voz" / args.lang
    if args.exportar_texto:
        exportar_texto(blocos, saida / "texto-elevenlabs.txt")
        return
    texto = ("\n\n" if eleven else " ").join(b["texto"] for b in blocos)
    voz = args.voz or (VOZ_ELEVEN_PADRAO if eleven else dados.get("voz_guia") or VOZ_EDGE_PADRAO.get(args.lang, VOZ_EDGE_PADRAO["pt"]))
    ajustes = ajustes_eleven(args, args.taxa, 0.5, 0.1)
    # a assinatura do ElevenLabs é a do voz.py antigo do Presto: quem já gerou não paga de novo
    sig = (hashlib.sha1(json.dumps([args.modelo, voz, ajustes, texto], sort_keys=True).encode("utf-8")).hexdigest() if eleven
           else sha("edge", voz, args.taxa, args.tom, texto))
    orc = Orcamento(Path(args.gasto) if args.gasto else base / "_midia" / "voz" / "gasto.json", args.teto)
    mp3, meta_arq, cache_arq = saida / "completa.mp3", saida / "completa.json", saida / "voz-cache.json"

    def assinatura_gravada():
        for a in (meta_arq, cache_arq):
            if a.exists():
                try:
                    s = json.loads(a.read_text(encoding="utf-8")).get("assinatura")
                    if s:
                        return s
                except json.JSONDecodeError:
                    pass
        return None

    em_cache = mp3.exists() and assinatura_gravada() == sig and not args.refazer
    plano = 0 if em_cache else len(texto)
    modo_emenda = bool(args.emendar and eleven and meta_arq.exists() and mp3.exists() and not em_cache)
    k = novas = velhas = None
    if modo_emenda:
        velhas = json.loads(meta_arq.read_text(encoding="utf-8"))["palavras"]
        k, novas = ponto_de_emenda(texto, velhas)
        if k == 0:
            sys.exit("nada em comum com a narração atual: gere inteira sem --emendar (ou com --refazer)")
        plano = len(texto) - novas[k].start()
    print(f"modo take · {arq.name} · {len(blocos)} blocos · {len(texto)} caracteres · motor {args.motor} · voz {voz}")
    print("cache: " + ("texto igual ao da última geração, nada a gerar (--refazer força)" if em_cache else
          (f"texto mudou; --emendar enviaria só {plano} caracteres (da frase {k} em diante)" if modo_emenda else f"geraria {plano} caracteres")))
    if eleven:
        print(f"créditos estimados: {custo_texto(plano, args.modelo):.0f} · gasto até aqui {orc.total} de {orc.teto} · "
              + ("cabe no teto" if orc.cabe(plano) else "NÃO cabe no teto: a geração seria recusada"))
    else:
        print("custo: zero (edge-tts é gratuito)")
    if args.checar:
        if eleven:
            relatar_conta(amb, voz)
        return
    if em_cache:
        return
    saida.mkdir(parents=True, exist_ok=True)
    if eleven:
        orc.conferir(plano)
        print("voz:", garantir_voz(amb, voz))
    if modo_emenda:
        enviado, palavras = emendar(amb, texto, saida, velhas, k, novas, voz, args.modelo, ajustes)
        gasto_agora = len(enviado)
    elif eleven:
        audio, fronteiras = eleven_tts(amb, texto, voz, args.modelo, ajustes)
        mp3.write_bytes(audio)
        palavras, gasto_agora = palavras_lista(fronteiras), len(texto)
    else:
        audio, fronteiras = edge_tts_sync(texto, voz, args.taxa, args.tom)
        mp3.write_bytes(audio)
        palavras, gasto_agora = palavras_lista(fronteiras), 0
    if gasto_agora:
        orc.somar(gasto_agora, modo="take", lang=args.lang, modelo=args.modelo, assinatura=sig, emenda=modo_emenda)
    meta = {"assinatura": sig, "voz": voz, "motor": args.motor, "palavras": palavras}
    if eleven:
        meta.update({"modelo": args.modelo, "ajustes": ajustes})
    cache_arq.write_text(json.dumps({"assinatura": sig}), encoding="utf-8")
    if palavras:   # sem palavras, o render deve usar o alinhamento por Whisper: não deixe um completa.json vazio
        meta_arq.write_text(json.dumps(meta, ensure_ascii=False, indent=1), encoding="utf-8")
    elif meta_arq.exists():
        meta_arq.unlink()
    print(f"pronto: {mp3} · {len(palavras)} palavras · gasto desta rodada {gasto_agora} caracteres, total {orc.total} de {orc.teto}")


def modo_blocos(args, amb: Ambiente, base: Path):
    eleven = args.motor == "elevenlabs"
    arq, dados = achar_blocos(args, base)
    blocos = dados["blocos"]
    saida = Path(args.saida) if args.saida else base / "_midia" / "voz" / args.lang
    if args.exportar_texto:
        exportar_texto(blocos, saida / "texto-elevenlabs.txt")
        return
    voz = args.voz or (VOZ_ELEVEN_PADRAO if eleven else dados.get("voz_guia") or VOZ_EDGE_PADRAO.get(args.lang, VOZ_EDGE_PADRAO["pt"]))
    ajustes = ajustes_eleven(args, args.taxa, 0.5, 0.1)
    orc = Orcamento(Path(args.gasto) if args.gasto else base / "_midia" / "voz" / "gasto.json", args.teto)
    manifesto_p = saida / "blocos.json"
    manifesto = json.loads(manifesto_p.read_text(encoding="utf-8")) if manifesto_p.exists() else {}
    refazer = {b["id"] for b in blocos} if args.refazer == "*" else {x.strip() for x in args.refazer.split(",") if x.strip()}
    plano = []
    for b in blocos:
        texto = b["texto"]
        chave = (sha("elevenlabs", args.modelo, voz, json.dumps(ajustes, sort_keys=True), texto) if eleven
                 else sha("edge", voz, args.taxa, args.tom, texto))
        mp3 = saida / f"{b['id']}.mp3"
        reg = manifesto.get(b["id"])
        regerar = not (mp3.exists() and reg and reg.get("chave") == chave and b["id"] not in refazer)
        plano.append((b["id"], texto, chave, mp3, regerar))
    a_gerar = sum(len(t) for _, t, _, _, r in plano if r)
    print(f"modo blocos · {arq.name} · {len(blocos)} blocos · motor {args.motor} · voz {voz}")
    print(f"a gerar: {sum(r for *_, r in plano)} bloco(s), {a_gerar} caracteres" + (f" ({', '.join(i for i, _, _, _, r in plano if r)})" if a_gerar else " (tudo em cache)"))
    if eleven:
        print(f"créditos estimados: {custo_texto(a_gerar, args.modelo):.0f} · gasto até aqui {orc.total} de {orc.teto} · "
              + ("cabe no teto" if orc.cabe(a_gerar) else "NÃO cabe no teto: a geração seria recusada"))
    else:
        print("custo: zero (edge-tts é gratuito)")
    if args.checar:
        if eleven:
            relatar_conta(amb, voz)
        return
    if not any(r for *_, r in plano):
        return
    saida.mkdir(parents=True, exist_ok=True)
    if eleven:
        orc.conferir(a_gerar)
        if a_gerar:
            print("voz:", garantir_voz(amb, voz))
    gasto_agora = 0
    for bid, texto, chave, mp3, regerar in plano:
        if not regerar:
            continue
        print(f"  bloco {bid}: sintetizando...", flush=True)
        if eleven:
            audio, fronteiras = eleven_tts(amb, texto, voz, args.modelo, ajustes)
            gasto_agora += len(texto)
        else:
            audio, fronteiras = edge_tts_sync(texto, voz, args.taxa, args.tom)
        mp3.write_bytes(audio)
        manifesto[bid] = {"chave": chave, "palavras": palavras_lista(fronteiras)}
    if gasto_agora:
        orc.somar(gasto_agora, modo="blocos", lang=args.lang, modelo=args.modelo)
    manifesto_p.write_text(json.dumps(manifesto, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"pronto: {saida} · gasto desta rodada {gasto_agora} caracteres, total {orc.total} de {orc.teto}")


# ---------------------------------------------------------------- linha de comando

def main():
    ap = argparse.ArgumentParser(description="Narração com edge-tts (gratuito) ou ElevenLabs; veja o README.md ao lado.")
    ap.add_argument("pasta", nargs="?", help="modo esteira: pasta do vídeo, com roteiro.md")
    ap.add_argument("--modo", choices=["esteira", "take", "blocos"], help="padrão: esteira se vier pasta, take se não")
    ap.add_argument("--motor", choices=["edge", "elevenlabs"], default="edge", help="serviço de voz (padrão edge, gratuito)")
    ap.add_argument("--voz", help="voz do edge-tts (ex.: pt-BR-AntonioNeural) ou ID da voz no ElevenLabs")
    ap.add_argument("--modelo", default=MODELO_PADRAO, help=f"modelo do ElevenLabs (padrão {MODELO_PADRAO})")
    ap.add_argument("--estabilidade", type=float, help="ElevenLabs, 0 a 1 (padrão 0,45 na esteira, 0,5 em take/blocos)")
    ap.add_argument("--estilo", type=float, help="ElevenLabs, 0 a 1 (padrão 0,15 na esteira, 0,1 em take/blocos)")
    ap.add_argument("--taxa", default="+0%", help="velocidade, ex.: +8%% ou -5%%")
    ap.add_argument("--tom", default="+0Hz", help="edge-tts: tom, ex.: -8Hz")
    ap.add_argument("--lang", default="pt", help="idioma (nomeia textos/<idioma>.json e a pasta de saída; padrão pt)")
    ap.add_argument("--checar", action="store_true", help="não gasta nada: mostra o plano, o custo estimado e a conta")
    ap.add_argument("--teto", type=int, default=int(os.environ.get("VOZ_TETO", TETO_PADRAO)),
                    help=f"teto de caracteres ElevenLabs somados em gasto.json (padrão {TETO_PADRAO} ou VOZ_TETO)")
    ap.add_argument("--gasto", help="caminho do gasto.json (padrão: ao lado da saída)")
    ap.add_argument("--refazer", nargs="?", const="*", default="",
                    help="esteira: parágrafos a regerar (ex.: 2,3); blocos: ids; take: sem valor força a geração inteira")
    ap.add_argument("--env", help="arquivo .env com ELEVENLABS_API_KEY (alternativa à variável de ambiente)")
    # take e blocos
    ap.add_argument("--base", help="pasta do projeto (padrão: a do script, se tiver textos/, senão a atual)")
    ap.add_argument("--blocos", help="JSON com a lista 'blocos' (padrão: textos/v3-<idioma>.json ou textos/<idioma>.json)")
    ap.add_argument("--saida", help="pasta de saída (padrão: <base>/_midia/voz/<idioma>)")
    ap.add_argument("--emendar", action="store_true", help="take, ElevenLabs: refaz só da primeira frase alterada em diante")
    ap.add_argument("--exportar-texto", action="store_true", help="só grava texto-elevenlabs.txt com pausas <break>; não chama API")
    # esteira
    ap.add_argument("--pausa", type=float, default=0.30, help="esteira: silêncio entre parágrafos, em segundos")
    ap.add_argument("--respiro", type=float, default=0.32, help="esteira: maior silêncio dentro do parágrafo; o que passar é encurtado")
    ap.add_argument("--pausa-marcada", type=float, default=0.25, help="esteira: silêncio de cada `/` do roteiro; `//` dobra")
    ap.add_argument("--elenco", help="esteira: elenco.json (padrão: o do canal, se existir)")
    ap.add_argument("--sem-aparar", action="store_true", help="esteira: não mexe no silêncio que o serviço devolve")
    args = ap.parse_args()
    for fluxo in (sys.stdout, sys.stderr):
        try:
            fluxo.reconfigure(encoding="utf-8")
        except Exception:
            pass
    if not re.fullmatch(r"[+-]\d+%", args.taxa):
        sys.exit("--taxa deve ser no formato +8% ou -5%")
    modo = args.modo or ("esteira" if args.pasta else "take")
    if modo == "esteira" and not args.pasta:
        sys.exit("o modo esteira precisa da pasta do vídeo: voz.py <pasta>")
    if modo == "take" and args.refazer == "*":
        args.refazer = "tudo"
    base = Path(args.base).resolve() if args.base else (SCRIPT if (SCRIPT / "textos").is_dir() else Path.cwd())
    dirs = [Path(args.pasta).resolve()] if args.pasta else []
    dirs += [base, Path.cwd().resolve(), SCRIPT]
    amb = Ambiente(args.env, dirs)
    if args.motor == "elevenlabs" and not args.checar and not args.exportar_texto:
        amb.exigir_chave()
    if modo == "esteira":
        modo_esteira(args, amb)
    elif modo == "take":
        modo_take(args, amb, base)
    else:
        modo_blocos(args, amb, base)


if __name__ == "__main__":
    main()
