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
# Projetos que consomem a stack como submódulo devem excluir vogel-stack/ do
# escopo (lá a malha é responsabilidade da própria stack).
# ---------------------------------------------------------------------------
$ErrorActionPreference = 'Stop'
$root = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
Push-Location $root
try {
    $md = Get-ChildItem -Recurse -Filter *.md -File |
        Where-Object { ($_.FullName -replace '\\', '/') -notmatch '/(\.git|\.obsidian|node_modules)/' }

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

    $bt = [char]96; $fence = "$bt$bt$bt"
    $fencePat  = "(?sm)^[ \t]*$fence.*?^[ \t]*$fence"   # blocos cercados (fence no início da linha)
    $inlinePat = "$bt[^$bt`n]*$bt"                       # código inline (sem cruzar linha)

    $broken = New-Object System.Collections.Generic.List[string]
    $checked = 0
    foreach ($f in $md) {
        $raw = Get-Content -Raw -LiteralPath $f.FullName
        $c = [regex]::Replace($raw, $fencePat, '')
        $c = [regex]::Replace($c, $inlinePat, '')
        foreach ($m in [regex]::Matches($c, '\[\[([^\]]+)\]\]')) {
            $inner  = $m.Groups[1].Value
            $target = ((($inner -split '\|')[0]) -split '#')[0].Trim()
            $checked++
            if ($target -eq '') { continue }   # [[#secao]] — link de seção na própria página
            $norm = ($target -replace '\.md$', '').ToLowerInvariant()
            $base = ($norm -split '/')[-1]
            if (-not ($byPath.Contains($norm) -or $byBase.Contains($base))) {
                $broken.Add(("{0}: [[{1}]]" -f $relOf[$f.FullName], $inner))
            }
        }
    }

    if ($broken.Count -gt 0) {
        Write-Host "X  $($broken.Count) wikilink(s) quebrado(s) em $($md.Count) arquivos:" -ForegroundColor Red
        $broken | Sort-Object | ForEach-Object { Write-Host "   $_" -ForegroundColor Red }
        exit 1
    }
    Write-Host "OK  $($md.Count) arquivos, $checked wikilinks verificados, 0 quebrados." -ForegroundColor Green
    exit 0
}
finally {
    Pop-Location
}
