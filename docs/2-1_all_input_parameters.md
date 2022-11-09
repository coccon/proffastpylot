# List of all input Parameters

The example input file [`input_sodankyla_example.yml`](https://gitlab.eudat.eu/coccon-kit/proffastpylot/-/blob/master/example/input_sodankyla_example.yml)
contains the most relevant input parameters to run the PROFFASTpylot.
However, there are several more parameters which can be used optionally.
In this file all parameters are given and explained.

## Site information
- **`instrument_number`**  
  The serial number of your EM27/SUN.
- **`site_name`**  
  The name of the current measurement site.
- **`site_abbrev`**  
  A two letter abbreviation to assign your site to a map file.
- **`coords`**  
  Coordinates of the measurement. Alternatively a coordinate file can be used (see below).
    - **`lat`**: Latitude, degrees north in decimal format 
    - **`lon`**: Longitude, degrees east in decimal format
    - **`alt`**: Altitude, km over sea level
- **`coord_file`**  
  Give the coordinates in a comma separated file. An example file can be found in `examples/input_data/coords.csv`
- **`utc_offset`**  
  The UTC-offset of your measurements. This can either be due to
  the measurement in a different time zone or due to an error in
  the syncing of the PC clock.
- **`note`**  
  Optional comment included in bin-files by PROFFAST preprocess.

## Steering of the behavior:

- **`min_interferogram_size`**  
  File size in MegaBytes. All interferograms smaller than the given size are skipped.
- **`igram_pattern`**  
  The file name pattern of the interferograms
  can be used to process only specific files in the interferogram folder.
  The default value is `*.*` which means that all files in the
  interferogram folders are used for processing.
- **`start_with_spectra`**  
  `True` or `False`  
  Start the processing chain with already available spectra. 
  The spectra have to be located at `<analysis>/SiteName_InstrumentNumber/YYMMDD/cal`
  where `<analysis>` is the given analysis path.
- **`start_date`**  
  Date with the format `YYYY-MM-DD`.  
  The first date to be processed. If not given, the earliest available date is the start date.
- **`end_date`**  
  Date with the format `YYYY-MM-DD`.  
  The last date to be processed. If not given, the latest available date is the end date.
- **`delete_abscosbin_files`**  
  `True` (default) or `False`  
  If True the `*abscos.bin`, the `pT_fast_out.dat` and the `pT_fast_out.dat` will be removed after the run.
  The `*abscos.bin` file contains the the simulation of the
  atmosphere which is the result of the PROFFAST pcxs program.  
  The `pT_fast_out.dat` file contains the daily a priori
  height profile of pressure, temperature, ...  
  The `VMR_fast_out_dat` contains the a prior vertical
  mix ratios of the gases.
- **`delete_input_files`**  
  `False` (default) or `True`  
  If False: The output of the PROFFAST programs will be moved to results folder.
- **`tccon_mode`**  
  Use PROFFAST to evaluate low resolution spectra recorded with
  a 125HR instrument. The resolution must be 0.5 cm^-1 and the
  interferograms must be recorded double sided.
- **`tccon_setting`**  
  Setting of the TCCON instrument. Will be evaluated in case of
  `tccon_mode: True` only.  
  1: Standard TCCON Setting  
  2: Karlsruhe TCCON Setting

## Path settings

- **`proffast_path`**  
  The path pointing to the PROFFAST folder.
- **`interferogram_path`**  
  The path to the interferograms. The data structure must
  be like `YYMMDD/YYMMDD*.XXX`
- **`map_path`**  
  The path pointing to the map files.
- **`pressure_path`**  
  The path pointing to the pressure data.
- **`pressure_type_file`**  
  The path pointing to the pressure setup file.
  _For more explanation see the article about pressure input in the documentation._
- **`analysis_path`**  
  In the analysis path the spectra produced by preprocess are
  written to. We recommend to call it analysis.
  Within this folder the PROFFASTpylot will create a folder
  structure like `analysis/SiteName_InstrumentNumber/YYMMDD.`
  _Consult also the article about folder structure in the documentation._
- **`result_path`**  
  The merged results, the log files and optionally the input files
  are written to the result path.
  Within it, PROFFASTpylot will create a folder named
  `SiteName_InstrumentNumber_StartDate-EndDate`.
