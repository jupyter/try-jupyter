# -*- coding: utf-8 -*-

import shutil

extensions = [
    'myst_parser',
    'jupyterlite_sphinx'
]

jupyterlite_dir = "."
jupyterlite_contents = "content"

master_doc = 'index'
source_suffix = '.md'

# General information about the project.
project = 'Try Jupyter'
author = 'Project Jupyter'

exclude_patterns = []
highlight_language = 'python'
pygments_style = 'sphinx'

html_theme = "pydata_sphinx_theme"
html_static_path = ['_static']

html_css_files = [
    'custom.css'
]

shutil.copy('README.md', 'index.md')
