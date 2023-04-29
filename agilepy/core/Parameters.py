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
from pathlib import Path

class Parameters:

    _datapath = Path(os.environ["AGILE"]).joinpath("model/scientific_analysis/data")
    _calibrationFiles = os.listdir(_datapath)

    _skymapTemplate = "{}_{}.SKY002.{}_{}.disp.conv.sky.gz"

    _sarmatrixTemplate = "AG_GRID_G0017_{}_{}.sar.gz"
    _edpmatrixTemplate = "AG_GRID_G0017_{}_{}.edp.gz"
    _psdmatrixTemplate = "AG_GRID_G0017_{}_{}.psd.gz"

    _mapNameTemplate = "TN{}_TX{}_EN{}_EX{}_ID{}"

    _supported_irfs = ["I0025", "H0025"]

    _supportedEnergyBins = [[10000,50000],
                            [1000,3000],
                            [1000,50000],
                            [100,1000],
                            [100,10000],
                            [100,200],
                            [100,300],
                            [100,400],
                            [100,50000],
                            [200,400],
                            [200,50000],
                            [3000,10000],
                            [3000,50000],
                            [300,1000],
                            [300,10000],
                            [300,3000],
                            [300,50000],
                            [30,100],
                            [30,1000],
                            [30,400],
                            [30,50],
                            [30,50000],
                            [400,1000],
                            [400,10000],
                            [400,3000],
                            [400,50000],
                            [50,100],
                            [50,400],
                            [1000,10000],
                            [100,3000],
                            [50,1000],
                            [50,10000],
                            [50,300],
                            [50,3000],
                            [50,50000]                            
                          ]


    @staticmethod
    def getFilterCodeMapping(filtercode):
        """
        filtercode = 0 ALL --> T
        filtercode = 1 != L --> GS
        filtercode = 2 != G --> LS
        filtercode = 3 != G != L --> S (+P)
        filtercode = 4 != S --> GL
        filtercode = 5 != S != L = G (+P)
        filtercode = 6 != S != G = L (+P)
        filtercode = 7 != S != G <> L = null --> P (+P)                
        """
        if filtercode == 0:
            return "SFMT"
        elif filtercode == 1:
            return "SFMGS"
        elif filtercode == 2:
            return "SFMLS"
        elif filtercode == 3:
            return "SFMS"
        elif filtercode == 4:
            return "SFMGL"
        elif filtercode == 5:
            return "SFMG"
        elif filtercode == 6:
            return "SFML"
        elif filtercode == 7:
            return "SFMP"
        else:
            raise ValueError(f"Filter code {filtercode} is not supported")

    @staticmethod
    def getCalibrationMatrices(filtercode, irf):

        if irf not in Parameters._supported_irfs:
            raise ValueError(f"IRF {irf} is not supported")
        
        sarmatrix = Parameters._sarmatrixTemplate.format(Parameters.getFilterCodeMapping(filtercode), irf)
        edpmatrix = Parameters._edpmatrixTemplate.format(Parameters.getFilterCodeMapping(filtercode), irf)
        psdmatrix = Parameters._psdmatrixTemplate.format(Parameters.getFilterCodeMapping(filtercode), irf)

        if sarmatrix not in Parameters._calibrationFiles:
            raise ValueError(f"Calibration matrix {sarmatrix} is not available")
        if edpmatrix not in Parameters._calibrationFiles:
            raise ValueError(f"Calibration matrix {edpmatrix} is not available")
        if psdmatrix not in Parameters._calibrationFiles:
            raise ValueError(f"Calibration matrix {psdmatrix} is not available")

        return [Parameters._datapath.joinpath(sarmatrix), Parameters._datapath.joinpath(edpmatrix), Parameters._datapath.joinpath(psdmatrix)]


    @staticmethod
    def getSkyMap(emin, emax, filtercode, irf):
        if irf not in Parameters._supported_irfs:
            raise ValueError(f"IRF {irf} is not supported")        
        skymap = Parameters._skymapTemplate.format(emin, emax, Parameters.getFilterCodeMapping(filtercode), irf)
        if skymap in Parameters._calibrationFiles:
            skymapPath = Parameters._datapath.joinpath(skymap)
            if skymapPath.exists():
                return skymapPath
            else:
                raise ValueError(f"Sky map {skymap} is not available in {Parameters._datapath}")
        else:
            raise ValueError(f"Sky map {skymap} is not available in {Parameters._datapath}")
        
    @staticmethod
    def getCatEminEmax(catalogName):
        if catalogName == "2AGL":
            return (100, 10000)
        else:
            raise ValueError(f"Catalog {catalogName} is not supported")

    @staticmethod
    def checkEnergyBin(energyBin):
        energyBin = [int(energy) for energy in energyBin]
        if energyBin in Parameters._supportedEnergyBins:
            return True
        return False


    @staticmethod
    def getMapNamePrefix(tmin, tmax, emin, emax, glon, glat, stepi):
        return Parameters._mapNameTemplate.format(str(tmin),str(tmax),str(emin).zfill(5), str(emax).zfill(5), str(stepi).zfill(2))

    @staticmethod
    def getSupportedIRFs():
        return Parameters._supported_irfs

    @staticmethod
    def getSupportedEnergyBins():
        return Parameters._supportedEnergyBins
        
    @staticmethod
    def getSupportedCalibrationFiles():
        return Parameters._calibrationFiles