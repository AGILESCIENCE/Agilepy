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
import numpy as np
from time import time
from astropy.coordinates import SkyCoord
from astropy import units as u
from astropy.io import fits
from astropy.time import Time
import matplotlib.pyplot as plt
import datetime


class AGEng:

    @staticmethod
    def computeAGILEAngularDistanceFromSource(logfilesIndex, tmin, tmax, l=None, b=None, ra=None, dec=None, zmax=60, step=1):

        start_t = time()

        if l is not None and b is not None:
            skyCords = SkyCoord(l=l*u.degree, b=b*u.degree, frame='galactic')
            skyCordsFK5 = skyCords.transform_to('icrs')
        else:
            skyCordsFK5 = SkyCoord(ra=ra*u.degree, dec=dec*u.degree, frame='icrs')

        logFiles = AGEng._getLogsFileInInterval(logfilesIndex, tmin, tmax)

        print("%d log files satisfy the interval %f-%f"%(len(logFiles), tmin, tmax))

        if not logFiles:
            print("No files.")
            exit(1)

        sep, time_s, time_e = AGEng._calcSeparation(logFiles, tmin, tmax, skyCordsFK5, zmax, step)

        end_t = time() - start_t

        print("Took %f seconds"%(end_t))

        return sep, time_s, time_e, skyCordsFK5.ra.deg, skyCordsFK5.dec.deg

    @ staticmethod
    def _calcSeparation(logFiles, tmin, tmax, skyCordsFK5, zmax, step):
        """ Function that computes the angular separation between the center of the
        AGILE GRID field of view and the coordinates for a given position in the sky,
        given by src_ra and src_dec.

        - logfilesIndex:
        - src_ra: float, right ascension of the source of interest (unit: degrees)
        - src_dec: float, declination of the source of interest (unit: degrees)
        - zmax: maximum zenith distance of the source to the center of the detector
          (unit: degrees)
        - tmin(optional): float, inferior observation time limit to analize.
          If left blank, timelimiti is set to the initial time in the agile_spacecraft
          file
        - tmax (optional): float, inferior observation time limit to analize.
          If left blank, timelimiti is set to the final time in the agile_spacecraft
          file
        - step (optional): integer, time interval in seconds between 2 consecutive points
          in the resulting plot. Minimum accepted value: 0.1 s. If left blank, step=0.1 is
          chosen

          Output: separation (array), time_i (array), time_f (array)

        """
        total = len(logFiles)
        tmin_start = tmin
        tmax_start = tmax

        sep_tot = None
        time_i_tot = None
        time_f_tot = None
        init = False

        for idx, logFile in enumerate(logFiles):

            idx = idx + 1

            if idx == 1 or idx == total:
                doTimeMask = True
            else:
                doTimeMask = False

            print("%d/%d %s"%(idx,total,logFile))

            sep, time_i, time_f = AGEng.computeSeparationPerFile(doTimeMask, logFile, tmin_start, tmax_start, skyCordsFK5, zmax, step)

            if not init:
                sep_tot = sep
                time_i_tot = time_i
                time_f_tot = time_f
                init = True
            else:
                sep_tot = np.concatenate((sep_tot, sep), axis=0)
                time_i_tot = np.concatenate((time_i_tot, time_i), axis=0)
                time_f_tot = np.concatenate((time_f_tot, time_f), axis=0)

            #print("sep: ", sep, len(sep), type(sep), sep.dtype)
            #print("time_i: ", time_i, len(time_i), type(time_i), time_i.dtype)

            #print("sep_tot: ", sep_tot, len(sep_tot), type(sep_tot), sep_tot.dtype)
            #print("time_i_tot: ", time_i_tot, len(time_i_tot), type(time_i_tot), time_i_tot.dtype)

            #input("..")

        return sep, time_i, time_f

    @staticmethod
    def computeSeparationPerFile(doTimeMask, logFile, tmin_start, tmax_start, skyCordsFK5, zmax, step):

        hdulist = fits.open(logFile)
        SC = hdulist[1].data

        if doTimeMask:
            # Filtering out
            booleanMask = np.logical_and(SC['TIME'] >= tmin_start, SC['TIME'] <= tmax_start)
            TIME = SC['TIME'][booleanMask]
            ATTITUDE_RA_Y= SC['ATTITUDE_RA_Y'][booleanMask]
            ATTITUDE_DEC_Y= SC['ATTITUDE_DEC_Y'][booleanMask]

        else:
            TIME = SC['TIME']
            ATTITUDE_RA_Y= SC['ATTITUDE_RA_Y']
            ATTITUDE_DEC_Y= SC['ATTITUDE_DEC_Y']

        hdulist.close()

        # This is to avoid problems with moments for which the AGILE pointing was set to RA=NaN, DEC=NaN
        booleanMaskRA = np.logical_not(np.isnan(ATTITUDE_RA_Y))
        booleanMaskDEC = np.logical_not(np.isnan(ATTITUDE_DEC_Y))

        TIME = TIME[booleanMaskRA]
        ATTITUDE_RA_Y= ATTITUDE_RA_Y[booleanMaskRA]
        ATTITUDE_DEC_Y= ATTITUDE_DEC_Y[booleanMaskDEC]


        deltatime = 0.1 # AGILE attitude is collected every 0.1 s

        tmin = np.min(TIME)
        tmax = np.max(TIME)

        index_ti = 0
        index_tf = len(TIME)-1

        # creating arrays filled with zeros
        src_raz  = np.zeros(len(TIME[index_ti:index_tf:int(step)]))
        src_decz  = np.zeros(len(TIME[index_ti:index_tf:int(step)]))

        # filling the just created arrays with our coordinates of interest
        src_ra   = src_raz + skyCordsFK5.ra
        src_dec   = src_decz + skyCordsFK5.dec

        c1  = SkyCoord(src_ra, src_dec, unit='deg', frame='icrs')
        c2  = SkyCoord(ATTITUDE_RA_Y[index_ti:index_tf:int(step)], ATTITUDE_DEC_Y[index_ti:index_tf:int(step)], unit='deg', frame='icrs')
#        print 'c1=', len(c1), 'c2=', len(c2) # to ensure c1 and c2 have the same length
        sep = c2.separation(c1)

        return np.asfarray(sep), TIME[index_ti:index_tf:int(step)], TIME[index_ti:index_tf:int(step)]+deltatime


    @staticmethod
    def _getLogsFileInInterval(logfilesIndex, tmin, tmax):

        logsFiles = []

        with open(logfilesIndex, "r") as lfi:
            lines = [line.strip() for line in lfi.readlines()]

        for line in lines:
            elements = line.split(" ")
            logFilePath = elements[0]
            logFileTmin = float(elements[1])
            logFileTmax = float(elements[2])

            if logFileTmin <= tmax and tmin <= logFileTmax:
                # print(logFileTmin,",",logFileTmax)
                logsFiles.append(logFilePath)

        return logsFiles

    @staticmethod
    def calc_mjd_simple(t_in):
        """ Returns the variable t_in, expressed AGILE MET seconds, converted to MJD
            Input: t_in, AGILE MET in seconds
            Output: t_mjd, AGILE MJD time
        """
        tref   = datetime.datetime(2004,1,1,0,0,0)
        t_temp = tref + datetime.timedelta(seconds=t_in)
        time2  = Time(t_temp, format='datetime')
        t_mjd  = time2.mjd
        return t_mjd

    @staticmethod
    def PlotVisibility(src_ra, src_dec, separation, tTTi, tTTf, zmax, step, twocolumn=False, show=False, histogram=False, im_fmt='png', plot=True):
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
        start_t = time()
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
        plt.rcParams.update(params)
#================== end of plotting settings =====================

        print("src_ra: ",src_ra)
        print("src_dec: ",src_dec)
        print("separation: ",separation, len(separation))
        print("tTTi: ",tTTi, len(tTTi))
        print("tTTf: ",tTTf, len(tTTf))
        print("zmax: ",zmax)
        print("step: ",step)


        ti_mjd = []
        tf_mjd = []

        time_conv_start_t = time()

        for i in np.arange(len(tTTi)):
            timjd = AGEng.calc_mjd_simple(tTTi[i])
            tfmjd = AGEng.calc_mjd_simple(tTTf[i])
            ti_mjd.append(timjd)
            tf_mjd.append(tfmjd)
        time_conv_end_t = time() - time_conv_start_t
        print("Time conversion took: ", time_conv_end_t)

        ti_mjd = np.array(ti_mjd)
        tf_mjd = np.array(tf_mjd)

        print("tf_mjd: ", tf_mjd, len(tf_mjd))
        print("ti_mjd: ", ti_mjd, len(ti_mjd))

        total_obs = (np.max(tf_mjd)-np.min(ti_mjd))//1 # in days
        meantime = (ti_mjd+tf_mjd)/2.

        deltat = tTTf - tTTi
        deltat1 = deltat[1]

        ttotal_obs = np.sum(deltat)
        ttotal_under_zmax = np.sum(tTTf[separation<zmax]-tTTi[separation<zmax])
        ttotal_above_zmax = np.sum(tTTf[separation>zmax]-tTTi[separation>zmax])
        print("Total integration time=", ttotal_obs*step, " s")
        print("Total time spent at separation < ", zmax, " deg:", ttotal_under_zmax*step, "s")
        print("Relative time spent at separation <", zmax, " deg:", ttotal_under_zmax*100./ttotal_obs, "%")
        print("Relative time spent at separation >", zmax, " deg:", ttotal_above_zmax*100./ttotal_obs, "%")
        with open("test.txt", "a") as f:
            f.write("AGILE\n")
            f.write("Total integration time={}s\n".format(ttotal_obs*step))
            f.write("Total time spent at separation < {} deg: {} s\n".format(zmax,ttotal_under_zmax*step))
            f.write("Relative time spent at separation < {} deg: {} %\n".format(zmax,ttotal_under_zmax*100./ttotal_obs))
            f.write("Relative time spent at separation > {} deg: {} %\n".format(zmax, ttotal_above_zmax*100./ttotal_obs))
        f.close()

        kk = open("times_bins_vs_separation.txt", "w")
        filesep = open('time_vs_separation_agile.txt', 'w')
        for i in np.arange(len(separation)):
            filesep.write("{} {}\n".format(meantime[i], separation[i]))
            kk.write("{} {} {}\n".format(tTTi[i], tTTf[i], separation[i]))
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
            print('Plotting figure...')
            f  = plt.figure()
            ax = f.add_subplot(111)
            ax.plot(meantime, separation, '-b')
#            ax.plot(meantime[separation < zmax], separation[separation < zmax], '-r')

            ax.set_ylim(0., zmax+5.0)
            ax.set_xlabel('MJD')
            ax.set_ylabel('off-axis angle [$^{\\circ}$]')

            print( 'Saving figure...')
            ax.set_xlim(np.min(meantime), np.max(meantime))
            if show==True:
                f.show()
            else:
                filename = 'agile_visibility_ra'+str(src_ra)+'_dec'+str(src_dec)+'_tstart'+str(np.min(tTTi))+'_tstop'+str(np.max(tTTf))+'.'+str(im_fmt)
                f.savefig(filename)
                print("Produce: ", filename)

        if histogram == True:
            print( "Plotting histogram...")
            bins  = [0, 10, 20, 30, 40, 50, 60]
            bins2 = [60, 180]
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
            labels  = [0, 10, 20, 30, 40, 50, 180]
            xlabels = [0, 10, 20, 30, 40, 50, 100]
            plt.xticks(xlabels, labels)

            fil = open('agile_histogram_visibility'+str(src_ra)+'_dec'+str(src_dec)+'_tstart'+str(np.min(tTTi))+'_tstop'+str(np.max(tTTf))+'.txt', 'w')
            for i in np.arange(len(center)):
                fil.write("{} {} \n".format(center[i], hist[i]))
            for i in np.arange(len(center2)):
                fil.write("{} {} \n".format(center2[i], hist2[i]))
            fil.close()

            print( 'Saving figure...')
            if show==True:
                f2.show()
            else:
                filename = 'agile_histogram_ra'+str(src_ra)+'_dec'+str(src_dec)+'_tstart'+str(np.min(tTTi))+'_tstop'+str(np.max(tTTf))+'.'+str(im_fmt)
                f2.savefig(filename)
                print("Produced: ",filename)

            end_t = time() - start_t

            print("Took %f seconds"%(end_t))

            return ttotal_obs, np.concatenate((hist,hist2))


if __name__ == "__main__":

    file = "/AGILE_PROC3/DATA_ASDCSTDk/INDEX/LOG.log.index"
    zmax = 60
    step = 5

    # sep, time_s, time_f, ra ,dec = AGEng.computeAGILEAngularDistanceFromSource(file, 221572734, 228830334, l=129.7, b=3.7, zmax=zmax, step=step)
    sep, time_s, time_f, ra ,dec = AGEng.computeAGILEAngularDistanceFromSource(file, 221572734, 221830334, l=129.7, b=3.7, zmax=zmax, step=step)

    AGEng.PlotVisibility(ra ,dec, sep, time_s, time_f, zmax, step, twocolumn=True, show=False, histogram=True, im_fmt='png', plot=True)
