VENV?=.venv
PY?=$(VENV)/bin/python
PIP?=$(VENV)/bin/pip
RUFF?=$(VENV)/bin/ruff

.PHONY: help
help:
	@echo "Development:"
	@echo "  bootstrap        - Complete first-time setup (install + migrate + seed_db + superuser)"
	@echo "  install          - Create venv and install package in editable mode"
	@echo "  run              - Start Django dev server"
	@echo "  migrate          - Run Django migrations"
	@echo "  seed_db          - Set up demo site and home page"
	@echo "  superuser        - Create Django superuser"
	@echo "  shell            - Open Django shell"
	@echo "  collectstatic    - Collect static files"
	@echo ""
	@echo "Testing:"
	@echo "  test             - Run all tests"
	@echo "  test-cov         - Run tests with coverage report"
	@echo ""
	@echo "Code Quality:"
	@echo "  lint             - Run ruff linter"
	@echo "  format           - Format code with ruff"
	@echo "  check-format     - Check code formatting without modifying"
	@echo ""
	@echo "Build & Release:"
	@echo "  build            - Build distribution packages"
	@echo "  clean-build      - Remove build artifacts"
	@echo "  tag              - Create a git tag for the current version"
	@echo ""
	@echo "Cleanup:"
	@echo "  clean            - Remove venv and demo site artifacts"

.venv:
	@python3 -m venv $(VENV)
	@$(PIP) install --upgrade pip wheel

.PHONY: install
install: .venv
	# Install this package in editable mode (brings Django + deps via install_requires)
	$(PIP) install -e .[dev]
	@echo "Installation complete."

.PHONY: bootstrap
bootstrap: install migrate seed_db adminuser
	@echo ""
	@echo "========================================="
	@echo "Bootstrap complete! 🚀"
	@echo "========================================="
	@echo "Start the dev server with: make run"
	@echo ""
	@echo "Demo site can then be accessed at http://127.0.0.1:8000/"
	@echo "Admin login: admin / admin"
	@echo "=========================================" 

.PHONY: migrate
migrate:
	$(PY) demo_site/manage.py migrate

.PHONY: seed_db
seed_db:
	$(PY) demo_site/manage.py setup_demo

.PHONY: adminuser
adminuser:
	$(PY) demo_site/manage.py createsuperuser --username admin --email admin@example.com || true

.PHONY: superuser
superuser:
	$(PY) demo_site/manage.py createsuperuser || true

.PHONY: run
run:
	$(PY) demo_site/manage.py runserver

.PHONY: shell
shell:
	$(PY) demo_site/manage.py shell

.PHONY: collectstatic
collectstatic:
	$(PY) demo_site/manage.py collectstatic --noinput

# Testing
.PHONY: test
test:
	$(PY) demo_site/manage.py test cmsutils.tests

.PHONY: test-cov
test-cov:
	cd demo_site && DJANGO_SETTINGS_MODULE=demo_site.settings ../$(PY) -m coverage run --source='../cmsutils' manage.py test cmsutils.tests
	cd demo_site && ../$(PY) -m coverage report
	cd demo_site && ../$(PY) -m coverage html

# Code Quality
.PHONY: lint
lint:
	$(RUFF) check .

.PHONY: format
format:
	$(RUFF) format .
	$(RUFF) check --fix .

.PHONY: check-format
check-format:
	$(RUFF) format --check .

# Build & Release
.PHONY: build
build: clean-build
	$(PY) -m build

.PHONY: clean-build
clean-build:
	rm -rf build/ dist/ *.egg-info/

.PHONY: tag
# create git tag for the current version
tag:  ## Create a git tag for the current version
	@VERSION=$$(grep '^version = ' pyproject.toml | sed 's/version = "\(.*\)"/\1/'); \
	git tag -a "v$$VERSION" -m "Release version $$VERSION"; \
	git push origin "v$$VERSION"
	@echo "Created and pushed git tag v$$VERSION"

# Cleanup
.PHONY: clean
clean:
	rm -rf $(VENV) demo_site/db.sqlite3 demo_site/staticfiles demo_site/media