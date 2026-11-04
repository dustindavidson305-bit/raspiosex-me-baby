#!/bin/bash
# ============================================================
#  RaspIOSex Me Baby - Linux installer
#  Installs to ~/.local/share/raspiosex-me-baby (no root needed)
#
#  REQUIREMENTS - READ BEFORE FLASHING:
#    * microSD card: 8 GB minimum, 16 GB or larger recommended
#      (32 GB ideal). The OS image itself is about 6.7 GB once
#      extracted, so an 8 GB card is the floor.
#    * Disk space: the OS download (about 1.4 GB), the extracted
#      image (about 6.7 GB) and Etcher (about 0.2 GB) together
#      stay under 10 GB.
#    * Python 3.9+ (preinstalled on almost every distro).
#      For the format option: 'dosfstools' (FAT32) and
#      'exfatprogs' (exFAT) packages.
# ============================================================
set -e
SRC="$(cd "$(dirname "$0")" && pwd)"
DEST="$HOME/.local/share/raspiosex-me-baby"
BIN="$HOME/.local/bin"
APPS="$HOME/.local/share/applications"

echo "Installing RaspIOSex Me Baby to $DEST ..."
echo
echo "REQUIREMENT: microSD card 8 GB minimum, 16 GB recommended (32 GB ideal)."
echo "REQUIREMENT: about 10 GB free disk space for the OS image + Etcher."
echo

# Python is part of the install stack: if python3 is missing, it is
# installed automatically with the distro's package manager.
if ! command -v python3 >/dev/null 2>&1; then
  echo "python3 not found - installing it with your package manager ..."
  if command -v apt-get >/dev/null 2>&1; then
    sudo apt-get update && sudo apt-get install -y python3
  elif command -v dnf >/dev/null 2>&1; then
    sudo dnf install -y python3
  elif command -v pacman >/dev/null 2>&1; then
    sudo pacman -S --noconfirm python
  elif command -v zypper >/dev/null 2>&1; then
    sudo zypper install -y python3
  fi
fi
if ! command -v python3 >/dev/null 2>&1; then
  echo "Python 3 could not be installed automatically. Install it with"
  echo "your package manager (package name: python3), then re-run."
  exit 1
fi

mkdir -p "$DEST" "$BIN" "$APPS"
cp "$SRC/raspiosex_me_baby.py" "$DEST/"
cp "$SRC/uninstall_linux.sh" "$DEST/"
chmod +x "$DEST/uninstall_linux.sh"

cat > "$DEST/run.sh" <<EOF
#!/bin/bash
exec python3 "$DEST/raspiosex_me_baby.py" "\$@"
EOF
chmod +x "$DEST/run.sh"
ln -sf "$DEST/run.sh" "$BIN/raspiosex-me-baby"

cat > "$APPS/raspiosex-me-baby.desktop" <<EOF
[Desktop Entry]
Type=Application
Name=RaspIOSex Me Baby
Comment=Download, verify and flash Raspberry Pi OS (with Etcher)
Exec=$DEST/run.sh
Terminal=true
Categories=Utility;
EOF

echo
echo "Installed. Run it from your applications menu, or in a terminal:"
echo "  raspiosex-me-baby"
echo "First run: option 1 downloads Raspberry Pi OS from the official"
echo "raspberrypi.com feed, option 3 gets Etcher, then flash."
echo "TIP: the built-in writer (option 5) needs: sudo raspiosex-me-baby flash"
