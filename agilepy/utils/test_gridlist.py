import os
import uuid
import json
import shutil
import tarfile
import requests
from os import stat
from tqdm import tqdm
from time import time
from pathlib import Path

from agilepy.utils.AstroUtils import AstroUtils
from agilepy.core.ScienceTools import Indexgen


tmin = 55113
tmax = 55120

tmin_utc = AstroUtils.time_mjd_to_utc(tmin)
tmax_utc = AstroUtils.time_mjd_to_utc(tmax)

api_url = f"https://toolsdev.ssdc.asi.it/AgileData/rest/GRIDList/{tmin_utc}/{tmax_utc}"

print(f"Downloading filelist to download ({tmin},{tmax}) from {api_url}..")

start = time() 

response = requests.get(api_url)

json_data = json.loads(response.text)

end = time() - start

print(f"Took {end} seconds")

print(json_data)


