# DESCRIPTION
#       Agileap: AGILE Observatory Aperture Photometry Analysis
# NOTICE
#      Any information contained in this software
#      is property of the AGILE TEAM and is strictly
#      private and confidential.
#      Copyright (C) 2005-2020 AGILE Team.
#          Bulgarelli Andrea <andrea.bulgarelli@inaf.it>
#          Antonio Addis <antonio.addis@inaf.it>
#          Valentina Fioretti <valentina.fioretti@inaf.it>
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
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from agilepy.utils.AstroUtils import AstroUtils


class APDisplayAGILEFermiComparison:
    """This class compares and plots Aperture photometry results with offaxis results
    """

    def __init__(self, logger):
        self.logger = logger


    def search_interval(self, arr1, arr2):
        result = []
        i = 0
        j = 0

        n = len(arr1)
        m = len(arr2)
        while i < n and j < m:
            l = max(arr1[i][0], arr2[j][0])
            r = min(arr1[i][1], arr2[j][1])
            if l < r:
                result.append([l,r])
            if arr1[i][1] < arr2[j][1]:
                i += 1
            else:
                j += 1
        return result

    def plot_aperture_photometry(self, ax, agile_data, fermi_data, timetype="MJD", data_column_name="cts", trigger_time_tt=None):

        #---AGILE----

        # Casistiche AGILE
        # 1° data_column_name = conteggi
        # 2° data_column_name = sigma, exposure
        # 3° data_column_name = rate, flussi, ..
        if data_column_name == "cts":
            yerr = np.sqrt(agile_data[data_column_name])
        elif "Sign" in data_column_name or data_column_name == "exp":
            yerr = 0
        elif "flux" in data_column_name or "rate" in data_column_name:
            yerr = agile_data[data_column_name+"Error"] #* 1e8
            agile_data[data_column_name] #*= 1e8
        
        # ---- times ---
        if timetype == "MJD":
            tm = (
                AstroUtils.time_agile_seconds_to_mjd(agile_data["tstart"]) + 
                AstroUtils.time_agile_seconds_to_mjd(agile_data["tstop"])) / 2
            tw = (
                AstroUtils.time_agile_seconds_to_mjd(agile_data["tstop"]) - 
                AstroUtils.time_agile_seconds_to_mjd(agile_data["tstart"])) / 2
        else:
            tm = (agile_data["tstart"] + agile_data["tstop"]) / 2
            tw = (agile_data["tstop"] - agile_data["tstart"]) / 2
            if trigger_time_tt is not None:
                tm -= trigger_time_tt

        ax.errorbar(tm, agile_data[data_column_name], xerr=tw, yerr=yerr, color="b", marker="o", ls="none", markersize=1.0, linewidth=0.8, label="AGILE")

        self.logger.info( f"AGILE mean, {agile_data[data_column_name].mean()}")
        self.logger.info( f"AGILE median {agile_data[data_column_name].median()}")
        self.logger.info( f"AGILE std {agile_data[data_column_name].std()}")

        agilemean = agile_data[data_column_name].median()
        agilestd = agile_data[data_column_name].std()

        ax.axhline(agilemean, linestyle='solid', color='b', linewidth=0.5)
        ax.axhline(agilemean + 1 * agilestd, linestyle='dotted', color='b', linewidth=0.5)#, label="1 sigma")
        ax.axhline(agilemean + 2 * agilestd, linestyle='dashed', color='b', linewidth=0.5)#, label="2 sigma")
        ax.axhline(agilemean + 3 * agilestd, linestyle='dashdot', color='b', linewidth=1)#,  label="3 sigma")

        #---Fermi----
        if timetype == "MJD":
            tmFermi = (
                AstroUtils.time_agile_seconds_to_mjd(fermi_data["tstart"]) + 
                AstroUtils.time_agile_seconds_to_mjd(fermi_data["tstop"])) / 2
            twFermi = (
                AstroUtils.time_agile_seconds_to_mjd(fermi_data["tstop"]) - 
                AstroUtils.time_agile_seconds_to_mjd(fermi_data["tstart"])) / 2      
        else:
            tmFermi = (fermi_data["tstart"] + fermi_data["tstop"]) / 2
            twFermi = (fermi_data["tstop"] - fermi_data["tstart"]) / 2
            if trigger_time_tt is not None:
                tmFermi -= trigger_time_tt

        # Casistiche FERMI
        if "Sign" in data_column_name or "flux" in data_column_name:
            self.logger.warning( f"Column {data_column_name} does not exist in FERMI data. Comparing with 'rate' column.")
            data_column_name = "rate"

        if data_column_name == "cts":
            yerr = np.sqrt(fermi_data[data_column_name])
        elif "Sign" in data_column_name or data_column_name == "exp":
            yerr = 0

        elif "flux" in data_column_name or "rate" in data_column_name:
            yerr = fermi_data[data_column_name+"Error"]# * 1e8
            fermi_data[data_column_name] #*= 1e8
            ax.set_yscale("log")
        
        ax.errorbar(tmFermi, fermi_data[data_column_name], xerr=twFermi, yerr=yerr, color="r", marker="s", ls="none", markersize=1.0, linewidth=0.8, label="FERMI")

        self.logger.info( f"Fermi mean {fermi_data[data_column_name].mean()}")
        self.logger.info( f"Fermi median {fermi_data[data_column_name].median()}")
        self.logger.info( f"Fermi std' {fermi_data[data_column_name].std()}")

        fermimean = fermi_data[data_column_name].mean()
        fermistd = fermi_data[data_column_name].std()

        ax.axhline(fermimean, linestyle='solid', color='r', linewidth=0.5)
        ax.axhline(fermimean + 1 * fermistd, linestyle='dotted', color='r', linewidth=0.5)
        ax.axhline(fermimean + 2 * fermistd, linestyle='dashed', color='r', linewidth=0.5)
        ax.axhline(fermimean + 3 * fermistd, linestyle='dashdot', color='r', linewidth=1)

        time_diff = fermi_data["tstop"] - fermi_data["tstart"]
        self.logger.info( f"Total time in GTI(bottom plot) {time_diff.sum()}")
            
        ax.set_xlabel(timetype)
        ax.set_ylabel(data_column_name)
        ax.ticklabel_format(axis="x", useOffset=False)
        ax.legend(loc='upper right', shadow=True, fontsize='xx-small')

        del agile_data, fermi_data, tm, tmFermi

        
    def plot_offaxis(self, axes, path, tstart_mjd, tstop_mjd, zmax, step, vertical_boxes, timetype="MJD", tstart_tt = None, tstop_tt = None, trigger_time_tt=None):

        try:
            agl_meantime, agl_separation = np.loadtxt(path+'/time_vs_separation_agile.txt', unpack=True)
            lat_meantime, lat_separation = np.loadtxt(path+'/time_vs_separation_fermi.txt', unpack=True)
        except:
            return

        if timetype =="MJD":
            tstart = tstart_mjd
            tstop = tstop_mjd
            five_minutes = 5/1440

        elif timetype =="TT" and tstart_tt is not None and tstop_tt is not None:
            tstart = tstart_tt
            tstop = tstop_tt
            five_minutes = 300
            agl_meantime = AstroUtils.time_mjd_to_agile_seconds(agl_meantime)
            lat_meantime = AstroUtils.time_mjd_to_agile_seconds(lat_meantime)
            if trigger_time_tt is not None:
                tstart -= trigger_time_tt
                tstop -= trigger_time_tt
                agl_meantime -= trigger_time_tt
                lat_meantime -= trigger_time_tt
                vertical_boxes -= trigger_time_tt
        else:
            raise Exception("Wrong timetype or missing TT times")

        agl_filt = agl_meantime[(agl_meantime > tstart) & (agl_meantime < tstop)]
        agl_sep_filt = agl_separation[(agl_meantime > tstart) & (agl_meantime < tstop)]

        lat_filt = lat_meantime[(lat_meantime > tstart) & (lat_meantime < tstop)]
        lat_sep_filt = lat_separation[(lat_meantime > tstart) & (lat_meantime < tstop)]

        self.logger.info( f"{tstart}, {tstop}")
        axes[0].plot(agl_filt, agl_sep_filt, color='blue', label='AGILE', linewidth=0.5)
        axes[0].plot(lat_filt, lat_sep_filt, color='red', label='Fermi', linewidth=1.5)

        ###### GREEN BOXES
        lat_filt2 = []
        for i in range(len(lat_filt) - 1):
            if (lat_filt[i+1] - lat_filt[i]) >= five_minutes:  
                self.logger.debug( f"Green box in: {lat_filt[i]}, {lat_filt[i+1]}")
                lat_filt2.append([lat_filt[i], lat_filt[i+1]])
                axes[0].axvline(lat_filt[i], linestyle='--', color='green', linewidth=0.5)
                axes[0].axvline(lat_filt[i+1], linestyle='--', color='green', linewidth=0.5)

        #######------GTI------###
        found = False
        total_s_in_gti = 0
        gti_list = []
        for l, s in zip(lat_filt, lat_sep_filt):

            if not found and s <= zmax:
                found = True
                gti_time = l
                l1 = l

            if found and s >= zmax:
                found = False
                gti_time = (l) - gti_time
                total_s_in_gti += gti_time
                l2 = l
                gti_list.append([l1,l2])        
        
        #####-----cleaning------
        result = self.search_interval(lat_filt2, gti_list)

        for l in result:
            seconds = (l[1] - l[0]) * 86400
            total_s_in_gti = total_s_in_gti - seconds

        for lines in gti_list:
            for ax in axes:
                ax.axvspan(xmin=lines[0], xmax=lines[1], facecolor='k', alpha=0.1)

        for lines in result:
            for ax in axes:
                ax.axvspan(xmin=lines[0], xmax=lines[1], facecolor='white')

        ###### YELLOW BOXES
        self.logger.info( f"Total time in GTI {total_s_in_gti}")
        try:
            for i in range(0,len(vertical_boxes),2):
                for ax in axes:
                    ax.axvspan(xmin=vertical_boxes[i], xmax=vertical_boxes[i+1], facecolor='y', alpha=0.1)
        except:
            self.logger.info( "No lines")

        axes[0].set_ylim(0., zmax+5.0)
        axes[0].set_title(f"T=[{tstart}, {tstop}] {timetype} Zmax={zmax}  ")
        axes[0].set_xlabel(timetype)
        axes[0].ticklabel_format(axis="x", useOffset=False)
        axes[0].legend(loc='lower right', shadow=True, fontsize='xx-small')
        axes[0].set_ylabel('off-axis angle [$^{\\circ}$]')

        #print(f'!!! times plot_offaxis {tstart} {trigger_time_tt}')
        del tstart, tstop, agl_meantime, lat_meantime, vertical_boxes


    def plot_ratemeters(self, ax, rm_files=[], rm_labels=[], timetype="MJD", trigger_time_tt=None):

        # load data
        colnames = ['col1', 'TIME', 'col2','COUNTS', 'col3', 'COUNTS_D']
        for f, label in zip(rm_files, rm_labels):
            data = pd.read_csv(f, header=None, names=colnames, sep='\s', 
                 engine='python')
            data = data.drop(['col1', 'col2', 'col3'], axis=1)

            # times (ratemeters are in TT)
            if timetype == 'MJD':
                data['TIME'] = AstroUtils.time_agile_seconds_to_mjd(data['TIME'])
            elif timetype == 'TT' and trigger_time_tt is not None:
                    data['TIME'] -= trigger_time_tt

            # plot data
            ax.plot(data['TIME'], data['COUNTS'], label=label)
            #print(f'!!! times plot_ratemeters {data["TIME"].iloc[0]} {trigger_time_tt}')
            del data

        # plot decorations
        ax.set_xlabel(timetype)
        ax.set_ylabel('counts')
        ax.ticklabel_format(axis="x", useOffset=False)
        ax.legend(loc='upper right', shadow=True, fontsize='xx-small')


    def checkSignificance(self, fermi, tstart, tstop):
        fermi_data = pd.read_csv(fermi, header=0, sep=" ")
        ntrials = 0
        nsig = 0

        for time in range(int(tstart), int(tstop)):
            tstart_tt = AstroUtils.time_mjd_to_agile_seconds(time)
            tstop_tt = AstroUtils.time_mjd_to_agile_seconds(time+1)
            fermi_data2 = fermi_data[fermi_data.tstart >= tstart_tt]
            fermi_data2 = fermi_data2[fermi_data.tstop <= tstop_tt]
            fermimean = fermi_data2["cts"].mean()
            fermistd = fermi_data2["cts"].std()

            n=0
            for cts in fermi_data2["cts"]:
                ntrials = ntrials + 1
                if cts >= (fermimean + 5 * fermistd):
                    self.logger.info( "####")
                    self.logger.info( f"{fermi_data2['tstart']}")
                    nsig = nsig + 1
                    break
                n = n + 1

        self.logger.info( f"ntrials {ntrials}")
        self.logger.info( f"nsig {nsig}")

    def load_and_plot(self, agile, fermi, tstart, tstop, path, vertical_boxes_mjd=[], zmax=60, timetype="MJD", data_column_name="cts", time_range=None, trigger_time_tt=None, add_rm=False, rm_files=None, rm_labels=None):

        if timetype not in ["MJD", "TT"]:
            raise Exception("timetype must be MJD or TT")

        #---- Loading data -----
        agile_data = pd.read_csv(agile, header=0, sep=" ") # TT
        fermi_data = pd.read_csv(fermi, header=0, sep=" ") # TT

        #---Converting times
        tstart_tt = AstroUtils.time_mjd_to_agile_seconds(tstart)
        tstop_tt = AstroUtils.time_mjd_to_agile_seconds(tstop)

        #---- Selecting data
        agile_data = agile_data[agile_data.tstart >= tstart_tt]
        agile_data = agile_data[agile_data.tstop <= tstop_tt]
        fermi_data = fermi_data[fermi_data.tstart >= tstart_tt]
        fermi_data = fermi_data[fermi_data.tstop <= tstop_tt]

        if timetype == "MJD":
            vertical_boxes = vertical_boxes_mjd
        else:
            vertical_boxes = AstroUtils.time_mjd_to_agile_seconds(vertical_boxes_mjd)
            
        # number of plots
        n_plots = 3
        if add_rm:
            n_plots += 1
        h_plot = 5*n_plots

        #------Plotting data
        #print(f'!!! times load_and_plot {tstart} {trigger_time_tt}')
        fig, axes = plt.subplots(n_plots, 1, figsize=(12.18,h_plot), sharex=True)
        self.plot_offaxis(axes, path, tstart, tstop, zmax, 1, vertical_boxes, timetype=timetype, tstart_tt=tstart_tt, tstop_tt=tstop_tt, trigger_time_tt=trigger_time_tt) 
        self.plot_aperture_photometry(axes[1], agile_data, fermi_data, timetype=timetype, data_column_name="exp", trigger_time_tt=trigger_time_tt)
        self.plot_aperture_photometry(axes[2], agile_data, fermi_data, timetype=timetype, data_column_name=data_column_name, trigger_time_tt=trigger_time_tt)
        # add ratemeters option
        if add_rm and rm_labels != None and rm_files != None:
            assert rm_files != None, 'if "add_rm" is True then "rm_files" cannot be None'
            assert rm_labels != None, 'if "add_rm" is True then "rm_files" cannot be None'
            self.plot_ratemeters(axes[3], rm_files=rm_files, rm_labels=rm_labels, timetype=timetype, trigger_time_tt=trigger_time_tt)

        if time_range is not None:
            if timetype == 'TT' and trigger_time_tt is not None:
                    time_range -= trigger_time_tt
            for ax in axes:
                ax.set_xlim(time_range)
        #print(f'!!! time range {time_range} {trigger_time_tt}')

        for ax in axes:
            ax.tick_params(labelbottom=True)
            ax.grid()

        plt.show()

        outfilename_pdf = 'merged_plot_'+str(tstart)+'_'+str(tstop)+'.'+str('pdf')
        self.logger.info( f"Plot: {outfilename_pdf}")
        fig.savefig(outfilename_pdf, format="pdf")

        outfilename_png = 'merged_plot_'+str(tstart)+'_'+str(tstop)+'.'+str('png')
        self.logger.info( f"Plot: {outfilename_png}")
        fig.savefig(outfilename_png, format="png")  

        plt.close()      
        del agile_data, fermi_data
        del time_range, vertical_boxes_mjd
        del tstart, tstop, trigger_time_tt
        del fig, axes