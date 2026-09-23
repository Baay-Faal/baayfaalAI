# Script PowerShell d'Installation de l'Agent Baay-Faal en Tâche Planifiée / Service Windows
# Permet de lancer l'agent automatiquement au démarrage de la session, silencieusement en arrière-plan.

$TaskName = "BaayFaalAgentService"
$ProjectPath = Resolve-Path "$PSScriptRoot\.."
$PythonExe = (Get-Command python).Source

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "   INSTALLATION DU SERVICE WINDOWS AUTONOME - BAAY-FAAL" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "Chemin du projet : $ProjectPath"
Write-Host "Interprète Python : $PythonExe"

# Suppression de la tâche si elle existe déjà
Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false -ErrorAction SilentlyContinue

# Définition de l'action de la tâche planifiée (exécute main.py)
$Action = New-ScheduledTaskAction -Execute $PythonExe -Argument "main.py" -WorkingDirectory $ProjectPath

# Définition du déclencheur (Au démarrage de la session utilisateur)
$Trigger = New-ScheduledTaskTrigger -AtLogon

# Définition des paramètres d'exécution silencieuse
$Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -ExecutionTimeLimit 0

# Enregistrement de la tâche
Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Trigger -Settings $Settings -Description "Service natif 24h/24 pour l'Agent IA local Baay-Faal."

Write-Host "`n[SUCCÈS] L'Agent Baay-Faal est configuré comme service silencieux Windows." -ForegroundColor Green
Write-Host "Il se démarrera automatiquement à chaque ouverture de session." -ForegroundColor Green
