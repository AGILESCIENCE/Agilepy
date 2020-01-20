Installing Agilepy
==================

Agilepy (and its dependencies) can be easily installed using Anaconda. You just
need to decide the name of the virtual environment that will be created by anaconda.
::

    conda config --add channels conda-forge
    conda install -n <virtualenv_name> -c agilescience agilepy

Supported platforms:

  - linux-64
  - osx-64


In order to use the software you need to activate the virtual environment first:
::

    conda activate <virtualenv_name>

When you activate the environment the following environment variables will be set:

    - AGILE=$CONDA_PREFIX/agiletools
    - PFILES=$PFILES:$AGILE/share
    - ROOTSYS=$CONDA_PREFIX
    - CFITSIO=$CONDA_PREFIX
    - GSL=$CONDA_PREFIX
    - PATH=$AGILE/bin:$AGILE/scripts:$AGILE/scripts/extendesources:$PATH
    - LD_LIBRARY_PATH=$CONDA_PREFIX/lib:$CONDA_PREFIX/lib64:$AGILE/lib:$LD_LIBRARY_PATH

Running tests:
::

    - start_agilepy_tests

MORE ON THE PACKAGE DISTRIBUTION.

  - download the AGILEDATA from agilepy-extra
