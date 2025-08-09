## ----------------------------------------------------------------------
##              !! DO NOT RUN THIS SCRIPT DIRECTLY !!
## This script must be executed using the *specific* Python interpreter
## that should be embedded in the virtual environment.
## For example:
##   /usr/bin/python3.12 ./setup_env.py
##
## -----
## Sets up a Python virtual environment, installs required packages,
## configures starter files, and manages VSCode extensions.
##
## Intended for use on the ENG209 virtual machine infrastructure.
## It may not work out-of-the-box on personal machines,
## as local VM images might not automatically mount the
## 'myfiles' directory at ~/Desktop/myfiles.
##
## Version: 2025-08-04
## ----------------------------------------------------------------------

import argparse
import glob
import json
import logging
import os
import shutil
import subprocess
import sys
import time
import urllib.request
import venv
import zipfile
from http.client import HTTPSConnection
from urllib.parse import urlparse, urljoin
from pathlib import Path

# === Config ===
PYTHON_VERSION = "3.12.2"
DEFAULT_TARGET_FOLDER = os.environ.get("DEFAULT_TARGET_FOLDER", Path.home() / "Desktop" / "myfiles")
SEMESTER = "2025"
GITHUB_PROJECT = os.environ.get("GITHUB_PROJECT", f"https://github.com/eng209/eng209_2025")
CODE_ARCHIVE = f"{GITHUB_PROJECT}/archive/main.zip"
COURSE_NAME = f"eng209_{SEMESTER}"
COURSE_NAME = os.environ.get("COURSE_NAME", f"eng209_2025")
VENV_DIR = "venv"
PACKAGES = [
    "ipykernel", "ipywidgets", "jupyterlab-latex", "matplotlib", "plotly",
    "numpy", "pandas", "scikit-learn", "func_timeout", "bpython", "mypy", "nbformat"
]
VSCODE_EXTENSIONS = {
    "install": [
        "ms-python.python", "ms-python.black-formatter", "ms-python.mypy-type-checker",
        "matangover.mypy", "jock.svg"
    ],
    "uninstall": ["formulahendry.code-runner"]
}
# === ===

logger: logging.Logger


class LogFormatter(logging.Formatter):
    SYMBOLS = {
        logging.DEBUG: "?",   #ALT 🪲, 🐛
        logging.INFO: "✓",
        logging.WARNING: "!", #ALT ⚠
        logging.ERROR: "✗",
        logging.CRITICAL: "✖" #ALT 💥, 🔥
    }


    COLORS = {
        logging.DEBUG:    "\033[1;90m",  # Bright black
        logging.INFO:     "\033[1;32m",  # Green
        logging.WARNING:  "\033[1;33m",  # Yellow
        logging.ERROR:    "\033[1;31m",  # Red
        logging.CRITICAL: "\033[41m\033[97m", # White on red bg
    }
    RESET = "\033[0m"
    BOLD  = "\033[1m"

    def __init__(self, use_color=True):
        super().__init__()
        self.use_color = use_color and sys.stdout.isatty()

    def format(self, record):
        label = self.SYMBOLS.get(record.levelno, "?")
        message = record.getMessage()
        prefix = ''
        if message.startswith('\r') and sys.stdout.isatty():
            prefix = '\r'
        message = message.lstrip('\r')
        if self.use_color:
            color = self.COLORS.get(record.levelno, "")
            label = color + label + self.RESET
            positions = [message.find(c) for c in "(:" if c in message]
            if not positions:
               message = self.BOLD + message + self.RESET
            else:
               pos = min(positions)
               message = self.BOLD + message[:pos] + self.RESET + message[pos:]
        #record.msg = f"{prefix}{label} {message}"
        #return super().format(record)
        return f"{prefix}{label} {message}"

class ProgressBar:
    SPINNER = "|/-\\"

    def __init__(self, width, fill='*', verbose=False):
        self.width = width
        self.fill = fill
        self.verbose = verbose
        self.position = 0
        self.is_terminal = sys.stdout.isatty()

    def update(self, progress):
        if self.verbose or not self.is_terminal:
            return

        spinner_char = self.SPINNER[progress % len(self.SPINNER)]
        dots = '.' * self.width
        fill = self.fill * self.width

        if progress == 0:
            bar = f"   \033[90m{dots}\033[0m{spinner_char}\033[1D"
            print(bar, end='', flush=True)
        else:
            filled_part = fill[:progress]
            empty_part = dots[progress:]
            bar = f"\r   \033[1;31m{filled_part}\033[0;90m{empty_part}\033[0m{spinner_char}\033[1D"
            print(bar, end='', flush=True)

    def finish(self):
        if not (self.verbose or not self.is_terminal):
            print('\r' + ' ' * (self.width + 5) + '\r', end='', flush=True)


def setup_logger():
    logger = logging.getLogger()
    handler = logging.StreamHandler(sys.stdout) # sys.stderr is default
    formatter = LogFormatter("%(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    return logger


def run(cmd, verbose=False, **kwargs):
    if verbose:
        return subprocess.run(cmd, check=True, text=True, **kwargs)
    else:
        return subprocess.run(cmd, check=True, text=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, **kwargs)

def download_github_zip(url, output_filename):
    logger.info(f"Download archive: {url}")
    req = urllib.request.Request(url, headers={"User-Agent": "Client"})
    try:
        with urllib.request.urlopen(req) as response, open(output_filename, 'wb') as out_file:
            shutil.copyfileobj(response, out_file)
        logger.debug(f"Downloaded ({url}) → ({output_filename})")
    except Exception as e:
        raise Exception(f"Download failed: {url}\n{e}")

def extract_archive(path, extract_to, overwrite=False, verbose=False):
    import time
    logger.info(f"Extract class materials: {path} to {extract_to}")
    if extract_to.exists():
        if overwrite:
            logger.warning(f"Overwrite existing files")
        else:
            logger.warning(f"Existing files are not updated (use --force)")
 
    with zipfile.ZipFile(str(path), 'r') as zip_ref:
        members = zip_ref.infolist()
        root_prefix = members[0].filename.split('/')[0] + '/'
        progress = ProgressBar(width=10, fill='*', verbose=verbose)
        progress.update(0)
        for i, member in enumerate(members, 1):
            relative_path = os.path.relpath(member.filename, root_prefix)
            target_path = os.path.join(extract_to, relative_path)
            if member.is_dir():
                continue
            if overwrite or not os.path.exists(target_path):
                os.makedirs(os.path.dirname(target_path), exist_ok=True)
                with open(target_path, 'wb') as f:
                    f.write(zip_ref.read(member))
            else:
                logger.debug(f"Skipped existing file: {target_path}")
            progress.update(int(10.0/len(members)*i))
        progress.finish()


def git_clone_with_retries(url, dest, timeout=15, verbose=False):
    logger.info(f"Cloning project: {url}")
    progress = ProgressBar(width=timeout, fill='X', verbose=verbose)
    start = time.time()
    i = 0
    while time.time() - start < timeout:
        try:
            run(["git", "clone", "--depth", "1", "--branch", "main", "--single-branch", url, str(dest)], verbose=verbose)
            return
        except subprocess.CalledProcessError:
            i += 1
            progress.update(i)
            time.sleep(1)
    progress.finish()
    if not Path(dest).exists():
        raise Exception(f"Failed to clone {url}")

def verify_python(required_version_str):
    required_major, required_minor = map(int, required_version_str.split(".")[:2])
    current_major, current_minor = sys.version_info[:2]

    if (current_major, current_minor) != (required_major, required_minor):
        raise Exception(f"Python {required_major}.{required_minor} required, found {current_major}.{current_minor}")

    logger.info(f"Python OK: {current_major}.{current_minor}")


def verify_vscode(verbose=False):
    try:
        output = run(["code", "--version"], capture_output=True, verbose=True).stdout.strip()
        logger.info(f"VS Code OK: {output.splitlines()[0]}")
        return True
    except Exception as e:
        logger.warning("VS Code not found (Skipping extension setup)")
        return False


def verify_git(verbose=False):
    try:
        output = run(["git", "--version"], capture_output=True, verbose=True).stdout.strip()
        logger.info(f"GIT OK: {output.splitlines()[0]}")
        return True
    except Exception as e:
        logger.warning("Git not found")
        return False


def create_virtualenv(course_path):
    venv_path = course_path / VENV_DIR
    (venv_path / "lib64").mkdir(parents=True, exist_ok=True)
    builder = venv.EnvBuilder(with_pip=True, clear=False, upgrade_deps=True, symlinks=False)
    logger.info(f"Creating venv: {venv_path}")
    builder.create(str(venv_path))
    return venv_path


def install_packages(pip_path, verbose=False):
    logger.info(f"Installing Python packages to venv")
    progress = ProgressBar(width=len(PACKAGES), fill='*', verbose=verbose)
    progress.update(0)
    for i, pkg in enumerate(PACKAGES, 1):
        run([str(pip_path), "install", "--require-virtualenv", "--no-input", pkg], verbose=verbose)
        progress.update(i)
    progress.finish()


def setup_vscode(project_path, venv_path):
    logger.info(f"Configuring VS Code for project")
    for workspace_file in glob.glob("*.code-workspace"):
        os.remove(workspace_file)
    vscode_dir = project_path / ".vscode"
    vscode_dir.mkdir(parents=True, exist_ok=True)
    bindir = "Scripts" if os.name == "nt" else "bin"

    settings = {
        "workbench.editor.showTabs": "multiple",
        "workbench.tree.indent": 20,
        "python.envFile": (Path("${workspaceFolder}") / "venv").as_posix(),
        "python.defaultInterpreterPath": (Path("venv") / bindir / "python").as_posix(),
        "python.terminal.activateEnvironment": True,
        "python.terminal.activateEnvInCurrentTerminal": False,
        "[python]": {
            "editor.formatOnSave": True,
            "editor.defaultFormatter": "ms-python.black-formatter"
        },
        "mypy.checkNotebooks": True,
        "mypy.mypyExecutable": (Path("${workspaceFolder}") / "venv" / bindir / "mypy").as_posix(),
        "mypy.dmypyExecutable": (Path("${workspaceFolder}") / "venv" / bindir / "dmypy").as_posix(),
        "files.watcherExclude": {
            "**/.env": True,
            "**/.git": True,
            "**/.DS_Store": True,
            "**/venv": True,
            "**/.mypy_cache": True,
            "**/.ipynb_checkpoints": True,
            "**/.__pycache__": True,
            "**/*.pyc": True,
        },
        "files.exclude": {
            "**/.env": True,
            "**/.git": True,
            "**/.DS_Store": True,
            "**/venv": True,
            "**/.mypy_cache": True,
            "**/.ipynb_checkpoints": True,
            "**/.__pycache__": True,
            "**/*.pyc": True,
        },
        "search.exclude": {
            "**/.env": True,
            "**/.git": True,
            "**/.DS_Store": True,
            "**/venv": True,
            "**/.mypy_cache": True,
            "**/.ipynb_checkpoints": True,
            "**/.__pycache__": True,
            "**/*.pyc": True,
        },
    }

    with open(vscode_dir / "settings.json", "w") as f:
        json.dump(settings, f, indent=4)

    if os.name == "nt":
        # Windows: assume that VS-code will run cmd.exe otherwise change command to
        # activate with venv\Scripts\activate.ps1 if using PowerShell.
        command = r"call venv\Scripts\activate.bat && venv\Scripts\bpython.exe"
    else:
        # Unix-like
        command = "source venv/bin/activate && exec venv/bin/bpython"

    tasks = {
        "version": "2.0.0",
        "tasks": [
            {
                "label": "bpython",
                "type": "shell",
                "command": command,
                "problemMatcher": [],
                "presentation": {
                    "focus": True,
                    "showReuseMessage": True,
                    "echo": False,
                    "panel": "dedicated"
                }
            }
        ]
    }

    with open(vscode_dir / "tasks.json", "w") as f:
        json.dump(tasks, f, indent=4)


def manage_vscode_extensions(verbose=False):
    logger.info(f"Managing VS Code extensions (user-level)")
    progress = ProgressBar(
        width=len(VSCODE_EXTENSIONS["install"])+len(VSCODE_EXTENSIONS["uninstall"]),
        fill='*', verbose=verbose)
    i = 0
    fail_install = []
    progress.update(i)
    for ext in VSCODE_EXTENSIONS["install"]:
        try:
            run(["code", "--install-extension", ext, "--force"], verbose=verbose)
        except subprocess.CalledProcessError:
            fail_install += [ext]
        i += 1
        progress.update(i)
    fail_uninstall = []
    for ext in VSCODE_EXTENSIONS["uninstall"]:
        try:
            run(["code", "--uninstall-extension", ext], verbose=verbose)
        except subprocess.CalledProcessError:
            fail_uninstall += [ext]
        i += 1
        progress.update(i)
    progress.finish()
    for ext in fail_install:
        logger.warning(f"Could not install VS Code extension '{ext}'")
    for ext in fail_uninstall:
        logger.warning(f"Could not uninstall extension '{ext}' (maybe not installed)")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", metavar="PATH", type=Path, help="Directory where the class folder will be created", default=os.environ.get("ENG209_DIR", DEFAULT_TARGET_FOLDER))
    parser.add_argument("--clone", action="store_true", help="Clone the class folder repository (for instructors or advanced users)")
    parser.add_argument("--force", action="store_true", help="Force update: overwrite existing files in the class folder")
    parser.add_argument("--verbose", action="store_true", help="Show verbose output of subprocess commands")
    args = parser.parse_args()

    global logger
    logger = setup_logger()

    verify_python(PYTHON_VERSION)
    has_git = verify_git()
    has_vscode = verify_vscode(verbose=args.verbose)

    if not args.base.exists():
        raise Exception(f"Target folder {args.base} does not exist")
    logger.info(f"Base folder OK: {args.base}")

    course_path = args.base / COURSE_NAME

    if args.clone:
        if not (course_path / ".git").is_dir():
            if not has_git:
                raise Exception(f"git command not found, cannot clone project")
            if course_path.exists():
                raise Exception(f"cannot clone ({course_path} exists and is not a git repository)")
            git_clone_with_retries(GITHUB_PROJECT + ".git", course_path, verbose=args.verbose)
        else:
            logger.info(f"Using existing project: {course_path}")

    if (course_path / ".git").is_dir():
        if has_git:
            os.chdir(course_path)
            logger.info(f"Updating project: {course_path}")
            run(["git", "pull"], verbose=args.verbose)
        else:
            logger.warning("Git command not found, cannot update existing git project")
    else:
        download_github_zip(CODE_ARCHIVE, args.base / "main.zip")
        extract_archive(args.base / "main.zip", course_path, overwrite=args.force, verbose=args.verbose)
        os.chdir(course_path)

    venv_path = create_virtualenv(course_path)
    pip = venv_path / "bin" / "pip"
    install_packages(pip, verbose=args.verbose)

    setup_vscode(course_path, venv_path)

    if has_vscode:
        manage_vscode_extensions(verbose=args.verbose)
        logger.info("Launching VS Code...")
        run(["code", str(course_path)], verbose=args.verbose)

    logger.info("Project setup complete...") # ✅
    logger.info("You're ready to start coding! 🚀")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.critical("\rInterrupted")
    except SystemExit as e:
        sys.exit(e.code)
    except Exception as e:
        logger.critical(f"Error: {e}")
        sys.exit(1)

