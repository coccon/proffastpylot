# -*- coding: utf-8 -*-
# !/usr/bin/python3
#=================================================================================================#
#-------------------------------------------------------------------------------------------------#
# Python Script: 01_create-preprocess-input-file.py
# Version/Date:  V01 (01.11.2020)
# Project:       COCCON-PROCEEDS, funded by ESA
# Created by:    Qiansi Tu, Karlsruhe Institute of Technology (KIT), Germany
# Modified by:   Darko Dubravica, Karlsruhe Institute of Technology (KIT), Germany
# Description:   Create a New Preprocess Input File with All Raw Data Paths
#-------------------------------------------------------------------------------------------------#
#=================================================================================================#


#=================================================================================================#
#-------------------------------------------------------------------------------------------------#
# import modules/packages

import os         # operating system
import shutil     # shell utils
import subprocess # ...

#-------------------------------------------------------------------------------------------------#
#=================================================================================================#


#=================================================================================================#
#-------------------------------------------------------------------------------------------------#
# definition of the preprocess and the raw OPUS data folder, the template and input file

# use "preprocess4.exe" for Windows, and "preprocess4" for Linux
processor = "preprocess4.exe"

prep_path = r'D:\prf96-EM27-fast\preprocess'                                    # preprocess folder
temp_path = r'D:\prf96-EM27-fast\auxil\templates\sod2017_em27sn039'             # preprocess folder

data_path = os.path.join(prep_path,'sod2017_em27sn039')                         # data folder

prep_inp = os.path.join(prep_path,'preprocess4.inp')                            # input file with data list
temp_inp = os.path.join(temp_path,'template_preprocess4_sod2017_em27sn039.inp') # input file template

date_list = os.listdir(data_path)                                               # data folder list (i.e. yymmdd)

#-------------------------------------------------------------------------------------------------#
#=================================================================================================#


#=================================================================================================#
#-------------------------------------------------------------------------------------------------#
# print foldes and files

print ("")
print ("================================================================================")
print ("--------------------------------------------------------------------------------")
print ("Searching for the OPUS raw data and ...")
print ("writing the data list into the input file.")
print ("Existing cal folders will be deleted!")
print ("--------------------------------------------------------------------------------")
print ("Prep path: ", prep_path)
print ("Temp path: ", temp_path)
print ("Data path: ", data_path)
print ("Prep file: ", prep_inp)
print ("Temp file: ", temp_inp)
print ("--------------------------------------------------------------------------------")

input_1 = input("Continue? Yes (Y) or No (N) ... ")

#-------------------------------------------------------------------------------------------------#
#=================================================================================================#


#=================================================================================================#
#-------------------------------------------------------------------------------------------------#
# start script

if input_1 == "Y":

    print ("--------------------------------------------------------------------------------")
    print ("Script started ...")
    print ("--------------------------------------------------------------------------------")

  # open the new input file
    with open(prep_inp,'w') as new:

      # open the template input file
        with open(temp_inp,'r+') as template:

          # read the template input file
            lines = template.readlines()
            lines.append('\n')

          # loop over all data folders (i.e. yymmdd)
            for date in date_list:

                print ("Raw OPUS data folder:", date)

              # complete path to the raw data of a certain day (i.e. ...\site\yymmdd)
                date_path = os.path.join(data_path,date)

              # complete path to the cal folder of the data folder (i.e. ...\site\yymmdd\cal)
                cal_path = os.path.join(date_path,'cal')

              # delete existing cal folder and create a new empty one
                if os.path.exists(cal_path):
                    print ("Deleate existing cal folder.")
                    shutil.rmtree(cal_path)
                  # create new empty cal folder
                    print ("Create new empty cal folder.")
                    os.mkdir(cal_path)
                else:
                  # create new empty cal folder
                    print ("Create new empty cal folder.")
                    os.mkdir(cal_path)

              # raw OPUS data list (format: hhmmssSN.xxx or hhmmssSN+SM.xxx)
                print ("Create data list of raw OPUS files.")
                file_list = os.listdir(date_path)

              # check size of the raw OPUS file and remove invalid files (size < 1E6)
                size_err = []

                for file in file_list:
                    file_size = os.path.getsize(os.path.join(date_path,file))
                    if file_size < 1E6:
                        size_err.append(file)

                file_list = [file for file in file_list if file not in size_err]

              # loop over all raw OPUS files, append to the input file
                for file in file_list:
                  # complete path to the raw OPUS file (i.e. ...\site\yymmdd\hhmmssSN.xxx)
                    file_path = os.path.join(date_path,file)
                  # print file_path, file
                  # append complete path to the raw OPUS file list for the input file
                    lines.append(file_path + '\n')

          # marker for the end of the data list in the input file
            lines.append('***')

      # write new input file with data paths
        new.writelines(lines)

    print ("--------------------------------------------------------------------------------")
    print ("Writing input file finished.")
    print ("Please check new input file (i.e. preprocess4.inp)!")
    print ("Execute <preprocess4.exe> on a command prompt.")
    print ("For parallel processing:")
    print ("Execute <start-preprocess.bat> on a command prompt or continue with this script.")
    print ("--------------------------------------------------------------------------------")
    print ("================================================================================")

#-------------------------------------------------------------------------------------------------#
# stop script

else:

    print ("--------------------------------------------------------------------------------")
    print ("Script stopped!")
    print ("--------------------------------------------------------------------------------")
    print ("================================================================================")

#-------------------------------------------------------------------------------------------------#

print ("--------------------------------------------------------------------------------")

input_2 = input("Execute PREPROCESS? Yes (Y) or No (N) ... ")

if input_2 == "Y":
    input_3 = input("Parallel processing? Yes (Y) or No (N) ... ")
else:
    input_3 = "N"

#print ("--------------------------------------------------------------------------------")

if input_3 == "Y":
    input_4 = input("Number of parallel jobs (1-8) ... ")
    if input_4 not in ["1","2","3","4","5","6","7","8"]:
        print ("Wrong input ! Number of parallal jobs set to 1 !!!")
        input_4 = "1"
else:
    input_4 = 1

#-------------------------------------------------------------------------------------------------#

if input_2 == "Y" and input_3 != "Y":

    print ("--------------------------------------------------------------------------------")
    print ("PREPROCESS started ...")
    print ("--------------------------------------------------------------------------------")
    print ("================================================================================")

    subprocess.Popen(["start", "/wait", "cmd", "/c", os.path.join(prep_path,processor)], shell = True, cwd = prep_path)
#   subprocess.Popen(["xterm", "-e", "cmd", "/c", os.path.join(prep_path,processor)], shell = True, cwd = prep_path) # Linux
#   subprocess.Popen(["start", "/wait", "cmd", "/c", os.path.join(prep_path,"preprocess4.exe")], shell = True, cwd = prep_path)
#   subprocess.Popen(["start", "/wait", "cmd", "/c", os.path.join(prep_path,"preprocess4.exe 1 0 < continue.txt")], shell = True, cwd = prep_path)

elif input_2 == "Y" and input_3 == "Y":

    print ("--------------------------------------------------------------------------------")
    print ("PREPROCESS started with " + input_4 + " parallel jobs ...")
    print ("--------------------------------------------------------------------------------")
    print ("================================================================================")

    jobs = int(input_4)

    for n in range(jobs):
      # print (os.path.join(prep_path,"{} {} {}".format(processor,jobs,n)))
        subprocess.Popen(["start", "/wait", "cmd", "/c", os.path.join(prep_path,"{} {} {}".format(processor,jobs,n))], shell = True, cwd = prep_path)
      # subprocess.Popen(["xterm", "-e", "cmd", "/c", os.path.join(prep_path,"{} {} {}".format(processor,jobs,n))], shell = True, cwd = prep_path) # Linux
      # subprocess.Popen(["start", "/wait", "cmd", "/c", os.path.join(prep_path,"{} {} {} < continue.txt".format(processor,jobs,n))], shell = True, cwd = prep_path)

#       subprocess.Popen(["start", "/wait", "cmd", "/c", os.path.join(prep_path,"preprocess4.exe {} {}".format(jobs,n))], shell = True, cwd = prep_path)
#       subprocess.Popen(["start", "/wait", "cmd", "/c", os.path.join(prep_path,"preprocess4.exe {} {} < continue.txt".format(jobs,n))], shell = True, cwd = prep_path)

else:

    print ("--------------------------------------------------------------------------------")
    print ("Script stopped!")
    print ("--------------------------------------------------------------------------------")
    print ("================================================================================")

#-------------------------------------------------------------------------------------------------#
#=================================================================================================#
