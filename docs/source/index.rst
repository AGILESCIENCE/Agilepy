Agilepy's documentation
=======================

Agilepy is an open-source Python package developed at `INAF/OAS Bologna <https://www.oas.inaf.it>`_  to analyse AGILE/GRID data built on top of the command-line version of the AGILE/GRID Science Tools.  

The main purpose of the package is to provide an easy to use high-level Python interface to analyse AGILE/GRID data by simplifying the configuration of the tasks and ensuring straightforward access to the data.  The current features are the generation and display of sky maps and light curves, the access to gamma-ray sources catalogues, the analysis to perform spectral model and position fitting including the background evaluation, the aperture photometry analysis, and the wavelet analysis.   In addition, Agilepy provides an engineering interface to analyse the time evolution of the AGILE off-axis viewing angle for a chosen sky region, comparing them with Fermi/LAT off-axis evolution.  

.. image:: static/agilecrab.jpg
   :alt: Agilepy
   :align: center

.. toctree::
  :maxdepth: 2
  :caption: Quickstart

  quickstart/main
  quickstart/installation
  quickstart/quick_start
  quickstart/jupyter_notebooks

.. toctree::
  :maxdepth: 2
  :caption: Manual
  
  manual/agile_grid_data
  manual/configuration_file
  manual/source_file
  manual/work_with_sources
  manual/products
  manual/advanced_configuration


.. toctree::
  :caption: API

  api/analysis_api
  api/engineering_api
  api/astroutils_api
  api/source_api

.. toctree::
  :caption: Science Tools

  sciencetools/tools
  sciencetools/mleinput
  sciencetools/mleoutput

.. toctree::
  :caption: Help

  help/help
  help/development
