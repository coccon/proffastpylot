# Folder Structure

This articles gives an overview about where to place or find what.


## Input data

You can specify three paths for your input data:
The path
1. of the interferograms,
2. of the the pressure files and
3. of the map files (containing atmospheric information).

Optionally a file with the coordinates of the measurements can be provided.

In our example all these folders and files are in `example/input_data`.

### Interferograms
The `interferogram_path` should be a folder with the interferograms inside.
It is expected to have the following structure:

```
interferogram_path
├── YYMMDD
│	├── YYMMDDSN.XXX
│	└── YYMMDDSN.XXX
├── YYMMDD
...
```

### Pressure input
Inside the `pressure_path` for each day of measurements a pressure file should be provided.
The filename should include the date information, apart from this the naming and the format of the file are flexible.
More information on the input of pressure data can be found in [`docs/pressure_input.md`]().


### Map Files

The prfPylot support the new and old version of map files.


## Output data
Two output paths have to be specified: the `analysis_path` and the `result_path`


### Analysis path
In the analysis folder day-specific output files from PROFFAST are stored directly.
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
The results of the retrieval of all days are merged and the logfiles of the runs are stored in `result_path/logfiles`
