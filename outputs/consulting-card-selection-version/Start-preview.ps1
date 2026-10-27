$ProjectRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../..'))
& (Join-Path $ProjectRoot 'tools/Start-Card-Selection.ps1') @args
