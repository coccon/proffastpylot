# Pressure Input

_The pressure input was reorganized in version 1.1_

This article explains how to handle pressure data with PROFFASTpylot. To perform the retrieval, PROFFAST needs pressure data from the measurement site. In PROFFAST 2.2 or newer, the pressure is read together with the spectra in the input file of invers. A template for this file can be found in `prfpylot/templates`. The `pT_intraday.inp` file is deprecated; the interpolation of the pressure is handled by PROFFASTpylot.

## Provided options in PROFFASTpylot

Two parameters in the main input file specify how the pressure is handled by PROFFASTpylot.

- `pressure_path` is the location of the pressure files
- `pressure_type_file` links to a second input file in which the format of the pressure files is defined

## Pressure type file

An example pressure type file is provided in `example/log_type_pressure.yml`, describing the KIT-style data format. The path to the pressure files recorded by the KIT datalogger needs to be given as `pressure_path`. To adapt this file to your own file format, the options are explained in the following.

### Filename parameters

The filename parameters define how the filename of the pressure file is constructed. The pressure module of PROFFASTpylot will search for files with the naming `<basename><time><ending>`.

```yaml
filename_parameters:
  basename: ""
  time_format: "%Y-%m-%d"
  ending: "*.dat"
```

### Dataframe parameters

In the dataframe parameters, the internal formatting of your files is specified.

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

For the date- and timestamp, the datetime can be constructed from two separate columns (`time_key` and `date_key`) or one column (`datetime_key`). It will be parsed with the corresponding format string. In addition to the formats supported by the datetime package (see below), the key `POSIX-timestamp` can be used. This assumes the datetime column to be in seconds passed since 1970-01-01 in UTC. `df[pressure_key]` should contain the corresponding pressure values.

For more information, you can look at the [pandas documentation](https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.read_csv.html) of `read_csv()` and the [datetime package](https://docs.python.org/3/library/datetime.html#strftime-strptime-behavior).

## Additional Options

- A UTC offset of the pressure file can be given as `utc_offset`.
- In `data_parameters`, you can define minimum and maximum pressure values.
- The pressure values are multiplied by the `pressure_factor`. It can be used to correct for a height offset or a different unit. The pressure is expected to be given in hPa.
- The `pressure_offset` is added to the pressure values. The pressure value is expected to be given in hPa.
- The `max_interpolation_time` is the maximum time distance between two pressure data points. If the distance between two points is larger, the spectra belonging to the corresponding time are skipped. Can be set to a value in hours. Its default value is 2 hours. If the time is outside the range of the given pressure values, the nearest value will be used up to a time difference of `max_interpolation_time`.
