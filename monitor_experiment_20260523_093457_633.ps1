$logFile = "C:\Users\Administrator\Desktop\aettl-research\experiments\monitor_phase3.log"
$doneFile = "C:\Users\Administrator\Desktop\aettl-research\experiments\phase3_done.txt"

while ($true) {
    if (Test-Path $doneFile) {
        $ts = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        Add-Content $logFile "[$ts] phase3_done.txt detected, triggering postprocess..."
        python "C:\Users\Administrator\Desktop\aettl-research\postprocess_phase3.py" 2>&1 | Add-Content $logFile
        break
    }
    Start-Sleep -Seconds 60
}