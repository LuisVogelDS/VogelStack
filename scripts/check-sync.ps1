#!/usr/bin/env pwsh
# ---------------------------------------------------------------------------
# check-sync.ps1 — lint determinístico do ESTADO DE PARTIDA do repositório.
#
# Verifica os invariantes da §1.1 de vogel-stack/operacao-agentes.md
# ("Checklist antes de começar uma alteração"):
#   - a branch atual tem upstream configurado                          [erro];
#   - a branch não está atrás do remoto                                [erro];
#   - o working tree não tem pendências de outra frente                [aviso].
#
# Por que existe: sem upstream, o Git NUNCA reporta "behind" — nem aqui, nem no
# 'git status', que diz "working tree clean" e é lido como "estou em dia". A
# defasagem fica invisível e a implementação sobre base velha sobrescreve
# trabalho publicado, passando em todos os testes de saída (§8). Erro silencioso
# contradiz o princípio nº 3 (erros precisam ser visíveis); este script é a rede
# automática que o torna audível.
#
# Uso — projetos que consomem a stack como submódulo NÃO precisam copiar:
#   ./vogel-stack/scripts/check-sync.ps1        # roda do submódulo, checa o PROJETO
#   ./scripts/check-sync.ps1                    # se o projeto tiver cópia própria
#   ./scripts/check-sync.ps1 -RepoPath D:\algo  # repo explícito
#   ... -NoFetch                                # usa a foto local de origin/* (sem rede)
#
# Trava LOCAL, de antes de começar. Ao contrário do link checker (§7.4), NÃO é
# checker de CI: no CI o checkout é sempre fresco, então "atrás do remoto" nunca
# dispararia lá. O valor está na máquina de quem vai implementar.
#
# Sem dependência de LLM, no espírito dos irmãos scripts/check-wikilinks.ps1 e
# scripts/check-quadro.ps1. Fora de repositório git, passa (exit 0).
#
# Exit 1 se houver qualquer erro; exit 0 caso contrário (avisos não falham).
# ---------------------------------------------------------------------------
[CmdletBinding()]
param(
    [switch]$NoFetch,
    [string]$RepoPath
)

$ErrorActionPreference = 'Stop'
# git é nativo: exit-code != 0 NÃO deve abortar o script (tratamos manualmente).
$PSNativeCommandUseErrorActionPreference = $false

# Qual repositório checar:
#   -RepoPath explícito            -> esse;
#   script veio pelo submódulo      -> o SUPERPROJETO (o projeto que consome a
#     stack) — checar o submódulo daria um OK falso sobre o repo errado;
#   script no próprio repo          -> <script>/.. (o repo dele).
$root =
    if ($RepoPath) { (Resolve-Path $RepoPath).Path }
    else {
        $cand  = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
        $super = (git -C $cand rev-parse --show-superproject-working-tree 2>$null)
        if ($LASTEXITCODE -eq 0 -and $super) { (Resolve-Path $super).Path } else { $cand }
    }

Push-Location $root
try {
    git rev-parse --is-inside-work-tree 2>$null | Out-Null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "OK  não é um repositório git — nada a checar." -ForegroundColor Green
        exit 0
    }

    $errors   = New-Object System.Collections.Generic.List[string]
    $warnings = New-Object System.Collections.Generic.List[string]

    $branch = (git rev-parse --abbrev-ref HEAD 2>$null)
    if (-not $branch -or $branch -eq 'HEAD') {
        Write-Host "!  HEAD destacado (detached) — sem branch para comparar." -ForegroundColor Yellow
        exit 0
    }

    if (-not $NoFetch) { git fetch --quiet 2>$null | Out-Null }

    # 1. Upstream configurado? Sem ele o Git nunca diz "behind" (a falha silenciosa).
    $up = (git rev-parse --abbrev-ref --symbolic-full-name '@{u}' 2>$null)
    $hasUpstream = ($LASTEXITCODE -eq 0 -and $up)
    if (-not $hasUpstream) {
        $errors.Add("branch '$branch' NÃO tem upstream — o Git nunca vai reportar 'behind' nela, nem o 'git status'. Corrija: git branch --set-upstream-to=origin/$branch $branch")
    }

    # 2. Atrás do remoto? Compara contra origin/<branch> mesmo sem upstream —
    #    é justamente o caso sem upstream que esconde a defasagem.
    $ref = if ($hasUpstream) { $up } else { "origin/$branch" }
    git rev-parse --verify --quiet $ref 2>$null | Out-Null
    if ($LASTEXITCODE -ne 0) {
        $warnings.Add("não consegui resolver '$ref' — o remoto tem esta branch? (o fetch rodou?)")
    }
    else {
        $atras = (git rev-list --count "HEAD..$ref" 2>$null)
        if ($LASTEXITCODE -eq 0 -and [int]$atras -gt 0) {
            $errors.Add("branch '$branch' está $atras commit(s) ATRÁS de $ref — implementar daqui sobrescreve trabalho já publicado. Traga antes: git pull --ff-only")
        }
    }

    # 3. Working tree sujo: pode ser trabalho de outra frente/sessão (item 4 da §1.1).
    $dirty = @(git status --porcelain 2>$null).Count
    if ($dirty -gt 0) {
        $warnings.Add("$dirty arquivo(s) pendente(s) no working tree — confirme que são seus antes de misturar com a alteração nova.")
    }

    Write-Host "repo: $root" -ForegroundColor DarkGray
    foreach ($w in $warnings) { Write-Host "!  $w" -ForegroundColor Yellow }

    if ($errors.Count -gt 0) {
        Write-Host "X  $($errors.Count) problema(s) no estado de partida:" -ForegroundColor Red
        $errors | ForEach-Object { Write-Host "   $_" -ForegroundColor Red }
        exit 1
    }

    Write-Host "OK  branch '$branch' sincronizada com $ref — estado de partida limpo." -ForegroundColor Green
    exit 0
}
finally {
    Pop-Location
}
