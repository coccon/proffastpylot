# -*- coding: utf-8 -*-
# !/usr/bin/python3
#=================================================================================================#
#-------------------------------------------------------------------------------------------------#
# Python Script: ReadInputFile.py (see also General-Input-File.inp, auxil directory!)
# Version/Date:  V01 (25.02.2021)
# Project:       COCCON-PROCEEDS, funded by ESA
# Created by:    Benedikt Herkommer, Karlsruhe Institut of Technology (KIT)
#                benedikt.herkommer@kit.edu
# Comments:      Originally this function is part of the GGGHandler
#-------------------------------------------------------------------------------------------------#
#=================================================================================================#


#=================================================================================================#
#-------------------------------------------------------------------------------------------------#
# import modules/packages

import os

#-------------------------------------------------------------------------------------------------#
#=================================================================================================#


#=================================================================================================#
#-------------------------------------------------------------------------------------------------#

def getInputVariables(InFile = None):
    varDict = {}
    if InFile == None:
        ownPath = os.path.dirname(os.path.abspath(__file__))
        InFile = os.path.join(ownPath, 'General-Input-File.inp')
    try:
        file = open(InFile, 'r')
        #read in the file into a 2d list
        for line in file:
            #skip comments and empy lines
            if line[0] == '#' or line[0] == '\n': continue
            #check if a comment is appended after the variable name:
            line = line.split('#')[0].strip()
            #use '='sign as separator
            cols = line.split('=')
            
            key = cols[0].strip()
            var =  cols[1].replace('\n', '').strip()
            #print (key, var)
            #write everything into a dictionary, and delete new line character
            #as well as whitespaces.
            varDict[key] = var
        file.close()
    except IOError:
        raise Exception('It was not possible to load the InputFile')

    #replace ${xxxx} with xxx=yyy, where xxx is the name of a previos entry
    for var, content in varDict.items(): #interate through key and items
        for i, content2 in varDict.items():
            varDict[i] = varDict[i].replace('${' + var + '}', varDict[var])
    for var, content in varDict.items():
        #delete ticks if there are any:
        varDict[var] = content.replace('"','')
        varDict[var] = content.replace("'",'')
        #for Windows the backslashes have to be replaced by double backslashes:
        varDict[var] = content.replace(r"\\", r'\\\\')

    return varDict

#-------------------------------------------------------------------------------------------------#
#=================================================================================================#
