# Deferred Fixes

## Summary

An audit of `social-signals` on 2026-09-24, run after the package moved to the repo root
(`7c97b25`), found bugs in the CLI, a stale release pipeline, and some housekeeping. The
quick fixes landed with this document (see [Completed](#completed)). This document tracks
the rest, in the order they should be done.

**Phase 1 blocks the `0.3.1` release.** The `sosig` Homebrew formula will pin the next
tagged version, so whatever `0.3.1` contains reaches `brew install` users. Today,
`sosig gh analyze` can delete a user's directory, can return another repository's results,
and exits 0 when it fails. Phases 2–4 can ship in later releases.

Each finding cites the code it lives in. Findings marked **Reproduced** were confirmed by
running the CLI with `XDG_DATA_HOME` and `XDG_CONFIG_HOME` pointed at a scratch directory,
with a stub `gh` where the test needed GitHub responses.

## Current State

| ID   | Issue                                                                | Severity | Blocks `0.3.1` | Status |
| ---- | -------------------------------------------------------------------- | -------- | -------------- | ------ |
| T1.1 | `gh analyze` deletes the `--workspace` directory                     | High     | Yes            | Open   |
| T1.2 | Repositories with the same name share one result                     | High     | Yes            | Open   |
| T1.3 | `gh analyze` exits 0 when analysis fails                             | Medium   | Yes            | Open   |
| T1.4 | `sqlmodel` is declared but unused; `sqlalchemy` is used but undeclared | Medium | Yes            | Open   |
| T1.5 | Misspelled author email in published metadata                        | Low      | Yes            | Open   |
| T2.1 | Single-commit repositories get the full update-frequency score       | Medium   | No             | Open   |
| T2.2 | Repository age uses the newest root commit                           | Low      | No             | Open   |
| T2.3 | Cached results never expire, and cache hits still clone              | Low      | No             | Open   |
| T2.4 | `RepoMetrics` timestamp defaults are fixed at import                 | Low      | No             | Open   |
| T2.5 | Counting lines of code starts one process per file                   | Medium   | No             | Open   |
| T2.6 | `db remove` swallows its own exit and documents a missing argument   | Low      | No             | Open   |
| T2.7 | `Database` singleton ignores `db_path` after the first call          | Low      | No             | Open   |
| T3.1 | Publish workflows use rye, `@master`, and long-lived tokens          | Medium   | No             | Open   |
| T3.2 | Dependabot watches a directory that doesn't exist                    | Low      | No             | Open   |
| T3.3 | The test workflow doesn't gate `main`                                | Medium   | No             | Open   |
| T4.1 | Housekeeping                                                         | Low      | No             | Open   |

## Completed

These landed with this document:

| Finding | Fix |
| ------- | --- |
| `db export --fields name,stars` was rejected as a single invalid field | Each `--fields` value is split on commas (`src/sosig/commands/db_cmds.py`); repeating `--fields` still works |
| `gh` error handlers caught `CalledProcessError`, which `run_command` never raises, so `get_open_issues` crashed the analysis instead of returning 0 | The handlers catch `GitCommandError` (`src/sosig/utils/gh_utils.py`) |
| `sosig config init` crashed with a traceback when `git` or `gh` was missing | `run_command` wraps `OSError` in `GitCommandError`, so `config init` reports the missing tool |
| `make user-repos` wrote to `results/` while `make analyze-repos` read `scripts/results/`, and the README passed `user=` where the target expects `dir=` | `fetch-repos.sh` writes to `scripts/results/<user>` and honors its `output_dir` argument; the README uses `dir=` |
| `analyze-repo-file.sh` stopped at the first failing repository (`set -e` on a failing `$(...)`) | The loop tests the command's status directly, so later repositories still run |
| Pre-publish failed on almost every push to `main` with `400 File already exists` from TestPyPI | `skip-existing: true`; the deprecated `packages_dir` and `repository_url` inputs are renamed in both publish workflows |

Regression tests: `tests/test_gh_utils.py`, plus `test_config_init_reports_missing_tools` and
`test_db_export_fields` in `tests/test_commands.py`.

## Phase 1: Before `0.3.1`

### T1.1 `gh analyze` deletes the `--workspace` directory

**Problem.** `analyze` cleans up by default with `shutil.rmtree(workspace)` on whatever
directory `--workspace` names (`src/sosig/commands/gh_cmds.py:57`). The cleanup runs in
`finally`, so it also runs when the analysis fails.
`sosig gh analyze owner/repo --workspace ~/code` deletes `~/code`.

**Reproduced.** A workspace directory containing `important.txt` was gone after one run
against a repository that doesn't exist.

**Fix.** Give each run its own directory inside the workspace with
`tempfile.mkdtemp(dir=workspace)`, and clone or copy each repository into
`<run-dir>/<name>` so the displayed name doesn't change. Cleanup removes only the run
directory, and `--no-cleanup` keeps it. This drops the reuse of an existing clone
(`src/sosig/utils/gh_repo_service.py:51`), which only ever helped with `--no-cleanup`.

**Done when** a test runs `gh analyze` with `--workspace` set to a directory holding a file,
and afterwards the file still exists and no clone is left behind.

### T1.2 Repositories with the same name share one result

**Problem.** The clone directory comes from the last path component of the argument
(`workspace / Path(path).name`, `src/sosig/utils/gh_repo_service.py:30`),
`calculate_social_signal` stores that clone directory as the row's `path`
(`src/sosig/utils/gh_utils.py:290`), and `analyze_repository` returns any cached row whose
`path` matches (`src/sosig/utils/gh_analyzer.py:20`). So after `foo/cli` has been analyzed,
analyzing `bar/cli` clones `bar/cli` and then returns `foo/cli`'s row, and nothing is stored
for `bar/cli`. `gh analyze .` has the same problem, because every `.` maps to the workspace
root. The README's Terraform table includes `terraform-compliance/cli`, so collisions are
realistic.

**Reproduced.** With two local repositories, `alice/cli` (10 stars) and `bob/cli`
(99 stars), and a stub `gh`, both runs reported owner `alice` with 10 stars, and the
database held one row.

**Fix.** Key rows on the source, not the clone directory:

- remote repositories: `owner/name`, parsed from the argument or taken from
  `gh repo view --json nameWithOwner`
- local repositories: the resolved absolute path

Pass that identifier into `calculate_social_signal`, store it in `Repository.path`, and use
it for the cache lookup. `name` stays the short name.

**Migration.** Existing rows hold clone-directory paths that will never match the new keys,
so they will linger as stale duplicates. The database has no migration mechanism
(`_initialize_database` only creates missing tables). The simplest route is a release note
telling users to run `sosig db remove --drop-db` and re-analyze.

**Done when** analyzing `alice/cli` and then `bob/cli` stores two rows with the right owners
and star counts.

### T1.3 `gh analyze` exits 0 when analysis fails

**Problem.** Failures are swallowed twice. `RepositoryService.analyze_repositories` catches
`GitCommandError` and `GitHubAPIError` for each repository, logs them, and returns only the
successes (`src/sosig/utils/gh_repo_service.py:34`). The `analyze` command catches every
other exception, prints it, and returns normally (`src/sosig/commands/gh_cmds.py:53`).
Scripts can't tell that anything went wrong.

**Reproduced.** Analyzing a repository that doesn't exist printed an error and exited 0.

**Fix.** Have the service return failures alongside results, print them, and exit 1 if any
repository failed. Don't raise `typer.Exit` inside the `try` body: the generic
`except Exception` catches it (see T2.6). `scripts/analyze-repo-file.sh` already continues
past a non-zero exit, so batch runs keep going.

**Done when** `sosig gh analyze does-not-exist/xyz` exits 1, and a batch containing one bad
repository still analyzes the others and exits 1.

### T1.4 Declare the database dependency that's actually used

**Problem.** `pyproject.toml` declares `sqlmodel`, which nothing imports. The code imports
`sqlalchemy` directly (`src/sosig/core/db.py`, `src/sosig/core/models.py`), and it is only
installed because `sqlmodel` depends on it. `src/sosig/core/models.py:4` also imports
`declarative_base` from `sqlalchemy.ext.declarative`, which has been deprecated since
SQLAlchemy 2.0, so every test run prints a `MovedIn20Warning`.

**Fix.**

- replace `sqlmodel>=0.0.22` with `sqlalchemy>=2.0` in `dependencies`
- import `declarative_base` from `sqlalchemy.orm`
- regenerate `requirements.lock` and `requirements-dev.lock`
- run `ruff format` on `models.py` in the same change (T4.1)

The Homebrew formula drops the `sqlmodel` resource when T5.5 of the
[formula readiness plan][formula-readiness] regenerates its resources.

**Done when** the tests pass without a `MovedIn20Warning`, and the built wheel's metadata
lists `sqlalchemy` and not `sqlmodel`.

### T1.5 Fix the author email

`pyproject.toml:6` lists `will.wright.engineeering@gmail.com` (three e's), while
`scripts/plots/pyproject.toml` uses `will.wright.engineering@gmail.com`. PyPI shows the
author address on the project page. Confirm the intended address and correct it.

**Done when** the built wheel's `Author-email` shows the corrected address.

## Phase 2: Scoring and CLI correctness

These change scores or CLI behavior but don't endanger data. T2.1, T2.2, and T2.5 change
`social_signal` values. After they land, re-analyze with `--force` and regenerate the README
example tables so old and new scores aren't mixed.

### T2.1 Single-commit repositories get the full update-frequency score

`get_update_frequency` returns `0` for a repository with fewer than two commits
(`src/sosig/utils/gh_utils.py:130`). `_normalize_metrics` scores frequency as
`1.0 - min(days / 30, 1.0)` (line 252), so 0 days is the best possible value. At the default
weight of 0.25, that's 25 of 100 points for having no update history at all. In the T1.2
reproduction, a one-commit repository with 10 stars scored 25.5.

**Fix.** Score the update-frequency term as 0 when `commit_count < 2`.

**Done when** a unit test on `_normalize_metrics` gives a one-commit repository 0 for that
term.

### T2.2 Repository age uses the newest root commit

`get_repo_age` runs `git log --reverse --max-parents=0 --max-count=1`
(`src/sosig/utils/gh_utils.py:95`). Git applies `--max-count` before `--reverse`, so when a
history has several root commits (merged histories, subtree imports), it returns the newest
root.

**Reproduced.** A repository with root commits from 2020 and 2025 reported 2025.

**Fix.** Run `git log --max-parents=0 --format=%ct` and take the minimum.

**Done when** the two-root test repository reports its 2020 root.

### T2.3 Cached results never expire, and cache hits still clone

`database.CACHE_TTL_HOURS` (24) appears in `config show`, but nothing reads it.
`RepositoryAnalyzer._is_analysis_fresh` (`src/sosig/utils/gh_analyzer.py:34`) is never
called, so a cached row is returned forever unless `--force` is passed. Separately, the
service clones the repository before the analyzer checks the cache
(`src/sosig/utils/gh_repo_service.py:51-54`), so a cache hit still pays for a full clone.

**Fix.** After T1.2, the cache key is known before cloning. Check the cache first, return
the row only if `_is_analysis_fresh` is true, and clone only when re-analysis is needed. If
cached results are meant to be permanent, delete the setting and the method instead.

### T2.4 `RepoMetrics` timestamp defaults are fixed at import

`last_analyzed: float = time.time()` and `date_created: float = time.time()`
(`src/sosig/core/interfaces.py:23-24`) are evaluated once, when the module is imported, so
every instance built without explicit values shares one timestamp. Current callers always
pass both values, so nothing is wrong yet.

**Fix.** `field(default_factory=time.time)`.

### T2.5 Counting lines of code starts one process per file

`get_lines_of_code` runs `wc -l` once per tracked file
(`src/sosig/utils/gh_utils.py:214`). For a repository the size of the README's `kubernetes`
row, that means tens of thousands of processes. It also counts binary files.

**Fix.** List files with `git ls-files -z`, read each one in Python, skip files with a NUL
byte in the first 8 KB, and count `b"\n"`. Then drop `wc` from the tools `config init`
checks for (`src/sosig/commands/config_cmds.py:45`). Counts change for repositories that
contain binary files.

**Done when** a test repository with one text file and one binary file reports only the text
file's lines.

### T2.6 `db remove` swallows its own exit and documents a missing argument

`remove` raises `typer.Exit(1)` and `typer.Abort()` inside a `try` whose `except Exception`
catches them, because both are `RuntimeError` subclasses
(`src/sosig/commands/db_cmds.py:44-55`).

**Reproduced.** `sosig db remove` prints the intended warning followed by
`Error dropping db: 1`. Declining the confirmation prompt prints `Error dropping db:` instead
of `Aborted!`.

Separately, `README.md:93` documents `sosig db remove repo-name`, and the help text says
"Remove a specific repository", but the command takes no repository argument.

**Fix.** Move the flag check and the confirmation above the `try`, or add
`except (typer.Exit, typer.Abort): raise` before the generic handler. Then either implement
per-repository removal or take it out of the help text and README.

### T2.7 `Database` singleton ignores `db_path` after the first call

`Database` is a process-wide singleton (`src/sosig/core/db.py:17-19`). A second
`Database(db_path=...)` returns the first instance and silently ignores the new path. The
test fixture resets `Database._instance` to work around this.

**Fix.** Replace the singleton with a `get_db()` cached per path (for example with
`functools.lru_cache`), so a different path gets a different engine.

## Phase 3: CI and release pipeline

### T3.1 Modernize the publish workflows

`publish.yml` and `pre-publish.yml`:

- install rye 0.42 with `curl | bash`; rye has been superseded by uv, which `tests.yml`
  already uses
- check out with `actions/checkout@master`, a moving ref, while `tests.yml` pins `@v7`
- authenticate with long-lived API tokens (`PYPI_TOKEN`, `TEST_PYPI_API_TOKEN`)

**Fix.**

- build with `astral-sh/setup-uv` and `uv build`
- pin `actions/checkout@v7`
- switch to PyPI trusted publishing: add `permissions: id-token: write`, remove `password:`,
  register both workflows as trusted publishers on PyPI and TestPyPI, and then delete the
  token secrets

Drop rye from the project at the same time as from CI. `[tool.rye] dev-dependencies` becomes
a PEP 735 `[dependency-groups] dev` table, the two rye lockfiles become `uv.lock`, and the
README's setup instructions switch to uv. That also gives T3.3 a real dev group to install.

**Done when** the next release publishes through OIDC with the token secrets deleted.

### T3.2 Fix the Dependabot configuration

- The `docker` entry watches `/docker`, which doesn't exist, so its runs fail with
  "No Dockerfiles nor Kubernetes YAML found in /docker" (for example on 2026-08-10). Delete
  the entry.
- The `pip` entry watches `/`, which had no manifest until the package moved to the repo
  root. It will now open PRs against `pyproject.toml`. After T3.1, switch it to the `uv`
  ecosystem so it updates `uv.lock` as well.

### T3.3 Make the test workflow gate `main`

`tests.yml`:

- runs only on `pull_request`, so direct pushes to `main` are never tested; add
  `push: branches: [main]` with the same path filter
- installs `.[dev]`, an extra that doesn't exist (the next line installs the pytest plugins
  by hand); install the dev group from T3.1 instead
- passes `file:` to `codecov/codecov-action`, which is deprecated in favor of `files:`
- sets `PYTHONPATH=src` even though the package is installed in editable mode; drop it

CI also resolves the newest version of every dependency and ignores the lockfiles, which pin
versions from November 2024. Recommendation: test against the lockfile on every PR, so
failures point at code changes, and against the newest versions on a weekly schedule, so
upstream breakage shows up before users hit it.

## Phase 4: Housekeeping

### T4.1 Housekeeping

- [ ] Delete `.github/.stale.yml`. It configures the Probot Stale app, which is no longer
      maintained. Use the `actions/stale` workflow if stale issue handling is still wanted.
- [ ] Change `default_language_version` in `.pre-commit-config.yaml` from `python3.9` to
      `python3.12` (the package requires 3.10+, and `.python-version` is 3.12). Then run
      `pre-commit autoupdate`, since the hook versions date from early 2025.
- [ ] Run `ruff format` on `src/sosig/core/models.py`, the only file that fails
      `ruff format --check`. Do this with T1.4.
- [ ] Remove `known_first_party = app` and `known_third_party = openai, requests` from
      `.isort.cfg`. None of these packages are used here, and isort already finds `sosig`
      through `src_paths`.
- [ ] Split the `local x=$(...)` declarations in `scripts/*.sh` (ShellCheck SC2155) so a
      failing command isn't masked.

## Verification

Run after each phase:

```bash
uv venv && uv pip install -e . pytest pytest-mock pytest-cov
.venv/bin/pytest
uvx ruff@0.9.6 check src tests
uvx ruff@0.9.6 format --check --line-length=120 src tests
uv build
tar -tzf dist/sosig-*.tar.gz | grep -F '..'   # must print nothing
```

Check T1.1 by hand as well. Before the fix, this deletes the directory:

```bash
mkdir -p /tmp/sosig-ws && touch /tmp/sosig-ws/keep
sosig gh analyze does-not-exist/xyz --workspace /tmp/sosig-ws
test -f /tmp/sosig-ws/keep && echo "workspace preserved"
```

It's safe to tag `0.3.1` once every Phase 1 row in [Current State](#current-state) is done.
Then continue with T5.4 in the [formula readiness plan][formula-readiness].

## References

- [formula-readiness.md][formula-readiness]: the Homebrew plan; its T5.4 (release `0.3.1`)
  and T5.5 (switch the formula to the sdist) come after Phase 1
- [Python `tempfile.mkdtemp`](https://docs.python.org/3/library/tempfile.html#tempfile.mkdtemp):
  per-run workspace directories (T1.1)
- [Python `dataclasses` default factory functions](https://docs.python.org/3/library/dataclasses.html#default-factory-functions)
  (T2.4)
- [Typer: Terminating](https://typer.tiangolo.com/tutorial/terminating/): `typer.Exit` and
  `typer.Abort` (T1.3, T2.6)
- [git-log: Commit Limiting](https://git-scm.com/docs/git-log#_commit_limiting):
  `--max-count`, `--max-parents`, and `--reverse` (T2.2)
- [SQLAlchemy 2.0 migration guide](https://docs.sqlalchemy.org/en/20/changelog/migration_20.html):
  `declarative_base` moved to `sqlalchemy.orm` (T1.4)
- [pypa/gh-action-pypi-publish](https://github.com/pypa/gh-action-pypi-publish):
  `skip-existing` and trusted publishing (T3.1)
- [PyPI trusted publishers](https://docs.pypi.org/trusted-publishers/) (T3.1)
- [uv documentation](https://docs.astral.sh/uv/) and [rye](https://github.com/astral-sh/rye):
  rye's README points to uv as its successor (T3.1)
- [PEP 735: Dependency Groups](https://peps.python.org/pep-0735/) (T3.1)
- [Dependabot options reference](https://docs.github.com/en/code-security/dependabot/working-with-dependabot/dependabot-options-reference)
  (T3.2)
- [codecov/codecov-action](https://github.com/codecov/codecov-action): the `files` input (T3.3)
- [actions/stale](https://github.com/actions/stale) (T4.1)
- [ShellCheck SC2155](https://www.shellcheck.net/wiki/SC2155) (T4.1)

[formula-readiness]: https://github.com/will-wright-eng/homebrew-tools/blob/main/docs/formula-readiness.md
