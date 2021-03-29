************
Analysis API
************

AGBaseAnalysis
**************
.. autoclass:: core.AGBaseAnalysis.AGBaseAnalysis
    :members: __init__, deleteAnalysisDir, setOptions, getOption, printOptions, getAnalysisDir


AGAnalysis
**********
.. autoclass:: api.AGAnalysis.AGAnalysis
    :members: __init__, destroy, getConfiguration, loadSourcesFromCatalog, loadSourcesFromFile, selectSources, freeSources, fixSource, addSource, deleteSources, getSources, updateSourcePosition, writeSourcesOnFile, generateMaps, calcBkg, mle, lightCurveMLE, aperturePhotometry, displayCtsSkyMaps, displayExpSkyMaps, displayGasSkyMaps, displayIntSkyMaps, displayLightCurve, convertCatalogToXml, parseMaplistFile, setOptionTimeMJD, setOptionEnergybin, displayGenericColumn 

AGAnalysisWavelet
*****************
.. autoclass:: api.AGAnalysisWavelet.AGAnalysisWavelet
    :members: __init__, getConfiguration, waveletAnalysis, waveletDisplay
