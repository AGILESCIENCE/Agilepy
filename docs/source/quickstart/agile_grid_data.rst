***************
AGILE-GRID data
***************

Download AGILE-GRID data
******************************

The AGILE-GRID data obtained both in pointing and in spinning mode are publicly available from the ASI/SSDC https://www.asdc.asi.it/mmia/index.php?mission=agilemmia

Prepare index files
**********************

There're two types of data files: events list (EVT) and log data (LOG). They both are compressed fits files. Each file
refers to a specific time interval.

Example:

::

    agql1511240600_1511240730.LOG.gz
    agql1511240730_1511240900.EVT__FM.gz

In order to use Agilepy (or the Agile science tools) a special file, called "index", is needed.
This file is used by Agilepy to know the position of the data files and which file refers to which interval.
Two index files are needed: one for the event data and one for the log data.

Those index files have four column:

  - file name
  - time start of the file in Terrestrial Time (TT)
  - time end of  the file in Terrestial time  (TT)
  - LOG or EVT marker to identify the fole types

Here some examples of LOG and EVT indexes:

::

    head -n 3 /ASDC_PROC3/DATA_ASDCe/INDEX/LOG.log.index
    /AGILE_PROC3/DATA_ASDCe/LOG/ag-107092735_STD0P_GO.LOG.gz 107092735. 107179134.9 LOG
    /AGILE_PROC3/DATA_ASDCe/LOG/ag-107179135_STD0P_GO.LOG.gz 107179135. 107265534.9 LOG
    /AGILE_PROC3/DATA_ASDCe/LOG/ag-107265535_STD0P_GO.LOG.gz 107265535. 107351934.9 LOG


    head -n 3 /ASDC_PROC3/FM3.119_ASDCSTDk/INDEX/EVT.index
    /ASDC_PROC3/FM3.119_ASDCSTDk/EVT/ag0910311200_0911301200_STD1Kal_FM.EVT.gz 184075134.000000 186667134.000000 EVT
    /ASDC_PROC3/FM3.119_ASDCSTDk/EVT/ag0911301200_0912201200_STD1Kal_FM.EVT.gz 186667134.000000 188395134.000000 EVT
    /ASDC_PROC3/FM3.119_ASDCSTDk/EVT/ag0912201200_1001151200_STD1Kal_FM.EVT.gz 188395134.000000 190641534.000000 EVT



Agilepy test data
******************
The Agilepy conda package gets shipped with two subsets of the AGILE data archive for the purpose of unit testing and to show how to run scientific analysis with the tutorial notebooks.

test_dataset_6.0
================
A test data to analyse Vela region. The provided period is MJD 58026.50-58031.50.

The index files are the following:

::

    evtfile="$AGILE/agilepy-test-data/test_dataset_6.0/EVT/EVT.index"
    logfile="$AGILE/agilepy-test-data/test_dataset_6.0/LOG/LOG.index"


test_dataset_agn
================
A test data to analyse the November's 2010 flare of 3C454.3 source. The provided period is MJD 55513.00-55520.00.

The index files are the following:
::

    evtfile="$AGILE/agilepy-test-data/test_dataset_agn/EVT/EVT.index"
    logfile="$AGILE/agilepy-test-data/test_dataset_agn/LOG/LOG.index"