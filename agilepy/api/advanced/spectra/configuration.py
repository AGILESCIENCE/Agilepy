import numpy as np

class Configuration:

    @staticmethod
    def getEvtFile(ffilter):
        if ffilter == 0:
            #GLS
            return "/ASDC_PROC2/FM3.119_2/INDEX/EVT.index"
        if ffilter == 1:
            #GLSP
            return "$HOME/shared_dir/GRB221009A/DATA/FM3.ALL_2/INDEX/EVT.index"

    @staticmethod
    def getLogFile(correction):
        if correction == 0:
            #logfile = "/shared_dir/GRB221009A/DATA/DATA_2/INDEX/LOG.log.index"
            return "/ASDC_PROC2/DATA_2/INDEX/LOG.log.index"
        if correction == 1:
            return "$HOME/shared_dir/GRB221009A/DATA/DATA_COR/INDEX/LOG.log.index"
        
    @staticmethod
    def getTimes(ow, t0, timeshift):
        if ow == "":
            timeshift = 5
            t0 = t0 - timeshift
            tstart = t0+200
            tstop = t0+1000
            return t0, tstart, tstop
        if ow == "OW1":
            tstart = t0+245
            tstop = t0+395
            return t0, tstart, tstop
        if ow == "OW1a":
            tstart = t0+245
            tstop = t0+305
            return t0, tstart, tstop
        if ow == "OW1b":
            tstart = t0+305
            tstop = t0+395
            return t0, tstart, tstop
        if ow == "OW2":
            tstart = t0+685
            tstop = t0+835
            return t0, tstart, tstop
        if ow == "OW3":
            tstart = t0+1130
            tstop = t0+1280
            return t0, tstart, tstop
        if ow == "OW4":
            tstart = t0+1570
            tstop = t0+1720        
            return t0, tstart, tstop
        raise Exception("Invalid ow value: "+ow)
    
    @staticmethod
    def getEnergyBins(channels_conf):
        if channels_conf == "C0":
            eb = [[30, 50000]]
        elif channels_conf == "C1":
            eb = [[100, 50000]]
        elif channels_conf == "C2":
            eb = [[30, 50], [50, 100], [100, 50000]]
        elif channels_conf == "C3":
            eb = [[100, 300], [300, 1000],  [1000, 3000],  [3000, 10000], [10000, 50000]]
        elif channels_conf == "C4":
            eb = [[50, 100], [100, 300], [300, 1000],  [1000, 3000],  [3000, 10000], [10000, 50000]]
        elif channels_conf == "C5":
            eb = [[50, 100], [100, 300], [300, 1000],  [1000, 3000],  [3000, 50000]]
        elif channels_conf == "C6":
            eb = [[50, 100], [100, 50000]]
        elif channels_conf == "C7":
            eb = [[50, 50000]]
        else:
            raise Exception("Invalid channels_conf value: "+channels_conf)

        return eb, len(eb), np.matrix(eb).min(), np.matrix(eb).max()
       
    @staticmethod
    def getGalIsoCoeff(filtercode, nchannels, emin, emax, edpcorrection):
        isocoeff = None
        galcoeff = None
        calcbkg = None

        if filtercode == 5 and nchannels == 1:
            if emin==30:
                if emax == 50:
                    galcoeff=[0.538993]
                    isocoeff=[16.6994]
                    calcbkg = False
                if emax == 50000:
                    galcoeff=[0.916092]
                    isocoeff=[32.1323]
                    calcbkg = False

            if emin == 100 and edpcorrection == 0:
                if emax == 50000:
                    galcoeff=[0.99496]
                    isocoeff=[8.5993]
                    calcbkg = False
                    
            if emin == 50 and edpcorrection == 0:
                if emax == 50000:
                    galcoeff=[0.50619] 
                    isocoeff=[19.1248]
                    calcbkg = False
            
            if emin == 100 and edpcorrection == 1:
                if emax == 50000:
                    galcoeff=[0.809928]
                    isocoeff=[6.97784]
                    calcbkg = False

        elif filtercode == 0 and nchannels == 1:
            if emin == 30:
                if emax == 50000:
                    galcoeff=[0.383978]
                    isocoeff=[90.9461]
                    calcbkg = False
            if emin == 50 and edpcorrection == 0:
                galcoeff=[0.598607] 
                isocoeff = [95.0167]
                calcbkg = False
                
            if emin == 100:
                if nchannels == 1 and emax == 50000 and edpcorrection == 0:
                    galcoeff=[1.15168]
                    isocoeff=[68.4577]
                    calcbkg = False

        elif nchannels > 1:
            calcbkg=True
            if nchannels == 6 and emin == 50 and filtercode == 0:
                galcoeff = [0.357662, 0.492034, 0.803689, 0.79751, 0.052694, 1.12412e-07] 
                isocoeff = [55.1059, 24.9061, 6.50057, 4.95914, 3.84313, 0.611997]
                calcbkg=False
            if nchannels == 6 and emin == 50 and filtercode == 5:
                galcoeff = [0.251742, 0.433215, 0.641693, 0.766406, 0.565295, 0.52546] 
                isocoeff = [12.7873, 5.64787, 1.23158, 0.460403, 1.06581e-12, 0.163649]
                calcbkg=False
            if nchannels == 5 and emin == 50 and filtercode == 0:
                galcoeff = [0.367802, 0.477324, 0.806744, 0.797866, 2.10078e-07] 
                isocoeff = [55.5768, 25.3146, 6.55635, 4.95946, 3.59756]
                calcbkg=False
            if nchannels == 5 and emin == 100 and filtercode == 5 and edpcorrection == 0:
                galcoeff = [0.477182, 1.03425, 0.660031, 0.134394, 1.38102] 
                isocoeff = [6.56676, 2.04145, 0.377544, 3.14748e-11, 0.473654] 
                calcbkg=False       
            if nchannels == 5 and emin == 100 and filtercode == 5 and edpcorrection == 1:
                galcoeff = [0.422366, 0.645264, 0.756601, 0.541866, 0.480979]
                isocoeff = [5.76807, 1.22284, 0.476669, 2.34368e-09, 0.181017]
                calcbkg=False
            if nchannels == 2 and emin == 50 and filtercode == 5 and edpcorrection == 0:
                galcoeff = [0.200853, 0.99915]
                isocoeff = [11.5295, 8.73058]
                calcbkg =False 
            if nchannels == 2 and emin == 50 and filtercode == 0 and edpcorrection == 0:
                galcoeff = [0.300311, 1.15633] 
                isocoeff = [49.0889, 45.4845]
                calcbkg =False 
        
        if isocoeff is None or galcoeff is None or calcbkg is None:
            raise Exception("Invalid combination of filtercode, nchannels, emin, emax, edpcorrection values: "+str(filtercode)+", "+str(nchannels)+", "+str(emin)+", "+str(emax)+", "+str(edpcorrection))
        
        return galcoeff, isocoeff, calcbkg