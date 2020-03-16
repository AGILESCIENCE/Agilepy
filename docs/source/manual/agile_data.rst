************
 Agile data
************

Data structure
==============
There're two types of data files: events and log data. They both are compressed fits files. Each file
refers to a specific time interval.

Example:

::

    agql1511240600_1511240730.LOG.gz
    agql1511240730_1511240900.EVT__FM.gz

In order to use Agilepy (or the Agile science tools) a special file, called "index", is needed.
This file is used by Agilepy to know the position of the data files and which file refers to which interval.
Two index files are needed: one for the event data and one for the log data.

Those index files are automatically provided to you by the Agilepy distribution but if you want to customize them,
here's their structure:

Example:

::

    head -n 3 /ASDC_PROC3/DATA_ASDCe/INDEX/LOG.log.index
    /AGILE_PROC3/DATA_ASDCe/LOG/ag-107092735_STD0P_GO.LOG.gz 107092735. 107179134.9 LOG
    /AGILE_PROC3/DATA_ASDCe/LOG/ag-107179135_STD0P_GO.LOG.gz 107179135. 107265534.9 LOG
    /AGILE_PROC3/DATA_ASDCe/LOG/ag-107265535_STD0P_GO.LOG.gz 107265535. 107351934.9 LOG


    head -n 3 /ASDC_PROC3/FM3.119_ASDCSTDk/INDEX/EVT.index
    /ASDC_PROC3/FM3.119_ASDCSTDk/EVT/ag0910311200_0911301200_STD1Kal_FM.EVT.gz 184075134.000000 186667134.000000 EVT
    /ASDC_PROC3/FM3.119_ASDCSTDk/EVT/ag0911301200_0912201200_STD1Kal_FM.EVT.gz 186667134.000000 188395134.000000 EVT
    /ASDC_PROC3/FM3.119_ASDCSTDk/EVT/ag0912201200_1001151200_STD1Kal_FM.EVT.gz 188395134.000000 190641534.000000 EVT



How to get the data
===================
TODO..


Agilepy test data
=================
The Agilepy conda package gets shipped with a little subset of the AGILE data archive for the purpose of unit testing and executing the tutorial notebooks.

The data has been generated using the following commands:

::
    ./AG_genselectedevtlist ./agilepy_test_dataset_55513_55520.evt /AGILE_PROC3/FM3.119_ASDCSTDk/INDEX/EVT.index None 40 0.2 86.11 -38.18 180 80 6 5 ARC 216691200 217296000 100 10000 0.0 60.0
    ./AG_genselectedloglist ./agilepy_test_dataset_55513_55520.log /AGILE_PROC3/DATA_ASDC2/INDEX/LOG.log.index /data01/AGILE-containers/tmp_download/AGILE-GRID-CAT2-Setup/AGILE-GRID-ScienceTools-Setup/AG_IRF/H0025/AG_GRID_G0017_SFMG_H0025.sar.gz /data01/AGILE-containers/tmp_download/AGILE-GRID-CAT2-Setup/AGILE-GRID-ScienceTools-Setup/AG_IRF/H0025/AG_GRID_G0017_SFMG_H0025.edp.gz None None 40 0.2 86.11 -38.18 180 80 0.5 360 5.0 6 ARC 5.0 160 2.1 456361778 456537945 100 10000 0.0 60.0

The index files are located here:

  * $AGILE/agilepy-test-data/evt_index/agilepy_test_dataset_EVT.index
  * $AGILE/agilepy-test-data/log_index/agilepy_test_dataset_LOG.log.index
