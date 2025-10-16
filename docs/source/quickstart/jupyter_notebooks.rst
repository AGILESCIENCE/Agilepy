*********
Tutorials
*********

Tutorials are available as Jupyter notebooks, showing the usage of ``agilepy`` analysis classes using the test datesets installed in the package:

- Scientific Analysis Tutorials: they show the usage of agilepy ``AGAnalysis`` class to perform a scientific analysis for source detection and analysis.

  - `Analysis of the VELA Region <../_static/notebooks/VELA.html>`_: Maximum Likelihood analysis of Vela region (Source Hypothesis, Background Estimation, MLE analysis and Light Curve)
  - `Analysis of a 3C454.3 Flare <../_static/notebooks/3C454d3-final.html>`_: analysis of November's 2010 gamma-ray flare of AGN 3C454.3.
  - `Download and Analysis of PKS1510-089 flare <../_static/notebooks/PKS1510-089_2009.html>`_: analysis of 2009 gamma-ray flare, showing the usage of Agilepy REST API to download data from SSDC.
  - `AGILE Full-Sky Map in AITOFF Projection <../_static/notebooks/aitoff_maps.html>`_: how to produce a full sky AITOFF projection image.
  - `Aperture Photometry Light Curve <../_static/notebooks/AperturePhotometry_tutorial.html>`_: Tutorial for computing the Aperture Photometry Light Curve using the 3C454.3 data.

- `Wavelet analysis <../_static/notebooks/wavelet_analysis.html>`_: it shows how to use the Agilepy's wavelet analysis API. 
- `Bayesian Blocks analysis <../_static/notebooks/BayesianBlocks_tutorial.html>`_: run the Bayesian Blocks algorithm on AGILE light curves produced by Maximum Likelihood or Aperture Photometry algorithms, or on unbinnned data.
- `Ratemeters analysis <../_static/notebooks/Ratemeters_tutorial.html>`_: Tutorial for the analysis of the Light Curves produced by the AGILE Scientific Ratemeters.
- `Visibility analysis <../_static/notebooks/Visibility_tutorial.html>`_: Tutorial to compute the Off-axis angle of a source to check its visibility. 

The Tutorials shown above can be downloaded in ``.ipynb`` format from: `agilepy/notebooks/tutorial_notebooks <https://github.com/AGILESCIENCE/Agilepy/tree/master/agilepy/notebooks/tutorial_notebooks>`_.


You can check the available Jupyter servers with:

::

   docker exec $CONTAINER_NAME /home/flareadvocate/.local/bin/jupyter server list




Analysis notebooks
******************
  
The analysis notebooks are available at: `agilepy/notebooks/analysis_notebooks <https://github.com/AGILESCIENCE/Agilepy/tree/master/agilepy/notebooks/analysis_notebooks>`_.
These notebooks have been developed for internal purposes of the AGILE Team.
A template notebook is also provided to speed up the development of a new analysis notebook for AGILE Flare Advocate team.
