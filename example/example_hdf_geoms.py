from prfpylot.output.hdf_geoms_writer import GeomsGenWriter

geomsgen_inputfile = "input_sodankyla_hdf_geoms.yml"
print(geomsgen_inputfile)

if __name__ == "__main__":
    MyCreator = GeomsGenWriter(geomsgen_inputfile)
    MyCreator.generate_geoms_files()
