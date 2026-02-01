# Pydgey

[![Support](https://img.shields.io/pypi/status/pydgey?label=support&color=f3c539)](https://pypi.org/project/pydgey/) [![PyPI](https://img.shields.io/pypi/v/pydgey?label=pypi&color=107cb8)](https://pypi.org/project/pydgey/)

<p align="center">
  <img src="docs/static/pydgey-logo.png" width="50%" alt="poorly drawn pydgey logo">
</p>

## Overview

Pydgey is a Python framework for building simple graphical user interfaces for pipelines that run interactively in Jupyter Notebooks (e.g., [Google Colab](https://colab.research.google.com/), [VSCode](https://code.visualstudio.com/docs/datascience/jupyter-notebooks), [JupyterLab](https://jupyter.org/)).

Built on top of [anywidget](https://anywidget.dev/), [React](https://react.dev/), and [shadcn/ui](https://ui.shadcn.com/), Pydgey aims to abstract away some of the complexities of widget building. It allows for pipelines to be defined using standard Python classes, and handles the generation of a clean, React-based UI.

## Purpose

I needed a simple framework to quickly wrap tools and basic pipelines into user-friendly interfaces that run easily on Google Colab. The goal being to save Bachelors and Masters students in our lab the hassle of installing and managing command-line tools, letting them focus on the limited time they have to actually *do science*.

As the intended use is to run Pydgey widgets within the constraints of free Google Colab environments, the goal is not to support massive scale, high-concurrency execution, or complex dependency graphs like [Snakemake](https://snakemake.github.io/) or [Nextflow](https://www.nextflow.io/). Pydgey prioritizes accessibility and ease-of-use for smaller, ad-hoc analyses over the computational efficiency required for large-scale workflows.

## Getting Started

Read [the documentation](https://leightonpayne.github.io/pydgey/) for information on how to use the Pydgey framework.
