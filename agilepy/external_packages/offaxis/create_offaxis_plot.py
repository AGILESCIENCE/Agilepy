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

import os,sys
import numpy as np
from agilepy.external_packages.offaxis.fermicheck import fermicheck
from agilepy.external_packages.offaxis.agilecheck import agilecheck 
from agilepy.external_packages.offaxis.merge import merge
from agilepy.external_packages.offaxis.MET2orbit import MET2orbit
from astropy.table import Table, vstack
from astropy.io import fits
import glob

class Create_offaxis_plot:
    """It plots offaxis curves using agile and fermi fits files
    """

    def __init__(self, time_windows, ra, dec, path_dati_fermi, path_log_index, run_number, zmax, mode, step, outdir):
        
        self.time_windows = time_windows
        self.ra = ra
        self.dec = dec
        self.path_dati_fermi = path_dati_fermi
        self.path_log_index = path_log_index
        self.run_number = run_number
        self.zmax = zmax
        self.mode = mode
        self.step = step
        self.outdir = outdir
        

    def merge_fits(self, input_file, tmin, tmax, output_file):

        concat_cmd = "$AGILE/bin/AG_select "+output_file+"_test"+" "+self.path_log_index+" None "+"{0:.7f}".format(tmin)+" "+"{0:.7f}".format(tmax)
        os.system(concat_cmd)

        hdul = fits.open(output_file+"_test")

        concat_table = Table(hdul[1].data)


        mask = concat_table["LIVETIME"] > 0
        concat_table = concat_table[mask]

        mask = concat_table["LOG_STATUS"] == 0
        concat_table = concat_table[mask]

        mask = concat_table["MODE"] == 2
        concat_table = concat_table[mask]

        mask = concat_table["PHASE"] != 1
        concat_table = concat_table[mask]

        mask = concat_table["PHASE"] != 2
        concat_table = concat_table[mask]

        concat_table.write(output_file, format='fits', overwrite=True)

    def MET2orbit(self, tmin, tmax, path_to_LOG, source='MySource', send=True):
        """
        This function creates two files:
            1) MySource_tmin_tmax.txt containing a list of paths to the attitude information for each selected orbit
            2) merged_list.fits, which is a fits file containing the attitude information, that will be passed to
            the agilecheck.py script. The merged file will be filtered on-the-fly in order to have always INSTR_STATUS>0.
        """
        index  = open(path_to_LOG, 'r')
        filename = str(source)+'_list_of_orbits_'+str(tmin)+'_'+str(tmax)+'.txt'
        file   = open(filename, 'w')
        lines  = index.readlines()
        index_i, index_f = 1e20,1e20
        for i in range(len(lines)):
            field = lines[i].split()
            tstart = field[1]
            tstop  = field[2]
            orbit  = field[0]
            tstart = float(tstart)
            tstop  = float(tstop)
            if (tstart <= tmin) & (tstop >= tmin):
                index_i = i
            if (tstart <=tmax) & (tstop >= tmax):
                index_f = i
            if (i >= index_i) & (i <= index_f):
                print(index_i, index_f, orbit)
                #print >> file, str(orbit)+'[1][MODE > 0 && INSTR_STATUS > 0]' #add row filtering to have good instr_status        
                print(str(orbit), file=file)
        
        print("files ", file, " created successfully")
        file.close()
        if send == True:
            #os.system("sh "+os.environ['AGILEPIPE']+"/merge_orbit_logs.sh "+str(filename)+" merged_list_"+str(tmin)+"_"+str(tmax)+".fits")
            print("Merging fits....")
            self.merge_fits(filename, tmin, tmax, "merged_list_" + str(tmin) + "_" + str(tmax) + ".fits")



    def run(self):

        dirs = []

        for times in self.time_windows:

            #count = count + 1
            #if count != 0:
                #   continue


            tstart = float(times[0])
            tstop = float(times[1])
            print("new ----- \n "+str(tstart)+" "+str(tstop))

            #create dir
            #new_dir =  "dir_"+str(self.run_number)+"_"+str(self.zmax)+"_"+str(tstart)+"_"+str(tstop)
            new_dir = self.outdir+"/dir_"+str(self.run_number)+"_"+str(self.zmax)+"_"+str(tstart)+"_"+str(tstop)
            
            dirs.append(new_dir)

            os.mkdir(new_dir)
            os.chdir(new_dir)

            f = open("output_"+str(self.zmax)+".txt", "a")
            f.write("\n#####\n")
            f.write(str(self.zmax)+" "+str(tstart)+" "+str(tstop)+"\n")
            f.close()

            #### FERMI ####

            if(self.mode == "fermi" or self.mode == "all"):

                fermi_met_start = (tstart - 51910.0 ) * 86400.0
                fermi_met_stop = (tstop - 51910.0 ) * 86400.0

                print("fermi time"+str(fermi_met_start)+" "+str(fermi_met_stop))

                check = fermicheck(self.path_dati_fermi, self.ra, self.dec, tstart, tstop, zmax=self.zmax, timelimiti=fermi_met_start,step=self.step, timelimitf=fermi_met_stop,out_name="output_"+str(self.zmax)+".txt")
                check.PlotVisibility()
                #os.system("cp fermi_visibility*eps "+new_dir)

            #AGILE

            if(self.mode == "agile" or self.mode == "all"):

                agile_met_start = (tstart - 53005.0) *  86400.0
                agile_met_stop = (tstop - 53005.0) *  86400.0

                print("agile "+str(agile_met_start)+" "+str(agile_met_stop))

                self.MET2orbit(agile_met_start, agile_met_stop, self.path_log_index)

                merged_file = glob.glob('merged_list_*.fits')[0]
                check = agilecheck(merged_file, self.ra, self.dec, tstart, tstop, zmax=self.zmax, timelimiti=agile_met_start, timelimitf=agile_met_stop, step=self.step, out_name="output_"+str(self.zmax)+".txt")
                check.PlotVisibility()

            ### MERGE TWO PLOT ###

            #if(mode == "all"):
            t0 = tstart+((tstop-tstart)/2)
            t0 = 0
            check=merge(timelimiti=tstart, timelimitf=tstop, t0=t0,zmax=self.zmax)
            check.Plotmerge(mode=self.mode)
            check.histogram_merge(mode=self.mode)

            os.chdir("..")

        return dirs