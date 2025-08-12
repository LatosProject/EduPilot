@echo off
chcp 65001 > nul
setlocal enabledelayedexpansion
set SCRIPT_DIR=%~dp0
set PROJECT_ROOT=%SCRIPT_DIR%..
pushd "%PROJECT_ROOT%\frontend\src"
start "EduPilot Frontend" cmd /k "npm run dev"
pushd "%PROJECT_ROOT%\backend\app"
start "EduPilot Backend" cmd /k "python app.py"
pushd "%PROJECT_ROOT%\desktop"
start "EduPilot Backend" cmd /k "npm start"
popd
pushd "%PROJECT_ROOT%\scripts"
python warmup.py
:end
endlocal
