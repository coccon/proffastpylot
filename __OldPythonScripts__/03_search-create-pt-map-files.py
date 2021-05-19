# -*- coding: utf-8 -*-
# !/usr/bin/python3
#=================================================================================================#
#-------------------------------------------------------------------------------------------------#
# Python Script: 03_search-create-pt-map-files.py
# Version/Date:  V01 (01.11.2020)
# Project:       COCCON-PROCEEDS, funded by ESA
# Created by:    Qiansi Tu, Karlsruhe Institute of Technology (KIT), Germany
# Modified by:   Darko Dubravica, Karlsruhe Institute of Technology (KIT), Germany
# Description:   Search and Copy map-Files, Create pT-Files
# Comments:      See also the Python script ReadInputFile.py and
#                the input file General-Input-File.inp in the auxil directory!
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
from auxil.ReadInputFile import *

#-------------------------------------------------------------------------------------------------#
#=================================================================================================#


#=================================================================================================#
#-------------------------------------------------------------------------------------------------#
# paths to the preprocessed data, to the analysis directory, to the map files, ...

vars = getInputVariables()
root_path = vars['root_path']

pre_path = os.path.join(root_path, 'preprocess', vars['site']) # preprocess directory
ana_path = os.path.join(root_path, 'analysis', vars['site'])   # analysis directory

map_path = vars['map_path'] # map file directory
pt_path = vars['pt_path']   # pt file directory (data logger)

#-------------------------------------------------------------------------------------------------#

pt_temp = os.path.join(root_path, 'auxil', 'templates', vars['pt_tempfile'])

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
# check file contents and remove incomplete directories

for date in date_list:

    search_file = os.path.join(ana_path, date, 'cal', '*SN.BIN')
    bin_file = glob(search_file)
    search_file = os.path.join(ana_path, date, 'pt', '*.map')
    map_file = glob(search_file)
    search_file = os.path.join(ana_path, date, 'pt', 'pT_intraday.inp')
    inp_file = glob(search_file)

    if (len(map_file) == 0) or (len(inp_file) == 0) or (len(bin_file) == 0):

        print ("--------------------------------------------------------------------------------")
        print ('Incomplete directory: ', os.path.join(ana_path, date))

        if (len(bin_file) == 0): print ('Missing file: ./cal/*SN.BIN')
        if (len(map_file) == 0): print ('Missing file: ./pt/*.map')
        if (len(inp_file) == 0): print ('Missing file: ./pt/pT_intraday.inp')

        input_1 = input("Delete? Yes (Y) or No (N) ... ")
        if (input_1 == "Y"): shutil.rmtree(os.path.join(ana_path, date))

#-------------------------------------------------------------------------------------------------#

print ("--------------------------------------------------------------------------------")
print ("================================================================================")

#-------------------------------------------------------------------------------------------------#
#=================================================================================================#