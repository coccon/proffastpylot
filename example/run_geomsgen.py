from prfpylot.geoms_gen.writer import GeomsGenWriter

geomsgen_inputfile = "input_sodankyla_geomsgen.yml"
print(geomsgen_inputfile)

if __name__ == "__main__":
    MyCreator = GeomsGenWriter(geomsgen_inputfile)
    MyCreator.generate_geoms_files()
