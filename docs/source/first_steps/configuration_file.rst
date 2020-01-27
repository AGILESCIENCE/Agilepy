******************
Configuration file
******************
This section described the configuration file used by Agilepy package. The configuration file has a structure that groups parameters into dictionaries separated by a section name. 

input
======================
This section defines the input data files. An input data file is an index file, i.e. a file that contains the list of evt files and log files. These files are mandatory and must be specified.

.. csv-table::
   :header: "Option", "Type", "Default", "Required", "Description"
   :widths: 20, 20, 20, 20, 100

   evtfile, str, none, Yes/No, "Path to index evt file name"
   logfile, str, none, Yes/No, "Path to index log file name"


output
=============
The output section collects options related to file generation. The outdir option sets the root directory of the analysis results where all output files are written. If outdir is None then the output directory is set to the directory in which the configuration file is located.


.. csv-table::
   :header: "Option", "Type", "Default", "Required", "Description"
   :widths: 20, 20, 20, 20, 100

   "outdir", "str", "none", "yes", "Path of the output directory"qqq
   "filenameprefix", "str", "None", "Yes", ""
   "logfilename", "str", "agilepy.log", "no", "Path to the log file. If None the log file is agilepy.log and is written to the directory in which the configuration file is located"
   "debuglvl", "int", 0, "no", "| 0 ⇒ WARNING: An indication that something unexpected happened, or indicative of some problem in the near future (e.g. ‘disk space low’). The software is still working as expected.
   | 1 ⇒ INFO: Confirmation that things are working as expected.
   | 2 ⇒ DEBUG: Detailed information, typically of interest only when diagnosing problems."


Selection
================================
The options of the maps section control the temporal, spatial and spectral binning of the data. The ROI center is defined by giving explicit Galactic sky coordinates (glon and glat).

.. csv-table::
   :header: "Option", "Type", "Default", "Required", "Description"
   :widths: 20, 20, 20, 20, 100

   "emin", "int", 100, "No", "Energy min in MeV"
   "emax", "int", 10000, "No", "Energy max in MeV"
   "glat", "float", "None", "No", "Center of the ROI. This is a mandatory parameter."
   "glon", "float", "None", "No", "Center of the ROI. This is a mandatory parameter."
   "tmin", "float", "None", "Yes", "Minimum time (in MJD or TT). Default is MJD"
   "tmax", "float", "None", "Yes", "Maximum time (in MJD or TT). Default is MJD"
   "timetype", "str", "None", "Yes", "MJD or TT. The date format of tmin and tmax"
   "timelist", "str", "None", "No", "a list of timeintervals tstart tstop in TT to generate summed maps. If specified, tmin and tmax are ignored."
   "projtype", "str", "WCS", "No", "Projection mode (WCS or HPX). Only WCS is available"
   "proj", "str", "ARC", "No", "Spatial projection for WCS mode. ARC or AIT."
   "filtercode", "int", 5, "No", "filtercode = 5 select G filtercode = 0 select G+L+S"
   "fovradmin", "int", 0, "No", "fovradmin < fovradmax"
   "fovradmax", "int", 60, "No", "fovradmin < fovradmax"
   "albedorad", "int", 80, "No", "albedo selection cut"
   "dq", "int", 0, "No", "| Data quality selection filter. A combination of fovradmax and albedorad.
   | dq=0 use specified or default albedorad and fovradmax. Possible values are:
   | dq = 1 -> albedorad=80, fovradmax=60
   | dq = 2 -> albedorad=80, fovradmax=50
   | dq = 3 -> albedorad=90, fovradmax=60
   | dq = 4 -> albedorad=90, fovradmax=50
   | dq = 5 -> albedorad=100, fovradmax=50
   | dq = 6 -> albedorad=90, fovradmax=40
   | dq = 7 -> albedorad=100, fovradmax=40
   | dq = 8 -> albedorad=90, fovradmax=30
   | dq = 9 -> albedorad=100, fovradmax=30"
   "phasecode", "int", "None", "No", "Photon list selection parameter based on the orbital phase. If None, the automated selection is done following the rules specified in Sect. “phasecode”"

Phasecode
-------------------------

| #2 -> per lo spinning, esclude la SAA con metodo conteggi AC
| #6 -> per lo spinning, esclude la SAA in base ad intensità campo magnetico (TPZ)
| #18 -> per il pointing, esclude la SAA e il recovery
| # Normalmente usate il phasecode = 6 nei dati in spinning. Questo phasecode esclude i fotoni presenti nella SAA ridefinita con i conteggi dell'AC. Se invece vuoi usare la vecchia definizione della SAA (in base all'intensità del campo magnetico così come definito da TPZ) devi usare il phasecode = 6.


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

|
|

.. csv-table::
   :header: "Option", "Default", "Required", "Description"
   :widths: 20, 20, 20, 150

   "lonpole", 180, "No", " --------------completare--------- "
   "lpointing", "None", "No", " --------------completare---------"
   "bpointing", "None", "No", " --------------completare---------"
   "maplistgen", "None", "No", "filename of a file for expmapgen with  mapspec.fovradmin >> mapspec.fovradmax >> mapspec.emin >> mapspec.emax >> mapspec.index"


Maps
================================

.. csv-table::
   :header: "Option", "Type", "Default", "Required", "Description"
   :widths: 20, 20, 20, 20, 100

   "mapsize", "float", 40, "No", "Width of the ROI in degrees."
   "useEDPmatrixforEXP", "boolean", "Yes", "No", "expmap: use the EDP matrix to generate expmap yes|no"
   "expstep", "int", "None", "No", "| expmap: step size of expmap calculation, if None it depends by
   | binsize ⇒ round(1 / binsize, 2) (e.g. 0.3->3, 0.25->4, 0.1->10)"

   "spectralindex", "float", 2.1, "No", "expmap: spectral index"
   "timestep", "float", 160, "No", "expmap: LOG file step size (LOG file are at 0.1s)"
   "skytype", "", "4", "No", "| gasmap:
   | 0) SKY000-1 + SKY000-5,
   | 1) gc_allsky maps + SKY000-5,
   | 2) SKY000-5
   | 3) SKY001 (old galcenter, binsize 0.1, full sky),
   | 4) SKY002 (new galcenter, binsize 0.1, full sky) "

   "binsize", "float", 0.1, "No", "Spatial bin size in degrees."
   "energybin", "List<List<int>>", "[100, 10000]", "No", "------- completare -----------"
   "fovbinnumber", "int", 1, "No", "| Number of bins between fovradmin and fovradmax.
   | Dim = (fovradmax-fovradmin)/fovbinnumber"

Hidden parameters

.. csv-table::
   :header: "Option", "Type", "Default", "Required", "Description"
   :widths: 20, 20, 20, 20, 100

   "offaxisangle", "None", 30, "No", "off axix pointing (default 30) - set into .maplist"

MAPLIST file
----------------------------
Each line contains a set of maps:

.. code-block::

    <countsMap> <exposureMap> <gasMap> <offaxisangle> <galcoeff> <isocoeff>


where:

 * offaxisangle is in degrees;
 * galcoeff and isocoeff are the coefficients for the galactic and isotropic diffuse components. If positive they will be considered fixed (but see galmode and isomode section).

The file names are separated by a space, so their name should not contain one.

Model
================================

.. csv-table::
   :header: "Option", "Type", "Default", "Required", "Description"
   :widths: 20, 20, 20, 20, 100

   "modelfile", "string", "None", "Yes", "A file name that contains point sources, diffuse and isotropic components"
   "galmode", "int", 1, "No",
   "isomode", "int", 1, "No",
   "galcoeff", "float", -1, "No", "set into .maplist if >= 0"
   "isocoeff", "float", -1, "No", "set into .maplist if >= 0"
   "emin_sources", "int", 100, "No", "energy min of the modelfile"
   "emax_sources", "int", 10000, "No", "energy max of the modelfile"

Hidden parameters

.. csv-table::
   :header: "Option", "Type", "Default", "Required", "Description"
   :widths: 20, 20, 20, 20, 100

   galmode2, None, 0, No, "| 0) none
   | 1) set gal0 for L0 and gal1 for L1
   | 2) set gal0 for L0 and L1
   | 3) set gal1 for L0 and L1
   | 4) set gal1 - gal1err for L0 and L1
   | 5) set gal1 + gal1err for L0 and L1"

   galmode2fit, none, 0, No, "| 0) do not fit
   | 1) pol0 fit
   | 2) powerlaw fit"

   isomode2, none, 0, No, "| 0) none
   | 1) set iso0 for L0 and gal1 for L1
   | 2) set iso0 for L0 and L1
   | 3) set iso1 for L0 and L1
   | 4) set iso1 - iso1err for L0 and L1
   | 5) set iso1 + iso1err for L0 and L1 "

   isomode2fit, none, 0, No, "| 0) do not fit
   | 1) pol0 fit
   | 2) powerlaw fit"

galmode and isomode
----------------------------

| galmode and isomode are integer values describing how the corresponding coefficients galcoeff or isocoeff found in all the lines of the maplist are to be used:
| 0) all the coefficients are fixed.
| 1) all the coefficients are fixed if positive, variable if negative (the absolute value is the initial value). This is the default behaviour.
| 2) all the coefficients are variable, regardless of their sign.
| 3) all the coefficients are proportionally variable, that is the relative weight of their absolute value is kept.


mle
================================

.. csv-table::
   :header: "Option", "Type", "Default", "Required", "Description"
   :widths: 20, 20, 20, 20, 100

   ranal, float, 10, No, radius of analysis
   ulcl, float, 2, No, "upper limit confidence level, expressed as sqrt(TS)"
   loccl, int, 95, No, "source location contour confidence level (default 95 (%)confidence level) Values: 99, 95, 68, 50 "

|
| Parameters for exp ratio evaluation
|


.. csv-table::
   :header: "Option", "Type", "Default", "Required", "Description"
   :widths: 20, 20, 20, 20, 100

   expratioevaluation, bool, yes, none, ""
   expratio_minthr, float, 0, none, ""
   expratio_maxthr, float, 15, none, ""
   expratio_size, float, 10, none, ""

|
| Hidden parameters for optimizer

.. csv-table::
   :header: "Option", "Type", "Default", "Required", "Description"
   :widths: 20, 20, 20, 20, 100

   minimizertype, none, Minuit, none, "Use Minuit if position is free"
   minimizeralg, none, Migrad, none, ""
   minimizerdefstrategy, none, 2, none, "Default 2 for Minuit"
   mindefaulttolerance, none, 0.01, none, ""
   integratortype, none, 1, none, "| 1 gauss
   | 2 gaussht
   | 3 gausslefevre
   | 4 gausslefevreht"

   contourpoints, none, 40, none, "Number of points to determine the contour (0-400)"


| **minimizertype** = Minuit (library libMinuit). Old version of Minuit, based on the TMinuit class. The list of possible algorithms (**minimizeralg**) are:
|  1) Migrad (default one)
|  2) Simplex
|  3) Minimize (it is a combination of Migrad and Simplex)
|  4) MigradImproved
|  5) Scan
|  6) Seek


| **minimizertype** = Minuit2 (library libMinuit2). New C++ version of Minuit. The list of the possible algorithms (**minimizeralg**) :
|  1) Migrad (default)
|  2) Simplex
|  3) Minimize
|  4) Scan

**minimizertype** = Fumili . This is the same algorithm of TFumili, but implemented in the Minuit2 library.

**minimizertype** = GSLMultiMin (library libMathMore). Minimizer based on the Multidimensional Minimization routines of the Gnu Scientific Library (GSL). The list of available algorithms (minimizeralg) is
| 1) BFGS2 (default) : second version of the vector Broyden-Fletcher-Goldfarb-Shanno (BFGS) algorithm;
| 2) BFGS : old version of the vector Broyden-Fletcher-Goldfarb-Shanno (BFGS) algorithm;
| 3) ConjugateFR : Fletcher-Reeves conjugate gradient algorithm;
| 4) ConjugatePR : Polak-Ribiere conjugate gradient algorithm;
| 5) SteepestDescent: steepest descent algorithm;

| #*** * GSLMultiFit (library libMathMore). Minimizer based on the Non-Linear Least-Square routines of GSL. This minimizer can be used only for least-square fits.
| #*** * GSLSimAn (library libMathMore). Minimizer based on simulated annealing.
| #*** * Genetic (library libGenetic). Genetic minimizer based on an algorithm implemented in the TMVA package.

Each minimizer can be configured using the ROOT::Math::MinimizerOptions class. The list of possible option that can be set are:

| **minimizertype:**
| Minimizer type (MinimizerOptions::SetMinimizerType(const char * )) .

| * Print Level (MinimizerOptions::SetPrintLevel(int )) to set the verbose printing level (default is 0).


| **mindefaulttolerance:**
| * Tolerance (MinimizerOptions::SetTolerance(double )) tolerance used to control the iterations.
| * Precision (MinimizerOptions::SetTolerance(double )). Precision value in the evaluation of the minimization function. Default is numerical double precision.

* Maximum number of function calls (MinimizerOptions::SetMaxFunctionCalls(int )).
* Maximum number of iterations (MinimizerOptions::SetMaxIterations(int )). Note that this is not used by Minuit. FCN Upper value for Error Definition (MinimizerOptions::SetMaxIterations(int )). Value in the minimization function used to compute the parameter errors. The default is to get the uncertainties at the 68% CL is a value of 1 for a chi-squared function minimization and 0.5 for a log-likelihood function.

| **minimizerdefstrategy:**
| * Strategy (MinimizerOptions::SetStrategy(int )), minimization strategy used. For each minimization strategy Minuit uses different configuration parameters (e.g. different requirements in computing derivatives, computing full Hessian (strategy = 2) or an approximate version. The default is a value of 1. In this case the full Hessian matrix is computed only after the minimization.


.. csv-table::
   :header: "Option", "Type", "Default", "Required", "Description"
   :widths: 20, 20, 20, 20, 100

   edpcorrection, none, 0.75, none, "default 0.75, otherwise any value between 0 and 1. EDP correction is enabled only for E>1000 MeV and if fluxcorrection=1, and only for point sources. flux = flux * edpcorrection"
   fluxcorrection, none, 1, none, "| 0) no correction
   | 1)  Flux calculation correction for spectral shape in output
   | 2) correction in input and output"


