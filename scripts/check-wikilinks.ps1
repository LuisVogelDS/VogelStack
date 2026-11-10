#!/usr/bin/env pwsh
# ---------------------------------------------------------------------------
# check-wikilinks.ps1 — piso determinístico da malha de wikilinks.
#
# Valida wikilinks em todos os .md do repositório:
#   [[alvo]]            [[alvo|alias]]            [[alvo#secao]]            [[#secao]]
#
# Resolve o alvo por caminho relativo OU por basename (o menor caminho que
# identifica o arquivo sem ambiguidade). Não valida a âncora
# #secao — só a existência do arquivo-alvo. Ignora código (blocos cercados e
# inline) para não acusar exemplos.
#
# Exit 1 se houver qualquer wikilink quebrado; exit 0 caso contrário.
# Ver vogel-stack/operacao-leve.md e princípio nº 18.
#
# Uso em projeto que consome a stack como submódulo (sem copiar o script):
#   ./vogel-stack/scripts/check-wikilinks.ps1   # checa o PROJETO, não a stack
# Nesse caso os .md de vogel-stack/ ficam fora da checagem (lá a malha é
# responsabilidade da própria stack), mas continuam valendo como alvo: um
# link do projeto para vogel-stack/vogel-stack/principios resolve normalmente.
# ---------------------------------------------------------------------------
[CmdletBinding()]
param([string]$RepoPath)

$ErrorActionPreference = 'Stop'
$PSNativeCommandUseErrorActionPreference = $false

# Mesma regra de raiz do check-sync.ps1: vindo do submódulo, checar o
# SUPERPROJETO. Checar a raiz do submódulo daria um OK falso sobre o repo errado.
$consumidor = $false
$root =
    if ($RepoPath) { (Resolve-Path $RepoPath).Path }
    else {
        $cand  = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
        $super = (git -C $cand rev-parse --show-superproject-working-tree 2>$null)
        if ($LASTEXITCODE -eq 0 -and $super) { $consumidor = $true; (Resolve-Path $super).Path } else { $cand }
    }
Push-Location $root
try {
    $md = Get-ChildItem -Recurse -Filter *.md -File |
        Where-Object { ($_.FullName -replace '\\', '/') -notmatch '/(\.git|\.obsidian|node_modules)/' }
    # Alvos resolvem contra tudo; checam-se só os arquivos do próprio projeto.
    $scan = if ($consumidor) {
        @($md | Where-Object { ($_.FullName -replace '\\', '/') -notmatch '/vogel-stack/' })
    } else { @($md) }

    # Conjuntos de resolução (case-insensitive).
    $byPath = New-Object 'System.Collections.Generic.HashSet[string]'
    $byBase = New-Object 'System.Collections.Generic.HashSet[string]'
    $relOf  = @{}
    foreach ($f in $md) {
        $rel = (((Resolve-Path -Relative $f.FullName) -replace '\\', '/') -replace '^\./', '')
        $noext = $rel -replace '\.md$', ''
        [void]$byPath.Add($noext.ToLowerInvariant())
        [void]$byBase.Add((($noext -split '/')[-1]).ToLowerInvariant())
        $relOf[$f.FullName] = $rel
    }
    # Alvo que não é .md (script, SQL, planilha): vale se o arquivo existe no
    # repositório, pelo caminho ou pelo nome, como no Obsidian.
    $anyPath = New-Object 'System.Collections.Generic.HashSet[string]'
    $anyBase = New-Object 'System.Collections.Generic.HashSet[string]'
    foreach ($t in @(git -C $root ls-files 2>$null)) {
        [void]$anyPath.Add($t.ToLowerInvariant())
        [void]$anyBase.Add((($t -split '/')[-1]).ToLowerInvariant())
    }

    $bt = [char]96; $fence = "$bt$bt$bt"
    $fencePat  = "(?sm)^[ \t]*$fence.*?^[ \t]*$fence"   # blocos cercados (fence no início da linha)
    $inlinePat = "$bt[^$bt`n]*$bt"                       # código inline (sem cruzar linha)

    $broken = New-Object System.Collections.Generic.List[string]
    $checked = 0
    foreach ($f in $scan) {
        $raw = Get-Content -Raw -LiteralPath $f.FullName
        if ($null -eq $raw) { continue }   # arquivo vazio
        $c = [regex]::Replace($raw, $fencePat, '')
        $c = [regex]::Replace($c, $inlinePat, '')
        foreach ($m in [regex]::Matches($c, '\[\[([^\]]+)\]\]')) {
            $inner  = $m.Groups[1].Value
            # Dentro de tabela o pipe do alias vem escapado: [[alvo\|alias]].
            $target = ((($inner -replace '\\\|', '|') -split '\|')[0] -split '#')[0].Trim()
            $checked++
            if ($target -eq '') { continue }   # [[#secao]] — link de seção na própria página
            $norm = ($target -replace '\.md$', '').ToLowerInvariant()
            $base = ($norm -split '/')[-1]
            $ok = $byPath.Contains($norm) -or $byBase.Contains($base)
            if (-not $ok -and $base -match '\.[a-z0-9]+$') {
                $ok = $anyPath.Contains($norm) -or $anyBase.Contains($base)
            }
            if (-not $ok) {
                $broken.Add(("{0}: [[{1}]]" -f $relOf[$f.FullName], $inner))
            }
        }
    }

    if ($broken.Count -gt 0) {
        Write-Host "X  $($broken.Count) wikilink(s) quebrado(s) em $($scan.Count) arquivos:" -ForegroundColor Red
        $broken | Sort-Object | ForEach-Object { Write-Host "   $_" -ForegroundColor Red }
        exit 1
    }
    Write-Host "OK  $($scan.Count) arquivos, $checked wikilinks verificados, 0 quebrados." -ForegroundColor Green
    exit 0
}
finally {
    Pop-Location
}
