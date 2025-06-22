========================
Bayesian Blocks Analysis
========================

Bayesian Blocks, provide an adaptive, data-driven method for optimal segmentation of time series or event data.
Instead of relying on fixed bin sizes, Bayesian Blocks dynamically determine change points in the data, dividing it into piecewise constant segments (blocks) that best represent the structure of the signal.
We follow the formalization of `Scargle et al. (2013) <https://iopscience.iop.org/article/10.1088/0004-637X/764/2/167>`_.

Key features of the Bayesian Blocks algorithm include:
  * Model selection via Bayesian inference: The algorithm selects the most probable segmentation under a Bayesian framework, balancing goodness-of-fit with model complexity.
  * Applicability to different data modes: It works with event data (e.g., photon arrival times), regularly sampled time series, and point measurements with errors.
  * Non-parametric nature: The method does not assume a particular functional form for the signal, making it robust and flexible.

``Agilepy`` implements a ``AGBayesianBlocks`` class that works with:
- Binned data, i.e. Light Curves. Input data can be provided in 3 different formats: the agile Aperture Photometry Light Curve format, the agile Maximum Likelihood Light Curve format, a *custom* light curve format.
- Unbinned data, i.e. a list of arrival times of detected photons.

The Bayesian Blocks algorithm has the following steps:
1. Prepare a ``YAML`` configuration file for ``AGBayesianBlocks``. You can do it manually or by using ``AGBayesianBlocks.getConfiguration()``.
2. Define a ``AGBayesianBlocks`` object, and load the data with ``AGBayesianBlocks.selectEvents()``.
3. Compute the Bayesian blocks with ``AGBayesianBlocks.bayesianBlocks()``.


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
   "filenameprefix", "string", "analysis_product", "no", "Prefix for files."
   "logfilenameprefix", "string", "analysis_log", "no", "Prefix for log files."
   "sourcename", "string", "bb-source", "no", "Tag with source name."
   "username", "string", "my_name", "no", "Tag with user name."
   "verboselvl", "int", "0", "yes", "0 for no extra logs, 1 for INFO, 2 for DEBUG."


Selection
~~~~~~~~~

 .. csv-table::
   :header: "Option", "Type", "Default", "Required", "Description"
   :widths: 20, 20, 20, 20, 100

   "file_path", "string", "", "yes", "Path to the input file."
   "file_mode", "string", "", "yes", "Input file format: AGILE_PH (unbinned data), AGILE_AP, AGILE_MLE or CUSTOM_LC (binned data)."
   "tstart", "float", "null", "no", "If definend, select events according to the start time."
   "tstop", "float", "null", "no", "If definend, select events according to the stop time."
   "ratecorrection", "float", "0", "no", "Flux correction."

For ``AGILE_AP`` and ``AGILE_MLE``, ``tstart`` and ``tstop`` must be in ``MJD`` format.
For ``CUSTOM_LC`` and ``AGILE_PH``, in the same format of the times provided.


.. note:: Note on ``ratecorrection``.
          The Bayesian Blocks algorithm works with integers, so fluxes need a correction factor for a correct statistical treatment.
          If 0 (default), the correction factor is the mean exposure.
          If a float is provided it will be applied as a correction factor for the flux.
          If -1, the algorithm will work with counts instead of fluxes.


Bayesianblocks
~~~~~~~~~~~~~~

 .. csv-table::
   :header: "Option", "Type", "Default", "Required", "Description"
   :widths: 20, 20, 20, 20, 100

   "fitness", "string", "events", "no", "Fitness function of the algorithm: events, measures or regular_events."
   "p0", "string", "0.35", "no", "Prior parameter, suggested for unbinned data, gives the false alarm probability to compute the prior."
   "gamma", "float", "null", "no", "Prior parameter, suggested for binned data, gives the slope of the prior on the number of bins."
   "useerror", "bool", "true", "no", "If true, account for error in blocks computation."


.. note:: Note on ``fitness``.
          It sets the type of algorithm.
          Possible values are `events` (binned light curve or unbinned event data), `measures` (sequence of flux measurements with Gaussian errors), `regular_events`(0/1 data measured regularly).

