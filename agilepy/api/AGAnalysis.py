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
from os.path import join, splitext
from pathlib import Path
from ntpath import basename
from time import time
from shutil import rmtree
# from multiprocessing import Process

from agilepy.config.AgilepyConfig import AgilepyConfig

from agilepy.api.SourcesLibrary import SourcesLibrary
from agilepy.api.ScienceTools import CtsMapGenerator, ExpMapGenerator, GasMapGenerator, IntMapGenerator, Multi

from agilepy.utils.PlottingUtils import PlottingUtils
from agilepy.utils.Parameters import Parameters
from agilepy.utils.MapList import MapList
from agilepy.utils.AgilepyLogger import AgilepyLogger
from agilepy.utils.AstroUtils import AstroUtils
from agilepy.utils.CustomExceptions import AGILENotFoundError, \
                                           PFILESNotFoundError, \
                                           ScienceToolInputArgMissing, \
                                           MaplistIsNone, \
                                           SourceNotFound

class AGAnalysis:
    """This class contains the high-level API methods you can use to run scientific analysis.

    This class requires you to setup a ``yaml configuration file`` to specify the software's behaviour
    and a ``xml descriptor file`` containing the list of the sources you want to take in account in your analysis.

    Class attributes:

    Attributes:
        config (:obj:`AgilepyConfig`): it is used to read/update configuration values.
        logger (:obj:`AgilepyLogger`): it is used to log messages with different importance levels.
        sourcesLibrary (:obj:`SourcesLibrary`): it contains the list of the sources and several useful methods.

    """

    def __init__(self, configurationFilePath, sourcesFilePath = None, overwriteOutputDir = False):
        """AGAnalysis constructor.

        Args:
            configurationFilePath (str): a relative or absolute path to the yaml configuration file.
            sourcesFilePath (str, optional): a relative or absolute path to a file containing the description of the sources. Defaults to None. \
            Three different types of format are supported: AGILE format (.txt), XML format (.xml) and AGILE catalog files (.multi).
            overwriteOutputDir (bool, optional): if True and if the output directory is not empty, the output directory content is deleted. Defaults to False.

        Raises:
            FileExistsError: if the output directory already exists.
            AGILENotFoundError: if the AGILE environment variable is not set.
            PFILESNotFoundError: if the PFILES environment variable is not set.

        Example:
            >>> from agilepy.api import AGAnalysis
            >>> aganalysis = AGAnalysis('agconfig.yaml', sourcesFilePath='sources.xml', removeOutputDir=True)

        """

        self.config = AgilepyConfig()

        self.config.loadConfigurations(configurationFilePath, validate=True)

        outdir = self.config.getConf("output","outdir")

        if overwriteOutputDir and Path(outdir).exists():
            rmtree(outdir)
            Path(outdir).mkdir(parents=True, exist_ok=True)


        if not overwriteOutputDir and Path(outdir).exists():
            raise FileExistsError("The output directory %s already exists! Please, delete it or specify another output directory!"%(outdir))

        self.logger = AgilepyLogger()

        self.logger.initialize(outdir, self.config.getConf("output","logfilenameprefix"), self.config.getConf("output","verboselvl"))

        self.sourcesLibrary = SourcesLibrary(self.config, self.logger)

        if sourcesFilePath:

            self.sourcesLibrary.loadSourcesFromFile(sourcesFilePath)

        self.plottingUtils = PlottingUtils(self.config, self.logger)

        if "AGILE" not in os.environ:
            raise AGILENotFoundError("$AGILE is not set.")

        if "PFILES" not in os.environ:
            raise PFILESNotFoundError("$PFILES is not set.")

        self.currentMapList = MapList()
        # MapList Observes the observable AgilepyConfig
        self.config.attach(self.currentMapList, "galcoeff")
        self.config.attach(self.currentMapList, "isocoeff")


    def destroy(self):
        self.sourcesLibrary.destroy()
        self.logger.reset()
        self.config.detach(self.currentMapList, "galcoeff")
        self.config.detach(self.currentMapList, "isocoeff")
        self.currentMapList = None


    ############################################################################
    # utility                                                                  #
    ############################################################################

    def setOptions(self, **kwargs):
        """It updates configuration options specifying one or more key=value pairs at once.

        Args:
            \*\*kwargs: key-values pairs, separated by a comma.

        Returns:
            None

        Raises:
            ConfigFileOptionTypeError: if the type of the option value is not wrong.
            ConfigurationsNotValidError: if the values are not coherent with the configuration.
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

    def getOption(self, optionName):
        """It reads an option value from the configuration.

        Args:
            optionName (str): the name of the option.

        Returns:
            The option value

        Raises:
            OptionNotFoundInConfigFileError: if the optionName is not found in the configuration.
        """



        return self.config.getOptionValue(optionName)

    def printOptions(self, section=None):
        """It prints the configuration options in the console.

        Args:
            section (str): you can specify a configuration file section to be printed out.

        Returns:
            None
        """
        return self.config.printOptions(section)

    def parseMaplistFile(self, maplistFilePath=None):
        """It parses the maplistfile in order to return sky map files paths.

        Args:
            maplistFilePath (str): if you don't specify the maplistfile path, the
            last generated one (if it exists) will be used.

        Returns:
            A matrix where each row contains a cts, ext and gas map.

        Raises:
            MaplistIsNone: if no maplist file is passed and no maplist file have been generated yet.
        """
        if not maplistFilePath and self.currentMapList.getFile() is None:

            raise MaplistIsNone("No 'maplist' files found. Please, pass a valid path to a maplist \
                                 file as argument or call generateMaps(). ")

        if not maplistFilePath:

            maplistFilePath = self.currentMapList.getFile()

        with open(maplistFilePath, "r") as mlf:

            mlf_content = mlf.readlines()

        maps = []

        for line in mlf_content:
            elements = line.split(" ")
            cts_map = elements[0]
            exp_map = elements[1]
            gas_map = elements[2]
            bin_center = elements[3]
            gas_coeff = elements[4]
            iso_coeff = elements[5].strip()
            maps.append( [cts_map, exp_map, gas_map, bin_center, gas_coeff, iso_coeff] )

        return maps

    def displayCtsSkyMaps(self, maplistFile=None, singleMode=True, smooth=4.0, saveImage=False, fileFormat=".png", title=None, cmap="CMRmap", regFilePath=None, catalogRegions=None, catalogRegionsColor="red"):
        """It displays the last generated cts skymaps.

        Args:
            maplistFile (str, optional): the path to the .maplist file. If not specified, the last generated maplist file will be used. It defaults to None.
            singleMode (bool, optional): if set to true, all maps will be displayed as subplots on a single figure. It defaults to True.
            smooth (float, optional): the sigma value of the gaussian smoothing. It defaults to 4.0.
            saveImage (bool, optional): if set to true, saves the image into the output directory. It defaults to False.
            fileFormat (str, optional): the extension of the output image. It defaults to '.png' .
            title (str, optional): the title of the image. It defaults to None.
            cmap (str, optional): Matplotlib colormap. It defaults to 'CMRmap'. Colormaps: https://matplotlib.org/tutorials/colors/colormaps.html
            regFilePath (str, optional): the relative or absolute path to a region file. It defaults to None.
            catalogRegions(str, optional): a catalog name. The regions that belongs to the catalog will be loaded. It defaults to None.
            catalogRegionsColor(str, optional): the color of the regions loaded from the catalog.

        Returns:
            It returns the paths to the image files written on disk.
        """
        return self._displaySkyMaps("CTS",  singleMode, maplistFile, smooth, saveImage, fileFormat, title, cmap, regFilePath, catalogRegions, catalogRegionsColor)

    def displayExpSkyMaps(self, maplistFile=None, singleMode=True, smooth=False, sigma=4.0, saveImage=False, fileFormat=".png", title=None, cmap="CMRmap", regFilePath=None, catalogRegions=None, catalogRegionsColor="red"):
        """It displays the last generated exp skymaps.

        Args:
            maplistFile (str, optional): the path to the .maplist file. If not specified, the last generated maplist file will be used. It defaults to None.
            singleMode (bool, optional): if set to true, all maps will be displayed as subplots on a single figure. It defaults to True.
            smooth (float, optional): the sigma value of the gaussian smoothing. It defaults to 4.0.
            saveImage (bool, optional): if set to true, saves the image into the output directory. It defaults to False.
            fileFormat (str, optional): the extension of the output image. It defaults to '.png' .
            title (str, optional): the title of the image. It defaults to None.
            cmap (str, optional): Matplotlib colormap. It defaults to 'CMRmap'. Colormaps: https://matplotlib.org/tutorials/colors/colormaps.html
            regFilePath (str, optional): the relative or absolute path to a region file. It defaults to None.
            catalogRegions(str, optional): a catalog name. The regions that belongs to the catalog will be loaded. It defaults to None.
            catalogRegionsColor(str, optional): the color of the regions loaded from the catalog.

        Returns:
            It returns the paths to the image files written on disk.
        """
        return self._displaySkyMaps("EXP", singleMode, maplistFile, smooth, saveImage, fileFormat, title, cmap, regFilePath, catalogRegions, catalogRegionsColor)

    def displayGasSkyMaps(self, maplistFile=None, singleMode=True, smooth=False, sigma=4.0, saveImage=False, fileFormat=".png", title=None, cmap="CMRmap", regFilePath=None, catalogRegions=None, catalogRegionsColor="red"):
        """It displays the last generated gas skymaps.

        Args:
            maplistFile (str, optional): the path to the .maplist file. If not specified, the last generated maplist file will be used. It defaults to None.
            singleMode (bool, optional): if set to true, all maps will be displayed as subplots on a single figure. It defaults to True.
            smooth (float, optional): the sigma value of the gaussian smoothing. It defaults to 4.0.
            saveImage (bool, optional): if set to true, saves the image into the output directory. It defaults to False.
            fileFormat (str, optional): the extension of the output image. It defaults to '.png' .
            title (str, optional): the title of the image. It defaults to None.
            cmap (str, optional): Matplotlib colormap. It defaults to 'CMRmap'. Colormaps: https://matplotlib.org/tutorials/colors/colormaps.html
            regFilePath (str, optional): the relative or absolute path to a region file. It defaults to None.
            catalogRegions(str, optional): a catalog name. The regions that belongs to the catalog will be loaded. It defaults to None.
            catalogRegionsColor(str, optional): the color of the regions loaded from the catalog.

        Returns:
            It returns the paths to the image files written on disk.
        """
        return self._displaySkyMaps("GAS", singleMode, maplistFile, smooth, saveImage, fileFormat, title, cmap, regFilePath, catalogRegions, catalogRegionsColor)



    ############################################################################
    # analysis                                                                 #
    ############################################################################

    def generateMaps(self, config = None, maplistObj = None):
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
        timeStart = time()

        if config:
            configBKP = config
        else:
            configBKP = AgilepyConfig.getCopy(self.config)

        if maplistObj:
            maplistObjBKP = maplistObj
        else:
            maplistObjBKP = self.currentMapList

        fovbinnumber = configBKP.getOptionValue("fovbinnumber")
        energybins = configBKP.getOptionValue("energybins")

        initialFovmin = configBKP.getOptionValue("fovradmin")
        initialFovmax = configBKP.getOptionValue("fovradmax")
        initialFileNamePrefix = configBKP.getOptionValue("filenameprefix")


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

                    configBKP.setOptions(filenameprefix=initialFileNamePrefix+"_"+fileNamePrefix)
                    configBKP.setOptions(fovradmin=fovmin, fovradmax=fovmax)
                    configBKP.addOptions("selection", emin=emin, emax=emax)
                    configBKP.addOptions("maps", skymapL=skymapL, skymapH=skymapH)


                    ctsMapGenerator = CtsMapGenerator("AG_ctsmapgen", self.logger)
                    expMapGenerator = ExpMapGenerator("AG_expmapgen", self.logger)
                    gasMapGenerator = GasMapGenerator("AG_gasmapgen", self.logger)
                    intMapGenerator = IntMapGenerator("AG_intmapgen", self.logger)

                    ctsMapGenerator.configureTool(configBKP)
                    expMapGenerator.configureTool(configBKP)
                    gasMapGenerator.configureTool(configBKP, {"expMapGeneratorOutfilePath": expMapGenerator.outfilePath})
                    intMapGenerator.configureTool(configBKP, {"expMapGeneratorOutfilePath": expMapGenerator.outfilePath, "ctsMapGeneratorOutfilePath" : ctsMapGenerator.outfilePath})

                    configBKP.addOptions("maps", expmap=expMapGenerator.outfilePath, ctsmap=ctsMapGenerator.outfilePath)

                    if not ctsMapGenerator.allRequiredOptionsSet(configBKP) or \
                       not expMapGenerator.allRequiredOptionsSet(configBKP) or \
                       not gasMapGenerator.allRequiredOptionsSet(configBKP) or \
                       not intMapGenerator.allRequiredOptionsSet(configBKP):

                        raise ScienceToolInputArgMissing("Some options have not been set.")

                    f1 = ctsMapGenerator.call()
                    self.logger.info(self, "Science tool ctsMapGenerator produced:\n %s", f1)

                    f2 = expMapGenerator.call()
                    self.logger.info(self, "Science tool expMapGenerator produced:\n %s", f2)

                    f3 = gasMapGenerator.call()
                    self.logger.info(self, "Science tool gasMapGenerator produced:\n %s", f3)

                    f4 = intMapGenerator.call()
                    self.logger.info(self, "Science tool intMapGenerator produced:\n %s", f4)

                    maplistObjBKP.addRow(  ctsMapGenerator.outfilePath, \
                                                expMapGenerator.outfilePath, \
                                                gasMapGenerator.outfilePath, \
                                                str(bincenter), \
                                                str(configBKP.getOptionValue("galcoeff")[bgCoeffIdx]), \
                                                str(configBKP.getOptionValue("isocoeff")[bgCoeffIdx])
                                              )
                else:
                    self.logger.warning(self,"Energy bin [%s, %s] is not supported. Map generation skipped.", stepe[0], stepe[1])


        outdir = configBKP.getOptionValue("outdir")

        maplistObjBKP.setFile(Path(outdir).joinpath(initialFileNamePrefix))

        maplistFilePath = maplistObjBKP.writeToFile()

        self.logger.info(self, "Maplist file created in %s", maplistFilePath)

        self.logger.info(self, "Took %f seconds.", time() - timeStart)

        return maplistFilePath

    def calcBkg(self, sourceName, galcoeff = None, pastTimeWindow = 14.0):
        """It estimates the isotropic and galactic background coefficients.
           It automatically updates the configuration.


        Args:
            sourceName (str): the name of the source under analysis.
            galcoeff (List, optional): the galactic background coefficients (one for each map).
            pastTimeWindow (float, optional): the number of days previous tmin. It defaults to 14. If \
                it's 0, the background coefficients will be estimated within the [tmin, tmax] interval.

        Returns:
            isoCoeff, galCoeff (List, List): the estimates of the background coefficients.


        """
        timeStart = time()


        ################################################################## checks
        self.sourcesLibrary.backupSL()

        inputSource = self.selectSources(f'name == "{sourceName}"', quiet=True)

        if not inputSource:
            self.logger.critical(self, "The source %s has not been loaded yet", sourceName)
            raise SourceNotFound(f"The source {sourceName} has not been loaded yet")

        analysisDataDir = Path(self.config.getOptionValue("outdir")).joinpath("calcBkg")

        if analysisDataDir.exists():
            rmtree(analysisDataDir)



        ######################################################## configurations
        configBKP = AgilepyConfig.getCopy(self.config)
        configBKP.setOptions(filenameprefix="calcBkg", outdir=str(analysisDataDir))


        ############################################################## galcoeff
        if galcoeff is not None:
            configBKP.setOptions(galcoeff=galcoeff)


        ################################################################# times
        tmin = self.config.getOptionValue("tmin")
        tmax = self.config.getOptionValue("tmax")
        timetype = self.config.getOptionValue("timetype")

        if timetype == "MJD":
            tmin = AstroUtils.time_mjd_to_tt(tmin)
            tmax = AstroUtils.time_mjd_to_tt(tmax)

        if pastTimeWindow != 0:
            tmax = tmin
            tmin = tmin - pastTimeWindow*86400

        self.logger.info(self, "tmin: %f tmax: %f type: %s", tmin, tmax, timetype)
        configBKP.setOptions(tmin = tmin, tmax = tmax, timetype = "TT")


        maplistObj = MapList()

        ######################################################## maps generation
        maplistFilePath = self.generateMaps(config = configBKP, maplistObj = maplistObj)


        #################################### fixflag = 0 except for input source
        for s in self.getSources():
            self.fixSource(s)

        # "sourceName" must have flux = 1
        self.freeSources(f'name == "{sourceName}"', "flux", True)




        #################################################################### mle
        #configBKP.setOptions(filenameprefix = "calcBkg", outdir = str(analysisDataDir))
        #configBKP.setOptions(tmin = tmin, tmax = tmax, timetype = "TT")
        sourceFiles = self.mle(maplistFilePath = maplistFilePath, config = configBKP, updateSourceLibrary = False)

        # extract iso e gal coeff of "sourceName"
        isoCoeff, galCoeff = self._extractBkgCoeff(sourceFiles, sourceName)

        self.sourcesLibrary.restoreSL()

        self.config.setOptions(galcoeff=galCoeff, isocoeff=isoCoeff)

        self.logger.info(self, "Took %f seconds.", time()-timeStart)

        return isoCoeff, galCoeff


    def mle(self, maplistFilePath = None, config = None, updateSourceLibrary = True):
        """It performs a maximum likelihood estimation analysis on every source withing the ``sourceLibrary``, producing one output file per source.

        The method's behaviour varies according to several configuration options (see docs :ref:`configuration-file`).

        The outputfiles have the ``.source`` extension.

        The method's behaviour varies according to several configuration options (see docs here).

        Note:
            It resets the configuration options to their original values before exiting.

        Args:
            maplistFilePath (str): if not provided, the mle() analysis will use the last generated mapfile produced by ``generateMaps()``.

        Returns:
            A list of absolute paths to the output ``.source`` files.

        Raises:
            MaplistIsNone: is the input argument is None.

        Example:
            >>> maplistFilePath = aganalysis.generateMaps()
            >>> aganalysis.mle(maplistFilePath)
            [/home/rt/agilepy/output/testcase0001_2AGLJ2021+4029.source /home/rt/agilepy/output/testcase0001_2AGLJ2021+3654.source]

        """
        timeStart = time()

        if config:
            configBKP = config
        else:
            configBKP = AgilepyConfig.getCopy(self.config)

        if not maplistFilePath and self.currentMapList.getFile() is None:

            raise MaplistIsNone("No 'maplist' files found. Please, pass a valid path to a maplist \
                                 file as argument or call generateMaps(). ")

        if not maplistFilePath:

            maplistFilePath = self.currentMapList.getFile()

        multi = Multi("AG_multi", self.logger)

        sourceListFilename = "sourceLibrary"+(str(multi.callCounter).zfill(5))
        sourceListAgileFormatFilePath = self.sourcesLibrary.writeToFile(outfileNamePrefix=join(self.config.getConf("output","outdir"), sourceListFilename), fileformat="txt")

        configBKP.addOptions("selection", maplist=maplistFilePath, sourcelist=sourceListAgileFormatFilePath)

        multisources = self.sourcesLibrary.getSourcesNames()
        configBKP.addOptions("selection", multisources=multisources)


        multi.configureTool(configBKP)

        sourceFiles = multi.call()

        if len(sourceFiles) == 0:
            self.logger.warning(self, "The number of .source files is 0.")

        self.logger.info(self,"AG_multi produced: %s", sourceFiles)

        if updateSourceLibrary:

            for sourceFile in sourceFiles:

                multiOutputData = self.sourcesLibrary.parseSourceFile(sourceFile)

                self.sourcesLibrary.updateMulti(multiOutputData)


        self.logger.info(self, "Took %f seconds.", time()-timeStart)


        return sourceFiles

    def lightCurve(self, sourceName, binsize = 86400, processes=1):
        """It generates a cvs file containing the data for a light curve plot.

        Args:
            sourceName (str): the name of the source under analysis.
            binsize (int): temporal bin size.

        Returns:
            The absolute path to the light curve data output file.
        """
        timeStart = time()

        tmin = self.config.getOptionValue("tmin")
        tmax = self.config.getOptionValue("tmax")
        timetype = self.config.getOptionValue("timetype")

        if timetype == "MJD":
            tmin = AstroUtils.time_mjd_to_tt(tmin)
            tmax = AstroUtils.time_mjd_to_tt(tmax)

        tmin = int(tmin)
        tmax = int(tmax)

        bins = [ (t1, t1+binsize) for t1 in range(tmin, tmax, binsize) ]
        tstart = bins[0][0]
        tstop = bins[-1][1]

        lcAnalysisDataDir = self.config.getOptionValue("outdir") + "/lc"

        binsForProcesses = AGAnalysis._chunkList(bins, processes)

        configBKP = AgilepyConfig.getCopy(self.config)

        # logFilenamePrefix = configBKP.getConf("output","logfilenameprefix")
        # verboseLvl = configBKP.getConf("output","verboselvl")

        self.logger.info(self, "Number of processes: %d, Number of bins per process %d", processes, len(binsForProcesses[0]))

        for t1,t2 in bins:

            binOutDir = f'{lcAnalysisDataDir}/bin_{t1}_{t2}'

            configBKP.setOptions(filenameprefix="lc_analysis", outdir = binOutDir)
            configBKP.setOptions(tmin = t1, tmax = t2, timetype = "TT")

            maplistFilePath = self.generateMaps(config = configBKP)

            configBKP.setOptions(filenameprefix="lc_analysis", outdir = binOutDir)
            configBKP.setOptions(tmin = t1, tmax = t2, timetype = "TT")
            _ = self.mle(maplistFilePath = maplistFilePath, config = configBKP, updateSourceLibrary = False)

        """
        processes = []
        for pID, pInputs in enumerate(binsForProcesses):
            logFilenamePrefix += f"_thread_{pID}"
            print("generating process...(%d). Chunk size for process: %d"%(pID, len(pInputs)))
            p = Process(target=self._computeLcBin, args=(pID, pInputs, configBKP, lcAnalysisDataDir, logsOutDir, logFilenamePrefix, verboseLvl))
            processes.append((pID,p,len(pInputs)))

        for pID, p, binsNumber in processes:
            self.logger.info(self, "Starting process %d for %d bins", pID, binsNumber)
            p.start()

        for pID, p, binsNumber in processes:
            p.join()
        """


        lcData = self.getLightCurveData(sourceName, lcAnalysisDataDir)

        lcOutputFilePath = Path(lcAnalysisDataDir).joinpath(f"light_curve_{tstart}_{tstop}.txt")

        with open(lcOutputFilePath, "w") as lco:
            lco.write(lcData)

        self.logger.info(self, "Light curve created in %s", lcOutputFilePath)

        self.logger.info(self, "Took %f seconds.", time()-timeStart)

        return str(lcOutputFilePath)

    def getLightCurveData(self, sourceName, lcAnalysisDataDir):


        binDirectories = os.listdir(lcAnalysisDataDir)

        lcData = "t_start t_end sqrt_ts flux flux_err flux_ul\n"

        for bd in binDirectories:

            mleOutputDirectories = Path(lcAnalysisDataDir).joinpath(bd).joinpath("mle")

            mleOutputFiles = os.listdir(mleOutputDirectories)

            for mleOutputFile in mleOutputFiles:

                mleOutputFilename, mleOutputFileExtension = splitext(mleOutputFile)

                if mleOutputFileExtension == ".source" and sourceName in mleOutputFilename:

                    mleOutputFilepath = mleOutputDirectories.joinpath(mleOutputFile)

                    lcRow = self._extractLightCurveDataFromSourceFile(str(mleOutputFilepath))

                    lcData += lcRow+"\n"

        self.logger.info(self, f"{lcData}")
        return lcData

    ############################################################################
    # sources management                                                       #
    ############################################################################

    def getSupportedCatalogs(self):
        """It returns a list of filepaths corresponding to the supported catalogs you can load.

        Returns:
            A List of filepaths.
        """
        return self.sourcesLibrary.getSupportedCatalogs()

    def loadSourcesFromCatalog(self, catalogName, rangeDist = (0, float("inf"))):
        """It loads the sources from a catalog.

        You can also specify a rangeDist argument to filter out the sources which distance from (glon, glat) is not in the rangeDist interval.

        If the catalog is 2AGL and if the energy range (emin, emax) specified by the user in the configuration file is different from the catalog's energy range,
        the flux of every source will be scaled.

        Args:
            catalogName (str): the catalog name (2AGL, 4FGL).
            rangeDist (tuple, optional): a interval (min, max) of distances (degree). It defaults to (0, +inf).
        Raises:
            FileNotFoundError: if the catalog is not supported.
            SourceModelFormatNotSupported: if the input file format is not supported.
            SourcesFileLoadingError: if any error occurs during the parsing of the sources file.

        Returns:
            The List of sources that have been succesfully loaded into the SourcesLibrary.
        """
        return self.sourcesLibrary.loadSourcesFromCatalog(catalogName, rangeDist)


    def loadSourcesFromFile(self, sourcesFilepath, rangeDist = (0, float("inf"))):
        """It loads the sources, reading them from a file. Three different types \
        of format are supported: AGILE format (.txt), XML format (.xml) and AGILE catalog files (.multi).

        You can also specify a rangeDist argument to filter out the sources which distance from (glon, glat) is not in the rangeDist interval.

        Args:
            sourcesFilePath (str): a relative or absolute path to a file containing the description of the sources. \
            rangeDist (tuple): a interval (min, max) of distances (degree)
        Raises:
            SourceModelFormatNotSupported: if the input file format is not supported.
            SourcesFileLoadingError: if any error occurs during the parsing of the sources file.

        Returns:
            The List of sources that have been succesfully loaded into the SourcesLibrary.
        """
        return self.sourcesLibrary.loadSourcesFromFile(sourcesFilepath, rangeDist)

    def selectSources(self, selection, quiet=False):
        """It returns the sources matching the selection criteria from the ``sourcesLibrary``.

        The sources can be selected with the ``selection`` argument, supporting either ``lambda functions`` and
        ``boolean expression strings``.

        The selection criteria can be expressed using the following ``Source`` class's parameters:

        - name: the unique code identifying the source.
        - dist: the distance of the source from the center of the maps.
        - flux: the flux value.
        - sqrtTS: the radix square of the ts.

        Warning:

            The sqrtTS parameter is available only after the maximum likelihood estimation analysis is performed.

        Args:
            selection (lambda or str): a lambda function or a boolean expression string specifying the selection criteria.
            quiet (boolean) (optional default=False): if quiet is True, the method will not console log the selected sources.

        Returns:
            List of sources.
        """
        return self.sourcesLibrary.selectSources(selection, quiet=quiet)

    def getSources(self):
        """It returns all the sources.

            Returns:
                List of sources.
        """
        return self.sourcesLibrary.sources

    def freeSources(self, selection, parameterName, free):
        """It can set to True or False a parameter's ``free`` attribute of one or more source.

        Example of source model:
        ::

            <source name="2AGLJ2021+4029" type="PointSource">
                <spectrum type="PLExpCutoff">
                  <parameter name="flux" free="1"  value="119.3e-08"/>
                  <parameter name="index" free="0" scale="-1.0" value="1.75" min="0.5" max="5"/>
                  <parameter name="cutoffEnergy" free="0" value="3307.63" min="20" max="10000"/>
                </spectrum>
                <spatialModel type="PointSource" location_limit="0">
                  <parameter name="pos" value="(78.2375, 2.12298)" free="0" />
                </spatialModel>
            </source>


        The supported ``parameterName`` are:

        - flux
        - index
        - index1
        - index2
        - cutoffEnergy
        - pivotEnergy
        - curvature
        - index2


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

            >>> aganalysis.freeSources(lambda name, dist, flux : Name == "2AGLJ2021+4029" AND dist > 0 AND flux > 0, "flux", True)
            [..]

            >>> aganalysis.freeSources('name == "2AGLJ2021+4029" AND dist > 0 AND flux > 0', "flux", True)
            [..]



        """
        return self.sourcesLibrary.freeSources(selection, parameterName, free)

    def fixSource(self, source):
        """Set to False all freeable params of a source.

        Args:
            sourceName (Source): the source object.

        Returns:
            True if at least one parameter of the source changes, False otherwise.

        """
        return self.sourcesLibrary.fixSource(source)

    def addSource(self, sourceName, sourceDict):
        """It adds a new source in the ``Sources Library``. You can add a source, passing \
        a dictionary containing the source's data. Some keys are required, other are optional.
        Here's an example:

        ::

            newSourceDict = {
                "glon" : 6.16978,
                "glat": -0.0676943,
                "spectrumType" : "LogParabola",
                "flux": 35.79e-08,
                "curvature": 0.682363
            }
            newSource = aganalysis.addSource("2AGLJ1801-2334", newSourceDict)

        Args:
            sourceName (str): the name of the source
            sourceDict (dict): a dictionary containing the source's data.

        Raises:
            SourceParamNotFoundError: if ``sourceName`` is None or empty, OR the \
            ``sourceDict`` input dictionary does not contain at least one of the \
            following keys: ["glon", "glat","spectrumType"].

        Returns:
            The source object if it is been loaded. None, otherwise.
        """
        return self.sourcesLibrary.addSource(sourceName, sourceDict)

    def deleteSources(self, selection):
        """It deletes the sources matching the selection criteria from the ``sourcesLibrary``.

        Args:
            selection (lambda or str): a lambda function or a boolean expression string specifying the selection criteria.

        Returns:
            The list containing the deleted sources.
        """
        return self.sourcesLibrary.deleteSources(selection)

    def updateSourcePosition(self, sourceName, useMulti=True, glon=None, glat=None):
        """It updates a source (l,b) position parameters. You can explicity pass new values
        or your can use the output of the last mle() analysis.

        Args:
            sourceName (str): the name of the source
            useMulti (bool): set it to True if you want to use the last mle analysis output
            glon (float): if useMulti is False this value is goint to be use.
            glat (float): if useMulti is False this value is goint to be use.

        Raises:
            SourceNotFound: if the source has not been loaded into the SourcesLibrary.
            MultiOutputNotFoundError: if useMulti is True but mle() has not been executed yet.
            ValueError: if useMulti is False but one of glon or glat in None.

        Returns:
            True if the position changes, False when the position don't change or the position is (-1, -1).
        """
        return self.sourcesLibrary.updateSourcePosition(sourceName, useMulti, glon, glat)

    def writeSourcesOnFile(self, outfileNamePrefix, fileFormat):
        """It writes on file the list of sources loaded into the *SourceLibrary*.
        The supported formats ('txt' AND 'xml') are described here: :ref:`sources-file`.

        Args:
            outfileNamePrefix (str): the relative or absolute path to the input fits file.
            fileFormat (str): Possible values: ['txt', 'xml'].

        Returns:
            Path to the file
        """
        self.sourcesLibrary.writeToFile(outfileNamePrefix, fileFormat)

    def convertCatalogToXml(self, catalogFilepath):
        """It takes a catalog file in AGILE (.txt) format as input and converts
        it in the xml format.

        Args:
            catalogFilepath (str): a relative or absolute path to the catalog file in AGILE (.txt) format.

        Raises:
            SourceModelFormatNotSupported: if the input file format is not supported.

        Returns:
            A string rapresenting the path to the output file.

        """
        return self.sourcesLibrary.convertCatalogToXml(catalogFilepath)



    ############################################################################
    # private methods                                                          #
    ############################################################################


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

    def _computeLcBin(self, threadID, bins, configBKP, lcAnalysisDataDir, logsOutDir, logFilenamePrefix, verboseLvl):

        logger = AgilepyLogger()

        logger.initialize(logsOutDir, logFilenamePrefix, verboseLvl)

        # outputs = []

        for t1,t2 in bins:

            binOutDir = f'{lcAnalysisDataDir}/bin_{t1}_{t2}'

            configBKP.setOptions(filenameprefix="lc_analysis", outdir = binOutDir)
            configBKP.setOptions(tmin = t1, tmax = t2, timetype = "TT")

            maplistFilePath = self.generateMaps(configBKP)

            configBKP.setOptions(filenameprefix="lc_analysis", outdir = binOutDir)
            configBKP.setOptions(tmin = t1, tmax = t2, timetype = "TT")
            _ = self.mle(maplistFilePath = maplistFilePath, config = configBKP, updateSourceLibrary = False)

    @staticmethod
    def _chunkList(lst, num):
        avg = len(lst) / float(num)
        out = []
        last = 0.0

        while last < len(lst):
            out.append(lst[int(last):int(last + avg)])
            last += avg

        return out

    def _extractLightCurveDataFromSourceFile(self, sourceFilePath):

        multiOutput = self.sourcesLibrary.parseSourceFile(sourceFilePath)

        tstart = multiOutput.get("startDataTT", strRepr=True)
        tstop = multiOutput.get("endDataTT", strRepr=True)
        sqrtTS = multiOutput.get("multiSqrtTS", strRepr=True)
        flux = multiOutput.get("multiSqrtTS", strRepr=True)
        fluxErr = multiOutput.get("multiFluxErr", strRepr=True)
        fluxUL = multiOutput.get("multiUL", strRepr=True)

        return f"{tstart} {tstop} {sqrtTS} {flux} {fluxErr} {fluxUL}"

    def _extractBkgCoeff(self, sourceFiles, sourceName):

        sourceFilePath = [ sourceFilePath for sourceFilePath in sourceFiles if sourceName in basename(sourceFilePath)]

        if len(sourceFilePath) > 1:
            self.logger.critical(self, f"Something is wrong, found two .source files {sourceFilePath} for the same source {sourceName}")
            raise ValueError(f"Something is wrong, found two .source files {sourceFilePath} for the same source {sourceName}")

        self.logger.debug(self, "Extracting isocoeff and galcoeff from %s", sourceFilePath)

        multiOutput = self.sourcesLibrary.parseSourceFile(sourceFilePath.pop())

        isoCoeff = multiOutput.get("multiIsoCoeff")
        galCoeff = multiOutput.get("multiGalCoeff")

        self.logger.debug(self, f"Multioutput: {multiOutput}")

        return isoCoeff, galCoeff


    def _displaySkyMaps(self, skyMapType, singleMode, maplistFile=None, smooth=4.0, saveImage=False, fileFormat=".png", title=None, cmap="CMRmap", regFilePath=None, catalogRegions=None, catalogRegionsColor=None):

        if self.currentMapList.getFile() is None and maplistFile is None:
            self.logger.warning(self, "No sky maps have already been generated yet and maplistFile is None. Please, call generateMaps() or pass a valid maplistFile.")
            return False

        if self.currentMapList.getFile() is None:
            maplistRows = self.parseMaplistFile(maplistFile)
        else:
            maplistRows = self.parseMaplistFile()

        outputs = []

        titles = []
        files = []

        for maplistRow in maplistRows:

            skymapFilename = basename(maplistRow[0])
            emin = skymapFilename.split("EMIN")[1].split("_")[0]
            emax = skymapFilename.split("EMAX")[1].split("_")[0]

            title = f"{skyMapType}\nemin: {emin} emax: {emax} bincenter: {maplistRow[3]}\ngalcoeff: {maplistRow[4]} isocoeff: {maplistRow[5]}"

            titles.append(title)

            if skyMapType == "CTS":
                mapIndex = 0

            elif skyMapType == "EXP":
                mapIndex = 1

            else:
                mapIndex = 2

            files.append(maplistRow[mapIndex])

        if len(files) == 1 and singleMode is True:
            self.logger.warning(self, "singleMode has been turned off because only one map is going to be displayed.")
            singleMode = False


        if singleMode:

            outputfile = self.plottingUtils.displaySkyMapsSingleMode(files, smooth=smooth, saveImage=saveImage, fileFormat=fileFormat, titles=titles, cmap=cmap, regFilePath=regFilePath, catalogRegions=catalogRegions, catalogRegionsColor=catalogRegionsColor)

            outputs.append(outputfile)

        else:

            for idx,title in enumerate(titles):

                outputfile = self.plottingUtils.displaySkyMap(files[idx], smooth, saveImage, fileFormat, title, cmap, regFilePath, catalogRegions, catalogRegionsColor)

                outputs.append(outputfile)

        return outputs
