************************
Download AGILE-GRID data
************************

The AGILE-GRID data can be downloaded in two ways: automated by Agilepy or manually.

Automated download using SSDC REST Api
*********************************************************

The AGILE-GRID data is download automatically by agilepy. 

Version 1.5.0 has implemented the SSDC REST Api in order to get the AGILE dataset from SSDC datacenter. All the required data is downloaded according to tmin and tmax values selected in configuration file.
This feature works when generatesmaps method is called.


Pre-requisites:
 - Internet connection (> 200 Mb/s)

SSDC Data policy:
 - EVT files contain 15 days of data (2 files per month) 
 - LOG files contain 1 day of data

Eg for getting data from 10/10/2018 to 05/11/2018 it returns:
 - 3 EVT files (30/09-15/10, 15/10-31/10, 31/10-15/11)
 - 26 LOG files, one file for each day

Two query files are created to keep track of the query history and to implement the policy above. Before calling Rest api, Agilepy checks if the dates selected are in query files, if True download is not performed.
If False Agilepy downloads the data in /tmp/ folder, it unpacks them into the selected datapath and it automatically calls indexgen tool for generating index files. Finally, it updates query files.

Example
========

::

	AGAnalysis.getConfiguration(
		confFilePath = confFilePath,
		evtfile=None,
		logfile=None,
		userName = "username",
		sourceName = "PKS1510-089",
		tmin = 54891,
		tmax = 54921,
		timetype = "MJD",
		glon = 351.29,
		glat = 40.13,
		outputDir = "$HOME/agilepy_analysis",
		verboselvl = 0,
		userestapi=True,
		datapath="$HOME/agile_dataset"
	)

Advanced Information
========================

Query files
^^^^^^^^^^^^

Agilepy uses text files called "qfiles". These files contain the slots requested by the user, according to SSDC policies. With query file it is possible to avoid multiple downloads for the same dates (useful for slow connections and if there are no data in the selected range days). 


Index files
^^^^^^^^^^^^
Index file is created by Indexgen tool immediately after the download. No action is required from the user.


Plotting index files vs query files
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

A function to plot the dates from index and query file can be useful to check differences between asked data and real data. Sometimes could happen that data are not available for several reasons (instruments off etc), 
data will not be downloaded but agilepy writes in query files in order to not perform a second request.

AGILE Data Coverage
^^^^^^^^^^^^^^^^^^^^^^^^

SSDC uploads AGILE dataset once per month, this means that it could not be possible to select a date close to the present day. 
In this particular case, query files must not be uploaded, because in the future data will be available.
Agilepy gets AGILE data coverage from SSDC and writes it into a file called Agilepy_coverage, when AGDataset starts it checks if last coverage is more than 60 days old from the present date and it updates it if positive.

Manual download
**********************************

The AGILE-GRID data obtained both in pointing and in spinning mode are publicly available and can be download manually from the ASI/SSDC https://www.asdc.asi.it/mmia/index.php?mission=agilemmia

Prepare index files
===================

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


You can use the AG_indexgen tool to generate the .index file:

::

    AG_indexgen <path to data> <type> <output file>

Where <type> can be EVT or LOG.

Example:

::

    AG_indexgen /AGILE_PROC3/FM3.119_ASDC2/EVT EVT /home/user/data.index



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