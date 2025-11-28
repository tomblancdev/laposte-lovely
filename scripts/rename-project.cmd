@echo off
REM Windows CMD script to rename project components (cross-platform alternative)
REM Usage: rename-project.cmd [NewProjectName]

setlocal enabledelayedexpansion
cd /d %~dp0\..

REM Get new name from argument or prompt
set NEW_NAME=%1
:prompt_name
if "%NEW_NAME%"=="" (
    echo Let's give your project a shiny new name!
    set /p NEW_NAME=Enter the new project name (Ctrl + C to cancel):
    if "%NEW_NAME%"=="" (
        echo Don't be shy, your project deserves a name!
        goto prompt_name
    )
)

REM Slugify: lowercase, replace spaces with _, remove non-alphanum/underscore/hyphen
set SLUGIFIED_NAME=%NEW_NAME%
REM Convert to lowercase (requires powershell)
for /f "delims=" %%A in ('powershell -Command "'%NEW_NAME%'.ToLower()"') do set SLUGIFIED_NAME=%%A
REM Replace spaces and invalid chars with _
set SLUGIFIED_NAME=%SLUGIFIED_NAME: =_%
for %%C in ("!SLUGIFIED_NAME!") do (
    set SLUGIFIED_NAME=!SLUGIFIED_NAME!
)
REM Remove non-alphanum/underscore/hyphen using powershell
for /f "delims=" %%A in ('powershell -Command "$s='%SLUGIFIED_NAME%'; -join ($s -replace '[^a-z0-9_-]', '_')"') do set SLUGIFIED_NAME=%%A
REM Trim leading/trailing underscores using powershell
for /f "delims=" %%A in ('powershell -Command "$s='%SLUGIFIED_NAME%'; $s -replace '^_+', '' -replace '_+$', ''"') do set SLUGIFIED_NAME=%%A

if not "%NEW_NAME%"=="%SLUGIFIED_NAME%" (
    echo The project name should be slugified.
    echo Suggested name: %SLUGIFIED_NAME%
    set /p USE_SUGGESTED=Use suggested name? [Y/n]:
    if /I "%USE_SUGGESTED%"=="Y" (
        set NEW_NAME=%SLUGIFIED_NAME%
        echo Great choice!
    ) else if "%USE_SUGGESTED%"=="" (
        set NEW_NAME=%SLUGIFIED_NAME%
        echo Great choice!
    ) else (
        :prompt_slug
        set /p NEW_NAME=Enter a slugified project name:
        set SLUGIFIED_NAME=%NEW_NAME%
        for /f "delims=" %%A in ('powershell -Command "$s='%SLUGIFIED_NAME%'; -join ($s -replace '[^a-z0-9_-]', '_')"') do set SLUGIFIED_NAME=%%A
        for /f "delims=" %%A in ('powershell -Command "$s='%SLUGIFIED_NAME%'; $s -replace '^_+', '' -replace '_+$', ''"') do set SLUGIFIED_NAME=%%A
        if "%NEW_NAME%"=="%SLUGIFIED_NAME%" if not "%NEW_NAME%"=="" (
            echo Looks perfect!
        ) else (
            echo Name must be slugified (lowercase, alphanumeric, _, -).
            goto prompt_slug
        )
    )
)

REM Get current project name from docker-compose.production.yml
set CURRENT_NAME=
for /f "tokens=2 delims=:" %%A in ('findstr /r "image:" docker-compose.production.yml') do (
    for /f "tokens=1 delims=_" %%B in ("%%A") do set CURRENT_NAME=%%B
)

REM Print current and new name
echo Current project name: %CURRENT_NAME%
echo New project name: %NEW_NAME%

REM Confirm
set /p CONFIRM=Are you sure you want to rename the project from '%CURRENT_NAME%' to '%NEW_NAME%'? [y/N]:
if /I not "%CONFIRM%"=="Y" (
    echo Renaming cancelled. Maybe next time!
    exit /b 0
)

REM Replace in files
for %%F in (docker-compose.production.yml docker-compose.local.yml .devcontainer\devcontainer.json) do (
    if exist %%F (
        powershell -Command "(Get-Content -Raw '%%F') -replace [regex]::Escape('%CURRENT_NAME%'), '%NEW_NAME%' | Set-Content '%%F'"
    )
)

echo Project renamed successfully to '%NEW_NAME%'!
echo Please review the changes.
echo You may want to rebuild the Docker images with: docker-compose -f docker-compose.local.yml build --no-cache or the VSCode Dev Container.

exit /b 0
