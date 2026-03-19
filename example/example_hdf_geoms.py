import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from prfpylot.download_example import ExampleDownloadHandler
from prfpylot.output.hdf_geoms_writer import GeomsGenWriter
from prfpylot.constants import EXAMPLE_DIR

if __name__ == "__main__":
    # download example data if not already present
    ExampleDownloadHandler.check_and_download_example_data(
        skip_confirmation=os.environ.get("NONINTERACTIVE", "0") == "1"
    )
    ExampleDownloadHandler.download_proffast()

    # run the example
    os.chdir(EXAMPLE_DIR)
    geomsgen_inputfile = os.path.join(EXAMPLE_DIR, "config", "input_sodankyla_hdf_geoms.yml")
    MyCreator = GeomsGenWriter(geomsgen_inputfile)
    MyCreator.generate_geoms_files()
