from setuptools import setup

setup(
    name="PROFFASTpylot",
    packages=["prfpylot"],
    version="1.0",
    author="Benedikt Herkommer, Lena Feld",
    author_email="lena.feld@kit.edu, benedikt.herkommer@kit.edu",
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
        ],
    license='GPLv3',
    )
