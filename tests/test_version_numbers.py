import os
import tomllib
import pytest


ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


@pytest.mark.order(0)
def test_project_version_equality() -> None:
    with open(os.path.join(ROOT_DIR, "pyproject.toml"), "rb") as f:
        pyproject_version = tomllib.load(f)["project"]["version"]

    with open(os.path.join(ROOT_DIR, "docs", "conf.py"), "r", encoding="utf-8") as f:
        conf_source = f.read()
    assert f'release = "{pyproject_version}"' in conf_source.replace("'", '"'), (
        "Version mismatch: pyproject.toml and docs/conf.py do not match"
    )
