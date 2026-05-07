
$outputPath = "d:\Ton_nhi\ielts_splits\ielts_all_data.js"
$jsContent = "const ALL_IELTS_DATA = {`n"

for ($i = 1; $i -le 11; $i++) {
    $dir = "d:\Ton_nhi\ielts_splits\ielts_data_p$i"
    Write-Host "Processing $dir..."
    if (Test-Path $dir) {
        $files = Get-ChildItem $dir -Filter "*.json"
        $partData = @()
        foreach ($file in $files) {
            try {
                $json = Get-Content $file.FullName -Raw | ConvertFrom-Json
                $partData += $json
            } catch {
                Write-Error "Failed to parse $($file.Name)"
            }
        }
        $jsonString = $partData | ConvertTo-Json -Depth 10
        $jsContent += "  p$($i): $jsonString,"
        if ($i -lt 11) { $jsContent += "`n" }
    } else {
        Write-Warning "$dir not found."
        $jsContent += "  p$($i): [],`n"
    }
}

$jsContent += "`n};"
Set-Content $outputPath $jsContent -NoNewline
Write-Host "Master data file created at $outputPath"
