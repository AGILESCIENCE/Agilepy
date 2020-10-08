# Setup-environment:
# source activate py_mcal_27
# source /opt/module/heasoft-6.25
#
# parameters:
#
# 1) time window path, this file must contains rows for different time windows in MJD format
# 54746.0 54747.0
# 54915.0 54916.0
# 2) ra: position of the source
# 3) dec: position of the source
# 4) path to Fermi data fits
# 5) path to AGILE index file (/AGILE_PROC3/DATA_2/INDEX/LOG.log.index)
# 6) run number
# 7) zmax: maximum zenith distance of the source to the center of the detector (unit: degrees) (50.0,60.0 ecc)
# 8) mode: agile || fermi || all

# example

# OUTPUT
# a list of directory for each time window, format dir_[run]_[tstart]_[tstop]
# output_[zmax]_[time window path] file for results



import os,sys
from fermicheck import *
from agilecheck import *

import glob

time_window_file = sys.argv[1]
ra = float(sys.argv[2])
dec = float(sys.argv[3])
path_dati_fermi = sys.argv[4]
path_log_index = sys.argv[5]
run_number = sys.argv[6]
zmax = float(sys.argv[7])
mode = sys.argv[8]
step = int(sys.argv[9])
line1 = float(sys.argv[10])
line2 = float(sys.argv[11])


def MET2orbit(tmin, tmax, path_to_LOG, source='MySource', send=True):
    """
       This function creates two files:
        1) MySource_tmin_tmax.txt containing a list of paths to the attitude information for each selected orbit
        2) merged_list.fits, which is a fits file containing the attitude information, that will be passed to
           the agilecheck.py script. The merged file will be filtered on-the-fly in order to have always INSTR_STATUS>0.
    """
    import os
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
            print(str(orbit)+'[1][LIVETIME > 0 && LOG_STATUS == 0 && MODE == 2 && PHASE .NE. 1 && PHASE .NE. 2]', file=file)
    
    print("files ", file, " created successfully")
    file.close()
    if send == True:
        os.system("sh "+os.environ['AGILEPIPE']+"/scripts/offaxis/merge_orbit_logs.sh "+str(filename)+" merged_list_"+str(tmin)+"_"+str(tmax)+".fits")

count = -1

f = open("output_"+str(zmax)+"_"+os.path.basename(time_window_file), "a+")
f.close()



with open(time_window_file) as fp:
   for cnt, line in enumerate(fp):

       #count = count + 1
       #if count != 0:
        #   continue


       tstart = float(line.split()[0])
       tstop = float(line.split()[1])
       print("new ----- \n "+str(tstart)+" "+str(tstop))

       f = open("output_"+str(zmax)+"_"+os.path.basename(time_window_file), "a")
       f.write("\n#####\n")
       f.write(str(zmax)+" "+str(tstart)+" "+str(tstop)+"\n")
       f.close()

       #create dir
       new_dir =  "dir_"+str(run_number)+"_"+str(zmax)+"_"+str(tstart)+"_"+str(tstop)
       os.mkdir(new_dir)
       os.chdir(new_dir)

       f = open("output_"+str(zmax)+"_"+os.path.basename(time_window_file), "a")
       f.write("\n#####\n")
       f.write(str(zmax)+" "+str(tstart)+" "+str(tstop)+"\n")
       f.close()

       #### FERMI ####

       if(mode == "fermi" or mode == "all"):

           fermi_met_start = (tstart - 51910.0 ) * 86400.0
           fermi_met_stop = (tstop - 51910.0 ) * 86400.0

           print("fermi time"+str(fermi_met_start)+" "+str(fermi_met_stop))

           check = fermicheck(path_dati_fermi, ra, dec, tstart, tstop, zmax=zmax, timelimiti=fermi_met_start,step=step, timelimitf=fermi_met_stop,out_name="output_"+str(zmax)+"_"+os.path.basename(time_window_file))
           check.PlotVisibility()
           #os.system("cp fermi_visibility*eps "+new_dir)

       #AGILE

       if(mode == "agile" or mode == "all"):

           agile_met_start = (tstart - 53005.0) *  86400.0;
           agile_met_stop = (tstop - 53005.0) *  86400.0;

           print("agile "+str(agile_met_start)+" "+str(agile_met_stop))

           MET2orbit(agile_met_start, agile_met_stop, path_log_index)

           merged_file = glob.glob('./merged_list_*.fits')[0]
           check = agilecheck(merged_file, ra, dec, tstart, tstop, zmax=zmax, timelimiti=agile_met_start, timelimitf=agile_met_stop, step=step, out_name="output_"+str(zmax)+"_"+os.path.basename(time_window_file))
           check.PlotVisibility()

       ### MERGE TWO PLOT ###

       #if(mode == "all"):
       from merge import *
       t0 = tstart+((tstop-tstart)/2)
       t0 = 0
       check=merge(timelimiti=tstart, timelimitf=tstop, t0=t0,zmax=zmax, lines=[line1, line2])
       check.Plotmerge(mode=mode)
       check.histogram_merge(mode=mode)

       os.chdir("..")
