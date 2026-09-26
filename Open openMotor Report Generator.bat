@echo off
setlocal

set "OPENMOTOR_DIR=%~dp0"
set "PYTHON=%OPENMOTOR_DIR%.venv\Scripts\python.exe"
set "REPORT_TOOL=%OPENMOTOR_DIR%tools\openmotor_report.py"
set "CONFIG=%OPENMOTOR_DIR%Rocket_Pedro4b_report.yaml"

if not exist "%REPORT_TOOL%" (
    echo The openMotor report generator was not found.
    echo Expected: %REPORT_TOOL%
    pause
    exit /b 1
)

if not exist "%PYTHON%" (
    echo The openMotor Python environment is missing.
    echo Expected: %PYTHON%
    pause
    exit /b 1
)

if /i "%~1"=="--check" (
    "%PYTHON%" "%REPORT_TOOL%" --help >nul
    if errorlevel 1 exit /b 1
    echo Report generator launcher is ready.
    exit /b 0
)

pushd "%OPENMOTOR_DIR%"
if exist "%CONFIG%" (
    "%PYTHON%" "%REPORT_TOOL%" gui "%CONFIG%"
) else (
    "%PYTHON%" "%REPORT_TOOL%" gui
)
set "EXIT_CODE=%ERRORLEVEL%"
popd

if not "%EXIT_CODE%"=="0" (
    echo.
    echo The openMotor report generator exited with error code %EXIT_CODE%.
    pause
)

endlocal & exit /b %EXIT_CODE%
