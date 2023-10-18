AG_multiterative
================

AG_multiterative is an application whose aim is to discover new sources in a region of the sky that may already contain known point sources.
It is based on the same engine as AG_multi, and is equivalent to iteratively calling AG_multi, adding sources one by one and using the previous results as the new input for the next session.
AG_multiterative makes this process automatic and more efficient by preserving across the sessions all the information in common, i.e. maps and calibration files.

AG_multiterative is based on two lists of sources, which we will call the initial and scan list.
The initial source list is a list of already known sources, and the sources in this list will always be included in each AG_multi session.
The scan list contains candidate sources, some of which may be significantly detected if added to the initial list.

The first step runs AG_multi using the initial list, and stores the results.
In the second step, AG_multi is called again several times, each time adding a source from the scan list and determining which of them is the most significant. If that source is significant enough it is added to the initial list, and the process starts over.
The most significant source is the one with the highest TS, and it is considered significant if its TS is greater than a given TS threshold and its distance from a previously known source is greater than a given value..
After each iteration, all the output files whose names contain the iteration number are generated.
This process repeats until a significant source is found, and until a given number of iterations is performed.

The AG_multiterative command line requires the same values as AG_multi, plus the TS threshold, the distance threshold and the maximum number of iterations.
There is also an optional parameter in the command line to globally limit the movement of all the scan sources in the same way as AG_multi does for each single source.

The AG_multiterative .par file thus contains the same parameters for AG_multi, with the same name and type, plus the 5 mentioned above, including the scan list file name.
All the parameters in the order they must appear in the command line are listed below.
The parameters shared with AG_multi are used across all the iterations, and the five new parameters regulate the iteration process


.. list-table:: AG_multi Parameters
   :header-rows: 1

   * - Parameter Type
     - Parameter Name
     - Description
   * - string
     - maplist
     - List of map files
   * - string
     - sarfile
     - SAR file
   * - string
     - edpfile
     - EDP file
   * - string
     - psdfile
     - PSD file
   * - string
     - expcorrfile
     - Exposure correction file
   * - string
     - srcscanlist
     - List of sources to test at each iteration
   * - integer
     - scaniterations
     - Maximum number of iterations
   * - real
     - sqrtstreshold
     - Threshold for considering sources insignificant (sqrt threshold)
   * - real
     - disttreshold
     - Distance threshold for considering two sources as the same source
   * - real
     - fixdistance
     - Maximum distance from initial position for each added source (in degrees)
   * - real
     - ranal
     - Ranal parameter
   * - integer
     - galmode
     - Galmode parameter
   * - integer
     - isomode
     - Isomode parameter
   * - string
     - srclist
     - List of sources
   * - string
     - outfile
     - Output file
   * - real
     - ulcl
     - ULCL parameter
   * - real
     - loccl
     - LOCCL parameter
