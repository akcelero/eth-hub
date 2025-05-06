install-pre-commit-hooks:
	pre-commit install -c .github/pre-commit-config.yaml

update-pre-commit-hooks:
	pre-commit autoupdate -c .github/pre-commit-config.yaml

install-editable:
    uv pip install -e .
