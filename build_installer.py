#!/usr/bin/env python3
"""
Builds RaspIOSex-Me-Baby-Setup.py — the universal installer.

The Setup file is a single self-contained Python program with the whole
app (raspiosex_me_baby.py) embedded as a compressed payload. Run it on
Windows, macOS or Linux: it detects the machine's OS and installs the
matching version of the app (right install folder, launchers, shortcuts
and uninstaller for that OS).

Usage:  python3 build_installer.py
"""

import base64
import zlib
from pathlib import Path

HERE = Path(__file__).resolve().parent
APP_SRC = HERE / "raspiosex_me_baby.py"
OUT = HERE / "RaspIOSex-Me-Baby-Setup.py"

TEMPLATE = r'''#!/usr/bin/env python3
# RaspIOSex Me Baby - universal installer (Windows / macOS / Linux).
#
# One file: it detects the machine it is running on and installs the
# matching version of the app - the right install folder, launchers,
# shortcuts and uninstaller for that OS. The app itself is embedded
# below as a compressed payload; nothing else is needed.
#
#   Install:    python3 RaspIOSex-Me-Baby-Setup.py
#   Uninstall:  python3 RaspIOSex-Me-Baby-Setup.py --uninstall
# (On Windows use "py -3" instead of "python3". Python 3.9+ required.)

import base64
import os
import platform
import shutil
import subprocess
import sys
import zlib
from pathlib import Path

APP_NAME = "RaspIOSex Me Baby"
APP_VERSION = "1.0.0"
APP_FILE = "raspiosex_me_baby.py"
PUBLISHER = "Delukz"

PAYLOAD_B64 = "@@PAYLOAD@@"

SD_NOTE = ("SD / microSD card required for flashing: 8 GB minimum, "
           "16 GB recommended (the app shows the exact size for the "
           "image you pick).")


def detect_os():
    s = platform.system().lower()
    if s.startswith("win"):
        return "windows"
    if s == "darwin":
        return "macos"
    return "linux"


def os_label(os_id):
    return {"windows": "Windows", "macos": "macOS", "linux": "Linux"}[os_id]


def app_source():
    return zlib.decompress(base64.b64decode(PAYLOAD_B64)).decode("utf-8")


def locations(os_id):
    home = Path.home()
    if os_id == "windows":
        root = Path(os.environ.get("LOCALAPPDATA",
                                   home / "AppData" / "Local"))
        base = root / "RaspIOSex-Me-Baby"
    elif os_id == "macos":
        base = home / "Applications" / "RaspIOSex-Me-Baby"
    else:
        base = home / ".local" / "share" / "raspiosex-me-baby"
    return home, base


def write_app(base):
    (base / "library").mkdir(parents=True, exist_ok=True)
    app = base / APP_FILE
    app.write_text(app_source(), encoding="utf-8")
    return app


def make_executable(path):
    try:
        mode = os.stat(path).st_mode
        os.chmod(path, mode | 0o111)
    except OSError:
        pass


# ---------------------------------------------------------------- Windows
def install_windows(home, base):
    app = write_app(base)
    pycmd = "py -3" if shutil.which("py") else "python"
    run_bat = base / "run.bat"
    run_bat.write_text("@echo off\n" + pycmd + ' "%~dp0' + APP_FILE + '" %*\n',
                       encoding="utf-8")
    desktop_link = home / "Desktop" / "RaspIOSex Me Baby.lnk"
    startmenu = (Path(os.environ.get("APPDATA", home / "AppData" / "Roaming"))
                 / "Microsoft" / "Windows" / "Start Menu" / "Programs")
    startmenu.mkdir(parents=True, exist_ok=True)
    start_link = startmenu / "RaspIOSex Me Baby.lnk"
    linked = False
    for link in (desktop_link, start_link):
        try:
            ps = ("$s=(New-Object -ComObject WScript.Shell).CreateShortcut('"
                  + str(link) + "');$s.TargetPath='" + str(run_bat)
                  + "';$s.WorkingDirectory='" + str(base) + "';$s.Save()")
            subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy",
                            "Bypass", "-Command", ps],
                           check=True, capture_output=True, timeout=60)
            linked = True
        except Exception:
            pass
    if not linked:
        (home / "Desktop" / "RaspIOSex Me Baby.bat").write_text(
            '@echo off\ncall "' + str(run_bat) + '"\npause\n',
            encoding="utf-8")
    uninstall_bat = base / "uninstall.bat"
    uninstall_bat.write_text(
        "@echo off\n"
        "cd /d %TEMP%\n"
        'del "%USERPROFILE%\\Desktop\\RaspIOSex Me Baby.lnk" 2>nul\n'
        'del "%USERPROFILE%\\Desktop\\RaspIOSex Me Baby.bat" 2>nul\n'
        'del "%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\'
        'RaspIOSex Me Baby.lnk" 2>nul\n'
        'reg delete "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\'
        'Uninstall\\RaspIOSexMeBaby" /f 2>nul\n'
        'rmdir /s /q "%LOCALAPPDATA%\\RaspIOSex-Me-Baby"\n'
        "echo RaspIOSex Me Baby removed.\n"
        "pause\n",
        encoding="utf-8")
    try:
        import winreg
        key = winreg.CreateKey(
            winreg.HKEY_CURRENT_USER,
            "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\"
            "RaspIOSexMeBaby")
        winreg.SetValueEx(key, "DisplayName", 0, winreg.REG_SZ,
                          APP_NAME + " " + APP_VERSION)
        winreg.SetValueEx(key, "Publisher", 0, winreg.REG_SZ, PUBLISHER)
        winreg.SetValueEx(key, "InstallLocation", 0, winreg.REG_SZ,
                          str(base))
        winreg.SetValueEx(key, "UninstallString", 0, winreg.REG_SZ,
                          '"' + str(uninstall_bat) + '"')
        winreg.CloseKey(key)
    except Exception:
        pass
    return ('Double-click "RaspIOSex Me Baby" on the Desktop or in the '
            "Start Menu.")


# ------------------------------------------------------------------ macOS
def install_macos(home, base):
    app = write_app(base)
    make_executable(app)
    launcher = base / "RaspIOSex Me Baby.command"
    launcher.write_text(
        "#!/bin/sh\n"
        'python3 "' + str(app) + '"\n'
        "echo\n"
        "echo 'Press any key to close.'\n"
        "read -n 1 -s\n",
        encoding="utf-8")
    make_executable(launcher)
    desk = home / "Desktop" / "RaspIOSex Me Baby.command"
    try:
        shutil.copyfile(launcher, desk)
        make_executable(desk)
    except OSError:
        pass
    uninstaller = base / "Uninstall RaspIOSex Me Baby.command"
    uninstaller.write_text(
        "#!/bin/sh\n"
        "cd /tmp\n"
        'rm -f "$HOME/Desktop/RaspIOSex Me Baby.command"\n'
        'rm -rf "$HOME/Applications/RaspIOSex-Me-Baby"\n'
        "echo 'RaspIOSex Me Baby removed.'\n",
        encoding="utf-8")
    make_executable(uninstaller)
    return 'Double-click "RaspIOSex Me Baby" on the Desktop.'


# ------------------------------------------------------------------ Linux
def install_linux(home, base):
    app = write_app(base)
    make_executable(app)
    bin_dir = home / ".local" / "bin"
    bin_dir.mkdir(parents=True, exist_ok=True)
    link = bin_dir / "raspiosex-me-baby"
    try:
        if link.exists() or link.is_symlink():
            link.unlink()
        os.symlink(app, link)
    except OSError:
        link.write_text('#!/bin/sh\nexec python3 "' + str(app) + '" "$@"\n',
                        encoding="utf-8")
        make_executable(link)
    apps_dir = home / ".local" / "share" / "applications"
    apps_dir.mkdir(parents=True, exist_ok=True)
    (apps_dir / "raspiosex-me-baby.desktop").write_text(
        "[Desktop Entry]\n"
        "Type=Application\n"
        "Name=RaspIOSex Me Baby\n"
        "Comment=Download and flash Raspberry Pi OS with balenaEtcher\n"
        "Exec=" + str(app) + "\n"
        "Terminal=true\n"
        "Categories=Utility;\n",
        encoding="utf-8")
    uninstaller = base / "uninstall.sh"
    uninstaller.write_text(
        "#!/bin/sh\n"
        "cd /tmp\n"
        'rm -f "$HOME/.local/bin/raspiosex-me-baby"\n'
        'rm -f "$HOME/.local/share/applications/raspiosex-me-baby.desktop"\n'
        'rm -rf "$HOME/.local/share/raspiosex-me-baby"\n'
        "echo 'RaspIOSex Me Baby removed.'\n",
        encoding="utf-8")
    make_executable(uninstaller)
    return "Run it from your applications menu, or type: raspiosex-me-baby"


# -------------------------------------------------------------- uninstall
def uninstall(os_id):
    home, base = locations(os_id)
    if os_id == "windows":
        for p in (home / "Desktop" / "RaspIOSex Me Baby.lnk",
                  home / "Desktop" / "RaspIOSex Me Baby.bat",
                  Path(os.environ.get("APPDATA",
                                      home / "AppData" / "Roaming"))
                  / "Microsoft" / "Windows" / "Start Menu" / "Programs"
                  / "RaspIOSex Me Baby.lnk"):
            try:
                p.unlink()
            except OSError:
                pass
        try:
            import winreg
            winreg.DeleteKey(
                winreg.HKEY_CURRENT_USER,
                "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\"
                "RaspIOSexMeBaby")
        except Exception:
            pass
    elif os_id == "macos":
        try:
            (home / "Desktop" / "RaspIOSex Me Baby.command").unlink()
        except OSError:
            pass
    else:
        for p in (home / ".local" / "bin" / "raspiosex-me-baby",
                  home / ".local" / "share" / "applications"
                  / "raspiosex-me-baby.desktop"):
            try:
                p.unlink()
            except OSError:
                pass
    shutil.rmtree(base, ignore_errors=True)
    print(APP_NAME + " removed from " + str(base))


def main():
    if sys.version_info < (3, 9):
        print("Python 3.9 or newer is required.")
        return 1
    os_id = detect_os()
    if "--uninstall" in sys.argv:
        uninstall(os_id)
        return 0
    home, base = locations(os_id)
    print("=" * 64)
    print(APP_NAME + " " + APP_VERSION + " - universal installer")
    print("Detected operating system: " + os_label(os_id)
          + " - installing the " + os_label(os_id) + " version.")
    print("Install folder: " + str(base))
    print("=" * 64)
    if os_id == "windows":
        how = install_windows(home, base)
    elif os_id == "macos":
        how = install_macos(home, base)
    else:
        how = install_linux(home, base)
    try:
        shutil.copyfile(Path(__file__).resolve(),
                        base / "RaspIOSex-Me-Baby-Setup.py")
    except OSError:
        pass
    print()
    print("Installed. " + how)
    print(SD_NOTE)
    print("Uninstall any time with the uninstaller in the install "
          "folder, or run this Setup again with --uninstall.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
'''


def main():
    app_bytes = APP_SRC.read_bytes()
    payload = base64.b64encode(zlib.compress(app_bytes, 9)).decode("ascii")
    chunks = [payload[i:i + 76] for i in range(0, len(payload), 76)]
    payload_block = "(\n" + "\n".join(f'    "{c}"' for c in chunks) + "\n)"
    setup_src = TEMPLATE.replace('PAYLOAD_B64 = "@@PAYLOAD@@"',
                                 "PAYLOAD_B64 = " + payload_block)
    compile(setup_src, str(OUT), "exec")  # syntax check before writing
    OUT.write_text(setup_src, encoding="utf-8")
    print(f"Wrote {OUT} ({OUT.stat().st_size:,} bytes); "
          f"embedded app is {len(app_bytes):,} bytes.")


if __name__ == "__main__":
    main()
