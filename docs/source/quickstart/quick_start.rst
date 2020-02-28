Quickstart guide
================

To import the library:

::

    from agilepy.api import AGAnalysis


When creating an AGAnalysis instance, the configuration is initialized by passing a YAML configuration file:

::

    aga = AGAnalysis('agconfig.yaml', 'sources.xml')

The you have to load the models of the sources (you can filter them by their distance (degree) from l,b provided within the configuration file):

::

    aga = loadSources('sources.xml', rangeDist=(0, 10))


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





.. hint:: Try out the **tutorial notebooks**:

   ::

      start_agilepy_notebooks.sh
