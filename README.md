# social-signals

## setup

```bash
rye add pip
rye sync
rye build
python -m pip install -e .
```

# SOSIG (Social Signal)

A command-line tool for analyzing GitHub repositories and calculating social signals based on various metrics.

## Features

- Analyze local Git repositories for various metrics and social signals
- Store and manage repository analysis data in a local database
- Configure analysis weights and parameters
- View repository statistics and comparisons
- Database management and optimization utilities

## Installation

```bash
# Clone the repository
git clone https://github.com/will-wright-eng/sosig.git
cd sosig

# Install dependencies
pip install -r requirements.lock

# For development
pip install -r requirements-dev.lock
```

## Usage

SOSIG provides three main command groups:

### GitHub Metrics Operations (`gh`)

```bash
# Analyze repositories
sosig gh analyze path/to/repo1 path/to/repo2

# List analyzed repositories (sorted by social signal by default)
sosig gh list
sosig gh list --sort stars  # Sort by stars
```

Available sort options:

- `social_signal` (default)
- `stars`
- `age_days`
- `name`
- `username`
- `last_analyzed`
- `commit_count`

### Database Operations (`db`)

```bash
# View database statistics
sosig db stats

# Show database schema
sosig db schema

# Remove specific repository
sosig db remove repo-name

# Clear all data
sosig db clear

# Optimize database
sosig db vacuum
```

### Configuration Operations (`config`)

```bash
# Show current configuration
sosig config show

# Update configuration values
sosig config set metrics.weights.age 0.3
```

## Project Structure

```
sosig/
├── src/sosig/
│   ├── commands/          # CLI command implementations
│   ├── core/             # Core functionality and models
│   └── utils/            # Utility functions and services
├── scripts/              # Helper scripts
│   └── results/          # Analysis results
└── requirements.lock     # Locked dependencies
```

## Scripts

The project includes several utility scripts:

- `analyze-repo-file.sh`: Batch analyze repositories from a file
- `fetch-repos.sh`: Fetch repository information from GitHub

## Development

### Debug Mode

All commands support a `--debug` flag for additional logging:

```bash
sosig gh analyze path/to/repo --debug
```

### Workspace Configuration

Analysis operations use a workspace directory (default: `~/.local/share/ssig/workspace`):

```bash
sosig gh analyze path/to/repo --workspace /custom/path
```
