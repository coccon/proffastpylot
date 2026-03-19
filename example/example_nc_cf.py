import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from prfpylot.download_example import ExampleDownloadHandler
from prfpylot.constants import EXAMPLE_DIR
from prfpylot.output.nc_cf_writer import NcWriter

if __name__ == "__main__":
    # download example data if not already present
    ExampleDownloadHandler.check_and_download_example_data(
        skip_confirmation=os.environ.get("NONINTERACTIVE", "0") == "1"
    )

    # run the example
    os.chdir(EXAMPLE_DIR)
    result_path = os.path.join(EXAMPLE_DIR, "results", "Sodankyla_SN039_170608-170609")
    writer = NcWriter(result_path)
    filename = writer.get_output_filename()
    writer.write_nc(filename)
