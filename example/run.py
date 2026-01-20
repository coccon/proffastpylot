"""Ready-to use example to demonstrate the usage of PROFFASTpylot.

To execute this file from .../proffastpylot/example as your working directory.

The Sodankyla example data set will be downloaded if not present.
All steps of the retrieval with PROFFAST will be executed
by Pylot.run() automatically.
"""

from prfpylot.download_example import ExampleDownloadHandler
from prfpylot.pylot import Pylot


# This statement needs to be executed in all run scripts to prevent problems
# with the multiprocessing on windows
if __name__ == "__main__":
    # Check if example input data is already available on disk,
    # if not download it.
    # This is not needed for your personal PROFASTpylot run-file
    ExampleDownloadHandler().check_and_download_example_data()

    # The following part can be adapted to your own retrieval
    input_file = "input_sodankyla_example.yml"
    MyPylot = Pylot(input_file, logginglevel="info")
    MyPylot.run(n_processes=2)
