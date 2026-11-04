#!/bin/bash
# RaspIOSex Me Baby - macOS uninstaller
# Removes the app, the downloaded OS image + Etcher, and the launcher.
DEST="$HOME/Applications/RaspIOSex-Me-Baby"
echo "This removes RaspIOSex Me Baby, including the downloaded OS image"
echo "and Etcher stored in $DEST/library."
read -r -p "Continue? (y/n): " OK
case "$OK" in
  y|Y) ;;
  *) echo "Cancelled."; exit 0 ;;
esac
rm -f "$HOME/Desktop/RaspIOSex Me Baby.command"
rm -rf "$DEST"
echo "RaspIOSex Me Baby removed."
