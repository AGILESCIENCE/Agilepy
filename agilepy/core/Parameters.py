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

class Parameters:

    datapath = os.path.join(os.environ["AGILE"], "model/scientific_analysis/data")

    _skymap = os.path.join(datapath, "{}_{}.SKY002.SFMG_H0025.disp.conv.sky.gz")
    _mapNamePrefix = "TMIN{}_TMAX{}_EMIN{}_EMAX{}_{}"

    # constants
    sarmatrix = os.path.join(datapath, "AG_GRID_G0017_SFMG_H0025.sar.gz")
    edpmatrix = os.path.join(datapath, "AG_GRID_G0017_SFMG_H0025.edp.gz")
    psdmatrix = os.path.join(datapath, "AG_GRID_G0017_SFMG_H0025.psd.gz")

    matrixconf = sarmatrix + " " + edpmatrix + " " + psdmatrix

    energybins = [[10000,50000],
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
                 ]


    @staticmethod
    def getCat2EminEmax():
        return (100, 10000)

    @staticmethod
    def checkEnergyBin(energyBin):
        energyBin = [int(energy) for energy in energyBin]
        if energyBin in Parameters.energybins:
            return True
        return False

    @staticmethod
    def getSkyMap(emin, emax):
        return Parameters._skymap.format(emin, emax)

    @staticmethod
    def getMapNamePrefix(tmin, tmax, emin, emax, stepi):
        return Parameters._mapNamePrefix.format(str(tmin),str(tmax),str(emin).zfill(5), str(emax).zfill(5), str(stepi).zfill(2))
