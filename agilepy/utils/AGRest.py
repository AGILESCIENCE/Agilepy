import os
import uuid
import json
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from time import time
from pathlib import Path

from tqdm import tqdm

from agilepy.utils.AstroUtils import AstroUtils
from agilepy.core.CustomExceptions import SSDCRestErrorDownload

class AGRest:

    def __init__(self, logger):
        self.logger = logger

        self.retry_strategy = Retry(
            total=5,
            status_forcelist=[429, 500, 502, 503, 504],
            method_whitelist=["HEAD", "GET", "OPTIONS"],
            backoff_factor=3)

        self.adapter = HTTPAdapter(max_retries=self.retry_strategy)
        self.http = requests.Session()
        self.http.mount("https://", self.adapter)
        self.http.mount("http://", self.adapter)

    def get_coverage(self):
        """
        It returns Data coverage of AGILE database on SSDC server
        Args:
            None

        Returns:
            tmin(dateformat fits type str)
            tmax(dateformat fits type str)
        """

        api_url = f"https://tools.ssdc.asi.it/AgileData/rest/publicdatacoverage"

        self.logger.info( f"Getting data coverage to SSDC server..")

        start = time() 

        response = self.http.get(api_url)

        if response.status_code != 200:
            raise SSDCRestErrorDownload(f"HTTP error. Failed to fetch data from SSDC: {response.status_code} - {response.text}")

        json_data = json.loads(response.text)

        if json_data["Response"]["statusCode"] != "OK":
            raise SSDCRestErrorDownload(json_data["Response"]["message"])

        tmin = json_data["DataCoverageFrom"]
        tmax = json_data["DataCoverageTo"]

        end = time() - start

        self.logger.info( f"Took {end} seconds")

        return tmin, tmax

    def gridList(self, tmin, tmax):
        """

        {'Response': {'message': None, 'statusCode': 'OK'}
        'AgileFiles': [ 
                {'filename': 'ag-182087934_STD0P.LOG.gz', 'absolutePath': 'std/0909301200_0910151200-86596/STD0P_LOG/ag-182087934_STD0P.LOG.gz'}, 
                {'filename': 'ag-182174334_STD0P.LOG.gz', 'absolutePath': 'std/0909301200_0910151200-86596/STD0P_LOG/ag-182174334_STD0P.LOG.gz'}, 
                {'filename': 'ag-182260734_STD0P.LOG.gz', 'absolutePath': 'std/0909301200_0910151200-86596/STD0P_LOG/ag-182260734_STD0P.LOG.gz'},
                {'filename': 'ag-182347134_STD0P.LOG.gz', 'absolutePath': 'std/0909301200_0910151200-86596/STD0P_LOG/ag-182347134_STD0P.LOG.gz'}, 
                {'filename': 'ag-182433534_STD0P.LOG.gz', 'absolutePath': 'std/0909301200_0910151200-86596/STD0P_LOG/ag-182433534_STD0P.LOG.gz'},
                {'filename': 'ag-182519934_STD0P.LOG.gz', 'absolutePath': 'std/0909301200_0910151200-86596/STD0P_LOG/ag-182519934_STD0P.LOG.gz'},
                {'filename': 'ag-182606334_STD0P.LOG.gz', 'absolutePath': 'std/0909301200_0910151200-86596/STD0P_LOG/ag-182606334_STD0P.LOG.gz'},
                {'filename': 'ag0909301200_0910151200_STD0P_FM.EVT.gz', 'absolutePath': 'std/0909301200_0910151200-86596/ag0909301200_0910151200_STD0P_FM.EVT.gz'}, 
                {'filename': 'ag-182692734_STD0P.LOG.gz', 'absolutePath': 'std/0910151200_0910311200-86597/STD0P_LOG/ag-182692734_STD0P.LOG.gz'}, 
                {'filename': 'ag0910151200_0910311200_STD0P_FM.EVT.gz', 'absolutePath': 'std/0910151200_0910311200-86597/ag0910151200_0910311200_STD0P_FM.EVT.gz'}
            ]
        """

        tmin_utc = AstroUtils.time_mjd_to_fits(tmin)
        tmax_utc = AstroUtils.time_mjd_to_fits(tmax)

        api_url = f"https://tools.ssdc.asi.it/AgileData/rest/GRIDList/{tmin_utc}/{tmax_utc}"

        self.logger.info( f"Downloading filelist to download ({tmin},{tmax}) ({tmin_utc}, {tmax_utc}) from {api_url}..")

        start = time() 
        
        response = self.http.get(api_url)

        if response.status_code != 200:
            raise SSDCRestErrorDownload(f"HTTP error. Failed to fetch data from SSDC: {response.status_code} - {response.text}")

        json_data = json.loads(response.text)

        end = time() - start

        self.logger.info( f"Took {end} seconds")

        if json_data["Response"]["statusCode"] != "OK":
            raise SSDCRestErrorDownload(json_data["Response"]["message"])

        if json_data["Response"]["statusCode"] == "OK" and json_data["Response"]["message"] == "No data found.":
            raise SSDCRestErrorDownload(json_data["Response"]["message"])

        return json_data["AgileFiles"]

    def gridFiles(self, tmin, tmax):
        """
        https://tools.ssdc.asi.it/AgileData/rest/GRIDFiles/2009-10-20T00:00:00/2009-11-10T00:00:00

        The actual data being downloaded could correspond to a bigger interval than tmin and tmax:
        this is because the SSDC rest service uses the following conventions:
        * the EVT file always contains 15 days of data
        * the LOG file always contains 1 day of data
        * the mapping between tmin,tmax and the actual time span of the data being downloaded can be inferred from the next examples:
            * tmin=03/01/21 tmax=05/01/21
                * 1 evt file: 01/01/21 to 15/01/21
                * 3 log files: 03/01/21, 04/01/21, 05/01/21
            * tmin=14/01/21 tmax=18/01/21
                * 2 evt files: 01/01/21 to 15/01/21 and 15/01/21 to 31/01/21
                * 5 log files: 14/01/21, 15/01/21, 16/01/21, 17/01/21, 18/01/21         
        """
        tmin_utc = AstroUtils.time_mjd_to_fits(tmin)
        tmax_utc = AstroUtils.time_mjd_to_fits(tmax)

        api_url = f"https://tools.ssdc.asi.it/AgileData/rest/GRIDFiles/{tmin_utc}/{tmax_utc}"

        self.logger.info( f"Downloading data ({tmin},{tmax}) from {api_url}..")

        start = time() 

        response = self.http.get(api_url, stream=True)

        if response.status_code != 200:
            raise SSDCRestErrorDownload(f"HTTP error. Failed to fetch data from SSDC: {response.status_code} - {response.text}")

        outpath = f"/tmp/agile_{str(uuid.uuid4())}.tar.gz"
        with open(outpath, "wb") as f:
            # Writing chunks for large downloads
            for chunk in tqdm(response.iter_content(chunk_size=1024*1024*10)):
                f.write(chunk)

        end = time() - start

        outpath_size = os.stat(outpath).st_size

        self.logger.info( f"Took {end} seconds. Downloaded {outpath_size} bytes.")

        if not Path(outpath).is_file():
            raise FileNotFoundError

        if outpath_size == 0:
            self.logger.warning( f"The downloaded data {outpath} is empty.")

        return outpath
