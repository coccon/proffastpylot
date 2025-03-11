from prfpylot.pressure import PressureHandler, CoordHandler
from prfpylot.prepare import TimeHandler
import pandas as pd
import logging


pressure_type_file = "vaisala_pressure_parameters.yml"
pressure_path = "input_data/pressure_coords_mobile/"
# dates = [pd.Timestamp("2017-06-08"), pd.Timestamp("2017-06-09")]
dates = [pd.Timestamp("2024-08-23")]
logger = logging.getLogger()

ph = PressureHandler(pressure_type_file, pressure_path, dates, logger)
ph.prepare_pressure_df()
print(ph.p_df)
# p = ph.get_pressure_at(pd.Timestamp("2017-06-09T20:26:00"))
p = ph.get_pressure_at(pd.Timestamp("2024-08-23T15:26:00"))
print("pressure", p)

print(ph.get_frequency(ph.p_df))


coord_type_file = "mira_coord_parameters.yml"
coord_path = "input_data/pressure_coords_mobile/"
dates = [pd.Timestamp("2024-08-23")]
logger = logging.getLogger()
ch = CoordHandler(coord_type_file, coord_path, dates, logger)
ch.prepare_coord_df()
print(ch.get_frequency(ch.coord_df))
coords = ch.get_coords_at(pd.Timestamp("2024-08-23T15:26:00"))
print(coords)
th = TimeHandler({"lat": coords[0], "lon": coords[1]}, 0)
igram = "input_data/interferograms/SN119/240823/240823SN.0160"
date_from_igram = th.get_times_from_opus(igram)
print(date_from_igram)
