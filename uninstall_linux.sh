#!/bin/bash
# RaspIOSex Me Baby - Linux uninstaller
# Removes the app, the downloaded OS image + Etcher, the command
# symlink and the applications-menu entry.
DEST="$HOME/.local/share/raspiosex-me-baby"
echo "This removes RaspIOSex Me Baby, including the downloaded OS image"
echo "and Etcher stored in $DEST/library."
read -r -p "Continue? (y/n): " OK
case "$OK" in
  y|Y) ;;
  *) echo "Cancelled."; exit 0 ;;
esac
rm -f "$HOME/.local/bin/raspiosex-me-baby"
rm -f "$HOME/.local/share/applications/raspiosex-me-baby.desktop"
rm -rf "$DEST"
echo "RaspIOSex Me Baby removed."
