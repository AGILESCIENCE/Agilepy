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

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from os.path import join, isfile
from agilepy.utils.AstroUtils import AstroUtils
from matplotlib.lines import Line2D

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

    def get_agile_rm_data(self, file):
        # header to reformat unevenly spaced columns
        colnames=['col1', 'time', 'col2','counts', 'col3', 'counts_d']
        data = pd.read_csv(file, header=None, names=colnames, sep='\s', 
                 engine='python')
        return data.drop(['col1', 'col2', 'col3'], axis=1)

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
            self.logger.info(self, "Empty 'agile_time_windows' list")
        return self

    def add_fermi_gti(self, ax, fermi_times, fermi_angles, zmax, threshold):
        # get fermi GTI
        fermi_gti_list = self.get_gti_list(times=fermi_times, angles=fermi_angles, zmax=zmax) 
        for l in fermi_gti_list:
            ax.axvspan(xmin=l[0], xmax=l[1], facecolor='k', alpha=0.1)
        # add interval green lines with 5 min threshold
        fermi_intervals = self.get_intervals_larger_than_threshold(ax=ax, times=fermi_times, threshold=threshold)      
        # get good intervals
        fermi_good_intervals = self.search_interval(fermi_intervals, fermi_gti_list)
        for l in fermi_good_intervals:
            ax.axvspan(xmin=l[0], xmax=l[1], facecolor='white')

        return self

    def plot_offaxis(self, ax, agile_data, timerange, fermi_data=None, zmax=60, agile_time_windows=[], timetype="MJD", trigger_time_tt=None):

        # define tstart and tstop
        tstart = timerange[0]
        tstop = timerange[1]
        self.logger.info(self, f"Time range = [{tstart}, {tstop}] {timetype}")

        # manage time frame and trigger time shift
        assert timetype in ['TT', 'MJD'], ValueError(f'{timetype} must be TT or MJD')
        if timetype == "TT" and trigger_time_tt is not None:
                tstart -= trigger_time_tt
                tstop -= trigger_time_tt
                agile_data -= trigger_time_tt
                if fermi_data is not None:
                    fermi_data -= trigger_time_tt
                agile_time_windows -= trigger_time_tt

        # filter time range
        agile_data = agile_data[(agile_data['time'] > tstart) & (agile_data['time'] < tstop)]
        # plot agile offaxis
        ax.plot(agile_data['time'], agile_data['angle'], color='blue', label='AGILE', linewidth=0.5)

        # plot fermi optionally
        if fermi_data is not None:
            # filter time range
            fermi_data = fermi_data[(fermi_data['time'] > tstart) & (fermi_data['time'] < tstop)]
            # plot fermi offaxis
            ax.plot(fermi_data['time'], fermi_data['angle'], color='red', label='Fermi', linewidth=1.5)

        # decorate axis
        ax.set_ylim(0., zmax+5.0)
        ax.set_xlabel(timetype)
        ax.set_ylabel('off-axis angle (deg)')
        ax.ticklabel_format(axis="x", useOffset=False)
        ax.legend(loc='lower right', shadow=True, fontsize='xx-small')
        return self

    def plot_analyses_comparison(self, ax, dataframes, datainfo, timetype="MJD", trigger_time_tt=None, add_stats_lines=True):

        # extract from data dictionary
        markers = Line2D.markers
        assert len(dataframes) <= len(markers), Exception(f'Too many dataframes ({len(dataframes)}) in a one plot: {len(markers)} max allowed')
            
        # loop over dataframes
        for d, data, m in zip(datainfo, dataframes, markers):
            label = d['label']
            column = d['column']
            error_column = d['error_column']

            # get x, y, xerr
            y = data[column]
            x = (data['tstart'] + data['tstop']) / 2
            xerr = (data['tstop'] - data['tstart']) / 2

            # get yerr
            if error_column is None:
                yerr = 0
            elif 'cts' in error_column.lower() or 'counts' in error_column.lower():
                yerr = np.sqrt(data[data])
            else:
                yerr = data[error_column]

            # option trigger time shift
            if timetype == 'TT' and trigger_time_tt is not None:
                x -= trigger_time_tt

            # plot data
            ax.errorbar(x, y, xerr=xerr, yerr=yerr, marker=m, ls="none", markersize=5.0, linewidth=0.8, label=label)

            # statistics
            if add_stats_lines:
                mean = data[column].mean()
                std = data[column].std()
                ax.axhline(mean, linestyle='solid', color='b', linewidth=0.5)
                ax.axhline(mean + 1 * std, linestyle='dotted', color='b', linewidth=0.5)#, label="1 sigma")
                ax.axhline(mean + 2 * std, linestyle='dashed', color='b', linewidth=0.5)#, label="2 sigma")
                ax.axhline(mean + 3 * std, linestyle='dashdot', color='b', linewidth=1)#,  label="3 sigma")

        # decorations
        ax.set_xlabel(timetype)
        ax.set_ylabel(column)
        ax.ticklabel_format(axis="x", useOffset=False)
        ax.legend(loc='upper right', shadow=True, fontsize='xx-small')
        return self

    def plot_ratemeters(self, ax, rm_dataframes=[], rm_labels=[], timetype="MJD", trigger_time_tt=None):
        # plot each RM 
        for data, label in zip(rm_dataframes, rm_labels):
            # option trigger time shift
            if timetype == 'TT' and trigger_time_tt is not None:
                data['time'] -= trigger_time_tt

            # plot data
            ax.plot(data['time'], data['counts'], label=label)

        # plot decorations
        ax.set_xlabel(timetype)
        ax.set_ylabel('counts')
        ax.ticklabel_format(axis="x", useOffset=False)
        ax.legend(loc='upper right', shadow=True, fontsize='xx-small')
        return self

    def plot_agile_fermi_comparison(self, agile_data_file, fermi_data_file, offaxis_path,  timetype="MJD", timerange=None, agile_time_windows=[], zmax=60, agile_datainfo={'label': 'AGILE', 'column': 'cts', 'error_column': None}, fermi_datainfo={'label': 'AGILE', 'column': 'cts', 'error_column': None}, trigger_time_tt=None, add_rm=False, rm_files=None, rm_labels=None, add_stats_lines=True):

        if timetype not in ["MJD", "TT"]:
            raise Exception("timetype must be MJD or TT")

        # load data
        agile_data = self.get_analysis_data(agile_data_file) # TT
        fermi_data = self.get_analysis_data(fermi_data_file) # TT
        agile_offaxis_data = self.get_agile_offaxis_data(path=offaxis_path) # MJD
        fermi_offaxis_data = self.get_fermi_offaxis_data(path=offaxis_path) # MJD
        rm_dataframes = []
        for f in rm_files:
            rm_dataframes.append(self.get_agile_rm_data(f)) # TT

        # time conversion
        if timetype == 'MJD':
            five_minutes = 5/1440
            agile_data['tstart'] = AstroUtils.time_agile_seconds_to_mjd(agile_data['tstart'])
            agile_data['tstop'] = AstroUtils.time_agile_seconds_to_mjd(agile_data['tstop'])
            fermi_data['tstart'] = AstroUtils.time_agile_seconds_to_mjd(fermi_data['tstart'])
            fermi_data['tstop'] = AstroUtils.time_agile_seconds_to_mjd(fermi_data['tstop'])
        elif timetype == 'TT':
            five_minutes = 300
            agile_offaxis_data['time'] = AstroUtils.time_mjd_to_agile_seconds(agile_offaxis_data['time'])
            fermi_offaxis_data['time'] = AstroUtils.time_mjd_to_agile_seconds(fermi_offaxis_data['time'])

        # define tstart and tstop
        if timerange is not None:
            tstart = timerange[0]
            tstop = timerange[1]
        else:
            tstart = agile_data['tsart'][0]
            tstop = agile_data['tstop'][-1]
            timerange = np.array([tstart, tstop])

        # optional trigger time shift
        if timetype == 'TT' and trigger_time_tt is not None:
            timerange = np.array(timerange) - trigger_time_tt
            tstart -= trigger_time_tt
            tstop -= trigger_time_tt
            agile_time_windows = np.array(agile_time_windows) - trigger_time_tt
            agile_data['tstart'] -= trigger_time_tt
            agile_data['tstop'] -= trigger_time_tt
            agile_offaxis_data['time'] -= trigger_time_tt
            fermi_data['tstart'] -= trigger_time_tt
            fermi_data['tstop'] -= trigger_time_tt
            fermi_offaxis_data['time'] -= trigger_time_tt
            if add_rm:
                for df in rm_dataframes:
                    df['time'] -= trigger_time_tt

        # time selection filter
        if timerange is not None:
            agile_data = agile_data[(agile_data['tstart'] >= tstart) & (agile_data['tstop'] <= tstop)]
            fermi_data = fermi_data[(fermi_data['tstart'] >= tstart) & (fermi_data['tstop'] <= tstop)]
            agile_offaxis_data = agile_offaxis_data[(agile_offaxis_data['time'] >= tstart) & (agile_offaxis_data['time'] <= tstop)]
            fermi_offaxis_data = fermi_offaxis_data[(fermi_offaxis_data['time'] >= tstart) & (fermi_offaxis_data['time'] <= tstop)]
            for df in rm_dataframes:
                df = df[(df['time'] >= tstart) & (df['time'] <= tstop)]

        # number of plots
        n_plots = 3
        if add_rm:
            n_plots += 1
        h_plot = 5 * n_plots
        fig, axes = plt.subplots(n_plots, 1, figsize=(12,h_plot), sharex=True)
        axes[0].set_title(f'{tstart} - {tstop} {timetype} (zmax={zmax})')

        # add offaxis
        self.plot_offaxis(ax=axes[0], agile_data=agile_offaxis_data, fermi_data=fermi_offaxis_data, timetype=timetype, timerange=timerange, zmax=zmax, agile_time_windows=agile_time_windows) 

        # add exposure
        exposure_datainfo = [
            {'label': 'AGILE', 'column': 'exp', 'error_column': None},
            {'label': 'FERMI', 'column': 'exp', 'error_column': None},
        ]
        self.plot_analyses_comparison(ax=axes[1], dataframes=[agile_data, fermi_data], datainfo=exposure_datainfo, timetype=timetype, add_stats_lines=add_stats_lines)

        # add third plot choice
        self.plot_analyses_comparison(ax=axes[2], dataframes=[agile_data, fermi_data], datainfo=[agile_datainfo, fermi_datainfo], timetype=timetype, add_stats_lines=add_stats_lines)

        # add ratemeters option
        if add_rm:
            assert rm_files != None, 'if "add_rm" is True then "rm_files" cannot be None'
            assert rm_labels != None, 'if "add_rm" is True then "rm_files" cannot be None'
            self.plot_ratemeters(axes[3], rm_dataframes=rm_dataframes, rm_labels=rm_labels, timetype=timetype)

        # x-axis range
        if timerange is not None:
            for ax in axes:
                ax.set_xlim(timerange)
        
        # for all axes
        for ax in axes:
            # add GTI
            self.add_agile_gti(ax=ax, agile_time_windows=agile_time_windows)
            # fermi GTI
            self.add_fermi_gti(ax=ax, fermi_times=fermi_offaxis_data['time'], fermi_angles=fermi_offaxis_data['angle'], zmax=zmax, threshold=five_minutes)
            # add decorations
            ax.tick_params(labelbottom=True)
            ax.grid()

        # show
        plt.show()
        # save pdf
        outfilename_pdf = 'merged_plot_'+str(tstart)+'_'+str(tstop)+'.'+str('pdf')
        self.logger.info(self, f"Plot: {outfilename_pdf}")
        fig.savefig(outfilename_pdf, format="pdf")
        # save png
        outfilename_png = 'merged_plot_'+str(tstart)+'_'+str(tstop)+'.'+str('png')
        self.logger.info(self, f"Plot: {outfilename_png}")
        fig.savefig(outfilename_png, format="png")        
        return self