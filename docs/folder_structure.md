# Folder Structure

We use the following folder structure in our example. This can be adapted to some extend and might me changed in future versions.

# Example

```
prfpylot
├── data
│	└── Sodankyla
│		├── log
│		├── map
│		└── SN039
│			└── raw_data
│				├── 170608
│				└── 170609
├── docs
├── prf
├── prfpylot
└── templates
```

Place the interferograms in `raw_data`, the map- and logfiles can be placed in the corresponding folders in the `<site>` folder.
In data you can edit the files `coords.csv` and `ILSList.csv` to insert your ILS parameters and the coordinates of the site.
