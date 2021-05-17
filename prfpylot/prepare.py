import os
import yaml
import datetime as dt
import pandas as pd
from glob import glob


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

        # set parameters from input file
        self.instrument_number = args["instrument_number"]
        self.site_name = args["site_name"]
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
            self.map_path = os.path.join(self.base_path, 'data',
                                         args['instrument_number'], 'map-Files'
                                         )
        self.pt_path = args["pt_path"]
        if self.pt_path == "default":
            # todo: decide if folder is 'log-Files', or 'met-Files'
            self.pt_path = os.path.join(self.base_path, 'data',
                                        args['instrument_number'], 'log-Files'
                                        )
        # path to ils file
        self.ils_file = args["ils_file"]
        if self.ils_file == "default":
            self.ils_file = os.path.join(self.base_path, 'data', 'ILSList.csv')

        # generate relevant parameters
        # all dates to be processed
        date_paths = glob(os.join(self.data_path, "*"))
        self.dates = []
        for date_path in date_paths:
            date = date_path.split()[-1]
            date = dt.strp_time(date)
            self.dates.append(date)

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

    def get_template_path(self, template_type):
        """Return path to the corresponding template file."""
        folder_path = os.path.join(self.base_path, 'prf', 'templates')
        filename = "template_{}.inp".format(self.template_types[template_type])
        template_path = os.path.join(folder_path, filename)
        return template_path

    def get_prf_input_path(self, template_type):
        """Return path to the corresponding prf_input_file."""
        folder_path = os.path.join(self.base_path, 'prf')
        filename = self.template_types[template_type] + ".inp"
        prf_input_path = os.path.join(folder_path, filename)
        return prf_input_path

    def generate_prf_input(self, template_type):
        """Generate a template file.

        Calling the corresponding collect parameters function
        and replace template function.

        params:
            template_type (str): Can be "prep", "pt", "inv" or "pcxc"
        """
        if template_type == "prep":
            parameters = self.get_prep_parameters()
            self.replace_params_in_template(parameters, template_type)
        else:
            return NotImplementedError("Implement other prf input files.")

    def replace_params_in_template(self, parameters, template_type):
        '''
        This methods generates a site specific input file by using a template.
        '''
        templ_file = self.get_template_path(template_type)
        prf_input_file = self.get_prf_input_path(template_type)
        templ_stream = open(templ_file, 'r')
        prf_input_stream = open(prf_input_file, 'w')
        for line in templ_stream:
            new_line = line
            for name, parameter in parameters.items():
                new_line = new_line.replace('%{}%'.format(name), parameter)
            prf_input_stream.write(new_line)
        templ_stream.close()
        prf_input_stream.close()

    def get_prep_parameters(self):
        '''
        Return Parameters to replace in the pereprocess input file.
        '''

        ILS_Channel1, ILS_Channel2 = self.get_ils_from_file()
        # TODO: Change this line to a correct date
        lat, lon, alt = self.coords
        comment = 'Spectra were generated using preprocess 4, a part of '
        'proffast and PRFpylot.'
        if self.note is not None:
            comment = "\n".join([comment, self.note])

        parameters = {
            'ILS_Channel1': ILS_Channel1,
            'ILS_Channel2': ILS_Channel2,
            'site_name': self.site_name,
            'lat': lat,
            'lon': lon,
            'alt': alt,
            'utc_offset': '0',
            'comment': comment
                     }

        return parameters

    def get_ils_from_file(self, return_string=True):
        '''
        This methods reads the ILS from the Instrument_list
        '''
        ils_df = pd.read_csv(self.ils_file)
        try:
            temp = ils_df[ils_df['Instrument'] == self.instrument_number]
            MEChan1 = temp.iloc[0]['Channel1ME']
            PEChan1 = temp.iloc[0]['Channel1PE']
            MEChan2 = temp.iloc[0]['Channel2ME']
            PEChan2 = temp.iloc[0]['Channel2PE']
        except KeyError as e:
            print('Error: it was not possible to get ILS from file')
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
            raise Exception('Error reading CoordFile. Please check format'
                            + ' and path.')
        return lat, lon, alt
