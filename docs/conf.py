# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import sys, os, datetime
sys.path.insert(0, os.path.abspath('../circuitpython/'))

project = 'pico_synth_sandbox'
creation_year = '2023'
current_year = str(datetime.datetime.now().year)
year_duration = (
    current_year
    if current_year == creation_year
    else creation_year + ' - ' + current_year
)
copyright = year_duration + ' Cooper Dalrymple'
author = 'Cooper Dalrymple'

version = '0.1'
release = '0.1'

language = 'en'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
    'sphinxcontrib.jquery',
    'sphinx.ext.intersphinx',
    'sphinx.ext.napoleon',
    'sphinx.ext.todo'
]

autodoc_mock_imports = [
    "board",
    "ulab",
    "synthio",
    "audiomixer",
    "digitalio",
    "busio",
    "rotaryio",
    "touchio",
    "adafruit_debouncer",
    "usb_midi",
    "adafruit_midi",
    "adafruit_character_lcd",
    "pwmio",
    "audiopwmio",
    "audiobusio"
]

templates_path = ['_templates']
exclude_patterns = [
    '__pycache__',
    'bin',
    'tests',
    'Thumbs.db',
    '.DS_Store',
    '.env',
    'README.md'
]

todo_include_todos = False
todo_emit_warnings = False

napoleon_numpy_docstring = False

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

import sphinx_rtd_theme

html_theme = 'sphinx_rtd_theme'
html_theme_path = [sphinx_rtd_theme.get_html_theme_path(), '.']
html_static_path = ['../_static']
