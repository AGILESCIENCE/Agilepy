
* (\#141) Added the utility method AGAnalysis.getConfiguration(..) to write on disk the configuration file needed by Agilepy.
* (\#141) Added the utility method AGAnalysis.deleteAnalysisDir() to delete the output folder of the analysis.
* (\#141) The methods loadSourcesFromCatalog(..), deleteSources(..), selectSources(..) and freeSources(..) have an additional optional input parameter called "show" (it defaults to False). If it is True the sources affected by the methods are printed on the standard output.
* (\#144) The light curve data has now more columns. The scientific notation of flux, flux_err, flux_ul has a fixed e-08 exponent.
* (\#147) The lightCurve() method accepts explicit tmin, tmax and timetype arguments that will override the deafult ones.
* (\#79) Added displayLightCurve() method.
