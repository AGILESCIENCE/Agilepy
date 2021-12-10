from agilepy.core.CustomExceptions import AttributeNotSupportedError

class MultiAnalysis:


    def __init__(self):

        self.name = None

        self.multiSqrtTS = {"value": None, "datatype": "float"}

        self.multiFix = {"value": None, "datatype": "float"}
        self.multiindex = {"value": None, "datatype": "float"}
        self.multiULConfidenceLevel = {"value": None, "datatype": "float"}
        self.multiSrcLocConfLevel = {"value": None, "datatype": "float"}

        self.multiFlux = {"value": None, "datatype": "float"}
        self.multiFluxErr = {"value": None, "datatype": "float"}
        self.multiFluxPosErr = {"value": None, "datatype": "float"}
        self.multiFluxNegErr = {"value": None, "datatype": "float"}

        self.multiStartFlux = {"value": None, "datatype": "float"}
        self.multiTypefun = {"value": None, "datatype": "float"}
        self.multipar2 = {"value": None, "datatype": "float"}
        self.multipar3 = {"value": None, "datatype": "float"}
        self.multiGalmode2 = {"value": None, "datatype": "float"}
        self.multiGalmode2fit = {"value": None, "datatype": "float"}
        self.multiIsomode2 = {"value": None, "datatype": "float"}
        self.multiIsomode2fit = {"value": None, "datatype": "float"}
        self.multiEdpcor = {"value": None, "datatype": "float"}
        self.multiFluxcor = {"value": None, "datatype": "float"}
        self.multiIntegratorType = {"value": None, "datatype": "float"}
        self.multiExpratioEval = {"value": None, "datatype": "float"}
        self.multiExpratioMinthr = {"value": None, "datatype": "float"}
        self.multiExpratioMaxthr = {"value": None, "datatype": "float"}
        self.multiExpratioSize = {"value": None, "datatype": "float"}


        self.multiUL = {"value": None, "datatype": "float"}

        self.multiExp = {"value": None, "datatype": "float"}


        self.multiErgLog = {"value": None, "datatype": "float"}
        self.multiErgLogErr = {"value": None, "datatype": "float"}
        self.multiErgLogUL = {"value": None, "datatype": "float"}


        self.multiStartL = {"value": None, "datatype": "float"}
        self.multiStartB = {"value": None, "datatype": "float"}

        self.multiDist = {"value": None, "datatype": "float"}

        self.multiLPeak = {"value": None, "datatype": "float"}
        self.multiBPeak = {"value": None, "datatype": "float"}
        self.multiDistFromStartPositionPeak = {"value": None, "datatype": "float"}

        self.multiL = {"value": None, "datatype": "float"}
        self.multiB = {"value": None, "datatype": "float"}
        self.multiDistFromStartPosition = {"value": None, "datatype": "float"}
        self.multir = {"value": None, "datatype": "float"}
        self.multia = {"value": None, "datatype": "float"}
        self.multib = {"value": None, "datatype": "float"}
        self.multiphi = {"value": None, "datatype": "float"}

        self.multiCounts = {"value": None, "datatype": "float"}
        self.multiCountsErr = {"value": None, "datatype": "float"}
        
        self.multiIndex = {"value": None, "datatype": "float"}
        self.multiIndexErr = {"value": None, "datatype": "float"}
        
        self.multiPar2 = {"value": None, "datatype": "float"}
        self.multiPar2Err = {"value": None, "datatype": "float"}

        self.multiPar3 = {"value": None, "datatype": "float"}
        self.multiPar3Err = {"value": None, "datatype": "float"}

        self.multiFitCts = {"value": None, "datatype": "float"}
        self.multiFitFitstatus0 = {"value": None, "datatype": "float"}
        self.multiFitFcn0 = {"value": None, "datatype": "float"}
        self.multiFitEdm0 = {"value": None, "datatype": "float"}
        self.multiFitNvpar0 = {"value": None, "datatype": "float"}
        self.multiFitNparx0 = {"value": None, "datatype": "float"}
        self.multiFitIter0 = {"value": None, "datatype": "float"}
        self.multiFitFitstatus1 = {"value": None, "datatype": "float"}
        self.multiFitFcn1 = {"value": None, "datatype": "float"}
        self.multiFitEdm1 = {"value": None, "datatype": "float"}
        self.multiFitNvpar1 = {"value": None, "datatype": "float"}
        self.multiFitNparx1 = {"value": None, "datatype": "float"}
        self.multiFitIter1 = {"value": None, "datatype": "float"}
        self.multiFitLikelihood1 = {"value": None, "datatype": "float"}
        
        self.multiGalCoeff = {"value": None, "datatype": "List<float>"}
        self.multiGalErr = {"value": None, "datatype": "List<float>"}

        self.multiIsoCoeff = {"value": None, "datatype": "List<float>"}
        self.multiIsoErr = {"value": None, "datatype": "List<float>"}

        self.startDataTT = {"value": None, "datatype": "float"}
        self.endDataTT = {"value": None, "datatype": "float"}

        self.multiEmin = {"value":None, "datatype": "List<float>"}
        self.multiEmax = {"value":None, "datatype": "List<float>"}
        self.multifovmin = {"value":None, "datatype": "List<float>"}
        self.multifovmax = {"value":None, "datatype": "List<float>"}
        self.multialbedo = {"value":None, "datatype": "float"}
        self.multibinsize = {"value":None, "datatype": "float"}
        self.multiexpstep = {"value":None, "datatype": "float"}
        self.multiphasecode = {"value":None, "datatype": "float"}

        self.multiExpRatio = {"value":None, "datatype": "float"}

    def setParameter(self, parameterName, dictionaryValues):

        dictionaryKeys = list(dictionaryValues.keys())
        for key in dictionaryKeys:
            if key not in ["value"]:
                raise AttributeNotSupportedError(f"The attribute '{key}' is not supported for object of type '{type(spectrumObject)}'")

        parameter = getattr(self, parameterName)
        for key,val in dictionaryValues.items():
            parameter[key] = val         