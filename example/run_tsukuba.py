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
    ExampleDownloadHandler.download_proffast()

    # run the example
    os.chdir(EXAMPLE_DIR)
    input_file = os.path.join(EXAMPLE_DIR, "config", "proffastpylot_parameters_tsukuba.yml")
    Pylot(input_file).run(n_processes=2)
