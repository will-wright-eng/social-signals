#!/bin/bash

set -euo pipefail

# Get the absolute path to the repository root (assumes script is in scripts/ directory)
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_PATH="$REPO_ROOT/sosig/.venv"

validate_inputs() {
    if [ $# -lt 1 ]; then
        echo "Error: Input file path is required" >&2
        echo "Usage: $0 <input_file>"
        echo "Example: $0 $REPO_ROOT/results/username/public_repo_urls.txt"
        exit 1
    fi

    if [ ! -f "$1" ]; then
        echo "Error: Input file '$1' not found" >&2
        exit 1
    fi
}

setup_environment() {
    if [ ! -f "$VENV_PATH/bin/activate" ]; then
        echo "Error: Virtual environment not found at $VENV_PATH"
        echo "Please create a virtual environment first:"
        echo "python -m venv $VENV_PATH"
        exit 1
    fi

    echo "Activating virtual environment at $VENV_PATH"
    source "$VENV_PATH/bin/activate"
}

analyze_repos() {
    local input_file="$1"
    
    echo "Starting analysis at $(date)"
    echo "Reading repos from: $input_file"
    echo "----------------------------------------"

    while IFS= read -r url || [ -n "$url" ]; do
        # Skip empty lines and comments
        if [[ -z "$url" || "$url" =~ ^# ]]; then
            continue
        fi

        echo "Analyzing: $url"
        output=$(sosig gh analyze "$url" --debug 2>&1)
        exit_code=$?

        if [ $exit_code -eq 0 ]; then
            echo "Success: $url"
        else
            echo "Error analyzing $url"
        fi

        echo "$output"
        echo "----------------------------------------"
        sleep 2
    done < "$input_file"

    echo "Analysis complete at $(date)"
}

main() {
    validate_inputs "$@"
    setup_environment
    analyze_repos "$1"
    deactivate
}

main "$@"
