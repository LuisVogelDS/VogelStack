# Cria (ou atualiza) um atalho .lnk para uma build do jogo. Molde: GobbleGoblin/Ferramentas/atalho_vale_floresta.ps1.
# O arquivo e so ASCII de proposito: o PowerShell 5.1 le script sem BOM como ANSI.
#
# Uso:
#   pwsh -NoProfile -File atalho.ps1 -Exe "C:\...\Builds\Jogo\GobbleGoblin.exe" -Nome "Gobble Goblin"
#   pwsh -NoProfile -File atalho.ps1 -Procurar -Projeto "C:\...\galinha" -Nome "Galinha (dev)" -Argumentos "-mapa Vale" -Log "Logs\atalho.log"
#   ... -Pasta "C:\pasta\de\teste" -DryRun        # testa sem tocar na area de trabalho
#
# -Exe        caminho do .exe da build
# -Procurar   com -Projeto, usa o .exe mais novo de <Projeto>\Builds (ignora UnityCrashHandler)
# -Nome       nome do atalho, sem .lnk
# -Argumentos argumentos de linha de comando do jogo (ex.: "-mapa ValeFloresta -fps")
# -Log        caminho (relativo ao projeto, ou absoluto) passado ao jogo como -logFile
# -Pasta      onde gravar o .lnk (padrao: a area de trabalho do usuario)
# -DryRun     so mostra o que faria
param(
    [string]$Exe,
    [switch]$Procurar,
    [string]$Projeto = (Get-Location).Path,
    [Parameter(Mandatory = $true)][string]$Nome,
    [string]$Argumentos = "",
    [string]$Log = "",
    [string]$Pasta = [Environment]::GetFolderPath("Desktop"),
    [switch]$DryRun
)
$ErrorActionPreference = "Stop"

if ($Procurar) {
    $b = Join-Path $Projeto "Builds"
    $c = Get-ChildItem -Path $b -Recurse -Filter *.exe -ErrorAction SilentlyContinue |
        Where-Object { $_.Name -notlike "UnityCrashHandler*" } |
        Sort-Object LastWriteTime -Descending | Select-Object -First 1
    if (-not $c) { Write-Error "nenhum .exe em $b (gere a build pela fila antes)"; exit 1 }
    $Exe = $c.FullName
}
if (-not $Exe) { Write-Error "informe -Exe ou -Procurar"; exit 1 }
if (-not (Test-Path -LiteralPath $Exe)) { Write-Error "nao achei o exe: $Exe"; exit 1 }
$Exe = (Resolve-Path -LiteralPath $Exe).Path

$args_ = $Argumentos
if ($Log) {
    $logAbs = if ([System.IO.Path]::IsPathRooted($Log)) { $Log } else { Join-Path $Projeto $Log }
    $args_ = ($args_ + " -logFile `"$logAbs`"").Trim()
}

$destino = Join-Path $Pasta ($Nome + ".lnk")
Write-Output "atalho: $destino"
Write-Output "  alvo: $Exe"
Write-Output "  args: $args_"
if ($DryRun) { Write-Output "  (dry-run: nada gravado)"; exit 0 }

New-Item -ItemType Directory -Force -Path $Pasta | Out-Null
$ws = New-Object -ComObject WScript.Shell
$lnk = $ws.CreateShortcut($destino)
$lnk.TargetPath = $Exe
$lnk.Arguments = $args_
$lnk.WorkingDirectory = Split-Path -Parent $Exe
$lnk.IconLocation = $Exe
$lnk.Save()
Write-Output "gravado."
