#!/bin/bash

# Linux/macOS wrapper for setup.py
# Finds python3.12 and creates the class project folder with a virtualenv inside
# Defaults to ~/Desktop/myfiles; pass in arguments a folder to override
# Made for ENG209 VM; may need adjustments on other systems.

main() {
    local COURSE_FOLDER="${1-${HOME}/Desktop/myfiles}"
    local PYTHON_PATH="${PYTHON_PATH-/opt/python3.12.2/bin/python3.12}"

    if [[ ! -e "${PYTHON_PATH}" ]]; then
        for python_exe in $(type -a -P python3.12 python3); do
            if [[ $("$python_exe" --version) =~ ^Python\ 3\.12 ]]; then
                PYTHON_PATH="${python_exe}"
            fi
        done
    fi
    "${PYTHON_PATH}" setup.py --base "${COURSE_FOLDER}"
}

main "$@"
