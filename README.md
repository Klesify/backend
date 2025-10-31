## Klesify backend — Quick start

This README describes how to clone the repository, prepare a Python environment, install dependencies, and run the backend application.

### Prerequisites
- Git (to clone the repository)
- Python 3.11 or newer recommended (3.10 may work but some dependencies may require newer versions)

If Python is not installed, download it from python.org and install for your platform. On Windows, enable "Add Python to PATH" during installation or use the installer option to add it to PATH.

### Clone the repo
Open a terminal and run:

```bash
# clone the repository (replace the URL with your repo URL)
git clone <repo path>
cd klesify/backend
```

### Create and activate a virtual environment (recommended)
Use a virtual environment to avoid modifying the system Python environment.

POSIX/macOS (bash):
```bash
python -m venv .venv
source .venv/bin/activate
```

Windows (Command Prompt):
```bat
python -m venv .venv
.venv\Scripts\activate.bat
```

Windows (PowerShell):
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Note: this project ignores `.venv/` in git (check `.gitignore`).

### Install dependencies
With the virtual environment active, install the pinned dependencies from `requirements.txt`:

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

If you add or update packages locally and want to update `requirements.txt`, either append a single pinned package:

```bash
# example: append current installed fastapi version
echo "fastapi==$(python -c 'import fastapi; print(fastapi.__version__)')" >> requirements.txt
```

or regenerate the full snapshot (overwrites `requirements.txt`):

```bash
pip freeze > requirements.txt
```

### Run the app
If the project entry point is `main.py` in this folder, run:

```bash
python main.py
```

If the app uses Uvicorn to serve FastAPI, run (common for FastAPI projects):

```bash
uvicorn main:app --reload
# or if app variable is in app.py: uvicorn app:app --reload
```

### Notes and troubleshooting
- Make sure your virtual environment is active before installing or running, otherwise packages will be installed system-wide or not found.
- If `python` maps to an older Python on your system, use `python3` or the full path to the desired interpreter.
- If package installation fails, check your network, pip version, and whether any system packages (C toolchain) are required for binary wheels.

### Contact / Next steps
If you want, I can:
- append a single package to `requirements.txt` after you `pip install` it locally, or
- regenerate `requirements.txt` from your environment and commit the change.

---
README created on October 31, 2025.
