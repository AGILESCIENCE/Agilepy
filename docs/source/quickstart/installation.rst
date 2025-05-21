Installation
============

Agilepy is available as a ready-to-use Docker container.

.. warning:: The Anaconda package is no longer maintained. 

.. note:: If you want to try new features that are not officially released yet, you need to install the development environment. 
          Check the `Development <../help/development.html>`_ page for installation instructions.

Installation with Docker
^^^^^^^^^^^^^^^^^^^^^^^^

.. note:: Docker is an open platform for developing, shipping, and running applications.
          Working with Docker is similar to working in a compact and virtual machine where only a software and its dependencies are already installed, with no installation issues or package conflicts.
          It is faster and lighter than virtual machines, and ensure reproducibility of the environment.
          Docker distinguishes between Images (a recipe to create a container) and Containers (a running instance of an image).
          `Get Docker <https://docs.docker.com/get-docker/>`_

1. **Pull** the Agilepy Docker image, using the latest tag (i.e., version) available at `agilepy/tags <https://hub.docker.com/r/agilescience/agilepy/tags>`_.
The command below will download the image from Docker Hub and store it locally.

    .. note:: In this guide, we refer to the image tag with the ``AGILEPY_RELEASE`` variable, defined as
            
            .. code-block::

                export AGILEPY_RELEASE=release-1.6.5

            You can find the available tags at `agilepy/tags <https://hub.docker.com/r/agilescience/agilepy/tags>`_.
            If you are using a different tag, please replace ``AGILEPY_RELEASE`` with the actual tag you want to use.


    * For Linux users:

        .. code-block::

            docker pull agilescience/agilepy:$AGILEPY_RELEASE

    * For Mac users:

        .. code-block::

            docker pull --platform linux/amd64 agilescience/agilepy:$AGILEPY_RELEASE

    * Using the Docker Desktop GUI:
        * Open Docker Desktop.
        * In the left sidebar, click on Docker Hub and search for ``agilescience/agilepy``.
        * Select the tag you want to download (e.g., ``release-1.6.5``), click on pull.
        * The image will be available in the Images tab of the left sidebar.




2. **Bootstrap.** The Agilepy image contains a ``flareadvocate`` user with a pre-defined user ID.
If you want to run Agilepy with your own user ID, you need to change the user ID inside the image to match the ID of your local user.
This is important to avoid permission issues when writing files in shared directories, and is especially important in shared machines with multiple users.
To perform the bootstrap, you can use the `bootstrap.sh <https://github.com/AGILESCIENCE/Agilepy/blob/master/agilepy/scripts/bootstrap.sh>`_ script provided in the Agilepy repository.

    * [*Skip if you have a Mac*] Download and execute the `bootstrap.sh <https://github.com/AGILESCIENCE/Agilepy/blob/master/agilepy/scripts/bootstrap.sh>`_. The script will create a new image, named ``agilescience/agilepy:${AGILEPY_RELEASE}_${USER}`` with the user ID inside the container matching your local user (``$USER``). If you want to use the same image for multiple users in a shared machine, pass the ``-d`` option to duplicate the image instead of overwriting it. In the latter case, the username will be appended to the image name.
    

        .. code-block::

            wget https://raw.githubusercontent.com/AGILESCIENCE/Agilepy/master/agilepy/scripts/bootstrap.sh
            chmod +x bootstrap.sh
            ./bootstrap.sh $AGILEPY_RELEASE



Execution with Docker
^^^^^^^^^^^^^^^^^^^^^

**Run** the Agilepy container using the ``docker run`` command and appropriate options.

.. note:: Mac users need to include the ``--platform linux/amd64`` option to run the container. 



The appropriate options to run a container depend on the task you want to perform and the operating system.
Full documentation is available at `docker run <https://docs.docker.com/engine/reference/commandline/run/>`_.
We provide a few examples below, but you can customize the command to suit your needs.
    
    1. **One-time interactive container + Jupyter Server**
    Run a one-time container with a jupyter notebook server and a bash shell.

    The following command assumes you have created a directory called ``shared_dir`` in the current working directory.
    Please replace with the actual path of the directory you want to use to share data between the host and the container.
    The following command assumes you have created a bootstrap image with the name ``agilescience/agilepy:${AGILEPY_RELEASE}_${USER}``.
    Please replace with the actual name of the image you want to use.

    .. code-block::

        export CONTAINER_NAME=my_agilepy_container
        docker run --rm -it --name $CONTAINER_NAME --network host -e DISPLAY=$DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix:rw -v $(pwd)/shared_dir:/shared_dir agilescience/agilepy:${AGILEPY_RELEASE}_${USER} bash -l

    You can exit the container with ``exit``.
    The container will be stopped (destroyed) when it exits.

    2. **One-time interactive container**
    This is similar to the previous example, but without the jupyter server.

    .. code-block::

        export CONTAINER_NAME=my_agilepy_container
        docker run --rm -it --name $CONTAINER_NAME --network host -e DISPLAY=$DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix:rw -v $(pwd)/shared_dir:/shared_dir --entrypoint bash agilescience/agilepy:${AGILEPY_RELEASE}_${USER} -l


    3. **Execute a command in a non-interactive mode**
    This is useful to execute a command or a script in a non-interactive mode.
    The following example will run a container and print the path of the Agilepy installation.
    When the command is executed, the container will stop.

    .. code-block::

        export CONTAINER_NAME=my_agilepy_container
        docker run --rm --name $CONTAINER_NAME --network host -v $(pwd)/shared_dir:/shared_dir --entrypoint bash agilescience/agilepy:${AGILEPY_RELEASE}_${USER} -c "python3 -c 'import agilepy as _; print(_.__path__[0])'"



    4. **Persistent container active on background**
    Run a container in the background which stays active.

    .. code-block::
    
        export CONTAINER_NAME=my_agilepy_container
        docker run --rm -t -d --name $CONTAINER_NAME --network host -e DISPLAY=$DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix:rw -v $(pwd)/shared_dir:/shared_dir agilescience/agilepy:${AGILEPY_RELEASE}_${USER}



    Enter the container with a bash shell:

    .. code-block::

        docker exec -it $CONTAINER_NAME bash -l



    You can run any command inside the container, including a jupyter notebook server:


    .. code-block::
    
        jupyter notebook --ip="*" --port=8888 --no-browser --allow-root --NotebookApp.token='yyy' --notebook-dir=/shared_dir

    You can exit the container with 
    
    .. code-block::
    
        exit
    

    Once exited, stop the container with:

    .. code-block::

        docker stop $CONTAINER_NAME


    



Tips for using Docker and Jupyter Server
"""""""""
The general structure of a ``docker run`` command is:

    .. code-block::

        docker run [OPTIONS] [IMAGE_NAME] [COMMAND] [ARG...]

    where:
    
    - **OPTIONS** are the options you want to use to run the container. Common options include:
        - ``--name``: a label to name the container.
        - ``-v``: mount a volume, e.g. a shared directory to transfer data between the host and the container. Agilepy has a ``/shared_dir`` directory we suggest to use for this purpose. It is not necessary to create a shared directory, but it's useful for several cases (exporting analysis outside the container, link another dataset etc.).
        - ``-e``: set an environment variable inside the container.
        - ``-p``: publish a port from the container to the host, e.g. for a jupyter server.
        - ``--network host``: share all ports between container and host.
        - ``-it``: run the container in interactive mode with a terminal.
        - ``-d``: run the container in detached mode (in the background).
        - ``--rm``: remove the container when it exits.
        - ``--entrypoint``: override the default entrypoint script of the image.
        - ``--platform``: specify the platform to use (e.g., ``linux/amd64`` for Mac users).
    - **IMAGE** is the name of the image you want to run, typically ``agilescience/agilepy:release-1.6.5`` (or ``agilescience/agilepy:release-1.6.5_${USER}`` if you performed the bootstrap).
    - **COMMAND** is the command you want to run inside the container (e.g., ``bash``, ``jupyter notebook``, etc.).
    - **ARG** are the arguments for the command you want to run.


When running a Jupyter Server, you can check the token of a running jupyter instance already running in a container with:

.. code-block::

    docker exec -it $CONTAINER_NAME bash -l -c "jupyter notebook list"

You can omit the ``-c`` option to enter the container with a bash shell.

.. note:: Jupyter server will listen at ``localhost:9999``, change the port if you want to use a different one. 




.. note:: If Agilepy is running or a remote machine, you need to setup an ssh tunnel to access the jupyter server: ``ssh -L 9999:localhost:9999 <user>@<host>``






Supported platforms
^^^^^^^^^^^^^^^^^^^

  - linux-64
  - osx-64
  - win-64(see note)

Tested on:

  - CentOs 7.6
  - Ubuntu 22.04
  - Ubuntu 24.04
  - macOs 15.4
  - Windows 10 v2004 (May 2020 Update)

.. note:: It's possible to run Agilepy's container in Windows10, you'll need to install WSL2.

          Check the installation instructions for WSL2 `here <https://docs.microsoft.com/en-us/windows/wsl/install-win10>`_


Manual Installation
^^^^^^^^^^^^^^^^^^^

If the installation does not work with the instructions above, it is recommended to install Agilepy and its dependencies from scratch.
The dependencies required by Agilepy are:

  - Root 6.26
  - Cfitsio 4.1
  - Zlib
  - `AGILE's Science Tools <https://github.com/AGILESCIENCE/AGILE-GRID-ScienceTools-Setup/tree/master>`_ (the correct tag to install can be found in the Docker container recipe)
  - `Agilepy python dependencies <https://github.com/AGILESCIENCE/Agilepy-recipe/blob/master/recipes/docker/base/requirements.txt>`_


Uninstalling
^^^^^^^^^^^^

Stop a running container with:

.. code-block::

    docker stop $CONTAINER_NAME

Remove the ``agilepy`` image with:

.. code-block::

    docker rmi agilescience/agilepy:$AGILEPY_RELEASE
