******************
Source file
******************
|

AGILE technical info
======================

Each source is described by a line containing space separated values, in the following order:

.. code-block::

   <flux> <l> <b> <spectral index> <fixFlag> <minSqrt(TS)> <name> <location_limit> <funtype> <par2> <par3> <index limit min> <index limit max> <par2 limit min> <par2 limit max> <par3 limit min> <par3 limit max>


The first 4 values, flux in cm^-2 s^-1, galactic longitude and latitude in degrees, and spectral index of each source, represent the initial estimates of the values for that source (a positive number).

fixflag
-------------------------

According to the fixflag some or all of those values will be optimized by being allowed to vary.
The fixflag is a bit mask, each bit indicating whether the corresponding value is to be allowed to vary:

| # fixFlag = 0 if everything is fixed (free=”0”)
| # fixFlag = 1 indicates the flux (free=”1” in <parameter name="Flux">)
| # fixFlag = 2 the position is free (free=”1” in <spatialModel type="PointSource">)
| # fixFlag = 4 the Index Index1 free (free=”1” in <parameter name="Index"> or <parameter name="Index1"> )
| # fixFlag = 8 par2 free (CutoffEnergy PivotEnergy ) variable (free=”1” in <parameter name="CutoffEnergy"> or <parameter name="PivotEnergy">)
| # fixFlag = 16 par3 free (Index2 Curvature) (free=”1” in <parameter name="Index2"> or <parameter name="Curvature">)
| # fixFlag = 32 force position to be variable only in Loop2 (free=”2” in <spatialModel type="PointSource">)
| #The user may combine these values, but the flux will always be allowed to vary if at least one of the other values are.


.. csv-table::
   :header: " ", "flux", "pos(free=1)", "Index/Index1", "cutoff/pivot", "Index2/Curvature", "pos(free=2)"
   :widths: 20, 20, 20, 20, 20, 20, 20

   fixflag, 1, 2, 4, 8, 16, 32

|
|
| #Examples:
| #fixFlag = 0: everything is fixed. This is for known sources which must be included in order to search for other nearby sources.
| #fixFlag = 1: flux variable, position fixed
| #fixFlag = 2: only the position is variable, but AG_multi will let the flux vary too, so this is equivalent to 3.
| #fixFlag = 3: flux and position variable, index fixed
| #fixFlag = 4: index variable (and flux variable)
| #fixFlag = 5: flux and Index variable, position fixed
| #fixFlag = 7: flux, position and Index variable and also
| #fixFlag = 28: Index, par2 and par3 variable (and flux variable)
| #fixFlag = 30: position, Index, par2 and par3 variable (and flux variable)
| #fixFlag = 32: position=2, the rest is fixed

funtype
---------------------

| #0) "PL", "x^(-[index])"
| #1) "PLExpCutoff", "x^(-[index]) * e^(- x / [par2])"
| #2) "PLSuperExpCutoff", "x^(-[index]) * e^(- pow(x / [par2], [par3]))"
| #3) "LogParabola", "( x / [par2] ) ^ ( -( [index] + [par3] * log ( x / [par2] ) ) )"


PointSources
======================

.. code-block:: xml


   <?xml version="1.0" ?>
   <source_library title="source library">

   <!-- Point Sources -->

   #7.45398e-08 92.4102 -10.3946 1.96903 0 2 2AGLJ2202+4214 0 0 0 0 0.5 5 20 10000 0 100

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

   #41.6072e-08 119.677 10.544 1.29082 0 2 2AGLJ0007+7308 0 1 2003.9 0 0.5 5 20 10000 0 100

   <source name="2AGLJ0007+7308" type="PointSource">
   <spectrum type="PLExpCutoff">
      <parameter name="Flux" free="1"  value="41.6072e-08"/>
      <parameter name="Index" free="1" scale="-1.0" value="1.29082" min="0.5" max="5"/>
      <parameter name="CutoffEnergy" free="1" scale="-1.0" value="2003.9" min="20" max="10000"/>
   </spectrum>
   <type="PointSource" location_limit="0" free="0">
      <parameter name="GLON" value="119.677" />
      <parameter name="GLAT" value="10.544" />
   </spatialModel>
   </source>


   #969.539e-08 263.585 -2.84083 1.71345 0 2 2AGLJ0835-4514 0 2 3913.06 1.34774 0.5 5 20 10000 0 100

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


   #35.79e-08 6.16978 -0.067694 3.37991 0 2 2AGLJ1801-2334 0 3 2935.07 0.68236 1 4 500 3000 0.1 3

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

The flux parameter estimates are relevant in the fitting process, as the sources are considered one by one starting with the one with the brightest initial flux value, regardless of the order they are given in the source file.


Diffuse and Isotropic emission model
========================================

.. code-block:: xml

   <!-- Diffuse Sources -->
   <source name="gal" type="DiffuseEmission">
       <spatialModel type="ConstantValue">
       <parameter free="0" name="gal" value="1.0"/>
   </spatialModel>

   </source>
   <source name="iso" type="IsotropicEmission">
       <spatialModel type="ConstantValue">
       <parameter free="0" name="iso" value="7.0"/>
   </spatialModel>
   </source>

   </source_library>
