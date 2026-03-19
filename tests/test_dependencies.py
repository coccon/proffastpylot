import os
import pytest


@pytest.mark.order(0)
@pytest.mark.quick
def test_dependencies() -> None:
    from prfpylot import pylot, prepare, download_example, auxiliary, filemover

    os.system("curl --version")
    os.system("gfortran --version")
    os.system("bash --version")
