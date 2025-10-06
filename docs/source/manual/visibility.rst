===================
Visibility Analysis
===================

The AGILE satellite operated from April 23, 2007 to January 18, 2024 observing thousands of astrophysical sources.

The AGILE spacecraft operated in "pointing mode" from the beginning of the mission to October 15, 2009, completing 101 observation blocks (OBs).
The OBs usually consisted of predefined long exposures, drifting about 1 deg per day with respect to the initial boresight direction to obey solar panels constraints.

In November 2009, the attitude control system was reconfigured, and scientific operations were performed "spinning mode" until the end of the mission.
AGILE scanned ≈ 80% sky daily (exposure of ≈ 7 · 106 cm2 s) with an angular velocity of about 0.8 deg s-1, performing 200 passes per day on the same sky region.

The visibility of a source thus depend on the off-axis angle with respect to the satellite pointing direction.

``Agilepy`` implements a ``AGVisibility`` class that reads the "log files" (AGILE spacecraft files) and extract the Spacecraft Pointing Direction and its time evolution.
The quantity can be used to compute the Off-axis angle of a source of interest to check its visibility.
If a Fermi Spacecraft file is provided, the same operation can be performed on the file for comparison purposes.

The Visibility Analysis follows these general steps:
  1. Prepare a ``YAML`` configuration file for ``AGVisibility``. You can do it manually or by using ``AGVisibility.getConfiguration()``.
  2. Define a ``AGVisibility`` object, and read the log files with ``AGVisibility.computePointingDirection()``.
  3. You can plot the Off-axis angle of a source of interest with ``AGVisibility.plotVisibility()``.
  4. Additionally, the off-axis angle from Fermi/LAT can be computed with ``AGVisibility.getFermiPointing()``.


The AGILE Pointing Direction is taken from the columns ``TIME``, ``ATTITUDE_RA_Y``, ``ATTITUDE_DEC_Y`` of the AGILE log files.
The Fermi Pointing Direction is taken from the columns ``START``, ``STOP``, ``RA_SCZ``, ``DEC_SCZ`` of the Fermi spacecraft files.
The results are provided as `astropy Table <https://docs.astropy.org/en/latest/table/index.html>`_ objects, contain the satellites' pointing coordinates for every given time and the source off-axis angle.
They are saved in ``.csv`` format by default.




Configuration
-------------
We describe here the parameters of the configuration file section by section.


Output
~~~~~~
These parameters are common to all ``agilepy`` classes.

 .. csv-table::
   :header: "Option", "Type", "Default", "Required", "Description"
   :widths: 20, 20, 20, 20, 100

   "outdir", "string", "", "yes", "Output Directory."
   "filenameprefix", "string", "ratemters_product", "no", "Prefix for files."
   "sourcename", "string", "rm-source", "no", "Tag with source name."
   "username", "string", "my_name", "no", "Tag with user name."
   "verboselvl", "int", "0", "yes", "0 for no extra logs, 1 for INFO, 2 for DEBUG."

Input
~~~~~

 .. csv-table::
   :header: "Option", "Type", "Default", "Required", "Description"
   :widths: 20, 20, 20, 20, 100

   "logfile", "string", "", "yes", "path to the index file listing relevant AGILE log files to be extracted."
   "fermiSpacecraftFile", "string", "null", "no", "path to the Fermi spacecraft file."


Analysis
~~~~~~~~

 .. csv-table::
   :header: "Option", "Type", "Default", "Required", "Description"
   :widths: 20, 20, 20, 20, 100

   "timetype", "string", "tt", "no", "Format of the Min and Max Times. AGILE seconds can be expressed as `tt`."
   "tmin", "float", "104371200", "no", "Minimum Time used for visibility estimation. Default is TT=104371200, i.e. 2007-04-23 00:00:00."
   "tmax", "float", "632620800", "no", "Maximum Time used for visibility estimation. Default is TT=632620800, i.e. 2024-01-18 00:00:00."
   "step", "float", "1.0", "no", "time interval in seconds between two consecutive points in the resulting table. Minimum accepted value: 0.1."

Source
~~~~~~

 .. csv-table::
   :header: "Option", "Type", "Default", "Required", "Description"
   :widths: 20, 20, 20, 20, 100

   "frame", "string", "icrs", "no", "Reference frame to express the coordinates of the target source."
   "coord1", "float", "null", "no", "1st coordinate of the source. If not provided, the off-axis angle is not computed and only the satellite pointing direction is extracted. It can be set during the analysis."
   "coord2", "float", "null", "no", "2nd coordinate of the source. If not provided, the off-axis angle is not computed and only the satellite pointing direction is extracted. It can be set during the analysis."

