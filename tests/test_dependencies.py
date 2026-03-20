import os
import pytest


@pytest.mark.order(0)
@pytest.mark.quick
def test_dependencies() -> None:
    from prfpylot import pylot, prepare, download_example, auxiliary, filemover

    assert os.system("curl --version") == 0
    assert os.system("gfortran --version") == 0
    assert os.system("bash --version") == 0
