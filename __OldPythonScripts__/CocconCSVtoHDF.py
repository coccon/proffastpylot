# -*- coding: utf-8 -*-
# !/usr/bin/python27
#==================================================================================================================#
#------------------------------------------------------------------------------------------------------------------#
# Python Script: CocconCSVtoHDF.py
# Version/Date:  V01 (15.11.2020)
# Project:       COCCON-PROCEEDS, FRM4GHG, and S5P-MPC funded by ESA
# Created by:    Bavo Langerock, Royal Belgian Institute for Space Aeronomy (BIRA-IASB), Belgium
#                Mahesh Kumar Sha, Royal Belgian Institute for Space Aeronomy (BIRA-IASB), Belgium
# Modified by:   Darko Dubravica, Karlsruhe Institute of Technology (KIT), Germany
# Description:   Converts CSV format to HDF format
#------------------------------------------------------------------------------------------------------------------#
#==================================================================================================================#


#==================================================================================================================#
#------------------------------------------------------------------------------------------------------------------#
# import modules/packages

import os, h5py, time, shutil, glob, math, re
import numpy as np
import nested_dict as nd
import collections as coll
import CocconClass as myClass
import CocconDef as myDef

#-------------------------------------------------------------------------------------------------#
#=================================================================================================#


#=================================================================================================#
#-------------------------------------------------------------------------------------------------#
# site coordinates, instrumental calibration factors, etc.

sitedef = dict(
  karlsruhe = {'longitude':  8.4397, 'latitude': 49.1025, 'altitude': 0.133},
  sodankyla = {'longitude': 26.6310, 'latitude': 67.3668, 'altitude': 0.188}
)

instcal = dict(
  karlsruhe    = {'XCO2_cal': 1.0000, 'XCH4_cal': 1.0000}, # EM27SUN SN037 (reference)
  sodankyla    = {'XCO2_cal': 0.9992, 'XCH4_cal': 0.9994}  # EM27SUN SN039
)

sitedat = dict(
  karlsruhe    = {'data': 'Station data'},
  sodankyla    = {'data': 'Station data'}
#----------------------------------------------------------------------------------------------------
# karlsruhe    = {'data': 'Campaign data'},
# sodankyla    = {'data': 'Campaign data'}
)

#-------------------------------------------------------------------------------------------------#
#=================================================================================================#


#=================================================================================================#
#-------------------------------------------------------------------------------------------------#
# creates the output file for the em27sun measurements done at a given site

def CSVtoHDF(main_path, site, instrument, file_dat, file_sen, file_ptf, file_vmr):

#-------------------------------------------------------------------------------------------------#
# PROFFAST output (single day)

  cols = ['H2O', 'O2', 'CO2', 'CH4', 'CO', 'CH4_S5P']

  file_path = os.path.join(main_path,site,instrument)
  underscore = '_'
  file_out = os.path.join(file_path,underscore.join([site,instrument,'hdfout.hdf']))

#-------------------------------------------------------------------------------------------------#
# data array definition / attributes

  data = myClass.dataDict({},attrs={})

  data['Instrument_name'] = instrument
  data.attrs['Instrument_name'] = {'description':'name of the instrument'}
  data['Site_name'] = site
  data.attrs['Site_name'] = {'description':'name of the site where the instrument is operational'}
  data['Measurement_mode'] = 'solar'
  data.attrs['Measurement_mode'] = {'description':'InGaAs detector'}

# data['Instrument_latitude'] = sitedef[site]['latitude']
# data.attrs['Instrument_latitude'] = {'unit':'degree_north','description':'latitude of the instrument'}
# data['Instrument_longitude'] = sitedef[site]['longitude']
# data.attrs['Instrument_longitude'] = {'unit':'degree_east','description':'longitude of the instrument'}
# data['Instrument_altitude'] = sitedef[site]['altitude']
# data.attrs['Instrument_altitude'] = {'unit':'km','description':'altitude of the instrument'}

# data['XCO2_cal'] = instcal[site]['XCO2_cal']
# data.attrs['XCO2_cal'] = {'unit':'','description':'calibration factor for XCO2'}
# data['XCH4_cal'] = instcal[site]['XCH4_cal']
# data.attrs['XCH4_cal'] = {'unit':'','description':'calibration factor for XCH4'}

#-------------------------------------------------------------------------------------------------#

  FILE_INP = file_dat

  FILE_INP_FORMAT = {"DateTime": 0, "JulianDate": 0, "HHMMSS_ID": 1, "gndP": 3, "gndT": 4, "latdeg": 5, "londeg": 6, "altim": 7, "appSZA": 8, "azimuth": 9, "XH2O": 10, "XAIR": 12, "XCO2": 14, "XCH4": 17, "XCH4_S5P": 20, "XCO": 21, "H2O": 25, "O2": 40, "CO2": 67, "CH4": 97, "CO": 127, "CH4_S5P": 125, "job01_rms": 23, "job03_rms": 63, "job04_rms": 90, "job05_rms": 119}

#-------------------------------------------------------------------------------------------------#

  FILE_INP_DATA = coll.OrderedDict()

  CO_avg = 0.0
  CO_lnr = 0.0

  with open(FILE_INP,'r') as fid: 
    header = fid.readline().split('\t') # skip header line
    for line in fid:
      line = re.sub(' +', ' ', line)
      line = line.split(' ')
      if line[21] == 'NaN': continue # incomplete line
      CO_avg += float(line[21])
      CO_lnr += 1.0

  CO_avg = CO_avg / CO_lnr

  with open(FILE_INP,'r') as fid: 
    header = fid.readline().split('\t') # skip header line
    for line in fid:
      line = re.sub(' +', ' ', line)
      line = line.split(' ')
    # if len(line) < 15: continue # data filter for incomplete lines
      if float(line[8]) > 75.0: continue # data filter for SZA greater than 75 deg
    # if float(line[5]) > 75.0: continue # data filter for SZA greater than 75 deg
      if float(line[12]) < 0.98: continue # data filter for XAIR smaller than 0.98
      if float(line[12]) > 1.02: continue # data filter for XAIR greater than 1.02
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
      [FILE_INP_DATA.setdefault(k,[]).append(line[c].replace('--','nan').replace('inf','nan') if line[c] else 'nan') for k,c in FILE_INP_FORMAT.items()] # this is to get rid of the -- values

  if (len(FILE_INP_DATA) < 12): print 'file_len: ', len(FILE_INP_DATA), ' (data filter applied)'; return -1 # test file lenght
# if (len(FILE_INP_DATA['DateTime']) < 12): return # test file lenght

  for k,allv in FILE_INP_DATA.items():
    if k == 'DateTime':
      print 'DateTime Column Skipped!'
    else:
      if k not in cols:
        FILE_INP_DATA[k] = np.array(allv,dtype=np.float) # FILE_INP_DATA contains all data from the PROFFAST data file
      else:
        FILE_INP_DATA[k] = np.array(allv,dtype=np.float) / 10000.0

  FILE_INP_DATA['DateTime'] = myDef.GEOMStoDateTime((FILE_INP_DATA['JulianDate'] - 2451544.5) * 86400.0)

  FILE_INP_DATA = coll.OrderedDict(zip(FILE_INP_DATA.keys(),map(np.array,zip(*sorted(zip(*FILE_INP_DATA.values()),key=lambda vs:vs[FILE_INP_DATA.keys().index('DateTime')])))))

  mask = np.ones(FILE_INP_DATA['DateTime'].shape, dtype=np.bool) # *(FILE_INP_DATA['SZA']<75)

#-------------------------------------------------------------------------------------------------#
# JDOrigin DateTime JulianDate HHMMSS_ID gndP gndT latdeg londeg altim appSZA azimuth XH2O XAIR XCO2 XCH4 XCO XCH4_S5P H2O O2 CO2 CH4 CO CH4_S5P
# job01_gas01: H2O, job02_gas07: O2, job03_gas03: CO2, job04_gas04: CH4, job05_gas06: CO, job05_gas04: CH4_S5P

# data['JDOrigin'] = FILE_INP_DATA['JDOrigin']; data.attrs['JDOrigin'] = {'unit':'','description':'JulianDate'}
  data['DateTime'] = FILE_INP_DATA['DateTime']; data.attrs['DateTime'] = {'unit':'','description':'DateTime'}
  data['JulianDate'] = FILE_INP_DATA['JulianDate']; data.attrs['JulianDate'] = {'unit':'','description':'JulianDate'}
  data['HHMMSS_ID'] = FILE_INP_DATA['HHMMSS_ID']; data.attrs['HHMMSS_ID'] = {'unit':'','description':'HHMMSS ID'}
  data['P_ground'] = FILE_INP_DATA['gndP']; data.attrs['P_ground'] = {'unit':'hPa','description':'ground pressure'}
  data['T_ground'] = FILE_INP_DATA['gndT']; data.attrs['T_ground'] = {'unit':'K','description':'ground temperature'}
  data['Instr_Lat'] = FILE_INP_DATA['latdeg']; data.attrs['Instr_Lat'] = {'unit':'deg','description':'instrument latitude'}
  data['Instr_Lon'] = FILE_INP_DATA['londeg']; data.attrs['Instr_Lon'] = {'unit':'deg','description':'instrument longitude'}
  data['Instr_Alt'] = FILE_INP_DATA['altim']; data.attrs['Instr_Alt'] = {'unit':'m','description':'instrument altitude'}
  data['Angle_zenith'] = FILE_INP_DATA['appSZA']; data.attrs['Angle_zenith'] = {'unit':'deg','description':'apparent solar zenith angle'}
  data['Angle_azimuth'] = FILE_INP_DATA['azimuth']+180.0; data.attrs['Angle_azimuth'] = {'unit':'deg','description':'solar azimuth angle'}

  data['XH2O'] = FILE_INP_DATA['XH2O']; data.attrs['XH2O'] = {'unit':'ppm','description':'total column XH2O'}
  data['XAIR'] = FILE_INP_DATA['XAIR']; data.attrs['XAIR'] = {'unit':'','description':'XAIR'}
  data['XCO2'] = FILE_INP_DATA['XCO2']; data.attrs['XCO2'] = {'unit':'ppm','description':'total column XCO2'}
  data['XCH4'] = FILE_INP_DATA['XCH4']; data.attrs['XCH4'] = {'unit':'ppm','description':'total column XCH4'}
  data['XCO'] = FILE_INP_DATA['XCO']; data.attrs['XCO'] = {'unit':'ppb','description':'total column XCO'}
  data['XCH4_S5P'] = FILE_INP_DATA['XCH4_S5P']; data.attrs['XCH4_S5P'] = {'unit':'ppm','description':'total column XCH4 S5P'}

  data['XCO2_cal'] = float(instcal[site]['XCO2_cal'])
  data['XCH4_cal'] = float(instcal[site]['XCH4_cal'])

  data['XCO2'] = data['XCO2'] * float(instcal[site]['XCO2_cal'])
  data['XCH4'] = data['XCH4'] * float(instcal[site]['XCH4_cal'])

  data['H2O'] = FILE_INP_DATA['H2O']; data.attrs['H2O'] = {'unit':'ppm','description':'column H2O'}
  data['O2'] = FILE_INP_DATA['O2']; data.attrs['O2'] = {'unit':'','description':'column O2'}
  data['CO2'] = FILE_INP_DATA['CO2']; data.attrs['CO2'] = {'unit':'ppm','description':'column CO2'}
  data['CH4'] = FILE_INP_DATA['CH4']; data.attrs['CH4'] = {'unit':'ppm','description':'column CH4'}
  data['CO'] = FILE_INP_DATA['CO']; data.attrs['CO'] = {'unit':'ppb','description':'column CO'}
  data['CH4_S5P'] = FILE_INP_DATA['CH4_S5P']; data.attrs['CH4_S5P'] = {'unit':'ppm','description':'column CH4 S5P'}

  data['XH2O_rms'] = FILE_INP_DATA['job01_rms']; data.attrs['XH2O_rms'] = {'unit':'ppmv','description':'total random uncertainty on the retrieved total column (expressed in units as the columns) XH2O'}
  data['XCO2_rms'] = FILE_INP_DATA['job03_rms']; data.attrs['XCO2_rms'] = {'unit':'ppmv','description':'total random uncertainty on the retrieved total column (expressed in units as the columns) XCO2'}
  data['XCH4_rms'] = FILE_INP_DATA['job04_rms']; data.attrs['XCH4_rms'] = {'unit':'ppmv','description':'total random uncertainty on the retrieved total column (expressed in units as the columns) XCH4'}
  data['XCO_rms'] = FILE_INP_DATA['job05_rms']; data.attrs['XCO_rms'] = {'unit':'ppmv','description':'total random uncertainty on the retrieved total column (expressed in units as the columns) XCO'}

#-------------------------------------------------------------------------------------------------#
# add a-priori profiles

  FILE_INP = file_ptf

  FILE_INP_FORMAT_A = {"Index": 0, "Altitude": 1, "Temperature": 2, "Pressure": 3, "Column": 4, "H2O": 5, "HDO": 6}

  FILE_INP_DATA = coll.OrderedDict()

  with open(FILE_INP,'r') as fid:
    header = fid.readline() # skip header lines
    for line in fid:
      line = line.lstrip()
      line = re.sub(' +', '\t', line)
      line = line.split('\t') # if len(line)<15: continue
      [FILE_INP_DATA.setdefault(k,[]).append(line[c]) for k,c in FILE_INP_FORMAT_A.items()]

  for k,allv in FILE_INP_DATA.items():
    if k == '' or k == 'Index':
      print 'Column Skipped!'
    elif k == 'Altitude':
      FILE_INP_DATA[k] = np.array(allv,dtype=np.float) / 1000.0 # m -> km
    elif k == 'Pressure':
      FILE_INP_DATA[k] = np.array(allv,dtype=np.float) / 100.0 # Pa -> hPa
    else:
      FILE_INP_DATA[k] = np.array(allv,dtype=np.float)

  data['H_prior'] = FILE_INP_DATA['Altitude']; data.attrs['H_prior'] = {'unit':'km','description':'prior height'}
  data['T_prior'] = FILE_INP_DATA['Temperature']; data.attrs['T_prior'] = {'unit':'K','description':'prior temperature'}
  data['P_prior'] = FILE_INP_DATA['Pressure']; data.attrs['P_prior'] = {'unit':'hPa','description':'prior pressure'}
  data['C_prior'] = FILE_INP_DATA['Column']; data.attrs['C_prior'] = {'unit':'molec/cm3','description':'prior dry air column'}
  data['H2O_prior'] = FILE_INP_DATA['H2O']; data.attrs['H2O_prior'] = {'unit':'parts','description':'prior H2O column'}
  data['HDO_prior'] = FILE_INP_DATA['HDO']; data.attrs['HDO_prior'] = {'unit':'parts','description':'prior HDO column'}

#-------------------------------------------------------------------------------------------------#

  k_B = 1.3807e-23 # 1.380649E-23 # kboltz = 1.3807e-23
  pi = 3.141592653589793 # math.pi
  dgdh = -3.086E-6 # grav. accel reduces with altitude (per meter)
  amunit = 1.6605E-27
  mu_dry = 28.97
  mu_h2o = 18.02
  lat_rad = float(sitedef[site]['latitude']) * pi / 180.0

  p_dry = FILE_INP_DATA['Pressure'] * 1.0 / (1.0 + 1.0E-6 * FILE_INP_DATA['H2O']) # / 100.0 # Pa -> hPa
  p_h2o = FILE_INP_DATA['Pressure'] * 1.0E-6 * FILE_INP_DATA['H2O'] / (1.0 + 1.0E-6 * FILE_INP_DATA['H2O']) # / 100.0 # Pa -> hPa
  n_dry = p_dry / (k_B * FILE_INP_DATA['Temperature'])
  n_h2o = p_h2o / (k_B * FILE_INP_DATA['Temperature'])

  FILE_INP_DATA['P_Dry'] = p_dry
  FILE_INP_DATA['N_Dry'] = n_dry
  FILE_INP_DATA['P_H2O'] = p_h2o
  FILE_INP_DATA['N_H2O'] = n_h2o
  FILE_INP_DATA['N_Tot'] = n_dry + n_h2o

  mutot_amu = (mu_dry + 1.0E-6 * FILE_INP_DATA['H2O'] * mu_h2o) / (1.0 + 1.0E-6 * FILE_INP_DATA['H2O'])

  g_eff_gnd = 9.780327 * (1.0 + 0.0053024*math.sin(lat_rad)*math.sin(lat_rad) - 5.8E-6*math.sin(2.0*lat_rad) * math.sin(2.0*lat_rad))

  g_eff = g_eff_gnd + dgdh * data['H_prior'] * 1000.0 # km -> m

  FILE_INP_DATA['ScaleHeight'] = k_B * FILE_INP_DATA['Temperature'] / (g_eff * mutot_amu * amunit)

#-------------------------------------------------------------------------------------------------#

  data['N_prior'] = FILE_INP_DATA['N_Tot']; data.attrs['N_prior'] = {'unit':'molec/cm3','description':'prior number denstity'}
  data['N_Dry_prior'] = FILE_INP_DATA['N_Dry']; data.attrs['N_Dry_prior'] = {'unit':'molec/cm3','description':'prior number density dry air'}
  data['N_H2O_prior'] = FILE_INP_DATA['N_H2O']; data.attrs['N_H2O_prior'] = {'unit':'molec/cm3','description':'prior number density h2o'}
  data['P_Dry_prior'] = FILE_INP_DATA['P_Dry']; data.attrs['P_Dry_prior'] = {'unit':'molec/cm3','description':'prior pressure dry air'}
  data['P_H2O_prior'] = FILE_INP_DATA['P_H2O']; data.attrs['P_H2O_prior'] = {'unit':'molec/cm3','description':'prior pressure h2o'}
  data['S_height'] = FILE_INP_DATA['ScaleHeight']; data.attrs['S_height'] = {'unit':'molec/cm3','description':'scale height'}

#-------------------------------------------------------------------------------------------------#
# add a-priori profiles
# Level index, Altitude(m), H2O, HDO, CO2, CH4, N2O, CO, O2, HF

  FILE_INP = file_vmr

  FILE_INP_FORMAT_B = {"Index": 0, "Altitude": 1, "H2O": 2, "HDO": 3, "CO2": 4, "CH4": 5, "N2O": 6, "CO": 7, "O2": 8, "HF": 9}

  FILE_INP_DATA = coll.OrderedDict()

  with open(FILE_INP,'r') as fid:
    for line in fid:
      line = line.lstrip()
      line = re.sub(' +', '\t', line)
      line = line.split('\t') # if len(line)<15: continue
      [FILE_INP_DATA.setdefault(k,[]).append(line[c]) for k,c in FILE_INP_FORMAT_B.items()]

  for k,allv in FILE_INP_DATA.items():
    if k == '' or k == 'Index':
      print 'Column Skipped!'
    elif k == 'Altitude':
      FILE_INP_DATA[k] = np.array(allv,dtype=np.float) / 1000.0 # m -> km
    else:
      FILE_INP_DATA[k] = np.array(allv,dtype=np.float)

#-------------------------------------------------------------------------------------------------#

  data['H_prior'] = FILE_INP_DATA['Altitude']; data.attrs['H_prior'] = {'unit':'km','description':'prior height'}
  data['H2O_prior'] = FILE_INP_DATA['H2O']; data.attrs['H2O_prior'] = {'unit':'parts','description':'prior H2O column'}
  data['HDO_prior'] = FILE_INP_DATA['HDO']; data.attrs['HDO_prior'] = {'unit':'parts','description':'prior HDO column'}
  data['CO2_prior'] = FILE_INP_DATA['CO2']; data.attrs['CO2_prior'] = {'unit':'ppm','description':'prior CO2 column'}
  data['CH4_prior'] = FILE_INP_DATA['CH4']; data.attrs['CH4_prior'] = {'unit':'ppb','description':'prior CH4 column'}
  data['N2O_prior'] = FILE_INP_DATA['N2O']; data.attrs['N2O_prior'] = {'unit':'ppb','description':'prior N2O column'}
  data['CO_prior'] = FILE_INP_DATA['CO']; data.attrs['CO_prior'] = {'unit':'ppb','description':'prior CO column'}
  data['O2_prior'] = FILE_INP_DATA['O2']; data.attrs['O2_prior'] = {'unit':'ppb','description':'prior O2 column'}
  data['HF_prior'] = FILE_INP_DATA['HF']; data.attrs['HF_prior'] = {'unit':'ppt','description':'prior HF column'}

#-------------------------------------------------------------------------------------------------#
# add column sensitivities
# alt [km], p [mbar], SZA[rad]: 0.000E+00, 3.965E-01, 5.607E-01, 6.867E-01, 7.930E-01, 8.866E-01, 9.712E-01, 1.049E+00, 1.121E+00, 1.189E+00, 1.254E+00, 1.315E+00, 1.373E+00, 1.430E+00, 1.484E+00

  FILE_INP = file_sen
 
  FILE_INP_GAS = ["H2O_sens", "HDO_sens", "CO2_sens", "CH4_sens", "N2O_sens", "CO_sens", "O2_sens", "HF_sens"]

  FILE_INP_FORMAT = {"H2O_sens": 2, "HDO_sens": 3, "CO2_sens": 4, "CH4_sens": 5, "CO_sens": 6, "O2_sens": 7, "HF_sens": 8}

  with open(FILE_INP,'r') as fid:

    sza = []

    for i in range(8): # H2O, HDO, CO2, CH4, N2O, CO, O2, HF

      FILE_INP_DATA = coll.OrderedDict()

      for j in range(6):
        header = fid.readline() # .split('\t') # skip header lines
        if i == 0 and j == 3:
          header = re.sub(' +', '\t', header)
          header = header.split('\t') #; print header
          sza = np.array(header[3:])  #; print sza
          sza = sza.astype(np.float)  #; print sza

      lines = []
      
      hsens = []
      psens = []

      for j in range(49):
        line = fid.readline()[1:-1]    # skip first empty space and carriage return character at the end
        line = re.sub(' +', ',', line) # replace empty spaces by a comma
        line = line.split(',')         # split line into columns

        hsens.append(line[0])
        psens.append(line[1])

        lines.append([])
        for k in range(2,len(line)):
          lines[j].append(float(line[k]))

      if i == 0: # repeated several times, but needed only once
        FILE_INP_DATA['Hsens'] = np.array(hsens,dtype=np.float)
        FILE_INP_DATA['Psens'] = np.array(psens,dtype=np.float)
        FILE_INP_DATA['SZAsens'] = np.array(sza,dtype=np.float)

        data['H_sens'] = FILE_INP_DATA['Hsens']; data.attrs['H_sens'] = {'unit':'km','description':'height sensivity for solar zenith angle'}
        data['P_sens'] = FILE_INP_DATA['Psens']; data.attrs['P_sens'] = {'unit':'mbar','description':'pressure sensivity for solar zenith angle'}
        data['SZA_sens'] = FILE_INP_DATA['SZAsens']; data.attrs['SZA_sens'] = {'unit':'rad','description':'solar zenith angles'}

      FILE_INP_DATA[FILE_INP_GAS[i]] = np.array(lines,dtype=np.float)

      data[FILE_INP_GAS[i]] = FILE_INP_DATA[FILE_INP_GAS[i]]; data.attrs[FILE_INP_GAS[i]] = {'unit':'','description':'column sensivity '+FILE_INP_GAS[i][:-4]+': solar zenith angle'}

#-------------------------------------------------------------------------------------------------#
# interpolation SZA

  FILE_INT_GAS = ["H2O_int", "HDO_int", "CO2_int", "CH4_int", "N2O_int", "CO_int", "O2_int", "HF_int"]

  for k in range(8): # H2O, HDO, CO2, CH4, N2O, CO, O2, HF

    FILE_INT_DATA = coll.OrderedDict()

    gas_sens = []

    for i in range(len(data['Angle_zenith'])): # measurements

      gas_sens.append([])

      SZA_app_rad = data['Angle_zenith'][i] * 2.0 * math.pi / 360.
      SZA_app_deg = data['Angle_zenith'][i]

      for j in range(len(data['SZA_sens'])-1): # SZA angels
        SZA_sen_rad_1 = data['SZA_sens'][j]
        SZA_sen_deg_1 = data['SZA_sens'][j] / 2.0 / math.pi * 360.
        SZA_sen_rad_2 = data['SZA_sens'][j+1]
        SZA_sen_deg_2 = data['SZA_sens'][j+1] / 2.0 / math.pi * 360.
        SZA_dif_rad = SZA_sen_rad_2 - SZA_sen_rad_1
        SZA_dif_deg = SZA_sen_deg_2 - SZA_sen_deg_1

        if SZA_app_rad >= SZA_sen_rad_1 and SZA_app_rad <= SZA_sen_rad_2:

          for h in range(len(data['H_sens'])):
            gas_1 = data[FILE_INP_GAS[k]][h][j]
            gas_2 = data[FILE_INP_GAS[k]][h][j+1]
            gas_dif = gas_2 - gas_1

            m_rad = gas_dif/SZA_dif_rad
            m_deg = gas_dif/SZA_dif_deg

            b_gas = gas_1 - m_rad * SZA_sen_rad_1

            gas_int = m_rad * SZA_app_rad + b_gas # gas interpolation
            gas_sens[i].append(gas_int)

        elif j == len(data['SZA_sens'])-2 and SZA_app_rad > data['SZA_sens'][len(data['SZA_sens'])-1]:

          for h in range(len(data['H_sens'])):
            gas_1 = data[FILE_INP_GAS[k]][h][j]
            gas_2 = data[FILE_INP_GAS[k]][h][j+1]
            gas_dif = gas_2 - gas_1

            m_rad = gas_dif/SZA_dif_rad
            m_deg = gas_dif/SZA_dif_deg

            b_gas = gas_1 - m_rad * SZA_sen_rad_1

            gas_int = m_rad * SZA_app_rad + b_gas # gas extrapolation
            gas_sens[i].append(gas_int)

    FILE_INT_DATA[FILE_INT_GAS[k]] = np.array(gas_sens,dtype=np.float)

    data[FILE_INT_GAS[k]] = FILE_INT_DATA[FILE_INT_GAS[k]]; data.attrs[FILE_INT_GAS[k]] = {'unit':'','description':'column sensivity '+FILE_INP_GAS[k][:-4]+': solar zenith angle'}

#-------------------------------------------------------------------------------------------------#
# change datetime to MJD2000

  data['DateTime'] = myDef.DateTimeToGEOMS(data['DateTime']) / 86400.0
  data.attrs['DateTime']['unit'] = 'days since 2000-01-01 00:00:00'

  with h5py.File(file_out,'w') as fid: 
    myDef.hdf_store(hdfid=fid, value=data, dtype='f')
  # myDef.hdf_store(hdfid=fid, value=data, dtype='f8')
    fid.attrs['DATA_PROCESSOR'] = 'PROFFAST'
    fid.attrs['DATA_FILE_VERSION'] = '001'
    fid.attrs['DATA_LOCATION'] = site.upper()
    fid.attrs['DATA_QUALITY'] = sitedat[site]['data']
    fid.attrs['FILE_GENERATION_DATE'] = time.strftime("%x")

  return 0

#-------------------------------------------------------------------------------------------------#
#=================================================================================================#
