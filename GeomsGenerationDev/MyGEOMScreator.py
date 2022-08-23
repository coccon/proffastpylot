import h5py
import os
import re
import math
import datetime as dt
import numpy as np
import pandas as pd
from GeomsHelperClass import Geoms_Helper


class PROFFAST_GEOMS_creator(Geoms_Helper):
    def __init__(self, GEOMS_input_file):

        """
        This init can probably be omitted completly once it gets a part
        of the Proffastpylot. for now it is kept for developement.
        """

      # Call the init method of the `Preparation` class.
      # This provides some usefull data within this class.

        super(PROFFAST_GEOMS_creator, self).__init__(GEOMS_input_file)

      # List of all variables for the GEOMS compliant HDF5 files.
      # For further information, see document "geoms-1.0.pdf":
      # https://avdc.gsfc.nasa.gov/PDF/GEOMS/geoms-1.0.pdf

        self.hdf5_vars = {
          "SRC_PRO": "SOURCE.PRODUCT",
          "DAT_TIM": "DATETIME",
          "ALT": "ALTITUDE",
          "SOL_ZEN": "ANGLE.SOLAR_ZENITH.ASTRONOMICAL",
          "SOL_AZI": "ANGLE.SOLAR_AZIMUTH",
          "INST_LAT": "LATITUDE.INSTRUMENT",
          "INST_LON": "LONGITUDE.INSTRUMENT",
          "INST_ALT": "ALTITUDE.INSTRUMENT",
          "SUR_IND": "SURFACE.PRESSURE_INDEPENDENT",
          "SUR_SRC": "SURFACE.PRESSURE_INDEPENDENT_SOURCE",
          "PRE_IND": "PRESSURE_INDEPENDENT",
          "PRE_SRC": "PRESSURE_INDEPENDENT_SOURCE",
          "TEM_IND": "TEMPERATURE_INDEPENDENT",
          "TEM_SRC": "TEMPERATURE_INDEPENDENT_SOURCE",
          "AIR_COL": "DRY.AIR.COLUMN.PARTIAL_INDEPENDENT",
          "AIR_DEN": "DRY.AIR.NUMBER.DENSITY_INDEPENDENT",
          "AIR_SRC": "DRY.AIR.NUMBER.DENSITY_INDEPENDENT_SOURCE",
          "H2O_COL": "H2O.COLUMN.MIXING.RATIO.VOLUME.DRY_ABSORPTION.SOLAR",
          "H2O_UNC": "H2O.COLUMN.MIXING.RATIO.VOLUME.DRY_ABSORPTION.SOLAR_UNCERTAINTY.RANDOM.STANDARD",
          "H2O_APR": "H2O.MIXING.RATIO.VOLUME.DRY_APRIORI",
          "H2O_SRC": "H2O.MIXING.RATIO.VOLUME.DRY_APRIORI.SOURCE",
          "H2O_AVK": "H2O.COLUMN_ABSORPTION.SOLAR_AVK",
          "CO2_COL": "CO2.COLUMN.MIXING.RATIO.VOLUME.DRY_ABSORPTION.SOLAR",
          "CO2_UNC": "CO2.COLUMN.MIXING.RATIO.VOLUME.DRY_ABSORPTION.SOLAR_UNCERTAINTY.RANDOM.STANDARD",
          "CO2_APR": "CO2.MIXING.RATIO.VOLUME.DRY_APRIORI",
          "CO2_SRC": "CO2.MIXING.RATIO.VOLUME.DRY_APRIORI.SOURCE",
          "CO2_AVK": "CO2.COLUMN_ABSORPTION.SOLAR_AVK",
          "CH4_COL": "CH4.COLUMN.MIXING.RATIO.VOLUME.DRY_ABSORPTION.SOLAR",
          "CH4_UNC": "CH4.COLUMN.MIXING.RATIO.VOLUME.DRY_ABSORPTION.SOLAR_UNCERTAINTY.RANDOM.STANDARD",
          "CH4_APR": "CH4.MIXING.RATIO.VOLUME.DRY_APRIORI",
          "CH4_SRC": "CH4.MIXING.RATIO.VOLUME.DRY_APRIORI.SOURCE",
          "CH4_AVK": "CH4.COLUMN_ABSORPTION.SOLAR_AVK",
          "CO_COL": "CO.COLUMN.MIXING.RATIO.VOLUME.DRY_ABSORPTION.SOLAR",
          "CO_UNC": "CO.COLUMN.MIXING.RATIO.VOLUME.DRY_ABSORPTION.SOLAR_UNCERTAINTY.RANDOM.STANDARD",
          "CO_APR": "CO.MIXING.RATIO.VOLUME.DRY_APRIORI",
          "CO_SRC": "CO.MIXING.RATIO.VOLUME.DRY_APRIORI.SOURCE",
          "CO_AVK": "CO.COLUMN_ABSORPTION.SOLAR_AVK"
        }

      # List of common attributes for the variables of the GEOMS compliant HDF5 files.
      # This list is not used for the source variables.

        self.hdf5_atts = {
            "VAR_DATA_TYPE": "",
            "VAR_DEPEND": "",
            "VAR_DESCRIPTION": "",
            "VAR_FILL_VALUE": -900000.0,
            "VAR_NAME": "",
            "VAR_NOTES": "",
            "VAR_SIZE": "",
            "VAR_SI_CONVERSION": "",
            "VAR_UNITS": "",
            "VAR_VALID_MAX": 0,
            "VAR_VALID_MIN": 0,
            "_FillValue": -900000.0,
            "units": "",
            "valid_range": [0,0]
        }

      # List of common attributes for the source variables of the GEOMS compliant HDF5 files.

        self.hdf5_atts_src = {
            "VAR_DATA_TYPE": "",
            "VAR_DEPEND": "",
            "VAR_DESCRIPTION": "",
            "VAR_FILL_VALUE": "",
            "VAR_NAME": "",
            "VAR_NOTES": "",
            "VAR_SIZE": "",
            "VAR_SI_CONVERSION": "",
            "VAR_UNITS": "",
            "VAR_VALID_MAX": "",
            "VAR_VALID_MIN": "",
            "_FillValue": "",
        }

        self.file_name = ''
        self.variables = []


    def generate_GEOMS_at(self, day):

        """ create a GEOMS file for a specific day """

        if not isinstance(day, dt.datetime):
            self.logger.error

      # Create path and preliminary name for the output HDF5 file.

        self.geoms_out = "_".join([self.site_name, self.instrument_number,
                                   'GEOMS_OUT.h5'])

        geoms_file = os.path.join(self.geoms_out_path, 'GEOMS_OUT.h5')

      # Create GEOMS output file.

        self.MyHDF5 = h5py.File(geoms_file, 'w')

      # Get data from the PROFFAST inparms output files

      # df = self.get_data_content(day)     # PROFFAST output (df pandas data frame)
        df = self.get_invparms_content(day) # invparms file

      # After applying the quality filter for SZA and XAIR (see get_invparms_content),
      # at least 12 remaining measurements per measurement day are required to generate an HDF5 file.

      # if df == -1:
      #     print (df, type(df))
      #     return

      # Get additional information from the colsens, pT_fast_out, and VMR_fast_out PROFFAST output files.

        vmr = self.get_vmr_content(day)      # VMR file
        ptf = self.get_pt_content(day)       # pT file
        sen = self.get_colsens_int(df, day)  # col sens file (including a sza interpolation)

      # Write all variables for generating the GEOMS compliant HDF5 files.

        self.write_source('SRC_PRO')                   # "SOURCE.PRODUCT"

        self.write_datetime(df, "DAT_TIM")             # "DATETIME"
        self.write_altitude(df, ptf, "ALT")            # "ALTITUDE"
        self.write_solar_angle_zenith(df, "SOL_ZEN")   # "ANGLE.SOLAR_ZENITH.ASTRONOMICAL"
        self.write_solar_angle_azimuth(df, "SOL_AZI")  # "ANGLE.SOLAR_AZIMUTH"
        self.write_instr_latitude(df, "INST_LAT")      # "LATITUDE.INSTRUMENT"
        self.write_instr_longitude(df, "INST_LON")     # "LONGITUDE.INSTRUMENT"
        self.write_instr_altitude(df, "INST_ALT")      # "ALTITUDE.INSTRUMENT"
        self.write_surface_pressure(df, "SUR_IND")     # "SURFACE.PRESSURE_INDEPENDENT"
        self.write_surface_pressure_src(df, "SUR_SRC") # "SURFACE.PRESSURE_INDEPENDENT_SOURCE"
        self.write_pressure(df, ptf, "PRE_IND")        # "PRESSURE_INDEPENDENT"
        self.write_pressure_src(df, "PRE_SRC")         # "PRESSURE_INDEPENDENT_SOURCE"
        self.write_temperature(df, ptf, "TEM_IND")     # "TEMPERATURE_INDEPENDENT"
        self.write_temperature_src(df, "TEM_SRC")      # "TEMPERATURE_INDEPENDENT_SOURCE"

        self.write_col(df, "H2O_COL")                  # "H2O.COLUMN.MIXING.RATIO.VOLUME.DRY_ABSORPTION.SOLAR"
        self.write_col_unc(df, "H2O_UNC")              # "H2O.COLUMN.MIXING.RATIO.VOLUME.DRY_ABSORPTION.SOLAR_UNCERTAINTY.RANDOM.STANDARD"
        self.write_apr(df, ptf, vmr, "H2O_APR")        # "H2O.MIXING.RATIO.VOLUME.DRY_APRIORI",
        self.write_apr_src(df, "H2O_SRC")              # "H2O.MIXING.RATIO.VOLUME.DRY_APRIORI.SOURCE",
        self.write_avk(df, ptf, sen, "H2O_AVK")        # "H2O.COLUMN_ABSORPTION.SOLAR_AVK",

        self.write_col(df, "CO2_COL")                  # "CO2.COLUMN.MIXING.RATIO.VOLUME.DRY_ABSORPTION.SOLAR"
        self.write_col_unc(df, "CO2_UNC")              # "CO2.COLUMN.MIXING.RATIO.VOLUME.DRY_ABSORPTION.SOLAR_UNCERTAINTY.RANDOM.STANDARD"
        self.write_apr(df, ptf, vmr, "CO2_APR")        # "CO2.MIXING.RATIO.VOLUME.DRY_APRIORI",
        self.write_apr_src(df, "CO2_SRC")              # "CO2.MIXING.RATIO.VOLUME.DRY_APRIORI.SOURCE",
        self.write_avk(df, ptf, sen, "CO2_AVK")        # "CO2.COLUMN_ABSORPTION.SOLAR_AVK",

        self.write_col(df, "CH4_COL")                  # "CH4.COLUMN.MIXING.RATIO.VOLUME.DRY_ABSORPTION.SOLAR"
        self.write_col_unc(df, "CH4_UNC")              # "CH4.COLUMN.MIXING.RATIO.VOLUME.DRY_ABSORPTION.SOLAR_UNCERTAINTY.RANDOM.STANDARD"
        self.write_apr(df, ptf, vmr, "CH4_APR")        # "CH4.MIXING.RATIO.VOLUME.DRY_APRIORI",
        self.write_apr_src(df, "CH4_SRC")              # "CH4.MIXING.RATIO.VOLUME.DRY_APRIORI.SOURCE",
        self.write_avk(df, ptf, sen, "CH4_AVK")        # "CH4.COLUMN_ABSORPTION.SOLAR_AVK",

        self.write_col(df, "CO_COL")                   # "CO.COLUMN.MIXING.RATIO.VOLUME.DRY_ABSORPTION.SOLAR"
        self.write_col_unc(df, "CO_UNC")               # "CO.COLUMN.MIXING.RATIO.VOLUME.DRY_ABSORPTION.SOLAR_UNCERTAINTY.RANDOM.STANDARD"
        self.write_apr(df, ptf, vmr, "CO_APR")         # "CO.MIXING.RATIO.VOLUME.DRY_APRIORI",
        self.write_apr_src(df, "CO_SRC")               # "CO.MIXING.RATIO.VOLUME.DRY_APRIORI.SOURCE",
        self.write_avk(df, ptf, sen, "CO_AVK")         # "CO.COLUMN_ABSORPTION.SOLAR_AVK",

        self.write_air_partial(df, ptf, "AIR_COL")     # "DRY.AIR.COLUMN.PARTIAL_INDEPENDENT"
        self.write_air_density(df, ptf, "AIR_DEN")     # "DRY.AIR.NUMBER.DENSITY_INDEPENDENT"
        self.write_air_density_src(df, "AIR_SRC")      # "DRY.AIR.NUMBER.DENSITY_INDEPENDENT_SOURCE"

      # Write meta information for the variables stored in the HDF5 files.

        self.write_metadata(day, df)
        geoms_file_name = os.path.join(self.geoms_out_path, self.file_name)

      # close file and write to hard disk.

        self.MyHDF5.close()

      # Remove existing file and rename preliminary file name.

        if os.path.exists(geoms_file_name):
            os.remove(geoms_file_name) # delete file in case the file already exits
        os.rename(geoms_file, geoms_file_name)


    def get_start_stop_date_time(self, day, df):

      # Get date and time of the first and last measurement of the measurement day.

        data = df["JulianDate"]

      # Possible problems with the subsequent quality checks of the HDF5 files can be fixed here.

        data = pd.DataFrame(data)
      # data = self._GEOMStoDateTime((data['JulianDate'] - 2451544.5) * 86400.0)
        data = self._GEOMStoDateTime(np.round((data['JulianDate'] - 2451544.5) * 86400.0)) # ???

        start_date = str(day)[0:10]
        start_date = start_date + 'T'
        start_date = start_date + str(data[0].time())
        start_date = start_date + 'Z'
        start_date = start_date.replace('-','')
        start_date = start_date.replace(':','')

        stop_date = str(day)[0:10]
        stop_date = stop_date + 'T'
        stop_date = stop_date + str(data[-1].time())
        stop_date = stop_date + 'Z'
        stop_date = stop_date.replace('-','')
        stop_date = stop_date.replace(':','')

        return (start_date, stop_date)


    def get_start_stop_date_time_csv(self, day):

        """ Get start and stop time for each measurement day """

        df = pd.read_csv(self._find_csv_file(day), skipinitialspace=True)
        df["UTC"] = pd.to_datetime(df["UTC"])
      # df["LocalTime"] = pd.to_datetime(df["LocalTime"])
        starttime = day.replace(hour=0, minute=0, second=0)
        endtime = day.replace(hour=23, minute=59, second=59)
        datetime_mask = (df["UTC"] > starttime) & (df["UTC"]< endtime)
      # datetime_mask = (df["LocalTime"] > starttime) & (df["LocalTime"]< endtime)

        df = df.loc[datetime_mask]
        data = df["UTC"].to_numpy()
      # data = df["LocalTime"].to_numpy()

        start_date = str(data[0])
        start_date = start_date.replace('-','')
        start_date = start_date.replace(':','')
        start_date = start_date.replace('.000000000','')
        start_date = start_date+'Z'

        stop_date = str(data[-1])
        stop_date = stop_date.replace('-','')
        stop_date = stop_date.replace(':','')
        stop_date = stop_date.replace('.000000000','')
        stop_date = stop_date+'Z'

        return (start_date, stop_date)


    def get_data_content(self, day):

      # Here, the data are obtained from the file that summarizes all the measurement days.
      # The data can be retrieved directly from ivparms.dat file instead.

        df = pd.read_csv(self._find_csv_file(day), skipinitialspace=True)
        df["UTC"] = pd.to_datetime(df["UTC"])

      # Get the data only for the current day.

        starttime = day.replace(hour=0, minute=0, second=0)
        endtime = day.replace(hour=23, minute=59, second=59)
        datetime_mask = (df["UTC"] > starttime) & (df["UTC"] < endtime)
        df = df.loc[datetime_mask]

        return df


    def get_vmr_content(self, day):

      # The content of the output VMR file is read separately for each measurement day.
      # Each VMR file (i.e. VMR_fast_out.dat) contains:
      # 0: "Index", 1: "Altitude", 2: "H2O", 3: "HDO", 4: "CO2", 5: "CH4", 6: "N2O", 7: "CO", 8: "O2", 9: "HF"

        vmr = pd.read_csv(self._get_pt_vmr_file(day, "VMR"), header=None, skipinitialspace=True, \
            usecols=[0,1,2,3,4,5,6,7,8,9], \
            names=['Index','Altitude','H2O','HDO','CO2','CH4','N2O','CO','O2','HF'], \
            sep=' ', engine='python')

        return vmr


    def get_pt_content(self, day):

      # The content of the pT output file is read separately for each measurement day.
      # Each pT file (i.e. pT_fast_out.dat) contains:
      # 0: "Index", 1: "Altitude", 2: "Temperature", 3: "Pressure", 4: "DryAirColumn", 5: "H2O", 6: "HDO"

        ptf = pd.read_csv(self._get_pt_vmr_file(day, "pT"), header=0, skipinitialspace=True, \
            usecols=[0,1,2,3,4,5,6], names=['Index','Altitude','Tem','Pre','DAC','H2O','HDO'], \
            sep=' ', engine='python')

        return ptf


    def get_invparms_content(self, day):

       # The results of the PROFFAST evaluation are provided in the invparms output file.
       # Each invparms file contains among others the date and time, the pressure and temperature,
       # the coordinates of the EM27/SUN instrument, the solar zenith and azimuth angles,
       # and the trace gas concentrations for CO2, H2O, CH4, and CO.
       # "DateTime": 0, "JulianDate": 0, "HHMMSS_ID": 1, 
       # 3: "gndP", 4: "gndT", 5: "latdeg", 6: "londeg", 7: "altim", 8: "appSZA", 9: "azimuth", 
       # 10: "XH2O", 12: "XAIR", 14: "XCO2", 17: "XCH4", 20: "XCH4_S5P", 21: "XCO", 
       # 25: "H2O", 40: "O2", 67: "CO2", 97: "CH4", 127: "CO", 125: "CH4_S5P",
       # 23: "job01_rms", 63: "job03_rms", 90: "job04_rms", 119: "job05_rms"

        lines = []
        CO_avg = 0.0
        CO_lnr = 0.0

      # Get path and name of the invparms file for the corresponding day.

        path = self._find_colsens_invparms_file(day, "invparms") # which: "colsens", "invparms"

      # Check if the second CO channel exists.

        with open(path,'r') as file:
            header = file.readline().split('\t') # skip header line
            for line in file:
                line = re.sub(' +', ' ', line)
                line = line.split(' ')
              # line = line.split('\t')
                if line[21] == 'NaN': continue # incomplete line
                CO_avg += float(line[21])
                CO_lnr += 1.0

            CO_avg = CO_avg / CO_lnr

            file.close

      # Apply several quality checks on the data set (e.g. XAIR, SZA, XCO, etc.).

        with open(path,'r') as file:
            header = file.readline() # read header line
            header = re.sub(' +', ' ', header)
            header = header.split(' ')

            for line in file:
                line = re.sub(' +', ' ', line)
                line = line.split(' ')

                if float(line[8])  > self.input_args['QUALITY_FILTER_SZA']:      continue # data filter for SZA greater than 75 deg
                if float(line[12]) < self.input_args['QUALITY_FILTER_XAIR_MIN']: continue # data filter for XAIR smaller than 0.98
                if float(line[12]) > self.input_args['QUALITY_FILTER_XAIR_MAX']: continue # data filter for XAIR greater than 1.02

                if line[10] == 'NaN': continue # incomplete line XH2O
                if line[14] == 'NaN': continue # incomplete line XCO2
                if line[17] == 'NaN': continue # incomplete line XCH4
                if line[21] == 'NaN': continue # incomplete line XCO

                if float(line[10]) == 0.0: continue # data filter for XH2O equal zero
                if float(line[14]) == 0.0: continue # data filter for XCO2 equal zero
                if float(line[17]) == 0.0: continue # data filter for XCH4 equal zero
              # if float(line[21]) == 0.0: continue # data filter for XCO equal zero (instrument with second channel)
                if (CO_avg >  0.0) and (float(line[21]) == 0.0): continue               # data filter for XCO equal zero (instrument with second channel)
                if (CO_avg == 0.0) and (float(line[21]) == 0.0): line[21] = '-900000.0' # data filter for XCO equal zero (instrument without second channel, fill value -900000.0)

                lines.append(line)

            file.close

      # Extract the required information from the data set
      # and apply the correction factors

        head000 = [] # "JulianDate"
        head003 = [] # "gndP"
        head004 = [] # "gndT"
        head005 = [] # "latdeg"
        head006 = [] # "londeg"
        head007 = [] # "altim"
        head008 = [] # "appSZA"
        head009 = [] # "azimuth"
        head010 = [] # "XH2O"
        head012 = [] # "XAIR"
        head014 = [] # "XCO2"
        head017 = [] # "XCH4"
        head020 = [] # "XCH4_S5P"
        head021 = [] # "XCO"
        head025 = [] # "H2O"
        head040 = [] # "O2"
        head067 = [] # "CO2"
        head097 = [] # "CH4"
        head127 = [] # "CO"
        head125 = [] # "CH4_S5P"
        head023 = [] # "job01_rms"
        head063 = [] # "job03_rms"
        head090 = [] # "job04_rms"
        head119 = [] # "job05_rms"

      # Get the correction factors for XCO2, XCH4 (as well as XAIR, XH2O, XCO, if available).

        corr_fac = self._get_correction_factors()

        for i in range(len(lines)):
            head000.append(np.float64(lines[i][0]))   # "JulianDate"
            head003.append(np.float64(lines[i][3]))   # "gndP"
            head004.append(np.float64(lines[i][4]))   # "gndT"
            head005.append(np.float64(lines[i][5]))   # "latdeg"
            head006.append(np.float64(lines[i][6]))   # "londeg"
            head007.append(np.float64(lines[i][7]) / 1000.0)   # "altim"
            head008.append(np.float64(lines[i][8]))   # "appSZA"
            head009.append(np.float64(lines[i][9]))   # "azimuth"
            head010.append(np.float64(lines[i][10]))  # "XH2O"
            head012.append(np.float64(lines[i][12]))  # "XAIR"
          # head014.append(np.float64(lines[i][14]))  # "XCO2"
          # head017.append(np.float64(lines[i][17]))  # "XCH4"
            head014.append(np.float64(lines[i][14]) * corr_fac['XCO2_cal']) # "XCO2"
            head017.append(np.float64(lines[i][17]) * corr_fac['XCH4_cal']) # "XCH4"
            head020.append(np.float64(lines[i][20]))  # "XCH4_S5P"
            head021.append(np.float64(lines[i][21]))  # "XCO"
            head025.append(np.float64(lines[i][25]))  # "H2O"
            head040.append(np.float64(lines[i][40]))  # "O2"
            head067.append(np.float64(lines[i][67]))  # "CO2"
            head097.append(np.float64(lines[i][97]))  # "CH4"
            head127.append(np.float64(lines[i][127])) # "CO"
            head125.append(np.float64(lines[i][125])) # "CH4_S5P"
            head023.append(np.float64(lines[i][23]))  # "job01_rms"
            head063.append(np.float64(lines[i][63]))  # "job03_rms"
            head090.append(np.float64(lines[i][90]))  # "job04_rms"
            head119.append(np.float64(lines[i][119])) # "job05_rms"

        if head010[i] <= 0.0 or head010[i] >= 10000.0: head010[i] = -900000.0 # "XH2O"
      # if head012[i] <= 0.0 or head012[i] >= 2.0:     head012[i] = -900000.0 # "XAIR"
        if head014[i] <= 0.0 or head014[i] >= 10000.0: head014[i] = -900000.0 # "XCO2"
        if head017[i] <= 0.0 or head017[i] >= 10.0:    head017[i] = -900000.0 # "XCH4"
      # if head020[i] <= 0.0 or head020[i] >= 10.0:    head020[i] = -900000.0 # "XCH4_S5P"
        if head021[i] <= 0.0 or head021[i] >= 10000.0: head021[i] = -900000.0 # "XCO"

        data = { header[0]:   head000, header[3]:   head003, header[4]:   head004, \
                 header[5]:   head005, header[6]:   head006, header[7]:   head007, \
                 header[8]:   head008, header[9]:   head009, header[10]:  head010, \
                 header[12]:  head012, header[14]:  head014, header[17]:  head017, \
                 header[20]:  head020, header[21]:  head021, header[25]:  head025, \
                 header[40]:  head040, header[67]:  head067, header[97]:  head097, \
                 header[127]: head127, header[125]: head125, header[23]:  head023, \
                 header[63]:  head063, header[90]:  head090, header[119]: head119, \
               }

        df = pd.DataFrame(data)

      # At least 12 remaining measurements per measurement day are required
      # to calculate the uncertainty using the moving average.

        if (len(lines) < 12):
            print ('file_len: ', len(lines), ' (data filter applied)')
            return -1 # test file lenght
        else:
            print ('file_len: ', len(lines), ' (data filter applied)')
            return df


    def get_colsens_sza(self, day):

      # The column sensivity file (i.e. *colsens.dat") contains the vertical profile of the pressure and
      # the sensitivities for each species (these are H2O, HDO, CO2, CH4, N2O, CO, O2, HF) as function of the SZA.
      # alt [km], p [mbar], SZA [rad]:
      # 0.000E+00, 3.965E-01, 5.607E-01, 6.867E-01, 7.930E-01, 8.866E-01, 9.712E-01, 1.049E+00,
      # 1.121E+00, 1.189E+00, 1.254E+00, 1.315E+00, 1.373E+00, 1.430E+00, 1.484E+00

        sza = []
        alt = []
        pre = []
        sen = []

      # Get path and name for the column sensitivity file of a certain day.

        path = self._find_colsens_invparms_file(day, "colsens") # which: "colsens", "invparms"

      # Read pressure and sensitivities as function of the altitude and SZA.

        with open(path,'r') as file:

            for i in range(8): # H2O, HDO, CO2, CH4, N2O, CO, O2, HF
                sza.append([])
                alt.append([])
                pre.append([])
                sen.append([])

                for j in range(6): # 6 header lines for each species
                    header = file.readline() # skip header line
                    if j == 3: # read SZA [rad] values in the third line
                        header = re.sub(' +', '\t', header)
                        header = header.split('\t') # tab separator
                        sza[i] = np.array(header[3:])  # SZA header/columns
                        sza[i] = sza[i].astype(float)  # string to float

                for j in range(49): # number of altitude levels
                    line = file.readline()[1:-1]   # skip first empty space and carriage return character at the end
                    line = re.sub(' +', ',', line) # replace empty spaces by a comma
                    line = line.split(',')         # split line into columns

                    alt[i].append(line[0])         # altitude (first column)
                    pre[i].append(line[1])         # pressure (second column)

                    sen[i].append([])
                    for k in range(2,len(line)):   # SZA (third column upwards, total 15 columns)
                        sen[i][j].append(float(line[k]))

        file.close()

        sza = np.array(sza,dtype=float) # SZA [deg]
        alt = np.array(alt,dtype=float) # altitude [km]
        pre = np.array(pre,dtype=float) # pressure [mbar]
        sen = np.array(sen,dtype=float) # sensitivity

        return sza, alt, pre, sen


    def get_colsens_int(self, df, day):

      # Here, the interpolation of SZA is calculated to be consistent
      # with the a-priori altitude levels of the map-files.
      # Then, the gas sensitivities are calculated using the interpolated SZA values.

        sza, alt, pre, sen = self.get_colsens_sza(day)

        appSZA = df["appSZA"].to_numpy()

        gas_sens = []

        for k in range(8): # H2O, HDO, CO2, CH4, N2O, CO, O2, HF

            gas_sens.append([])

            for i in range(len(appSZA)): # number of measurements

                gas_sens[k].append([])

                SZA_app_rad = appSZA[i] * 2.0 * math.pi / 360.
                SZA_app_deg = appSZA[i]

                for j in range(len(sza[k])-1): # number SZA angels

                    SZA_sen_rad_1 = sza[k][j]
                    SZA_sen_deg_1 = sza[k][j] / 2.0 / math.pi * 360.
                    SZA_sen_rad_2 = sza[k][j+1]
                    SZA_sen_deg_2 = sza[k][j+1] / 2.0 / math.pi * 360.
                    SZA_dif_rad = SZA_sen_rad_2 - SZA_sen_rad_1
                    SZA_dif_deg = SZA_sen_deg_2 - SZA_sen_deg_1

                    if SZA_app_rad >= SZA_sen_rad_1 and SZA_app_rad <= SZA_sen_rad_2:

                        for h in range(len(alt[k])):
                            gas_1 = sen[k][h][j]
                            gas_2 = sen[k][h][j+1]
                            gas_dif = gas_2 - gas_1

                            m_rad = gas_dif/SZA_dif_rad
                            m_deg = gas_dif/SZA_dif_deg

                            b_gas = gas_1 - m_rad * SZA_sen_rad_1

                            gas_int = m_rad * SZA_app_rad + b_gas # gas interpolation
                            gas_sens[k][i].append(gas_int)

                    elif j == len(sza[k])-2 and SZA_app_rad > sza[k][len(sza)-1]:

                        for h in range(len(alt[k])):
                            gas_1 = sen[k][h][j]
                            gas_2 = sen[k][h][j+1]
                            gas_dif = gas_2 - gas_1

                            m_rad = gas_dif/SZA_dif_rad
                            m_deg = gas_dif/SZA_dif_deg

                            b_gas = gas_1 - m_rad * SZA_sen_rad_1

                            gas_int = m_rad * SZA_app_rad + b_gas # gas extrapolation
                            gas_sens[k][i].append(gas_int)
        return gas_sens


    def get_col_unc(self, df):

      # The error calculation (uncertainty) is performed
      # by using the column mixing ratios and dry air mole fraction.

        XH2O = df["XH2O"].to_numpy()
        XCO2 = df["XCO2"].to_numpy()
        XCH4 = df["XCH4"].to_numpy()
        XCO  = df["XCO"].to_numpy()

        AvgNr = 11           # number of moving mean values
        ErrNr = int(AvgNr/2) # number of moving mean values divided by two
        MeaNr = len(XH2O)    # number of measurements

      # Calculation of the moving mean for each species with 11 data points.

        XH2O_mean = np.zeros(df['JulianDate'].shape)
        XCO2_mean = np.zeros(df['JulianDate'].shape)
        XCH4_mean = np.zeros(df['JulianDate'].shape)
        XCO_mean  = np.zeros(df['JulianDate'].shape)

        for i in range(MeaNr-AvgNr+1): # moving mean calculation
            XH2O_mean_tmp = 0.0
            XCO2_mean_tmp = 0.0
            XCH4_mean_tmp = 0.0
            XCO_mean_tmp  = 0.0

            for j in range(AvgNr):
                XH2O_mean_tmp += XH2O[i+j]
                XCO2_mean_tmp += XCO2[i+j]
                XCH4_mean_tmp += XCH4[i+j]
                XCO_mean_tmp  += XCO[i+j]

            XH2O_mean[i+ErrNr] = XH2O_mean_tmp / float(AvgNr)
            XCO2_mean[i+ErrNr] = XCO2_mean_tmp / float(AvgNr)
            XCH4_mean[i+ErrNr] = XCH4_mean_tmp / float(AvgNr)
            XCO_mean[i+ErrNr]  = XCO_mean_tmp / float(AvgNr)

        for i in range(ErrNr): # first entries const
            XH2O_mean[i] = XH2O_mean[ErrNr]
            XCO2_mean[i] = XCO2_mean[ErrNr]
            XCH4_mean[i] = XCH4_mean[ErrNr]
            XCO_mean[i]  = XCO_mean[ErrNr]

        for i in range(ErrNr): # last entries const
            XH2O_mean[MeaNr-i-1] = XH2O_mean[MeaNr-ErrNr-1]
            XCO2_mean[MeaNr-i-1] = XCO2_mean[MeaNr-ErrNr-1]
            XCH4_mean[MeaNr-i-1] = XCH4_mean[MeaNr-ErrNr-1]
            XCO_mean[MeaNr-i-1]  = XCO_mean[MeaNr-ErrNr-1]

      # The error calculation is based on the difference between the column mixing ratios
      # and the the moving mean value for each trace gas.
      # Therefore, it corresponds to a standard deviation with respect to the moving mean.

        XH2O_err = np.zeros(MeaNr)
        XCO2_err = np.zeros(MeaNr)
        XCH4_err = np.zeros(MeaNr)
        XCO_err  = np.zeros(MeaNr)

        for i in range(MeaNr-AvgNr+1):
            XH2O_err_tmp = 0.0
            XCO2_err_tmp = 0.0
            XCH4_err_tmp = 0.0
            XCO_err_tmp  = 0.0

            for j in range(AvgNr):

                XH2O_err_tmp += np.power(XH2O[i+j] - XH2O_mean[i+j], 2)
                XCO2_err_tmp += np.power(XCO2[i+j] - XCO2_mean[i+j], 2)
                XCH4_err_tmp += np.power(XCH4[i+j] - XCH4_mean[i+j], 2)
                XCO_err_tmp  += np.power(XCO[i+j]  - XCO_mean[i+j], 2)

            XH2O_err[i+ErrNr] = np.sqrt(XH2O_err_tmp / float(AvgNr-1))
            XCO2_err[i+ErrNr] = np.sqrt(XCO2_err_tmp / float(AvgNr-1))
            XCH4_err[i+ErrNr] = np.sqrt(XCH4_err_tmp / float(AvgNr-1))
            XCO_err[i+ErrNr]  = np.sqrt(XCO_err_tmp / float(AvgNr-1)) * 1000.0

            if XH2O[i+ErrNr] == -900000.0: XH2O_err[i+ErrNr] = -900000.0
            if XCO2[i+ErrNr] == -900000.0: XCO2_err[i+ErrNr] = -900000.0
            if XCH4[i+ErrNr] == -900000.0: XCH4_err[i+ErrNr] = -900000.0
            if XCO[i+ErrNr]  == -900000.0: XCO_err[i+ErrNr]  = -900000.0

      # The uncertainty for the first and last entries is constant.

        for i in range(ErrNr):

            XH2O_err[i] = XH2O_err[ErrNr]
            XCO2_err[i] = XCO2_err[ErrNr]
            XCH4_err[i] = XCH4_err[ErrNr]
            XCO_err[i]  = XCO_err[ErrNr]

            if XH2O[i] == -900000.0: XH2O_err[i] = -900000.0
            if XCO2[i] == -900000.0: XCO2_err[i] = -900000.0
            if XCH4[i] == -900000.0: XCH4_err[i] = -900000.0
            if XCO[i]  == -900000.0: XCO_err[i]  = -900000.0

        for i in range(ErrNr):

            XH2O_err[MeaNr-i-1] = XH2O_err[MeaNr-ErrNr-1]
            XCO2_err[MeaNr-i-1] = XCO2_err[MeaNr-ErrNr-1]
            XCH4_err[MeaNr-i-1] = XCH4_err[MeaNr-ErrNr-1]
            XCO_err[MeaNr-i-1]  = XCO_err[MeaNr-ErrNr-1]

            if XH2O[MeaNr-i-1] == -900000.0: XH2O_err[MeaNr-i-1] = -900000.0
            if XCO2[MeaNr-i-1] == -900000.0: XCO2_err[MeaNr-i-1] = -900000.0
            if XCH4[MeaNr-i-1] == -900000.0: XCH4_err[MeaNr-i-1] = -900000.0
            if XCO[MeaNr-i-1]  == -900000.0: XCO_err[MeaNr-i-1]  = -900000.0

        return XH2O_err, XCO2_err, XCH4_err, XCO_err


    def write_source(self, cont): # "SRC_PRO": "SOURCE.PRODUCT"

      # Write information to the HDF5 file which is relevant to the source history.

        dataset_name = self.hdf5_vars[cont]
        self.variables.append(dataset_name)

        data = 'Some Information.'

        self.hdf5_atts_src["VAR_DATA_TYPE"] = "STRING"
        self.hdf5_atts_src["VAR_DEPEND"] = "INDEPENDENT"
        self.hdf5_atts_src["VAR_DESCRIPTION"] = \
            "Information relevant to the source history " \
            "of the Metadata and Data in the form " \
            "Original_Archive;Original_Filename;" \
            "Original_File_Generation_Date"
        self.hdf5_atts_src["VAR_NAME"] = dataset_name
      # self.hdf5_atts_src["VAR_NOTES"] = ""
        self.hdf5_atts_src["VAR_SIZE"] = "1"

        self.SRC_dtst = self._write_dataset_src(data, dataset_name, self.hdf5_atts_src)


    def write_datetime(self, df, cont): # "DAT_TIM": "DATETIME"

      # Write DateTime to the HDF5 file (MJD2K is 0.0 on January 1, 2000 at 00:00:00 UTC).

        dataset_name = self.hdf5_vars[cont]
        self.variables.append(dataset_name)

        data = df["JulianDate"].to_numpy()

        data = self._GEOMStoDateTime((data - 2451544.5) * 86400.0)
      # data = self._GEOMStoDateTime(np.round((data - 2451544.5) * 86400.0)) # ???
        data = self._DateTimeToGEOMS(data) / 86400.0

        self.hdf5_atts["VAR_DATA_TYPE"] = "DOUBLE"
        self.hdf5_atts["VAR_DEPEND"] = "DATETIME"
        self.hdf5_atts["VAR_DESCRIPTION"] = "MJD2K is 0.0 on January 1, 2000 at 00:00:00 UTC"
        self.hdf5_atts["VAR_FILL_VALUE"] = -900000.0
        self.hdf5_atts["VAR_NAME"] = dataset_name
      # self.hdf5_atts["VAR_NOTES"] = ""
        self.hdf5_atts["VAR_SIZE"] = str(np.size(data))
        self.hdf5_atts["VAR_SI_CONVERSION"] = "0.0;86400.0;s"
        self.hdf5_atts["VAR_UNITS"] = "MJD2K"
        self.hdf5_atts["VAR_VALID_MAX"] = np.amax(data)
        self.hdf5_atts["VAR_VALID_MIN"] = np.amin(data)
        self.hdf5_atts["_FillValue"] = -900000.0
        self.hdf5_atts["units"] = "MJD2K"
        self.hdf5_atts["valid_range"] = [np.amin(data),np.amax(data)]

        self.SRC_dtst = self._write_dataset_dt(data, dataset_name, self.hdf5_atts)


    def write_altitude(self, df, ptf, cont): # "ALT": "ALTITUDE"

      # Write altitude information used in the a-priori profile matrix.

        dataset_name = self.hdf5_vars[cont]
        self.variables.append(dataset_name)

        data = np.zeros(df['JulianDate'].shape+ptf['Altitude'].shape)

        for i in range(df['JulianDate'].shape[0]):
            for j in range(ptf['Altitude'].shape[0]):
                data[i][j] = ptf['Altitude'][j] / 1000.0 # in km

        self.hdf5_atts["VAR_DATA_TYPE"] = "REAL"
        self.hdf5_atts["VAR_DEPEND"] = "DATETIME;ALTITUDE"
        self.hdf5_atts["VAR_DESCRIPTION"] = \
            "A-priori altitude profile matrix. Values " \
            "are monotonically increasing"
        self.hdf5_atts["VAR_FILL_VALUE"] = -900000.0
        self.hdf5_atts["VAR_NAME"] = dataset_name
      # self.hdf5_atts["VAR_NOTES"] = ""
      # self.hdf5_atts["VAR_SIZE"] = str(np.size(data))
        self.hdf5_atts["VAR_SIZE"] = str(np.array(';'.join(map(str,list(data.shape)))))
        self.hdf5_atts["VAR_SI_CONVERSION"] = "0.0;1.0E3;m"
        self.hdf5_atts["VAR_UNITS"] = "km"
        self.hdf5_atts["VAR_VALID_MAX"] = np.amax(data)
        self.hdf5_atts["VAR_VALID_MIN"] = np.amin(data)
        self.hdf5_atts["_FillValue"] = -900000.0
        self.hdf5_atts["units"] = "km"
        self.hdf5_atts["valid_range"] = [np.amin(data),np.amax(data)]

        self.SRC_dtst = self._write_dataset(data, dataset_name, self.hdf5_atts)


    def write_solar_angle_zenith(self, df, cont): # "SOL_ZEN": "ANGLE.SOLAR_ZENITH.ASTRONOMICAL"

      # Write solar zenith angle to the HDF5 file (solar astronomical zenith angle).

        dataset_name = self.hdf5_vars[cont]
        self.variables.append(dataset_name)

        data = df["appSZA"].to_numpy()

        self.hdf5_atts["VAR_DATA_TYPE"] = "REAL"
        self.hdf5_atts["VAR_DEPEND"] = "DATETIME"
        self.hdf5_atts["VAR_DESCRIPTION"] = \
            "The solar astronomical zenith angle at which " \
            "the measurement was taken"
        self.hdf5_atts["VAR_FILL_VALUE"] = -900000.0
        self.hdf5_atts["VAR_NAME"] = dataset_name
      # self.hdf5_atts["VAR_NOTES"] = ""
        self.hdf5_atts["VAR_SIZE"] = str(np.size(data))
        self.hdf5_atts["VAR_SI_CONVERSION"] = "0.0;1.74533E-2;rad"
        self.hdf5_atts["VAR_UNITS"] = "deg"
        self.hdf5_atts["VAR_VALID_MAX"] = np.amax(data)
        self.hdf5_atts["VAR_VALID_MIN"] = np.amin(data)
        self.hdf5_atts["_FillValue"] = -900000.0
        self.hdf5_atts["units"] = "deg"
        self.hdf5_atts["valid_range"] = [np.amin(data),np.amax(data)]

        self.SRC_dtst = self._write_dataset(data, dataset_name, self.hdf5_atts)


    def write_solar_angle_azimuth(self, df, cont): # "SOL_AZI": "ANGLE.SOLAR_AZIMUTH"

      # Write solar azimuth angle to the HDF5 file.

        dataset_name = self.hdf5_vars[cont]
        self.variables.append(dataset_name)

        data = df["azimuth"].to_numpy() + 180.0

      # To avoid values lower than 0.0° or higher than 360.0° causing an error message
      # in the quality checks of the HDF5 files, a small numer is added or subtracted.

        for i in range(len(data)):
            if data[i] <= 0.0 + 1.E-5 or data[i] >= 360.0 - 1.E-5: data[i] = 0.0 + 1.E-5

        self.hdf5_atts["VAR_DATA_TYPE"] = "REAL"
        self.hdf5_atts["VAR_DEPEND"] = "DATETIME"
        self.hdf5_atts["VAR_DESCRIPTION"] = \
            "The azimuth viewing direction of the instrument " \
            "using north as the reference plane and increasing " \
            "clockwise (0 for north 90 for east and so on)"
        self.hdf5_atts["VAR_FILL_VALUE"] = -900000.0
        self.hdf5_atts["VAR_NAME"] = dataset_name
      # self.hdf5_atts["VAR_NOTES"] = ""
        self.hdf5_atts["VAR_SIZE"] = str(np.size(data))
        self.hdf5_atts["VAR_SI_CONVERSION"] = "0.0;1.74533E-2;rad"
        self.hdf5_atts["VAR_UNITS"] = "deg"
        self.hdf5_atts["VAR_VALID_MAX"] = np.amax(data)
        self.hdf5_atts["VAR_VALID_MIN"] = np.amin(data)
        self.hdf5_atts["_FillValue"] = -900000.0
        self.hdf5_atts["units"] = "deg"
        self.hdf5_atts["valid_range"] = [np.amin(data),np.amax(data)]

        self.SRC_dtst = self._write_dataset(data, dataset_name, self.hdf5_atts)


    def write_instr_latitude(self, df, cont): # "INST_LAT": "LATITUDE.INSTRUMENT"

      # Write the instrument's latitude to the HDF5 file (i.e. the geolocation with + for north and - for south).

        dataset_name = self.hdf5_vars[cont]
        self.variables.append(dataset_name)

        data = df["latdeg"].to_numpy()

        self.hdf5_atts["VAR_DATA_TYPE"] = "REAL"
        self.hdf5_atts["VAR_DEPEND"] = "DATETIME"
        self.hdf5_atts["VAR_DESCRIPTION"] = \
            "Instrument geolocation (+ for north; - for south)"
        self.hdf5_atts["VAR_FILL_VALUE"] = -900000.0
        self.hdf5_atts["VAR_NAME"] = dataset_name
      # self.hdf5_atts["VAR_NOTES"] = ""
        self.hdf5_atts["VAR_SIZE"] = str(np.size(data))
        self.hdf5_atts["VAR_SI_CONVERSION"] = "0.0;1.74533E-2;rad"
        self.hdf5_atts["VAR_UNITS"] = "deg"
        self.hdf5_atts["VAR_VALID_MAX"] = np.amax(data)
        self.hdf5_atts["VAR_VALID_MIN"] = np.amin(data)
        self.hdf5_atts["_FillValue"] = -900000.0
        self.hdf5_atts["units"] = "deg"
        self.hdf5_atts["valid_range"] = [np.amin(data),np.amax(data)]

        self.SRC_dtst = self._write_dataset(data, dataset_name, self.hdf5_atts)


    def write_instr_longitude(self, df, cont): # "INST_LON": "LONGITUDE.INSTRUMENT"

      # Write the instrument's longitude to the HDF5 file (i.e. the geolocation with + for east and - for west).

        dataset_name = self.hdf5_vars[cont]
        self.variables.append(dataset_name)

        data = df["londeg"].to_numpy()

        self.hdf5_atts["VAR_DATA_TYPE"] = "REAL"
        self.hdf5_atts["VAR_DEPEND"] = "DATETIME"
        self.hdf5_atts["VAR_DESCRIPTION"] = \
            "Instrument geolocation (+ for east; - for west)"
        self.hdf5_atts["VAR_FILL_VALUE"] = -900000.0
        self.hdf5_atts["VAR_NAME"] = dataset_name
      # self.hdf5_atts["VAR_NOTES"] = ""
        self.hdf5_atts["VAR_SIZE"] = str(np.size(data))
        self.hdf5_atts["VAR_SI_CONVERSION"] = "0.0;1.74533E-2;rad"
        self.hdf5_atts["VAR_UNITS"] = "deg"
        self.hdf5_atts["VAR_VALID_MAX"] = np.amax(data)
        self.hdf5_atts["VAR_VALID_MIN"] = np.amin(data)
        self.hdf5_atts["_FillValue"] = -900000.0
        self.hdf5_atts["units"] = "deg"
        self.hdf5_atts["valid_range"] = [np.amin(data),np.amax(data)]

        self.SRC_dtst = self._write_dataset(data, dataset_name, self.hdf5_atts)


    def write_instr_altitude(self, df, cont): # "INST_ALT": "ALTITUDE.INSTRUMENT"

      # Write the instrument's altitude to the HDF5 file (i.e. the geolocation).

        dataset_name = self.hdf5_vars[cont]
        self.variables.append(dataset_name)

        data = df["altim"].to_numpy()

        self.hdf5_atts["VAR_DATA_TYPE"] = "REAL"
        self.hdf5_atts["VAR_DEPEND"] = "DATETIME"
        self.hdf5_atts["VAR_DESCRIPTION"] = \
            "Instrument geolocation"
        self.hdf5_atts["VAR_FILL_VALUE"] = -900000.0
        self.hdf5_atts["VAR_NAME"] = dataset_name
      # self.hdf5_atts["VAR_NOTES"] = ""
        self.hdf5_atts["VAR_SIZE"] = str(np.size(data))
        self.hdf5_atts["VAR_SI_CONVERSION"] = "0.0;1.0E3;m"
        self.hdf5_atts["VAR_UNITS"] = "km"
        self.hdf5_atts["VAR_VALID_MAX"] = np.amax(data)
        self.hdf5_atts["VAR_VALID_MIN"] = np.amin(data)
        self.hdf5_atts["_FillValue"] = -900000.0
        self.hdf5_atts["units"] = "km"
        self.hdf5_atts["valid_range"] = [np.amin(data),np.amax(data)]

        self.SRC_dtst = self._write_dataset(data, dataset_name, self.hdf5_atts)


    def write_surface_pressure(self, df, cont): # "SUR_IND": "SURFACE.PRESSURE_INDEPENDENT"

      #  Write the surface pressure (i.e. the ground pressure) to the HDF5 file.

        dataset_name = self.hdf5_vars[cont]
        self.variables.append(dataset_name)
 
        data = df["gndP"].to_numpy()
 
        self.hdf5_atts["VAR_DATA_TYPE"] = "REAL"
        self.hdf5_atts["VAR_DEPEND"] = "DATETIME"
        self.hdf5_atts["VAR_DESCRIPTION"] = \
            "Surface/ground pressure"
        self.hdf5_atts["VAR_FILL_VALUE"] = -900000.0
        self.hdf5_atts["VAR_NAME"] = dataset_name
      # self.hdf5_atts["VAR_NOTES"] = ""
        self.hdf5_atts["VAR_SIZE"] = str(np.size(data))
        self.hdf5_atts["VAR_SI_CONVERSION"] = "0.0;1.0E2;kg m-1 s-2"
        self.hdf5_atts["VAR_UNITS"] = "hPa"
        self.hdf5_atts["VAR_VALID_MAX"] = np.amax(data)
        self.hdf5_atts["VAR_VALID_MIN"] = np.amin(data)
        self.hdf5_atts["_FillValue"] = -900000.0
        self.hdf5_atts["units"] = "hPa"
        self.hdf5_atts["valid_range"] = [np.amin(data),np.amax(data)]
 
        self.SRC_dtst = self._write_dataset(data, dataset_name, self.hdf5_atts)


    def write_surface_pressure_src(self, df, cont): # "SUR_SRC": "SURFACE.PRESSURE_INDEPENDENT_SOURCE"

      # Write the source of the surface pressure (i.e. the ground pressure) to the HDF5 file.

        dataset_name = self.hdf5_vars[cont]
        self.variables.append(dataset_name)
 
        data = df["londeg"].to_numpy()
        data_size = data.size
        data_src = [f"{self.input_args['PRESSURE_SOURCE']}"] * data_size
 
        self.hdf5_atts_src["VAR_DATA_TYPE"] = "STRING"
        self.hdf5_atts_src["VAR_DEPEND"] = "DATETIME"
        self.hdf5_atts_src["VAR_DESCRIPTION"] = \
            "Surface pressure profile source (e.g. Mercury barometer etc.)"
        self.hdf5_atts_src["VAR_NAME"] = dataset_name
      # self.hdf5_atts_src["VAR_NOTES"] = ""
        self.hdf5_atts_src["VAR_SIZE"] = str(np.size(data))
 
        self.SRC_dtst = self._write_dataset_src(data_src, dataset_name, self.hdf5_atts_src)


    def write_pressure(self, df, ptf, cont): # "PRE_IND": "PRESSURE_INDEPENDENT"

      # Write the effective air pressure at each altitude level to the HDF5 file.

        dataset_name = self.hdf5_vars[cont]
        self.variables.append(dataset_name)

        data = np.zeros(df['JulianDate'].shape+ptf['Altitude'].shape)

        for i in range(df['JulianDate'].shape[0]):
            for j in range(ptf['Altitude'].shape[0]):
                data[i][j] = ptf['Pre'][j] / 100.0 # hPa

        self.hdf5_atts["VAR_DATA_TYPE"] = "REAL"
        self.hdf5_atts["VAR_DEPEND"] = "DATETIME;ALTITUDE"
        self.hdf5_atts["VAR_DESCRIPTION"] = \
            "Effective air pressure at each altitude"
        self.hdf5_atts["VAR_FILL_VALUE"] = -900000.0
        self.hdf5_atts["VAR_NAME"] = dataset_name
      # self.hdf5_atts["VAR_NOTES"] = ""
      # self.hdf5_atts["VAR_SIZE"] = str(np.size(data))
        self.hdf5_atts["VAR_SIZE"] = str(np.array(';'.join(map(str,list(data.shape)))))
        self.hdf5_atts["VAR_SI_CONVERSION"] = "0.0;1.0E2;kg m-1 s-2"
        self.hdf5_atts["VAR_UNITS"] = "hPa"
        self.hdf5_atts["VAR_VALID_MAX"] = np.amax(data)
        self.hdf5_atts["VAR_VALID_MIN"] = np.amin(data)
        self.hdf5_atts["_FillValue"] = -900000.0
        self.hdf5_atts["units"] = "hPa"
        self.hdf5_atts["valid_range"] = [np.amin(data),np.amax(data)]

        self.SRC_dtst = self._write_dataset(data, dataset_name, self.hdf5_atts)


    def write_pressure_src(self, df, cont): # "PRE_SRC": "PRESSURE_INDEPENDENT_SOURCE"

      # Write the source of the effective air pressure for each altitude to the HDf5 file.

        dataset_name = self.hdf5_vars[cont]
        self.variables.append(dataset_name)

        data_src = []

        for i in range(df['JulianDate'].shape[0]):
            data_src.append("Pressure profile from NCEP at local noon")

        self.hdf5_atts_src["VAR_DATA_TYPE"] = "STRING"
        self.hdf5_atts_src["VAR_DEPEND"] = "DATETIME"
        self.hdf5_atts_src["VAR_DESCRIPTION"] = \
            "Pressure profile source (hydrostatic)"
        self.hdf5_atts_src["VAR_NAME"] = dataset_name
      # self.hdf5_atts_src["VAR_NOTES"] = ""
        self.hdf5_atts_src["VAR_SIZE"] = str(np.size(data_src))

        self.SRC_dtst = self._write_dataset_src(data_src, dataset_name, self.hdf5_atts_src)


    def write_temperature(self, df, ptf, cont): # "TEM_IND": "TEMPERATURE_INDEPENDENT"

      # Write the effective air temperature at each altitude to the HDF5 file.

        dataset_name = self.hdf5_vars[cont]
        self.variables.append(dataset_name)

        data = np.zeros(df['JulianDate'].shape+ptf['Altitude'].shape)

        for i in range(df['JulianDate'].shape[0]):
            for j in range(ptf['Altitude'].shape[0]):
                data[i][j] = ptf['Tem'][j]

        self.hdf5_atts["VAR_DATA_TYPE"] = "REAL"
        self.hdf5_atts["VAR_DEPEND"] = "DATETIME;ALTITUDE"
        self.hdf5_atts["VAR_DESCRIPTION"] = \
            "Effective air temperature at each altitude"
        self.hdf5_atts["VAR_FILL_VALUE"] = -900000.0
        self.hdf5_atts["VAR_NAME"] = dataset_name
      # self.hdf5_atts["VAR_NOTES"] = ""
      # self.hdf5_atts["VAR_SIZE"] = str(np.size(data))
        self.hdf5_atts["VAR_SIZE"] = str(np.array(';'.join(map(str,list(data.shape)))))
        self.hdf5_atts["VAR_SI_CONVERSION"] = "0.0;1.0;K"
        self.hdf5_atts["VAR_UNITS"] = "K"
        self.hdf5_atts["VAR_VALID_MAX"] = np.amax(data)
        self.hdf5_atts["VAR_VALID_MIN"] = np.amin(data)
        self.hdf5_atts["_FillValue"] = -900000.0
        self.hdf5_atts["units"] = "K"
        self.hdf5_atts["valid_range"] = [np.amin(data),np.amax(data)]

        self.SRC_dtst = self._write_dataset(data, dataset_name, self.hdf5_atts)


    def write_temperature_src(self, df, cont): # "TEM_SRC": "TEMPERATURE_INDEPENDENT_SOURCE"

      # Write the source of the effective air pressure for each altitude to the HDF5 file.

        dataset_name = self.hdf5_vars[cont]
        self.variables.append(dataset_name)

        data_src = []

        for i in range(df['JulianDate'].shape[0]):
            data_src.append("Temperature profile from NCEP at local noon")

        self.hdf5_atts_src["VAR_DATA_TYPE"] = "STRING"
        self.hdf5_atts_src["VAR_DEPEND"] = "DATETIME"
        self.hdf5_atts_src["VAR_DESCRIPTION"] = \
            "Temperature profile source (e.g. Lidar NCEP Sonde ECMWF etc.)"
        self.hdf5_atts_src["VAR_NAME"] = dataset_name
      # self.hdf5_atts_src["VAR_NOTES"] = ""
        self.hdf5_atts_src["VAR_SIZE"] = str(np.size(data_src))

        self.SRC_dtst = self._write_dataset_src(data_src, dataset_name, self.hdf5_atts_src)


    def write_col(self, df, cont): # "XXX_COL": "XXX.COLUMN.MIXING.RATIO.VOLUME.DRY_ABSORPTION.SOLAR"

      # Write column average dry air mole fractions for each trace gas to HDF5 file.

        dataset_name = self.hdf5_vars[cont]
        self.variables.append(dataset_name)
        print (cont, dataset_name)

      # Convert data to numpy array.
        if cont == "H2O_COL":   # "H2O_COL": "H2O.COLUMN.MIXING.RATIO.VOLUME.DRY_ABSORPTION.SOLAR"
            data = df["XH2O"].to_numpy()
            self.hdf5_atts["VAR_SI_CONVERSION"] = "0.0;1.0E-6;1"
            self.hdf5_atts["VAR_UNITS"] = "ppmv"
            self.hdf5_atts["units"] = "ppmv"
        elif cont == "CO2_COL": # "CO2_COL": "CO2.COLUMN.MIXING.RATIO.VOLUME.DRY_ABSORPTION.SOLAR"
            data = df["XCO2"].to_numpy()
            self.hdf5_atts["VAR_SI_CONVERSION"] = "0.0;1.0E-6;1"
            self.hdf5_atts["VAR_UNITS"] = "ppmv"
            self.hdf5_atts["units"] = "ppmv"
        elif cont == "CH4_COL": # "CH4_COL": "CH4.COLUMN.MIXING.RATIO.VOLUME.DRY_ABSORPTION.SOLAR"
            data = df["XCH4"].to_numpy()
            self.hdf5_atts["VAR_SI_CONVERSION"] = "0.0;1.0E-6;1"
            self.hdf5_atts["VAR_UNITS"] = "ppmv"
            self.hdf5_atts["units"] = "ppmv"
        elif cont == "CO_COL":  # "CO_COL":  "CO.COLUMN.MIXING.RATIO.VOLUME.DRY_ABSORPTION.SOLAR"
            data = df["XCO"].to_numpy() * 1000.0 # in ppbv
            self.hdf5_atts["VAR_SI_CONVERSION"] = "0.0;1.0E-9;1"
            self.hdf5_atts["VAR_UNITS"] = "ppbv"
            self.hdf5_atts["units"] = "ppbv"

        self.hdf5_atts["VAR_DATA_TYPE"] = "REAL"
        self.hdf5_atts["VAR_DEPEND"] = "DATETIME"
        self.hdf5_atts["VAR_DESCRIPTION"] = "Column average dry air mole fraction"
        self.hdf5_atts["VAR_FILL_VALUE"] = -900000.0
        self.hdf5_atts["VAR_NAME"] = dataset_name
      # self.hdf5_atts["VAR_NOTES"] = ""
        self.hdf5_atts["VAR_SIZE"] = str(np.size(data))
      # self.hdf5_atts["VAR_SI_CONVERSION"] = "0.0;1.0E-6;1"
        self.hdf5_atts["VAR_VALID_MAX"] = np.amax(data)
        self.hdf5_atts["VAR_VALID_MIN"] = np.amin(data)
        self.hdf5_atts["_FillValue"] = -900000.0
        self.hdf5_atts["valid_range"] = [np.amin(data),np.amax(data)]

        self.SRC_dtst = self._write_dataset(data, dataset_name, self.hdf5_atts)


    def write_col_unc(self, df, cont): # "XXX_UNC": "XXX.COLUMN.MIXING.RATIO.VOLUME.DRY_ABSORPTION.SOLAR_UNCERTAINTY.RANDOM.STANDARD"

      # Write uncertainty on the retrieved total column for each trace gas to HDF5 file.

        dataset_name = self.hdf5_vars[cont]
        self.variables.append(dataset_name)

        data = np.zeros(df['JulianDate'].shape)

        h2o_unc, co2_unc, ch4_unc, co_unc = self.get_col_unc(df)

        if cont == "H2O_UNC":   # "H2O_UNC": "H2O.COLUMN.MIXING.RATIO.VOLUME.DRY_ABSORPTION.SOLAR_UNCERTAINTY.RANDOM.STANDARD"
            data = h2o_unc # uncertainty for H2O
            self.hdf5_atts["VAR_SI_CONVERSION"] = "0.0;1.0E-6;1"
            self.hdf5_atts["VAR_UNITS"] = "ppmv"
            self.hdf5_atts["units"] = "ppmv"
        elif cont == "CO2_UNC": # "CO2_UNC": "CO2.COLUMN.MIXING.RATIO.VOLUME.DRY_ABSORPTION.SOLAR_UNCERTAINTY.RANDOM.STANDARD"
            data = co2_unc # uncertainty for CO2
            self.hdf5_atts["VAR_SI_CONVERSION"] = "0.0;1.0E-6;1"
            self.hdf5_atts["VAR_UNITS"] = "ppmv"
            self.hdf5_atts["units"] = "ppmv"
        elif cont == "CH4_UNC": # "CH4_UNC": "CH4.COLUMN.MIXING.RATIO.VOLUME.DRY_ABSORPTION.SOLAR_UNCERTAINTY.RANDOM.STANDARD"
            data = ch4_unc # uncertainty for CH4
            self.hdf5_atts["VAR_SI_CONVERSION"] = "0.0;1.0E-6;1"
            self.hdf5_atts["VAR_UNITS"] = "ppmv"
            self.hdf5_atts["units"] = "ppmv"
        elif cont == "CO_UNC":  # "CO_UNC":  "CO.COLUMN.MIXING.RATIO.VOLUME.DRY_ABSORPTION.SOLAR_UNCERTAINTY.RANDOM.STANDARD"
            data = co_unc # uncertainty for CO
            self.hdf5_atts["VAR_SI_CONVERSION"] = "0.0;1.0E-9;1"
            self.hdf5_atts["VAR_UNITS"] = "ppbv"
            self.hdf5_atts["units"] = "ppbv"

        self.hdf5_atts["VAR_DATA_TYPE"] = "REAL"
        self.hdf5_atts["VAR_DEPEND"] = "DATETIME"
        self.hdf5_atts["VAR_DESCRIPTION"] = \
            "Total random uncertainty on the retrieved total column \
            (expressed in same units as the column)"
        self.hdf5_atts["VAR_FILL_VALUE"] = -900000.0
        self.hdf5_atts["VAR_NAME"] = dataset_name
      # self.hdf5_atts["VAR_NOTES"] = ""
        self.hdf5_atts["VAR_SIZE"] = str(np.size(data))
      # self.hdf5_atts["VAR_SIZE"] = str(np.array(';'.join(map(str,list(data.shape)))))
        self.hdf5_atts["VAR_VALID_MAX"] = np.amax(data)
        self.hdf5_atts["VAR_VALID_MIN"] = np.amin(data)
        self.hdf5_atts["_FillValue"] = -900000.0
        self.hdf5_atts["valid_range"] = [np.amin(data),np.amax(data)]

        self.SRC_dtst = self._write_dataset(data, dataset_name, self.hdf5_atts)


    def write_apr(self, df, ptf, vmr, cont): # "XXX_APR": "XXX.MIXING.RATIO.VOLUME.DRY_APRIORI"

      # Write a-prior total vertical column for each trace gas to the HDF5 file.

        dataset_name = self.hdf5_vars[cont]
        self.variables.append(dataset_name)

        data = np.zeros(df['JulianDate'].shape+ptf['Altitude'].shape)

        if cont == "H2O_APR": # "H2O_APR": "H2O.MIXING.RATIO.VOLUME.DRY_APRIORI"
            H2O_prior = ptf["H2O"] # VMR prior for H2O
            for i in range(df['JulianDate'].shape[0]):
                for j in range(ptf['Altitude'].shape[0]):
                    data[i][j] = H2O_prior[j] # in ppm
            self.hdf5_atts["VAR_SI_CONVERSION"] = "0.0;1.0E-6;1"
            self.hdf5_atts["VAR_UNITS"] = "ppmv"
            self.hdf5_atts["units"] = "ppmv"
        elif cont == "CO2_APR": # "CO2_APR": "CO2.MIXING.RATIO.VOLUME.DRY_APRIORI"
            CO2_prior = vmr["CO2"] # VMR prior for CO2
            for i in range(df['JulianDate'].shape[0]):
                for j in range(ptf['Altitude'].shape[0]):
                    data[i][j] = CO2_prior[j] # in ppm
            self.hdf5_atts["VAR_SI_CONVERSION"] = "0.0;1.0E-6;1"
            self.hdf5_atts["VAR_UNITS"] = "ppmv"
            self.hdf5_atts["units"] = "ppmv"
        elif cont == "CH4_APR": # "CH4_APR": "CH4.MIXING.RATIO.VOLUME.DRY_APRIOR"
            CH4_prior = vmr["CH4"] * 1000.0 # VMR prior for CH4
            for i in range(df['JulianDate'].shape[0]):
                for j in range(ptf['Altitude'].shape[0]):
                    data[i][j] = CH4_prior[j] # in ppb
            self.hdf5_atts["VAR_SI_CONVERSION"] = "0.0;1.0E-9;1"
            self.hdf5_atts["VAR_UNITS"] = "ppbv"
            self.hdf5_atts["units"] = "ppbv"
        elif cont == "CO_APR": # "CO_APR": "CO.MIXING.RATIO.VOLUME.DRY_APRIORI"
            CO_prior = vmr["CO"] * 1000.0 # VMR prior for CO
            for i in range(df['JulianDate'].shape[0]):
                for j in range(ptf['Altitude'].shape[0]):
                    data[i][j] = CO_prior[j] # in ppb
            self.hdf5_atts["VAR_SI_CONVERSION"] = "0.0;1.0E-9;1"
            self.hdf5_atts["VAR_UNITS"] = "ppbv"
            self.hdf5_atts["units"] = "ppbv"

        self.hdf5_atts["VAR_DATA_TYPE"] = "REAL"
        self.hdf5_atts["VAR_DEPEND"] = "DATETIME;ALTITUDE"
        self.hdf5_atts["VAR_DESCRIPTION"] = \
            "A-priori total vertical column of target gas"
        self.hdf5_atts["VAR_FILL_VALUE"] = -900000.0
        self.hdf5_atts["VAR_NAME"] = dataset_name
      # self.hdf5_atts["VAR_NOTES"] = ""
      # self.hdf5_atts["VAR_SIZE"] = str(np.size(data))
        self.hdf5_atts["VAR_SIZE"] = str(np.array(';'.join(map(str,list(data.shape)))))
        self.hdf5_atts["VAR_VALID_MAX"] = np.amax(data)
        self.hdf5_atts["VAR_VALID_MIN"] = np.amin(data)
        self.hdf5_atts["_FillValue"] = -900000.0
        self.hdf5_atts["valid_range"] = [np.amin(data),np.amax(data)]

        self.SRC_dtst = self._write_dataset(data, dataset_name, self.hdf5_atts)


    def write_apr_src(self, df, cont): # "XXX_SRC": "XXX.MIXING.RATIO.VOLUME.DRY_APRIORI.SOURCE"

      # Write source of the a-prior total vertical column for each trace gas to the HDF5 file.

        dataset_name = self.hdf5_vars[cont]
        self.variables.append(dataset_name)

        data_src = []

        for i in range(df['JulianDate'].shape[0]):
            if cont == "H2O_SRC":   # "H2O_SRC": "H2O.MIXING.RATIO.VOLUME.DRY_APRIORI.SOURCE"
                data_src.append("Total vertical column of H2O from NCEP at local noon")
            elif cont == "CO2_SRC": # "CO2_SRC": "CO2.MIXING.RATIO.VOLUME.DRY_APRIORI.SOURCE"
                data_src.append("Map file GFIT Code")
            elif cont == "CH4_SRC": # "CH4_SRC": "CH4.MIXING.RATIO.VOLUME.DRY_APRIORI.SOURCE"
                data_src.append("Map file GFIT Code")
            elif cont == "CO_SRC":  # "CO_SRC":  "CO.MIXING.RATIO.VOLUME.DRY_APRIORI.SOURCE"
                data_src.append("Map file GFIT Code")

        self.hdf5_atts_src["VAR_DATA_TYPE"] = "STRING"
        self.hdf5_atts_src["VAR_DEPEND"] = "DATETIME"
        self.hdf5_atts_src["VAR_DESCRIPTION"] = \
            "Source of the vertical profile of a-priori per layer"
        self.hdf5_atts_src["VAR_NAME"] = dataset_name
      # self.hdf5_atts_src["VAR_NOTES"] = ""
        self.hdf5_atts_src["VAR_SIZE"] = str(np.size(data_src))

        self.SRC_dtst = self._write_dataset_src(data_src, dataset_name, self.hdf5_atts_src)


    def write_avk(self, df, ptf, sen, cont): # "XXX_AVK": "XXX.COLUMN_ABSORPTION.SOLAR_AVK"

      # Write column sensitivities assosiated with the total vertical column
      # for each trace gas to the HDF5 file.

        dataset_name = self.hdf5_vars[cont]
        self.variables.append(dataset_name)

        data = np.zeros(df['JulianDate'].shape+ptf['Altitude'].shape)

        if cont == "H2O_AVK": # "H2O_APR": "H2O.MIXING.RATIO.VOLUME.DRY_APRIORI"
            for i in range(df['JulianDate'].shape[0]):
                for j in range(ptf['Altitude'].shape[0]):
                    data[i][j] = sen[0][i][j] # 0: "CO2_int"
        elif cont == "CO2_AVK": # "CO2_APR": "CO2.MIXING.RATIO.VOLUME.DRY_APRIORI"
            for i in range(df['JulianDate'].shape[0]):
                for j in range(ptf['Altitude'].shape[0]):
                    data[i][j] = sen[2][i][j] # 1: "CH4_int"
        elif cont == "CH4_AVK": # "CH4_APR": "CH4.MIXING.RATIO.VOLUME.DRY_APRIOR"
            for i in range(df['JulianDate'].shape[0]):
                for j in range(ptf['Altitude'].shape[0]):
                    data[i][j] = sen[3][i][j] # 2: "CO_int"
        elif cont == "CO_AVK": # "CO_APR": "CO.MIXING.RATIO.VOLUME.DRY_APRIORI"
            for i in range(df['JulianDate'].shape[0]):
                for j in range(ptf['Altitude'].shape[0]):
                    data[i][j] = sen[5][i][j] # 3: "H2O_int"

        self.hdf5_atts["VAR_DATA_TYPE"] = "REAL"
        self.hdf5_atts["VAR_DEPEND"] = "DATETIME;ALTITUDE"
        self.hdf5_atts["VAR_DESCRIPTION"] = \
            "Column sensitivity associated with the total vertical column of the target gas"
        self.hdf5_atts["VAR_FILL_VALUE"] = -900000.0
        self.hdf5_atts["VAR_NAME"] = dataset_name
      # self.hdf5_atts["VAR_NOTES"] = ""
      # self.hdf5_atts["VAR_SIZE"] = str(np.size(data))
        self.hdf5_atts["VAR_SIZE"] = str(np.array(';'.join(map(str,list(data.shape)))))
        self.hdf5_atts["VAR_SI_CONVERSION"] = "0.0;1.0;1"
        self.hdf5_atts["VAR_UNITS"] = "1"
        self.hdf5_atts["VAR_VALID_MAX"] = np.amax(data)
        self.hdf5_atts["VAR_VALID_MIN"] = np.amin(data)
        self.hdf5_atts["_FillValue"] = -900000.0
        self.hdf5_atts["units"] = "1"
        self.hdf5_atts["valid_range"] = [np.amin(data),np.amax(data)]

        self.SRC_dtst = self._write_dataset(data, dataset_name, self.hdf5_atts)


    def write_air_partial(self, df, ptf, cont): # "AIR_COL": "DRY.AIR.COLUMN.PARTIAL_INDEPENDENT"

      # Write vertical profile of partial columns of air number densities
      # (for conversion between VMR and partial column profile).
      # 0: "Index", 1: "Altitude", 2: "Tem", 3: "Pre", 4: "DAC", 5: "H2O", 6: "HDO"
      # 0: "Index", 1: "Altitude", 2: "Temperature", 3: "Pressure", 4: "Column", 5: "H2O", 6: "HDO"

        dataset_name = self.hdf5_vars[cont]
        self.variables.append(dataset_name)

        data = np.zeros(df['JulianDate'].shape+ptf['Altitude'].shape)

        k_B = 1.3807e-23 # 1.380649E-23 # k_boltz = 1.3807e-23

        T_prior   = ptf["Tem"]
        P_prior   = ptf["Pre"] / 100.0 # conversion Pa to hPa
        H2O_prior = ptf["H2O"] # / 10000.0 ???

        p_dry = P_prior * 1.0 / (1.0 + 1.0E-6 * H2O_prior) # / 100.0 for conversion Pa to hPa
        n_dry = p_dry / (k_B * T_prior)

      # Calcualtion of the vertical profile, i.e. the partial columns of air number densities.
      # Each layer is obtained by an integration between two boundary layers.

        for i in range(df['JulianDate'].shape[0]):
            sum1 = 0.0
            sum2 = 0.0

            for j in range(ptf['Altitude'].shape[0]):
                if j < len(ptf['Altitude'])-1:

                    h1 = float(ptf['Altitude'][j]) # * 1000.0 for conversion km to m
                    h2 = float(ptf['Altitude'][j+1]) # * 1000.0 for conversion km to m

                    n1_dry = float(n_dry[j])
                    n2_dry = float(n_dry[j+1])
                    sc_dry = (h2-h1) / math.log(n1_dry/n2_dry)
                    n0_dry = n1_dry * math.exp(h1/sc_dry)

                    Col1 = n0_dry * sc_dry * math.exp(-(h1/sc_dry))
                    Col2 = n0_dry * sc_dry * math.exp(-(h2/sc_dry))

                    data[i][j] = 100.0 * (Col1 - Col2)
                  # data[i][H_len-j] = 100.0 * (Col1 - Col2)

                    sum1 += data[i][j]
                  # sum1 += data[i][H_len-j]
                    sum2 += float(ptf['DAC'][j])

                else:
                    data[i][j] = 0
                  # data[i][H_len-j] = 0
                    sum1 += data[i][j]
                  # sum1 += data[i][H_len-j]
                    sum2 += float(ptf['DAC'][j])

        data = data / 1.0E25

        self.hdf5_atts["VAR_DATA_TYPE"] = "REAL"
        self.hdf5_atts["VAR_DEPEND"] = "DATETIME;ALTITUDE"
        self.hdf5_atts["VAR_DESCRIPTION"] = \
            "Vertical profile of partial columns of air number densities \
            (for conversion between VMR and partial column profile)"
        self.hdf5_atts["VAR_FILL_VALUE"] = -900000.0
        self.hdf5_atts["VAR_NAME"] = dataset_name
      # self.hdf5_atts["VAR_NOTES"] = ""
      # self.hdf5_atts["VAR_SIZE"] = str(np.size(data))
        self.hdf5_atts["VAR_SIZE"] = str(np.array(';'.join(map(str,list(data.shape)))))
        self.hdf5_atts["VAR_SI_CONVERSION"] = "0.0;1.66054E1;mol m-2"
        self.hdf5_atts["VAR_UNITS"] = "Zmolec cm-2"
        self.hdf5_atts["VAR_VALID_MAX"] = np.amax(data)
        self.hdf5_atts["VAR_VALID_MIN"] = np.amin(data)
        self.hdf5_atts["_FillValue"] = -900000.0
        self.hdf5_atts["units"] = "Zmolec cm-2"
        self.hdf5_atts["valid_range"] = [np.amin(data),np.amax(data)]

        self.SRC_dtst = self._write_dataset(data, dataset_name, self.hdf5_atts)


    def write_air_density(self, df, ptf, cont): # "AIR_DEN": "DRY.AIR.NUMBER.DENSITY_INDEPENDENT"

      # Write the dry air number density profile to the HDF5 file.
      # 0: "Index", 1: "Altitude", 2: "Tem", 3: "Pre", 4: "DAC", 5: "H2O", 6: "HDO"
      # 0: "Index", 1: "Altitude", 2: "Temperature", 3: "Pressure", 4: "Column", 5: "H2O", 6: "HDO"

        dataset_name = self.hdf5_vars[cont]
        self.variables.append(dataset_name)

        data = np.zeros(df['JulianDate'].shape+ptf['Altitude'].shape)

        k_B = 1.3807e-23 # 1.380649E-23 # k_boltz = 1.3807e-23

        T_prior   = ptf["Tem"]
        P_prior   = ptf["Pre"] / 100.0 # conversion to hPa
        H2O_prior = ptf["H2O"] # / 10000.0 ???

      # Calculation of the dry air number density profile.

        p_dry = P_prior * 1.0 / (1.0 + 1.0E-6 * H2O_prior) # / 100.0 for conversion Pa to hPa
        n_dry = p_dry / (k_B * T_prior)

        for i in range(df['JulianDate'].shape[0]):
            for j in range(ptf['Altitude'].shape[0]):
                data[i][j] = n_dry[j]

        self.hdf5_atts["VAR_DATA_TYPE"] = "REAL"
        self.hdf5_atts["VAR_DEPEND"] = "DATETIME;ALTITUDE"
        self.hdf5_atts["VAR_DESCRIPTION"] = \
            "Dry air number density profile"
        self.hdf5_atts["VAR_FILL_VALUE"] = -900000.0
        self.hdf5_atts["VAR_NAME"] = dataset_name
      # self.hdf5_atts["VAR_NOTES"] = ""
      # self.hdf5_atts["VAR_SIZE"] = str(np.size(data))
        self.hdf5_atts["VAR_SIZE"] = str(np.array(';'.join(map(str,list(data.shape)))))
        self.hdf5_atts["VAR_SI_CONVERSION"] = "0.0;1.66054E-18;mol m-3"
        self.hdf5_atts["VAR_UNITS"] = "molec cm-3"
        self.hdf5_atts["VAR_VALID_MAX"] = np.amax(data)
        self.hdf5_atts["VAR_VALID_MIN"] = np.amin(data)
        self.hdf5_atts["_FillValue"] = -900000.0
        self.hdf5_atts["units"] = "molec cm-3"
        self.hdf5_atts["valid_range"] = [np.amin(data),np.amax(data)]

        self.SRC_dtst = self._write_dataset(data, dataset_name, self.hdf5_atts)


    def write_air_density_src(self, df, cont): # "AIR_SRC": "DRY.AIR.NUMBER.DENSITY_INDEPENDENT_SOURCE"

      # Write source of the dry air number density profile (hydrostatic) to the HDF5 file.

        dataset_name = self.hdf5_vars[cont]
        self.variables.append(dataset_name)

        data_src = []

        for i in range(df['JulianDate'].shape[0]):
            data_src.append("Dry air number density profile from NCEP at local noon")

        self.hdf5_atts_src["VAR_DATA_TYPE"] = "STRING"
        self.hdf5_atts_src["VAR_DEPEND"] = "DATETIME"
        self.hdf5_atts_src["VAR_DESCRIPTION"] = \
            "Dry air number density profile source (hydrostatic)"
        self.hdf5_atts_src["VAR_NAME"] = dataset_name
      # self.hdf5_atts_src["VAR_NOTES"] = ""
        self.hdf5_atts_src["VAR_SIZE"] = str(np.size(data_src))

        self.SRC_dtst = self._write_dataset_src(data_src, dataset_name, self.hdf5_atts_src)


    def write_metadata(self, day, df):

        """ Write metadata to the GEOMS file! """

      # Attribut list, which contains the variables given in the input files.

        attribute_list =\
            ["DATA_FILE_VERSION", "DATA_LOCATION", "DATA_PROCESSOR",
             "DATA_QUALITY", "DATA_SOURCE", "DATA_TEMPLATE",
             "FILE_DOI", "FILE_META_VERSION",
             "PI_NAME", "PI_EMAIL", "PI_AFFILIATION", "PI_ADDRESS",
             "DO_NAME", "DO_EMAIL", "DO_AFFILIATION", "DO_ADDRESS",
             "DS_NAME", "DS_EMAIL", "DS_AFFILIATION", "DS_ADDRESS"]

        for attr in attribute_list:
          # H5Py needs to store the strings using this numpy method:
          # see: https://docs.h5py.org/en/2.3/strings.html
          # Furhtermore they have to be in edged brackets to provide an array.
            self.MyHDF5.attrs[attr] = np.string_(self.input_args[attr])

        self.MyHDF5.attrs['DATA_DESCRIPTION'] = \
            np.string_(f"EM27/SUN ({self.instrument_number}) measurements"
                     f" from {self.site_name}.")

        self.MyHDF5.attrs['DATA_DISCIPLINE'] = \
             np.string_(f"ATMOSPHERIC.CHEMISTRY;REMOTE.SENSING;GROUNDBASED")

        self.MyHDF5.attrs['DATA_GROUP'] = \
             np.string_(f"EXPERIMENTAL;PROFILE.STATIONARY")

      # Get the ILS values from the ILSList.csv file.

        ME1, PE1, ME2, PE2 = self.get_ils_from_file(day)

      # Get the correction factors from the Calibration_Parameters.csv file.

        corr_fac = self._get_correction_factors()

        self.MyHDF5.attrs['DATA_MODIFICATIONS'] = \
            np.string_("ILS parms applied: "
                     f"{ME1} for ME, {PE1} for PE. "
                     "Calibration factors applied:: "
                     f"{corr_fac['XCO2_cal']} for XCO2, "
                     f"{corr_fac['XCH4_cal']} for XCH4.")

      # Get the start and stop datetime, that is also needed for the file name.

      # start, stop = self.get_start_stop_date_time(day)
        start, stop = self.get_start_stop_date_time(day, df)
      # start, stop = self.get_start_stop_date_time_csv(day)
        self.MyHDF5.attrs['DATA_START_DATE'] = np.string_(start)
        self.MyHDF5.attrs['DATA_STOP_DATE'] = np.string_(stop)

        self.MyHDF5.attrs['DATA_VARIABLES'] = \
            np.string_(';'.join(self.variables))

        self.MyHDF5.attrs['FILE_ACCESS'] = np.string_('COCCON')

        self.MyHDF5.attrs['FILE_GENERATION_DATE'] = \
            np.string_(dt.datetime.now().strftime('%Y%m%dT%H%M%SZ'))

      # Create the final file name of the GEOMS compliant HDF5 file.

        self.file_name = ("groundbased_"
            f"{self.input_args['DATA_SOURCE']}_"
            f"{self.input_args['DATA_LOCATION']}_"
            f"{start}_{stop}_"
            f"{self.input_args['DATA_FILE_VERSION']}"
            f".h5").lower()

        self.MyHDF5.attrs['FILE_NAME'] = np.string_(self.file_name)

        self.MyHDF5.attrs['FILE_PROJECT_ID'] = np.string_('COCCON')


if __name__ == "__main__":

  # input_file = "input_sodankyla_GEOMS_Extention.yml"
    input_file = "input_karlsruhe_GEOMS_Extention.yml"

    MyCreator = PROFFAST_GEOMS_creator(input_file)

  # MyTestDay = dt.datetime.strptime("2017-06-09", "%Y-%m-%d")
    MyTestDay = dt.datetime.strptime("2021-05-31", "%Y-%m-%d")
    MyCreator.generate_GEOMS_at(day=MyTestDay)

