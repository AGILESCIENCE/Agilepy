# Changelog

## Release 1.6.5 (May 20, 2025)
* [#41](https://github.com/AGILESCIENCE/Agilepy/issues/41): Documentation update on installation procedures.
* [#48](https://github.com/AGILESCIENCE/Agilepy/issues/48): Fix a bug in the `entrypoint.sh` script for `agilepy` container that caused it to crash.
* [#46](https://github.com/AGILESCIENCE/Agilepy/issues/46): Implement `agilepy/scripts/start_test_rest_api.sh` to test the REST API with data download from SSDC, and use it in CI pipelines.
* [#37](https://github.com/AGILESCIENCE/Agilepy/issues/37): Introduce a CI pipeline that builds the `agilepy` image, runs the container and performs unit tests.
* [#44](https://github.com/AGILESCIENCE/Agilepy/issues/44): Fix CI pipelines to use `agilepy-recipe:BUILD26` instead of `BUILD25b6-v3`. Fix log directories so that tests can be executed without needing the root user.
* [#38](https://github.com/AGILESCIENCE/Agilepy/issues/38): Introduce a "Deprecated Option" Error to be thrown when the user tries to use "emin" and "emax" parameters for the AGAnalysis class. 
* Bug fix: the code to download data with the REST API used to crash due to a misplaced logging instruction.

## Release 1.6.4 (Oct 18, 2023, d3c067e)
* The old Jupyter notebooks have been replaced with JupyterLab (notebook v7)
* The Docker base image has been refactored. The user inside the container can be set to the user on the host to avoid file permission issues. The Root's python bindings are fixed. The unnecessary virtual environment has been removed. Ruby has been installed. The docker recipies have been moved inside the Agilepy repository. The Science Tools BUILD25b7 have been installed.
* The documentation has been improved.
* The Agilepy's python dependencies are now locked. 
* The "emin" and "emax" configuration parameters under "selection" have been deprecated. They are automatically calculated from the "energybins" configuration parameter.
* The "irf" configuration parameter has been introduced. It is used to select the IRF to be used in the analysis. The default value is "default".
* The logger has been refactored and improved. The duplicate logs issue has been fixed. The logging messages have been revisited.
* The test suite has been ported to pytest.
* The AGRatemeters tool has been added.
* The "advanced" API packaged has been introduced: it contains analysis scripts that are built over the "basic" API.

## Release 1.6.3
* Science Tools BUILD25b6, with changes on scripts to make them compatible with Python 3

## Release 1.6.2
* display off-axis comparison refined for GRB analysis
* minor fixes for aperture photometry

## Release 1.6.1
* Minor fixes
* root 6.26
* compilation with c++17

## Release 1.6.0
* (\#296) Now calcbkg updates the results if called multiple times
* (\#331) Docs updated
* (\#334) Minor fixes in print source
* (\#335) New parameter position in lightcurveMLE, default ellipse
* (\#336) Bugfix when computing fixflag   
* (\#342) Now it is possible to select [tmin - pastimewindow, tmax - tmin] as parameter om calcbkg
* (\#346) Minor fix in plots
* (\#347) Handling -nan parameter in multi tool
New anaconda recipes and docker container, environment and dependencies updated

## Release 1.5.1 (March 3, 2022)
* Minor bugfixes and doc updated

## Release 1.5.0 (February 24, 2022)
* (\#287) New Feature: automatic download of the AGILE public data using a REST API directly from SSDC!
* (\#234) Internal refactoring of Source class, new set/get interface for Source class. Docs updated.
* (\#291) Codacy coverage fixed
* (\#282) Dependencies updated and CI improved
* (\#287b) Brand new API for date conversion using Astropy Time
* (\#303) AG_spotfinder tool added
* Various bugfixes and improvements

## Release 1.4.2 (May 26, 2021)
* Minor hotfixes and docs updated

## Release 1.4.1 (April 26, 2021)
* minor bugfixes and docs updated

##  Release 1.4.0 (April 22, 2021)
* (\#234) Added new installation method with docker containers
* (\#267) Added several columns into lightcurvedata txt
* (\#272) Updated method for displaying columns of lightcurve data
* Various bugfixes and improvements

##  Release 1.3.0 (March 29, 2021)
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
* (\#260) New lightcurvedata file
* (\#264) New plotting method for generic lightcurvedata columns
* (\#265) New parameter for plotting FERMI's lightcurve
* (anaconda package update) The installation time of Agilepy has been reduced a lot.

## Release 1.2.0 (December 10, 2020)
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

## Release 1.1.1 (March 28, 2020)
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
