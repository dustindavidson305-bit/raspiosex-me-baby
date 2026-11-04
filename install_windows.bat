@echo off
REM ============================================================
REM  RaspIOSex Me Baby - Windows installer
REM  Installs to %LOCALAPPDATA%\RaspIOSex-Me-Baby (no admin needed)
REM
REM  REQUIREMENTS - READ BEFORE FLASHING:
REM    * microSD card: 8 GB minimum, 16 GB or larger recommended
REM      (32 GB ideal). The OS image itself is about 6.7 GB once
REM      extracted, so an 8 GB card is the floor.
REM    * Disk space on this PC: the OS download (about 1.4 GB),
REM      the extracted image (about 6.7 GB) and Etcher (about
REM      0.3 GB) together stay under 10 GB.
REM    * Python 3.9 or newer (free from https://www.python.org)
REM ============================================================
setlocal
set "DEST=%LOCALAPPDATA%\RaspIOSex-Me-Baby"
echo Installing RaspIOSex Me Baby to %DEST% ...
echo.
echo REQUIREMENT: microSD card 8 GB minimum, 16 GB recommended (32 GB ideal).
echo REQUIREMENT: about 10 GB free disk space for the OS image + Etcher.
echo.

REM --- Python is part of the install stack: if it is missing, the
REM --- official Python installer is downloaded from python.org and
REM --- run automatically (per-user, no admin needed).
py -3 --version >nul 2>&1
if %errorlevel%==0 set "PYCMD=py -3"
if not defined PYCMD (
  python --version >nul 2>&1
  if %errorlevel%==0 set "PYCMD=python"
)
if not defined PYCMD (
  echo Python 3 not found - installing it now from python.org ...
  set "PYEXE=%TEMP%\python-3.15.2-amd64.exe"
  powershell -NoProfile -Command "Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.15.2/python-3.15.2-amd64.exe' -OutFile '%PYEXE%'"
  if exist "%PYEXE%" (
    "%PYEXE%" /passive InstallAllUsers=0 PrependPath=1 Include_launcher=1
    del "%PYEXE%" >nul 2>&1
  )
  py -3 --version >nul 2>&1
  if %errorlevel%==0 set "PYCMD=py -3"
  if not defined PYCMD (
    python --version >nul 2>&1
    if %errorlevel%==0 set "PYCMD=python"
  )
)
if not defined PYCMD (
  echo Python 3 could not be installed automatically. Install it free
  echo from https://www.python.org/downloads/ then run this installer again.
  pause
  exit /b 1
)
echo Found Python: %PYCMD%

mkdir "%DEST%" 2>nul
copy /Y "%~dp0raspiosex_me_baby.py" "%DEST%\" >nul
copy /Y "%~dp0uninstall_windows.bat" "%DEST%\" >nul

REM --- Launcher batch ---
> "%DEST%\run.bat" echo @echo off
>>"%DEST%\run.bat" echo %PYCMD% "%DEST%\raspiosex_me_baby.py" %%*
>>"%DEST%\run.bat" echo pause

REM --- Shortcuts (Desktop + Start Menu) ---
powershell -NoProfile -Command "$ws = New-Object -ComObject WScript.Shell; $s = $ws.CreateShortcut([Environment]::GetFolderPath('Desktop') + '\RaspIOSex Me Baby.lnk'); $s.TargetPath = '%DEST%\run.bat'; $s.WorkingDirectory = '%DEST%'; $s.Save(); $sm = [Environment]::GetFolderPath('StartMenu') + '\Programs\RaspIOSex Me Baby.lnk'; $s2 = $ws.CreateShortcut($sm); $s2.TargetPath = '%DEST%\run.bat'; $s2.WorkingDirectory = '%DEST%'; $s2.Save()"

REM --- Add/Remove Programs entry (per-user, no admin needed) ---
reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Uninstall\RaspIOSex-Me-Baby" /v DisplayName /t REG_SZ /d "RaspIOSex Me Baby (Raspberry Pi OS + Etcher)" /f >nul
reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Uninstall\RaspIOSex-Me-Baby" /v UninstallString /t REG_SZ /d "\"%DEST%\uninstall_windows.bat\"" /f >nul
reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Uninstall\RaspIOSex-Me-Baby" /v InstallLocation /t REG_SZ /d "%DEST%" /f >nul

echo.
echo Installed. Launch "RaspIOSex Me Baby" from your Desktop or Start Menu.
echo First run: choose option 1 to download Raspberry Pi OS from the
echo official raspberrypi.com feed, then option 3 for Etcher, then flash.
echo TIP: for the built-in writer (option 5), right-click the shortcut
echo and "Run as administrator". Etcher (option 4) asks for admin itself.
pause
