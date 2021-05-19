# -*- coding: utf-8 -*-
#=================================================================================================#
#-------------------------------------------------------------------------------------------------#
# Python Script: CocconHDFtoGEOMS.py
# Version/Date:  V01 (15.10.2020)
# Project:       COCCON-PROCEEDS, FRM4GHG, and S5P-MPC funded by ESA 
# Created by:    Mahesh Kumar Sha & Bavo Langerock, Royal Belgian Institute for Space Aeronomy (BIRA-IASB), Belgium
# Modified by:   Darko Dubravica, Karlsruhe Institute of Technology (KIT), Germany
# Description:   Converts HDF format to GEOMS compliant format
#-------------------------------------------------------------------------------------------------#
#=================================================================================================#


#=================================================================================================#
#-------------------------------------------------------------------------------------------------#
# import modules/packages

import os, h5py, time, shutil, glob, math, re
import numpy as np
import datetime
#import nested_dict as nd
import collections as coll
import CocconDef as mydef

#-------------------------------------------------------------------------------------------------#
#=================================================================================================#


#=================================================================================================#
#-------------------------------------------------------------------------------------------------#

doi_address = 'https://doi.org/xx.xxxxx/xxxxxxxx'

#-------------------------------------------------------------------------------------------------#
#=================================================================================================#


#=================================================================================================#
#-------------------------------------------------------------------------------------------------#
# ...

def HDFtoGEOMS(main_path, site_path, file_hdf, strict=True, table='tableattrvalue_04R052.dat', template='GEOMS-TE-FTIR-COCCON-001.csv', fileversion=1):
#def HDFtoGEOMS(main_path, site_path, file_hdf='karlsruhe_EM27SUN_hdfout.hdf', strict=True, table='tableattrvalue_04R052.dat', template='GEOMS-TE-FTIR-COCCON-001.csv', fileversion=1):
#def HDFtoGEOMS(main_path, site_path, file_hdf='gobabeb_EM27SUN_hdfout.hdf', strict=True, table='tableattrvalue_04R052.dat', template='GEOMS-TE-FTIR-COCCON-001.csv', fileversion=1):
#def HDFtoGEOMS(main_path, site_path, file_hdf='thessaloniki_EM27SUN_hdfout.hdf', strict=True, table='tableattrvalue_04R052.dat', template='GEOMS-TE-FTIR-COCCON-001.csv', fileversion=1):
#def HDFtoGEOMS(main_path, site_path, file_hdf='fairbanks_EM27SUN_hdfout.hdf', strict=True, table='tableattrvalue_04R052.dat', template='GEOMS-TE-FTIR-COCCON-001.csv', fileversion=1):

  file_path = os.path.join(site_path,file_hdf)
  table_path = os.path.join(main_path,table)
  template_path = os.path.join(main_path,template)
  outdir = os.path.dirname(file_path)

  print '\n', "file_path", file_path
  print "table_path", table_path
  print "template_path", template_path
  print "outdir", outdir, '\n' # site_path

  variableswritten = []; fileattrs = coll.OrderedDict()

#-------------------------------------------------------------------------------------------------#
# function to store GEOMS data (this only calls hdf_store...)

  def GEOMS_store(tem, data, si, m=None, strict=strict, M=None, fill=-900000., note=''):

    variableswritten.append(tem['name'])
    maskdata = np.ma.masked_array(data,np.isnan(data)+np.isinf(data))

    if not strict: m = None; M = None

    if np.array_equal(m,None): m = maskdata.min()

    if np.array_equal(M,None): M = maskdata.max()

    if data.shape == (): data = np.array([data])

    if tem['dtype'] == 'DOUBLE': dt = 'f8'
    elif tem['dtype'] == 'REAL': dt = 'f'
    elif tem['dtype'] == 'UINT': dt = 'u'
    elif tem['dtype'] == 'INT': dt = 'i'
    elif tem['dtype'] == 'STRING': dt = 's'

    mydef.hdf_store(gfid, tem['name'], np.ma.masked_array(data,maskdata.mask+(maskdata.filled(m)<m)+(maskdata.filled(M)>M)).filled(fill).astype(dt), dtype=dt,
      VAR_NAME=np.array(tem['name']), VAR_DESCRIPTION=np.array(tem['desc']),
      VAR_NOTES=np.array(note), VAR_SIZE=np.array(';'.join(map(str,list(data.shape)))),
      VAR_DEPEND=np.array(tem['dep']), VAR_DATA_TYPE=np.array(tem['dtype']),
      VAR_UNITS=np.array(tem['unit']), units=np.array(tem['unit']), VAR_SI_CONVERSION=np.array(si))

    gfid[tem['name']].attrs.create('VAR_VALID_MIN',m,dtype=dt) # According to GEOMS standard, these attrs must be stored
    gfid[tem['name']].attrs.create('VAR_VALID_MAX',M,dtype=dt) # with the same datatype as the data itself...
    gfid[tem['name']].attrs.create('valid_range',np.array([m,M]),dtype=dt)
    gfid[tem['name']].attrs.create('VAR_FILL_VALUE',fill,dtype=dt)
    gfid[tem['name']].attrs.create('_FillValue',fill,dtype=dt)

    return

#-------------------------------------------------------------------------------------------------#
# function to store GEOMS string data (this only calls hdf_store...)

  def GEOMS_store_string(tem,data, note='', fill='\x00'):

    variableswritten.append(tem['name'])

    mydef.hdf_store(gfid,tem['name'],data,dtype=str(data.dtype)[1:],
      VAR_NAME=np.array(tem['name']),VAR_DESCRIPTION=np.array(tem['desc']),
      VAR_NOTES=np.array(note),VAR_SIZE=np.array(';'.join(map(str,list(data.shape))) if data.shape else '1'),
      VAR_DEPEND=np.array(tem['dep']),VAR_DATA_TYPE=np.array(tem['dtype']),VAR_UNITS=np.array(''),VAR_SI_CONVERSION=np.array(''),VAR_VALID_MIN=np.array(''),VAR_VALID_MAX=np.array(''),VAR_FILL_VALUE=np.array(fill))

    gfid[tem['name']].attrs['_FillValue'] = np.array(fill)

    return

#-------------------------------------------------------------------------------------------------#
# get all information to construct output file name

  with h5py.File(file_path, 'r') as fid:

    fileattrs['DATA_LOCATION'] = str(fid['Site_name'][...]).upper()
    iname = str(fid['Instrument_name'][...])
    isite = str(fid['Site_name'][...])

    if fileattrs['DATA_LOCATION'] == 'FAIRBANKS': fileattrs['DATA_LOCATION'] = 'FAIRBANKS.AK'

    if iname == 'EM27SUN': fileattrs['DATA_SOURCE'] = 'FTIR.COCCON_'
  # if iname == 'EM27SUN': fileattrs['DATA_SOURCE'] = 'EM27SUN.COCCON_'
  # else: fileattrs['DATA_SOURCE'] = 'FTIR.COCCON_'

    fileattrs['DATA_DISCIPLINE'] = 'ATMOSPHERIC.CHEMISTRY;REMOTE.SENSING;GROUNDBASED'
    fileattrs['DATA_GROUP'] = 'EXPERIMENTAL;PROFILE.STATIONARY'
    alldatetimes = mydef.GEOMStoDateTime(fid['DateTime'][...]*86400.)

    if iname=='EM27SUN' and isite=='karlsruhe':
        fileattrs['DATA_SOURCE'] += 'KIT.IMK.ASF037';
        fileattrs['PI_NAME'] = 'Hase;Frank';
      # fileattrs['PI_AFFILIATION'] = 'Karlsruhe Institute of Technology;KIT';
        fileattrs['PI_AFFILIATION'] = 'Karlsruhe Institute of Technology - Institute of Meteorology and Climate Research - Atmospheric Trace Gases and Remote Sensing;KIT.IMK.ASF';
        fileattrs['PI_ADDRESS'] = 'P.O. Box 3640;D-76021 Karlsruhe;GERMANY';
        fileattrs['PI_EMAIL'] = 'frank.hase@kit.edu';
        fileattrs['DO_NAME'] = 'Alberti;Carlos';
      # fileattrs['DO_AFFILIATION'] = 'Karlsruhe Institute of Technology;KIT';
        fileattrs['DO_AFFILIATION'] = 'Karlsruhe Institute of Technology - Institute of Meteorology and Climate Research - Atmospheric Trace Gases and Remote Sensing;KIT.IMK.ASF';
        fileattrs['DO_ADDRESS'] = 'P.O. Box 3640;D-76021 Karlsruhe;GERMANY';
        fileattrs['DO_EMAIL'] = 'carlos.alberti@kit.edu';
        fileattrs['DS_NAME'] = 'Dubravica;Darko';
      # fileattrs['DS_AFFILIATION'] = 'Karlsruhe Institute of Technology;KIT';
        fileattrs['DS_AFFILIATION'] = 'Karlsruhe Institute of Technology - Institute of Meteorology and Climate Research - Atmospheric Trace Gases and Remote Sensing;KIT.IMK.ASF';
        fileattrs['DS_ADDRESS'] = 'P.O. Box 3640;D-76021 Karlsruhe;GERMANY';
        fileattrs['DS_EMAIL'] = 'darko.dubravica@kit.edu'
  # elif iname=='EM27SUN' and isite=='fairbanks':
  # elif iname=='EM27SUN' and isite=='gobabeb':
  # elif iname=='EM27SUN' and isite=='thessaloniki':
  # elif iname=='EM27SUN' and isite=='kiruna':
  # elif iname=='EM27SUN' and isite=='izana':
  # elif iname=='EM27SUN' and isite=='newzealand':
  # elif iname=='EM27SUN' and isite=='mexico':
  # elif iname=='EM27SUN' and isite=='tsukuba':
    elif iname=='EM27SUN' and isite=='sodankyla':
        fileattrs['DATA_SOURCE'] += 'KIT.IMK.ASF037';
        fileattrs['PI_NAME'] = 'Hase;Frank';
      # fileattrs['PI_AFFILIATION'] = 'Karlsruhe Institute of Technology;KIT';
        fileattrs['PI_AFFILIATION'] = 'Karlsruhe Institute of Technology - Institute of Meteorology and Climate Research - Atmospheric Trace Gases and Remote Sensing;KIT.IMK.ASF';
        fileattrs['PI_ADDRESS'] = 'P.O. Box 3640;D-76021 Karlsruhe;GERMANY';
        fileattrs['PI_EMAIL'] = 'frank.hase@kit.edu';
        fileattrs['DO_NAME'] = 'Alberti;Carlos';
      # fileattrs['DO_AFFILIATION'] = 'Karlsruhe Institute of Technology;KIT';
        fileattrs['DO_AFFILIATION'] = 'Karlsruhe Institute of Technology - Institute of Meteorology and Climate Research - Atmospheric Trace Gases and Remote Sensing;KIT.IMK.ASF';
        fileattrs['DO_ADDRESS'] = 'P.O. Box 3640;D-76021 Karlsruhe;GERMANY';
        fileattrs['DO_EMAIL'] = 'carlos.alberti@kit.edu';
        fileattrs['DS_NAME'] = 'Dubravica;Darko';
      # fileattrs['DS_AFFILIATION'] = 'Karlsruhe Institute of Technology;KIT';
        fileattrs['DS_AFFILIATION'] = 'Karlsruhe Institute of Technology - Institute of Meteorology and Climate Research - Atmospheric Trace Gases and Remote Sensing;KIT.IMK.ASF';
        fileattrs['DS_ADDRESS'] = 'P.O. Box 3640;D-76021 Karlsruhe;GERMANY';
        fileattrs['DS_EMAIL'] = 'darko.dubravica@kit.edu'

  # if iname=='VERTEX70': fileattrs['DATA_SOURCE']+='BIRA.IASB005'; fileattrs['PI_NAME']='Notholt;Justus'; fileattrs['PI_AFFILIATION']='Institut fuer Umweltphysik, Universitaet Bremen;IUP'; fileattrs['PI_ADDRESS']='Otto-Hahn-Allee 1;D-28334 Bremen;GERMANY'; fileattrs['PI_EMAIL']='jnotholt@iup.physik.uni-bremen.de'; fileattrs['DO_NAME']='Petri;Christof'; fileattrs['DO_AFFILIATION']='Institut fuer Umweltphysik, Universitaet Bremen;IUP'; fileattrs['DO_ADDRESS']='Otto-Hahn-Allee 1;D-28334 Bremen;GERMANY'; fileattrs['DO_EMAIL']='christof_p@iup.physik.uni-bremen.de'; fileattrs['DS_NAME']='Sha;Mahesh Kumar'; fileattrs['DS_AFFILIATION']='Belgian Institute for Space Aeronomy;BIRA.IASB'; fileattrs['DS_ADDRESS']='Ringlaan 3;B-1180 Brussels;BELGIUM'; fileattrs['DS_EMAIL']='mahesh.sha@aeronomie.be'
  # elif iname=='IRCUBE': fileattrs['DATA_SOURCE']+='UOW227'; fileattrs['PI_NAME']='Jones;Nicholas'; fileattrs['PI_AFFILIATION']='University of Wollongong;UOW'; fileattrs['PI_ADDRESS']='Northfields Ave Wollongong;NSW 2522;AUSTRALIA'; fileattrs['PI_EMAIL']='njones@uow.edu.au'; fileattrs['DO_NAME']='Jones;Nicholas'; fileattrs['DO_AFFILIATION']='University of Wollongong;UOW'; fileattrs['DO_ADDRESS']='Northfields Ave Wollongong;NSW 2522;AUSTRALIA'; fileattrs['DO_EMAIL']='njones@uow.edu.au'; fileattrs['DS_NAME']='Sha;Mahesh Kumar'; fileattrs['DS_AFFILIATION']='Belgian Institute for Space Aeronomy;BIRA.IASB'; fileattrs['DS_ADDRESS']='Ringlaan 3;B-1180 Brussels;BELGIUM'; fileattrs['DS_EMAIL']='mahesh.sha@aeronomie.be'
  # elif iname=='EM27SUN': fileattrs['DATA_SOURCE']+='KIT.IMK.ASF037'; fileattrs['PI_NAME']='Hase;Frank'; fileattrs['PI_AFFILIATION']='Karlsruhe Institute of Technology;KIT'; fileattrs['PI_ADDRESS']='P.O. Box 3640;D-76021 Karlsruhe;GERMANY'; fileattrs['PI_EMAIL']='frank.hase@kit.edu'; fileattrs['DO_NAME']='Alberti;Carlos'; fileattrs['DO_AFFILIATION']='Karlsruhe Institute of Technology;KIT'; fileattrs['DO_ADDRESS']='P.O. Box 3640;D-76021 Karlsruhe;GERMANY'; fileattrs['DO_EMAIL']='carlos.alberti@kit.edu'; fileattrs['DS_NAME']='Dubravica;Darko'; fileattrs['DS_AFFILIATION']='Karlsruhe Institute of Technology;KIT'; fileattrs['DS_ADDRESS']='P.O. Box 3640;D-76021 Karlsruhe;GERMANY'; fileattrs['DS_EMAIL']='darko.dubravica@kit.edu'
  # elif iname=='LHR': fileattrs['DATA_SOURCE']+='RAL.SPACE004'; fileattrs['PI_NAME']='Weidmann;Damien'; fileattrs['PI_AFFILIATION']='Rutherford Appleton Laboratory Space Department;RAL.SPACE'; fileattrs['PI_ADDRESS']='Harwell Campus Didcot;Oxfordshire OX11 0QX;UNITED KINGDOM'; fileattrs['PI_EMAIL']='damien.weidmann@stfc.ac.uk'; fileattrs['DO_NAME']='Hoffmann;Alex'; fileattrs['DO_AFFILIATION']='Rutherford Appleton Laboratory Space Department;RAL.SPACE'; fileattrs['DO_ADDRESS']='Harwell Campus Didcot;Oxfordshire OX11 0QX;UNITED KINGDOM'; fileattrs['DO_EMAIL']='alex.hoffmann@stfc.ac.uk'; fileattrs['DS_NAME']='Sha;Mahesh Kumar'; fileattrs['DS_AFFILIATION']='Belgian Institute for Space Aeronomy;BIRA.IASB'; fileattrs['DS_ADDRESS']='Ringlaan 3;B-1180 Brussels;BELGIUM'; fileattrs['DS_EMAIL']='mahesh.sha@aeronomie.be'
  # elif iname=='HR125LR': fileattrs['DATA_SOURCE']+='FMI001'; fileattrs['PI_NAME']='Kivi;Rigel'; fileattrs['PI_AFFILIATION']='Finnish Meteorological Institute;FMI'; fileattrs['PI_ADDRESS']='Tahtelantie 62;FIN-99660 Sodankyla;FINLAND'; fileattrs['PI_EMAIL']='rigel.kivi@fmi.fi'; fileattrs['DO_NAME']='Tu;Qiansi'; fileattrs['DO_AFFILIATION']='Karlsruhe Institute of Technology;KIT'; fileattrs['DO_ADDRESS']='P.O. Box 3640;D-76021 Karlsruhe;GERMANY'; fileattrs['DO_EMAIL']='qiansi.tu@kit.edu'; fileattrs['DS_NAME']='Sha;Mahesh Kumar'; fileattrs['DS_AFFILIATION']='Belgian Institute for Space Aeronomy;BIRA.IASB'; fileattrs['DS_ADDRESS']='Ringlaan 3;B-1180 Brussels;BELGIUM'; fileattrs['DS_EMAIL']='mahesh.sha@aeronomie.be'

    fileattrs['DATA_START_DATE'] = alldatetimes[0].strftime('%Y%m%dT%H%M%SZ')
    fileattrs['DATA_STOP_DATE'] = alldatetimes[-1].strftime('%Y%m%dT%H%M%SZ')
    fileattrs['DATA_FILE_VERSION'] = '%03d'%fileversion
    fileattrs['FILE_NAME'] = geomsf = ('groundbased_%s_%s_%s_%s_%s.h5'%(fileattrs['DATA_SOURCE'],fileattrs['DATA_LOCATION'],fileattrs['DATA_START_DATE'],fileattrs['DATA_STOP_DATE'],fileattrs['DATA_FILE_VERSION'])).lower()
  # fileattrs['FILE_NAME'] = geomsf = ('groundbased_%s_%s_%s_%s_%s.h5'%(fileattrs['DATA_SOURCE'],fileattrs['DATA_LOCATION'],\
  #   fileattrs['DATA_START_DATE'],fileattrs['DATA_STOP_DATE'],fileattrs['DATA_FILE_VERSION'])).lower()

  # get times, start,end time, format times, get creation time ,site name, ... 
    geomsf = os.path.join(outdir,geomsf)

#-------------------------------------------------------------------------------------------------#
# ...

    with h5py.File(geomsf,'w') as gfid:

#-------------------------------------------------------------------------------------------------#
# ...

      GEOMS_store_string(dict(name='SOURCE.PRODUCT',desc='Information relevant to the source history of the Metadata and Data in the form Original_Archive;Original_Filename;Original_File_Generation_Date',dep='INDEPENDENT',dtype='STRING'),np.array('some information'))

      GEOMS_store(dict(name='DATETIME',dtype='DOUBLE',unit='MJD2K',desc='MJD2K is 0.0 on January 1, 2000 at 00:00:00 UTC',dep='DATETIME'),fid['DateTime'][...],si='0.0;86400.0;s')

      GEOMS_store(dict(name='ANGLE.SOLAR_ZENITH.ASTRONOMICAL',dtype='REAL',unit='deg',desc='The solar astronomical zenith angle at which the measurement was taken',dep='DATETIME'),fid['Angle_zenith'][...],si='0.0;1.74533E-2;rad')
      GEOMS_store(dict(name='ANGLE.SOLAR_AZIMUTH',dtype='REAL',unit='deg',desc='The azimuth viewing direction of the instrument using north as the reference plane and increasing clockwise (0 for north 90 for east and so on)',dep='DATETIME'),fid['Angle_azimuth'][...],si='0.0;1.74533E-2;rad')

#-------------------------------------------------------------------------------------------------#
# column mixing ratios, dry air mole fraction

      GEOMS_store(dict(name='H2O.COLUMN.MIXING.RATIO.VOLUME.DRY_ABSORPTION.SOLAR',dtype='REAL',unit='ppmv',desc='Column average dry air mole fraction',dep='DATETIME'),fid['XH2O'][...],si='0.0;1.0E-6;1')
      GEOMS_store(dict(name='CO2.COLUMN.MIXING.RATIO.VOLUME.DRY_ABSORPTION.SOLAR',dtype='REAL',unit='ppmv',desc='Column average dry air mole fraction',dep='DATETIME'),fid['XCO2'][...],si='0.0;1.0E-6;1')
      GEOMS_store(dict(name='CH4.COLUMN.MIXING.RATIO.VOLUME.DRY_ABSORPTION.SOLAR',dtype='REAL',unit='ppmv',desc='Column average dry air mole fraction',dep='DATETIME'),fid['XCH4'][...],si='0.0;1.0E-6;1')
      GEOMS_store(dict(name='CO.COLUMN.MIXING.RATIO.VOLUME.DRY_ABSORPTION.SOLAR', dtype='REAL',unit='ppbv',desc='Column average dry air mole fraction',dep='DATETIME'),fid['XCO'][...]*1000.0,si='0.0;1.0E-9;1')

    # if 'XH2O' in fid: GEOMS_store(dict(name='H2O.COLUMN.MIXING.RATIO.VOLUME.DRY_ABSORPTION.SOLAR',dtype='REAL',unit='ppmv',desc='Column average dry air mole fraction',dep='DATETIME'),fid['XH2O'][...],si='0.0;1.0E-6;1')
    # if 'XCO2' in fid: GEOMS_store(dict(name='CO2.COLUMN.MIXING.RATIO.VOLUME.DRY_ABSORPTION.SOLAR',dtype='REAL',unit='ppmv',desc='Column average dry air mole fraction',dep='DATETIME'),fid['XCO2'][...],si='0.0;1.0E-6;1')
    # if 'XCH4' in fid: GEOMS_store(dict(name='CH4.COLUMN.MIXING.RATIO.VOLUME.DRY_ABSORPTION.SOLAR',dtype='REAL',unit='ppmv',desc='Column average dry air mole fraction',dep='DATETIME'),fid['XCH4'][...],si='0.0;1.0E-6;1')
    # if 'XCO' in fid: GEOMS_store(dict(name='CO.COLUMN.MIXING.RATIO.VOLUME.DRY_ABSORPTION.SOLAR', dtype='REAL',unit='ppbv',desc='Column average dry air mole fraction',dep='DATETIME'),fid['XCO'][...]*1000.0,si='0.0;1.0E-9;1')

#-------------------------------------------------------------------------------------------------#
# column mixing ratios, dry air mole fraction error (uncertainty)

      AvgNr = 11
      ErrNr = int(AvgNr / 2)

    # moving mean

      XH2O_mean = np.zeros(fid['DateTime'].shape)
      XCO2_mean = np.zeros(fid['DateTime'].shape)
      XCH4_mean = np.zeros(fid['DateTime'].shape)
      XCO_mean = np.zeros(fid['DateTime'].shape)

      for i in range(fid['DateTime'].shape[0]-AvgNr+1):

        XH2O_mean_tmp = 0.0
        XCO2_mean_tmp = 0.0
        XCH4_mean_tmp = 0.0
        XCO_mean_tmp = 0.0

        for j in range(AvgNr):

          XH2O_mean_tmp += float(fid['XH2O'][i+j])
          XCO2_mean_tmp += float(fid['XCO2'][i+j])
          XCH4_mean_tmp += float(fid['XCH4'][i+j])
          XCO_mean_tmp += float(fid['XCO'][i+j])

        XH2O_mean[i+ErrNr] = XH2O_mean_tmp / float(AvgNr)
        XCO2_mean[i+ErrNr] = XCO2_mean_tmp / float(AvgNr)
        XCH4_mean[i+ErrNr] = XCH4_mean_tmp / float(AvgNr)
        XCO_mean[i+ErrNr] = XCO_mean_tmp / float(AvgNr)

      for i in range(ErrNr):

        XH2O_mean[i] = XH2O_mean[ErrNr]
        XCO2_mean[i] = XCO2_mean[ErrNr]
        XCH4_mean[i] = XCH4_mean[ErrNr]
        XCO_mean[i] = XCO_mean[ErrNr]

      for i in range(ErrNr):

        XH2O_mean[fid['DateTime'].shape[0]-i-1] = XH2O_mean[fid['DateTime'].shape[0]-ErrNr-1]
        XCO2_mean[fid['DateTime'].shape[0]-i-1] = XCO2_mean[fid['DateTime'].shape[0]-ErrNr-1]
        XCH4_mean[fid['DateTime'].shape[0]-i-1] = XCH4_mean[fid['DateTime'].shape[0]-ErrNr-1]
        XCO_mean[fid['DateTime'].shape[0]-i-1] = XCO_mean[fid['DateTime'].shape[0]-ErrNr-1]

    # error calculation

      XH2O_err = np.zeros(fid['DateTime'].shape)
      XCO2_err = np.zeros(fid['DateTime'].shape)
      XCH4_err = np.zeros(fid['DateTime'].shape)
      XCO_err = np.zeros(fid['DateTime'].shape)

      for i in range(fid['DateTime'].shape[0]-AvgNr+1):

        XH2O_err_tmp = 0.0
        XCO2_err_tmp = 0.0
        XCH4_err_tmp = 0.0
        XCO_err_tmp = 0.0

        for j in range(AvgNr):

          XH2O_err_tmp += np.power(float(fid['XH2O'][i+j]) - XH2O_mean[i+j], 2)
          XCO2_err_tmp += np.power(float(fid['XCO2'][i+j]) - XCO2_mean[i+j], 2)
          XCH4_err_tmp += np.power(float(fid['XCH4'][i+j]) - XCH4_mean[i+j], 2)
          XCO_err_tmp += np.power(float(fid['XCO'][i+j]) - XCO_mean[i+j], 2)

        XH2O_err[i+ErrNr] = np.sqrt(XH2O_err_tmp / float(AvgNr-1))
        XCO2_err[i+ErrNr] = np.sqrt(XCO2_err_tmp / float(AvgNr-1))
        XCH4_err[i+ErrNr] = np.sqrt(XCH4_err_tmp / float(AvgNr-1))
        XCO_err[i+ErrNr] = np.sqrt(XCO_err_tmp / float(AvgNr-1)) * 1000.0

    # uncertainty for the last entry (for each species)

      for i in range(ErrNr):

        XH2O_err[i] = XH2O_err[ErrNr]
        XCO2_err[i] = XCO2_err[ErrNr]
        XCH4_err[i] = XCH4_err[ErrNr]
        XCO_err[i] = XCO_err[ErrNr]

      for i in range(ErrNr):

        XH2O_err[fid['DateTime'].shape[0]-i-1] = XH2O_err[fid['DateTime'].shape[0]-ErrNr-1]
        XCO2_err[fid['DateTime'].shape[0]-i-1] = XCO2_err[fid['DateTime'].shape[0]-ErrNr-1]
        XCH4_err[fid['DateTime'].shape[0]-i-1] = XCH4_err[fid['DateTime'].shape[0]-ErrNr-1]
        XCO_err[fid['DateTime'].shape[0]-i-1] = XCO_err[fid['DateTime'].shape[0]-ErrNr-1]

      GEOMS_store(dict(name='H2O.COLUMN.MIXING.RATIO.VOLUME.DRY_ABSORPTION.SOLAR_UNCERTAINTY.RANDOM.STANDARD',dtype='REAL',unit='ppmv',desc='Total random uncertainty on the retrieved total column (expressed in same units as the column)',dep='DATETIME'),XH2O_err,si='0.0;1.0E-6;1')
      GEOMS_store(dict(name='CO2.COLUMN.MIXING.RATIO.VOLUME.DRY_ABSORPTION.SOLAR_UNCERTAINTY.RANDOM.STANDARD',dtype='REAL',unit='ppmv',desc='Total random uncertainty on the retrieved total column (expressed in same units as the column)',dep='DATETIME'),XCO2_err,si='0.0;1.0E-6;1')
      GEOMS_store(dict(name='CH4.COLUMN.MIXING.RATIO.VOLUME.DRY_ABSORPTION.SOLAR_UNCERTAINTY.RANDOM.STANDARD',dtype='REAL',unit='ppmv',desc='Total random uncertainty on the retrieved total column (expressed in same units as the column)',dep='DATETIME'),XCH4_err,si='0.0;1.0E-6;1')
      GEOMS_store(dict(name='CO.COLUMN.MIXING.RATIO.VOLUME.DRY_ABSORPTION.SOLAR_UNCERTAINTY.RANDOM.STANDARD', dtype='REAL',unit='ppbv',desc='Total random uncertainty on the retrieved total column (expressed in same units as the column)',dep='DATETIME'),XCO_err,si='0.0;1.0E-9;1')

    # if 'XH2O_rms' in fid: GEOMS_store(dict(name='H2O.COLUMN.MIXING.RATIO.VOLUME.DRY_ABSORPTION.SOLAR_UNCERTAINTY.RANDOM.STANDARD',dtype='REAL',unit='ppmv',desc='Total random uncertainty on the retrieved total column (expressed in same units as the column)',dep='DATETIME'),fid['XH2O_rms'][...],si='0.0;1.0E-6;1')
    # if 'XCO2_rms' in fid: GEOMS_store(dict(name='CO2.COLUMN.MIXING.RATIO.VOLUME.DRY_ABSORPTION.SOLAR_UNCERTAINTY.RANDOM.STANDARD',dtype='REAL',unit='ppmv',desc='Total random uncertainty on the retrieved total column (expressed in same units as the column)',dep='DATETIME'),fid['XCO2_rms'][...],si='0.0;1.0E-6;1')
    # if 'XCH4_rms' in fid: GEOMS_store(dict(name='CH4.COLUMN.MIXING.RATIO.VOLUME.DRY_ABSORPTION.SOLAR_UNCERTAINTY.RANDOM.STANDARD',dtype='REAL',unit='ppmv',desc='Total random uncertainty on the retrieved total column (expressed in same units as the column)',dep='DATETIME'),fid['XCH4_rms'][...],si='0.0;1.0E-6;1')
    # if 'XCO_rms' in fid: GEOMS_store(dict(name='CO.COLUMN.MIXING.RATIO.VOLUME.DRY_ABSORPTION.SOLAR_UNCERTAINTY.RANDOM.STANDARD', dtype='REAL',unit='ppbv',desc='Total random uncertainty on the retrieved total column (expressed in same units as the column)',dep='DATETIME'),fid['XCO_rms'][...],si='0.0;1.0E-9;1')

#-------------------------------------------------------------------------------------------------#
# ...

      Y = np.zeros(fid['DateTime'].shape)

      X = np.zeros(fid['DateTime'].shape+fid['H_prior'].shape)

      prior_index_map = np.zeros(fid['DateTime'].shape+fid['H_prior'].shape)

#-------------------------------------------------------------------------------------------------#
# ...

      for i in range(fid['DateTime'].shape[0]): Y[i] = fid['Instrument_latitude'][...]

      GEOMS_store(dict(name='LATITUDE.INSTRUMENT',dtype='REAL',unit='deg',desc='Instrument geolocation (+ for north; - for south)',dep='DATETIME'),Y,si='0.0;1.74533E-2;rad')

      for i in range(fid['DateTime'].shape[0]): Y[i] = fid['Instrument_longitude'][...]

      GEOMS_store(dict(name='LONGITUDE.INSTRUMENT',dtype='REAL',unit='deg',desc='Instrument geolocation (+ for east; - for west)',dep='DATETIME'),Y,si='0.0;1.74533E-2;rad')

      for i in range(fid['DateTime'].shape[0]): Y[i] = fid['Instrument_altitude'][...]

      GEOMS_store(dict(name='ALTITUDE.INSTRUMENT',dtype='REAL',unit='km',desc='Instrument geolocation',dep='DATETIME'),Y,si='0.0;1.0E3;m')

      P_sur_str = []
      P_ind_str = []
      T_ind_str = []
      N_den_str = []
      M_h2o_str = []
      M_gas_str = []

      for i in range(fid['DateTime'].shape[0]):
        Y[i] = fid['P_ground'][i]
        P_sur_str.append("Datalogger") # local meteo station
        P_ind_str.append("Pressure profile from NCEP at local noon")
        T_ind_str.append("Temperature profile from NCEP at local noon")
        N_den_str.append("Dry air number density profile from NCEP at local noon")
        M_h2o_str.append("Total vertical column of H2O from NCEP at local noon")
        M_gas_str.append("Map file GFIT Code")

      GEOMS_store(dict(name='SURFACE.PRESSURE_INDEPENDENT',dtype='REAL',unit='hPa',desc='Surface/ground pressure',dep='DATETIME'),Y,si='0.0;1.0E2;kg m-1 s-2')
      GEOMS_store_string(dict(name='SURFACE.PRESSURE_INDEPENDENT_SOURCE',desc='Surface pressure profile source (e.g. Mercury barometer etc.)',dep='DATETIME',dtype='STRING'),np.array(P_sur_str))
      GEOMS_store_string(dict(name='PRESSURE_INDEPENDENT_SOURCE',desc='Pressure profile source (hydrostatic)',dep='DATETIME',dtype='STRING'),np.array(P_ind_str))
      GEOMS_store_string(dict(name='TEMPERATURE_INDEPENDENT_SOURCE',desc='Temperature profile source (e.g. Lidar NCEP Sonde ECMWF etc.)',dep='DATETIME',dtype='STRING'),np.array(T_ind_str))
      GEOMS_store_string(dict(name='DRY.AIR.NUMBER.DENSITY_INDEPENDENT_SOURCE',desc='Dry air number density profile source (hydrostatic)',dep='DATETIME',dtype='STRING'),np.array(N_den_str))

      GEOMS_store_string(dict(name='H2O.MIXING.RATIO.VOLUME.DRY_APRIORI.SOURCE',desc='Source of the vertical profile of a-priori per layer',dep='DATETIME',dtype='STRING'),np.array(M_h2o_str))
      GEOMS_store_string(dict(name='CO2.MIXING.RATIO.VOLUME.DRY_APRIORI.SOURCE',desc='Source of the vertical profile of a-priori per layer',dep='DATETIME',dtype='STRING'),np.array(M_gas_str))
      GEOMS_store_string(dict(name='CH4.MIXING.RATIO.VOLUME.DRY_APRIORI.SOURCE',desc='Source of the vertical profile of a-priori per layer',dep='DATETIME',dtype='STRING'),np.array(M_gas_str))
      GEOMS_store_string(dict(name='CO.MIXING.RATIO.VOLUME.DRY_APRIORI.SOURCE',desc='Source of the vertical profile of a-priori per layer',dep='DATETIME',dtype='STRING'),np.array(M_gas_str))

#-------------------------------------------------------------------------------------------------#
# ...

    # H_len = len(fid['H_prior']) - 1

      for i in range(fid['DateTime'].shape[0]):
        for j in range(fid['H_prior'].shape[0]):
          X[i][j] = fid['H_prior'][j]
        # X[i][H_len-j] = fid['H_prior'][j]

      GEOMS_store(dict(name='ALTITUDE',dtype='REAL',unit='km',desc='A-priori altitude profile matrix. Values are monotonically increasing',dep='DATETIME;ALTITUDE'),X,si='0.0;1.0E3;m')

      for i in range(fid['DateTime'].shape[0]):
        for j in range(fid['H_prior'].shape[0]):
          X[i][j] = fid['P_prior'][j]
        # X[i][H_len-j] = fid['P_prior'][j]

      GEOMS_store(dict(name='PRESSURE_INDEPENDENT',dtype='REAL',unit='hPa',desc='Effective air pressure at each altitude',dep='DATETIME;ALTITUDE'),X,si='0.0;1.0E2;kg m-1 s-2')

      for i in range(fid['DateTime'].shape[0]):
        for j in range(fid['H_prior'].shape[0]):
          X[i][j] = fid['T_prior'][j]
        # X[i][H_len-j] = fid['T_prior'][j]

      GEOMS_store(dict(name='TEMPERATURE_INDEPENDENT',dtype='REAL',unit='K',desc='Effective air temperature at each altitude',dep='DATETIME;ALTITUDE'),X,si='0.0;1.0;K')

      for i in range(fid['DateTime'].shape[0]):
        for j in range(fid['H_prior'].shape[0]):
          X[i][j] = fid['N_Dry_prior'][j]
        # X[i][H_len-j] = fid['N_Dry_prior'][j]

      GEOMS_store(dict(name='DRY.AIR.NUMBER.DENSITY_INDEPENDENT',dtype='REAL',unit='molec cm-3',desc='Dry air number density profile',dep='DATETIME;ALTITUDE'),X,si='0.0;1.66054E-18;mol m-3')

      for i in range(fid['DateTime'].shape[0]):
        sum1 = 0.0
        sum2 = 0.0

        for j in range(fid['H_prior'].shape[0]):
          if j < len(fid['H_prior'])-1:

            h1 = float(fid['H_prior'][j]) * 1000.0 # km -> m
            h2 = float(fid['H_prior'][j+1]) * 1000.0 # km -> m

            n1_dry = float(fid['N_Dry_prior'][j])
            n2_dry = float(fid['N_Dry_prior'][j+1])
            sc_dry = (h2-h1) / math.log(n1_dry/n2_dry)
            n0_dry = n1_dry * math.exp(h1/sc_dry)

            Col1 = n0_dry * sc_dry * math.exp(-(h1/sc_dry))
            Col2 = n0_dry * sc_dry * math.exp(-(h2/sc_dry))

            X[i][j] = 100.0 * (Col1 - Col2)
          # X[i][H_len-j] = 100.0 * (Col1 - Col2)

            sum1 += X[i][j]
          # sum1 += X[i][H_len-j]
            sum2 += float(fid['C_prior'][j])

          else:
            X[i][j] = 0
          # X[i][H_len-j] = 0
            sum1 += X[i][j]
          # sum1 += X[i][H_len-j]
            sum2 += float(fid['C_prior'][j])

      GEOMS_store(dict(name='DRY.AIR.COLUMN.PARTIAL_INDEPENDENT',dtype='REAL',unit='Zmolec cm-2',desc='Vertical profile of partial columns of air number densities (for conversion between VMR and partial column profile)',dep='DATETIME;ALTITUDE'),X,si='0.0;1.66054E1;mol m-2')

#-------------------------------------------------------------------------------------------------#
# prior mixing ratios

    # H_len = len(fid['H_prior']) - 1

      for i in range(fid['DateTime'].shape[0]):
        for j in range(fid['H_prior'].shape[0]):
          X[i][j] = fid['H2O_prior'][j]       # * 1E6 # ppm
        # X[i][H_len-j] = fid['H2O_prior'][j] # * 1E6 # ppm

      GEOMS_store(dict(name='H2O.MIXING.RATIO.VOLUME.DRY_APRIORI',dtype='REAL',unit='ppmv',desc='A-priori total vertical column of target gas',dep='DATETIME;ALTITUDE'),X,si='0.0;1.0E-6;1')

      for i in range(fid['DateTime'].shape[0]):
        for j in range(fid['H_prior'].shape[0]):
          X[i][j] = fid['CO2_prior'][j]       # * 1E6 # ppm
        # X[i][H_len-j] = fid['CO2_prior'][j] # * 1E6 # ppm

      GEOMS_store(dict(name='CO2.MIXING.RATIO.VOLUME.DRY_APRIORI',dtype='REAL',unit='ppmv',desc='A-priori total vertical column of target gas',dep='DATETIME;ALTITUDE'),X,si='0.0;1.0E-6;1')

      for i in range(fid['DateTime'].shape[0]):
        for j in range(fid['H_prior'].shape[0]):
          X[i][j] = fid['CH4_prior'][j] * 1000.0       # * 1E9 # ppb
        # X[i][H_len-j] = fid['CH4_prior'][j] * 1000.0 # * 1E9 # ppb

      GEOMS_store(dict(name='CH4.MIXING.RATIO.VOLUME.DRY_APRIORI',dtype='REAL',unit='ppbv',desc='A-priori total vertical column of target gas',dep='DATETIME;ALTITUDE'),X,si='0.0;1.0E-9;1')

      for i in range(fid['DateTime'].shape[0]):
        for j in range(fid['H_prior'].shape[0]):
          X[i][j] = fid['CO_prior'][j] * 1000.0       # * 1E9 # ppb
        # X[i][H_len-j] = fid['CO_prior'][j] * 1000.0 # * 1E9 # ppb

      GEOMS_store(dict(name='CO.MIXING.RATIO.VOLUME.DRY_APRIORI',dtype='REAL',unit='ppbv',desc='A-priori total vertical column of target gas',dep='DATETIME;ALTITUDE'),X,si='0.0;1.0E-9;1')

#-------------------------------------------------------------------------------------------------#
# sensitivities (interpolation)

      X = np.zeros(fid['DateTime'].shape+fid['H_sens'].shape)

#-------------------------------------------------------------------------------------------------#
# ...

    # H_len = len(fid['H_sens']) - 1

      for i in range(fid['DateTime'].shape[0]):
        for j in range(fid['H_sens'].shape[0]):
          X[i][j] = fid['H2O_int'][i][j]
        # X[i][H_len-j] = fid['H2O_int'][i][j]

      GEOMS_store(dict(name='H2O.COLUMN_ABSORPTION.SOLAR_AVK',dtype='REAL',unit='1',desc='Column sensitivity associated with the total vertical column of the target gas',dep='DATETIME;ALTITUDE'),X,si='0.0;1.0;1')

      for i in range(fid['DateTime'].shape[0]):
        for j in range(fid['H_sens'].shape[0]):
          X[i][j] = fid['CO2_int'][i][j]
        # X[i][H_len-j] = fid['CO2_int'][i][j]

      GEOMS_store(dict(name='CO2.COLUMN_ABSORPTION.SOLAR_AVK',dtype='REAL',unit='1',desc='Column sensitivity associated with the total vertical column of the target gas',dep='DATETIME;ALTITUDE'),X,si='0.0;1.0;1')

      for i in range(fid['DateTime'].shape[0]):
        for j in range(fid['H_sens'].shape[0]):
          X[i][j] = fid['CH4_int'][i][j]
        # X[i][H_len-j] = fid['CH4_int'][i][j]

      GEOMS_store(dict(name='CH4.COLUMN_ABSORPTION.SOLAR_AVK',dtype='REAL',unit='1',desc='Column sensitivity associated with the total vertical column of the target gas',dep='DATETIME;ALTITUDE'),X,si='0.0;1.0;1')

      for i in range(fid['DateTime'].shape[0]):
        for j in range(fid['H_sens'].shape[0]):
          X[i][j] = fid['CO_int'][i][j]
        # X[i][H_len-j] = fid['CO_int'][i][j]

      GEOMS_store(dict(name='CO.COLUMN_ABSORPTION.SOLAR_AVK',dtype='REAL',unit='1',desc='Column sensitivity associated with the total vertical column of the target gas',dep='DATETIME;ALTITUDE'),X,si='0.0;1.0;1')

#-------------------------------------------------------------------------------------------------#
# file attributes

      for key,v in fileattrs.items(): gfid.attrs[key.upper()] = np.array(v)

      gfid.attrs['DATA_DESCRIPTION'] = np.array('%s measurements from %s '%(str(fid['Instrument_name'][...]),str(fid['Site_name'][...]).lower()))
      gfid.attrs['DATA_VARIABLES'] = np.array(';'.join(variableswritten))
      gfid.attrs['DATA_TEMPLATE'] = np.array(os.path.basename(os.path.splitext(template_path)[0]))
    # gfid.attrs['DATA_TEMPLATE'] = np.array(os.path.basename(os.path.splitext(template_path)[0]).replace('-VA',''))
      gfid.attrs['DATA_QUALITY'] = np.array('Campaign data')
      gfid.attrs['DATA_PROCESSOR'] = np.array(fid.attrs['DATA_PROCESSOR'])
      gfid.attrs['FILE_GENERATION_DATE'] = np.array(datetime.datetime.now().strftime('%Y%m%dT%H%M%SZ'))
      gfid.attrs['FILE_ACCESS'] = np.array('COCCON')
      gfid.attrs['FILE_DOI'] = np.array(doi_address)
      gfid.attrs['FILE_META_VERSION'] = np.array('04R052;CUSTOM')
    # gfid.attrs['FILE_META_VERSION'] = np.array('%s;CUSTOM'%('04R052' if True else os.path.basename(os.path.splitext(table_path)[0]).split('_')[1]))
      gfid.attrs['FILE_PROJECT_ID'] = np.array('COCCON')

#-------------------------------------------------------------------------------------------------#
# HDF5 to HDF4 GEOMS

  mydef.hdf5tohdf4(geomsf)

  return geomsf

#-------------------------------------------------------------------------------------------------#
#=================================================================================================#
