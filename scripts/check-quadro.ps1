#!/usr/bin/env pwsh
# ---------------------------------------------------------------------------
# check-quadro.ps1 — lint determinístico do quadro de trabalho (_QUADRO.md).
#
# Verifica os invariantes da §7.1.1 de vogel-stack/operacao-agentes.md:
#   - existe a linha "Última reconciliação: AAAA-MM-DD" (contrato de frescor)   [erro];
#   - a reconciliação não está velha (> $MaxDays dias)                          [aviso];
#   - o quadro NÃO tem uma seção "## ✅ Concluído" acumulando itens — o ✅ é
#     transitório e deve drenar para o changelog, não virar coluna             [erro].
#
# Sem dependência de LLM, no espírito do irmão scripts/check-wikilinks.ps1.
# Projetos sem nenhum _QUADRO.md passam (exit 0) — o quadro é opcional.
#
# Exit 1 se houver qualquer erro; exit 0 caso contrário (avisos não falham).
# ---------------------------------------------------------------------------
[CmdletBinding()]
param([string]$RepoPath)

$ErrorActionPreference = 'Stop'
$PSNativeCommandUseErrorActionPreference = $false

# Mesma regra de raiz do check-sync.ps1: vindo do submódulo
# (./vogel-stack/scripts/check-quadro.ps1), checar o quadro do PROJETO.
$root =
    if ($RepoPath) { (Resolve-Path $RepoPath).Path }
    else {
        $cand  = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
        $super = (git -C $cand rev-parse --show-superproject-working-tree 2>$null)
        if ($LASTEXITCODE -eq 0 -and $super) { (Resolve-Path $super).Path } else { $cand }
    }
$MaxDays = 45
Push-Location $root
try {
    $quadros = Get-ChildItem -Recurse -Filter '_QUADRO.md' -File |
        Where-Object { ($_.FullName -replace '\\', '/') -notmatch '/(\.git|\.obsidian|node_modules|vogel-stack)/' }

    if (-not $quadros) {
        Write-Host "OK  nenhum _QUADRO.md no repo — nada a checar." -ForegroundColor Green
        exit 0
    }

    $errors   = New-Object System.Collections.Generic.List[string]
    $warnings = New-Object System.Collections.Generic.List[string]
    $today    = (Get-Date).Date

    foreach ($q in $quadros) {
        $rel = (((Resolve-Path -Relative $q.FullName) -replace '\\', '/') -replace '^\./', '')
        $raw = Get-Content -Raw -Encoding utf8 -LiteralPath $q.FullName

        # 1. Contrato de frescor: "Última reconciliação: AAAA-MM-DD" na mesma linha.
        $m = [regex]::Match($raw, '(?im)reconcilia[çc][ãa]o[^0-9\r\n]*(\d{4}-\d{2}-\d{2})')
        if (-not $m.Success) {
            $errors.Add("${rel}: falta a linha 'Última reconciliação: AAAA-MM-DD' (contrato de frescor da §7.1.1).")
        }
        else {
            try {
                $d = [datetime]::ParseExact($m.Groups[1].Value, 'yyyy-MM-dd', $null).Date
                $age = ($today - $d).Days
                if ($age -gt $MaxDays) {
                    $warnings.Add("${rel}: reconciliado há $age dias (> $MaxDays) — o quadro pode ter derivado do estado real.")
                }
            }
            catch {
                $errors.Add("${rel}: data de reconciliação inválida '$($m.Groups[1].Value)'.")
            }
        }

        # 2. ✅ é transitório: não pode existir seção de concluídos acumulando.
        if ([regex]::IsMatch($raw, '(?im)^\s*#{2,}\s*✅')) {
            $errors.Add("${rel}: há uma seção '## ✅ Concluído' no quadro. ✅ é transitório — drene a entrega para o changelog e pode a linha (§7.1.1, Drenagem).")
        }
    }

    foreach ($w in $warnings) { Write-Host "!  $w" -ForegroundColor Yellow }

    if ($errors.Count -gt 0) {
        Write-Host "X  $($errors.Count) problema(s) em $($quadros.Count) quadro(s):" -ForegroundColor Red
        $errors | Sort-Object | ForEach-Object { Write-Host "   $_" -ForegroundColor Red }
        exit 1
    }

    Write-Host "OK  $($quadros.Count) quadro(s) verificado(s), 0 problemas." -ForegroundColor Green
    exit 0
}
finally {
    Pop-Location
}
