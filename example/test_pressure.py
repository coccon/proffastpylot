from prfpylot.pressure import PressureHandler
import pandas as pd
import logging


pressure_type_file = "log_type_pressure.yml"
pressure_path = "input_data/pressure_sodankyla/"
dates = [pd.Timestamp("2017-06-08"), pd.Timestamp("2017-06-09")]
logger = logging.getLogger()

ph = PressureHandler(pressure_type_file, pressure_path, dates, logger)
ph.prepare_pressure_df()
p = ph.get_pressure_at(pd.Timestamp("2017-06-09T20:26:00"))
print(p)
