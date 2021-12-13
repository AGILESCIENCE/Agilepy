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

from agilepy.core.CustomExceptions import AttributeNotSupportedError
from agilepy.core.source.SourceComponent import SourceComponent

class MultiAnalysis(SourceComponent):

    spectrumMultiMapping = {
        "flux" : "multiFlux",
        "index" : "multiIndex",
        "index1" : "multiIndex",
        "cutoffEnergy" : "multiPar2",
        "pivotEnergy" : "multiPar2",
        "index2" : "multiPar3",
        "curvature" : "multiPar3",
    }


    def __init__(self):

        self.multiDate = {"value": None, "datatype": "date", "um": ""}
        self.multiName = {"value": None, "datatype": "str", "um": ""}

        self.multiSqrtTS = {"value": None, "datatype": "float", "um": ""}

        self.multiFix = {"value": None, "datatype": "float", "um": ""}
        self.multiindex = {"value": None, "datatype": "float", "um": ""}
        self.multiULConfidenceLevel = {"value": None, "datatype": "float", "um": ""}
        self.multiSrcLocConfLevel = {"value": None, "datatype": "float", "um": ""}

        self.multiFlux = {"value": None, "err": None, "datatype": "float", "um": "ph/cm2s"}
        self.multiFluxErr = {"value": None, "datatype": "float", "um": ""}
        self.multiFluxPosErr = {"value": None, "datatype": "float", "um": ""}
        self.multiFluxNegErr = {"value": None, "datatype": "float", "um": ""}

        self.multiStartFlux = {"value": None, "datatype": "float", "um": ""}
        self.multiTypefun = {"value": None, "datatype": "float", "um": ""}
        self.multipar2 = {"value": None, "datatype": "float", "um": ""}
        self.multipar3 = {"value": None, "datatype": "float", "um": ""}
        self.multiGalmode2 = {"value": None, "datatype": "float", "um": ""}
        self.multiGalmode2fit = {"value": None, "datatype": "float", "um": ""}
        self.multiIsomode2 = {"value": None, "datatype": "float", "um": ""}
        self.multiIsomode2fit = {"value": None, "datatype": "float", "um": ""}
        self.multiEdpcor = {"value": None, "datatype": "float", "um": ""}
        self.multiFluxcor = {"value": None, "datatype": "float", "um": ""}
        self.multiIntegratorType = {"value": None, "datatype": "float", "um": ""}
        self.multiExpratioEval = {"value": None, "datatype": "float", "um": ""}
        self.multiExpratioMinthr = {"value": None, "datatype": "float", "um": ""}
        self.multiExpratioMaxthr = {"value": None, "datatype": "float", "um": ""}
        self.multiExpratioSize = {"value": None, "datatype": "float", "um": ""}


        self.multiUL = {"value": None, "datatype": "float", "um": "ph/cm2s"}

        self.multiExp = {"value": None, "datatype": "float","um": "cm2s"}


        self.multiErgLog = {"value": None, "err": None, "datatype": "float", "um": "erg/cm2s"}
        self.multiErgLogErr = {"value": None, "datatype": "float", "um": ""}
        self.multiErgLogUL = {"value": None, "datatype": "float", "um": ""}


        self.multiStartL = {"value": None, "datatype": "float", "um": ""}
        self.multiStartB = {"value": None, "datatype": "float", "um": ""}

        self.multiDist = {"value": None, "datatype": "float", "um": ""}

        self.multiLPeak = {"value": None, "datatype": "float", "um": ""}
        self.multiBPeak = {"value": None, "datatype": "float", "um": ""}
        self.multiDistFromStartPositionPeak = {"value": None, "datatype": "float", "um": ""}

        self.multiL = {"value": None, "datatype": "float", "um": ""}
        self.multiB = {"value": None, "datatype": "float", "um": ""}
        self.multiDistFromStartPosition = {"value": None, "datatype": "float", "um": ""}
        self.multir = {"value": None, "datatype": "float", "um": ""}
        self.multia = {"value": None, "datatype": "float", "um": ""}
        self.multib = {"value": None, "datatype": "float", "um": ""}
        self.multiphi = {"value": None, "datatype": "float", "um": ""}

        self.multiCounts = {"value": None, "err": None, "datatype": "float", "um": ""}
        self.multiCountsErr = {"value": None, "datatype": "float", "um": ""}
        
        self.multiIndex = {"value": None, "err": None, "datatype": "float", "um": ""}
        self.multiIndexErr = {"value": None, "datatype": "float", "um": ""}
        
        self.multiPar2 = {"value": None, "err": None, "datatype": "float", "um": ""}
        self.multiPar2Err = {"value": None, "datatype": "float", "um": ""}

        self.multiPar3 = {"value": None, "err": None, "datatype": "float", "um": ""}
        self.multiPar3Err = {"value": None, "datatype": "float", "um": ""}

        self.multiFitCts = {"value": None, "datatype": "float", "um": ""}
        self.multiFitFitstatus0 = {"value": None, "datatype": "float", "um": ""}
        self.multiFitFcn0 = {"value": None, "datatype": "float", "um": ""}
        self.multiFitEdm0 = {"value": None, "datatype": "float", "um": ""}
        self.multiFitNvpar0 = {"value": None, "datatype": "float", "um": ""}
        self.multiFitNparx0 = {"value": None, "datatype": "float", "um": ""}
        self.multiFitIter0 = {"value": None, "datatype": "float", "um": ""}
        self.multiFitFitstatus1 = {"value": None, "datatype": "float", "um": ""}
        self.multiFitFcn1 = {"value": None, "datatype": "float", "um": ""}
        self.multiFitEdm1 = {"value": None, "datatype": "float", "um": ""}
        self.multiFitNvpar1 = {"value": None, "datatype": "float", "um": ""}
        self.multiFitNparx1 = {"value": None, "datatype": "float", "um": ""}
        self.multiFitIter1 = {"value": None, "datatype": "float", "um": ""}
        self.multiFitLikelihood1 = {"value": None, "datatype": "float", "um": ""}
        
        self.multiGalCoeff = {"value": None, "err": None, "datatype": "List<float>", "um": ""}
        self.multiGalErr = {"value": None, "datatype": "List<float>", "um": ""}

        self.multiIsoCoeff = {"value": None, "err": None, "datatype": "List<float>", "um": ""}
        self.multiIsoErr = {"value": None, "datatype": "List<float>", "um": ""}

        self.startDataTT = {"value": None, "err": None, "datatype": "float", "um": ""}
        self.endDataTT = {"value": None, "datatype": "float", "um": ""}

        self.multiEmin = {"value":None, "datatype": "List<float>", "um": ""}
        self.multiEmax = {"value":None, "datatype": "List<float>", "um": ""}
        self.multifovmin = {"value":None, "datatype": "List<float>", "um": ""}
        self.multifovmax = {"value":None, "datatype": "List<float>", "um": ""}
        self.multialbedo = {"value":None, "datatype": "float", "um": ""}
        self.multibinsize = {"value":None, "datatype": "float", "um": ""}
        self.multiexpstep = {"value":None, "datatype": "float", "um": ""}
        self.multiphasecode = {"value":None, "datatype": "float", "um": ""}

        self.multiExpRatio = {"value":None, "datatype": "float", "um": ""}

    def setParameter(self, parameterName, dictionaryValues):

        dictionaryKeys = list(dictionaryValues.keys())
        for key in dictionaryKeys:
            if key not in ["value"]:
                raise AttributeNotSupportedError(f"The attribute '{key}' is not supported for object of type '{type(self)}'")

        parameter = getattr(self, parameterName)
        for key,val in dictionaryValues.items():
            try: parameter[key] = eval(val)       
            except: parameter[key] = val
