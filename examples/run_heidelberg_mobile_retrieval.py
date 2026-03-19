import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from prfpylot.pylot import Pylot
from prfpylot.constants import EXAMPLE_DIR
from utils import prepare_pylot_test_environment

CONFIG_DIR = os.path.join(EXAMPLE_DIR, "config")
DATA_DIR = os.path.join(EXAMPLE_DIR, "data")
INPUT_DATA_DIR = os.path.join(EXAMPLE_DIR, "data", "input_data")


if __name__ == "__main__":
    # download example data if not already present
    # possibly remove existing results to ensure a clean run
    results_filepath = prepare_pylot_test_environment("Heidelberg_SN119_240823-240823")

    # run the example
    os.chdir(EXAMPLE_DIR)
    proffastpylot_parameters = {
        "instrument_number": "SN119",
        "site_name": "Heidelberg",
        "site_abbrev": "he",
        "coord_file": os.path.join(INPUT_DATA_DIR, "coords.csv"),
        "interferogram_path": os.path.join(INPUT_DATA_DIR, "interferograms/SN119"),
        "map_path": os.path.join(INPUT_DATA_DIR, "pressure_coords_mobile"),
        "pressure_path": os.path.join(INPUT_DATA_DIR, "pressure_coords_mobile"),
        "pressure_type_file": os.path.join(CONFIG_DIR, "vaisala_pressure_parameters.yml"),
        "coord_type_file": os.path.join(CONFIG_DIR, "mira_coord_parameters.yml"),
        "analysis_path": os.path.join(DATA_DIR, "analysis"),
        "result_path": os.path.join(DATA_DIR, "results"),
        "coord_path": os.path.join(INPUT_DATA_DIR, "pressure_coords_mobile"),
        "altitude_factor": 1e-3,  # conversion to km
    }
    Pylot(proffastpylot_parameters).run()

    # check if the expected results file was created
    if not os.path.exists(results_filepath):
        raise FileNotFoundError(
            f"Expected results file not found at {results_filepath}. Please check the logs for any errors during the run."
        )
