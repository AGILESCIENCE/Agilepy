AG_multiext
===========

.. list-table:: Parameter Table
   :header-rows: 1

   * - Name
     - Type
     - Description
   * - maplist
     - String
     - Maps file name
   * - sarfile
     - String
     - SAR file name
   * - edpfile
     - String
     - EDP file name
   * - psdfile
     - String
     - PSD file name
   * - ranal
     - Real
     - Radius of analysis region
   * - galmode
     - Integer
     - Diffuse emission mode
   * - isomode
     - Integer
     - Isotropic emission mode
   * - srclist
     - String
     - Sources list
   * - extsrclist
     - String
     - Extended sources list
   * - outfile
     - String
     - Output file name
   * - ulcl
     - Real
     - Upper limit confidence level
   * - loccl
     - Real
     - Source location contour confidence level


Here is the provided text translated into English:



Overview
^^^^^^^^
The AG_multiExt application is a twin of AG_multi, sharing its functionalities and most of its software. It also manages extended sources. Extended sources are objects whose shape is described by a map, similar to what happens with diffuse components. During the fitting process, extended sources are added to point sources and treated similarly. AG_multiExt's software is based on a main module that is very similar to AG_multi's, which also accesses the list of extended sources to be processed. The processing relies on the RoiMulti class, the same one used by AG_multi but specially modified to accommodate these sources. The functionalities and interface of RoiMulti remain unchanged if extended sources are not considered, and consequently, AG_multi remains unchanged as well.

User Interface
^^^^^^^^^^^^^^
The list of extended sources is contained in a separate file commonly known as "extfile." AG_multiExt requires the name of this file among its execution parameters. This file can also be omitted, in which case AG_multiExt replicates the behavior of AG_multi exactly. Similar to other parameters, such as ExposureCorrection, specifying that no input file is provided uses the special filename 'None.'

The extended source file has the following format. It is a text file with as many lines as there are extended sources to consider. The data on each line consists of identifiers or numbers separated by spaces. They are in the following order: the source name, the flux, and the spectral index followed by the names of the extended map files. The source's flux can be either fixed or variable during processing. In the latter case, it will be indicated in the file with a negative sign, similar to other similar contexts. The extended maps are convolved maps that must have the same dimensions and the same center, and there must be as many of them as there are sets of maps in the maplist. AG_multiExt considers the center of the extended maps as the center of the extended source. The spectral index is not part of the fitting process, unlike the point sources.

Requirements for Extended Maps
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
The maps describing the extended sources are the result of a process closely related to the sets of maps (counts, exposure, gas) and other data provided as input to AG_multiExt, primarily maplist and psf. The extended maps must meet the following requirements that AG_multiExt can verify:

1. The extended maps are as many as the rows in the maplist.
2. If the extended map contains information about the angle or energy channel, it must be for the same angle and channel as the corresponding map set; otherwise, an error occurs, and the processing terminates. In the absence of such information, only a warning is issued, and the information from the maplist is assumed to be correct.
3. Extended maps in the same row must have the same center.
4. Extended maps in the same column must overlap with the corresponding exposure map in the same way that the exposure overlaps with counts, particularly having the same center.

Note that the combination of requirements 3 and 4 implies that, in practice, there can be only one extended source, even though AG_multiExt can handle an unlimited number of them. The process of generating extended maps requires matching the maplist data with convolved maps that describe the shape of the extended sources. It is recommended that this same process also generates the extlist. The script controlling this process could easily generate the command line that launches AG_multiExt.

Fitting Cycles
^^^^^^^^^^^^^^
In the AG_multi application, there are two fitting cycles for point sources. In each of these cycles, for each fit execution, the extended components are either free to vary or fixed based on the user's decision. The point sources, even if free to vary in some of their parameters, are fixed to the values found according to the context.

In the first cycle, the variable sources, ordered by presumed flux, are introduced into the model one by one. An initial determination of their parameters is made, and during this process, the previously introduced variable sources are allowed to vary only in flux. Sources that do not appear sufficiently significant are removed from the model.

The second cycle is similar to the first and aims to characterize the parameters with greater precision. The sources are re-evaluated one by one, and the others are allowed to vary (only in flux) if they are nearby; otherwise, their flux is fixed.

Extended sources are incorporated into this strategy by taking the top positions in the source list and maintaining the order they had in the extfile. They are introduced one by one into the model before point sources. They do not change their position or spectral index, and only two fits are performed to calculate TS. Like point sources, if the TS value does not exceed the threshold, the sources are removed from the model; otherwise, they are allowed to vary while expanding the model to include other extended and point sources.

Results
^^^^^^^^
At the end of the fitting process, the flux with its associated error and TS of the variable extended sources are determined. This data is included in two output files: the general text file and the HTML file. In both cases, each source occupies a row in a table. The source name is followed by TS, flux, and error. TS and error are zero for fixed sources.

Open Issues
^^^^^^^^^^^

Here is a list of points that have not yet been discussed, some expressed as proposals, at least for the first version:
1. The parameters of diffuse sources to be published remain those related to the first point source, if present, or the last extended source.
2. It does not seem necessary to produce a source file for each of the extended sources.
