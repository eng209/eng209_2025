#!/bin/bash

# This setups a Python venv, installs some packages,
# setups some start files, and adds VSCode extenstions.
# As is, it is suitable to use on the VM infrastructure used in e.g. ENG209
# It will probably not work right away on local VM
# images may lack automatic mounting of myfiles at ~/Desktop/myfiles.
# Authors: Jean-Philippe Pellet, Matthieu Bovel
# Version: 2025-08-04

SEMESTER="2025"
PYTHON_VERSION="3.12.2"
PYTHON_HOME="/opt/python${PYTHON_VERSION}"

echostep() {
    str="$1"
    bkg="${2:-4}"
    len=${#str}
    pad="$(printf %-$((len + 5))s '')"
    pre="$(tput bold)$(tput setaf ${bkg})$(tput rev)"
    post="$(tput sgr0)"
    echo ""
    echo "----"
    echo "$pre$pad$post"
    echo "$pre>> $1  $post"
    echo "$pre$pad$post"
    echo "----"
}

err() {
    echostep "Installation failed! Please, get help..." 9
}

main() {
set -euC
trap err    ERR

PYTHON_EXEC=python${PYTHON_VERSION%.*}
PYTHON_PATH="${PYTHON_HOME}/bin/${PYTHON_EXEC}" 
PYTHON_PIP3="${PYTHON_HOME}/bin/pip3" 
COURSEFOLDERNAME="eng209_${SEMESTER}"

tput clear

if [[ ! -x "${PYTHON_PATH-x}" ]]; then
    echostep "Python executable ${PYTHON_EXEC} not found..." 9
    return
fi

# Clone the latest commit from the main branch, retrying until successful or 10 seconds elapse.
# Subsequent pulls replace it with the latest commit (local history depth remains 1).
cd ~/Desktop/myfiles
if [[ ! -d ${COURSEFOLDERNAME} ]]; then
    echostep "Cloning github repository..."
    timeout 10 bash -c "while ! git clone --depth 1 --branch main --single-branch https://github.com/eng209/eng209_${SEMESTER}.git; do sleep 2; done"
fi

cd "$COURSEFOLDERNAME"
git pull

echostep "Creating a ${PYTHON_EXEC} virtual environment on myfiles..."

mkdir -p venv/lib64 # needed to avoid symlink creation error on smb share
"$PYTHON_PATH" -m venv --copies --upgrade-deps venv
source venv/bin/activate

echostep "Installing Python packages..."

pip3 install --require-virtualenv --no-input ipykernel
pip3 install --require-virtualenv --no-input ipywidgets
pip3 install --require-virtualenv --no-input jupyterlab-latex
pip3 install --require-virtualenv --no-input matplotlib
pip3 install --require-virtualenv --no-input plotly
pip3 install --require-virtualenv --no-input numpy
pip3 install --require-virtualenv --no-input pandas
pip3 install --require-virtualenv --no-input scikit-learn
pip3 install --require-virtualenv --no-input func_timeout # for testing harness
pip3 install --require-virtualenv --no-input bpython # interpreter with completion and syntax highlighting
pip3 install --require-virtualenv --no-input mypy
pip3 install --require-virtualenv --no-input nbformat

echostep "Finishing setup in myfiles..."

mkdir -p .vscode

# This can be of course tweaked to reflect the best initial options for
# the created VS Code workspace. Careful with $, which must be escaped.
rm -f *.code-workspace
rm -f .vscode/settings.json
cat > .vscode/settings.json << EOM
// Ce fichier détermine les paramètres de votre workspace.
// Merci de ne pas le modifier à moins que la donnée d'un
// exercice vous demande de le faire.
{
    "workbench.editor.showTabs": "multiple",
    "workbench.tree.indent": 20,
    "python.envFile": "\${workspaceFolder}/venv",
    "python.defaultInterpreterPath": "venv/bin/python",
    "python.terminal.activateEnvironment": true,
    "python.terminal.activateEnvInCurrentTerminal": true,
    "[python]": {
        "editor.formatOnSave": true,
        "editor.defaultFormatter": "ms-python.black-formatter"
    },
    "mypy.checkNotebooks": true,
    "mypy.mypyExecutable": "\${workspaceFolder}/venv/bin/mypy",
    "mypy.dmypyExecutable": "\${workspaceFolder}/venv/bin/dmypy",
    "files.watcherExclude": {
        "**/.env/**": true,
        "**/venv/**": true,
        "**/.mypy_cache": true,
        "**/.ipynb_checkpoints": true
    },
    "files.exclude": {
        "**/.env/**": true,
        "**/venv/**": true,
        "**/.mypy_cache": true,
        "**/.ipynb_checkpoints": true
    },
    "python.terminal.activateEnvInCurrentTerminal": false
}
EOM

# Predefined tasks can be provided like this
rm -f .vscode/tasks.json
cat > .vscode/tasks.json << EOM
{
    "version": "2.0.0",
    "tasks": [
        {
            "label": "bpython",
            "type": "shell",
            "command": "source venv/bin/activate && venv/bin/bpython",
            "problemMatcher": [],
            "presentation": {
                "focus": true,
                "showReuseMessage": true,
                "echo": false,
                "panel": "dedicated"
            }
        }
    ]
}
EOM

echostep "Installing VS Code extensions..."

code --install-extension ms-python.python --force
code --install-extension ms-python.black-formatter --force
code --install-extension ms-python.mypy-type-checker --force
code --install-extension matangover.mypy --force # because it can check notebooks
code --install-extension jock.svg --force
code --uninstall-extension formulahendry.code-runner 2> /dev/null || echo "Legacy code-runner not installed, good"

echostep "Done. Launching VS Code and opening folder '${COURSEFOLDERNAME}'..."

code ~/Desktop/myfiles/"${COURSEFOLDERNAME}"
}

main "$@"
