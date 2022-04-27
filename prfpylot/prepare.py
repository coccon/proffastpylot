"""Prepare is a module of PROFFASTpylot.

Initialasation, handling of all parameters, generation of the
PROFFAST input files.

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

import prfpylot
from prfpylot.pressure import PressureHandler
import os
import sys
import yaml
from datetime import datetime as dt
from datetime import timedelta
import pandas as pd
from glob import glob
import logging
from timezonefinder import TimezoneFinder
import pytz
import fortranformat
import inspect


class Preparation():
    """Import input parameters, and create input files."""

    template_types = {
        "prep": "preprocess4",
        "tccon": "tccon",
        "inv": "invers20",
        "pcxs": "pcxs20"
    }

    global_inputfile_list = []

    # in 'pylot.run_pcxs_at' it is tested if ggg2014 or ggg2020 map files are
    # used
    ggg2020mapfiles = False

    def __init__(self, input_file, pressure_type_file, logginglevel="info"):
        # read input file
        with open(input_file, "r") as f:
            args = yaml.load(f, Loader=yaml.FullLoader)
        self.input_file = input_file

        # now, the logfile can be created:
        self.logger = self.get_logger(logginglevel=logginglevel)
        self.logger.info(
            "++++ Welcome to PROFFASTpylot ++++\n")
        self.logger.debug("Start reading input file...")

        # set parameters from input file
        self.instrument_number = args["instrument_number"]
        self.site_name = args["site_name"]
        self.site_abbrev = args["site_abbrev"]
        self.note = args["note"]

        # inspect.getsourcefile needes __init__.py!
        self.prfpylot_path = os.path.dirname(inspect.getsourcefile(prfpylot))
        # path to the PROFFAST executables
        self.proffast_path = args["proffast_path"]
        if self.proffast_path is None:
            head, _ = os.path.split(self.prfpylot_path)
            self.proffast_path = os.path.join(head, "prf")
        if not os.path.exists(self.proffast_path):
            self.logger.critical(
                    "PROFFAST does not exist! Make sure to download PROFFAST "
                    "before running PROFFASTpylot. Either copy it to "
                    "proffastpylot/prf or specify the path "
                    "where it is located.")
            sys.exit()

        # coordinates
        if None not in args["coords"].values():
            self.coords = args["coords"]
            self.coord_file = None  # to avoid overriding given coords
            self.use_coordfile = False
        else:
            if args["coord_file"] is not None:
                self.coords = {}
                self.coord_file = args["coord_file"]
                self.use_coordfile = True
                # self.coords = {}
            else:
                self.logger.error("coord_file is not specified!")
                sys.exit()

        # utc time shift of the recorded data
        if args["utc_offset"] is None:
            self.utc_offset = 0.0
        else:
            self.utc_offset = args["utc_offset"]

        # additional paths
        self.map_path = args["map_path"]
        if self.map_path is None:
            self.logger.error("map_path is not specified!")
            sys.exit()

        self.pressure_path = args["pressure_path"]
        if self.pressure_path is None:
            self.logger.error("pressure_path is not specified!")
            sys.exit()

        # self.pressure_type = args["pressure_type"]
        # if self.pressure_type != "original":
        #     # Read in Params from pressure file:
        #     with open(self.pressure_type, "r") as f:
        #         self.pressure_args = yaml.load(f, Loader=yaml.FullLoader)

        # ILS-File is hardcoded since it will be released with prfpylot
        self.ils_file = os.path.join(self.prfpylot_path, 'ILSList.csv')

        # igram path:
        self.igram_path = args["interferogram_path"]
        if self.igram_path is None:
            self.logger.error("interferogram_path is not specified!")
            sys.exit()

        # spectra path, i.e. output of preprocess:
        self.analysis_path = args["analysis_path"]
        if self.analysis_path is None:
            self.logger.error("analysis_path is not specified!")
            sys.exit()
        self.analysis_instrument_path = os.path.join(
                    self.analysis_path,
                    f"{self.site_name}_{self.instrument_number}")

        # record some notes about the behaviour of the pylot:

        if args["start_with_spectra"] is not None:
            self.start_with_spectra = args["start_with_spectra"]
        else:
            self.logger.error("start_with_spectra not specified!")
            sys.exit()

        if args["delete_abscosbin_files"] is not None:
            self.delete_abscosbin = args["delete_abscosbin_files"]
        else:
            self.logger.error("delete_abscosbin_files not specified!")
            sys.exit()

        if args["delete_input_files"] is not None:
            self.bool_delete_input_files = args["delete_input_files"]
        else:
            self.bool_delete_input_files = False

        # file size limit of igrams:
        if args["igram_size_filter"] is not None:
            self.igram_filter_size = args["igram_size_filter"]
        else:
            self.logger.error("igram_size_filter is not given!")
            sys.exit()

        # check if tccon mode is activated. Raise warning if it is activated
        if args["tccon_mode"]:
            self.tccon_mode = True
            self.tccon_setting = args["tccon_setting"]
            self._tccon_mode_warning()
        else:
            self.tccon_mode = False
            self.tccon_setting = args["tccon_setting"]

        # list of dates
        self.dates = self.get_dates(
                start_date=args["start_date"],
                end_date=args["end_date"]
            )

        # only the base where the result folder is to be safed
        # is given. The final folder is created every runtime.
        self.result_path = args["result_path"]
        if self.result_path is None:
            self.logger.error("result_path is not specified!")
            sys.exit()
        dtfs = "%Y%m%d"  # dtformatstring
        result_foldername = "{}_{}_{}_{}".format(self.site_name,
                                                 self.instrument_number,
                                                 self.dates[0].strftime(dtfs),
                                                 self.dates[-1].strftime(dtfs))
        self.result_folder = os.path.join(self.result_path, result_foldername)

        # log of the processes
        self.logfile_path = os.path.join(
            self.result_folder, "logfiles")

        # calculate the _localtime_offset
        self._localtime_offset = self._get_localtime_offset()

        # initialise pressure handler
        self.pressure_handler = PressureHandler(
            pressure_type_file, self.pressure_path, self.dates, self.logger)

        self.logger.debug("... read in finished!")

    def get_logger(self, logginglevel="info"):
        """Create and return a logger."""
        logger = logging.getLogger('prfpylot')
        # set logging to debug to record everything in the first place
        logger.setLevel(logging.DEBUG)
        StreamHandler = logging.StreamHandler()
        cwd = os.getcwd()
        self.generalLogfile = os.path.join(cwd, "GeneralLogfile.log")
        logfile = os.path.join("GeneralLogfile.log")
        FHandler = logging.FileHandler(logfile, mode='w')

        if logginglevel == "debug":
            StreamHandler.setLevel(logging.DEBUG)
            FHandler.setLevel(logging.DEBUG)
        elif logginglevel == "info":
            StreamHandler.setLevel(logging.INFO)
            FHandler.setLevel(logging.INFO)
        elif logginglevel == "warning":
            StreamHandler.setLevel(logging.WARNING)
            FHandler.setLevel(logging.WARNING)

        logger.addHandler(StreamHandler)
        logger.addHandler(FHandler)
        StreamFormat = logging.Formatter(
            '{asctime}, {levelname}: {message}',
            style='{')
        StreamHandler.setFormatter(StreamFormat)
        FHandler.setFormatter(StreamFormat)
        return logger

    def get_dates(self, start_date=None, end_date=None):
        """Return a list of dates for the given site, instrument.
        Truncate the list if start_date and end_date are given.

        Params:
            start_date (dt.date): optional start date
            end_date (dt.date): optional end date
        """
        if not self.start_with_spectra:
            self.logger.debug(
                "Searching for all interferogram folders ...")
            datapath = os.path.join(self.igram_path, "*")
        else:
            self.logger.debug(
                "Searching for all spectra folders ...")
            datapath = os.path.join(self.analysis_instrument_path, "*")

        dates = self._create_datelist(datapath)
        if len(dates) == 0:
            self.logger.critical(
                f"No interferograms were found at {self.igram_path}!")
            sys.exit()

        date_str_list = [date.strftime("%y-%m-%d") for date in dates]
        self.logger.info(
            f"The following dates were found at {self.igram_path}: "
            f"{', '.join(date_str_list)}")

        if start_date is not None:
            i = self._get_start_date_pos(start_date, dates)
            dates = dates[i:]
        if end_date is not None:
            i = self._get_end_date_pos(end_date, dates)
            dates = dates[:i]

        return dates

    def _create_datelist(self, path):
        """Create datelist of given path.
        Skip elements that are not folders of the format "YYMMDD".
        """
        date_paths = glob(path)

        dates = []
        for date_path in date_paths:
            date_str = os.path.split(date_path)[1]

            if not os.path.isdir(date_path):
                self.logger.debug(
                    f"Skipping invalid element in datelist: {date_str}. "
                    "No Directory!")
                continue
            try:
                date = dt.strptime(date_str, "%y%m%d")
            except ValueError:
                self.logger.debug(
                    f"Skipping invalid element in datelist: {date_str}. "
                    "Could not parse date!")
                continue

            dates.append(date)

        dates.sort()
        return dates

    def get_template_path(self, template_type):
        """Return path to the corresponding template file."""
        folder_path = os.path.join(self.prfpylot_path, "templates")
        filename = "template_{}.inp".format(self.template_types[template_type])
        template_path = os.path.join(folder_path, filename)
        return template_path

    def get_prf_input_path(self, template_type, date=None):
        """Return path to the corresponding prf_input_file."""
        if template_type in ["pcxs", "inv"]:
            folder_path = os.path.join(self.proffast_path, "inp_fast")
            date_str = dt.strftime(date, "%y%m%d")
            filename = "".join(
                [self.template_types[template_type],
                    f"{self.site_name}_{date_str}.inp"]
            )
        elif template_type == "prep":
            folder_path = os.path.join(self.proffast_path, "preprocess")
            date_str = dt.strftime(date, "%y%m%d")
            filename = "".join(
                [self.template_types[template_type],
                    f"{self.site_name}_{date_str}",
                    ".inp"]
                )
        elif template_type == "tccon":
            folder_path = os.path.join(self.proffast_path, "preprocess")
            filename = "".join([self.template_types[template_type], ".inp"])

        prf_input_path = os.path.join(folder_path, filename)
        return prf_input_path

    def get_map_file(self, date):
        """Return path to mapfile of given date.

        params:
            date: datetime object
        """
        search_string = os.path.join(
            self.map_path,
            "*{date}.map".format(date=date.strftime("%y%m%d")))
        map_file = glob(search_string)

        assert len(map_file) == 1
        map_file = map_file[0]

        return map_file

    def generate_prf_input(self, template_type, date=None):
        """Generate a template file.

        Calling the corresponding collect parameters function
        and replace template function.

        params:
            template_type (str): Can be "prep", "tccon", "pt", "inv" or "pcxc"
        """
        # the name of the input file to be generated
        prf_input_file = self.get_prf_input_path(template_type, date)

        if date is not None:
            date_str = dt.strftime(date, "%y%m%d")

        foundData = True
        if template_type == "prep":
            self.logger.debug(
                f"Generating preprocess inp file for {date_str}..")
            parameters = self.get_prep_parameters(date)
            if parameters["igrams"] == "":
                foundData = False

        elif template_type == "tccon":
            parameters = {"tccon_setting": self.tccon_setting}

        elif template_type == "pcxs":
            parameters = self.get_pcxs_parameters(date)
            self.logger.debug(
                f"Generating {self.template_types[template_type]}"
                f" inp file for {date_str}..")

        elif template_type == "inv":
            self.logger.debug(
                f"Generating {self.template_types[template_type]}"
                f" inp file for {date_str}..")
            parameters = self.get_inv_parameters(date)
            prf_input_files = []
            for i, parameter_i in enumerate(parameters):
                # TODO: check if this is neccessary 
                # if parameter_i["SPECTRA_PT_INPUT"] == "":
                #     foundData = False
                prf_input_files.append(prf_input_file[:-4] + f"_{i}.inp")
                self.replace_params_in_template(
                    parameter_i, template_type, prf_input_files[-1])
            # safe inputfiles in global list to move/delete them later
            self.global_inputfile_list.extend(prf_input_files)
            # return several input files hence to it already here:
            return prf_input_files
        else:
            raise ValueError(f"Unknown template_type {template_type}")

        self.replace_params_in_template(
            parameters, template_type, prf_input_file)
        if foundData:
            self.global_inputfile_list.append(prf_input_file)
            return prf_input_file
        else:
            return None

    def get_igrams(self, date):
        """Search for interferograms disk and return a list of files."""
        date_str = date.strftime("%y%m%d")
        igrams = glob(os.path.join(self.igram_path, date_str, "*.*"))
        # check for filesize: if smaller than a certain limit the file is
        # must be corrupt
        temp_list = igrams[:]
        for igram in temp_list:
            filesize = os.path.getsize(igram) / (1024 * 1024)  # in MB
            self.logger.debug(f"Check filesize of igram {igram}...")
            # print(f"Filesize of {igram} is : {filesize}")
            if filesize < self.igram_filter_size:
                igrams.remove(igram)
                self.logger.warning(
                    f"Interferogram {igram} has size "
                    f"{filesize} < {self.igram_filter_size} MB. Skip it!")
            else:
                self.logger.debug("... all good!")
        if igrams == []:
            self.logger.debug(f"No suitable Interferogram at day {date_str} "
                              "found in get_igrams().")
        return igrams

    def get_localdate_spectra(self):
        """Return dict linking all spectra to local dates.
        returns:
            {local_date: ["YYMMDD_HHMMSSSN.BIN", ...]}
        """
        all_spectra = []
        for date in self.dates:
            searchpath = os.path.join(
                self.analysis_instrument_path,
                date.strftime("%y%m%d"),
                "cal",
                "*SN.BIN")
            all_spectra.extend(glob(searchpath))
        all_spectra.sort()
        localdate_spectra = {}
        for spectrum in all_spectra:
            spectrum = os.path.basename(spectrum)
            utc_time = dt.strptime(spectrum, "%y%m%d_%H%M%SSN.BIN")
            local_time = utc_time + timedelta(hours=self._localtime_offset)
            local_date = local_time.date()
            if local_date in localdate_spectra.keys():
                localdate_spectra[local_date].append(spectrum)
            else:
                localdate_spectra[local_date] = [spectrum]
        return localdate_spectra

    def replace_params_in_template(
            self, parameters, template_type, prf_input_file):
        """Generate a site specific input file by using a template.
        params:
            parameters(dict): containing keys which match the variable
                              names in the template file. They are replaced by
                              the entries.

            template_type(str): Can be "prep", "pt", "inv" or "pcxc"
            prf_input_file(str): the filename of the input file
        """
        templ_file = self.get_template_path(template_type)
        templ_stream = open(templ_file, 'r')
        prf_input_stream = open(prf_input_file, 'w')
        for line in templ_stream:
            new_line = line
            for key, parameter in parameters.items():
                new_line = new_line.replace(
                    '%{}%'.format(key), str(parameter))
                new_line = self._replace_backslash(new_line)

            prf_input_stream.write(new_line)
        templ_stream.close()
        prf_input_stream.close()
        if template_type == "tccon":
            self.tccon_file = prf_input_file

    def get_prep_parameters(self, date):
        '''
        Return Parameters to be replaced in the pereprocess input file.
        '''

        # get ILS for Channel 1 and 2 for a specific date
        ME1, PE1, ME2, PE2 = self.get_ils_from_file(date)
        # if coordfile is used, check for the correct coords for each day.
        # otherwise use the same for all days
        if self.use_coordfile:
            self.get_coords_from_file(date)
        lat = self.coords.get("lat", -1.)
        lon = self.coords.get("lon", -1.)
        alt = self.coords.get("alt", -1.)

        if lat == -1. or lon == -1. or alt == -1.:
            self.logger.critical("Could not determine coodinates. Exit!")
            sys.exit()

        comment = (
            "This spectrum is generated using preprocess4, a part of "
            "PROFFAST controlled by PROFFASTpylot.")
        if self.note is not None:
            comment = " ".join([comment, self.note])
        # get all good igrams. If no good igrams is found the day is put in
        # the badDayQueue
        igrams = self.get_igrams(date)
        igrams = "\n".join(igrams)
        # generate path to outputfolder for this date:
        datestring = date.strftime("%y%m%d")
        # NOTE: the 'cal' is necessary since "invers" automatically adds
        #       a "cal" string to the spectra path.
        outfolder = os.path.join(
            self.analysis_instrument_path, datestring, "cal")

        logfile = f"Internal_preprocess_log_{datestring}.log"

        parameters = {
            'ILS_Channel1': f"{ME1} {PE1}",
            'ILS_Channel2': f"{ME2} {PE2}",
            'site_name': self.site_name,
            'lat': lat,
            'lon': lon,
            'alt': alt,
            'utc_offset': str(self.utc_offset),
            'comment': comment,
            'igrams': igrams,
            'path_preprocess_log': self.logfile_path,
            'filename_logfile': logfile,
            'path_spectra': outfolder
                     }
        return parameters

    def get_pcxs_parameters(self, date):
        """Return parameters to replace in the pcxs20.inp file."""

        self.logger.debug("Create inv input parameters ...")
        # coordinates of the corresponding date
        if self.use_coordfile:
            self.get_coords_from_file(date)

        lat = self.coords.get("lat", -1.)
        lon = self.coords.get("lon", -1.)
        alt = self.coords.get("alt", -1.)
        if lat == -1. or lon == -1. or alt == -1.:
            self.logger.critical("Could not determine coodinates. Exit!")
            sys.exit()

        parameters = {
            "ALT": alt,
            "LAT": lat,
            "LON": lon,
            "DATAPATH": self.analysis_instrument_path,
            "DATE": date.strftime("%y%m%d"),
            "SITE": self.site_name,
            "MAPPATH": self.map_path,
            "SITE_ABBREV": self.site_abbrev,
            "DATE_LONG": date.strftime("%Y%m%d"),
        }
        # in case of pcxs20 the parameter %WET_VMR% is needed in addition:
        if self.ggg2020mapfiles:
            # in case of GGG2014 map files it is dry air (False)
            # in case of GGG2020 map files it is wet air. (True)
            parameters["WET_VMR"] = True
        else:
            parameters["WET_VMR"] = False
        return parameters

    def get_inv_parameters(self, date):
        """Return Parameters to replace in the invers10.inp file.
        Returns:
            parameters(list): contains one or two dict depending on measurement
                              time. See get_spectra_pT_input docstring.
        """
        spectra_pT_input = self.get_spectra_pT_input(date)
        parameters = []
        for sub_pT_input in spectra_pT_input:
            measurement_date = sub_pT_input[0][0:6]
            temp_parameters = {
                "DATAPATH": self.analysis_instrument_path,
                "MEASUREMENT_DATE": measurement_date,
                "LOCAL_DATE": date.strftime("%y%m%d"),
                "SITE": self.site_name,
                "SPECTRA_PT_INPUT": "\n".join(sub_pT_input)
            }
            parameters.append(temp_parameters)
        return parameters

    def get_spectra_pT_input(self, date):
        """Return a list of list of strings containing spectra and pT infos.
        If two UTC-Dates are found inside of one local day, spectra_pT_input
        contains two lists.

        YYMMDD_HHMMSSSN.BIN, pressure, T_PBL

        This function replaces the pt_intraday.inp file!
        Note that T_PBL is currently set to 0.0.

        params:
            (date): dt.Datetime, measurement time in local time or UTC time
        """
        spectra_list = self.localdate_spectra[date]
        spectra_list.sort()

        # in case of two UTC days in a local day list, split them up:
        spectra1 = []
        spectra2 = []
        first_date = dt.strptime(spectra_list[0][:6], "%y%m%d")
        spectra1.append(spectra_list[0])
        for spectrum in spectra_list[1:]:
            current_date = dt.strptime(spectrum[:6], "%y%m%d")
            if current_date != first_date:
                spectra2.append(spectrum)
            else:
                spectra1.append(spectrum)
        if len(spectra2) == 0:
            assert spectra_list == spectra1
            spectra_list = [spectra1]
        else:
            spectra_list = [spectra1, spectra2]

        spectra_pT_input = []
        for sublist in spectra_list:
            temp_pT_input = []
            for s in sublist:
                # get timestamp of spectrum, can be UTC or local time depending on
                # self.utc_offset
                timestamp = dt.strptime(s, "%y%m%d_%H%M%SSN.BIN")
                # apply a possible offset of the pressure data and the igram data:
                time_offset_p_igram = \
                    self.pressure_handler.utc_offset - self.utc_offset
                timestamp += timedelta(hours=time_offset_p_igram)
                # get pressure from mapfile
                p = self.pressure_handler.get_pressure_at(timestamp)

                temp_pT_input.append(f"{s}, {p}, 0.0")
            spectra_pT_input.append(temp_pT_input)

        return spectra_pT_input

    def get_ils_from_file(self, date):
        """
        This methods reads the ILS from the Instrument_list.
        If return_string=True, it returns a string which is already
        preformatted such that it can be inserted into the template file
        directly.
        """
        if self.tccon_mode:
            return (0.983, 0., 0.983, 0.)

        ils_df = pd.read_csv(self.ils_file, skipinitialspace=True)
        ils_df["ValidSince"] = pd.to_datetime(ils_df["ValidSince"])
        ils_df = ils_df.set_index("Instrument")

        try:
            ils_df = ils_df.loc[self.instrument_number]
        except KeyError:
            self.logger.critical(
                f"{self.instrument_number} is not in ILS-file.\n"
                "Please ensure you are using the newest version of "
                "PROFFASTpylot.\n"
                )
            sys.exit()
        if isinstance(ils_df, pd.Series):
            # this is the case, if only one entry per instrument is available
            MEChan1 = ils_df['Channel1ME']
            PEChan1 = ils_df['Channel1PE']
            MEChan2 = ils_df['Channel2ME']
            PEChan2 = ils_df['Channel2PE']
        elif isinstance(ils_df, pd.DataFrame):
            ils_df = ils_df.loc[ils_df["ValidSince"] <= date]
            row = ils_df.sort_values(by=["ValidSince"])
            MEChan1 = row["Channel1ME"].iloc[-1]
            MEChan2 = row["Channel2ME"].iloc[-1]
            PEChan1 = row["Channel1PE"].iloc[-1]
            PEChan2 = row["Channel2PE"].iloc[-1]
        else:
            self.logger.critical(
                "An unknown error occured while reading the "
                "ILS-list.")
            sys.exit()

        return (MEChan1, PEChan1, MEChan2, PEChan2)

    def get_coords_from_file(self, date):
        '''Return the coordinates from the coord file.'''
        coord_df = pd.read_csv(self.coord_file, skipinitialspace=True)
        coord_df["Starttime"] = pd.to_datetime(coord_df["Starttime"])
        coord_df = coord_df.set_index('Site')
        try:
            coord_df = coord_df.loc[self.site_name]
        except KeyError:
            self.logger.critical(f"{self.site_name} is not in coord.csv!")
            sys.exit()
        if isinstance(coord_df, pd.Series):
            # this is the case, if only one entry per site is available
            self.coords["lon"] = coord_df["Longitude"]
            self.coords["lat"] = coord_df["Latitude"]
            self.coords["alt"] = coord_df["Altitude_kmasl"]
        elif isinstance(coord_df, pd.DataFrame):
            coord_df = coord_df.loc[coord_df["Starttime"] <= date]
            row = coord_df.sort_values(by=["Starttime"])
            self.coords["lon"] = row["Longitude"].iloc[-1]
            self.coords["lat"] = row["Latitude"].iloc[-1]
            self.coords["alt"] = row["Altitude_kmasl"].iloc[-1]

    def _get_start_date_pos(self, start_date, dates):
        """Return position of the start date in dates."""
        self.logger.debug("Locating the first date in the given interval.")
        start_date = dt.combine(start_date, dt.min.time())

        if start_date > dates[-1]:
            self.logger.error(
                "The start date is later than the date of the last "
                "interferogram on disk. Terminating program.")
            quit()
        else:
            for i, date in enumerate(dates):
                if date >= start_date:
                    return i

    def _get_end_date_pos(self, end_date, dates):
        """Return position of the end date in dates."""
        self.logger.debug("Locating the last date in the given interval.")
        end_date = dt.combine(end_date, dt.min.time())

        if end_date < dates[0]:
            self.logger.error(
                "The end date is earlier than the date of the first "
                "interferogram on disk. Terminating program.")
            quit()
        else:
            for i, date in enumerate(dates):
                if date == end_date:
                    return i+1
                if date > end_date:
                    return i

    def _find_closest(self, when, date, datelist):
        """Find the closest entry in a date list.
        Before or after a given date.

        Params:
            when (str): 'before' or 'after'
            date: date to slice the list
            datelist (list): list of all dates
        """
        self.logger.debug(
            "Finding the closest date in datelist "
            f"{when} {date.strftime('%y-%m-%d')}")

        if when == "after":  # in case of finding the start date
            assert date <= datelist[-1]
            if datelist[0] >= date:
                return 0
        if when == "before":  # in case of finding the end date
            assert date >= datelist[0]
            if datelist[-1] <= date:
                return len(datelist)

        for i, date_i in enumerate(datelist):
            if date_i == date:
                return i
            if date_i > date:
                assert datelist[i-1] < date
                if when == "before":
                    return i-1
                if when == "after":
                    return i

    def _replace_backslash(self, line):
        """Replace backslash with slash if run on linux."""
        if sys.platform == "linux":
            return line.replace("\\", "/")
        return line

    def prepare_map_file(self, date):
        """Generate map file if GGG2020 map file"""
        # search for GGG2020 map files:
        srchstrg = f"{self.site_abbrev}_*_*Z.map"
        mapfiles = glob(os.path.join(self.map_path, srchstrg))
        if len(mapfiles) != 0:
            self.logger.debug("Detected GGG2020 map files!")
            # GGG2020map files found!
            self.ggg2020mapfiles = True
            self._interpolate_map_files(date)
        else:
            srchstrg = f"{self.site_abbrev}{date.strftime('%Y%m%d')}.map"
            mapfiles = glob(os.path.join(self.map_path, srchstrg))
            if len(mapfiles) == 1:
                self.logger.debug("Detected GGG2014 map file!")
                self.ggg2020mapfiles = False
            else:
                self.logger.critical(
                    "No suitable map file found at "
                    f"{self.map_path} for {date.strftime('%Y-%m-%d')}.")
                sys.exit()

    def _interpolate_map_files(self, date):
        """
        interpolates the new map files to genereate a map
        file at 12:00 local time
        """
        # TODO: delete this part and replace with _localtime ?
        # First find out, at which timezone the current files are recorded:
        if self.use_coordfile:
            self.get_coords_from_file(self.dates[0])
        tf = TimezoneFinder()
        # get timezone as a string:
        local_tz_name = tf.timezone_at(
            lat=self.coords["lat"],
            lng=self.coords["lon"])
        # convert string to pytz object:
        local_tz = pytz.timezone(local_tz_name)
        utc_tz = pytz.utc
        # create a timestamp of local noon:
        noon_local = date.replace(hour=12, minute=0, second=0)

        # convert this to a localized timestamp using localize of pytz.
        # this is neccesary since there is a bug in using the tzinfo of the
        # datetime module:
        tz_diff = utc_tz.localize(noon_local).astimezone(local_tz) \
            - local_tz.localize(noon_local)
        noon_utc = noon_local - tz_diff

        # next get a list of all *.map files of the needed date:
        # TODO: Here we could check fo the correct lat and long as well!
        srchstrg = f"{self.site_abbrev}_*_"\
                   + f"{noon_utc.strftime('%Y%m%d')}*Z.map"
        mapfiles = glob(os.path.join(self.map_path, srchstrg))
        # find the right map files: bevore and after the hour of noon_utc:
        ind = 0
        noon_hour = noon_utc.hour
        for i, file in enumerate(mapfiles):
            hour_file = int(file[-7:-5])
            if hour_file > noon_hour:
                ind = i
                break
        file1 = pd.read_csv(mapfiles[ind-1],
                            skipinitialspace=True, header=11)
        file1 = file1.to_numpy().transpose()
        file2 = pd.read_csv(mapfiles[ind],
                            skipinitialspace=True, header=11)
        file2 = file2.to_numpy().transpose()
        # interpolate between the files:
        # since the difference between two file is allways 3 hours this can be
        # hardcoded:
        tdiff = 3 * 60 * 60   # seconds
        # furthermore we need the date of file 1 for the requested time diff.
        date_file1 = dt.strptime(
                    (os.path.basename(mapfiles[ind-1])[12:22]), "%Y%m%d%H"
                                )
        for i in range(file1.shape[0]):
            # do a linear interpolation, calculate everything in seconds:
            file1[i, :] = file1[i, :] + (file2[i, :] - file1[i, :]) / tdiff \
                * (noon_utc - date_file1).total_seconds()

        current_mapfile = \
            f"{self.site_abbrev}{date.strftime('%Y%m%d')}.map"
        current_mapfile = os.path.join(self.map_path, current_mapfile)

        # Now after interpolation is done, read in Header:
        with open(mapfiles[0], "r") as f:
            header = f.readlines()[:12]
        # write header
        with open(current_mapfile, "w") as f:
            for line in header:
                f.write(line)
        # write the rest of the file
        with open(current_mapfile, "a") as f:
            frw = fortranformat.FortranRecordWriter(
                "(2(f8.3,','),4(e10.3,','),1x,(f7.3,','),1x,(f7.3,','),"
                "(e10.3,','),1x,(f6.1,','),(f8.3,','),1x,(f6.4,','),1x,"
                "f5.3)")
            file1 = file1.transpose()
            for line in file1:
                f.write(frw.write(line) + "\n")

    def _tccon_mode_warning(self):
        """ Print warning if TCCON mode is activated """
        self.logger.warning(
            "TCCON Mode is activated!\nThis will not work with standard"
            " EM27/SUN interferograms.\nOnly continue if this setting"
            " was choosen by purpose. Otherwise break the execution!")
    
    def _get_localtime_offset(self):
        """Return offset between measurement time.
        utc_offset + localtime_offset = total offset beteen Localtime and UTC.
        """
        if self.use_coordfile:
            self.get_coords_from_file(self.dates[0])
        tf = TimezoneFinder()
        local_tz_name = tf.timezone_at(
            lat=self.coords["lat"],
            lng=self.coords["lon"])
        local_tz = pytz.timezone(local_tz_name)
        # Allways use winter time
        date_winter = dt.strptime("2000-01-01", "%Y-%m-%d")
        local_timedelta = local_tz.utcoffset(date_winter)
        _local_time_offset = int(local_timedelta.total_seconds() / 3600)
        return _local_time_offset


