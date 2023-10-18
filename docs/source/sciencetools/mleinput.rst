********************************************************
Input files of the MLE
********************************************************

This page provides detailed description of the input files of the science tool `AG_multi <AG_multi.html>`_.


Map list input files
========================

*'.maplist4'* file
^^^^^^^^^^^^^^^^^^
The map list is a text file listing containing at least one line of text. Each line of text describes one set of maps and it is possible to include empty lines or comment lines. The comment lines begin with an exclamation mark.

Each line contains a set of maps:

.. code-block::

    <countsMap> <exposureMap> <gasMap> <offaxisangle> <galcoeff> <isocoeff>

where:

 * countsMap, exposureMap and gasMap are file system paths pointing to the corresponding sky maps (see `Sky Maps section <../manual/products.html>`_)   
 * offaxisangle is in degrees;
 * galcoeff and isocoeff are the coefficients for the galactic and isotropic diffuse components. If positive they will be considered fixed (but see `galmode and isomode <../manual/configuration_file.html#section-model>`_ section).

AGILE format (text file)
========================
The source list is a text file listing at least one source. Each line of text describes one source, and it is possible to include empty lines or comment lines. The comment lines begin with an exclamation mark. 

Each source is described by a line containing space-separated values, in the following order:

::

   'flux' 'l' 'b' 'index' 'fixflag' 'minSqrt(TS)' 'name' 'locationlimit' 'funtype' 'par2' 'par3' 'index limit min' 'index limit max' 'par2 limit min' 'par2 limit max' 'par3 limit min' 'par3 limit max'

The '*flux*' parameter is expressed in cm^-2 s^-1, and galactic longitude '*l* 'and latitude '*b*' are expressed in degrees.

*minSqrt(TS)* is the minimum acceptable value for the square root of TS: if the optimized significance of a source lies below this value, the source is considered undetected and will be ignored (set to flux = 0) when considering the other sources.

After the source's name (which should not contain a space), an optional value for the location limitation ('*locationlimit*') in degrees may be provided. If this value is present and not zero, the longitude and latitude of the source will not be allowed to vary by more than this value from its initial position.

According to the *fixflag*, some or all values will be optimized by being allowed to vary. 

The *funtype* parameter and the spectral model
----------------------------------------------

The '*funtype*' specify the spectral model. PL indicates power-law fit to the energy spectrum; PC indicates power-law with exponential cut-off fit to the energy spectrum; PS indicates power-law with super-exponential cut-off fit to the energy spectrum; LP indicates log-parabola fit to the energy spectrum.

The '*index*' of each source represents the initial estimates of the values for that source (a positive number) and could represent the spectral index of the source (see the following table). The other spectral parameters depend on the spectral shape of the source. '*index limit min*' and '*index limit max*' specifies the minimum and maximum range where the '*index*' is searched.

The '*par2*' and '*par3*' parameters represent additional spectral parameters in the following table.  '*par2 limit min*', '*par2 limit max*', '*par3 limit min*', and '*par3 limit max*' specify the minimum and maximum range of the '*par2*' and '*par3*' respectively.

.. csv-table::
  :header: "funtype", "spectral model", " ", "index", "par2", "par3"

    0, "PL", "PowerLaw", "x^(-[index])", α, ,
    1, "PC", "PLExpCutoff", "x^(-[index]) * e^(- x / [par2])", α, Ec, 
    2, "PS", "PLSuperExpCutoff", "x^(-[index]) * e^(- pow(x / [par2], [par3]))", α, Ec, β
    3, "LP", "LogParabola", "( x / [par2] ) ^ ( -( [index] + [par3] * log ( x / [par2] ) ) )", α, Ec, β

The match of the parameteres is:

- *index* = α: Spectral index for PL, PC, and PS spectral models, first index for LP spectral model; Could be Index or Index1 in the XML format
- *par2* = Ec (MeV): cut-off energy for PC and PS spectral models, pivot energy for LP spectral model;
- *par3* = β: Second index for PS spectral models, curvature for LP spectral model;


The usual energy range used to calculate these parameters is 100 MeV – 10 GeV. The MLE procedure calculates also the 1σ uncertainty of the spectral parameters:

- ∆α: Statistical 1σ uncertainty of α;
- ∆Ec (MeV): Statistical 1σ uncertainty of Ec;
- ∆β: Statistical 1σ uncertainty of β.

The fixflag parameter
---------------------

According to the '*fixflag*' some or all of those values will be optimized by being allowed to vary.
The fixflag is a bit mask, each bit indicating whether the corresponding value is to be allowed to vary:

| fixflag = 0 everything is fixed (free=”0”)
| fixflag = 1 indicates the flux (free=”1” in <parameter name="Flux">)
| fixflag = 2 the position is free (free=”1” in <spatialModel type="PointSource">)
| fixflag = 4 the Index or Index1 is free (free=”1” in <parameter name="index"> or <parameter name="index1"> )
| fixflag = 8 the par2 is free (free=”1” in <parameter name="cutoffEnergy"> or <parameter name="pivotEnergy">)
| fixflag = 16 the par3 is free (free=”1” in <parameter name="index2"> or <parameter name="curvature">)
| fixflag = 32 force position to be variable only in Loop2 (free=”2” in <spatialModel type="PointSource">)

The user may combine these values, but the flux will always be allowed to vary if at least one of the other values are.

.. csv-table::
   :header: " ", "flux", "pos(free=1)", "index/index1", "par2=cutoffEnergy/pivotEnergy", "par3=index2/curvature", "pos(free=2)"
   :widths: 20, 20, 20, 20, 20, 20, 20

   fixflag, 1, 2, 4, 8, 16, 32

| Examples:
| fixflag = 0: everything is fixed. This is for known sources which must be included in order to search for other nearby sources.
| fixflag = 1: flux variable, position fixed
| fixflag = 2: only the position is variable, but MLE will let the flux vary too, so this is equivalent to 3.
| fixflag = 3: flux and position variable, *index* fixed
| fixflag = 4: *index* variable (and flux variable)
| fixflag = 5: flux and *index* variable, position fixed
| fixflag = 7: flux, position and *index* variable and also
| fixflag = 28: *index*, *par2* and *par3* variable (and flux variable)
| fixflag = 30: position, *index*, *par2* and *par3* variable (and flux variable)
| fixflag = 32: position=2, the rest is fixed


