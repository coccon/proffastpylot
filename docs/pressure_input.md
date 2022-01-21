# Pressure Input

_This might be restructured in the future._

This article explains how handle pressure data with PROFFASTpylot.
To perform the retrieval PROFFAST needs pressure data from the measurement site.
This data ist provided for PROFFAST using the file `pt_intraday.inp`.
A template for this file can be found in the `prfpylot/templates` folder.


## Provided options in PROFFASTpylot

Two parameters in the input file specify how the pressure is handled by PROFFASTpylot.

- `pressure_path` is the location of the pressure files
- `pressure_type` specifies the format of the pressure file

### pressure_type: original

It is possible to create the `pt_intraday.inp` file externally by your own.
Then, the files in the pressure_path are assumed to be named in the following way:
`<site_abbrev>_<yy-mm-dd>.inp`.

### pressure_type: log

For users using the dataformat in the KIT-style, the pressure_type `log` have to be used.
The pressure files recorded by the KIT datalogger need to be placed inside the `pressure_path`.

### Custom pressure types

It is possible to define your own pressure type. Therefore you need to extend the class `PressureParameters` in `prfpylot/pressure.py`. Add an entry for your new pressure type to the `filename_parameters` and `dataframe_parameters` dictionaries in the class.

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

    dataframe_parameters = {
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
In the `dataframe_parameters`, the internal formatting of your file can be given.

The pressure file will be read in the following way.

```python
import pandas as pd
params = filename_parameters
csv_kwargs = dataframe_parameters["csv_kwargs"]

filename = "".join(
    [
        params["basename"],
        date.strftime(params["time_format"]),
        params["ending"]
    ]
)

df = pd.read_csv(filename, **csv_kwargs)
```

`df[key_time]` is the name of the time column and will be converted with the `fmt_time` format string. `df[key_pressure]` should contain the corresponding pressure values.

For more information you can look at the pandas [documentation](https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.read_csv.html) of `read_csv()` and the [datetime package](https://docs.python.org/3/library/datetime.html#strftime-strptime-behavior).
