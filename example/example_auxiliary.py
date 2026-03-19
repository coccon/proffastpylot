import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from example.run_heidelberg_mobile import INPUT_DATA_DIR
from prfpylot.auxiliary import PressureHandler, CoordHandler
from prfpylot.prepare import TimeHandler
from prfpylot.constants import EXAMPLE_DIR
import pandas as pd
import logging

CONFIG_DIR = os.path.join(EXAMPLE_DIR, "config")
INPUT_DATA_DIR = os.path.join(EXAMPLE_DIR, "data", "input_data")

# This short example illustrates how the internal PressureHandler and
# CoordHandler are working, different file types are illustrated

if __name__ == "__main__":
    os.chdir(EXAMPLE_DIR)
    logger = logging.getLogger()

    print("--- Vaisala pressure ---\n")
    pressure_type_file = os.path.join(CONFIG_DIR, "vaisala_pressure_parameters.yml")
    pressure_path = os.path.join(INPUT_DATA_DIR, "pressure_coords_mobile")
    dates = [pd.Timestamp("2024-08-23")]

    ph = PressureHandler(pressure_type_file, pressure_path, dates, logger)
    ph.prepare_pressure_df()
    t1 = pd.Timestamp("2024-08-23T15:26:00")
    p1 = ph.get_pressure_at(t1.to_pydatetime())
    print(f"pressure from {pressure_path} at {t1}: {p1}")
    assert p1 is not None, f"Expected a pressure value for time {t1}, got None"
    assert 900 <= p1 <= 1100, f"Expected pressure value to be between 900 and 1100 hPa, got {p1}"

    # test out of bounds
    t2 = pd.Timestamp("2021-08-23T15:26:00")
    p2 = ph.get_pressure_at(t2.to_pydatetime())
    print(f"pressure from {pressure_path} at {t2}: {p2}")
    assert p2 is None, f"Expected None for out of bounds time, got {p2}"

    # test acessing the frequency
    f = ph.get_frequency(ph.p_df)
    print(f"data frequency from {pressure_path} is {f}")

    print("\n--- Mira coord file ---\n")
    coord_type_file = os.path.join(CONFIG_DIR, "mira_coord_parameters.yml")
    coord_path = os.path.join(INPUT_DATA_DIR, "pressure_coords_mobile")
    dates = [pd.Timestamp("2024-08-23")]
    logger = logging.getLogger()
    ch = CoordHandler(coord_type_file, coord_path, dates, logger)
    ch.prepare_coord_df()

    t3 = pd.Timestamp("2024-08-23T15:26:00")
    c3 = ch.get_coords_at(t3)
    print(f"coordinates from {coord_path} at {t3}: {c3}")
    assert c3 is not None, f"Expected coordinates for time {t3}, got None"
    assert isinstance(c3, list) and len(c3) == 3, (
        f"Expected a list of 3 coordinates (lat, lon, alt), got {c3}"
    )
    assert -90 <= c3[0] <= 90, f"Expected latitude to be between -90 and 90, got {c3[0]}"
    assert -180 <= c3[1] <= 180, f"Expected longitude to be between -180 and 180, got {c3[1]}"
    assert c3[2] >= 0, f"Expected altitude to be non-negative, got {c3[2]}"

    # test the Time Handler (get local_time, utc_time and measurement_time)
    th = TimeHandler({"lat": c3[0], "lon": c3[1]}, 0)  # type:ignore
    igram = os.path.join(INPUT_DATA_DIR, "interferograms", "SN119", "240823", "240823SN.0160")
    date_from_igram = th.get_times_from_opus(igram)
    print(f"the date from {igram} is: {date_from_igram}")
    assert isinstance(date_from_igram, dict), (
        f"Expected a dictionary of times, got {date_from_igram}"
    )
    assert "local_time" in date_from_igram, (
        f"Expected 'local_time' key in the times dictionary, got {date_from_igram}"
    )
    assert "utc_time" in date_from_igram, (
        f"Expected 'utc_time' key in the times dictionary, got {date_from_igram}"
    )
    assert "meas_time" in date_from_igram, (
        f"Expected 'measurement_time' key in the times dictionary, got {date_from_igram}"
    )

    # different coordinate file type
    print("\n--- Japan coordinates and pressure ---\n")
    coord_type_file = os.path.join(CONFIG_DIR, "japan_coord_parameters.yml")
    coord_path = INPUT_DATA_DIR
    dates = [pd.Timestamp("2023-10-25")]
    ch = CoordHandler(
        coord_type_file,
        coord_path,
        dates,
        logger,
        {"alt": 0.0, "lat": 10.0, "lon": 15.0},
    )  # test giving static coordinates
    ch.prepare_coord_df()
    t4 = pd.Timestamp("2023-10-25T00:26:00")
    c4 = ch.get_coords_at(t4)
    print(f"coordinates from {coord_path} at {t4}: {c4}")
    assert c4 is not None, f"Expected coordinates for time {t4}, got None"
    assert isinstance(c4, list) and len(c4) == 3, (
        f"Expected a list of 3 coordinates (lat, lon, alt), got {c4}"
    )
    assert -90 <= c4[0] <= 90, f"Expected latitude to be between -90 and 90, got {c4[0]}"
    assert -180 <= c4[1] <= 180, f"Expected longitude to be between -180 and 180, got {c4[1]}"
    assert c4[2] >= 0, f"Expected altitude to be non-negative, got {c4[2]}"

    pressure_type_file = os.path.join(CONFIG_DIR, "pressure_type_tsukuba.yml")
    pressure_path = os.path.join(INPUT_DATA_DIR, "pressure_tsukuba")
    dates = [pd.Timestamp("2024-07-22")]

    ph = PressureHandler(pressure_type_file, pressure_path, dates, logger)
    ph.prepare_pressure_df()
    t5 = pd.Timestamp("2024-07-22T12:00:00")
    p5 = ph.get_pressure_at(t5.to_pydatetime())
    print(f"pressure from {pressure_path} at {t5}: {p5}")
    assert p5 is not None, f"Expected a pressure value for time {t5}, got None"
    assert 900 <= p5 <= 1100, f"Expected pressure value to be between 900 and 1100 hPa, got {p5}"

    print("\n---")
