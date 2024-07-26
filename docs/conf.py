# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import sys
from typing import Generic, TypeVar, get_args
from warnings import warn

sys.path.insert(0, os.path.abspath(os.path.join(__file__, "..", "..")))

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "zammadoo"
copyright = "2023, MMM"
author = "flashdagger"

# The full version, including alpha/beta/rc tags
release = "0.4.0.dev0"
# The short X.Y version
version = ".".join(release.split(".")[:2])

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration
html_logo = "images/zammadoo.svg"
html_favicon = "images/favicon.ico"

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.coverage",
]

autodoc_default_options = {
    "undoc-members": True,
    "member-order": "groupwise",
    "exclude-members": "cached_info",
    "inherited-members": True,
}
autoclass_content = "both"
autodoc_typehints = "description"
autodoc_member_order = "groupwise"
autodoc_class_signature = "mixed"
autodoc_typehints_description_target = "documented"
autodoc_typehints_format = "short"
autodoc_inherit_docstrings = False
maximum_signature_line_length = None
add_module_names = False

templates_path = ["_templates"]


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

# The master toctree document.
master_doc = "index"

# The language for content autogenerated by Sphinx. Refer to documentation
# for a list of supported languages.
#
# This is also used if you do content translation via gettext catalogs.
# Usually you set "language" from the command line for these cases.
language = "en"

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path .
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = "sphinx"

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "sphinx_rtd_theme"

# Theme options are theme-specific and customize the look and feel of a theme
# further.  For a list of options available for each theme, see the
# documentation.
html_theme_options = {
    "canonical_url": "",
    "analytics_id": "",
    "logo_only": False,
    "display_version": True,
    "prev_next_buttons_location": "bottom",
    "style_external_links": False,
    "collapse_navigation": True,
    "sticky_navigation": True,
    "navigation_depth": 3,
    "includehidden": True,
    "titles_only": False,
}


html_static_path = ["_static"]
html_css_files = ["css/custom.css"]


def generic_return(cls, method):
    if isinstance(method, str):
        method = getattr(cls, method, object())
    annotations = getattr(method, "__annotations__", {})
    return_type = annotations.get("return")

    if return_type and isinstance(return_type, TypeVar):
        if isinstance(cls, Generic):
            orig_cls = getattr(cls, "__orig_class__")
            return_type = get_args(orig_cls)[0]
        elif annotations.get("self") is return_type:
            return {**annotations, "return": cls}

    return return_type


def docstring_hook(_app, what, name, obj, _options, _lines):
    if what != "class":
        return

    annotations = {}
    for cls in reversed(obj.mro()):
        cls_annotations = getattr(cls, "__annotations__", None)

        if cls_annotations is None:
            continue

        for key, attr in cls.__dict__.items():
            if (
                key.startswith("_")
                or not isinstance(attr, object)
                or key in cls_annotations
                or callable(attr)
            ):
                continue

            try:
                return_type = generic_return(attr, "__get__")
                if return_type is not None:
                    annotations[key] = return_type
            except AttributeError:
                warn(f"Cannot determine generic type of {name}.{key}={cls}")

        if cls is obj and annotations:
            cls_annotations.update(
                {
                    key: value
                    for key, value in annotations.items()
                    if key not in cls_annotations
                }
            )


def setup(app):
    app.connect("autodoc-process-docstring", docstring_hook)
