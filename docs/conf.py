#!/home/ly1868/Temp_Pylot/docvenv/bin/python3
# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import os
import sys
sys.path.insert(0, os.path.abspath('../prfpylot'))



project = 'PROFFASTpylot'
copyright = '2023, Lena Feld, Benedikt Herkommer Karlsruhe Institut of Technology'
author = 'Lena Feld, Benedikt Herkommer'
release = 'v1.2'


# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration


def remove_module_docstring(app, what, name, obj, options, lines):
    if what == "module":
        del lines[:]


def setup(app):
    app.connect("autodoc-process-docstring", remove_module_docstring)


extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    # "myst_parser",
    'sphinx_mdinclude',
    ]

# source_suffix = ['.rst', '.md']
napoleon_use_rtype = False
autodoc_default_options = {
    "members": True,
    "undoc-members": True,
    "private-members": True
}

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'haiku'

html_static_path = ['_static']

# With the following code the KIT logo can be included.
# However, this is not working properly with the current custom CSS file!.
# html_logo= '_static/images/kitlogo_200dpi.png'
# html_theme_options = {
#     'full_logo': False}

html_css_files = ['css/custom.css']

