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


from agilepy.api.AGEng import AGEng
from agilepy.external_packages.offaxis.create_offaxis_plot import *
from agilepy.external_packages.offaxis import create_offaxis_plot, agilecheck, fermicheck
from agilepy.external_packages.ap.APDisplayAGILEFermiComparison import *


class AGEngVisibility2(AGEng):
    """This class contains the high-level API methods to run offaxis and offaxis_ap_comparison tools. It's a AGEng subclass"""
    
    def visibilityPlot2(self, time_windows, ra, dec, fermi_datapath, agile_datapath, run, zmax, mode=all, step=1):
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

        offaxis = Create_offaxis_plot(time_windows, ra, dec, fermi_datapath, agile_datapath, run, zmax, mode, step)

        dir = offaxis.run()

        self.logger.info(self,"Output directory: %s", dir)

        return dir

    def apOffaxisComparation(self, agile_pathAP, fermi_pathAP, tstart, tstop, path_offaxis,lines = [], plotrate=False):
        """ It compares and shows aperture photometry data with offaxis results

        Args:
            agile_pathAP (str): agile ap filepath
            fermi_pathAP (str): fermi ap filepath
            tstart (float): time start in MJD
            tstop (float): time stop in MJD
            path_offaxis (str): directory path to offaxis results
            lines (list): 
            plotrate (bool): if true select column rate instead of counts

        return:
            void

        """

        comparison = APDisplayAGILEFermiComparison()

        comparison.load_and_plot(agile_pathAP, fermi_pathAP, tstart, tstop, path_offaxis, lines, plotrate)