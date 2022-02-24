********************
Working with sources
********************

The Source abstraction
**********************
The main abstraction of Agilepy is the Source class. It is described by several parameters, some of which can be free to vary, and they are 
changed by the mle() analysis.

The set of the parameters describing the source can vary, depending on the spectrum and spatial model types of the source. 

The different types of sources are described `here <../manual/source_file.html#source-library-format-xml-document>`_.


How to load or add new sources
******************************
In order to perform a scientific analysis with Agilpy, at least one Source model must be loaded. There are several ways to do that.

The `loadSourcesFromCatalog(catalogName, rangeDist=0, inf, show=False) <../api/analysis_api.html#api-AGAnalysis-AGAnalysis-loadSourcesFromCatalog>`_ 
allows to load a source catalog, while filtering the sources by their distance (degree) from the l,b position provided within the configuration file.

::

    sources = ag.loadSourcesFromCatalog('2AGL', rangeDist=(0, 10))


The `loadSourcesFromFile(sourcesFilepath, rangeDist=0, inf, show=False) <../api/analysis_api.html#api-AGAnalysis-AGAnalysis-loadSourcesFromFile>`_
loads the sources, reading their model from a file. 

The `addSource(sourceName, sourceDict) <../api/analysis_api.html#api-AGAnalysis-AGAnalysis-addSource>`_ method allows the user to define on the fly a 
source model with a python dictionary. Check the tutorial notebooks for an example. 

How to select Source objects
****************************
The sources can be selected via the the `selectSources(selection, show=False) <../api/analysis_api.html#api-AGAnalysis-AGAnalysis-selectSources>`_ method.
The "selection" argument supports either lambda functions and boolean expression strings. The user can call selectSources (with show=True) to show the source description 

::
    
    source = ag.selectSources('name == "2AGLJ2254+1609"', show=False).pop()
    print(source)
    -----------------------------------------------------------
    Source name: 2AGLJ2254+1609 (PointSource)
     * Free parameters: flux
     * Initial source parameters: (PowerLaw)
        - flux(ph/cm2s): 7.50937e-07
        - index: 2.20942
        - Source position: (86.1236, -38.1824) (l,b)
        - Distance from map center: 0.011 deg
   -----------------------------------------------------------

Other examples:

::

    sources = ag.selectSources('name == "PKS1510-089"', show=False)

::

    sources = ag.selectSources('flux > 0', show=False)

::

    sources = ag.selectSources(lambda name, sqrtTS: name == "2AGLJ2021+4029" AND sqrtTS> 0, show=False)


How to let the source's parameters to vary
******************************************
In order to free or fix a sources' parameter, the user can rely on the `freeSources(selection, parameterName, free, show=False) <../api/analysis_api.html#api-AGAnalysis-AGAnalysis-freeSources>`_
method. The "selection" argument is used like in `selectSources`, so you can free a parameter of multiple sources at once.

::
    
    aganalysis.freeSources(lambda name, dist, flux : Name == "2AGLJ2021+4029" AND dist > 0 AND flux > 0, "flux", True)

::

    ag.freeSources('name == "2AGLJ1513-0905"', "index", True, show=True)

Check the api documentation or the tutorial notebooks for additional examples. 



How to check which source's parameters are free to vary
*******************************************************
The user can obtain this information by printing the Source object or calling the getFreeParams() method of the Source object.

::
    
    print(source.getFreeParams())
    ['flux']



The "multi" description of a Source object
******************************************
If the user performs an mle analysis, the Source object will contain also the analysis results. 

::

    print(source)
    -----------------------------------------------------------
    Source name: 2AGLJ2254+1609 (PointSource) => sqrt(ts): 10.2226
     * Free parameters: flux index
     * Initial source parameters: (PowerLaw)
     - flux(ph/cm2s): 7.50937e-07
     - index: 2.20942
     - Source position: (86.1236, -38.1824) (l,b)
     - Distance from map center: 0.011 deg
     * Last MLE analysis:
     - flux(ph/cm2s): 8.68363e-06 +/- 1.62474e-06
     - index: 2.51001 +/- 0.173795
     - upper limit(ph/cm2s): 1.13967e-05
     - ergLog(erg/cm2s): 1.39217e-09 +/- 2.6048e-10
     - galCoeff: [0.7, 0.7, 0.7, 0.7, 0.7]
     - isoCoeff: [5.24757, 3.14662, 0.953512, 1.59944e-10, 0.557554] +/- [0.519283, 0.209362, 0.051478, 0.000108147, 0.000720814]
     - exposure(cm2s): 13672200.0
     - exp-ratio: 0.0
     - L_peak: 86.1236
     - B_peak: -38.1824
     - Distance from start pos: 0.0
     - position:
         - L: -1.0
         - B: -1.0
         - Distance from start pos: -1.0
         - radius of circle: -1.0
         - ellipse:
         - a: -1.0
         - b: -1.0
         - phi: -1.0
   -----------------------------------------------------------

The values L_peak and B_peak set to the initial values in the source location is fixed. If it is allowed to vary then they are set to the position for which the TS is maximized. If a confidence contour was found, the parameters of the "ellipse" section describe the best-fit ellipse of the contour, described in detail below. The counts and fluxes are provided, as well as their symmetric, positive, and negative errors if the flux is allowed to vary. For convenience, the exposure of the source, used to calculate the source counts from the flux, is also provided. Finally, the spectral index and its error, or the other spectral parameters, if applicable, are provided.



How to manually inspect source's attributes
*******************************************
The user can rely on a getter method `get(sourceAttribute) <../core/source_api.html#core-SourceModel-Source-get>`_ method. 

::

    print(source.get("cutoffEnergy"))
    print(source.get("index"))
    print(source.get("pos"))
    print(source.get("dist"))
    print(source.get("locationLimit"))
    print(source.get("multiFlux"))



How to manually change a source's attributes
********************************************
The user can rely on a setter method `set(sourceAttribute) <../core/source_api.html#core-SourceModel-Source-set>`_ method. 

:: 

    source.set("index2", 1.34774)


The setAttributes() method allows to change the following attributes: value, free, scale, min, max, locationLimit. Example:

:: 

    source.spectrum.cutoffEnergy.setAttributes(min=3000, max=5000)



In order to change the position of a source, the user can rely on the `updateSourcePosition(sourceName, glon, glat) <../api/analysis_api.html#api-AGAnalysis-AGAnalysis-updateSourcePosition>`_ 
method.





