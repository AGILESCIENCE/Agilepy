*****************
Jupyter Notebooks
*****************

Several Jupyter notebooks are available. You can check the available JupyterLab servers with:

::

   docker exec $CONTAINER_NAME /home/flareadvocate/.local/bin/jupyter server list


Tutorial notebooks
******************
There're several categories of tutorial notebooks:

- science_api_tutorial: the most important ones. They show the basic usage of Agilepy to perform a scientific analysis for sources detection. The following notebooks are useful example of the use of Agilepy and they can be runned using provided sample data: 

  - `VELA <../_static/notebooks/VELA.html>`_: analysis of Vela region
  - `3C454.3 <../_static/notebooks/3C454d3-final.html>`_: analysis of November's 2010 gamma-ray flare of AGN 3C454.3.
  - `AITOFF <../_static/notebooks/aitoff_maps.html>`_: how to produce a full sky AITOFF projection image.

- `Wavelet analysis <../_static/notebooks/wavelet_analysis.html>`_: it shows how to use the Agilepy's wavelet analysis API. 
- engineering_api_tutorial: they show how to use the Agilepy's engineering analysis API. 
- `Bayesian Blocks analysis <../_static/notebooks/BayesianBlocks_tutorial.html>`_: run the Bayesian Blocks algorithm on AGILE light curves produced by Maximum Likelihood or Aperture Photometry algorithms, or on unbinnned data.
- `Ratemeters analysis <../_static/notebooks/Ratemeters_tutorial.html>`_: Tutorial for the analysis of the Light Curves produced by the AGILE Scientific Ratemeters.


The following notebook is another useful example of the use of Agilepy that is runned downloading AGILE data from SSDC website:

  - `PKS1510-089 <../_static/notebooks/PKS1510-089_2009.html>`_: analysis of 2009 gamma-ray flare




Analysis notebooks
******************
  
  - These notebooks have been developed for internal purposes of the AGILE Team. 
  - A template notebook is also provided to speed up the development of a new analysis notebook for AGILE Flare Advocate team.