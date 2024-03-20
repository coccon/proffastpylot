# Instrument Parameters

**WARNING:** The settings described here are only for advanced users.
For a regular processing of EM27/SUN spectra, the settings given here are not needed.

Starting with PROFFAST 2.3. there is the possibility to process data from other
instruments than the EM27/SUN.

Technically this is solved by adding new parameter in the PREPROCESS input file,
which allows to adapt the behavior of the PREPROCESS to the instrument.

PROFFASTpylot comes with several templates prepared already for the following instruments:   
    - `em27`
    - `tccon_ka_hr`
    - `tccon_ka_lr`
    - `tccon_default_hr`
    - `tccon_default_lr`
    - `invenio`
    - `vertex`
    - `ircube`

To use one of these instruments set the parameter `instrument_parameters` to one of the options above.

Alternatively, it is possible to give the path to a so called `instrument-parameter-file`.
This option is only recommended to be used by expert-users. Therefore no template for this case is given.
If you want to create your own `instrument-parameter-file` please adapt one of the prepared parameter files.  
They are located in `prfpylot\templates\instrument_templates`