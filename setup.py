from setuptools import setup

setup(
    name="prfPylot",
    packages=["prfpylot"],
    version="0.1",
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
    license='MIT',
    )
