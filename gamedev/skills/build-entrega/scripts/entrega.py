#!/usr/bin/env python3
"""Apoio à entrega de uma build Unity: zip datado para colegas e linha do docs/builds.md.

  zip    [PASTA_DA_BUILD] [--nome Jogo] [--saida PASTA]   empacota a build em <Nome>-AAAA-MM-DD-HHMM-<commit>.zip
  linha  --versao vX.Y --notas "o que mudou" [--anexar docs/builds.md]   linha da tabela de builds (ou a acrescenta)
  achar                                                   mostra o .exe de build mais novo do projeto

O projeto é achado subindo da pasta atual até ProjectSettings/ (ou --projeto). Sem PASTA_DA_BUILD, vale a pasta do .exe
mais novo em Builds/. Nada aqui commita nem empurra. Saída: 0 ok, 1 erro de uso, 2 build suspeita (use --forcar).
"""
import argparse
import datetime
import os
import re
import subprocess
import sys
import zipfile

SEM_JANELA = getattr(subprocess, "CREATE_NO_WINDOW", 0)
# lixo de build do Unity que não vai para colega: símbolos do Burst, backup do IL2CPP, logs e dumps de crash
EXCLUI_PASTAS = ("_BurstDebugInformation_DoNotShip", "_BackUpThisFolder_ButDontShipItWithYourGame", "Logs", "crashes")
EXCLUI_EXT = (".pdb", ".log", ".dmp")
EXCLUI_NOMES = ("UnityCrashHandler64.exe", "UnityCrashHandler32.exe")   # o jogo roda sem; só pesa
SEGREDOS = (".env", ".pem", ".key", "credentials.json", "secrets.json")


def achar_projeto(explicito=None):
    d = os.path.abspath(explicito or os.getcwd())
    while not os.path.isdir(os.path.join(d, "ProjectSettings")):
        if os.path.dirname(d) == d:
            sys.exit("não achei um projeto Unity (ProjectSettings/) subindo da pasta atual; use --projeto")
        d = os.path.dirname(d)
    return d


def git(raiz, *args):
    try:
        r = subprocess.run(["git", "-C", raiz, *args], capture_output=True, text=True, errors="replace", creationflags=SEM_JANELA)
        return r.stdout.strip() if r.returncode == 0 else ""
    except OSError:
        return ""


def exe_mais_novo(raiz):
    melhor = None
    for dp, dn, fn in os.walk(os.path.join(raiz, "Builds")):
        dn[:] = [d for d in dn if not d.endswith(EXCLUI_PASTAS[:2]) and d not in ("Entregas",)]
        for f in fn:
            if f.lower().endswith(".exe") and f not in EXCLUI_NOMES:
                p = os.path.join(dp, f)
                if melhor is None or os.path.getmtime(p) > os.path.getmtime(melhor):
                    melhor = p
    return melhor


def cmd_achar(a):
    exe = exe_mais_novo(achar_projeto(a.projeto))
    if not exe:
        print("nenhum .exe em Builds/ (gere a build pela fila primeiro)")
        return 1
    print(exe, datetime.datetime.fromtimestamp(os.path.getmtime(exe)).strftime("(%d/%m/%Y %H:%M)"))
    return 0


def cmd_zip(a):
    raiz = achar_projeto(a.projeto)
    pasta = os.path.abspath(a.pasta) if a.pasta else (os.path.dirname(exe_mais_novo(raiz) or "") or None)
    if not pasta or not os.path.isdir(pasta):
        print("sem pasta de build: passe PASTA_DA_BUILD ou gere a build em Builds/")
        return 1
    exes = [f for f in os.listdir(pasta) if f.lower().endswith(".exe") and f not in EXCLUI_NOMES]
    if not exes:
        print(f"{pasta} não tem .exe; não é uma build do Windows")
        return 1
    nome = a.nome or os.path.splitext(exes[0])[0]
    commit = git(raiz, "rev-parse", "--short", "HEAD") or "semgit"
    sujo = bool(git(raiz, "status", "--porcelain", "--", "Assets", "ProjectSettings", "Packages"))
    suspeitas = []
    if sujo:
        suspeitas.append("há mudança sem commit em Assets/ProjectSettings/Packages: a build pode não ser a do commit " + commit)
    t_exe = os.path.getmtime(os.path.join(pasta, exes[0]))
    t_commit = git(raiz, "log", "-1", "--format=%ct")
    if t_commit.isdigit() and t_exe < int(t_commit):
        suspeitas.append("o .exe é mais velho que o último commit: gere a build de novo")
    arquivos = []
    for dp, dn, fn in os.walk(pasta):
        dn[:] = [d for d in dn if not d.endswith(EXCLUI_PASTAS[:2]) and d not in EXCLUI_PASTAS[2:]]
        for f in fn:
            if f.lower().endswith(EXCLUI_EXT) or f in EXCLUI_NOMES:
                continue
            if f.lower() in SEGREDOS or f.lower().endswith((".pem", ".key")):
                suspeitas.append(f"arquivo com cara de segredo na build: {os.path.relpath(os.path.join(dp, f), pasta)}")
                continue
            arquivos.append(os.path.join(dp, f))
    for s in suspeitas:
        print("aviso:", s)
    if suspeitas and not a.forcar:
        print("não zipei; corrija ou rode com --forcar se for de propósito")
        return 2
    saida = os.path.abspath(a.saida) if a.saida else os.path.join(raiz, "Builds", "Entregas")
    zname = f"{nome}-{datetime.datetime.now().strftime('%Y-%m-%d-%H%M')}-{commit}.zip"
    destino = os.path.join(saida, zname)
    total = sum(os.path.getsize(f) for f in arquivos)
    print(f"{len(arquivos)} arquivos, {total / 1048576:.0f} MB -> {destino}")
    if a.dry_run:
        return 0
    os.makedirs(saida, exist_ok=True)
    with zipfile.ZipFile(destino, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        for f in arquivos:
            z.write(f, os.path.join(nome, os.path.relpath(f, pasta)))   # dentro do zip: <Nome>/<arquivos>, para não espalhar na pasta de quem abre
    print(f"zip pronto: {os.path.getsize(destino) / 1048576:.0f} MB. A pasta Builds/ é fora do git; mande por fora do repositório.")
    return 0


def cmd_linha(a):
    raiz = achar_projeto(a.projeto)
    commit = git(raiz, "rev-parse", "--short", "HEAD") or "?"
    data = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
    notas = a.notas.replace("|", "/").replace("\n", " ").strip()
    linha = f"| {a.versao} | {data} | {commit} | {notas} |"
    print(linha)
    if not a.anexar:
        return 0
    alvo = a.anexar if os.path.isabs(a.anexar) else os.path.join(raiz, a.anexar)
    if not os.path.isfile(alvo):
        print(f"{alvo} não existe; crie o docs/builds.md com a tabela | Versão | Data | Commit | O que mudou |", file=sys.stderr)
        return 1
    with open(alvo, encoding="utf-8", newline="") as fh:
        texto = fh.read()
    linhas = texto.splitlines(keepends=True)   # arquivo com fim de linha misturado: cada linha guarda o seu
    # a tabela de builds começa na última linha de cabeçalho "| Versão" e vai até a primeira linha que não começa com "|"
    cab = [i for i, l in enumerate(linhas) if re.match(r"\|\s*Vers", l)]
    if not cab:
        print("não achei a tabela | Versão | ... | no arquivo; cole a linha à mão", file=sys.stderr)
        return 1
    ult = cab[-1]
    while ult + 1 < len(linhas) and linhas[ult + 1].startswith("|"):
        ult += 1
    if a.dry_run:
        print(f"(dry-run) entraria depois da linha {ult + 1} de {alvo}")
        return 0
    eol = "\r\n" if linhas[ult].endswith("\r\n") else "\n"
    if not linhas[ult].endswith(("\n", "\r")):
        linhas[ult] += eol   # a tabela é o fim do arquivo, sem quebra na última linha
    linhas.insert(ult + 1, linha + eol)
    with open(alvo, "w", encoding="utf-8", newline="") as fh:
        fh.write("".join(linhas))
    print(f"linha acrescentada em {alvo}")
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
    p = comum(sub.add_parser("achar")); p.set_defaults(f=cmd_achar)
    p = comum(sub.add_parser("zip")); p.add_argument("pasta", nargs="?"); p.add_argument("--nome"); p.add_argument("--saida")
    p.add_argument("--forcar", action="store_true"); p.set_defaults(f=cmd_zip)
    p = comum(sub.add_parser("linha")); p.add_argument("--versao", required=True); p.add_argument("--notas", required=True)
    p.add_argument("--anexar"); p.set_defaults(f=cmd_linha)
    a = ap.parse_args()
    return a.f(a)


if __name__ == "__main__":
    sys.exit(main())
