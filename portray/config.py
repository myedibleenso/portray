"""Defines the configuration defaults and load functions used by `portray`"""
import os
from typing import Dict, List, Union, cast
from urllib import parse

import mkdocs.config as _mkdocs_config
import mkdocs.exceptions as _mkdocs_exceptions
from git import Repo
from toml import load as toml_load

from portray.exceptions import NoProjectFound

PORTRAY_DEFAULTS = {"docs_dir": "docs", "output_dir": "site", "port": 8000, "host": "127.0.0.1"}

MKDOCS_DEFAULTS = {
    "site_name": os.path.basename(os.getcwd()),
    "theme": {
        "name": "material",
        "palette": {"primary": "green", "accent": "lightgreen"},
        "custom_dir": os.path.join(os.path.dirname(__file__), "mkdocs_templates"),
    },
    "markdown_extensions": [
        "admonition",
        "codehilite",
        "extra",
        "pymdownx.details",
        "pymdownx.highlight",
    ],
}

PDOC3_DEFAULTS = {
    "modules": [os.path.basename(os.getcwd())],
    "filter": None,
    "force": True,
    "html": False,
    "pdf": False,
    "html_dir": None,
    "html_no_source": False,
    "overwrite": False,
    "external_links": False,
    "template_dir": os.path.join(os.path.dirname(__file__), "pdoc3_templates"),
    "link_prefix": None,
    "close_stdin": False,
    "http": "",
    "config": {"show_type_annotations": True},
}  # type: Dict[str, Union[str, str, bool, None, Dict, List]]


def project(directory: str, config_file: str, **overrides) -> dict:
    """Returns back the complete configuration - including all sub configuration components defined below
       that `portray` was able to determine for the project
    """
    if not (
        os.path.isfile(os.path.join(directory, config_file))
        or os.path.isfile(os.path.join(directory, config_file))
    ):
        raise NoProjectFound(directory)

    project_config = {**PORTRAY_DEFAULTS, "directory": directory}
    project_config.update(toml(os.path.join(directory, config_file), **overrides))
    project_config["mkdocs"] = mkdocs(directory, **project_config.get("mkdocs", {}))
    project_config["pdoc3"] = pdoc3(directory, **project_config.get("pdoc3", {}))
    return project_config


def toml(location: str, **overrides) -> dict:
    """Returns back the configuration found within the projects
       [TOML](https://github.com/toml-lang/toml#toml) config (if there is one).

       Generally this is a `pyproject.toml` file at the root of the project
       with a `[tool.portray]` section defined.
    """
    try:
        config = toml_load(location).get("tool", {}).get("portray", {})
        config.update(overrides)
        config["file"] = location
        return config
    except Exception:
        print("WARNING: No {} config file found".format(location))

    return {}


def repository(directory: str) -> dict:
    """Returns back any information that can be determined by introspecting the projects git repo
       (if there is one).
    """
    config = {}
    try:
        config["repo_url"] = Repo(directory).remotes.origin.url
        config["repo_name"] = parse.urlsplit(config["repo_url"]).path.rstrip(".git").lstrip("/")
    except Exception:
        print("WARNING: Unable to identify `repo_name` and `repo_url` automatically")

    return config


def mkdocs(directory: str, **overrides) -> dict:
    """Returns back the configuration that will be used when running mkdocs"""
    return {**MKDOCS_DEFAULTS, **repository(directory), **overrides}


def pdoc3(directory: str, **overrides) -> dict:
    """Returns back the configuration that will be used when running pdoc3"""
    defaults = {**PDOC3_DEFAULTS}
    defaults["config"] = [
        "{}={}".format(key, value) for key, value in PDOC3_DEFAULTS["config"].items()
    ]
    defaults.update(overrides)
    return defaults
