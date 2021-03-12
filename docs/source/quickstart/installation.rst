Installation
============

Installation with Anaconda
^^^^^^^^^^^^^^^^^^^^^^^^^^

Agilepy (and its dependencies) can be easily installed using Anaconda. You just
need to decide the name of the virtual environment that will be created by anaconda.
::

    conda config --add channels conda-forge
    conda config --add channels plotly
    conda create -n <virtualenv_name> -c agilescience agilepy

.. note:: If you want to try agilepy's new features that are not officially released yet, 
           a develpoment environment called agilepy-environment is available into Anaconda cloud. 
           It contains all the dependencies unless agilepy, 
           which must be installed by hand cloning the repository.
           Check the installation instructions `here <../help/development.html#install-the-development-environment>`_

Supported platforms:

  - linux-64
  - osx-64

.. note:: An experimental package for IBM POWER architecture(ppc64le) is available on Anaconda cloud. Due to some incompability this package does not contain
          ROOT and AGILE science tools that need to be installed from source. Check the instructions to install AGILE science tools
          `here <https://github.com/AGILESCIENCE/AGILE-GRID-ScienceTools-Setup>`_

Tested on:

  - CentOs 7.6
  - Ubuntu 18.04
  - Ubuntu 19.10
  - Ubuntu 20.04
  - macOs 10.14
  - macOs 10.15

In order to use the software you need to activate the virtual environment first:
::

    conda activate <virtualenv_name>

or

::

    source activate <virtualenv_name>

When you activate the environment the following environment variables will be set:
::

    AGILE=$CONDA_PREFIX/agiletools
    PATH=$AGILE/bin:$AGILE/scripts:$AGILE/scripts/extendesources:$PATH
    LD_LIBRARY_PATH=$CONDA_PREFIX/lib:$CONDA_PREFIX/lib64:$AGILE/lib:$LD_LIBRARY_PATH

Running unit tests:
::

    start_coverage.sh



Uninstalling
^^^^^^^^^^^^
::

    conda env remove --name <virtualenv_name>


Package distribution structure
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
The virtual environment <virtualenv_name> folder is under the "envs" folder within
the root folder of your anaconda installation.

It contains all the dependencies Agilepy requires. Here, there is the "agiletools"
directory, containing AGILE's scientific software.
