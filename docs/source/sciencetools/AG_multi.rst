AG_multi
===========

AG_multi is a command line application running under Linux  64 bits, or Mac OS X.
The aim of this application is to find the best values for the flux, the position and/or the spectral index of a list of gamma ray sources to explain a set of experimental data.
The user will provide a list of maps containing maps of photons detected by the AGILE satellite during one or a series of observations,
together with maps of the instrument exposure during those observations and the corresponding Galactic diffuse emission models.
The user will also provide a list of sources that may explain the photons detected, giving a guess for the flux, position and spectral index of those sources.
AG_multi will find the best values for the sources to fit the data using the method of maximum likelihood, estimating the improved likelihood due to the presence of each source in the list.
The user has a variety of options to influence the process as explained in the following.

The Command Line
^^^^^^^^^^^^^^^^
The command line is internally managed by the parameter interface library (PIL) developed by the INTEGRAL Science Data Centre (ISDC). Each command line option is described by a .par file, AG_multi.par in this case, a sample of which comes with the distribution.
The environment variable PFILES should be defined in your account, pointing to the directory where the file AG_multi.par resides.
The user has two ways to specify the option values in the command line. One is to specify the option name and its value (in any order), the other is to give just the option values in the order they appear in the .par file.
For example

::

	AG_multi option1=value1 option2=value2 option3=value3...

or

::

	AG_multi4 value1 value2 value3...

If any of the command line options are missing, AG_multi will prompt the user to either confirm the previously used value or to provide a new one.
The values used in the current session will be stored and used in the next session.
This behaviour depends on the .par file that comes with the distribution, which the user may change. Refer to the PIL library online documentation for all the details.



List of parameters:

.. csv-table::
	:header: "Name", "Type", "Description"
	:widths: 5, 5, 5

	maplist,	String,	Name of a text file containing the  list of the maps
	sarfile,	String,	SAR file name
	edpfile,	String,	EDP file name
	psdfile,	String,	PSD file name
	ranal,	Real,	Radius of analysis (degrees)
	galmode,	Integer,	Galactic parameter mode
	isomode,	Integer,	Isotropic parameter mode
	srclist,	String, The name of a text file containing the the list of the gamma ray sources to fit to the list of maps above.
	outfile,	String,	The name of the main text output file - the title of the HTML output - the prefix of the other output file names.
	ulcl,	Real,	Upper limit confidence level
	loccl,	Real,	Location contour confidence level

Input files
^^^^^^^^^^^^^^^^^^^^
A detailed description of the input files of the MLE is provided `here <mleinput.html>`_
.

Output files
^^^^^^^^^^^^^^^^^^^^
A detailed description of the output files of the MLE is provided `here <mleoutput.html>`_
.

Technical Documents
^^^^^^^^^^^^^^^^^^^^

`PSF_generation.pdf <../_static/pdf/PSF_generation.pdf>`_
