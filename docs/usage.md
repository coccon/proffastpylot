# Usage

## Input file

In the input file you can specify the information about the program as the location of you in- and output files
and information about the processed data.  
It is stored in the `yaml` format.
In the file `example_sodankyla_input.yml` you can find and example with comments.
Adjust this file for your requirements.

## Starting the program

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

# Recommended folder sturcture

We propose a folder structure. It is explained in `folder_structure.md`.
