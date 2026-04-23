"""Ready-to use example to demonstrate the usage of PROFFASTpylot.

To execute this file from .../proffastpylot/example as your working directory.

The Sodankyla example data set will be downloaded if not present.
All steps of the retrieval with PROFFAST will be executed
by Pylot.run() automatically.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from prfpylot.pylot import Pylot
from prfpylot.constants import EXAMPLE_DIR
from utils import prepare_pylot_test_environment


# The `if __name__ == "__main__"`s tatement needs to be included in all run
# scripts to prevent problems with the multiprocessing on windows

if __name__ == "__main__":
    # download example data if not already present
    # possibly remove existing results to ensure a clean run
    results_filepath = prepare_pylot_test_environment("Sodankyla_SN039_170608-170609")

    # run the example (change for your own setup)
    os.chdir(EXAMPLE_DIR)
    input_filepath = os.path.join(EXAMPLE_DIR, "config", "input_sodankyla_example.yml")
    MyPylot = Pylot(input_filepath, logginglevel="info")
    MyPylot.run(n_processes=2)

    # check if the expected results file was created
    if not os.path.exists(results_filepath):
        raise FileNotFoundError(
            f"Expected results file not found at {results_filepath}. Please check the logs for any errors during the run."
        )
