from agilepy.api.AGAnalysis import AGAnalysis


class SpectraSingleBin:

    @staticmethod
    def calculateSpectraOnSingleEnergyBin(confFilePath, sourcename, initialsource, emin, emax, dq, filtercode, galcoeff, isocoeff):
    
        ag_bin = AGAnalysis(str(confFilePath))
        
        energybins=[[emin, emax]]
        
        ag_bin.setOptions(timestep=1, filtercode=filtercode, energybins=energybins, dq=dq, useEDPmatrixforEXP=True)

        newSourceDict = {
            "glon" : float(initialsource.get('multiLPeak')['value']),
            "glat": float(initialsource.get('multiBPeak')['value']),
            "spectrumType" : "PowerLaw",
            "flux": 1e-03,
            "index": float(initialsource.get("multiIndex")['value'])
        }

        s = ag_bin.addSource(sourcename, newSourceDict)
        
        #print("Full list of sources")
        #for s in ag_bin.sources:
        #    print(s)
        
        _sources = ag_bin.freeSources(f'name == "{sourcename}"', "pos", False, show=False)
        _sources = ag_bin.freeSources(f'name == "{sourcename}"', "index", False, show=False)
        _sources = ag_bin.freeSources(f'name == "{sourcename}"', "flux", True, show=False)
        
        ag_bin.generateMaps()
        
        ag_bin.setOptions(galcoeff=[galcoeff], isocoeff=[isocoeff])
        
        _=ag_bin.mle()
        
        _sources = ag_bin.selectSources(f'name == "{sourcename}"', show=True)
        
        return _sources[0]         
