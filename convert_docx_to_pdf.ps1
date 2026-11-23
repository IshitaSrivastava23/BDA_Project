$wdFormatPDF = 17
$word = New-Object -ComObject Word.Application
$word.Visible = $false

$docxPath = (Get-Item "BDA_Report_Final_Reference_Style.docx").FullName
$pdfPath = (Join-Path (Get-Location) "BDA_Report_Final_Reference_Style.pdf")

Write-Output "Converting $docxPath to $pdfPath ..."
$doc = $word.Documents.Open($docxPath)
$doc.ExportAsFixedFormat($pdfPath, $wdFormatPDF)
$doc.Close()
$word.Quit()

Write-Output "Successfully converted to PDF!"
