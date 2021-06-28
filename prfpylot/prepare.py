import os
import yaml
from datetime import datetime as dt
import pandas as pd
from glob import glob
import logging


class Preparation():
    template_types = {
        "prep": "preprocess4",
        "pt": "pT_intraday",
        "inv": "invers10",
        "pcxs": "pcxs10"
    }

    """Import input parameters, and create input files."""

    def __init__(self, input_path="input.yml"):
        # read input file
        with open(input_path, "r") as f:
            args = yaml.load(f, Loader=yaml.FullLoader)

        # Create a logger
        self.logger = self.get_logger()
        # set parameters from input file
        self.instrument_number = args["instrument_number"]
        self.site_name = args["site_name"]
        self.site_abbrev = args["site_abbrev"]
        self.note = args["note"]

        # generate paths
        # path to profast base directory
        self.base_path = args["base_path"]
        if self.base_path == "default":
            self.base_path = os.getcwd()

        self.data_path = os.path.join(
            self.base_path, "data", self.instrument_number, self.site_name)

        self.map_path = args["map_path"]
        if self.map_path == "default":
            self.map_path = os.path.join(
                self.base_path, 'data', "atmospheric", self.site_name, "map")

        self.log_path = args["log_path"]
        if self.log_path == "default":
            self.log_path = os.path.join(
                self.base_path, "data", "atmospheric", self.site_name, "log")

        self.pt_path = args["pt_path"]
        if self.pt_path == "default":
            self.pt_path = os.path.join(
                self.base_path, "data", "atmospheric", self.site_name, "pt")

        # path to ils file
        self.ils_file = args["ils_file"]
        if self.ils_file == "default":
            self.ils_file = os.path.join(self.base_path, 'data', 'ILSList.csv')

        # path to preprocess folder and to preprocess log-folder
        self.prep_path = os.path.join(self.base_path, "prf", "preprocess")
        if args["prep4_logpath"] == "default":
            self.prep4_logpath = os.path.join(self.prep_path, "log-files")
        else:
            self.prep4_logpath = args["prep4_logpath"]

        # safe the path where the igrams and spectra are safed as class
        # variable since it is needed often.
        self.igram_path = os.path.join(self.data_path, "interferograms")
        self.spectra_path = os.path.join(self.data_path, "spectra")
        # generate relevant parameters
        # all dates to be processed:
        date_paths = glob(os.path.join(self.igram_path, "*"))
        self.dates = []
        # TODO: Implement a possibility to specify startDate and endDate.
        #       If implemented, a list like the one below can be generated
        #       artificially.
        for date_path in date_paths:
            date = os.path.split(date_path)[1]
            date = dt.strptime(date, "%y%m%d")
            self.dates.append(date)

        def find_closest(list, item):
            '''Find the closest entry in a list copared to item'''
            i = 0
            diff1 = abs(list[0] - item)
            for j, entry in enumerate(list):
                diff0 = abs(entry - item)
                if diff0 < diff1:
                    i = j
                    diff1 = diff0
            return i

        if args['start_date'] != 'default':

            self.start_date = dt.combine(args["start_date"], dt.min.time())
            if self.start_date < self.dates[0]:
                i = 0
                self.logger.warning("Start_date given in input file is earlier"
                                    + " than earliest date on disk.")
            elif self.start_date > self.dates[-1]:
                self.logger.error("The start date is later than the"
                                  + " date of the last interferogram on disk."
                                  + "\nTerminate program.")
                quit()
            else:
                i = find_closest(self.dates, self.start_date)
            self.dates = self.dates[i:]

        if args['end_date'] != 'default':
            self.end_date = dt.combine(args["end_date"], dt.min.time())
            if self.end_date > self.dates[-1]:
                i = len(self.dates)
                self.logger.warning("End_date is larger than the date"
                                    "of the last interferogram on disk.")
            elif self.end_date < self.dates[0]:
                self.logger.error("The end date is earlier than the"
                                  + " date of the first interferogram on disk."
                                  + "\nTerminate program.")
                quit()
            else:
                i = find_closest(self.dates, self.end_date)
            self.dates = self.dates[:i]

        # coordinates
        if None not in args["coords"].values():
            self.coords = args["coords"]
            self.coord_file = None  # to avoid overriding given coords
        else:
            if args["coord_file"] != "default":
                coord_file = args["coord_file"]
            else:
                coord_file = os.path.join(
                    self.base_path, "data",
                    self.instrument_number, "coords.csv")
            self.coords = self.get_coords_from_file(coord_file)

    def get_logger(self):
        # Create a logger
        logger = logging.getLogger('Preparation')
        # set logging to debug to record everythin in the first place
        logger.setLevel(logging.DEBUG)
        StreamHandler = logging.StreamHandler()
        FHandler = logging.FileHandler('Logfile.txt', mode='w')
        StreamHandler.setLevel(logging.DEBUG)
        FHandler.setLevel(logging.DEBUG)
        logger.addHandler(StreamHandler)
        logger.addHandler(FHandler)
        StreamFormat = logging.Formatter(
            '{asctime}: {filename},line {lineno} -> {levelname}: {message}',
            style='{')
        StreamHandler.setFormatter(StreamFormat)
        FHandler.setFormatter(StreamFormat)
        return logger

    def get_template_path(self, template_type):
        """Return path to the corresponding template file."""
        folder_path = os.path.join(self.base_path, "prf", "templates")
        filename = "template_{}.inp".format(self.template_types[template_type])
        template_path = os.path.join(folder_path, filename)
        return template_path

    def get_prf_input_path(self, template_type, date=None):
        """Return path to the corresponding prf_input_file."""
<<<<<<< HEAD
        folder_path = os.path.join(self.base_path, 'prf')
        if template_type in ["pcxs", "inv"]:
            date_str = dt.strftime(date, "%y%m%d")
        else:
            date_str = ""
        filename = self.template_types[template_type] + date_str + ".inp"
=======
        folder_path = os.path.join(self.base_path, "prf")
        # preprocess is in an other folder than the rest:
        if template_type == "prep":
            folder_path = os.path.join(folder_path, "preprocess")
        filename = self.template_types[template_type] + ".inp"
>>>>>>> master
        prf_input_path = os.path.join(folder_path, filename)
        return prf_input_path

    def generate_prf_input(self, template_type, date=None):
        """Generate a template file.

        Calling the corresponding collect parameters function
        and replace template function.

        params:
            template_type (str): Can be "prep", "pt", "inv" or "pcxc"
        """
        if date is not None:
            date_str = dt.strftime(date, "%y%m%d")
        if template_type == "prep":
            self.logger.info("generating preprocess4.inp ...")
            parameters = self.get_prep_parameters()
        elif template_type == "pcxs":
<<<<<<< HEAD
            print(f"generating pcxs10_{date_str}.inp ...")
            parameters = self.get_pcxs_and_inv_parameters(date)
        elif template_type == "inv":
            print(f"generating invers10_{date_str}.inp ...")
=======
            self.logger.info("generating pcxs10.inp ...")
            parameters = self.get_pcxs_and_inv_parameters(date)
        elif template_type == "inv":
            self.logger.info("generating invers10.inp ...")
>>>>>>> master
            parameters = self.get_pcxs_and_inv_parameters(date)
        else:
            raise NotImplementedError("Implement other prf input files.")
        self.replace_params_in_template(parameters, template_type)

    def get_igrams(self):
        """
        Search for spectra on disk an add them to the preprocess input file.
        """
        # TODO: Implement start and endDate
        igram_list = []
        for date in self.dates:
            date_str = date.strftime("%y%m%d")
            igrams = glob(os.path.join(self.igram_path, date_str, "*.*"))

            if igrams == []:
                self.logger.warning(f"Interferogram at day {date} not found.")
        return igram_list

    def replace_params_in_template(self, parameters, template_type):
        """
        This methods generates a site specific input file by using a template.
        params:
            parameters(dict): containing keys which match the variable
                              names in the template file. They are replaced by
                              the entries.

            template_type(str): Can be "prep", "pt", "inv" or "pcxc"
        """
        templ_file = self.get_template_path(template_type)
        prf_input_file = self.get_prf_input_path(template_type)
        templ_stream = open(templ_file, 'r')
        prf_input_stream = open(prf_input_file, 'w')
        for line in templ_stream:
            new_line = line
            for key, parameter in parameters.items():
                if isinstance(parameter, list):
                    # some files need to be filled with a list of files.
                    # hence check if the parameter is a list. Then add each
                    # entry as an extra line.
                    if key in new_line:
                        new_line = '\n'.join(parameter)
                else:
                    new_line = new_line.replace('%{}%'.format(key),
                                                str(parameter)
                                                )
            prf_input_stream.write(new_line)
        templ_stream.close()
        prf_input_stream.close()

    def get_prep_parameters(self):
        '''
        Return Parameters to be replace in the pereprocess input file.
        '''

        ILS_Channel1, ILS_Channel2 = self.get_ils_from_file()
        # TODO: Change this line to a correct date
        lat, lon, alt = self.coords
        comment = (
            "This spectrum is generated using preprocess4, a part of "
            "PROFAST controlled by PRFpylot.")
        if self.note is not None:
            comment = " ".join([comment, self.note])

        igrams = "\n".join(self.get_igrams())
        parameters = {
            'ILS_Channel1': ILS_Channel1,
            'ILS_Channel2': ILS_Channel2,
            'site_name': self.site_name,
            'lat': lat,
            'lon': lon,
            'alt': alt,
            'utc_offset': '0.0',
            'comment': comment,
            'igrams': igrams,
                     }
        # TODO: Add key 'raw_measurement_list' to dict
        #       this dict contains  a list of all raw measurements.

        return parameters

    def get_pcxs_and_inv_parameters(self, date):
        """Return Parameters to replace in the pcxs10.inp
        or invers10.inp files."""
        lat, lon, alt = self.coords

        parameters = {
            "ALT": alt,
            "LAT": lat,
            "LON": lon,
            "INSTRUMENT": self.instrument_number,
            "SITE": self.site_name,
            "DATE": date.strftime("%y%m%d"),
            "DATE_LONG": date.strftime("%Y%m%d"),
            "SITE_ABBREV": self.site_abbrev,
        }
        return parameters

    def get_ils_from_file(self, return_string=True):
        """
        This methods reads the ILS from the Instrument_list.
        If return_string=True, it returns a string which is already
        preformatted such that it can be inserted into the template file
        directly.
        """
        ils_df = pd.read_csv(self.ils_file)
        try:
            temp = ils_df[ils_df['Instrument'] == self.instrument_number]
            MEChan1 = temp.iloc[0]['Channel1ME']
            PEChan1 = temp.iloc[0]['Channel1PE']
            MEChan2 = temp.iloc[0]['Channel2ME']
            PEChan2 = temp.iloc[0]['Channel2PE']
        except KeyError as e:
            self.logger.error('It was not possible to get ILS from file')
            raise (e)
        if return_string:
            return ('{} {}'.format(MEChan1, PEChan1),
                    '{} {}'.format(MEChan2, PEChan2)
                    )
        else:
            return (MEChan1, PEChan1, MEChan2, PEChan2)

    def get_coords_from_file(self, coord_file):
        '''This methods reads out the coordinates from the coord file.'''
        coord_df = pd.read_csv(coord_file).set_index("Site")
        lat, lon, alt = 0., 0., 0.

        row = coord_df.loc[self.site_name]
        lon = row["Longitude"]
        lat = row["Latitude"]
        alt = row["Altitude_kmasl"]

        if lat == 0. or lon == 0. or alt == 0:
            raise Exception(
                "Error reading CoordFile. Please check format and path.")
        return lat, lon, alt
