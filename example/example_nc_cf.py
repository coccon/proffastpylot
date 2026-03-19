import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from prfpylot.constants import EXAMPLE_DIR
from prfpylot.output.nc_cf_writer import NcWriter

NETCDF_DIR = os.path.join(EXAMPLE_DIR, "data", "output_netcdf")

if __name__ == "__main__":
    os.chdir(EXAMPLE_DIR)

    print("Cleaning up existing NetCDF files... ")
    for f in os.listdir(NETCDF_DIR):
        if f.endswith(".nc"):
            os.remove(os.path.join(NETCDF_DIR, f))

    for run_label in [
        "Sodankyla_SN039_170608-170609",
        "Tsukuba_SN063_240619-240722",
        "Heidelberg_SN119_240823-240823",
    ]:
        print(f"Processing run {run_label}...")
        result_path = os.path.join(EXAMPLE_DIR, "data", "results", run_label)
        if not os.path.exists(result_path):
            print(f"Results for run {run_label} not found at {result_path}. Skipping.")
            continue
        writer = NcWriter(result_path)
        filepath = os.path.join(NETCDF_DIR, writer.get_output_filename())
        writer.write_nc(filepath)

        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Expected NetCDF file not found at {filepath} after writing.")
        else:
            print(f"Successfully created NetCDF file at {filepath}.")
