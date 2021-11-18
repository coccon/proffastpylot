"""Module to hand the pressure to PROFFAST.
The user can add own functions to handle the viarity of data formats.
"""

import os
import shutil
import pandas as pd
from datetime import datetime as dt


log_file_parms = {
    "key_pressure": "BaroTHB40",
    "key_time": "UTCtime___",
    "fmt_time": "%H:%M:%S",
    "csv_kwargs": {
        "sep": "\t"
    }
}


def generate_pt_intraday(self, date):
    """Skript #3 generate pt files."""
    # TODO: Insert Header!

    date_str = date.strftime("%y%m%d")
    pt_folder = os.path.join(self.data_path, date_str, "pT")
    pt_file = os.path.join(pt_folder, "pT_intraday.inp")

    if self.intraday_path is not None:
        filename = "{}_{}.inp".format(
            self.site_abbrev, date.strftime("%y-%m-%d"))
        intraday_file = os.path.join(
            self.intraday_path, filename)
        shutil.copy(intraday_file, pt_file)
        return

    log_file = self.get_log_file(date)
    pt_lines = self._read_pressure_from_logfile(log_file)
    with open(pt_file, "w") as f:
        f.write("$\n")
        f.write("\n".join(pt_lines))
        f.write("\n***\n")


def read_pressure_from_file(
        self, file, key_pressure, key_time, fmt_time, csv_kwargs={}):
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
        p = row[key_time]
        if p > 500 and p < 1500:
            time = dt.strptime(row[key_time], fmt_time)
        p_list.append((p, time))
    return p_list


def create_p_lines(self, p_list):
    """Create list of lines in the format of the intraday file.
    Params:
        p_list: list of tuple with time and pressure.
    """
    p_lines = []
    for time, p in p_list:
        p_line = "\t".join(
            [
                time.strftime("%H%M%S"),
                str(p),
                "0.0"
            ])
        p_lines.append(p_line)
    return p_lines
