Quickstart guide
================

To import the library:

::

    from agilepy.api import AGAnalysis


When creating an AGAnalysis instance, the configuration is initialized by passing a YAML configuration file path and a XML file describing the sources to the class constructor:
::

    aga = AGAnalysis('agconfig.yaml', 'sources.xml')

Keyword arguments can be passed via setOptions() to override configuration parameters:
::

    aga.setOptions(binsize=0.50, outdir="./output")

To generate maps:
::

    maplistfile = aga.generateMaps()

To perform an maximum likelyhood estimation analysis:
::

    sourcefiles = aga.mle(maplistfile)


.. hint:: Try out the tutorial on the **quickstart notebook**:

   ::

      start_tutorial_notebook.sh
