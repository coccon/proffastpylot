# Usage

The usage of the prfPylot is explained with the help of an example from Sodankyla which is provided in `example/`.
The example interferograms, as well as the pressure and atmospheric data is located in `example/input_data`.

Executing PROFFAST with the prfPylot takes two steps:
1. Create a input file with the required information
2. Execute prfPylot via a python script.

`example/run.py` is a ready to use example where the corresponding input file is created automatically.

Both steps will be explained in more detail, in the following.



## Input file creation

In the input file you can specify the information about the program as the location of your in- and output files
and information about the processed data.  
It is stored in the `yaml` format.

In the file `example_sodankyla_input.yml` you can find and example with comments.
Adjust this file for your requirements.

The prfPylot provides also a interactive tool to create a input file.
You can run
```
python prfpylot/create_inputfile.py
```
And you will be asked about all input parameters.

## Starting the run

For starting the program you need to create an instance of the Pylot class with your input file.

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
Or run all these steps together

```python
my_pylot.run(n_processes)
```

## Folder structure

The results will be created automatically. Please see [`docs/folder_structure.md`](https://git.scc.kit.edu/cw4643/prfpylot/-/blob/master/docs/folder_structure.md) about how the results are organized.
