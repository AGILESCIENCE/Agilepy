***********************
Advanced  configuration
***********************

Selection
=========

.. csv-table::
  :header: "Option", "Description", "Default", "Required"
  :widths: 20, 20, 20, 150

  "lonpole", " --------------completare--------- ", 180, "no"
  "lpointing", " --------------completare--------- ", "null", "no"
  "bpointing", " --------------completare--------- ", "null", "no"
  "maplistgen", "filename of a file for expmapgen with  mapspec.fovradmin >> mapspec.fovradmax >> mapspec.emin >> mapspec.emax >> mapspec.index", "null", "no"


Maps
====

 .. csv-table::
    :header: "Option", "Type", "Default", "Required", "Description"
    :widths: 20, 20, 20, 20, 100

    "offaxisangle", "null", 30, "no", "off axix pointing (default 30) - set into .maplist"



Model
=====

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



mle
===

Advanced options for optimizer
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

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


Advanced options for internal corrections
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^


.. csv-table::
   :header: "Option", "Type", "Default", "Required", "Description"
   :widths: 20, 20, 20, 20, 100

   edpcorrection, none, 0.75, none, "default 0.75, otherwise any value between 0 and 1. EDP correction is enabled only for E>1000 MeV and if fluxcorrection=1, and only for point sources. flux = flux * edpcorrection"
   fluxcorrection, none, 1, none, "| 0) no correction
   | 1)  Flux calculation correction for spectral shape in output
   | 2) correction in input and output"
