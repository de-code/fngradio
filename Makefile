#!/usr/bin/make -f

VENV = .venv
UV = uv
PIP = $(VENV)/bin/pip
PYTHON = $(VENV)/bin/python

PYTEST_WATCH_MODULES =
ARGS =


venv-clean:
	@if [ -d "$(VENV)" ]; then \
		rm -rf "$(VENV)"; \
	fi

venv-create:
	$(UV) venv

dev-install:
	$(UV) sync

dev-upgrade-all:
	$(UV) sync --upgrade

dev-venv: venv-create dev-install


dev-flake8:
	$(UV) run -m flake8 fngradio tests

dev-pylint:
	$(UV) run -m pylint fngradio tests

dev-mypy:
	$(UV) run -m mypy --check-untyped-defs fngradio tests

dev-lint: dev-flake8 dev-pylint dev-mypy


dev-unit-tests:
	$(UV) run -m pytest -vv

dev-watch:
	$(UV) run -m pytest_watcher \
		--runner=$(VENV)/bin/python \
		. \
		-m pytest -vv $(PYTEST_WATCH_MODULES)


dev-test: dev-lint dev-unit-tests


dev-run-example-simple:
	$(UV) run -m examples.simple


dev-run-example-complex:
	$(UV) run -m examples.complex


dev-build-dist:
	$(UV) build
