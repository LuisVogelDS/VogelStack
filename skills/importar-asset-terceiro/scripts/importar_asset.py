#!/usr/bin/env python3
"""Importa asset de terceiro para um projeto Unity sem abrir o editor. Unifica o extrair_unitypackage.py do Slime,
o importar_pacote.py do Fang You Very Much e o promover_acervo.py do GobbleGoblin.

O pacote é dado não confiável: nada dele é executado, só lido e copiado como arquivo (rode com `python -I`).
Cada subcomando descobre o projeto subindo da pasta atual até achar ProjectSettings/ (ou use --projeto).

  licenca  FORNECEDOR [PACOTE]          confere a LICENCAS.md da pasta única (sai 0 só se "sim")
  lista    PACOTE [FILTRO]              caminhos dentro do .unitypackage
  pacote   FORNECEDOR PACOTE...         extrai inteiro para Assets/AssetDump/<FORNECEDOR>/ (com .meta, GUIDs preservados)
             [--sem-scripts] [--com-demo] [--sobrescrever] [--max-mb N]
  recorte  PACOTE PREFIXO DESTINO RAIZ...   extrai só RAIZ... e o que elas referenciam por GUID
             (PREFIXO: trecho do caminho do pacote; DESTINO: relativo ao projeto; RAIZ termina em "/" = pasta inteira)
  acervo   [AUTOR/PACK] [--nome N]      sem argumento lista a pasta única; com argumento copia o pack para o AssetDump
  origem   PASTA ORIGEM LICENCA O_QUE_VEIO   imprime a linha pronta do ORIGENS.md
  conferir                              pastas do AssetDump sem menção em ORIGENS*.md

Todos aceitam --dry-run (não escrevem) e --projeto CAMINHO. Saídas: 0 ok, 1 uso/erro, 2 licença barra, 3 sem linha na licença.
"""
import argparse
import json
import os
import re
import shutil
import sys
import tarfile

GUID = re.compile(rb"guid: ([0-9a-f]{32})")
TEXTO = (".prefab", ".mat", ".asset", ".controller", ".anim", ".overrideController")
SCRIPTS = (".cs", ".asmdef", ".unity")
BINARIOS = (".dll", ".so", ".dylib", ".bundle", ".a", ".exe")
FORA_ACERVO = ("__macosx", "library", "logs", "packages", "projectsettings", "usersettings", "obj", "gltf", "glb", "blends", "blend", "source")
MODELO, TEXTURA, DOCS = (".fbx",), (".png", ".jpg", ".jpeg", ".tga", ".psd"), (".txt", ".md", ".pdf")
AUTORES_FORA = {"Sonniss", "Sonniss GDC2024", "Blender models"}   # áudio e trabalho nosso: não são packs 3D de terceiros


# ---------- projeto e caminhos ----------

def achar_projeto(explicito=None):
    d = os.path.abspath(explicito or os.getcwd())
    while not os.path.isdir(os.path.join(d, "ProjectSettings")):
        if os.path.dirname(d) == d:
            sys.exit("não achei um projeto Unity (ProjectSettings/) subindo da pasta atual; use --projeto")
        d = os.path.dirname(d)
    return d


def dentro(base, alvo):
    base, alvo = os.path.normpath(base), os.path.normpath(alvo)
    return os.path.commonpath([base, alvo]) == base


def caminho_seguro(rel):
    """Caminho de pacote (Assets/...) sem '..', sem raiz e sem unidade; None se não presta."""
    rel = rel.replace("\\", "/").strip()
    if not rel.startswith("Assets/") or ".." in rel.split("/") or ":" in rel or rel.startswith("/"):
        return None
    return rel


def pasta_acervo():
    for c in (os.environ.get("ACERVO_ASSETS_DIR"), os.environ.get("TATUACU_EXTRAIDOS"),
              os.path.join(os.path.expanduser("~"), "Documents", "GameDev", "Assets")):
        if c and os.path.isdir(c):
            return c
    return None


def aviso_unity_aberto(raiz):
    if os.path.exists(os.path.join(raiz, "Temp", "UnityLockfile")):
        print("aviso: Temp/UnityLockfile existe; se o editor está aberto neste projeto, feche-o antes de importar "
              "(trava órfã de um Unity que caiu também deixa o arquivo).", file=sys.stderr)


# ---------- licença ----------

def achar_licencas():
    for c in (os.environ.get("ACERVO_LICENCAS"),
              os.path.join(pasta_acervo() or "", "LICENCAS.md")):
        if c and os.path.isfile(c):
            return c
    return None


def _norm(s):
    return re.sub(r"[^a-z0-9]", "", s.lower())


def ler_licencas(caminho):
    linhas = []
    with open(caminho, encoding="utf-8") as fh:
        for l in fh:
            if not l.startswith("|"):
                continue
            c = [x.strip() for x in l.strip().strip("|").split("|")]
            if len(c) >= 5 and c[0] != "Fornecedor" and not set(c[0]) <= set("-: "):
                linhas.append(dict(fornecedor=c[0], pacote=c[1], licenca=c[2], fonte=c[3], entra=c[4], obs=c[5] if len(c) > 5 else ""))
    return linhas


def cmd_licenca(a):
    caminho = achar_licencas()
    if not caminho:
        print("LICENCAS.md não encontrada (pasta única de assets: defina ACERVO_ASSETS_DIR ou ACERVO_LICENCAS). "
              "Sem ela não há como provar a licença: peça ao dono do acervo.")
        return 3
    forn = _norm(a.fornecedor)
    casam = [r for r in ler_licencas(caminho) if forn and (forn in _norm(r["fornecedor"]) or _norm(r["fornecedor"]) in forn)]
    if a.pacote:
        pac = _norm(os.path.splitext(os.path.basename(a.pacote))[0])
        estreito = [r for r in casam if _norm(r["pacote"]) and (_norm(r["pacote"]) in pac or pac in _norm(r["pacote"]))]
        casam = estreito or casam
    if not casam:
        print(f"sem linha para {a.fornecedor!r}{' / ' + a.pacote if a.pacote else ''} em {caminho}: "
              "licença não registrada, não importe; registre no acervo primeiro.")
        return 3
    for r in casam:
        print(f"{r['fornecedor']} / {r['pacote']}: {r['licenca']} | entra: {r['entra']}" + (f" | {r['obs']}" if r["obs"] else ""))
    entra = [r["entra"].lower() for r in casam]
    if all(e.startswith("sim") for e in entra):
        if any("só em repositório privado" in e or "privado" in e for e in entra):
            print("atenção: 'sim' só em repositório privado; confira se este repo é privado.")
        return 0
    print("BARRADO: nem toda linha tem 'sim' na coluna 'Entra'. Não importe sem decisão do dono (\"a confirmar\" e \"não\" ficam de fora).")
    return 2


# ---------- unitypackage ----------

def indexar(pacote):
    """guid -> caminho, lendo só os membros 'pathname' (pequenos)."""
    mapa = {}
    with tarfile.open(pacote, "r:gz") as t:
        for m in t:
            partes = m.name.replace("\\", "/").strip("./").split("/")
            if m.isfile() and len(partes) == 2 and partes[1] == "pathname" and m.size < 4096:
                mapa[partes[0]] = t.extractfile(m).read().decode("utf-8", "replace").splitlines()[0].strip()
    return mapa


def cmd_lista(a):
    filtro = a.filtro or ""
    for caminho in sorted(indexar(a.pacote).values()):
        if filtro in caminho:
            print(caminho)
    return 0


def _gravar(t, m, destino, dry):
    if dry:
        return m.size
    os.makedirs(os.path.dirname(destino), exist_ok=True)
    with open(destino, "wb") as f:
        shutil.copyfileobj(t.extractfile(m), f)
    return m.size


def cmd_pacote(a):
    raiz = achar_projeto(a.projeto)
    aviso_unity_aberto(raiz)
    base = os.path.join(raiz, "Assets", "AssetDump", a.fornecedor)
    limite = a.max_mb * 1048576
    r = cmd_licenca(argparse.Namespace(fornecedor=a.fornecedor, pacote=a.pacotes[0]))
    if r != 0 and not a.dry_run:
        if not a.ignorar_licenca:
            print("importação interrompida pela licença (use --ignorar-licenca só se o dono já liberou por outro meio).")
            return r
    for pacote in a.pacotes:
        mapa = indexar(pacote)
        alvo_de, pulados = {}, {}
        for guid, rel in mapa.items():
            seguro = caminho_seguro(rel)
            if seguro is None:
                pulados[rel] = "fora de Assets/ ou caminho suspeito"
                continue
            r = seguro[len("Assets/"):]
            if r.endswith(".unitypackage") or "/Render_Pipeline_Convert/" in r:
                pulados[rel] = "conversor de pipeline"
                continue
            if not a.com_demo and ("/Scenes/" in r or "/Demo" in r):
                pulados[rel] = "cena/demonstração (--com-demo mantém)"
                continue
            if a.sem_scripts and r.endswith(SCRIPTS):
                pulados[rel] = "script/cena de demonstração (--sem-scripts)"
                continue
            if r.lower().startswith(a.fornecedor.lower() + "/"):
                r = r[len(a.fornecedor) + 1:]   # Assets/ithappy/... -> AssetDump/ithappy/..., não ithappy/ithappy
            alvo = os.path.normpath(os.path.join(base, r))
            if not dentro(base, alvo):
                pulados[rel] = "escapa do destino"
                continue
            alvo_de[guid] = alvo
        gravados = existentes = grandes = 0
        bytes_ = 0
        topos, scripts, binarios = set(), [], []
        with tarfile.open(pacote, "r:gz") as t:
            for m in t:
                partes = m.name.replace("\\", "/").strip("./").split("/")
                if not m.isfile() or len(partes) != 2 or partes[0] not in alvo_de or partes[1] not in ("asset", "asset.meta"):
                    continue
                destino = alvo_de[partes[0]] + (".meta" if partes[1] == "asset.meta" else "")
                if os.path.exists(destino) and not a.sobrescrever:
                    existentes += 1
                    continue
                if m.size > limite:
                    grandes += 1
                    print(f"  pulado (>{a.max_mb} MB): {os.path.relpath(destino, raiz)}")
                    continue
                bytes_ += _gravar(t, m, destino, a.dry_run)
                gravados += 1
                if partes[1] == "asset":
                    topos.add(os.path.relpath(destino, base).split(os.sep)[0])
                    if destino.lower().endswith(".cs"):
                        scripts.append(destino)
                    elif destino.lower().endswith(BINARIOS):
                        binarios.append(destino)
            # pastas vazias do pacote (só pathname + meta): garante a pasta, o .meta já veio acima
            for guid, alvo in alvo_de.items():
                if not a.dry_run and not os.path.exists(alvo) and os.path.exists(alvo + ".meta"):
                    os.makedirs(alvo, exist_ok=True)
        modo = "(dry-run) " if a.dry_run else ""
        print(f"{modo}{os.path.basename(pacote)}: {gravados} arquivos, {bytes_ / 1048576:.1f} MB em Assets/AssetDump/{a.fornecedor}/"
              f"{{{', '.join(sorted(topos))}}}; já existiam {existentes}; pulados por regra {len(pulados)}; grandes demais {grandes}")
        if scripts or binarios:
            print(f"  REVISAR: {len(scripts)} scripts .cs e {len(binarios)} binários nativos vieram de terceiro e rodam no editor/build. "
                  "Leia os scripts (ou reimporte com --sem-scripts) e desconfie de .dll/.so sem fonte.")
    print(f"\nPróximo passo: linha no ORIGENS.md ->  python -I importar_asset.py origem \"{a.fornecedor}/<pack>/\" \"<origem>\" \"<licença>\" \"<o que veio>\"")
    print("Depois: abrir o projeto (pela fila) para importar e conferir o log sem erro.")
    return 0


def cmd_recorte(a):
    raiz = achar_projeto(a.projeto)
    aviso_unity_aberto(raiz)
    prefixo = a.prefixo.rstrip("/")
    destino = a.destino.replace("\\", "/").rstrip("/")
    if not caminho_seguro(destino + "/x") or not dentro(os.path.join(raiz, "Assets"), os.path.join(raiz, destino)):
        print("DESTINO precisa ficar dentro de Assets/ do projeto")
        return 1
    mapa = indexar(a.pacote)
    por_caminho = {c: g for g, c in mapa.items()}
    raiz_guids = set()
    for r in a.raizes:
        cheio = prefixo + "/" + r
        for c, g in por_caminho.items():
            if (r.endswith("/") and c.startswith(cheio)) or c == cheio:
                raiz_guids.add(g)
    if not raiz_guids:
        print("nenhuma RAIZ casou com o pacote; confira com o subcomando lista")
        return 1
    conteudo = {}
    with tarfile.open(a.pacote, "r:gz") as t:
        for m in t:
            partes = m.name.replace("\\", "/").strip("./").split("/")
            if m.isfile() and len(partes) == 2 and partes[1] == "asset" and mapa.get(partes[0], "").endswith(TEXTO) and m.size < 20_000_000:
                conteudo[partes[0]] = t.extractfile(m).read()
    fecho, fila = set(), list(raiz_guids)
    while fila:
        g = fila.pop()
        if g in fecho or g not in mapa:
            continue
        fecho.add(g)
        fila += [ref.decode() for ref in GUID.findall(conteudo.get(g, b""))]
    novos, ja, fora = {}, [], []
    for g in sorted(fecho, key=lambda x: mapa[x]):
        if not mapa[g].startswith(prefixo):
            fora.append(mapa[g])
            continue
        d = os.path.normpath(os.path.join(raiz, destino + mapa[g][len(prefixo):]))
        if not dentro(os.path.join(raiz, "Assets"), d):
            fora.append(mapa[g])
        elif os.path.exists(d):
            ja.append(d)
        else:
            novos[g] = d
    print(f"fecho: {len(fecho)} assets; novos {len(novos)}; já existem {len(ja)}; fora do prefixo {len(fora)}")
    for f in fora:
        print("  FORA:", f)
    if a.dry_run:
        for d in novos.values():
            print("  novo:", os.path.relpath(d, raiz))
        return 0
    # pastas ancestrais ainda inexistentes: leva só o .meta (GUID original); a pasta o disco cria
    base = os.path.normpath(os.path.join(raiz, destino))
    solo_meta = {}
    for d in novos.values():
        pai = os.path.dirname(d)
        while dentro(base, pai) and pai != base:
            g = por_caminho.get(prefixo + pai[len(base):].replace(os.sep, "/"))
            if g and not os.path.exists(pai + ".meta"):
                solo_meta[g] = pai
            pai = os.path.dirname(pai)
    tot = 0
    with tarfile.open(a.pacote, "r:gz") as t:
        for m in t:
            partes = m.name.replace("\\", "/").strip("./").split("/")
            if not m.isfile() or len(partes) != 2:
                continue
            guid, nome = partes
            if guid in solo_meta and nome == "asset.meta":
                _gravar(t, m, solo_meta[guid] + ".meta", False)
            if guid in novos and nome in ("asset", "asset.meta"):
                tot += _gravar(t, m, novos[guid] + (".meta" if nome == "asset.meta" else ""), False)
    print(f"copiados {len(novos)} assets, {tot / 1048576:.2f} MB")
    return 0


# ---------- acervo (pasta única) ----------

def _planejar_acervo(origem):
    plano = []
    for dp, dn, fn in os.walk(origem):
        rel = os.path.relpath(dp, origem)
        if any(p.lower() in FORA_ACERVO for p in rel.split(os.sep) if p != "."):
            continue
        for f in fn:
            if f.lower().endswith(MODELO + TEXTURA + DOCS):
                plano.append((os.path.join(dp, f), rel if rel != "." else ""))
    return plano


def cmd_acervo(a):
    raiz = achar_projeto(a.projeto)
    acervo = pasta_acervo()
    if not acervo:
        print("pasta única de assets não encontrada (defina ACERVO_ASSETS_DIR)")
        return 1
    dump = os.path.join(raiz, "Assets", "AssetDump")
    if not a.pack:
        ja = {f"{au}/{sub}".lower() for au in (os.listdir(dump) if os.path.isdir(dump) else []) if os.path.isdir(os.path.join(dump, au))
              for sub in os.listdir(os.path.join(dump, au))}
        print(f"Acervo em {acervo}\n")
        for autor in sorted(os.listdir(acervo)):
            pa = os.path.join(acervo, autor)
            if not os.path.isdir(pa) or autor.startswith((".", "_")) or autor in AUTORES_FORA:
                continue
            for pack in sorted(os.listdir(pa)):
                if os.path.isdir(os.path.join(pa, pack)):
                    print(f"  {autor}/{pack}" + ("  [já no jogo]" if f"{autor}/{pack}".lower() in ja else ""))
        return 0
    autor, _, pack = a.pack.replace("\\", "/").partition("/")
    origem = os.path.join(acervo, autor, pack)
    if not pack or not os.path.isdir(origem):
        print(f"não achei no acervo: {origem}")
        return 1
    r = cmd_licenca(argparse.Namespace(fornecedor=autor, pacote=pack))
    if r != 0:
        return r
    nome = a.nome or pack
    destino = os.path.join(dump, autor, nome)
    if os.path.exists(destino):
        print(f"JÁ EXISTE no AssetDump: {autor}/{nome}; nada a fazer")
        return 1
    plano = _planejar_acervo(origem)
    if not plano:
        print(f"nada para levar em {origem} (sem FBX/textura fora das pastas ignoradas)")
        return 1
    print(f"{a.pack} -> Assets/AssetDump/{autor}/{nome}: {len(plano)} arquivos, {sum(os.path.getsize(s) for s, _ in plano) / 2**20:.1f} MB")
    if a.dry_run:
        for s, sub in plano[:20]:
            print("   ", os.path.join(sub, os.path.basename(s)))
        return 0
    for src, sub in plano:
        dst = os.path.join(destino, sub, os.path.basename(src))
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy2(src, dst)   # sem .meta: o do espelho é local; o Unity gera os do AssetDump
    print("copiado. Próximo: a linha do ORIGENS.md (subcomando origem), com autor e licença da LICENCAS.md.")
    return 0


# ---------- ORIGENS.md ----------

def cmd_origem(a):
    pasta = a.pasta.strip("/")
    print(f"| `{pasta}/` | {a.origem} | {a.licenca} | {a.o_que_veio} |")
    print("\n(cole na tabela certa do Assets/AssetDump/ORIGENS.md, na ordem das colunas daquele arquivo)", file=sys.stderr)
    return 0


def cmd_conferir(a):
    raiz = achar_projeto(a.projeto)
    dump = os.path.join(raiz, "Assets", "AssetDump")
    texto = ""
    for f in os.listdir(dump) if os.path.isdir(dump) else []:
        if f.upper().startswith("ORIGENS") and f.lower().endswith(".md"):
            with open(os.path.join(dump, f), encoding="utf-8") as fh:
                texto += fh.read().lower().replace("\\", "/")
    falta = []
    for au in sorted(os.listdir(dump)):
        p = os.path.join(dump, au)
        if not os.path.isdir(p):
            continue
        if f"{au.lower()}/" in texto and f"`{au.lower()}/`" in texto:
            continue   # o fornecedor inteiro está listado de uma vez
        subs = [s for s in sorted(os.listdir(p)) if os.path.isdir(os.path.join(p, s))] or [""]
        for s in subs:
            chave = (f"{au}/{s}" if s else au).lower()
            if chave not in texto:
                falta.append(chave)
    if falta:
        print("sem menção no ORIGENS*.md:")
        for f in falta:
            print("  ", f)
        return 1
    print("todas as pastas do AssetDump têm menção no ORIGENS*.md")
    return 0


def main():
    for fluxo in (sys.stdout, sys.stderr):
        if hasattr(fluxo, "reconfigure"):
            fluxo.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    def comum(p):
        p.add_argument("--projeto", default=None)
        p.add_argument("--dry-run", action="store_true")
        return p
    p = comum(sub.add_parser("licenca")); p.add_argument("fornecedor"); p.add_argument("pacote", nargs="?"); p.set_defaults(f=cmd_licenca)
    p = comum(sub.add_parser("lista")); p.add_argument("pacote"); p.add_argument("filtro", nargs="?"); p.set_defaults(f=cmd_lista)
    p = comum(sub.add_parser("pacote")); p.add_argument("fornecedor"); p.add_argument("pacotes", nargs="+")
    p.add_argument("--sem-scripts", action="store_true"); p.add_argument("--com-demo", action="store_true")
    p.add_argument("--sobrescrever", action="store_true"); p.add_argument("--max-mb", type=int, default=500)
    p.add_argument("--ignorar-licenca", action="store_true"); p.set_defaults(f=cmd_pacote)
    p = comum(sub.add_parser("recorte")); p.add_argument("pacote"); p.add_argument("prefixo"); p.add_argument("destino")
    p.add_argument("raizes", nargs="+"); p.set_defaults(f=cmd_recorte)
    p = comum(sub.add_parser("acervo")); p.add_argument("pack", nargs="?"); p.add_argument("--nome"); p.set_defaults(f=cmd_acervo)
    p = comum(sub.add_parser("origem")); p.add_argument("pasta"); p.add_argument("origem"); p.add_argument("licenca")
    p.add_argument("o_que_veio"); p.set_defaults(f=cmd_origem)
    p = comum(sub.add_parser("conferir")); p.set_defaults(f=cmd_conferir)
    a = ap.parse_args()
    return a.f(a)


if __name__ == "__main__":
    sys.exit(main())
