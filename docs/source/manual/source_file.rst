.. _sources-file:

************
Sources file
************

The sources can be defined using one of two different formats: xml document and `text file <../sciencetools/mleinput.html#agile-format-text-file>`_.

The flux parameter estimates are relevant in the fitting process, as the sources
are considered one by one, starting with the one with the brightest initial flux
value, regardless of the order they are given in the source file.

Spectral models
========================
A full energy band spectral fit of the data is performed with different spectral model. The spectral representations used in the BUILD25 are PL, exponential cut-off PL, super-exponential cut-off PL, and log parabola (LP). More details are reported in https://arxiv.org/abs/1903.06957

The PL spectral model is used for all sources that are not significantly curved and have low exposure, 

.. image:: ../static/pl.png

where N0 is the prefactor and alpha is the index explicitly evaluated by the MLE method. Our MLE spectral fitting does not explicitly output the prefactor value, which is internally calculated by the numerical procedure.
The majority of the AGILE sources are described by a PL.

The exponential cut-off PL spectral model (PC) is

.. image:: ../static/pc.png

where N0 is the prefactor, α is the index, and Ec is the cut-off energy. The values Ec and α are explicitly provided by the MLE method.

The super exponential cut-off PL spectral model (PS) is

.. image:: ../static/ps.png

where N0 is the prefactor, α is the first index, β the second index, and Ec is the cut-off energy. The parameters α, Ec, and β are explicitly provided by the MLE method.

The LP spectral model is

.. image:: ../static/lp.png

where N0 is the prefactor, Ec is the pivot energy, α is the first index, β the curvature. The parameters α, Ec, and β are explicitly provided by the MLE method.

The selection of curved spectra followed the acceptance criteria described in bulgarelli19. Briefly, a source is considered significantly curved if T Scurved > 16, where T Scurved = 2 × (log L(curved spectrum)−log L(power law), where L is the likelihood function obtained changing only the spectral representation of that source and refitting all free parameters.

Source library format (xml document)
====================================

.. code-block:: xml

  <?xml version="1.0" ?>
  <source_library title="source library">

    <!-- Point Sources -->
    <source name="2AGLJ2202+4214" type="PointSource">
      <spectrum type="PowerLaw">
        <parameter name="flux" free="1"  value="7.45398e-08"/>
        <parameter name="index" free="1" scale="-1.0" value="1.96903" min="0.5" max="5"/>
      </spectrum>
      <spatialModel type="PointSource" location_limit="0">
        <parameter name="pos" value="(92.4102, -10.3946)" free="0" />
      </spatialModel>
    </source>

    <source name="2AGLJ0007+7308" type="PointSource">
      <spectrum type="PLExpCutoff">
         <parameter name="flux" free="1"  value="41.6072e-08"/>
         <parameter name="index" free="1" scale="-1.0" value="1.29082" min="0.5" max="5"/>
         <parameter name="cutoffEnergy" free="1" scale="-1.0" value="2003.9" min="20" max="10000"/>
      </spectrum>
      <spatialModel type="PointSource" location_limit="0">
         <parameter name="pos" value="(119.677, 10.544)" free="0" />
      </spatialModel>
    </source>

    <source name="2AGLJ0835-4514" type="PointSource">
      <spectrum type="PLSuperExpCutoff">
        <parameter name="flux" free="1"  value="969.539e-08"/>
        <parameter name="index1" free="1" scale="-1.0" value="1.71345" min="0.5" max="5"/>
        <parameter name="cutoffEnergy" free="1" value="3913.06" min="20" max="10000"/>
        <parameter name="index2" free="1" value="1.3477" min="0"  max="100"/>
      </spectrum>
      <spatialModel type="PointSource" location_limit="0">
        <parameter name="pos" value="(263.585, -2.84083)" free="0" />
      </spatialModel>
    </source>

    <source name="2AGLJ1801-2334" type="PointSource">
      <spectrum type="LogParabola">
        <parameter name="flux" free="1"  value="35.79e-08"/>
        <parameter name="index" free="1" scale="-1.0" value="3.37991" min="1" max="4"/>
        <parameter name="pivotEnergy" free="1" scale="-1.0" value="2935.07" min="500" max="3000"/>
        <parameter name="curvature" free="1" scale="-1.0" value="0.682363" min="0.1" max="3"/>
      </spectrum>
      <spatialModel type="PointSource" location_limit="0">
        <parameter name="pos" value="(6.16978, -0.0676943)" free="1" />
      </spatialModel>
    </source>

  </source_library>



