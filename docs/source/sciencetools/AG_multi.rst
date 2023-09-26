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

	AG_multi value1 value2 value3...

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
	ulcl,	Real,	Sources for which a flux optimization is requested will have a flux upper limit calculated (in addition to a best-fit flux and error where possible). This parameter specifies the confidence level for the flux upper limits (=1 for 1 sigma - =2 for two sigma - etc.)
	loccl,	Real,	This parameter specifies the confidence limit of the source location contour for sources for which a source location optimization is requested. It is expressed as a difference in test statistic distributed according to chi-squared with two degrees of freedom (e.g.  1.38629 = 50% - 2.29575 = 68% - 5.99147 = 95% - 9.21034 = 99%).

The parameters ulcl and loccl will typically have the values 2.0 (2 sigma upper limits) and 5.99147 (95% confidence contour), respectively, but may be changed by the user for use in, for example, light curves (e.g. ulcl = 1) or cases in which the 95% contour cannot be calculated (e.g. loccl = 2.29575).

The parameter ranal should be the smallest value consistent with 1) the angular extent of the point spread function in the given energy range and 2) the distance to nearby strong sources. In most cases, no more than 10 degrees will be required, and in many cases it is possible to use a smaller value such as 5 degrees.

As we have seen above, during the fitting process some values are fixed and others are variable, depending on the values of the flags. The execution time strongly depends on the number of the variable parameters. It is not possible to predict how long the fitting process will last or how it depends on the number of parameters, but the dependence is not linear.
If all the diffuse coefficients are variable and all the fix flags are set to 7, for M maps and S sources the number of variable parameters will be 2M+4S.
In the case of many maps and many sources, this may lead to a very long execution time.

The fitting process takes place in two steps, according to the method of Maximum Likelihood. During each step all the sources are considered one by one, and several fitting attempts are performed by invoking the function TH1D::Fit() provided by the ROOT library, developed by CERN.
The user will see on the screen the ouput printed by that function, and will find the related documentation on the CERN web site.

Input files
^^^^^^^^^^^^^^^^^^^^
A detailed description of the input files of the MLE is provided `here <mleinput.html>`_
.

Output files
^^^^^^^^^^^^^^^^^^^^
A detailed description of the output files of the MLE is provided `here <mleoutput.html>`_
.

TS Calculation
^^^^^^^^^^^^^^^^^^^^

Overview of TS

The calculation of TS for a given source is carried out as per Mattox's document [1] in the following manner.

We define Likelihood (L) as the probability of the observed data for a certain emission model, calculated as the product of probabilities for each pixel:

.. math::

  (1) L = \prod_{ij} p_{ij}

Now, let's consider the natural logarithm of L, taking into account a Poisson distribution of the probability of observing n_{ij} counts in pixel ij:

.. math::

  (2) \ln L = \sum_{ij} n_{ij} \ln(\theta_{ij}) - \sum_{ij} \theta_{ij} - \sum_{ij} \ln(n_{ij}!)

where \(\theta_{ij}\) represents the photons expected by the model, and \(n_{ij}\) are the measured counts.

The third term does not depend on the model but only on the data, and it is not useful for our purpose. Thus, we can define:

.. math::

 (3)  \ln L = \sum_{ij} n_{ij} \ln(\theta_{ij}) - \sum_{ij} \theta_{ij}

The value of TS for a given source is defined as minus twice the difference between the logarithms of L for a model that excludes that source and one that includes it, denoted as L0 and L1, respectively:

.. math::

 (4)  TS = -2(\ln L_0 - \ln L_1)

It is worth noting that the term dependent only on the data, which was eliminated in the transition from (2) to (3), would cancel out as the data are the same in both cases.

The same formula can also be seen as:

.. math::

 (5)  TS = 2 \sum_{ij} n_{ij} (\ln \theta_{ij1} - \ln \theta_{ij0}) - (\theta_{ij1} - \theta_{ij0})

where the subscripts 1 and 0 respectively indicate the model with or without the source under examination.

TS Calculation

AG_multi calculates the TS values for each source predicted by the model, relying on the Minuit functions provided by the Root library to perform the fitting. There is a function that, at the end of the fitting, returns a value referred to as FCN in that context, which we have confirmed corresponds to twice the logarithm of L given by formula (2).

The same function, iteratively called during the fitting process, the so-called FitFunction, can be invoked at any time to provide the part of ln L dependent on the model, as described by formula (3).
For each pixel, it sums all the contributions from the sources in the model and thus precisely provides the value of :math:`\theta_{ij}`. That is, :math:`\theta_{ij} = f(ij, M)` where :math:`f` is the FitFunction, :math:`ij` is the pixel, and :math:`M` is a vector of numbers describing the model. The value of :math:`n_{ij}` is contained in the count map, and if desired, it is straightforward to calculate the last term in (2), although this does not contribute to the TS calculation.

There are two contexts in which TS needs to be calculated. One is during the fitting process to guide the process itself, and the other is at the end of processing to provide results to the user. In the first case, the TS value refers to a model that is not entirely consolidated, whereas in the second case, it relates to the final model.

Currently, AG_multi calculates the TS value to present to the user when the model is not fully consolidated but is already close to the final result.
In particular, when calculating the position of the i-th source in the list, the position and spectral index of the subsequent sources have not yet assumed their definitive values.
The TS calculation is based on the FCN value returned by the Minuit routines immediately after fitting.

TS Calculation in the Presence of Other Variable Components

The fitting process typically considers more than one variable component in the model, be they diffuse components, extended, or point-like sources.
To calculate the TS value, it is necessary to consider two versions of the model, one that includes the source under examination and one that does not, obtaining the two values referred to as :math:`L_1` and :math:`L_0` in (4).
In the presence of other variable components, when removing the source under examination, the fitting process will tend to compensate by attributing the missing photons to those components.
In the absence of other variable components, on the other hand, the values of :math:`\theta_{ij0}` will necessarily be lower than those of :math:`\theta_{ij1}`, simply because we have 'turned off' the source under examination, and this difference alone determines the value of TS.
Therefore, the TS value for a source is not purely associated with that source but depends on the level of uncertainty in the entire model. If one accepts that certain photons can be explained by the higher intensity of other sources, one will typically obtain a lower TS.

However, it is possible to know, without performing the fitting again, what the TS would have been for each source under different initial assumptions. Using the output data from the fitting and applying formula (5), you can calculate the TS assuming all other sources are fixed and the diffuse components are fixed.

Conclusions

We have verified that the TS value calculated by AG_multi conforms to the requirements. In fact, the value of FCN provided by Minuit is precisely the value to be inserted into the formulas mentioned above.
This value could be calculated more accurately at the end of fitting when definitive data are available. However, it would yield a value only slightly different at the cost of significant development efforts.
Instead, it is easy to calculate the 'alternative' TS values (in the case of different initial assumptions), and indeed, the latest version of AG_multi prints these values on-screen.

References
1) J.R.Mattox et al., "The Likelihood analysis of Egret data," The Astrophysical Journal, 461:396-407, 1996 April 10


Technical Documents
^^^^^^^^^^^^^^^^^^^^

`PSF_generation.pdf <../_static/pdf/PSF_generation.pdf>`_
