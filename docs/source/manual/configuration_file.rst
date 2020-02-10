.. _configuration-file:

******************
Configuration file
******************

A configuration file is needed to customize the software behaviour and it must be passed to the AGAnalysis class constructor.

The configuration file's format is `yaml <https://docs.ansible.com/ansible/latest/reference_appendices/YAMLSyntax.html>`_ .

It is composed by several sections and each section holds several configuration options, some of which are optional (having a default value), some are required.

It supports the environment variables, that you can use to define filesystem paths.

The minimal configuration a user is required to write, it is composed by the following options:

.. code-block:: yaml

  input:
    evtfile: $AGILE/agilepy-test-data/evt_index/agile_proc3_fm3.119_asdc2_EVT.index
    logfile: $AGILE/agilepy-test-data/log_index/agile_proc3_data_asdc2_LOG.log.index

  output:
    outdir: $AGILE/agilepy-test-data/unittesting-output/utils/logs
    filenameprefix: testcase
    logfilenameprefix: testcase
    verboselvl: 2

  selection:
    tmin: 456361778
    tmax: 456537945
    timetype: TT
    glon: 80
    glat: 0


The next paragraphs of this document will describe each configuration option.


Section: *'input'*
==================
This section defines the input data files.
The input data files are indexes: each row of the file holds the position of an
actual event data/log file together with the time interval it refers to.

.. csv-table::
   :header: "Option", "Description", "Type", "Required", "Default"
   :widths: 20, 20, 20, 20, 100

   evtfile, "Path to index evt file name", str, yes, null
   logfile, "Path to index log file name", str, Yes, null


Section: *'output'*
===================
The output section collects options related to the output files generation.

The *'outdir'* option sets the root directory of the analysis results where all output files are written.

Agilepy has two type of loggers, one logging messages on the console, the other logging message on file.
The *'verboselvl'* option sets the verbosity of the Agilepy console logger. The Agilepy file logger verbosity is set to 2 by default.
There are 4 kind of messages based on their importance factor:

  - CRITICAL: a message describing a critical problem, something unexpected, preceding a program crash or an Exception raise.
  - WARNING: an indication that something unexpected happened, or indicative of some problem in the near future (e.g. ‘disk space low’). The software is still working as expected.
  - INFO: confirmation that things are working as expected.
  - DEBUG: detailed information, typically of interest only when diagnosing problems.

.. csv-table::
   :header: "Option", "Description", "Type", "Required", "Default"
   :widths: 20, 20, 20, 20, 100

   "outdir", "Path of the output directory", "str", "yes", "null"
   "filenameprefix", "The filename prefix of each output file", "str", "yes", "null"
   "logfilenameprefix", "The filename prefix of the log file", "str", "yes", "null"
   "verboselvl", "| 0 ⇒ *CRITICAL* and *WARNING* messages are logged on the console.
   | 1 ⇒ *CRITICAL*, *WARNING* and *INFO* messages are logged on the console.
   | 2 ⇒ *CRITICAL*, *WARNING*, *INFO* and *DEBUG* messages are logged on the console",  "int", "no", 1


Section: *'selection'*
======================

The temporal, spatial and spectral binning of the data can be customized using the configuration option of this section.

The *ROI* (region of interest) center is defined by giving explicit Galactic sky coordinates (glon and glat).

.. csv-table::
   :header: "Option", "Description", "Type", "Default", "Required"
   :widths: 20, 20, 20, 20, 100

   "emin", "Energy min in MeV", "int", 100, "no"
   "emax", "Energy max in MeV", "int", 10000, "no"
   "glat", "Center of the ROI ('*latitude*' or *'b'*)", "float", "null", "no"
   "glon", "Center of the ROI ('*longitude*' or *'l'*)", "float", "null", "no"
   "tmin", "Minimum time (in MJD or TT)", "float", "null", "yes"
   "tmax", "Maximum time (in MJD or TT)", "float", "null", "yes"
   "timetype", "| The date format of tmin and tmax.
   | Possibile values: [*'MJD'*, *'TT'*]", "str", "null", "yes"
   "timelist", "| A list of time intervals tstart tstop in TT
   | format to generate maps
   | integrated within a time window.
   | If specified, *'tmin'* and *'tmax'* are ignored.", "str", "null", "no"
   "projtype", "Projection mode. Possible values: ['*WCS*']", "str", "WCS", "no"
   "proj", "| Spatial projection for WCS mode.
   | Possible values: ['*ARC*', '*AIT*']", "str", "ARC", "no"
   "filtercode", "filtercode = 5 select G filtercode = 0 select G+L+S", "int", 5, "no"
   "fovradmin", "fovradmin < fovradmax", "int", 0, "no"
   "fovradmax", "fovradmax > fovradmin", "int", 60, "no"
   "albedorad", "albedo selection cut", "int", 80, "no"
   "dq", "| Data quality selection filter.
   | A combination of fovradmax and albedorad.
   | dq = 0 use specified or default
   | albedorad and fovradmax. Possible values are:
   | dq = 1 -> albedorad=80, fovradmax=60
   | dq = 2 -> albedorad=80, fovradmax=50
   | dq = 3 -> albedorad=90, fovradmax=60
   | dq = 4 -> albedorad=90, fovradmax=50
   | dq = 5 -> albedorad=100, fovradmax=50
   | dq = 6 -> albedorad=90, fovradmax=40
   | dq = 7 -> albedorad=100, fovradmax=40
   | dq = 8 -> albedorad=90, fovradmax=30
   | dq = 9 -> albedorad=100, fovradmax=30", "int", 0, "no"
   "phasecode", "| Photon list selection parameter based
   | on the orbital phase. If 'None', the
   | automated selection is done following
   | the *'phasecode'* rule", "int", "null", "no"

Phasecode rule
--------------

  - phasecode = 2 -> spinning mode, SAA excluded with AC counts method.
  - phasecode = 6 -> spinning mode, SAA excluded according to the magnetic field intensity (old definition of SAA, defined by TPZ)
  - phasecode = 18 -> pointing mode, SAA and recovery exluded.

It is suggested to use phasecode = 2 for data taken in spinning mode.

.. code-block:: ruby

    def setPhaseCode(tmax)
       if @phasecode == -1
          if tmax.to_f >= 182692800.0
             @phasecode = 6 #SPIN
          else
             @phasecode = 18 #POIN
          end
       end
    end



Section: *'maps'*
=================

These options control the behaviour of the sky maps generation tools.
The *'energybin'* and *'fovbinnumber'* modify the number of maps that are generated.

The *'energybin'* option is a list of strings with the following format:

.. code-block:: yaml

    energybins:
      - 100, 1000
      - 1000, 3000

The *'fovbinnumber'* option sets the number of bins between *'fovradmin'* and *'fovradmax'* as:

.. math::

    number\_of\_bins = (fovradmax-fovradmin)/fovbinnumber

.. note:: One map is generated for each possible combination between the *'energybin'* (emin, emax) and the *'fovbinnumber'* (fovmin, fovmax).
   The order of map generation is described by the following pseudocode:

   | For each fovmin..fovmax:
   |    For each emin..emax:
   |        generateMap(fovmin, fovmax, emin, emax)


.. csv-table::
   :header: "Option", "Description", "Type", "Default", "Required"
   :widths: 20, 100, 20, 20, 20

   "mapsize", "Width of the ROI in degrees","float", 40, "no"
   "useEDPmatrixforEXP", "Use the EDP matrix to generate the exposure map. Possible values = [*yes*, *no*]", "boolean", "yes", "no"
   "expstep", "| Step size of the exposure map, if 'None' it depends by
   | round(1 / binsize, 2) (e.g. 0.3->3, 0.25->4, 0.1->10)", "int", "None", "no"
   "spectralindex", "Spectral index of the exposure map", "float", 2.1, "no"
   "timestep", "LOG file step size of exposure map (LOG file are at 0.1s)", "float", 160, "no"
   "skytype", "| gasmap:
   | 0) SKY000-1 + SKY000-5,
   | 1) gc_allsky maps + SKY000-5,
   | 2) SKY000-5
   | 3) SKY001 (old galcenter, binsize 0.1, full sky),
   | 4) SKY002 (new galcenter, binsize 0.1, full sky) ", "int", "4", "no"
   "binsize", "Spatial bin size in degrees", "float", 0.1, "no"
   "energybin", "------- completare -----------", "List<String>", "[100, 10000]", "no"
   "fovbinnumber", "| Number of bins between fovradmin and fovradmax.
   | Dim = (fovradmax-fovradmin)/fovbinnumber", "int", 1, "no"



Section: *'model'*
==================

The '*galcoeff*' and '*isocoeff*' options values can take the default value of -1 or they can be a a list of values separated by a comma,
for example:

.. code-block:: yaml

    model:
      galcoeff: 10, 15
      isocoeff: 0.6, 0.8

In this case, you should pay attention on how the sky maps are generated: the
following example show which iso/gal coefficients are assigned to which map.

.. code-block:: yaml

    selection:
      fovradmin: 0
      fovradmax: 60

    maps:
      energybins:
        - 100, 300
        - 300, 1000
      fovbinnumber: 2

    model:
      galcoeff: 10, 15
      isocoeff: 0.6, 0.8

| **Map #1** has: fovmax:0  fovmax:30 emin:100 emax:300   galcoeff:10.0 isocoeff:0.6
| **Map #2** has: fovmax:0  fovmax:30 emin:300 emax:1000  galcoeff:15.0 isocoeff:0.8
| **Map #3** has: fovmax:30 fovmax:60 emin:100 emax:300   galcoeff:10.0 isocoeff:0.6
| **Map #4** has: fovmax:30 fovmax:60 emin:300 emax:1000  galcoeff:15.0 isocoeff:0.8



.. csv-table::
   :header: "Option", "Description", "Type", "Default", "Required"
   :widths: 20, 20, 20, 20, 100

   "modelfile", "| A file name that contains point
   | sources, diffuse and isotropic components", "string", "null", "yes"
   "galmode",  "int", 1, "no",
   "isomode", "int", 1, "no",
   "galcoeff", "set into .maplist if >= 0", "float or str", -1, "no"
   "isocoeff", "set into .maplist if >= 0", "float or str", -1, "no"
   "emin_sources", "energy min of the modelfile", "int", 100, "no"
   "emax_sources", "energy max of the modelfile", "int", 10000, "no"

galmode and isomode
-------------------

*'galmode'* and *'isomode'* are integer values describing how the corresponding
coefficients *'galcoeff'* or *'isocoeff'* found in all the lines of the maplist will be used:

| 0: all the coefficients are fixed.
| 1: all the coefficients are fixed if positive, variable if negative (the absolute value is the initial value). This is the default behaviour.
| 2: all the coefficients are variable, regardless of their sign.
| 3: all the coefficients are proportionally variable, that is the relative weight of their absolute value is kept.


Section: *'mle'*
================

The maximum likelihood estimation analysis is configured by the following options:

.. csv-table::
   :header: "Option", "Description", "Type", "Default", "Required"
   :widths: 20, 20, 20, 20, 100

   "ranal", "Radius of analysis", float, 10, No
   "ulcl", "Upper limit confidence level, expressed as sqrt(TS)", float, 2, No
   "loccl", "Source location contour confidence level (default 95 (%)confidence level) Possible values: [ *99*, *95*, *98*, *50*]", int, 95, No

Exp-ratio evaluation options
----------------------------

.. csv-table::
   :header: "Option", "Type", "Default", "Required", "Description"
   :widths: 20, 20, 20, 20, 100

   expratioevaluation, bool, yes, none, ""
   expratio_minthr, float, 0, none, ""
   expratio_maxthr, float, 15, none, ""
   expratio_size, float, 10, none, ""


Section: *'plot'*
=================

This section defines the plotting configuration.

.. csv-table::
    :header: "Option", "Description", "Type", "Required", "Default"
    :widths: 20, 20, 20, 20, 100

    twocolumns, "The plot is adjusted to the size of a two column journal publication", boolean, no, False
