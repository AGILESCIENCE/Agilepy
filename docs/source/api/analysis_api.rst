Analysis API
============

.. autoclass:: core.AGBaseAnalysis.AGBaseAnalysis
    :members: __init__, deleteAnalysisDir, setOptions, getOption, printOptions


.. autoclass:: api.AGAnalysis.AGAnalysis
    :members: __init__, getConfiguration, loadSourcesFromCatalog, loadSourcesFromFile, convertCatalogToXml, parseMaplistFile, generateMaps, calcBkg, mle, updateSourcePosition, aperturePhotometry, lightCurveMLE, getSources, selectSources, freeSources, addSource, deleteSources, displayCtsSkyMaps, displayExpSkyMaps, displayGasSkyMaps, displayLightCurve

.. autoclass:: api.AGAnalysisWavelet.AGAnalysisWavelet
    :members: __init__, getConfiguration, waveletAnalysis, waveletDisplay