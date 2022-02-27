import json
import logging
from typing import Optional

import requests
from bs4 import BeautifulSoup
from utils.constants import LOGFILE_PATH, HEADERS
import unicodedata

from utils.reception import Reception


def normalize(text):
  """Normalizes the provided text. This is needed to get rid of weird entries like \xa0."""
  return unicodedata.normalize("NFKD", text)

def get_website_content(url, headers=HEADERS):
  """Gets the website content with BS4."""
  website = requests.get(url, headers=headers)
  return BeautifulSoup(website.content, 'html.parser')

def get_reception_points(kml: dict, style_urls_to_skip: Optional[list[str]]):
  folders = kml["kml"]["Document"]["Folder"]
  for folder in folders:
    if "Border crossing point" in folder["name"]:
      return get_placemarks(folder, style_urls_to_skip)


def get_placemarks(folder: dict, style_urls_to_skip: Optional[list[str]]) -> list[Reception]:
  if style_urls_to_skip is None:
    style_urls_to_skip = []
  reception_points: list[Reception] = []
  placemarks: dict = folder["Placemark"]
  for placemark in placemarks:
    if placemark["styleUrl"] not in style_urls_to_skip:
      r = Reception()
      r.name = placemark["name"]
      coord = placemark["Point"]["coordinates"].split(',')
      r.lon = coord[0].strip()
      r.lat = coord[1].strip()
      reception_points.append(r)
  return reception_points

def gmaps_url_to_lat_lon(url):
  """Converts a Google maps URL string into latitude and longitude."""
  return url.split("!3d")[1].split("!4d")

def write_to_json(filename, text_arr, reception_arr, source):
  reception = []
  for rec in reception_arr:
    reception.append({
      "name": rec.name,
      "lat": rec.lat,
      "lon": rec.lon,
      "address": rec.address,
      "qr": rec.qr,
    })
  data = {"general": text_arr, "reception": reception, "source": source}
  with open(filename, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

def setup_logger():
  LOGGER = logging.getLogger("scraper")
  logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%d-%b-%y %H:%M:%S',
    handlers=[
        logging.FileHandler(LOGFILE_PATH, 'a', 'utf-8'),
        logging.StreamHandler()
    ]
  )
  return LOGGER
