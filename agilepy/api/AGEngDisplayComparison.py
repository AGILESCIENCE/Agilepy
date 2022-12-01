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
from os.path import join, isfile
from agilepy.utils import Utils
from agilepy.utils.AstroUtils import AstroUtils
from agilepy.external_packages.offaxis.create_offaxis_plot import Create_offaxis_plot

# plt revert to font defaults
plt.rc('font', family='sans-serif') 
plt.rc('font', serif='Helvetica Neue') 
plt.rc('text', usetex='false') 

## WIP!!
## this is intended as a generalised refactoring of APDisplayAgileFermiComparison

class AGEngDisplayComparison:
    """This class compares and plots results from different AGILE analyses and/or from AGILE and FERMI analyses. 
    """

    def __init__(self, logger):
        self.logger = logger

    def search_interval(self, arr1, arr2):
        intervals = []
        i = 0
        j = 0

        n = len(arr1)
        m = len(arr2)
        while i < n and j < m:
            l = max(arr1[i][0], arr2[j][0])
            r = min(arr1[i][1], arr2[j][1])
            if l < r:
                intervals.append([l,r])
            if arr1[i][1] < arr2[j][1]:
                i += 1
            else:
                j += 1
        return intervals

    def get_agile_offaxis_file(self, path, file='time_vs_separation_agile.txt'):
        f = join(path, file)
        assert isfile(f), FileNotFoundError()
        return f

    def get_fermi_offaxis_file(self, path, file='time_vs_separation_fermi.txt'):
        f = join(path, file)
        assert isfile(f), FileNotFoundError()
        return f

    def get_agile_offaxis_data(self, path, file='time_vs_separation_agile.txt'):
        f = self.get_agile_offaxis_file(path=path, file=file)
        # times are in MJD
        data = pd.read_csv(f, names=['time','angle'], header=None, sep=' ')
        return data

    def get_fermi_offaxis_data(self, path, file='time_vs_separation_fermi.txt'):
        f = self.get_fermi_offaxis_file(path=path, file=file)
        # times are in MJD
        data = pd.read_csv(f, names=['time','angle'], header=None, sep=' ')
        return data

    def get_analysis_data(self, file):
        # times in TT
        data = pd.read_csv(file, header=0, sep=' ')
        return data

    def get_gti_list(self, times, angles, zmax=60):
        found = False
        total_s_in_gti = 0
        gti_list = []
        for t, a in zip(times, angles):

            if not found and a <= zmax:
                found = True
                gti_time = t
                t1 = t

            if found and a >= zmax:
                found = False
                gti_time = (t) - gti_time
                total_s_in_gti += gti_time
                t2 = t
                gti_list.append([t1, t2]) 

        self.logger.info(self, f"Total time in GTI = {total_s_in_gti} s")
        return gti_list

    def get_intervals_larger_than_threshold(self, ax, times, threshold):
        intervals = []
        for i in range(len(times) - 1):
            if (times[i+1] - times[i]) >= threshold:  
                self.logger.debug(self, f"Green box in: {times[i]}, {times[i+1]}")
                intervals.append([times[i], times[i+1]])
                ax.axvline(times[i], linestyle='--', color='green', linewidth=0.5)
                ax.axvline(times[i+1], linestyle='--', color='green', linewidth=0.5)
        return intervals

    def add_agile_gti(self, ax, agile_time_windows):
        try:
            for i in range(0,len(agile_time_windows),2):
                ax.axvspan(xmin=agile_time_windows[i], xmax=agile_time_windows[i+1], facecolor='y', alpha=0.1)
        except:
            self.logger.info(self, "No GTI provided")
        return self

    def add_fermi_gti(self, ax, fermi_times, fermi_angles, zmax, threshold):
        # add interval green lines with 5 min threshold
        fermi_intervals = self.get_intervals_larger_than_threshold(ax=ax, times=fermi_times, threshold=threshold)      
        # get good intervals
        fermi_good_intervals = self.search_interval(fermi_intervals, fermi_gti_list)
        for l in fermi_good_intervals:
            ax.axvspan(xmin=l[0], xmax=l[1], facecolor='white')
        # get fermi GTI
        fermi_gti_list = self.get_gti_list(times=fermi_times, angles=fermi_angles, zmax=zmax) 
        for l in fermi_gti_list:
            ax.axvspan(xmin=l[0], xmax=l[1], facecolor='k', alpha=0.1)
        return self

    def plot_offaxis(self, ax, agile_data, timerange, fermi_data=None, zmax=60, agile_time_windows=[], timetype="MJD", trigger_time_tt=None):

        # define tstart and tstop
        tstart = tstart
        tstop = tstop
        self.logger.info(self, f"Time range = [{tstart}, {tstop}] {timetype}")

        # manage time frame and trigger time shift
        if timetype =="MJD":
            five_minutes = 5/1440
        elif timetype =="TT":
            five_minutes = 300
            if trigger_time_tt is not None:
                tstart -= trigger_time_tt
                tstop -= trigger_time_tt
                agile_data -= trigger_time_tt
                if fermi_data != None:
                    fermi_data -= trigger_time_tt
                agile_time_windows -= trigger_time_tt
        else:
            raise Exception("Wrong timetype or missing TT times")

        # filter time range
        agile_data = agile_data[(agile_data['time'] > tstart) & (agile_data['time'] < tstop)]
        # plot agile offaxis
        ax.plot(agile_data['time'], agile_data['angle'], color='blue', label='AGILE', linewidth=0.5)
        # add agile GTI
        self.add_agile_gti(ax=ax, agile_time_windows=agile_time_windows)

        # plot fermi optionally
        if fermi_data != None:
            # filter time range
            fermi_data = fermi_data[(fermi_data['time'] > tstart) & (fermi_data['time'] < tstop)]
            # plot fermi offaxis
            ax.plot(fermi_data['time'], fermi_data['angle'], color='red', label='Fermi', linewidth=1.5)
            # fermi GTI
            self.add_fermi_gti(ax=ax, fermi_times=fermi_data['time'], fermi_angles=fermi_data['angle'], zmax=zmax, threshold=five_minutes)

        # decorate axis
        ax.set_ylim(0., zmax+5.0)
        ax.set_xlabel(timetype)
        ax.ticklabel_format(axis="x", useOffset=False)
        ax.legend(loc='lower right', shadow=True, fontsize='xx-small')
        ax.set_ylabel('off-axis angle (deg)')
        ax.set_title(f'{tstart} - {tstop} {timetype} (zmax={zmax})')
        return self




    def agile_fermi_comparison(self, agile_data_file, fermi_data_file, offaxis_path,  timetype="MJD", timerange=None, agile_time_windows=[], zmax=60, data_column_name="cts", trigger_time_tt=None, add_rm=False, rm_files=None, rm_labels=None):

        if timetype not in ["MJD", "TT"]:
            raise Exception("timetype must be MJD or TT")

        # loag data
        agile_data = self.get_analysis_data(agile_data_file) # TT
        fermi_data = self.get_analysis_data(fermi_data_file) # TT
        agile_offaxis_data = self.get_agile_offaxis_data(path=offaxis_path) # MJD
        fermi_offaxis_data = self.get_fermi_offaxis_data(path=offaxis_path) # MJD

        # time conversion
        if timetype == 'MJD':
            agile_data['tstart'] = AstroUtils.time_agile_seconds_to_mjd(agile_data['tstart'])
            agile_data['tstop'] = AstroUtils.time_agile_seconds_to_mjd(agile_data['tstop'])
            fermi_data['tstart'] = AstroUtils.time_agile_seconds_to_mjd(fermi_data['tstart'])
            fermi_data['tstop'] = AstroUtils.time_agile_seconds_to_mjd(fermi_data['tstop'])
        elif timetype == 'TT':
            agile_offaxis_data['time'] = AstroUtils.time_mjd_to_agile_seconds(agile_offaxis_data['time'])
            fermi_offaxis_data['time'] = AstroUtils.time_mjd_to_agile_seconds(fermi_offaxis_data['time'])

        # define tstart and tstop
        if timerange != None:
            tstart = timerange[0]
            tstart = timerange[1]
        else:
            tstart = agile_data['tsart'][0]
            tstop = agile_data['tstop'][-1]

        # time selection
        if timerange != None:
            agile_data = agile_data[(agile_data.tstart >= tstart) & (agile_data.tstop <= tstop)]
            fermi_data = fermi_data[(fermi_data.tstart >= tstart) & (fermi_data.tstop <= tstop)]
            agile_offaxis_data = agile_offaxis_data[(agile_offaxis_data.time >= tstart) & (agile_offaxis_data.time <= tstop)]
            fermi_offaxis_data = fermi_offaxis_data[(fermi_offaxis_data.time >= tstart) & (fermi_offaxis_data.time <= tstop)]

        if timetype == "MJD":
            agile_time_windows = agile_time_windows
        else:
            agile_time_windows = AstroUtils.time_mjd_to_agile_seconds(agile_time_windows)
            
        # number of plots
        n_plots = 3
        if add_rm:
            n_plots += 1
        h_plot = 5 * n_plots

        # plotting
        f, axes = plt.subplots(n_plots, 1, figsize=(12,h_plot), sharex=True)
        # add offaxis
        self.plot_offaxis(ax=axes[0], agile_data=agile_data, fermi_data=fermi_data, timetype=timetype, timerange=timerange, zmax=zmax, agile_git_list=agile_time_windows, trigger_time_tt=trigger_time_tt) 
        # add exposure
        self.plot_aperture_photometry(axes[1], agile_data, fermi_data, timetype=timetype, data_column_name="exp", trigger_time_tt=trigger_time_tt)
        # add third plot choice
        self.plot_aperture_photometry(axes[2], agile_data, fermi_data, timetype=timetype, data_column_name=data_column_name, trigger_time_tt=trigger_time_tt)
        # add ratemeters option
        if add_rm and rm_labels != None and rm_files != None:
            assert rm_files != None, 'if "add_rm" is True then "rm_files" cannot be None'
            assert rm_labels != None, 'if "add_rm" is True then "rm_files" cannot be None'
            self.plot_ratemeters(axes[3], rm_files=rm_files, rm_labels=rm_labels, timetype=timetype, trigger_time_tt=trigger_time_tt)

        if timerange is not None:
            if timetype == 'TT' and trigger_time_tt is not None:
                    timerange -= trigger_time_tt
            for ax in axes:
                ax.set_xlim(timerange)
            
        for ax in axes:
            ax.tick_params(labelbottom=True)
            ax.grid()

        plt.show()

        outfilename_pdf = 'merged_plot_'+str(tstart)+'_'+str(tstop)+'.'+str('pdf')
        self.logger.info(self, f"Plot: {outfilename_pdf}")
        f.savefig(outfilename_pdf, format="pdf")

        outfilename_png = 'merged_plot_'+str(tstart)+'_'+str(tstop)+'.'+str('png')
        self.logger.info(self, f"Plot: {outfilename_png}")
        f.savefig(outfilename_png, format="png")        