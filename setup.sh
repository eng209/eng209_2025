#!/bin/bash

# Linux/macOS wrapper for setup.py
# Finds python3.12 and creates the class project folder with a virtualenv inside.
# Defaults to ~/Desktop/myfiles; pass a folder in first argument to override.
# Made for ENG209 VM; may need adjustments on other systems.

main() {
	set -euC
	local -r COURSE_FOLDER="${1-${HOME}/Desktop/myfiles}"
	local -r PYTHON_PATH="${PYTHON_PATH-/opt/python3.12.2/bin/python3.12}"
	local -r SETUP_URL="https://raw.githubusercontent.com/eng209/assets/refs/heads/main/tools/setup.py"

	if [[ ! -e "${COURSE_FOLDER}" ]]; then
        echo "${COURSE_FOLDER} does not exist. Try: ./setup.sh /path/to/folder"
		return 1
    fi

	for python_exe in ${PYTHON_PATH} $(type -a -P -- python3.12 python3); do
		if [[ $("${python_exe}" --version 2>&1) =~ ^Python\ 3\.12 ]]; then
			local -r PYTHON_EXE="${python_exe}"
			break
		fi
	done

	if [[ ! -x "${PYTHON_EXE-}" ]]; then
		echo "Python 3.12 not found. Try: PYTHON_PATH=/path/to/python.exe ./setup.sh"
		return 1
	fi

	[[ -e ${COURSE_FOLDER}/setup.py ]] || "${PYTHON_EXE}" -- <<-EOF
		import urllib.request
		urllib.request.urlretrieve('${SETUP_URL}', '${COURSE_FOLDER}/setup.py')
EOF

	"${PYTHON_EXE}" -- "${COURSE_FOLDER}/setup.py" --base "${COURSE_FOLDER}"
}

main "$@"
