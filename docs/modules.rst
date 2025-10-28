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
   :members:
   :undoc-members:
   :show-inheritance:


Filemover
----------

.. automodule:: filemover
   :members:
   :undoc-members:
   :show-inheritance:


Prepare
---------

.. automodule:: prepare
   :members:
   :undoc-members:
   :show-inheritance:



Auxiliary 
---------

.. automodule:: auxiliary
   :members:
   :undoc-members:
   :show-inheritance:

Output
------

NetCDF (following cf-conventions)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. automodule:: output.nc_cf_writer
   :members:
   :undoc-members:
   :show-inheritance:

HDF5 (following GEOMS conventions)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. automodule:: output.hdf_geoms_helper
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: output.hdf_geoms_writer
   :members:
   :undoc-members:
   :show-inheritance:
