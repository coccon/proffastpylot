"""GeomsGenHelper is a module of PROFFASTpylot.

It contains several helper routines for the generation of
hdf5 files.

License information:
PROFFASTpylot - Running PROFFAST with Python
Copyright (C)   2022    Lena Feld, Benedikt Herkommer,
                        Darko Dubravica,
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


import yaml
import sys
import os
import math
import glob
import datetime as dt
import numpy as np
import pandas as pd


from prfpylot.prepare import Preparation


class GeomsGenHelper(Preparation):
    def __init__(self, geomsgen_inputfile, prfpylot_inputfile):
        super(GeomsGenHelper, self).__init__(
            prfpylot_inputfile, logginglevel="warning")

        self.geomsgen_logger = self.get_logger(logginglevel="info")

        # Read the input file.
        # Contains additional information to create the geoms file
        with open(geomsgen_inputfile, "r") as f:
            self.input_args = yaml.load(f, Loader=yaml.FullLoader)
        self.input_file = geomsgen_inputfile

        # Path of output files:
        self.geoms_out_filename = "_".join(
            [self.site_name, self.instrument_number, 'GEOMS_OUT.h5'])
        if self.input_args["geoms_out_path"] is not None:
            self.geoms_out_path = self.input_args["geoms_out_path"]
        else:
            self.geoms_out_path = os.getcwd()

    def _get_correction_factors(self):
        """Returns a dict containing the correction factors for the gases"""
        # This dict is only a preliminary version.
        # In the final version it is read in from a file.
        df = pd.read_csv(
            self.input_args["calibration_params_list"],
            skipinitialspace=True)
        # Strip the whitespaces from the column names:
        newCols = {}
        for key in df.keys():
            newCols[key] = key.strip()
        df.rename(columns=newCols, inplace=True)
        # Get the factors of the correct instrument
        df = df.loc[df["Instrument"] == self.instrument_number]
        return df.iloc[0].to_dict()

    # def _write_dataset(self, data, dataset_name, attributes, dtype):
    def _write_dataset(self, data, dataset_name, attributes):
        """
        Helper method to write a dataset to the file.
        Params:
            data (np.array): The data to be stored
            dataset_name (string): The name of the dataset
            attributes (dict): The attributes to be stored
        """
        dtst = self.MyHDF5.create_dataset(dataset_name, data=data, dtype='f')
        keys = [
            "VAR_FILL_VALUE",
            "VAR_VALID_MAX",
            "VAR_VALID_MIN",
            "_FillValue",
            "valid_range"]
        for key, value in attributes.items():
            if key in keys:
                dtst.attrs[key] = np.float32(value)
            else:
                dtst.attrs[key] = np.string_(value)
        return dtst

    def _write_dataset_src(self, data, dataset_name, attributes):
        """
        Helper method to write a dataset to the file.
        Params:
            data (np.array): The data to be stored
            dataset_name (string): The name of the dataset
            attributes (dict): The attributes to be stored
        """
        dtst = self.MyHDF5.create_dataset(dataset_name, data=data)
        for key, value in attributes.items():
            dtst.attrs[key] = np.string_(value)
        return dtst

    def _write_dataset_dt(self, data, dataset_name, attributes):
        """
        Helper method to write a dataset to the file.
        Params:
            data (np.array): The data to be stored
            dataset_name (string): The name of the dataset
            attributes (dict): The attributes to be stored
        """
        dtst = self.MyHDF5.create_dataset(dataset_name, data=data, dtype='f8')
        keys = [
            "VAR_FILL_VALUE",
            "VAR_VALID_MAX",
            "VAR_VALID_MIN",
            "_FillValue",
            "valid_range"]
        for key, value in attributes.items():
            if key in keys:
                dtst.attrs[key] = np.float64(value)
            else:
                dtst.attrs[key] = np.string_(value)
        return dtst

    def _find_csv_file(self, day):
        """
        Returns the csv file containing the correct data for the
        requested day
        Params:
            day (dt.datetime) The day the data is requested
        """
        target_folder = self._find_correct_folder(day)
        self.logger.debug(target_folder)
        csv_file = glob.glob(os.path.join(
            target_folder, f"combined_invparms_{self.site_name}*.csv"))
        if len(csv_file) > 1:
            self.logger.critical(
                "To many csv files in result folder. Exiting..")
            sys.exit(1)
        return csv_file[0]

    def _find_colsens_invparms_file(self, day, which):
        """
        Returns the path to the correct colsens/invparm file.
        If colsen or invparms depends on the input of the argument `which`
        """
        if which not in ["colsens", "invparms"]:
            self.logger.error("Give 'colsens' or 'invparms' for 'which'!")
            return ""
        target_folder = self._find_correct_folder(day)
        filename = f"{self.site_name}{day.strftime('%y%m%d')}" + \
                   f"-{which}_a.dat"
        return os.path.join(target_folder, filename)

    # why can self.result_folder not be used here instead?
    def _find_correct_folder(self, day):
        """
        Returns the path to the folder providing the data of the day
        Params:
            day (dt.datetime): the day the data is requested
        """
        # parse the result folders to find the correct time span
        # searchstrg = f"{self.site_name}_{self.instrument_number}_*"
        # folder_list = glob.glob(
        #     os.path.join(self.result_path, searchstrg))
        # folder_list.sort()
        # target_folder = ""
        # for folder in folder_list:
        #     if "_backup" in folder:
        #         continue
        #     folder_elements = folder.split("_")
        #     processing_time = folder_elements[-1].split("-")

        #     startdate = dt.datetime.strptime(
        #         processing_time[0], "%y%m%d")
        #     enddate = dt.datetime.strptime(
        #         processing_time[1]+"T23:59",
        #         "%y%m%dT%H:%M")

        #     if day < startdate:
        #         continue
        #     if day > enddate:
        #         continue
        #     if day >= startdate and day <= enddate:
        #         target_folder = folder
        #         break

        return self.result_folder

    def _get_pt_vmr_file(self, day, which):
        """
        Returns the path to the pt- or vmr-file of a specific day.
        If pt or vmr depends on the input of the `which` parameter.
        """
        if which not in ["pT", "VMR"]:
            self.logger.error("Parameter 'which' must be 'pT' or 'VMR'")
            return ""

        datestr = day.strftime("%y%m%d")
        file = os.path.join(
            self.result_folder, "pT-VMR-files",
            f"{self.site_name}{datestr}-{which}_fast_out.dat")
        return file

    def _GEOMStoDateTime(self, times):
        """
        Transforms GEOMS DATETIME variable to dt.datetime instances
        (input is seconds, since 1/1/2000 at 0UT)
        """
        ntimes = []
        times = times / 86400.
        t_ref = dt.date(2000, 1, 1).toordinal()

        for t in times:
            t_tmp = dt.datetime.fromordinal(t_ref + int(t))
            t_del = dt.timedelta(days=(t - math.floor(t)))

            ntimes.append(t_tmp + t_del)

        return np.array(ntimes)

    def _DateTimeToGEOMS(self, times):
        """
        Transforms dt.datetime instances to GEOMS DATETIME
        (output is seconds, since 1/1/2000 at 0UT)
        """
        gtimes = []

        t_ref = np.longdouble(dt.date(2000, 1, 1).toordinal())

        for t in times:
            t_h = np.longdouble(t.hour)
            t_m = np.longdouble(t.minute)
            t_s = np.longdouble(t.second)
            t_ms = np.longdouble(t.microsecond)
            t_ord = np.longdouble(t.toordinal())

            gtime = t_ord + (t_h + (t_m + (t_s + t_ms/1.e6) / 60.) / 60.) \
                / 24. - t_ref

            gtimes.append(gtime * 86400.)

        return np.array(gtimes)

    def apply_quality_checks(self, df):

        # Check if the second CO channel exists.
        CO_avg = df["XCO"].mean()
        if CO_avg == 0.:
            df["XCO"] = [-900000.]*len(df)

        # quality checks
        quality_check_passed = True
        for index, row in df.iterrows():
            if row["appSZA"] > self.input_args["QUALITY_FILTER_SZA"]:
                quality_check_passed = False
            if row["XAIR"] < self.input_args["QUALITY_FILTER_XAIR_MIN"]:
                quality_check_passed = False
            if row["XAIR"] > self.input_args["QUALITY_FILTER_XAIR_MAX"]:
                quality_check_passed = False

            for col in ["XH2O", "XCO2", "XCH4", "XCO"]:
                if row[col] in [np.nan, 0.]:
                    quality_check_passed = False

            # remove row from df
            if quality_check_passed is False:
                df.drop(index=index)

        # apply correction factors
        corr_fac = self._get_correction_factors()
        df["XCO2"] *= corr_fac["XCO2_cal"]
        df["XCH4"] *= corr_fac["XCH4_cal"]
        df["altim"] /= 1000.

        # write fill value to values out of bounds
        df["XH2O"].mask(df["XH2O"] <= 0., inplace=True)
        df["XH2O"].mask(df["XH2O"] >= 10000., inplace=True)
        df["XCO2"].mask(df["XCO2"] <= 0., inplace=True)
        df["XCO2"].mask(df["XCO2"] >= 10000., inplace=True)
        df["XCH4"].mask(df["XCH4"] <= 0., inplace=True)
        df["XCH4"].mask(df["XCH4"] >= 10., inplace=True)
        df["XCO"].mask(df["XCO"] <= 0., inplace=True)
        df["XCO"].mask(df["XCO"] >= 10000., inplace=True)

        fill_value = -900000.
        df.replace(np.nan, fill_value, inplace=True)

        # return none if less than 11 lines
        if len(df) < 11:
            raise RuntimeError("Less than 11 valid measurement points!")
        else:
            self.logger.debug('Data filter applied... ', 'file_len: ', len(df))
            return df

    def get_comb_invparms_df(self, day):
        invparms_file = self._comb_invparms_file()
        cols = [
            "UTC",
            "LocalTime",
            "JulianDate",
            "gndP",
            "gndT",
            "latdeg",
            "londeg",
            "altim",
            "appSZA",
            "azimuth",
            "XH2O",
            "XAIR",
            "XCO2",
            "XCH4",
            "XCH4_S5P",
            "XCO",
            "H2O",
            "O2",
            "CO2",
            "CH4",
            "CO",
            "CH4_S5P",
            "H2O_rms",
            "CO2_rms",
            "CH4_rms",
            "CO_rms",
        ]
        df = pd.read_csv(
            invparms_file, delimiter=",", skipinitialspace=True,
            parse_dates=["UTC", "LocalTime"]
            )

        df = df[cols]
        # drop all columns except the selected day
        for i, row in df.iterrows():
            current_date = row["LocalTime"].date()
            if current_date != day.date():
                df.drop(index=i, inplace=True)

        df = self.apply_quality_checks(df)
        return df
