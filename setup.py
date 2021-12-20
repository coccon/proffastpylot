from setuptools import setup

setup(
    name="prfPylot",
    packages=["prfpylot"],
    author="Benedikt Herkommer, Lena Feld",
    author_email="lena.feld@kit.edu, benedikt.herkommer@kit.edu",
    description="Run PROFFAST with Python",
    install_requires=[
        "pandas",
        "PyYAML",
        "timezonefinder",
        "pytz",
        ],
    license='MIT',
    )
