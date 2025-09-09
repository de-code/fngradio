#!/usr/bin/make -f

VENV = .venv
UV = uv
PIP = $(VENV)/bin/pip
PYTHON = $(VENV)/bin/python

UV_RUN = $(UV) run --no-sync

PYTEST_WATCH_MODULES =
ARGS =


venv-clean:
	@if [ -d "$(VENV)" ]; then \
		rm -rf "$(VENV)"; \
	fi

venv-create:
	$(UV) venv

dev-install:
	$(UV) sync --frozen --all-extras --dev

dev-upgrade-all:
	$(UV) sync --upgrade

dev-venv: venv-create dev-install


dev-flake8:
	$(UV_RUN) -m flake8 fngradio tests examples

dev-pylint:
	$(UV_RUN) -m pylint fngradio tests examples

dev-mypy:
	$(UV_RUN) -m mypy --check-untyped-defs fngradio tests examples

dev-lint: dev-flake8 dev-pylint dev-mypy


dev-unit-tests:
	$(UV_RUN) -m pytest -vv $(ARGS)

dev-watch:
	$(UV_RUN) -m pytest_watcher \
		--runner=$(VENV)/bin/python \
		. \
		-m pytest -vv $(PYTEST_WATCH_MODULES)


dev-test: dev-lint dev-unit-tests


dev-run-example-simple:
	$(UV_RUN) -m examples.simple


dev-run-example-complex:
	$(UV_RUN) -m examples.complex


dev-build-dist:
	$(UV) build
