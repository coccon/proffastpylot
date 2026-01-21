# Folder Structure

With PROFFASTpylot, most of the folder structure can be chosen freely. This article gives an overview of the required folders and files. They can be divided into four categories:

1. Input data: Interferograms, pressure files, map files
2. Output data: Spectra, results of the processing, config files
3. Program Files: This includes the folder to the PROFFAST binaries as well as the `proffastpylot` directory (see note below).
4. Steering Files: input files and run files for specific runs

All paths can be chosen freely (e.g., input data can be located on an external hard disk). **We recommend disentangling input data, output data, and the program execution files from each other.**

_Note_: To run the example files using [run.py](https://github.com/coccon/proffastpylot/blob/main/example/run.py) PROFFAST must be located inside the `proffastpylot` directory as described in the **Installation** article.

## 1. Input data

You can specify three paths for your input data:

- Path of the interferograms
- Path of the pressure files
- Path of the map files (containing atmospheric information)

Optionally, a file with the coordinates of the measurements can be provided.

In our example, all these folders and files are in `example/input_data`.

### Interferograms

The `interferogram_path` should be a folder with the interferograms inside. It needs to have the following structure:

```
interferogram_path
├── YYMMDD
│	├── YYMMDDSN.XXX
│	├── YYMMDDSN.XXX
│	└── ...
├── YYMMDD
│	├── ...
├── ...
```

### Pressure input

Inside the `pressure_path`, pressure measurements for each measurement day should be provided. The frequency of the files (e.g., monthly or daily) and the formatting are flexible. In the `pressure_type_file`, the file format can be defined. See the **Pressure Input** article for how the pressure type file is organized.

### Map Files

PROFFASTpylot supports the usage of the GGG2014 and GGG2020 map files. It detects automatically what kind of map file is used. The path to the files is specified by the `map_path` in the input file.

## 2. Output data

Two output paths have to be specified: the `analysis_path` and the `result_path`.

### Analysis path

Day-specific output files are written to the analysis folder by PROFFAST automatically. The analysis folder is created with the following structure:

```
analysis_path
├── <site_name>_<instrument>
|	├──YYMMDD
│	|	└── cal
|	├──YYMMDD
...
```

Inside the `YYMMDD` folder, the spectra, which are named `YYMMDD_HHMMSSSN.BIN` (or `SM.BIN`), will be located. Note that this timestamp, as well as the folder name, corresponds to the measurement time. The UTC time of the measurement, which is derived from the variable `utc_offset` in `preprocess`, is written to the header of the spectrum. For more information on time offsets, see the **Time Offsets** article.

The files that were located in `YYMMDD/pT` are handled elsewhere since version 1.1. 

### Result path

In the result folder, run-specific information is stored. In the folder, the retrieval results of all days are stored. Those files are merged to a single file `comb_invparms_<site_name>_<instrument_nr>_<YYMMDD>-<YYMMDD>.csv`. Furthermore, the logfiles of the runs are stored in `result_path/logfiles`.

## 3. Program Files

In principle, the `proffastpylot` directory can be located elsewhere than the PROFFAST binaries. The location can be given as `proffast_path` in the input file. The default is `proffastpylot/prf`

## 4. Steering Files

The input files and Python scripts that call proffastpylot do not need to be located inside the `proffastpylot` directory.

## Example for a possible folder structure

An example of how a folder structure could look is given below (most sub-directories are created automatically).

```
E:\EM27_Sodankyla_RawData
    ├── interferograms
    ├── map
    └── pressure

D:\EM27_OutputData
    ├── analysis
    │    └── Sodankyla_SN039
    │       └── cal
    └── results
         └── Sodankyla_SN039_170608-170609
            ├── logfiles
            ├── ...
            └── comb_invparms_Sodankyla_SN039_170608-170608.csv

D:\Sodankyla_Retrieval
    ├── run_sodankyla.py
    ├── sodankyla_pressure_type.yml
    ├── sodankyla_coords.csv
    └── input_sodankyla.yml

D:\proffastpylot (does not contain any personal data)
    ├── docs
    ├── prf
    │    ├── pxcs20.exe
    │    ├── invers20.exe
    │    ├── ...
    │    ├── preprocess
    │    │    └── preprocess4.exe
    │    ├── out_fast
    │    ├── inp_fast
    │    ├── ...
    │    └── wrk_fast
    └── prfpylot
        └── ...
```

In this example, the relevant paths given in the input file would be:

```yaml
coord_file: sodankyla_coords.csv

interferogram_path: E:\EM27_Sodankyla_RawData\interferograms
map_path: E:\EM27_Sodankyla_RawData\map
pressure_path: E:\EM27_Sodankyla_RawData\pressure

pressure_type_file: sodankya_pressure_type.yml

analysis_path: D:\EM27_OutputData\analysis
result_path: D:\EM27_OutputData\results
```

Note that paths can also be relative.
