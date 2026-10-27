param(
    [ValidateRange(1024,65535)][int]$Port = 8776,
    [string]$PhpPath = '',
    [switch]$NoBrowser,
    [switch]$SmokeTest
)
$ErrorActionPreference = 'Stop'
$ProjectRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
$SiteRoot = Join-Path $ProjectRoot 'outputs/consulting-interactive-lesson'
$RuntimeRoot = Join-Path $ProjectRoot '.runtime'
$PortablePhp = Join-Path $RuntimeRoot 'php84/php.exe'
$RouterPath = Join-Path $ProjectRoot 'work/consulting-interactive-lesson/preview_order_router.php'
$ServerUrl = "http://127.0.0.1:$Port/"
New-Item -ItemType Directory -Path $RuntimeRoot -Force | Out-Null

if (-not $PhpPath) {
    $InstalledPhp = Get-Command php -ErrorAction SilentlyContinue
    if (Test-Path -LiteralPath $PortablePhp) { $PhpPath = $PortablePhp }
    elseif ($InstalledPhp) { $PhpPath = $InstalledPhp.Source }
    else {
        Write-Host 'Downloading official PHP for local preview...'
        [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
        $ArchivePath = Join-Path $RuntimeRoot 'php84.zip'
        Invoke-WebRequest -UseBasicParsing -Uri 'https://downloads.php.net/~windows/releases/php-8.4.27-nts-Win32-vs17-x64.zip' -OutFile $ArchivePath
        $ExpectedHash = '93bd8a815a52156606fb906d0573437908c61f96e2cc52c03a51e36a41bf5236'
        if ((Get-FileHash -LiteralPath $ArchivePath -Algorithm SHA256).Hash.ToLowerInvariant() -ne $ExpectedHash) { throw 'PHP archive checksum mismatch. Download not used.' }
        Expand-Archive -LiteralPath $ArchivePath -DestinationPath (Join-Path $RuntimeRoot 'php84') -Force
        $PhpPath = $PortablePhp
    }
}

if ($PhpPath -eq $PortablePhp) {
    $ExtensionDirectory = (Join-Path $RuntimeRoot 'php84/ext').Replace('\','/')
    $IniText = @"
extension_dir="$ExtensionDirectory"
extension=mbstring
extension=openssl
extension=pdo_sqlite
extension=sqlite3
extension=gd
extension=fileinfo
extension=zip
date.timezone=Europe/Belgrade
memory_limit=256M
max_execution_time=45
display_errors=Off
log_errors=On
"@
    [IO.File]::WriteAllText((Join-Path $RuntimeRoot 'php84/php.ini'),$IniText,(New-Object Text.UTF8Encoding($false)))
}

$RuntimeCheckFile = Join-Path $RuntimeRoot 'check-runtime.php'
[IO.File]::WriteAllText($RuntimeCheckFile,'<?php echo PHP_VERSION_ID >= 80100 && extension_loaded("mbstring") && extension_loaded("pdo_sqlite") && extension_loaded("dom") && extension_loaded("gd") && class_exists("ZipArchive") ? "READY" : "MISSING_EXTENSIONS";',(New-Object Text.UTF8Encoding($false)))
$RuntimeCheck = & $PhpPath $RuntimeCheckFile
if ($LASTEXITCODE -ne 0 -or $RuntimeCheck -ne 'READY') { throw 'PHP 8.1+ with DOM, mbstring, PDO_SQLite, GD and ZipArchive is required. See README.md.' }
if (-not (Test-Path -LiteralPath (Join-Path $SiteRoot 'training-order/vendor/dompdf/autoload.inc.php'))) { throw 'PDF dependency is missing. Restore the full repository or run prepare_order_runtime.py and rebuild.' }
if (Get-NetTCPConnection -State Listen -LocalPort $Port -ErrorAction SilentlyContinue) { throw "Port $Port is already used. Close the earlier preview or use a free port, for example -Port 8777." }

# Only generic preview settings are loaded. Real payment settings remain outside Git.
$ExamplePath = (Join-Path $SiteRoot 'training-order/settings.example.php').Replace('\','/').Replace("'","\'")
$ConfigPath = Join-Path $RuntimeRoot 'preview-settings-interactive-lesson.php'
$ConfigText = "<?php`n`$config=require '$ExamplePath';`n`$config['mode']='preview';`n`$config['allowed_origins']=['http://127.0.0.1:$Port','http://localhost:$Port'];`nreturn `$config;`n"
[IO.File]::WriteAllText($ConfigPath,$ConfigText,(New-Object Text.UTF8Encoding($false)))
$PreviousConfig = $env:TRAINING_ORDER_CONFIG
$PreviousData = $env:TRAINING_ORDER_DATA_DIR
$env:TRAINING_ORDER_CONFIG = $ConfigPath
$env:TRAINING_ORDER_DATA_DIR = Join-Path $env:LOCALAPPDATA 'TopEngineer/training-order-preview-interactive-lesson'
$PreviewProcess = $null
try {
    $PreviewProcess = Start-Process -FilePath $PhpPath -ArgumentList @('-S',"127.0.0.1:$Port",'-t',('"'+$SiteRoot+'"'),('"'+$RouterPath+'"')) -WorkingDirectory $SiteRoot -WindowStyle Hidden -PassThru -RedirectStandardOutput (Join-Path $RuntimeRoot "preview-$Port.out.log") -RedirectStandardError (Join-Path $RuntimeRoot "preview-$Port.err.log")
    $Ready = $false
    for ($Attempt=0; $Attempt -lt 30; $Attempt++) {
        if ($PreviewProcess.HasExited) { throw 'Preview server stopped. Check .runtime preview logs.' }
        try {
            $ConfigReply = Invoke-RestMethod -Uri ($ServerUrl+'training-order/api.php?action=config') -TimeoutSec 2
            if ($ConfigReply.mode -eq 'preview') { $Ready=$true; break }
        } catch { Start-Sleep -Milliseconds 200 }
    }
    if (-not $Ready) { throw 'Preview server did not become ready.' }
    Write-Host "TopEngineer is running at $ServerUrl"
    if ($SmokeTest) { Write-Host 'Preview API verified. Payments disabled.'; return }
    if (-not $NoBrowser) { Start-Process $ServerUrl }
    Write-Host 'Keep this window open. Press Ctrl+C to stop the preview.'
    $PreviewProcess.WaitForExit()
} finally {
    if ($PreviewProcess -and -not $PreviewProcess.HasExited) { Stop-Process -Id $PreviewProcess.Id }
    $env:TRAINING_ORDER_CONFIG = $PreviousConfig
    $env:TRAINING_ORDER_DATA_DIR = $PreviousData
}
