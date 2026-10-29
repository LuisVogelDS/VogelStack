"""Checagem de compilação FORA do editor (versão canônica do VogelStack; nasceu no GobbleGoblin em 05/09): lê o
.csproj gerado pelo Unity (referências, defines) e compila todos os .cs do assembly com o Roslyn que o próprio Unity
traz. Serve pra pegar erro de sintaxe/símbolo quando o editor está ocupado ou a ponte MCP caiu; não substitui o Play.

Uso: python Ferramentas/compilar_fora.py [<Prefixo>.Runtime] [<Prefixo>.Editor ...] [--projeto <cópia>] [--dry-run]
Sem argumentos compila "alvos_padrao" de Ferramentas/unity.json (padrão: <prefixo_assembly>.Runtime e .Editor).
Assemblies do próprio jogo referenciados (ProjectReference com o prefixo) são compilados antes e viram DLL em
Ferramentas/tmp/dll/ (ou na pasta de COMPILAR_SAIDA: agentes em paralelo usam pastas próprias, 24/09).
--dry-run lista as fontes e referências de cada assembly sem chamar o compilador.

Códigos de saída: 0 compilou tudo; 1 algum assembly falhou; 4 projeto ou editor não encontrado.
"""
import glob
import io
import json
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))  # também sob python -I
import unity_comum as comum  # noqa: E402

SEM_JANELA = comum.SEM_JANELA
RAIZ = CFG = PREFIXO = DOTNET = CSC = SAIDA = None
DRY = False


def configurar(projeto=None):
    global RAIZ, CFG, PREFIXO, DOTNET, CSC, SAIDA
    RAIZ = comum.achar_raiz(projeto, __file__)
    CFG = comum.ler_config(RAIZ)
    PREFIXO = CFG.get('prefixo_assembly') or ''
    DOTNET, CSC = comum.roslyn(comum.editor_data(RAIZ, CFG))
    SAIDA = os.environ.get('COMPILAR_SAIDA') or os.path.join(RAIZ, 'Ferramentas', 'tmp', 'dll')


def ler_csproj(nome):
    p = os.path.join(RAIZ, nome + '.csproj')
    if not os.path.exists(p) and PREFIXO and nome == PREFIXO + '.Teste':
        # r25/F9: o Unity só gera o csproj do <Prefixo>.Teste na primeira abertura; até lá, vale o do Runtime (mesmas
        # referências e defines) com o próprio Runtime como projeto referenciado
        d, h, _, _ = ler_csproj(PREFIXO + '.Runtime')
        return d, h, [PREFIXO + '.Runtime'], []
    s = io.open(p, encoding='utf-8').read()
    defines = re.search(r'<DefineConstants>(.*?)</DefineConstants>', s, re.S).group(1).replace('\n', '').split(';')
    hints = re.findall(r'<HintPath>(.*?)</HintPath>', s)
    projs = re.findall(r'<ProjectReference Include="(.*?)\.csproj"', s)
    comps = re.findall(r'<Compile Include="(.*?)"', s)
    return [d.strip() for d in defines if d.strip()], hints, projs, comps


def pasta_do_asmdef(nome):
    """05/10: acha a pasta do .asmdef do assembly, para enxergar pastas novas de frente que o .csproj ainda não lista."""
    for f in glob.glob(os.path.join(RAIZ, 'Assets', '**', '*.asmdef'), recursive=True):
        try:
            if json.load(io.open(f, encoding='utf-8-sig')).get('name') == nome:
                return os.path.dirname(f)
        except ValueError:
            pass
    return None


def asmrefs():
    """r25/F9: pastas com .asmref entregam seus .cs ao assembly nomeado nele (ex.: Scripts/UI/Teste -> <Prefixo>.Teste)."""
    saida = []
    for f in glob.glob(os.path.join(RAIZ, 'Assets', '**', '*.asmref'), recursive=True):
        try:
            saida.append((os.path.dirname(f), json.load(io.open(f, encoding='utf-8-sig')).get('reference')))
        except ValueError:
            pass
    return saida


def fontes_do_assembly(nome, comps):
    # o csproj lista os .cs na hora em que o Unity gerou; arquivos e pastas novos podem faltar: completa
    # varrendo a pasta do .asmdef inteira (menos subpastas que têm .asmdef próprio)
    achados = set(c.replace('\\', '/') for c in comps)
    raiz_asm = pasta_do_asmdef(nome)
    if raiz_asm:
        outras = [os.path.dirname(f) for f in glob.glob(os.path.join(raiz_asm, '**', '*.asmdef'), recursive=True)
                  if os.path.dirname(f) != raiz_asm]
        for f in glob.glob(os.path.join(raiz_asm, '**', '*.cs'), recursive=True):
            if any(os.path.commonpath([f, o]) == o for o in outras):
                continue
            achados.add(os.path.relpath(f, RAIZ).replace('\\', '/'))
    else:
        # sem .asmdef (versão original do GobbleGoblin): varre as pastas que o csproj já cobre
        for pasta in sorted({os.path.dirname(c) for c in comps}):
            for f in glob.glob(os.path.join(RAIZ, pasta, '**', '*.cs'), recursive=True):
                achados.add(os.path.relpath(f, RAIZ).replace('\\', '/'))
    # r25/F9: os .asmref tiram a pasta do assembly de origem e a põem no assembly de destino
    for pasta, destino in asmrefs():
        for f in glob.glob(os.path.join(pasta, '**', '*.cs'), recursive=True):
            rel = os.path.relpath(f, RAIZ).replace('\\', '/')
            if destino == nome:
                achados.add(rel)
            else:
                achados.discard(rel)
    # e arquivos apagados desde a geração do csproj saem da lista
    return sorted(a for a in achados if os.path.exists(os.path.join(RAIZ, a)))


def refs_do_asmdef(nome, refs, projs):
    """23/10: o .csproj só muda quando o Unity o regenera. A referência nova do .asmdef (Unity.Burst, Unity.Mathematics,
    Unity.Collections) que ainda não está nele vem da DLL que o Unity já compilou em Library/ScriptAssemblies."""
    pasta = pasta_do_asmdef(nome)
    if not pasta:
        return []
    arq = [f for f in glob.glob(os.path.join(pasta, '*.asmdef'))]
    if not arq:
        return []
    try:
        nomes = json.load(io.open(arq[0], encoding='utf-8-sig')).get('references', [])
    except ValueError:
        return []
    tem = set(os.path.splitext(os.path.basename(r.replace('\\', '/')))[0] for r in refs) | set(os.path.basename(p) for p in projs)
    extra = []
    for n in nomes:
        if n.startswith('GUID:') or n in tem:
            continue
        dll = os.path.join(RAIZ, 'Library', 'ScriptAssemblies', n + '.dll')
        if os.path.exists(dll):
            extra.append(dll)
            print(f'   + {n} (do .asmdef, fora do .csproj)')
    return extra


def do_jogo(nome):
    """O assembly é do próprio jogo (compilado aqui) e não de pacote (usa a DLL que o Unity já compilou)."""
    return bool(PREFIXO) and nome.startswith(PREFIXO)


feitos = {}


def compilar(nome):
    if nome in feitos:
        return feitos[nome]
    defines, hints, projs, comps = ler_csproj(nome)
    refs = list(hints)
    # r25/F9: assembly do jogo citado no .asmdef que o csproj ainda não conhece (<Prefixo>.Teste no <Prefixo>.Editor)
    pasta_asm = pasta_do_asmdef(nome)
    if pasta_asm:
        for f in glob.glob(os.path.join(pasta_asm, '*.asmdef')):
            for r_ in json.load(io.open(f, encoding='utf-8-sig')).get('references', []):
                if do_jogo(r_) and r_ not in projs and r_ != nome:
                    projs = projs + [r_]
    for pj in projs:
        # assembly de projeto: usa a DLL que o Unity já compilou (Library/ScriptAssemblies); só compila se faltar
        nome_pj = os.path.basename(pj)
        pronta = os.path.join(RAIZ, 'Library', 'ScriptAssemblies', nome_pj + '.dll')
        if nome_pj in feitos and feitos[nome_pj]:
            dll = feitos[nome_pj]
        elif do_jogo(nome_pj):
            dll = compilar(nome_pj)   # compilada agora nesta rodada (o Runtime pro Editor)
        else:
            dll = pronta if os.path.exists(pronta) else compilar(nome_pj)
        if dll:
            refs.append(dll)
    refs += refs_do_asmdef(nome, refs, projs)
    fontes = fontes_do_assembly(nome, comps)
    alvo = os.path.join(SAIDA, nome + '.dll')
    rsp = os.path.join(SAIDA, nome + '.rsp')
    print(f'== {nome}: {len(fontes)} fontes, {len(refs)} referências')
    if DRY:
        print(f'   (dry-run) defines: {len(defines)} · rsp: {rsp} · projetos referenciados: {[os.path.basename(p) for p in projs]}')
        feitos[nome] = alvo
        return alvo
    os.makedirs(SAIDA, exist_ok=True)
    with io.open(rsp, 'w', encoding='utf-8') as w:
        w.write('-nologo\n-target:library\n-langversion:9.0\n-nowarn:0169,0649,0414,0108,0618,1998,8632\n')
        w.write('-warn:0\n-nostdlib\n')
        w.write('-out:' + alvo + '\n')
        w.write('-define:' + ';'.join(defines) + '\n')
        for r in refs:
            w.write('-reference:"' + r + '"\n')
        for f in fontes:
            w.write('"' + os.path.join(RAIZ, f) + '"\n')
    r = subprocess.run([DOTNET, CSC, '@' + rsp], capture_output=True, text=True, encoding='utf-8', errors='replace',
                       creationflags=SEM_JANELA)
    erros = [l for l in (r.stdout + r.stderr).splitlines() if 'error CS' in l]
    for l in erros[:40]:
        print('   ' + l.replace(RAIZ + '\\', ''))
    if r.returncode != 0 and not erros:
        print(r.stdout[-2000:], r.stderr[-2000:])
    print(f"   -> {'OK' if r.returncode == 0 else 'FALHOU'} ({len(erros)} erros)")
    feitos[nome] = alvo if r.returncode == 0 else None
    return feitos[nome]


def main(argv):
    global DRY
    argv = list(argv)
    projeto = None
    if '--projeto' in argv:
        i = argv.index('--projeto')
        projeto = argv[i + 1] if i + 1 < len(argv) else None
        del argv[i:i + 2]
    if '--dry-run' in argv:
        DRY = True
        argv.remove('--dry-run')
    if '-h' in argv or '--help' in argv:
        print(__doc__)
        return 0
    configurar(projeto)
    if not comum.eh_projeto_unity(RAIZ):
        print(f'[compilar_fora] {RAIZ} não é um projeto Unity (falta ProjectSettings/ProjectVersion.txt); use --projeto', file=sys.stderr)
        return 4
    if not DRY and not (os.path.isfile(DOTNET) and os.path.isfile(CSC)):
        print(f'[compilar_fora] Roslyn não encontrado ({CSC}); confira unity_versao em Ferramentas/unity.json', file=sys.stderr)
        return 4
    alvos = argv or CFG.get('alvos_padrao') or ([PREFIXO + '.Runtime', PREFIXO + '.Editor'] if PREFIXO else [])
    if not alvos:
        print('[compilar_fora] sem alvos: passe os assemblies ou defina prefixo_assembly/alvos_padrao em Ferramentas/unity.json', file=sys.stderr)
        return 2
    ok = all(compilar(a) for a in alvos)
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
