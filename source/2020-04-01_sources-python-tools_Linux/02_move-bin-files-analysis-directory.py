# -*- coding: utf-8 -*-
#=================================================================================================#
#-------------------------------------------------------------------------------------------------#
# Python Script: 02_move-bin-files-analysis-directory.py
# Version/Date:  V01 (01.04.2020)
# Project:       COCCON-PROCEEDS, funded by ESA
# Created by:    Qiansi TU, Karlsruhe Institute of Technology (KIT), Germany
# Modified by:   Darko Dubravica, Karlsruhe Institute of Technology (KIT), Germany
# Description:   Move/Copy Preprocessed Binary Data to Analysis Folder
#-------------------------------------------------------------------------------------------------#
#=================================================================================================#


#=================================================================================================#
#-------------------------------------------------------------------------------------------------#
# import modules/packages

import os             # operating system
import shutil         # shell utils
import math           # math
from glob import glob # ...

#-------------------------------------------------------------------------------------------------#
#=================================================================================================#


#=================================================================================================#
#-------------------------------------------------------------------------------------------------#
# paths to the preprocessed data, to the analysis folder, to the map files, ...

pre_path = r'./preprocess/sod2017_em27sn039'
ana_path = r'./analysis/sod2017_em27sn039'

#-------------------------------------------------------------------------------------------------#
#=================================================================================================#


#=================================================================================================#
#-------------------------------------------------------------------------------------------------#
# definitions and functions

# create main folder
def create_main_folder (dst):
    if os.path.exists(dst):
        print ("Main folder allready exists ...")
        enter = input("Delete main folder? Yes (Y) or No (N) ... ")
        if enter == "Y":
            shutil.rmtree(dst)
            os.mkdir(dst)
            print ("Main folder deleted and recreated ...")
        else:
            print ("Main folder NOT deleated !!!")
    else: # folder does not exist
        os.mkdir(dst)
        print ("Main folder created ...")


# create folder and subfolder ...\analysis\site\yymmdd\pt
def create_folder (dst,date):
    if os.path.exists(os.path.join(dst,date)):
        shutil.rmtree(os.path.join(dst,date))
        os.mkdir(os.path.join(dst,date))
        os.mkdir(os.path.join(dst,date,'pt'))
#       os.mkdir(os.path.join(dst,date,'cal'))
    else: # folder does not exist
        os.mkdir(os.path.join(dst,date))
        os.mkdir(os.path.join(dst,date,'pt'))
#       os.mkdir(os.path.join(dst,date,'cal'))


# copy cal folder (i.e. the preprocessed binary files) ...
# from the preprocess folder to the analysis folder of proffast
def copy_bin (src,dst,date):
    src_cal = os.path.join(src,date,'cal')
    dst_cal = os.path.join(dst,date,'cal')
    if os.path.exists(src_cal) and os.path.exists(os.path.join(dst,date)):
        shutil.copytree(src_cal,dst_cal,symlinks=False,ignore=None)
    else:
        print ("Main folder does NOT exist ...")


# move cal folder (i.e. the preprocessed binary files) ...
# from the preprocess folder to the analysis folder of proffast
def move_bin (src,dst,date):
    src_cal = os.path.join(src,date,'cal')
    dst_cal = os.path.join(dst,date,'cal')
    if os.path.exists(src_cal) and os.path.exists(os.path.join(dst,date)):
        shutil.move(src_cal,dst_cal)
    else:
        print ("Main folder does NOT exist !!!")

#-------------------------------------------------------------------------------------------------#
#=================================================================================================#


#=================================================================================================#
#-------------------------------------------------------------------------------------------------#
# start script

print ("\n")
print ("================================================================================")
print ("--------------------------------------------------------------------------------")
print ("Pre_path: ", pre_path)
print ("Ana_path: ", ana_path)
print ("--------------------------------------------------------------------------------")

#-------------------------------------------------------------------------------------------------#
# loop over all measurement days

date_list = os.listdir (pre_path)

print ("Create folder ...")

create_main_folder (ana_path)

enter = input("Copy/Move binary files to analysis folder? Yes (Y) or No (N) ... ")

if enter == "Y":

    for date in date_list:

        print ("Date dir:", date)

        create_folder (ana_path, date)

        print ("Move binary files to analysis folder ...")
        move_bin (pre_path, ana_path, date)

#       print ("Copy binary files to analysis folder ...")
#       copy_bin (pre_path, ana_path, date)

        print ("... finished!")

else:
    print ("Script stopped !!!")

#-------------------------------------------------------------------------------------------------#

print ("--------------------------------------------------------------------------------")
print ("================================================================================")

#-------------------------------------------------------------------------------------------------#
#=================================================================================================#
