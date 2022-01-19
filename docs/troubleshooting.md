# Troubleshooting

_(to be extended)_

If you encounter any problems, please do not hesitate to contact us. We will update this documentation with the occurring problems.


## Installation

### Problems creating a virtual environment

If you have several python installations, where some are not included to your
PATH variable it might happen that the creation of an virtual environment
results in  `Error: [WinError 2] The system cannot find the file specified`.      

In this case the a solution can be to give to full path to your python
executable whilst creating the virtual environment: `C:\path\to\your\python\python.exe -m venv prf_venv`


## Execution

### Infinite Loop: General logfile is being used by another process

Ensure if your runscript contains `if __name__ == "__main__"`. If this is missing, it can crash the multiprocessing in a Windows environment.
