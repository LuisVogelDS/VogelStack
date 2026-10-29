r"""Base comum de unity_batch.py e compilar_fora.py: acha o projeto, lê Ferramentas/unity.json e localiza o editor.

Configuração por projeto: <raiz>/Ferramentas/unity.json, todas as chaves opcionais.
    unity_versao         padrão: m_EditorVersion de ProjectSettings/ProjectVersion.txt
    unity_exe            caminho completo do Unity.exe (vence unity_versao)
    unity_editores       pasta dos editores do Hub (padrão C:\Program Files\Unity\Hub\Editor)
    jogo_exe             exe da build (ex. "Slime.exe"); a fila espera ele fechar antes de uma BUILD.
                         Padrão: productName de ProjectSettings/ProjectSettings.asset sem espaços + ".exe"
    palavra_build        trecho do nome do método que o torna "build" (padrão "build")
    espera_padrao        segundos de espera na fila (padrão 1800)
    trava                caminho relativo da trava (padrão Logs/unity-batch.lock)
    prefixo_assembly     prefixo dos assemblies do próprio jogo (compilar_fora; ex. "Galinha")
    alvos_padrao         assemblies que o compilar_fora compila sem argumento
"""
import glob
import json
import os
import re
import subprocess

# sem janela de console no Windows: o processo filho abria uma janela por um instante e tirava o foco do
# jogo em tela cheia que o dono estava jogando enquanto os agentes compilavam
SEM_JANELA = getattr(subprocess, 'CREATE_NO_WINDOW', 0)

EDITORES_PADRAO = r'C:\Program Files\Unity\Hub\Editor'


def achar_raiz(projeto=None, script=None):
    """--projeto (ou UNITY_PROJETO) vence; senão a pasta-mãe da pasta do script (<raiz>/Ferramentas/x.py)."""
    projeto = projeto or os.environ.get('UNITY_PROJETO')
    if projeto:
        return os.path.abspath(projeto)
    return os.path.dirname(os.path.dirname(os.path.abspath(script)))


def eh_projeto_unity(raiz):
    return os.path.isfile(os.path.join(raiz, 'ProjectSettings', 'ProjectVersion.txt'))


def ler_config(raiz):
    """Ferramentas/unity.json do projeto (ou o arquivo de UNITY_CONFIG); ausente ou ilegível = padrões."""
    try:
        with open(os.environ.get('UNITY_CONFIG') or os.path.join(raiz, 'Ferramentas', 'unity.json'), encoding='utf-8-sig') as fh:
            c = json.load(fh)
        return c if isinstance(c, dict) else {}
    except (OSError, ValueError):
        return {}


def _ler(raiz, rel):
    try:
        with open(os.path.join(raiz, rel), encoding='utf-8-sig', errors='replace') as fh:
            return fh.read()
    except OSError:
        return ''


def versao_do_projeto(raiz):
    m = re.search(r'm_EditorVersion:\s*(\S+)', _ler(raiz, 'ProjectSettings/ProjectVersion.txt'))
    return m.group(1) if m else None


def jogo_exe(raiz, cfg):
    if cfg.get('jogo_exe'):
        return cfg['jogo_exe']
    m = re.search(r'^\s*productName:\s*(.+)$', _ler(raiz, 'ProjectSettings/ProjectSettings.asset'), re.M)
    return (re.sub(r'\s+', '', m.group(1)) + '.exe') if m else None


def unity_exe(raiz, cfg):
    """Unity.exe do editor certo para o projeto (configurado, ou o da versão em ProjectVersion.txt)."""
    if cfg.get('unity_exe'):
        return cfg['unity_exe']
    versao = cfg.get('unity_versao') or versao_do_projeto(raiz) or '6000.3.10f1'
    return os.path.join(cfg.get('unity_editores') or EDITORES_PADRAO, versao, 'Editor', 'Unity.exe')


def editor_data(raiz, cfg):
    """Pasta Editor/Data do editor (onde moram o dotnet e o Roslyn)."""
    return os.path.join(os.path.dirname(unity_exe(raiz, cfg)), 'Data')


def roslyn(data):
    """(dotnet.exe, csc.dll): no 6000.6 o Roslyn mora dentro do DotNetSdk; nas versões antigas, em DotNetSdkRoslyn."""
    novo = sorted(glob.glob(os.path.join(data, 'DotNetSdk', 'sdk', '*', 'Roslyn', 'bincore', 'csc.dll')))
    if novo:
        return os.path.join(data, 'DotNetSdk', 'dotnet.exe'), novo[-1]
    return os.path.join(data, 'NetCoreRuntime', 'dotnet.exe'), os.path.join(data, 'DotNetSdkRoslyn', 'csc.dll')
