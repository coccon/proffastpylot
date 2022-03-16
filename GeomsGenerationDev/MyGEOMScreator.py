import h5py
import yaml
import sys
import os
import inspect
from prfpylot.prepare import Preparation



class PROFFAST_GEOMS_creator(Preparation):
    def __init__(self, input_file):
        """
        This init can proably completly be omitted as soon as it gets a part
        of the Proffastpylot. for now it is kept for developement.
        """
        super(PROFFAST_GEOMS_creator, self).__init__(input_file)

        # read input file. Contains additional information to create the geoms
        # file
        with open(input_file, "r") as f:
            args = yaml.load(f, Loader=yaml.FullLoader)
        self.input_file = input_file

        self.pt_file_template = os.path.join(
            self.analysis_instrument_path, "{}", "pT",'pT_fast_out.dat')
        self.vmr_file_template = os.path.join(
            self.analysis_instrument_path, "{}" 'pT','VMR_fast_out.dat')


        # Output files:
        self.geoms_out = "_".join([self.site_name,self.instrument_number,
                                   'GEOMS_OUT.h5'])

        self.MyHDF5 = h5py.File(self.geoms_out, 'w')



    def write_metadata(self):
        """ Write metadata to the GEOMS file! """
        # data = myClass.dataDict({},attrs={})

        self.MyHDF5['Instrument_name'] = self.instrument_number
       

    def start(self):
        pass
        #for day in days:
        #    self.write_day()

    def write_day(self, date=None):
        """ create a h5 file for a specific day """
        self.write_metadata()
        #self.MyHDF5.keys()
        self.write_to_disk()

    def write_to_disk(self):
        """ Close the file and write to disk """
        self.MyHDF5.close()

    def _get_correction_factors(self):
        """Returns a dict containing the correction factors for the gases"""
        # This dict is only a preliminary version. In the final version it is
        # read in from a file
        instcal = dict(
            Karlsruhe = {'XCO2_cal': 1.0000, 'XCH4_cal': 1.0000}, # SN037 (ref)
            Sodankyla = {'XCO2_cal': 0.9992, 'XCH4_cal': 0.9994},  # SN039
            Toronto = {'XCO2_cal': 0.9993, 'XCH4_cal': 0.9991}  # SN075
            )
        try:
            cor_fac = instcal[self.site_name]
        except KeyError:
            self.logger.error(f"Could not find site {self.site_name} in list!")
            sys.exit(1)

    def _find_colsen_file(self, date):
        """Find the correct folder where the *colsen.dat of date is located"""
        # in this test stage it only returns a hardcoded folder.
        # in future versions it looks for the correct result folder depending
        # on the date (remember: the results are in a date range folder!)
        path = "E:\\01_proffastpylot_dev\\example\\results\\Sodankyla_"+\
               r"SN039_20170608_20170609\\"
        filename = f"{self.site_name}{self.date.strftime('%y%m%d')}"+\
                   "-colsens.dat"
        return os.path.join(path, filename)

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


if __name__ == "__main__":
    input_file = "input_sodankyla_hdf5extensiontest.yml"

    MyCreator = PROFFAST_GEOMS_creator(input_file)

    MyCreator.write_day()
