********************************************************
Output files of the MLE
********************************************************

This page provides detailed description of the output files of the science tool `AG_multi <AG_multi.html>`_.

The details of the output of the science tool AG_multi that performs the likelihood procedure is still accessible from agilepy. This section describes the "low level" results of the AG_multi procedure. The results are available in the $HOME/agilepy_analysis/<sourcename>_<username>_<date>-<time>/mle directory, where <sourcename> and <username> are defined in the yaml configuration file, <date> and <time> are defined by the system when the analysis starts.

At the end of the fitting process AG_multi generates two main files, describing the most relevant results for all the sources, and a set of source-specific files containing more detailed data about that source. 

One of the two main files is in HTML format, and it includes both the input and output data grouped in tables. Having a look at this file the user should quickly understand the outcome of the fitting process and its main results. The next section describes the HTML output in more detail.

The second of the two main files contains the same data printed in text format. This file is divided in two sections. The first contains one line for each diffuse component and the second one line for each source. The first line of each section begins with an exclamation mark (a comment line for many applications) labeling the values printed beneath. In each line the values are separated by a space. This is an example of the text output of the analysis of the 2AGLJ2254+1609 (3C454.3) with the test dataset provided. For this analysis, only one set of maps and one source is used. The iotropic emission components coefficients are kep free and symmetric errors are provided. The flux and position of the source are allowed to vary, while the spectral index is fixed. The name, significance of the source detection, position, source counts with error, source flux with error, and spectral index with error are provided. 

::

    ! DiffName, Flux, Err, +Err, -Err
    Galactic 0.7 0 0 0
    Isotropic 8.79898 0.969867 0.984804 -0.955381
    ! SrcName, sqrt(TS), L_peak, B_peak, Counts, Err, Flux, Err, Index, Err, Par2, Par2Err, Par3, Par3Err, TypeFun
    2AGLJ2254+1609 35.5482 86.0638 -38.1753 719.369 35.2059 2.63371e-05 1.28894e-06 2.20942 0 0 0 0 0 0

index, par2, par3 and related errors depend by the spectral mode used.

The counts and fluxes are provided, as well as their errors if the flux is allowed to vary.  Finally, the spectral index and its error, if applicable, are provided.

.. note:: If a source is outside the Galactic plane, fix the diffuse emission coefficient parameter (gal) to 0.7 with ag.setOptions(galcoeff=[0.7]) 

'*.source*' file
^^^^^^^^^^^^^^^^
The .source file is an internal technical file produced by the maximum likelihood estimator mle() procedure for each source. It contains all the analysis results for each source that is part of the ensemble of models. Agilepy extract from this .source file the most important parameters useful for the final user.

When possible, two additional files describing the source contour (possibile only if position is kept free). 

The text file contains some comment-like lines (first character is an exclamation mark) labeling the values printed beneath. This is an example of text output, consistent with the example given above:

::

    ! Label Fix index ULConfidenceLevel SrcLocConfLevel start_l start_b start_flux [ lmin,  lmax ] [ bmin, bmax ] typefun par2 par3 galmode2 galmode2fit isomode2 isomode2fit edpcor fluxcor integratortype expratioEval expratio_minthr expratio_maxthr expratio_size [ index_min , index_max ] [ par2_min , par2_max ] [ par3_min , par3_max ] contourpoints minimizertype minimizeralg minimizerdefstrategy minimizerdeftol
    ! sqrt(TS)
    ! L_peak B_peak Dist_from_start_position
    ! L B Dist_from_start_position r a b phi
    ! Counts Err +Err -Err UL
    ! Flux(ph/cm2s) [0 , 1e+07] Err +Err -Err UL(ph/cm2s) ULbayes(ph/cm2s) Exp(cm2s) ExpSpectraCorFactor null null null Erglog(erg/cm2s) Erglog_Err Erglog_UL(erg/cm2s) Sensitivity FluxPerChannel(ph/cm2s)
    ! Index [0.5 , 5] Index_Err Par2 [20 , 10000] Par2_Err Par3 [0 , 100] Par3_Err
    ! cts fitstatus0 fcn0 edm0 nvpar0 nparx0 iter0 fitstatus1 fcn1 edm1 nvpar1 nparx1 iter1 Likelihood1
    ! Gal coeffs [0 , 100] and errs
    ! Gal zero coeffs and errs
    ! Iso coeffs [0 , 100] and errs
    ! Iso zero coeffs and errs
    ! Start_date(UTC) End_date(UTC) Start_date(TT) End_date(TT) Start_date(MJD) End_date(MJD)
    ! Emin..emax(MeV) fovmin..fovmax(deg) albedo(deg) binsize(deg) expstep phasecode ExpRatio
    ! Fit status of steps ext1, step1, ext2, step2, contour, index, ul [-1 step skipped, 0 ok, 1 errors]
    ! Number of counts for each step (to evaluate hypothesis)
    ! skytypeL.filter_irf skytypeH.filter_irf
    2AGLJ2254+1609 1 2.20942 2 5.99147 86.1236 -38.1824 2.64387e-05 [ -1 , -1 ]  [ -1 , -1 ]  0 0 0 0 0 0 0 0.75 0 1 1 0 15 10 [ 0.5 , 5 ] [ 20 , 10000 ] [ 0 , 100 ] 40 Minuit Migrad 2 0.01
    47.8468
    86.1236 -38.1824 0
    -1 -1 -1 -1 -1 -1 -1 
    718.633 31.0247 31.4119 -30.6392 782.234
    2.64387e-05 1.14141e-06 1.15565e-06 -1.12722e-06 2.87787e-05 2.01487e-05 2.71811e+07 1 0 0 0 4.27293e-09 1.8447e-10 4.6511e-09 0.0 2.64387e-05
    2.20942 0 0 0 0 0
    909 -1 2456.44 0.5 0 8 3 0 1311.78 7.28513e-16 1 8 3 1828.16
    0.7 0
    0.7 0
    8.83231 0
    8.83231 0
    2010-11-13T00:01:06 2010-11-21T00:01:06 216691200.0000000 217382400.0000000 55513.0000000 55521.0000000
    100..10000 0..60 80 0.25 0 6 0
    -1 -1 -1 0 -1 -1 0 
    -1 2124 -1 2124 -1 -1 2124 
    SKY002.SFMG_H0025 SKY002.SFMG_H0025

The counts and fluxes are provided, as well as their symmetric, positive, and negative errors if the flux is allowed to vary. For convenience, the exposure of the source, used to calculate the source counts from the flux, is also provided. Finally, the spectral index and its error, if applicable, are provided.

'*.source*' Attributes
^^^^^^^^^^^^^^^^^^^^^^
.. csv-table::
   :header: "Parameter name", "UM", "Description", "default", "range"
   :widths: 20, 20, 100, 10, 10

   Label, , , ,
   Fix, , Value of the *fixflag*, ,
   index, , Initial value of the *index* parameter , ,
   ULConfidenceLevel, , Upper limit confidence level espressed as sqrt(TS) , 2 , 
   SrcLocConfLevel, , Source location contour confidence level % , 95 99 95 68 50 , 95
   start_l, , , ,
   start_b, , , ,
   start_flux , (ph/cm2s) , , ,
   [ lmin lmax ], , , ,
   [ bmin bmax ], , , ,
   typefun, , , ,
   par2, , , ,
   par3, , , ,
   galmode2, , , ,
   galmode2fit, , , ,
   isomode2, , , ,
   isomode2fit, , , ,
   edpcor, , , ,
   fluxcor, , , ,
   integratortype, , , ,
   expratioEval, , , ,
   expratio_minthr, , , ,
   expratio_maxthr, , , ,
   expratio_size, , , ,
   [ index_min index_max ], , , ,
   [ par2_min par2_max ], , , ,
   [ par3_min  par3_max ], , , ,
   contourpoints, , , ,
   minimizertype, , , ,
   minimizeralg, , , ,
   minimizerdefstrategy, , , ,
   minimizerdeftol, , , ,
   sqrt(TS), , , ,
   L_peak, , , ,
   B_peak, , , ,
   Dist_from_start_position, , , ,
   L, , , ,
   B, , , ,
   Dist_from_start_position, , , ,
   r, , , ,
   a, , , ,
   b, , , ,
   phi, , , ,
   Counts, , , ,
   Err, , , ,
   +Err, , , ,
   -Err, , , ,
   UL, , ,
   Flux,(ph/cm2s), , ,
   Err, , , ,
   +Err, , , ,
   -Err, , , ,
   UL, (ph/cm2s), , ,
   ULbayes, (ph/cm2s), , ,
   Exp, (cm2s), , ,
   ExpSpectraCorFactor, , , ,
   Erglog, (erg/cm2s), , ,
   Erglog_Err, , , ,
   Erglog_UL, (erg/cm2s) , , ,
   Sensitivity, , , ,
   FluxPerChannel, (ph/cm2s) , , ,
   Index, , , ,
   Index_Err, , , ,
   Par2, , , ,
   Par2_Err, , , ,
   Par3, , , ,
   Par3_Err, , , ,
   cts, , , ,
   fitstatus0, , , ,
   fcn0, , , ,
   edm0, , , ,
   nvpar0, , , ,
   nparx0, , , ,
   iter0, , , ,
   fitstatus1, , , ,
   fcn1, , , ,
   edm1, , , ,
   nvpar1, , , ,
   nparx1, , , ,
   iter1, , , ,
   Likelihood1, , , ,
   Gal coeffs, , , ,
   errs, , , ,
   Gal zero coeffs, , , ,
   errs, , , ,
   Iso coeffs, , , ,
   errs, , , ,
   Iso zero coeffs, , , ,
   errs, , , ,
   Start_date(UTC), , , ,
   End_date(UTC), , , ,
   Start_date(TT), , , ,
   End_date(TT), , , ,
   Start_date(MJD), , , ,
   End_date(MJD), , , ,
   Emin..emax , MeV , , ,
   fovmin..fovmax, deg , , ,
   albedo, deg , , ,
   binsize, deg , , ,
   expstep, , ,  ,
   phasecode, , , ,
   ExpRatio, , , ,
   Fit status of steps ext1,  , , ,
   Fit status of steps step1, , , ,
   Fit status of steps ext2, , , ,
   Fit status of steps step2, , , ,
   Fit status of steps contour, , , ,
   Fit status of steps index, , , ,
   Fit status of steps ul, , , ,
   Number of counts for ext1, , , ,
   Number of counts for step1, , , ,
   Number of counts for ext2, , , ,
   Number of counts for step2, , , ,
   Number of counts for contour, , , ,
   Number of counts for index, , , ,
   Number of counts for ul, , , ,
   skytypeL.filter_irf, , , ,
   skytypeH.filter_irf, , , ,

'*.source.con*' file and ellipse
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
outfile.source.con: source contour (if found).

If AG_multi was able to find a source contour, an ellipse is fit to the contour.
The source contour is a list of points which defines a polygon by connecting each point sequentially. The value of Radius found in the HTML output is the radius in degrees of a circle with the same area as the polygon.
AG_multi determines the ellipse which best fits the contour. This ellipse will have the same area as the polygon, and the distance between each contour point and the intersection between the ellipse and the line connecting that point to the centre will be minimized.
The ellipse is completely described by three parameters: the two axes and the rotation (in degrees) of the first axis around the centre, as expected by the ds9 application.
If the ellipse is a circle, its axes will both be equal to the Radius found in the HTML output.
The ellipse is described by two files that are readable by ds9: one is a .reg file which contais the centre, the axes and the rotation of the ellipse, while the other describes the same ellipse as a list of points in galactic coordinates, thus using the same syntax of a contour file, and has extension .ellipse.con.
This is an example of ellipse .reg file:

::
    galactic
    ellipse(263.579,-2.8398,0.0167177,0.0205552,22.3895)

'*.source.reg*' file
^^^^^^^^^^^^^^^^^^^^^^^^
outfile.source.reg: ellipse best fitting the source contour (if found).

'*.log*' file
^^^^^^^^^^^^^^^^^^^^^^^^
Log file with a line for each step of the fitting process.

HTML output 
^^^^^^^^^^^^^^^^^^^^^^^^

AG_multi provides an HTML output of the results.
The HTML output file is divided into two sections, input and output.
The input section contains three subsections: the command line options, the map list and the source list contents. The command line options are listed in two tables, one with the names of the IRFs (PSD, SAR and EDP) files, the other with the rest of the command line. The maplist subsection also contains two tables. The first lists the mapfile contents and the second contains the data from the map files themselves. This table contains one map per row, and each column contains one value only if it is the same for all the maps. The last table of the input section contains the source list contents.
The output section is also divided into three subsections. The first is a table showing the Galactic and isotropic coefficients and their errors. Also in this table some cells may be grouped together when the values are all the same. The second is a table showing the fit results for the sources and their errors. One of the listed values is the contour equivalent radius, explained in the next section. The last table shows the source flux per energy channel, and it is present only when different energy channels are considered. This table has one row for each source and one column for each energy channel.



