Quickstart guide
================

To import the library:

::

    from agilepy.api import AGAnalysis

You can create the (required) yaml configuration file, using the following utility method:

::

    AGAnalysis.getConfiguration(
      confFilePath = "agconfig.yaml",
      userName = "username",
      sourceName = "OJ287",
      tmin = 58930,
      tmax = 58936,
      timetype = "MJD",
      glon = 206.8121188769472,
      glat = 35.8208923457401,
      outputDir = "$HOME/agilepy_analysis",
      verboselvl = 1
    )


In order to interact with the library you need to obtain an instance of the AGAnalysis class:

::

    ag = AGAnalysis('agconfig.yaml')


The you have to load the models of the sources (you can filter them by their distance (degree) from l,b provided within the configuration file):

::

    ag = loadSourcesFromCatalog('2AGL', rangeDist=(0, 10))


Keyword arguments can be passed via setOptions() to override configuration parameters:

::

    ag.setOptions(binsize=0.50, outdir="./output")

To generate sky maps:

::

    maplistfile = ag.generateMaps()

To display the sky maps:

::

  ag.displayCtsSkyMaps(smooth=True, sigma=3)
  ag.displayExpSkyMaps()
  ag.displayGasSkyMaps()


To perform an maximum likelyhood estimation analysis:

::

    sourcefiles = ag.mle()

You can query the Sources Library with an arbitrary boolean expression string:

::

    selectedSources = ag.selectSources("flux > 0 AND dist <= 1 OR sqrtTS > 3")


To fix or free a source parameter:

::

    sourcefiles = ag.freeSources('name == "CYGX3"', "flux", True)


You can generate a light curve data file with...

::

    lightCurveData = ag.lightCurve("CYGX3", tmin=58930 , tmax=58936, binsize=10800)


...and display the light curve plot with:

::

    ag.displayLightCurve()



.. hint:: Try out the **tutorial notebooks** and the **analysis notebooks**:

   ::

      start_agilepy_notebooks.sh


.. hint:: Check out the API documentation!
