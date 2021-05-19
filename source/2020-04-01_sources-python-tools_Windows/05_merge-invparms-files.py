# -*- coding: utf-8 -*-
#=================================================================================================#
#-------------------------------------------------------------------------------------------------#
# Python Script: 05_merge-invparms-files.py
# Version/Date:  V01 (01.04.2020)
# Project:       COCCON-PROCEEDS, funded by ESA
# Created by:    Qiansi TU, Karlsruhe Institute of Technology (KIT), Germany
# Modified by:   Darko Dubravica, Karlsruhe Institute of Technology (KIT), Germany
# Description:   Merge All Output Data (invparms.dat for Each Day) and Select Data (*selc.dat)
#-------------------------------------------------------------------------------------------------#
#=================================================================================================#


#=================================================================================================#
#-------------------------------------------------------------------------------------------------#
# import modules/packages

import os             # operating system
import shutil         # shell utils
import datetime       # date and time
import pandas as pd   # ...
from glob import glob # ...
from jdcal import *   # julian date calculation

#-------------------------------------------------------------------------------------------------#
#=================================================================================================#


#=================================================================================================#
#-------------------------------------------------------------------------------------------------#

site = 'sod2017_em27sn039'

out_path = r'D:\prf96-EM27-fast\out_fast'
new_path = r'D:\prf96-EM27-fast\out_fast\sod2017_em27sn039'

out_file = 'sod2017_em27sn039' + '.dat'
sel_file = 'sod2017_em27sn039' + '_selc' + '.dat'

#-------------------------------------------------------------------------------------------------#

# utc time - local time
# +8: Alaska
# -2: Karlsruhe / Sodankyla / Madrid / Namibia
utc_gap = -2

#-------------------------------------------------------------------------------------------------#
#=================================================================================================#


#=================================================================================================#
#-------------------------------------------------------------------------------------------------#

def read_header(inv_parms_file):
    with open(inv_parms_file,'r') as f:
        header = f.readlines()[0]
        return header

def read_inv_parms(inv_parms_file):
    with open(inv_parms_file,'r') as f:
        data = f.readlines()[1:]
        return data

def get_date(jd,utc_gap):
    datetimes = []
    for i in jd:
        i = i - utc_gap/24.0
        dt = jd2gcal(0,i)
        date = "%02d-%02d-%02d" % (dt[0], dt[1], dt[2])
        timeday = dt[3] # get time of the day (0.92839...)
        t = 24 * timeday
        hour = int(t)
        minute = int(60 * (t-hour))
        second = int(60 * ((60 * (t-hour)) % 1))
        time = "%02d:%02d:%02d" % (hour, minute, second)
        datetime = date + ' ' + time
        datetimes.append(datetime)
    return datetimes

def create_folder (dst):
    if os.path.exists(dst):
        print ("Folder allready exists ...")
        enter = input("Delete folder? Yes (Y) or No (N) ... ")
        if enter == "Y":
            shutil.rmtree(dst)
            os.mkdir(dst)
            print ("Folder deleted and recreated ...")
        else:
            print ("Folder NOT deleated !!!")
    else: # folder does not exist
        os.mkdir(dst)
        print ("Folder created ...")

def move_dat_spc (src,dst):
    if os.path.exists(dst):
        shutil.move(src,dst)
    else:
        print ("Main folder does NOT exist !!!")

#-------------------------------------------------------------------------------------------------#
#=================================================================================================#


#=================================================================================================#
#-------------------------------------------------------------------------------------------------#
# create site folder, move files to site folder

print ("Create folder ...", site)

create_folder (new_path)

enter = input("Move output files to site folder? Yes (Y) or No (N) ... ")

if enter == "Y":

    print ("Move output files to ...", site)

    file_list = glob(out_path + '\\' + site + '*.dat') # ...

    for file in file_list:
        move_dat_spc (file, new_path)

    file_list = glob(out_path + '\\' + site + '*.spc') # ...

    for file in file_list:
        move_dat_spc (file, new_path)

else:
    print ("Files NOT moved !!!")

#-------------------------------------------------------------------------------------------------#
# merge all output files

file_list = glob(new_path + '\\' + '*invparms.dat') # title

total = []

if len(file_list) != 0:

    with open(os.path.join(new_path,out_file),'w+') as f:

        header = read_header(file_list[0])
        f.writelines(header) # write header line

        for file in file_list:
            total += read_inv_parms(file)

        f.writelines(total) # write data (or results)

    f.close()

#-------------------------------------------------------------------------------------------------#
# select columns of interest, rename header and write output file

print ("Merge output files ...", out_file)

data = pd.read_csv(os.path.join(new_path,out_file),delimiter=r"\s+") # read file (csv format)

jd = data['JulianDate']

selc = data[['JulianDate','HHMMSS_ID','gndP','gndT','appSZA',\
             'XH2O','XAIR','XCO2','XCH4','XCO','XCH4_S5P',\
             'job01_gas01','job02_gas07','job03_gas03','job04_gas04','job05_gas06','job05_gas04']]

selc = selc.rename(columns={'job01_gas01':'H2O', 'job02_gas07':'O2', 'job03_gas03':'CO2',\
                            'job04_gas04':'CH4', 'job05_gas06':'CO', 'job05_gas04':'CH4_S5P'})

selc['XCO'] = 1000 * selc['XCO'] # transform ppm to ppb (for XCO)

JDOrigin = selc['JulianDate'] - 0.5

local_DT = pd.DataFrame(get_date(jd,utc_gap),columns={'Datetime'})

selc.insert(0,'JDOrigin',JDOrigin) # insert Julian Day
selc.insert(1,'Datetime',local_DT) # insert Local DateTime

#-------------------------------------------------------------------------------------------------#

print ("Select columns ...", sel_file)

lines = len(open(os.path.join(new_path,out_file)).readlines())

#print (os.path.join(new_path,out_file))
#print ('Lines: ' + lines)

with open(os.path.join(new_path,sel_file),'w+') as f:

    f.write ('JDOrigin Datetime JulianDate HHMMSS_ID gndP gndT appSZA XH2O ')
    f.write ('XAIR XCO2 XCH4 XCO XCH4_S5P H2O O2 CO2 CH4 CO CH4_S5P\n')

    for nr in range(0,lines-1):
        f.write ('{:13.5f}'.format(selc['JDOrigin'][nr]) + '\t')
        f.write ('{}'.format(selc['Datetime'][nr]) + '\t')
        f.write ('{:13.5f}'.format(selc['JulianDate'][nr]) + '\t')
        f.write ('{:06}'.format(selc['HHMMSS_ID'][nr]) + '\t')
        f.write ('{:6.2f}'.format(selc['gndP'][nr]) + '\t')
        f.write ('{:6.2f}'.format(selc['gndT'][nr]) + '\t')
        f.write ('{:5.2f}'.format(selc['appSZA'][nr]) + '\t')
        f.write ('{:7.2f}'.format(selc['XH2O'][nr]) + '\t')
        f.write ('{:7.5f}'.format(selc['XAIR'][nr]) + '\t')
        f.write ('{:7.3f}'.format(selc['XCO2'][nr]) + '\t')
        f.write ('{:7.5f}'.format(selc['XCH4'][nr]) + '\t')
        f.write ('{:7.4f}'.format(selc['XCO'][nr]) + '\t')
        f.write ('{:5.3f}'.format(selc['XCH4_S5P'][nr]) + '\t')
        f.write ('{:11.5e}'.format(selc['H2O'][nr]) + '\t')
        f.write ('{:11.5e}'.format(selc['O2'][nr]) + '\t')
        f.write ('{:11.5e}'.format(selc['CO2'][nr]) + '\t')
        f.write ('{:11.5e}'.format(selc['CH4'][nr]) + '\t')
        f.write ('{:11.5e}'.format(selc['CO'][nr]) + '\t')
        f.write ('{:11.5e}'.format(selc['CH4_S5P'][nr]) + '\n')

f.close()

#-------------------------------------------------------------------------------------------------#
#=================================================================================================#
