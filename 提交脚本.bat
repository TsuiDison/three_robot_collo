@echo off
setlocal enabledelayedexpansion

:menu
echo Please choose an action:
echo 1. Commit changes
echo 2. Pull and merge changes
echo 3. Discard local changes and pull the latest version
echo 4. Set HTTP/HTTPS proxy (for terminal acceleration)
set /p choice=Enter your choice (1, 2, 3, or 4):

if "%choice%"=="1" (
    set /p commitMsg=Please enter your commit message:
    if "!commitMsg!"=="" (
        echo Commit message cannot be empty.
        pause
        goto menu
    )
    git add .
    git commit -m "!commitMsg!"
    git push origin master
    goto end
) else if "%choice%"=="2" (
    git pull origin master
    git merge origin/master
    goto end
) else if "%choice%"=="3" (
    echo Discarding local changes and pulling the latest version...
    git reset --hard HEAD
    git pull origin master
    goto end
) else if "%choice%"=="4" (
    echo Setting HTTP/HTTPS proxy for terminal acceleration...
    set http_proxy=http://127.0.0.1:7890
    set https_proxy=http://127.0.0.1:7890
    echo Proxy set successfully:
    echo   http_proxy=!http_proxy!
    echo   https_proxy=!https_proxy!
    echo.
    echo Note: This setting is temporary and only valid in this session.
    pause
    goto menu
) else (
    echo Invalid choice, please try again...
    timeout /t 2 >nul
    goto menu
)

:end
pause