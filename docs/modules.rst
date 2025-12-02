Modules
==================

This page list the internal methods of all modules, for developing purposes.

PROFFASTpylot consists of four main modules:

* **Pylot**: High level functionality.
* **Filemover**: Create a consistent file structure from the PROFFAST output.
* **Prepare**: Derive all processing options from the input.
* **Auxiliary**: Read and interpolate the pressure and coordinate data.
* **Output**: Write additional output formats.


Pylot
------

.. automodule:: pylot


Filemover
----------

.. automodule:: filemover



Prepare
---------

.. automodule:: prepare

Auxiliary 
---------

.. automodule:: auxiliary

Output
------

NetCDF (following cf-conventions)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. automodule:: output.nc_cf_writer

HDF5 (following GEOMS conventions)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. automodule:: output.hdf_geoms_helper
   :undoc-members:


.. automodule:: output.hdf_geoms_writer
   :undoc-members:

