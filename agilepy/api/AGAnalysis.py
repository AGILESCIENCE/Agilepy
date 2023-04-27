# DESCRIPTION
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
import re
import numpy as np
# from tqdm import tqdm, trange  
from tqdm.notebook import trange, tqdm
from time import time
from pathlib import Path
from shutil import rmtree
from ntpath import basename
from os.path import join, splitext, expandvars

from agilepy.core.AGDataset import AGDataset
pattern = re.compile('e([+\-]\d+)')

from agilepy.core.AGBaseAnalysis import AGBaseAnalysis
from agilepy.core.SourcesLibrary import SourcesLibrary
from agilepy.core.ScienceTools import CtsMapGenerator, ExpMapGenerator, GasMapGenerator, IntMapGenerator, Multi, AP
from agilepy.config.AgilepyConfig import AgilepyConfig
from agilepy.utils.AstroUtils import AstroUtils
from agilepy.core.Parameters import Parameters
from agilepy.core.MapList import MapList
from agilepy.utils.Utils import Utils
from agilepy.core.CustomExceptions import   AGILENotFoundError, \
                                            PFILESNotFoundError, \
                                            ScienceToolInputArgMissing, \
                                            MaplistIsNone, SelectionParamNotSupported, \
                                            SourceNotFound, \
                                            SourcesLibraryIsEmpty, \
                                            ValueOutOfRange
                                            
class AGAnalysis(AGBaseAnalysis):
    """This class contains the high-level API to run scientific analysis, data visualization and some utility methods.

    This constructor of this class requires a ``yaml configuration file``.

    """
    INSTANCE_COUNT = 0

    def __init__(self, configurationFilePath, sourcesFilePath = None):
        """AGAnalysis constructor.

        Args:
            configurationFilePath (str): a relative or absolute path to the yaml configuration file.
            sourcesFilePath (str, optional): a relative or absolute path to a file containing the description of the sources. Defaults to None. \
            Three different types of formats are supported: AGILE format (.txt), XML format (.xml) and AGILE catalog files (.multi).

        Raises:
            AGILENotFoundError: if the AGILE environment variable is not set.
            PFILESNotFoundError: if the PFILES environment variable is not set.

        Example:
            >>> from agilepy.api import AGAnalysis
            >>> aganalysis = AGAnalysis('agconfig.yaml', sourcesFilePath='sources.xml')

        """
        super().__init__(configurationFilePath)
        
        if AGAnalysis.INSTANCE_COUNT > 0:
            print("\n>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>\n[WARNING] Each notebook should instantiate only one AGAnalysis object, otherwise the logger will be duplicated. Duplicate logs can be tricky. If you want to make another analysis, create a new notebook or restart the Kernel and update this one.")
        AGAnalysis.INSTANCE_COUNT += 1
    
        self.config.loadConfigurationsForClass("AGAnalysis")

        self.sourcesLibrary = SourcesLibrary(self.config, self.logger)

        if sourcesFilePath:

            self.sourcesLibrary.loadSourcesFromFile(sourcesFilePath)

        # MapList Observes the observable AgilepyConfig
        self.currentMapList = MapList(self.logger)
        self.config.attach(self.currentMapList, "galcoeff")
        self.config.attach(self.currentMapList, "isocoeff")

        self.lightCurveData = {
            "mle" : None,
            "ap" : None
        }

        self.multiTool = Multi("AG_multi", self.logger)

        if self.config.getOptionValue("userestapi"):
            self.agdataset = AGDataset(self.logger)
            self.agdataset.agilecoverage()


    def destroy(self):
        """ It clears the list of sources and the current maplist file.
        """
        self.sourcesLibrary.destroy()
        self.logger.reset()
        self.config.detach(self.currentMapList, "galcoeff")
        self.config.detach(self.currentMapList, "isocoeff")
        self.currentMapList = None


    ############################################################################
    # utility                                                                  #
    ############################################################################

    @staticmethod
    def getConfiguration(confFilePath, userName, sourceName, tmin, tmax, timetype, glon, glat, outputDir, verboselvl, evtfile="/AGILE_PROC3/FM3.119_ASDC2/INDEX/EVT.index", logfile="/AGILE_PROC3/DATA_ASDC2/INDEX/LOG.log.index", userestapi=True, datapath=None):
        """Utility method to create a configuration file.

        Args:
            confFilePath (str): the path and filename of the configuration file that is going to be created.
            userName (str): the username of who is running the software.
            sourceName (str): the name of the source.
            tmin (float): the start time of the analysis.
            tmax (float): the stop time of the analysis.
            timetype (str): timetype format possible values: "TT" or "MJD"
            glon (float): the galactic longitude (L) of the analysis.
            glat (float): the galactic latitude (B) of the analysis.
            outputDir (str): the path to the output directory. The output directory will be created using the following format: 'userName_sourceName_todaydate'
            verboselvl (int): the verbosity level of the console output. Message types: level 0 => critical, warning, level 1 => critical, warning, info, level 2 => critical, warning, info, debug
            evtfile (str, optional [default=/AGILE_PROC3/FM3.119_ASDC2/INDEX/EVT.index]): the index file to be used for event data if userestapi is set to False. The time range starts from 107092735 TT, 54244.49924768 MJD, 2007-05-24 11:58:55 UTC
            logfile (str, optional [default=/AGILE_PROC3/DATA_ASDC2/INDEX/LOG.log.index]): the index file to be used for log data if userestapi is set to False. The time range starts from 107092735 TT, 54244.49924768 MJD, 2007-05-24 11:58:55 UTC
            userestapi (bool, optional [default=True]): If True, the SSDC REST API will be used to download missing data.
            datapath (str, optional [default=None]): Datapath to download AGILE data if userestapi is set to True. Index files will be generated into this path.


        Returns:
            None
        """

        configuration = f"""
input:
  evtfile: {evtfile}
  logfile: {logfile}
  userestapi: {userestapi}
  datapath: {datapath}

output:
  outdir: {outputDir}
  filenameprefix: analysis_product
  logfilenameprefix: analysis_log
  sourcename: {sourceName}
  username: {userName}
  verboselvl: {verboselvl}

selection:  
  emin: 100
  emax: 10000
  tmin: {tmin}
  tmax: {tmax}
  timetype: {timetype}
  glon: {glon}
  glat: {glat}
  proj: ARC
  timelist: None
  filtercode: 5
  fovradmin: 0
  fovradmax: 60
  albedorad: 80
  dq: 0
  phasecode: null
  lonpole: 180
  lpointing: null
  bpointing: null
  maplistgen: "None"

maps:
  mapsize: 40
  useEDPmatrixforEXP: false
  expstep: null
  spectralindex: 2.1
  timestep: 160
  projtype: WCS
  proj: ARC
  binsize: 0.25
  energybins:
    - 100, 10000
  fovbinnumber: 1
  offaxisangle: 30

model:
  modelfile: null
  galmode: 1
  isomode: 1
  galcoeff: null
  isocoeff: null
  galmode2: 0
  galmode2fit: 0
  isomode2: 0
  isomode2fit: 0

mle:
  ranal: 10
  ulcl: 2
  loccl: 95
  expratioevaluation: true
  expratio_minthr: 0
  expratio_maxthr: 15
  expratio_size: 10
  minimizertype: Minuit
  minimizeralg: Migrad
  minimizerdefstrategy: 2
  mindefaulttolerance: 0.01
  integratortype: 1
  contourpoints: 40
  edpcorrection: 1
  fluxcorrection: 0

ap:
  radius: 3
  timeslot: 3600

plotting:
  twocolumns: False

        """

        with open(Utils._expandEnvVar(confFilePath),"w") as cf:

            cf.write(configuration)



    ############################################################################
    # sources management                                                       #
    ############################################################################

    def loadSourcesFromCatalog(self, catalogName, rangeDist = (0, float("inf")), show=False):
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
        return self.sourcesLibrary.loadSourcesFromCatalog(catalogName, rangeDist, show = show)

    def loadSourcesFromFile(self, sourcesFilepath, rangeDist = (0, float("inf")), show=False):
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
        return self.sourcesLibrary.loadSourcesFromFile(sourcesFilepath, rangeDist, show = show)

    def selectSources(self, selection, show=False):
        """It returns the sources matching the selection criteria from the ``sourcesLibrary``.

        The sources can be selected with the ``selection`` argument, supporting either ``lambda functions`` and
        ``boolean expression strings``.

        The selection criteria can be expressed using the following ``Source`` class's parameters:

        - name: the unique code identifying the source.
        - dist: the distance of the source from the center of the maps.
        - flux: the flux value.
        - sqrtts: the radix square of the ts.

        Warning:

            The sqrtts parameter is available only after the maximum likelihood estimation analysis is performed.

        Args:
            selection (lambda or str): a lambda function or a boolean expression string specifying the selection criteria.
            quiet (boolean) (optional default=False): if quiet is True, the method will not console log the selected sources.

        Returns:
            List of sources.
        """
        return self.sourcesLibrary.selectSources(selection, show =show)

    def freeSources(self, selection, parameterName, free, show=False):
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
        - pos


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
        return self.sourcesLibrary.freeSources(selection, parameterName, free, show)

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

    def deleteSources(self, selection, show = False):
        """It deletes the sources matching the selection criteria from the ``sourcesLibrary``.

        Args:
            selection (lambda or str): a lambda function or a boolean expression string specifying the selection criteria.

        Returns:
            The list containing the deleted sources.
        """
        return self.sourcesLibrary.deleteSources(selection, show = show)

    def getSources(self):
        """It returns all the sources.
            Returns:
                List of sources.
        """
        return self.sourcesLibrary.sources

    def updateSourcePosition(self, sourceName, glon, glat):
        """It updates a source (l,b) position parameters. The 'dist' value will also be updated.

        Args:
            sourceName (str): the name of the source
            glon (float): galactic longitude.
            glat (float): galactic latitude.

        Raises:
            SourceNotFound: if the source has not been loaded into the SourcesLibrary.
            ValueError: if glon or glat values are out of range.

        Returns:
            True if the position changes, False otherwise.
        """
        return self.sourcesLibrary.updateSourcePosition(sourceName, glon, glat)

    def writeSourcesOnFile(self, outfileNamePrefix, fileFormat, sources=None):
        """It writes on file the list of sources loaded into the *SourceLibrary*.
        The supported formats ('txt' AND 'xml') are described here: :ref:`sources-file`.

        Args:
            outfileNamePrefix (str): the name of the output file (without the extension).
            fileFormat (str): Possible values: ['txt', 'xml', 'reg'].
            sources (List<Source>): a list of Source objects. If is is None, every loaded source will be written on file.

        Raises:
            SourceModelFormatNotSupported: if the file format is not supported.

        Returns:
            Path to the file
        """
        return self.sourcesLibrary.writeToFile(outfileNamePrefix, fileformat=fileFormat, sources=sources)

    def setOptionTimeMJD(self, tmin, tmax):
        """It performs a time conversion MJD -> TT and set new values using setOptions functions
        
        Args:
            tmin(float): tmin in MJD 
            tmax(float): tmax in MJD

        """

        self.config.setOptions(tmin=AstroUtils.time_mjd_to_agile_seconds(tmin), tmax=AstroUtils.time_mjd_to_agile_seconds(tmax), timetype="TT")

    def setOptionEnergybin(self, value):
        """An useful utility method that maps a value in a specific energybin and it calls the setOptions function.

        Args:
            Value (int): A value between 0 and 5  

                - 0: [[100, 10000]]  
                - 1: [[100, 50000]]  
                - 2: [[100, 300], [300, 1000], [1000, 3000], [3000, 10000]]  
                - 3: [[100, 300], [300, 1000], [1000, 3000], [3000, 10000], [10000, 50000]]
                - 4: [[50, 100], [100, 300], [300, 1000], [1000, 3000], [3000, 10000]]
                - 5: [[50, 100], [100, 300], [300, 1000], [1000, 3000], [3000, 10000], [10000, 50000]]
        
        Raises:
            ValueOutOfRange: if the value is not between 0 and 5.
        """

        if value < 0 or value > 5:
            self.logger.critical(self, "Value out of range, possible values [0, 1, 2, 3, 4, 5]")
            raise ValueOutOfRange("Value out of range, possible values[0, 1, 2, 3, 4, 5]")

        elif value == 0:
            self.config.setOptions(energybins=[[100, 10000]])
        
        elif value == 1:
            self.config.setOptions(energybins=[[100, 50000]])

        elif value == 2:
            self.config.setOptions(
                energybins=[[100, 300], [300, 1000], [1000, 3000], [3000, 10000]])

        elif value == 3:
            self.config.setOptions(energybins=[[100, 300], [300, 1000], [
                                   1000, 3000], [3000, 10000], [10000, 50000]])
        
        elif value == 4:
            self.config.setOptions(energybins=[[50, 100], [100, 300], [
                                   300, 1000], [1000, 3000], [3000, 10000]])

        elif value == 5:
            self.config.setOptions(energybins=[[50, 100], [100, 300], [300, 1000], [
                                   1000, 3000], [3000, 10000], [10000, 50000]])

    ############################################################################
    # analysis                                                                 #
    ############################################################################

    def generateMaps(self, config = None, maplistObj = None, dqdmOff = False):
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
            self.currentMapList.reset()
            maplistObjBKP = self.currentMapList


        fovbinnumber = configBKP.getOptionValue("fovbinnumber")
        energybins = configBKP.getOptionValue("energybins")
            

        initialFovmin = configBKP.getOptionValue("fovradmin")
        initialFovmax = configBKP.getOptionValue("fovradmax")
        initialFileNamePrefix = configBKP.getOptionValue("filenameprefix")

        tmin = configBKP.getOptionValue("tmin")
        tmax = configBKP.getOptionValue("tmax")
        timetype = configBKP.getOptionValue("timetype")

        ####### REST API #######

        if configBKP.getOptionValue("userestapi"):
            if timetype == "TT":
                tminRest = AstroUtils.time_agile_seconds_to_mjd(tmin)
                tmaxRest = AstroUtils.time_agile_seconds_to_mjd(tmax)
            self.agdataset.downloadData(tminRest, tmaxRest, configBKP.getOptionValue("datapath"), configBKP.getOptionValue("evtfile"), configBKP.getOptionValue("logfile"))

        
        if timetype == "MJD":
            tmin =  AstroUtils.time_mjd_to_agile_seconds(tmin)
            tmax =  AstroUtils.time_mjd_to_agile_seconds(tmax)    
            configBKP.setOptions(tmin=tmin, tmax=tmax, timetype="TT")

        glon = configBKP.getOptionValue("glon")
        glat = configBKP.getOptionValue("glat")

        # Creating the output directory if it does not exist
        outputDir = Path(configBKP.getConf("output","outdir")).joinpath("maps")
        outputDir.mkdir(exist_ok=True, parents=True)
        outputDir = Utils._createNextSubDir(outputDir)
        configBKP.setOptions(outdir=str(outputDir))

        # Change the maplist file path
        maplistObjBKP.setFile(outputDir)

        if not dqdmOff:
            print("Generating maps..please wait.")
    
        for stepi in trange(0, fovbinnumber, desc=f"Fov bins loop", disable=dqdmOff, leave=dqdmOff):

            if fovbinnumber == 1:
                bincenter = 30
                fovmin = initialFovmin
                fovmax = initialFovmax
            else:
                bincenter, fovmin, fovmax = AGAnalysis._updateFovMinMaxValues(fovbinnumber, initialFovmin, initialFovmax, stepi+1)


            for bgCoeffIdx, stepe in tqdm(enumerate(energybins), desc=f"Energy bins loop", disable=dqdmOff, leave=dqdmOff):

                if Parameters.checkEnergyBin(stepe):

                    emin = stepe[0]
                    emax = stepe[1]

                    skymapL = Parameters.getSkyMap(emin, emax)
                    skymapH = Parameters.getSkyMap(emin, emax)
                    fileNamePrefix = Parameters.getMapNamePrefix(tmin, tmax, emin, emax, glon, glat, stepi+1)

                    self.logger.debug(self, "Map generation => fovradmin %s fovradmax %s bincenter %s emin %s emax %s fileNamePrefix %s skymapL %s skymapH %s", \
                                       fovmin,fovmax,bincenter,emin,emax,fileNamePrefix,skymapL,skymapH)


                    configBKP.setOptions(filenameprefix=initialFileNamePrefix+"_"+fileNamePrefix)
                    configBKP.setOptions(dq=0, fovradmin=int(fovmin), fovradmax=int(fovmax))
                    configBKP.addOptions("selection", emin=int(emin), emax=int(emax))
                    configBKP.addOptions("maps", skymapL=skymapL, skymapH=skymapH)


                    ctsMapGenerator = CtsMapGenerator("AG_ctsmapgen", self.logger)
                    expMapGenerator = ExpMapGenerator("AG_expmapgen", self.logger)
                    gasMapGenerator = GasMapGenerator("AG_gasmapgen", self.logger)
                    intMapGenerator = IntMapGenerator("AG_intmapgen", self.logger)

                    ctsMapGenerator.configureTool(configBKP)
                    expMapGenerator.configureTool(configBKP)
                    gasMapGenerator.configureTool(configBKP, {"expMapGeneratorOutfilePath": next(iter(expMapGenerator.products.items()))[0]})
                    intMapGenerator.configureTool(configBKP, {"expMapGeneratorOutfilePath": next(iter(expMapGenerator.products.items()))[0], "ctsMapGeneratorOutfilePath" : next(iter(ctsMapGenerator.products.items()))[0]})

                    configBKP.addOptions("maps", expmap=next(iter(expMapGenerator.products.items()))[0], ctsmap=next(iter(ctsMapGenerator.products.items()))[0])

                    if not ctsMapGenerator.allRequiredOptionsSet(configBKP) or \
                       not expMapGenerator.allRequiredOptionsSet(configBKP) or \
                       not gasMapGenerator.allRequiredOptionsSet(configBKP) or \
                       not intMapGenerator.allRequiredOptionsSet(configBKP):

                        raise ScienceToolInputArgMissing("Some options have not been set.")

                    f1 = ctsMapGenerator.call()

                    f2 = expMapGenerator.call()

                    f3 = gasMapGenerator.call()

                    f4 = intMapGenerator.call()

                    maplistObjBKP.addRow(   next(iter(ctsMapGenerator.products.items()))[0], \
                                            next(iter(expMapGenerator.products.items()))[0], \
                                            next(iter(gasMapGenerator.products.items()))[0], \
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

    def calcBkg(self, sourceName, galcoeff = None, pastTimeWindow = 14.0, excludeTmaxTmin=False):
        """It estimates the isotropic and galactic background coefficients.

        Note: 
            The current value of the isotropic and galactic bkg coeffs will be set to -1 in order \
            to be free to vary during the fit. It automatically updates the configuration.

        Args:
            sourceName (str): the name of the source under analysis.
            galcoeff (List, optional): the galactic background coefficients (one for each map).
            pastTimeWindow (float, optional): the number of days previous tmin. It defaults to 14. If \
                it's 0, the background coefficients will be estimated within the [tmin, tmax] interval.
            excludeTmaxTmin (bool, optional): if this value is True (defalut=False) and pasttimewindow > 0 the calcbkg method computes coeffs \
                between [tmin-pastTimeWindow, tmin] instead of [tmin-pastTimeWindow, tmax]

        Returns:
            galactic coefficients, isotropic coefficients, maplist file (List, List, str): the estimates of the background coefficients and the \
                path to the updated maplist file.


        """
        print("Computing background coefficients..please wait.")

        timeStart = time()


        ################################################################## checks
        self.sourcesLibrary.backupSL()

        inputSource = self.selectSources(f'name == "{sourceName}"', show=False)

        if not inputSource:
            self.logger.critical(self, "The source %s has not been loaded yet", sourceName)
            raise SourceNotFound(f"The source {sourceName} has not been loaded yet")



        ######################################################## configurations

        analysisDataDir = Path(self.config.getOptionValue("outdir")).joinpath("calcBkg")

        configBKP = AgilepyConfig.getCopy(self.config)
        configBKP.setOptions(filenameprefix="calcBkg", outdir=str(analysisDataDir))


        numberOfBkgCoeffs = len(configBKP.getOptionValue("energybins"))*configBKP.getOptionValue("fovbinnumber")

        # isocoeff is always resetted to -1 in order to be free to vary during the fit
        configBKP.setOptions(isocoeff=[-1 for _ in range(numberOfBkgCoeffs)])

        # is galcoeff is None, it is set to -1 in order to be free to vary during the fit
        if galcoeff is None:
            configBKP.setOptions(galcoeff=[-1 for _ in range(numberOfBkgCoeffs)])

        

        ######################################################## Own MapList
        maplistObj = MapList(self.logger)
        configBKP.attach(maplistObj, "galcoeff")
        configBKP.attach(maplistObj, "isocoeff")

        print(maplistObj)



        ################################################################# times
        tmin = self.config.getOptionValue("tmin")
        tmax = self.config.getOptionValue("tmax")
        timetype = self.config.getOptionValue("timetype")

        if timetype == "MJD":
            tmin = AstroUtils.time_mjd_to_agile_seconds(tmin)
            tmax = AstroUtils.time_mjd_to_agile_seconds(tmax)

        if pastTimeWindow == 0 and not excludeTmaxTmin:
            tmin = tmin
        elif pastTimeWindow > 0 and not excludeTmaxTmin:
            tmin = tmin - 86400*abs(pastTimeWindow)
        elif pastTimeWindow > 0 and excludeTmaxTmin:
            tmax = tmin
            tmin = tmin - 86400*abs(pastTimeWindow)
        elif pastTimeWindow == 0 and excludeTmaxTmin:
            raise SelectionParamNotSupported("Cannot compute coeffs with pasttimewindow 0 and excludetmaxtmin True")

        self.logger.info(self, "tmin: %f tmax: %f type: %s", tmin, tmax, timetype)
        configBKP.setOptions(tmin = tmin, tmax = tmax, timetype = "TT")



        ######################################################## maps generation
        maplistFilePath = self.generateMaps(config = configBKP, maplistObj = maplistObj)




        ############################################################## galcoeff
        if galcoeff is not None:
            configBKP.setOptions(galcoeff=galcoeff)



        #################################### fixflag = 0 except for input source
        for s in self.sourcesLibrary.sources:
            self.fixSource(s)

        # "sourceName" must have flux = 1
        self.freeSources(f'name == "{sourceName}"', "flux", True)




        #################################################################### mle
        #configBKP.setOptions(filenameprefix = "calcBkg", outdir = str(analysisDataDir))
        #configBKP.setOptions(tmin = tmin, tmax = tmax, timetype = "TT")
        sourceFiles = self.mle(maplistFilePath = maplistFilePath, config = configBKP, updateSourceLibrary = False)





        # extract iso e gal coeff of "sourceName"
        isoCoeff, galCoeff = self._extractBkgCoeff(sourceFiles, sourceName)

        self.logger.info(self, f"New isoCoeff: {isoCoeff}, New galCoeff: {galCoeff}")

        self.sourcesLibrary.restoreSL()
        # check if self.maplist exist
        self.config.setOptions(galcoeff=galCoeff, isocoeff=isoCoeff)

        self.logger.info(self, "Took %f seconds.", time()-timeStart)

        return galCoeff, isoCoeff, maplistFilePath

    def mle(self, maplistFilePath = None, config = None, updateSourceLibrary = True, position="ellipse"):
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

        if len(self.sourcesLibrary.sources) == 0:

            raise SourcesLibraryIsEmpty("No sources have been laoded yet.")
            

        if not maplistFilePath:

            maplistFilePath = self.currentMapList.getFile()

        # Creating the output directory if it does not exist
        outputDir = Path(configBKP.getConf("output","outdir")).joinpath("mle")
        outputDir.mkdir(exist_ok=True, parents=True)
        outputDir = Utils._createNextSubDir(outputDir)
        configBKP.setOptions(outdir=str(outputDir))

        # The multi tools needs to know which maps (maplistfile) it will consider during the analysis.
        configBKP.addOptions("selection", maplist=maplistFilePath)

        # The multi tools needs to know which which sources (in AGILE format) it will consider during the analysis.
        sourceListFilename = "sourceLibrary"+(str(self.multiTool.callCounter).zfill(5))
        sourceListAgileFormatFilePath = self.sourcesLibrary.writeToFile(outfileNamePrefix=outputDir.joinpath(sourceListFilename), fileformat="txt", position=position)
        configBKP.addOptions("selection", sourcelist=sourceListAgileFormatFilePath)

        # The multi tools needs to know the name of the sources it will consider during the analysis.
        multisources = self.sourcesLibrary.getSourcesNames()
        configBKP.addOptions("selection", multisources=multisources)




        self.multiTool.configureTool(configBKP)

        products = self.multiTool.call()

        # filter .source files
        sourceFiles = [product for product in products if product and ".source" in product]

        if len(sourceFiles) == 0:
            self.logger.warning(self, "The number of .source files is 0.")

        self.logger.info(self,"AG_multi produced: %s", sourceFiles)

        if updateSourceLibrary:

            for sourceFile in sourceFiles:

                multiOutputData = self.sourcesLibrary.parseSourceFile(sourceFile)

                self.sourcesLibrary.updateSourceWithMLEResults(multiOutputData)

        self.logger.info(self, "Took %f seconds.", time()-timeStart)

        return sourceFiles

    def lightCurveMLE(self, sourceName, tmin = None, tmax = None, timetype = None, binsize = 86400, position="ellipse"):
        """It generates a cvs file containing the data for a light curve plot.

        Args:
            sourceName (str): the name of the source under analysis.
            tmin (float, optional): starting point of the light curve. It defaults to None. If None the 'tmin' value of the configuration file will be used.
            tmax (float, optional): ending point of the light curve. It defaults to None. If None the 'tmax' value of the configuration file will be used.
            timetype (str, optional): the time format ('MJD' or 'TT'). It defaults to None. If None the 'timetype' value of the configuration file will be used.
            binsize (int, optional): temporal bin size. It defaults to 86400.
            position (str, optional): the position of the source: {"ellipse", "peak", "initial"}

        Returns:
            The absolute path to the light curve data output file.
        """
        print("Computing light curve bins..please wait.")

        timeStart = time()

        if not tmin or not tmax or not timetype:
            tmin = self.config.getOptionValue("tmin")
            tmax = self.config.getOptionValue("tmax")
            timetype = self.config.getOptionValue("timetype")
        
        if timetype == "MJD":
            if self.config.getOptionValue("userestapi"):
                self.agdataset.downloadData(tmin, tmax, self.config.getOptionValue("datapath"), self.config.getOptionValue("evtfile"), self.config.getOptionValue("logfile"))

            tmin = AstroUtils.time_mjd_to_agile_seconds(tmin)
            tmax = AstroUtils.time_mjd_to_agile_seconds(tmax)
        
        if self.config.getOptionValue("userestapi"):    
            self.agdataset.downloadData(AstroUtils.time_agile_seconds_to_mjd(tmin), AstroUtils.time_agile_seconds_to_mjd(tmax), self.config.getOptionValue("datapath"), self.config.getOptionValue("evtfile"), self.config.getOptionValue("logfile"))
            
        bins = [(t1, t1 + binsize) for t1 in np.arange(tmin, tmax, binsize)]

        tstart = bins[0][0]
        tstop = bins[-1][1]

        self.logger.info(self,f"[LC] Using the tmin {tmin}, tmax {tmax}, number of temporal bins: {len(bins)}.")


        processes = 1
        binsForProcesses = AGAnalysis._chunkList(bins, processes)

        configBKP = AgilepyConfig.getCopy(self.config)

        # Creating the output directory if it does not exist
        lcAnalysisDataDir = Path(configBKP.getConf("output","outdir")).joinpath("lc")
        lcAnalysisDataDir.mkdir(exist_ok=True, parents=True)
        lcAnalysisDataDir = Utils._createNextSubDir(lcAnalysisDataDir)
        configBKP.setOptions(outdir=str(lcAnalysisDataDir))

        (_, last) = Utils._getFirstAndLastLineInFile(configBKP.getConf("input", "evtfile"))
        idxTmax = float(Utils._extractTimes(last)[1])

        # logFilenamePrefix = configBKP.getConf("output","logfilenameprefix")
        # verboseLvl = configBKP.getConf("output","verboselvl")

        self.logger.info(self, f"[LC] Number of processes: {processes}, Number of bins per process {len(binsForProcesses[0])}")

        idx = 0
        for bin in tqdm(bins, desc="Temporal bin loop"):

            t1 = bin[0]
            t2 = bin[1]

            if t2 > idxTmax:
                newbinsize = idxTmax - t1
                self.logger.warning(self, f"[LC] The last bin [{t1}, {t2}] of the light curve analysis falls outside the range of the available data [.. , {idxTmax}]. The binsize is reduced to {newbinsize} seconds, the new bin is [{t1}, {idxTmax}]")
                t2 = idxTmax

            self.logger.warning(self,f"[LC] Analysis of temporal bin: [{t1},{t2}] {idx+1}/{len(bins)}")

            #binOutDir = str(lcAnalysisDataDir.joinpath(f"bin_{t1}_{t2}"))

            binOutDir = str(lcAnalysisDataDir.joinpath(f"{idx}_bin_{t1}_{t2}"))


            configBKP.setOptions(filenameprefix="lc_analysis", outdir=binOutDir)
            configBKP.setOptions(tmin = t1, tmax = t2, timetype = "TT")
            

            maplistObj = MapList(self.logger)

            maplistFilePath = self.generateMaps(config=configBKP, maplistObj=maplistObj, dqdmOff=False)

            configBKP.setOptions(filenameprefix="lc_analysis", outdir = binOutDir)
            configBKP.setOptions(tmin = t1, tmax = t2, timetype = "TT")
            _ = self.mle(maplistFilePath = maplistFilePath, config = configBKP, updateSourceLibrary = False, position=position)

            idx += 1
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

        lcData = self._getLightCurveData(sourceName, lcAnalysisDataDir, binsize)

        lcOutputFilePath = Path(lcAnalysisDataDir).joinpath(f"light_curve_{tstart}_{tstop}.txt")

        with open(lcOutputFilePath, "w") as lco:
            lco.write(lcData)

        self.logger.info(self, "Light curve created in %s", lcOutputFilePath)

        self.logger.info(self, "Took %f seconds.", time()-timeStart)

        self.lightCurveData["mle"] = str(lcOutputFilePath)

        return str(lcOutputFilePath)

    def aperturePhotometry(self):
        """It generates a cvs file containing the data for a light curve plot.
        The method's behaviour varies according to several configuration options (see docs :ref:`configuration-file`).

        Returns:
            The absolute path to the light curve data output file.

        Raises:
            ScienceToolInputArgMissing: if not all the required configuration options have been set.
        """
        apTool = AP("AG_ap", self.logger)

        apTool.configureTool(self.config)

        if not apTool.allRequiredOptionsSet(self.config):

            raise ScienceToolInputArgMissing("Some options have not been set.")

        products = apTool.call()
        self.logger.info(self, f"Science tool AP produced:\n {products}")

        self.lightCurveData["ap"] = products[0]

        return products[0], products[1] 


    ############################################################################
    # visualization                                                            #
    ############################################################################


    def displayCtsSkyMaps(self, maplistFile=None, singleMode=True, smooth=4.0, saveImage=False, fileFormat=".png", title=None, cmap="CMRmap", regFiles=None, regFileColors=[], catalogRegions=None, catalogRegionsColor="red", normType="linear"):
        """It displays the last generated cts skymaps.

        Args:
            maplistFile (str, optional): the path to the .maplist file. If not specified, the last generated maplist file will be used. It defaults to None.
            singleMode (bool, optional): if set to true, all maps will be displayed as subplots on a single figure. It defaults to True.
            smooth (float, optional): the sigma value of the gaussian smoothing. It defaults to 4.0.
            saveImage (bool, optional): if set to true, saves the image into the output directory. It defaults to False.
            fileFormat (str, optional): the extension of the output image. It defaults to '.png' .
            title (str, optional): the title of the image. It defaults to None.
            cmap (str, optional): Matplotlib colormap. It defaults to 'CMRmap'. Colormaps: https://matplotlib.org/tutorials/colors/colormaps.html
            regFiles (list, optional): A list containing region file(s) absolute path.
            regFileColors(list, optional): A list with a color for each region file, the length must be the same of regFiles.
            catalogRegions(str, optional): a catalog name. The regions that belongs to the catalog will be loaded. It defaults to None.
            catalogRegionsColor(str, optional): the color of the regions loaded from the catalog.
            normType (str, optional): It selects a normalization function for the data, possible valuses {‘linear’, ‘sqrt’, ‘power’, log’, ‘asinh’}, default 'linear'.

        Returns:
            It returns the paths to the image files written on disk.
        """
        print("Generating plot..please wait.")

        return self._displaySkyMaps("CTS",  singleMode, maplistFile, smooth, saveImage, fileFormat, title, cmap, regFiles, regFileColors, catalogRegions, catalogRegionsColor, normType)

    def displayExpSkyMaps(self, maplistFile=None, singleMode=True, smooth=False, sigma=4.0, saveImage=False, fileFormat=".png", title=None, cmap="CMRmap", regFiles=None, regFileColors=[], catalogRegions=None, catalogRegionsColor="red", normType="linear"):
        """It displays the last generated exp skymaps.

        Args:
            maplistFile (str, optional): the path to the .maplist file. If not specified, the last generated maplist file will be used. It defaults to None.
            singleMode (bool, optional): if set to true, all maps will be displayed as subplots on a single figure. It defaults to True.
            smooth (float, optional): the sigma value of the gaussian smoothing. It defaults to 4.0.
            saveImage (bool, optional): if set to true, saves the image into the output directory. It defaults to False.
            fileFormat (str, optional): the extension of the output image. It defaults to '.png' .
            title (str, optional): the title of the image. It defaults to None.
            cmap (str, optional): Matplotlib colormap. It defaults to 'CMRmap'. Colormaps: https://matplotlib.org/tutorials/colors/colormaps.html
            regFiles (list, optional): A list containing region file(s) absolute path
            regFileColors(list, optional): A list with a color for each region file, the length must be the same of regFiles
            catalogRegions(str, optional): a catalog name. The regions that belongs to the catalog will be loaded. It defaults to None.
            catalogRegionsColor(str, optional): the color of the regions loaded from the catalog.
            normType (str, optional): It selects a normalization function for the data, possible valuses {‘linear’, ‘sqrt’, ‘power’, log’, ‘asinh’}, default 'linear'.


        Returns:
            It returns the paths to the image files written on disk.
        """
        print("Generating plot..please wait.")

        return self._displaySkyMaps("EXP", singleMode, maplistFile, smooth, saveImage, fileFormat, title, cmap, regFiles, regFileColors, catalogRegions, catalogRegionsColor, normType)

    def displayGasSkyMaps(self, maplistFile=None, singleMode=True, smooth=False, sigma=4.0, saveImage=False, fileFormat=".png", title=None, cmap="CMRmap", regFiles=None, regFileColors=[], catalogRegions=None, catalogRegionsColor="red", normType="linear"):
        """It displays the last generated gas skymaps.

        Args:
            maplistFile (str, optional): the path to the .maplist file. If not specified, the last generated maplist file will be used. It defaults to None.
            singleMode (bool, optional): if set to true, all maps will be displayed as subplots on a single figure. It defaults to True.
            smooth (float, optional): the sigma value of the gaussian smoothing. It defaults to 4.0.
            saveImage (bool, optional): if set to true, saves the image into the output directory. It defaults to False.
            fileFormat (str, optional): the extension of the output image. It defaults to '.png' .
            title (str, optional): the title of the image. It defaults to None.
            cmap (str, optional): Matplotlib colormap. It defaults to 'CMRmap'. Colormaps: https://matplotlib.org/tutorials/colors/colormaps.html
            regFiles (list, optional): A list containing region file(s) absolute path
            regFileColors(list, optional): A list with a color for each region file, the length must be the same of regFiles
            catalogRegions(str, optional): a catalog name. The regions that belongs to the catalog will be loaded. It defaults to None.
            catalogRegionsColor(str, optional): the color of the regions loaded from the catalog.
            normType (str, optional): It selects a normalization function for the data, possible valuses {‘linear’, ‘sqrt’, ‘power’, log’, ‘asinh’}, default 'linear'.


        Returns:
            It returns the paths to the image files written on disk.
        """
        print("Generating plot..please wait.")

        return self._displaySkyMaps("GAS", singleMode, maplistFile, smooth, saveImage, fileFormat, title, cmap, regFiles, regFileColors, catalogRegions, catalogRegionsColor, normType)

    def displayIntSkyMaps(self, maplistFile=None, singleMode=True, smooth=False, sigma=4.0, saveImage=False, fileFormat=".png", title=None, cmap="CMRmap", regFiles=None, regFileColors=[], catalogRegions=None, catalogRegionsColor="red", normType="linear"):
        """It displays the last generated int skymaps.

        Args:
            maplistFile (str, optional): the path to the .maplist file. If not specified, the last generated maplist file will be used. It defaults to None.
            singleMode (bool, optional): if set to true, all maps will be displayed as subplots on a single figure. It defaults to True.
            smooth (float, optional): the sigma value of the gaussian smoothing. It defaults to 4.0.
            saveImage (bool, optional): if set to true, saves the image into the output directory. It defaults to False.
            fileFormat (str, optional): the extension of the output image. It defaults to '.png' .
            title (str, optional): the title of the image. It defaults to None.
            cmap (str, optional): Matplotlib colormap. It defaults to 'CMRmap'. Colormaps: https://matplotlib.org/tutorials/colors/colormaps.html
            regFiles (list, optional): A list containing region file(s) absolute path
            regFileColors(list, optional): A list with a color for each region file, the length must be the same of regFiles
            catalogRegions(str, optional): a catalog name. The regions that belongs to the catalog will be loaded. It defaults to None.
            catalogRegionsColor(str, optional): the color of the regions loaded from the catalog.
            normType (str, optional): It selects a normalization function for the data, possible valuses {‘linear’, ‘sqrt’, ‘power’, log’, ‘asinh’}, default 'linear'.


        Returns:
            It returns the paths to the image files written on disk.
        """
        print("Generating plot..please wait.")

        return self._displaySkyMaps("INT", singleMode, maplistFile, smooth, saveImage, fileFormat, title, cmap, regFiles, regFileColors, catalogRegions, catalogRegionsColor, normType)

    def displayLightCurve(self, analysisName, filename=None, lineValue=None, lineError=None, saveImage=False, fermiLC = None):
        """It displays the light curve plot. You can call this method after lightCurveMLE() or aperturePhotometry().
        If you pass a filename containing the light curve data, this file will be used instead of using the data generated 
        by the mentioned methods. 

        Args:
            analysisName (str, required): the analysis used to generate the light curve data: choose between 'mle' or 'ap'.
            filename (str, optional): the path of the Lightcurve text data file. It defaults to None. If None the last generated file will be used.
            lineValue (int, optional): mean flux value. It defaults to None.
            lineError (int, optional): mean flux error lines. It defaults to None.
            saveImage (bool, optional): if set to true, saves the image into the output directory. It defaults to False.
            fermiLC (str, optional): the path of FERMI lightcurve data

        Returns:
            It returns the lightcurve plot

        """
        print("Generating plot..please wait.")

        if analysisName is None:
            self.logger.warning(self, "analysisName cannot be null.")
            return False

        if analysisName not in ["mle", "ap"]:
            self.logger.warning(self, "The analysisName={} is not supported. You can choose between 'mle' and 'ap'.")
            return False

        if (filename is None) and (self.lightCurveData["mle"] is None) and (self.lightCurveData["ap"] is None):
            self.logger.warning(self, "The light curve has not been generated yet and the filename is None. Please, call lightCurveMLE() or aperturePhotometry() or pass a valid filename")
            return False


        if filename is not None and analysisName == "mle":
            return self.plottingUtils.plotLc(filename, lineValue, lineError, saveImage, fermiLC)

        if filename is not None and analysisName == "ap":
            return self.plottingUtils.plotSimpleLc(filename, lineValue, lineError)


        if analysisName == "mle" and self.lightCurveData["mle"] is None:
            self.logger.warning(self, "The light curve has not been generated yet. Please, lightCurveMLE().")
            return False

        if analysisName == "ap" and self.lightCurveData["ap"] is None:
            self.logger.warning(self, "The light curve has not been generated yet. Please, aperturePhotometry().")
            return False

        if self.lightCurveData[analysisName] is not None and analysisName=="mle":
            return self.plottingUtils.plotLc(self.lightCurveData[analysisName], lineValue, lineError, saveImage=saveImage, fermiLC=fermiLC)

        if self.lightCurveData[analysisName] is not None and analysisName=="ap":
            return self.plottingUtils.plotSimpleLc(self.lightCurveData[analysisName], lineValue, lineError, saveImage=saveImage)

    def displayGenericColumns(self, filename, columns, um=None, saveImage=False):
        """An utility method for viewing a generic column from the lightcurvedata

        Args:
            filename (str): the path of the Lightcurve text data file. It defaults to None. If None the last generated file will be used.
            columns (array of str): the name of the columns to display(first display is always LC), possible values:
                (time_start_mjd | time_end_mjd | sqrt(ts) | flux | flux_err | flux_ul | gal | gal_error | iso | iso_error | l_peak | b_peak | dist_peak | l | b | r | 
                ell_dist | a | b | phi | exposure | ExpRatio | counts | counts_err | Index | Index_Err | Par2 | Par2_Err | Par3 | Par3_Err | Erglog | Erglog_Err | Erglog_UL |
                time_start_utc | time_end_utc | time_start_tt | time_end_tt | Fix | index | ULConfidenceLevel | SrcLocConfLevel | start_l | start_b | start_flux | 
                typefun | par2 | par3 | galmode2 | galmode2fit | isomode2 | isomode2fit | edpcor | fluxcor | integratortype | expratioEval | 
                expratio_minthr | expratio_maxthr | expratio_size | Emin | emax | fovmin | fovmax | albedo | binsize | expstep | phasecode | fit_cts | fit_fitstatus0 | 
                fit_fcn0 | fit_edm0 | fit_nvpar0 | fit_nparx0 | fit_iter0 | fit_fitstatus1 | fit_fcn1 | fit_edm1 | fit_nvpar1 | fit_nparx1 | fit_iter1 | fit_Likelihood1)
            
            um (array of str): unit of measurement, same length of columns
            saveImage (bool): if set to true, saves the image into the output directory. It defaults to False.

        Returns:
            If saveImage is true tha path of the image otherwise the plot
        """
        return self.plottingUtils.plotGenericColumns(filename, columns, um, saveImage)


    ############################################################################
    # utility                                                                  #
    ############################################################################

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


    ############################################################################
    # private methods                                                          #
    ############################################################################

    def _getLightCurveData(self, sourceName, lcAnalysisDataDir, binsize):

        binDirectories = sorted(os.listdir(lcAnalysisDataDir))

        lcData = "time_start_mjd time_end_mjd sqrt(ts) flux flux_err flux_ul gal gal_error iso iso_error l_peak b_peak dist_peak " \
        "l b r ell_dist a b phi exposure ExpRatio counts counts_err Index Index_Err Par2 Par2_Err Par3 Par3_Err Erglog Erglog_Err " \
        "Erglog_UL time_start_utc time_end_utc time_start_tt time_end_tt Fix index ULConfidenceLevel SrcLocConfLevel start_l start_b start_flux " \
        "typefun par2 par3 galmode2 galmode2fit isomode2 isomode2fit edpcor fluxcor integratortype expratioEval expratio_minthr expratio_maxthr " \
        "expratio_size Emin emax fovmin fovmax albedo binsize expstep phasecode fit_cts fit_fitstatus0 fit_fcn0 fit_edm0 fit_nvpar0 fit_nparx0 fit_iter0 " \
        "fit_fitstatus1 fit_fcn1 fit_edm1 fit_nvpar1 fit_nparx1 fit_iter1 fit_Likelihood1\n"
        
        timecounter = 0

        for bd in binDirectories:

            mleOutputDirectories = Path(lcAnalysisDataDir).joinpath(bd,"mle","0")

            mleOutputFiles = os.listdir(mleOutputDirectories)

            for mleOutputFile in mleOutputFiles:

                mleOutputFilename, mleOutputFileExtension = splitext(mleOutputFile)

                if mleOutputFileExtension == ".source" and sourceName in mleOutputFilename:

                    mleOutputFilepath = mleOutputDirectories.joinpath(mleOutputFile)

                    lcDataDict = self._extractLightCurveDataFromSourceFile(str(mleOutputFilepath))

                    time_start_tt = lcDataDict["time_start_tt"] # + binsize * timecounter
                    time_end_tt   = lcDataDict["time_end_tt"]   # + binsize * timecounter

                    time_start_mjd = AstroUtils.time_agile_seconds_to_mjd(time_start_tt)
                    time_end_mjd   = AstroUtils.time_agile_seconds_to_mjd(time_end_tt)

                    time_start_utc = AstroUtils.time_mjd_to_fits(time_start_mjd)
                    time_end_utc   = AstroUtils.time_mjd_to_fits(time_end_mjd)

                    # time_start_mjd time_end_mjd sqrt(ts) flux flux_err flux_ul gal gal_error iso iso_error l_peak b_peak dist
                    # l b r ell_dist a b phi exposure ExpRatio counts counts_err Index Index_Err Par2 Par2_Err Par3 Par3_Err Erglog Erglog_Err
                    # Erglog_UL time_start_utc time_end_utc time_start_tt time_end_tt Fix index ULConfidenceLevel SrcLocConfLevel start_l start_b start_flux
                    # typefun par2 par3 galmode2 galmode2fit isomode2 isomode2fit edpcor fluxcor integratortype expratioEval expratio_minthr expratio_maxthr
                    # expratio_size Emin emax fovmin fovmax albedo binsize expstep phasecode fit_cts fit_fitstatus0 fit_fcn0 fit_edm0 fit_nvpar0 fit_nparx0 fit_iter0
                    # fit_fitstatus1 fit_fcn1 fit_edm1 fit_nvpar1 fit_nparx1 fit_iter1 fit_Likelihood1

                    if "nan" in lcDataDict['flux']:
                        lcDataDict['flux'] = 0
                        lcDataDict['flux_err'] = 0
                        lcDataDict['flux_ul'] = 0

                    lcData += f"{time_start_mjd} {time_end_mjd} {lcDataDict['sqrt(ts)']} {lcDataDict['flux']} {lcDataDict['flux_err']} {lcDataDict['flux_ul']} " \
                        f"{lcDataDict['gal']} {lcDataDict['gal_error']} {lcDataDict['iso']} {lcDataDict['iso_error']} "\
                        f"{lcDataDict['l_peak']} {lcDataDict['b_peak']} {lcDataDict['dist_peak']} {lcDataDict['l']} {lcDataDict['b']} {lcDataDict['r']} "\
                        f"{lcDataDict['ell_dist']} {lcDataDict['a']} {lcDataDict['b']} {lcDataDict['phi']} {lcDataDict['exp']} {lcDataDict['ExpRatio']} "\
                        f"{lcDataDict['counts']} {lcDataDict['counts_err']} {lcDataDict['Index']} {lcDataDict['Index_Err']} {lcDataDict['Par2']} {lcDataDict['Par2_Err']} "\
                        f"{lcDataDict['Par3']} {lcDataDict['Par3_Err']} {lcDataDict['Erglog']} {lcDataDict['Erglog_Err']} {lcDataDict['Erglog_UL']} "\
                        f"{time_start_utc} {time_end_utc} {lcDataDict['time_start_tt']} {lcDataDict['time_end_tt']} "\
                        f"{lcDataDict['Fix']} {lcDataDict['index']} {lcDataDict['ULConfidenceLevel']} {lcDataDict['SrcLocConfLevel']} {lcDataDict['start_l']} "\
                        f"{lcDataDict['start_b']} {lcDataDict['start_flux']} {lcDataDict['typefun']} {lcDataDict['par2']} {lcDataDict['par3']} {lcDataDict['galmode2']} "\
                        f"{lcDataDict['galmode2fit']} {lcDataDict['isomode2']} {lcDataDict['isomode2fit']} {lcDataDict['edpcor']} {lcDataDict['fluxcor']} {lcDataDict['integratortype']} "\
                        f"{lcDataDict['expratioEval']} {lcDataDict['expratio_minthr']} {lcDataDict['expratio_maxthr']} {lcDataDict['expratio_size']} {lcDataDict['emin']} {lcDataDict['emax']} "\
                        f"{lcDataDict['fovmin']} {lcDataDict['fovmax']} {lcDataDict['albedo']} {lcDataDict['binsize']} {lcDataDict['expstep']} {lcDataDict['phasecode']} " \
                        f"{lcDataDict['fit_cts']} {lcDataDict['fit_fitstatus0']} {lcDataDict['fit_fcn0']} {lcDataDict['fit_edm0']} {lcDataDict['fit_nvpar0']} {lcDataDict['fit_nparx0']} " \
                        f"{lcDataDict['fit_iter0']} {lcDataDict['fit_fitstatus1']} {lcDataDict['fit_fcn1']} {lcDataDict['fit_edm1']} {lcDataDict['fit_nvpar1']} {lcDataDict['fit_nparx1']} " \
                        f"{lcDataDict['fit_iter1']} {lcDataDict['fit_Likelihood1']}\n"

                    timecounter += 1

        self.logger.info(self, f"\n{lcData}")

        return lcData

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


    """
    The light curve data generation could be parallalezed..
    def _computeLcBin(self, threadID, bins, configBKP, lcAnalysisDataDir, logsOutDir, logFilenamePrefix, verboseLvl):

        logger = AgilepyLogger()

        logger.initialize(logsOutDir, logFilenamePrefix, verboseLvl)

        # outputs = []

        for t1,t2 in bins:

            binOutDir = f'{lcAnalysisDataDir}/bin_{t1}_{t2}'

            configBKP.setOptions(filenameprefix = "lc_analysis", outdir = binOutDir)
            configBKP.setOptions(tmin = t1, tmax = t2, timetype = "TT")

            maplistFilePath = self.generateMaps(configBKP)

            configBKP.setOptions(filenameprefix = "lc_analysis", outdir = binOutDir)
            configBKP.setOptions(tmin = t1, tmax = t2, timetype = "TT")

            _ = self.mle(maplistFilePath = maplistFilePath, config = configBKP, updateSourceLibrary = False)
    """
    
    @staticmethod
    def _chunkList(lst, num):
        avg = len(lst) / float(num)
        out = []
        last = 0.0

        while last < len(lst):
            out.append(lst[int(last):int(last + avg)])
            last += avg

        return out

    def _fixToNegativeExponent(self, number, fixedExponent=-8):

        if number == "-nan": #if the produced value is -nan return 0 according to #347
            return "0"

        if fixedExponent > 0:
            return str(number)

        if number == 0:
            return str(number)

        number_str = str(number)
        exponent = pattern.findall(number_str)
        #print("\nNumber: ", number)
        #print("Number_str: ", number_str)
        #print("Exponent:",exponent)
        fixExponentString = f"e-0{abs(fixedExponent)}"

        #print("fixExponentString:",fixExponentString)

        if len(exponent) == 0:
            if fixedExponent == 0:
                return number
            return str(number * 1e08)+fixExponentString

        exponent = float(exponent.pop())

        #print("exponent:",exponent)

        if exponent == fixedExponent:
            return str(number)

        number_no_exp = float(number_str.split("e")[0])
        #print("number_no_exp:",number_no_exp)
        distance = abs(fixedExponent - exponent)
        #print("distance:",distance)
        if distance > 0:
            number_no_exp = number_no_exp*(pow(10,distance))
        else:
            number_no_exp = number_no_exp/(pow(10,distance))

        #print("number_no_exp:",number_no_exp)

        number = str(round(number_no_exp, 5))+fixExponentString
        #print("number:",number)
        return number

    def _extractLightCurveDataFromSourceFile(self, sourceFilePath):


        # "(0)sqrtts (6)time_mjd (7)time_tt (8)time_utc (9)flux*10^-8 (10)flux_err*10^-8 (11)flux_ul*10^-8 \n"
        # "sqrt(ts) flux flux_err flux_ul gal iso l_peak b_peak dist_peak l b r dist time_start_tt time_end_tt\n"

        multiOutput = self.sourcesLibrary.parseSourceFile(sourceFilePath)

        flux     = self._fixToNegativeExponent(multiOutput.getVal("multiFlux"), fixedExponent=-8)
        flux_err = self._fixToNegativeExponent(multiOutput.getVal("multiFluxErr"), fixedExponent=-8)
        flux_ul  = self._fixToNegativeExponent(multiOutput.getVal("multiUL"), fixedExponent=-8)



        lcDataDict = {
            "sqrt(ts)" : multiOutput.getVal("multiSqrtTS", strr=True),
            "flux"     : flux,
            "flux_err" : flux_err,
            "flux_ul"  : flux_ul,

            "gal" : ','.join(map(str, multiOutput.getVal("multiGalCoeff"))),
            "gal_error": ','.join(map(str, multiOutput.getVal("multiGalErr"))),

            "iso" : ','.join(map(str, multiOutput.getVal("multiIsoCoeff"))),
            "iso_error": ','.join(map(str, multiOutput.getVal("multiIsoErr"))),
            
            "l_peak"    : multiOutput.getVal("multiLPeak", strr=True),
            "b_peak"    : multiOutput.getVal("multiBPeak", strr=True),
            "dist_peak" : multiOutput.getVal("multiDistFromStartPositionPeak", strr=True),

            "l"    : multiOutput.getVal("multiL", strr=True),
            "b"    : multiOutput.getVal("multiB", strr=True),
            "r"    : multiOutput.getVal("multir", strr=True),
            "ell_dist": multiOutput.getVal("multiDistFromStartPosition", strr=True),

            "a": multiOutput.getVal("multia", strr=True),
            "b": multiOutput.getVal("multib", strr=True),
            "phi": multiOutput.getVal("multiphi", strr=True),
            "exp": multiOutput.getVal("multiExp", strr=True),
            "ExpRatio": multiOutput.getVal("multiExpRatio", strr=True),
            "counts": multiOutput.getVal("multiCounts", strr=True),
            "counts_err": multiOutput.getVal("multiCountsErr", strr=True),
            "Index": multiOutput.getVal("multiIndex", strr=True),
            "Index_Err": multiOutput.getVal("multiIndexErr", strr=True),
            "Par2": multiOutput.getVal("multiPar2", strr=True),
            "Par2_Err": multiOutput.getVal("multiPar2Err", strr=True),
            "Par3": multiOutput.getVal("multiPar3", strr=True),
            "Par3_Err": multiOutput.getVal("multiPar3Err", strr=True),
            "Erglog":  multiOutput.getVal("multiErgLog", strr=True),
            "Erglog_Err": multiOutput.getVal("multiErgLogErr", strr=True),
            "Erglog_UL": multiOutput.getVal("multiErgLogUL", strr=True),

            "fit_cts": multiOutput.getVal("multiFitCts", strr=True),
            "fit_fitstatus0": multiOutput.getVal("multiFitFitstatus0", strr=True),
            "fit_fcn0": multiOutput.getVal("multiFitFcn0", strr=True),
            "fit_edm0": multiOutput.getVal("multiFitEdm0", strr=True),
            "fit_nvpar0": multiOutput.getVal("multiFitNvpar0", strr=True),
            "fit_nparx0": multiOutput.getVal("multiFitNparx0", strr=True),
            "fit_iter0": multiOutput.getVal("multiFitIter0", strr=True),
            "fit_fitstatus1": multiOutput.getVal("multiFitFitstatus1", strr=True),
            "fit_fcn1": multiOutput.getVal("multiFitFcn1", strr=True),
            "fit_edm1": multiOutput.getVal("multiFitEdm1", strr=True),
            "fit_nvpar1": multiOutput.getVal("multiFitNvpar1", strr=True),
            "fit_nparx1": multiOutput.getVal("multiFitNparx1", strr=True),
            "fit_iter1": multiOutput.getVal("multiFitIter1", strr=True),
            "fit_Likelihood1": multiOutput.getVal("multiFitLikelihood1", strr=True),


            "time_start_tt" : float(multiOutput.getVal("startDataTT", strr=True)),
            "time_end_tt"   : float(multiOutput.getVal("endDataTT", strr=True)),

            "Fix": multiOutput.getVal("multiFix", strr=True),
            "index": multiOutput.getVal("multiindex", strr=True),
            "ULConfidenceLevel": multiOutput.getVal("multiULConfidenceLevel", strr=True),
            "SrcLocConfLevel": multiOutput.getVal("multiSrcLocConfLevel", strr=True),
            "start_l": multiOutput.getVal("multiStartL", strr=True),
            "start_b": multiOutput.getVal("multiStartB", strr=True),
            "start_flux": multiOutput.getVal("multiStartFlux", strr=True),
            "typefun": multiOutput.getVal("multiTypefun", strr=True),
            "par2": multiOutput.getVal("multipar2", strr=True),
            "par3": multiOutput.getVal("multipar3", strr=True),
            "galmode2":  multiOutput.getVal("multiGalmode2", strr=True),
            "galmode2fit": multiOutput.getVal("multiGalmode2fit", strr=True),
            "isomode2":  multiOutput.getVal("multiIsomode2", strr=True),
            "isomode2fit": multiOutput.getVal("multiIsomode2fit", strr=True),
            "edpcor": multiOutput.getVal("multiEdpcor", strr=True),
            "fluxcor": multiOutput.getVal("multiFluxcor", strr=True),
            "integratortype": multiOutput.getVal("multiIntegratorType", strr=True),
            "expratioEval": multiOutput.getVal("multiExpratioEval", strr=True),
            "expratio_minthr": multiOutput.getVal("multiExpratioMinthr", strr=True),
            "expratio_maxthr":  multiOutput.getVal("multiExpratioMaxthr", strr=True),
            "expratio_size": multiOutput.getVal("multiExpratioSize", strr=True),

            "emin": ','.join(map(str, multiOutput.getVal("multiEmin"))),
            "emax": ','.join(map(str, multiOutput.getVal("multiEmax"))),
            "fovmin": ','.join(map(str, multiOutput.getVal("multifovmin"))),
            "fovmax": ','.join(map(str, multiOutput.getVal("multifovmax"))),
            
            "albedo": multiOutput.getVal("multialbedo", strr=True),
            "binsize": multiOutput.getVal("multibinsize", strr=True),
            "expstep": multiOutput.getVal("multiexpstep", strr=True),
            "phasecode": multiOutput.getVal("multiphasecode", strr=True)

        }

        return lcDataDict

    def _extractBkgCoeff(self, sourceFiles, sourceName):

        sourceFilePath = [ sourceFilePath for sourceFilePath in sourceFiles if sourceName in basename(sourceFilePath)]

        if len(sourceFilePath) > 1:
            self.logger.critical(self, f"Something is wrong, found two .source files {sourceFilePath} for the same source {sourceName}")
            raise ValueError(f"Something is wrong, found two .source files {sourceFilePath} for the same source {sourceName}")

        self.logger.debug(self, "Extracting isocoeff and galcoeff from %s", sourceFilePath)

        multiOutput = self.sourcesLibrary.parseSourceFile(sourceFilePath.pop())

        isoCoeff = multiOutput.getVal("multiIsoCoeff")
        galCoeff = multiOutput.getVal("multiGalCoeff")

        self.logger.debug(self, f"Multioutput: {multiOutput}")

        return isoCoeff, galCoeff

    def _displaySkyMaps(self, skyMapType, singleMode, maplistFile=None, smooth=4.0, saveImage=False, fileFormat=".png", title=None, cmap="CMRmap", regFiles=None, regFileColors=[], catalogRegions=None, catalogRegionsColor=None, normType="linear"):

        if self.currentMapList.getFile() is None and maplistFile is None:
            self.logger.warning(self, "No sky maps have already been generated yet and maplistFile is None. Please, call generateMaps() or pass a valid maplistFile.")
            return False

        elif self.currentMapList.getFile() is None and maplistFile is not None:
            maplistRows = self.parseMaplistFile(maplistFile)
        else:
            maplistRows = self.parseMaplistFile()

        outputs = []

        titles = []
        files = []

        for maplistRow in maplistRows:

            skymapFilename = basename(maplistRow[0])

            # This data should be read from the FITS header
            emin = skymapFilename.split("EN")[1].split("_")[0]
            emax = skymapFilename.split("EX")[1].split("_")[0]

            title = f"{skyMapType}\nemin: {emin} emax: {emax} bincenter: {maplistRow[3]}\ngalcoeff: {maplistRow[4]} isocoeff: {maplistRow[5]}"

            titles.append(title)

            if skyMapType == "CTS":
                files.append(maplistRow[0])

            elif skyMapType == "EXP":
                files.append(maplistRow[1])

            elif skyMapType == "GAS":
                files.append(maplistRow[2])
            
            elif skyMapType == "INT":
                name = maplistRow[0].split(".cts.gz")
                name = name[0]+".int.gz"

                files.append(name)



        if len(files) == 1 and singleMode is True:
            self.logger.warning(self, "singleMode has been turned off because only one map is going to be displayed.")
            singleMode = False


        if singleMode:

            outputfile = self.plottingUtils.displaySkyMapsSingleMode(files, smooth=smooth, saveImage=saveImage, fileFormat=fileFormat, titles=titles, cmap=cmap, regFiles=regFiles, regFileColors=regFileColors, catalogRegions=catalogRegions, catalogRegionsColor=catalogRegionsColor, normType=normType)

            outputs.append(outputfile)

        else:

            for idx,title in enumerate(titles):

                outputfile = self.plottingUtils.displaySkyMap(files[idx], smooth, saveImage, fileFormat, title, cmap, regFiles, regFileColors, catalogRegions, catalogRegionsColor, normType)

                outputs.append(outputfile)

        return outputs
