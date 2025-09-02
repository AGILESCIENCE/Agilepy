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
    :members: __init__, destroy, getConfiguration, loadSourcesFromCatalog, loadSourcesFromFile, selectSources, freeSources, fixSource, addSource, deleteSources, getSources, updateSourcePosition, writeSourcesOnFile, generateMaps, calcBkg, mle, lightCurveMLE, aperturePhotometry, displayCtsSkyMaps, displayExpSkyMaps, displayGasSkyMaps, displayIntSkyMaps, displayLightCurve, convertCatalogToXml, parseMaplistFile, setOptionTimeMJD, setOptionEnergybin, displayGenericColumns 

AGAnalysisWavelet
*****************
.. autoclass:: api.AGAnalysisWavelet.AGAnalysisWavelet
    :members: __init__, getConfiguration, waveletAnalysis, waveletDisplay

AGBayesianBlocks
*****************
.. autoclass:: api.AGBayesianBlocks.AGBayesianBlocks
    :members: __init__, getConfiguration, selectEvents, headEvents, headDetections, getDataIn, getDataOut, datamode, filemode, bayesianBlocks, plotBayesianBlocks

AGRatemeters
************
.. autoclass:: api.AGRatemeters.AGRatemeters
    :members: __init__, getConfiguration, readRatemeters, ratemetersTables, plotRatemeters, analyseSignal, estimateDuration
