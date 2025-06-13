from prfpylot.auxiliary import PressureHandler, CoordHandler
from prfpylot.prepare import TimeHandler
import pandas as pd
import logging


# This short example illustrates how the internal PressureHandler and
# CoordHandler are working, different file types are illustrated

logger = logging.getLogger()


print("Vaisala pressure")
pressure_type_file = "vaisala_pressure_parameters.yml"
pressure_path = "input_data/pressure_coords_mobile/"
dates = [pd.Timestamp("2024-08-23")]


ph = PressureHandler(pressure_type_file, pressure_path, dates, logger)
ph.prepare_pressure_df()

t1 = pd.Timestamp("2024-08-23T15:26:00")
p1 = ph.get_pressure_at(t1.to_pydatetime())
print(f"pressure from {pressure_path} at {t1}: {p1}")

# test out of bounds
t2 = pd.Timestamp("2021-08-23T15:26:00")
p2 = ph.get_pressure_at(t2.to_pydatetime())
print(f"pressure from {pressure_path} at {t2}: {p2}")

# test acessing the frequency
f = ph.get_frequency(ph.p_df)
print(f"data frequency from {pressure_path} is {f}")


print(
    "\n"
    "Mira coord file"
)
coord_type_file = "mira_coord_parameters.yml"
coord_path = "input_data/pressure_coords_mobile/"
dates = [pd.Timestamp("2024-08-23")]
logger = logging.getLogger()
ch = CoordHandler(coord_type_file, coord_path, dates, logger)
ch.prepare_coord_df()

t3 = pd.Timestamp("2024-08-23T15:26:00")
c3 = ch.get_coords_at(t3)
print(f"coordinates from {coord_path} at {t3}: {c3}")

# test the Time Handler (get local_time, utc_time and measurement_time)
th = TimeHandler({"lat": c3[0], "lon": c3[1]}, 0)
igram = "input_data/interferograms/SN119/240823/240823SN.0160"
date_from_igram = th.get_times_from_opus(igram)
print(f"the date from {igram} is: {date_from_igram}")

# different coordinate file type
print(
    "\n"
    "Japan coordinates"
)
coord_type_file = "japan_coord_parameters.yml"
coord_path = "input_data/"
dates = [pd.Timestamp("2023-10-25")]
ch = CoordHandler(
    coord_type_file, coord_path, dates, logger,
    {"alt": 0.0, "lat": 10.0, "lon": 15.0})  # test giving static coordinates
ch.prepare_coord_df()
t4 = pd.Timestamp("2023-10-25T00:26:00")
c4 = ch.get_coords_at(t4)
print(f"coordinates from {coord_path} at {t4}: {c4}")
