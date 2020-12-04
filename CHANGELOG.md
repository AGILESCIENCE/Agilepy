# Changelog

## Release 1.2.0
* (\#154) The method displayCtsSkyMaps() won't throw an error anymore in case of two maps to be drawn with singleMode=True.
* (\#152) The setOptions() call to increment the number of energy bins while galcoeff and isocoeff are equal = null  won't throw an error anymore.
* (\#161, \#165, \#166) Documentation updated.
* (\#160) Interactive plots in notebooks
* (\#170) Added APDisplayAGILEFermiComparison class to compare ap and offaxis results
* (\#172) Added Offaxis tool to compute agile and fermi offaxis
* (\#173) Refactoring: internal refactoring, AGEngVisibility1 renamed in AGEngAgileOffaxisVisibility, AGEngVisibility2 renamed in AGEngAgileFermiOffaxisVisibilityComparison, notebooks/documentation updated.  
* (\#176) Added AG_ap science tool => new AGAnalysis API method aperturePhotometry(). When displayLightCurve() is called the type of light curve to display must be choosen.
* (\#177) New feature Wavelet analysis
* (\#180) Agilepy logger in external packages
* (\#186) Timelist handling
* (\#189) New feature to display INT maps
* (\#191) New feature wavelet display

## Release 1.1.1 - 28/03/20
* (\#151) The method getConfiguration() accepts also "evtfile" and "logfile" and it raises an Exception if those files are not compabile with "tmin" and "tmax".
* The flare advocate template notebook is moved under the analysis_notebook folder.  
* (\#150) Fixed API documentation build error.
* Added OJ287 analysis notebook.
* Documentation: "QuickStart" chapter updated.

## Release 1.1.0
* (\#141) Added the utility method AGAnalysis.getConfiguration(..) to write on disk the configuration file needed by Agilepy.
* (\#141) Added the utility method AGAnalysis.deleteAnalysisDir() to delete the output folder of the analysis.
* (\#141) The methods loadSourcesFromCatalog(..), deleteSources(..), selectSources(..) and freeSources(..) have an additional optional input parameter called "show" (it defaults to False). If it is True the sources affected by the methods are printed on the standard output.
* (\#144) The light curve data has now more columns. The scientific notation of flux, flux_err, flux_ul has a fixed e-08 exponent.
* (\#147) The lightCurve() method accepts explicit tmin, tmax and timetype arguments that will override the deafult ones.
* (\#79) Added displayLightCurve() method.
