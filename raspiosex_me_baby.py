#!/usr/bin/env python3
"""
RaspIOSex Me Baby — a cross-platform (Windows / macOS / Linux) helper that:

  1. Downloads Raspberry Pi OS from the OFFICIAL Raspberry Pi download feed
     (the same os_list feed the official Raspberry Pi Imager uses).
  2. Downloads balenaEtcher from its OFFICIAL GitHub releases and unpacks it
     (built-in ZIP support — no extra unzip program needed).
  3. Extracts the .img.xz operating-system image (built-in XZ support) while
     verifying its SHA-256 checksum in the same pass.
  4. Flashes the image to a microSD card, either by launching Etcher or with
     the built-in writer.
  5. Formats / wipes a card with filesystem options (FAT32, exFAT, EXT4).

Everything is stored in a "library" folder next to this app so the whole
toolkit — app, OS image and Etcher — stays in one place and uninstalling is
just deleting the folder (uninstall scripts are included).

Size budget (recommended Raspberry Pi OS 64-bit Desktop, Oct 2026 build):
  download (.img.xz)  ~1.36 GB + extracted .img ~6.74 GB + Etcher ~0.21 GB
  = about 8.3 GB peak — inside the 10 GB budget. The "Full" variants are
  bigger and the app warns when a choice would break the 10 GB budget.

microSD card requirement: 8 GB minimum, 16 GB or larger recommended
(32 GB ideal). The installer scripts state this up front, and the app
repeats it before any download or flash.

Pure Python standard library — no pip installs needed. Python 3.9+.
"""

import hashlib
import json
import lzma
import os
import platform
import plistlib
import shutil
import subprocess
import sys
import tarfile
import urllib.request
import zipfile

APP_NAME = "RaspIOSex Me Baby"
VERSION = "1.0.0"
BUDGET_BYTES = 10 * 1000 * 1000 * 1000  # 10 GB budget for OS + Etcher on disk

OS_LIST_URL = "https://downloads.raspberrypi.com/os_list_imagingutility_v4.json"
ETCHER_API = "https://api.github.com/repos/balena-io/etcher/releases/latest"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LIB_DIR = os.path.join(BASE_DIR, "library")
OS_DIR = os.path.join(LIB_DIR, "os")
ETCHER_DIR = os.path.join(LIB_DIR, "etcher")

SYSTEM = platform.system()  # 'Windows', 'Darwin', 'Linux'
MACHINE = platform.machine().lower()

# --------------------------------------------------------------------------
# Small helpers
# --------------------------------------------------------------------------

def gb(n):
    return n / 1000 ** 3

def fmt_size(n):
    if n is None:
        return "unknown size"
    return f"{gb(n):.2f} GB ({n:,} bytes)"

def ensure_dirs():
    for d in (LIB_DIR, OS_DIR, ETCHER_DIR):
        os.makedirs(d, exist_ok=True)

def banner():
    print("=" * 68)
    print(f" {APP_NAME} v{VERSION}  —  Raspberry Pi OS + Etcher, one toolkit")
    print("=" * 68)
    print(" microSD card required: 8 GB minimum, 16 GB recommended (32 GB ideal)")
    print(" On-disk budget for OS image + Etcher: 10 GB (app warns if exceeded)")
    print("=" * 68)

def http_get_json(url):
    req = urllib.request.Request(url, headers={"User-Agent": f"{APP_NAME}/1.0"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode("utf-8"))

def download_file(url, dest, expected_size=None, label="file"):
    """Download with a progress bar. Returns the path written."""
    tmp = dest + ".part"
    req = urllib.request.Request(url, headers={"User-Agent": f"{APP_NAME}/1.0"})
    with urllib.request.urlopen(req, timeout=60) as r:
        total = expected_size or int(r.headers.get("Content-Length") or 0)
        done = 0
        with open(tmp, "wb") as f:
            while True:
                chunk = r.read(1024 * 1024)
                if not chunk:
                    break
                f.write(chunk)
                done += len(chunk)
                if total:
                    pct = done * 100 // total
                    bar = "#" * (pct // 2) + "-" * (50 - pct // 2)
                    print(f"\r  {label}: [{bar}] {pct}%  {fmt_size(done)}", end="", flush=True)
                else:
                    print(f"\r  {label}: {fmt_size(done)} downloaded", end="", flush=True)
    print()
    os.replace(tmp, dest)
    return dest

def sha256_of_file(path, label="verify"):
    h = hashlib.sha256()
    total = os.path.getsize(path)
    done = 0
    with open(path, "rb") as f:
        while True:
            chunk = f.read(1024 * 1024)
            if not chunk:
                break
            h.update(chunk)
            done += len(chunk)
            print(f"\r  {label}: {done * 100 // max(total,1)}%", end="", flush=True)
    print()
    return h.hexdigest()

def ask(prompt, default=None):
    suffix = f" [{default}]" if default else ""
    try:
        val = input(f"{prompt}{suffix}: ").strip()
    except (EOFError, KeyboardInterrupt):
        print()
        return default
    return val if val else default

def confirm(prompt):
    return (ask(prompt + " (y/n)", "n") or "n").lower().startswith("y")

# --------------------------------------------------------------------------
# Raspberry Pi OS catalogue (official feed)
# --------------------------------------------------------------------------

def fetch_os_catalogue():
    """Flatten the official os_list feed into Pi OS image entries."""
    data = http_get_json(OS_LIST_URL)
    out = []

    def walk(items):
        for it in items:
            if it.get("url"):
                out.append(it)
            if it.get("subitems"):
                walk(it["subitems"])

    walk(data.get("os_list", []))
    # Keep only genuine Raspberry Pi OS images (the feed also carries
    # third-party images built on top of it — those are excluded by name).
    return [e for e in out if e.get("name", "").startswith("Raspberry Pi OS")]

def os_local_paths(entry):
    fname = os.path.basename(entry["url"])                 # ....img.xz
    img_name = fname[:-3] if fname.endswith(".xz") else fname + ".img"
    return (os.path.join(OS_DIR, fname), os.path.join(OS_DIR, img_name))

def print_sizes():
    banner()
    print("\nFetching the official Raspberry Pi OS list…")
    entries = fetch_os_catalogue()
    etcher_size = etcher_asset_info(quiet=True)
    print(f"\n{'Image':38} {'Download':>10} {'Extracted':>10} {'+Etcher total':>14}")
    print("-" * 78)
    for e in entries:
        dl = e.get("image_download_size") or 0
        ex = e.get("extract_size") or 0
        total = dl + ex + (etcher_size or 0)
        flag = "" if total <= BUDGET_BYTES else "  <-- OVER the 10 GB budget"
        print(f"{e['name'][:38]:38} {gb(dl):>8.2f} GB {gb(ex):>8.2f} GB {gb(total):>12.2f} GB{flag}")
    print("\nRecommended: 'Raspberry Pi OS (64-bit)' — the standard desktop build.")
    print("microSD: the extracted image size is the minimum card size it fills;")
    print("use an 8 GB card minimum, 16 GB+ recommended so the Pi has room to grow.")

def choose_os():
    print("\nFetching the official Raspberry Pi OS list…")
    entries = fetch_os_catalogue()
    rec = next((i for i, e in enumerate(entries) if e["name"] == "Raspberry Pi OS (64-bit)"), 0)
    for i, e in enumerate(entries):
        dl = e.get("image_download_size") or 0
        ex = e.get("extract_size") or 0
        mark = " (Recommended)" if i == rec else ""
        print(f"  {i+1:2}. {e['name']} — {e.get('release_date','')} — "
              f"download {fmt_size(dl)}, extracted {fmt_size(ex)}{mark}")
    choice = ask("Choose an image number", str(rec + 1))
    try:
        idx = int(choice) - 1
        if 0 <= idx < len(entries):
            return entries[idx]
    except (TypeError, ValueError):
        pass
    print("Invalid choice, using the recommended image.")
    return entries[rec]

def download_os(entry=None):
    ensure_dirs()
    entry = entry or choose_os()
    xz_path, img_path = os_local_paths(entry)
    dl = entry.get("image_download_size") or 0
    ex = entry.get("extract_size") or 0
    etcher_size = etcher_asset_info(quiet=True) or 0
    total = dl + ex + etcher_size
    print(f"\n{entry['name']} ({entry.get('release_date','')})")
    print(f"  Download: {fmt_size(dl)}   Extracted: {fmt_size(ex)}   "
          f"With Etcher ≈ {fmt_size(total)} on disk")
    if total > BUDGET_BYTES:
        print("  WARNING: this variant pushes the toolkit over the 10 GB budget.")
        if not confirm("  Continue anyway?"):
            return None
    if os.path.exists(xz_path) and os.path.getsize(xz_path) == dl and dl:
        print("  Already downloaded — skipping.")
    else:
        print(f"  Source (official): {entry['url']}")
        download_file(entry["url"], xz_path, dl, "OS image")
    want = entry.get("image_download_sha256")
    if want:
        print("  Verifying download checksum…")
        got = sha256_of_file(xz_path, "download checksum")
        if got.lower() != want.lower():
            print("  ERROR: checksum mismatch — download is corrupt. Delete and retry.")
            return None
        print("  Download checksum OK.")
    return entry

def extract_os(entry=None):
    ensure_dirs()
    if entry is None:
        # Pick the first downloaded .img.xz in the library.
        have = [f for f in os.listdir(OS_DIR) if f.endswith(".img.xz")]
        if not have:
            print("No downloaded OS image found — download one first (option 1).")
            return None
        entry = {"name": have[0], "url": "https://local/" + have[0]}
        # Try to recover the official checksum for this file name.
        try:
            for e in fetch_os_catalogue():
                if os.path.basename(e["url"]) == have[0]:
                    entry = e
                    break
        except Exception:
            pass
    xz_path, img_path = os_local_paths(entry)
    if not os.path.exists(xz_path):
        print("Image archive not found — download it first (option 1).")
        return None
    if os.path.exists(img_path):
        print(f"Already extracted: {img_path}")
        return img_path
    print(f"Extracting {os.path.basename(xz_path)} → {os.path.basename(img_path)}")
    print("(Built-in XZ decompression — no separate unzip program needed.)")
    h = hashlib.sha256()
    total = entry.get("extract_size") or 0
    done = 0
    with lzma.open(xz_path, "rb") as src, open(img_path, "wb") as dst:
        while True:
            chunk = src.read(1024 * 1024)
            if not chunk:
                break
            dst.write(chunk)
            h.update(chunk)
            done += len(chunk)
            if total:
                print(f"\r  extract: {done * 100 // total}%  {fmt_size(done)}", end="", flush=True)
    print()
    want = entry.get("extract_sha256")
    if want:
        ok = h.hexdigest().lower() == want.lower()
        print("  Extracted-image SHA-256:", "OK — image is genuine." if ok else "MISMATCH!")
        if not ok:
            os.remove(img_path)
            return None
    print(f"  Done: {img_path} ({fmt_size(os.path.getsize(img_path))})")
    return img_path

# --------------------------------------------------------------------------
# balenaEtcher (official GitHub releases)
# --------------------------------------------------------------------------

def etcher_asset_info(quiet=False):
    """Return (size_bytes) of the right Etcher asset for this platform."""
    try:
        rel = http_get_json(ETCHER_API)
    except Exception:
        return None
    asset = pick_etcher_asset(rel)
    return asset["size"] if asset else None

def pick_etcher_asset(release):
    assets = {a["name"]: a for a in release.get("assets", [])}
    names = list(assets)
    def find(*needles):
        for n in names:
            low = n.lower()
            if all(x in low for x in needles):
                return assets[n]
        return None
    if SYSTEM == "Windows":
        return find("win32", "x64", ".zip") or find("setup", ".exe")
    if SYSTEM == "Darwin":
        if MACHINE in ("arm64", "aarch64"):
            return find("darwin", "arm64", ".zip") or find("arm64", ".dmg")
        return find("darwin", "x64", ".zip") or find("x64", ".dmg")
    # Linux
    return find("linux", "x64", ".zip") or find("amd64", ".deb")

def download_etcher():
    ensure_dirs()
    print("\nChecking the official balenaEtcher releases…")
    rel = http_get_json(ETCHER_API)
    asset = pick_etcher_asset(rel)
    if not asset:
        print("Could not find an Etcher build for this platform automatically.")
        print("Get it manually from https://etcher.balena.io/")
        return None
    dest = os.path.join(ETCHER_DIR, asset["name"])
    print(f"  Etcher {rel.get('tag_name','')} — {asset['name']} ({fmt_size(asset['size'])})")
    print(f"  Source (official): {asset['browser_download_url']}")
    if not os.path.exists(dest):
        download_file(asset["browser_download_url"], dest, asset["size"], "Etcher")
    # Verify against the SHA256SUMS asset published with the release, if any.
    sums = next((a for a in rel.get("assets", []) if a["name"].startswith("SHA256SUMS")), None)
    if sums:
        try:
            txt_path = os.path.join(ETCHER_DIR, sums["name"])
            if not os.path.exists(txt_path):
                download_file(sums["browser_download_url"], txt_path, sums["size"], "checksums")
            want = None
            with open(txt_path) as f:
                for line in f:
                    parts = line.split()
                    if len(parts) == 2 and parts[1].lstrip("*") == asset["name"]:
                        want = parts[0]
            if want:
                got = sha256_of_file(dest, "Etcher checksum")
                print("  Etcher SHA-256:", "OK." if got.lower() == want.lower() else "MISMATCH!")
        except Exception as exc:
            print(f"  (Checksum check skipped: {exc})")
    # Unpack (built-in ZIP support).
    out_dir = os.path.join(ETCHER_DIR, "app")
    if asset["name"].endswith(".zip"):
        if not os.path.exists(out_dir):
            print("  Unpacking Etcher…")
            with zipfile.ZipFile(dest) as z:
                z.extractall(out_dir)
    else:
        out_dir = ETCHER_DIR  # .exe installer / .deb / .rpm used as-is
    print(f"  Etcher ready in: {out_dir if os.path.exists(out_dir) else dest}")
    return dest

def find_extracted_image():
    imgs = [f for f in os.listdir(OS_DIR) if f.endswith(".img")] if os.path.isdir(OS_DIR) else []
    return os.path.join(OS_DIR, imgs[0]) if imgs else None

def launch_etcher():
    img = find_extracted_image()
    app_dir = os.path.join(ETCHER_DIR, "app")
    exe = None
    if os.path.isdir(app_dir):
        for root, _dirs, files in os.walk(app_dir):
            for f in files:
                low = f.lower()
                if low.startswith("balenaetcher") and (low.endswith(".exe") or low.endswith(".appimage")):
                    exe = os.path.join(root, f)
                    break
                if f == "balenaEtcher" and SYSTEM == "Linux":
                    exe = os.path.join(root, f)
            if exe:
                break
    if SYSTEM == "Darwin":
        for root, dirs, _files in os.walk(app_dir if os.path.isdir(app_dir) else ETCHER_DIR):
            for d in dirs:
                if d.lower().endswith(".app") and "etcher" in d.lower():
                    print(f"Opening Etcher…  (image: {img})")
                    subprocess.Popen(["open", os.path.join(root, d)])
                    print("In Etcher: 'Flash from file' → pick the .img, select your SD card, Flash.")
                    return True
    if exe:
        if SYSTEM == "Linux":
            os.chmod(exe, 0o755)
        print(f"Launching Etcher…  (image: {img})")
        subprocess.Popen([exe])
        print("In Etcher: 'Flash from file' → pick the .img, select your SD card, Flash.")
        return True
    print("Etcher app not unpacked yet — run the Etcher download option first,")
    print("or open the downloaded Etcher installer from:", ETCHER_DIR)
    return False

# --------------------------------------------------------------------------
# Disk handling — listing, built-in writer, formatting
# --------------------------------------------------------------------------

def is_admin():
    try:
        if SYSTEM == "Windows":
            import ctypes
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        return os.geteuid() == 0
    except Exception:
        return False

def list_removable_disks():
    """Return a list of dicts: id, label, size, model, removable."""
    disks = []
    try:
        if SYSTEM == "Linux":
            out = subprocess.run(
                ["lsblk", "--json", "-o", "NAME,PATH,SIZE,TYPE,RM,TRAN,MODEL,MOUNTPOINT"],
                capture_output=True, text=True, timeout=30).stdout
            for d in json.loads(out).get("blockdevices", []):
                if d.get("type") == "disk":
                    disks.append({
                        "id": d["path"], "size": d.get("size") or 0,
                        "model": (d.get("model") or "disk").strip(),
                        "removable": bool(d.get("rm")) or (d.get("tran") or "") in ("usb", "mmc"),
                        "mounted": bool(d.get("mountpoint")),
                    })
        elif SYSTEM == "Darwin":
            raw = subprocess.run(["diskutil", "list", "-plist", "external", "physical"],
                                 capture_output=True, timeout=30).stdout
            plist = plistlib.loads(raw)
            for dev in plist.get("AllDisksAndPartitions", []):
                info_raw = subprocess.run(["diskutil", "info", "-plist", dev],
                                          capture_output=True, timeout=30).stdout
                info = plistlib.loads(info_raw)
                disks.append({
                    "id": "/dev/" + dev, "size": info.get("TotalSize") or 0,
                    "model": info.get("MediaName") or "disk",
                    "removable": bool(info.get("RemovableMediaOrExternalDevice")),
                    "mounted": bool(info.get("Mountpoint")),
                })
        elif SYSTEM == "Windows":
            ps = ("Get-Disk | Select-Object Number,FriendlyName,Size,BusType,"
                  "IsSystem,IsBoot | ConvertTo-Json")
            out = subprocess.run(["powershell", "-NoProfile", "-Command", ps],
                                 capture_output=True, text=True, timeout=60).stdout
            rows = json.loads(out)
            if isinstance(rows, dict):
                rows = [rows]
            for r in rows:
                disks.append({
                    "id": f"\\\\.\\PhysicalDrive{r['Number']}",
                    "number": r["Number"],
                    "size": r.get("Size") or 0,
                    "model": r.get("FriendlyName") or "disk",
                    "removable": (r.get("BusType") or "").upper() in ("USB", "SD", "MMC"),
                    "system": bool(r.get("IsSystem") or r.get("IsBoot")),
                    "mounted": True,
                })
    except Exception as exc:
        print(f"Could not list disks automatically ({exc}).")
    return disks

def pick_disk(purpose="flash"):
    disks = list_removable_disks()
    if not disks:
        print("No disks found. Insert the microSD card (in a reader) and try again.")
        return None
    print(f"\nDisks — pick the SD card for {purpose}:")
    for i, d in enumerate(disks):
        tags = []
        if d.get("removable"):
            tags.append("removable")
        if d.get("system"):
            tags.append("SYSTEM — protected")
        print(f"  {i+1}. {d['id']}  {fmt_size(d['size'])}  {d['model']}  {' '.join(tags)}")
    choice = ask("Disk number")
    try:
        d = disks[int(choice) - 1]
    except (TypeError, ValueError, IndexError):
        print("Invalid choice.")
        return None
    if d.get("system"):
        print("That is a system disk — refusing for safety.")
        return None
    if not d.get("removable"):
        print("WARNING: that disk does not report itself as removable.")
        if not confirm("Are you absolutely sure it is the SD card?"):
            return None
    return d

def flash_builtin():
    img = find_extracted_image()
    if not img:
        print("No extracted .img found — download and extract the OS first.")
        return
    if SYSTEM in ("Linux", "Darwin") and not is_admin():
        print("Flashing needs administrator rights. Re-run this app with sudo:")
        print(f"  sudo {sys.executable} {os.path.abspath(__file__)} flash")
        return
    if SYSTEM == "Windows" and not is_admin():
        print("Flashing needs administrator rights. Right-click the app and")
        print("'Run as administrator', then choose the flash option again.")
        return
    d = pick_disk("flashing")
    if not d:
        return
    img_size = os.path.getsize(img)
    if d["size"] and d["size"] < img_size:
        print(f"Card too small: image is {fmt_size(img_size)}, disk is {fmt_size(d['size'])}.")
        print("You need at least an 8 GB card (16 GB recommended).")
        return
    print(f"\nAbout to ERASE {d['id']} ({fmt_size(d['size'])}) and write:")
    print(f"  {img} ({fmt_size(img_size)})")
    typed = ask(f"Type the disk id exactly to continue ({d['id']})")
    if typed != d["id"]:
        print("Name did not match — cancelled, nothing written.")
        return
    if SYSTEM == "Windows":
        # Take the disk offline so Windows lets go of its volumes.
        subprocess.run(["powershell", "-NoProfile", "-Command",
                        f"Set-Disk -Number {d['number']} -IsOffline $true"],
                       capture_output=True, text=True, timeout=60)
    print("Writing… do not remove the card.")
    try:
        target = d["id"]
        if SYSTEM == "Darwin" and target.startswith("/dev/disk"):
            target = "/dev/r" + target[len("/dev/"):]  # raw device = much faster
        with open(img, "rb") as src, open(target, "r+b", buffering=0) as dst:
            done = 0
            while True:
                chunk = src.read(4 * 1024 * 1024)
                if not chunk:
                    break
                dst.write(chunk)
                done += len(chunk)
                print(f"\r  flash: {done * 100 // img_size}%  {fmt_size(done)}", end="", flush=True)
            dst.flush()
            try:
                os.fsync(dst.fileno())
            except Exception:
                pass
        print("\nFlash complete. Eject the card before removing it.")
    except PermissionError:
        print("\nPermission denied — run the app as administrator / with sudo.")
    except OSError as exc:
        print(f"\nWrite failed: {exc}")
    finally:
        if SYSTEM == "Windows":
            subprocess.run(["powershell", "-NoProfile", "-Command",
                            f"Set-Disk -Number {d['number']} -IsOffline $false"],
                           capture_output=True, text=True, timeout=60)

def format_card():
    d = pick_disk("formatting")
    if not d:
        return
    print("\nFilesystem options:")
    print("  1. FAT32  — most compatible; standard for boot/utility cards")
    print("  2. exFAT  — for cards over 32 GB or files over 4 GB")
    print("  3. EXT4   — Linux filesystem (Linux hosts only)" if SYSTEM == "Linux"
          else "  3. (EXT4 is only available on Linux hosts)")
    fs_choice = ask("Choose filesystem", "1")
    fs = {"1": "FAT32", "2": "EXFAT"}.get(fs_choice)
    if fs_choice == "3" and SYSTEM == "Linux":
        fs = "EXT4"
    if not fs:
        print("Invalid choice.")
        return
    print("\nPartition options:")
    print("  1. Single full-card partition (standard)")
    print("  2. Wipe only — clear the partition table, leave card blank")
    part_choice = ask("Choose partition option", "1")
    label = (ask("Volume label", "RASPI") or "RASPI")[:11].upper()
    print(f"\nAbout to ERASE {d['id']} and apply: {fs}, option {part_choice}, label {label}")
    if not confirm("Continue?"):
        print("Cancelled.")
        return
    try:
        if SYSTEM == "Linux":
            base = ["sudo"] if not is_admin() else []
            subprocess.run(base + ["wipefs", "-a", d["id"]], check=False, timeout=120)
            if part_choice == "2":
                print("Partition table cleared.")
                return
            if fs == "FAT32":
                subprocess.run(base + ["mkfs.vfat", "-F", "32", "-n", label, d["id"]],
                               check=True, timeout=600)
            elif fs == "EXFAT":
                subprocess.run(base + ["mkfs.exfat", "-n", label, d["id"]],
                               check=True, timeout=600)
            else:
                subprocess.run(base + ["mkfs.ext4", "-F", "-L", label, d["id"]],
                               check=True, timeout=600)
        elif SYSTEM == "Darwin":
            if part_choice == "2":
                subprocess.run(["diskutil", "zeroDisk", "short", d["id"]], check=True, timeout=600)
                print("Card wiped.")
                return
            fmt = "FAT32" if fs == "FAT32" else "ExFAT"
            subprocess.run(["diskutil", "eraseDisk", fmt, label, "MBRFormat", d["id"]],
                           check=True, timeout=600)
        elif SYSTEM == "Windows":
            if not is_admin():
                print("Formatting needs administrator rights — re-run the app as administrator.")
                return
            script = os.path.join(LIB_DIR, "diskpart.txt")
            lines = [f"select disk {d['number']}", "clean"]
            if part_choice != "2":
                lines += ["create partition primary",
                          f"format fs={fs.lower()} label={label} quick", "assign"]
            with open(script, "w") as f:
                f.write("\n".join(lines) + "\n")
            subprocess.run(["diskpart", "/s", script], check=True, timeout=600)
        print("Format complete. Eject the card before removing it.")
    except subprocess.CalledProcessError as exc:
        print(f"Format failed (exit {exc.returncode}). On Linux, FAT32/exFAT tools come from")
        print("the 'dosfstools' and 'exfatprogs' packages if they are missing.")
    except FileNotFoundError as exc:
        print(f"Missing tool: {exc.filename}. Install it and try again.")

# --------------------------------------------------------------------------
# Uninstall
# --------------------------------------------------------------------------

def uninstall():
    print("\nUninstalling removes the OS image, Etcher and this app's files.")
    print(f"Toolkit folder: {BASE_DIR}")
    if not confirm("Remove all downloaded files (OS image + Etcher) now?"):
        print("Cancelled.")
        return
    if os.path.isdir(LIB_DIR):
        shutil.rmtree(LIB_DIR, ignore_errors=True)
    print("Downloaded files removed.")
    print("To finish: delete the toolkit folder itself, or run the uninstall")
    print("script for your system (uninstall_windows.bat / uninstall_macos.command")
    print("/ uninstall_linux.sh) that came with the app.")

# --------------------------------------------------------------------------
# Menu + CLI
# --------------------------------------------------------------------------

MENU = """
  1. Download Raspberry Pi OS (official site, checksum-verified)
  2. Extract the OS image (.img.xz → .img, checksum-verified)
  3. Download + unpack balenaEtcher (official release)
  4. Flash the SD card with Etcher (guided)
  5. Flash the SD card with the built-in writer (advanced)
  6. Format / wipe an SD card (FAT32 / exFAT / EXT4 options)
  7. Show image sizes and the 10 GB budget
  8. Uninstall (remove downloaded OS + Etcher)
  0. Quit
"""

def menu():
    banner()
    ensure_dirs()
    while True:
        print(MENU)
        choice = ask("Choose an option", "0")
        try:
            if choice == "1":
                entry = download_os()
                if entry and confirm("Extract it now?"):
                    extract_os(entry)
            elif choice == "2":
                extract_os()
            elif choice == "3":
                download_etcher()
            elif choice == "4":
                launch_etcher()
            elif choice == "5":
                flash_builtin()
            elif choice == "6":
                format_card()
            elif choice == "7":
                print_sizes()
            elif choice == "8":
                uninstall()
            elif choice == "0":
                print("Bye.")
                return
            else:
                print("Unknown option.")
        except KeyboardInterrupt:
            print("\nInterrupted.")
        except Exception as exc:
            print(f"Error: {exc}")

def main(argv):
    cmds = {
        "download": lambda: download_os(),
        "extract": lambda: extract_os(),
        "etcher": lambda: download_etcher(),
        "flash-etcher": lambda: launch_etcher(),
        "flash": flash_builtin,
        "format": format_card,
        "sizes": print_sizes,
        "uninstall": uninstall,
    }
    if len(argv) > 1 and argv[1] in cmds:
        ensure_dirs()
        cmds[argv[1]]()
    elif len(argv) > 1:
        print(f"Unknown command '{argv[1]}'. Commands: {', '.join(cmds)} — or no argument for the menu.")
        return 2
    else:
        menu()
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv))
