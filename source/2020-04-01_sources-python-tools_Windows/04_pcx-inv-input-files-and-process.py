# -*- coding: utf-8 -*-
#=================================================================================================#
#-------------------------------------------------------------------------------------------------#
# Python Script: 04_pcx-inv-input-files-and-process.py
# Version/Date:  V01 (01.04.2020)
# Project:       COCCON-PROCEEDS, funded by ESA
# Created by:    Qiansi TU, Karlsruhe Institute of Technology (KIT), Germany
# Modified by:   Darko Dubravica, Karlsruhe Institute of Technology (KIT), Germany
# Description:   Prepare pcxs10_template and invers10_template Input File for Each Day ...
#                Execute <pcxs10.exe pcxs10_yymmdd.inp> and <invers10.exe invers10_yymmdd.inp>
#-------------------------------------------------------------------------------------------------#
#=================================================================================================#


#=================================================================================================#
#-------------------------------------------------------------------------------------------------#
# import modules/packages

import os                     # operating system
import sys                    # system
import glob                   # ...
import shutil                 # shell utils
from glob import glob as gb   # ...
from datetime import datetime # date and time

#-------------------------------------------------------------------------------------------------#
#=================================================================================================#


#=================================================================================================#
#-------------------------------------------------------------------------------------------------#

main_path = r'D:\prf96-EM27-fast'

site = 'sod2017_em27sn039'

ana_path = r'D:\prf96-EM27-fast\analysis\sod2017_em27sn039'
out_path = r'D:\prf96-EM27-fast\out_fast'
pcx_temp = r'D:\prf96-EM27-fast\auxil\templates\sod2017_em27sn039\template_pcxs10_sod2017_em27sn039.inp'
inv_temp = r'D:\prf96-EM27-fast\auxil\templates\sod2017_em27sn039\template_invers10_sod2017_em27sn039.inp'

#-------------------------------------------------------------------------------------------------#
#=================================================================================================#


#=================================================================================================#
#-------------------------------------------------------------------------------------------------#

if len(sys.argv) == 3:
    jobs = int(sys.argv[1])
    job_n = int(sys.argv[2])
else:
    jobs = 1
    job_n = 0

#print (len(sys.argv))
#print (sys.argv)
print ("jobs {}, job_n {}".format(jobs,job_n))

#-------------------------------------------------------------------------------------------------#
#=================================================================================================#


#=================================================================================================#
#-------------------------------------------------------------------------------------------------#
# read pcxs10_template.inp

with open(pcx_temp,'r') as f:
    pcx_template = f.readlines()
    pcx_template = [x for x in pcx_template]

# read invers10_template.inp
with open(inv_temp,'r') as f:
    inv_template = f.readlines()
    inv_template = [x for x in inv_template]

#-------------------------------------------------------------------------------------------------#

# replace datum in template to change date
def replace_datum(template,date_str):
    result = [x.replace('%DATUM%',date_str.strftime("%y%m%d")) for x in template]
    return result

# replace site and map names in template
def replace_site(template,site):
    result = [x.replace('%SITE%',site) for x in template]
    return result

# create file name list to be added later into pcxs10.inp
def append_filelist(folder):
    file_path = gb(folder)
    files = [os.path.basename(file_path[i]) for i in range(len(file_path))] # create file name list
    files = [x+'\n' for x in files]
    files.append('***')
    return files

# create invers10.inp file content based on invers10_template.inp, date and file list
def generate_inv(date_str,folder,site,template=inv_template):
    filelist = append_filelist(folder)
    template = replace_datum(template,date_str)
    template = replace_site(template,site)
    return template + filelist

# create new invers10_yymmdd.inp file
def write_inv(inv_path,date_str,folder,site,template=inv_template):
    with open(inv_path,'w+') as f:
        inv = generate_inv(date_str,folder,site,template)
        f.writelines(inv)

# create new pcxs10_yymmdd.inp file based on pcxs10_template.inp and date
def write_pcx(pcx_path,date_str,site,template=pcx_template):
    pcx = replace_datum(template,date_str)
    pcx = replace_site(pcx,site)
    with open(pcx_path,'w+') as f:
        f.writelines(pcx)

#-------------------------------------------------------------------------------------------------#

# execute pcxs10.exe
def run_pcx(pcx_file):
    pcx_command = os.path.join(main_path,'pcxs10.exe') + ' ' + pcx_file
#   pcx_command = os.path.join(main_path,'pcxs10.exe') + ' ' + pcx_file + ' < continue.txt'
    os.chdir(main_path)
    os.system(pcx_command)

# execute invers10.exe
def run_inv(inv_file):
    inv_command = os.path.join(main_path,'invers10.exe') + ' ' + inv_file
#   inv_command = os.path.join(main_path,'invers10.exe') + ' ' + inv_file + ' < continue.txt'
    os.chdir(main_path) # special invers10.exe for calpy-created bin files
    os.system(inv_command)

#-------------------------------------------------------------------------------------------------#
#=================================================================================================#


#=================================================================================================#
#-------------------------------------------------------------------------------------------------#

start = datetime.now()

date_list = os.listdir(ana_path)

date_list_job = date_list[job_n::jobs]

#-------------------------------------------------------------------------------------------------#

print ("")
print ("================================================================================")
print ("--------------------------------------------------------------------------------")
print ("main path:", main_path)
print ("ana  path:", ana_path)
print ("pcx  temp:", pcx_temp)
print ("inv  temp:", inv_temp)
print ("--------------------------------------------------------------------------------")
print (date_list)
print (date_list_job)
print ("--------------------------------------------------------------------------------")

#-------------------------------------------------------------------------------------------------#
# start script

#for date in date_list:
for date in date_list_job:

    print ("Data folder:", date)
    print ("--------------------------------------------------------------------------------")

  #-----------------------------------------------------------------------------------------------#
  # update pcxs10.inp and then start pcxs10.exe

    date_str = datetime.strptime(date,'%y%m%d')

    pcx_path = os.path.join(main_path,'inp_fast','pcxs10_' + site + '_' + date + '.inp')
    pcx_file = 'pcxs10_' + site + '_' + date + '.inp'

    write_pcx(pcx_path,date_str,site)
#   update_pcx(date_str,map_file,0.181)

    print ("pcx path:", pcx_path)
    print ("pcx file:", pcx_file)

    print ("Start pcx exe ...")
    run_pcx(pcx_file)

  #-----------------------------------------------------------------------------------------------#
  # create invers10_date.inp file and start invers10.exe invers10.inp

    date_str = datetime.strptime(date,'%y%m%d')
    string = date_str.strftime("%y%m%d")
    check_path = ana_path + '\\' + string + '\\cal\\*SN.BIN'

    inv_path = os.path.join(main_path, 'inp_fast','invers10_' + site + '_' + date + '.inp')
    inv_file = 'invers10_' + site + '_' + date + '.inp'

    write_inv(inv_path,date_str,check_path,site)

    print ("inv path:", inv_path)
    print ("inv file:", inv_file)

    print ('Start inv exe ...')
    run_inv(inv_file)

#-------------------------------------------------------------------------------------------------#

end = datetime.now()

print ("--------------------------------------------------------------------------------")
print ("Time consumed:", end-start)
print ("--------------------------------------------------------------------------------")
print ("================================================================================")

#-------------------------------------------------------------------------------------------------#
#=================================================================================================#