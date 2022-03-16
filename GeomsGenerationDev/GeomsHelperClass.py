import h5py
import yaml
import sys
import os
import glob
import inspect
import collections as coll
import datetime as dt
import numpy as np
import pandas as pd

from prfpylot.prepare import Preparation


class Geoms_Helper(Preparation):
    def __init__(self, GEOMS_input_file):
        super(Geoms_Helper, self).__init__(GEOMS_input_file)

        # Read the input file.
        # Contains additional information to create the geoms file
        with open(GEOMS_input_file, "r") as f:
            self.input_args = yaml.load(f, Loader=yaml.FullLoader)
        self.input_file = GEOMS_input_file
        
        # Path of output files:
        self.geoms_out_filename = "_".join(
            [self.site_name,self.instrument_number, 'GEOMS_OUT.h5'])
        if self.input_args["geoms_out_path"] is not None:
            self.geoms_out_path = self.input_args["geoms_out_path"]
        else:
            self.geoms_out_path = os.getcwd()


    def _get_correction_factors(self):
        """Returns a dict containing the correction factors for the gases"""
        # This dict is only a preliminary version. In the final version it is
        # read in from a file
        df = pd.read_csv(
            self.input_args["calibration_params_list"],
            skipinitialspace=True)
        # strip the whitespaces from the column names:
        newCols = {}
        for key in df.keys():
            newCols[key]= key.strip()
        df.rename(columns=newCols, inplace=True)
        # Get the factors of the correct instrument
        df = df.loc[df["Instrument"] == self.instrument_number]
        return df.iloc[0].to_dict()

    def _find_colsens_invparms_file(self, date, which):
        """ 
        Returns the path to the correct colsens/invparm file.
        If colsen or invparms depends on the input of the argument `which`
        """
        if which not in ["colsens", "invparms"]:
            print("Give 'colsens' or 'invparms' for 'which'!")
            return ""
        # parse the result folders to find the correct time span
        searchstrg = f"{self.site_name}_{self.instrument_number}_*"
        folder_list = glob.glob(
            os.path.join(self.result_path, searchstrg))
        folder_list.sort()
        target_folder = ""        
        for folder in folder_list:
            if "_backup" in folder:
                continue
            startdate = dt.datetime.strptime(folder.split("_")[-2], "%Y%m%d")
            enddate = dt.datetime.strptime(folder.split("_")[-1]+"T23:59",
                                           "%Y%m%dT%H:%M")
            if date < startdate:
                continue
            if date > enddate:
                continue
            if date >= startdate and date <= enddate:
                target_folder = folder
                break
        filename = f"{self.site_name}{date.strftime('%y%m%d')}"+\
                   f"-{which}.dat"
        return os.path.join(target_folder, filename)

    def _find_invparms_file(self, date):
        """Find the correct folder where the *invparm.dat of date is located"""
        # in this test stage it only returns a hardcoded folder.
        # in future versions it looks for the correct result folder depending
        # on the date (remember: the results are in a date range folder!)
        path = "E:\\01_proffastpylot_dev\\example\\results\\Sodankyla"+\
               "_SN039_20170608_20170609\\"
        filename = f"{self.site_name}{self.date.strftime('%y%m%d')}"+\
                   "-invparms.dat"
        return os.path.join(path, filename)

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
            "pT",f"{which}_fast_out.dat")
        return file
