***********
Development
***********

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

e.g. feature-#61-bayesian-blocks

The **hotfix** branch name takes the following format:

    hotfix-#<card-number>-<release-number>

e.g. hotfix-#57-1.0.0


The release number is the one of the production release from which it originates from.

Practice
--------

Development of a new feature
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If you start from scratch:
::

    git clone --single-branch --branch develop https://github.com/AGILESCIENCE/Agilepy.git

Create a new **feature** branch:
::

    git checkout develop
    git pull origin develop
    git checkout -b feature-#61-bayesian-blocks develop



Development and testing of the new feature.

When you're done, you commit your changes and update the CHANGELOG.md .

::

    vim CHANGELOG
    git commit -m ""

In the meantime it is possible that someone else have pushed his work into the develop branch. In this case
you have to merge the changes in your feature branch.

::

    git pull **origin** develop


Finally you can merge your feature branch back to **develop** branch.

::

    git merge --no-ff feature-#61-bayesian-blocks
    git branch -d feature-#61-bayesian-blocks
    git push origin develop


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

.. image:: static/agilepy_devops.jpg
  :width: 1200
  :alt: Git flow
