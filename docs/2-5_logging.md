# Advanced Logging Options

The PROFFASTpylot has an built-in logging functionality.
By default the user do not have to care about this.
This section is only intended for advanced usage of the PROFFASTpylot, e.g. when
it is embedded into an larger environment.

The PROFFASTpylot uses the standard Python [logging module](https://docs.python.org/3/library/logging.html).
There are three possible use cases on how to use the logging functionality of PROFFASTpylot:

1. **Default mode:**  
    As the PROFFASTpylot is mainly intended to be used as a standalone program,
    logging is configured such, that a custom logger object is created and stream and
    file handlers are added to this logger. The logger instance is initialized using the current datetime in the format YYMMDDHHMMSSssss as the loggers name.
    In this mode the logger is mainly encapsulated to the PROFFASTpylot and difficult to be accessed from the outside.
2. **Submodule mode**:  
    The `submodule mode` is designed to use the Pylot as a submodule. This means that the logger instance is created outside of the PROFFASTpylot and passed to the Pylot as an argument. For this, the `Pylot` class has the argument `external_logger` to which an instance of the external logger is passed to.
    This mode has the advantage, that it is possible to use the logging before an instance of the Pylot has been created.  
    Note, that to this instance a logging file handler will be added which results in the standard logging file within the result directory.
    To this handler a filter is applied which only passes messages originating from the Pylot. Hence, the logfile in the PROFFASTpylot result directory does NOT contain any of the log messages from outside of the PROFFASTpylot
    Furthermore, no stream handler is added. This must be taken care of outside of the PROFFASTpylot.
3. **Mainmodule mode**:  
    The `mainmodule mode` is designed to use the Pylot as the main module which takes care of the logging and also is used to record the logging messages of other modules.
    This is realized by passing a name to the Pylot using the `loggername` argument, which will be used to initialize the logger.
    Then, the logger can be accessed by the code snippet below. This only works if the name of the logger passed to the Pylot is the same as the one used to initialize a new logger.

```
import logging
from prfpylot.pylot import Pylot

MyPylot = Pylot(input_file, logginglevel="info", loggername="my_logger")
my_logger = logging.get_logger("my_logger")
my_logger.info("This message is written from outside of the PROFFASTpylot")
```
All messages you will log there will also appear in the log file of the PROFFASTpylot.
