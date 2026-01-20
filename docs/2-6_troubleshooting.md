# Troubleshooting

In case of problems, please first take a look in the `results/<site>_<instrument>_<dates>/logfiles` folder. There the output of `PROFFASTpylot`, as well as the output of the subroutines `preprocess`, `pcxs` and `invers` are stored. Sometimes the subroutines fail without returning an error, therefore it looks successful at first in the pylot logfile.

If you encounter any problems, please do not hesitate to contact us via email or directly in GitLab. We will update this documentation with the occurring problems.

## Installation

### Problems creating a virtual environment

If you have several python installations, and some are not included to your `PATH` variable it might happen that the creation of a virtual environment results in `Error: [WinError 2] The system cannot find the file specified`.      

In this case the solution can be to give to full path to your python executable whilst creating the virtual environment: `C:\path\to\your\python\python.exe -m venv prf_venv`

## Execution

### Infinite Loop: General logfile is being used by another process

Ensure if your run-script contains `if __name__ == "__main__"`. If this is missing, it can crash the multiprocessing in a Windows environment.
