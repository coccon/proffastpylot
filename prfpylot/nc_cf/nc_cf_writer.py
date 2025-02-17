"""nc_cf_writer is a module of PROFFASTpylot.

Generate netcdf files following the cf conventions.

License information:
PROFFASTpylot - Running PROFFAST with Python
Copyright (C)   2025    Lena Feld
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
import numpy as np
from glob import glob
import os
import xarray as xr
import datetime as dt
import cftime
import prfpylot
from prfpylot.prepare import TimeHandler
import yaml
import inspect

# Todos:
# - Write ILS list to file
# - implement filters
# - implement attributes
#     - information from separate file
#     - information equivalent for all runs
#     - information gaven in proffastpylot input file
# - implement which version was used
# - add scaling factors (SI units, following cf conventions!)


class NcWriter(object):
    """
    Create netcdf files from PROFFAST output following the cf conventions.
    """
    cftime_unit = "days since 1990-01-01 00:00:00"
    cftime_calendar = "standard"
    sza = [
        0.0,
        0.3965,
        0.5607,
        0.6867,
        0.793,
        0.8866,
        0.9712,
        1.049,
        1.121,
        1.189,
        1.254,
        1.315,
        1.373,
        1.43,
        1.484]

    def __init__(self, path_results):
        self.path_results = path_results
        self.path_raw_output_proffast = os.path.join(
            path_results, "raw_output_proffast")

        path_proffastpylot_parameters = os.path.join(
            path_results, "proffastpylot_parameters.yml")
        with open(path_proffastpylot_parameters, "r") as f:
            proffastpylot_parameters = yaml.safe_load(f)

        self.utc_offset = proffastpylot_parameters.get("utc_offset")
        if self.utc_offset is None:
            self.utc_offset = 0.

        self.site_name = proffastpylot_parameters["site_name"]

        self.df_invparms = self.get_comb_invparms()
        self.coords = self.get_coords()

        self.time_handler = TimeHandler(
            coords=self.coords, utc_offset=self.utc_offset)

    def create_dataset(self):
        """Combine all proffast output in one ds.

        1. combine all data
        2. replace secondary time columns
        3. apply filters
        4. write all metadata and set fill_values

        Returns:
            dataset (xr.Dataset): dataset following the cf conventions
        """
        # combine all data
        ds = self.df_invparms.to_xarray()
        ds = self.modify_time(ds)
        ds = self.add_avk(ds)
        ds = self.add_prior(ds)

        # replace secondary time columns
        ds = self.add_local_noon_column(ds)
        ds = ds.drop(["LocalTime", "JulianDate", "UTtimeh"])

        # apply filters
        ds = self.apply_filters(ds)

        # write all metadata
        ds = self.add_variable_attrs(ds)
        ds = self.add_global_attrs(ds)
        # implement setting/using fill values

        return ds

    def get_coords(self):
        """Read coords from first line of comb_invparms.
        This is used for the time offsets, recording in multiple time zones
        is not supported."""
        coords = {
            "lat": self.df_invparms["latdeg"].iloc[0],
            "lon": self.df_invparms["londeg"].iloc[0],
        }
        return coords

    def modify_time(self, ds):
        """Rename, and make cf conform main time column."""

        time_atts = {
            "standard_name": "time",
            "long_name": "time of observation in UTC",
            "units": self.cftime_unit,
            "calendar": self.cftime_calendar,
        }

        cftime_data = cftime.date2num(
                    [t.to_pydatetime() for t in self.df_invparms.index],
                    units=self.cftime_unit,
                    calendar=self.cftime_calendar,
                )
        cftime_data
        ds = ds.rename_dims({"UTC": "time"})
        ds = ds.rename_vars({"UTC": "time"})
        ds["time"] = cftime_data
        ds["time"].attrs = time_atts
        return ds

    def add_local_noon_column(self, ds):
        local_noon = []
        for lt in self.df_invparms["LocalTime"]:
            ln = self.time_handler.get_local_noon_utc(lt.date())
            local_noon.append(ln)

        ds["local_noon"] = xr.DataArray(
            cftime.date2num(
                local_noon,
                units=self.cftime_unit,
                calendar=self.cftime_calendar),
            dims={"time": ds["time"]})
        return ds

    def apply_filters(self, ds):
        return ds

    def get_files_colsens(self):
        """Return filelist with all colsens files."""
        search_str = os.path.join(
            self.path_raw_output_proffast,
            "*colsens.dat"
        )

        files_colsens = sorted(glob(search_str))
        return files_colsens

    def get_files_prior(self):
        """Return filelist with all prior (VMR_fast_out.dat) files."""
        search_str = os.path.join(
            self.path_raw_output_proffast,
            "*VMR_fast_out.dat"
        )
        files_prior = sorted(glob(search_str))
        return files_prior

    def get_comb_invparms(self):
        path = os.path.join(self.path_results, "comb_invparms*.csv")
        files = glob(path)
        if len(files) != 1:
            self.logger.error("The invparms file could not be determined.")
            raise RuntimeError("The invparms file could not be determined.")
        df = pd.read_csv(
            files[0],
            skipinitialspace=True,
            delimiter=",",
            parse_dates=["UTC", "LocalTime"])
        df = df.set_index("UTC")
        return df

    def get_prior(self, path):
        """Return df with prior values maped on the internal altitude grid.

        The values are converto to SI units.

        The VMR file has no header. It contains:
        0: "Index", 1: "Altitude", 2: "H2O", 3: "HDO", 4: "CO2", 5: "CH4",
        6: "N2O", 7: "CO", 8: "O2", 9: "HF"
        """

        names = [
            'Index',
            'Altitude',
            'H2O',
            'HDO',
            'CO2',
            'CH4',
            'N2O',
            'CO',
            'O2',
            'HF']
        df = pd.read_csv(
            path,
            header=None,
            skipinitialspace=True,
            usecols=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
            names=names,
            sep=' ',
            engine='python')

        # convert to SI units
        prior_scaling_values = {
            "H2O": 1,  # parts
            "CO2": 1e-6,  # ppm
            "CH4": 1e-9,  # ppb
            "CO": 1e-9,  # ppb
            # todo extend!
        }
        for key, scaling in prior_scaling_values.items():
            df[key] *= scaling

        return df

    def get_colsens_for(self, path, species):
        """Return the column sensitivities for a given species."""

        header = [
            'alt',
            'p',
            *self.sza
            ]

        header_values_for_dfs = {
            "H2O": 3,
            "HDO": 56,
            "CO2": 109,
            "CH4": 162,
            "N2O": 215,
            "CO": 268,
            "O2": 321,
        }

        df = pd.read_csv(
            path, sep="\s+",
            skip_blank_lines=True,
            header=header_values_for_dfs[species],
            names=header,
            nrows=49)
        return df

    def get_prior_time(self):
        """Return cf times."""
        files_colsens = self.get_files_colsens()

        time_prior = []
        for file in files_colsens:
            filename = os.path.basename(file)
            local_date = dt.datetime.strptime(
                filename[-18:-12], "%y%m%d").date()
            local_date_utc = self.time_handler.get_local_noon_utc(local_date)
            time_prior.append(local_date_utc)

        time_prior_cf = cftime.date2num(
            time_prior, units=self.cftime_unit, calendar=self.cftime_calendar)
        return time_prior_cf

    def get_avk_dims(self):
        """Return dict with dims for averaging kernels."""
        avk_dims = self.get_prior_dims()
        sza_avk = np.array(self.sza)
        avk_dims["sza_avk"] = sza_avk

        return avk_dims

    def add_avk(self, ds):
        """Add averaging kernel variables to dataset."""
        files_colsens = self.get_files_colsens()
        list_species = ["H2O", "HDO", "CO2", "CH4", "N2O", "CO", "O2"]
        for species in list_species:
            list_colsens = []
            for file in files_colsens:
                df_colsens = self.get_colsens_for(file, species)
                del df_colsens["alt"]
                del df_colsens["p"]
                colsens_array = df_colsens.to_numpy()
                list_colsens.append(colsens_array)

            avk_dims = self.get_avk_dims()
            ds[species+"_avk"] = xr.DataArray(
                np.array(list_colsens),
                dims=avk_dims)
        return ds

    def get_prior_dims(self):
        """Return dict with dims for prior variables."""
        time_prior_cf = self.get_prior_time()

        path = self.get_files_colsens()[0]
        df = self.get_colsens_for(path, "H2O")
        alt_prior = df["alt"].values

        prior_dims = {
            "time_prior": time_prior_cf,
            "alt_prior": alt_prior,
        }
        return prior_dims

    def add_prior(self, ds):
        """Add prior variables to dataset."""
        files_prior = self.get_files_prior()
        dict_priors = {
            k: [] for k
            in ['H2O', 'HDO', 'CO2', 'CH4', 'N2O', 'CO', 'O2', 'HF']
        }
        for file in files_prior:
            df_prior = self.get_prior(file)
            for key in dict_priors.keys():
                prior_array = df_prior[key].to_numpy()
                dict_priors[key].append(prior_array)

        prior_dims = self.get_prior_dims()
        for key, prior_array in dict_priors.items():
            ds[key+"_prior"] = xr.DataArray(
                prior_array, dims=prior_dims)

        return ds

    def rename_variables(self, ds):
        name_dict = {
            "latdeg": "lat",
            "londeg": "lon",
            'gndP': "p",
            'gndT': "t",
            'altim': "height",
            'appSZA': "sza",
        }
        ds.rename(name_dict)
        return ds

    def add_global_attrs(self, ds):
        prfpylot_path = os.path.dirname(inspect.getsourcefile(prfpylot))
        path_global_atts = os.path.join(
            prfpylot_path, "nc_cf", "global_attrs.yml")
        with open(path_global_atts, "r") as f:
            global_attrs = yaml.safe_load(f)
        ds.attrs = global_attrs
        return ds

    def add_variable_attrs(self, ds):
        prfpylot_path = os.path.dirname(inspect.getsourcefile(prfpylot))
        path_var_atts = os.path.join(
            prfpylot_path, "nc_cf", "variable_attrs.yml")
        with open(path_var_atts, "r") as f:
            var_attrs = yaml.safe_load(f)

        for key, var_attr in var_attrs.items():
            if key in ds:
                ds[key].attrs = var_attr
        return ds
