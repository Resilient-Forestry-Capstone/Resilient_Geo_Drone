@echo off
SETLOCAL EnableDelayedExpansion

REM Enable ANSI escape sequences
reg add HKCU\Console /v VirtualTerminalLevel /t REG_DWORD /d 1 /f >nul 2>&1

REM Define colors with ESC character
for /F %%a in ('echo prompt $E ^| cmd') do set "ESC=%%a"
set "GREEN=%ESC%[32m"
set "RED=%ESC%[31m"
set "RESET=%ESC%[0m"


echo %GREEN%Starting QGIS Environment Setup...%RESET%

echo   %GREEN%Checking Python Edition...%RESET%

REM Get Python version dynamically
FOR /F "tokens=* USEBACKQ" %%F IN (`python -c "import sys; print(f'{sys.version_info.major}{sys.version_info.minor}')"`) DO (
    SET PYVER=%%F
)

echo     %GREEN%Python Version: %PYVER% %RESET%

echo   %GREEN%Creating Python Virtual Environment...%RESET%

REM Create and activate virtual environment
python -m venv .venv
CALL .venv\Scripts\activate
IF %ERRORLEVEL% NEQ 0 (
    echo %RED%Error: Virtual environment activation failed.%RESET%
    exit /b 1
)

echo     %GREEN%Virtual Environment Created And Activated.%RESET%

REM Set Python paths
SET "PATH=%USERPROFILE%\AppData\Roaming\Python\Python%PYVER%\Scripts;%PATH%"
SET "PYTHONPATH=C:\Program Files\QGIS 3.40.1\apps\qgis\python;%PYTHONPATH%"

echo   %GREEN%Initializing QGIS Dependency Linker .bat...%RESET%

REM Call QGIS initialization
CALL "C:\Program Files\QGIS 3.40.1\bin\python-qgis.bat"
IF %ERRORLEVEL% NEQ 0 (
    echo %RED%Error: QGIS Initialization Failed.%RESET%
    exit /b 1%
)

echo     %GREEN%Linked All Dependencies For QGIS.%RESET%

echo   %GREEN%Pip Installing All Needed Dependencies For Codebase...%RESET%

REM Install requirements with error checking
python -m pip install -r requirements.txt --no-cache-dir --quiet --disable-pip-version-check
IF %ERRORLEVEL% NEQ 0 (
    echo %RED%Error: Package installation failed.%RESET%
    exit /b 1
)

echo     %GREEN%Installed All Dependencies.%RESET%

echo %GREEN%Environment Setup Complete.%RESET%
echo %GREEN%Running Pipeline...%RESET%

python "%~dp0main.py" --input "%~dp0data\raw\Bellarmine" --output "%~dp0data\output"

echo %GREEN%Done Running Pipeline.%RESET%

ENDLOCAL
pause