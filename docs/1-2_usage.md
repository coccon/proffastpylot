# Usage

## Content

1. General use
	- Input file creation
	- Starting the run
2. Special case: Process spectra directly
3. Folder Structure
4. Advanced usage: Logging


## 1. General use

**Ready-to-use Example**  
You can follow the usage of PROFFASTpylot with the help of an example from Sodankylä which is provided as `example/run.py`.
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

The results will be created automatically. Please see the **Folder structure** article about how the results are organized.

## 4. Advanced usage: Logging

The PROFFASTpylot has an built-in logging functionality.
By default the user do not have to care about this.
This section is only intended for advanced usage of the PROFFASTpylot, e.g. when
it is embedded into an larger environment.

The PROFFASTpylot uses the standard Python [logging module](https://docs.python.org/3/library/logging.html).
There are three possible use cases on how to use the logging functionailty of PROFFASTpylot:

1. **Default mode:**  
As the PROFFASTpylot is mainly intended to be used as a standalone program,
logging is configured such, that a custom logger object is created and stream and
file handlers are added to this logger. The logger instance is initialized using the current datetime in the format YYMMDDHHMMSSssss as the loggers name.
In this mode the logger is mainly encapsulated to the PROFFASTpylot and difficult to be accessed from the outside.

2. **Submodule mode**:  
The `submodule mode` is designed to use the Pylot as a submodule. This means that the logger instance is created outside of the PROFFASTpylot and passed to the Pylot as an argument. For this, the `Pylot` class has the argument `external_logger` to which an instance of the external logger is passed to.
This mode has the advantage, that it is possible to use the logging before an instance of the Pylot has been created.  
Note, that to this instance a logging file handler will be added which results in the standard logging file within the result directory.
To this handler a filter is applied which only passes messages originating from the Pylot. Hence, the logfile in the PROFFASTpylot result dir does NOT conatain any of the log messages from outside of the PROFFASTpylot
Furthermore, no stream handler is added. This must be taken care of outside of the PROFFASTpylot.

3. **Mainmodule mode**:  
The `mainmodule mode` is designed to use the Pylot as the main module which takes care of the logging and also is used to record the logging messages of other modules.
This is realized by passing a name to the Pylot using the `loggername` argument, which will be used to initialize the logger.
Then, the logger can be accessed by the codesnippet below. This only works if the name of the logger passed to the Pylot is the same as the one used to initialize a new logger.
```
import logging
from prfpylot.pylot import Pylot

MyPylot = Pylot(input_file, logginglevel="info", loggername="my_logger")
my_logger = logging.get_logger("my_logger")
my_logger.info("This message is written from outside of the PROFFASTpylot")
```
All messages you will log there will also appear in the log file of the 
PROFFASTpylot.