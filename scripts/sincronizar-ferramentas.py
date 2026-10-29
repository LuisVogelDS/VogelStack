#!/usr/bin/env python3
"""Copia as ferramentas canônicas de ferramentas/ para os repos listados em ferramentas/manifesto.json.

Cada repo continua autocontido (quem clona o jogo sem o VogelStack tem a ferramenta): a cópia leva um cabeçalho
"cópia gerada do VogelStack/ferramentas/...; edite lá", e a configuração própria de cada repo mora num arquivo dele
(ex.: Ferramentas/unity.json), gerado na primeira vez a partir da versão antiga da ferramenta.

Uso:
    python scripts/sincronizar-ferramentas.py                 # prévia, igual a --dry-run (não escreve)
    python scripts/sincronizar-ferramentas.py --dry-run       # o que mudaria, arquivo por arquivo, com a configuração a gerar
    python scripts/sincronizar-ferramentas.py --checar        # só relata divergência; sai com 1 se houver (não escreve)
    python scripts/sincronizar-ferramentas.py --aplicar       # escreve as cópias e os arquivos de configuração que faltam
Filtros: --ferramenta unity  --repo slime   (repetíveis). Não faz commit nem push em nenhum repo.

Estados de cada arquivo: ok (igual à canônica), novo (não existe no repo), antiga (existe sem cabeçalho: versão
escrita à mão, será substituída), diverge (tem cabeçalho mas difere: a canônica mudou, ou alguém editou a cópia).
"""
import argparse
import difflib
import json
import os
import re
import sys

STACK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MANIFESTO = os.path.join(STACK, 'ferramentas', 'manifesto.json')
COMENTARIO = {'.py': '#', '.ps1': '#', '.sh': '#'}   # extensões que levam cabeçalho; as outras vão sem


def cabecalho(origem_rel, nome, ext):
    c = COMENTARIO.get(ext)
    if not c:
        return ''
    return f'{c} Cópia gerada do VogelStack/{origem_rel}/{nome}; edite lá e rode scripts/sincronizar-ferramentas.py --aplicar.\n'


def esperado(ferr, nome):
    """Texto (LF) que a cópia deve ter: cabeçalho + canônica."""
    caminho = os.path.join(STACK, ferr['origem'], nome)
    with open(caminho, encoding='utf-8', newline='') as fh:
        corpo = fh.read().replace('\r\n', '\n')
    return cabecalho(ferr['origem'], nome, os.path.splitext(nome)[1]) + corpo


def ler_destino(caminho):
    """(texto com LF, usa_crlf) ou (None, False) se não existe."""
    try:
        with open(caminho, 'rb') as fh:
            b = fh.read()
    except OSError:
        return None, False
    return b.decode('utf-8-sig', errors='replace').replace('\r\n', '\n'), b'\r\n' in b


def tem_cabecalho(texto):
    return 'Cópia gerada do VogelStack/' in texto[:400]


def contagem_diff(velho, novo):
    a, b = velho.splitlines(), novo.splitlines()
    mais = menos = 0
    for l in difflib.ndiff(a, b):
        if l.startswith('+ '):
            mais += 1
        elif l.startswith('- '):
            menos += 1
    return mais, menos


# ---- geradores de configuração (um por ferramenta; recebem a raiz do repo, leem as versões antigas ANTES da cópia) ----

def gerar_unity(raiz, antigos):
    """Ferramentas/unity.json a partir do unity_batch.py/compilar_fora.py antigos do repo (e do ProjectSettings)."""
    cfg, avisos = {}, []
    batch = antigos.get('unity_batch.py') or ''
    comp = antigos.get('compilar_fora.py') or ''
    m = re.search(r"Name='Unity\.exe' or Name='([^']+\.exe)'", batch) or re.search(r"startswith\('\"(?!Unity\.exe)([^\"]+\.exe)\"'\)", batch)
    if m:
        cfg['jogo_exe'] = m.group(1)
    else:
        avisos.append('jogo_exe não achado na versão antiga; vale o padrão (productName + .exe), confira')
    versoes = {v for v in re.findall(r'Editor[\\/]+(\d{4}\.\d+\.\d+\w*)[\\/]+Editor', batch + '\n' + comp)}
    try:
        with open(os.path.join(raiz, 'ProjectSettings', 'ProjectVersion.txt'), encoding='utf-8') as fh:
            doprojeto = re.search(r'm_EditorVersion:\s*(\S+)', fh.read()).group(1)
    except (OSError, AttributeError):
        doprojeto = None
    for v in versoes:
        if v != doprojeto:
            cfg['unity_versao'] = v
            avisos.append(f'versão do Unity da ferramenta antiga ({v}) difere do ProjectVersion.txt ({doprojeto}); mantida em unity_versao')
    m = re.search(r'startswith\("(\w+)"\)', comp) or re.search(r"startswith\('(\w+)'\)", comp)
    if m:
        cfg['prefixo_assembly'] = m.group(1)
        m2 = re.search(r'alvos = sys\.argv\[1:\] or \[(.*?)\]', comp)
        if m2:
            alvos = re.findall(r'"([^"]+)"', m2.group(1))
            if alvos and alvos != [m.group(1) + '.Runtime', m.group(1) + '.Editor']:
                cfg['alvos_padrao'] = alvos
    else:
        avisos.append('prefixo_assembly não achado na compilar_fora antiga; preencha à mão se o repo usa compilar_fora')
    return cfg, avisos


GERADORES = {'unity': gerar_unity}


# ---- manifesto ----

def expandir(m, nomes):
    """Nomes de repo/grupo (ou {"repo","destino"}) -> lista de (nome, destino|None) sem repetir."""
    saida, vistos = [], set()
    for item in nomes:
        destino = None
        if isinstance(item, dict):
            destino, item = item.get('destino'), item['repo']
        for r in m.get('grupos', {}).get(item, [item]):
            if r not in vistos:
                vistos.add(r)
                saida.append((r, destino))
    return saida


def planejar(m, filtro_ferr, filtro_repo):
    """Lista de ações, uma por (ferramenta, repo)."""
    acoes = []
    for fnome, ferr in m['ferramentas'].items():
        if filtro_ferr and fnome not in filtro_ferr:
            continue
        for rnome, destino in expandir(m, ferr.get('repos', [])):
            if filtro_repo and rnome not in filtro_repo:
                continue
            if rnome not in m['repos']:
                acoes.append({'ferr': fnome, 'repo': rnome, 'erro': 'repo não está em "repos" do manifesto'})
                continue
            raiz = os.path.expanduser(m['repos'][rnome])
            acoes.append({'ferr': fnome, 'repo': rnome, 'raiz': raiz, 'destino': destino or ferr.get('destino', '.'), 'def': ferr})
    return acoes


def avaliar(a):
    """Preenche a['arquivos'] (estado de cada um) e a['config'] (o que fazer com o arquivo de configuração)."""
    ferr = a['def']
    if not os.path.isdir(a['raiz']):
        a['estado'] = 'ausente'
        return
    if not os.path.isdir(os.path.join(STACK, ferr['origem'])):
        a['estado'] = 'origem ausente'
        return
    a['estado'] = 'ok'
    a['arquivos'] = []
    antigos = {}
    for nome in ferr['arquivos']:
        alvo = os.path.join(a['raiz'], *a['destino'].split('/'), nome)
        novo = esperado(ferr, nome)
        atual, crlf = ler_destino(alvo)
        antigos[nome] = atual
        if atual is None:
            est, delta = 'novo', None
        elif atual == novo:
            est, delta = 'ok', None
        else:
            est = 'diverge' if tem_cabecalho(atual) else 'antiga'
            delta = contagem_diff(atual, novo)
        a['arquivos'].append({'nome': nome, 'alvo': alvo, 'novo': novo, 'crlf': crlf, 'estado': est, 'delta': delta})
    cfg = ferr.get('config')
    if cfg:
        caminho = os.path.join(a['raiz'], *cfg['arquivo'].split('/'))
        if os.path.isfile(caminho):
            a['config'] = {'caminho': caminho, 'acao': 'existe'}
        else:
            conteudo, avisos = GERADORES[cfg['gerador']](a['raiz'], antigos)
            a['config'] = {'caminho': caminho, 'acao': 'gerar', 'conteudo': conteudo, 'avisos': avisos}


def relatar(a, detalhe):
    topo = f"[{a['ferr']}] {a['repo']}"
    if 'erro' in a:
        print(f"{topo}: ERRO {a['erro']}")
        return
    if a['estado'] != 'ok':
        print(f"{topo}: {a['estado']} ({a['raiz']}); pulado")
        return
    partes = []
    for f in a['arquivos']:
        s = f['estado']
        if f['delta']:
            s += f" +{f['delta'][0]}/-{f['delta'][1]}"
        partes.append(f"{f['nome']}={s}")
    cfg = a.get('config')
    if cfg:
        partes.append('config=' + ('existe' if cfg['acao'] == 'existe' else 'a gerar'))
    print(f"{topo}: " + ', '.join(partes))
    if detalhe and cfg and cfg['acao'] == 'gerar':
        print(f"    {os.path.relpath(cfg['caminho'], a['raiz'])} <- " + json.dumps(cfg['conteudo'], ensure_ascii=False))
        for av in cfg['avisos']:
            print('    aviso: ' + av)


def pendente(a):
    if 'erro' in a:
        return True
    if a['estado'] != 'ok':
        return False   # repo que não existe nesta máquina não conta como divergência
    return any(f['estado'] != 'ok' for f in a['arquivos']) or (a.get('config') or {}).get('acao') == 'gerar'


def aplicar(a):
    for f in a['arquivos']:
        if f['estado'] == 'ok':
            continue
        os.makedirs(os.path.dirname(f['alvo']), exist_ok=True)
        texto = f['novo'].replace('\n', '\r\n') if f['crlf'] else f['novo']
        with open(f['alvo'], 'wb') as fh:
            fh.write(texto.encode('utf-8'))
        print(f"    escrito {os.path.relpath(f['alvo'], a['raiz'])}")
    cfg = a.get('config')
    if cfg and cfg['acao'] == 'gerar':
        os.makedirs(os.path.dirname(cfg['caminho']), exist_ok=True)
        with open(cfg['caminho'], 'w', encoding='utf-8', newline='\n') as fh:
            json.dump(cfg['conteudo'], fh, ensure_ascii=False, indent=2)
            fh.write('\n')
        print(f"    escrito {os.path.relpath(cfg['caminho'], a['raiz'])}")
        for av in cfg['avisos']:
            print('    aviso: ' + av)


def main():
    for fluxo in (sys.stdout, sys.stderr):
        if hasattr(fluxo, 'reconfigure'):
            fluxo.reconfigure(encoding='utf-8', errors='replace')   # console cp1252 do Windows
    ap = argparse.ArgumentParser(description='Sincroniza as ferramentas canônicas do VogelStack com os repos do manifesto.',
                                 epilog='Sem flag de modo, faz a prévia (--dry-run). Nunca faz commit.')
    modo = ap.add_mutually_exclusive_group()
    modo.add_argument('--dry-run', action='store_true', help='mostra o que mudaria, sem escrever')
    modo.add_argument('--checar', action='store_true', help='relata divergência sem escrever; sai com 1 se houver')
    modo.add_argument('--aplicar', action='store_true', help='escreve as cópias e a configuração que falta')
    ap.add_argument('--ferramenta', action='append', help='só esta ferramenta do manifesto (repetível)')
    ap.add_argument('--repo', action='append', help='só este repo (repetível)')
    ap.add_argument('--manifesto', default=MANIFESTO)
    args = ap.parse_args()
    with open(args.manifesto, encoding='utf-8') as fh:
        m = json.load(fh)
    acoes = planejar(m, args.ferramenta, args.repo)
    if not acoes:
        print('nada a fazer (filtros sem correspondência ou manifesto vazio)')
        return 0
    for a in acoes:
        if 'erro' not in a:
            avaliar(a)
        relatar(a, detalhe=not args.checar)
        if args.aplicar and 'erro' not in a and a['estado'] == 'ok':
            aplicar(a)
    pend = [a for a in acoes if pendente(a)]
    ausentes = [a['repo'] for a in acoes if a.get('estado') in ('ausente', 'origem ausente')]
    print(f"\n{len(acoes)} destino(s); {len(pend)} com pendência" + (f"; {len(ausentes)} pulado(s) por ausência" if ausentes else ''))
    if not args.aplicar:
        if pend and not args.checar:
            print('nada foi escrito; use --aplicar para copiar')
        return 1 if (args.checar and pend) else 0
    return 0


if __name__ == '__main__':
    sys.exit(main())
