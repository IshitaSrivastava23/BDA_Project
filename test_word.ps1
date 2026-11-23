$word = New-Object -ComObject Word.Application
$word.Visible = $false
Write-Output "Word COM Application successfully created: $($word.Name) Version: $($word.Version)"
$word.Quit()
