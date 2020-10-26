Analysis API
============

.. autoclass:: api.AGBaseAnalysis.AGBaseAnalysis
    :members: __init__, deleteAnalysisDir, setOptions, getOption, printOptions


.. autoclass:: api.AGAnalysis.AGAnalysis
    :members: __init__, getConfiguration, loadSourcesFromCatalog, loadSourcesFromFile, convertCatalogToXml, parseMaplistFile, generateMaps, calcBkg, mle, updateSourcePosition, lightCurve, getSources, selectSources, freeSources, addSource, deleteSources, displayCtsSkyMaps, displayExpSkyMaps, displayGasSkyMaps, displayLightCurve
