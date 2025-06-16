from setuptools import setup

setup(
    name="PROFFASTpylot",
    packages=["prfpylot"],
    version="prf2.4.1-0",
    author="Benedikt Herkommer, Lena Feld",
    author_email="lena.feld@kit.edu",
    description="Run PROFFAST with Python",
    install_requires=[
        "wheel",
        "pandas",
        "PyYAML",
        "timezonefinder",
        "pytz",
        "fortranformat",
        "requests",
        "tqdm",
        "numpy",
        "h5py",
        "netCDF4",
        "xarray",
        "cftime",
        ],
    license='GPLv3',
    )
