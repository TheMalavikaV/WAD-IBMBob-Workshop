#!/usr/bin/env python3
"""Workshop setup checker. No dependencies; works on Windows, macOS and Linux.

    python check-setup/check_setup.py      (Windows)
    python3 check-setup/check_setup.py     (macOS / Linux)
"""
import re
import shutil
import socket
import subprocess
import sys

OK, WARN, FAIL = "OK  ", "WARN", "FAIL"
problems = []


def report(status, name, detail):
    print(f"[{status}] {name:<10} {detail}")
    if status == FAIL:
        problems.append(name)


def version_of(cmd, args=("--version",)):
    exe = shutil.which(cmd)
    if not exe:
        return None, None
    try:
        out = subprocess.run([exe, *args], capture_output=True, text=True, timeout=20)
    except (OSError, subprocess.SubprocessError) as exc:
        return exe, f"could not run: {exc}"
    text = (out.stdout or "") + (out.stderr or "")
    return exe, text.strip().splitlines()[0] if text.strip() else ""


def major_minor(text):
    m = re.search(r"(\d+)\.(\d+)", text or "")
    return (int(m.group(1)), int(m.group(2))) if m else (0, 0)


def main():
    print("Workshop setup check\n")

    # Python: the interpreter running this script
    py = sys.version_info
    py_text = f"Python {py.major}.{py.minor}.{py.micro} ({sys.executable})"
    report(OK if py >= (3, 10) else FAIL, "python", py_text + ("" if py >= (3, 10) else "  -> need 3.10+"))

    try:
        import venv  # noqa: F401
        import ensurepip  # noqa: F401
        report(OK, "venv", "available")
    except ImportError:
        report(FAIL, "venv", "missing -> Ubuntu/Debian: sudo apt install python3-venv")

    exe, text = version_of("git")
    report(OK if exe else FAIL, "git", text if exe else "not found -> see PREREQUISITES.md")

    exe, text = version_of("node")
    if not exe:
        report(WARN, "node", "not found (optional, only if you solve The Open Slot in Node.js)")
        major = major_minor(text.lstrip("v"))[0]
        report(OK if major >= 18 else FAIL, "node", text + ("" if major >= 18 else "  -> need v18+ (Linux: use nvm)"))

    exe, text = version_of("npm")
    report(OK if exe else WARN, "npm", text if exe else "not found (optional, comes with Node.js)")
    exe, text = version_of("java")
    if not exe:
        report(WARN, "java", "not found (optional, only for Java teams)")
    else:
        major = major_minor(text)[0]
        report(OK if major >= 17 else WARN, "java", text + ("" if major >= 17 else "  -> 17+ needed for `java Main.java`"))

    # Port 5001 is used by the web apps in this workshop
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.bind(("127.0.0.1", 5001))
        report(OK, "port 5001", "free")
    except OSError:
        report(WARN, "port 5001", "in use - stop the program using it before starting a workshop app")
    finally:
        sock.close()

    print()
    if problems:
        print("NOT READY - fix: " + ", ".join(problems) + "  (see PREREQUISITES.md)")
        return 1
    print("ALL GOOD - you are ready for the workshop.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
