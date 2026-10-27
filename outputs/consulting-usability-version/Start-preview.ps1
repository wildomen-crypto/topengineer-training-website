$ProjectRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../..'))
& (Join-Path $ProjectRoot 'tools/Start-Usability.ps1') @args
