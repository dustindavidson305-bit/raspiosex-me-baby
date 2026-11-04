#!/bin/bash
# ============================================================
#  RaspIOSex Me Baby - macOS installer
#  Installs to ~/Applications/RaspIOSex-Me-Baby (no admin needed)
#
#  REQUIREMENTS - READ BEFORE FLASHING:
#    * microSD card: 8 GB minimum, 16 GB or larger recommended
#      (32 GB ideal). The OS image itself is about 6.7 GB once
#      extracted, so an 8 GB card is the floor.
#    * Disk space on this Mac: the OS download (about 1.4 GB),
#      the extracted image (about 6.7 GB) and Etcher (about
#      0.2 GB) together stay under 10 GB.
#    * Python 3.9+ (macOS may offer the free Command Line Tools
#      the first time you run python3, or get it from python.org)
# ============================================================
set -e
SRC="$(cd "$(dirname "$0")" && pwd)"
DEST="$HOME/Applications/RaspIOSex-Me-Baby"

echo "Installing RaspIOSex Me Baby to $DEST ..."
echo
echo "REQUIREMENT: microSD card 8 GB minimum, 16 GB recommended (32 GB ideal)."
echo "REQUIREMENT: about 10 GB free disk space for the OS image + Etcher."
echo

# Python is part of the install stack: if python3 is missing, the
# official Python package is downloaded from python.org and installed
# automatically (asks for your Mac password once, for sudo).
if ! command -v python3 >/dev/null 2>&1; then
  echo "python3 not found - installing Python from python.org ..."
  PKG="/tmp/python-3.15.2-macos11.pkg"
  if curl -fL -o "$PKG" "https://www.python.org/ftp/python/3.15.2/python-3.15.2-macos11.pkg"; then
    sudo installer -pkg "$PKG" -target /
    rm -f "$PKG"
  fi
fi
if ! command -v python3 >/dev/null 2>&1; then
  echo "Python could not be installed automatically. Run"
  echo "'xcode-select --install' for Apple's free Command Line Tools,"
  echo "or install Python from https://www.python.org, then re-run."
  exit 1
fi

mkdir -p "$DEST"
cp "$SRC/raspiosex_me_baby.py" "$DEST/"
cp "$SRC/uninstall_macos.command" "$DEST/"
chmod +x "$DEST/uninstall_macos.command"

cat > "$HOME/Desktop/RaspIOSex Me Baby.command" <<EOF
#!/bin/bash
cd "$DEST" && python3 raspiosex_me_baby.py
EOF
chmod +x "$HOME/Desktop/RaspIOSex Me Baby.command"

echo
echo "Installed. Launch 'RaspIOSex Me Baby' from your Desktop."
echo "First run: option 1 downloads Raspberry Pi OS from the official"
echo "raspberrypi.com feed, option 3 gets Etcher, then flash."
echo "TIP: the built-in writer (option 5) needs: sudo python3 $DEST/raspiosex_me_baby.py flash"
