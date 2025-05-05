install_pre_commit_hooks:
	pre-commit install -c .github/pre-commit-config.yaml

update_pre_commit_hooks:
	pre-commit autoupdate -c .github/pre-commit-config.yaml
