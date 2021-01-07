.. _configuration-file:

******************
Configuration file
******************

A `yaml <https://docs.ansible.com/ansible/latest/reference_appendices/YAMLSyntax.html>`_ configuration file is required in order to run Agilepy.

It is composed by several sections and each section holds several configuration options, some of which are optional (having a default value), some others are required.

It supports environment variables (they can be used to define file system paths).

It can be created easily, calling the following static method and passing the minimal set of (required) configuration parameters.

::

    AGAnalysis.getConfiguration(
          "./agconfig.yaml", # the destination path of the configuration file
          "username", # the name of the flare advocate
          "OJ287", # the name of the source
          58930, # tmin
          58936, # tmax
          "MJD", # time type
          206.8121188769472, # glon
          35.8208923457401, # glat
          "$HOME/agilepy_analysis", # the destination path of the output directory
          1, # the verbosity level
          evtfile="$AGILE/agilepy-test-data/evt_index/agile_proc3_fm3.119_asdc2_EVT.index", # optional parameter
          logfile="$AGILE/agilepy-test-data/log_index/agile_proc3_data_asdc2_LOG.log.index" # optional parameter
    )

The method above will create the following configuration file:

.. code-block:: yaml

  input:
    evtfile: $AGILE/agilepy-test-data/evt_index/agile_proc3_fm3.119_asdc2_EVT.index
    logfile: $AGILE/agilepy-test-data/log_index/agile_proc3_data_asdc2_LOG.log.index

  output:
    outdir: "$HOME/agilepy_analysis"
    filenameprefix: analysis_product
    logfilenameprefix: analysis_log
    sourcename: OJ287
    username: user-xxx
    verboselvl: 1

  selection:
    tmin: 58930
    tmax: 58936
    timetype: MJD
    glon: 206.8121188769472
    glat: 35.8208923457401
    proj: ARC
    timelist: None
    filtercode: 5
    fovradmin: 0
    fovradmax: 60
    albedorad: 80
    dq: 0
    phasecode: null
    lonpole: 180
    lpointing: null
    bpointing: null
    maplistgen: "None"

  maps:
    mapsize: 40
    useEDPmatrixforEXP: no
    expstep: null
    spectralindex: 2.1
    timestep: 160
    projtype: WCS
    proj: ARC
    # skytype: 4
    binsize: 0.25
    energybins:
      - 100, 10000
    fovbinnumber: 1
    offaxisangle: 30

  model:
    modelfile: null
    galmode: 1
    isomode: 1
    galcoeff: null
    isocoeff: null
    emin_sources: 100
    emax_sources: 10000
    
    galmode2: 0
    galmode2fit: 0
    isomode2: 0
    isomode2fit: 0

  mle:
    ranal: 10
    ulcl: 2
    loccl: 
    
    expratioevaluation: yes
    expratio_minthr: 0
    expratio_maxthr: 15
    expratio_size: 10

    minimizertype: Minuit
    minimizeralg: Migrad
    minimizerdefstrategy: 2
    mindefaulttolerance: 0.01
    integratortype: 1
    contourpoints: 40

    edpcorrection: 0.75
    fluxcorrection: 1
  
  ap:
    radius: 3
    timeslot: 3600
  
  plotting:
    twocolumns: False

The next paragraphs describe the configuration options.

Section: *'input'*
==================
This section defines the input data files. The input data files are indexes: each
row holds the file system position of an actual event data/log file, together with
the time interval it refers to.

.. csv-table::
   :header: "Option", "Description", "Type", "Required", "Default"
   :widths: 20, 100, 20, 20, 20

   evtfile, "Path to index evt file name", str, no, /AGILE_PROC3/FM3.119_ASDC2/INDEX/EVT.index
   logfile, "Path to index log file name", str, no, /AGILE_PROC3/DATA_ASDC2/INDEX/LOG.log.index


Section: *'output'*
===================
The output section collects options related to the output files generation and logging.

The *'outdir'* option sets the root directory of the analysis results where all output files are written.

Agilepy use two loggers, one logs messages on the console, the other writes messages on disk.
The *'verboselvl'* option sets the verbosity of the Agilepy console logger. The Agilepy file logger verbosity is set to 2 by default.
There are 4 kind of messages based on their importance factor:

  - CRITICAL: a message describing a critical problem, something unexpected, preceding a program crash or an Exception raise.
  - WARNING: an indication that something unexpected happened, or indicative of some problem in the near future (e.g. ‘disk space low’). The software is still working as expected.
  - INFO: confirmation that things are working as expected.
  - DEBUG: detailed information, typically of interest only when diagnosing problems.

.. csv-table::
   :header: "Option", "Description", "Type", "Required", "Default"
   :widths: 20, 100, 20, 20, 20

   "outdir", "Path of the output directory", "str", "yes", "null"
   "filenameprefix", "The filename prefix of each output file", "str", "yes", "null"
   "logfilenameprefix", "The filename prefix of the log file", "str", "yes", "null"
   "sourcename", "The name of the source under analysis", "str", "yes", "null"
   "userName", "The name of the user performing the analysis", "str", "yes", "null" 
   "verboselvl", "| 0 ⇒ *CRITICAL* and *WARNING* messages are logged on the console.
   | 1 ⇒ *CRITICAL*, *WARNING* and *INFO* messages are logged on the console.
   | 2 ⇒ *CRITICAL*, *WARNING*, *INFO* and *DEBUG* messages are logged on the console",  "int", "no", 1


Section: *'selection'*
======================

The temporal, spatial and spectral binning of the data can be customized using the configuration options of this section.

The center of the *ROI* (region of interest) is defined by explicit Galactic sky coordinates (glon and glat).

.. csv-table::
   :header: "Option", "Description", "Type", "Default", "Required"
   :widths: 20, 100, 20, 20, 20

   "emin", "Energy min in MeV", "int", 100, "no"
   "emax", "Energy max in MeV", "int", 10000, "no"
   "glat", "Center of the ROI ('*latitude*' or *'b'*)", "float", "null", "yes"
   "glon", "Center of the ROI ('*longitude*' or *'l'*)", "float", "null", "yes"
   "tmin", "Minimum time (in MJD or TT)", "float", "null", "yes"
   "tmax", "Maximum time (in MJD or TT)", "float", "null", "yes"
   "timetype", "| The date format of tmin and tmax.
   | Possibile values: [*'MJD'*, *'TT'*]", "str", "null", "yes"
   "timelist", "| it's a path to a file containing a list of time intervals in TT
   | format to generate maps
   | integrated within a time window.
   | If specified, *'tmin'* and *'tmax'* are ignored.", "str", "null", "no"
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
             @phasecode = 18 #POINTING
          end
       end
    end



Section: *'maps'*
=================

These options control the behaviour of the sky maps generation tools.
The *'energybin'* and *'fovbinnumber'* options set the number of maps that are generated:

::

    number of maps = number of energy bins * fovbinnumber


The *'energybin'* option is a list of strings with the following format:

.. code-block:: yaml

    energybins:
      - 100, 1000
      - 1000, 3000

The *'fovbinnumber'* option sets the number of bins between *'fovradmin'* and *'fovradmax'* as:

::

    number of fov bins = (fovradmax-fovradmin)/fovbinnumber

.. note:: One map is generated for each possible combination between the *'energybin'* (emin, emax) and the *'fovbinnumber'* (fovmin, fovmax).
   The order of map generation is described by the following pseudocode:

   | For each fovmin..fovmax:
   |    For each emin..emax:
   |        generateMap(fovmin, fovmax, emin, emax)


.. csv-table::
   :header: "Option", "Description", "Type", "Default", "Required"
   :widths: 20, 100, 20, 20, 20

   "mapsize", "Width of the ROI in degrees","float", 40, "no"
   "useEDPmatrixforEXP", "Use the EDP matrix to generate the exposure map.", "boolean", "False", "no"
   "expstep", "| Step size of the exposure map, if 'None' it depends by
   | round(1 / binsize, 2) (e.g. 0.3->3, 0.25->4, 0.1->10)", "int", "None", "no"
   "spectralindex", "Spectral index of the exposure map", "float", 2.1, "no"
   "timestep", "LOG file step size of exposure map (LOG file are at 0.1s)", "float", 160, "no"
   "projtype", "Projection mode. Possible values: ['*WCS*']", "str", "WCS", "no"
   "proj", "| Spatial projection for WCS mode.
   | Possible values: ['*ARC*', '*AIT*']", "str", "ARC", "no"
   "skytype", "| gasmap:
   | 0) SKY000-1 + SKY000-5,
   | 1) gc_allsky maps + SKY000-5,
   | 2) SKY000-5
   | 3) SKY001 (old galcenter, binsize 0.1, full sky),
   | 4) SKY002 (new galcenter, binsize 0.1, full sky) ", "int", "4", "no"
   "binsize", "Spatial bin size in degrees", "float", 0.25, "no"
   "energybin", "------- completare -----------", "List<String>", "[100, 10000]", "no"
   "fovbinnumber", "| Number of bins between fovradmin and fovradmax.
   | Dim = (fovradmax-fovradmin)/fovbinnumber", "int", 1, "no"



Section: *'model'*
==================

The '*galcoeff*' and '*isocoeff*' options values can take the default value of null or they can be a a list of values separated by a comma.
If they are set to null it means they are free to change.

.. code-block:: yaml

    model:
      galcoeff: 0.8, 0.6, 0.5, 0.4
      isocoeff: 8, 10, 12, 14

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
      galcoeff: 0.8, 0.6, 0.5, 0.4
      isocoeff: 8, 10, 12, 14

| **FOV bins:**
| (0, 30), (30, 60)


| **Map #1** has: fovmax:0  fovmax:30 emin:100 emax:300   galcoeff:0.8 isocoeff:8
| **Map #2** has: fovmax:0  fovmax:30 emin:300 emax:1000  galcoeff:0.6 isocoeff:10
| **Map #3** has: fovmax:30 fovmax:60 emin:100 emax:300   galcoeff:0.5 isocoeff:12
| **Map #4** has: fovmax:30 fovmax:60 emin:300 emax:1000  galcoeff:0.4 isocoeff:14



.. csv-table::
   :header: "Option", "Description", "Type", "Default", "Required"
   :widths: 20, 100, 20, 20, 20

   "modelfile", "| A file name that contains point
   | sources, diffuse and isotropic components", "string", "null", "yes"
   "galmode",  "int", 1, "no",
   "isomode", "int", 1, "no",
   "galcoeff", "set into .maplist if >= 0", "null, float or str", null, "no"
   "isocoeff", "set into .maplist if >= 0", "null, float or str", null, "no"
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
   :widths: 20, 100, 20, 20, 20

   "ranal", "Radius of analysis", float, 10, No
   "ulcl", "Upper limit confidence level, expressed as sqrt(TS)", float, 2, No
   "loccl", "Source location contour confidence level (default 95 (%)confidence level) Possible values: [ *99*, *95*, *98*, *50*]", int, 95, No

Exp-ratio evaluation options
----------------------------

.. csv-table::
   :header: "Option", "Type", "Default", "Required", "Description"
   :widths: 20, 100, 20, 20, 20

   expratioevaluation, bool, yes, none, ""
   expratio_minthr, float, 0, none, ""
   expratio_maxthr, float, 15, none, ""
   expratio_size, float, 10, none, ""


Section: *'ap'*
===============

This section describes the configuration parameters for the Aperture Photometry analysis.

.. csv-table::
    :header: "Option", "Description", "Type", "Required", "Default"
    :widths: 20, 100, 20, 20, 20

    radius, "The radius of analysis", float, no, 3
    timeslot, "The size of the temporal bin", int, no, 3600


Section: *'plot'*
=================

This section defines the plotting configuration.

.. csv-table::
    :header: "Option", "Description", "Type", "Required", "Default"
    :widths: 20, 100, 20, 20, 20

    twocolumns, "The plot is adjusted to the size of a two column journal publication", boolean, False, no
