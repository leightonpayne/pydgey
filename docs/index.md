---
icon: lucide/home
---
# Pydgey

<p align="center">
  <img src="static/pydgey-logo.png" width="50%" alt="poorly drawn pydgey logo">
</p>

## Overview

Pydgey is a Python framework for building simple graphical user interfaces for pipelines that run interactively in Jupyter Notebooks (e.g., [Google Colab](https://colab.research.google.com/), [VSCode](https://code.visualstudio.com/docs/datascience/jupyter-notebooks), [JupyterLab](https://jupyter.org/)).

Built on top of [anywidget](https://anywidget.dev/), [React](https://react.dev/), and [shadcn/ui](https://ui.shadcn.com/), Pydgey aims to abstract away some of the complexities of widget building. It allows for pipelines to be defined using standard Python classes, and handles the generation of a clean, React-based UI.

## Purpose

I needed a simple framework to quickly wrap tools and basic pipelines into user-friendly interfaces that run easily on Google Colab. The goal being to save Bachelors and Masters students in our lab the hassle of installing and managing command-line tools, letting them focus on the limited time they have to actually *do science*.

As the intended use is to run Pydgey widgets within the constraints of free Google Colab environments, the goal is not to support massive scale, high-concurrency execution, or complex dependency graphs like [Snakemake](https://snakemake.github.io/) or [Nextflow](https://www.nextflow.io/). Pydgey prioritizes accessibility and ease-of-use for smaller, ad-hoc analyses over the computational efficiency required for large-scale workflows.

## Getting Started

Check out the [Installation](about/installation.md) guide to get set up, or jump straight into [Usage](usage/the-whole-game.md) to build your first pipeline.
