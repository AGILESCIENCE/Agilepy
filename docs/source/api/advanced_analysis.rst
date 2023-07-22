*****************
Advanced Analysis
*****************

They need to perform analyses with different configurations and they need to work with a new AGAnalysis object every time. AGAnalysis does not support a "stateless" mode, So they are implemented to create an new AGAnalysis object and perform analysis in a loop.

The code of the analysis is in the ``agilepy/api/advanced`` directory.

Spectra
*******
The analysis involves spectral fitting and light curve generation for a specific source in the dataset. 
Check the command line here

.. literalinclude:: ../../../agilepy/api/advanced/spectra/main.py
   :language: python
   :lines: 15-38