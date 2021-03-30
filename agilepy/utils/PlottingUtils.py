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
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
from astropy.wcs import WCS
from astropy.io import fits
from astropy.visualization import simple_norm
from regions import read_ds9
import scipy.ndimage as ndimage
import scipy
import ntpath
from os.path import join
import numpy as np
from pathlib import Path
from scipy.stats import norm
from time import strftime
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.figure_factory as ff
import pandas as pd
from math import ceil
from agilepy.utils.Utils import Utils
from agilepy.core.CustomExceptions import ConfigurationsNotValidError

from agilepy.utils.Utils import Singleton


class PlottingUtils(metaclass=Singleton):

    def __init__(self, agilepyConfig, agilepyLogger):

        self.config = agilepyConfig
        self.logger = agilepyLogger

        self.outdir = Path(self.config.getConf("output", "outdir")).joinpath("plots")
        self.outdir.mkdir(parents=True, exist_ok=True)

        # self._updateRC()

    def getSupportedRegionsCatalogs(self):
        return {
            "2AGL":"$AGILE/catalogs/2AGL_2.reg",
            "3EG":"$AGILE/catalogs/3EG_1.reg",
            "1AGL":"$AGILE/catalogs/1AGL_agl-allcat.reg",
            "3FGL":"$AGILE/catalogs/3FGL/3FGL_gll_psc_v14_ell.reg",
            "4FGL":"$AGILE/catalogs/4FGL/gll_psc_v17_ell.reg"
        }

    """
        fig1   fig2
        fig3   fig4
        fig5   fig6
        ..     ..
    """
    def displaySkyMapsSingleMode(self, fitsFilepaths, smooth, saveImage, fileFormat, titles, cmap, regFiles, regFileColors, catalogRegions, catalogRegionsColor, normType):
        # self._updateRC()
        regionsFiles = self._getRegionsFiles(regFiles, catalogRegions)
        regionsColors = [*regFileColors, catalogRegionsColor]

        numberOfSubplots = len(fitsFilepaths)

        hideLast = False
        if numberOfSubplots % 2 != 0:
            numberOfSubplots += 1
            hideLast = True

        hdu = fits.open(fitsFilepaths[0])[0]
        wcs = WCS(hdu.header)

        nrows = ceil(numberOfSubplots/2)
        ncols = 2

        fig, axs = plt.subplots(nrows, ncols, subplot_kw={'projection': wcs}, figsize=(20, 20), squeeze=False)

        for idx in range(len(fitsFilepaths)):

            row, col = divmod(idx, ncols)

            hdu = fits.open(fitsFilepaths[idx])[0]

            if smooth > 0:
                data = ndimage.gaussian_filter(hdu.data, sigma=float(smooth), order=0, output=float)
            else:
                data = hdu.data
            
            norm = simple_norm(data, normType)

            im = axs[row][col].imshow(data, origin='lower', norm=norm, cmap=cmap)

            fig.colorbar(im, ax=axs[row][col],fraction=0.046, pad=0.04)

            wcs = WCS(hdu.header)
            axs[row][col] = self._configAxes(axs[row][col], titles[idx], regionsFiles, regionsColors, wcs)
            #cmap = plt.cm.CMRmap
            #cmap.set_bad(color='black')
        if hideLast:
            axs[-1][-1].remove()

        # fig.tight_layout(pad=3.0)
        #plt.subplots_adjust(bottom=-0.1)

        

        if saveImage:
            _, filename = ntpath.split(fitsFilepaths[0])
            values = filename.split("_")
            prefix = values[0]
            suffix = values[-1]
            skymaptype = suffix.split(".")[1]
            filename = self.outdir.joinpath(prefix+"_"+skymaptype+"_"+strftime("%Y%m%d-%H%M%S")).with_suffix(fileFormat)
            plt.savefig(str(filename))
            self.logger.info(self, "Produced: %s", filename)
            return str(filename)
        else:
            plt.show()
            return None

    def displaySkyMap(self, fitsFilepath, smooth, saveImage, fileFormat, title, cmap, regFiles, regFileColors, catalogRegions, catalogRegionsColor, normType):
        # self._updateRC()

        regionsFiles = self._getRegionsFiles(regFiles, catalogRegions)
        regionsColors = [*regFileColors ,catalogRegionsColor]

        hdu = fits.open(fitsFilepath)[0]
        wcs = WCS(hdu.header)

        fig, ax = plt.subplots(nrows=1, ncols=1, subplot_kw={'projection': wcs}, figsize=(12, 12))

        if smooth > 0:
            data = ndimage.gaussian_filter(hdu.data, sigma=float(smooth), order=0, output=float)
        else:
            data = hdu.data
        
        norm = simple_norm(data, normType)

        plt.imshow(data, origin='lower', norm=norm, cmap=cmap)

        ax = self._configAxes(ax, title, regionsFiles, regionsColors, wcs)

        #cmap = plt.cm.CMRmap
        #cmap.set_bad(color='black')
        plt.colorbar()

        if saveImage:
            _, filename = ntpath.split(fitsFilepath)
            filename = self.outdir.joinpath(filename+"_"+strftime("%Y%m%d-%H%M%S")).with_suffix(fileFormat)
            plt.savefig(filename)
            self.logger.info(self, "Produced: %s", filename)
            return str(filename)
        else:
            plt.show()
            return None

    def visibilityPlot(self, separations, ti_tt, tf_tt, ti_mjd, tf_mjd, src_ra, src_dec, zmax, step, saveImage, outDir, fileFormat, title):
        # self._updateRC()

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
        # self._updateRC()

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

    def _getRegionsFiles(self, regFiles, catalogRegions):

        regionsFiles = []
        if regFiles:
            for regionFile in regFiles:
                if regionFile:
                    regionFile = Utils._expandEnvVar(regionFile)
                    self.logger.info(self, "The region catalog %s will be loaded.", regionFile)

                regionsFiles.append(regionFile)

        regionsFilesDict = self.getSupportedRegionsCatalogs()
        if catalogRegions in regionsFilesDict.keys():
            catalogRegions = Utils._expandEnvVar(regionsFilesDict[catalogRegions])
            self.logger.info(self, "The region catalog %s will be loaded.", catalogRegions)

        regionsFiles.append(catalogRegions)

        return regionsFiles

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

    def _configAxes(self, ax, title, regionFiles, regionsColors, wcs):

        if title:
            ax.set_title(title, fontsize='large')

        if len(regionFiles) != len(regionsColors):
            raise ConfigurationsNotValidError(
                "lenght of regFiles does not match with length of regFileColors\n")

        # interpolation = "gaussian",
        for idx, regionFile in enumerate(regionFiles):
            if regionFile is not None:
                regions = read_ds9(regionFile)
                for region in regions:
                    pixelRegion = region.to_pixel(wcs=wcs)
                    pixelRegion.plot(ax=ax, edgecolor=regionsColors[idx])

        if "GLON" in wcs.wcs.ctype[0]:
            ax.set_xlabel('Galactic Longitude' + " (" + str(wcs.wcs.cunit[0]) + ")")
            ax.set_ylabel('Galactic Latitude' + " (" + str(wcs.wcs.cunit[1]) + ")")

        elif "RA" in wcs.wcs.ctype[0]:
            ax.set_xlabel('Right ascension' + " (" + str(wcs.wcs.cunit[0]) + ")")
            ax.set_ylabel('Declination' + " (" + str(wcs.wcs.cunit[1]) + ")")

        else:
            self.logger.warning(self, f"wcs type does not contain GLAT or RA but {wcs.wcs.ctype[0]}")

        ax.grid(b=True, color='white', ls='solid')

        return ax

    def plotGenericColumn(self, filename, column, um=None, saveImage=False):

        data = pd.read_csv(filename, header=0, sep=" ")
        data["tm"] = data[["time_start_mjd", "time_end_mjd"]].mean(axis=1)
        data = data.sort_values(by="tm")

        fig = go.Figure()

        fig.add_traces(go.Scatter(x=data["tm"], y=data[column]))

        fig.update_xaxes(showline=True, linecolor="black", title="Time(MJD)")

        fig.update_yaxes(showline=True, linecolor="black",
                         title=um)
        fig.update_layout(xaxis=dict(tickformat="g"))

        if saveImage:
            filePath = join(self.outdir, column+".png")
            self.logger.info(self, column+" plot at: %s", filePath)
            fig.write_image(filePath)
            return filePath
        else:
            fig.show()
            return None
        



    def plotLc(self, filename, lineValue, lineError, saveImage, fermiLC):
        # reading and setting dataframe
        data = pd.read_csv(filename, header=0, sep=" ")
        data["flux"] = data["flux"] * 10 ** 8
        data["flux_err"] = data["flux_err"] * 10 ** 8
        data["flux_ul"] = data["flux_ul"] * 10 ** 8
        data["gal"] = data["gal"] * 10 ** 8
        data["tm"] = data[["time_start_mjd", "time_end_mjd"]].mean(axis=1)
        data["x_plus"] = data["time_end_mjd"] - data["tm"]
        data["x_minus"] = data["tm"] - data["time_start_mjd"]
        sel1 = data.loc[data["sqrt(ts)"] >= 3]
        sel2 = data.loc[data["sqrt(ts)"] < 3]
        
        #Plotting
        fig = go.Figure()
        fig.add_traces(go.Scatter(x=sel1["tm"], y=sel1["flux"],
                                  error_x=dict(type="data", symmetric=False, array=sel1["x_plus"],
                                               arrayminus=sel1["x_minus"]),
                                  error_y=dict(type="data", symmetric=True, array=sel1["flux_err"]), mode="markers",
                                  customdata = np.stack((sel1["time_start_mjd"],
                                             sel1["time_end_mjd"]), axis=-1),
                                  hovertemplate="tstart: %{customdata[0]:.4f} - tend:%{customdata[1]:.4f}, flux: %{y:.2f} +/- %{error_y.array:.2f}", name="sqrts >=3"))
        fig.add_traces(go.Scatter(x=sel2["tm"], y=sel2["flux_ul"],
                                  error_x=dict(type="data", symmetric=False, array=sel2["x_plus"],
                                               arrayminus=sel2["x_minus"]), mode='markers',
                                  hovertemplate="tstart: %{customdata[0]:.4f}, tend:%{customdata[1]:.4f}, flux_ul: %{y:.2f}",
                                  customdata=np.stack((sel2["time_start_mjd"],
                                                      sel2["time_end_mjd"]), axis=-1),
                                  marker_symbol="triangle-down", marker_size=10, name="sqrts < 3"))

        if fermiLC is not None:
            fermiData = pd.read_csv(fermiLC, header=0, sep=" ")
            fermiData["tm"] = fermiData[["time_start_mjd", "time_end_mjd"]].mean(axis=1)
            fermiData["x_plus"] = fermiData["time_end_mjd"] - fermiData["tm"]
            fermiData["x_minus"] = fermiData["tm"] - fermiData["time_start_mjd"]
            fermiData["sqrt(ts)"] = fermiData["ts"].apply(np.sqrt)
            fermiData["flux"] = fermiData["flux"] *10 ** 8
            fermiData["flux_err"] = fermiData["flux_err"] * 10 ** 8
            fermiData["flux_ul95"] = fermiData["flux_ul95"] * 10 ** 8
            fermiDatasel1 = fermiData.loc[fermiData["sqrt(ts)"] >= 3]
            fermiDatasel2 = fermiData.loc[fermiData["sqrt(ts)"] < 3]

            fig.add_traces(go.Scatter(x=fermiDatasel1["tm"], y=fermiDatasel1["flux"],
                                      error_x=dict(type="data", symmetric=False, array=fermiDatasel1["x_plus"],
                                                   arrayminus=fermiDatasel1["x_minus"]),
                                      error_y=dict(type="data", symmetric=True, array=fermiDatasel1["flux_err"]), mode="markers",
                                      customdata=np.stack((fermiDatasel1["time_start_mjd"],
                                                           fermiDatasel1["time_end_mjd"]), axis=-1),
                                      hovertemplate="FERMI tstart: %{customdata[0]:.4f} - tend:%{customdata[1]:.4f}, flux: %{y:.2f} +/- %{error_y.array:.2f}", name="FERMI sqrts >=3"))
            
            fig.add_traces(go.Scatter(x=fermiDatasel2["tm"], y=fermiDatasel2["flux_ul95"],
                                      error_x=dict(type="data", symmetric=False, array=fermiDatasel2["x_plus"],
                                                   arrayminus=fermiDatasel2["x_minus"]), mode='markers',
                                      hovertemplate="FERMI tstart: %{customdata[0]:.4f}, tend:%{customdata[1]:.4f}, flux_ul: %{y:.2f}",
                                      customdata=np.stack((fermiDatasel2["time_start_mjd"],
                                                           fermiDatasel2["time_end_mjd"]), axis=-1),
                                      marker_symbol="triangle-down", marker_size=10, name="FERMI sqrts < 3"))

        if lineValue is not None and lineError is not None:
            fig.add_traces(go.Scatter(x=data["tm"], y=[lineValue] * len(data["tm"]), error_y= dict(type="constant", value=lineError), line=dict(dash="dash"), name="line1"))


        fig.update_xaxes(showline=True, linecolor="black", title="Time(MJD)")
        fig.update_yaxes(showline=True, linecolor="black", title=r"$10^{-8} ph cm^{-2} s^{-1}$")
        fig.update_layout(legend=dict(font=dict(size=20)), xaxis=dict(tickformat="g"))
        
        if saveImage:
            filePath = join(self.outdir, "LightCurve.png")
            self.logger.info(self, "Light curve plot at: %s", filePath)
            fig.write_image(filePath)
            return filePath
        else:
            fig.show()
            return None

    def plotSimpleLc(self, filename, lineValue, lineError, saveImage=False):
        # reading and setting dataframe
        data = pd.read_csv(filename, index_col=False, header=0, names=["tmin_tt","tmax_tt","exp","cts"], sep=" ")

        tmean = data[["tmin_tt", "tmax_tt"]].mean(axis=1)

        #Plotting



        fig = make_subplots(rows=2, cols=2, shared_xaxes=True)

        fig.add_trace(go.Scatter(x=tmean, y=data["cts"], name="counts", mode="markers"), row=1, col=1)

        fig.add_trace(go.Scatter(x=tmean, y=data["exp"], name="exposure", mode="markers"), row=2, col=1)

        #fig.add_trace(go.Histogram(y=data["exp"], histnorm='probability'), row=2, col=2)

        #fig.add_trace(ff.create_distplot([data["exp"]], ["label"], curve_type="normal"), row=2, col=2)
        
        counts, bins = np.histogram(data["exp"], bins=40)

        bins = 0.5 * (bins[:-1] + bins[1:])

        mu, sigma = scipy.stats.norm.fit(data["exp"])
        # print(mu, sigma)
        best_fit_line = scipy.stats.norm.pdf(bins, mu, sigma) * 10**9

        fig.add_trace(go.Bar(x=bins, y=counts), row=2, col=2)

        fig.add_trace(go.Scatter(x=bins, y=best_fit_line), row=2, col=2)

        fig.update_xaxes(showline=True, linecolor="black", title="Time(tt)")
        fig.update_yaxes(showline=True, linecolor="black", title="Counts", row=1, col=1)
        fig.update_yaxes(showline=True, linecolor="black", title="Exp", row=2, col=1)

        fig.update_layout(legend=dict(font=dict(size=20)), xaxis=dict(tickformat="g"), height=800, width=1600, xaxis_showticklabels=True)

        if saveImage:
            outfilename = f"light_curve_{data['tmin_tt'].iloc[0]}_{data['tmax_tt'].iloc[-1]}.png"
            filePath = join(self.outdir, outfilename)
            self.logger.info(self, "Light curve plot at: %s", filePath)
            fig.write_image(filePath)
            return filePath
        else:
            fig.show()
            return None
