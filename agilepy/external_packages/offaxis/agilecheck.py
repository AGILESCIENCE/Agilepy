import matplotlib.pyplot as plt
import os
import pylab
import numpy as np
import datetime
import matplotlib
from matplotlib import*
import matplotlib.pyplot as plt
import astropy
from astropy.time import Time
from astropy import coordinates as coord
from astropy import units as u
from astropy.coordinates import SkyCoord
#import aplpy
#import pyfits
from astropy.io import fits
from matplotlib.ticker import MultipleLocator, FormatStrFormatter
import bisect

def agileMET_to_mjd(t_in):
    """ Returns the variable t_in, expressed AGILE MET seconds, converted to MJD
        Input: t_in, AGILE MET in seconds
        Output: t_mjd, AGILE MJD time
    """
    tref   = datetime.datetime(2004,1,1,0,0,0)
    t_temp = tref + datetime.timedelta(seconds=t_in)
    time2  = Time(t_temp, format='datetime')
    t_mjd  = time2.mjd
    return t_mjd


class agilecheck:
    """ This class provides a series of calculations and plots to check the off-axis angle of a source wrt AGILE center FoV.


         Written by: P. Munar-Adrover
         Version 2.0
         Last edition: 2016-09-29



        Input parameters:
        - agile_spacecraft: string, name of the SC agile file, resulted from merging log files
        - src_ra: float, right ascension of the source of interest (unit: degrees)
        - src_dec: float, declination of the source of interest (unit: degrees)
        - zmax: maximum zenith distance of the source to the center of the detector
          (unit: degrees)
        - timelimiti(optional): float, inferior observation time limit to analize.
          If left blank, timelimiti is set to the initial time in the agile_spacecraft
          file
        - timelimitf (optional): float, inferior observation time limit to analize.
          If left blank, timelimiti is set to the final time in the agile_spacecraft
          file
        - step (optional): integer, time interval in seconds between 2 consecutive points
          in the resulting plot. Minimum accepted value: 0.1 s. If left blank, step=0.1 is
          chosen

        Functions within the class:
        calc_separation
        calc_mjd
        calc_mjd_simple
        WriteTimes
        PlotVisibility
    """


    def __init__(self, agile_spacecraft, src_ra, src_dec, tstart, tstop, logger, zmax=75., timelimiti=-1, timelimitf=-1, step=0.1, out_name = "output_agile.txt"):
        self.agile_spacecraft = agile_spacecraft
        self.zmax        = zmax
        self.src_ra      = src_ra
        self.src_dec     = src_dec
        self.timelimiti  = timelimiti
        self.timelimitf  = timelimitf
        self.step        = step*10.
        self.out_name = out_name
        self.tstart = tstart
        self.tstop = tstop
        self.logger = logger

    def calc_separation(self):
        """ Function that computes the angular separation between the center of the
        AGILE GRID field of view and the coordinates for a given position in the sky,
        given by src_ra and src_dec.
            Output: separation (array), time_i (array), time_f (array)
        """

        self.logger.info(self, "Computing angular distance to the center of f.o.v")
        self.logger.info(self, "This might take a while...")

        # reading the Attitude AGILE file (the one created by merging the .log files)
        file1 = fits.open(self.agile_spacecraft)
        SC = file1[1].data
        file1.close()

#       This is to avoid problems with moments for which the AGILE pointing was set to RA=NaN, DEC=NaN
        TIME = SC['TIME'][np.logical_not(np.isnan(SC['ATTITUDE_RA_Y']))]
        #TIME = SC["TIME"][SC['MODE'] != 0]
        ATTITUDE_RA_Y = SC['ATTITUDE_RA_Y'][np.logical_not(np.isnan(SC['ATTITUDE_RA_Y']))]
        #ATTITUDE_RA_Y = SC["ATTITUDE_RA_Y"][SC['MODE'] != 0]
        ATTITUDE_DEC_Y = SC['ATTITUDE_DEC_Y'][np.logical_not(np.isnan(SC['ATTITUDE_DEC_Y']))]
        #ATTITUDE_DEC_Y = SC["ATTITUDE_DEC_Y"][SC['MODE'] != 0]

        deltatime = 0.1 # AGILE attitude is collected every 0.1 s

        # if non specified, the initial and final time will be the first and last time in the SC file, respectively
        if self.timelimiti == -1 or self.timelimiti < np.min(TIME):
            self.timelimiti = np.min(TIME)
        if self.timelimitf == -1 or self.timelimitf > np.max(TIME):
            self.timelimitf = np.max(TIME)

        # selecting the index corresponding to the time prior to the selected timelimiti (in case timelimiti does not
        # coincide with any given time in the SC file)
        index_ti = bisect.bisect_left(TIME,self.timelimiti)

        # selecting the index corresponding to the time after to the selected timelimitf (in case timelimitf does not
        # coincide with any given time in the SC file)
        index_tf = bisect.bisect_left(TIME,self.timelimitf)

        # creating arrays filled with zeros
        src_raz  = np.zeros(len(TIME[index_ti:index_tf:int(self.step)]))
        src_decz  = np.zeros(len(TIME[index_ti:index_tf:int(self.step)]))

        # filling the just created arrays with our coordinates of interest
        src_ra   = src_raz + self.src_ra
        src_dec   = src_decz + self.src_dec

        c1  = SkyCoord(src_ra, src_dec, unit='deg', frame='icrs')
        c2  = SkyCoord(ATTITUDE_RA_Y[index_ti:index_tf:int(self.step)], ATTITUDE_DEC_Y[index_ti:index_tf:int(self.step)], unit='deg', frame='icrs')
#        print 'c1=', len(c1), 'c2=', len(c2) # to ensure c1 and c2 have the same length
        sep = c2.separation(c1)
        return np.asfarray(sep), TIME[index_ti:index_tf:int(self.step)], TIME[index_ti:index_tf:int(self.step)]+deltatime

    def calc_mjd(self):
        """
        Function that transforms a given array-like time in MET (Missin Ellapsed Time) to MJD
        (Modified Julian Date).
        Output: t_start (array), t_stop (array)
        """
        self.logger.info(self, "Converting MET to MJD time.")
        self.logger.info(self,"This might take a while...")

        file     = fits.open(self.agile_spacecraft)
        SC       = file[1].data
        file.close()

#       This is to avoid problems with moments for which the AGILE pointing was set to RA=NaN, DEC=NaN
        TIME = SC['TIME'][np.logical_not(np.isnan(SC['ATTITUDE_RA_Y']))]
        #TIME = SC["TIME"][SC['MODE'] != 0]
        #ATTITUDE_RA_Y = SC['ATTITUDE_RA_Y'][np.logical_not(np.isnan(SC['ATTITUDE_RA_Y']))]
        #ATTITUDE_RA_Y = SC["ATTITUDE_RA_Y"][SC['MODE'] != 0]
        #ATTITUDE_DEC_Y = SC['ATTITUDE_DEC_Y'][np.logical_not(np.isnan(SC['ATTITUDE_DEC_Y']))]
        #ATTITUDE_DEC_Y = SC["ATTITUDE_DEC_Y"][SC['MODE'] != 0]

        deltatime = 0.1
        if self.timelimiti == -1 or self.timelimiti < np.min(TIME):
            self.timelimiti = np.min(TIME)
        if self.timelimitf == -1 or self.timelimitf > np.max(TIME):
            self.timelimitf = np.max(TIME)
        index_ti = bisect.bisect_left(TIME,self.timelimiti)
        index_tf = bisect.bisect_left(TIME,self.timelimitf)
        self.logger.info(self, f"Time_i = {TIME[index_ti]}")
        self.logger.info(self, f"Time_f = {TIME[index_tf]}")
        tref     = datetime.datetime(2004,1,1,0,0,0)
        t_mjd  = []
        for i in np.arange(index_ti,index_tf, int(self.step)):
            time         = TIME[i]
            t_temp       = tref + datetime.timedelta(seconds=time)
            time2        = Time(t_temp, format='datetime')
            time_date    = time2.mjd
            t_mjd.append(time_date)
        return np.asfarray(t_mjd), np.asfarray(t_mjd)+deltatime

    def calc_mjd_simple(self, t_in):
        """ Returns the variable t_in, expressed AGILE MET seconds, converted to MJD
            Input: t_in, AGILE MET in seconds
            Output: t_mjd, AGILE MJD time
        """
        tref   = datetime.datetime(2004,1,1,0,0,0)
        t_temp = tref + datetime.timedelta(seconds=t_in)
        time2  = Time(t_temp, format='datetime')
        t_mjd  = time2.mjd
        return t_mjd

    def PlotVisibility(self, twocolumn=False, show=False, histogram=True, im_fmt='eps', plot=True):
        """PlotVisibility makes a plot of the zenith distance of a given source
           (src_ra and src_dec selected in the agilecheck parameters).

           Input (optional) parameters:
           - twocolumn: boolean, True or False (default). If two column=True, the
             plot is adjusted to the size of a two column journal publication.
           - show: boolean, True or False (default). If set to True the plot is
             displayed in the interactive ipython plotting window.
           - im_fmt: string, desired format for the image to be stored (if show=False
             is selected). Current supported formats are: 'eps', 'jpg', 'png', 'ps', 'pdf'.
           - histogram: boolean, True or False (default). If set to True a histogram of
             the percentage of time spent at diferent zenith distance bins (10 degrees bins)
             is saved.
        """

#=================================================================
#====================== plotting settings ========================
#=================================================================

        if twocolumn == True:
            fig_width_pt = 255.76535
            fontsize     = 12
        else:
            fig_width_pt = 426.79134
            fontsize     = 10


        inches_per_pt = 1.0/72.27               # Convert pt to inch
        golden_mean = (np.sqrt(5)+1.0)/2.0         # Aesthetic ratio
        fig_width = fig_width_pt*inches_per_pt  # width in inches
        fig_height = fig_width/golden_mean      # height in inches
        fig_size =  [fig_width,fig_height]

        params = {'backend': 'pdf',
            'axes.labelsize': fontsize,
            'font.size': fontsize,
            'legend.fontsize': fontsize,
            'xtick.labelsize': fontsize,
            'ytick.labelsize': fontsize,
            'axes.linewidth': 0.5,
            'lines.linewidth': 0.5,
            #'text.usetex': True,
            'ps.usedistiller': False,
            'figure.figsize': fig_size,
            'font.family': 'Times New Roman',
            'font.serif': ['Bitstream Vera Serif']}
        pylab.rcParams.update(params)
#================== end of plotting settings =====================

        separation, tTTi, tTTf = self.calc_separation()

        separation = separation.value
        ti_mjd = []
        tf_mjd = []

        for i in np.arange(len(tTTi)):
            timjd = self.calc_mjd_simple(tTTi[i])
            tfmjd = self.calc_mjd_simple(tTTf[i])
            ti_mjd.append(timjd)
            tf_mjd.append(tfmjd)

        ti_mjd = np.array(ti_mjd)
        tf_mjd = np.array(tf_mjd)

        total_obs = (np.max(tf_mjd)-np.min(ti_mjd))//1 # in days
        meantime = (ti_mjd+tf_mjd)/2.

        deltat = tTTf - tTTi
        deltat1 = deltat[1]

        #num_obs = (self.tstop-self.tstart )*86400 / 5460
        #idle_secs = num_obs * 900

        ttotal_obs = np.sum(deltat)
        ttotal_abs = (self.tstop-self.tstart)*86400
        ttotal_under_zmax = np.sum(tTTf[separation<self.zmax]-tTTi[separation<self.zmax])
        #ttotal_above_zmax = np.sum(tTTf[separation>self.zmax]-tTTi[separation>self.zmax])

        self.logger.info(self, f"Total integration time = {'{0:.2f}'.format(ttotal_obs*self.step)} s Total_bins: {total_obs} {len(tTTf)} Mean sep. < {self.zmax}: {str(round(np.mean(separation[separation<self.zmax]),4))}")
        self.logger.info(self, f"Total absolute time= {'{0:.2f}'.format(ttotal_abs)}") #NEW
        self.logger.info(self, f"Total time spent at separation < {self.zmax} deg: {'{0:.2f}'.format(ttotal_under_zmax*self.step)} s")
        self.logger.info(self, f"Relative time spent at separation < {self.zmax} deg: {'{0:.2f}'.format((ttotal_under_zmax*self.step)/(ttotal_obs*self.step)*100.)} %%")
        self.logger.info(self, f"Relative time spent at separation > {self.zmax} deg: {'{0:.2f}'.format(((ttotal_obs*self.step)-(ttotal_under_zmax*self.step)) / (ttotal_obs*self.step)*100.)} %%")
        self.logger.info(self, f"Absolute time spent at separation < {self.zmax} deg: {'{0:.2f}'.format((ttotal_under_zmax*self.step)/(ttotal_abs)*100.)} %%") #NEW
        self.logger.info(self, f"Absolute time spent at separation > {self.zmax} deg: {'{0:.2f}'.format(((ttotal_obs*self.step)-(ttotal_under_zmax*self.step)) / (ttotal_abs)*100.)} %%") #NEW
        self.logger.info(self, f"Duty Cycle: {'{0:.2f}'.format((((ttotal_obs*self.step) / (ttotal_abs)))*100.)} %%") #NEW

        f = open(self.out_name, "a")
        print("AGILE", file=f)
        print ("Total integration time=", "{0:.2f}".format(ttotal_obs*self.step), " s", 'Total_bins:', total_obs, len(tTTf), 'Mean sep. < ', self.zmax, ':', str(round(np.mean(separation[separation<self.zmax]),4)), file=f)
        print("Total absolute time=", "{0:.2f}".format(ttotal_abs), file=f) #NEW
        print("Total time spent at separation < ", self.zmax, " deg:", "{0:.2f}".format(ttotal_under_zmax*self.step), "s", file=f)
        print("Relative time spent at separation <", self.zmax, " deg:",  "{0:.2f}".format((ttotal_under_zmax*self.step)/(ttotal_obs*self.step)*100.), "%", file=f)
        print("Relative time spent at separation >", self.zmax, " deg:", "{0:.2f}".format(((ttotal_obs*self.step)-(ttotal_under_zmax*self.step)) / (ttotal_obs*self.step)*100.), "%",file=f)
        print("Absolute time spent at separation <", self.zmax, " deg:", "{0:.2f}".format((ttotal_under_zmax*self.step)/(ttotal_abs)*100.), " %", file=f) #NEW
        print("Absolute time spent at separation >", self.zmax, " deg:", "{0:.2f}".format(((ttotal_obs*self.step)-(ttotal_under_zmax*self.step)) / (ttotal_abs)*100.), " %", file=f) #NEW
        print("Duty Cycle: ", "{0:.2f}".format((((ttotal_obs*self.step) / (ttotal_abs)))*100.), "%", file=f) #NEW
        f.close()

        kk = open("times_bins_vs_separation.txt", "w")
        filesep = open('time_vs_separation_agile.txt', 'w')
        for i in np.arange(len(separation)):
            print(meantime[i], separation[i], file=filesep)
            print(tTTi[i], tTTf[i], separation[i], file=kk)
        filesep.close()
        kk.close()



# This commented lines where to plot grey shade in the corresponding detected flares by AGILE for MWC 656
#        agile_i = np.array([217468930.0, 236347395.0, 252763332.0, 298123266.0, 299548866.0, 301708933.0, 324000132.0, 339724932.0, 384307200.0, 395107200.0])
#        agile_f = np.array([217598530.0, 236498595.0, 252979332.0, 298231266.0, 299721666.0, 301881732.0, 324172932.0, 339897732.0, 384393600.0, 395280000.0])

#        tref     = datetime.datetime(2001,1,1,0,0,0)
#        t_agilestart  = []
#        t_agilestop   = []
#        for i in np.arange(len(agile_i)):
#            time_i       = agile_i[i]
#            time_f       = agile_f[i]
#            t_start_temp = tref + datetime.timedelta(seconds=time_i)
#            t_stop_temp  = tref + datetime.timedelta(seconds=time_f)
#            tstart       = Time(t_start_temp, format='datetime')
#            tstop        = Time(t_stop_temp, format='datetime')
#            tstart_data  = tstart.mjd
#            tstop_data   = tstop.mjd
#            t_agilestart.append(tstart_data)
#            t_agilestop.append(tstop_data)

#        t_agilei_mjd = np.asfarray(t_agilestart)
#        t_agilef_mjd = np.asfarray(t_agilestop)

#        for i in np.arange(len(t_agilei_mjd)):
#            ax.fill_between([t_agilei_mjd[i], t_agilef_mjd[i]], 0, 200, color='grey', alpha=0.5)

        if plot == True:
            self.logger.info(self, 'Plotting figure...')
            f  = plt.figure()
            ax = f.add_subplot(111)
            ax.plot(meantime, separation, '-b')
#            ax.plot(meantime[separation < self.zmax], separation[separation < self.zmax], '-r')

            ax.set_ylim(0., self.zmax+5.0)
            ax.set_xlabel('MJD')
            ax.set_ylabel('off-axis angle [$^{\\circ}$]')

            self.logger.info(self, 'Saving figure...')
            ax.set_xlim(np.min(meantime), np.max(meantime))
            if show==True:
                f.show()
            else:
                f.savefig('agile_visibility_ra'+str(self.src_ra)+'_dec'+str(self.src_dec)+'_tstart'+str(np.min(tTTi))+'_tstop'+str(np.max(tTTf))+'.'+str(im_fmt))

        if histogram == True:
            self.logger.info(self, "Plotting histogram...")
            bins  = [0, 10, 20, 30, 40, 50, 60, 70]
            bins2 = [70, 180]
            hist, bins = np.histogram(separation, bins=bins, density=False)
            hist2, bins2 = np.histogram(separation, bins=bins2, density=False)
            width = 1. * (bins[1] - bins[0])
            center = (bins[:-1] + bins[1:]) / 2
            width2 = 1. * (bins2[1] - bins2[0])
            center2 = (bins2[:-1] + bins2[1:]) / 2
#            print hist, bins, center, width
#            print hist2, bins2, center2, width2
#            print len(separation)

            f2  = plt.figure()
            ax2 = f2.add_subplot(111)
            ax2.bar(center, hist*deltat1/ttotal_obs*100., align='center', color='w', edgecolor='b', width=width)
            ax2.bar(center2, hist2*deltat1/ttotal_obs*100., align='center', color='w', edgecolor='b', width=width2)

            ax2.set_xlim(0., 100.)
            ax2.set_ylim(0., 100.)
            ax2.set_ylabel('\\% of time spent')
            ax2.set_xlabel('off-axis angle $[^\\circ]$')
            labels  = [0, 10, 20, 30, 40, 50, 60, 180]
            xlabels = [0, 10, 20, 30, 40, 50, 60, 100]
            plt.xticks(xlabels, labels)

            #fil = open('agile_histogram_visibility'+str(self.src_ra)+'_dec'+str(self.src_dec)+'_tstart'+str(np.min(tTTi))+'_tstop'+str(np.max(tTTf))+'.txt', 'w')
            fil = open('agile_histogram_visibility.txt', 'w')
            for i in np.arange(len(center)):
                print(center[i], hist[i]*deltat1/ttotal_obs*100., width, file=fil)
            for i in np.arange(len(center2)):
                print(center2[i], hist2[i]*deltat1/ttotal_obs*100., width2, file=fil)
            fil.close()

            self.logger.info(self, 'Saving figure...')
            if show==True:
                f2.show()
            else:
                f2.savefig('agile_histogram_ra'+str(self.src_ra)+'_dec'+str(self.src_dec)+'_tstart'+str(np.min(tTTi))+'_tstop'+str(np.max(tTTf))+'.'+str(im_fmt))
            return ttotal_obs, np.concatenate((hist,hist2))
