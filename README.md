# Try Jupyter, powered by JupyterLite

[![lite-badge](https://jupyterlite.rtfd.io/en/latest/_static/badge.svg)](https://jupyter.org/try-jupyter)

A tour of Jupyter and IPython, powered by JupyterLite.

## ✨ Try it in your browser ✨

➡️ **https://jupyter.org/try-jupyter**

Clicking the link above should load a JupyterLab environment running in your browser. Open the Introductory notebook at `notebooks/Intro.ipynb` to get started.

## About this repository

This is a demonstration repository meant for use at `try.jupyter.org`. It uses the [JupyterLite project](https://jupyterlite.readthedocs.io/en/latest/) to embed a self-contained Jupyter environment in the browser, along with many popular packages in scientific computing.

It uses GitHub pages to serve the JupyterLite bundle, and is accessible at https://jupyter.org/try-jupyter.

### How to edit these notebooks

The notebooks in this repository are written with [JupyterLite kernels](https://jupyterlite.readthedocs.io/en/latest/kernels/index.html), so if you edit them locally, you will likely over-write the kernel information with your local kernels.
As such, the easiest way to make edits to them is to do so [**via the Try Jupyter Page**](https://jupyter.org/try-jupyter).
Make the edits you wish at that URL, then download the notebook and replace the one in a repository locally.

### Beta site

The beta site at https://jupyter.org/try-jupyter/beta/ serves the same notebooks with the pre-releases of JupyterLite, JupyterLab and Jupyter Notebook.
`pixi run build-beta` builds it into `dist/beta` after `pixi run build`, and it loads the xeus kernel packages of the stable site to stay within the 1 GB limit of GitHub Pages.
To follow a newer pre-release of a package, set its label channel (`_alpha`, `_beta` or `_rc`) and its lower bound in `pyproject.toml`, then run `pixi update -e beta`.
Remove the label channel of a package once its final release is on conda-forge.
