#!/usr/bin/env bash

set -euo pipefail

readonly DEFAULT_LIMIT=100
readonly REQUIRED_COMMANDS=("gh" "jq")
readonly REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

check_dependencies() {
    for cmd in "${REQUIRED_COMMANDS[@]}"; do
        if ! command -v "$cmd" &> /dev/null; then
            echo "Error: $cmd is not installed" >&2
            exit 1
        fi
    done
}

show_usage() {
    cat << EOF
Usage: $(basename "$0") <username> [output_dir]
    username    GitHub username to fetch repositories for
    output_dir  Optional: Directory to store output files (default: current directory)
EOF
    exit 1
}

validate_inputs() {
    if [ $# -lt 1 ]; then
        echo "Error: GitHub username is required" >&2
        show_usage
    fi

    # Validate username format
    if [[ ! "$1" =~ ^[a-zA-Z0-9-]+$ ]]; then
        echo "Error: Invalid GitHub username format" >&2
        exit 1
    fi
}

# Function to generate repository summary
generate_summary() {
    local username="$1"
    local output_dir="$2"
    local repo_count="$3"

    cat << EOF > "$output_dir/repo_summary.txt"
Repository Summary for $username
Generated on $(date)
Total Public Repositories: $repo_count

Details:
EOF

    jq -r '.[] | "- \(.name)\n  Created: \(.createdAt)\n  URL: \(.url)\n  Description: \(.description // "No description")\n"' \
        "$output_dir/public_repos.json" >> "$output_dir/repo_summary.txt"
}

# Function to fetch and process repositories
fetch_repositories() {
    local username="$1"
    local output_dir="$2"

    echo "Fetching repositories for user: $username"
    gh repo list "$username" \
        --json name,visibility,description,createdAt,url,languages \
        --limit "$DEFAULT_LIMIT" | \
        jq '[.[] | select(.visibility == "PUBLIC")]' > "$output_dir/public_repos.json"

    # Extract public repository URLs
    jq -r '.[] | .url' "$output_dir/public_repos.json" > "$output_dir/public_repo_urls.txt"
}

main() {
    validate_inputs "$@"
    check_dependencies

    local username="$1"
    local output_dir="$REPO_ROOT/results/$username"

    # Create output directory if it doesn't exist
    mkdir -p "$output_dir"

    fetch_repositories "$username" "$output_dir"

    # Get repository count and generate summary
    local repo_count
    repo_count=$(jq length "$output_dir/public_repos.json")
    echo "Found $repo_count public repositories"

    generate_summary "$username" "$output_dir" "$repo_count"

    echo "Output files generated in $output_dir:"
    echo "- public_repos.json: Complete repository data"
    echo "- public_repo_urls.txt: List of public repository URLs"
    echo "- repo_summary.txt: Human-readable summary"
}

main "$@"
