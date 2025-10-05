Agilepy
===============

Agilepy is an open-source Python package developed at `INAF/OAS Bologna <https://www.oas.inaf.it>`_  to analyse AGILE/GRID data built on top of the command-line version of the AGILE/GRID Science Tools.   

The main purpose of the package is to provide an easy to use high-level Python interface to analyse AGILE/GRID data by simplifying the configuration of the tasks and ensuring straightforward access to the data.
The current features are the generation and display of sky maps and light curves, the access to gamma-ray sources catalogues, the analysis to perform spectral model and position fitting including the background evaluation, the aperture photometry analysis, the bayesian blocks analysis and the wavelet analysis.
In addition, Agilepy provides a visibiliy interface to analyse the time evolution of the AGILE off-axis viewing angle for a chosen sky region, comparing them with Fermi/LAT off-axis evolution.
The analysis of the AGILE Scientific Ratemeters is also possible.

Agilepy is similar to `Fermipy <https://fermipy.readthedocs.io/>`_ and `gammapy <https://docs.gammapy.org/>`_ tools, providing a common way to analyse gamma-ray data.

Agilepy provides the last version of the available Science Tools (BUILD26), the H0025 instrument response functions (IRFs), and the latest version of the diffuse Galactic emission model.

Agilepy (and its dependencies) can be easily installed using `Docker <https://docs.docker.com/get-docker/>`_.

.. note:: **AGILE DATASET DOWNLOAD**: 
          Now it possible to download all the public AGILE dataset stored on SSDC datacenter through a REST Api. 
          Agilepy automatically handles the data and no actions are required from the user.
          For more information visit `this page <../manual/agile_grid_data.html>`_.
          
AGILE
^^^^^^

AGILE (Astrorivelatore Gamma ad Immagini LEggero) is an astrophysics mission  of the Italian Space Agency (ASI) operating since 2007 April
devoted to gamma-ray and X-ray astrophysics. It carries two  instruments observing at hard X-rays between 18 and 60 keV (Super-AGILE) and in the gamma-ray band between 30 MeV and 50 GeV (Silicon Tracker). The payload is completed by a calorimeter (MCAL) sensitive in the 0.4–100 MeV range  and an anticoincidence  (AC) system. The combination of the Silicon Tracker, MCAL, and AC forms the Gamma-Ray Imaging Detector (GRID).

A set of different on-board triggers enables the discrimination of background events (mainly cosmic rays in the AGILE Low Earth Orbit) from gamma-ray events. AGILE raw data are down-linked every about 100 min to the ASI Malindi ground station in Kenya, and transmitted first to the Telespazio Mission Control Center at Fucino, and then to the AGILE Data Center (ADC), which is part of the ASI Space Science Data Center (SSDC, previously known as ASDC) and then to the INAF/OAS Bologna for the real-time analysis of data.

Main AGILE websites:

- SSDC: https://agile.ssdc.asi.it
- IAPS/Rome: http://agile.rm.iasf.cnr.it/

AGILE Apps:

- iOs iPhone: https://apps.apple.com/it/app/agilescience/id587328264
- iOs iPad: https://apps.apple.com/it/app/agilescience-for-ipad/id690462286
- Android: https://play.google.com/store/apps/details?id=com.agile.science&hl=en&gl=US
- Support wed site: http://www.agilescienceapp.it/wp/agilescienceen/

AGILE Science Tools
^^^^^^^^^^^^^^^^^^^^

The `AGILE/GRID Science Tools <sciencetools\tools.html>`_ developed by the AGILE Team are used to analyse gamma-ray data starting from spacecraft files (called LOG), and the acquired events (EVT  files or event list). They provide a way to generate gamma-ray counts, exposure and diffuse emission maps that are used as input for the binned maximum likelihood estimator (MLE).  The analysis depends on the isotropic and Galactic diffuse emission, the gamma-ray photon statistics, and on the instrument response functions (IRFs). IRFs are matrices that characterise the effective area (Aeff), the point spread function (PSF), and the energy dispersion probability (EDP), that depend on the direction of the incoming gamma-ray in instrument coordinates, its energy and on the on-ground event filter. 

The result of the MLE is an evaluation of the presence of one or more point-like or extended sources in the sky maps: this is the essential step for the scientific results of AGILE.  

A full description and characterisation of the last release of the Science Tools is available in https://arxiv.org/abs/1903.06957. Science Tools, IRFs and Galactic emission model are publicly available from the AGILE website at SSDC: https://agile.ssdc.asi.it. 





Agilepy analysis
^^^^^^^^^^^^^^^^^^
The AGILE-GRID data analysis can be performed with Agilepy with different techniques:

- using the maximum likelihood estimator analysis
- wavelet techniques
- Lomb-Scargle periodogram analysis (coming soon)

The likelihood analysis reach better sensitivity, more accurate flux measurement, better evaluation of the backgrounds and can work with a detailed source models where more sources can be considered at the same time.

AGILE-GRID light curves can be created in two different ways:

- using the maximum likelihood estimator analysis
- using aperture photometry.

Aperture photometry provides a raw measure of the flux of a sigle source and is less computing demanding.

Maximium Likelihood Estimator caveats
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

During the fitting process some values are fixed and others are variable, depending on the values of the flags. The execution time strongly depends on the number of the variable parameters. It is not possible to predict how long the fitting process will last or how it depends on the number of parameters, but the dependence is not linear. If all the diffuse coefficients are variable and all spectral parameters are free, for M maps and S sources the number of variable parameters will be 2M+4S. In the case of many maps and many sources, this may lead to a very long execution time.

The fitting process takes place in two steps, according to the method of Maximum Likelihood. During each step all the sources are considered one by one, and several fitting attempts are performed by invoking the function TH1D::Fit() provided by the ROOT library, developed by CERN and will find the related documentation on the CERN web site.
