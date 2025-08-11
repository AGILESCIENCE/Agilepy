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

#import matplotlib as mpl
#mpl.use("Agg")

import scipy
import ntpath
import datetime
import numpy as np
import pandas as pd
from math import ceil
from pathlib import Path
from os.path import join
from time import strftime
from astropy.io import fits
from astropy.wcs import WCS
from regions import Regions
from scipy.stats import norm
import matplotlib.pyplot as plt
import scipy.ndimage as ndimage
import plotly.graph_objects as go
import matplotlib.dates as mdates
import plotly.figure_factory as ff
from agilepy.utils.Utils import Utils
from agilepy.utils.Utils import Singleton
from plotly.subplots import make_subplots
from astropy.visualization import simple_norm
from agilepy.utils.AstroUtils import AstroUtils
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
from agilepy.core.CustomExceptions import ConfigurationsNotValidError


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
            self.logger.info( "Produced: %s", filename)
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
            self.logger.info( "Produced: %s", filename)
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
            self.logger.warning( "No data to plot")
            return None

        self.logger.info( "Loading visibility plot...")
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
            self.logger.info( "Visibility plot at: %s", filePath)
            f.savefig(filePath)
        else:
            plt.show()

        return filePath

    def visibilityHisto(self, separations, ti_tt, tf_tt, src_ra, src_dec, zmax, step, saveImage, outDir, fileFormat, title):
        # self._updateRC()

        if len(separations) == 0:
            self.logger.warning( "No data to plot")
            return None

        deltat = tf_tt - ti_tt
        ttotal_obs = np.sum(deltat)
        deltat1 = deltat[0] # for histogram always 0.1!!!

        bins  = [0, 10, 20, 30, 40, 50, 60, 70, 80]
        bins2 = [80, 180]
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
            self.logger.info( "Visibility histogram at: %s", filePath)
        else:
            f2.show()

        return filePath

    def _getRegionsFiles(self, regFiles, catalogRegions):

        regionsFiles = []
        if regFiles:
            for regionFile in regFiles:
                if regionFile:
                    regionFile = Utils._expandEnvVar(regionFile)
                    self.logger.info( "The region catalog %s will be loaded.", regionFile)

                regionsFiles.append(regionFile)

        regionsFilesDict = self.getSupportedRegionsCatalogs()
        if catalogRegions in regionsFilesDict.keys():
            catalogRegions = Utils._expandEnvVar(regionsFilesDict[catalogRegions])
            self.logger.info( "The region catalog %s will be loaded.", catalogRegions)

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
            self.logger.info( "Plot configuration: 'two column journal publication'. fig_width_pt: %f fontsize:%f", fig_width_pt, fontsize)
        else:
            fig_width_pt = 426.79134
            fontsize     = 11
            self.logger.info( "Plot configuration: 'standard'. fig_width_pt: %f fontsize:%f", fig_width_pt, fontsize)

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
                regions = Regions.read(regionFile)
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
            self.logger.warning( f"wcs type does not contain GLAT or RA but {wcs.wcs.ctype[0]}")

        ax.grid(b=True, color='white', ls='solid')

        return ax

    """def plotGenericColumn(self, filename, column, um=None, saveImage=False):

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
            self.logger.info( column+" plot at: %s", filePath)
            fig.write_image(filePath)
            return filePath
        else:
            fig.show()
            return None"""

    def plotGenericColumns(self, filename, columns, um=None, saveImage=False):

        if len(um) != len(columns):
            raise ConfigurationsNotValidError(
                "lenght of um does not match with length of columns\n")

        data = pd.read_csv(filename, header=0, sep=" ")
        data["tm"] = data[["time_start_mjd", "time_end_mjd"]].mean(axis=1)
        data["x_plus"] = data["time_end_mjd"] - data["tm"]
        data["x_minus"] = data["tm"] - data["time_start_mjd"]
        data = data.sort_values(by="tm")

        nrows = len(columns) +1
        
        fig = make_subplots(rows=nrows, cols=1, shared_xaxes=True)

        trace1, trace2 = self.plotLc(filename, None, None, False, None, True)

        fig.add_trace(trace1, row=1, col=1)
        fig.add_trace(trace2, row=1, col=1)

        fig.update_yaxes(showline=True, linecolor="black",
                         title="cm^2 s sr", row=1, col=1)
        fig.update_xaxes(showline=True, linecolor="black",
                         title="Time(MJD)", tickformat="g", row=1, col=1, showticklabels=True)

        for i in range(len(columns)):
            
            fig.add_trace(go.Scatter(
                x=data["tm"], y=data[columns[i]], name=columns[i], error_x=dict(type="data", symmetric=False, array=data["x_plus"],
                                         arrayminus=data["x_minus"]), mode='markers'), row=i+2, col=1)
            
            fig.update_yaxes(showline=True, linecolor="black",
                             title=um[i], row=i+2, col=1)
            fig.update_xaxes(showline=True, linecolor="black",
                             title="Time(MJD)", tickformat="g", row=i+2, col=1, showticklabels=True)

        fig.update_layout(height=500+(len(columns)*500))
        

        if saveImage:
            filePath = join(self.outdir, "plot.png")
            self.logger.info("plot at: %s", filePath)
            fig.write_image(filePath)
            return filePath
        else:
            fig.show()
            return None

    def plotLc(self, filename, lineValue, lineError, saveImage, fermiLC, trace=False):
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
        trace1 = go.Scatter(x=sel1["tm"], y=sel1["flux"],
                            error_x=dict(type="data", symmetric=False, array=sel1["x_plus"],
                                         arrayminus=sel1["x_minus"]),
                            error_y=dict(type="data", symmetric=True, array=sel1["flux_err"]), mode="markers",
                            customdata=np.stack((sel1["time_start_mjd"],
                                                 sel1["time_end_mjd"], sel1["sqrt(ts)"]), axis=-1),
                            hovertemplate="tstart: %{customdata[0]:.4f} - tend:%{customdata[1]:.4f}, flux: %{y:.2f} +/- %{error_y.array:.2f}, sqrts: %{customdata[2]:.4f}", name="flux")
        fig.add_traces(trace1)

        trace2 = go.Scatter(x=sel2["tm"], y=sel2["flux_ul"],
                            error_x=dict(type="data", symmetric=False, array=sel2["x_plus"],
                                         arrayminus=sel2["x_minus"]), mode='markers',
                            hovertemplate="tstart: %{customdata[0]:.4f}, tend:%{customdata[1]:.4f}, flux_ul: %{y:.2f}, sqrts: %{customdata[2]:.4f}",
                            customdata=np.stack((sel2["time_start_mjd"],
                                                 sel2["time_end_mjd"], sel2["sqrt(ts)"]), axis=-1),
                            marker_symbol="triangle-down", marker_size=10, name="flux_ul")
        
        fig.add_traces(trace2)

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
        fig.update_layout(legend=dict(font=dict(
            size=17), orientation="h", yanchor="bottom", y=1.02, xanchor="left"), xaxis=dict(tickformat="g"))
        
        if saveImage:
            filePath = join(self.outdir, "LightCurve.png")
            self.logger.info( "Light curve plot at: %s", filePath)
            fig.write_image(filePath)
            return filePath

        elif trace: #trace==true is used by displaygenericolumns for getting the curves on its subplot
            return trace1, trace2
        else:
            fig.show()
            return None

    def plotSimpleLc(self, filename, lineValue, lineError, saveImage=False):
        # reading and setting dataframe
        data = pd.read_csv(filename, index_col=False, header=0, names=["tmin_tt","tmax_tt","exp","cts"], sep=" ")

        data["tm"] = data[["tmin_tt", "tmax_tt"]].mean(axis=1)

        data["x_plus"] = data["tmax_tt"] - data["tm"]
        data["x_minus"] = data["tm"] - data["tmin_tt"]

        #Plotting



        fig = make_subplots(rows=2, cols=1, shared_xaxes=True)

        fig.add_trace(go.Scatter(x=data["tm"], error_x=dict(type="data", symmetric=False, array=data["x_plus"],
                                                   arrayminus=data["x_minus"]), y=data["cts"],  error_y=dict(type="data", symmetric=True, array=data["cts"]**(1/2)), name="counts", mode="markers"), row=1, col=1)

        fig.add_trace(go.Scatter(x=data["tm"], error_x=dict(type="data", symmetric=False, array=data["x_plus"],
                                                   arrayminus=data["x_minus"]), y=data["exp"], name="exposure", mode="markers"), row=2, col=1)

        fig.update_xaxes(showline=True, linecolor="black", title="Time(tt)")
        fig.update_yaxes(showline=True, linecolor="black", title="Counts", row=1, col=1)
        fig.update_yaxes(showline=True, linecolor="black", title="Exp", row=2, col=1)

        fig.update_layout(legend=dict(font=dict(size=20)), xaxis1=dict(tickformat="f"), xaxis2=dict(tickformat="f"), height=800, width=1000, xaxis_showticklabels=True)

        if saveImage:
            outfilename = f"light_curve_{data['tmin_tt'].iloc[0]}_{data['tmax_tt'].iloc[-1]}.png"
            filePath = join(self.outdir, outfilename)
            self.logger.info( "Light curve plot at: %s", filePath)
            fig.write_image(filePath)
            return filePath
        else:
            fig.show()
            return None

    def plotDataAvailability(self, qFilePath, indexFilePath, saveImage=False):

        queryDatesDF = pd.read_csv(qFilePath, header=None, sep=" ", names=["tmin","tmax"], parse_dates=["tmin","tmax"])
        
       
        # df = pd.read_csv( "/agilepy/testing/unittesting/utils/data/EVT.index", header=None, sep=" ", names=["name","tmin", "tmax", "type"])
        indexDatesDF = pd.read_csv(indexFilePath, header=None, sep=" ", names=["name","tmin", "tmax", "type"])

        dateformat = "%Y-%m-%d"

        indexDatesDF["tmin"] = AstroUtils.time_agile_seconds_to_fits(indexDatesDF["tmin"])
        indexDatesDF["tmax"] = AstroUtils.time_agile_seconds_to_fits(indexDatesDF["tmax"])

        indexDatesDF["tmin"] = [
                datetime.datetime.strptime(
                        tmin, "%Y-%m-%dT%H:%M:%S.%f").strftime(dateformat) for tmin in indexDatesDF["tmin"]]
        
        indexDatesDF["tmax"] = [
                datetime.datetime.strptime(
                        tmax, "%Y-%m-%dT%H:%M:%S.%f").strftime(dateformat) for tmax in indexDatesDF["tmax"]]
        

        fig, ax = plt.subplots(1, 1)
        #ax2 = ax.twinx()

        for index, slot in indexDatesDF.iterrows():  
            daterange = pd.date_range(start=slot["tmin"], end=slot["tmax"], freq="D" )
            ax.plot(daterange,[0.5 for _ in range(len(daterange))], color="green", )

        for index, slot in queryDatesDF.iterrows():  
            daterange = pd.date_range(start=slot["tmin"], end=slot["tmax"], freq="D")
            #ax.plot([7 for _ in range(len(daterange))],daterange, color="green", )
            
            ax.fill_between(daterange, 0, 1, 
                            where = np.ones(shape=len(daterange)), 
                            color='green', 
                            alpha=0.5, 
                            transform=ax.get_xaxis_transform(),
                            edgecolor=None
            )
            
            

            #ax.bar(slot["tmin"], 0.5, width=slot["tmax"]-slot["tmin"])
        
        fig.autofmt_xdate(rotation=45)
        
        if saveImage:
            filePath = join(self.outdir, "data_availability.png")
            self.logger.info(f"Plot at: {filePath}")
            fig.savefig(filePath)
            return filePath
        else:
            fig.show()
            return None
        
        
    def plotBayesianBlocks(self, data, datamode, plotTDelta=True, plotYErr=True, edgePoints=True, dataCells=True, meanBlocks=True, sumBlocks=False, plotRate=False, saveImage=False):
        """
        Plot the results of the Bayesian Blocks analysis, including the light curve, detected blocks, and optionally the mean value of each block.
        
        Parameters:
        -----------
        data : dict
            Dictionary with input (raw) and output (processed by Bayesian Blocks) data to plot.
        datamode : int
            Unbinned data=1, binned data=2.
        plotTDelta, plotYErr : bool
            If True, include error bars based on time resolution (dt) and Poisson uncertainties in the plot.
        edgePoints : bool
            If True, plots the positions of the edge points between blocks.
        dataCells : bool
            If True, plots the positions of data cells or segments identified by the algorithm. 
        meanBlocks : bool
            If True, plots the mean value within each identified block.
        sumBlocks : bool
            If True, plots the sum within each identified block.
        plotRate : bool
            if True, add a second plot with the rate.
        saveImage : bool
            If True, save a copy of the plot.
        """
        
        data_in = data["in"]
        data_out= data["out"]
        
        # Error bars
        if plotTDelta:
            try:
                terr = data_in['t_delta'] / 2.0
            except Exception:
                terr = np.full_like(data_in['x'], data_in['dt'] / 2.0)
        else:
            terr = np.zeros_like(data_in['x'])
        
        
        # Sanity Check
        if isinstance(data_in['sigma'], int) and plotYErr:
            self.logger.warning(f"Incoherent options: useerror=False and then plotYErr=True. Forcing plotYErr=False")
            plotYErr = False
        
        if plotYErr:
            yerr = data_in['sigma'] # np.sqrt(self.data_in['x'])
        else:
            yerr = np.zeros_like(data_in['x'])
        
        # Datamode
        if datamode==1:
            data_cells = data_in['t']
        elif datamode==2:
            data_cells = data_in['data_cells']
        else:
            raise ValueError(f"Datamode {datamode} not recognised, run selectEvents first.")
        
        #Plotting
        fig = make_subplots(
            rows=2 if plotRate else 1,
            cols=1,
            shared_xaxes=True,
            vertical_spacing=0.1,
            subplot_titles=["Light Curve", "Rate Vector"] if plotRate else ["Light Curve"]
        )

        # Plot vertical lines for edge points
        shape_ep = []
        if edgePoints:
            for edge_point in data_out['edge_points']:
                sh = fig.add_shape(
                    type='line',
                    x0=edge_point, x1=edge_point,
                    y0=0, y1=max(data_in['x'] + yerr),
                    line=dict(color="green", dash='dash', width=1.5),
                    name='Edge blocks',  # note: shapes don't appear in legend
                    row=1, col=1,
                )
                shape_ep.append(sh)
            fig.add_trace(go.Scatter(x=[None],y=[None],
                                     mode='lines',line=dict(color="green", dash='dash', width=1.5),
                                     name='Edge blocks',
                                     ),
                                     row=1, col=1
                          ) # For legend only
        
        # Plot the data cells if specified
        shape_dc = []
        if dataCells:
            for data_cell in data_cells:
                sh = fig.add_shape(
                    type='line',
                    x0=data_cell, x1=data_cell,
                    y0=0, y1=max(data_in['x'] + yerr),
                    line=dict(color='gray', dash='dash', width=0.5),
                    name='Data cells', row=1, col=1,
                )
                shape_dc.append(sh)
            fig.add_trace(go.Scatter(x=[None],y=[None],
                                     mode='lines',line=dict(color='gray', dash='dash', width=0.5),
                                     name='Data cells',
                                     ),
                          row=1, col=1
                          ) # For legend only
        
        # Plot the light curve with error bars
        trace1 = go.Scatter(
            x=data_in['t'],
            y=data_in['x'],
            error_x=dict(type='data', array=terr),
            error_y=dict(type='data', array=yerr),
            mode='markers',
            name='Data',
            marker=dict(size=6, color='blue'),
            # customdata=np.stack((data_in["time_start_mjd"], data_in["time_end_mjd"], data_in["sqrt(ts)"]), axis=-1),
            # hovertemplate="tstart: %{customdata[0]:.4f} - tend:%{customdata[1]:.4f}, flux: %{y:.2f} +/- %{error_y.array:.2f}, sqrts: %{customdata[2]:.4f}",
        )
        fig.add_trace(trace1, row=1, col=1)

        
        
        # Plot the mean values of the blocks if specified
        if meanBlocks:
            means = []
            i_edge = 0
            for t in data_cells:
                if i_edge < len(data_out['edge_points']) and t >= data_out['edge_points'][i_edge]:
                    i_edge += 1
                means.append(data_out['mean_blocks'][i_edge])
            
            trace2 = go.Scatter(
                x=data_cells,
                y=means,
                mode='lines',
                line_shape='hv',
                name='Blocks Mean',
                line=dict(color='purple'),
            )
            fig.add_trace(trace2, row=1, col=1)
            
        # Plot block sums as a step line
        if sumBlocks:
            sumb = []
            i_edge = 0
            for t in data_cells:
                if i_edge < len(data_out['edge_points']) and t >= data_out['edge_points'][i_edge]:
                    i_edge += 1
                sumb.append(data_out['sum_blocks'][i_edge])

            trace3 = go.Scatter(
                x=data_cells,
                y=sumb,
                mode='lines',
                line_shape='hv',
                name='Blocks Sum',
                line=dict(color='red')
            )
            fig.add_trace(trace3, row=1, col=1)
            
            
        # Plot rate in a second Plot if Required
        if plotRate:
            rates = []
            rateblocks = []
            i_edge = 0
            rate_key = 'blockrate2' if data_in['datamode'] == 2 else 'blockrate'

            for t in data_cells:
                if i_edge < len(data_out['edge_points']) and t >= data_out['edge_points'][i_edge]:
                    i_edge += 1
                
                event_rate = data_out['eventrate'][i_edge]
                block_rate = data_out[rate_key][i_edge]

                rates.append(event_rate if event_rate != np.inf else 0)
                rateblocks.append(block_rate if block_rate != np.inf else 0)
            
            # --- Add edge points and data cells as vertical lines in subplot 2 ---
            ymax_rate = max(rateblocks)
            # --- Add step plot for block rate ---
            trace4 = go.Scatter(x=data_cells,
                                y=rateblocks,
                                mode='lines',
                                line=dict(shape='hv', color='blue'),
                                name=rate_key
                                )
            fig.add_trace(trace4, row=2, col=1)


            if edgePoints:
                for x in data_out['edge_points']:
                    fig.add_shape(
                        type='line',
                        x0=x, x1=x,
                        y0=0, y1=ymax_rate,
                        line=dict(color="green", dash='dash', width=1.5),
                        row=2, col=1
                    )

            if dataCells:
                for x in data_cells:
                    fig.add_shape(
                        type='line',
                        x0=x, x1=x,
                        y0=0, y1=ymax_rate,
                        line=dict(color='gray', dash='dash', width=0.5),
                        row=2, col=1
                    )
                    
            # --- Axis labels and formatting ---
            fig.update_yaxes(title_text="Rate", row=2, col=1)
            fig.update_xaxes(title_text="Time",tickangle=45,tickmode="array",row=2, col=1)

        
        # Update layout
        fig.update_xaxes(title_text="Time",tickangle=45, showline=True, linecolor="black", row=1, col=1)
        fig.update_yaxes(title_text="Light Curve", showline=True, linecolor="black", row=1, col=1)
        fig.update_layout(
            title=f"Bayesian Blocks Analysis on a Time Series",
            xaxis=dict(tickformat="g"),
            template='plotly_white',
            hovermode="closest",
            showlegend=True,
            #legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(size=17)),
            #margin=dict(t=60, b=60),
            #height=600
        )
        
        # Write plot
        if saveImage:
            fileName = "bayesianblocks"
            fileName+= "_results" if edgePoints else "_data"
            fileName+= "_rate" if plotRate else ""
            fileName+= ".png"
            filePath = join(self.outdir,fileName)
            self.logger.info(f"Plot at: {filePath}")
            fig.write_image(filePath)
            return filePath
        else:
            fig.show()
            return None

    def plotRatemeters(self, data_dict, instruments, T0, x_limits=None, useDetrendedData=True, filePath=None):
        """Plot the Light Curve of the AGILE Scientific Ratemeters.

        Args:
            data_dict (dict[str, Table]): Keys are instrument names, values are Astropy Tables with 'OBT', 'COUNTS', 'COUNTS_D' columns.
            instruments (list[str]): Names of the instruments to plot.
            T0 (float): Burst T0 in AGILE seconds.
            x_limits (tuple(float,float)): plot limits in seconds relative to T0.
            useDetrendedData (bool): If True, plot detrended counts, otherwise plot raw counts. Defaults to True.
            filePath (str): Output path of the plot.

        Returns:
            filePath (str): Output path of the plot.
        """
        # Harcoded information
        INSTRUMENT_COLORS = {
            "SA": "blue",
            "AC0": "green",
            "AC1": "#006400",
            "AC2": "#006400",
            "AC3": "#006400",
            "AC4": "#006400",
            "MCAL": "red",
        }
        INSTRUMENT_RANGES = {
            "SA": "SuperAGILE [18-60 keV]",
            "AC0": "AC Top [50-200 keV]",
            "AC1": "AC Lat 1 [80-200 keV]",
            "AC2": "AC Lat 2 [80-200 keV]",
            "AC3": "AC Lat 3 [80-200 keV]",
            "AC4": "AC Lat 4 [80-200 keV]",
            "MCAL": "MCAL [0.4-100 MeV]",
            "GRID": "GRID [>50 MeV]",
        }
        
        # Subplot layout: one row per instrument
        fig = make_subplots(
            rows=len(instruments),
            cols=1,
            subplot_titles=[INSTRUMENT_RANGES.get(inst, "NotFound") for inst in instruments]
            )
        
        # Add traces for each instrument
        for i, inst in enumerate(instruments, start=1):
            # Select data
            data_table = data_dict[inst]
            if x_limits is not None:
                mask = (data_table['OBT']>T0+x_limits[0])&(data_table['OBT']<T0+x_limits[1])
                data_table = data_table[mask]
            time = data_table['OBT'].data - T0
            counts = data_table['COUNTS_D'].data if useDetrendedData else data_table['COUNTS'].data
            time_width = data_table['OBT'][1]-data_table['OBT'][0]
            rate = counts / time_width
            
            # Add Trace
            trace_1 = go.Scatter(x=time,
                                 y=rate,
                                 mode='lines',
                                 name=inst,
                                 line=dict(shape='hv', color=INSTRUMENT_COLORS.get(inst, "black"))
                                 )
            fig.add_trace(trace_1, row=i, col=1)
            # Axis labels and Limits
            fig.update_yaxes(title_text="Counts Rate [cts/s]", row=i, col=1)
            fig.update_xaxes(title_text="Time - T0 [s]",tickmode="array",row=i, col=1)
            if x_limits is not None:
                fig.update_xaxes(range=[x_limits[0], x_limits[1]], row=i, col=1)
        
        # Update layout
        T0_iso = AstroUtils.convert_time_from_agile_seconds(T0).iso
        detrended_flag = "Detrended " if useDetrendedData else ""
        fig.update_layout(
            title_text = f"{detrended_flag}AGILE Scientific Ratemeters<br>T0={T0_iso} (UTC)",
            title_x=0.5,
            xaxis=dict(tickformat="g"),
            template='plotly_white',
            hovermode="closest",
            height=300 * len(instruments),
            showlegend=False
        )
        
        # Show Image and Write Plot
        fig.show()
        if filePath is not None:
            self.logger.info(f"Plot at: {filePath}")
            fig.write_image(filePath)

        return filePath


    def plotRatemetersDuration(self, data_dict, instruments, T0, backgroundRange=(None,None), signalRange=(None,None), x_limits=None, filePath=None):
        """Plot Ratemeters Light Curves for Burst Duration Computation.

        Args:
            data_dict (dict[str, Table]): Keys are instrument names, values are Astropy Tables with 'OBT', 'COUNTS', 'COUNTS_D' columns.
            instruments (list[str]): Names of the instruments to plot.
            T0 (float): Burst T0 in AGILE seconds.
            x_limits (tuple(float,float)): plot limits in seconds relative to T0.
            useDetrendedData (bool): If True, plot detrended counts, otherwise plot raw counts. Defaults to True.
            filePath (str): Output path of the plot.

        Returns:
            filePath (str): Output path of the plot.
        """
        # Harcoded information
        INSTRUMENT_RANGES = {
            "SA": "SuperAGILE [18-60 keV]",
            "AC0": "AC Top [50-200 keV]",
            "AC1": "AC Lat 1 [80-200 keV]",
            "AC2": "AC Lat 2 [80-200 keV]",
            "AC3": "AC Lat 3 [80-200 keV]",
            "AC4": "AC Lat 4 [80-200 keV]",
            "MCAL": "MCAL [0.4-100 MeV]",
            "GRID": "GRID [>50 MeV]",
        }
        
        # Subplot layout: one column per instrument, two rows
        fig = make_subplots(rows=2,cols=len(instruments),
                            subplot_titles=[f"Light Curve {INSTRUMENT_RANGES.get(inst, 'NotFound')}" for inst in instruments]+[f"Cumulative {INSTRUMENT_RANGES.get(inst, 'NotFound')}" for inst in instruments]
                            )
        
        # Add traces for each instrument
        for i, inst in enumerate(instruments, start=1):
            # Select data
            data_table = data_dict[inst]
            time = data_table['time']
            counts=data_table['counts']
            counts_bkgsub=data_table['counts_bkgsub']
            integral_counts=data_table['integral_counts']
            sigrise_time=data_table['sigrise_time']
            
            # Add Light Curve Trace
            trace_1 = go.Scatter(x=time,y=counts_bkgsub,mode='lines',name=inst,line=dict(shape='hv', color="black"))
            fig.add_trace(trace_1, row=1, col=i)
                
            # Add Cumulative Light Curve Trace
            trace_2 = go.Scatter(x=time,y=integral_counts,mode='lines',name=inst,line=dict(shape='hv', color="black"))
            fig.add_trace(trace_2, row=2, col=i)

            # Add Lines for the Rising Section if present
            try:
                fig.add_vline(x=sigrise_time[ 0],line=dict(color="green",width=2,dash="dash"),row="all",col=i)
                fig.add_vline(x=sigrise_time[-1],line=dict(color="green",width=2,dash="dash"),row="all",col=i)
            except IndexError:
                pass
            
            # Graphis
            fig.update_yaxes(title_text="Counts [cts]", row=1, col=i)
            fig.update_xaxes(title_text="Time - T0 [s]",row=1, col=i)
            fig.update_yaxes(title_text="Counts [cts]", row=2, col=i)
            fig.update_xaxes(title_text="Time - T0 [s]",row=2, col=i)
            

        # Add the Background and Signal Bands
        fig.add_vrect(x0=signalRange[0], x1=signalRange[1],
                      fillcolor="blue", opacity=0.4, line_width=0,
                      row="all", col="all"
                      )
        fig.add_vrect(x0=backgroundRange[0], x1=backgroundRange[1],
                      fillcolor="red", opacity=0.2, line_width=0,
                      row="all", col="all"
                      )
        
        # Graphics
        if x_limits is not None:
            fig.update_xaxes(range=[x_limits[0], x_limits[1]], row="all", col="all")

        # Update layout
        T0_iso = AstroUtils.convert_time_from_agile_seconds(T0).iso
        fig.update_layout(
            title_text = f"AGILE Scientific Ratemeters (Background Subtracted)<br>T0={T0_iso} (UTC)",
            title_x=0.5,
            xaxis=dict(tickformat="g"),
            template='plotly_white',
            hovermode="closest",
            height=900,
            width=500 * len(instruments),
            showlegend=False
        )
        
        # Show Image and Write Plot
        fig.show()
        if filePath is not None:
            self.logger.info(f"Plot at: {filePath}")
            fig.write_image(filePath)

        return filePath
