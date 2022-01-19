# Folder Structure

This articles gives an overview about the folder structure used by the prfPylot.    
The needed folders can be divided into three categories:
 1. Input data: E.g. Interferograms, pressure files, map files.
 2. Output data: E.g. the spectra, the results of the processing, some config files.
 3. The PROFAST path: the folder where the binaries of the profast files are located.

 Please note that those three folders do not have to be in the same parent folder.
 The user is free to choose the folder structure as he likes.  
_However, to run the example files using [`run.py`](https://gitlab.eudat.eu/coccon-kit/proffastpylot/-/blob/master/example/run.py) the folder structure must be as given in [`docs/installation.md`](https://gitlab.eudat.eu/coccon-kit/proffastpylot/-/blob/master/docs/installation.md)_

## 1. Input data

You can specify three paths for your input data:
The path
1. of the interferograms,
2. of the the pressure files and
3. of the map files (containing atmospheric information).

Optionally a file with the coordinates of the measurements can be provided.

In our example all these folders and files are in `example/input_data`.

### Interferograms
The `interferogram_path` should be a folder with the interferograms inside.
It needs to have the following structure:
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
Inside the `pressure_path` for each day of measurements a pressure file should be provided.
The filename should include the date information, apart from this the naming and the format of the file are flexible.
More information on the input of pressure data can be found in [`docs/pressure_input.md`]().


### Map Files

The prfPylot support the usage of the GGG2014 and GGG2020 map files.
It detects automatically what kind of map file is used.
The path to the files is specified by the `map_path` in the input file.

## 2. Output data
Two output paths have to be specified: the `analysis_path` and the `result_path`


### Analysis path
Day-specific output files are written to the analysis folder by PROFAST automatically.
The analysis folder has the following structure:

```
analysis_path
├── <site_name>_<instrument>
|	├──YYMMDD
│	|	├── cal
│	|	└── pT
|	├──YYMMDD
...
```

It is compatible to PROFFIT

### Result path
In the result folder run specific information is stored.
In ths folder the retrieval of all days are stored. Those files are merged to a
single file `combined_invparms_<site_name>_StartStopDates<YYYYMMDD>_<YYYYMMDD>.csv`.
Furhtermore the logfiles of the runs are stored in `result_path/logfiles`.


## 3. The PROFAST path

The prfPylot needs the information where the binaries of the profast folder
are stored in. This information is passed to prfPylot by `<profast_path>`.


# Example for a possible folder structure:
An example of how a folder structure could look like is given below.
```
D:\EM27_InputData
    ├── coords.csv
    ├── interferograms_sodankyla
    ├── map_sodankyla
    └── pressure_sodankyla


D:\EM27_OutputData
    ├── analysis
    │    └── Sodankyla_SN039
    └── result_data
        └── results_sodankyla


D:\proffastpylot
    ├── docs
    ├── run_sodankyla.py
    ├── input_sodankyla.yml
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
        ├── ILS-List.csv
        ├── prepare.py
        ├── ...
        └── templates
              └── ...

```
In this example some of the paths would be:
```
proffast_path: D:\proffastpylot\prf
interferogram_path: D:\EM27_InputData\interferograms_sodankyla
analysis_path: D:\EM27_OutputData\analysis
```
