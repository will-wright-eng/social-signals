#!/bin/bash

# Get the absolute path to the repository root (assumes script is in scripts/ directory)
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Activate virtual environment
VENV_PATH="$REPO_ROOT/sosig/.venv"
if [ ! -f "$VENV_PATH/bin/activate" ]; then
    echo "Error: Virtual environment not found at $VENV_PATH"
    echo "Please create a virtual environment first:"
    echo "python -m venv $VENV_PATH"
    exit 1
fi

echo "Activating virtual environment at $VENV_PATH"
source "$VENV_PATH/bin/activate"

# Check if input file is provided
if [ $# -ne 1 ]; then
    echo "Usage: $0 <input_file>"
    echo "Example: $0 $REPO_ROOT/scripts/results/tiangolo/public_repo_urls.txt"
    exit 1
fi

input_file="$1"

# Check if input file exists
if [ ! -f "$input_file" ]; then
    echo "Error: Input file '$input_file' not found"
    exit 1
fi

echo "Starting analysis at $(date)"
echo "Reading repos from: $input_file"
echo "----------------------------------------"

# Read each line from the input file
while IFS= read -r url || [ -n "$url" ]; do
    # Skip empty lines and comments
    if [[ -z "$url" || "$url" =~ ^# ]]; then
        continue
    fi

    echo "Analyzing: $url"

    # Run the analysis command and always display the output
    output=$(sosig gh analyze "$url" --debug 2>&1)
    exit_code=$?

    if [ $exit_code -eq 0 ]; then
        echo "Success: $url"
    else
        echo "Error analyzing $url"
    fi

    # Always show the output regardless of success/failure
    echo "$output"

    echo "----------------------------------------"

    # Add a small delay between requests to avoid rate limiting
    sleep 2
done < "$input_file"

echo "Analysis complete at $(date)"

# Deactivate virtual environment
deactivate
