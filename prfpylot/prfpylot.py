import os
import yaml
import datetime as dt
import pandas as pd


class PRFpylot():
    """PROFAST wrapper."""

    def __init__(self, input_path="input.yml"):
        # read input file
        with open(input_path, "r") as f:
            args = yaml.load(f, Loader=yaml.FullLoader)

        # set parameters from input file
        self.instrument_number = args["instrument_number"]
        self.site_name = args["site_name"]
        self.root_path = args["root_path"]
        if self.root_path == "default":
            cwd = os.getcwd()
            cwd = os.path.split(cwd)
            self.root_path = os.path.join(*cwd[:-1], '..')

        self.map_path = args["map_path"]
        if self.map_path == "default":
            self.map_path = os.path.join(self.root_path, 'data',
                                         args['instrument_number'], 'map-Files'
                                         )
        self.pt_path = args["pt_path"]
        if self.pt_path == "default":
            # todo: decide if folder is 'log-Files', or 'met-Files'
            self.pt_path = os.path.join(self.root_path, 'data',
                                        args['instrument_number'], 'log-Files'
                                        )

        self.coord_file = args["coord_file"]
        if self.coord_file == "default":
            # todo: decide if folder is 'log-Files', or 'met-Files'
            self.coord_file = os.path.join(self.root_path, 'data',
                                           args['instrument_number'],
                                           'CoordFile.txt'
                                           )
        self.ils_file = args["ils_file"]
        if self.ils_file == "default":
            self.ils_file = os.path.join(self.root_path, 'data', 'ILSList.csv')
        # set general parameters
        template_path = os.path.join(self.root_path, 'prf', 'templates')
        self.tempfiles = {
            "prep": os.path.join(template_path, 'template_preprocess4.inp'),
            "pt": os.path.join(template_path, 'template_pT_intraday.inp'),
            "inv": os.path.join(template_path, 'template_invers10.inp'),
            "pcxs": os.path.join(template_path, 'template_pcxs10.inp')
        }
        # generate the paths of the input files:
        binary_path = os.path.join(self.root_path, 'prf')
        self.inputfiles = {
            "prep": os.path.join(binary_path, 'preprocess4.inp'),
            "pt": os.path.join(binary_path, 'pT_intraday.inp'),
            "inv": os.path.join(binary_path, 'invers10.inp'),
            "pcxs": os.path.join(binary_path, 'pcxs10.inp')
        }

    def fill_template_file(self, dict, template):
        '''
        This methods generates a site specific input file by using a template.
        '''
        templ_file = self.tempfiles[template]
        input_file = self.inputfiles[template]
        templ_stream = open(templ_file, 'r')
        input_stream = open(input_file, 'w')
        for line in templ_stream:
            new_line = line
            for key in dict:
                new_line = new_line.replace('%{}%'.format(key), str(dict[key]))
            input_stream.write(new_line)
        templ_stream.close()
        input_stream.close()

    def get_coords_from_file(self, currDate):
        '''
        This methods reads out the coordinates from the coord file.
        '''
        coordDataFrame = pd.read_csv(self.coord_file, sep=',', engine='python')
        lat, lon, alt = 0., 0., 0.

        for i, date in enumerate(coordDataFrame['Date']):
            date = dt.datetime.strptime(str(date), '%Y%m%d')
            if currDate >= date:
                lat = coordDataFrame.iloc[i]['Latitude']
                lon = coordDataFrame.iloc[i]['Longitude']
                alt = coordDataFrame.iloc[i]['Alt_kmasl']
        if lat == 0. or lon == 0. or alt == 0:
            raise Exception('Error reading CoordFile. Please check format'
                            + ' and path.')
        return (lat, lon, alt)

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

    def generate_preproces_template(self):
        '''
        This method generates the preprocess template file.
        '''
        ILS_Channel1, ILS_Channel2 = self.get_ils_from_file()
        # TODO: Change this line to a correct date
        currDate = dt.datetime.now()
        lat, lon, alt = self.get_coords_from_file(currDate)
        comment = 'Spectra were generated using preprocess 4, a part of ' \
                  + 'proffast and PRFpylot.'
        parameter = {
            'ILS_Channel1': ILS_Channel1,
            'ILS_Channel2': ILS_Channel2,
            'site_name': self.site_name,
            'lat': lat,
            'lon': lon,
            'alt': alt,
            'utc_offset': '0',
            'comment': comment
                     }
        self.fill_template_file(parameter, 'prep')
