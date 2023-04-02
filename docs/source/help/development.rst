***********
Development
***********

Install the development environment with Docker
===============================================

If you want to develop new Agilepy features or try the newest yet unreleased ones,
a development Docker image called agilepy-recipe is availabe on DockerHub.
It contains all the dependencies but Agilepy, which must be manually installed by cloning the repository.

Agilepy's development containers can be found at dockerhub `agilescience/agilepy-recipe <https://hub.docker.com/repository/docker/agilescience/agilepy-recipe>`_ page,
please check it for the latest tag.

Instructions
------------

1. Pull the development Docker image, replace :code:`<LATEST-TAG>` with the
latest tag available at `agilepy-recipe/tags <https://hub.docker.com/r/agilescience/agilepy-recipe/tags>`_.

.. code-block::
    
    export LATEST_TAG=BUILD25b6-v2
    docker pull agilescience/agilepy-recipe:$LATEST_TAG

2. Prepare your workspace by creating a directory :code:`agile`
and store its path in a variable :code:`$PATH_TO_AGILE`.
The :code:`agile` directory is going to be shared between your local file system tree and the developement container's one.

.. code-block::

    mkdir agilepy_development && cd agilepy_development

3. Clone the GitHub Agilepy repository, switch to the development branch you are interested to work on
(e.g. :code:`develop` or any other branch with a given feature).

.. code-block::

    git clone https://github.com/AGILESCIENCE/Agilepy.git && cd Agilepy && git switch develop && cd ..

4. Execute the `boostrap_dev` script to change the user inside the container to your local user.

.. code-block::

    ./Agilepy/agilepy/scripts/bootstrap_dev.sh $LATEST_TAG

5. Create a Docker container with name :code:`agilepy_dev` from the Docker image.
The following command binds port :code:`8888` of the container to port :code:`8090` of your local host,
change it if already occupated.
It shares the :code:`agile` directory between host and container.

.. code-block::

    docker run --rm -t -d -p 8090:8888 --name agilepy_dev -e DISPLAY=$DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix:rw -v $(pwd):/home/flareadvocate/agile agilescience/agilepy-recipe:$LATEST_TAG


6. Enter the container with:

.. code-block::

    docker exec -it agilepy_dev bash -l

7. Inside the container activate the :code:`agilepy` virtual environment,
move to the repository location and install the code in *editable* mode:

.. code-block::

    source $HOME/venv/agilepy/bin/activate
    cd $HOME/agile/Agilepy
    pip install -e .

Now you have the Agilepy's latest development version installed in your environment.
You can also edit it to implement your own agilepy features!

8. The documentation can be built with:

.. code-block::

    source $HOME/venv/agilepy/bin/activate
    cd $HOME/agile/Agilepy/docs
    make html

9. If you need to run a jupyter notebook you can run it in the binded port :code:`8888` from within the container. 
Run the following command and then go to `localhost:8090 <http://localhost:8090>`_:

::

    jupyter notebook --ip='*' --port 8888 --notebook-dir="$HOME/agile/Agilepy/agilepy/notebooks" --NotebookApp.token='' --NotebookApp.password=''

 
You can disable the authentication with :code:`--NotebookApp.token='' --NotebookApp.password=''` but it is not recommended.

::

    jupyter notebook --NotebookApp.token='' --NotebookApp.password='' --ip='*' --port 8888 --notebook-dir="$HOME/agile/Agilepy/agilepy/notebooks"

If you are working in a remote machine, add the :code:`--no-browser` option.

::

    jupyter notebook --no-browser --ip='*' --port 8888 --notebook-dir="$HOME/agile/Agilepy/agilepy/notebooks" --NotebookApp.token='' --NotebookApp.password=''


10. When you need to exit the container just enter :code:`exit`.

11. To stop the container use

.. code-block::

    docker stop agilepy_dev

Docker images
=============
To build the docker image of Agilepy clone the [Agilepy-recipe repository](https://github.com/AGILESCIENCE/Agilepy-recipe)

.. Anaconda
.. --------
.. ::
..     conda config --add channels conda-forge
..     conda config --add channels plotly
..     conda create -n agilepydev -c agilescience agiletools agilepy-dataset
..     conda activate agilepydev
..     git clone https://github.com/AGILESCIENCE/Agilepy.git
..     cd Agilepy && git checkout develop
..     conda env update -f environment.yml
..     python setup.py develop


Git flow
========


Branches
--------

Two main branches:

* **master**: contains only production releases.
* **develop**: contains commits that will be included in the next production release.

Two support branches:

* **feature** branch: each new feature (Trello's card) should be developed in its own feature branch, branching from **develop** and merged back into it. The **feature** branch are not pushed into the remote.
* **hotfix** branch: if an hotfix is needed it should be develop in its own branch, branching from **master** and merged back to it.

.. image:: static/gitflow.jpg
  :width: 600
  :alt: Git flow


Versioning
----------
The **master** branch contains only production releases: when the **develop** branch (or **hotfix** branch) is merged
to **master** a new release tag must be created. Its name follows the `semantic versioning <https://semver.org/>`_.

    x.y.z

Incrementing:

* x version when you make incompatible API changes,
* y version when you add functionality in a backwards compatible manner, and
* z version when you make backwards compatible bug fixes.


Branches names
--------------

The **master** and the **develop** branch have an infinite lifetime, hence their name is fixed.

The **feature** branch takes the following format:

    feature-#<card-number>-<short-description>

e.g. feature-#61-new-cool-feature

The **hotfix** branch name takes the following format:

    hotfix-#<card-number>-<release-number>

e.g. hotfix-#57-1.0.0


The release number is the one of the production release from which it originates from.

Getting started
---------------

Development of a new feature
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Create a new **feature** branch:
::

    git checkout develop 
    git pull origin develop
    git checkout -b feature-#61-new-cool-feature develop



Development and testing of the new feature.

When you have finished, update the CHANGELOG.md and commit your changes.

::

    vim CHANGELOG
    git commit -m "feature-#61-new-cool-feature done"

In the meantime it is possible that someone else have pushed his work into the develop branch. In this case
you have to merge the changes in your feature branch.

::

    git pull **origin** develop


Finally, you can open a merge request to merge your feature branch back to the **develop** branch.


Add configuration parameters
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Let's say we want to add the following configuration section to the AGAnalysis' configuration file.

::
    
    ap:
        radius: 0.25
        timeslot: 3600

* Add the new section to the AGAnalysis.getConfiguration() method.
* Add the type of the configuration parameters within the AGAnalysisConfig.checkOptionsType() method (in the corresponding lists).
* If the parameters need some kind of validation (this is not the case), add a new method in ValidationStrategies and call it within the AGAnalysisConfig.validateConfiguration() (check examples).
* If the parameters need some kind of transformation (this is not the case), add a new method in CompletionStrategies and call it within the AGAnalysisConfig.completeConfiguration() (check examples).
* Add the new configuration section to all the unit test configuration files. 
* Document the new configuration parameters within the manual/configuration_file.rst file. 

Add a new science tool
^^^^^^^^^^^^^^^^^^^^^^

Let's say we want to add a new (c++) science tool: AG_ap.

* Add a new class within the api/ScienceTools.py script. You need to implement some abstract methods.
* You can use the new class as follows: 

:: 

    apTool = AP("AG_ap", self.logger)
    apTool.configureTool(self.config)
    if not apTool.allRequiredOptionsSet(self.config):
        raise ScienceToolInputArgMissing("Some options have not been set.")
    products = apTool.call()



Release of a new version
^^^^^^^^^^^^^^^^^^^^^^^^

Change the version of the software in setup.py. The version increment must be take
in account all the commits of the **develop** branch. You can check the CHANGELOG.md
to facilitate this process. Please, add the new tag within the CHANGELOG.md file.

::

    git checkout master
    git merge --no-ff develop
    git tag -a <new-tag>
    git push origin <new-tag>


DevOps
======

A high level description of agilepy's devops is in the image below: 

.. image:: static/agilepy_devops.jpg
  :width: 1200
  :alt: Git flow

This scheme workflow produces three images:

* **base_image**: It's an image with all the dependencies except Agilepy python library, it's used for developing purposes only by developers. Base image is built after a new commit in agilepy-recipe repository.

* **latest code image**: It's the base_image with Agilepy's develop branch at latest commit, useful for using or testing agilepy's updates not officially released. This image is not supported nor stable and is built by dockerhub after github's testing pipelines are successful.

* **released image**: The base_image with Agilepy's release tag. By default the community shall be download this image. It's built when a new tag is created.

