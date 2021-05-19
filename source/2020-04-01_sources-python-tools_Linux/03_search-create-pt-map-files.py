# -*- coding: utf-8 -*-
#=================================================================================================#
#-------------------------------------------------------------------------------------------------#
# Python Script: 03_search-create-pt-map-files.py
# Version/Date:  V01 (01.04.2020)
# Project:       COCCON-PROCEEDS, funded by ESA
# Created by:    Qiansi TU, Karlsruhe Institute of Technology (KIT), Germany
# Modified by:   Darko Dubravica, Karlsruhe Institute of Technology (KIT), Germany
# Description:   Search and Copy map-Files, Create pT-Files
#-------------------------------------------------------------------------------------------------#
#=================================================================================================#


#=================================================================================================#
#-------------------------------------------------------------------------------------------------#
# import modules/packages

import os             # operating system
import shutil         # shell utils
import math           # math
import pandas as pd   # ...
from glob import glob # ...

#-------------------------------------------------------------------------------------------------#
#=================================================================================================#


#=================================================================================================#
#-------------------------------------------------------------------------------------------------#
# paths to the preprocessed data, to the analysis folder, to the map files, ...

ana_path = r'./analysis/sod2017_em27sn039'        # analysis folder
pre_path = r'./preprocess/sod2017_em27sn039'      # preprocess folder

map_path = r'./auxil/map-files/sod2017_em27sn039' # map file folder
pt_path = r'./auxil/log-files/sod2017_em27sn039'  # pt file folder (data logger)

#-------------------------------------------------------------------------------------------------#

pt_temp = r'./auxil/templates/template_pT_intraday.inp'

#-------------------------------------------------------------------------------------------------#
#=================================================================================================#


#=================================================================================================#
#-------------------------------------------------------------------------------------------------#
# definitions and functions

# read datalogger file, write Time (hhmmss), Pressure (BaroTHB40) and delta Temperature (0.0)
def pt_logger (n):
    line = pt.UTCtime___[n]
#   line = line.replace("\"",'')
    line = line.replace(":",'')
    if pt.BaroTHB40[n] > 500.0 and pt.BaroTHB40[n] < 1500.0:
        pressure = pt.BaroTHB40[n]
        line = line[0:6] + '\t' + str(pressure)[0:10] + '\t' + '0.0' + '\n'
    else:
        line = ''
    return line

#-------------------------------------------------------------------------------------------------#
#=================================================================================================#


#=================================================================================================#
#-------------------------------------------------------------------------------------------------#
# start script

print ("\n")
print ("================================================================================")
print ("--------------------------------------------------------------------------------")
print ("PrePro path:  ", pre_path)
print ("Analysis path:", ana_path)
print ("Map file path:", map_path)
print ("PT logger path:", pt_path)
print ("PT templ. file:", pt_temp)
print ("--------------------------------------------------------------------------------")

#-------------------------------------------------------------------------------------------------#
# read template pt input file (only header part), i.e. pT_intraday_template.inp

with open(pt_temp,'r') as f:
    head_inp = f.readlines()

#-------------------------------------------------------------------------------------------------#
# loop over all measurement days

#date_list = os.listdir(pre_path)
date_list = os.listdir(ana_path)

for date in date_list:

    search_map = map_path + '\\*' + date + '.map'

    print ("Date dir:", date)
    print ("Map file:", search_map)

  # create map file list with one single entry
    map_file = glob(search_map)

    if len(map_file) == 1:

        print ("Map file exists ...", date)
#       print ("Continue ...")

        shutil.copy(map_file[0],os.path.join(ana_path,date,'pt'))

        pt_intraday_inp = os.path.join(ana_path,date,'pt','pT_intraday.inp')

     #---------------------------------------------------------------------------------------------#
     # data logger file

        print ('Searching for suitable pt file ...', date)

      # find datalogger file, read time and pressure values
        pt_file = glob(pt_path + '\\'+'20'+date[0:2]+'-'+date[2:4]+'-'+date[4:6] + '_*.dat')
        pt = pd.DataFrame(pd.read_csv(pt_file[0],sep='\t'))

        print ('PT file:', pt_file[0])

        with open(pt_intraday_inp,'w+') as f:
            f.writelines(head_inp)
            for i in pt.index:
                i = int(i)
                f.writelines(pt_logger(i))
            f.writelines("***")
            f.close()

#-------------------------------------------------------------------------------------------------#
# continue script

    else: # if len(map_file) != 1:

        print ("Map file does NOT exist for ...", date)

#       continue

#-------------------------------------------------------------------------------------------------#

print ("--------------------------------------------------------------------------------")
print ("================================================================================")

#-------------------------------------------------------------------------------------------------#
#=================================================================================================#
