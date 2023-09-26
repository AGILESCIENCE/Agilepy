Calibration files
=================

The parameters sarfile, edpfile, and psdfile provide the names of the three calibration files. These files are described in detail in other documents, and are provided with the distribution. They are FITS files whose common prefix specifies the filter and event type used and whose suffixes are .sar.gz, .edp.gz and .psd.gz, respectively. Ordinarily, they should not be changed by the user.
The parameter expcorrfile provides a correction factor as a function of off-axis angle for older calibration files. It should not be changed by the user.