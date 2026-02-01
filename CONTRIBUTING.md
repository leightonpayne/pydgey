# Contributing to Pydgey

Pydgey uses a hybrid architecture with a Python backend and a React/TypeScript frontend.

## Development Setup

We use [Pixi](https://pixi.sh/) to manage dependencies and development tasks.

### 1. Clone and Setup

```bash
git clone https://github.com/leightonpayne/pydgey.git
cd pydgey
pixi install
```

## Development Workflow

### 2. Frontend Development

The widget relies on the compiled React frontend (`src/pydgey/widget/dist/widget.js`). Rebuild when making UI changes:

```bash
pixi run build
```

Check for linting errors:

```bash
pixi run lint-ui
```

### 3. Backend Development

```bash
# Run tests
pixi run test

# Check code style
pixi run lint

# Format code
pixi run format
```

### 4. Run Locally

Example implementations are in `examples/`:

```bash
# Run example script
python examples/showcase/run_showcase.py
```

Or in a notebook inside `examples/showcase/`:

```python
import sys
sys.path.insert(0, "../../src")

from pydgey import create_launcher
from showcase_pipeline import ShowcasePipeline

widget = create_launcher(ShowcasePipeline())
widget
```

## Project Structure

```
pydgey/
├── frontend/                 # React + TypeScript UI
│   └── src/
├── src/pydgey/
│   ├── core/                 # Pipeline, Config, Params, Errors
│   ├── layout/               # UI elements, fields, validators, components
│   ├── execution/            # Logging, progress, results
│   ├── runtime/              # Commands, environment, Colab utilities
│   └── widget/               # PipelineWidget, transport, dist/
├── docs/                     # Documentation (MkDocs)
├── examples/                 # Example pipelines
└── pyproject.toml
```

## Documentation

Serve docs locally:

```bash
pixi run docs-serve
```

Build docs:

```bash
pixi run docs-build
```

## Release Process

The package auto-publishes to PyPI via GitHub Actions.

1. Bump version: `pixi run bump`
2. Create a GitHub Release
3. The action builds frontend, packages wheel, and publishes
