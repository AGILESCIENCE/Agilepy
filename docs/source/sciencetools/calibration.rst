********************************************************
IRF and diffuse emission
********************************************************

IRF
========================

The parameters sarfile, edpfile, and psdfile provide the names of the three calibration files. These files are described in detail in other documents, and are provided with the distribution. They are FITS files whose common prefix specifies the filter and event type used and whose suffixes are .sar.gz, .edp.gz and .psd.gz, respectively. Ordinarily, they should not be changed by the user.
The parameter expcorrfile provides a correction factor as a function of off-axis angle for older calibration files. It should not be changed by the user.

Diffuse emission 
========================

Procedure generate conv.sky and disp.conv.sky maps
===================================================

0. Load the environment
------------------------

Enter into the Agilepy Docker container.

.. code-block:: bash

    docker exec -it agilepy-1.7.0 bash -l
	cd $AGILE/scripts/dispconv/

1. Get the repositories
------------------------

It is better to work directly on the official git repositories. To get them:

.. code-block:: bash

    git clone https://github.com/AGILESCIENCE/AG_IRF.git
    git clone https://github.com/AGILESCIENCE/AG_SKY.git
    git clone https://github.com/AGILESCIENCE/AG_SKY_CONV.git
    git clone https://github.com/AGILESCIENCE/AG_SKY_DISPCONV.git

Remember the naming convention for the various projects:

- AG_SKY: `<emin>_<emax>.<sky>.sky.gz`
- AG_SKY_CONV: `<emin>_<emax>.<sky>.S<filter>_<matrix>.conv.sky.gz`
- AG_SKY_DISPCONV: `<emin>_<emax>.<sky>.S<filter>_<matrix>.disp.conv.sky.gz`

NOTE: The substring `<sky>` identifying a new sky map has to be like 'SKY002', for old ones `<sky>` is '0.1' or '0.5' depending on the binning. The following scripts work with both naming conventions.

2. Choose the AG_IRF you want to use
---------------------------------------

The standard procedure is to install your chosen IRF in the standard path $AGILE/model/scientific_analysis/data.

.. code-block:: bash

    cd ~/AG_IRF/<matrix>
    make install

Example: Install the H0025 matrix

.. code-block:: bash

    cd ~/AG_IRF/H0025
    make install

NOTE: If you don't want to install them, you can use the -d option in the following scripts.

3. Work on a new AG_SKY_CONV directory
----------------------------------------

Create a new output directory inside AG_SKY_CONV, with the given naming and run the next script from there.

.. code-block:: bash

    mkdir -p AG_SKY_CONV/<sky>_<matrix>
    cd AG_SKY_CONV/<sky>_<matrix>

Example:

.. code-block:: bash

    mkdir -p ~/AG_SKY_CONV/SKY002_H0025
    cd ~/AG_SKY_CONV/SKY002_H0025

4. Generate conv.sky maps
--------------------------

Command:

.. code-block:: bash

    makeconv.sh [ options ... ] <sky map> ...

- -h: print help
- -m MATRIX: matrix to use
- -f FILTER: filter to use
- -d PATH: model data path
- -i INDEX: the spectral index

Default options: -m H0025 -f FMG -d $AGILE/model/scientific_analysis/data -i 2.0

NOTE: The makeconv scripts generate the conv.sky maps in the current path.

Example: Convolution of SKY002 with the H0025 matrix installed, FMG filter, and 2.0 as the index

.. code-block:: bash

    ~/makeconv.sh -m H0025 -f FMG ~/AG_SKY/SKY002/*.gz

Example2: Same as above, but using the load leveler and reporting tasks completion 

.. code-block:: bash

    ~/makeconv_submit.sh -m H0025 -f FMG -u user@inaf.it ~/AG_SKY/SKY002/*.gz

Grab a coffee, it is going to take a while. Eventually, you can add the generated maps into the AG_SKY_CONV repository:

.. code-block:: bash

    git add *.conv.sky.gz
    git commit

5. Work on a new AG_SKY_DISPCONV directory
--------------------------------------------

Create a new output directory inside AG_SKY_DISPCONV, with the given naming and run the next script from there.

.. code-block:: bash

    mkdir -p AG_SKY_DISPCONV/<sky>_<matrix>
    cd AG_SKY_DISPCONV/<sky>_<matrix>

Example:

.. code-block:: bash

    mkdir -p ~/AG_SKY_DISPCONV/SKY002_H0025
    cd ~/AG_SKY_DISPCONV/SKY002_H0025

6. Copy the convolution map file listing
-----------------------------------------

In order to generate the disp.conv.sky maps, you need the .in file generated with the makeconv.sh script.

.. code-block:: bash

    cp AG_SKY_CONV/<sky>_<matrix>/AG_add_diff.<sky>.S<filter>_<matrix>.in ./

Example:

.. code-block:: bash

    cp ~/AG_SKY_CONV/SKY002_H0025/AG_add_diff.SKY002_SFMG.H0025.in ./

7. Generate disp.conv.sky maps
-------------------------------

Command:

.. code-block:: bash

    makedisp.sh [ options ... ]

This script searches for a file .in in the current directory and generates a .disp.conv.sky for each .conv.sky defined in the .in. To use different energy ranges, see the -r option.

- -h: print help
- -d PATH: model data path
- -n EMIN_STRING: additional user-defined emin energies
- -x EMAX_STRING: additional user-defined emax energies

Default options: -d $AGILE/model/scientific_analysis/data

NOTE: The makedisp script generates the disp.conv.sky maps in the current path.

Example: Default generation with one disp.conv.sky for each conv.sky generated before.

.. code-block:: bash

    ~/makedisp.sh

Example2: Generate additional disp.conv.sky given the user-defined ranges: (100 400) (100 1000) (100 10000) (100 50000) (200 50000) (400 3000) (400 10000) (400 50000) (1000 50000) (3000 50000)

.. code-block:: bash

    ~/makedisp.sh -n "100 100 100 100 200 400 400 400 1000 3000" -x "400 1000 10000 50000 50000 3000 10000 50000 50000 50000"

You can add the generated maps into the AG_SKY_DISPCONV repository:

.. code-block:: bash

    git add *.disp.conv.sky.gz
    git commit

