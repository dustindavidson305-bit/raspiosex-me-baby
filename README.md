# RaspIOSex Me Baby

One toolkit that puts **Raspberry Pi OS + balenaEtcher** on your computer
and flashes a microSD card — for **Windows, macOS and Linux**.

## What it does

1. **Downloads Raspberry Pi OS from the official source** — it reads the
   same `os_list` feed from downloads.raspberrypi.com that the official
   Raspberry Pi Imager uses, so you always get the current official build,
   never a random mirror. You pick the variant (Desktop, Lite, Full,
   32/64-bit, Legacy).
2. **Verifies checksums** — the download and the extracted image are
   checked against the official SHA-256 values.
3. **Extracts the image itself** — Raspberry Pi OS ships as a compressed
   disk image (`.img.xz`), not an ISO. The toolkit decompresses it with
   built-in XZ support, so no separate unzip program is needed. (ZIP
   support is also built in — it's how Etcher is unpacked.)
4. **Downloads balenaEtcher from its official GitHub releases**, unpacks
   it, and can launch it pointed at your image — or flash with the
   **built-in writer** if you prefer.
5. **Format / wipe options** for spare cards: FAT32, exFAT (and EXT4 on
   Linux), single full-card partition or wipe-only, custom volume label.
6. **Uninstaller included** for every platform (and an uninstall option
   inside the app that clears the downloaded OS + Etcher).

## Requirements — read this first

- **microSD card: 8 GB minimum, 16 GB or larger recommended (32 GB
  ideal).** The recommended Desktop image is ~6.7 GB once extracted, so
  8 GB is the floor; a bigger card gives the Pi room for updates and
  your files.
- **Disk space on your computer: under 10 GB total.** Current official
  figures for the recommended build (Raspberry Pi OS 64-bit Desktop,
  2026-10-06 / Debian Trixie):
  - OS download (`.img.xz`): **1.36 GB**
  - Extracted image (`.img`): **6.74 GB**
  - Etcher: **~0.2–0.3 GB** depending on platform
  - **Total ≈ 8.3 GB peak** — inside the 10 GB budget. The app warns you
    if you pick a "Full" variant that would break the budget (Full's
    extracted image alone is ~10 GB).
- **Python 3.9 or newer** — part of the install stack: if it's missing,
  the installer installs it automatically (the official python.org
  build, currently 3.15.2, on Windows/macOS; your distro's python3
  package on Linux). No pip packages needed — standard library only.
- Administrator/sudo rights are needed only for the built-in writer and
  the format option (Etcher asks for them itself).

## Install

One installer for every system. Download the installer package (or
clone this repo), then run the starter for your system:

| System  | Run this |
|---------|----------|
| Windows | double-click `Setup-Windows.bat` |
| macOS   | double-click `Setup-Mac.command` (right-click → Open the first time) |
| Linux   | `bash Setup-Linux.sh` |

The starter only makes sure Python 3 is present (installing it if
needed), then hands over to **one universal installer**,
`RaspIOSex-Me-Baby-Setup.py`. The installer **detects whether you're on
Windows, macOS or Linux and installs the matching version** — the right
install folder, shortcuts/launchers and uninstaller for your system:

- Windows: `%LOCALAPPDATA%\RaspIOSex-Me-Baby`, Desktop + Start Menu
  shortcuts, and an entry in Settings → Apps
- macOS: `~/Applications/RaspIOSex-Me-Baby` + a Desktop launcher
- Linux: `~/.local/share/raspiosex-me-baby`, a `raspiosex-me-baby`
  command, and an applications-menu entry

**Uninstall:** run the uninstaller placed in the install folder, or
`RaspIOSex-Me-Baby-Setup.py --uninstall`.

*(Developers: `build_installer.py` rebuilds the Setup file with the
current app embedded.)*

## First run

1. Launch **RaspIOSex Me Baby**.
2. Option **1** — download Raspberry Pi OS (checksum-verified), then let
   it extract (option **2** if you skipped it).
3. Option **3** — download + unpack Etcher.
4. Option **4** — flash with Etcher (guided), or option **5** — the
   built-in writer (it lists your disks, refuses system disks, and makes
   you type the disk name before erasing anything).

Command-line use also works, e.g. `raspiosex_me_baby.py download`,
`extract`, `etcher`, `flash`, `format`, `sizes`, `uninstall`.

## Safety notes

- Flashing and formatting **erase the target disk completely**. The
  built-in writer only lists disks, highlights removable ones, refuses
  system disks, and requires you to type the exact disk identifier
  before writing. Always double-check the size matches your card.
- Only download sources are used: downloads.raspberrypi.com and
  github.com/balena-io/etcher. Nothing else is contacted.

## Developer

Built by **Delukz** — RaspIOSex Me Baby v1.0.0 (2026).
The toolkit itself is MIT-licensed (see `LICENSE`). Raspberry Pi OS and
balenaEtcher are downloaded from their official sources at install time
and remain under their own licenses.
