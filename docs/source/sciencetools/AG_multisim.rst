AG_multisim
===========

.. list-table:: Parameter Table
   :header-rows: 1

   * - Name
     - Type
     - Description
   * - opmode
     - Integer
     - Operation Mode
   * - block
     - Integer
     - Block
   * - nruns
     - Integer
     - Number of runs
   * - seed
     - Integer
     - Seed
   * - sarfile
     - String
     - SAR file name
   * - edpfile
     - String
     - EDP file name
   * - psdfile
     - String
     - PSD file name
   * - maplistsim
     - String
     - Simulation map list
   * - srclistsim
     - String
     - Simulation source list
   * - outfile
     - String
     - Output file name
   * - maplistanalysis
     - String
     - Analysis map list
   * - srclistanalysis
     - String
     - Analysis source list
   * - ranal
     - Real
     - Radius of analysis region
   * - galmode
     - Integer
     - Diffuse emission mode
   * - isomode
     - Integer
     - Isotropic emission mode
   * - ulcl
     - Real
     - Upper limit confidence level
   * - loccl
     - Real
     - Source location contour confidence level


AG_multisim
***********

Introduction
------------

AG_multisim performs Monte Carlo simulations to generate count maps for analysis using the maximum likelihood method. The count maps can be analyzed in real-time and saved to disk. The simulation is based on a list of exposure and gas maps and a set of sources, and for each exposure map, a corresponding count map is generated. These maps can either be concatenated and analyzed as a set of separate maps or grouped, summed up, and analyzed as single maps. The map groups are obtained by considering the first N maps, then again other N maps starting from the second, and so on. In either way, the obtained count maps are analyzed in the same way as AG_multi.

Command Line Options
---------------------

The command line options include:

1. **opmode** (BitMask): Operation mode (see below)
2. **block** (Integer): How to group the maps (see below)
3. **nruns** (Integer): Number of simulations to perform
4. **seed** (Integer): Seed for statistics functions

Calibration Files (required by both simulation and analysis)

5. **sarfile** (FileName): SAR file
6. **edpfile** (FileName): EDP file
7. **psdfile** (FileName): PSD file

Simulation Parameters

8. **maplistsim** (FileName): Map list used for simulation. The counts maps in this file, if present, are ignored, the gas maps are optional, the exposure maps must be specified, and the off-axis angles are ignored. The absolute values of the diffuse coefficients are used. See below the MapList format.
9. **srclistsim** (FileName): Source list for simulation. See below the SourceList format.
10. **outfile** (String): Output file names are based on this value, appending prefixes and suffixes

Analysis Parameters (optional)

11. **maplistanalysis** (FileName): Map list used for analysis. It can be the same as maplistsim. The counts maps in this file, if present, are ignored and replaced with those evaluated in the simulation step. If block is zero, all the lines after the first, if present, would be ignored.
12. **srclistanalysis** (FileName): Source list for analysis. It can be the same as srclistsim.
13. **ranal** (Float): Analysis radius
14. **galmode** (Enumerative): How to treat the galactic diffuse component (see below)
15. **isomode** (Enumerative): How to treat the isotropic diffuse component (see below)
16. **ulcl** (Float): Upper limit confidence level
17. **loccl** (Float): Location contour confidence level

Please refer to the AG_multi User Manual for an explanation of the related options. The other options are explained below.

opmode
------

This program option is a bit mask with the following meaning:

- Bit 0 (Value 1): concise (Generate a single log file rather than a file for each source and each analysis)
- Bit 1 (Value 2): skipanalysis (Do the simulation only, skip any analysis)
- Bit 2 (Value 4): doubleanalysis (Do the analysis in two steps, the second using the sources obtained from the first)
- Bit 3 (Value 8): savemaps (Save to disk all the maps evaluated at runtime and used for the analysis)

Please note the following:
- If bit 1 is off, bits 0 and 2 are ignored.
- If bit 1 is on and bit 3 is off, no output is generated.
- If bit 1 is set, command line options 10 to 17 are optional and ignored if present.

block
-----

The block parameter defines how to group the maps. There are two cases:

- If block is zero, all the maps are concatenated together and analyzed the same way AG_multi normally does. maplistanalysis must have the same number of entries as maplistsim.

- If block is greater than zero, the analysis is performed using the sum of block maps as the count map and the sum of block exposure maps as the exposure map. If there are N maps, then the maps are summed up N-block times, starting from the first, from the 2nd, and so on. In this case, maplistanalysis may contain only one line, and both its counts and exposure maps would be ignored and replaced with the ones evaluated as explained above.

nrun
----

The simulation is repeated nrun times.

seed
----

This unsigned number is used to start the random generator. You can give either zero, meaning the random generator is based on the machine time, or any number you like. If you give zero, AG_multisim prints the number actually used to the screen so that you can repeat the same simulation later on. To perform a different analysis on the same simulation, you need to use the same seed as well as the same calibration files, maps, and sources, which are parameters 5 to 9.

The Two MapLists
----------------

The MapList is a text file whose format is described in the AG_multi User Manual. In the context of AG_multisim, we have two map lists, one for simulation and one for analysis. The counts maps in the simulation MapList are ignored, so they can be set to 'None'. Everything else in the simulation MapList is used to generate the counts maps, one for each line of the MapList. If block is zero, the counts maps will replace those of the analysis MapList, if any. If block is greater than zero, the analysis MapList will be only one line long, and both its counts and exposure maps would be replaced by those generated by the simulation.

Example 1
---------

Both MapLists may look like this:

::

	None map1.exp.fits map1.gas.fits 30 -0.8 -7.2
	None map2.exp.fits map2.gas.fits 30 -0.8 -7.2


The minus sign of the coefficients would be ignored during the simulation, but marks them as variable during the analysis. Two counts maps are generated and inserted in the map list for the analysis. In a case like this example, the same MapList filename can be provided both as simulation and analysis MapList. If block > 0, the second line of the MapLists would be ignored for the analysis, as well as the exposure file name.

Example 2
---------

If block is not zero, the two maps may look like this:

Simulation MapList:

::

	None map1.exp.fits map1.gas.fits 30 0.82 7.2
	None map2.exp.fits map2.gas.fits 40 0.78 6.8


Analysis MapList:

::

	None None map.gas.fits 35 -0.7 -7.0


Two counts maps are generated by the simulation, and their sum replaces the corresponding placeholder in the analysis MapList (the first 'None'). The sum of the corresponding exposure maps will replace the second 'None'. In this case, it is necessary to provide two different MapLists because the angles and the diffuse coefficients differ from one another. The diffuse coefficients of the simulation MapList may or may not have the minus sign, but those of the analysis MapList must have it if we want those coefficients to be variable.

Output File Names
-----------------

If the counts maps are saved to disk, their name is given by:

::

	<iteration><mapProg><outfile>.cts.gz


Where:

- `<iteration>` is a 10-digit number between 1 and nruns
- `<mapProg>` is a 3-digit number between 1 and the number of exposure maps given
- `<outfile>` is the outfile command line option

If block > 0, `<mapProg>` is between 1 and mapCount-block+1. For example, 001 is the sum of the first block counts map, 002 is from the second to block+1, and so on. In this case, the exposure map is also saved with the same name but with a .exp.gz suffix.

If `opmode & concise == concise`, two files are generated at each iteration. Their names are:

::

	<iteration><mapProg><outfile>

and:

::

	<iteration><mapProg><outfile>_<source_name>


Where `<source_name>` is the name of each variable source, and `<mapProg>` is present only if block > 0.

If `opmode & concise == 0`, only one output file is generated for the entire simulation. The first entry of each line is the same as `<iteration>`. In this case, if block > 0, there will be `(mapCount-block+1) * varSourcesCount` lines beginning with the same number (Note: This may need to be changed).
