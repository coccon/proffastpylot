"""Module to hand the pressure to PROFFAST.
The user can add own functions to handle the viarity of data formats.
"""

import pandas as pd
from datetime import datetime as dt


class PressureParameters():
    """Storage for different pressure file formats."""

    filename_parameters = {
        "log": {
            "basename": "",
            "time_format": "%Y-%m-%d",
            "ending": "*.dat"
        }
    }

    df_parameters = {
        "log": {
            "key_pressure": "BaroTHB40",
            "key_time": "UTCtime___",
            "fmt_time": "%H:%M:%S",
            "csv_kwargs": {
                "sep": "\t"
            }
        }
    }

    def get_filename(self, pressure_type, date):
        """Return merged filename of pressure_type."""
        params = self.filename_parameters[pressure_type]
        filename = "".join(
                [params["basename"],
                    date.strftime(params["time_format"]),
                    params["ending"]]
            )
        return filename


def create_p_lines(p_list):
    """Create a string with times and pressure in the format of the intraday file.
    
    Params:
        p_list: list of tuple with time and pressure.
    """
    p_lines_list = []
    for time, p in p_list:
        p_line = "\t".join(
            [
                time.strftime("%H%M%S"),
                str(p),
                "0.0"
            ])
        p_lines_list.append(p_line)
    p_lines = "\n".join(p_lines_list)
    return p_lines


def generate_pt_intraday(p_list, template_path):
    """Generate pt_intraday file from p_list.

    Params:
        p_list: See read_pressure_from_file
        template_path: path to  template_pt_intraday.inp
    """
    p_lines = create_p_lines(p_list)
    with open(template_path, "r") as f:
        intraday_lines = f.readlines()
    for i, line in enumerate(intraday_lines):
        intraday_lines[i] = line.replace("%p_lines%", p_lines)
        print(intraday_lines[i])
    pt_intraday = "".join(intraday_lines)
    return pt_intraday


def read_pressure_from_file(
        file, key_pressure, key_time, fmt_time, csv_kwargs={}):
    """Read list of lines with pairs of time and pressure.

    Params:
        file: filename including pressure and time data
            (has to be read by pandas.read_csv()).
        key_pressure: key of the pressure column
        key_time: key of the time column
        fmt_time: format string to read time column
            (see datetime.datetime.strptime())
        csv_kwargs: keyword arguments that are passed to pandas.read_csv()
            (for example {"sep"="\\t")

    """
    log = pd.read_csv(file, **csv_kwargs)
    p_list = []
    for i, row in log.iterrows():
        p = row[key_pressure]
        if p > 500 and p < 1500:
            time = dt.strptime(row[key_time], fmt_time)
            p_list.append((time, p))
    return p_list
