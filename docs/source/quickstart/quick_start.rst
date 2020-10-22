Quickstart guide
================

To import the library:

::

    from agilepy.api import AGmle

You can create the (required) yaml configuration file, calling the following static method:

::

    AGmle.getConfiguration(
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
          evtfile="/AGILE_PROC3/FM3.119_ASDC2/INDEX/EVT.index", # optional parameter
          logfile="/AGILE_PROC3/DATA_ASDC2/INDEX/LOG.log.index" # optional parameter
    )


In order to interact with the library you need to obtain an instance of the AGmle class:

::

    ag = AGmle('agconfig.yaml')


The you have to load the models of the sources (you can filter them by their distance (degree) from l,b provided within the configuration file):

::

    ag = loadSourcesFromCatalog('2AGL', rangeDist=(0, 10))


Keyword arguments can be passed via setOptions() to override configuration parameters:

::

    ag.setOptions(binsize=0.50, outdir="./output")

To generate sky maps:

::

    maplistfile = ag.generateMaps()

To display and interact with the sky maps:

::

  ag.displayCtsSkyMaps(smooth=True, sigma=3)
  ag.displayExpSkyMaps()
  ag.displayGasSkyMaps()


To perform an maximum likelyhood estimation analysis:

::

    sourcefiles = ag.mle()

You can query the Sources Library with an arbitrary boolean expression string..

::

    selectedSources = ag.selectSources("flux > 0 AND dist <= 1 OR sqrtTS > 3")


..and fix or free a source's parameter:

::

    sourcefiles = ag.freeSources('name == "CYGX3"', "flux", True)


You can generate a light curve data file with...

::

    lightCurveData = ag.lightCurve("CYGX3", tmin=58930 , tmax=58936, binsize=10800)


...and display the interactive light curve plot with:

::

    ag.displayLightCurve()



.. hint:: Try out the **tutorial notebooks** and the **analysis notebooks**:

   ::

      start_agilepy_notebooks.sh


.. hint:: Check out the API documentation!
