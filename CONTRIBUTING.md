# Contributing to Super-Model

Thanks for the interest. This is a personal project and PRs may not be merged, but issue reports and design feedback are welcome.

## Local dev setup

Detailed instructions arrive in a later phase, alongside `pyproject.toml`. The short version:

```sh
python -m venv .venv
. .venv/bin/activate    # or `.venv\Scripts\activate.bat` on Windows
pip install -e .[dev]
pytest tests/foundation/ -v
```

## Commit conventions

Imperative-mood subject lines, ~72 char max. Body wrapped at 72. Reference the implementation phase if relevant (e.g., `Phase 4 — atomic JSON writes`).

## Smoke test

After `pip install -e .[dev]`, run the script against a temp dir:

```sh
python super-mode-setup.py /tmp/smoketest
ls /tmp/smoketest/.super /tmp/smoketest/.claude
```

Expected: per-project state created; no user-level state touched.
