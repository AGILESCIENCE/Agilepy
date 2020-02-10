************
Sources file
************

The sources can be defined using one of two different formats: xml document and text file.

The flux parameter estimates are relevant in the fitting process, as the sources
are considered one by one starting with the one with the brightest initial flux
value, regardless of the order they are given in the source file.

Text file format (AGILE format)
===============================

Each source is described by a line containing space separated values, in the following order:

::

   'flux' 'l' 'b' 'spectral index' 'fixflag' 'minSqrt(TS)' 'name' 'locationlimit' 'funtype' 'par2' 'par3' 'index limit min' 'index limit max' 'par2 limit min' 'par2 limit max' 'par3 limit min' 'par3 limit max'

The '*flux*' parameter is expressed in cm^-2 s^-1, galactic longitude '*l* 'and latitude '*b*' are expressed in degrees.

The spectral index of each source represents the initial estimates of the values for that source (a positive number).

The fixflag parameter
---------------------

According to the '*fixflag*' some or all of those values will be optimized by being allowed to vary.
The fixflag is a bit mask, each bit indicating whether the corresponding value is to be allowed to vary:

| fixflag = 0 everything is fixed (free=”0”)
| fixflag = 1 indicates the flux (free=”1” in <parameter name="Flux">)
| fixflag = 2 the position is free (free=”1” in <spatialModel type="PointSource">)
| fixflag = 4 the Index or Index1 is free (free=”1” in <parameter name="Index"> or <parameter name="Index1"> )
| fixflag = 8 the par2 is free (free=”1” in <parameter name="CutoffEnergy"> or <parameter name="PivotEnergy">)
| fixflag = 16 the par3 is free (free=”1” in <parameter name="Index2"> or <parameter name="Curvature">)
| fixflag = 32 force position to be variable only in Loop2 (free=”2” in <spatialModel type="PointSource">)

The user may combine these values, but the flux will always be allowed to vary if at least one of the other values are.

.. csv-table::
   :header: " ", "flux", "pos(free=1)", "Index/Index1", "cutoff/pivot", "Index2/Curvature", "pos(free=2)"
   :widths: 20, 20, 20, 20, 20, 20, 20

   fixflag, 1, 2, 4, 8, 16, 32

| Examples:
| fixflag = 0: everything is fixed. This is for known sources which must be included in order to search for other nearby sources.
| fixflag = 1: flux variable, position fixed
| fixflag = 2: only the position is variable, but AG_multi will let the flux vary too, so this is equivalent to 3.
| fixflag = 3: flux and position variable, index fixed
| fixflag = 4: index variable (and flux variable)
| fixflag = 5: flux and Index variable, position fixed
| fixflag = 7: flux, position and Index variable and also
| fixflag = 28: Index, par2 and par3 variable (and flux variable)
| fixflag = 30: position, Index, par2 and par3 variable (and flux variable)
| fixflag = 32: position=2, the rest is fixed

The funtype parameter
---------------------

| 0) "PL", "x^(-[index])"
| 1) "PLExpCutoff", "x^(-[index]) * e^(- x / [par2])"
| 2) "PLSuperExpCutoff", "x^(-[index]) * e^(- pow(x / [par2], [par3]))"
| 3) "LogParabola", "( x / [par2] ) ^ ( -( [index] + [par3] * log ( x / [par2] ) ) )"




xml format
==========

.. code-block:: xml

  <?xml version="1.0" ?>
  <source_library title="source library">

    <!-- Point Sources -->
    <source name="2AGLJ2202+4214" type="PointSource">
      <spectrum type="PowerLaw">
        <parameter name="Flux" free="1"  value="7.45398e-08"/>
        <parameter name="Index" free="1" scale="-1.0" value="1.96903" min="0.5" max="5"/>
      </spectrum>
      <spatialModel type="PointSource" location_limit="0" free="0">
        <parameter name="GLON" value="92.4102" />
        <parameter name="GLAT" value="-10.3946" />
      </spatialModel>
    </source>

    <source name="2AGLJ0007+7308" type="PointSource">
      <spectrum type="PLExpCutoff">
         <parameter name="Flux" free="1"  value="41.6072e-08"/>
         <parameter name="Index" free="1" scale="-1.0" value="1.29082" min="0.5" max="5"/>
         <parameter name="CutoffEnergy" free="1" scale="-1.0" value="2003.9" min="20" max="10000"/>
      </spectrum>
      <spatialModel type="PointSource" location_limit="0" free="0">
         <parameter name="GLON" value="119.677" />
         <parameter name="GLAT" value="10.544" />
      </spatialModel>
    </source>

    <source name="2AGLJ0835-4514" type="PointSource">
      <spectrum type="PLSuperExpCutoff">
        <parameter name="Flux" free="1"  value="969.539e-08"/>
        <parameter name="Index1" free="1" scale="-1.0" value="1.71345" min="0.5" min="5"/>
        <parameter name="CutoffEnergy" free="1" value="3913.06" min="20" max="10000"/>
        <parameter name="Index2" free="1" value="1.3477" min="0"  max="100"/>
      </spectrum>
      <spatialModel type="PointSource" location_limit="0" free="0">
        <parameter name="GLON" value="263.585" />
        <parameter name="GLAT" value="-2.84083" />
      </spatialModel>
    </source>

    <source name="2AGLJ1801-2334" type="PointSource">
      <spectrum type="LogParabola">
        <parameter name="Flux" free="1"  value="35.79e-08"/>
        <parameter name="Index" free="1" scale="-1.0" value="3.37991" min="1" min="4"/>
        <parameter name="PivotEnergy" free="1" scale="-1.0" value="2935.07" min="500" max="3000"/>
        <parameter name="Curvature" free="1" scale="-1.0" value="0.682363" min="0.1" max="3"/>
      </spectrum>
      <spatialModel type="PointSource" location_limit="0" free="1">
        <parameter name="GLON" value="6.16978" />
        <parameter name="GLAT" value="-0.0676943" />
      </spatialModel>
    </source>

  </source_library>
