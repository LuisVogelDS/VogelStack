#!/usr/bin/env python3
"""Confere que o repo continua neutro: sem caminho de usuário, sem e-mail pessoal e sem nome proibido.

Varre os arquivos versionados (git ls-files), menos os binários, e barra:
  - caminho absoluto de usuário (C:\\Users\\<nome>, /c/Users/<nome>, /Users/<nome>/, /home/<nome>/), salvo
    placeholder óbvio (<usuario>, $USER, %USERNAME%, "usuario", "user", "runner"...);
  - e-mail que não seja de exemplo (example.com/.org/.net) nem de máquina (git@host, noreply@...);
  - nome proibido, sem que o nome esteja escrito em lugar nenhum do repo: scripts/neutralidade-hashes.txt guarda só o
    SHA-256 de cada termo (minúsculas, sem acento, palavras separadas por um espaço). Cada linha (e cada nome de
    arquivo) é quebrada em palavras (letras e dígitos; hífen e sublinhado separam), e o hash de cada palavra e de cada
    sequência de 2 ou 3 palavras vizinhas é comparado com a lista.

Uso:
    python scripts/check-neutralidade.py                   # confere o repo; sai com 1 se achar algo
    python scripts/check-neutralidade.py --adicionar TERMO # acrescenta o hash de TERMO (1 a 3 palavras) à lista

A saída é arquivo:linha e a regra; do nome proibido só se diz "nome proibido", nunca qual. Só biblioteca padrão.
Palavra comum do idioma não entra na lista (daria falso positivo): só nome próprio que não deve aparecer.
"""
import argparse
import hashlib
import os
import re
import subprocess
import sys
import unicodedata

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HASHES = os.path.join(RAIZ, 'scripts', 'neutralidade-hashes.txt')
IGNORADOS = {'scripts/neutralidade-hashes.txt'}
MAX_PALAVRAS = 3

# ---- caminho de usuário ----
CAMINHO = re.compile(
    r'(?:(?<![A-Za-z0-9])[A-Za-z]:[\\/]+|(?<![\w.~/\\-])/[A-Za-z]/|(?<![\w.~/\\-])/)'
    r'(?:Users|home)[\\/]+([^\\/\s"\'`,;)\]}]+)', re.I)
NOMES_EXEMPLO = {'usuario', 'user', 'username', 'nome', 'name', 'seu', 'voce', 'you', 'me', 'exemplo', 'example',
                 'foo', 'bar', 'xxx', 'runner', 'public', 'default', 'all', 'shared', 'ubuntu', 'vagrant'}

# ---- e-mail ----
EMAIL = re.compile(r'([A-Za-z0-9._%+-]+)@([A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)*\.([A-Za-z]{2,24}))(?![A-Za-z0-9-])')
DOMINIOS_EXEMPLO = ('example.com', 'example.org', 'example.net')
LOCAIS_NEUTROS = {'git', 'user', 'usuario', 'noreply', 'no-reply', 'nome', 'seu-email', 'email'}
EXTENSOES = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'svg', 'ico', 'bmp', 'avif', 'js', 'mjs', 'ts', 'css', 'json',
             'md', 'py', 'cs', 'txt', 'html', 'ps1', 'sh', 'yml', 'yaml', 'wav', 'mp3', 'mp4', 'ogg', 'zip'}

PALAVRA = re.compile(r'[^\W_]+', re.UNICODE)


def normaliza(texto):
    """Minúsculas e sem acento."""
    d = unicodedata.normalize('NFKD', texto)
    return ''.join(c for c in d if not unicodedata.combining(c)).lower()


def sha(termo):
    return hashlib.sha256(termo.encode('utf-8')).hexdigest()


def carregar_hashes():
    try:
        with open(HASHES, encoding='utf-8') as fh:
            return {l.strip().lower() for l in fh if l.strip() and not l.lstrip().startswith('#')}
    except OSError:
        return set()


def termo_normalizado(termo):
    return ' '.join(PALAVRA.findall(normaliza(termo)))


def adicionar(termo):
    norm = termo_normalizado(termo)
    n = len(norm.split())
    if not 1 <= n <= MAX_PALAVRAS:
        print('termo precisa ter de 1 a %d palavras' % MAX_PALAVRAS, file=sys.stderr)
        return 2
    hashes = carregar_hashes()
    h = sha(norm)
    if h in hashes:
        print('já estava na lista (%d termo(s))' % len(hashes))
        return 0
    hashes.add(h)
    with open(HASHES, 'w', encoding='utf-8', newline='\n') as fh:
        fh.write('# SHA-256 de termos proibidos (minúsculas, sem acento). Edite só com: check-neutralidade.py --adicionar TERMO\n')
        for x in sorted(hashes):
            fh.write(x + '\n')
    print('hash acrescentado (%d termo(s))' % len(hashes))
    return 0


def nome_proibido(linha, hashes):
    palavras = PALAVRA.findall(normaliza(linha))
    for i in range(len(palavras)):
        for n in range(1, MAX_PALAVRAS + 1):
            if i + n <= len(palavras) and sha(' '.join(palavras[i:i + n])) in hashes:
                return True
    return False


def caminho_pessoal(linha):
    for m in CAMINHO.finditer(linha):
        nome = m.group(1)
        base = nome.lower().strip('.')
        if nome[:1] in '<$%{~*' or base in NOMES_EXEMPLO or base.startswith(('seu', 'sua', 'your', 'meu')):
            continue
        return m.group(0)
    return None


def email_pessoal(linha):
    for m in EMAIL.finditer(linha):
        local, dominio, tld = m.group(1).lower(), m.group(2).lower(), m.group(3).lower()
        if dominio in DOMINIOS_EXEMPLO or local in LOCAIS_NEUTROS or tld in EXTENSOES:
            continue
        if dominio == 'anthropic.com' and local == 'noreply':
            continue
        return m.group(0)
    return None


def arquivos_versionados():
    out = subprocess.run(['git', '-C', RAIZ, 'ls-files', '-z'], capture_output=True, check=True)
    return [p for p in out.stdout.decode('utf-8', errors='replace').split('\0') if p]


def conferir():
    hashes = carregar_hashes()
    if not hashes:
        print('aviso: scripts/neutralidade-hashes.txt vazio ou ausente; nomes proibidos não conferidos', file=sys.stderr)
    achados = []
    for rel in arquivos_versionados():
        if rel in IGNORADOS:
            continue
        if hashes and nome_proibido(rel, hashes):
            achados.append('%s:0: nome proibido (no nome do arquivo)' % rel)
        caminho = os.path.join(RAIZ, *rel.split('/'))
        try:
            with open(caminho, 'rb') as fh:
                bruto = fh.read()
        except OSError:
            continue    # removido do disco mas ainda no índice
        if b'\0' in bruto[:8192]:
            continue    # binário
        texto = bruto.decode('utf-8', errors='replace')
        for n, linha in enumerate(texto.splitlines(), 1):
            achado = caminho_pessoal(linha)
            if achado:
                achados.append('%s:%d: caminho absoluto de usuário (%s)' % (rel, n, achado))
            achado = email_pessoal(linha)
            if achado:
                achados.append('%s:%d: e-mail que não é de exemplo (%s)' % (rel, n, achado))
            if hashes and nome_proibido(linha, hashes):
                achados.append('%s:%d: nome proibido' % (rel, n))
    for a in achados:
        print(a)
    if achados:
        print('\n%d ocorrência(s) em %d arquivo(s)' % (len(achados), len({a.split(':')[0] for a in achados})))
        return 1
    print('neutro: nenhuma ocorrência')
    return 0


def main():
    for fluxo in (sys.stdout, sys.stderr):
        if hasattr(fluxo, 'reconfigure'):
            fluxo.reconfigure(encoding='utf-8', errors='replace')   # console cp1252 do Windows
    ap = argparse.ArgumentParser(description='Confere a neutralidade dos arquivos versionados.')
    ap.add_argument('--adicionar', metavar='TERMO', help='acrescenta o hash de um nome proibido (1 a 3 palavras)')
    args = ap.parse_args()
    if args.adicionar:
        return adicionar(args.adicionar)
    return conferir()


if __name__ == '__main__':
    sys.exit(main())
