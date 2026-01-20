# Time Offsets

PROFFASTpylot allows to process measurements which have been recorded near the dateline, where one local day belongs to two different UTC days and vice versa.

Three different times are of importance

1. The UTC time
2. The measurement time (i.e. the time of the laptop)
3. The local time

with the corresponding offsets between them

```
utc to local time = utc to measurement time + measurement time to local time
```

The measurement time can be UTC time, local time or any other time. The user has to provide the offset between UTC and measurement time in the input file (`utc_offset`). `PROFFASTpylot` calculates the local time automatically from the given coordinates. In case your computer clock was not accurate, `utc_offset` can also be set to non-integer values.

In case of UTC measurements near the date line it splits the spectra of one local day into two independent processes for the corresponding location of the spectra in the folders that are sorted by measurement date. This is necessary since the map file corresponds to the local noon. Nevertheless, we strongly recommend you to use local time in case you are measuring near the date line. It makes handling of the data less confusing. E.g., the start- and end-date in the input file correspond to measurement time, not to local time.
