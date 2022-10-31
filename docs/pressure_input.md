# Pressure Input

_The pressure input was reorganized in version 1.1_

This article explains how to handle pressure data with PROFFASTpylot.
To perform the retrieval PROFFAST needs pressure data from the measurement site.
PROFFAST 2.2 reads in this data together with the spectra in the invers input file.
A template for this file can be found in the `prfpylot/templates` folder.
The `pT_intraday.inp` file is deprecated, the interpolation of the pressure is handled by PROFFASTpylot.


## Provided options in PROFFASTpylot

Two parameters in the main input file specify how the pressure is handled by PROFFASTpylot.

- `pressure_path` is the location of the pressure files
- `pressure_type_file` links to a second input file in which the format of the pressure files is defined

## Pressure type file

For users using the data format in the KIT-style, a example pressure type file is provided in `example/log_type_pressure.yml`
The pressure files recorded by the KIT datalogger need to be placed inside the `pressure_path`.

To adapt this file two your own type of files, the most important options are explained in the following.



### Filename parameters

The filename parameters define how the filename of the pressure file is constructed.
```yaml
filename_parameters:
  basename: ""
  time_format: "%Y-%m-%d"
  ending: "*.dat"
```

### Dataframe parameters

In the dataframe parameters the internal formatting of your files is specified.
```yaml
dataframe_parameters:
  pressure_key: "BaroTHB40"
  time_key: "UTCtime___"
  time_fmt: "%H:%M:%S"
  date_key: "UTCdate_____"
  date_fmt: "%d.%m.%Y"
  datetime_key: ""
  datetime_fmt: ""
  csv_kwargs:
    sep: "\t"
```

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
For the date- and timestamp the datetime can be constructed from two separate columns (time_key and date_key) or one column (datetime_key). It will be parsed with the corresponding format string.
`df[pressure_key]` should contain the corresponding pressure values.

For more information you can look at the pandas [documentation](https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.read_csv.html) of `read_csv()` and the [datetime package](https://docs.python.org/3/library/datetime.html#strftime-strptime-behavior).

# Additional Options

- A UTC offset of the pressure file can be given as `utc_offset`.
- In `data_parameters` you can define minimum and maximum pressure values.
- The `frequency` of your files can be defined. Currently the frequencies `"daily"`, `"subdaily"` and `"yearly"` are available.
- The `pressure_factor` is multiplied to the pressure values. It can be used to correct for a height offset or a different unit. The pressure is expected to be given in hPa.
- The `pressure_offset` is added to the pressure values. The pressure value is expected to be given in hPa.
