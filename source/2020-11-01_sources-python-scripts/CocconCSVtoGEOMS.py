# -*- coding: utf-8 -*-
#=================================================================================================#
#-------------------------------------------------------------------------------------------------#
# Python Script: CocconCSVtoGEOMS.py
# Version/Date:  V01 (01.10.2020)
# Project:       COCCON-PROCEEDS, FRM4GHG, and S5P-MPC funded by ESA 
# Created by:    Darko Dubravica, Karlsruhe Institute of Technology (KIT), Germany
# Description:   Convert CVS format to GEOMS 
#-------------------------------------------------------------------------------------------------#
#=================================================================================================#


#=================================================================================================#
#-------------------------------------------------------------------------------------------------#
# import modules/packages

import os               # operating system
import CocconCSVtoHDF   # CSV to HDF format
import CocconHDFtoGEOMS # HDF to GEOMS format
from glob import glob   # ...

#-------------------------------------------------------------------------------------------------#
#=================================================================================================#


#=================================================================================================#
#-------------------------------------------------------------------------------------------------#

temp_file = 'GEOMS-TE-FTIR-COCCON-001.csv'
tabl_file = 'tableattrvalue_04R052.dat'

site_file = 'sodankyla'

inst_file = 'EM27SUN'

site_hdf = site_file + '_' + inst_file + '_hdfout.hdf'

#-------------------------------------------------------------------------------------------------#
#

ana_path = r'D:\prf96-EM27-fast\analysis\sod2017_em27sn039'
out_path = r'D:\prf96-EM27-fast\out_fast\sod2017_em27sn039'

#-------------------------------------------------------------------------------------------------#
#=================================================================================================#


#=================================================================================================#
#-------------------------------------------------------------------------------------------------#
# count number of lines

def file_len(fname):
    with open(fname) as f:
        for i, l in enumerate(f):
            pass
    return i + 1

#-------------------------------------------------------------------------------------------------#
#=================================================================================================#


#=================================================================================================#
#-------------------------------------------------------------------------------------------------#
# merge all output files

inv_list = glob(out_path + '\\' + '*invparms.dat') # invparms file list
sen_list = glob(out_path + '\\' + '*colsens.dat')  # colsens file list
inv_list_len = len(inv_list)                       # invparms file list length
sen_list_len = len(sen_list)                       # colsens file list length

if (inv_list_len != 0) and (sen_list_len != 0):

  print ''
  print '================================================================================'
  print '--------------------------------------------------------------------------------'
  print 'out_path: ', out_path
  print 'ana_path: ', ana_path
  print 'inv_list_len: ', inv_list_len
  print 'sen_list_len: ', sen_list_len
  if (inv_list_len != sen_list_len): print 'inv_list_len != sen_list_len !!!'

# for file in file_list:
#   print(file)

  for i in range(inv_list_len):
    inv_file = inv_list[i]
    sen_file = inv_file[:-12] + 'colsens.dat'
    date = inv_file[-19:-13]

    ptf_file = os.path.join(ana_path,date,'pt','pT_fast_out.dat')
    vmr_file = os.path.join(ana_path,date,'pt','VMR_fast_out.dat')

    site_path = os.path.join(out_path,site_file)
    inst_path = os.path.join(site_path,inst_file)

    print '--------------------------------------------------------------------------------'
    print 'date: ', date
    print '--------------------------------------------------------------------------------'

    if os.path.exists(sen_file) and os.path.exists(ptf_file) and os.path.exists(vmr_file):
      print 'inv_file: ', inv_file
      print 'sen_file: ', sen_file
      print 'ptf_file: ', ptf_file
      print 'vmr_file: ', vmr_file
      print '--------------------------------------------------------------------------------'

      if not os.path.exists(site_path): os.mkdir(site_path)
      if not os.path.exists(inst_path): os.mkdir(inst_path)

      if file_len(inv_file) < 12: print 'file_len: ', file_len(inv_file); continue
      else: print 'file_len: ', file_len(inv_file)

      print '--------------------------------------------------------------------------------'

      CocconCSVtoHDF.CSVtoHDF(main_path=out_path, site=site_file, instrument='EM27SUN', file_dat=inv_file, file_sen=sen_file, file_ptf=ptf_file, file_vmr=vmr_file)
      CocconHDFtoGEOMS.HDFtoGEOMS(main_path=out_path, site_path=inst_path, file_hdf=site_hdf, strict=True, table=tabl_file, template=temp_file, fileversion=1)
#     CocconCSVtoHDF.CSVtoHDF(main_path=out_path, site='karlsruhe', instrument='EM27SUN', file_dat=inv_file, file_sen=sen_file, file_ptf=ptf_file, file_vmr=vmr_file)
#     CocconHDFtoGEOMS.HDFtoGEOMS(main_path=out_path, site_path=inst_path, file_hdf='karlsruhe_EM27SUN_hdfout.hdf', strict=True, table=tabl_file, template=temp_file, fileversion=1)

    else:
      print 'File Does NOT Exist !!!'
      print 'sen_file: ', sen_file
      print ''

  print '--------------------------------------------------------------------------------'
  print '================================================================================'

else:
  print '================================================================================'
  print '--------------------------------------------------------------------------------'
  print("File List Empty or ... !!!")
  print '--------------------------------------------------------------------------------'
  print '================================================================================'

#-------------------------------------------------------------------------------------------------#
#=================================================================================================#
