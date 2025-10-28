# Developer Guide

This document gives an overview about the structure of the PROFFASTpylot code. It should help all users who want to adapt PROFFASTpylot to their own needs.

The general structure of the code is depicted schematically in the following image.

![developer_guider.png](developer_guider.png)



- The `Pylot` class contains the most top-level fucntionality for steering PROFAST. The user creates an instance of the `Pylot` class. This class is inheriting functionality from `FileMover` and `Preparation` classes.
- The `Filemover` class contains the functionality to organize all outputfiles in a file structure.
- The `Preparation` class contains most functionality determining the relevant parameters for the processing. It is the most extensive class and inside functionality from the `PressureHandler`, `CoordHandler` and `TimeHandler` classes are called.

These are the most important functions for steering PROFFAST.
The most important functions and interactions are described in the following.
Additional code for different output formats located in `/output` is not covered in this document.


## prepare.py

Genererally the user provides an input file or dictonary with the corresponding parameters for the processing. 
From this many additional options are derived.
This happens in the `Preparation` class.
The following functonality is handled by the `Preparation` class.

### Preparation

- Initinialize Logging
- Read the input parameters and deriving the following parameters for further processing
- Read corresponding instrument_parameters from list
- Search available interferograms/spectra on disk
- Create a list of dates to be processed
- Generate the input parameters needed for the individual PROFFAST input files
- Handling of Coordinates (either fixed or variable, (for variable coordinates see `CoordHandler`))
- Mapfile interpolation to local noontime


### TimeHandler
- Time zone of the processing and list of dates
- Return local_time, utc and measrument time for a given spectrum or interferogram
- Determine local noon of a given day for given coordinates (here, allways the local timezone of the location is used, never the daylight saving time)

## filemover.py

PROFFASTpylot disentagles the output, input and program files. There fore files that are written to a location inside the PROFFAST folder by the FORTRAN PROFFAST routines are moved at the end of a run. This sorting of the files is handled by the filemover class.

### Filemover

- creating the output file structure
- moving or copying generated files from the prf folder to the result folder

## pylot.py

Here the most top-level functions called by the user are present.

### Plot

- execute the three PROFFAST routines (preprocess, pcxs and invers)
- call generation of input files for PROFFAST by filling the corresponding parameters into the respective templates
- combine results

## auxiliary.py

PROFFAST needs accurate pressure data. Pressure values can be read from a file with variable formatting and data frequency. This is handled in auxiliary.py in the class `PressureHandler`.
An internal dataframe is created from the file by `prepare_pressure_df()`. It can be accessed by `Pylot.p_df`.

For handling observations with a variable position of the instrument the coord handler interpolates coord data to the observation time steps. 

The `AuxiliariyHandler` class contains all functionality that is shared between both classes.

### AuxiliaryHandler

- Read data and construct dataframe
- Parse datetime column from one or multiple columns
- Interpolate data to specific time

### PressureHandler

- Create pressure dataframe as a instance of PressureHandler
- Apply pressure Factors
- Filter Outliers


### CoordHandler

- Create coord dataframe
- For High-Frequency-Data average over Observation Period, otherwise interpolate to observation time


### Output
There are four types of output

1. **Raw output**:
	The PROFFAST routines are writing several asccii formatted tables, which are placed into the `raw_output_proffast` folder.
2. **comb_invparms_<...>.csv**
	combines all invparms files and renames the most important to identifyable names (see `pylot.pylot.combine_results()`)
3. **HDF5 (GEOMS)**
	HDF5 binary files following the GEOMS conventions are produced by `output/hdf_geoms_helper.py` and `outtput/hdf_geoms_writer.py`. These files contain the vertical columns, the column averaged molar fractions, and the column sensitivities, as well as the prior profiles for CO2, CO, CH4 and H2O.
4. **netCDF4 (cf)**
	This files contains the same information as the HDF GEOMS files but is delivered in netCDF4 format and follows the cf conventions.
