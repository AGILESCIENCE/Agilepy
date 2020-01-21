Configuration file
==================
This section described the configuration file used by Agilepy package. The configuration file has a structure that groups parameters into dictionaries separated by a section name. 

input
**********************
This section defines the input data files. An input data file is an index file, i.e. a file that contains the list of evt files and log files. These files are mandatory and must be specified.

+------------+------------+-----------+----------------------------+
| Option     | Default    | Required  | Description                |
+============+============+===========+============================+
| evtfile    | None       | Yes       |Path to index evt file name |
+------------+------------+-----------+----------------------------+
| logfile    | None       | Yes       |Path to index log file name |
+------------+------------+-----------+----------------------------+
