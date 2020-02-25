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
