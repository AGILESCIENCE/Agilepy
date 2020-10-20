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


# if __name__ == "__main__":

#     #---------------Offaxis testing-------------------
    
#     path = "/data01/homes/addis/Agilepy/agilepy/external_packages/offaxis_conf.yaml"
#     ageng = AGEngVisibility2(path)
#     """
#     time_windows = [[55599.0, 55600.0]]
#     ra = 263.85
#     dec = -32.93
#     fermi_path = "/data01/FERMI_DATA/SC00.fits"
#     #agile_path = "/data01/ASDC_PROC3/DATA_ASDCe/INDEX/LOG.log.index"
#     agile_path = "/data01/ASDC_PROC2/DATA_2/INDEX/LOG.log.index"
#     run = 49
#     zmax = 60
#     mode = "all"
#     step = 1

#     dir = ageng.visibilityPlot2(time_windows, ra, dec, fermi_path, agile_path, run, zmax, mode, step)
#     """
#     #---------------comparison testing------------------

#     ap_agile = "/data01/homes/addis/Agilepy/agilepy/external_packages/ap/AGILE3.ap4"
#     ap_fermi = "/data01/homes/addis/Agilepy/agilepy/external_packages/ap/FERMI5.ap4"
#     tstart = 55599.0
#     tstop = 55600.0
#     path_offaxis = "dir_49_60_55599.0_55600.0"
#     lines = [55599.2, 55599.4]
#     plotrate = False

#     ageng.apOffaxisComparation(ap_agile, ap_fermi, tstart, tstop, path_offaxis, lines, plotrate)



        


