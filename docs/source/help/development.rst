Development (before 1.0.0)
==========================

Clone the following repository:
::

    cd
    git clone https://github.com/AGILESCIENCE/Agilepy/
    cd Agilepy


Export the following environment variable:
::

    export PYTHONPATH=.


Activate the anaconda virtual environment:
::

    conda activate <env_name>


Update the source, then commit and push.

If you want your modification to be included into the anaconda package you need to

  - delete the remote v1.0.0 tag
  - delete the local v1.0.0 tag
  - create a new v1.0.0 tag, pointing to the last commit
  - push the commit and the tag on the master branch

::

    git push --delete origin v1.0.0
    git tag -d v1.0.0
    git tag v1.0.0 $(git log --format="%H" -n 1)
    git push origin master --tags
