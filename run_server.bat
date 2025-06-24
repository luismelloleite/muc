@echo off
cd /D "%~dp0"
setlocal

netstat -ano | findstr "LISTENING" | findstr ":8000" > nul

if %errorlevel% equ 0 (
    start "" http://127.0.0.1:8000
    exit /b
) else (

    call venv\Scripts\activate.bat
    if errorlevel 1 (
        exit /b 1
    )

    start "Waitress_MUC_Portaria" /B pythonw -m waitress --host 127.0.0.1 --port 8000 portaria_muc.wsgi:application > waitress.log 2>&1

    ping -n 2 127.0.0.1 > nul
    start "" http://127.0.0.1:8000
    exit /b
)
endlocal
