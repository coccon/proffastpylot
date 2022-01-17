import prfpylot
import os
import sys
import yaml
from datetime import datetime as dt
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
        "inv": "invers20",
        "pcxs": "pcxs20"
    }

    # in 'pylot.run_pcxs_at' it is tested if ggg2014 or ggg2020 map files are
    # used
    ggg2020mapfiles = False

    def __init__(self, input_path="input.yml", logginglevel="info"):
        # read input file
        with open(input_path, "r") as f:
            args = yaml.load(f, Loader=yaml.FullLoader)

        # now, the logfile can be created:
        self.logger = self.get_logger(logginglevel=logginglevel)
        self.logger.info("++++ Welcome to Proffast powered by PrfPylot ++++")
        self.logger.info("Start reading input file...")

        # set parameters from input file
        self.instrument_number = args["instrument_number"]
        self.site_name = args["site_name"]
        self.site_abbrev = args["site_abbrev"]
        self.note = args["note"]
   
        # TODO: This is a temporary solution! Think about if this is needed
        #       for future versions.
        # inspect.getsourcefile needes __init__.py!
        self.prfpylot_path = os.path.dirname(inspect.getsourcefile(prfpylot))
        # path to the PROFFAST executables
        self.proffast_path = args["proffast_path"]
        if self.proffast_path is None:
            head, _ = os.path.split(self.prfpylot_path)
            self.proffast_path = os.path.join(head, "prf")
            if not os.path.exists(self.proffast_path):
                self.logger.critical(
                    "Could not automatically find the proffast path. Please "
                    "specify it in the input file!")
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
            self.utc_offset = args["utc_gap"]

        # additional paths
        self.map_path = args["map_path"]
        if self.map_path is None:
            self.logger.error("map_path is not specified!")
            sys.exit()

        # TODO: Change to pressure_path
        self.pressure_path = args["pressure_path"]
        if self.pressure_path is None:
            self.logger.error("pressure_path is not specified!")
            sys.exit()

        self.pressure_type = args["pressure_type"]

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

        # record some notes about the behaviour of the pylot:

        if args["start_with_spectra"] is not None:
            self.start_with_spectra = args["start_with_spectra"]
        else:
            self.logger.error("start_with_spectra not specified!")
            sys.exit()

        if args["delete_abscos.bin_files"] is not None:
            self.delete_abscosbin = args["delete_abscos.bin_files"]
        else:
            self.logger.error("delete_abscos.bin_files not specified!")
            sys.exit()
        
        if args["delete_input_files"] is not None:
            self.bool_delete_input_files = args["delete_input_files"]
        else:
            self.logger.error("delete_input_files not specified!")
            sys.exit()

        # list of dates
        self.dates = self.get_dates(
                start_date=args["start_date"],
                end_date=args["end_date"]
            )
        if len(self.dates) == 0:
            self.logger.critical("No igrams found! Please check the path!\n"
                                 f"Current path is {self.igram_path}")
            sys.exit()

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
        
        self.logger.info("... read in finished!")

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

    def get_dates(self, start_date, end_date):
        """Return a list of dates for the given site, instrument and
        start- and end date.
        """
        if not self.start_with_spectra:
            self.logger.debug("Search for all interferogram files of the "
                              "side and device")
            date_paths = glob(os.path.join(self.igram_path, "*"))

        else:
            # in filemover.py the analysis path is extended to its final
            # version (i.e. analysis/Site_Instrumentnumer). However this is
            # NOT done here yet. Hence do this temporarily by hand:
            self.logger.debug("Search for all spectra files of the "
                              "side and device")
            date_paths = glob(os.path.join(
                self.analysis_path,
                f"{self.site_name}_{self.instrument_number}", "*"))
        dates = []

        # create a list of all dates available on the disk
        for date_path in date_paths:
            date = os.path.split(date_path)[1]
            # TODO: Catch for invalid folder names (i.e. not YYMMDD)
            date = dt.strptime(date, "%y%m%d")
            dates.append(date)
            dates.sort()
        # if start and/or end date is given truncate the list
        if start_date is not None:
            i = self._get_start_date_pos(start_date, dates)
            dates = dates[i:]
        if end_date is not None:
            i = self._get_end_date_pos(end_date, dates)
            dates = dates[:i]
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
        if template_type == "prep":
            folder_path = os.path.join(self.proffast_path, "preprocess")
            date_str = dt.strftime(date, "%y%m%d")
            filename = "".join(
                [self.template_types[template_type],
                    f"{self.site_name}_{date_str}",
                    ".inp"]
                )
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

    def generate_prf_input(self, template_type, date):
        """Generate a template file.

        Calling the corresponding collect parameters function
        and replace template function.

        params:
            template_type (str): Can be "prep", "pt", "inv" or "pcxc"
        """

        date_str = dt.strftime(date, "%y%m%d")
        if template_type == "prep":
            self.logger.info(
                f"Generating preprocess inp file for {date_str}..")
            parameters = self.get_prep_parameters(date)
        else:
            self.logger.info(f"Generating {self.template_types[template_type]}"
                             f" inp file for {date_str}..")
            parameters = self.get_pcxs_and_inv_parameters(date)

        self.replace_params_in_template(parameters, template_type, date)

    def get_igrams(self, date):
        """Search for interferograms disk and return a list of files."""
        date_str = date.strftime("%y%m%d")
        igrams = glob(os.path.join(self.igram_path, date_str, "*.*"))
        if igrams == []:
            self.logger.warning(f"Interferogram at day {date} not found.")
        return igrams

    def replace_params_in_template(self, parameters, template_type, date):
        """
        Generate a site specific input file by using a template.
        params:
            parameters(dict): containing keys which match the variable
                              names in the template file. They are replaced by
                              the entries.

            template_type(str): Can be "prep", "pt", "inv" or "pcxc"
        """
        templ_file = self.get_template_path(template_type)
        prf_input_file = self.get_prf_input_path(template_type, date)
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

    def get_prep_parameters(self, date):
        '''
        Return Parameters to be replaced in the pereprocess input file.
        '''
        # get ILS for Channel 1 and 2 for a specific date
        ME1, PE1, ME2, PE2 = self.get_ils_from_file(date)
        # if coordfile is used, check for the corred coords for each day.
        # otherwise use the same for all days
        if self.use_coordfile:
            self.get_coords_from_file(date)
        lat = self.coords.get("lat", -1.)
        lon = self.coords.get("lon", -1.)
        alt = self.coords.get("alt", -1.)

        if lat == -1. or lon == -1. or alt == -1.:
            self.logger.critical("Could not determine coodinates. Exit!")
            sys.exit()

        # TODO: Add to comment things like version of Profast, PrfPylot, ...
        comment = (
            "This spectrum is generated using preprocess4, a part of "
            "PROFAST controlled by PRFpylot.")
        if self.note is not None:
            comment = " ".join([comment, self.note])

        igrams = "\n".join(self.get_igrams(date))
        # generate path to outputfolder for this date:
        datestring = date.strftime("%y%m%d")
        # NOTE: the 'cal' is necessary since "invers" automatically adds
        #       a "cal" string to the spectra path.
        outfolder = os.path.join(self.analysis_path, datestring, "cal")
        
        # Give the logfile a name:
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

    def get_pcxs_and_inv_parameters(self, date):
        """Return Parameters to replace in the pcxs10.inp
        or invers10.inp files."""
        self.logger.info("create pcxs and inv input parameter")
        if self.use_coordfile:
            self.get_coords_from_file(date)
        lat = self.coords.get("lat", -1.)
        lon = self.coords.get("lon", -1.)
        alt = self.coords.get("alt", -1.)
        if lat == -1. or lon == -1. or alt == -1.:
            self.logger.critical("Could not determine coodinates. Exit!")
            sys.exit()

        spectra_list = self._get_spectra_list(date)
        parameters = {
            "ALT": alt,
            "LAT": lat,
            "LON": lon,
            "INSTRUMENT": self.instrument_number,
            "SITE": self.site_name,
            "DATE": date.strftime("%y%m%d"),
            "DATE_LONG": date.strftime("%Y%m%d"),
            "SITE_ABBREV": self.site_abbrev,
            "DATAPATH": self.analysis_path,
            "MAPPATH": self.map_path,
            "SPECTRA_LIST": "\n".join(spectra_list)
        }
        # in case of pcxs20 the parameter %WET_VMR% is needed in addition:

        if self.ggg2020mapfiles:
            # in case of GGG2014 map files it is dry air (False)
            # in case of GGG2020 map files it is wet air. (True)
            parameters["WET_VMR"] = True
        else:
            parameters["WET_VMR"] = False
        return parameters

    def get_ils_from_file(self, date):
        """
        This methods reads the ILS from the Instrument_list.
        If return_string=True, it returns a string which is already
        preformatted such that it can be inserted into the template file
        directly.
        """
        # TODO: when getting the ILS check for the date. 
        ils_df = pd.read_csv(self.ils_file, skipinitialspace=True)
        ils_df["ValidSince"] = pd.to_datetime(ils_df["ValidSince"])
        ils_df = ils_df.set_index("Instrument")

        try:
            ils_df = ils_df.loc[self.instrument_number]
        except KeyError:
            self.logger.critical(
                f"{self.instrument_number} is not in ILS-file.\n"
                "Please ensure you downloaded the newest version from GitLab\n"
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
            self.logger.critical("An unknown error occured while reading the "
                                 "ILS-list. Please contact the support!")
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
        start_date = dt.combine(start_date, dt.min.time())
        if start_date < dates[0]:
            i = 0
            self.logger.warning("Start_date given in input file is earlier"
                                + " than earliest date on disk.")
        elif start_date > dates[-1]:
            self.logger.error("The start date is later than the"
                              + " date of the last interferogram on disk."
                              + "\nTerminate program.")
            quit()  # better raise an error here?
        else:
            i = self._find_closest(dates, start_date)
        return i

    def _get_end_date_pos(self, end_date, dates):
        """Return position of the end date in dates."""
        end_date = dt.combine(end_date, dt.min.time())
        if end_date > dates[-1]:
            i = len(dates)
            self.logger.warning("End_date is larger than the date"
                                "of the last interferogram on disk.")
        elif end_date < self.dates[0]:
            self.logger.error("The end date is earlier than the"
                              + " date of the first interferogram on disk."
                              + "\nTerminate program.")
            quit()  # better raise an error here?
        else:
            i = self._find_closest(self.dates, end_date)
        return i

    def _find_closest(self, datelist, date):
        '''Find the closest entry in a list of dates compared 
        to a specific date.'''
        i = 0
        diff1 = abs(datelist[0] - date)
        for j, entry in enumerate(datelist):
            diff0 = abs(entry - date)
            if diff0 < diff1:
                i = j
                diff1 = diff0
        return i

    def _replace_backslash(self, line):
        """Replace backslash with slash if run on linux."""
        if sys.platform == "linux":
            return line.replace("\\", "/")
        return line

    def _get_spectra_list(self, date):
        """Return list of spectra files generated by preprocess."""
        date_str = date.strftime("%y%m%d")
        spectra_search_str = os.path.join(
            self.analysis_path, date_str, "cal", "*SN.BIN")
        spectra_list = glob(spectra_search_str)
        spectra_list = [os.path.basename(spectra) for spectra in spectra_list]
        if len(spectra_list) == 0:
            raise(RuntimeError("No spectra were found"))
        return spectra_list
        
    def _interpolate_map_files(self, date):
        """
        interpolates the new map files to genereate a map
        file at 12:00 local time
        """
        # print("Interpolate map files to local noon for date ", date)
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
        # only for developement: add 1 h 30 min
        # TODO: Delete after developement!
        # noon_local = noon_local + timedelta(hours=1, minutes=30)

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
