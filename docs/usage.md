# Usage

## Content

1. General Use
	2. Input file
	3. Starting the run
4. Special case: Process already available spectra

## General use

We explain the usage of the prfPylot with the help of an example from Sodankyla which is provided in `example/`.
The example interferograms, as well as the pressure and atmospheric data is located in `example/input_data`.

**Executing PROFFAST with the prfPylot takes two steps**:
1. Create a input file with the required information
2. Execute prfPylot via a python script.

`example/run.py` is a ready to use example where the corresponding input file is created automatically.

Both steps will be explained in more detail, in the following.



### Input file creation

The input file (stored in the yaml format) contains all the key information required by prfPylot and PROFFAST, e.g. the location of the input and output files, or meta information about the data to be processed.
In the input file “example_sodankyla_input.yml” for the test data set is provided as an example with plenty of comments and explanations.
Adjust this file to your requirements.

Alternatively, the prfPylot provides an interactive tool to create an input file.  
You can run
```
python prfpylot/create_inputfile.py
```
You will be asked about all input parameters.


### Starting the run

For starting the program you need to create an instance of the Pylot class with an input file.

```python
from prfpylot.pylot import Pylot

input_file = "input_sodankyla_example.yml"
MyPylot = Pylot(input_file)
```

Afterwards you can either run all steps of PROFFAST individually with the following commands:

```python
n_processes = 2
MyPylot.run_preprocess(n_processes)
MyPylot.run_pcxs(n_processes)
MyPylot.run_inv(n_processes)
MyPylot.combine_results(n_processes)
```
Or run all these steps automatically one after the other

```python
my_pylot.run(n_processes)
```

You can execute `run.py` to test this with the example data provided.


## Special case: Process already available spectra

If the spectra are already available, set the option `start_with_spectra` to `True` in the inputfile.
The path to the spectra is given to prfPylot by the entry `analysis_path`.
Note, that the folder `analysis_path` must have the
following substructure: `analysis/SiteName_InstrumentNumber/YYMMDD`.  
Afterwards, run the functions `run_pcxs`, `run_inv` and `combine_results`.

# Folder structure

The results will be created automatically. Please see [`docs/folder_structure.md`](https://git.scc.kit.edu/cw4643/prfpylot/-/blob/master/docs/folder_structure.md) about how the results are organized.
