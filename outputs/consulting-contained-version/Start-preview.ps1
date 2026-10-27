$ProjectRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../..'))
& (Join-Path $ProjectRoot 'tools/Start-Contained.ps1') @args
