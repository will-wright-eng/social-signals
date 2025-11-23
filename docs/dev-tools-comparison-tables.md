# Modern Dev Tools Comparison for Polyglot Development

## Runtime/Version Management Tools

| Tool | Languages | Key Features | Performance | Config Format | Caching | Remote Cache | Learning Curve | Best For |
|------|-----------|--------------|-------------|---------------|---------|--------------|----------------|----------|
| **mise** | All via plugins | Fast (Rust), parallel installs, task runner built-in, env vars | Excellent | .mise.toml | Local | No | Low | Teams wanting modern asdf replacement |
| **asdf** | All via plugins | Plugin ecosystem, shell integration, legacy version files | Good | .tool-versions | Local | No | Low | Teams with existing asdf setup |
| **proto** | Multiple built-in | WASM plugins, built-in toolchain support | Excellent | .prototools | Local | No | Low | Teams wanting lightweight solution |
| **volta** | Node/JS focused | Fast, per-project bins, npm/yarn aware | Excellent | package.json | Local | No | Very Low | JavaScript-heavy projects |
| **rtx** | (Now mise) | - | - | - | - | - | - | Deprecated, use mise |
| **nvm/pyenv/rbenv** | Single language | Mature, simple, widely adopted | Moderate | .*rc files | Local | No | Very Low | Single-language projects |

## Build Orchestration & Monorepo Tools

| Tool | Languages | Key Features | Performance | Config Format | Caching | Remote Cache | Learning Curve | Best For |
|------|-----------|--------------|-------------|---------------|---------|--------------|----------------|----------|
| **Nx** | Agnostic | Project graph, affected detection, generators, plugins | Excellent | nx.json + project.json | Local | Yes (Nx Cloud) | High | Large monorepos, enterprise teams |
| **Turborepo** | Agnostic | Simple config, incremental builds, pipeline model | Excellent | turbo.json | Local | Yes (Vercel) | Low | Existing monorepos, simple orchestration |
| **Bazel** | Agnostic | Hermetic builds, reproducible, Google-scale tested | Excellent | BUILD files | Local | Yes | Very High | Large orgs, complex dependencies |
| **Pants** | Python/Go/Java/Scala | Fine-grained deps, minimal config, smart caching | Very Good | BUILD files | Local | Yes | High | Python-heavy polyglot repos |
| **Rush** | JS/TS focused | Microsoft-backed, strict versioning, change management | Good | rush.json | Local | Yes (BuildCache) | Medium | Enterprise JS monorepos |
| **Lerna** | JS/TS | Package publishing, versioning, bootstrapping | Moderate | lerna.json | None | No | Low | JS library monorepos |
| **Moon** | Agnostic | Rust-based, project graph, task inheritance | Excellent | moon.yml | Local | Yes | Medium | Modern monorepos wanting speed |
| **Lage** | JS/TS focused | Microsoft-backed, pipeline caching, simple config | Good | lage.config.js | Local | No | Low | JS monorepos needing orchestration |

## Task Runners & Build Tools

| Tool | Languages | Key Features | Performance | Config Format | Caching | Remote Cache | Learning Curve | Best For |
|------|-----------|--------------|-------------|---------------|---------|--------------|----------------|----------|
| **Just** | Agnostic | Make-like, no dependencies, shell commands | Excellent | Justfile | None | No | Very Low | Simple task automation |
| **Task** | Agnostic | YAML config, built-in variables, includes | Very Good | Taskfile.yml | Output | No | Low | Teams preferring YAML |
| **Make** | Agnostic | Universal, mature, dependency-based | Good | Makefile | File-based | No | Medium | Traditional builds, UNIX systems |
| **Earthly** | Agnostic | Dockerfile + Makefile, reproducible, container-based | Good | Earthfile | Layer | Yes | Medium | CI/CD, reproducible builds |
| **Dagger** | Agnostic | Programmable CI/CD, SDK-based, DAG execution | Very Good | Code (Go/Python/TS) | Yes | Yes | High | Complex pipelines as code |

## Dependency Management Tools

| Tool | Languages | Key Features | Performance | Config Format | Caching | Remote Cache | Learning Curve | Best For |
|------|-----------|--------------|-------------|---------------|---------|--------------|----------------|----------|
| **Renovate** | Agnostic | Auto-updates, flexible config, monorepo support | N/A | renovate.json | N/A | N/A | Medium | Automated dependency updates |
| **Dependabot** | Agnostic | GitHub native, simple setup, PR automation | N/A | .github/dependabot.yml | N/A | N/A | Low | GitHub-based projects |
| **FOSSA** | Agnostic | License compliance, vulnerability scanning | N/A | .fossa.yml | N/A | N/A | Low | Compliance-focused orgs |

## Environment & Configuration Management

| Tool | Languages | Key Features | Performance | Config Format | Caching | Remote Cache | Learning Curve | Best For |
|------|-----------|--------------|-------------|---------------|---------|--------------|----------------|----------|
| **direnv** | Agnostic | Auto-load env vars, shell integration, .envrc files | Excellent | .envrc | None | No | Low | Per-project environments |
| **dotenv** | Agnostic | Simple .env files, wide language support | Excellent | .env | None | No | Very Low | Simple env var management |
| **Chamber** | Agnostic | AWS SSM/Secrets integration, secure storage | Good | CLI/JSON | None | No | Medium | AWS-based secrets |
| **Teller** | Agnostic | Multi-provider secrets, single interface | Good | .teller.yml | Local | No | Medium | Multi-cloud secrets |

## Development Environment Tools

| Tool | Languages | Key Features | Performance | Config Format | Caching | Remote Cache | Learning Curve | Best For |
|------|-----------|--------------|-------------|---------------|---------|--------------|----------------|----------|
| **Devbox** | Agnostic | Nix-based, reproducible, isolated shells | Good | devbox.json | Nix store | Yes (Cachix) | Medium | Reproducible dev environments |
| **Flox** | Agnostic | Nix-based, shareable environments, declarative | Good | .flox/ | Nix store | Yes | Medium | Team environment sharing |
| **devenv** | Agnostic | Nix-based, pre-commit integration, services | Good | devenv.nix | Nix store | Yes (Cachix) | High | Nix users wanting convenience |
| **Docker Compose** | Agnostic | Container orchestration, service definitions | Good | docker-compose.yml | Layers | Registry | Medium | Containerized development |

## Multi-Repo Synchronization & Management Tools

| Tool | Type | Key Features | Use Cases | Config Format | Learning Curve | Best For |
|------|------|--------------|-----------|---------------|----------------|----------|
| **Copybara** | Transform & Sync | Bidirectional sync, file transformation, path filtering | Internal/external repos, visibility management | .sky files | High | Large orgs with complex sync needs |
| **multi-gitter** | Bulk Changes | PR creation across repos, scriptable changes, GitHub/GitLab support | Config updates, migrations, security patches | CLI/scripts | Low | One-time or scheduled updates |
| **git-xargs** | Command Runner | Parallel execution, filtered repo selection, dry-run mode | Bulk operations, dependency updates | CLI args | Very Low | Simple bulk commands |
| **Bit** | Component Platform | Version management, dependency tracking, component marketplace | Shared components, design systems | bit.json | Medium | Component-based architecture |
| **Meta** | Multi-Repo CLI | Unified commands, project discovery, plugin system | Development workflow, CI/CD | .meta file | Low | Teams wanting monorepo-like workflow |
| **Projen** | Project Generation | Synthesized configs, type-safe definitions, upgradeable | JS/TS projects, standardization | .projenrc.js | Medium | JavaScript ecosystem standardization |
| **Cruft** | Template Updates | Template linking, conflict resolution, update tracking | Project templates, boilerplate management | .cruft.json | Low | Maintaining cookiecutter projects |
| **git-subrepo** | File Sharing | Better than submodules, actual file copies, history preservation | Shared configs, common files | .gitrepo | Medium | Alternative to git submodules |

## Creative Multi-Repo Solutions Using Existing Tools

| Approach | Tools Used | Implementation | Pros | Cons | Best For |
|----------|------------|----------------|------|------|----------|
| **Renovate Custom Managers** | Renovate | Regex patterns for any file type, custom datasources | Leverages existing tool, PR workflow, scheduling | Complex configuration, limited to pattern matching | Teams already using Renovate |
| **GitHub Actions Dispatch** | GitHub Actions | Template repo triggers updates via repository_dispatch | Native GitHub, full control, audit trail | GitHub-specific, requires workflow in each repo | GitHub-based organizations |
| **Terraform Management** | terraform-provider-github/gitlab | IaC for repo settings and files | Declarative, version controlled, drift detection | Limited to provider capabilities, state management | Infrastructure-oriented teams |
| **Centralized Pre-commit** | pre-commit | Host configs in central repo, reference by version | Simple, version pinning, gradual adoption | Only for pre-commit hooks, manual version updates | Standardizing linting/formatting |
| **Yeoman Generators** | Yeoman | Custom generators for updates, interactive prompts | Interactive, flexible, extensible | Manual process, JavaScript-based | Interactive project updates |

## Comparison Matrix for Multi-Repo Management

| Requirement | Best Tool | Alternative | Notes |
|-------------|-----------|-------------|-------|
| **One-time migration across repos** | git-xargs | multi-gitter | git-xargs for simple, multi-gitter for PRs |
| **Continuous file synchronization** | Copybara | Bit | Copybara for transforms, Bit for versioning |
| **Pre-commit config management** | Centralized pre-commit | Renovate custom | Central repo for control, Renovate for automation |
| **Project template updates** | Cruft | Projen | Cruft for any language, Projen for JS/TS |
| **Common dependency updates** | Renovate | Dependabot + scripts | Renovate more flexible for custom patterns |
| **CI/CD pipeline standardization** | GitHub Actions Dispatch | Terraform providers | Actions for GitHub, Terraform for multi-platform |
| **Shared code/components** | Bit | git-subrepo | Bit for versioning, subrepo for simplicity |
| **Bulk security patches** | multi-gitter | git-xargs + CI | multi-gitter creates PRs for review |

## Implementation Patterns for Common Scenarios

### Scenario 1: Standardizing Pre-commit Across 20+ Repos

**Option A - Centralized Reference:**

```yaml
# Each repo's .pre-commit-config.yaml
repos:
  - repo: https://github.com/yourorg/pre-commit-configs
    rev: v2.1.0
    hooks:
      - id: standard-checks
```

- **Tools**: pre-commit + Renovate for version updates
- **Pros**: Version control, gradual adoption
- **Cons**: Manual initial setup per repo

**Option B - Automated Sync:**

- **Tools**: multi-gitter + scheduled CI
- **Pros**: Fully automated, bulk updates
- **Cons**: Less control per team

### Scenario 2: Common Dependencies (e.g., security libraries)

**Option A - Renovate Custom Manager:**

```json
{
  "customManagers": [{
    "customType": "regex",
    "fileMatch": ["^requirements.*\\.txt$"],
    "matchStrings": ["security-lib==(?<currentValue>.*?)\\n"],
    "datasourceTemplate": "pypi",
    "depNameTemplate": "security-lib"
  }]
}
```

**Option B - Copybara Transformation:**

```python
core.workflow(
    name = "sync_security_deps",
    origin = git.origin(url = "https://github.com/org/templates"),
    destination = git.destination(url = "https://github.com/org/service"),
    transformations = [
        core.replace("requirements.txt", "security-lib==1.0.0", "security-lib==2.0.0")
    ]
)
```

## Language-Specific Build Tools (For Context)

| Language | Modern Tools | Traditional Tools | Key Considerations |
|----------|--------------|-------------------|-------------------|
| **JavaScript/TypeScript** | Vite, esbuild, swc, Bun, Rome/Biome | Webpack, Babel, TSC | Speed vs compatibility |
| **Python** | Poetry, PDM, Hatch, Rye | pip, setuptools, pipenv | Dependency resolution complexity |
| **Go** | go modules, go work | dep, glide | Mostly standardized on go modules |
| **Rust** | Cargo (standard) | - | Excellent built-in tooling |
| **Java/JVM** | Gradle, Maven | Ant | Gradle for flexibility, Maven for convention |
| **Ruby** | Bundler (standard) | - | Mostly standardized on Bundler |

## Decision Matrix for Your Startup

### For Multi-Repo, Polyglot Setup

**Recommended Combination:**

1. **Runtime Management**: `mise` - Handles all languages uniformly, fast, modern
2. **Task Running**: `Just` or `Task` - Simple, works across repos, minimal setup
3. **CI/CD Orchestration**: Consider `Earthly` or `Dagger` for reproducible builds
4. **Dependency Updates**: `Renovate` - Excellent multi-repo support
5. **Multi-Repo Sync**: `multi-gitter` or `git-xargs` for simple needs, `Copybara` for complex transformations
6. **Pre-commit Standardization**: Centralized pre-commit config repo + version pinning

**If Moving to Monorepo:**

1. **Small-Medium Scale**: `Turborepo` + `mise`
2. **Large Scale/Complex**: `Nx` + `mise`
3. **Python-Heavy**: Consider `Pants` + `mise`

### Key Evaluation Criteria

| Criteria | Weight | Considerations |
|----------|--------|----------------|
| **Language Support** | High | Does it handle all your languages equally well? |
| **Learning Curve** | Medium | Can your team adopt it quickly? |
| **Caching Strategy** | High | Local vs remote, granularity, invalidation |
| **Migration Path** | High | Can you adopt incrementally? |
| **CI/CD Integration** | High | Does it work with your existing pipeline? |
| **Community/Support** | Medium | Active development, documentation quality |
| **Performance** | Medium | Build times, cold starts, cache hits |

### Migration Strategy Suggestions

1. **Start with runtime management** (mise) - Immediate benefit, low risk
2. **Add task standardization** (Just/Task) - Creates consistency across repos
3. **Evaluate build orchestration** only if you have clear pain points:
   - Long CI times → Focus on caching solutions
   - Complex dependencies → Consider Nx/Bazel
   - Reproducibility issues → Look at Earthly/Nix-based tools

### Anti-Patterns to Avoid

- Don't adopt Bazel/Pants without dedicated build engineering resources
- Avoid mixing multiple task runners (Make + Just + package.json scripts)
- Don't implement remote caching before local caching is optimized
- Resist adopting monorepo tools if staying with multi-repo architecture
