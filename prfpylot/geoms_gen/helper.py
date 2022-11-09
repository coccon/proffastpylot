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
        super(GeomsGenHelper, self).__init__(prfpylot_inputfile)

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
            newCols[key]= key.strip()
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
        print(target_folder)
        csv_file = glob.glob(os.path.join(
            target_folder, f"combined_invparms_{self.site_name}*.csv"))
        if len(csv_file) > 1:
            print("To many csv files in result folder. Exiting..")
            sys.exit(1)
        return csv_file[0]

    def _find_colsens_invparms_file(self, day, which):
        """
        Returns the path to the correct colsens/invparm file.
        If colsen or invparms depends on the input of the argument `which`
        """
        if which not in ["colsens", "invparms"]:
            print("Give 'colsens' or 'invparms' for 'which'!")
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

        # print("target folder", target_folder)
        # print("result folder", self.result_folder)
        return self.result_folder

    def _get_pt_vmr_file(self, day, which):
        """
        Returns the path to the pt- or vmr-file of a specific day.
        If pt or vmr depends on the input of the `which` parameter.
        """
        if which not in ["pT", "VMR"]:
            print("Parameter 'which' must be 'pT' or 'VMR'")
            return ""

        datestr = day.strftime("%y%m%d")
        file = os.path.join(
            self.analysis_instrument_path, datestr,
            "pT", f"{which}_fast_out.dat")
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
