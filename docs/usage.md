# Usage

## Out of the box example: execution of an example

The prfPylot provides a out-of-the-box example which can be run directly after
the installation. For this you only have to execute `example\run.py`.
Everything else is executed automatically.

## Input file

In the input file you can specify the information about the program as the location of your in- and output files
as well as information about the processed data.  
It is stored in the `yaml` format.
In the file `example_sodankyla_input.yml` you can find and example with comments.
It is possible to either adjust this file to your requirements or to use the
program `prfpylot/create_inputfile.py` This program starts an assistant which
guides you step by step trough all relevant settings to create an input file
suitable for your site and needs.

## General use of the prfPylot

For starting the program you need to create an instance of the Pylot class with a input file.

```python
from prfpylot.pylot import Pylot

input_file = "input_sodankyla_example.yml"
my_pylot = Pylot(input_file)
```

Afterwards you can either run all steps of PROFFAST individually with the following commands:

```python
n_processes = 2
my_pylot.run_preprocess(n_processes)
my_pylot.run_pcxs(n_processes)
my_pylot.run_inv(n_processes)
my_pylot.combine_results(n_processes)
```
Or run all these steps together

```python
my_pylot.run(n_processes)
```

You can execute `run.py` to test this with the example data provided.


## Special case: Process already available spectra
How to start the processing chain with already available spectra, is explained
here.
One would like to do this for example if one have to reprocessed some data 
with an other pressure value or an other map-file.   
In this case you have to set the option `start_with_spectra: True`.
The path to the spectra is given to prfPylot as `analysis_path`.
Please NOTE: In this case the folder `analysis_path` point to must have the 
following substructur: `analysis/SiteName_InstrumentNumber/YYMMDD`



# Recommended folder sturcture

We propose a folder structure. It is explained in `folder_structure.md`.
