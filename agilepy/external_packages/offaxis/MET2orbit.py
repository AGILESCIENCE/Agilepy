import os

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
            print(str(orbit)+'[1][INSTR_STATUS > 0]', file=file) #add row filtering to have good instr_status
    print("files ", file, " created successfully")
    file.close()
    if send == True:
        os.system("./merge_orbit_logs.sh "+str(filename)+" merged_list_"+str(tmin)+"_"+str(tmax)+".fits")


def orbit2MET(orbita):
    index  = open('/home/agilefateam/ANALYSIS4/pmunar/LOG_index.log', 'r')
    line   = index.readline()
    file   = open('list_of_METs_'+str(orbita)+'.txt', 'w')
    while line:
        field  = line.split()
        orbit  = field[0]
        orbit  = int(orbit[-13:-7])
        tstart = field[1]
        tstop  = field[2]
        tstart = float(tstart)
        tstop  = float(tstop)
        if orbit == orbita:
            ti_desired = tstart
            tf_desired = tstop
            print(ti_desired, tf_desired, file=file)
        line = index.readline()

if __name__ == '__main__':
    ask_for_path = [True, True]
    while ask_for_path[0] == True:
        if ask_for_path[1] == False:
            continued = input('Do you want to continue? (y/n): ')
            if continued == 'n' or continued == 'no':
                print(' See you soon!')
                break
            elif continued == 'y' or continued == 'yes':
                ask_for_path[1] = True
        # Ask for the binary system and take its parameters
        path = input('Write a path where to look for the LOG.index file: ')
        try:
            os.system("ls "+path)
        except:
            answer = input('Wrong name. \n Do you want to continue? (y/n): ')
            if answer == 'n' or answer == 'no':
                print('See you soon!')
                break
            else:
                continue
        while ask_for_path[1] == True:
            time_i = input('introduce initial time in MET units: ')
            time_f = input('introduce final time in MET units: ')
            try:
                MET2orbit(float(time_i), float(time_f), path)
                ask_for_path[1] = False
                break
            except:
                answer = input('Wrong name. \n Do you want to continue? (y/n):')
                if answer == 'n' or answer == 'no':
                    print('See you soon!')
                    break
                    ask_for_path[1] = False
                    ask_for_path[0] = False
                else:
                    continue
            # If there is an exception. Because of a bad date or the user want to go out
 #           except Exception as e:
 #               print e
 #               answer = raw_input('Bad path or time. Do you want to continue? (y/n)\n')
 #               if answer == 'y' or answer == 'yes':
                #     pass
                # else:
                #     ask_for_path[1] = False
                #     answer = raw_input('Do you want to choose other path or time? (y/n)\n')
                #     if answer == 'y' or answer == 'yes':
                #         break
                #     else:
                #         print 'See you soon!'
                #         ask_for_path[0] = False
                #         break
