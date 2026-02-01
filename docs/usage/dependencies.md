---
icon: lucide/blocks
---
# Dependency Management

Pydgey uses [Pixi](https://pixi.sh) for reproducible, declarative dependency management. When your pipeline ships with a `pixi.lock` file, Pydgey automatically ensures the correct environment is set up before execution.

## How It Works

1. **You ship a lockfile**: Your pipeline repository includes `pixi.toml` and `pixi.lock`.
2. **Pydgey detects it**: When `create_launcher()` runs, Pydgey looks for `pixi.lock` in the notebook directory.
3. **Auto-setup on Colab**: If on Google Colab and the environment isn't ready, Pydgey installs Pixi and runs `pixi install`.
4. **Transparent wrapping**: All commands executed via `run_command()` are automatically wrapped with `pixi run --`.

## Repository Structure

```
my-pipeline/
├── pixi.toml           # Dependency manifest
├── pixi.lock           # Lockfile (commit this!)
├── src/
│   └── my_pipeline.py
└── launcher.ipynb
```

## Creating pixi.toml

Define your external tool dependencies:

```toml
[project]
name = "my-pipeline"
channels = ["conda-forge", "bioconda"]
platforms = ["linux-64"]

[dependencies]
hmmer = ">=3.4"
prodigal = ">=2.6"
```

Generate the lockfile:

```bash
pixi install
```

Commit both `pixi.toml` and `pixi.lock` to your repository.

## Local Development

When developing locally, activate the Pixi environment in your terminal:

```bash
pixi shell
```

Or run Jupyter directly through Pixi:

```bash
pixi run jupyter lab
```

## The Colab Experience

When a user opens your notebook in Colab:

```python
%pip install pydgey
from pydgey import create_launcher
from src.my_pipeline import MyPipeline

create_launcher(MyPipeline())
```

On first run, the widget will:

1. Detect the `pixi.lock` file
2. Install Pixi (streaming logs)
3. Run `pixi install` (streaming logs)
4. Proceed with the pipeline

Subsequent runs skip the setup phase.

## Manual Environment Check

You can programmatically check the environment status:

```python
from pydgey import check_environment, setup_environment

env = check_environment()
print(f"Lockfile: {env.lockfile_path}")
print(f"Ready: {env.is_ready}")

# Force setup (useful in notebooks)
success, env = setup_environment(logger)
```

## Disabling Pixi Wrapper

If you need to run a command *without* the Pixi wrapper:

```python
run_command("ls -la", logger, use_pixi=False)
```
