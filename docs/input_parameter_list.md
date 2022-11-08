# List of all input Parameters

The example input file [input_sodankyla_example.yml](https://gitlab.eudat.eu/coccon-kit/proffastpylot/-/blob/master/example/input_sodankyla_example.yml)
contains the most relevant input parameters to run the PROFFASTpylot.
However, there are several more parameters which can be used optionally.
In this file ALL parameters are given and explained:

## Site information
- instrument_number: The serial number of your EM27/SUN.
                     (Or any other number you want to give to your instrument.)

- site_name: The name of the current measurement site.

- site_abbrev: To order the map files to a site a two letter abbreviation is
               needed. This abbreviation must be used in your map files, too.

- coords:  
  Leave empty if coordinates should be taken from file. An example file can
  be found in examples/input_data/coords.csv
    - lat: The latitude 
    - lon: The longitude
    - alt: The altitude in km over sea level.

- coord_file: Alternative way of giving the coordinates:
  A comma separated file. 

- utc_offset: The UTC-offset of your measurements. This can either be due to
              the measurement in a different time zone or due to an error in
              the syncing of the PC clock.

- note: Optional comment included in bin-files by PREPROCESS.
        Leave empty for adding no comment

## Steering of the behavior:

- min_interferogram_size: A file size filter for interferograms: all interferograms with a
                          file size less than the value specified here are
                          assumed to be corrupt. File size in MegaBytes

- igram_pattern: The pattern used to look for interferograms.
                 This parameter can be used to select only files from
                 within the interferogram folder matching with the given
                 pattern.
                 The default value is `*.*` which means that all files in the
                 interferogram folders are used for processing.


- start_with_spectra: Start the processing chain with already available
                      spectra. The directory to the spectra is given as the
                      'analysis_path'.  
                      Set to True/False.
                      **NOTE:** In this case the folder this path points to
                      must have a substructure like
                      `analysis/SiteName_InstrumentNumber/YYMMDD/cal`.

- start_date: The first date to be processed. Leave empty to start with the
              first date in the data folder. Date format: YYYY-MM-DD.
- end_date: The last date to be processed. Leave empty to start with the
            last date in the data folder. Date format: YYYY-MM-DD.


- delete_abscosbin_files: Delete the abscos.bin files? (True/False)
                          The abscos.bin file contains the simulation of the
                          atmosphere which is the result of the 'pcxs' program
                          part of PROFFAST. The pT_fast_out.dat and
                          VMR_fast_out.dat files will be removed as well.
                          The pT_fast_out.dat file contains the daily a priori
                          height profile of pressure, temperature, ...
                          The VMR_fast_out_dat. contains the a prior vertical
                          mix ratios of the gases

- delete_input_files: Delete PROFFAST input files? (True/False)
                      If False: Files will be moved to results folder.
                      Default: False.

- tccon_mode: Use PROFFAST to evaluate low resolution spectra recorded with
              a 125HR instrument. The resolution must be 0.5 cm^-1 and the
              interferograms must be recorded double sided.

- tccon_setting: Setting of the TCCON instrument. Will be evaluated in case of
                 `tccon_mode: True` only.  
                 1: Standard TCCON Setting  
                 2: Karlsruhe TCCON Setting

## Path settings

- proffast_path: The path pointing to the PROFFAST folder.

- interferogram_path: The path to the interferograms. The data structure must
                      be like `YYMMDD/YYMMDD*.XXX`
- map_path: The path pointing to the map files.
- pressure_path: The path pointing to the pressure data.
- pressure_type_file: The path pointing to the pressure setup file.

- analysis_path: In the analysis path the spectra produced by preprocess are
                 written to. We recommend to call it analysis.
                 Within this folder the PROFFASTpylot will create a folder
                 structure like `analysis/SiteName_InstrumentNumber/YYMMDD.`
- result_path: The merged results, the log files and optionally the input files
               are written to the result path.
               Within it, PROFFASTpylot will create a folder named
               `SiteName_InstrumentNumber_StartDate-EndDate`.
