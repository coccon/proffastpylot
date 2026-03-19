import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from prfpylot.output.hdf_geoms_writer import GeomsGenWriter
from prfpylot.constants import EXAMPLE_DIR

HDF_GEOMS_DIR = os.path.join(EXAMPLE_DIR, "data", "output_hdf_geoms")

if __name__ == "__main__":
    os.chdir(EXAMPLE_DIR)

    print("Cleaning up existing HDF Geoms files... ")
    for f in os.listdir(HDF_GEOMS_DIR):
        if f.endswith(".h5"):
            os.remove(os.path.join(HDF_GEOMS_DIR, f))

    geomsgen_inputfile = os.path.join(EXAMPLE_DIR, "config", "input_sodankyla_hdf_geoms.yml")
    MyCreator = GeomsGenWriter(geomsgen_inputfile)
    MyCreator.generate_geoms_files()

    h5filecount: int = len([f for f in os.listdir(HDF_GEOMS_DIR) if f.endswith(".h5")])
    if h5filecount > 0:
        print(f"Successfully created {h5filecount} HDF Geoms files in {HDF_GEOMS_DIR}")
    else:
        raise FileNotFoundError(f"No HDF Geoms files were created in {HDF_GEOMS_DIR}.")
