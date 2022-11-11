from prfpylot.geoms_gen.writer import GeomsGenWriter
import datetime as dt

geomsgen_inputfile = "input_sodankyla_geomsgen.yml"
prfpylot_inputfile = "input_sodankyla_example.yml"
date = dt.datetime.strptime("2017-06-08", "%Y-%m-%d")

if __name__ == "__main__":
    MyCreator = GeomsGenWriter(geomsgen_inputfile, prfpylot_inputfile)
    MyCreator.generate_GEOMS_at(day=date)
