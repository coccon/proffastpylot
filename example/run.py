"""Ready-to use example to demonstrate the usage of PROFFASTpylot.

To execute this file from .../proffastpylot/example as your working directory.

The Sodankyla example data set will be downloaded if not present.
All steps of the retrieval with PROFFAST will be executed
by Pylot.run() automatically.
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from prfpylot.download_example import ExampleDownloadHandler
from prfpylot.pylot import Pylot
from prfpylot.constants import EXAMPLE_DIR


# The `if __name__ == "__main__"`s tatement needs to be included in all run
# scripts to prevent problems with the multiprocessing on windows

if __name__ == "__main__":
    # download example data if not already present
    ExampleDownloadHandler.check_and_download_example_data(
        skip_confirmation=os.environ.get("NONINTERACTIVE", "0") == "1"
    )
    ExampleDownloadHandler.download_and_install_proffast()

    # run the example (change for your own setup)
    os.chdir(EXAMPLE_DIR)
    input_filepath = os.path.join(EXAMPLE_DIR, "config", "input_sodankyla_example.yml")
    MyPylot = Pylot(input_filepath, logginglevel="info")
    MyPylot.run(n_processes=2)
