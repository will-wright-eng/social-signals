REPO_ROOT := $(shell git rev-parse --show-toplevel)


.PHONY: $(shell sed -n -e '/^$$/ { n ; /^[^ .\#][^ ]*:/ { s/:.*$$// ; p ; } ; }' $(MAKEFILE_LIST))

.DEFAULT_GOAL := help

help: ## list make commands
	@echo ${MAKEFILE_LIST}
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

user-repos: ## fetch user repos (usage: make user-repos user=username)
	@if [ -z "$(user)" ]; then \
		echo "Error: user parameter is required. Usage: make user-repos user=username"; \
		exit 1; \
	fi
	bash scripts/fetch-repos.sh "$(user)"

analyze-repos: ## analyze user repos (usage: make analyze-repos dir=directory-name)
	@if [ -z "$(dir)" ]; then \
		echo "Error: dir parameter is required. Usage: make analyze-repos dir=directory-name"; \
		exit 1; \
	fi
	bash scripts/analyze-repo-file.sh "$(REPO_ROOT)/scripts/results/$(dir)/public_repo_urls.txt"

#* Cleaning
pycache-remove: ## cleanup subcommand - pycache-remove
	find . | grep -E "(__pycache__|\.pyc|\.pyo$$)" | xargs rm -rf

dsstore-remove: ## cleanup subcommand - dsstore-remove
	find . | grep -E ".DS_Store" | xargs rm -rf

mypycache-remove: ## cleanup subcommand - mypycache-remove
	find . | grep -E ".mypy_cache" | xargs rm -rf

ipynbcheckpoints-remove: ## cleanup subcommand - ipynbcheckpoints-remove
	find . | grep -E ".ipynb_checkpoints" | xargs rm -rf

pytestcache-remove: ## cleanup subcommand - pytestcache-remove
	find . | grep -E ".pytest_cache" | xargs rm -rf

cleanup: pycache-remove dsstore-remove mypycache-remove ipynbcheckpoints-remove pytestcache-remove ## run all cleanup commands
