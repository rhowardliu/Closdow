import json
import requests
# from time import strftime,sleep
from asyncio import sleep
import logging

RAINFALL_URL = "https://api.data.gov.sg/v1/environment/rainfall"
QUERY_LOCATION = "Nanyang Avenue"
MIN_RAINFALL = 5

PM_25_URL="https://api.data.gov.sg/v1/environment/pm25"
QUERY_REGION = "west"
MIN_PM25 = 10

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

def format_current_time():
    return strftime("%Y-%m-%dT%H:%M:%S")

def get_url(url):
    response = requests.get(url)
    content = response.content.decode("utf8")
    return content

# def get_url(response):
#     if response.error:
#         print("Error: ", response.error)
#
#     else:
#         url = response.request.url
#         data = response.body
#         return data


def get_json_from_url(url):
    content = get_url(url)
    js = json.loads(content)
    return js


def get_station_id_from_json(js):
    for loc in js["metadata"]["stations"]:
        if loc["name"] == QUERY_LOCATION:
            return loc["id"]


def get_rainfall_from_id(js, stn_id):
    for loc in js["items"][0]["readings"]:
        if loc["station_id"] == stn_id:
            return loc["value"]

def get_pm_25_by_region(js, region):
    pm_loc = js["items"][0]["readings"]["pm25_one_hourly"][region]
    return pm_loc


def fetch_rainfall_data_run():
        # current_time_query = "?date_time=" + format_current_time()
        js_rain = get_json_from_url(RAINFALL_URL)
        station_id = get_station_id_from_json(js_rain)
        rain_ppt = get_rainfall_from_id(js_rain, station_id)
        logger.info("rain")
        logger.info(rain_ppt)



def fetch_pm_25_data_run():
        js_pm = get_json_from_url(PM_25_URL)
        pm_25 = get_pm_25_by_region(js_pm, QUERY_REGION)
        logger.info("pm25")
        logger.info(pm_25)



if __name__ == '__main__':
    fetch_rainfall_data_run()
