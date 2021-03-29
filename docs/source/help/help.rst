Need Help
=========

If you have troubles please email to:

  - leonardo.baroncelli@inaf.it
  - andrea.bulgarelli@inaf.it

or open an issue of GitHub: https://github.com/AGILESCIENCE/Agilepy/issues

Known issues
------------

  - The unit test "test_aperture_photometry" fails on macos, therefore the aperturePhotometry() method is not available on this OS. 
  - Each notebook should instantiate only one AGAnalysis object, otherwise the logger will be duplicated.
  - In certain situations %matplotlib widget has a weird behaviour. If you have problems with map sizes or interactions, comment the line %matplotlib widget