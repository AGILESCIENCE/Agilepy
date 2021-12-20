import os
import uuid
import urllib
import tarfile
import requests
from os import stat
from tqdm import tqdm
from time import time
from pathlib import Path

from agilepy.utils.AstroUtils import AstroUtils

class AGRest:

    def __init__(self, logger):
        self.logger = logger

    def getData(self, tmin, tmax, dataPath):
        actualTmin, actualTmax = self._computeInterval(tmin, tmax)
        fileTarPath = self._restCall(actualTmin, actualTmax)
        self._extractData(fileTarPath, dataPath)
        self._generateIndex(dataPath)

    def _computeInterval(self, tmin, tmax):
        return tmin, tmax

    def _restCall(self, tmin, tmax):

        tmin_utc = AstroUtils.time_mjd_to_utc(tmin)
        tmax_utc = AstroUtils.time_mjd_to_utc(tmax)

        api_url = f"https://toolsdev.ssdc.asi.it/AgileData/rest/GRIDFiles/{tmin_utc}/{tmax_utc}"

        self.logger.info(self, f"Downloading data ({tmin},{tmax}) from {api_url}..")

        start = time() 

        response = requests.get(api_url)

        end = time() - start

        self.logger.info(self, "Took {} seconds")
        print(f"Took {end} seconds")

        outpath = f"/tmp/agile_{str(uuid.uuid4())}.tar.gz"

        with open(outpath, "wb") as f:
            f.write(response.content)

        if not Path(outpath).is_file():
            raise FileNotFoundError

        if os.stat(outpath).st_size == 0:
            self.logger.warning(self, f"The downloaded data {outpath} is empty.")

        return outpath

    def _extractData(self, targzPath, destDir):
        """
        MI SERVONO I FILES dentro data/ per testare la tar-lib :)

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

        evtDest = destDir.joinpath("EVT")
        logDest = destDir.joinpath("LOG")

        evtDest.mkdir(exist_ok=True, parents=True)
        logDest.mkdir(exist_ok=True, parents=True)

        tf = tarfile.open(f"{targzPath}")
        members = tf.getmembers()

        start = time() 

        for tarInfo in tqdm(members):
            
            if "EVT" in tarInfo.name:
                self.handleTarInfo(tf, tarInfo, "EVT", evtDest)
            elif "LOG" in tarInfo.name:
                self.handleTarInfo(tf, tarInfo, "LOG", logDest)
            else:
                raise ValueError(f"TarInfo name is incompatible: {tarInfo}")

        self.logger.debug(self, f"Took {time()-start} seconds.")

    def handleTarInfo(self, tarFileHandle, tarInfo, fileType, destPath):

        tmpPath = Path("/tmp")

        # /tmp/std/0909131200_0909161200-86594/ag0909131200_0909161200_STD0P_FM.EVT.gz
        tmpFilePath = tmpPath.joinpath(tarInfo.name)

        # /WHATEVER/EVT/ag0909131200_0909161200_STD0P_FM.EVT.gz
        outFile = Path(destPath).joinpath(tmpFilePath.name)

        # if file already exist, append a suffix to it
        if outFile.exists():
            # /WHATEVER/EVT/ag0909131200_0909161200_STD0P_FM, .EVT.gz
            root, _ = str(outFile).split(f".{fileType}.gz")
            # /WHATEVER/EVT/ag0909131200_0909161200_STD0P_FM_fb08e8c8-b879-4d5e-9924-07ed3a994075.EVT.gz
            outFile = Path(f"{root}_{str(uuid.uuid4())}").with_suffix(f".{fileType}.gz")

        # /blabla../utils/tmp/std/0909161200_0909301200-186883/ag0909161200_0909301200_STD0P_FM.EVT.gz
        tarFileHandle.extract(tarInfo, path=tmpFilePath)

        tmpFilePath.rename(outFile)

        self.logger.debug(self, f"New file: {outFile} created.")



    def _generateIndex(self, dataPath):
        # Instanziare IndexGen Science Tool..
        pass
         