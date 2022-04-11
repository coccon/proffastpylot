"""Pressure is a module of PROFFASTpylot.

Hand the pressure to PROFFAST, add own functions to handle different
data formats.

License information:
PROFFASTpylot - Running PROFFAST with Python
Copyright (C)   2022    Lena Feld, Benedikt Herkommer,
                        Karlsruhe Institut of Technology (KIT)

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License version 3 as published by
the Free Software Foundation.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import pandas as pd
import datetime as dt
import glob
import os
import numpy as np


class PressureHandler():
    """ A class to handle various pressure files. """
    def __init__(self, pressure_path, pArgs, dayList):
        self.pressure_path = pressure_path
        self.pArgs = pArgs
        self.dayList = dayList

    def prepare_pressure_df(self):
        """Read the pressure of a day, from files with a certain frequency
        """
        frequency = self.pArgs["frequency"]

        # Create a list containing all pressure files:
        if frequency == "subdaily":
            p_dict = self.read_subdaily_files()
        elif frequency == "daily":
            p_dict = self.read_subdaily_files()
        elif frequency == "weekly":
            raise NotImplementedError
        elif frequency == "monthly":
            raise NotImplementedError
        elif frequency == "yearly":
            p_dict = self.read_yearly_files()
        return p_dict

    def read_subdaily_files(self):
        """Reads the subdaily files into a single df
        """
        pressure_dict = {}
        for day in self.dayList:
            daily_df = pd.DataFrame()
            filename = self._get_filename(day)
            dataloggerFileList = glob.glob(
                os.path.join(self.pressure_path, filename))
            dataloggerFileList.sort()
            # get all files of one day and concat them:
            for file in dataloggerFileList:
                temp = pd.read_csv(
                    file,
                    **(self.pArgs["dataframe_parameters"]["csv_kwargs"]))
                daily_df = pd.concat([temp, daily_df])
            daily_df = self._parse_datetime_col(daily_df, day)
            pressure_dict[day] = self._to_pressure_list(daily_df)
        return pressure_dict

    def read_yearly_files(self):
        """read yearly files and return a dict containing the pressure
        for each day in dayList
        """
        first_year = self.dayList[0].year
        last_year = self.dayList[-1].year
        if first_year == last_year:
            years = [first_year]
        else:
            years = np.arange(first_year, last_year + 1)
        # read in all needed years:
        df = pd.DataFrame()
        for year in years:
            filename = self._get_filename(
                dt.datetime(year=year, month=2, day=1))
            fileList = glob.glob(
                os.path.join(self.pressure_path, filename))
            if len(fileList) > 1:
                raise RuntimeError("Found more than one yearly pressure file")
            if len(fileList) == 0:
                raise RuntimeError("Could not find a pressure file")
            temp = pd.read_csv(
                fileList[0],
                **(self.pArgs["dataframe_parameters"]["csv_kwargs"]))
            df = pd.concat([df, temp])

        pdtc = "parsed_datecol"
        df = self._parse_datetime_col(df)
        p_dict = {}
        # get the pressure values for each day:
        for day in self.dayList:
            day_strt = day.replace(hour=0, minute=0, second=0)
            day_stp = day.replace(hour=23, minute=59, second=59)

            # get a daily subset of the df:
            dailyDf = df.loc[(df[pdtc] > day_strt) & (df[pdtc] < day_stp)]
            p_dict[day] = self._to_pressure_list(dailyDf)
        return p_dict

    def generate_pt_intraday(self, p_list, template_path):
        """Generate pt_intraday file from p_list.

        Params:
            p_list: See read_pressure_from_file
            template_path: path to  template_pt_intraday.inp
        """
        p_lines = self._create_p_lines(p_list)
        with open(template_path, "r") as f:
            intraday_lines = f.readlines()
        for i, line in enumerate(intraday_lines):
            intraday_lines[i] = line.replace("%p_lines%", p_lines)
        pt_intraday = "".join(intraday_lines)
        return pt_intraday

    def _parse_datetime_col(self, df, date=None):
        """
        parse the dataframe for a suitable datetime.
        Add the column 'parsed_datecol' to the dataframe
        """
        df_args = self.pArgs["dataframe_parameters"]
        time_key = df_args["time_key"]
        time_fmt = df_args["time_fmt"]
        date_key = df_args["date_key"]
        date_fmt = df_args["date_fmt"]
        datetime_key = df_args["datetime_key"]
        datetime_fmt = df_args["datetime_fmt"]

        pdtc = "parsed_datecol"

        if time_key != "" and datetime_key != "":
            raise RuntimeError(
                "time_key and datetime_key can not be given at the same time")

        if datetime_key == "":
            # no datetime column available, check for date column:
            if date_key == "":
                # no date key avaliable as well. Do only take the time from
                # file.
                # day is taken from call day
                df[pdtc] = pd.to_datetime(
                    df[time_key], format=time_fmt)

                df[pdtc] = df[pdtc].apply(
                    lambda x: x.replace(
                        day=date.day, month=date.month, year=date.year))
            else:
                # combine two columns to datetime
                df[pdtc] = pd.to_datetime(
                    df[date_key] + df[time_key],
                    format=date_fmt+time_fmt)
        else:
            # seems that a datetime column is available:
            df[pdtc] = pd.to_datetime(df[datetime_key], format=datetime_fmt)
        return df

    def _to_pressure_list(self, df):
        """
        Gets an raw df and returns a list of tuples with
        (datetime, pressure)
        """
        pdtc = "parsed_datecol"
        df_args = self.pArgs["dataframe_parameters"]
        pressure_key = df_args["pressure_key"]
        # copy the dataframe to avoid strange results:
        df = pd.DataFrame(df)

        # Filter values which are too large or too small.
        # Replace or remove them.
        maxVal = float(self.pArgs["data_parameters"]["max_pressure"])
        minVal = float(self.pArgs["data_parameters"]["min_pressure"])
        replace_val = 0
        if self.pArgs["data_parameters"]["default_value"] == "skip":
            replace_val = np.nan
        else:
            replace_val = float(self.pArgs["data_parameters"]["default_value"])
        df[pressure_key] = np.where(
            df[pressure_key] > maxVal, replace_val, df[pressure_key])
        df[pressure_key] = np.where(
            df[pressure_key] < minVal, replace_val, df[pressure_key])
        df.dropna(inplace=True)

        # generate a list of tuples
        temp = df[[pdtc, pressure_key]].apply(tuple, axis=1)
        list = temp.tolist()

        return list

    def _get_filename(self, date):
        """Return merged filename of pressure_type."""
        params = self.pArgs["filename_parameters"]
        filename = "".join(
                [params["basename"],
                    date.strftime(params["time_format"]),
                    params["ending"]]
            )
        return filename

    def _create_p_lines(self, p_list):
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
