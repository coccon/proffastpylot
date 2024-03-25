from prfpylot.geoms_gen.writer import GeomsGenWriter
import datetime as dt

geomsgen_inputfile = "input_sodankyla_geomsgen.yml"
prfpylot_inputfile = "input_sodankyla_example.yml"

if __name__ == "__main__":

    MyCreator = GeomsGenWriter(geomsgen_inputfile, prfpylot_inputfile)
    print (geomsgen_inputfile, prfpylot_inputfile)
    datetimes = MyCreator.get_datetimes()

    geoms_start_date = MyCreator.get_start_date()
    geoms_end_date = MyCreator.get_end_date()

    print (geoms_start_date, " ... ", geoms_end_date)
    for date in datetimes:
        if date < geoms_start_date:
            continue
        elif date > geoms_end_date:
            break
        else:
            print (date)
            MyCreator.generate_GEOMS_at(day=date)