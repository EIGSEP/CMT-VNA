# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Python package (`cmt_vna`) for controlling a Copper Mountain Technologies (CMT) R60 Vector Network Analyzer via SCPI commands over PyVISA. Measurement and instrument control only — the OSL calibration math based on Monsalve et al. 2016 lives in `eigsep_cal`. Designed for the EIGSEP radio astronomy project, typically deployed on a Raspberry Pi running Debian Trixie.

## Common Commands

```bash
# Install with dev dependencies
pip install -e .[dev]

# Run all tests
python -m pytest tests/ -v

# Run a single test file
python -m pytest tests/test_vna.py -v

# Run a specific test
python -m pytest tests/test_vna.py::TestDummyVNA::test_read_data -v

# Lint and format check
ruff check .
ruff format --check .

# Auto-fix formatting
ruff format .
```

## Architecture

Two modules in `src/cmt_vna/`. This package drives the instrument and does no analysis: the calibration math (`calkit`) lives in `eigsep_cal`.

- **`vna.py`** — `VNA` class: connects to the instrument via PyVISA (TCP socket on port 5025), configures measurement parameters, performs S11 measurements, runs OSL measurement sequences, and saves data to NPZ files. Optionally integrates with a `SwitchNetwork` (from `picohost`) for antenna/receiver switching.

- **`testing.py`** — `DummyVNA` and `DummyResource` classes that mock hardware for testing. `DummyVNA` extends `VNA` and overrides hardware communication; `DummyResource` simulates PyVISA responses.

## Code Style

- **ruff** for linting and formatting, 79-char line length
- No type hints (targets Python 3.10+ without typing imports)
- F401 (unused imports) suppressed in `__init__.py`
- `scripts/lab_test_scripts/`, `examples/`, and `*.ipynb` are excluded from linting

## Testing

- Tests use `DummyVNA`/`DummyResource` — no hardware needed
- pytest-timeout set to 60s per test
- Coverage reports via pytest-cov (uploaded to Codecov in CI)
- CI runs against Python 3.10, 3.11, 3.12, 3.13

## Release Process

Uses [release-please](https://github.com/googleapis/release-please) with conventional commits. Merging a release PR triggers PyPI publishing via trusted publishing (no API tokens).
