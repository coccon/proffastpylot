# Usage

## Content

1. General use
    - Input file creation
    - Starting the run
2. Special case: Process spectra directly
3. Folder Structure

## 1. General use

**Ready-to-use Example**

You can follow the usage of PROFFASTpylot using an example from Sodankylä, provided in `example/run.py`. The example input data (i.e., the example interferogram, map, and pressure files) are downloaded automatically when running `run.py` for the first time. The runscript needs to be executed inside the `example` folder.

### Executing PROFFAST with the PROFFASTpylot takes two steps

1. Create an input file with the required information
2. Execute PROFFASTpylot via a Python script

Both steps will be explained in more detail in the following.

#### Input file creation

The input file (stored in the YAML format) contains all the key information required by PROFFASTpylot and PROFFAST, e.g., the locations of the input and output files, or metadata about the data to be processed. An example with explanations (`example_sodankyla_input.yml`) is provided. It contains all options required to process the example data set. Adjust this file to your requirements.

#### Starting the processing

To start the processing, you need to create an instance of the Pylot class with an input file.

```python
from prfpylot.pylot import Pylot

if __name__ == "__main__":
    input_file = "input_sodankyla_example.yml"
    MyPylot = Pylot(input_file=input_file)
```

Note that the `if __name__ == "__main__"` statement must be placed before initializing Pylot to prevent multiprocessing issues on Windows.

Afterwards, all steps of PROFFAST can be executed automatically one after the other:

```python
    MyPylot.run(n_processes)
```

Alternatively, you can run all steps of PROFFAST individually with the following commands:

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

#### Alternative way of starting the processing

In the case above, we loaded a YAML file to get the input parameters. However, when processing larger datasets or embedding PROFFASTpylot into a larger environment, it can be helpful to pass the input parameters directly as a dictionary instead of a file. In this case, the initialization would look like:

```python
from prfpylot.pylot import Pylot

input_dict = {
    "instrument_number": "SN039",
    "site_name": "Sodankyla",
    "site_abbrev": "so",
    # ... and all other needed parameters
}

if __name__ == "__main__":
    MyPylot = Pylot(input_file=input_dict)
```

## 2. Special case: Process spectra directly

If the spectra are already available, set the option `start_with_spectra` to `True` in the input file. The path to the spectra is provided to PROFFASTpylot via the `analysis_path` entry. Note that the folder `analysis_path` must have the following substructure: `analysis/SiteName_InstrumentNumber/YYMMDD`. Afterwards, `Pylot.run()` will not execute preprocess.

## 3. Folder structure

The results will be created automatically. Please see the **Folder structure** article about how the results are organized.
