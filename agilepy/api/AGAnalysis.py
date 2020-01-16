"""
 DESCRIPTION
       Agilepy software

 NOTICE
       Any information contained in this software
       is property of the AGILE TEAM and is strictly
       private and confidential.
       Copyright (C) 2005-2020 AGILE Team.
           Addis Antonio <antonio.addis@inaf.it>
           Baroncelli Leonardo <leonardo.baroncelli@inaf.it>
           Bulgarelli Andrea <andrea.bulgarelli@inaf.it>
           Parmiggiani Nicolò <nicolo.parmiggiani@inaf.it>
       All rights reserved.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

from os.path import join

from agilepy.config.AgilepyConfig import AgilepyConfig

from agilepy.api.SourcesLibrary import SourcesLibrary
from agilepy.api.ScienceTools import ctsMapGenerator, expMapGenerator, gasMapGenerator, intMapGenerator, multi

from agilepy.utils.Utils import AgilepyLogger, Decorators
from agilepy.utils.Parameters import Parameters

class AGAnalysis:

    """

        Public interface

    """

    @Decorators.accepts(object, str, str)
    def __init__(self, configurationFilePath, sourcesFilePath):
        """
        This method ... blabla ...
        """
        self.config = AgilepyConfig(configurationFilePath)

        self.logger = AgilepyLogger(self.config.getConf("output","outdir"), self.config.getConf("output","logfilename"), self.config.getConf("output","debuglvl"), init=True)

        self.sourcesLibrary = SourcesLibrary(sourcesFilePath)


    @Decorators.accepts(object)
    def resetConf(self):
        self.config.reset()


    def setOptions(self, **kwargs):
        """
        This method ... blabla ...
        """
        rejected = self.config.setOptions(**kwargs)

        if rejected:

            self.logger.warning(self, "Some options have not been set: {}".format(rejected))


    @Decorators.accepts(object, str)
    def printOptions(self, section=None):
        """
        This method ... blabla ...
        """
        self.config.printOptions(section)


    @Decorators.accepts(object)
    def getSourcesLibrary(self):
        """
        This method ... blabla ...
        """
        return self.sourcesLibrary


    @Decorators.accepts(object, "*", str, bool)
    def freeSources(self, selectionLamda, parameterName, free):
        """
        This method ... blabla ...
        """
        return self.sourcesLibrary.freeSources(selectionLamda, parameterName, free)


    @Decorators.accepts(object, "*")
    def deleteSources(self, selectionLamda):
        """
        This method ... blabla ...
        """
        return self.sourcesLibrary.deleteSources(selectionLamda)


    @Decorators.accepts(object)
    def generateMaps(self):
        """
        This method ... blabla ...
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
                bincenter, fovmin, fovmax = self._updateFovMinMaxValues(fovbinnumber, initialFovmin, initialFovmax, stepi+1)


            for stepe in energybins:

                if Parameters.checkEnergyBin(stepe):

                    emin = stepe[0]
                    emax = stepe[1]

                    skymapL = Parameters.getSkyMap(emin, emax)
                    skymapH = Parameters.getSkyMap(emin, emax)
                    fileNamePrefix = Parameters.getMapNamePrefix(emin, emax, stepi+1)

                    self.logger.info(self, "\n\nMap generation => fovradmin %s fovradmax %s bincenter %s emin %s emax %s fileNamePrefix %s skymapL %s skymapH %s", [fovmin,fovmax,bincenter,emin,emax,fileNamePrefix,skymapL,skymapH])

                    self.config.setOptions(filenameprefix=initialFileNamePrefix+"_"+fileNamePrefix)
                    self.config.setOptions(fovradmin=fovmin, fovradmax=fovmax)
                    self.config.addOptions("selection", emin=emin, emax=emax)
                    self.config.addOptions("maps", skymapL=skymapL, skymapH=skymapH)

                    ctsMapGenerator.setArguments(self.config)
                    expMapGenerator.setArguments(self.config)
                    gasMapGenerator.setArguments(self.config)
                    intMapGenerator.setArguments(self.config)

                    self.config.addOptions("maps", expmap=expMapGenerator.outfilePath, ctsmap=ctsMapGenerator.outfilePath)

                    if not ctsMapGenerator.allRequiredOptionsSet(self.config) or not expMapGenerator.allRequiredOptionsSet(self.config) or not gasMapGenerator.allRequiredOptionsSet(self.config) or not intMapGenerator.allRequiredOptionsSet(self.config):
                        self.logger.critical(self,"Some options have not been set.")
                        exit(1)

                    ctsMapGenerator.call()
                    expMapGenerator.call()
                    gasMapGenerator.call()
                    intMapGenerator.call()

                    mapListFileContent.append(ctsMapGenerator.outfilePath + " " + expMapGenerator.outfilePath + " " + gasMapGenerator.outfilePath + " " + str(bincenter) + " " + str(self.config.getOptionValue("galcoeff")) + " " + str(self.config.getOptionValue("isocoeff")) )

                else:

                    self.logger.warning(self,"Energy bin [%s, %s] is not supported. Map generation skipped.", [stepe[0], stepe[1]])


        with open(maplistFilePath,"w") as mlf:
            for line in mapListFileContent:
                mlf.write(line+"\n")

        self.logger.info(self, "Maplist file created in %s", [maplistFilePath])

        self.config.reset()


        return maplistFilePath

    @Decorators.accepts(object, str)
    def mle(self, maplistFilePath):
        """
        This method ... blabla ...
        """
        if not maplistFilePath:
            self.logger.critical(self, "The 'maplistFilePath' input argument is None. Please, pass a valid path to a maplist file as argument (perhaps you want to call generateMaps() first). ")
            exit(1)

        sourceListFilePath = self.sourcesLibrary.writeToFile(outfileNamePrefix="sourceLibrary", format="AG")

        self.config.addOptions("selection", maplist=maplistFilePath, sourcelist=sourceListFilePath)

        multi.setArguments(self.config)

        source = multi.call()

        self.sourcesLibrary.updateMulti(source)




















    """

        Private methods

    """

    def _updateFovMinMaxValues(self, fovbinnumber, fovradmin, fovradmax, stepi):
        """
        This method ... blabla ...
        """
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
