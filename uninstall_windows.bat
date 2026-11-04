@echo off
REM RaspIOSex Me Baby - Windows uninstaller
REM Removes the app, the downloaded OS image + Etcher, shortcuts,
REM and the Add/Remove Programs entry.
setlocal
set "DEST=%LOCALAPPDATA%\RaspIOSex-Me-Baby"
echo This removes RaspIOSex Me Baby, including the downloaded OS image
echo and Etcher stored in %DEST%\library.
set /p OK="Continue? (y/n): "
if /I not "%OK%"=="y" exit /b 0

powershell -NoProfile -Command "Remove-Item ([Environment]::GetFolderPath('Desktop') + '\RaspIOSex Me Baby.lnk') -ErrorAction SilentlyContinue; Remove-Item ([Environment]::GetFolderPath('StartMenu') + '\Programs\RaspIOSex Me Baby.lnk') -ErrorAction SilentlyContinue"
reg delete "HKCU\Software\Microsoft\Windows\CurrentVersion\Uninstall\RaspIOSex-Me-Baby" /f >nul 2>&1

cd /d "%TEMP%"
rmdir /s /q "%DEST%"
echo.
echo RaspIOSex Me Baby removed.
pause
