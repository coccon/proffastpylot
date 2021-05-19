# -*- coding: utf-8 -*-
#==================================================================================================================#
#------------------------------------------------------------------------------------------------------------------#
# Python Script: CocconHeader.py
# Version/Date:  V01 (01.10.2020)
# Project:       COCCON-PROCEEDS, FRM4GHG, and S5P-MPC funded by ESA 
# Created by:    Mahesh Kumar Sha & Bavo Langerock, Royal Belgian Institute for Space Aeronomy (BIRA-IASB), Belgium
# Modified by:   Darko Dubravica, Karlsruhe Institute of Technology (KIT), Germany
# Description:   Converts CSV format to HDF format
#------------------------------------------------------------------------------------------------------------------#
#==================================================================================================================#


#==================================================================================================================#
#------------------------------------------------------------------------------------------------------------------#
# import modules/packages

import os, h5py, time, shutil, glob, math, re
import numpy as np
import datetime as dt
import pyhdf
import pyhdf.SD as SD
import nested_dict as nd
import CocconClass as myclass

#------------------------------------------------------------------------------------------------------------------#
#==================================================================================================================#


#==================================================================================================================#
#-------------------------------------------------------------------------------------------------#
# Transforms GEOMS DATETIME variable to dt.datetime instances (input is seconds, since 1/1/2000 at 0UT)

def GEOMStoDateTime(times):

  times = times / 86400.
  ntimes = []

  for t in times:
    tmptim = dt.datetime.fromordinal(dt.date(2000,1,1).toordinal()+int(t))
  # in days because dt.fromordinal forgets seconds???
    ntimes.append(tmptim+dt.timedelta(days=(t-math.floor(t))))

  return np.array(ntimes);

#-------------------------------------------------------------------------------------------------#
# Transforms dt.datetime instances to GEOMS DATETIME (output is seconds, since 1/1/2000 at 0UT)

def DateTimeToGEOMS(times):

  gtimes = np.array([np.longdouble(t.toordinal())+(t.hour+(t.minute+(t.second+t.microsecond/1e6)/(60.))/60.)/24.-dt.date(2000,1,1).toordinal() for t in times])

  return gtimes * 86400;

#-------------------------------------------------------------------------------------------------#
# Expands a dict as a 1-depth dict (i.e. values are not dicts) with concatenated keys separator='/'.
# The meta='attr' keywords filters out subdicts with key meta, and constructs 1 flattened dict

def expand_dict(d,meta='attr',separator='/'):

  dd = d.copy(); attr = {}

  if meta in dd:
    attr = d[meta];
    del dd[meta];

  while any([isinstance(v,dict) for v in dd.values()]):
    for k,v in dd.items():
      if isinstance(v,dict):
        try: localattr = v.pop(meta);
        except KeyError: localattr = {}

        attr.setdefault(k,{}).update(localattr)

        for kk,vv in v.items():
          dd.update({separator.join([str(k),str(kk)]):vv});
          if kk in attr[k]: attr.update({separator.join([str(k),str(kk)]):attr[k][kk]})

        del dd[k]; del attr[k] 

  return dd,attr;

#-------------------------------------------------------------------------------------------------#
# Store a string,bool,np.array,list,datetime (as tuple),dict to a HDF5 datafile hdfid, with name arrayname
# When Saving a dict instance, the keys are transformed to (sub)groups. 
# If the dict has an 'attrs' attribute then attributes are set according to this attribute dict (must have the same keys...)
#-------------------------------------------------------------------------------------------------#
# Input arguments::
#   hdfid: h5py openend file
#   arrayname = '', where to store the data in the file
#   value = data to save;;
# Optional key arguments::
#  dtype = 'f'(='float32'), 'f8'(='float64'), or 's', 'ref' (a hdf reference) or 'vars' (variable length string),...
#  kargs are stored in the attrs of the dataset (for a dict instance, all values will get these attr...);;
#-------------------------------------------------------------------------------------------------#

def hdf_store(hdfid, arrayname='', value=np.array([]), dtype='f', **kargs):
#def hdf_store(hdfid, arrayname='', value=array([]), dtype='f', logger=rootlogger, **kargs):

  extraat = {}
# logger = getlogger(logger,'hdf_store')

  if hdfid == None: return
##elif hdfid==str: hdfid=h5Py.File(hdfid,'w')

  if dtype == 'vars': dtype = h5py.special_dtype(vlen=str)
  elif dtype == 'ref': dtype = h5py.special_dtype(ref=h5py.RegionReference)

  if isinstance(value,dict):
    if type(value) == nd.nested_dict or type(value) == myclass.dataDict:
      if type(value) == nd.nested_dict:
        value = value.flatten()
        attr = nd.nested_dict(value.attrs) if hasattr(value,'attrs') else {}
##      logger.debug('Found attributes for %s'%', '.join(attr.keys())) # make the attr a nested dict, for key lookup
      else:
        value,attr = expand_dict(value,meta='attr') # for compatibility reasons ...
#       attr = nd.nested_dict(value.attrs) if hasattr(value,'attrs') else {} ###
        attr = value.attrs

      for k,v in value.items():
        extraat = {}; dtype = 'f'

        if type(v) in [int,bool]: v = np.array(int(v)); dtype = 'i'
        elif type(v) == float: v = np.array(v); dtype = 'f'
        elif type(v) == dt.datetime or type(v) == dt.date:
          v = np.array(list(v.timetuple()[:7])); dtype = 'i'; extraat.update({'units':'Year,Month,Day,hour,minutes,seconds,microseconds'})
        elif isinstance(v,str): v = np.array(v); dtype = v.dtype.str.replace('|','') # dtype = 'S%d'%len(v)
        elif type(v) in (list,tuple):
          if any([type(i) != float for i in v]): dtype = h5py.special_dtype(vlen=str); v = np.array(map(str,v));
          else: dtype = 'f'; v = np.array(v)
        elif type(v) == np.ndarray: dtype = v.dtype.name[0];

        if dtype in ('S','O'): dtype = h5py.special_dtype(vlen=str) # try this ...
#       if dtype in ('s','o'): dtype = h5py.special_dtype(vlen=str) # try this ...
        elif dtype == 'f' and v.dtype == np.longdouble: v = v.astype(np.float64); dtype = 'f8'
#       elif dtype == 'f' and v.dtype == np.float128: v = v.astype(np.float64); dtype = 'f8'
      # else: dtype = v.dtype
        elif type(v) == np.longdouble: v = (v.astype(np.float64)); dtype = 'f8'
#       elif type(v) == np.float128: v = (v.astype(np.float64)); dtype = 'f8'

#       try: if array_equal(v,None) or v.nbytes == 0: continue
#       except AttributeError: logger.error('The value for %s does not have a nbytes attribute: %s'%(k,v))

#       if k[-1] == '/': logger.error('There is a bad key in this dict %s=%s, %s'%(k,type(v),v.shape)); continue
#       logger.debug('k=%s,dtype=%s,v.dtype=%s'%(k,dtype,v.dtype if hasattr(v,'dtype') else None))

        d = hdfid.create_dataset(arrayname+'/'+k,v.shape,dtype=dtype)

        d[...] = v
#       try: d[...] = v
#       except TypeError: logger.error('%s: dtype=%s, trying to save with dtype %s'%(k,type(v),dtype));raise
#       except ValueError: logger.error('%s: dtype=%s, trying to save with dtype %s, shape=%s'%(k,type(v),dtype,v.shape));raise

        for kk,vv in kargs.items() + extraat.items(): d.attrs[kk] = vv

#       if k in attr:
        if k in attr and isinstance(attr[k],dict):
          for kk,vv in attr[k].items():
            if isinstance(vv,str):
              d.attrs[kk] = np.array(vv,dtype=str)
            else:
              d.attrs[kk] = vv
#         return;

    elif type(value) in [list,tuple,int,str,bool,float,h5py.h5r.RegionReference]:
      value = np.array(value)
    elif type(value) == dt.datetime or type(value) == dt.date:
      value = np.array(list(value.timetuple()[:7])); dtype='i'; extraat.update({'units':'Year,Month,Day,hour,minutes,seconds,microseconds'})
      d = hdfid.create_dataset(arrayname,value.shape,dtype=dtype)
      d[...] = value.astype(dtype)
#     try: d[...] = value.astype(dtype)
#     except TypeError: rootlogger.error('%s: dtype=%s, trying to save with dtype %s, value=%s'%(arrayname,type(value),dtype,value[0])); raise
#     except ValueError: rootlogger.error('%s: dtype=%s,%s, trying to save with dtype %s, shape=%s'%(arrayname,type(value),value.dtype,dtype,value.shape)); raise

      for k,v in kargs.items() + extraat.items():
        if isinstance(v,str): d.attrs[k] = np.array(v,dtype=str) # for compatability with coda...
        else: d.attrs[k] = v
        return;

  if type(value) == np.ndarray:

    d = hdfid.create_dataset(arrayname,value.shape,dtype=dtype)
    d[...] = value.astype(dtype)

#   for k,v in kargs.items():
    for k,v in kargs.items() + extraat.items():
      if isinstance(v,str): d.attrs[k] = np.array(v,dtype=str) # for compatability with coda...
      else: d.attrs[k] = v

    return;

#-------------------------------------------------------------------------------------------------#
# Transfroms a HDF5 GEOMS file to a HDF4 GEOMS file

def hdf5tohdf4(filename):
#def hdf5tohdf4(filename,logger=rootlogger):
  
# reload(fg);fg.hdf5tohdf4('/ae/projects4/FTIR/retrievals/working/bavol/sfit4/xianghe/bruker125HR/O3/new_sfit4_test/geoms/groundbased_ftir.o3_cas.iap001_xianghe_20181003t055723z_20181003t083244z_001.h5',logger=fg.testlogger)

# logger = getlogger(logger,'hdf5tohdf4')

  import pyhdf.SD as SD

  def dtype524(dtype5):
    if type(dtype5) != str: dtype5 = str(dtype5)
    if '|S' in dtype5: dtype4 = SD.SDC.CHAR8
    elif dtype5 == 'int32': dtype4 = SD.SDC.INT32
    elif dtype5 == 'int16': dtype4 = SD.SDC.INT16
  # elif dtype5 == 'int64': dtype4 = SD.SDC.INT64 -> this does not exist in pyhdf.SD
    elif dtype5 == 'float32': dtype4 = SD.SDC.FLOAT32
    elif dtype5 == 'float64': dtype4 = SD.SDC.FLOAT64
  # else: logger.error('No translation found for dtype %s to SDC'%dtype5); raise ValueError
    return dtype4;

  outputfile = os.path.splitext(filename)[0] + '.hdf'
# if outputfile == filename: logger.error('The source file will be overwritten by the output file'); return
# if os.path.isfile(outputfile): logger.warning('Removing the existing outputfile %s'%os.path.basename(outputfile));os.remove(outputfile)

  hdf4id = SD.SD(outputfile,SD.SDC.WRITE|SD.SDC.TRUNC|SD.SDC.CREATE)
# hdf4id = SD.SD(outputfile,SD.SDC.WRITE|SDC.TRUNC|SDC.CREATE)

  with h5py.File(filename,'r') as fid:

    try: 
    # WRITE ALL FILE attributes
      for att5,v in list(fid.attrs.items()):
      # logger.debug('Writing file attribute %s=%s'%(att5,v))
        att4 = hdf4id.attr(str(att5))
        dtype5 = v.dtype.str
        if dtype5[:2] == '|S': v=v.astype(dtype='U')
        if dtype5 == '|S0': att4.set(dtype524(dtype5),'\x00')
        else: # an empty attribute
          if att5 == 'FILE_NAME': v = os.path.basename(outputfile)
          att4.set(dtype524(dtype5),v)

    # WRITE VARIABLES + ATTRIBUTES
      for var,v in list(fid.items()):
      # logger.debug('Writing variable %s with shape %s, dtype %s'%(var,v.shape,v.dtype))
        v = v[...] # get numpy arrays
        if v.shape == (): v = v.reshape(1,)
        if '|S' in str(v.dtype) and str(v.dtype) != '|S1': v = np.array(list(v.tobytes().decode('utf-8')),dtype='S1').reshape(v.shape+(int(v.dtype.str.replace('|S','')),)) # fix shape only if not S1...
        vid4 = hdf4id.create(str(var),dtype524(v.dtype),v.shape)
        vid4[:] = v

        for att5,atv in list(fid[var].attrs.items()):
        # logger.debug('\tSetting attribute %s (dtype=%s,shape=%s): %s'%(att5,atv.dtype,atv.shape,atv))
          att4 = vid4.attr(str(att5))
          dtype5 = atv.dtype
          if 'float' in str(dtype5): 
            try: atv = float(atv)
            except TypeError: atv = list(map(float,atv))
          if str(dtype5)[:2] == '|S': atv = atv.astype(dtype='U')
          if str(dtype5) == '|S0': att4.set(dtype524(dtype5),'\x00') # an empty attribute
          else: att4.set(dtype524(dtype5),atv)

        vid4.endaccess()

  # except Exception as e: logger.error('Troubles: %s: %s'%(repr(e),traceback.format_exc()))

    finally: hdf4id.end();

  return


#-------------------------------------------------------------------------------------------------#
#=================================================================================================#
