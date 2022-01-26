import tarfile
import calendar
import datetime
from time import time
from tqdm import tqdm
from pathlib import Path
from agilepy.utils.AGRest import AGRest
from agilepy.core.ScienceTools import Indexgen
from agilepy.utils.AstroUtils import AstroUtils

import pandas as pd
from enum import Enum

class DataStatus(Enum):
    OK = 0
    MISSING = 1
    #PARTIALLY_MISSING = 2 # not hanlded
    #TOTALLY_MISSING = 3 # not hanlded

class AGDataset:
    """
    This class manages the AGILE's archive stored on SSDC servers, it contains a REST API
    to download AGILE EVT and LOG data and it creates query files in order to keep the data requests updated.
    """

    def __init__(self, logger):
        self.logger = logger

    def downloadData(self, tmin, tmax, dataPath, evtIndex, logIndex):
        """ It downloads EVT and LOG data that the user requires to perform a scientific
        analysis from tmin to tmax (in MJD format).

        If the data is already present on disk, the download will be skipped. 

        The actual data being downloaded could correspond to a bigger interval than tmin and tmax:
        this is because the SSDC rest service.

        @param tmin: mjd
        @param tmax: mjd
        """
        dataPath = Path(dataPath)

        evtPath  = dataPath.joinpath("EVT")
        logPath  = dataPath.joinpath("LOG")

        evtQfile =  dataPath.joinpath("EVT.qfile")
        logQfile = dataPath.joinpath("LOG.qfile")

        evtDataMissing = False
        logDataMissing = False

        if self.dataIsMissing(tmin, tmax, evtQfile, 15) == DataStatus.MISSING:
            self.logger.info(self, f"EVT data in interval {tmin} {tmax} is missing!")
            evtDataMissing = True
        else:
            self.logger.info(self, f"Local data for EVT already in dataset")

        if self.dataIsMissing(tmin, tmax, logQfile, 1) == DataStatus.MISSING:
            self.logger.info(self, f"LOG data in interval {tmin} {tmax} is missing!")
            logDataMissing = True
        else:
            self.logger.info(self, f"Local data for LOG already in dataset")

        if evtDataMissing or logDataMissing:

            agRest = AGRest(self.logger)
            # filesList = agRest.gridList(tmin, tmax)
            tarFilePath = agRest.gridFiles(tmin, tmax)


        if evtDataMissing:
            extractedFiles = self.extractData("EVT", tarFilePath, dataPath)
            self.logger.debug(self, f"Extracted files: {extractedFiles}")
            self.updateQFile(evtQfile, tmin, tmax, evtQfile)
            self.generateIndex(evtPath, "EVT", evtIndex)

        if logDataMissing:
            extractedFiles = self.extractData("LOG", tarFilePath, dataPath)
            self.logger.debug(self, f"Extracted files: {extractedFiles}")
            self.updateQFile(logQfile, tmin, tmax, logQfile)
            self.generateIndex(logPath, "LOG", logIndex)

        return evtDataMissing or logDataMissing


    def computeEVT_SSDCslots(self, tmin, tmax):
        """
        Funzione che dato un tmin e tmax crea slot di 15 gg:
        Es:
        tmin 16/06/2018 tmax 25/09/2018

        return
        15/06/2018 30/06/2018
        30/07/2018 15/07/2018
        15/07/2018 31/07/2018
        31/08/2018 15/08/2018
        15/08/2018 31/08/2018
        31/09/2018 15/09/2018
        15/09/2018 30/09/2018
        """

        tmin = AstroUtils.time_mjd_to_utc(tmin)
        tmax = AstroUtils.time_mjd_to_utc(tmax)

        tmin = datetime.datetime.strptime(tmin, "%Y-%m-%dT%H:%M:%S")
        tmax = datetime.datetime.strptime(tmax, "%Y-%m-%dT%H:%M:%S")
        
        dt1 = datetime.timedelta(days=1)
        dt14 = datetime.timedelta(days=14)        
        dt15 = datetime.timedelta(days=15)        

        slots = []
        while tmin <= tmax:

            #print("start tmin:",tmin)
            firstDayOfMonth = tmin.replace(day=1)
            lastDay = calendar.monthrange(tmin.year, tmin.month)[-1]
            lastDayOfMonth = datetime.date(tmin.year, tmin.month, lastDay)
            lastDayOfMonth = datetime.datetime.combine(lastDayOfMonth, datetime.datetime.min.time())

            if tmin >= firstDayOfMonth and tmin <= firstDayOfMonth + dt14:
                slot = [firstDayOfMonth - dt1, firstDayOfMonth + dt14]
                tmin = firstDayOfMonth + dt15

            elif tmin > firstDayOfMonth + dt14 and tmin <= lastDayOfMonth:
                slot = [firstDayOfMonth + dt14, lastDayOfMonth]
                tmin = lastDayOfMonth + dt1

            slots.append(slot)

        return pd.DataFrame(slots, columns=["tmin", "tmax"])


    def computeLOG_SSDCslots(self, tmin, tmax):
        """
        Given tmin e tmax it creates a daytime slot(tmax is included):
        Es:
        tmin 16/06/2018 tmax 20/06/2018

        return
        16/06/2018 17/06/2018
        17/06/2018 18/06/2018
        18/06/2018 19/06/2018
        19/06/2018 20/06/2018
        20/06/2018 21/06/2018
        """

        dt1 = datetime.timedelta(days=1)
        tmin = AstroUtils.time_mjd_to_utc(tmin)
        tmax = AstroUtils.time_mjd_to_utc(tmax)

        tmin = datetime.datetime.strptime(tmin, "%Y-%m-%dT%H:%M:%S")
        tmax = datetime.datetime.strptime(tmax, "%Y-%m-%dT%H:%M:%S")
        slots = []
        while tmin <= tmax:

            slot = [tmin, tmin + dt1]
            tmin = tmin + dt1
            slots.append(slot)

        return pd.DataFrame(slots, columns=["tmin", "tmax"])

    def dataIsMissing(self, tmin, tmax, queryFilepath, blockSize):
        """ This method can be extended to handle the case of partial missing data
        """
        if not queryFilepath.exists():
            self.logger.warning(self, f"Query file {queryFilepath} does not exists")
            return DataStatus.MISSING

        tminUtc = AstroUtils.time_mjd_to_utc(tmin) # YYYY-MM-DDTHH:mm:ss
        tmaxUtc = AstroUtils.time_mjd_to_utc(tmax)

        tminUtc = datetime.datetime.strptime(tminUtc, "%Y-%m-%dT%H:%M:%S")
        tmaxUtc = datetime.datetime.strptime(tmaxUtc, "%Y-%m-%dT%H:%M:%S")

        self.logger.debug(self, f"({tmin}, {tmax}) => ({tminUtc}, {tmaxUtc})")

        datesDF = pd.read_csv(queryFilepath, header=None, sep=" ", names=["ssdctmin","ssdctmax"], parse_dates=["ssdctmin","ssdctmax"])

        
        self.logger.debug(self, str(datesDF))
        self.logger.debug(self, f"{tminUtc}, {tmaxUtc}")

        # check interval of tmin 
        intervalIndexTmin = self.getInterval(datesDF, tminUtc)
        # if tmin is not included in any interval:
        if intervalIndexTmin == -1:
            self.logger.debug(self, f"tminUtc {tminUtc} not present in any interval!")
            return DataStatus.MISSING
        
        # check interval of tmax:
        intervalIndexTmax = self.getInterval(datesDF, tmaxUtc)
        # if tmax is not included in any interval:
        if intervalIndexTmax == -1:
            self.logger.debug(self, f"tmaxUtc {tmaxUtc} not present in any interval!")
            return DataStatus.MISSING

        self.logger.debug(self, f"intervalIndexTmin: {str(intervalIndexTmin)}")
        self.logger.debug(self, f"intervalIndexTmax: {str(intervalIndexTmax)}")

        # check if there's missing data between the 2 intervals
        if self.gotHole(datesDF, intervalIndexTmin, intervalIndexTmax):
            self.logger.debug(self, f"Missing data between the 2 intervals!")
            return DataStatus.MISSING
        
        return DataStatus.OK


    def getInterval(self, datesDF, t):
        for index, block in datesDF.iterrows():
            if t >= block['ssdctmin'] and t < block['ssdctmax']:
                return index
        return -1

    def gotHole(self, datesDF, intervalIndexTmin, intervalIndexTmax):
        
        tstart = intervalIndexTmin
        tstop = intervalIndexTmax

        while tstart < tstop:
            ssdcStartDate = datesDF.iloc[[tstart]]["ssdctmax"]
            ssdcStopDate = datesDF.iloc[[tstart+1]]["ssdctmin"]
            tstart = tstart+1
            if ssdcStopDate.iloc[0] != ssdcStartDate.iloc[0]:
                return True

        return False
    

    def extractData(self, fileType, targzPath, destDir):
        """ This method iterates on the tarball members. For any member of a given "fileType", 
        if the member is not yet present in the dabatase of Agilepy, it will be added.   

        Tarball tree:
            std/           
                t0-t1 / 
                    blabla1.EVT.gz
                    STD0P_LOG/
                        blabla1.LOG.gz 
                        blabla2.LOG.gz 
                t2-t3 /
                    blabla2.EVT.gz
                    STD0P_LOG/
                        blabla3.LOG.gz 
                        blabla4.LOG.gz

            EVT / 
                blabla1.EVT.gz
                blabla2.EVT.gz
            LOG /
                blabla1.LOG.gz
                blabla2.LOG.gz
                blabla3.LOG.gz
                blabla4.LOG.gz              
        """
        self.logger.debug(self, f"Extracting data from {targzPath} to {destDir}")

        fileDest = destDir.joinpath(fileType)

        fileDest.mkdir(exist_ok=True, parents=True)

        tf = tarfile.open(f"{targzPath}")
        members = tf.getmembers()

        start = time() 

        extractedFiles = [] 
        for tarInfo in tqdm(members):            
            if fileType in tarInfo.name:
                added = self.handleTarInfo(tf, tarInfo, fileType, fileDest)
                if added:
                    extractedFiles.append(tarInfo.name)
        
        self.logger.debug(self, f"Extracted {len(extractedFiles)} {fileType} files. Took {time()-start} seconds.")
        return extractedFiles                    


    def updateQFile(self, qfile, tmin, tmax, qfileOut):
        """
        @param tmin: mjd
        @param tmax: mjd
        """
        if Path(qfile).exists():
            datesDF = pd.read_csv(qfile, header=None, sep=" ", names=["tmin","tmax"], parse_dates=["tmin","tmax"])
        else:
            datesDF = pd.DataFrame([])

        if "EVT" in qfile.stem:
            slots = self.computeEVT_SSDCslots(tmin, tmax)
        
        if "LOG" in qfile.stem:
            slots = self.computeLOG_SSDCslots(tmin, tmax)

        concatted = pd.concat([datesDF, slots], ignore_index=True)

        concatted.sort_values(by='tmin', inplace=True)
        concatted.reset_index(drop=True, inplace=True)

        concatted.to_csv(qfileOut, index=False, header=False, sep=" ", date_format="%Y-%m-%dT%H:%M:%S")


    
    def handleTarInfo(self, tarFileHandle, tarInfo, fileType, destPath):
        """ This method extract a member of the tarball. If the member is not yet present in the dabatase of Agilepy, it will be added.   

        """
        tmpPath = Path("/tmp")

        # /tmp/std/0909131200_0909161200-86594/ag0909131200_0909161200_STD0P_FM.EVT.gz
        tmpFilePath = tmpPath.joinpath(tarInfo.name)

        # /WHATEVER/EVT/ag0909131200_0909161200_STD0P_FM.EVT.gz
        outFile = Path(destPath).joinpath(tmpFilePath.name)

        self.logger.debug(self, f"tmpFilePath.name is {tmpFilePath.name}")

        # if file already exist, append a suffix to it
        if outFile.exists():
            self.logger.debug(self, f"The '{fileType}' file '{outFile}' is already present. Skipping it.")
            return False
            # /WHATEVER/EVT/ag0909131200_0909161200_STD0P_FM, .EVT.gz
            #root, _ = str(outFile).split(f".{fileType}.gz")
            # /WHATEVER/EVT/ag0909131200_0909161200_STD0P_FM_fb08e8c8-b879-4d5e-9924-07ed3a994075.EVT.gz
            #outFile = Path(f"{root}_{str(uuid.uuid4())}").with_suffix(f".{fileType}.gz")

        # /blabla../utils/tmp/std/0909161200_0909301200-186883/ag0909161200_0909301200_STD0P_FM.EVT.gz

        tarFileHandle.extract(tarInfo, path=tmpPath)

        #shutil.move(tmpFilePath, outFile)

        tmpFilePath.rename(outFile)

        self.logger.debug(self, f"Moving {tmpFilePath} to {outFile}.")

        return True

    def generateIndex(self, dataPath, filetype, pathToIndex):

        index_name = f"{filetype}.index"

        self.logger.debug(self, f"pathtoindex is {pathToIndex}")

        extraparams = {
                       "out_dir" : pathToIndex.parent,
                       "out_file": pathToIndex.name,
                       "type": filetype,
                       "data_dir":dataPath}
        
        igen = Indexgen("AG_indexgen", self.logger)
        igen.configureTool(extraParams=extraparams)


        #check if indexgen exists and delete it for overwriting
        ifile = Path(pathToIndex)
        if ifile.exists():
            ifile.unlink()

        indexfile = igen.call()
        self.logger.info(self, f"indexfile at {indexfile}")

    """
    def _checkindexfile(self, indexfile):

        with open(indexfile, "r") as f:
            pass
    """