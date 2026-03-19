import os
import sys
import pytest


ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXAMPLES_DIR = os.path.join(ROOT_DIR, "examples")
os.environ["NONINTERACTIVE"] = "1"  # ensure non-interactive mode for example data download


@pytest.mark.order(1)
def test_sodankyla_example() -> None:
    assert (
        os.system(f"{sys.executable} {os.path.join(EXAMPLES_DIR, 'run_sodankyla_retrieval.py')}")
        == 0
    )


@pytest.mark.order(2)
def test_tsukuba_example() -> None:
    assert (
        os.system(f"{sys.executable} {os.path.join(EXAMPLES_DIR, 'run_tsukuba_retrieval.py')}") == 0
    )


@pytest.mark.order(3)
def test_heidelberg_mobile_example() -> None:
    assert (
        os.system(
            f"{sys.executable} {os.path.join(EXAMPLES_DIR, 'run_heidelberg_mobile_retrieval.py')}"
        )
        == 0
    )


@pytest.mark.order(4)
def test_netcdf_generation() -> None:
    assert (
        os.system(f"{sys.executable} {os.path.join(EXAMPLES_DIR, 'example_netcdf_generation.py')}")
        == 0
    )


@pytest.mark.order(5)
def test_hdf_geoms_generation() -> None:
    assert (
        os.system(
            f"{sys.executable} {os.path.join(EXAMPLES_DIR, 'example_hdf_geoms_generation.py')}"
        )
        == 0
    )


@pytest.mark.order(6)
def test_auxiliary_examples() -> None:
    assert (
        os.system(f"{sys.executable} {os.path.join(EXAMPLES_DIR, 'example_auxiliary_usage.py')}")
        == 0
    )
