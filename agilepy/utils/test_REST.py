import urllib
import requests



def request_data(datemin, datemax, mode):

    api_url = "https://toolsdev.ssdc.asi.it/AgileData/rest/getfiles/LOG/STDSYSTEM/GO/STD0P/2009-08-01T00:00:00/2009-08-10T00:00:00"

    url = "https://toolsdev.ssdc.asi.it/AgileData/rest"

    response = requests.get(api_url)

    with open("agile.tar.gz", "wb") as f:
        f.write(response.content)


if __name__=="__main__":
    request_data(0,0,0)