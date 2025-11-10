# SSH-Verbindungsparameter (bitte anpassen)
$User = "jetson"
$Host = "192.168.0.145"
$RemotePath = "~/spino-main/test/lidar"
$CsvDatei = "scan_result.csv"
$LocalPath = ".\$CsvDatei"

Write-Host "Verbinde zu $Host..." -ForegroundColor Cyan

# Python-Skript auf dem Zielsystem ausführen
ssh "$User@$Host" "cd $RemotePath && python3 saveScan.py"

if ($LASTEXITCODE -eq 0) {
    Write-Host "Python-Skript erfolgreich ausgeführt!" -ForegroundColor Green
    
    Write-Host "Übertrage die erzeugte CSV-Datei..." -ForegroundColor Cyan
    
    # CSV-Datei vom Zielsystem herunterladen
    scp "${User}@${Host}:${RemotePath}/${CsvDatei}" $LocalPath
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Vorgang erfolgreich abgeschlossen!" -ForegroundColor Green
        Write-Host "Datei gespeichert unter: $LocalPath" -ForegroundColor Yellow
    } else {
        Write-Host "Fehler beim Übertragen der Datei!" -ForegroundColor Red
    }
} else {
    Write-Host "Fehler beim Ausführen des Python-Skripts!" -ForegroundColor Red
}

Read-Host "Drücke Enter zum Beenden"