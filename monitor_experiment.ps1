$doneFile = "C:\Users\Administrator\Desktop\aettl-research\experiments\phase3_done.txt"
$resultFile = "C:\Users\Administrator\Desktop\aettl-research\experiments\mm_epc_phase3_final.json"
$logFile = "C:\Users\Administrator\Desktop\aettl-research\experiments\phase3_monitor.log"

"$(Get-Date) Monitor started, waiting for $doneFile" | Out-File $logFile -Encoding utf8

while ($true) {
    if (Test-Path $doneFile) {
        "$(Get-Date) Experiment complete signal detected!" | Out-File $logFile -Append -Encoding utf8
        
        Start-Sleep 5  # Wait for file write to complete
        
        if (Test-Path $resultFile) {
            "$(Get-Date) Result file found, running post-processing..." | Out-File $logFile -Append -Encoding utf8
            
            Set-Location "C:\Users\Administrator\Desktop\aettl-research"
            python postprocess_phase3.py 2>&1 | Out-File $logFile -Append -Encoding utf8
            
            "$(Get-Date) Post-processing complete!" | Out-File $logFile -Append -Encoding utf8
        } else {
            "$(Get-Date) ERROR: Result file not found" | Out-File $logFile -Append -Encoding utf8
        }
        break
    }
    
    Start-Sleep 60
}