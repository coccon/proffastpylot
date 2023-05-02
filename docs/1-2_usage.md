# Usage

## Content

1. General use
	- Input file creation
	- Starting the run
2. Special case: Process spectra directly
3. Folder Structure


## 1. General use

**Ready-to-use Example**  
You can follow the usage of PROFFASTpylot with the help of an example from Sodankyla which is provided as `example/run.py`.
The example input data (i.e. the example interferogram, map- and pressure files) are downloaded automatically when running `run.py` the first time.
The runscript needs to be executed inside the `example` folder.

### Executing PROFFAST with the PROFFASTpylot takes two steps
1. Create an input file with the required information
2. Execute PROFFASTpylot via a Python script

Both steps will be explained in more detail, in the following.

#### Input file creation

The input file (stored in the yaml format) contains all the key information required by PROFFASTpylot and PROFFAST, e.g. the location of the input and output files, or meta information about the data to be processed.
An example with explanations (`example_sodankyla_input.yml`) is provided. It contains all options that are required to process the example data set.
Adjust this file to your requirements.

#### Starting the processing

For starting the processing you need to create an instance of the Pylot class with an input file.

```python
from prfpylot.pylot import Pylot

if __name__ == "__main__":
    input_file = "input_sodankyla_example.yml"
    MyPylot = Pylot(input_file)
```
Note that the `if __name__ == "__main__"` statement needs to be put before initializing the Pylot to prevent problems with the multiprocessing on Windows.

Afterwards all steps of PROFFAST can be executed automatically one after the other:

```python
    MyPylot.run(n_processes)
```

Alternatively you can run all steps of PROFFAST individually with the following commands:

```python
    n_processes = 2
    try:
        MyPylot.run_preprocess(n_processes)
        MyPylot.run_pcxs(n_processes)
        MyPylot.run_inv(n_processes)
        MyPylot.combine_results()
    finally:
        MyPylot.clean_files()
```

You can execute `run.py` to test this with the example data provided.


## 2. Special case: Process spectra directly

If the spectra are already available, set the option `start_with_spectra` to `True` in the input file.
The path to the spectra is given to PROFFASTpylot by the entry `analysis_path`.
Note, that the folder `analysis_path` must have the
following substructure: `analysis/SiteName_InstrumentNumber/YYMMDD`.  
Afterwards, `Pylot.run()` will not execute preprocess.

## 3. Folder structure

The results will be created automatically. Please see [`docs/folder_structure.md`](https://gitlab.eudat.eu/coccon-kit/proffastpylot/-/blob/master/docs/1-4_folder_structure.md) about how the results are organized.
