import os
import argparse
import pandas as pd
from pathlib import Path

from agilepy.api.AGAnalysis import AGAnalysis
from agilepy.api.advanced.spectra.configuration import Configuration
from agilepy.api.advanced.spectra.spectra_single_bin import SpectraSingleBin

"""
agilepy_spectra --username baroncelli --sourcename GRB221009A --glon 52.985514 --glat 4.337308 --flux 1e-03 --index 1.94638 --spectrum-type PowerLaw --outputdir $HOME/spectra_analysis --filtercode 5 --ffilter 0 --approx-grb-time 592406219 --timeshift 0 --ow OW4 --channels-conf C7
"""

def main():
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--username'            , type=str,   required=True, help='')
    parser.add_argument('--sourcename'          , type=str,   required=True, help='')
    parser.add_argument('--glon'                , type=float, required=True, help='')
    parser.add_argument('--glat'                , type=float, required=True, help='')
    parser.add_argument('--flux'                , type=float, required=True, help='')
    parser.add_argument('--index'               , type=float, required=True, help='')
    parser.add_argument('--spectrum-type'       , type=str,   required=True, help='')    
    parser.add_argument('--outputdir'           , type=str,   required=True, help='')

    parser.add_argument('--filtercode'          , type=int,   required=True, help='')
    parser.add_argument('--ffilter'             , type=int,   required=True, help='')
    parser.add_argument('--approx-grb-time'     , type=float, required=True, help='This is t0 (in TT)')
    parser.add_argument('--timeshift'           , type=float, required=True, help='')
    parser.add_argument('--ow'                  , type=str,   required=True, help='')
    parser.add_argument('--channels-conf'       , type=str,   required=True, help='')
    parser.add_argument('--correction'          , type=int,   required=False, default=1, help='Verrechia\'s correction')
    parser.add_argument('--fluxcorrection'      , type=int,   required=False, default=0, help='')
    parser.add_argument('--edpcorrection'       , type=int,   required=False, default=0, help='')
    parser.add_argument('--timebin'             , type=int,   required=False, default=10, help='')
    parser.add_argument('--background-window'   , type=int,   required=False, default=14, help='')
    parser.add_argument('--fovradmax'           , type=int,   required=False, default=60, help='')
    parser.add_argument('--dq'                  , type=int,   required=False, default=1, help='')
    args = parser.parse_args()

    ######################### CONFIGURATION  #########################
    
    evtfile = Configuration.getEvtFile(args.ffilter)
    logfile = Configuration.getLogFile(args.correction)
    
    t0, tstart, tstop = Configuration.getTimes(args.ow, args.approx_grb_time, args.timeshift)

    energybins, nchannels, emin, emax = Configuration.getEnergyBins(args.channels_conf)
   
    galcoeff, isocoeff, calcbkg = Configuration.getGalIsoCoeff(args.filtercode, nchannels, emin, emax, args.edpcorrection)

    Path(args.outputdir).mkdir(parents=True, exist_ok=True)
    confFilePath = Path(args.outputdir).joinpath("./agilepy_conf_mle.yaml")

    AGAnalysis.getConfiguration(
        confFilePath = str(confFilePath),
        evtfile = evtfile,
        logfile = logfile,
        userName = args.username,
        sourceName = args.sourcename,
        tmin = tstart,
        tmax = tstop,
        timetype = "TT",
        glon = args.glon,
        glat = args.glat,
        outputDir = str(args.outputdir),
        verboselvl = 0,
        userestapi = False,
        datapath = "$HOME/agile_dataset"
    )


    ag = AGAnalysis(str(confFilePath))

    ag.setOptions(timestep=1, 
                  binsize=0.5, 
                  filtercode=args.filtercode, 
                  energybins=energybins, 
                  dq=args.dq, 
                  useEDPmatrixforEXP=bool(args.edpcorrection), 
                  expstep=2, 
                  fluxcorrection=args.fluxcorrection, 
                  edpcorrection=0.75 ### <---- !!
                  )
    ag.printOptions()

    ag.logger.info(f"Adding source {args.sourcename}")

    newSourceDict = {
        "glon" : args.glon,
        "glat": args.glat,
        "spectrumType" : args.spectrum_type,
        "flux": args.flux,
        "index": args.index
    }
    
    s = ag.addSource(args.sourcename, newSourceDict)    

    _sources = ag.freeSources(f'name == "{args.sourcename}"', "pos", True, show=True)
    _sources = ag.freeSources(f'name == "{args.sourcename}"', "flux", True, show=True)


    ######################### ANALYSIS #########################
    ag.generateMaps()
    if calcbkg:
        galcoeff, isocoeff, maplist = ag.calcBkg(args.sourcename, pastTimeWindow = args.background_window)
    else:
        ag.setOptions(galcoeff=galcoeff, isocoeff=isocoeff)
    ag.logger.info(f"Background has been calculated? {calcbkg}. galcoeff: {galcoeff}, isocoeff: {isocoeff}")



    ######################### SINGLE SOURCE ANALYSIS #########################
    mleres=ag.mle()
    _source = ag.selectSources("sqrtTS > 0", show=True)
    _source[0].get("multiIndex")['value']



    ######################### SPECTRA #########################
    emin = _source[0].get("multiEmin")['value']
    emax = _source[0].get("multiEmax")['value']
    galcoeff = _source[0].get("multiGalCoeff")['value']
    isocoeff = _source[0].get("multiIsoCoeff")['value']
    ag.logger.info(f"emin: {emin[0]}, emax: {emax[-1]} galcoeff: {str(galcoeff).replace(' ', '')} isocoeff: {isocoeff}")
        
    #results
    ressource = []

    startDataTT = _source[0].get("startDataTT")['value']
    ressource += [startDataTT]
    endDataTT = _source[0].get("endDataTT")['value']
    ressource += [endDataTT]
    sqrtts = _source[0].get("multiSqrtTS")['value']
    ressource += [sqrtts]
    flux = _source[0].get("multiFlux")['value']
    ressource += [flux]
    flux_error = _source[0].get("multiFluxErr")['value']
    ressource += [flux_error]
    counts = _source[0].get("multiCounts")['value']
    ressource += [counts]
    countsErr = _source[0].get("multiCountsErr")['value']
    ressource += [countsErr]
    multiExp = _source[0].get("multiExp")['value']
    ressource += [multiExp]
    multiExpRatio = _source[0].get("multiExpRatio")['value']
    ressource += [multiExpRatio]
    index = _source[0].get("multiIndex")['value']
    ressource += [index]
    indexError = _source[0].get("multiIndexErr")['value']
    ressource += [indexError]
    dist = _source[0].get("multiDistFromStartPositionPeak")['value']
    ressource += [dist]
    sourcename = _source[0].get("multiName")['value']
    ressource += [sourcename]
    ressource += [int(emin[0])]
    ressource += [int(emax[-1])]
    ressource += [str(galcoeff).replace(' ', '')]
    ressource += [str(isocoeff).replace(' ', '')]

    fullsource = []
    fullsource += [ressource]

    ag.logger.info(f"ressource: {ressource}")

    fullres = []
    fullresred = []

    ag.logger.info(f"Starting bins analysis loop..")

    for index, em in enumerate(emin):
        
        ag.logger.info(f"Emin: {em}, Emax: {emax[index]}")
                 
        confFilePath = Path(args.outputdir).joinpath(f"./agilepy_conf_mle_{int(emin[index])}_{int(emax[index])}.yaml")
                
        AGAnalysis.getConfiguration(
            confFilePath = str(confFilePath),
            evtfile=evtfile,
            logfile = logfile,
            userName = args.username,
            sourceName = args.sourcename,
            tmin = tstart,
            tmax = tstop,
            timetype = "TT",
            glon = args.glon,
            glat = args.glat,
            outputDir = str(ag.getOption("outdir").joinpath(f"spectra_{int(emin[index])}_{int(emax[index])}")),
            verboselvl = 0,
            userestapi = False,
            datapath = "$HOME/agile_dataset"
        )
        
        s1 = \
            SpectraSingleBin \
                .calculateSpectraOnSingleEnergyBin(
                    confFilePath, args.sourcename, _source[0], 
                    int(emin[index]), int(emax[index]), args.dq, 
                    args.filtercode, galcoeff[index], isocoeff[index] )
        

        resspectra = []
        resspectrared = []
        s1_emin = float(s1.get("multiEmin")['value'][0])
        resspectra += [s1_emin]
        resspectrared += [s1_emin]
        s1_emax = float(s1.get("multiEmax")['value'][0])
        resspectra += [s1_emax]
        resspectrared += [s1_emax]
        s1_sqrtts = s1.get("multiSqrtTS")['value']
        resspectra += [s1_sqrtts]
        resspectrared += [s1_sqrtts]
        s1_flux = s1.get("multiFlux")['value']
        resspectra += [s1_flux]
        resspectrared += [s1_flux]
        s1_flux_error = s1.get("multiFluxErr")['value']
        resspectra += [s1_flux_error]
        resspectrared += [s1_flux_error]
        s1_multiUL = s1.get("multiUL")['value']
        resspectra += [s1_multiUL]
        resspectrared += [s1_multiUL]
        s1_multiExp = s1.get("multiExp")['value']
        resspectra += [s1_multiExp]
        resspectrared += [s1_multiExp]
        s1_multiErgLog = s1.get("multiErgLog")['value']
        resspectra += [s1_multiErgLog]
        s1_multiErgLogErr = s1.get("multiErgLogErr")['value']
        resspectra += [s1_multiErgLogErr]
        s1_multiErgLogUL = s1.get("multiErgLogUL")['value']
        resspectra += [s1_multiErgLogUL]
        s1_counts = s1.get("multiCounts")['value']
        resspectra += [s1_counts]
        s1_countsErr = s1.get("multiCountsErr")['value']
        resspectra += [s1_countsErr]

        s1_multiExpRatio = s1.get("multiExpRatio")['value']
        resspectra += [s1_multiExpRatio]
        print(resspectra)
        
        fullres += [resspectra]
        fullresred += [resspectrared]
        index += 1
        

    ######################################## SAVING RESULTS ########################################
    ag.logger.info(f"Saving results..")
    Path(args.outputdir).joinpath("results").mkdir(parents=True, exist_ok=True)

    fileout = f"{args.ow}-FLT{args.ffilter}COR{args.correction}-FF{args.filtercode}-TB{args.timebin}shift{args.timeshift}-{emin}-{emax}-fov{args.fovradmax}-edpc{args.edpcorrection}-fc{args.fluxcorrection}.mle{nchannels}"


    df = pd.DataFrame(fullres, columns=['emin', 'emax', 'sqrtTS', 'flux', 'fluxErr', 'fluxUL', 'exp', 
                                        'fluxErg', 'fluxErgErr', 'fluxErgUL', 'counts', 'countsErr', 'expratio' ])
    df.to_csv(Path(args.outputdir).joinpath("results", fileout ).with_suffix(".csv"), index=False, sep=" ")


    dfs = pd.DataFrame(fullsource, columns=['startdata', 'enddata', 'sqrtTS', 'flux', 'fluxErr', 'counts', 'countsErr', 'exp', 'expratio', 'index', 'indexErr', 'dist', 'name', 'emin', 'emax', 'galcoeff', 'isocoeff' ])
    df.to_csv(Path(args.outputdir).joinpath("results", fileout ).with_suffix(".source.csv"), index=False, sep=" ")

    
    ######################################## LIGHT CURVE ########################################
    _sources = ag.freeSources(f'name == "{args.sourcename}"', "pos", False, show=True)
    _sources = ag.freeSources(f'name == "{args.sourcename}"', "index", False, show=True)    
    lightCurveData = ag.lightCurveMLE(args.sourcename, binsize=args.timebin)
    ag.displayLightCurve("mle", saveImage=True)
    df3 = pd.read_csv(lightCurveData, sep=" ")
    df4 = df3[['time_start_tt', 'time_end_tt', 'flux', 'flux_err', 'sqrt(ts)', 'sqrt(ts)', 'flux_ul', 'exposure', 'counts']]
    emin=emin[0]
    emax=emax[nchannels-1]
    fileout = f"{args.ow}-FLT{args.ffilter}COR{args.correction}-FF{args.filtercode}-TB{args.timebin}shift{args.timeshift}-{emin}-{emax}-fov{args.fovradmax}-edpc{args.edpcorrection}-fc{args.fluxcorrection}.mle{nchannels}"
    os.system(f"cp {lightCurveData} {Path(args.outputdir).joinpath('results', fileout).with_suffix('.csv')}")


if __name__ == "__main__":
    main()