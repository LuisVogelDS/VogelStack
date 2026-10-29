"""Fila do Unity em batch (versão canônica do VogelStack; nasceu no GobbleGoblin em 23/09 e foi copiada e remendada
em cada jogo): duas sessões de agente trabalham no repo em paralelo e o Unity só abre o projeto uma vez, e quem
chegava segundo abortava com "another Unity instance is running". Este wrapper espera a vez (trava em
Logs/unity-batch.lock + checagem de Unity.exe vivo NESTE projeto), roda o método e solta a trava.

Só conta o Unity aberto neste projeto (06/10): um editor de outro jogo não trava a fila. O exe da build só barra
uma BUILD (27/09): é ela que sobrescreve a pasta de build; um método de bootstrap/foto em batch roda com o dono jogando.

Uso:
    python Ferramentas/unity_batch.py <Classe.Metodo> [--log Logs/x.log] [--quem nome-da-sessao] [-- args extras pro Unity]
    python Ferramentas/unity_batch.py <Classe.Metodo> --sem-quit --log Logs/teste-x.log -- -roteiro x   # teste em Play
    python Ferramentas/unity_batch.py <Classe.Metodo> --projeto <cópia>   # roda numa cópia (cada projeto tem a própria trava)
    python Ferramentas/unity_batch.py --status          # quem está com o Unity agora
    python Ferramentas/unity_batch.py <Classe.Metodo> --dry-run   # mostra configuração e comando, sem esperar nem abrir

A build também passa por aqui: buildar com o jogo de alguém aberto quebra (resources.assets corrompido).
Configuração por projeto em Ferramentas/unity.json (ver unity_comum.py); sem ela valem os padrões.

Códigos de saída: o do Unity; 3 = desisti da fila depois de --espera segundos; 4 = projeto ou Unity.exe não encontrado;
2 = uso errado.
"""
import argparse
import datetime
import json
import os
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))  # também sob python -I
import unity_comum as comum  # noqa: E402

SEM_JANELA = comum.SEM_JANELA
RAIZ = TRAVA = CFG = JOGO = UNITY = None


def configurar(projeto=None):
    """Resolve o projeto (a pasta-mãe do script, ou --projeto/UNITY_PROJETO) e carrega a configuração dele."""
    global RAIZ, TRAVA, CFG, JOGO, UNITY
    RAIZ = comum.achar_raiz(projeto, __file__)
    CFG = comum.ler_config(RAIZ)
    TRAVA = os.path.join(RAIZ, *CFG.get('trava', 'Logs/unity-batch.lock').split('/'))
    JOGO = comum.jogo_exe(RAIZ, CFG)
    UNITY = comum.unity_exe(RAIZ, CFG)


def _norm(s):
    return s.replace('/', '\\').lower()


def _cita_projeto(linha, alvo):
    """A linha de comando cita este projeto, e não outro que só começa igual (games/nuvem contra games/nuvem-jogo)."""
    linha, alvo = _norm(linha), _norm(alvo)
    i = linha.find(alvo)
    while i != -1:
        fim = i + len(alvo)
        if fim == len(linha) or linha[fim] in '"\' \\':
            return True
        i = linha.find(alvo, i + 1)
    return False


def _listar_processos():
    """[(nome, linha de comando)] de Unity.exe e do exe da build; None se o Windows não deixou perguntar."""
    nomes = "Name='Unity.exe'" + (f" or Name='{JOGO}'" if JOGO else '')
    cmd = ['powershell', '-NoProfile', '-Command',
           f"Get-CimInstance Win32_Process -Filter \"{nomes}\" | ForEach-Object {{ $_.Name + '|' + $_.CommandLine }}"]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, errors='replace', creationflags=SEM_JANELA, timeout=30)
    except (OSError, subprocess.TimeoutExpired):
        return None
    if r.returncode != 0:
        return None
    return [(n.strip(), c) for n, _, c in (l.partition('|') for l in r.stdout.splitlines()) if n.strip()]


def processos_vivos(com_jogo=True):
    """Unity.exe com este projeto aberto (o editor do dono também conta) e, para build, o exe do jogo.
    Linha de comando ilegível (sem permissão) conta, por segurança; sem PowerShell, todo Unity.exe conta."""
    procs = _listar_processos()
    if procs is None:
        try:
            saida = subprocess.run(['tasklist', '/FO', 'CSV', '/NH'], capture_output=True, text=True, errors='replace',
                                   creationflags=SEM_JANELA).stdout
        except OSError:
            return []
        procs = [(l.split(',')[0].strip('"'), '') for l in saida.splitlines()]
        procs = [(n, c) for n, c in procs if n == 'Unity.exe' or (JOGO and n.lower() == JOGO.lower())]
    vivos = []
    for nome, linha in procs:
        if nome.lower() == 'unity.exe' and (not linha.strip() or _cita_projeto(linha, RAIZ)):
            vivos.append(nome)
        elif com_jogo and JOGO and nome.lower() == JOGO.lower():
            vivos.append(nome)
    return vivos


def ler_trava():
    try:
        with open(TRAVA, encoding='utf-8') as fh:
            return json.load(fh)
    except (OSError, ValueError):
        return None


def trava_viva(t):
    if not t:
        return False
    try:
        out = subprocess.run(['tasklist', '/FI', f"PID eq {t['pid']}", '/FO', 'CSV', '/NH'], capture_output=True, text=True,
                             errors='replace', creationflags=SEM_JANELA).stdout
        return str(t['pid']) in out
    except (OSError, KeyError):
        return False


def pegar(quem, oque):
    os.makedirs(os.path.dirname(TRAVA), exist_ok=True)
    try:
        fd = os.open(TRAVA, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError:
        t = ler_trava()
        if trava_viva(t):
            return False
        os.remove(TRAVA)  # trava de um processo que morreu
        return pegar(quem, oque)
    with os.fdopen(fd, 'w', encoding='utf-8') as fh:
        json.dump({'pid': os.getpid(), 'quem': quem, 'oque': oque, 'desde': datetime.datetime.now().isoformat(timespec='seconds')}, fh)
    return True


def main():
    ap = argparse.ArgumentParser(description='Fila do Unity em batch (uma instância por projeto).')
    ap.add_argument('metodo', nargs='?', help='Classe.Metodo estático do editor')
    ap.add_argument('--log', default=None, help='log do Unity, relativo ao projeto (padrão Logs/<metodo>.log)')
    ap.add_argument('--quem', default=os.environ.get('CLAUDE_SESSAO', '?'), help='nome da sessão, gravado na trava')
    ap.add_argument('--espera', type=int, default=None, help='segundos de espera na fila (padrão 1800)')
    ap.add_argument('--status', action='store_true')
    ap.add_argument('--sem-quit', action='store_true', help='não passa -quit (testes em Play que saem sozinhos com EditorApplication.Exit)')
    ap.add_argument('--projeto', default=None, help='caminho de uma cópia do projeto (cada cópia tem a própria trava); padrão: o deste script')
    ap.add_argument('--dry-run', action='store_true', help='mostra a configuração e o comando, sem esperar a vez nem abrir o Unity')
    args, extras = ap.parse_known_args()
    if extras and extras[0] == '--':
        extras = extras[1:]
    configurar(args.projeto)
    if not comum.eh_projeto_unity(RAIZ):
        print(f'[unity_batch] {RAIZ} não é um projeto Unity (falta ProjectSettings/ProjectVersion.txt); use --projeto', file=sys.stderr)
        return 4
    if args.status:
        print('trava:', ler_trava(), '| viva:', trava_viva(ler_trava()), '| processos:', processos_vivos())
        return 0
    if not args.metodo:
        ap.error('falta Classe.Metodo')
    espera_max = args.espera if args.espera is not None else int(CFG.get('espera_padrao', 1800))
    log = args.log or f"Logs/{args.metodo.replace('.', '-')}.log"
    build = CFG.get('palavra_build', 'build').lower() in args.metodo.lower()
    cmd = [UNITY, '-batchmode'] + ([] if args.sem_quit else ['-quit']) + ['-projectPath', RAIZ, '-executeMethod', args.metodo, '-logFile', os.path.join(RAIZ, log)] + extras
    if args.dry_run:
        print(f'[unity_batch] projeto: {RAIZ}\n  trava: {TRAVA}\n  exe da build: {JOGO} (método conta como build: {"sim" if build else "não"})\n'
              f'  Unity existe: {os.path.isfile(UNITY)}\n  espera máx.: {espera_max}s\n  comando: {subprocess.list2cmdline(cmd)}')
        return 0
    if not os.path.isfile(UNITY):
        print(f'[unity_batch] Unity.exe não encontrado: {UNITY} (ajuste unity_versao/unity_exe em Ferramentas/unity.json)', file=sys.stderr)
        return 4
    t0 = time.time(); avisou = False
    while True:
        if not processos_vivos(build) and pegar(args.quem, args.metodo):
            if processos_vivos(build):  # alguém abriu entre a checagem e a trava
                os.remove(TRAVA)
            else:
                break
        if time.time() - t0 > espera_max:
            print(f'[unity_batch] desisti depois de {espera_max}s — com o Unity: {ler_trava()} {processos_vivos()}')
            return 3
        if not avisou:
            print(f'[unity_batch] esperando a vez — trava: {ler_trava()} · processos: {processos_vivos(build)}', flush=True)
            avisou = True
        time.sleep(10)
    try:
        espera = time.time() - t0
        if espera > 1:
            print(f'[unity_batch] vez conseguida depois de {espera:.0f}s', flush=True)
        r = subprocess.run(cmd, cwd=RAIZ)
        print(f'[unity_batch] {args.metodo} saiu com {r.returncode} (log: {log})')
        return r.returncode
    finally:
        t = ler_trava()
        if t and t.get('pid') == os.getpid():
            os.remove(TRAVA)


if __name__ == '__main__':
    sys.exit(main())
