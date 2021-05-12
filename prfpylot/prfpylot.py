import os
import yaml
import datetime as dt
import pandas as pd
from prepare import Preparation


class Pylot(Prepare):
    """Start all Profast processes."""

    def __init__(self, input_file):
        super(Pylot, self).__init__(input_file)

    

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
        self.fill_template_file(parameters, 'prep')
