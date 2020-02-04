# DESCRIPTION
#       Agilepy software
#
# NOTICE
#      Any information contained in this software
#      is property of the AGILE TEAM and is strictly
#      private and confidential.
#      Copyright (C) 2005-2020 AGILE Team.
#          Baroncelli Leonardo <leonardo.baroncelli@inaf.it>
#          Addis Antonio <antonio.addis@inaf.it>
#          Bulgarelli Andrea <andrea.bulgarelli@inaf.it>
#          Parmiggiani Nicolò <nicolo.parmiggiani@inaf.it>
#      All rights reserved.

#This program is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.

#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.

#You should have received a copy of the GNU General Public License
#along with this program.  If not, see <https://www.gnu.org/licenses/>.

import os
from os.path import join, exists

from agilepy.config.AgilepyConfig import AgilepyConfig

from agilepy.api.SourcesLibrary import SourcesLibrary
from agilepy.api.ScienceTools import ctsMapGenerator, expMapGenerator, gasMapGenerator, intMapGenerator, multi

from agilepy.utils.AstroUtils import AstroUtils
from agilepy.utils.Parameters import Parameters
from agilepy.utils.AgilepyLogger import agilepyLogger
from agilepy.utils.CustomExceptions import AGILENotFoundError, \
                                           PFILESNotFoundError, \
                                           ScienceToolInputArgMissing, \
                                           MaplistIsNone

class AGAnalysis:
    """This class contains the high-level API methods you can use to run scientific analysis.

    This class is a wrapper around the ``SourcesLibrary``, ``ScienceTools`` and ``AgilepyConfig`` classes and implements
    high level functionality.

    This class requires you to setup a ``yaml configuration file`` to specify the software's behaviour
    and a ``xml descriptor file`` that contains a list of all the sources you want to consider.

    Class attributes:

    Attributes:
        config (:obj:`AgilepyConfig`): it is used to read/update configuration values.
        logger (:obj:`AgilepyLogger`): it is used to log messages with different importance levels.
        sourcesLibrary (:obj:`SourcesLibrary`): it contains the list of the sources and several useful methods.

    """

    def __init__(self, configurationFilePath, sourcesFilePath):
        """AGAnalysis constructor.

        Args:
            configurationFilePath (str): the relative or absolute path to the yaml configuration file.
            sourcesFilePath (str): the relative or absolute path to the xml sources descriptor file.

        Raises:
            FileExistsError: if the output directory already exists.
            AGILENotFoundError: if the AGILE environment variable is not set.
            PFILESNotFoundError: if the PFILES environment variable is not set.

        Example:
            >>> from agilepy.api import AGAnalysis
            >>> aganalysis = AGAnalysis('agconfig.yaml', 'sources.xml')

        """

        self.config = AgilepyConfig()

        self.config.loadConfigurations(configurationFilePath, validate=True)

        self.outdir = self.config.getConf("output","outdir")

        if exists(self.outdir):
            raise FileExistsError("The output directory %s already exists! Please, delete it or specify another output directory!"%(self.outdir))

        self.logger = agilepyLogger

        self.logger.initialize(self.outdir, self.config.getConf("output","logfilenameprefix"), self.config.getConf("output","verboselvl"))

        self.sourcesLibrary = SourcesLibrary()

        self.sourcesLibrary.loadSources(sourcesFilePath)

        if "AGILE" not in os.environ:
            raise AGILENotFoundError("$AGILE is not set.")

        if "PFILES" not in os.environ:
            raise PFILESNotFoundError("$PFILES is not set.")


    def setOptions(self, **kwargs):
        """It updates configuration options specifying one or more key=value pairs at once.

        Args:
            \*\*kwargs: key-values pairs, separated by a comma.

        Returns:
            None

        Raises:
            ConfigFileOptionTypeError: if the type of the option value is not wrong.
            CannotSetHiddenOptionError: if the option is hidden.
            OptionNotFoundInConfigFileError: if the option is not found.

        Note:
            The ``config`` attribute is initialized by reading the corresponding
            yaml configuration file, loading its contents in memory. Updating the values
            held by this object will not affect the original values written on disk.

        Example:

            >>> aganalysis.setOptions(mapsize=60, binsize=0.5)
            True

        """
        return self.config.setOptions(**kwargs)


    def resetOptions(self):
        """It resets the configuration options to their original values.

        Returns:
            None, newline=True.
        """
        return self.config.reset()


    def printOptions(self, section=None):
        """It prints the configuration options in the console.

        Args:
            section (str): you can specify a configuration file section to be printed out.

        Returns:
            None
        """
        return self.config.printOptions(section)


    def generateMaps(self):
        """It generates (one or more) counts, exposure, gas and int maps and a ``maplist file``.

        The method's behaviour varies according to several configuration options (see docs :ref:`configuration-file`).

        Note:
            It resets the configuration options to their original values before exiting.

        Returns:
            The absolute path to the generated ``maplist file``.

        Raises:
            ScienceToolInputArgMissing: if not all the required configuration options have been set.

        Example:
            >>> aganalysis.generateMaps()
            /home/rt/agilepy/output/testcase.maplist4

        """
        fovbinnumber = self.config.getOptionValue("fovbinnumber")
        energybins = self.config.getOptionValue("energybins")

        initialFovmin = self.config.getOptionValue("fovradmin")
        initialFovmax = self.config.getOptionValue("fovradmax")

        initialFileNamePrefix = self.config.getOptionValue("filenameprefix")
        outdir = self.config.getOptionValue("outdir")

        mapListFileContent = []
        maplistFilePath = join(outdir, initialFileNamePrefix+".maplist4")

        for stepi in range(0, fovbinnumber):

            if fovbinnumber == 1:
                bincenter = 30
                fovmin = initialFovmin
                fovmax = initialFovmax
            else:
                bincenter, fovmin, fovmax = AGAnalysis._updateFovMinMaxValues(fovbinnumber, initialFovmin, initialFovmax, stepi+1)


            for bgCoeffIdx, stepe in enumerate(energybins):

                if Parameters.checkEnergyBin(stepe):

                    emin = stepe[0]
                    emax = stepe[1]

                    skymapL = Parameters.getSkyMap(emin, emax)
                    skymapH = Parameters.getSkyMap(emin, emax)
                    fileNamePrefix = Parameters.getMapNamePrefix(emin, emax, stepi+1)

                    self.logger.debug(self, "Map generation => fovradmin %s fovradmax %s bincenter %s emin %s emax %s fileNamePrefix %s skymapL %s skymapH %s", \
                                       fovmin,fovmax,bincenter,emin,emax,fileNamePrefix,skymapL,skymapH)

                    self.config.setOptions(filenameprefix=initialFileNamePrefix+"_"+fileNamePrefix)
                    self.config.setOptions(fovradmin=fovmin, fovradmax=fovmax)
                    self.config.addOptions("selection", emin=emin, emax=emax)
                    self.config.addOptions("maps", skymapL=skymapL, skymapH=skymapH)

                    ctsMapGenerator.configure(self.config)
                    expMapGenerator.configure(self.config)
                    gasMapGenerator.configure(self.config)
                    intMapGenerator.configure(self.config)

                    self.config.addOptions("maps", expmap=expMapGenerator.outfilePath, ctsmap=ctsMapGenerator.outfilePath)

                    if not ctsMapGenerator.allRequiredOptionsSet(self.config) or \
                       not expMapGenerator.allRequiredOptionsSet(self.config) or \
                       not gasMapGenerator.allRequiredOptionsSet(self.config) or \
                       not intMapGenerator.allRequiredOptionsSet(self.config):

                        raise ScienceToolInputArgMissing("Some options have not been set.")

                    f1 = ctsMapGenerator.call()
                    self.logger.info(self, "Science tool ctsMapGenerator produced %s", f1)

                    f2 = expMapGenerator.call()
                    self.logger.info(self, "Science tool expMapGenerator produced %s", f2)

                    f3 = gasMapGenerator.call()
                    self.logger.info(self, "Science tool gasMapGenerator produced %s", f3)

                    f4 = intMapGenerator.call()
                    self.logger.info(self, "Science tool intMapGenerator produced %s", f4)


                    mapListFileContent.append( ctsMapGenerator.outfilePath + " " + \
                                               expMapGenerator.outfilePath + " " + \
                                               gasMapGenerator.outfilePath + " " + \
                                               str(bincenter) + " " + \
                                               str(self.config.getOptionValue("galcoeff")[bgCoeffIdx]) + " " + \
                                               str(self.config.getOptionValue("isocoeff")[bgCoeffIdx]) )

                else:

                    self.logger.warning(self,"Energy bin [%s, %s] is not supported. Map generation skipped.", stepe[0], stepe[1])


        with open(maplistFilePath,"a") as mlf:
            for line in mapListFileContent:
                mlf.write(line+"\n")

        self.logger.info(self, "Maplist file created in %s", maplistFilePath)

        self.config.reset()


        return maplistFilePath


    def mle(self, maplistFilePath):
        """It performs a maximum likelihood estimation analysis on every source withing the ``sourceLibrary``, producing one output file per source.

        The method's behaviour varies according to several configuration options (see docs :ref:`configuration-file`).

        The outputfiles have the ``.source`` extension.

        The method's behaviour varies according to several configuration options (see docs here).

        Note:
            It resets the configuration options to their original values before exiting.

        Args:
            maplistFilePath (str): the absolute path to the ``maplist file`` generated by ``generateMaps()``.

        Returns:
            A list of absolute paths to the output ``.source`` files.

        Raises:
            MaplistIsNone: is the input argument is None.

        Example:
            >>> maplistFilePath = aganalysis.generateMaps()
            >>> aganalysis.mle(maplistFilePath)
            [/home/rt/agilepy/output/testcase0001_2AGLJ2021+4029.source /home/rt/agilepy/output/testcase0001_2AGLJ2021+3654.source]

        """
        if not maplistFilePath:
            raise MaplistIsNone("The 'maplistFilePath' input argument is None. Please, pass a valid path to a maplist \
                                 file as argument (perhaps you want to call generateMaps() first). ")

        sourceListFilename = "sourceLibrary"+(str(multi.callCounter).zfill(5))
        sourceListAgileFormatFilePath = self.sourcesLibrary.writeToFile(outfileNamePrefix=join(self.outdir, sourceListFilename), fileformat="AG")

        self.config.addOptions("selection", maplist=maplistFilePath, sourcelist=sourceListAgileFormatFilePath)

        multisources = self.sourcesLibrary.getSourcesNames()
        self.config.addOptions("selection", multisources=multisources)


        multi.configure(self.config)

        sourceFiles = multi.call()

        if len(sourceFiles) == 0:
            self.logger.warning(self, "The number of .source files is 0.")

        self.logger.info(self,"AG_multi produced: %s", sourceFiles)

        for sourceFile in sourceFiles:

            multiOutputData = self.sourcesLibrary.parseSourceFile(sourceFile)

            self.sourcesLibrary.updateMulti(multiOutputData)


        self.config.reset()

        return sourceFiles

    def selectSources(self, selection):
        """It returns the sources matching the selection criteria from the ``sourcesLibrary``.

        The sources can be selected with the ``selection`` argument, supporting either ``lambda functions`` and
        ``boolean expression strings``.

        The selection criteria can be expressed using the following ``Source`` class's parameters:

        - Name: the unique code identifying the source.
        - Dist: the distance of the source from the center of the maps.
        - Flux: the flux value.
        - SqrtTS: the radix square of the ts.

        Warning:

            The SqrtTS parameter is available only after the maximum likelihood estimation analysis.

        Args:
            selection (lambda or str): a lambda function or a boolean expression string specifying the selection criteria.

        Returns:
            List of sources.
        """
        return self.sourcesLibrary.selectSources(selection)

    def freeSources(self, selection, parameterName, free):
        """It can set to True or False a parameter's ``free`` attribute of one or more source.

        Example of source model:
        ::

            <source name="2AGLJ2021+4029" type="PointSource">
                <spectrum type="PLExpCutoff">
                  <parameter name="Flux" free="1"  value="119.3e-08"/>
                  <parameter name="Index" free="0" scale="-1.0" value="1.75" min="0.5" max="5"/>
                  <parameter name="CutoffEnergy" free="0" value="3307.63" min="20" max="10000"/>
                </spectrum>
                <spatialModel type="PointSource" location_limit="0" free="0">
                  <parameter name="GLON" value="78.2375" />
                  <parameter name="GLAT" value="2.12298" />
                </spatialModel>
            </source>


        The supported ``parameterName`` are:

        - Flux
        - Index
        - Index1
        - Index2
        - CutoffEnergy
        - PivotEnergy
        - Curvature
        - Index2
        - Loc


        Args:
            selection (lambda or str): a lambda function or a boolean expression string specifying the selection criteria.
            parameterName (str): the ``free`` attribute of this parameter will be updated.
            free (bool): the boolean value used.

        Returns:
            The list of the sources matching the selection criteria.

        Note:
            The ``sourcesLibrary`` attribute is initialized by reading the corresponding
            xml descriptor file, loading its contents in memory. Updating the values
            held by this object will not affect the original values written on disk.

        Example:

            The following calls are equivalent and they set to True the ``free`` attribute of the "Flux" parameter for all the sources
            named "2AGLJ2021+4029" which distance from the map center is greater than zero and which flux value
            is greater than zero.

            >>> aganalysis.freeSources(lambda Name, Dist, Flux : Name == "2AGLJ2021+4029" and Dist > 0 and Flux > 0, "Flux", True)
            [..]

            >>> aganalysis.freeSources('Name == "2AGLJ2021+4029" AND Dist > 0 AND Flux > 0', "Flux", True)
            [..]



        """
        return self.sourcesLibrary.freeSources(selection, parameterName, free)



    def deleteSources(self, selection):
        """It deletes the sources matching the selection criteria from the ``sourcesLibrary``.

        Args:
            selection (lambda or str): a lambda function or a boolean expression string specifying the selection criteria.

        Returns:
            The list containing the deleted sources.
        """
        return self.sourcesLibrary.deleteSources(selection)

    def displaySkyMap(self, fitsFilepath,  smooth=False, sigma=4, save_image=False, format="png", title=None):
        """It shows fits skymap passed as first argument.

        Args:
            fitsimage (str): the relative or absolute path to the input fits file.
            smooth (bool): if set to true, gaussian smoothing will be computed
            sigma (float): value requested for computing gaussian smoothing
            save_image (bool): if set to true, saves the image into outdir directory
            format (string): the format of the image
            title: the title of the image


        Returns:
            Path to the file
        """
        return AstroUtils.displaySkyMap(fitsFilepath, smooth, sigma, save_image, self.outdir, format, title)




    @staticmethod
    def _updateFovMinMaxValues(fovbinnumber, fovradmin, fovradmax, stepi):
        # print("\nfovbinnumber {}, fovradmin {}, fovradmax {}, stepi {}".format(fovbinnumber, fovradmin, fovradmax, stepi))
        A = float(fovradmax) - float(fovradmin)
        B = float(fovbinnumber)
        C = stepi

        binleft =  ( (A / B) * C )
        binright = ( A / B  )
        bincenter = binleft - binright / 2.0
        fovmin = bincenter - ( A / B ) / 2.0
        fovmax = bincenter + ( A / B ) / 2.0

        # print("bincenter {}, fovmin {}, fovmax {}".format(bincenter, fovmin, fovmax))

        return bincenter, fovmin, fovmax
