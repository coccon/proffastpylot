import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from prfpylot.pylot import Pylot
from prfpylot.constants import EXAMPLE_DIR
from utils import prepare_pylot_test_environment

# The `if __name__ == "__main__"`s tatement needs to be included in all run
# scripts to prevent problems with the multiprocessing on windows

if __name__ == "__main__":
    # download example data if not already present
    # possibly remove existing results to ensure a clean run
    results_filepath = prepare_pylot_test_environment("Tsukuba_SN063_240619-240722")

    # run the example
    os.chdir(EXAMPLE_DIR)
    input_file = os.path.join(EXAMPLE_DIR, "config", "proffastpylot_parameters_tsukuba.yml")
    Pylot(input_file).run(n_processes=2)

    # check if the expected results file was created
    if not os.path.exists(results_filepath):
        raise FileNotFoundError(
            f"Expected results file not found at {results_filepath}. Please check the logs for any errors during the run."
        )
