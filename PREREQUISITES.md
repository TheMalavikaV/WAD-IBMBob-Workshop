# Prerequisites

Please do this **before** the workshop (it takes 10-15 minutes, mostly downloads).

| Tool | Minimum version | Needed for |
|---|---|---|
| Git | any recent | everything |
| Python | **3.10+** | ClaimsFlow, the setup checker and the greenfield checkers |
| Node.js | **18+** (LTS recommended) | One Purchase, One Line; optional for greenfield problems |
| Java (JDK) | 17+ *(optional)* | only if your team wants to solve a greenfield problem in Java |
| An editor | - | VS Code or whatever you like |
| Your AI coding agent | - | as instructed by the facilitators; make sure you can log in from **your own** machine |

No Docker, no databases, no cloud accounts are needed.

---

## Windows (10/11)

Open **PowerShell** and run:

```powershell
winget install Git.Git
winget install Python.Python.3.12
winget install OpenJS.NodeJS.LTS
# optional, only for Java teams:
winget install Microsoft.OpenJDK.17
```

**Then close and reopen the terminal** so the new tools are on your `PATH`.

Notes:
- Use `python` (or the launcher `py`). If typing `python` or `python3` opens the **Microsoft Store**, the
  real Python is not on your PATH: reopen the terminal, or turn off the "App execution aliases" for
  python.exe / python3.exe in *Settings → Apps → Advanced app settings → App execution aliases*.
- If PowerShell refuses to run `.venv\Scripts\Activate.ps1`, run this once:
  `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`

## macOS

1. Install Homebrew from **https://brew.sh** (copy the one-line installer from that page).
   macOS may ask to install the **Xcode Command Line Tools**: click *Install* and wait for it to finish.
2. Then:
   ```bash
   brew install git python node
   # optional, only for Java teams:
   brew install openjdk@17
   ```
   (`brew info openjdk@17` prints one extra `ln -sfn ...` command if you want the system `java` to find it.)

Use `python3` (not `python`) on macOS.

## Linux

**Ubuntu / Debian**
```bash
sudo apt update && sudo apt install -y git python3 python3-venv python3-pip
# optional, only for Java teams:
sudo apt install -y openjdk-17-jdk
```

**Fedora / RHEL**
```bash
sudo dnf install -y git python3 python3-pip nodejs
# optional, only for Java teams:
sudo dnf install -y java-17-openjdk-devel
```

**Node.js on Linux: use nvm.** Distribution packages are often older than Node 18.
```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh | bash
# close and reopen the terminal, then:
nvm install --lts
nvm use --lts
```

Use `python3` (not `python`) on Linux.

---

## Verify your setup

| Check | Windows | macOS / Linux | Expect |
|---|---|---|---|
| Git | `git --version` | `git --version` | any version |
| Python | `python --version` (or `py --version`) | `python3 --version` | 3.10 or higher |
| Node.js | `node --version` | `node --version` | v18 or higher |
| npm | `npm --version` | `npm --version` | any version |
| Java *(optional)* | `java --version` | `java --version` | 17 or higher |

Or run the checker from the root of this repo, which does all of the above:

```
python check-setup/check_setup.py      # Windows
python3 check-setup/check_setup.py     # macOS / Linux
```

It ends with `ALL GOOD` (or tells you exactly what is missing).

---

## Common problems

| Symptom | Fix |
|---|---|
| `python: command not found` (macOS/Linux) | Use `python3`. |
| `python` opens the Microsoft Store (Windows) | Reopen the terminal after installing, use `py`, or disable the App execution aliases (see above). |
| `error: externally-managed-environment` from pip | You are installing into the system Python (macOS Homebrew, Ubuntu 23.04+, Debian 12+). Create and activate a virtual environment first (each problem's README shows how). |
| `The virtual environment was not created successfully because ensurepip is not available` (Ubuntu/Debian) | `sudo apt install python3-venv` |
| `...Activate.ps1 cannot be loaded because running scripts is disabled` (Windows) | `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`, then try again. |
| `node --version` shows v12/v16 (Linux) | Install a current LTS with nvm (see above). |
| `Address already in use` / port busy | All workshop apps use port **5001** (macOS AirPlay takes 5000). Stop whatever is on 5001, or start the app on another port as described in its README. |
| Corporate proxy blocks `pip install` / `npm install` | Ask the facilitators; ClaimsFlow needs only Flask, One Purchase, One Line needs nothing from npm. |
