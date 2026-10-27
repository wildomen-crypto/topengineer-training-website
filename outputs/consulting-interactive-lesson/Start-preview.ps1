$ProjectRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../..'))
& (Join-Path $ProjectRoot 'tools/Start-Interactive-Lesson.ps1') @args
