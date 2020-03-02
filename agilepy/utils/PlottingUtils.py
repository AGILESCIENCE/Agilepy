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

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.


#mpl.use("Agg")
import matplotlib.pyplot as plt
from astropy.wcs import WCS
from astropy.io import fits
from regions import read_ds9
import scipy.ndimage as ndimage
import ntpath
from os.path import join
import numpy as np
from pathlib import Path
from time import strftime

from agilepy.utils.Utils import Singleton


class PlottingUtils(metaclass=Singleton):

    def __init__(self, agilepyConfig, agilepyLogger):

        self.config = agilepyConfig
        self.logger = agilepyLogger

        self.outdir = Path(self.config.getConf("output", "outdir")).joinpath("plots")
        self.outdir.mkdir(parents=True, exist_ok=True)

        self._updateRC()


    def displaySkyMapsSingleMode(self, fitsFilepaths, smooth, sigma, saveImage, fileFormat, titles, cmap, regFilePath):
        self._updateRC()

        if regFilePath:
            regFilePath = self.config._expandEnvVar(regFilePath)

        numberOfSubplots = len(fitsFilepaths)

        hideLast = False
        if numberOfSubplots % 2 != 0:
            numberOfSubplots += 1
            hideLast = True

        hdu = fits.open(fitsFilepaths[0])[0]
        wcs = WCS(hdu.header)
        fig, axs = plt.subplots(int(numberOfSubplots/2),int(numberOfSubplots/2), subplot_kw={'projection': wcs})

        for idx, fitsImage in enumerate(fitsFilepaths):

            row,col = self._getCell(idx, int(numberOfSubplots/2))

            hdu = fits.open(fitsFilepaths[idx])[0]
            wcs = WCS(hdu.header)

            if smooth:
                data = ndimage.gaussian_filter(hdu.data, sigma=float(sigma), order=0, output=float)
            else:
                data = hdu.data

            im = axs[row][col].imshow(data, origin='lower', norm=None, cmap=cmap)

            fig.colorbar(im, ax=axs[row][col])

            axs[row][col] = self._configAxes(axs[row][col], titles[idx], regFilePath, wcs)
            #cmap = plt.cm.CMRmap
            #cmap.set_bad(color='black')

        if hideLast:
            lastR = int(numberOfSubplots/2 - 1)
            lastC = lastR
            axs[lastR][lastC].remove()

        if saveImage:
            _, filename = ntpath.split(fitsFilepaths[0])
            values = filename.split("_")
            prefix = values[0]
            suffix = values[-1]
            skymaptype = suffix.split(".")[1]
            filename = self.outdir.joinpath(prefix+"_"+skymaptype+"_"+strftime("%Y%m%d-%H%M%S")).with_suffix(fileFormat)
            plt.savefig(str(filename))
            self.logger.info(self, "Produced: %s", filename)
            return filename
        else:
            plt.show()
            return None

    def displaySkyMap(self, fitsFilepath, smooth, sigma, saveImage, fileFormat, title, cmap, regFilePath):
        self._updateRC()

        if regFilePath:
            regFilePath = self.config._expandEnvVar(regFilePath)


        hdu = fits.open(fitsFilepath)[0]
        wcs = WCS(hdu.header)

        fig, ax = plt.subplots(nrows=1, ncols=1, subplot_kw={'projection': wcs})

        if smooth:
            data = ndimage.gaussian_filter(hdu.data, sigma=float(sigma), order=0, output=float)
        else:
            data = hdu.data

        plt.imshow(data, origin='lower', norm=None, cmap=cmap)

        ax = self._configAxes(ax, title, regFilePath, wcs)

        #cmap = plt.cm.CMRmap
        #cmap.set_bad(color='black')
        plt.colorbar()

        if saveImage:
            _, filename = ntpath.split(fitsFilepath)
            filename = self.outdir.joinpath(filename+"_"+strftime("%Y%m%d-%H%M%S")).with_suffix(fileFormat)
            plt.savefig(filename)
            self.logger.info(self, "Produced: %s", filename)
            print("filename: ",filename)
            return filename
        else:
            plt.show()
            return None

    def visibilityPlot(self, separations, ti_tt, tf_tt, ti_mjd, tf_mjd, src_ra, src_dec, zmax, step, saveImage, outDir, fileFormat, title):
        self._updateRC()

        """visibilityPlot makes a plot of the zenith distance of a given source
           (src_ra and src_dec selected in the agilecheck parameters).
        """

        if len(separations) == 0:
            self.logger.warning(self, "No data to plot")
            return None

        self.logger.info(self, "Loading visibility plot...")
        # total_obs = (np.max(tf_mjd)-np.min(ti_mjd))//1 # in days

        meantimes = (ti_mjd+tf_mjd)/2. # for plot

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
        #            tstart       = Time(t_start_temp, fileFormat='datetime')
        #            tstop        = Time(t_stop_temp, fileFormat='datetime')
        #            tstart_data  = tstart.mjd
        #            tstop_data   = tstop.mjd
        #            t_agilestart.append(tstart_data)
        #            t_agilestop.append(tstop_data)

        #        t_agilei_mjd = np.asfarray(t_agilestart)
        #        t_agilef_mjd = np.asfarray(t_agilestop)

        #        for i in np.arange(len(t_agilei_mjd)):
        #            ax.fill_between([t_agilei_mjd[i], t_agilef_mjd[i]], 0, 200, color='grey', alpha=0.5)


        f  = plt.figure()
        ax = f.add_subplot(111)
        ax.plot(meantimes, separations, '-b')
#            ax.plot(meantimes[separations < zmax], separations[separations < zmax], '-r')

        ax.set_title(title, fontsize='large')
        ax.set_ylim(0., zmax+5.0)
        ax.set_xlabel('MJD')
        ax.set_ylabel('off-axis angle [$^{\\circ}$]')
        ax.set_xlim(np.min(meantimes), np.max(meantimes))

        if saveImage:
            filePath = join(outDir,'agile_visibility_ra'+str(src_ra)+'_dec'+str(src_dec)+'_tstart'+str(np.min(ti_tt))+'_tstop'+str(np.max(tf_tt))+'_zmax'+str(zmax)+'step'+str(step)+'.'+str(fileFormat))
            self.logger.info(self, "Visibility plot at: %s", filePath)
            f.savefig(filePath)
        else:
            plt.show()

        return filePath

    def visibilityHisto(self, separations, ti_tt, tf_tt, src_ra, src_dec, zmax, step, saveImage, outDir, fileFormat, title):
        self._updateRC()

        if len(separations) == 0:
            self.logger.warning(self, "No data to plot")
            return None

        deltat = tf_tt - ti_tt
        ttotal_obs = np.sum(deltat)
        deltat1 = deltat[0] # for histogram always 0.1!!!

        bins  = [0, 10, 20, 30, 40, 50, 60, 70, 80]
        bins2 = [80, 180]
        separations = [s.value for s in separations]
        hist, bins = np.histogram(separations, bins=bins, density=False)
        hist2, bins2 = np.histogram(separations, bins=bins2, density=False)

        print(hist)

        width = 1. * (bins[1] - bins[0])
        center = (bins[:-1] + bins[1:]) / 2
        width2 = 1. * (bins2[1] - bins2[0])
        center2 = (bins2[:-1] + bins2[1:]) / 2

        f2  = plt.figure()
        ax2 = f2.add_subplot(111)
        ax2.set_title(title, fontsize='large')
        ax2 = f2.add_subplot(111)
        ax2.bar(center, hist*deltat1/ttotal_obs*100., align='center', color='w', edgecolor='b', width=width)
        ax2.bar(center2, hist2*deltat1/ttotal_obs*100., align='center', color='w', edgecolor='b', width=width2)

        ax2.set_xlim(0., 100.)
        ax2.set_ylim(0., 100.)
        ax2.set_ylabel('\\% of time spent')
        ax2.set_xlabel('off-axis angle $[^\\circ]$')
        labels  = [0, 10, 20, 30, 40, 50, 60, 70, 80, 180]
        xlabels = [0, 10, 20, 30, 40, 50, 60, 70, 80, 180]
        plt.xticks(xlabels, labels)

        """
        fil = open('agile_histogram_visibility'+str(src_ra)+'_dec'+str(src_dec)+'_tstart'+str(np.min(ti_tt))+'_tstop'+str(np.max(tf_tt))+'.txt', 'w')
        for i in np.arange(len(center)):
            fil.write("{} {} \n".format(center[i], hist[i]))
        for i in np.arange(len(center2)):
            fil.write("{} {} \n".format(center2[i], hist2[i]))
        fil.close()
        """
        if saveImage:
            filePath = join(outDir,'agile_histogram_ra'+str(src_ra)+'_dec'+str(src_dec)+'_tstart'+str(np.min(ti_tt))+'_tstop'+str(np.max(tf_tt))+'_zmax'+str(zmax)+'step'+str(step)+'.'+str(fileFormat))
            f2.savefig(filePath)
            self.logger.info(self, "Visibility histogram at: %s", filePath)
        else:
            f2.show()

        return filePath



    def _updateRC(self):
        twocolumns = self.config.getConf("plotting","twocolumns")

        """
        twocolumn: boolean, True or False (default). If two column=True, the
        plot is adjusted to the size of a two column journal publication.
        """
        if twocolumns:
            fig_width_pt = 255.76535
            fontsize     = 10
            self.logger.info(self, "Plot configuration: 'two column journal publication'. fig_width_pt: %f fontsize:%f", fig_width_pt, fontsize)
        else:
            fig_width_pt = 426.79134
            fontsize     = 11
            self.logger.info(self, "Plot configuration: 'standard'. fig_width_pt: %f fontsize:%f", fig_width_pt, fontsize)

        inches_per_pt = 1.0/72.27               # Convert pt to inch
        golden_mean = (np.sqrt(5)+1.0)/2.0      # Aesthetic ratio
        fig_width = fig_width_pt*inches_per_pt  # width in inches
        fig_height = fig_width/golden_mean      # height in inches

        fig_size =  [fig_width,fig_height]

        params = {  'backend': 'pdf',
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
                    'font.family': 'DejaVu Sans',
                    'font.serif': ['Bitstream Vera Serif']}

        plt.rcParams.update(params)

    def _configAxes(self, ax, title, regionFile, wcs):

        if title:
            ax.set_title(title, fontsize='large')


        # interpolation = "gaussian",
        if regionFile is not None:
            regions = read_ds9(regionFile)
            for region in regions:
                pixelRegion = region.to_pixel(wcs=wcs)
                pixelRegion.plot(ax=ax, color="green")

        if "GLON" in wcs.wcs.ctype[0]:
            ax.set_xlabel('Galactic Longitude')
            ax.set_ylabel('Galactic Latitude')

        elif "RA" in wcs.wcs.ctype[0]:
            ax.set_xlabel('Right ascension')
            ax.set_ylabel('Declination')

        else:
            self.logger.warning(self, f"wcs type does not contain GLAT or RA but {wcs.wcs.ctype[0]}")

        ax.grid(b=True, color='white', ls='solid')

        return ax

    def _getCell(self, idx, numberOfSubplots):
        # print(f"{idx} / {numberOfSubplots}")
        q, r = divmod(idx, numberOfSubplots)
        row = q
        col = r
        return row, col
