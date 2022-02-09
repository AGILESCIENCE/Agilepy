*****************************
Dataset Download via REST API
*****************************


Overview
********

Version 1.5.0 has implemented the SSDC REST Api in order to get the AGILE dataset from SSDC datacenter. All the required data is downloaded according to tmin and tmax values into a datapath selected in configuration file.
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

Advanced Information
********************

Query files
===========

Agilepy uses text files called "qfiles". These files contain the slots requested by the user, according to SSDC policies. With query file it is possible to avoid multiple downloads for the same dates (useful for slow connections and if there are no data in the selected range days). 


Index files
===========
Index file is created by Indexgen tool immediately after the download. No action is required from the user.


Plotting index files vs query files
===================================

A function to plot the dates from index and query file can be useful to check differences between asked data and real data. Sometimes could happen that data are not available for several reasons (instruments off etc), 
data will not be downloaded but agilepy writes in query files in order to not perform a second request.

AGILE Data Coverage
===================

SSDC uploads AGILE dataset once per month, this means that it could not be possible to select a date close to the present day. 
In this particular case, query files must not be uploaded, because in the future data will be available.
Agilepy gets AGILE data coverage from SSDC and writes it into a file called Agilepy_coverage, when AGDataset starts it checks if last coverage is more than 60 days old from the present date and it updates it if positive.