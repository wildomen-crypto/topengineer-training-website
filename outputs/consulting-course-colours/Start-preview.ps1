$ProjectRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../..'))
& (Join-Path $ProjectRoot 'tools/Start-Windows.ps1') @args
