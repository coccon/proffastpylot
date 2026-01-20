from setuptools import setup

setup(
    name="PROFFASTpylot",
    packages=["prfpylot"],
    version="2.4.1-2",
    author="Benedikt Herkommer, Lena Feld, Darko Dubravica, Moritz Makowski",
    author_email="darko.dubravica@kit.edu, moritz.makowski@tum.de",
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
        "scipy",
    ],
    license="GPLv3",
)
