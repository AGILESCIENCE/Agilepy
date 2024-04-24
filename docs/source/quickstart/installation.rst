Installation
============

Agilepy is available as a ready-to-use Docker container.

.. warning:: The Anaconda package is no longer mantained. 

.. note:: If you want to try new features that are not officially released yet, you need to install the development environment. 
          Check the `Development <../help/development.html>`_ page for installation instructions.

Installation with Docker
^^^^^^^^^^^^^^^^^^^^^^^^

.. note:: If you don't have Docker: 
          `docs.docker.com/get-docker <https://docs.docker.com/get-docker/>`_

1. Pull the Agilepy Docker image, using the latest tag available at `agilepy/tags <https://hub.docker.com/r/agilescience/agilepy/tags>`_.
The example below use release 1.6.4 (April 2023).

.. code-block::

    export AGILEPY_RELEASE=1.6.4
    docker pull agilescience/agilepy:release-$AGILEPY_RELEASE

.. code-block::

    For Mac users:
    export AGILEPY_RELEASE=1.6.4
    docker pull --platform linux/amd64 agilescience/agilepy:release-$AGILEPY_RELEASE


2. (Skyp if you have a Mac) Download the `bootstrap.sh <https://github.com/AGILESCIENCE/Agilepy/blob/master/agilepy/scripts/bootstrap.sh>`_. 
The script will change the user ID inside the container to match the ID of your local user. If you want to use the same image for multiple user
in a shared machine, pass the `-d` option to duplicate the image instead of overwriting it. In the latter case, the username will be appended to the image name.

.. code-block::

    wget https://raw.githubusercontent.com/AGILESCIENCE/Agilepy/master/agilepy/scripts/bootstrap.sh
    wget https://raw.githubusercontent.com/AGILESCIENCE/Agilepy/master/agilepy/scripts/utilities.sh
    source bootstrap.sh release-$AGILEPY_RELEASE

3. Start the Agilepy container. If you want a shared directory between the host and the container, create a folder in the host machine and use the -v option to mount it in the container as shown below.
It is not necessary to create a shared directory, but it's useful for several cases (exporting analysis outside the container, link another dataset etc.).
Using the command below you can launch the container and automatically start jupyter notebook.

.. code-block::
  
    mkdir shared_dir
    docker run --name agilepy-$AGILEPY_RELEASE -itd --rm -v $(pwd)/shared_dir:/shared_dir -p 9999:8888 -e DISPLAY=$DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix:rw agilescience/agilepy:release-$AGILEPY_RELEASE bash - l
    
    For mac:
    
    docker run --name agilepy-$AGILEPY_RELEASE -itd --rm -v $(pwd)/shared_dir:/shared_dir -p 9999:8888 --platform linux/amd64 -e DISPLAY=$DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix:rw agilescience/agilepy:release-$AGILEPY_RELEASE bash - l    

Enter inside the container to activate jupyter:

.. code-block::

    docker exec -it [docker container id] /bin/bash
    source entrypoint.sh 

    nohup jupyter-lab --ip=“*” --port 8888 --no-browser --autoreload --NotebookApp.token='xxx' --notebook-dir=/shared_dir --allow-root > jupyterlab_start.log 2>&1 &

Check the token from already running jupyter instance 
.. code-block::
    
    docker exec -it agilepy-$AGILEPY_RELEASE bash -l -c "jupyter notebook list"

You can omit the "-c" option to enter the container with a bash shell.

.. note:: Jupyter server will listen at localhost:9999, change the port if you want to use a different one. 
    
.. note:: If Agilepy is running or a remote machine, you need to setup an ssh tunnel to access the jupyter server: `ssh -L 9999:localhost:9999 <user>@<host>`






Supported platforms
^^^^^^^^^^^^^^^^^^^

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

.. note:: It's possible to run Agilepy's container in Windows10, you'll need to install WSL2.

          Check the installation instructions for WSL2 `here <https://docs.microsoft.com/en-us/windows/wsl/install-win10>`_


Manual Installation
^^^^^^^^^^^^^^^^^^^

If the isntallation does not work with the instructions above, it is recommended to install Agilepy and its dependencies from scratch.
The dependencies required by Agilepy are:

  - Root 6.26
  - Cfitsio 4.1
  - Zlib

`AGILE's Science Tools <https://github.com/AGILESCIENCE/AGILE-GRID-ScienceTools-Setup/tree/master>`_ (the correct tag to install can be found in the Docker container recipe)

`Agilepy python dependencies <https://github.com/AGILESCIENCE/Agilepy-recipe/blob/master/recipes/docker/base/requirements.txt>`_


Uninstalling
^^^^^^^^^^^^

Stop the container with:

::

    docker stop agilepy-$AGILEPY_RELEASE

::

    docker rmi agilescience/agilepy:release-$AGILEPY_RELEASE
