import h5py
import os
import datetime as dt
import numpy as np
import pandas as pd
from GeomsHelperClass import Geoms_Helper


class PROFFAST_GEOMS_creator(Geoms_Helper):
    def __init__(self, GEOMS_input_file):
        """
        This init can proably completly be omitted as soon as it gets a part
        of the Proffastpylot. for now it is kept for developement.
        """
        # call the init method of the `Preparation` class. This provides
        # some usefull data within this class.
        super(PROFFAST_GEOMS_creator, self).__init__(GEOMS_input_file)

    def generate_GEOMS_at(self, day):
        """ create a GEOMS file for a specific day """
        if not isinstance(day, dt.datetime):
            self.logger.error

        # create filename:
        self.geoms_out = "_".join([self.site_name, self.instrument_number,
                                   'GEOMS_OUT.h5'])
        datestring = day.strftime("%y%m%d")
        geoms_file = "_".join(
            [self.site_name, self.instrument_number,
             datestring, 'GEOMS_OUT.h5']
                             )
        geoms_file = os.path.join(self.geoms_out_path, geoms_file)

        # create Geoms file:
        self.MyHDF5 = h5py.File(geoms_file, 'w')
        # Do stuff...
        self.write_metadata()
        self.write_CH4_data(day)
        # close the file and write to disk.
        self.MyHDF5.close()

    def write_CH4_data(self, day):
        """ Collects the CH4 data and writes them to the HDF5 file """
        dataset_name = \
            "CH4.COLUMN.MIXING.RATIO.VOLUME.DRY_ABSORPTION.SOLAR"

        # Here the data has to be collected.
        # I do not know if this is the best way to do it.
        # Maybe it is better to retrieve it directly from ivparms.dat file??
        df = pd.read_csv(self._find_csv_file(day), skipinitialspace=True)
        df["UTC"] = pd.to_datetime(df["UTC"])
        # get only the data of current day:
        starttime = day.replace(hour=0, minute=0, second=0)
        endtime = day.replace(hour=23, minute=59, second=59)
        datetime_mask = (df["UTC"] > starttime) & (df["UTC"]< endtime)
        df = df.loc[datetime_mask]
        # convert to numpy:
        data = df["XCH4"].to_numpy()

        # TODO: This list is not complete it serves only as an example
        attributes = {
            "VAR_DEPEND": "DATETIME",
            "units": "ppmv",
            "VAR_DESCRIPTION": "Column average dry air mole fraction",
        }

        self.CH4_dtst = self._write_dataset(data, dataset_name, attributes)

    def write_metadata(self):
        """ Write metadata to the GEOMS file! """
        # attribut list, which contains the variables given in the input files
        attribute_list =\
            ["DATA_SOURCE", "DS_AFFILIATION", "DS_ADDRESS", "DS_EMAIL",
             "DS_NAME", "PI_NAME", "PI_EMAIL", "PI_AFFILIATION", "PI_ADDRESS",
             "DO_NAME", "DO_AFFILIATION", "DO_ADDRESS", "DO_EMAIL", "FILE_DOI"]
        for attr in attribute_list:
            # H5Py needs to store the strings using this numpy method:
            # see: https://docs.h5py.org/en/2.3/strings.html
            # Furhtermore they have to be in edged brackets to provide an array
            self.MyHDF5.attrs[attr] = [np.string_(self.input_args[attr])]

        # The following attributes are copied from `CocconHDFtoGEOMS.py`
        # and partly adapted as fas as the data was already available
        # The rest is commented and have to be done later.
        self.MyHDF5.attrs["DATA_TEMPLATE"] = \
            [np.string_('GEOMS-TE-FTIR-COCCON-001.csv')]

        self.MyHDF5.attrs['DATA_DESCRIPTION'] = \
            [np.string_(f"{self.instrument_number} measurements"
                     f" from {self.site_name}")]

        corr_fac = self._get_correction_factors()
        self.MyHDF5.attrs['DATA_MODIFICATIONS'] = \
            [np.string_("Calibration factors applied:"
                     f" {corr_fac['XCO2_cal']} for XCO2"
                     f" and {corr_fac['XCH4_cal']} for XCH4")]

        self.MyHDF5.attrs['FILE_ACCESS'] = [np.string_('COCCON')]

        self.MyHDF5.attrs['FILE_META_VERSION'] = [np.string_('04R052;CUSTOM')]

        self.MyHDF5.attrs['FILE_PROJECT_ID'] = [np.string_('COCCON')]

        # self.MyHDF5.attrs['DATA_PROCESSOR'] = \
        #     [np.string_(fid.attrs['DATA_PROCESSOR'])]

        # self.MyHDF5.attrs['DATA_VARIABLES'] = \
        #     [np.string_(';'.join(variableswritten)]

        # self.MyHDF5.attrs['DATA_QUALITY'] = \
        #     [np.string_(fid.attrs['DATA_QUALITY'])]

        self.MyHDF5.attrs['FILE_GENERATION_DATE'] = \
            [np.string_(dt.datetime.now().strftime('%Y%m%dT%H%M%SZ'))]


if __name__ == "__main__":
    input_file = "input_sodankyla_GEOMS_Extention.yml"

    MyCreator = PROFFAST_GEOMS_creator(input_file)

    MyTestDay = dt.datetime.strptime("2017-06-09", "%Y-%m-%d")
    MyCreator.generate_GEOMS_at(day=MyTestDay)

