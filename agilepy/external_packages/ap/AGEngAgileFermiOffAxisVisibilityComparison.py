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

from agilepy.core.AGBaseAnalysis import AGBaseAnalysis

from agilepy.external_packages.offaxis.create_offaxis_plot import Create_offaxis_plot
from agilepy.external_packages.offaxis import create_offaxis_plot, agilecheck, fermicheck
from agilepy.external_packages.ap.APDisplayAGILEFermiComparison import APDisplayAGILEFermiComparison
from agilepy.utils.Utils import Utils, expandvars
from pathlib import Path


class AGEngAgileFermiOffAxisVisibilityComparison(AGBaseAnalysis):
    """This class contains the high-level API methods to run offaxis and offaxis_ap_comparison tools. It's a AGEng subclass"""




    def visibilityPlot(self, time_windows, ra, dec, fermi_datapath, agile_datapath, run, zmax, mode=all, step=1):
        """It runs offaxis tools and creates a directory containing the result files
        
        Args:
            time_windws (2d float Array): It contains the tstart-tstop intervals to process the data, the structure has developed as a 2d array(eg [[t1,t2],[t3, t4], ..., [tn-1, tn]])
            ra (float): ra value
            dec (float): dec value
            fermi_datapath (str): fermi log filepath
            agile_datapath (str): agile log filepath
            run (integer): run number
            zmax (float): maximum offaxis degrees
            mode (str): options "agile" | "fermi" | "all": Select all to plot both data, otherwise it will plot only agile/fermi data 
            step (float): step value for plotting
        
        Returns:
            dir (str): A new directory containing the results
        """
        self.outdir = self.config.getOptionValue("outdir")

        agile_datapath = Utils._expandEnvVar(agile_datapath)
        fermi_datapath = Utils._expandEnvVar(fermi_datapath)


        offaxis = Create_offaxis_plot(time_windows, ra, dec, fermi_datapath, agile_datapath, run, zmax, mode, step, outdir=self.outdir, logger=self.logger)

        dir = offaxis.run()

        self.logger.info("Output directory: %s", dir)

        return dir

    def apOffaxisComparation(self, agile_pathAP, fermi_pathAP, tstart_mjd, tstop_mjd, path_offaxis, vertical_boxes_mjd = [], zmax=60, timetype="MJD", data_column_name="cts", time_range=None, trigger_time_tt=None, add_rm=False, rm_files=None, rm_labels=None):
        """ It compares and shows aperture photometry data with offaxis results. 
        
        WARNING: This class should be instanced anew any time a new plot is generated, to ensure its correctness.

        Args:
            agile_pathAP (str): agile ap filepath
            fermi_pathAP (str): fermi ap filepath
            tstart_mjd (float): time start in MJD
            tstop_mjd (float): time stop in MJD
            path_offaxis (str): directory path to offaxis results
            vertical_boxes_mjd (list): time in MJD
            zmax (float): maximum offaxis degrees
            timetype (str): time type to plot [MJD, TT]
            data_column_name (str): name of column to plot
            time_range (list): time xrange in MJD or TT depending on "timetype"
            trigger_time_tt (float or None): trigger time in TT
            add_rm (bool): add fourth plot with AGILE ratemeters
            rm_files (list): list of absolute paths for all RM to plot
            rm_lables (list): list of labels to pair to RM files

        return:
            void

        """

        comparison = APDisplayAGILEFermiComparison(self.logger)

        #print(f'!!! times apOffAxisComparation {tstart_mjd} {trigger_time_tt}')
        comparison.load_and_plot(agile_pathAP, fermi_pathAP, tstart_mjd, tstop_mjd, path_offaxis, zmax=zmax, vertical_boxes_mjd=vertical_boxes_mjd, timetype=timetype, data_column_name=data_column_name, time_range=time_range, trigger_time_tt=trigger_time_tt, add_rm=add_rm, rm_files=rm_files, rm_labels=rm_labels)

