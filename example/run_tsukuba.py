import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from prfpylot.pylot import Pylot
from prfpylot.constants import EXAMPLE_DIR


if __name__ == "__main__":
    os.chdir(EXAMPLE_DIR)
    input_file = os.path.join(EXAMPLE_DIR, "config", "proffastpylot_parameters_tsukuba.yml")
    Pylot(input_file).run(n_processes=2)
