---
icon: lucide/heart-handshake
---
# Contributing

We welcome contributions to Pydgey! This guide covers the development setup and workflow.

## Quick Start

```bash
git clone https://github.com/leightonpayne/pydgey.git
cd pydgey
pixi install
```

## Development Commands

| Command                 | Description                 |
| ----------------------- | --------------------------- |
| `pixi run build`      | Build the React frontend    |
| `pixi run test`       | Run Python tests            |
| `pixi run lint`       | Check Python code style     |
| `pixi run lint-ui`    | Check frontend code style   |
| `pixi run format`     | Auto-format Python code     |
| `pixi run docs-serve` | Serve documentation locally |

## Project Structure

```
src/pydgey/
├── core/        # Pipeline, Config, Params, Errors
├── layout/      # UI elements, fields, validators, components
├── execution/   # Logging, progress, results
├── runtime/     # Commands, environment, Colab utilities
└── widget/      # PipelineWidget, transport, dist/
```

## Making Changes

### Backend (Python)

1. Make your changes in `src/pydgey/`
2. Run tests: `pixi run test`
3. Check style: `pixi run lint`

### Frontend (React/TypeScript)

1. Make changes in `frontend/src/`
2. Rebuild: `pixi run build`
3. Check style: `pixi run lint-ui`

### Documentation

1. Edit files in `docs/`
2. Preview: `pixi run docs-serve`
3. Check build: `pixi run docs-build`

## Testing Locally

Run example pipelines from the `examples/` directory:

```python
from pydgey import create_launcher
from examples.showcase.showcase_pipeline import ShowcasePipeline

create_launcher(ShowcasePipeline())
```

## Submitting Changes

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Submit a pull request

## Release Process

Maintainers release via GitHub Actions:

1. Run `pixi run bump` to increment version
2. Create a GitHub Release
3. CI builds and publishes to PyPI
