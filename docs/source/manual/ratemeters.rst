===================
Ratemeters Analysis
===================

The AGILE Scientific Ratemeter files contain the photon counts recorded by every AGILE instrument:
  * The Gamma-Ray Imaging Detector (GRID), with photon energy >50 MeV.
  * The Mini-Calorimeter (MCAL), energy band [0.4 - 100] MeV.
  * The SuperAGILE (SA), energy band [18 - 60] keV.
  * The 5 panels of the Anti-Coincidence System:
      * The Top panel (AC0), energy band [50 - 200] keV.
      * The 4 lateral panels (AC1, AC2, AC3, AC4), energy band [80 - 200] keV.

The counts recorded are integrated in the energy range of the detector and in time bins of fixed width of 1.024 s, with the exception of the SuperAGILE ratemeters which use bins of 0.512 s.

The ratemeter files (the so-called "3913" files) are provided in a compressed FITS Format optimized for data download from the satellite.
One file was produced for every satellite contact.

``Agilepy`` implements a ``AGRatemeters`` class that reads the ratemeters files and extract the Ratemeters Light Curves.
The Light Curves can be used to check for transient phenomena, and if the Burst Onest Time (``T0``) of a Burst is provided, the significance and duration of the Burst can be estimated.

The Analysis of the Scientific Ratemeters follows these general steps:
  1. Prepare a ``YAML`` configuration file for ``AGRatemeters``. You can do it manually or by using ``AGRatemeters.getConfiguration()``.
  2. Define a ``AGRatemeters`` object, and read the 3913 file with ``AGRatemeters.readRatemeters()``.
  3. You can plot the Light Curve with the ``AGRatemeters.plotRatemeters()`` function, perform a simple Aperture Photometry analysis with ``AGRatemeters.analyseSignal()``, perform a basic estimation of the burst duration with ``AGRatemeters.estimateDuration()``.


.. note:: Note on Detectors.
          Each instrument is pointed in a different direction.
          In particular, AC4 is always pointed towards the Sun.


The Light Curves produced by the ``AGRatemeters`` class include 3 columns:
  * ``OBT``: detection time in AGILE seconds.
  * ``COUNTS``: counts measured.
  * ``COUNTS_D``: counts de-trended with a FFT (Fast Fourier Transform) algorithm to remove background modulation due to the orbital motion and spinning of the satellite.


Configuration
-------------
We describe here the parameters of the configuration file section by section.


Output
~~~~~~
These parameters are common to all ``Agilepy`` classes.

 .. csv-table::
   :header: "Option", "Type", "Default", "Required", "Description"
   :widths: 20, 20, 20, 20, 100

   "outdir", "string", "", "yes", "Output Directory."
   "filenameprefix", "string", "ratemters_product", "no", "Prefix for files."
   "sourcename", "string", "rm-source", "no", "Tag with source name."
   "username", "string", "my_name", "no", "Tag with user name."
   "verboselvl", "int", "0", "yes", "0 for no extra logs, 1 for INFO, 2 for DEBUG."


Selection
~~~~~~~~~

 .. csv-table::
   :header: "Option", "Type", "Default", "Required", "Description"
   :widths: 20, 20, 20, 20, 100

   "file_path", "string", "", "yes", "Path to the input file."


Analysis
~~~~~~~~

 .. csv-table::
   :header: "Option", "Type", "Default", "Required", "Description"
   :widths: 20, 20, 20, 20, 100

   "timetype", "string", "", "yes", "Format of the Burst Oneset Time."
   "background_tmin", "float", "-4.0", "no", "Minimum Time used for background estimation."
   "background_tmax", "float", "-2.0", "no", "Maximum Time used for background estimation."
   "signal_tmin", "float", "-1.0", "no", "Minimum Time used for signal estimation."
   "signal_tmax", "float", "1.0", "no", "Maximum Time used for signal estimation."


.. note:: Note on Time Formats.
          The ``timetype`` can be ``TT`` or ``OBT`` for AGILE seconds (TT seconds since ``2004-01-01 00:00:00.000``), or a format acknowledged by the ``astropy.time.Time`` class.
          ``T0`` will be converted in AGILE seconds and used as reference time for plots and analyses.
