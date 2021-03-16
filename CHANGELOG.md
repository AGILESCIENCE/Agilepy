# Changelog
## Next release (1.3.0)
* (\#133) New normalization functions in displaymaps
* (\#196) Notebooks have their own documentation section
* (\#201) The confFilePath parameter of the getConfiguration(..) method now supports environment variables.
* (\#202) A new dataset (for testing/validation purposes) has been included.
* (\#203) The "INDEX file with one line crash" bug has been fixed.
* (\#208) useEDPmatrixforEXP default value is now: False.
* (\#215) After calling mle(), each free parameter will be updated (if they need to).
* (\#217) The quickstart guide and the tutorial notebooks show how to change the value of a spectrum parameter of a source
* (\#231) New utility for filtering ap in Astroutils
* (\#238) New methods setOptionTimeMJD setOptionEnergybin
* (\#242) tdms progress bars 
* (\#252) New methods for setting dq
* (anaconda package update) The installation time of Agilepy has been reduced a lot.

## Release 1.2.0 - 10/12/20
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
