# Pressure Input

This article explains how handle pressure data with the prfPylot.
To perform the retrieval PROFFAST needs pressure data from the measurement site.
This data ist provided to PRFFAST in the file `pt_intraday.inp`.
A template for this file can be found in `prfpylot/prfpylot/templates`.


## Provided options 

Two parameters in the input file specify how the pressure in handled:

- `pressure_path` is the location of the pressure files
- `pressure_type` specifies the format of the pressure file

### pressure_type: original

It is possible to create the `pt_intraday.inp` file externally by your own.
Then, the files in the pressure_path are assumed to be named in the following way:
`<site_abbrev>_<yy-mm-dd>.inp`.

### pressure_type: log

For users of the KIT DataLogger, the pressure_type `log` can be specified. The pressure files recorded by the datalogger need to be placed inside the `pressure_path`.

### Custom pressure types

It is possible to define your own pressure type. Therefore you need to extend the class `PressureParameters` in `prfpylot/pressure.py`.
Add an entry for your new pressure type to the `filename_parameters` and `df_parameters` dictionaries in the class.

```python
class PressureParameters():
    """Storage for different pressure file formats."""

    filename_parameters = {
        "log": {
            "basename": "",
            "time_format": "%Y-%m-%d",
            "ending": "*.dat"
        }
    }

    df_parameters = {
        "log": {
            "key_pressure": "BaroTHB40",
            "key_time": "UTCtime___",
            "fmt_time": "%H:%M:%S",
            "csv_kwargs": {
                "sep": "\t"
            }
        }
    }
```

In the `filename_parameters` the naming of your pressure files can be specified.
In the df_parameters, the internal formatting of your file can be given.

The pressure file will be read in the following way.

```python
import pandas as pd
df = pd.read_csv(filename, **csv_kwargs)
```

`df[key_time]` is should be the time column and will be converted with the `fmt_time` format string. `df[key_pressure]` should contain the corresponding pressure values.

For more information you can look at the pandas documentation of `read_csv()` [[1](https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.read_csv.html)] and the datetime package [[2](https://docs.python.org/3/library/datetime.html#strftime-strptime-behavior)] can be consulted about the format string.
