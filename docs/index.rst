.. PROFFASTpylot documentation master file, created by
   sphinx-quickstart on Tue Jul 25 15:45:55 2023.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to PROFFASTpylot's documentation!
==========================================

Measurements of atmospheric greenhouse gas (GHG) concentrations are important to assess the effect of climate change mitigation policies.
Additionally, climate models depend on a precise knowledge of greenhouse gas abundances and emissions.
A variety of measurement methods is addressing these needs.
The Collaborative Carbon Column Observing Network (COCCON) was established in 2019, as a supporting framework for users of the portable Fourier-Transform spectrometers EM27/SUN, that measures precisely and accurately GHG column abundances from near-infrared solar absorption spectra.
To ensure common quality standards across the COCCON, raw EM27/SUN measurements are processed with the PROFFAST Fortran routines.
The Python interface PROFFASTpylot significantly reduces the workload during the processing of large sets of observational data and supports a network-wide consistent data processing.


For more information about PROFFAST, see https://www.imk-asf.kit.edu/english/3225.php.
The PROFFASTpylot source code is available at https://gitlab.eudat.eu/coccon-kit/proffastpylot. If you have any comments or questions, contact us at benedikt.herkommer@kit.edu and lena.feld@kit.edu. You are welcome to contribute.

This documentation and the PROFFASTpylot source code is licensed under GPL-3.0.



User Guide
===========

In the following, you can find all instructions on PROFFASTpylot.


Getting Started
----------------

.. toctree::
   1-1_installation.md
   :maxdepth: 1
.. toctree::
   1-2_usage.md
   :maxdepth: 1
.. toctree::
   1-3_pressure_input.md
   :maxdepth: 1
.. toctree::
   1-4_folder_structure.md
   :maxdepth: 1


User Information
-----------------

.. toctree::
   2-1_all_input_parameters.md
   :maxdepth: 1

.. toctree::
   2-2_time_offsets.md
   :maxdepth: 1

.. toctree::
   2-3_ils_parameters.md
   :maxdepth: 1

.. toctree::
   2-4_instrument_parameters.md
   :maxdepth: 1

.. toctree::
   2-5_logging.md
   :maxdepth: 1

.. toctree::
   2-6_troubleshooting.md
   :maxdepth: 1




Developer Information
---------------------

.. toctree::
   3-1_contribution_notes.md

.. toctree::
   modules
   :maxdepth: 2
    


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
