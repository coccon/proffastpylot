import os


def test_dependencies() -> None:
    from prfpylot import pylot, prepare, download_example, auxiliary, filemover

    os.system("curl --version")
    os.system("gfortran --version")
    os.system("bash --version")
