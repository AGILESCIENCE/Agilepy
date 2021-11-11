Installation
============

Agilepy is available as Anaconda package or into a ready-to-use Docker container (from 1.4.0)

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
  - macOS 12.0.1

In order to use the software you need to activate the virtual environment first:
::

    conda activate <virtualenv_name>

or

::

    source activate <virtualenv_name>

Running jupyter server:
::

    start_agilepy_notebooks.sh


Installation with Docker
^^^^^^^^^^^^^^^^^^^^^^^^

You can pull the image directly from dockerhub using the following command:

::

    docker pull agilescience/agilepy:release-1.4.1

.. note:: If you want to try agilepy’s new features that are not officially released yet, you need to
          pull a develop image available using **agilepy:develop-latest** tag


Using this command you can launch the container and automatically start jupyter notebook.


::

    docker run --rm -it -p 8888:8888 \
    -e DISPLAY=$DISPLAY \
    -v /tmp/.X11-unix:/tmp/.X11-unix:rw \
    -v $PWD/shared_dir:/shared_dir \
    agilescience/agilepy:release-1.4.1 /bin/bash -c \
    "source /opt/anaconda3/etc/profile.d/conda.sh && conda activate agilepydev && \
    jupyter notebook --ip='*' --port=8888 --no-browser --allow-root --notebook-dir="/Agilepy/agilepy/notebooks" --NotebookApp.token='' --NotebookApp.password=''"

shared_dir must be created before launching the command, it is not necessary, but useful for several cases (exporting analysis outside the container, link another dataset etc.)

Jupyter server is at localhost:8888

Agilepy's containers can be found at dockerhub `page <https://hub.docker.com/repository/docker/agilescience/agilepy>`_

Supported platforms:

  - linux-64
  - osx-64
  - win-64(see note)

Tested on:

  - CentOs 7.6
  - Ubuntu 18.04
  - Ubuntu 19.10
  - Ubuntu 20.04
  - macOs 10.14
  - macOs 10.15
  - Windows 10 v2004 (May 2020 Update)

.. note:: It's possible to run Agilepy's container in Windows10(still not supported by Anaconda installation),
          in order to do that, you need to install WSL2 and docker first.

          Check the installation instructions for WSL2 `here <https://docs.microsoft.com/en-us/windows/wsl/install-win10>`_
          and docker `here <https://docs.docker.com/docker-for-windows/wsl/>`_




Uninstalling
^^^^^^^^^^^^
Anaconda
::

    conda env remove --name <virtualenv_name>

Docker
::

    docker rmi agilescience/agilepy:release-1.4.1


Package distribution structure
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
The virtual environment <virtualenv_name> folder is under the "envs" folder within
the root folder of your anaconda installation.

It contains all the dependencies Agilepy requires. Here, there is the "agiletools"
directory, containing AGILE's scientific software.
